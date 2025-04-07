echo "Dockerfile modified. Building and pushing Docker image..."


# These commands should be executed in WSL at the directory of my-quarto-build
cd ./my-jupyter-with-julia || exit 1

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag juliaworkspace okatsn/my-jupyter-with-julia:latest

# push it to dockerhub
docker push okatsn/my-jupyter-with-julia:latest

echo "Docker image built and pushed successfully."

cd ..
