#!/bin/sh
# # How to use:
# - `. stripcomments.sh README.md`
# - `. stripcomments.sh README.md README-no-comments.md`
# - `. stripcomments.sh paper.tex`
# - `. stripcomments.sh paper.tex paper-no-comments.tex`

# Check if at least one argument (the filename) is provided.
if [ $# -eq 0 ]; then
  echo "Usage: $0 <filename.md|filename.tex> [output_filename]"
  exit 1
fi

# Get the input filename.
input_file="$1"

# Get the output filename, or use the input filename if no output is specified.
output_file="${2:-$input_file}" # Use $input_file if $2 is empty.  Crucially, this handles the case where no second arg is given.

# Detect file type based on extension
file_extension="${input_file##*.}"

# Set pandoc options based on file type
if [ "$file_extension" = "md" ]; then
  # Markdown file options
  format_from="markdown"
  format_to="markdown-raw_attribute"
elif [ "$file_extension" = "tex" ]; then
  # TeX file options
  format_from="latex"
  format_to="latex"
else
  echo "Error: Unsupported file extension '$file_extension'. Only .md and .tex files are supported."
  exit 1
fi

# Build the docker command.  We use pandoc/core.
# # KEYNOTE: the working directory (where pandoc/core start) is `/data`.
docker run --rm \
  --volume "$(pwd):/data" \
  --workdir /data \
  --user "$(id -u):$(id -g)" \
  pandoc/core "$input_file" -o "$output_file" \
  --strip-comments \
  --wrap=none \
  -f "$format_from" \
  -t "$format_to"

echo "Comments stripped from $input_file and saved to $output_file"
