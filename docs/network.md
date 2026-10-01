# Network Architecture

This document outlines the networking topology and routing for the Spot simulation project.

## Components & Ports

The architecture consists of three main services:

1. **Frontend (React/Vite)**
   - **Port**: `5173` (Local Dev)
   - **Role**: Renders the UI and the 3D KdFlex canvas. In production, the built static files are served directly by Caddy.

2. **Python Controls Server (`server`)**
   - **Port**: `8080` (Internal Docker Network)
   - **Role**: Receives mouse coordinates/commands from the frontend via WebSockets and translates them into ROS 2 commands.

3. **KdFlex Simulation Server (`sim_sub`)**
   - **Port**: `3247` (Internal Docker Network)
   - **Role**: Serves the 3D simulation data over WebSockets (`/ws`) and provides a health check endpoint over HTTP (`/health`). Uses a Boost.Beast web server internally.

## Routing & Proxy (Caddy)

We use **Caddy** as a reverse proxy for both local development and production. 

**Why Caddy?**
- It unifies all services under a single domain and port, which completely eliminates CORS (Cross-Origin Resource Sharing) restrictions.
- It handles SSL/TLS termination automatically in production, protecting the backend servers from encrypted traffic they aren't designed to parse.

**Path Mappings:**
- `/*` ➔ Routes to the Frontend.
- `/ws*` ➔ Strips prefix and routes to the Python Controls Server (`server:8080`).
- `/sim_server*` ➔ Strips prefix and routes to the KdFlex Simulation (`server:3247`).

## Environment Variables

The React frontend uses the following environment variables to determine where to connect:

- `VITE_SIM_WS_URL`: Connects to KdFlex (e.g., `ws://localhost/sim_server/ws`)
- `VITE_SIM_HEALTH_URL`: Connects to KdFlex health (e.g., `http://localhost/sim_server/health`)
- `VITE_CONTROLS_WS_URL`: Connects to Python Server (e.g., `ws://localhost/ws`)

*Note: In production, these variables use `wss://` and `https://` with the production domain.*

## Common Pitfalls & Solutions

Throughout development, several major networking quirks were identified and resolved:

### 1. The `bad method` Crash (TLS vs Plain HTTP)
The KdFlex simulation server strictly expects plain-text HTTP/WS. If a browser attempts to establish a secure connection (`https://` or `wss://`), it sends a binary TLS handshake. The Boost.Beast server fails to parse this as an HTTP method, throws a `bad method` exception, and **crashes the entire simulation process**. 
**Solution:** Caddy sits in front of the server, terminating all HTTPS/TLS traffic and forwarding only plain-text HTTP to port 3247.

### 2. CORS Preflight (`OPTIONS`) Rejections
The KdFlex server does not support CORS headers and rejects `OPTIONS` preflight requests with an `HTTP 400 Bad Request`.
**Solution:** Proxying all traffic through Caddy makes the requests "same-origin," preventing the browser from ever sending a CORS preflight request.

### 3. The WebSocket Endpoint Path
The simulation viewer attempts to connect to a WebSocket for rendering data. Originally, it was assumed this endpoint was at `/viewer`. However, connecting to `/viewer` results in an `HTTP 400 Bad Request` from KdFlex.
**Solution:** The correct WebSocket endpoint exposed by the KdFlex binary is strictly `/ws`.
