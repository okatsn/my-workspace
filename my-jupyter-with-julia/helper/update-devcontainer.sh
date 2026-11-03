#!/usr/bin/env bash
# Update/sync a project's devcontainer files (and this helper/ directory) with the latest template in my-workspace.
# Populates the templates with the project's own `data.json` and overwrites the files in the project.
#
# Usage: update-devcontainer.sh [PROJECT_DIR]    (default: the current directory)
#
# The template is found at, in order: `$MY_WORKSPACE/my-jupyter-with-julia`, the parent of this script's
# directory (when run inside my-workspace), or `~/projects/my-workspace/my-jupyter-with-julia`.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project="${1:-.}"

if [ -n "${MY_WORKSPACE:-}" ]; then
  template_dir="$MY_WORKSPACE/my-jupyter-with-julia"
elif [ -f "$script_dir/../create_project.sh" ]; then
  template_dir="$script_dir/.."
else
  template_dir="$HOME/projects/my-workspace/my-jupyter-with-julia"
fi

[ -f "$template_dir/create_project.sh" ] || { echo "Error: template not found at '$template_dir'. Set MY_WORKSPACE." >&2; exit 1; }
[ -f "$project/data.json" ] || { echo "Error: '$project/data.json' not found." >&2; exit 1; }

bash "$template_dir/create_project.sh" --source "$project/data.json" --target "$project" --force
