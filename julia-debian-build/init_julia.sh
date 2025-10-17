#!/bin/sh
set -e

# The version is the first argument
VERSION="$1"

JULIA_ENV_DIR=~/.julia/environments/
JULIA_CONFIG_DIR=~/.julia/config/

mkdir -p "$JULIA_ENV_DIR"
mkdir -p "$JULIA_CONFIG_DIR"

cp /tmp/julia/Project.toml "${JULIA_ENV_DIR}"
cp /tmp/julia/startup.jl "${JULIA_CONFIG_DIR}"
