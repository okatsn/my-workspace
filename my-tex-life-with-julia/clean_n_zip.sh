#!/usr/bin/env bash
set -euo pipefail

# Work in a temporary directory
# Create the working directory; on failure print an error, wait 5s, then exit
if ! mkdir latex-manuscript/; then
	echo "Error: failed to create directory 'latex-manuscript/'" >&2
	# wait so the user can see the message (ShellGuide: wait 5 seconds on custom errors)
	sleep 5
	exit 1
fi
cp -r manuscript/. latex-manuscript/

cd latex-manuscript


# Remove auxiliary files before zipping (to avoid journal system to compile wrongly):
find -type f -name '*.aux' -exec rm {} \;
find -type f -name '*.blg' -exec rm {} \;
find -type f -name 'main.*' -exec rm {} \;
find -type f -name '*.sh' -exec rm {} \;
find -type f -name '*.dvc' -exec rm {} \;
# Remove all .tex files except manuscript.tex
find -type f -name '*.tex' ! -name 'manuscript.tex' -exec rm {} \;


rm .gitignore

cd ..
zip -9 -r latex-manuscript.zip latex-manuscript
# the compression level from -0 (no compression) to -9 (highest compression).

rm -rv latex-manuscript