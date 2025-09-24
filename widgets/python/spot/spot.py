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
    Algorithms
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
    ground.setTranslation([0, 0, -0.815])


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

        # initialize the simulation
        self.init_sim(port, sync_real_time)

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(axes=0.5, port=port, local_client='never')
            self._proxy_scene = self._mb.getScene()
            # projection = OrthographicProjection()
            # projection.height = 25.0
            # projection.near = 0.1
            # projection.far = 100.0
            # viz_scene.defaultCamera().setProjection(projection)
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

        # create the environment
        createEnvironment(50, self._proxy_scene)

         # add target object
        # mat_info = PhysicalMaterialInfo()
        # mat_info.color = Color.BLUE
        # blue = PhysicalMaterial(mat_info)

        # create the target
        # target_geom = CylinderGeometry(0.25, 0.05)
        # self._target = ProxyScenePart(
        #     "target_part",
        #     scene=self._proxy_scene,
        #     geometry=target_geom,
        #     material=blue,
        #     layers=LAYER_GRAPHICS,
        # )
        # self._target.setUnitQuaternion(UnitQuaternion([1 / sqrt(2), 0, 0, 1 / sqrt(2)]))
        # self._target_pos = np.zeros(2, dtype=np.float32)

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
        # add the legs to collision detection
        front_left = self._mb.getBody("fl_lleg")
        front_right = self._mb.getBody("fr_lleg")
        hind_left = self._mb.getBody("hl_lleg")
        hind_right = self._mb.getBody("hr_lleg")
        mdl.registerBody(front_left)
        mdl.registerBody(front_right)
        mdl.registerBody(hind_left)
        mdl.registerBody(hind_right)
        mdl.params.kp = 100000
        mdl.params.kc = 20000
        mdl.params.mu = 0.3
        mdl.params.n = 1.5
        mdl.params.linear_region_tol = 1e-3
        self._sp.registerModel(mdl)
        del mdl

        def compensate_gravity(t, x):
            torques = Algorithms.evalGravityCompensation(self._mb)
            self._mb.setT(torques)

        sp_opts.fns.pre_deriv_fns["compensate_gravity"] = compensate_gravity

    def step(self):
        # simulation
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())

        # setup timed event (every 0.01s)
        h = np.timedelta64(int(1e7), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t

        self._sp.advanceBy(10.0)

    def close(self):
        del self._proxy_scene, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()