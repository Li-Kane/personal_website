# setup server
cd server/
docker build -t server .
docker run -it -p 3247:3247 -p 8080:8080 -v $(pwd):/server server
docker exec -it <container> bash

# new server
cd server/
docker build -t new_server .
docker run -it -p 3247:3247 -p 8080:8080 -v $(pwd):/server server
docker exec -it <container> bash

# setup frontend
cd frontend/
docker build -t frontend .
docker run -p 5173:5173 -v $(pwd):/app frontend

# delete
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -a -q)

## Setup Checklist
1. Setup ECS
    - Push Server container to ECR
    - Setup task, VPC, subnets, security groups
    - Spin up a container and allow me to see it's url in the browser 
    - Allow me to connect to container's websocket url
2. Setup AWS API
    - Allow containers to be orchestrated from an API call
    - Container warming, automatic shutdown, etc.
    - Cloudwatch events
3. Setup frontend
    - Deploy frontend to call API and get URLS