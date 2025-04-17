# README

Basic usage pattern:

```bash
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box "<command>"
```

> **Note:** The `--rm` flag automatically removes the container when it exits. This is recommended for utility operations to prevent accumulation of stopped containers and save disk space. 
> 
> **Hint**: Use `docker container prune` to remove all stopped containers.

## Usage without writing permissions

```bash
docker run --rm okatsn/my-util-box "jq --version"
docker run --rm okatsn/my-util-box "go version"
docker run --rm okatsn/my-util-box "stitchmd --help"
```

```bash
cd my-jupyter-with-julia
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'jq "." data.json'
cd ..
```

```bash
cd mustache-project
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'mustache data.json template.mustache' > output.txt
cd ..
```

```bash
cd my-util-box
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'stitchmd test.md'
cd ..
```

## Usage with writing permissions

```bash
cd my-util-box
docker run --rm -v ${PWD}:/workspace --user "$(id -u):$(id -g)" okatsn/my-util-box 'stitchmd -no-toc -o output.md test.md'
cd ..
```

## PDF combine

### using QPdf

```bash
cd my-util-box
docker run --rm -v ${PWD}:/workspace --user "$(id -u):$(id -g)" okatsn/my-util-box 'qpdf --empty --pages doc_1.pdf doc_2.pdf -- doc_12.pdf'
cd ..
```


### Convert to WORD (Not working)

https://github.com/unoconv/unoserver-docker

```bash
docker run --rm -it -v ${PWD}:/home/worker/ ghcr.io/unoconv/unoserver-docker unoconvert apply-combined.pdf apply-combined.doc
```