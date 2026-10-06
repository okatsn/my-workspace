#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [tag1 tag2 ...]
# Typst is not built here: the official image of TYPST_VERSION is mirrored to the immutable, channel and latest tags derived from release.env.
source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/release_vars.sh"
IMAGE_NAME="$TYPST_BUILD_IMAGE"
MIRROR_FROM="$TYPST_UPSTREAM_REF"
DEFAULT_TAGS=("$TYPST_BUILD_TAG" "$TYPST_BUILD_CHANNEL" latest)

# The entrypoint of the official image is /bin/typst, and `--version` prints "typst 0.14.2 (<commit>)".
smoke_test() {
  [[ "$(docker run --rm "$1" --version)" == "typst $TYPST_VERSION "* ]] ||
    { echo "ERROR: $1 is not typst $TYPST_VERSION" >&2; return 1; }
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
