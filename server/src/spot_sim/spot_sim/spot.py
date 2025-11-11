import os
from typing import Optional, cast
import numpy as np
import gymnasium as gym
import torch
from math import sqrt
from ament_index_python.packages import get_package_share_directory

from spot_sim.helpers import (
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
GROUND_SIZE = 50.0
BOUND = GROUND_SIZE / 2.0 - 2.0

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
        policy_path = os.path.join(get_package_share_directory('spot_sim'), "resources", "spot_policy.pt")
        self._policy = torch.jit.load(policy_path, map_location="cpu")
        self._policy.eval()

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
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(axes=0.0, port=port, local_client='never')
            viz_scene.defaultCamera().pointCameraAt(
                [0.0, 15.0, 10.0], [0, 5, 0,], [0, 0, 1],
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
        hc.params.kp = 1e6
        hc.params.kc = 5e5
        hc.params.mu = 1.0
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

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())
        self._proxy_scene.update()

        # setup timed event (every 0.5 ms)
        h = np.timedelta64(int(2e5), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

    def update_target(self, position: np.ndarray):
        self._target.setTranslation([position[0], position[1], -0.5])

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self._mb.resetData()
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)

        # init vars
        self._agent_yaw = np.float32(0.0)
        self._agent_pos = np.zeros(2, dtype=np.float32)
        self._prev_action = np.zeros(12, dtype=np.float32)
        
        # set sim according to vars
        self._root_hinge.fitQ(
            HomTran(vec=np.zeros(3))
        )
        self._desired_pos = DEFAULT_POS
        Q = self._coorddata.getQ()
        Q[6:] = self._desired_pos
        self._coorddata.setQ(Q)

        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())
        self._proxy_scene.update()
        self._sp.advanceBy(0.01)

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

    # def step(self, action: int):
    def step(self, action: np.ndarray):
        # Time observation gathering
        observation = self.get_policy_observation(action)
        with torch.inference_mode():
            policy_action = self._policy(observation)  # -> (1, 12)
        policy_action = policy_action.squeeze(0).cpu().numpy()
        self._prev_action = policy_action

        # apply action to joints
        action = policy_to_urdf(policy_action * 0.2) # use 0.2 from isaacsim
        Q = self._coorddata.getQ()
        Q[6:] = DEFAULT_POS + action
        self._desired_pos = DEFAULT_POS + action

        # Time advanceBy
        self._sp.advanceBy(0.02)

        # update vars
        transform = self._f2f.relTransform().toVector6()
        self._agent_pos = transform[3:5]
        self._agent_yaw = transform[2]

        # check for numerical instability or falling over
        U = self._coorddata.getUdot()
        if np.any(np.abs(U) > 1e5) or abs(transform[5]) > 0.5:
            self.reset()
            return [0.0, 0.0, 0.0]
        return  [self._agent_pos[0], self._agent_pos[1], self._agent_yaw]

    def close(self):
        del self._proxy_scene, self._body, self._f2f, self._root_hinge, self._coorddata, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()