from typing import Optional, cast
import numpy as np
import gymnasium as gym
from pathlib import Path
from math import pi, sqrt

from Karana.Frame.Frame_Py import FrameContainer
from Karana.Core.KCore_Py import discard, allDestroyed
from Karana.Dynamics.SOADyn_types import (
    MultibodyDS,
    PinSubhingeDS,
    Linear3SubhingeDS,
    SphericalSubhingeDS,
    HingeDS,
)
from Karana.Dynamics.SOADyn_Py import (
    Multibody,
    HINGE_TYPE,
    StatePropagator,
    TimedEvent,
    PhysicalBody,
    PhysicalHinge,
)
from Karana.Math import UnitQuaternion, HomTran
from Karana.Scene.Scene_Py import (
    BoxGeometry,
    CylinderGeometry,
    Color,
    PhysicalMaterialInfo,
    PhysicalMaterial,
    LAYER_GRAPHICS,
    LAYER_ALL,
    LAYER_COLLISION,
    Texture,
    OrthographicProjection
)
from Karana.Scene.ProxyScene_Py import ProxyScenePart, ProxyScene
from Karana.Scene.CoalScene_Py import CoalScene
from Karana.Dynamics.Collision_Py import FrameCollider, PenaltyContact
from Karana.Models.GeneralKModels_Py import UniformGravity, UpdateProxyScene, SyncRealTime
from Karana.Math.Integrators_Py import IntegratorType


# helper to wrap angles
def wrap_to_pi(x):
    return (x + np.pi) % (2 * np.pi) - np.pi


def createMbody(fc: FrameContainer) -> Multibody:
    urdf_file = Path().absolute() / "atrvjr" / "atrvjr.urdf"
    multibody_info = MultibodyDS.fromUrdf(urdf_file)
    # convert to full6DOF hinge between root frame and rover.
    multibody_info.base_bodies[0].body.hinge = HingeDS(
        hinge_type=HINGE_TYPE.FULL6DOF,
        subhinges=[
            Linear3SubhingeDS(prescribed=False),
            SphericalSubhingeDS(prescribed=False),
        ],
    )

    # unlock locked Hinges for wheels from the URDF
    for i in [0, 1]:
        multibody_info.base_bodies[0].children[i].body.hinge = HingeDS(
            hinge_type=HINGE_TYPE.PIN,
            subhinges=[PinSubhingeDS(prescribed=False, unit_axis=np.array([0.0, 0.0, 1.0]))],
        )
    for i in [2, 3]:
        multibody_info.base_bodies[0].children[i].body.hinge = HingeDS(
            hinge_type=HINGE_TYPE.PIN,
            subhinges=[PinSubhingeDS(prescribed=False, unit_axis=np.array([0.0, 0.0, -1.0]))],
        )
    for visual in multibody_info.base_bodies[0].body.visuals:
        visual.layers = LAYER_GRAPHICS

    multibody = multibody_info.toMultibody(fc)
    multibody.ensureCurrent()
    multibody.resetData()
    assert multibody.isFinalized()
    return multibody


