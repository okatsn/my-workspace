#!/usr/bin/env bash
# Shared logic of every `docker_build_and_push.sh`; source it from a wrapper that defines:
# - `IMAGE_NAME`: e.g., "okatsn/my-julia-build"
# - `build_image`: a function that builds the image and tags it as "$IMAGE_NAME:temp"
# Optional in the wrapper:
# - `DEFAULT_TAGS`: an array of tags to push when none is given on the command line
# - `smoke_test`: a function that must succeed on "$IMAGE_NAME:temp" before anything is pushed
#
# Usage of the wrapper: ./docker_build_and_push.sh [--no-build] [tag1 tag2 ...]
#
# A tag like `v2026c.0` or `v1.12-2026c.0` is immutable: pushing is refused if it already exists in the registry.
# Execute the wrapper (do not `source` it) so that `exit` and `set` do not affect your shell.
set -Eeuo pipefail
trap 'echo "ERROR: line $LINENO: $BASH_COMMAND (exit $?)" >&2' ERR

: "${IMAGE_NAME:?IMAGE_NAME must be set by the wrapper}"
declare -F build_image >/dev/null || { echo "ERROR: build_image must be defined by the wrapper" >&2; exit 2; }

# Wrappers rely on relative paths such as `../my-build.env`.
cd "$(dirname "${BASH_SOURCE[1]}")"

BUILD_IMAGE=true
TAGS=()
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --no-build) BUILD_IMAGE=false ;;
    *) TAGS+=("$1") ;;
  esac
  shift
done

if [ ${#TAGS[@]} -eq 0 ] && [ -n "${DEFAULT_TAGS+x}" ]; then
  TAGS=("${DEFAULT_TAGS[@]}")
fi

if [ ${#TAGS[@]} -eq 0 ]; then
  echo "Usage: $0 [--no-build] <tag1> [tag2 ...]" >&2
  exit 1
fi

# Fail before building (not after) if an immutable tag is taken or the registry cannot be checked.
for TAG in "${TAGS[@]}"; do
  [[ "$TAG" =~ [0-9]{4}[a-z]\.[0-9]+$ ]] || continue
  if out=$(docker buildx imagetools inspect "$IMAGE_NAME:$TAG" 2>&1); then
    echo "ERROR: immutable tag already exists: $IMAGE_NAME:$TAG (bump the revision)" >&2
    exit 1
  elif [[ "$out" != *"not found"* ]]; then
    echo "ERROR: cannot verify $IMAGE_NAME:$TAG in the registry: $out" >&2
    exit 1
  fi
done

if [ "$BUILD_IMAGE" = true ]; then
  echo "Building Docker image with tag: $IMAGE_NAME:temp"
  build_image
else
  echo "Skipping build step (--no-build specified)."
  echo "Assuming image $IMAGE_NAME:temp already exists locally..."
  docker image inspect "$IMAGE_NAME:temp" >/dev/null
fi

if declare -F smoke_test >/dev/null; then
  echo "Smoke testing $IMAGE_NAME:temp"
  smoke_test
fi

for TAG in "${TAGS[@]}"; do
  echo "Tagging image as: $IMAGE_NAME:$TAG"
  docker tag "$IMAGE_NAME:temp" "$IMAGE_NAME:$TAG"

  echo "Pushing Docker image: $IMAGE_NAME:$TAG"
  docker push "$IMAGE_NAME:$TAG"
done

echo "Docker image processed successfully for tags: ${TAGS[*]}"
