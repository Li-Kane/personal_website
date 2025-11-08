docker build -t server .
docker run -it -p 3247:3247 -v $(pwd)/src:/src server