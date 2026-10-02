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
