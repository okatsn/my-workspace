#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [--no-build] [tag1 tag2 ...]
# Without tags, pushes the tags derived from release.env (immutable, channel and latest).
source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/release_vars.sh"
IMAGE_NAME="$JUPYTER_IMAGE"
DEFAULT_TAGS=("$JUPYTER_TAG" "$JUPYTER_CHANNEL" latest)

build_image() {
  # Fail before the long build if a build image has not been pushed yet.
  for ref in "$JULIA_BUILD_REF" "$QUARTO_BUILD_REF" "$TYPST_BUILD_REF"; do
    docker buildx imagetools inspect "$ref" >/dev/null || { echo "ERROR: build image not in the registry: $ref" >&2; exit 1; }
  done
  docker compose --env-file ../my-build.env build --no-cache
  docker tag juliaworkspace "$IMAGE_NAME:temp"
}

# The checks run inside the container because the entrypoint of the image prints its own log to stdout.
smoke_test() {
  docker run --rm -e JULIA_VERSION -e QUARTO_VERSION "$IMAGE_NAME:temp" bash -c '
    test "$(julia --startup-file=no -e "print(VERSION)")" = "$JULIA_VERSION" &&
    test "$(quarto --version)" = "$QUARTO_VERSION" &&
    typst --version'
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
