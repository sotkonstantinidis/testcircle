#!/bin/bash

docker build -t locust .
docker run -d -v dirname:/locust -P locust --host=https://qcat.wocat.net
docker_ip=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' $(docker ps -q))
url="http://$docker_ip:8089"
xdg-open $url