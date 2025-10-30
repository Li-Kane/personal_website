import numpy as np
from math import pi
from typing import cast
import gymnasium as gym
from typing import Optional

from Karana.Frame import FrameContainer
from Karana.Core import discard, allFinalized, allDestroyed
from Karana.Dynamics import (
    Multibody,
    HINGE_TYPE,
    StatePropagator,
    TimedEvent,
    PhysicalBody,
    PhysicalHinge,
    LockedSubhinge,
    PinSubhinge,
)
from Karana.Math import UnitQuaternion, HomTran, SpatialInertia
from Karana.Scene import (
    BoxGeometry,
    CylinderGeometry,
    Color,
    PhysicalMaterialInfo,
    PhysicalMaterial,
    LAYER_GRAPHICS,
)
from Karana.Scene import ProxyScenePart, ProxyScene
from Karana.Models import UniformGravity, UpdateProxyScene, SyncRealTime
from Karana.Math import IntegratorType


# create a cart and a pole1 multibody system
def create_multibody(
    fc: FrameContainer,
) -> tuple[LockedSubhinge, PinSubhinge, PinSubhinge, Multibody]:
    mb = Multibody("mb", fc)

    # add a cart of mass 1.0kg and 0.4 x 0.2 x 0.15 (L, W, H)
    # on a left and right slider
    cart = PhysicalBody("cart", mb)
    cart.setSpatialInertia(SpatialInertia(1.0, np.zeros(3), np.eye(3)))
    slider_hinge = PhysicalHinge(mb.virtualRoot(), cart, HINGE_TYPE.LOCKED)
    slider_subhinge = cast(LockedSubhinge, slider_hinge.subhinge(0))
    cart_to_slider = HomTran([0, 0, 0])
    cart.setBodyToJointTransform(cart_to_slider)

    # add pole1 of mass 0.1 kg, and 0.02 x 0.5 (R, L)
    # on a pin joint
    pole1 = PhysicalBody("pole1", mb)
    inertia_matrix = np.diag([0.0020933, 0.0020933, 0.00002])
    pole1.setSpatialInertia(SpatialInertia(0.1, [0, 0, 0], inertia_matrix))
    pin1_hinge = PhysicalHinge(cart, pole1, HINGE_TYPE.PIN)
    pole1_to_pin1 = HomTran([0.0, 0.0, -(0.5 / 2.0)])
    pole1.setBodyToJointTransform(pole1_to_pin1)
    cart_to_pin1 = HomTran([0.0, 0.0, 0.15 / 2.0])
    pin1_hinge.onode().setBodyToNodeTransform(cart_to_pin1)
    pin1_subhinge = cast(PinSubhinge, pin1_hinge.subhinge(0))
    pin1_subhinge.setUnitAxis([0, 1, 0])

    # add pole2 of mass 0.1 kg, and 0.02 x 0.5 (R, L)
    # on a pin joint
    pole2 = PhysicalBody("pole2", mb)
    inertia_matrix = np.diag([0.0020933, 0.0020933, 0.00002])
    pole2.setSpatialInertia(SpatialInertia(0.1, [0, 0, 0], inertia_matrix))
    pin2_hinge = PhysicalHinge(pole1, pole2, HINGE_TYPE.PIN)
    pole2_to_pin2 = HomTran([0.0, 0.0, -(0.5 / 2.0)])
    pole2.setBodyToJointTransform(pole2_to_pin2)
    pin1_to_pin2 = HomTran([0.0, 0.0, (0.5 / 2.0)])
    pin2_hinge.onode().setBodyToNodeTransform(pin1_to_pin2)
    pin2_subhinge = cast(PinSubhinge, pin2_hinge.subhinge(0))
    pin2_subhinge.setUnitAxis([0, 1, 0])

    # check
    mb.ensureCurrent()
    mb.resetData()
    assert allFinalized()
    return slider_subhinge, pin1_subhinge, pin2_subhinge, mb


