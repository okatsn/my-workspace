FROM mcr.microsoft.com/devcontainers/universal:5-linux

# OPTION 1: The "Shim" (Best for Vibe Coding)
# Keeps 'git' for local commits but blocks 'push'
RUN mv /usr/bin/git /usr/bin/git-real \
    && echo '#!/bin/sh\n\
    if [ "$1" = "push" ]; then\n\
    echo "🚫 GIT PUSH BLOCKED: Vibe coding safety active."\n\
    exit 1\n\
    fi\n\
    exec /usr/bin/git-real "$@"' > /usr/bin/git \
    && chmod +x /usr/bin/git

# RUN sudo apt-get remove -y git