ARG DEBIAN_VERSION="blablabla"
ARG NB_GID="to be replaced by that in docker-compose.yml"
ARG NB_UID="to be replaced by that in docker-compose.yml"

FROM debian:${DEBIAN_VERSION}

USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-pip \
    && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN pip3 install tldr
