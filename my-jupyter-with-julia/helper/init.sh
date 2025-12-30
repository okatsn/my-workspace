#!/bin/sh
set -e

# The version is the first argument, referring `ls -la ~/.julia/environments/` (e.g., "v1.12")
# For example:
# ```bash
# . .devcontainer/init.sh "v1.12"
# ```
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