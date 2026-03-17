FROM debian:bullseye-slim

ARG NB_USER
ARG NB_GID
ARG NB_UID
ARG HOME=home/${NB_USER}
ENV NB_USER=${NB_USER} \
    NB_GID=${NB_GID}\
    NB_UID=${NB_UID}



# Install basic functionality
RUN apt update \
    && apt install -y wget gnupg
# which is used for handling the GPG key.

# `tree` list the tree of file directory.
RUN apt-get update && apt-get install -y \
    curl \
    # Directory/File tree
    tree \
    # This is essential for dvc and bash completion
    bash-completion \
    # This update git.
    git



# Install DVC
RUN wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list \
    && wget -qO - https://dvc.org/deb/iterative.asc | gpg --dearmor > packages.iterative.gpg \
    && install -o root -g root -m 644 packages.iterative.gpg /etc/apt/trusted.gpg.d/ \
    && rm -f packages.iterative.gpg \
    && apt update \
    && apt -y install dvc \
    # DVC and git auto completion
    && dvc completion -s bash | tee /etc/bash_completion.d/dvc \
    && curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash > ~/.git-completion.sh


# Setup non-root user
RUN useradd -m -u $NB_UID -g $NB_GID -s /bin/bash $NB_USER


RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc