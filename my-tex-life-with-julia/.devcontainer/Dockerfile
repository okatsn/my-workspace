# CHECKPOINT: When I'm trying to build a new container base on it (saying `FROM okatsn/my-tex-life-with-julia`), permission error occurred when the docker-compose.yml of the new container also create/attach the volume of .vscode-server.
# The error is fixed when I build the image again using the following command instead; previously, the image was build using docker-compose.yml.
# However, I cannot reproduce the error again. I'm not sure the permission denied error is solved by using the following building command, or by remove all the my-tex-life-with-julia--related containers, images and volumes.
# 
# Building command: 
# # SETME: `devjuliatex` and `my-tex-life-with-julia` can be replaced by arbitrary names.
# # SETME: Remember to change the tag name
# $ docker build -t devjuliatex -f .devcontainer/Dockerfile .
# $ docker tag devjuliatex okatsn/my-tex-life-with-julia:latest
# $ docker push okatsn/my-tex-life-with-julia:latest

# KEYNOTE: Trouble shooting
# Use the following command if it fails to build in one machine but success in the other with exactly the same script.
# - `docker builder prune` # Clear Build Cache
# - `docker volume prune` # Remove Unused Volumes

# # WARN: Try BOTH delete volumes and `docker builder prune` before rebuild. Ohterwise, the Project.toml won't be overwritten by Project_for_env.toml.
# # Explain:
# # If the volume mounted for julia already exists, anything modifying the volume won't work. For example, 
#
# # This works:
# RUN cp /home/$NB_USER/.julia/environments/v1.10/Project.toml /home/Project2.toml
#
# # But the followings do nothing if volume not deleted and builder not pruned:
# # (This doesn't work)
# COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /home/$NB_USER/.julia/environments/v1.10/Project_for_env.toml
#
# # (This doesn't work either):
# COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /tmp/Project.toml
# RUN mv -f /tmp/Project.toml /home/$NB_USER/.julia/environments/${JULIA_VER}/Project.toml

FROM okatsn/my-typst-space AS build0

FROM okatsn/my-julia-build:v1.10-2024a as build-julia
FROM okatsn/my-tex-life:v2024a1
# Docker image https://hub.docker.com/repository/docker/okatsn/my-tex-life/general built from https://github.com/okatsn/MyTeXLife


USER root


ARG JULIA_VER
# KEYNOTE: This variable is defined in docker-compose.yml, and should be consistent with that of my-julia-build


# # Install Zotero
RUN curl -sL https://raw.githubusercontent.com/retorquere/zotero-deb/master/install.sh | bash
RUN apt-get update && apt-get -y install \
    zotero
# TODO: Install Zotero and BibTeX (cannot be done in Dockerfile)
# - Download Better BibTeX: https://github.com/retorquere/zotero-better-bibtex/releases/latest 
# - $ zotero          // open zotero (a window of zotero app should pop out)
# - In Zotero app, click Tools > Add-ons > ⚙️ (setting icon) > Install Add-on from file... and click on the zotero-better-bibtex-6.7.143.xpi you just downloaded.
#
# KEYNOTE: How to use
# - Open Zotero ($ zotero)
# - Use VSCode addon XING.zotero-cite "Zotero Cite: Cite and Create Bibliograph for Pandoc/LaTeX." (it creates main.bib for main.tex for example), or use raykr.zotex "Zotex: Cite and Create Bibliograph for LaTeX."



# For OhMyREPL
# KEYNOTE: use $HOME instead of /home/$NB_USER will fail! Since $HOME is not recognized as absolute directory!
# RUN mkdir -p /home/$NB_USER/.julia/config
# COPY .devcontainer/startup.jl /home/$NB_USER/.julia/config/startup.jl


# CHECKPOINT: Multi stage build; Merge these keynotes to the README of my-tex-life-with-julia
# https://cindyliu923.com/2021/05/23/What-is-docker-multi-stage/
# - Explanation: What are inside an image?  layers!
# - Keypoints: Middle images won't presents as layers in the final image.
# - All files and folders not `COPY`ed won't survive in the final stage. (?!)
# - Application: Thus you can have some secrets inside the middle image!

# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#use-multi-stage-builds
# - Only the instructions RUN, COPY, ADD create layers.


# # For Typst
# # # Install Rust
# # # Please refers https://www.rust-lang.org/learn/get-started. `-s -- -y` is suggested by ChatGPT in order to install using default settings without interrupt.
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y




# # Julia part (Please refer the Dockerfile in okatsn/my-julia-build)
COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia
COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /home/$NB_USER/.julia/environments/${JULIA_VER}/Project.toml
COPY --from=build-julia --chown=$NB_UID:$NB_GID /opt/julia-okatsn /opt/julia-okatsn
# Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia

# WORKDIR $WORKSPACE_DIR
USER $NB_USER
# RUN julia -e '...' will fail if the permission settings (`chown`) have problems.

# # Install jlpkg, which allows direct use of Pkg in bash command line.
# # Please refer https://github.com/fredrikekre/jlpkg
# # KEYNOTE: use jlpkg to install Pkg was intended to fix the " UndefVarError: `Pkg` not defined". However, this error is resulted by a stupid mistake in the next RUN that `Pkg.instantiate()` is used without `using Pkg` (you used `&&` to concatenate two `RUN julia -e '...'`). Feel free to delete this "Install jlpkg" section in the future.
# RUN curl -fsSL https://github.com/fredrikekre/jlpkg/releases/download/v1.5.1/jlpkg-v1.5.1.tar.gz | \
#     tar -xzC /usr/local/bin && \
#     jlpkg add Pkg && \

# KEYNOTE: This seems to cause Permission denied error until you (firstly disable this line in order to successfully build the container) add and build IJulia in your container, and rebuild again. (The permission issue is related to conda)
# RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 

COPY --from=build0 /bin/typst /bin
# Please refer: https://github.com/my-typst-space

