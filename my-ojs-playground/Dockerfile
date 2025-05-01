# Use a stable Node.js release as the base image
FROM node:lts

# Set the working directory in the container
WORKDIR /app

# --- Install pnpm (typically done as root for global installs) ---
RUN npm install -g pnpm

# --- Install Starship (typically done as root for global binary) ---
# Download and run the Starship installer script
# The binary will be placed in a system PATH location accessible to all users
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- -y

# --- Configure Starship for the 'node' user ---
# Switch to the non-root 'node' user provided by the base image
USER node

# Set the HOME environment variable explicitly for the 'node' user's session
ENV HOME=/home/node

# Create necessary directories for Starship configuration and cache
# Running mkdir as the 'node' user ensures correct ownership
RUN mkdir -p "$HOME/.config" \
    "$HOME/.cache/starship"

# Copy the Starship configuration file from your local machine
# Make sure you have the starship.toml file in a `.devcontainer` directory
# relative to your Dockerfile.
# Use --chown to ensure the copied file belongs to the 'node' user
COPY --chown=node:node .devcontainer/starship.toml "$HOME/.config/starship.toml"

# Add Starship initialization to the node user's .bashrc
# This ensures Starship is activated when you start a bash session as the node user
RUN echo 'eval "$(starship init bash)"' >> "$HOME/.bashrc"

# --- End Starship Configuration ---

# The container is now set up with Node.js, pnpm, and Starship for the 'node' user.
# When you run the container interactively (e.g., `docker run -it ... bash`),
# you will be the 'node' user in the /app working directory, with Starship enabled.

# To use, build the image and run it mounting your project:
# docker build -t observable-framework-tutorial .
# docker run -it -v /path/to/your/observable-project:/app -p 3000:3000 observable-framework-tutorial bash
# Then follow the tutorial steps inside the container.