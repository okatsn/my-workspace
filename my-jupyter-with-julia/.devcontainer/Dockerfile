FROM okatsn/my-julia-build:v1.10-2024d as build-julia
FROM okatsn/my-quarto-build:2024c as build-quarto

# Please refer to https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-minimal-notebook
# # Docker image repository seems to moved to quay.io
# # The list of available tags: https://quay.io/repository/jupyter/minimal-notebook?tab=tags
FROM quay.io/jupyter/minimal-notebook:2024-07-15

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


# # Julia part
COPY --from=build-julia --chown=$NB_UID:$NB_GID /home/okatsn/.julia /home/$NB_USER/.julia

COPY --from=build-julia --chown=$NB_UID:$NB_GID /opt/julia-okatsn /opt/julia-okatsn

# Optional: Use customized Project.toml for default julia environment.
# The variable JULIA_PROJECT is defined in my-julia-build
COPY --chown=$NB_UID:$NB_GID .devcontainer/Project_for_env.toml /home/$NB_USER/.julia/environments/${JULIA_PROJECT}/Project.toml

# Create link in the new machine (based on that /usr/local/bin/ is already in PATH)
RUN ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia



# # Quarto part
COPY --from=build-quarto --chown=$NB_UID:$NB_GID /opt/quarto /opt/quarto
# Making the application located at `/opt/quarto/bin/quarto` accessible from anywhere on your system by simply using the command `quarto`.
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


# Build IJulia
RUN julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");' 


# You must start the container as NB_USER, because all apps are owned by NB_USER. For example, error will occur if a root user in Julia pkg REPL do `registry up`.
# USER root