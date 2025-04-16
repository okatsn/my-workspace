ARG DEBIAN_VERSION="blablabla"
ARG NB_GID="to be replaced by that in docker-compose.yml"

ARG NB_UID="to be replaced by that in docker-compose.yml"

# SETME:
ARG QUARTO_VER="1.6.43"
ARG QUARTO_URL="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VER}/quarto-${QUARTO_VER}-linux-amd64.deb"
# # or the latest:
# ARG QUARTO_URL = "https://quarto.org/download/latest/quarto-linux-amd64.deb"

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


RUN curl -LO ${QUARTO_URL} \
    && gdebi --non-interactive quarto-linux-amd64.deb



