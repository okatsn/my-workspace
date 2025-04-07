#!/bin/sh

echo "Dockerfile modified. Building and pushing Docker image..."

# Navigate to the directory
cd ./my-util-box || exit 1

docker build -t okatsn/my-util-box .

# Push to Docker Hub (optional)
docker push okatsn/my-util-box

echo "Docker image built and pushed successfully."

cd ..