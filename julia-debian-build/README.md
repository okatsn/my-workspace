# Docker

# KEYNOTE: How to build the image solely from this Dockerfile:
# (These commands should be executed in WSL at the repository directory my-julia-build)
# $ docker-compose build
# $ docker tag jbuild okatsn/my-julia-build:latest
# $ docker push okatsn/my-julia-build:latest
#
# # Hint: Use a local build for testing
# Create a temporary local build: `docker tag jbuild temp-local:latest`, and
# use it in other Dockerfile `FROM temp-local as build-julia`.
#
# Explain:
# - bulid docker image of tag (-t) "jbuild" using file ("-f") "Dockerfile" in the context of current directory (`.` in the end)
# - tag the image 
# - push it to dockerhub
# Why not use devcontainer.json to build (saying `$ docker-compose -f .devcontainer/docker-compose.yml build`)?
# - Building image from devcontainer.json creates some additional files, such as those in /home/okatsn/.vscode-server and /home/okatsn/.vscode-server-insiders
# - If there are other container (saying the-target) that was directly built upon this image, and it also has /home/okatsn/.vscode-server but should with different content, the files in source (my-julia-build) is kept, and those in the target are discarded. This is not what we want.
#
# References:
# https://github.com/andferrari/julia_notebook/blob/master/Dockerfile
# https://github.com/marius311/CMBLensing.jl/blob/master/Dockerfile
# https://github.com/MalteBoehm/julia_docker-compose_template/blob/main/Dockerfile
#
#
# KEYNOTE: How to use (please replace $NB_USER, $WORKSPACE_DIR and $VARIANT yourself). $JULIA_PROJECT is something like "v1.10".
# FROM okatsn/my-julia-build:latest as build-julia
# # (at USER root). Refer .env file of the last stage (i.e., my-tex-life) for NB_UID and NB_GID; or define your NB_UID and NB_GID for this build in .env, and include it in docker-compose.yml as args.
# COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia
# COPY --from=build-julia --chown=$NB_UID:$NB_GID /opt/julia-okatsn /opt/julia-okatsn
# # Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
# RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia
# # (Switch to $NB_USER)
# # Build IJulia
# RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 
#
# # VSCODE environment: Add Named volume in your docker-compose.yml; please refer MyTeXLife or MyTeXLifeWithJulia as an example.





# KEYNOTE
1. The building of `my-julia-build` is controlled by `docker-compose.yml`.
2. Please follow the instruction in Dockerfile.
3. Those in `.devcontainer` is intended just for the convenience of building the image and open the container using VSCODE's interface. Without them, the building command instruction in Dockerfile should still work.
4. The `devcontainer.json` is suggested by VSCODE. 

# Next TODOs
- [ ] Find a way to synchronize all the `.env` files in different repos. For example, `okatsn/my-julia-build/.env` should describe the same environment variables as those in `okatsn/MyTeXLife/.devcontainer/.env`.