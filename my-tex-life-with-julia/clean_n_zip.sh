#!/usr/bin/env bash
set -euo pipefail

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