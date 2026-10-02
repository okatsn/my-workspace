ARG DEBIAN_VERSION="blablabla"
ARG NB_GID="to be replaced by that in docker-compose.yml"

ARG NB_UID="to be replaced by that in docker-compose.yml"

# QUARTO_VER (e.g., "1.8.26") has no default: set it in `release.env` and build via `docker_build_and_push.sh`.
ARG QUARTO_VER
ARG QUARTO_URL="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VER}/quarto-${QUARTO_VER}-linux-amd64.deb"
ARG QUARTO_FILE="quarto-${QUARTO_VER}-linux-amd64.deb"
# # or the latest:
# ARG QUARTO_URL="https://quarto.org/download/latest/quarto-linux-amd64.deb"
# ARG QUARTO_FILE="quarto-linux-amd64.deb"

FROM debian:${DEBIAN_VERSION}

# Re-declare ARGs after FROM to make them available
ARG QUARTO_VER
ARG QUARTO_URL
ARG QUARTO_FILE

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


# - `curl -f` fails on HTTP errors; the last check fails the build if the installed Quarto is not QUARTO_VER.
RUN : "${QUARTO_VER:?QUARTO_VER is required}" \
    && echo "QUARTO_URL: ${QUARTO_URL}" \
    && curl -fLO ${QUARTO_URL} \
    && gdebi --non-interactive ${QUARTO_FILE} \
    && test "$(quarto --version)" = "${QUARTO_VER}"



