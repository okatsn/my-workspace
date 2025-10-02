#!/usr/bin/env bash
# This is `expand_output.sh` (FIXED version)
set -e

# Pause before exit when the script fails so the caller can see the error.
# - Uses an EXIT trap to catch any non-zero exit (including explicit `exit 1`).
# - If running interactively it prompts the user to press Enter. In CI or
#   non-interactive environments it sleeps for 5 seconds instead.
trap 'rc=$?; if [ "$rc" -ne 0 ]; then
  echo "\nERROR: script exited with code $rc at $(date)" >&2
  # If running in CI or not attached to a terminal, avoid waiting for input.
  if [ -n "$CI" ] || [ ! -t 1 ]; then
    echo "Non-interactive or CI environment detected; sleeping 5s before exit..." >&2
    sleep 5
  else
    read -rp "Press Enter to exit..."
  fi
fi' EXIT

# Check for exactly one argument
if [ "$#" -ne 1 ]; then
	echo "Error: This script requires exactly one argument (document folder path)" >&2
	echo "Usage: $0 <document-folder>" >&2
	exit 1
fi
# Work in a temporary directory
DOCFILE="$1"

# KEYNOTE: use `cd` is crucial; `latexpand "$DOCFILE/main.tex"` cannot find input files in a parent directories like ../chapters/*.tex
cd $DOCFILE/

echo "Expanding main.tex into manuscript.tex..."
latexpand -o manuscript.tex main.tex

latexindent --output=manuscript.tex manuscript.tex

echo "Creating reference files for local use..."

cp manuscript.tex ../ref-manuscript.tex

latexpand --keep-comments -o ../ref-manuscript-wc.tex main.tex

cd ..

latexindent --output=ref-manuscript-wc.tex ref-manuscript-wc.tex

echo "Expansion complete. 'output.tex' is now ready for compilation and submission."