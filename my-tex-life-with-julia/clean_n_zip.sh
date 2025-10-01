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

# Work in a temporary directory
DOCFILE="$1"
# Create the working directory; on failure print an error, wait 5s, then exit
if ! mkdir latex-manuscript/; then
	echo "Error: failed to create directory 'latex-manuscript/'" >&2
	# wait so the user can see the message (ShellGuide: wait 5 seconds on custom errors)
	sleep 5
	exit 1
fi
cp -r $DOCFILE/. latex-manuscript/

cd latex-manuscript


# Remove auxiliary files before zipping (to avoid journal system to compile wrongly):
find -type f -name '*.aux' -exec rm {} \;
find -type f -name '*.blg' -exec rm {} \;
find -type f -name 'main.*' -exec rm {} \;
find -type f -name '*.sh' -exec rm {} \;
find -type f -name '*.dvc' -exec rm {} \;
# Remove TOML files
find -type f -name '*.toml' -exec rm {} \;
# Remove all .tex files except `-name <file>`
find -type f -name '*.tex' ! -name 'output.tex' -exec rm {} \;
find -type f -name '*.pdf' ! -name 'output.pdf' -exec rm {} \;


rm .gitignore

zip -9 -r ../latex-manuscript.zip .
# the compression level from -0 (no compression) to -9 (highest compression).
# instead of `zip -r latex-manuscript`, `zip -r .` make files in the root.

cd ..
rm -rv latex-manuscript