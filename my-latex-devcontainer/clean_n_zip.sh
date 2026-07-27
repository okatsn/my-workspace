#!/usr/bin/env bash
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

# Check for exactly two arguments
if [ "$#" -ne 2 ]; then
	echo "Error: This script requires exactly two arguments" >&2
	echo "Usage: $0 <document-folder> <temp-directory-name>" >&2
	exit 1
fi

# Work in a temporary directory
DOCFILE="$1"
TEMP_DIR="$2"
# Create the working directory; on failure print an error, wait 5s, then exit
if ! mkdir "$TEMP_DIR"/; then
	echo "Error: failed to create directory '$TEMP_DIR/'" >&2
	# wait so the user can see the message (ShellGuide: wait 5 seconds on custom errors)
	sleep 5
	exit 1
fi
cp -r "$DOCFILE"/. "$TEMP_DIR"/

cd "$TEMP_DIR"

# Remove auxiliary files before zipping (to avoid journal system to compile wrongly):
find -type f -name '*.aux' -exec rm {} \;
find -type f -name '*.blg' -exec rm {} \;
find -type f -name 'main.*' -exec rm {} \;
find -type f -name '*.sh' -exec rm {} \;
find -type f -name '*.dvc' -exec rm {} \;
find -type f -name '*.spl' -exec rm {} \;
find -type f -name '*.synctex.gz' -exec rm {} \;
find -type f -name '*:Zone.Identifier' -exec rm {} \;
# Remove TOML files
find -type f -name '*.toml' -exec rm {} \;
# Remove all .tex files except `-name <file>`
find -type f -name '*.tex' ! -name 'manuscript.tex' -exec rm {} \;
find -type f -name '*.pdf' ! -name 'manuscript.pdf' -exec rm {} \;


rm .gitignore

zip -9 -r "../${TEMP_DIR}.zip" .
# the compression level from -0 (no compression) to -9 (highest compression).
# instead of `zip -r latex-manuscript`, `zip -r .` make files in the root.

cd ..
rm -rv "$TEMP_DIR"