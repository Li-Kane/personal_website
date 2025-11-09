import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from sim_interfaces.msg import FromServer, FromSim
import numpy as np
import asyncio
import websockets
import json
import threading


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
        
        # WebSocket vars
        self.mouse_x = 0
        self.mouse_y = 0
        self.latest_mouse_timestamp = 0

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
        self.target_pos = np.array([-5.0, 5.0])
        forward_vel, _, angular_vel = self.compute_command_to_target()
        msg = FromServer()
        msg.server_data = [forward_vel, angular_vel, self.target_pos[0], self.target_pos[1]]
        self.publisher_.publish(msg)
    
    def update_mouse_position(self, x, y, timestamp):
        """Update mouse position from WebSocket"""
        self.mouse_x = x
        self.mouse_y = y
        self.get_logger().info(f'Mouse position updated: x={x}, y={y}')

async def websocket_handler(websocket, server_node):
    """Handle WebSocket connections and messages"""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                x = data.get('x', 0)
                y = data.get('y', 0)
                timestamp = data.get('timestamp', 0)
                
                # Update the server node with mouse data
                server_node.update_mouse_position(x, y, timestamp)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")


async def start_websocket_server(server_node, host='0.0.0.0', port=8080):
    """Start the WebSocket server"""
    async def handler(websocket):
        await websocket_handler(websocket, server_node)
    
    async with websockets.serve(handler, host, port):
        print(f"WebSocket server started on ws://{host}:{port}")
        await asyncio.Future()  # run forever


def run_websocket_server(server_node):
    """Run the WebSocket server in an asyncio event loop"""
    asyncio.run(start_websocket_server(server_node))

def main(args=None):
    try:
        with rclpy.init(args=args):
            server = Server()
            
            # Start WebSocket server in a separate thread
            ws_thread = threading.Thread(target=run_websocket_server, args=(server,), daemon=True)
            ws_thread.start()

            rclpy.spin(server)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()