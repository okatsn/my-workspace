[TOC]

# README
## How to build the image solely from the Dockerfile:

The Quarto version is set in [release.env](../release.env) (see [Version bump](../my-jupyter-with-julia/README.md#version-bump-julia--quarto--typst)); do not edit the Dockerfile for it.

```bash
# These commands should be executed in WSL in the quarto-debian-build directory
cd quarto-debian-build

# build, smoke test and push `v<major>.<minor>-<RELEASE>.<REV>`, `v<major>.<minor>-<RELEASE>` and `latest` derived from release.env
./docker_build_and_push.sh
```

## How to use:
```Dockerfile
FROM okatsn/my-quarto-build:latest AS build-quarto
# COPY the main application
COPY --from=build-quarto --chown=$NB_UID:$NB_GID /opt/quarto /opt/quarto
# Making the application located at `/opt/quarto/bin/quarto` accessible from anywhere on your system by simply using the command `quarto`.
RUN ln -fs /opt/quarto/bin/quarto /usr/local/bin/quarto
```
You can use the following commands to find out dependencies for quarto
- `which quarto`
- `type quarto`
- `dpkg-query -W -f='${Depends}\n' quarto`
- `apt-cache rdepends quarto`
- `apt-cache depends quarto`
Search the log by keyword or time:
- `cat /var/log/dpkg.log | grep '2024-04-22'`
- `cat /var/log/dpkg.log | grep 'quarto'`

## For the first time use of a `my-quarto-build` dependent container

In VSCode:
- Install extension `quarto.quarto`
- If you want to use either julia or python in your qmd file, installation of Jupyter is required.