# Personal Website
A personal portfolio demonstrating my experience in robotics, simulators, and web development. On my AWS EC2 server, I run a [kdFlex](https://www.karanadyn.com/) simulation in a docker container where a Spot robot autonomously navigates to a target. It communicates with my React frontend through websockets and an nginx proxy to have Spot follow wherever the user's mouse is.

## Server
1. Add evaluation.license and a kdflex-0.9.19-Linux.deb to /server/docker_files from www.karanadyn.com
2. cd into server and run
```
docker build -t name:tag .
docker run -p 3247:3247 -p name:tag
```

## Frontend
1. Setup environment variables inside /frontend/.env according to /frontend/.env.example
2. Cd into frontend and run
```
npm install
npm run dev
```
3. There is already a github actions workflow configured to deploy the website to github pages