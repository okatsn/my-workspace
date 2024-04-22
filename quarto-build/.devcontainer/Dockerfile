# Build stage
FROM okatsn/my-julia-space:v1.9.4

USER root
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


USER $NB_USER
WORKDIR $WORKSPACE_DIR


COPY .devcontainer/startup_ijulia.jl /home/$NB_USER/.julia/config/startup_ijulia.jl

# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; Pkg.build(\"IJulia\")'"]
# ENTRYPOINT ["julia", "--project=@.", "-e", "'using Pkg; println(pwd()); show(Pkg.status())'"]

