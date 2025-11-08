docker build -t frontend .
docker run -p 5173:5173 -v $(pwd):/app frontend