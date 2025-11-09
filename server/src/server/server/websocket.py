import asyncio
import websockets
import json

async def websocket_handler(websocket, server_node):
    """Handle WebSocket connections and messages"""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                x = data.get('x', 0)
                y = data.get('y', 0)
                ratio = data.get('ratio', 1)
                
                # Update the server node with mouse data
                server_node.update_mouse_position(x, y, ratio)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")


async def start_websocket_server(server_node, host='0.0.0.0', port=8080):
    """Start the WebSocket server"""
    async def handler(websocket):
        await websocket_handler(websocket, server_node)
    
    async with websockets.serve(handler, host, port):
        print(f"WebSockets server started on ws://{host}:{port}")
        await asyncio.Future()  # run forever


def run_websocket_server(server_node):
    """Run the WebSocket server in an asyncio event loop"""
    asyncio.run(start_websocket_server(server_node))