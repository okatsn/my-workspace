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
Usage: diff_ref.sh [--alsolatexdiff] <branch> <file_to_compare> <output_diff>

Compare a file in the workspace with the same file at a reference
branch/revision using `dvc get`. If the reference revision does not
have the file tracked yet (e.g. the very first `dvc repro`), a dummy
diff file with an obvious warning is written instead of failing.

Options:
  --alsolatexdiff Also run latexdiff and write output to a derived filename
                  (e.g., manuscript/manuscript_diff_<branch>.tex)

Arguments:
  branch          Git branch/revision to fetch the reference file from
  file_to_compare Path (relative to the repo root) to the file to compare
  output_diff     Path to write the resulting diff (or warning) to

Examples:
  ./diff_ref.sh main manuscript/manuscript.tex manuscript_0.diff
  ./diff_ref.sh --alsolatexdiff main manuscript/manuscript.tex manuscript_0.diff
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

# Handle --alsolatexdiff flag
use_latexdiff=false
if [[ "${1:-}" == "--alsolatexdiff" ]]; then
  use_latexdiff=true
  shift
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

  # If --alsolatexdiff was requested and latexdiff is available, run it
  if [ "$use_latexdiff" = true ] && command -v latexdiff >/dev/null 2>&1; then
    # Derive the latexdiff output filename: insert _diff_<branch> before the extension
    # Example: manuscript/manuscript.tex -> manuscript/manuscript_diff_main.tex
    dir=$(dirname "$file_to_compare")
    filename=$(basename "$file_to_compare")
    filename_without_ext="${filename%.*}"
    ext="${filename##*.}"
    output_diff_tex="$dir/${filename_without_ext}_diff_${branch}.${ext}"

    latexdiff "$reference_file" "$file_to_compare" > "$output_diff_tex" || true
  elif [ "$use_latexdiff" = true ]; then
    echo "WARNING: --alsolatexdiff requested but 'latexdiff' command not found on PATH." >&2
  fi

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
