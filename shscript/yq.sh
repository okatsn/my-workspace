#!/bin/bash

# Check if required arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <yq_command> <target_file>"
  echo "Example: $0 '.key = \"value\"' config.yaml"
  sleep 5
  exit 1
fi

# Assign command-line arguments to variables
yq_command="$1"
target_file="$2"

# Check if target file exists
if [ ! -f "$target_file" ]; then
  echo "Error: Target file '$target_file' does not exist."
  sleep 5
  exit 1
fi

# Run yq command using Docker
docker run --rm \
  --volume "$(pwd):/workspace" \
  --workdir /workspace \
  --user "$(id -u):$(id -g)" \
  okatsn/my-util-box:v2025b "yq -i $yq_command $target_file"

echo "Applied yq command to $target_file"