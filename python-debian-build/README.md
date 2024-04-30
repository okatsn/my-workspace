[TOC]

# README
## How to build the image solely from the Dockerfile:

```bash
# These commands should be executed in WSL at the directory of my-python-build
cd ./python-debian-build

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag pbuild okatsn/my-python-build:latest

# push it to dockerhub
docker push okatsn/my-python-build:latest
```

## How to use:
```Dockerfile
FROM okatsn/my-python-build:latest as build-python
```

!!! note 
    When you `dive` into `pbuild`, you will discover that what `pip3 install` (`pip3 install tldr`) must depend on python. 
    Diving into the layer a step earlier (`apt-get install python3-pip`), you will find it impractical to copy the entire python installation to the next stage since there are countless files separated at different locations to be dealed with. 
    Thus, anything related to python installation should be considered the last stage in the Dockerfile.
