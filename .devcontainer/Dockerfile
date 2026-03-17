FROM okatsn/my-mini-explorer:latest

# Add any project-specific tools or configurations below.
# Example: install additional apt packages
# RUN apt-get update && apt-get install -y \
#     your-package \
#     && rm -rf /var/lib/apt/lists/*


## Install Starship
## Starship configuration
ARG NB_USER


# Note: Since pip installs dvc to a specific path, you might need to rename
# the original DVC binary to `dvc.real` and name the wrapper `dvc`.

USER $NB_USER