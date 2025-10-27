from isaacsim import SimulationApp

CONFIG = {"headless": True}   # headless recommended for streaming
simulation_app = SimulationApp(launch_config=CONFIG)

# from isaacsim.core.utils.extensions import enable_extension
# # enable_extension("omni.services.livestream.nvcf")
# enable_extension("omni.services.livestream.webrtc")

import gymnasium as gym
from pxr import UsdGeom, Gf
import carb
import numpy as np
from typing import Optional

from isaacsim.core.api import World
from isaacsim.core.utils.prims import define_prim, set_prim_property
from isaacsim.robot.policy.examples.robots import SpotFlatTerrainPolicy
from isaacsim.storage.native import get_assets_root_path

# --- networking / ports: MUST match stream.config.json ---
# HTTP server for signaling + serving the client endpoints
# simulation_app.set_setting('exts."omni.services.transport.server.http".port', 8211)

# # Single fixed UDP media port (easy firewalling)
# simulation_app.set_setting("/app/livestream/port", 49100)

# # Nice-to-haves
# simulation_app.set_setting("/app/window/drawMouse", True)
# simulation_app.set_setting("/app/livestream/allowResize", True)

# helper to wrap angles
def wrap_to_pi(x):
    return (x + np.pi) % (2 * np.pi) - np.pi

class SpotEnv(gym.Env):
    def __init__(self):
        self.size = 30
        self._bound = self.size / 2.0 - 3.0
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
            dtype=np.double,
        )
        high = np.array(
            [self._bound, self._bound, self.size, self.size, 6.0, 6.0, 0.25, 6.0, 1.0, 1.0],
            dtype=np.double,
        )
        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=np.double)

        # define action space
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(3,), dtype=np.double)


        self._init_sim()

        # vars
        self.base_command = np.zeros(3)
        self._terminated = False
        self._agent_pos = None
        self._target_pos = None
        self._agent_vel = None
        self._agent_roll = None
        self._agent_yaw_vel = None
        self._angle_diff = None
        self.np_random = None

    def _init_sim(self):
        # spawn world
        self.world = World(stage_units_in_meters=1.0, physics_dt=1 / 500, rendering_dt=1 / 50)
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")

        # spawn warehouse scene
        prim = define_prim("/World/Ground", "Xform")
        asset_path = assets_root_path + "/Isaac/Environments/Grid/default_environment.usd"
        prim.GetReferences().AddReference(asset_path)

        # add visual cube
        target_prim = define_prim("/World/Cube2", "Cube")
        set_prim_property("/World/Cube2", "size", 0.2)

        # visual properties
        gprim = UsdGeom.Gprim(target_prim)
        gprim.CreateDisplayColorAttr([Gf.Vec3f(1.0, 0.0, 0.0)])
        gprim.CreateDisplayOpacityAttr([1.0])

        # transform properties
        xform = UsdGeom.Xformable(target_prim)
        self.t_op = xform.AddTranslateOp()

        # spawn robot
        self.spot = SpotFlatTerrainPolicy(
            prim_path="/World/Spot",
            name="Spot",
            position=np.array([0, 0, 0.8]),
        )
        self.world.reset()
        self.world.add_physics_callback("physics_step", callback_fn=self._on_physics_step)


    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if self.np_random is None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)

        # init vars
        self.base_command = np.zeros(3)
        self._terminated = False
        self._agent_pos = self.np_random.uniform(-self._bound, self._bound, size=(2,)).astype(
            np.double
        )
        self._target_pos = self.np_random.uniform(-1.0, 1.0, size=(2,)).astype(
            np.double
        )
        # self._agent_vel = np.zeros(2, dtype=np.double)
        # self._agent_roll = np.zeros(1, dtype=np.double)
        # self._agent_yaw_vel = np.zeros(1, dtype=np.double)
        # agent_yaw = self.np_random.uniform(-np.pi, np.pi, size=(1,)).astype(np.double)

        # calculate previous distance and angle difference
        # difference = self._target_pos - self._agent_pos
        # ideal_angle = np.arctan2(difference[1], difference[0])
        # self._distance = np.linalg.norm(difference)
        # self._angle_diff = wrap_to_pi(ideal_angle - agent_yaw)

        # self._angle_diff = None

        # update simulation
        self.t_op.Set(Gf.Vec3d(self._target_pos[0], self._target_pos[1], 0.1))
        self.spot.initialize()
        # self.spot.set_world_pose(
        #     np.array([self._agent_pos[0], self._agent_pos[1], 0.3]), np.array([0, 0, 0, 1])
        # )
        self.world.reset(True)

    def _on_physics_step(self, step_size) -> None:
        self.spot.forward(step_size, self.base_command)

    def step(self, action):
        self.base_command = action
        self.world.step(render=True)
        if self.world.is_stopped():
            self.reset_needed = True
        obs = np.zeros(self.observation_space.shape)  # placeholder
        reward = 0.0  # placeholder
        done = False  # placeholder
        info = {}  # placeholder
        return obs, reward, done, False, info
    
    def close(self):
        self.world = None
        simulation_app.close()

# # robot command
# i = 0
# while simulation_app.is_running():
#     my_world.step(render=True)
#     if my_world.is_stopped():
#         reset_needed = True
#     if my_world.is_playing():
#         if i >= 0 and i < 80:
#             # forward
#             base_command = np.array([2, 0, 0])
#         elif i >= 80 and i < 130:
#             # rotate
#             base_command = np.array([1, 0, 2])
#         elif i >= 130 and i < 200:
#             # side ways
#             base_command = np.array([0, 1, 0])
#         elif i == 200:
#             i = 0
#             print("Reached: ", spot.robot.get_world_pose()[0])
#         # print("Pos: ", spot.robot.get_world_pose()[0])
#         # print("quaternion?: ", spot.robot.get_world_pose()[1])
#         # print("linear vel: ", spot.robot.get_linear_velocity())
#         # print("angular vel: ", spot.robot.get_angular_velocity())
#         t_op.Set(Gf.Vec3d(1.0, 0.0, 0.1))
#         i += 1

# # get world pos seems to return x, y, z


# simulation_app.close()