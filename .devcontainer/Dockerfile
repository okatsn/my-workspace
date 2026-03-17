FROM okatsn/my-mini-explorer:latest

# Add any project-specific tools or configurations below.
# Example: install additional apt packages
# RUN apt-get update && apt-get install -y \
#     your-package \
#     && rm -rf /var/lib/apt/lists/*


## Install Starship
## Starship configuration
ARG NB_USER


# ... [Keep your previous Dockerfile steps above this] ...

# 1. Create a safe wrapper for Git
RUN echo '#!/bin/bash\n\
    for arg in "$@"; do\n\
    if [[ "$arg" == "push" ]]; then\n\
    echo "🚨 SECURITY: git push is disabled in this AI sandbox."\n\
    exit 1\n\
    fi\n\
    done\n\
    exec /usr/bin/git "$@"' > /usr/local/bin/git && \
    chmod +x /usr/local/bin/git

# 2. Create a safe wrapper for DVC
RUN echo '#!/bin/bash\n\
    for arg in "$@"; do\n\
    if [[ "$arg" == "push" ]] || [[ "$arg" == "gc" ]]; then\n\
    echo "🚨 SECURITY: dvc push/gc are disabled in this AI sandbox."\n\
    exit 1\n\
    fi\n\
    done\n\
    # Assuming DVC was installed via pip to ~/.local/bin or similar, \n\
    # we need to point to the real executable. \n\
    exec /usr/local/bin/dvc.real "$@"' > /usr/local/bin/dvc-wrapper && \
    chmod +x /usr/local/bin/dvc-wrapper

# Note: Since pip installs dvc to a specific path, you might need to rename
# the original DVC binary to `dvc.real` and name the wrapper `dvc`.

USER $NB_USER