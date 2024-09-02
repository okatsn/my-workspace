# DEPRECATED

After dive into the image, it turns out the DVC installation involves modifications of multiple files/folders across the system, seeming to make dvc works seamlessly with such as sftp, git and so on. 
Thus, it is impractical to identify all the modifications to be `COPY`ed.

## How to build the image solely from the Dockerfile:

```bash
# These commands should be executed in WSL at the directory of my-julia-build
cd ./dvc-build

docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag dvcbuild okatsn/my-dvc-build:latest

# push it to dockerhub
docker push okatsn/my-dvc-build:latest
```
