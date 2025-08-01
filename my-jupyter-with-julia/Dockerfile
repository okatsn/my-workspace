FROM okatsn/my-julia-build:v1.11-2025b AS build-julia
FROM okatsn/my-quarto-build:v1.6-2025a AS build-quarto
FROM okatsn/my-typst-space:v2025a AS build0
# Please refer to https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-minimal-notebook
# # Docker image repository seems to moved to quay.io
# # The list of available tags: https://quay.io/repository/jupyter/minimal-notebook?tab=tags
FROM quay.io/jupyter/minimal-notebook:2025-05-30

# Referring [User-related configurations](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#user-related-configurations)
# ENV CHOWN=yes

# Referring [Permission-specific configurations](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html#permission-specific-configurations)
# # This command is currently useless
# ENV GRANT_SUDO=yes



ARG HOME="/home/$NB_USER"
# KEYNOTE: the tailing "/" matters. 

ARG VSCODE_PATH="$HOME/.vscode-server/"
ARG WORKSPACE_DIR="$HOME/workspace/"
ARG JULIA_PKG_DEVDIR="$HOME/.julia/dev/"
# just let it be default. See [JULIA_PKG_DEVDIR](https://docs.julialang.org/en/v1/manual/environment-variables/#JULIA_PKG_DEVDIR). Be aware that some tests will depend on JULIA_PKG_DEVDIR.
ARG SUB_PROJECT_DIR="$HOME/workspace/projects/" 
# KEYNOTE: also check 
# - "gitProjectManager.baseProjectsFolders" in devcontainer.json that if GPM can get JULIA_PKG_DEVDIR and SUB_PROJECT_DIR
# - docker-compose.yml for defining volumes.

USER root
# Root user is necessary for the following command that creates the julia/quarto... link


# # Fix permissions for directories that is going to be mounted as volume but not-yet created when building this image. For those mounted as volume but user might need their permissions, directories must be made first.
#
# - The starship cache: allow starship to create log. 
RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship
# - pydrive2fs: persistent dvc remote credentials.
# RUN mkdir -p /home/$NB_USER/.cache/pydrive2fs && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/pydrive2fs
# KEYNOTE: this cannot solve the permission issue. Still only root can access pydrive2fs. 
# - I've also tried named volume instead (e.g., - pydrive2fs-cache:/home/jovyan/.cache/pydrive2fs), but 1. not working 2. named volume does not align with my goal (one container one credential; it's much better for every container to mount the only credential on host.)
# - Currently, in host (WSL) run `sudo chown -R okatsn:okatsn /home/okatsn/` can solve this issue.

RUN apt-get update && apt-get -y install \
    bash-completion \
    #
    # KEYNOTE:
    # - `apt-cache search fonts | grep noto` to see available fonts.
    # - See also https://samwhelp.github.io/note-about-ubuntu/read/adjustment/env/font.html
    # RUN apt-get update && apt-get -y install \
    tree 
    # `tree` list the tree of file directory.
    
# # Install fonts
# RUN apt-get update && apt-get -y install \
#     fontconfig \
#     fonts-noto-cjk \
#     fonts-noto-cjk-extra \
#     fonts-noto-color-emoji \
#     # 中文類楷體
#     fonts-arphic-ukai

# ## Install fonts that supports smcp
# RUN wget https://github.com/adobe-fonts/source-serif/archive/refs/heads/release.zip -O /tmp/temp123.zip  \
#     && unzip /tmp/temp123.zip -d /tmp/temp123  \
#     && mkdir -p /usr/share/fonts/opentype/source-serif-pro \
#     && cp /tmp/temp123/source-serif-release/OTF/*.otf /usr/share/fonts/opentype/source-serif-pro/ \
#     && fc-cache -fv \
#     && rm -rv /tmp/temp123 \
#     && rm -rv /tmp/temp123.zip

## Install typst
COPY --from=build0 /bin/typst /bin

## Install Starship
## Starship configuration
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc


# # Julia part
# Noted that the following command makes no change IF you are rebuilding the image WITHOUT prune build and volumes.
# Explain: Modification on a directory mounted as a volume will be overriden by the volume if the volume already exist. See explanlation in julia-debian-build/README.md
COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia

COPY --from=build-julia /opt/julia-okatsn /opt/julia-okatsn
# TODO:  --chown=$NB_UID:$NB_GID is disabled because julia was installed by root and only root had the permissions. If everything is OK, modify the README of julia-debian-build accordingly

# Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia



# # Quarto part
COPY --from=build-quarto /opt/quarto /opt/quarto
# TODO:  --chown=$NB_UID:$NB_GID is disabled because quarto was installed by root and only root had the permissions. If everything is OK, modify the README of quarto-debian-build accordingly
#
# # Making the application located at `/opt/quarto/bin/quarto` accessible from anywhere on your system by simply using the command `quarto`.
RUN ln -fs /opt/quarto/bin/quarto /usr/local/bin/quarto

# [There is no "Jupyter path"](https://github.com/quarto-dev/quarto-cli/discussions/9432)
# and it is currently no need to set QUARTO_PYTHON 
# Quarto CLI (e.g., `quarto preview ...`, `quarto render ...`) works when this container is built; however, additional VSCode settings needs to be correctly specified otherwise VSCode quarto extension won't work properly (cannot find Jupyter  pre-installed in minimal-notebook). See the settings in devcontainer.json
# ENV QUARTO_PYTHON=/opt/conda/bin/jupyter

RUN mkdir -p $WORKSPACE_DIR $SUB_PROJECT_DIR $JULIA_PKG_DEVDIR



## Fix permissions for NB_USER
# ERROR will occur if:
# - Without `chown $NB_USER:$NB_GID /home/$NB_USER`, subdirectories for vscode cannot be created because "/home/$NB_USER" is created and only owned by root.
RUN mkdir -p $VSCODE_PATH/extensions && \
    chown $NB_USER:$NB_GID $WORKSPACE_DIR && \
    chown $NB_USER:$NB_GID /usr/local/bin
# in order to install starship

# Switch to $NB_USER
# # Switch to $NB_USER is essential for the following RUN julia -e ...
# # because associated files and directories are owned by NB_USER
USER $NB_USER

# Install font via conda.
# RUN conda install font-ttf-noto-cjk font-ttf-noto-emoji -y

# Build IJulia
RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 

# Referring: https://github.com/okatsn/MyJuliaSpace/blob/master/.devcontainer/Dockerfile
# Also see: https://dvc.org/doc/install/linux#install-with-pip
RUN mamba install --quiet --yes \
    dvc \
    dvc-gdrive \
    dvc-webdav \
    dvc-ssh \
    # ipywidgets=8.0 \
    # invoke=2.0 \
    # pre-commit=3.1 \
    # commitizen=2.28 \
    # dvc=3.33.4 \
    # dvc-s3=2.21 \
    # dvc-gdrive=2.19 \
    # # DVC-S3 uses S3 protocol, such as for Amazon S3
    # jupyter_contrib_nbextensions=0.7 \
    && mamba clean --all -f -y

# Update pandoc to the latest
# (this allows typst conversion e.g., `pandoc input.typ -o output.docx`)
# RUN conda install -y -c conda-forge pandoc
# Use pandoc image directly instead. See stripcomments.sh



USER root
# Install UV
# See [How to create a python project using UV](https://youtu.be/PwGKhvqJCQM?si=DzCSBuMeVWuaYNCx&t=396)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# CHECKPOINT: How to use UV and multi-stage build of UV:
# - How to use it in the current `my-jupyter-with-julia` from [Step 2: Manage a Python Project](https://gemini.google.com/app/163205d2b0d67349)
# - Additional resource:
#   - [uv 容器化實作：使用官方 image 建立 Dockerfile](https://blog.kyomind.tw/uv-dockerfile/#%E5%BE%9E-Poetry-%E5%88%B0-uv%EF%BC%9ADockerfile-%E5%AF%AB%E6%B3%95%E5%A4%A7%E4%B8%8D%E5%90%8C)
#   - [Official multi-stage Dockerfile of uv aiming for production application](https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile)
ENV PATH=$PATH:$HOME/.local/bin


# # Set dvc auto-complete. This requires bash-completion to be installed.
# KEYNOTE: git auto-completion seems to be handled correctly in jupyter minimal notebook. For how to set git completion, you may refer to [the Dockerfile of MyTeXLife](https://github.com/okatsn/MyTeXLife/blob/fc00e3b840db2f63d8e3d67ac41065042f5b0602/.devcontainer/Dockerfile)
RUN dvc completion -s bash | tee /etc/bash_completion.d/dvc


USER $NB_USER

# You must start the container as NB_USER, because all apps are owned by NB_USER. For example, error will occur if a root user in Julia pkg REPL do `registry up`.
# USER root