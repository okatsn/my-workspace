FROM okatsn/my-mini-explorer:latest

# Add any project-specific tools or configurations below.
# Example: install additional apt packages
# RUN apt-get update && apt-get install -y \
#     your-package \
#     && rm -rf /var/lib/apt/lists/*


## Install Starship
## Starship configuration
ARG NB_USER


# ==========================================
# AI SANDBOX SECURITY WRAPPERS
# ==========================================

# 1. Secure Git Wrapper
# Rename the original git binary so the agent can't bypass the wrapper using an absolute path
RUN mv /usr/bin/git /usr/bin/git.real

# Create the interceptor script
RUN echo '#!/bin/bash\n\
    for arg in "$@"; do\n\
    # Intercept any command containing "push"\n\
    if [[ "$arg" == "push" ]]; then\n\
    echo "🚨 SECURITY BLOCKED: '\''git push'\'' is disabled in this AI sandbox to protect the remote repository." >&2\n\
    exit 1\n\
    fi\n\
    done\n\
    # If safe, pass all arguments to the real git binary\n\
    exec /usr/bin/git.real "$@"' > /usr/bin/git && \
    chmod +x /usr/bin/git

# 2. Secure DVC Wrapper
# Since DVC was installed via pip as root, it resides in /usr/local/bin/dvc
RUN mv /usr/local/bin/dvc /usr/local/bin/dvc.real

# Create the interceptor script
RUN echo '#!/bin/bash\n\
    for arg in "$@"; do\n\
    # Intercept push and garbage collection (gc)\n\
    if [[ "$arg" == "push" ]] || [[ "$arg" == "gc" ]]; then\n\
    echo "🚨 SECURITY BLOCKED: '\''dvc $arg'\'' is disabled in this AI sandbox." >&2\n\
    exit 1\n\
    fi\n\
    done\n\
    # If safe, pass all arguments to the real dvc binary\n\
    exec /usr/local/bin/dvc.real "$@"' > /usr/local/bin/dvc && \
    chmod +x /usr/local/bin/dvc

# ==========================================

# Note: Since pip installs dvc to a specific path, you might need to rename
# the original DVC binary to `dvc.real` and name the wrapper `dvc`.

USER $NB_USER