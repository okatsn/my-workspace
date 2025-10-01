#!/usr/bin/env bash
set -euo pipefail

# Work in a temporary directory
mkdir latex-manuscript/
cp -r manuscript/. latex-manuscript/

cd latex-manuscript


. compile.sh output.tex

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