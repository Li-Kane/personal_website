# SPDX-FileCopyrightText: 2026 Kane Li <kaneli200456@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import numpy as np
import threading

# ros2 boolean msg type
from std_msgs.msg import Bool
from sim_interfaces.msg import FromServer, FromSim
from server.websocket import run_websocket_server

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

class Server(Node):

    def __init__(self):
        super().__init__('server')
        self.subscription = self.create_subscription(
            FromSim,
            'from_sim',
            self.listener_callback,
            1)
        self.subscription
        timer_period = 0.1
        self.publisher_ = self.create_publisher(FromServer, 'from_server', 1)
        self.status_publisher_ = self.create_publisher(Bool, 'server_in_use', 5)
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # init vars
        self.spot_pos = np.zeros(2)
        self.spot_yaw = 0.0
        self.target_pos = np.array([-5.0, 5.0])
        
        # WebSocket vars
        self.mouse_x = 0
        self.mouse_y = 0
        self.ratio = 1.0

    def compute_command_to_target(
        self,
        max_forward_vel: float = 2.0,
        max_angular_vel: float = 2.0,
    ) -> np.ndarray:
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

    # callback when receiving spot position from sim
    def listener_callback(self, msg):
        self.spot_pos = np.array([msg.sim_data[0], msg.sim_data[1]])
        self.spot_yaw = msg.sim_data[2]

    # callback to send command to sim
    def timer_callback(self):
        self.target_pos = self.raycast_to_ground()
        forward_vel, _, angular_vel = self.compute_command_to_target()
        msg = FromServer()
        msg.server_data = [forward_vel, angular_vel, self.target_pos[0], self.target_pos[1]]
        self.publisher_.publish(msg)
    
    def update_mouse_position(self, x, y, ratio):
        """Update mouse position from WebSocket"""
        self.mouse_x = x
        self.mouse_y = y
        self.ratio = ratio

    def update_ws_status(self, status_msg):
        """Update WebSocket status message so we know to open or close the sim"""
        status_msg_ros = Bool()
        status_msg_ros.data = status_msg
        self.status_publisher_.publish(status_msg_ros)

    def raycast_to_ground(self):
        """Convert mouse position to world coordinates on ground plane"""
        # fov = 50, near = 0.1, far = 2000
        ray_x = self.mouse_x * self.ratio * TAN_HALF_FOV
        ray_y = self.mouse_y * TAN_HALF_FOV
        ray_dir = np.array([ray_x, ray_y, 1.0])

        # transform ray to world space
        world_ray_dir = (ray_dir[0] * RIGHT_DIR +
                         ray_dir[1] * UP_DIR +
                         ray_dir[2] * FORWARD_DIR)
        world_ray_dir /= np.linalg.norm(world_ray_dir)

        # trace ( we know the gorund is at -0.525)
        t = GROUND_DIST / world_ray_dir[2]
        ground_x = t * world_ray_dir[0]
        ground_y = 15.0 + t * world_ray_dir[1]
        return np.array([ground_x, ground_y])

def main(args=None):
    rclpy.init(args=args)
    try:
        server = Server()
        
        # Start WebSocket server in a separate thread
        ws_thread = threading.Thread(target=run_websocket_server, args=(server,), daemon=True)
        ws_thread.start()

        rclpy.spin(server)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()