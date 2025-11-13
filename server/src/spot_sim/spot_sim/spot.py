import os
from typing import Optional, cast
import numpy as np
from math import sqrt
from ament_index_python.packages import get_package_share_directory
import time

from spot_sim.onnx_policy import ONNXSpotPolicy
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

class SpotEnv():
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
        onnx_path = os.path.join(get_package_share_directory('spot_sim'), "resources", "spot_policy.onnx")
        self._policy = ONNXSpotPolicy(onnx_path)
        self.obs = np.zeros(48)

        # initialize the simulation
        self.init_sim(port, sync_real_time)
        
        # Timing metrics
        self.step_count = 0
        self.total_step_time = 0.0
        self.total_inference_time = 0.0
        self.total_advanceby_time = 0.0
        self.total_python_ops_time = 0.0
        self.log_interval = 100  # Log every 100 steps

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

        # Set penalty contact model parameters
        hc = HuntCrossley("hunt_crossley_contact")
        hc.params.kp = 5e5
        hc.params.kc = 2e5
        hc.params.mu = 1.0
        hc.params.n = 1.5
        hc.params.linear_region_tol = 1e-40

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

        # setup physics timed event (every 0.2 ms)
        h = np.timedelta64(int(2e5), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

    def update_target(self, position: np.ndarray):
        self._target.setTranslation([position[0], position[1], -0.5])

    def reset(self):
        self._mb.resetData()

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
        # 3 base_lin_vel
        self.obs[:3] = np.matmul(transform, wsp_vel[3:6])
        # 3 base_ang_vel
        self.obs[3:6] = np.matmul(transform, wsp_vel[0:3])
        # 3 gravity
        proj_gravity = self._body.getGravAccel()
        self.obs[6:9] = proj_gravity / np.linalg.norm(proj_gravity)
        # 3 command
        self.obs[9:12] = action
        # 12 joint offset (current_joint_pos - default_pos)
        self.obs[12:24] = urdf_to_policy(self._coorddata.getQ()[6:] - DEFAULT_POS)
        # 12 joint velocities
        self.obs[24:36] = urdf_to_policy(self._coorddata.getU()[6:])
        # 12 previous action (the raw policy output)
        self.obs[36:48] = self._prev_action
        return self.obs.astype(np.float32) 

    # def step(self, action: int):
    def step(self, action: np.ndarray):
        step_start = time.perf_counter()
        
        # Time observation preparation (Python ops)
        python_ops_start = time.perf_counter()
        observation = self.get_policy_observation(action)
        python_ops_end = time.perf_counter()
        
        # Time inference
        inference_start = time.perf_counter()
        policy_action = self._policy(observation)  # -> (12,) NumPy array
        inference_end = time.perf_counter()
        
        # Time Python operations (action processing)
        python_ops2_start = time.perf_counter()
        self._prev_action = policy_action

        # apply action to joints
        action = policy_to_urdf(policy_action * 0.2) # use 0.2 from isaacsim
        self._desired_pos = DEFAULT_POS + action
        python_ops2_end = time.perf_counter()

        # Time advanceBy
        advanceby_start = time.perf_counter()
        self._sp.advanceBy(0.02)
        advanceby_end = time.perf_counter()

        # Time final Python operations (update vars and checks)
        python_ops3_start = time.perf_counter()
        # update values
        self._proxy_scene.update()
        transform = self._f2f.relTransform().toVector6()
        self._agent_pos = transform[3:5]
        self._agent_yaw = transform[2]

        # check for numerical instability or falling over
        U = self._coorddata.getUdot()
        if np.any(np.abs(U) > 1e5) or abs(transform[5]) > 0.5:
            self.reset()
            python_ops3_end = time.perf_counter()
            step_end = time.perf_counter()
            
            # Still update metrics even on reset
            self._update_metrics(
                step_end - step_start,
                inference_end - inference_start,
                advanceby_end - advanceby_start,
                (python_ops_end - python_ops_start) + 
                (python_ops2_end - python_ops2_start) + 
                (python_ops3_end - python_ops3_start)
            )
            return [0.0, 0.0, 0.0]
        
        python_ops3_end = time.perf_counter()
        step_end = time.perf_counter()
        
        # Update metrics
        self._update_metrics(
            step_end - step_start,
            inference_end - inference_start,
            advanceby_end - advanceby_start,
            (python_ops_end - python_ops_start) + 
            (python_ops2_end - python_ops2_start) + 
            (python_ops3_end - python_ops3_start)
        )
        
        return [self._agent_pos[0], self._agent_pos[1], self._agent_yaw]
    
    def _update_metrics(self, step_time, inference_time, advanceby_time, python_ops_time):
        """Update and log timing metrics."""
        self.total_step_time += step_time
        self.total_inference_time += inference_time
        self.total_advanceby_time += advanceby_time
        self.total_python_ops_time += python_ops_time
        self.step_count += 1
        
        # Log metrics periodically
        if self.step_count % self.log_interval == 0:
            avg_step = self.total_step_time / self.step_count * 1000  # ms
            avg_inference = self.total_inference_time / self.step_count * 1000  # ms
            avg_advanceby = self.total_advanceby_time / self.step_count * 1000  # ms
            avg_python_ops = self.total_python_ops_time / self.step_count * 1000  # ms
            
            inference_pct = (self.total_inference_time / self.total_step_time * 100) if self.total_step_time > 0 else 0
            advanceby_pct = (self.total_advanceby_time / self.total_step_time * 100) if self.total_step_time > 0 else 0
            python_ops_pct = (self.total_python_ops_time / self.total_step_time * 100) if self.total_step_time > 0 else 0
            
            print(f"[Spot Metrics after {self.step_count} steps]")
            print(f"  Total step: {avg_step:.3f}ms (100%)")
            print(f"  Inference: {avg_inference:.3f}ms ({inference_pct:.1f}%)")
            print(f"  AdvanceBy: {avg_advanceby:.3f}ms ({advanceby_pct:.1f}%)")
            print(f"  Python ops: {avg_python_ops:.3f}ms ({python_ops_pct:.1f}%)")
            print(f"  Other: {avg_step - avg_inference - avg_advanceby - avg_python_ops:.3f}ms ({100 - inference_pct - advanceby_pct - python_ops_pct:.1f}%)")

    def close(self):
        del self._proxy_scene, self._body, self._f2f, self._root_hinge, self._coorddata, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()