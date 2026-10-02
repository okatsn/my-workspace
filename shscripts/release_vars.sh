#!/usr/bin/env bash
# Source this file to load `release.env` (at the workspace root), validate it and export the derived values.
set -Eeuo pipefail

die() { echo "ERROR: release.env: $*" >&2; exit 2; }

# check_format NAME VALUE REGEX
check_format() { [[ "$2" =~ $3 ]] || die "$1='$2' does not match $3"; }

set -a
source "$(dirname "${BASH_SOURCE[0]}")/../release.env"
set +a

check_format JULIA_VERSION "${JULIA_VERSION:-}" '^[0-9]+\.[0-9]+\.[0-9]+$'
check_format JULIA_RELEASE "${JULIA_RELEASE:-}" '^[0-9]{4}[a-z]$'
check_format JULIA_REV "${JULIA_REV:-}" '^[0-9]+$'

JULIA_MINOR="${JULIA_VERSION%.*}"
export JULIA_PROJECT="v${JULIA_MINOR}"
export JULIA_BUILD_CHANNEL="v${JULIA_MINOR}-${JULIA_RELEASE}"
export JULIA_BUILD_TAG="${JULIA_BUILD_CHANNEL}.${JULIA_REV}"

check_format QUARTO_VERSION "${QUARTO_VERSION:-}" '^[0-9]+\.[0-9]+\.[0-9]+$'
check_format QUARTO_RELEASE "${QUARTO_RELEASE:-}" '^[0-9]{4}[a-z]$'
check_format QUARTO_REV "${QUARTO_REV:-}" '^[0-9]+$'

QUARTO_MINOR="${QUARTO_VERSION%.*}"
export QUARTO_BUILD_CHANNEL="v${QUARTO_MINOR}-${QUARTO_RELEASE}"
export QUARTO_BUILD_TAG="${QUARTO_BUILD_CHANNEL}.${QUARTO_REV}"

check_format TYPST_RELEASE "${TYPST_RELEASE:-}" '^[0-9]{4}[a-z]$'
check_format TYPST_REV "${TYPST_REV:-}" '^[0-9]+$'
check_format JUPYTER_RELEASE "${JUPYTER_RELEASE:-}" '^[0-9]{4}[a-z]$'
check_format JUPYTER_REV "${JUPYTER_REV:-}" '^[0-9]+$'

export TYPST_BUILD_CHANNEL="v${TYPST_RELEASE}"
export TYPST_BUILD_TAG="${TYPST_BUILD_CHANNEL}.${TYPST_REV}"
export JUPYTER_CHANNEL="v${JUPYTER_RELEASE}"
export JUPYTER_TAG="${JUPYTER_CHANNEL}.${JUPYTER_REV}"

# Image names, and the refs of the build images consumed by my-jupyter-with-julia/Dockerfile (always immutable tags).
export JULIA_BUILD_IMAGE="okatsn/my-julia-build"
export QUARTO_BUILD_IMAGE="okatsn/my-quarto-build"
export TYPST_BUILD_IMAGE="okatsn/my-typst-space"
export JUPYTER_IMAGE="okatsn/my-jupyter-with-julia"
export JULIA_BUILD_REF="${JULIA_BUILD_IMAGE}:${JULIA_BUILD_TAG}"
export QUARTO_BUILD_REF="${QUARTO_BUILD_IMAGE}:${QUARTO_BUILD_TAG}"
export TYPST_BUILD_REF="${TYPST_BUILD_IMAGE}:${TYPST_BUILD_TAG}"
