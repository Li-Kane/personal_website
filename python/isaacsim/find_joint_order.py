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

CONFIG = {"headless": True}   # headless recommended for streaming
simulation_app = SimulationApp(launch_config=CONFIG)

from isaacsim.core.prims import Articulation
from isaacsim.storage.native import get_assets_root_path
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api import World

# Create a world (needed for physics simulation)
world = World()

# Get asset path
assets_root_path = get_assets_root_path()
usd_path = assets_root_path + "/Isaac/Robots/BostonDynamics/spot/spot.usd"

# Add the robot to the stage
prim_path = "/World/Spot"
add_reference_to_stage(usd_path=usd_path, prim_path=prim_path)

# Reset world to initialize physics
world.reset()

# Create articulation and get DOF names
prim = Articulation(prim_path)
prim.initialize()
print(str(prim.dof_names))

simulation_app.close()