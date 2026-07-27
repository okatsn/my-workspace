#!/usr/bin/env bash
set -euo pipefail

# Best Practice: Robust Cleanup & Exit Handler
cleanup() {
  local rc=$?

  if [ "$rc" -ne 0 ] || [ "${PAUSE_ON_EXIT:-false}" = "true" ]; then
    if [ "$rc" -ne 0 ]; then
      echo "" >&2
      echo "ERROR: Script exited with code $rc at $(date)" >&2
    fi

    if [ -n "${CI:-}" ] || [ ! -t 0 ] || [ ! -t 1 ]; then
      if [ "$rc" -ne 0 ]; then
        echo "Non-interactive environment; sleeping 5s before exit..." >&2
        sleep 5
      fi
    else
      read -rp "Press Enter to exit..." </dev/tty
    fi
  fi
}

trap cleanup EXIT

show_usage() {
  cat << 'EOF'
Usage: diff_ref.sh <branch> <file_to_compare> <output_diff>

Compare a file in the workspace with the same file at a reference
branch/revision using `dvc get`. If the reference revision does not
have the file tracked yet (e.g. the very first `dvc repro`), a dummy
diff file with an obvious warning is written instead of failing.

Arguments:
  branch          Git branch/revision to fetch the reference file from
  file_to_compare Path (relative to the repo root) to the file to compare
  output_diff     Path to write the resulting diff (or warning) to

Example:
  ./diff_ref.sh main manuscript/manuscript.tex manuscript_0.diff
EOF
}

# Help flag handler
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  if [ -t 1 ] && command -v less >/dev/null 2>&1; then
    show_usage | less -F -X -R
  else
    show_usage
  fi
  exit 0
fi

if [ "$#" -ne 3 ]; then
  show_usage >&2
  exit 1
fi

branch="$1"
file_to_compare="$2"
output_diff="$3"

temp_dir="temp"
reference_file="$temp_dir/$(basename "$file_to_compare" .tex)_0.tex"

mkdir -p "$temp_dir"

if dvc get . "$file_to_compare" --rev "$branch" -o "$reference_file"; then
  # `git diff --no-index` exits with code 1 when differences are found,
  # so it must not trigger the strict-mode error handler.
  git diff --no-index "$reference_file" "$file_to_compare" > "$output_diff" || true
  rm -f "$reference_file"
else
  echo "" >&2
  echo "WARNING: 'dvc get . $file_to_compare --rev $branch' failed." >&2
  echo "WARNING: '$file_to_compare' is likely not tracked yet at revision '$branch' (e.g. first 'dvc repro')." >&2
  {
    echo "WARNING: Could not fetch '$file_to_compare' at revision '$branch'."
    echo "WARNING: This is expected if '$branch' does not have '$file_to_compare' tracked yet (e.g. the first 'dvc repro')."
    echo "WARNING: No diff was generated."
  } > "$output_diff"
fi
