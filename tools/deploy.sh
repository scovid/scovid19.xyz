#!/usr/bin/env bash

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

# Scale up to 2 containers, the new one being our new build
# Kill the old container, then scale down to 1
echo "Scaling up scovid (NOTE: You can ignore the following two warnings about the container name and port)"
docker rename scovid "scovid_old"
sleep 2
docker-compose -f docker-compose.yml up -d --scale scovid=2 --no-recreate --build --no-deps scovid

echo "Building new container"
sleep 20

echo "New container built, removing old one"
docker rm -f "scovid_old"
docker-compose -f docker-compose.yml up -d --scale scovid=1 --no-recreate scovid
echo "Deploy finished"