def createEnvironment(
    size: int, mb: Multibody, proxy_scene: ProxyScene
) -> tuple[PhysicalBody, PhysicalBody, PhysicalBody, PhysicalBody]:
    thickness = 0.25
    height = 2.5
    mat_info = PhysicalMaterialInfo()
    mat_info.color = Color.GRAY
    gray = PhysicalMaterial(mat_info)
    # add wheels to our atrv model
    wheel_geom = CylinderGeometry(0.125, 0.075)
    left_front_wheel = mb.getBody("left_front_wheel_link")
    left_front_wheel_node = ProxyScenePart(
        name="left_front_wheel_link_node", scene=proxy_scene, geometry=wheel_geom, material=gray
    )
    left_front_wheel_node.attachTo(left_front_wheel)
    left_front_wheel_node.setTranslation([0, 0, 0.03])
    left_front_wheel_node.setUnitQuaternion(UnitQuaternion(pi / 2, [1.0, 0.0, 0.0]))

    left_rear_wheel = mb.getBody("left_rear_wheel_link")
    left_rear_wheel_node = ProxyScenePart(
        name="left_rear_wheel_link_node", scene=proxy_scene, geometry=wheel_geom, material=gray
    )
    left_rear_wheel_node.attachTo(left_rear_wheel)
    left_rear_wheel_node.setTranslation([0, 0, 0.03])
    left_rear_wheel_node.setUnitQuaternion(UnitQuaternion(pi / 2, [1.0, 0.0, 0.0]))

    right_front_wheel = mb.getBody("right_front_wheel_link")
    right_front_wheel_node = ProxyScenePart(
        name="right_front_wheel_link_node", scene=proxy_scene, geometry=wheel_geom, material=gray
    )
    right_front_wheel_node.attachTo(right_front_wheel)
    right_front_wheel_node.setTranslation([0, 0, 0.03])
    right_front_wheel_node.setUnitQuaternion(UnitQuaternion(pi / 2, [1.0, 0.0, 0.0]))

    right_rear_wheel = mb.getBody("right_rear_wheel_link")
    right_rear_wheel_node = ProxyScenePart(
        name="right_rear_wheel_link_node", scene=proxy_scene, geometry=wheel_geom, material=gray
    )
    right_rear_wheel_node.attachTo(right_rear_wheel)
    right_rear_wheel_node.setTranslation([0, 0, 0.03])
    right_rear_wheel_node.setUnitQuaternion(UnitQuaternion(pi / 2, [1.0, 0.0, 0.0]))

    # add ground
    ground_geom = BoxGeometry(size, size, thickness)
    mat_info.color = Color.WHITE
    texture_file = Path().absolute() / "atrvjr" / "grid.png"
    grid_texture = Texture.lookupOrCreateTexture(str(texture_file))
    mat_info.colorMap = grid_texture
    grid = PhysicalMaterial(mat_info)
    ground = ProxyScenePart(
        "ground", scene=proxy_scene, geometry=ground_geom, material=grid, layers=LAYER_ALL
    )
    ground.setTranslation([0, 0, -0.1])

    # add walls
    mat_info.color = Color.KHAKI
    mat_info.colorMap = None
    khaki = PhysicalMaterial(mat_info)
    wall_geom = BoxGeometry(size, thickness, height)
    north_wall = ProxyScenePart(
        "north_wall", scene=proxy_scene, geometry=wall_geom, material=khaki, layers=LAYER_ALL
    )
    north_wall.setTranslation([size / 2.0 + thickness / 2, 0, height / 2 - thickness])
    north_wall.setUnitQuaternion(UnitQuaternion([1 / sqrt(2), 1 / sqrt(2), 0, 0]))
    south_wall = ProxyScenePart(
        "south_wall", scene=proxy_scene, geometry=wall_geom, material=khaki, layers=LAYER_ALL
    )
    south_wall.setTranslation([-size / 2.0 - thickness / 2, 0, height / 2 - thickness])
    south_wall.setUnitQuaternion(UnitQuaternion([-1 / sqrt(2), 1 / sqrt(2), 0, 0]))
    west_wall = ProxyScenePart(
        "west_wall", scene=proxy_scene, geometry=wall_geom, material=khaki, layers=LAYER_ALL
    )
    west_wall.setTranslation([0, size / 2.0 + thickness / 2, height / 2 - thickness])
    east_wall = ProxyScenePart(
        "east_wall", scene=proxy_scene, geometry=wall_geom, material=khaki, layers=LAYER_ALL
    )
    east_wall.setTranslation([0, -size / 2.0 - thickness / 2, height / 2 - thickness])

    return left_front_wheel, left_rear_wheel, right_front_wheel, right_rear_wheel


