FROM debian:bullseye-slim

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

