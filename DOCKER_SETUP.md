# Docker Setup

This project uses Docker Compose to run both the frontend and server containers with a shared network.

## Architecture

- **Frontend**: React + Vite application (port 5173)
- **Server**: ROS2 + WebSocket server (ports 3247, 8080)
- **Network**: Both containers communicate via `personal_website_network`

## Network Communication

- Frontend can access server via iframe at `http://server:3247`
- WebSocket communication between containers on port `8080`
- Frontend WebSocket connects to server at `ws://server:8080`
- Server WebSocket listens on port `3247` (legacy) and `8080`

## Usage

### Start all services:
```bash
docker compose up
```

### Start services in detached mode:
```bash
docker compose up -d
```

### Build and start:
```bash
docker compose up --build
```

### Stop services:
```bash
docker compose down
```

### View logs:
```bash
docker compose logs -f
```

### View logs for specific service:
```bash
docker compose logs -f frontend
docker compose logs -f server
```

## Port Mapping

| Service  | Internal Port | External Port | Purpose                    |
|----------|---------------|---------------|----------------------------|
| Frontend | 5173          | 5173          | Vite dev server           |
| Frontend | 8080          | 8080          | WebSocket (frontend side) |
| Server   | 3247          | 3247          | Server/iframe/WebSocket   |
| Server   | 8080          | 8080          | WebSocket (server side)   |

## Environment Variables

### Frontend
- `VITE_SERVER_URL`: URL to reach the server (default: `http://server:3247`)
- `VITE_WS_URL`: WebSocket URL (default: `ws://server:8080`)

### Server
- `KARANA_LICENSE_FILE`: License file path for kdFlex
- `ROS_DOMAIN_ID`: ROS2 domain ID

## Volume Mounts

- Frontend: `./frontend` → `/app` (with node_modules excluded)
- Server: `./server` → `/server`

## Troubleshooting

### Cannot connect to server from frontend
1. Ensure both containers are on the same network: `docker network inspect personal_website_network`
2. Check if server is running: `docker compose ps`
3. Check server logs: `docker compose logs server`

### Port already in use
If you get port binding errors, check if the ports are already in use:
```bash
sudo lsof -i :5173
sudo lsof -i :3247
sudo lsof -i :8080
```

### Rebuild containers
If you make changes to Dockerfiles:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

## Development Notes

- Frontend hot-reload is enabled via volume mount
- Server container runs in interactive mode (`stdin_open: true`, `tty: true`)
- Both containers share the `app-network` bridge network for inter-container communication
