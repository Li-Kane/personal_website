from typing import Optional, cast
import numpy as np
import gymnasium as gym
import torch
from math import sqrt

from helpers import (
    urdf_to_policy,
    policy_to_urdf,
    createMbody,
    createEnvironment,
    wrap_to_pi,
)
from Karana.Frame import FrameContainer
from Karana.Core import discard, allDestroyed
from Karana.Dynamics import (
    StatePropagator,
    TimedEvent,
    PhysicalBody,
    PhysicalHinge,
)
from Karana.Scene import (
    LAYER_COLLISION,
    ProxyScene,
    CoalScene,
    PhysicalMaterialInfo,
    PhysicalMaterial,
    Color,
    ProxyScenePart,
    CylinderGeometry,
    LAYER_GRAPHICS,
)
from Karana.Collision import FrameCollider, HuntCrossley
from Karana.Models import UniformGravity, UpdateProxyScene, SyncRealTime, PenaltyContact
from Karana.Math import (
    IntegratorType,
    UnitQuaternion,
    HomTran,
)

DEFAULT_POS = np.array([0.1, 0.9, -1.5, -0.1, 0.9, -1.5, 0.1, 1.1, -1.5, -0.1, 1.1, -1.5])
EFFORT_LIMITS = np.array([45.0, 45.0, 115.0, 45.0, 45.0, 115.0, 45.0, 45.0, 115.0, 45.0, 45.0, 115.0])
STIFFNESS = 80.0
DAMPING = 1.5
GROUND_SIZE = 25.0
BOUND = GROUND_SIZE / 2.0

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
        
        # our spot policy controller
        self._policy = torch.jit.load("spot_policy.pt", map_location="cpu")
        self._policy.eval()

        # (tx, ty, ax, ay, ar, ap, ay, vx, vy, vz, sin, cos)
        # low = np.array([
        #     -BOUND,
        #     -BOUND,
        #     -BOUND,
        #     -BOUND,

        # ], dtype=np.float32)

        # initialize the simulation
        self.init_sim(port, sync_real_time)

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # attach a frame2frame to the spot base
        self._body = cast(PhysicalBody, self._mb.getBody("body"))
        self._f2f = cast(PhysicalBody, self._mb.getNewtonianFrame()).frame2Frame(
            self._body
        )
        self._root_hinge = cast(PhysicalHinge, self._body.parentHinge())
        self._coorddata = self._mb.subhingeCoordData()

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(port=port, local_client='never')
            viz_scene.defaultCamera().pointCameraAt(
                [0.0, 3.0, 1.5], [0, 0, 0,], [0, 0, 1],
            )
            self._proxy_scene = self._mb.getScene()
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

        # setup a target object for the robot to follow
        mat_info = PhysicalMaterialInfo()
        mat_info.color = Color.RED
        red = PhysicalMaterial(mat_info)
        target_geom = CylinderGeometry(0.25, 0.05)
        self._target = ProxyScenePart(
            "target_part",
            scene=self._proxy_scene,
            geometry=target_geom,
            material=red,
            layers=LAYER_GRAPHICS,
        )
        self._target.setUnitQuaternion(UnitQuaternion([1 / sqrt(2), 0, 0, 1 / sqrt(2)]))
        self._target.setTranslation(np.array([0.0, 0.0, -0.5]))

        # create the environment
        createEnvironment(GROUND_SIZE, self._proxy_scene)

        # setup collision client
        col_scene = CoalScene("collision_scene")
        self._proxy_scene.registerClientScene(
            col_scene, self._mb.virtualRoot(), layers=LAYER_COLLISION
        )

        # setup state propagator and models
        self._sp = StatePropagator(self._mb, integrator_type=IntegratorType.EULER)
        sp_opts = self._sp.getOptions()

        # for visualization
        # if sync_real_time:
        #     self._sp.registerModel(SyncRealTime("sync_real_time", 1.0))

        # gravity model
        ug = UniformGravity("grav_model", self._mb)
        ug.params.g = np.array([0, 0, -9.81])
        self._sp.registerModel(ug)
        del ug

        # update proxy scene model
        self._sp.registerModel(UpdateProxyScene("update_proxy_scene", self._proxy_scene))

        # Set penalty contact model parameters
        hc = HuntCrossley("hunt_crossley_contact")
        hc.params.kp = 1e7
        hc.params.kc = 5e6
        hc.params.mu = 1.1
        hc.params.n = 1.5
        hc.params.linear_region_tol = 1e-20

        # collision model
        mdl = PenaltyContact("penalty_contact", self._mb, [FrameCollider(self._proxy_scene, col_scene)], hc)
        self._sp.registerModel(mdl)
        del mdl

        # define the apply forces function
        def apply_forces(t, x):
            Q = self._coorddata.getQ()[6:]
            U = self._coorddata.getU()[6:]
            err = self._desired_pos - Q
            new_T = np.clip(STIFFNESS * err - DAMPING * U, -EFFORT_LIMITS, EFFORT_LIMITS)
            T = self._coorddata.getT()
            T[6:] = new_T
            self._coorddata.setT(T)
        sp_opts.fns.pre_deriv_fns["apply_forces"] = apply_forces

    def calc_angle_diff(self, agent_yaw):
        # calculate previous distance and angle difference
        difference = self._target_pos - self._agent_pos
        ideal_angle = np.arctan2(difference[1], difference[0])
        self._distance = np.linalg.norm(difference)
        self._angle_diff = wrap_to_pi(ideal_angle - agent_yaw)

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)

        # move base to random position
        agent_yaw = self.np_random.uniform(-np.pi, np.pi, size=(1,)).astype(np.float32)
        agent_pos = np.random.uniform(-10.0, 10.0, size=(2,))
        orientation = UnitQuaternion(agent_yaw[0], [0.0, 0.0, 1.0])
        self._root_hinge.fitQ(
            HomTran(q=orientation, vec=np.array([agent_pos[0], agent_pos[1], 0.0]))
        )
        self._target.setTranslation([self._target_pos[0], self._target_pos[1], -0.5])

        # set initial qpos
        self._desired_pos = DEFAULT_POS
        Q = self._coorddata.getQ()
        Q[6:] = self._desired_pos
        self._coorddata.setQ(Q)

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())
        self._proxy_scene.update()

        # setup timed event (every 0.2 ms)
        h = np.timedelta64(int(2e5), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

        self._sp.advanceBy(0.01)

        # init vars
        self._prev_action = np.zeros(12, dtype=np.float32)
        self._terminated = False
        self._target_pos = np.zeros(2, dtype=np.float32)
        self._agent_vel = np.zeros(6, dtype=np.float32)
        self.calc_angle_diff(agent_yaw)
        self._agent_pose = self._f2f.relTransform().toVector6()

    # create a (48,) array to feed into the spot policy
    def get_policy_observation(self, action: np.ndarray):
        wsp_vel = self._f2f.relSpVel().toVector6()
        transform = self._f2f.relTransform().getMatrix()[:3, :3].transpose()
        obs = np.zeros(48)
        # 3 base_lin_vel
        obs[:3] = np.matmul(transform, wsp_vel[3:6])
        # 3 base_ang_vel
        obs[3:6] = np.matmul(transform, wsp_vel[0:3])
        # 3 gravity
        proj_gravity = self._body.getGravAccel()
        obs[6:9] = proj_gravity / np.linalg.norm(proj_gravity)
        # 3 command
        obs[9:12] = action
        # 12 joint offset (current_joint_pos - default_pos)
        Q = urdf_to_policy(self._coorddata.getQ()[6:] - DEFAULT_POS)
        obs[12:24] = Q
        # 12 joint velocities
        U = urdf_to_policy(self._coorddata.getU()[6:])
        obs[24:36] = U
        # 12 previous action (the raw policy output)
        obs[36:48] = self._prev_action
        return torch.as_tensor(obs, dtype=torch.float32).view(1, -1)

    def step(self, action: np.ndarray):
        action_scale = 0.2

        # Time observation gathering
        observation = self.get_policy_observation(action)
        with torch.inference_mode():
            policy_action = self._policy(observation)  # -> (1, 12)
        policy_action = policy_action.squeeze(0).cpu().numpy()
        self._prev_action = policy_action

        # apply action to joints
        action = policy_to_urdf(policy_action * action_scale)
        Q = self._coorddata.getQ()
        Q[6:] = DEFAULT_POS + action
        self._desired_pos = DEFAULT_POS + action
        
        # Time advanceBy
        self._sp.advanceBy(0.02)

        # get our gymnasium observation values
        T = self._f2f.relTransform()
        agent_pose = T.toVector6()
        agent_vel = self._f2f.relSpVel()
        agent_yaw = agent_pose[2]


    def close(self):
        del self._proxy_scene
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()