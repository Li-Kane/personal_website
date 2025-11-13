docker build -t server .
docker run -it -p 3247:3247 -p 8080:8080 -v $(pwd):/server server
docker exec -it <container> bash

# delete
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -a -q)

## Numpy
Average (last 100) - Total: 50.56ms, Inference: 5.17ms, AdvanceBy: 45.15ms
Average (last 100) - Total: 48.45ms, Inference: 1.72ms, AdvanceBy: 46.45ms
Average (last 100) - Total: 48.28ms, Inference: 5.25ms, AdvanceBy: 42.76ms
Average (last 100) - Total: 50.28ms, Inference: 2.50ms, AdvanceBy: 47.54ms
Average (last 100) - Total: 54.16ms, Inference: 5.34ms, AdvanceBy: 48.55ms
Average (last 100) - Total: 47.06ms, Inference: 0.51ms, AdvanceBy: 46.34ms
Average (last 100) - Total: 50.84ms, Inference: 3.76ms, AdvanceBy: 46.84ms
Average (last 100) - Total: 48.42ms, Inference: 0.72ms, AdvanceBy: 47.45ms
Average (last 100) - Total: 50.65ms, Inference: 3.99ms, AdvanceBy: 46.45ms
Average (last 100) - Total: 64.54ms, Inference: 16.18ms, AdvanceBy: 48.03ms

## Pytorch
Average (last 100) - Total: 20.82ms, Inference: 2.24ms, AdvanceBy: 18.32ms
Average (last 100) - Total: 27.08ms, Inference: 4.83ms, AdvanceBy: 21.94ms
Average (last 100) - Total: 28.76ms, Inference: 8.47ms, AdvanceBy: 19.97ms
Average (last 100) - Total: 27.41ms, Inference: 5.91ms, AdvanceBy: 21.16ms
Average (last 100) - Total: 27.49ms, Inference: 6.07ms, AdvanceBy: 21.08ms
Average (last 100) - Total: 26.37ms, Inference: 5.53ms, AdvanceBy: 20.54ms
Average (last 100) - Total: 28.44ms, Inference: 7.91ms, AdvanceBy: 20.23ms
Average (last 100) - Total: 26.33ms, Inference: 5.77ms, AdvanceBy: 20.25ms
Average (last 100) - Total: 25.62ms, Inference: 5.72ms, AdvanceBy: 19.59ms
Average (last 100) - Total: 26.72ms, Inference: 5.63ms, AdvanceBy: 20.78ms

## ONNX
Average (last 100) - Total: 18.05ms, Inference: 0.18ms, AdvanceBy: 17.61ms
Average (last 100) - Total: 23.84ms, Inference: 0.17ms, AdvanceBy: 23.44ms
Average (last 100) - Total: 21.97ms, Inference: 0.18ms, AdvanceBy: 21.55ms
Average (last 100) - Total: 22.15ms, Inference: 0.21ms, AdvanceBy: 21.67ms
Average (last 100) - Total: 21.64ms, Inference: 0.21ms, AdvanceBy: 21.16ms
Average (last 100) - Total: 20.07ms, Inference: 0.18ms, AdvanceBy: 19.66ms
Average (last 100) - Total: 19.96ms, Inference: 0.19ms, AdvanceBy: 19.52ms
Average (last 100) - Total: 21.89ms, Inference: 0.20ms, AdvanceBy: 21.43ms
Average (last 100) - Total: 21.39ms, Inference: 0.19ms, AdvanceBy: 20.95ms
Average (last 100) - Total: 20.59ms, Inference: 0.19ms, AdvanceBy: 20.15ms
Average (last 100) - Total: 21.63ms, Inference: 0.19ms, AdvanceBy: 21.18ms
Average (last 100) - Total: 21.40ms, Inference: 0.18ms, AdvanceBy: 20.99ms