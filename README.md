# setup server
1. Add evaluation.license and a kdflex-0.9.19-Linux.deb to server/docker_files
2. cd into server and run
docker build -t server .
docker run -p 3247:3247 -p 8080:8080 server
docker exec -it <container> bash

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