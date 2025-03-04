# README

Basic usage pattern:

```bash
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box "<command>"
```

> **Note:** The `--rm` flag automatically removes the container when it exits. This is recommended for utility operations to prevent accumulation of stopped containers and save disk space. 
> 
> **Hint**: Use `docker container prune` to remove all stopped containers.

Usage examples:

```bash
docker run --rm okatsn/my-util-box "jq --version"
docker run --rm okatsn/my-util-box "go version"
docker run --rm okatsn/my-util-box "stitchmd --help"
```

```bash
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'jq "." data.json'
```

```bash
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'mustache data.json template.mustache > output.txt'
```

```bash
docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'stitchmd summary.md'
```