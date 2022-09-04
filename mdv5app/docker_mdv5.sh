# dockerized version of the above, ran into dependency issue for termcolor
# https://github.com/pytorch/serve/tree/master/docker
docker run --rm -p 8080:8080 -p 8081:8081 -p 8082:8082 -p 7070:7070 -p 7071:7071 -v "$(pwd)":/app -it pytorch/torchserve:0.5.3-cpu bash /app/serve_megadetect.sh
