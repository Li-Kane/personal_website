import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import FromServer, FromSim
import numpy as np


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
        self.publisher_ = self.create_publisher(FromServer, 'from_server', 10)
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # init vars
        self.spot_pos = np.zeros(2)
        self.spot_yaw = 0.0
        self.target_pos = np.array([-5.0, 5.0])

    def compute_command_to_target(
        self,
        max_forward_vel: float = 2.0,
        max_angular_vel: float = 2.0,
    ) -> np.ndarray:
        """
        Compute [forward, sideways, yaw_rate] command to reach target.
        Returns: np.ndarray([f, s, y]) - robot-relative velocities
        """
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
        forward_vel, _, angular_vel = self.compute_command_to_target()
        msg = FromServer()
        msg.server_data = [forward_vel, angular_vel, self.target_pos[0], self.target_pos[1]]
        self.publisher_.publish(msg)

def main(args=None):
    try:
        with rclpy.init(args=args):
            server = Server()

            rclpy.spin(server)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()