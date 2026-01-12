#!/bin/bash

set -e

# Pause before exit when the script fails so the caller can see the error.
# - Uses an EXIT trap to catch any non-zero exit (including explicit `exit 1`).
# - If running interactively it prompts the user to press Enter. In CI or
#   non-interactive environments it sleeps for 5 seconds instead.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then
  echo "\nERROR: script exited with code $rc at $(date)" >&2
  # If running in CI or not attached to a terminal, avoid waiting for input.
  if [ -n "$CI" ] || [ ! -t 1 ]; then
    echo "Non-interactive or CI environment detected; sleeping 5s before exit..." >&2
    sleep 5
  else
    read -rp "Press Enter to exit..."
  fi
fi' EXIT

IMAGE_NAME="okatsn/my-tex-life-with-julia"
BUILD_IMAGE=true
TAGS=()

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-build) BUILD_IMAGE=false; shift ;;
        *) TAGS+=("$1"); shift ;;
    esac
done

# Check if any tags were provided
if [ ${#TAGS[@]} -eq 0 ]; then
  echo "Usage: $0 [--no-build] <tag1> [tag2 ...]"
  sleep 5
  exit 1
fi

# Build the image if BUILD_IMAGE is true
if [ "$BUILD_IMAGE" = true ]; then
  echo "Building Docker image with tag: $IMAGE_NAME:temp"
  # Build with docker compose
  docker compose --env-file ../my-build.env build --no-cache
  docker tag jtexworkspace "$IMAGE_NAME:temp"
else
  echo "Skipping build step (--no-build specified)."
  echo "Assuming image $IMAGE_NAME:temp already exists locally..."
fi

# Tag and push all specified tags
for TAG in "${TAGS[@]}"; do
  echo "Tagging image as: $IMAGE_NAME:$TAG"
  docker tag "$IMAGE_NAME:temp" "$IMAGE_NAME:$TAG"

  echo "Pushing Docker image: $IMAGE_NAME:$TAG"
  docker push "$IMAGE_NAME:$TAG"
done

echo "Docker image processed successfully for tags: ${TAGS[*]}"
