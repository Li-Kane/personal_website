"""
Unified server combining WebSocket handling and Spot simulation.
Runs in a single event loop without ROS2 or multithreading.
"""

import asyncio
import websockets
import json
import numpy as np
import time
from typing import Optional

from spot import SpotEnv


# Camera/raycast constants (from original server)
# fov = 50, near = 0.1, far = 2000
TAN_HALF_FOV = np.tan(np.radians(50.0) / 2)
# construct basis vectors
# offset = [0.0, 15.0, 10.0], target = [0, 5, 0], up = [0, 0, 1]
FORWARD = np.array([0.0, -10.0, -10.0])
FORWARD_DIR = FORWARD / np.linalg.norm(FORWARD)
RIGHT = np.cross(FORWARD_DIR, np.array([0, 0, 1]))
RIGHT_DIR = RIGHT / np.linalg.norm(RIGHT)
UP = np.cross(RIGHT_DIR, FORWARD_DIR)
UP_DIR = UP / np.linalg.norm(UP)
GROUND_DIST = -0.525 - 10.0


class SpotServer:
    """Unified server handling WebSocket connections and simulation."""
    
    def __init__(self, render_mode: Optional[str] = "human", port: int = 3247):
        # Initialize simulation
        self.sim = SpotEnv(port=port, render_mode=render_mode)
        self.sim.reset()
        
        # Robot state
        self.spot_pos = np.zeros(2)
        self.spot_yaw = 0.0
        self.action = np.zeros(3)
        self.target_pos = np.array([-5.0, 5.0])
        
        # WebSocket state
        self.mouse_x = 0
        self.mouse_y = 0
        self.ratio = 1.0
        
        # Timing
        self.last_sim_step = time.time()
        self.last_target_update = time.time()
        
        # WebSocket server
        self.websocket_clients = set()
    
    def compute_command_to_target(
        self,
        max_forward_vel: float = 2.0,
        max_angular_vel: float = 2.0,
    ) -> np.ndarray:
        """Compute velocity commands to reach target position."""
        # 1. Compute vector from robot to target (world frame)
        delta = self.target_pos - self.spot_pos
        distance = np.linalg.norm(delta)
        if distance < 0.6:
            return np.array([0.0, 0.0, 0.0])
        
        # 2. Compute desired heading angle (world frame)
        desired_yaw = np.arctan2(delta[1], delta[0])
        
        # 3. Compute heading error (wrapped to [-pi, pi])
        yaw_error = desired_yaw - self.spot_yaw
        yaw_error = np.arctan2(np.sin(yaw_error), np.cos(yaw_error))

        # 4. Generate commands
        forward_vel = np.tanh(distance) * max_forward_vel * np.cos(yaw_error)
        angular_vel = np.clip(2.0 * yaw_error, -max_angular_vel, max_angular_vel)
        # Sideways velocity: typically 0 for "head first" pursuit
        return np.array([forward_vel, 0.0, angular_vel])
    
    def raycast_to_ground(self) -> np.ndarray:
        """Convert mouse position to world coordinates on ground plane."""
        # fov = 50, near = 0.1, far = 2000
        ray_x = self.mouse_x * self.ratio * TAN_HALF_FOV
        ray_y = self.mouse_y * TAN_HALF_FOV
        ray_dir = np.array([ray_x, ray_y, 1.0])

        # transform ray to world space
        world_ray_dir = (ray_dir[0] * RIGHT_DIR +
                         ray_dir[1] * UP_DIR +
                         ray_dir[2] * FORWARD_DIR)
        world_ray_dir /= np.linalg.norm(world_ray_dir)

        # trace (we know the ground is at -0.525)
        t = GROUND_DIST / world_ray_dir[2]
        ground_x = t * world_ray_dir[0]
        ground_y = 15.0 + t * world_ray_dir[1]
        return np.array([ground_x, ground_y])
    
    def update_mouse_position(self, x: float, y: float, ratio: float):
        """Update mouse position from WebSocket."""
        self.mouse_x = x
        self.mouse_y = y
        self.ratio = ratio
    
    async def handle_websocket(self, websocket):
        """Handle WebSocket connections and messages."""
        # Register client
        self.websocket_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    x = data.get('x', 0)
                    y = data.get('y', 0)
                    ratio = data.get('ratio', 1)
                    
                    # Update mouse position
                    self.update_mouse_position(x, y, ratio)
                    
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        finally:
            # Unregister client
            self.websocket_clients.discard(websocket)
    
    async def simulation_loop(self):
        """Main simulation loop running at specified intervals."""
        while True:
            current_time = time.time()
            
            # Run simulation step every 0.03 seconds (33.33 Hz)
            if current_time - self.last_sim_step >= 0.03:
                # Step the simulation with current action
                sim_data = self.sim.step(self.action)
                
                # Update robot state from simulation
                self.spot_pos = np.array([sim_data[0], sim_data[1]])
                self.spot_yaw = sim_data[2]
                
                self.last_sim_step = current_time
            
            # Update target position every 0.1 seconds (10 Hz)
            if current_time - self.last_target_update >= 0.1:
                # Update target based on mouse position
                self.target_pos = self.raycast_to_ground()
                self.sim.update_target(self.target_pos)
                
                # Compute new action based on target
                forward_vel, _, angular_vel = self.compute_command_to_target()
                self.action = np.array([forward_vel, 0.0, angular_vel])
                
                self.last_target_update = current_time
            
            # Small sleep to prevent busy-waiting (check every 5ms)
            await asyncio.sleep(0.005)
    
    async def run(self, host: str = '0.0.0.0', ws_port: int = 8080):
        """Start the server with WebSocket and simulation loop."""
        print(f"Starting Spot Server...")
        print(f"WebSocket server on ws://{host}:{ws_port}")
        
        # Start WebSocket server
        async with websockets.serve(self.handle_websocket, host, ws_port):
            print("WebSocket server started")
            
            # Run simulation loop
            await self.simulation_loop()


def main():
    """Main entry point."""
    # Create server with visualization enabled
    server = SpotServer(render_mode="human", port=3247)
    
    # Run the async event loop
    try:
        asyncio.run(server.run(host='0.0.0.0', ws_port=8080))
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.sim.close()


if __name__ == '__main__':
    main()
