# KEYNOTE: How to build the image solely from this Dockerfile:
# (In MyJuliaSpace/; change "latest" to any other tag names)
# $ docker build -t myjspace -f .devcontainer/Dockerfile .
# $ docker tag myjspace okatsn/my-julia-space:latest
# $ docker push okatsn/my-julia-space:latest
#
# Why not use devcontainer.json to build?
# - Building image from devcontainer.json creates some additional files, such as those in /home/jovyan/.vscode-server and /home/jovyan/.vscode-server-insiders
# - If there are other container (saying the-target) built upon this image, and it also has /home/jovyan/.vscode-server but should with different content, the files in source (my-julia-space) is kept, and those in the target are discarded. This is not what we want.
#
# TODOs:
# - auto pairing for .qmd (``, ...) (auto closing works fine)
# - consider delete docker-compose.yml and devcontainer.json
#
# References:
# https://github.com/andferrari/julia_notebook/blob/master/Dockerfile
# https://github.com/marius311/CMBLensing.jl/blob/master/Dockerfile
# https://github.com/MalteBoehm/julia_docker-compose_template/blob/main/Dockerfile

FROM okatsn/my-julia-build as build-julia
# Please refer to the instruction in the Dockerfile of okatsn/my-julia-build

FROM jupyter/minimal-notebook:python-3.10
# From dockerhub get an example image that you don't need to build your linux environment from scratch
# https://hub.docker.com/layers/jupyter/minimal-notebook/python-3.10/images/sha256-ff7d41def49b6805cb40c0e570d0a0fa12131d1bb9377d7744935be561d16dc9?context=explore
USER root


# RUN echo $("ls")
# To see where am I

ARG WORKSPACE_DIR=/home/jovyan/devspace
## Starship configuration
# - The current building context (see docker-compose.yml) is ".." (the parent folder of Dockerfile); thus .devcontainer/starship.toml is the right directory
# - In jupyter/base-notebook, WORKDIR is switched to $HOME; in jupyter/minimal-notebook, no WORKDIR switch action. The WORKDIR in previous building seems to be void in this stage.
# - Make sure all things under /home/$NB_USER should be fix-permissions later.
COPY .devcontainer/starship.toml /home/$NB_USER/.config/starship.toml


# [Optional] Add sudo support. Omit if you don't need to install software after connecting.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    sudo \
    curl \
    bash-completion \
    lcov \
    jq \
    ghostscript \
    pdf2svg \
    gdebi-core\
    tree \
    && echo $NB_USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$NB_USER \
    && chmod 0440 /etc/sudoers.d/$NB_USER \
    && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# ghostscript for handling eps image files
# pdf2svg is for vscode eps-preview extension
# gdebi-core is for install deb file
# tree is a convenient tool to print directory tree

# Install quarto
# See: 
# - https://www.r-bloggers.com/2022/07/how-to-set-up-quarto-with-docker-part-1-static-content/
# - https://docs.posit.co/resources/install-quarto/#quarto-deb-file-install
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
RUN gdebi --non-interactive quarto-linux-amd64.deb

# Install Julia
ARG JULIA_PKG_DEVDIR=/home/jovyan/.julia/dev
ARG SUB_PROJECT_DIR=/home/jovyan/devspace/subprojects

# Set enviroment variable
ENV JULIA_PKG_DEVDIR=${JULIA_PKG_DEVDIR} \
    SUB_PROJECT_DIR=${SUB_PROJECT_DIR}
# equivalent to:
# RUN export JULIA_PKG_DEVDIR=${JULIA_PKG_DEVDIR}


# CHECKPOINT: I don't know why USER's GID is 1000, which is not 100  as here (https://hub.docker.com/layers/jupyter/minimal-notebook/ubuntu-22.04/images/sha256-a1b3973c6699351118799ad96b55c1fa71b186fa2a9983a4a63aa103905fb073?context=explore) or here (https://hub.docker.com/r/jupyter/base-notebook/dockerfile)
# Add NB_USER to the group of NB_GID (fix-permissions still failed (14/14] RUN fix-permissions /home/jovyan))
# RUN usermod -g $NB_GID $NB_USER



# NB_USER is defined in jupyter/minimal-notebook
USER $NB_USER
WORKDIR $WORKSPACE_DIR


# Environments
# TODO: Use environment.yml, Project.toml and Manifest.toml to add python and julia packages

# # KEYNOTE: disable conda env update if:
# - UnsatisfiableError: The following specifications were found to be incompatible with a past
# pinned spec python==3.10.10 conflicts with explicit specs. (by conda-forge)
# COPY .devcontainer/environment.yml ${WORKSPACE_DIR}
# RUN conda env update --file environment.yml \
#     && rm -f environment.yml
#     && mkdir -p ~/.julia/environments/v`echo ${VARIANT} | cut -d. -f 1,2`
#     && cp Project.toml Manifest.toml ~/.julia/environments/v`echo ${VARIANT} | cut -d. -f 1,2`/Project.toml \
#     && julia -e 'using Pkg; Pkg.instantiate(); Pkg.precompile()'

