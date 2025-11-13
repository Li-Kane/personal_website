import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import FromServer, FromSim
from spot_sim.spot import SpotEnv
import numpy as np


class SimSubscriber(Node):

    def __init__(self):
        super().__init__('sim_subscriber')
        self.subscription = self.create_subscription(
            FromServer,
            'from_server',
            self.listener_callback,
            1)
        self.subscription  # prevent unused variable warning
        self.publisher = self.create_publisher(FromSim, 'from_sim', 1)
        timer_period = 0.02
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.sim = SpotEnv(port=3247, render_mode="human")
        self.sim.reset()
        self.action = np.zeros(3)
        self.spot_pos = np.zeros(3)

    def listener_callback(self, msg):
        self.action = np.array([msg.server_data[0], 0.0, msg.server_data[1]])
        self.sim.update_target(np.array([msg.server_data[2], msg.server_data[3]]))

    def timer_callback(self):
        msg = FromSim()
        msg.sim_data = self.sim.step(self.action)
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    try:
        sim_subscriber = SimSubscriber()
        rclpy.spin(sim_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()