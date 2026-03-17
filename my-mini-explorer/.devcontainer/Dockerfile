FROM okatsn/my-mini-explorer:latest

# Add any project-specific tools or configurations below.
# Example: install additional apt packages
# RUN apt-get update && apt-get install -y \
#     your-package \
#     && rm -rf /var/lib/apt/lists/*

ARG NB_USER
ARG NB_GID
ARG NB_UID
ARG HOME=home/${NB_USER}

RUN useradd -m -u $NB_UID -g $NB_GID -s /bin/bash $NB_USER



RUN mkdir -p /home/root/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship

## Install Starship
## Starship configuration
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc

USER $NB_USER