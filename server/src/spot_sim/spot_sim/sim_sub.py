import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import Controller
from spot_sim.spot import SpotEnv
import numpy as np


class SimSubscriber(Node):

    def __init__(self):
        super().__init__('sim_subscriber')
        self.subscription = self.create_subscription(
            Controller,
            'controller',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        timer_period = 0.02
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.sim = SpotEnv(port=3247, render_mode="human")
        self.sim.reset()
        self.action = np.zeros(3)

    def listener_callback(self, msg):
        self.action = np.array([msg.forward_vel, 0.0, msg.angular_vel])

    def timer_callback(self):
        self.sim.step(self.action)

def main(args=None):
    try:
        with rclpy.init(args=args):
            sim_subscriber = SimSubscriber()

            rclpy.spin(sim_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

if __name__ == '__main__':
    main()