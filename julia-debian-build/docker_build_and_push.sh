#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [--no-build] [tag1 tag2 ...]
# Without tags, pushes the tags derived from release.env (immutable, channel and latest).
IMAGE_NAME="okatsn/my-julia-build"

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/release_vars.sh"
DEFAULT_TAGS=("$JULIA_BUILD_TAG" "$JULIA_BUILD_CHANNEL" latest)

build_image() {
  docker compose --env-file ../my-build.env build --no-cache
  docker tag jbuild "$IMAGE_NAME:temp"
}

smoke_test() {
  docker run --rm "$IMAGE_NAME:temp" julia --startup-file=no -e "
    @assert VERSION == v\"$JULIA_VERSION\"
    @assert ENV[\"JULIA_PROJECT\"] == \"$JULIA_PROJECT\"
    println(\"Julia \", VERSION, \" OK\")"
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
