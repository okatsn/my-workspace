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
Usage: expand_output.sh [options] <document-folder>

Options:
  -h, --help              Show this help message
  -f, --file <filename>   Specify the main file name (default: main.tex)

Examples:
  # Expand default main.tex in a document folder
  ./expand_output.sh ./my-document/

  # Expand a custom file name
  ./expand_output.sh -f thesis.tex ./my-document/

  # Show this help message
  ./expand_output.sh --help
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

# Parse arguments
file_name="main.tex"
doc_folder=""

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--file)
      if [ $# -lt 2 ]; then
        echo "Error: --file requires an argument" >&2
        exit 1
      fi
      file_name="$2"
      shift 2
      ;;
    -*)
      echo "Error: Unknown option $1" >&2
      echo "Use -h or --help for usage information" >&2
      exit 1
      ;;
    *)
      if [ -z "$doc_folder" ]; then
        doc_folder="$1"
      else
        echo "Error: Too many positional arguments" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

# Check if document folder was provided
if [ -z "$doc_folder" ]; then
  echo "Error: Document folder path is required" >&2
  echo "Use -h or --help for usage information" >&2
  exit 1
fi

# KEYNOTE: use `cd` is crucial; `latexpand` cannot find input files in parent directories like ../chapters/*.tex
cd "$doc_folder"

echo "Expanding $file_name into manuscript.tex..."
latexpand -o manuscript.tex "$file_name"

latexindent --output=manuscript.tex manuscript.tex

echo "Creating reference files for local use..."

# # KEYNOTE: No need to generate ref-manuscript because we have `diff_ref` and `compile_diff_pdf` stages. Remove this later.
# cp manuscript.tex ../ref-manuscript.tex
# latexpand --keep-comments -o ../ref-manuscript-wc.tex "$file_name"
# latexindent --output=ref-manuscript-wc.tex ref-manuscript-wc.tex

echo "Expansion complete. 'manuscript.tex' is now ready for compilation and submission."
cd ..