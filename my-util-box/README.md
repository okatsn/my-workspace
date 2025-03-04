# README

Basic usage pattern:

```bash
docker run -v "${PWD}":/workspace okatsn/my-util-box "<command>"
```

Usage examples:

```bash
docker run okatsn/my-util-box "jq --version"
docker run okatsn/my-util-box "go version"
docker run okatsn/my-util-box "stitchmd --help"
```

```bash
docker run -v "${PWD}":/workspace okatsn/my-util-box 'jq "." data.json'
```