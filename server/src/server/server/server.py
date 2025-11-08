import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import Controller


class Server(Node):

    def __init__(self):
        super().__init__('server')
        self.publisher_ = self.create_publisher(Controller, 'controller', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

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