ARG DEBIAN_VERSION="blablabla"
FROM debian:${DEBIAN_VERSION}

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    bash-completion \
    lcov \
    jq \
    gdebi-core\
    && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# ghostscript for handling eps image files
# pdf2svg is for vscode eps-preview extension
# gdebi-core is for install deb file

# Install quarto
# See: 
# - https://www.r-bloggers.com/2022/07/how-to-set-up-quarto-with-docker-part-1-static-content/
# - https://docs.posit.co/resources/install-quarto/#quarto-deb-file-install
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
RUN gdebi --non-interactive quarto-linux-amd64.deb


USER $NB_USER
WORKDIR $WORKSPACE_DIR


COPY .devcontainer/startup_ijulia.jl /home/$NB_USER/.julia/config/startup_ijulia.jl

# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; Pkg.build(\"IJulia\")'"]
# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; println(pwd()); show(Pkg.status())'"]

