#!/bin/sh

echo "Dockerfile modified. Building and pushing Docker image..."

# Navigate to the directory
cd ./my-mini-explorer || exit 1

# Build the Docker image
docker-compose --env-file ../my-build.env build --no-cache

# Tag the image
docker tag dvcbuild okatsn/my-mini-explorer:latest

# Push the image to Docker Hub
docker push okatsn/my-mini-explorer:latest

echo "Docker image built and pushed successfully."
