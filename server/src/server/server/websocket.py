import asyncio
import websockets
import json
from collections import deque
import time

# Track the active connections
queue_length = 10
queue = deque()
active_connection = None
last_activity_time = None
idle_timeout = 60.0  # seconds of inactivity before disconnecting
connection_lock = asyncio.Lock()

async def check_idle_timeout():
    """Background task to check for idle timeout and disconnect inactive clients"""
    global active_connection, last_activity_time
    
    while True:
        await asyncio.sleep(1.0)  # Check every second
        
        async with connection_lock:
            if active_connection is not None and last_activity_time is not None:
                idle_time = time.time() - last_activity_time
                if idle_time > idle_timeout:
                    print(f"Connection idle for {idle_time:.1f}s, disconnecting...")
                    try:
                        await active_connection.close(1000, "Idle timeout")
                    except Exception as e:
                        print(f"Error closing idle connection: {e}")
                    
                    await promote_next_client()

async def promote_next_client():
    """Reset active connection and promote next client from queue if available"""
    global active_connection, last_activity_time, queue
    
    active_connection = None
    last_activity_time = None
    
    # If there are clients in the queue, promote the next one
    if len(queue) > 0:
        active_connection = queue.popleft()
        last_activity_time = time.time()
        await active_connection.send(json.dumps({
            "status": "Connected"
        }))
        # Broadcast updated positions to remaining queued clients
        await broadcast_queue_positions()

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
    global active_connection, queue_length, queue, last_activity_time
    
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
            last_activity_time = time.time()
    
    try:
        async for message in websocket:
            if websocket != active_connection:
                continue  # Ignore messages from queued clients
            
            # Update last activity time for active connection
            async with connection_lock:
                last_activity_time = time.time()
            
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
                await promote_next_client()
            else:
                # Remove from queue and update all remaining queue positions
                queue.remove(websocket)
                await broadcast_queue_positions()


async def start_websocket_server(server_node, host='0.0.0.0', port=8080):
    """Start the WebSocket server"""
    async def handler(websocket):
        await websocket_handler(websocket, server_node)
    
    # Start the idle timeout checker as a background task
    asyncio.create_task(check_idle_timeout())
    
    async with websockets.serve(handler, host, port):
        print(f"WebSockets server started on ws://{host}:{port}")
        print(f"Idle timeout set to {idle_timeout} seconds")
        await asyncio.Future()  # run forever


def run_websocket_server(server_node):
    """Run the WebSocket server in an asyncio event loop"""
    asyncio.run(start_websocket_server(server_node))