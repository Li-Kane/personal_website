from typing import Optional, cast
import numpy as np
import gymnasium as gym
import torch
import time

from helpers import (
    urdf_to_policy,
    policy_to_urdf,
    createMbody,
    createEnvironment,
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
)
from Karana.Scene import ProxyScene
from Karana.Scene import CoalScene
from Karana.Collision import FrameCollider, HuntCrossley
from Karana.Models import UniformGravity, UpdateProxyScene, SyncRealTime, PenaltyContact
from Karana.Math import IntegratorType

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

        # initialize the simulation
        self.init_sim(port, sync_real_time)

        # init vars
        self._agent_pos = np.array([0.0, 0.0])
        self._default_pos = np.array(
            [
                0.1,
                0.9,
                -1.5,
                -0.1,
                0.9,
                -1.5,
                0.1,
                1.1,
                -1.5,
                -0.1,
                1.1,
                -1.5,
            ]
        )
        self._prev_action = np.zeros(12)

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # attach a frame2frame to the spot base
        self._body = cast(PhysicalBody, self._mb.getBody("body"))
        self._f2f = cast(PhysicalBody, self._mb.virtualRoot()).frame2Frame(
            self._body
        )
        self._root_hinge = cast(PhysicalHinge, self._body.parentHinge())
        self._coorddata = self._mb.subhingeCoordData()
        self._effort_limits = np.array([45.0, 45.0, 115.0, 45.0, 45.0, 115.0, 45.0, 45.0, 115.0, 45.0, 45.0, 115.0])

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(port=port, local_client='never')
            viz_scene.defaultCamera().pointCameraAt(
                [0.0, 3.0, 1.5], [0, 0, 0,], [0, 0, 1],
            )
            self._proxy_scene = self._mb.getScene()
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

        # create the environment
        createEnvironment(100, self._proxy_scene)

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
            t0 = time.perf_counter()
            Q = self._coorddata.getQ()[6:]
            U = self._coorddata.getU()[6:]
            err = self._desired_pos - Q
            new_T = np.clip(80.0 * err - 1.5 * U, -self._effort_limits, self._effort_limits)
            T = self._coorddata.getT()
            T[6:] = new_T
            self._coorddata.setT(T)
            self._af_time_ns += time.perf_counter() - t0
        sp_opts.fns.pre_deriv_fns["apply_forces"] = apply_forces

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        self._agent_pos = np.random.uniform(-10.0, 10.0, size=(2,))

        # move base to random position
        # self._root_hinge.fitQ(
        #     HomTran(vec=np.array([self._agent_pos[0], self._agent_pos[1], 0.0]))
        # )

        # timing metrics
        self._step_times = []
        self._observation_times = []
        self._advance_times = []
        self._step_count = 0
        self._af_time_ns = 0
        self._af_per_step = []

        self._desired_pos = self._default_pos
        Q = self._coorddata.getQ()
        Q[6:] = self._desired_pos
        self._coorddata.setQ(Q)

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())
        self._proxy_scene.update()

        # setup timed event (every 0.2 ms)
        h = np.timedelta64(int(1e5), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

        self._sp.advanceBy(0.001)

    def get_observation(self, action: np.ndarray):
        # convert to body frames and use projected gravity
        wsp_vel = self._f2f.relSpVel().toVector6()
        # bsp_vel = -self._f2f.pframeObservedRelSpVel().toVector6()
        sp_vel = wsp_vel
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
        Q = urdf_to_policy(self._coorddata.getQ()[6:] - self._default_pos)
        obs[12:24] = Q
        # 12 joint velocities
        U = urdf_to_policy(self._coorddata.getU()[6:])
        obs[24:36] = U
        # 12 previous action (the raw policy output)
        obs[36:48] = self._prev_action
        return torch.as_tensor(obs, dtype=torch.float32).view(1, -1)

    def step(self, action: np.ndarray):
        self._af_time_ns = 0
        step_start = time.perf_counter()
        action_scale = 0.2

        # Time observation gathering
        obs_start = time.perf_counter()
        observation = self.get_observation(action)
        with torch.inference_mode():
            policy_action = self._policy(observation)  # -> (1, 12)
        policy_action = policy_action.squeeze(0).cpu().numpy()
        self._prev_action = policy_action
        obs_time = time.perf_counter() - obs_start

        # apply action to joints
        action = policy_to_urdf(policy_action * action_scale)
        Q = self._coorddata.getQ()
        Q[6:] = self._default_pos + action
        self._desired_pos = self._default_pos + action
        
        # Time advanceBy
        advance_start = time.perf_counter()
        self._sp.advanceBy(0.02)
        advance_time = time.perf_counter() - advance_start
        
        # Calculate total step time
        step_time = time.perf_counter() - step_start
        
        # Store timing metrics
        self._step_count += 1
        self._step_times.append(step_time)
        self._observation_times.append(obs_time)
        self._advance_times.append(advance_time)
        self._af_per_step.append(self._af_time_ns)

    def close(self):
        del self._proxy_scene
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()