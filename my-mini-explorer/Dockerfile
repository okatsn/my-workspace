# okatsn/my-mini-explorer
FROM debian:bullseye-slim


ARG NB_USER
ARG NB_GID
ARG NB_UID
ARG HOME=home/${NB_USER}
ENV NB_USER=${NB_USER} \
    NB_GID=${NB_GID}\
    NB_UID=${NB_UID}

ARG VSCODE_PATH="$HOME/.vscode-server/"
ARG WORKSPACE_DIR="$HOME/workspace/"

# `tree` list the tree of file directory.
RUN apt-get update && apt-get install -y \
    curl \
    # Directory/File tree
    tree \
    # # This install/update git.
    # git \
    # # Required for installing DVC via pip
    # python3-pip \
    # This is essential for dvc and bash completion
    bash-completion



# # Install DVC via pip (the apt repo at dvc.org/deb is no longer maintained)
# RUN pip3 install dvc \
#     # DVC bash completion
#     && dvc completion -s bash | tee /etc/bash_completion.d/dvc




# Setup non-root user
RUN useradd -m -u $NB_UID -g $NB_GID -s /bin/bash $NB_USER

# # Git bash completion (must run after useradd -m creates the home directory)
# # .bash_profile sources ~/.git-completion.bash, so the filename must match exactly
# RUN curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash \
#     -o /home/$NB_USER/.git-completion.bash

RUN mkdir -p $WORKSPACE_DIR && \
    mkdir -p $VSCODE_PATH/extensions && \
    # # This allows installation at runtime
    # chown $NB_USER:$NB_GID /usr/local/bin && \
    chown $NB_USER:$NB_GID $WORKSPACE_DIR

RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    # && echo 'if [ -f ~/.git-completion.bash ]; then . ~/.git-completion.bash; fi' >> ~/.bashrc \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc

# # `.bash_profile` sources ~/.git-completion.bash (for login shells)
# COPY --chown=$NB_UID:$NB_GID .devcontainer/.bash_profile /$HOME/.bash_profile

# # # Set dvc auto-complete. This requires bash-completion to be installed.
# RUN dvc completion -s bash | tee /etc/bash_completion.d/dvc