# add a visual rectangle and cylinder
def add_geometries(mb: Multibody, proxy_scene: ProxyScene) -> None:
    box_geom = BoxGeometry(0.4, 0.2, 0.15)
    cylinder_geom = CylinderGeometry(0.02, 0.5)
    mat_info = PhysicalMaterialInfo()
    mat_info.color = Color.FIREBRICK
    firebrick = PhysicalMaterial(mat_info)
    mat_info.color = Color.GOLD
    gold = PhysicalMaterial(mat_info)
    mat_info.color = Color.CRIMSON
    beige = PhysicalMaterial(mat_info)
    mat_info.color = Color.WHITE
    white = PhysicalMaterial(mat_info)

    # add geometry to bodies
    cart_body = ProxyScenePart(
        "cart_body", scene=proxy_scene, geometry=box_geom, material=firebrick
    )
    cart_body.attachTo(mb.getBody("cart"))
    pole1_body = ProxyScenePart(
        "pole1_body", scene=proxy_scene, geometry=cylinder_geom, material=gold
    )
    pole1_body.setUnitQuaternion(UnitQuaternion(pi / 2, [1, 0, 0]))
    pole1_body.attachTo(mb.getBody("pole1"))
    pole2_body = ProxyScenePart(
        "pole2_body", scene=proxy_scene, geometry=cylinder_geom, material=beige
    )
    pole2_body.setUnitQuaternion(UnitQuaternion(pi / 2, [1, 0, 0]))
    pole2_body.attachTo(mb.getBody("pole2"))

    # add a floor
    ground_geom = BoxGeometry(20, 20, 0.5)
    ground = ProxyScenePart(
        "ground", scene=proxy_scene, geometry=ground_geom, material=white, layers=LAYER_GRAPHICS
    )
    ground.setTranslation([0, 0, -0.325])


class TwoLinkCartPoleEnv(gym.Env):
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
        self._force_magnitude = 10.0

        # init simulation
        self.init_sim(port=port, sync_real_time=sync_real_time)

    def init_sim(self, port: int = 0, sync_real_time: bool = False):
        self._fc = FrameContainer("root")
        self._slider, self._pin1, self._pin2, self._mb = create_multibody(self._fc)

        # add visuals
        if self.render_mode == "human":
            self._cleanup_graphics, web_scene = self._mb.setupGraphics(port=port, axes=0)
            self._proxy_scene = self._mb.getScene()
            web_scene.defaultCamera().pointCameraAt([0, 3, 1], [0, 0, 0], [0, 0, 1])
            add_geometries(self._mb, self._proxy_scene)
        else:
            self._proxy_scene = ProxyScene(f"{self._mb.name()}_proxyscene", self._mb.virtualRoot())

        # add models
        self._sp = StatePropagator(self._mb, integrator_type=IntegratorType.RK4)
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
        sp_opts = self._sp.getOptions()

        def apply_forces(t, x):
            self._pin1.setT(self.calculate_torque(self._pin1.getQ(), self._desired_pin1_pos))
            self._pin2.setT(self.calculate_torque(self._pin2.getQ(), self._desired_pin2_pos))

        sp_opts.fns.pre_deriv_fns["apply_forces"] = apply_forces

    def close(self):
        del self._slider, self._pin1, self._pin2, self._proxy_scene
        discard(self._sp)
        if self.render_mode == "human":
            self._cleanup_graphics()
        discard(self._mb)
        discard(self._fc)
        assert allDestroyed()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if not self.np_random:
            self.np_random, _ = gym.utils.seeding.np_random(seed)

        # init values
        self._pin1_pos = self.np_random.uniform(-0.1, 0.1)
        self._pin1_vel = self.np_random.uniform(-0.1, 0.1)
        self._pin2_pos = self.np_random.uniform(-0.1, 0.1)
        self._pin2_vel = self.np_random.uniform(-0.1, 0.1)

        # set our state
        self._mb.resetData()
        self._pin1.setQ(self._pin1_pos)
        self._pin1.setU(self._pin1_vel)
        self._pin2.setQ(self._pin2_pos)
        self._pin2.setU(self._pin2_vel)
        t_init = np.timedelta64(0, "ns")
        self._sp.setState(t_init, self._mb.dynamicsToState())

        # setup timed event
        h = np.timedelta64(int(2e6), "ns")
        t = TimedEvent("hop_size", h, lambda _: None, False)
        t.period = h
        self._sp.registerTimedEvent(t)
        del t
        self._proxy_scene.update()

    def calculate_torque(self, current_pos: float, desired_pos: float) -> float:
        max_effort = 45.0
        kp = 60.0
        return np.clip(
            kp * (desired_pos - current_pos),
            -max_effort,
            max_effort,
        )

    def step(self, action: np.ndarray):
        self._desired_pin1_pos = self._pin1_pos + action[0]
        self._desired_pin2_pos = self._pin2_pos + action[1]
        self._sp.advanceBy(0.02)