class ATRVEnv(gym.Env):
    metadata = {"render_modes": ["human", "none"]}

    def __init__(
        self,
        render_mode: Optional[str] = None,
        port: int = 0,
        sync_real_time: bool = False,
        **kwargs,
    ):
        self.render_mode = "none"
        if render_mode and render_mode in self.metadata["render_modes"]:
            self.render_mode = render_mode
        self.size = 30
        self._bound = self.size / 2.0 - 3.0
        self._torque_magnitude = 20.0

        # initialize the simulation
        self.init_sim(port, sync_real_time)

        # [txpos, typos, x, y, vx, vy, roll, yaw_vel, sin(angle_diff), cos(angle_diff)]
        low = np.array(
            [
                -self._bound,
                -self._bound,
                -self.size,
                -self.size,
                -6.0,
                -6.0,
                -0.25,
                -6.0,
                -1.0,
                -1.0,
            ],
            dtype=np.float32,
        )
        high = np.array(
            [self._bound, self._bound, self.size, self.size, 6.0, 6.0, 0.25, 6.0, 1.0, 1.0],
            dtype=np.float32,
        )
        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=np.float32)

        # define action space
        # torque on [left, right]
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)

        # initialize class variables
        self._left = None
        self._right = None
        self._agent_pos = None
        self._agent_vel = None
        self._agent_roll = None
        self._agent_yaw_vel = None
        self._angle_diff = None
        self.np_random = None

        self.pointer_pos = np.array([0.0, 0.0])

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # attach our multibody's to the root frame
        self._f2f = cast(PhysicalBody, self._mb.virtualRoot()).frame2Frame(
            self._mb.getBody("center_link")
        )
        self._root_hinge = cast(PhysicalHinge, self._mb.getBody("center_link").parentHinge())

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(axes=0.5, port=port, local_client='never')
            self._proxy_scene = self._mb.getScene()
            projection = OrthographicProjection()
            projection.height = 25.0
            projection.near = 0.1
            projection.far = 100.0
            viz_scene.defaultCamera().setProjection(projection)
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

         # add target object
        mat_info = PhysicalMaterialInfo()
        mat_info.color = Color.BLUE
        blue = PhysicalMaterial(mat_info)

        # create the target
        target_geom = CylinderGeometry(0.25, 0.05)
        self._target = ProxyScenePart(
            "target_part",
            scene=self._proxy_scene,
            geometry=target_geom,
            material=blue,
            layers=LAYER_GRAPHICS,
        )
        self._target.setUnitQuaternion(UnitQuaternion([1 / sqrt(2), 0, 0, 1 / sqrt(2)]))
        self._target_pos = np.zeros(2, dtype=np.float32)

        # setup wheels, ground, and walls
        left_front_wheel, left_rear_wheel, right_front_wheel, right_rear_wheel = createEnvironment(
            self.size, self._mb, self._proxy_scene
        )

        # setup collision client
        col_scene = CoalScene("collision_scene")
        self._proxy_scene.registerClientScene(
            col_scene, self._mb.virtualRoot(), layers=LAYER_COLLISION
        )

        # setup state propagator and models
        self._sp = StatePropagator(self._mb, integrator_type=IntegratorType.RK4)
        sp_opts = self._sp.getOptions()

        # gravity model
        ug = UniformGravity("grav_model", self._mb)
        ug.params.g = np.array([0, 0, -9.81])
        self._sp.registerModel(ug)
        del ug

        # for visualization
        if sync_real_time:
            self._sp.registerModel(SyncRealTime("sync_real_time", 1.0))

        # update proxy scene model
        self._sp.registerModel(UpdateProxyScene("update_proxy_scene", self._proxy_scene))

        # collision model
        mdl = PenaltyContact("penalty_contact", FrameCollider(self._proxy_scene, col_scene))
        mdl.registerBody(left_front_wheel)
        mdl.registerBody(left_rear_wheel)
        mdl.registerBody(right_front_wheel)
        mdl.registerBody(right_rear_wheel)
        mdl.params.kp = 100000
        mdl.params.kc = 20000
        mdl.params.mu = 0.3
        mdl.params.n = 1.5
        mdl.params.linear_region_tol = 1e-3
        self._sp.registerModel(mdl)
        del mdl

        def check_termination(t, x):
            # check if the car is flipping over
            flip = abs(self._f2f.relTransform().getUnitQuaternion().toEulerAngles().alpha()) > 0.2
            # if more than our 4 wheels are in contact, we have a collision
            if len(col_scene.cachedCollisions()) > 4 or flip:
                self._terminated = True
                return True
            return False

        def pre_deriv_fn(t, x):
            left_front_wheel.parentHinge().subhinge(0).setT(self._left)
            left_rear_wheel.parentHinge().subhinge(0).setT(self._left)
            right_front_wheel.parentHinge().subhinge(0).setT(self._right)
            right_rear_wheel.parentHinge().subhinge(0).setT(self._right)

        sp_opts.fns.pre_deriv_fns["apply_torque"] = pre_deriv_fn
        sp_opts.fns.terminate_advance_to_fns["check_termination"] = check_termination

    def _get_obs(self):
        return np.concatenate(
            (
                self._target_pos,
                self._agent_pos,
                self._agent_vel,
                self._agent_roll,
                self._agent_yaw_vel,
                np.sin(self._angle_diff),
                np.cos(self._angle_diff),
            )
        ).astype(np.float32)

    # use non-normalized values for info
    def _get_info(self):
        return {
            "target_pos": self._target_pos,
            "agent_pos": self._agent_pos,
            "agent_vel": self._agent_vel,
            "agent_roll": self._agent_roll,
            "agent_yaw_vel": self._agent_yaw_vel,
            "angle_diff": self._angle_diff,
        }

    def close(self):
        del self._proxy_scene, self._f2f, self._root_hinge, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)

        # initialize values
        self._terminated = False
        self._left = 0.0
        self._right = 0.0
        self._agent_pos = self.np_random.uniform(-self._bound, self._bound, size=(2,)).astype(
            np.float32
        )
        self._agent_vel = np.zeros(2, dtype=np.float32)
        self._agent_roll = np.zeros(1, dtype=np.float32)
        self._agent_yaw_vel = np.zeros(1, dtype=np.float32)
        agent_yaw = self.np_random.uniform(-np.pi, np.pi, size=(1,)).astype(np.float32)

        # calculate previous distance and angle difference
        difference = self._target_pos - self._agent_pos
        ideal_angle = np.arctan2(difference[1], difference[0])
        self._distance = np.linalg.norm(difference)
        self._angle_diff = wrap_to_pi(ideal_angle - agent_yaw)

        # reset the rover position and velocity
        self._mb.resetData()
        orientation = UnitQuaternion(agent_yaw[0], [0.0, 0.0, 1.0])
        self._root_hinge.fitQ(
            HomTran(q=orientation, vec=[self._agent_pos[0], self._agent_pos[1], 0])
        )

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())

        # setup timed event (every 0.01s)
        h = np.timedelta64(int(1e7), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t
        self._proxy_scene.update()
        return self._get_obs(), self._get_info()
    
    def set_pointer_pos(self, pos: np.ndarray):
        self.pointer_pos = pos
        self._target.setTranslation([self.pointer_pos[0], self.pointer_pos[1], 0.25])

    def step(self, action: np.ndarray):
        # initial target_pos
        self._target_pos = self.pointer_pos

        # apply action
        torque = action * self._torque_magnitude
        self._left = torque[0]
        self._right = torque[1]
        self._sp.advanceBy(0.05)
        T = self._f2f.relTransform()
        self._agent_pos = T.getTranslation()[:2]
        q = T.getUnitQuaternion()
        ea = q.toEulerAngles()
        agent_yaw = np.array([ea.gamma()])
        self._agent_roll = np.array([ea.alpha()])
        sp_vel = self._f2f.relSpVel().toVector6()
        self._agent_vel = sp_vel[3:5]
        self._agent_yaw_vel = np.array([sp_vel[2]])

        # check termination
        difference = self._target_pos - self._agent_pos
        distance = np.linalg.norm(difference)
        ideal_angle = np.arctan2(difference[1], difference[0])
        angle_diff = wrap_to_pi(ideal_angle - agent_yaw)
        reward = 0.0
        if bool(distance < 1.0):
            self._terminated = True
            reward += 4.0
        elif self._terminated:
            reward -= 4.0
        else:
            # reward calculations
            progress = self._distance - distance
            angle_progress = np.abs(self._angle_diff) - np.abs(angle_diff)
            reward += progress
            reward += 4 * angle_progress
            reward -= 0.03  # step penalty
            self._distance = distance
            self._angle_diff = angle_diff

        # observation, reward, terminated, truncated, data
        return self._get_obs(), float(reward), self._terminated, False, self._get_info()