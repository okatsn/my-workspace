#!/usr/bin/env bash
# Populate the templates in this directory with a `data.json` and copy the result to a target project.
# Path stable: run it from anywhere, as an executable (`bash create_project.sh ...`), not sourced.
#
# Usage: create_project.sh --target DIR [--source data.json] [--force]
#   --target  destination project directory (required); it must not exist unless `--force` is given.
#   --source  `data.json` to populate the templates with (default: `data.json` next to this script).
#   --force   allow an existing target and overwrite the files in it (`cp -rf`).
#
# Examples:
#   Create a new project:  create_project.sh --target ~/projects/NewProject
#   Update a project:      cd ~/projects/Project1 && create_project.sh --source ./data.json --target . --force
set -euo pipefail

template_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_json="$template_dir/data.json"
target=""
force=false

while [ $# -gt 0 ]; do
  case "$1" in
    --source) source_json="${2:?--source needs a path}"; shift 2 ;;
    --target) target="${2:?--target needs a path}"; shift 2 ;;
    --force) force=true; shift ;;
    *) echo "Error: unknown argument '$1'." >&2; exit 1 ;;
  esac
done

[ -n "$target" ] || { echo "Error: --target is required." >&2; exit 1; }
[ -f "$source_json" ] || { echo "Error: --source '$source_json' is not a file." >&2; exit 1; }

# Without --force, an existing target is an error to prevent unintended overwrites.
if [ -e "$target" ] && [ "$force" = false ]; then
  echo "Error: '$target' already exists. Use --force to overwrite." >&2
  exit 1
fi

# Guard: ensure node is available
if ! command -v node > /dev/null 2>&1; then
  echo "Error: 'node' is not installed. Please install Node.js before running this script." >&2
  exit 1
fi

# Guard: ensure mustache package is installed (install automatically if missing)
if [ ! -d "$template_dir/node_modules" ]; then
  echo "node_modules not found. Running npm install..." >&2
  (cd "$template_dir" && npm install)
fi

# Render into a temporary directory so the template directory is never modified.
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
cp -r "$template_dir/.devcontainer" "$stage/.devcontainer"
node "$template_dir/render.js" --data "$source_json" --out "$stage"

# `cp -rf DIR "$target/"` merges into an existing "$target/DIR" instead of nesting.
mkdir -p "$target"
cp -rf "$stage/.devcontainer" "$target/"
# `--source` may already be the target's own data.json.
[ "$source_json" -ef "$target/data.json" ] || cp -f "$source_json" "$target/data.json"

echo "Project '$target' is populated from '$source_json'."
