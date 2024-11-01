[TOC]

# README
## How to build the image solely from the Dockerfile:

```bash
# These commands should be executed in WSL at the directory of my-quarto-build
cd ./quarto-debian-build

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag qbuild okatsn/my-quarto-build:latest

# push it to dockerhub
docker push okatsn/my-quarto-build:latest
```

## How to use:
```Dockerfile
FROM okatsn/my-quarto-build:latest AS build-quarto
# COPY the main application
COPY --from=build-quarto --chown=$NB_UID:$NB_GID /opt/quarto /opt/quarto
# Making the application located at `/opt/quarto/bin/quarto` accessible from anywhere on your system by simply using the command `quarto`.
RUN ln -fs /opt/quarto/bin/quarto /usr/local/bin/quarto
```
You can use the following commands to find out dependencies for quarto
- `which quarto`
- `type quarto`
- `dpkg-query -W -f='${Depends}\n' quarto`
- `apt-cache rdepends quarto`
- `apt-cache depends quarto`
Search the log by keyword or time:
- `cat /var/log/dpkg.log | grep '2024-04-22'`
- `cat /var/log/dpkg.log | grep 'quarto'`

## For the first time use of a `my-quarto-build` dependent container

In VSCode:
- Install extension `quarto.quarto`
- If you want to use either julia or python in your qmd file, installation of Jupyter is required.