#!/usr/bin/env bash
# Usage: ./docker_build_and_push.sh [--no-build] <tag1> [tag2 ...]
IMAGE_NAME="okatsn/my-util-box"

build_image() {
  docker build -t "$IMAGE_NAME:temp" .
}

source "$(dirname "${BASH_SOURCE[0]}")/../shscripts/docker_build_push_lib.sh"
