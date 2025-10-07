# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import gymnasium as gym
from pxr import UsdGeom, Gf

import carb
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.utils.prims import define_prim, set_prim_property
from isaacsim.robot.policy.examples.robots import SpotFlatTerrainPolicy
from isaacsim.storage.native import get_assets_root_path

first_step = True
reset_needed = False

# initialize robot on first step, run robot advance
def on_physics_step(step_size) -> None:
    global first_step
    global reset_needed
    if first_step:
        spot.initialize()
        first_step = False
    elif reset_needed:
        my_world.reset(True)
        reset_needed = False
        first_step = True
    else:
        spot.forward(step_size, base_command)


# spawn world
my_world = World(stage_units_in_meters=1.0, physics_dt=1 / 500, rendering_dt=1 / 50)
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
ops = xform.GetOrderedXformOps()
t_op = xform.AddTranslateOp()

# spawn robot
spot = SpotFlatTerrainPolicy(
    prim_path="/World/Spot",
    name="Spot",
    position=np.array([0, 0, 0.8]),
)
my_world.reset()
my_world.add_physics_callback("physics_step", callback_fn=on_physics_step)

# robot command
base_command = np.zeros(3)

i = 0
while simulation_app.is_running():
    my_world.step(render=True)
    if my_world.is_stopped():
        reset_needed = True
    if my_world.is_playing():
        if i >= 0 and i < 80:
            # forward
            base_command = np.array([2, 0, 0])
        elif i >= 80 and i < 130:
            # rotate
            base_command = np.array([1, 0, 2])
        elif i >= 130 and i < 200:
            # side ways
            base_command = np.array([0, 1, 0])
        elif i == 200:
            i = 0
            print("Reached: ", spot.robot.get_world_pose()[0])
        # print("Pos: ", spot.robot.get_world_pose()[0])
        # print("quaternion?: ", spot.robot.get_world_pose()[1])
        # print("linear vel: ", spot.robot.get_linear_velocity())
        # print("angular vel: ", spot.robot.get_angular_velocity())
        t_op.Set(Gf.Vec3d(1.0, 0.0, 0.1))
        i += 1

# get world pos seems to return x, y, z


simulation_app.close()