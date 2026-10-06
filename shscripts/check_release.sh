#!/usr/bin/env bash
# Usage: ./shscripts/check_release.sh
# Fails loudly unless the distributed Dockerfile (my-jupyter-with-julia/.devcontainer/Dockerfile) is based on
# the immutable image of release.env, and that image exists in the registry.
set -Eeuo pipefail
here="$(dirname "${BASH_SOURCE[0]}")"
source "$here/release_vars.sh"

dockerfile="$here/../my-jupyter-with-julia/.devcontainer/Dockerfile"
expected="FROM $JUPYTER_IMAGE:$JUPYTER_TAG"
actual="$(grep '^FROM ' "$dockerfile")"

if [ "$actual" != "$expected" ]; then
  echo "ERROR: $dockerfile" >&2
  echo "  expected exactly one line: $expected" >&2
  echo "  found:                     ${actual:-<no FROM line>}" >&2
  exit 1
fi

docker buildx imagetools inspect "$JUPYTER_IMAGE:$JUPYTER_TAG" >/dev/null ||
  { echo "ERROR: $JUPYTER_IMAGE:$JUPYTER_TAG is not in the registry" >&2; exit 1; }

echo "OK: $expected"
