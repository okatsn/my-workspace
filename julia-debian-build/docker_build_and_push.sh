#!/bin/sh

echo "Dockerfile modified. Building and pushing Docker image..."

# Navigate to the directory
cd ./julia-debian-build || exit 1

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag jbuild okatsn/my-julia-build:latest

# push it to dockerhub
docker push okatsn/my-julia-build:latest

echo "Docker image built and pushed successfully."

cd ..