# Add python packages and add invoke shell completion
# installation of rise: equivalent to `conda install -c conda-forge rise` in bash.
#     Note that installing "rise" and other packages at the same time will give an error (not sure why), so use the new install command line to install "rise".
# jupyter_contrib_nbextensions: equivalent to `pip install jupyter_contrib_nbextensions` and `jupyter contrib nbextension install --user` in bash.
# BONUS: setting `"rise": {"scroll": true}`: Open File in vscode (Ctrl+O) and add `"rise": {"scroll": true}` in `/home/<username>/.jupyter/nbconfig/notebook.json`.
# HINT: `conda list` to see the version.
# HINT: `jupyter notebook` in bash to get the link to the notebook hosted in the virtual machine.
# TODO: write documentation in InstallJupyterLabWithoutAnaconda.md


# KEYNOTE: In cases of AttributeError, (e.g., AttributeError: module 'lib' has no attribute 'OpenSSL_add_all_algorithms'), try the followings:
# # [In the case where there is no attribute openssl](https://stackoverflow.com/questions/74980825/build-the-project-in-git-actions-using-sam-i-am-getting-new-error-attributeerr)
# RUN pip install --upgrade pyopenssl
# Similar issues:
# # https://askubuntu.com/questions/1428181/module-lib-has-no-attribute-x509-v-flag-cb-issuer-check/1433089#1433089
# # https://stackoverflow.com/questions/73830524/attributeerror-module-lib-has-no-attribute-x509-v-flag-cb-issuer-check
# RUN pip install pip --upgrade \
#     && pip install pyopenssl --upgrade
#
# # [In the case where there is no attribute X509_V_FLAG_CB_ISSUER_CHECK](https://stackoverflow.com/questions/74705127/how-to-fix-error-module-lib-has-no-attribute-x509-v-flag-cb-issuer-check)
# RUN pip uninstall -y cryptography \
#     && pip install --upgrade cryptography==36.0.2

# KEYNOTE: Pinned Version is successfully installed at 2023-03-03
RUN mamba install --quiet --yes \
    ipywidgets=8.0 \
    invoke=2.0 \
    pre-commit=3.1 \
    commitizen=2.28 \
    dvc=3.33.4 \
    # dvc-s3=2.21 \
    # dvc-gdrive=2.19 \
    # # DVC-S3 uses S3 protocol, such as for Amazon S3
    jupyter_contrib_nbextensions=0.7 \
    && mamba clean --all -f -y \
    && npm cache clean --force

# Avoid VS Code extension reinstalls. For more information, see
# - https://github.com/microsoft/vscode-remote-release/issues/7690
# - https://code.visualstudio.com/remote/advancedcontainers/overview#_advanced-containers-topics
# - https://code.visualstudio.com/docs/devcontainers/containers#_create-a-devcontainerjson-file

RUN mkdir -p $JULIA_PKG_DEVDIR \
    $SUB_PROJECT_DIR

# Jupyter settings
RUN mkdir -p /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/notebook-extension \
    && echo '{"codeCellConfig": {"lineNumbers": true}}' | jq\
    >> /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/notebook-extension/tracker.jupyterlab-settings \
    && mkdir -p /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/shortcuts-extension \
    && echo '{"shortcuts": [{"command": "runmenu:restart-and-run-all", "keys": ["Alt R"], "selector": "[data-jp-code-runner]"}]}' | jq\
    >> /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/shortcuts-extension/shortcuts.jupyterlab-settings \
    && mkdir -p /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/apputils-extension \
    && echo '{"modal": false}' | jq\
    >> /home/$NB_USER/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/palette.jupyterlab-settings \
    && mkdir -p /home/$NB_USER/.jupyter/nbconfig \
    && echo '{"nbext_hide_incompat": false}' | jq \
    >> /home/$NB_USER/.jupyter/nbconfig/commom.json \
    && echo '{"load_extensions": {"toc2/main": true}, "rise": {"scroll": true, "enable_chalkboard": true}}' | jq \
    >> /home/$NB_USER/.jupyter/nbconfig/notebook.json

# Shell completion and alias
RUN inv --print-completion-script bash > ~/.invoke-completion.sh \
    && echo "source ~/.invoke-completion.sh" >> ~/.bashrc \
    && dvc completion -s bash | sudo tee /etc/bash_completion.d/dvc \
    && echo -e "alias juliaclient='julia --startup-file=no -e \"using DaemonMode; runargs()\"'" >> ~/.bashrc

# Install Starship
RUN sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- -y \
    && echo 'eval "$(starship init bash)"' >> ~/.bashrc \
    && mkdir -p ~/.config
#    && echo -e '[conda]\nsymbol = "Conda "\nignore_base = false' > ~/.config/starship.toml
# starship settings are now all managed directly in .devcontainer/starship.toml
# ">" : overwrite
# ">>": append

# # CHECKPOINT: Temporary disable fix-permissions
# RUN fix-permissions /home/$NB_USER
# See also: [The fix-permissions script must be re-run on $HOME after various setup.](https://github.com/jupyter/docker-stacks/issues/547)

# # KEYNOTE: For OhMyREPL etc.
# RUN mkdir -p /home/$NB_USER/.julia/config && cp .devcontainer/startup.jl "$_" # This mkdir all necessary paths and copy files to there in one line. It worked in bash but failed in Dockerfile.
# KEYNOTE: use $HOME instead of /home/$NB_USER will fail! Since $HOME is not recognized as absolute directory!
COPY --from=build-julia /home/okatsn/.julia /home/$NB_USER/.julia
COPY --from=build-julia /opt/julia-okatsn /opt/julia-okatsn
RUN sudo ln -fs /opt/julia-okatsn/bin/julia /usr/local/bin/julia

# Pluto port
EXPOSE 1234