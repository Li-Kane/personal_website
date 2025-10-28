from typing import Optional, cast
import numpy as np
import gymnasium as gym
from pathlib import Path
from math import pi, sqrt

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
    StatePropagator,
    TimedEvent,
    PhysicalBody,
    PhysicalHinge,
    Algorithms
)
from Karana.Math import UnitQuaternion, HomTran
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

        # init vars
        self._agent_pos = np.array([0.0, 0.0])

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        # setup bodies and scene
        self._fc = FrameContainer("root")
        self._mb = createMbody(self._fc)

        # obtain all the necessary joints
        self._fl_hip = cast(PhysicalHinge, self._mb.getBody("fl_hip").parentHinge()).subhinge(0)
        self._fr_hip = cast(PhysicalHinge, self._mb.getBody("fr_hip").parentHinge()).subhinge(0)
        self._hl_hip = cast(PhysicalHinge, self._mb.getBody("hl_hip").parentHinge()).subhinge(0)
        self._hr_hip = cast(PhysicalHinge, self._mb.getBody("hr_hip").parentHinge()).subhinge(0)
        self._fl_uleg = cast(PhysicalHinge, self._mb.getBody("fl_uleg").parentHinge()).subhinge(0)
        self._fr_uleg = cast(PhysicalHinge, self._mb.getBody("fr_uleg").parentHinge()).subhinge(0)
        self._hl_uleg = cast(PhysicalHinge, self._mb.getBody("hl_uleg").parentHinge()).subhinge(0)
        self._hr_uleg = cast(PhysicalHinge, self._mb.getBody("hr_uleg").parentHinge()).subhinge(0)
        self._fl_lleg = cast(PhysicalHinge, self._mb.getBody("fl_lleg").parentHinge()).subhinge(0)
        self._fr_lleg = cast(PhysicalHinge, self._mb.getBody("fr_lleg").parentHinge()).subhinge(0)
        self._hl_lleg = cast(PhysicalHinge, self._mb.getBody("hl_lleg").parentHinge()).subhinge(0)
        self._hr_lleg = cast(PhysicalHinge, self._mb.getBody("hr_lleg").parentHinge()).subhinge(0)

        # attach a frame2frame to the spot base
        self._f2f = cast(PhysicalBody, self._mb.virtualRoot()).frame2Frame(
            self._mb.getBody("body")
        )
        self._root_hinge = cast(PhysicalHinge, self._mb.getBody("body").parentHinge())

        # setup graphics if enabled
        if self.render_mode == "human":
            self._cleanup_graphics, viz_scene = self._mb.setupGraphics(axes=0.5, port=port, local_client='never')
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

        # for visualization
        if sync_real_time:
            self._sp.registerModel(SyncRealTime("sync_real_time", 1.0))

        # update proxy scene model
        self._sp.registerModel(UpdateProxyScene("update_proxy_scene", self._proxy_scene))

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        self._agent_pos = np.random.uniform(-10.0, 10.0, size=(2,))
        
        # print(self._fl_uleg.subhingeType())
        # self._fl_uleg.setQ(pi)
        # self._hl_hip.setQ(pi)
        self._root_hinge.fitQ(
            HomTran(vec=np.array([self._agent_pos[0], self._agent_pos[1], 0.0]))
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

    # def action_to_subhinges(self, action: np.ndarray):
    #     self._fl_hx.sol(action[0])

    def get_observation(self):
        # base linear velocity
        
        # return zero observation for now
        return np.zeros(0)

    def step(self):
        self._sp.advanceBy(10.0)

    def close(self):
        del self._proxy_scene, self._target
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()