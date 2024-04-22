ARG DEBIAN_VERSION="blablabla"
ARG NB_GID="to be replaced by that in docker-compose.yml"
ARG NB_UID="to be replaced by that in docker-compose.yml"

FROM debian:${DEBIAN_VERSION}

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
     # gdebi-core is for install deb file
    gdebi-core\
    && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Install quarto
# See: 
# - https://www.r-bloggers.com/2022/07/how-to-set-up-quarto-with-docker-part-1-static-content/
# - https://docs.posit.co/resources/install-quarto/#quarto-deb-file-install

RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb \
    && gdebi --non-interactive quarto-linux-amd64.deb

RUN mkdir -p /home/$NB_USER/.julia/config
COPY startup_ijulia.jl /home/$NB_USER/.julia/config/startup_ijulia.jl


