ARG DEBIAN_VERSION="blablabla"
ARG NB_GID="to be replaced by that in docker-compose.yml"
ARG NB_UID="to be replaced by that in docker-compose.yml"

FROM debian:${DEBIAN_VERSION}

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Install quarto
# See: 
# - https://www.r-bloggers.com/2022/07/how-to-set-up-quarto-with-docker-part-1-static-content/
# - https://docs.posit.co/resources/install-quarto/#quarto-deb-file-install


