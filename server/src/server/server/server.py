import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import Controller
import numpy as np


class Server(Node):

    def __init__(self):
        super().__init__('server')
        self.publisher_ = self.create_publisher(Controller, 'controller', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def compute_command_to_target(
        robot_pos: np.ndarray,      # [x, y] in world frame
        robot_yaw: float,            # current heading in radians
        target_pos: np.ndarray,      # [x, y] in world frame
        max_forward_vel: float = 2.0,
        max_angular_vel: float = 2.0,
    ) -> np.ndarray:
        """
        Compute [forward, sideways, yaw_rate] command to reach target.
        Returns: np.ndarray([f, s, y]) - robot-relative velocities
        """
        # 1. Compute vector from robot to target (world frame)
        delta = target_pos - robot_pos
        distance = np.linalg.norm(delta)
        
        # 2. Compute desired heading angle (world frame)
        desired_yaw = np.arctan2(delta[1], delta[0])
        
        # 3. Compute heading error (wrapped to [-pi, pi])
        yaw_error = desired_yaw - robot_yaw
        yaw_error = np.arctan2(np.sin(yaw_error), np.cos(yaw_error))
        
        # 4. Generate commands
        # Forward velocity: proportional to distance, reduced when misaligned
        forward_vel = np.tanh(distance) * max_forward_vel * np.cos(yaw_error)
        
        # Angular velocity: proportional to heading error
        angular_vel = np.clip(2.0 * yaw_error, -max_angular_vel, max_angular_vel)
        
        # Sideways velocity: typically 0 for "head first" pursuit
        sideways_vel = 0.0
        
        return np.array([forward_vel, sideways_vel, angular_vel])

    def timer_callback(self):
        msg = Controller()
        msg.forward_vel = float(self.i) * 0.1
        msg.angular_vel = float(self.i) * 0.1
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)
        self.i += 1

def main(args=None):
    try:
        with rclpy.init(args=args):
            server = Server()

            rclpy.spin(server)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()