[TOC]

# README
## How to build the image solely from the Dockerfile:

```bash
# These commands should be executed in WSL at the directory of my-quarto-build
cd ./quarto-debian-build

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build

# tag the image 
docker tag qbuild okatsn/my-quarto-build:latest

# push it to dockerhub
docker push okatsn/my-quarto-build:latest
```

## How to use:
```Dockerfile
FROM okatsn/my-quarto-build:latest as build-quarto
COPY --from=build-quarto --chown=$NB_UID:$NB_GID /usr/local/bin/quarto /usr/local/bin/quarto
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



## Instruction for developer
### Build the image based on files in .devcontainer
Make sure the following files are prepared:
- Dockerfile: Script for building the container
- docker-compose.yml: The Compose file that uses Dockerfile and set volumes up.
- devcontainer.json: The file for vscode set up.

#### In vscode 

Steps
- Install `Dev Containers` (as well as WSL and so on. See [this](https://github.com/okatsn/swc-forecast-TWAI-23a/blob/master/DEVELOPMENT.md#install-or-set-up-prerequisite) for more information)
- `Ctrl+Shift+P` and select **Dev Containers: Rebuild Container Without Cache**

### Push and use Docker image

[Ref.](https://docs.docker.com/engine/reference/commandline/commit/)

Once an image is successfully built, commit and push the image as follows:

#### Get container ID
**in wsl**
- `docker container list` to get the CONTAINER_ID 

**in Docker Desktop**
- click on tab "Containers" 
- expand the droplist of `myjuliaspace_devcontainer` and it shows

#### Commit

- In wsl, `docker commit CONTAINER_ID user/repo` 
    - e.g., `docker commit 3935a2cd9ee6 okatsn/my-julia-space`

commit with a tag and message:
- `docker commit -m "Hello World!" 89065a96c90b okatsn/my-tex-life-with-julia:helloworld`

#### Push committed image (with tag)

Push committed image
- in wsl, `docker image push okatsn/my-julia-space`
- By default it pushes the image with the tag of `latest`.

Push the image with the `helloworld` tag:
- `docker image push okatsn/my-julia-space:helloworld`

#### To use the image:
- in .devcontainer/Dockerfile, with `FROM okatsn/my-julia-space`
- add .devcontainer/docker-compose.yml
- add .devcontainer/devcontainer.json


## Instruction for users

### First-time use
For `OhMyREPL` to work: 
- `pkg> instantiate`
- close julia REPL and open it again; you should see julia syntax highlighted by colors (which means `startup.jl` successfully executed at the start up of julia REPL).