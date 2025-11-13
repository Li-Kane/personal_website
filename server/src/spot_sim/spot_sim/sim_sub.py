import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import FromServer, FromSim
from spot_sim.spot import SpotEnv
import numpy as np
import time


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
        
        # Timing metrics
        self.step_count = 0
        self.total_step_time = 0.0
        self.total_publish_time = 0.0
        self.log_interval = 100  # Log every 100 steps

    def listener_callback(self, msg):
        self.action = np.array([msg.server_data[0], 0.0, msg.server_data[1]])
        self.sim.update_target(np.array([msg.server_data[2], msg.server_data[3]]))

    def timer_callback(self):
        msg = FromSim()
        
        # Time the sim step
        step_start = time.perf_counter()
        msg.sim_data = self.sim.step(self.action)
        step_end = time.perf_counter()
        step_time = step_end - step_start
        
        # Time the publish
        publish_start = time.perf_counter()
        self.publisher.publish(msg)
        publish_end = time.perf_counter()
        publish_time = publish_end - publish_start
        
        # Update metrics
        self.total_step_time += step_time
        self.total_publish_time += publish_time
        self.step_count += 1
        
        # Log metrics periodically
        if self.step_count % self.log_interval == 0:
            avg_step = self.total_step_time / self.step_count * 1000  # ms
            avg_publish = self.total_publish_time / self.step_count * 1000  # ms
            publish_ratio = (self.total_publish_time / self.total_step_time * 100) if self.total_step_time > 0 else 0
            
            self.get_logger().info(
                f"[Metrics after {self.step_count} steps] "
                f"Avg step: {avg_step:.3f}ms, Avg publish: {avg_publish:.3f}ms, "
                f"Publish/Step ratio: {publish_ratio:.2f}%"
            )

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