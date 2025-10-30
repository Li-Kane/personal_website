from typing import Optional, cast
import numpy as np
import gymnasium as gym
from pathlib import Path
from math import pi, sqrt
import torch
from collections import deque

from Karana.Frame import FrameContainer
from Karana.Core import discard, allDestroyed
from Karana.Dynamics.SOADyn_types import (
    MultibodyDS,
    PinSubhingeDS,
    Linear3SubhingeDS,
    SphericalSubhingeDS,
    HingeDS,
)
from Karana.Dynamics import (
    Multibody,
    HINGE_TYPE,
    PinSubhinge,
    StatePropagator,
    TimedEvent,
    PhysicalBody,
    PhysicalHinge,
    Algorithms
)
from Karana.Math import UnitQuaternion, HomTran, SpatialVector
from Karana.Scene import (
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
from Karana.Scene import ProxyScenePart, ProxyScene
from Karana.Scene import CoalScene
from Karana.Collision import FrameCollider, HuntCrossley
from Karana.Models import UniformGravity, UpdateProxyScene, SyncRealTime, PenaltyContact
from Karana.Math import IntegratorType

def calculate_torque(current_pos: float, desired_pos: float, current_vel: float, max_effort: float = 45.0) -> float:
    # stiffness kp = 60.0
    # damping kd = 1.5
    return np.clip(
        60.0 * (desired_pos - current_pos) - 1.5 * current_vel,
        -max_effort,
        max_effort,
    )

def createMbody(fc: FrameContainer) -> Multibody:
    urdf_file = Path().absolute() / "assets" / "spot_simple.urdf"
    multibody_info = MultibodyDS.fromUrdf(urdf_file)
    # convert to full6DOF hinge between root frame and spot base
    multibody_info.base_bodies[0].body.hinge = HingeDS(
        hinge_type=HINGE_TYPE.FULL6DOF,
        subhinges=[
            Linear3SubhingeDS(prescribed=False),
            SphericalSubhingeDS(prescribed=False),
        ],
    )

    # iterate through all bodies and make them visual (except for lleg)
    my_deque = deque()
    my_deque.append(multibody_info.base_bodies[0])
    while my_deque:
        current = my_deque.popleft()
        if "lleg" in current.body.name:
            continue
        for visual in current.body.visuals:
            visual.layers = LAYER_GRAPHICS
        for child in current.children:
            my_deque.append(child)

    # convert to multibody
    multibody = multibody_info.toMultibody(fc)
    multibody.ensureCurrent()
    multibody.resetData()
    assert multibody.isFinalized()
    return multibody


def createEnvironment(
    size: int, proxy_scene: ProxyScene
):
    mat_info = PhysicalMaterialInfo()
    mat_info.color = Color.CORAL
    coral = PhysicalMaterial(mat_info)
    ground_geom = BoxGeometry(size, size, 0.25)
    ground = ProxyScenePart(
        "ground", scene=proxy_scene, geometry=ground_geom, material=coral, layers=LAYER_ALL
    )
    ground.setTranslation([0, 0, -0.64])


class SpotEnv(gym.Env):
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
        # out spot policy controller
        self._policy = torch.jit.load("spot_policy.pt", map_location="cpu")
        self._policy.eval()

        # initialize the simulation
        self.init_sim(port, sync_real_time)

        # init vars
        self._agent_pos = np.array([0.0, 0.0])
        self._default_pos = np.array(
            [
                0.1,
                -0.1,
                0.1,
                -0.1,
                0.9,
                0.9,
                1.1,
                1.1,
                -1.5,
                -1.5,
                -1.5,
                -1.5,
            ]
        )
        self._prev_action = np.zeros(12)

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # obtain all the necessary joints
        self._fl_hip = cast(PinSubhinge, self._mb.getBody("fl_hip").parentHinge().subhinge(0))
        self._fr_hip = cast(PinSubhinge, self._mb.getBody("fr_hip").parentHinge().subhinge(0))
        self._hl_hip = cast(PinSubhinge, self._mb.getBody("hl_hip").parentHinge().subhinge(0))
        self._hr_hip = cast(PinSubhinge, self._mb.getBody("hr_hip").parentHinge().subhinge(0))
        self._fl_uleg = cast(PinSubhinge, self._mb.getBody("fl_uleg").parentHinge().subhinge(0))
        self._fr_uleg = cast(PinSubhinge, self._mb.getBody("fr_uleg").parentHinge().subhinge(0))
        self._hl_uleg = cast(PinSubhinge, self._mb.getBody("hl_uleg").parentHinge().subhinge(0))
        self._hr_uleg = cast(PinSubhinge, self._mb.getBody("hr_uleg").parentHinge().subhinge(0))
        self._fl_lleg = cast(PinSubhinge, self._mb.getBody("fl_lleg").parentHinge().subhinge(0))
        self._fr_lleg = cast(PinSubhinge, self._mb.getBody("fr_lleg").parentHinge().subhinge(0))
        self._hl_lleg = cast(PinSubhinge, self._mb.getBody("hl_lleg").parentHinge().subhinge(0))
        self._hr_lleg = cast(PinSubhinge, self._mb.getBody("hr_lleg").parentHinge().subhinge(0))

        # attach a frame2frame to the spot base
        self._body = cast(PhysicalBody, self._mb.getBody("body"))
        self._f2f = cast(PhysicalBody, self._mb.virtualRoot()).frame2Frame(
            self._body
        )
        self._root_hinge = cast(PhysicalHinge, self._mb.getBody("body").parentHinge())

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(port=port, local_client='never')
            self._proxy_scene = self._mb.getScene()
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

        # create the environment
        createEnvironment(50, self._proxy_scene)

        # setup collision client
        col_scene = CoalScene("collision_scene")
        self._proxy_scene.registerClientScene(
            col_scene, self._mb.virtualRoot(), layers=LAYER_COLLISION
        )

        # setup state propagator and models
        self._sp = StatePropagator(self._mb, integrator_type=IntegratorType.RK4)
        sp_opts = self._sp.getOptions()

        self._sp.registerModel(SyncRealTime("sync_real_time", 1.0))

        # for visualization
        if sync_real_time:
            self._sp.registerModel(SyncRealTime("sync_real_time", 1.0))

        # gravity model
        ug = UniformGravity("grav_model", self._mb)
        ug.params.g = np.array([0, 0, -9.81])
        self._sp.registerModel(ug)
        del ug

        # update proxy scene model
        self._sp.registerModel(UpdateProxyScene("update_proxy_scene", self._proxy_scene))

        # Set penalty contact model parameters
        hc = HuntCrossley("hunt_crossley_contact")
        hc.params.kp = 1.453e5
        hc.params.kc = 0
        hc.params.mu = 1.5
        hc.params.n = 1.5
        hc.params.linear_region_tol = 0

        # collision model
        mdl = PenaltyContact("penalty_contact", self._mb, [FrameCollider(self._proxy_scene, col_scene)], hc)
        self._sp.registerModel(mdl)
        del mdl

        # define the apply forces function
        def apply_forces(t, x):
            self._fl_hip.setT(calculate_torque(self._fl_hip.getQ(), self._fl_hip_des, self._fl_hip.getU()))
            self._fr_hip.setT(calculate_torque(self._fr_hip.getQ(), self._fr_hip_des, self._fr_hip.getU()))
            self._hl_hip.setT(calculate_torque(self._hl_hip.getQ(), self._hl_hip_des, self._hl_hip.getU()))
            self._hr_hip.setT(calculate_torque(self._hr_hip.getQ(), self._hr_hip_des, self._hr_hip.getU()))
            self._fl_uleg.setT(calculate_torque(self._fl_uleg.getQ(), self._fl_uleg_des, self._fl_uleg.getU()))
            self._fr_uleg.setT(calculate_torque(self._fr_uleg.getQ(), self._fr_uleg_des, self._fr_uleg.getU()))
            self._hl_uleg.setT(calculate_torque(self._hl_uleg.getQ(), self._hl_uleg_des, self._hl_uleg.getU()))
            self._hr_uleg.setT(calculate_torque(self._hr_uleg.getQ(), self._hr_uleg_des, self._hr_uleg.getU()))
            self._fl_lleg.setT(calculate_torque(self._fl_lleg.getQ(), self._fl_lleg_des, self._fl_lleg.getU(), 115.0))
            self._fr_lleg.setT(calculate_torque(self._fr_lleg.getQ(), self._fr_lleg_des, self._fr_lleg.getU(), 115.0))
            self._hl_lleg.setT(calculate_torque(self._hl_lleg.getQ(), self._hl_lleg_des, self._hl_lleg.getU(), 115.0))
            self._hr_lleg.setT(calculate_torque(self._hr_lleg.getQ(), self._hr_lleg_des, self._hr_lleg.getU(), 115.0))
        sp_opts.fns.pre_deriv_fns["apply_forces"] = apply_forces

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        self._agent_pos = np.random.uniform(-10.0, 10.0, size=(2,))

        # move base to random position
        self._root_hinge.fitQ(
            HomTran(vec=np.array([self._agent_pos[0], self._agent_pos[1], 0.0]))
        )

        # set desired position variables
        self._fl_hip_des = 0.1
        self._fr_hip_des = -0.1
        self._hl_hip_des = 0.1
        self._hr_hip_des = -0.1
        self._fl_uleg_des = 0.9
        self._fr_uleg_des = 0.9
        self._hl_uleg_des = 1.1
        self._hr_uleg_des = 1.1
        self._fl_lleg_des = -1.5
        self._fr_lleg_des = -1.5
        self._hl_lleg_des = -1.5
        self._hr_lleg_des = -1.5

        # set to default position:
        self._fl_hip.setQ(self._fl_hip_des)
        self._fr_hip.setQ(self._fr_hip_des)
        self._hl_hip.setQ(self._hl_hip_des)
        self._hr_hip.setQ(self._hr_hip_des)
        self._fl_uleg.setQ(self._fl_uleg_des)
        self._fr_uleg.setQ(self._fr_uleg_des)
        self._hl_uleg.setQ(self._hl_uleg_des)
        self._hr_uleg.setQ(self._hr_uleg_des)
        self._fl_lleg.setQ(self._fl_lleg_des)
        self._fr_lleg.setQ(self._fr_lleg_des)
        self._hl_lleg.setQ(self._hl_lleg_des)
        self._hr_lleg.setQ(self._hr_lleg_des)

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())
        self._proxy_scene.update()

        # setup timed event (every 0.002s)
        h = np.timedelta64(int(2e6), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

        self._sp.advanceBy(0.001)

    def get_observation(self, action: np.ndarray):
        # convert to body frames and use projected gravity
        sp_vel = self._f2f.relSpVel().toVector6()
        obs = np.zeros(48)
        # 3 base_lin_vel
        obs[:3] = sp_vel[3:6]
        # 3 base_ang_vel
        obs[3:6] = sp_vel[0:3]
        # 3 gravity
        proj_gravity = self._body.getGravAccel()
        obs[6:9] = proj_gravity / np.linalg.norm(proj_gravity)
        # 3 command
        obs[9:12] = action
        # 12 joint offset (current_joint_pos - default_pos)
        obs[12] = self._fl_hip.getQ() - self._default_pos[0]
        obs[13] = self._fr_hip.getQ() - self._default_pos[1]
        obs[14] = self._hl_hip.getQ() - self._default_pos[2]
        obs[15] = self._hr_hip.getQ() - self._default_pos[3]
        obs[16] = self._fl_uleg.getQ() - self._default_pos[4]
        obs[17] = self._fr_uleg.getQ() - self._default_pos[5]
        obs[18] = self._hl_uleg.getQ() - self._default_pos[6]
        obs[19] = self._hr_uleg.getQ() - self._default_pos[7]
        obs[20] = self._fl_lleg.getQ() - self._default_pos[8]
        obs[21] = self._fr_lleg.getQ() - self._default_pos[9]
        obs[22] = self._hl_lleg.getQ() - self._default_pos[10]
        obs[23] = self._hr_lleg.getQ() - self._default_pos[11]
        # 12 joint velocities
        obs[24] = self._fl_hip.getU()
        obs[25] = self._fr_hip.getU()
        obs[26] = self._hl_hip.getU()
        obs[27] = self._hr_hip.getU()
        obs[28] = self._fl_uleg.getU()
        obs[29] = self._fr_uleg.getU()
        obs[30] = self._hl_uleg.getU()
        obs[31] = self._hr_uleg.getU()
        obs[32] = self._fl_lleg.getU()
        obs[33] = self._fr_lleg.getU()
        obs[34] = self._hl_lleg.getU()
        obs[35] = self._hr_lleg.getU()
        # 12 previous action (the raw policy output)
        obs[36:48] = self._prev_action
        return torch.as_tensor(obs, dtype=torch.float32).view(1, -1)

    def step(self, action: np.ndarray):
        action_scale = 0.2

        observation = self.get_observation(action)
        with torch.no_grad():
            policy_action = self._policy(observation)  # -> (1, 12)
        policy_action = policy_action.squeeze(0).cpu().numpy()
        self._prev_action = policy_action

        # apply action to joints
        action = policy_action * action_scale
        self._fl_hip_des = self._default_pos[0] + action[0]
        self._fr_hip_des = self._default_pos[1] + action[1]
        self._hl_hip_des = self._default_pos[2] + action[2]
        self._hr_hip_des = self._default_pos[3] + action[3]
        self._fl_uleg_des = self._default_pos[4] + action[4]
        self._fr_uleg_des = self._default_pos[5] + action[5]
        self._hl_uleg_des = self._default_pos[6] + action[6]
        self._hr_uleg_des = self._default_pos[7] + action[7]
        self._fl_lleg_des = self._default_pos[8] + action[8]
        self._fr_lleg_des = self._default_pos[9] + action[9]
        self._hl_lleg_des = self._default_pos[10] + action[10]
        self._hr_lleg_des = self._default_pos[11] + action[11]
        self._sp.advanceBy(0.02)

    def close(self):
        del self._proxy_scene, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()