#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [--no-build] [tag1 tag2 ...]
# Without tags, pushes the tags derived from release.env (immutable, channel and latest).
source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/release_vars.sh"
IMAGE_NAME="$QUARTO_BUILD_IMAGE"
DEFAULT_TAGS=("$QUARTO_BUILD_TAG" "$QUARTO_BUILD_CHANNEL" latest)

build_image() {
  docker compose --env-file ../my-build.env build --no-cache
  docker tag qbuild "$IMAGE_NAME:temp"
}

smoke_test() {
  test "$(docker run --rm "$IMAGE_NAME:temp" quarto --version)" = "$QUARTO_VERSION"
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
