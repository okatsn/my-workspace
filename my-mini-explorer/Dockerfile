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
    # This is essential for dvc and bash completion
    bash-completion \
    # This update git.
    git \
    # Required for installing DVC via pip
    python3-pip



# Install DVC via pip (the apt repo at dvc.org/deb is no longer maintained)
RUN pip3 install dvc \
    # DVC bash completion
    && dvc completion -s bash | tee /etc/bash_completion.d/dvc \
    # Git bash completion
    && curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash > ~/.git-completion.sh


# Setup non-root user
RUN useradd -m -u $NB_UID -g $NB_GID -s /bin/bash $NB_USER

RUN mkdir -p $WORKSPACE_DIR && \
    mkdir -p $VSCODE_PATH/extensions && \
    chown $NB_USER:$NB_GID $WORKSPACE_DIR && \
    chown $NB_USER:$NB_GID /usr/local/bin

RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc