import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from std_msgs.msg import Bool
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
        self.status_subscriber = self.create_subscription(
            Bool,
            'server_in_use',
            self.status_callback,
            5)
        self.status_subscriber  # prevent unused variable warning
        self.publisher = self.create_publisher(FromSim, 'from_sim', 1)
        timer_period = 0.03
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # init vars
        self.sim = SpotEnv(port=3247, render_mode="human")
        self.running = False
        self.action = np.zeros(3)
        self.spot_pos = np.zeros(3)

    def status_callback(self, msg):
        self.sim.reset()
        self.running = msg.data

    def listener_callback(self, msg):
        if self.running:
            self.action = np.array([msg.server_data[0], 0.0, msg.server_data[1]])
            self.sim.update_target(np.array([msg.server_data[2], msg.server_data[3]]))

    def timer_callback(self):
        if self.running:
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