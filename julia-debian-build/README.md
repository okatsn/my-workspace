- [Docker](#docker)
  - [How to build the image solely from the Dockerfile:](#how-to-build-the-image-solely-from-the-dockerfile)
    - [Explain](#explain)
  - [How to use `my-julia-build` in another `Dockerfile`](#how-to-use-my-julia-build-in-another-dockerfile)
    - [Import the image](#import-the-image)
    - [Consistent environment variable](#consistent-environment-variable)
    - [`COPY` the julia installation in the last stage](#copy-the-julia-installation-in-the-last-stage)
    - [VSCODE environment](#vscode-environment)
    - [Other KEYNOTE](#other-keynote)
  - [Known Issue](#known-issue)
    - [Copy `Project.toml`](#copy-projecttoml)
- [Next TODOs](#next-todos)
# Docker

The content of this folder is migrated from [okatsn/my-julia-build](https://github.com/okatsn/my-julia-build); please refer to this archive for older history.

## How to build the image solely from the Dockerfile:

```bash
# These commands should be executed in WSL at the directory of my-julia-build
cd ./julia-debian-build

# bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag jbuild okatsn/my-julia-build:latest

# push it to dockerhub
docker push okatsn/my-julia-build:latest
```

### Explain
Why not use devcontainer.json to build (saying `$ docker-compose -f .devcontainer/docker-compose.yml build`)?
- Building image from devcontainer.json creates some additional files, such as those in `/home/okatsn/.vscode-server` and `/home/okatsn/.vscode-server-insiders`
- If there are other container (saying the-target) that was directly built upon this image, and it also has `/home/okatsn/.vscode-server` but should with different content, the files in source (my-julia-build) is kept, and those in the target are discarded. This is not what we want.
- References: 
    - https://github.com/andferrari/julia_notebook/blob/master/Dockerfile
    - https://github.com/marius311/CMBLensing.jl/blob/master/Dockerfile
    - https://github.com/MalteBoehm/julia_docker-compose_template/blob/main/Dockerfile

## How to use `my-julia-build` in another `Dockerfile`

### Import the image

- `FROM okatsn/my-julia-build:latest AS build-julia`

### Consistent environment variable

The environment variables such as `NB_UID` and `NB_GID` are defined in the `.env` file which are included as arguments for `Dockerfile` in the `docker-compose.yml`.

These variables should be consistent with your final-stage image. For example: 

```Dockerfile
FROM okatsn/my-julia-build:v1.10-2024a AS build-julia
FROM okatsn/my-tex-life:v2024a1
```

In this case, both the `Dockerfile` in `my-julia-build` and `my-tex-life` ([okatsn/MyTeXLife](https://github.com/okatsn/MyTeXLife.git)) have 
`NB_GID` and `NB_UID` described in their `.env` file. You have to make sure they are consistent because they are critical in setting the ownership of files/applications.


### `COPY` the julia installation in the last stage

```Dockerfile
COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia

COPY --from=build-julia --chown=$NB_UID:$NB_GID /opt/julia-okatsn /opt/julia-okatsn

# Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia

# Switch to $NB_USER
USER $NB_USER
# Build IJulia
RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 
```

### VSCODE environment

Add Named volume in your docker-compose.yml; please refer [okatsn/MyTeXLife] or [MyTeXLifeWithJulia] as an example.


### Other KEYNOTE
1. The building of `my-julia-build` is controlled by `docker-compose.yml`.
2. Please follow the instruction in Dockerfile.
3. Those in `.devcontainer` is intended just for the convenience of building the image and open the container using VSCODE's interface. Without them, the building command instruction in Dockerfile should still work.
4. The `devcontainer.json` is suggested by VSCODE. 

## Known Issue

### Copy `Project.toml`

One may like to copy a custom `Project.toml`, saying `.devcontainer/Project_for_env.toml` for example, to initial julia project environment such as `~/.julia/environments/v1.xx`.
This works when the julia depository has not been mounted to volume yet.

Once the julia depository, `julia-depot:/home/jovyan/.julia`, has been mounted to a volume, commands in building stages won't change any of the contents in this directory unless you delete the volume or prune the builder before running Dockerfile. For example:

```Dockerfile
# This works since /home has not been mounted as volume before:
RUN cp /home/$NB_USER/.julia/environments/v1.10/Project.toml /home/Project2.toml
```

```Dockerfile
# (This doesn't work)
COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /home/$NB_USER/.julia/environments/v1.10/Project_for_env.toml
# (This doesn't work either):
COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /tmp/Project.toml
RUN mv -f /tmp/Project.toml /home/$NB_USER/.julia/environments/${JULIA_PROJECT}/Project.toml
```

To make the copy command working, try BOTH delete volumes and `docker builder prune` before rebuild since the mounted volume will not be modified (and should not) in the container building stage. 



# Next TODOs

- [ ] Find a way to synchronize all the `.env` files in different repos. For example, `okatsn/my-julia-build/.env` should describe the same environment variables as those in `okatsn/MyTeXLife/.devcontainer/.env`.