import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import Controller


class SimSubscriber(Node):

    def __init__(self):
        super().__init__('sim_subscriber')
        self.subscription = self.create_subscription(
            Controller,
            'controller',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%f"' % msg.forward_vel)
        self.get_logger().info('I heard: "%f"' % msg.angular_vel)


def main(args=None):
    try:
        with rclpy.init(args=args):
            sim_subscriber = SimSubscriber()

            rclpy.spin(sim_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()

def main(args=None):
    try:
        with rclpy.init(args=args):
            sim_subscriber = SimSubscriber()

            rclpy.spin(sim_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()