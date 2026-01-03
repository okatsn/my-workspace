#!/bin/sh
set -e
# Pause before exit when the script fails so the caller can see the error.
# - Uses an EXIT trap to catch any non-zero exit (including explicit `exit 1`).
# - If running interactively it prompts the user to press Enter. In CI or
#   non-interactive environments it sleeps for 5 seconds instead.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then
  echo "\nERROR: script exited with code $rc at $(date)" >&2
  if [ -n "$CI" ] || [ ! -t 1 ]; then
    echo "Non-interactive or CI environment detected; sleeping 5s before exit..." >&2
    sleep 5
  else
    read -rp "Press Enter to exit..."
  fi
fi' EXIT

# The version is the first argument, referring `ls -la ~/.julia/environments/` (e.g., "v1.12")
# For example:
# ```bash
# . .devcontainer/init.sh "v1.12"
# ```
if [ -z "$1" ]; then
  echo "ERROR: VERSION argument is required (e.g., v1.12)" >&2
  exit 1
fi

VERSION="$1"

JULIA_ENV_DIR="$HOME/.julia/environments/$VERSION"
JULIA_CONFIG_DIR="$HOME/.julia/config/"

mkdir -p "$JULIA_ENV_DIR"
mkdir -p "$JULIA_CONFIG_DIR"

cp -f /tmp/julia/Project.toml "${JULIA_ENV_DIR}/Project.toml"
cp -f /tmp/julia/startup.jl "${JULIA_CONFIG_DIR}/startup.jl"

echo "Project.toml and startup.jl copied!"

julia -e 'using Pkg; Pkg.update(); Pkg.instantiate(); Pkg.build("IJulia");'

echo "Julia environment $VERSION instantiated complete"