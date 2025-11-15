import asyncio
import websockets
import json
from collections import deque

# Track the active connections
queue_length = 10
queue = deque()
active_connection = None
connection_lock = asyncio.Lock()

async def broadcast_queue_positions():
    """Send updated queue positions to all queued clients"""
    global queue
    for i, ws in enumerate(queue):
        try:
            await ws.send(json.dumps({
                "status": "Queued",
                "queue_position": queue.index(ws) + 1
            }))
        except Exception as e:
            print(f"Error broadcasting to queued client: {e}")

async def websocket_handler(websocket, server_node):
    """Handle WebSocket connections and messages per client"""
    global active_connection, queue_length, queue
    
    # Check if another client is already connected
    async with connection_lock:
        if len(queue) > queue_length:
            await websocket.close(1008, "Queue full")
            return
        elif active_connection is not None:
            queue.append(websocket)
            await websocket.send(json.dumps({
                "status": "Queued",
                "queue_position": queue.index(websocket) + 1
            }))
        else:
            await websocket.send(json.dumps({
                "status": "Connected"
            }))
            # Claim this connection as active
            active_connection = websocket
    
    try:
        async for message in websocket:
            if websocket != active_connection:
                continue  # Ignore messages from queued clients
            try:
                data = json.loads(message)
                x = data.get('x', 0)
                y = data.get('y', 0)
                ratio = data.get('ratio', 1)
                
                # Update the server node with mouse data
                server_node.update_mouse_position(x, y, ratio)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}") 
    finally:
        # Clean up when connection closes
        async with connection_lock:
            if active_connection == websocket:
                active_connection = None
                # If there are clients in the queue, promote the next one
                if len(queue) > 0:
                    next_websocket = queue.popleft()
                    active_connection = next_websocket
                    await next_websocket.send(json.dumps({
                        "status": "Connected"
                    }))
                    # Broadcast updated positions to remaining queued clients
                    await broadcast_queue_positions()
            else:
                # Remove from queue and update all remaining queue positions
                queue.remove(websocket)
                await broadcast_queue_positions()


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