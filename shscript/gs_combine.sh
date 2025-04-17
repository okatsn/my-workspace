#!/bin/bash
# filepath: /home/okatsn/my-workspace/shscript/qpdf_combine.sh

output_file="output.pdf"
pdf_files=()

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --out)
      output_file="$2"
      shift 2
      ;;
    *.pdf)
      pdf_files+=("$1")
      shift
      ;;
    *)
      echo "Error: Unknown argument or file format: $1"
      echo "Usage: $0 file1.pdf file2.pdf ... [--out output.pdf]"
      exit 1
      ;;
  esac
done

# Check if at least one PDF file was provided
if [ ${#pdf_files[@]} -eq 0 ]; then
  echo "Error: No PDF files provided"
  echo "Usage: $0 file1.pdf file2.pdf ... [--out output.pdf]"
  exit 1
fi

# Construct the pages argument for qpdf
pages_arg=""
for pdf in "${pdf_files[@]}"; do
  pages_arg+="$pdf "
done

# Run qpdf with docker
docker run --rm \
  --volume "$(pwd):/workspace" \
  --workdir /workspace \
  --user "$(id -u):$(id -g)" \
  okatsn/my-util-box "gs -sDEVICE=pdfwrite -dSAFER -dNOPAUSE -dBATCH -sOutputFile=$output_file $pages_arg"
  
#   okatsn/my-util-box "ls -la"

echo "Combined PDFs into: $output_file"