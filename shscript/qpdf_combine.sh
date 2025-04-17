docker run --rm \
  --volume "$(pwd):/data" \
  --workdir /data \
  --user "$(id -u):$(id -g)" \
  qpdf --empty --pages apply-preface.pdf apply.pdf -- output_qpdf.pdf
