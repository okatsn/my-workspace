#!/usr/bin/env bash
# This is `expand_output.sh` - Expand LaTeX document and create reference files
set -euo pipefail

# Pause before exit when the script fails OR when explicitly requested (like --help).
# - Uses an EXIT trap to catch any exit.
# - If running interactively it prompts the user to press Enter. In CI or
#   non-interactive environments it sleeps for 5 seconds instead.
trap 'rc=$?; if [ "$rc" -ne 0 ] || [ "$PAUSE_ON_EXIT" = "true" ]; then
  if [ "$rc" -ne 0 ]; then
    echo "" >&2
    echo "ERROR: script exited with code $rc at $(date)" >&2
  fi
  if [ -n "$CI" ] || [ ! -t 1 ]; then
    echo "Non-interactive or CI environment detected; sleeping 5s before exit..." >&2
    sleep 5
  else
    read -rp "Press Enter to exit..."
  fi
fi' EXIT

show_help() {
  cat << 'EOF'
expand_output.sh - Expand LaTeX document and create reference files

Usage:
  expand_output.sh [OPTIONS] <document-folder>

Options:
  -f, --file FILE    Specify the main LaTeX file (default: main.tex)
  -h, --help         Show this help message

Examples:
  # Expand main.tex in the docs folder
  expand_output.sh docs/

  # Expand custom.tex in the docs folder
  expand_output.sh -f custom.tex docs/

  # Expand another.tex using long form
  expand_output.sh --file another.tex docs/
EOF
}

# Initialize variables
file_name="main.tex"
doc_folder=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h | --help)
      show_help
      PAUSE_ON_EXIT=true
      exit 0
      ;;
    -f | --file)
      if [[ $# -lt 2 ]]; then
        echo "Error: --file requires an argument" >&2
        exit 1
      fi
      file_name="$2"
      shift 2
      ;;
    -*)
      echo "Error: Unknown option: $1" >&2
      exit 1
      ;;
    *)
      doc_folder="$1"
      shift
      ;;
  esac
done

# Validate that document folder was provided
if [[ -z "$doc_folder" ]]; then
  echo "Error: Document folder path is required" >&2
  show_help
  exit 1
fi

DOCFILE="$doc_folder"

# KEYNOTE: use `cd` is crucial; `latexpand "$DOCFILE/$file_name"` cannot find input files in a parent directories like ../chapters/*.tex
cd "$DOCFILE"

echo "Expanding ${file_name} into manuscript.tex..."
latexpand -o manuscript.tex "$file_name"

latexindent --output=manuscript.tex manuscript.tex

echo "Creating reference files for local use..."

cp manuscript.tex ../ref-manuscript.tex

latexpand --keep-comments -o ../ref-manuscript-wc.tex "$file_name"

cd ..

latexindent --output=ref-manuscript-wc.tex ref-manuscript-wc.tex

echo "Expansion complete. 'manuscript.tex' is now ready for compilation and submission."