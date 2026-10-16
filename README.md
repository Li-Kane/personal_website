# Personal Website
A personal portfolio demonstrating my experience in robotics, simulators, and web development. On my AWS EC2 server, I run a [kdFlex](https://www.karanadyn.com/) simulation in a docker container where a Spot robot autonomously navigates to a target. It communicates with my React frontend through websockets and an nginx proxy to have Spot follow wherever the user's mouse is.

## Server
Add evaluation.license and a kdflex-0.9.19-Linux.deb to /server/docker_files from www.karanadyn.com

## Frontend
1. Setup environment variables inside /frontend/.env according to /frontend/.env.example
2. Cd into frontend and run
```
npm install
npm run dev
```

## Run together in local dev:
```bash
docker compose -f docker-compose.yml up --build
```

## Production Deployment
The website is deployed on a home-server and is therefore managed as a submodule of that server. A custom compose.yml and Dockerfile.prod is used for production.
