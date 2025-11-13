docker build -t server .
docker run -it -p 3247:3247 -p 8080:8080 -v $(pwd):/server server
docker exec -it <container> bash

# delete
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -a -q)