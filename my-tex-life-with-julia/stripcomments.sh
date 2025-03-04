#!/bin/sh
# # How to use:
# - `. stripcomments.sh README.md`
# - `. stripcomments.sh README.md README-no-comments.md`

# Check if at least one argument (the filename) is provided.
if [ $# -eq 0 ]; then
  echo "Usage: $0 <filename.md> [output_filename.md]"
  exit 1
fi

# Get the input filename.
input_file="$1"

# # Check if the input file exists.
# if [ ! -f "$input_file" ]; then
#   echo "Error: Input file '$input_file' not found."
#   exit 1
# fi

# Get the output filename, or use the input filename if no output is specified.
output_file="${2:-$input_file}" # Use $input_file if $2 is empty.  Crucially, this handles the case where no second arg is given.

# Build the docker command.  We use pandoc/core.
docker run --rm \
  --volume "$(pwd):/data" \
  --workdir /data \
  --user "$(id -u):$(id -g)" \
  pandoc/core "$input_file" -o "$output_file" \
  --strip-comments \
  --wrap=none \
  -f markdown \
  -t markdown-raw_attribute
