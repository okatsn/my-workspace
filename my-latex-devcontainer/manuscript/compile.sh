#!/bin/sh

# Check if a document file argument is provided
if [ -z "$1" ]; then
  echo "Usage: ./compile.sh <latex_document_name.tex>"
  exit 1
fi

DOCFILE="$1"

xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"
DOCFILE_BASE="${DOCFILE%.*}" # Remove extension to get base filename for bibtex
bibtex "$DOCFILE_BASE"
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"
xelatex -synctex=1 -interaction=nonstopmode -file-line-error "$DOCFILE"