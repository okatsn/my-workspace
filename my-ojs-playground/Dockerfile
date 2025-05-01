# Use a stable Node.js release as the base image
FROM node:lts
USER root
# Root user is necessary for the following command that creates the julia/quarto... link


# # Fix permissions for directories that is going to be mounted as volume but not-yet created when building this image. For those mounted as volume but user might need their permissions, directories must be made first.
#
# - The starship cache: allow starship to create log. 
RUN mkdir -p /home/$NB_USER/.cache/starship && chown -R $NB_USER:$NB_GID /home/$NB_USER/.cache/starship
## Install Starship
## Starship configuration
COPY --chown=$NB_UID:$NB_GID .devcontainer/starship.toml /$HOME/.config/starship.toml
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc



USER $NB_USER

# Set the working directory in the container
WORKDIR /app

# Install pnpm globally, which is recommended by Observable Framework
RUN npm install -g pnpm

# The container is now set up to run Observable Framework commands.
# You can
# 1. Mount your project directory into the container
# 2. Open a shell in the container
# 3. Run the tutorial commands like `pnpm init @observablehq` and `pnpm dev`