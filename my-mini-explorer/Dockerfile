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
    && curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash > ${HOME}/.git-completion.sh




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


# # Set dvc auto-complete. This requires bash-completion to be installed.
RUN dvc completion -s bash | tee /etc/bash_completion.d/dvc
