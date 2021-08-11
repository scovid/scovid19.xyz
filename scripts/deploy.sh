#!/usr/bin/env bash

# Scale up to 2 containers, the new one being our new build
# Kill the old container, then scale down to 1
echo "Scaling up $name (NOTE: You can ignore the following two warnings about the container name and port)"
docker rename $name "${name}_old"
sleep 2
docker-compose up -d --scale scovid=2 --no-recreate --build --no-deps scovid

echo "Building new container"
sleep 20

echo "New container built, removing old one"
docker rm -f "${name}_old"
docker-compose up -d --scale scovid=1 --no-recreate scovid
echo "Deploy finished"
