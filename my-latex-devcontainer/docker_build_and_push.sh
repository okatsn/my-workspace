#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [--no-build] <tag1> [tag2 ...]
IMAGE_NAME="okatsn/my-latex-devcontainer"

build_image() {
  docker compose --env-file ../my-build.env build --no-cache
  docker tag jtexworkspace "$IMAGE_NAME:temp"
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
