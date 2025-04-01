# README

## Dockerfile for building this workspace (for developer)

The Dockerfile script for building this workspace is [my-jupyter-with-julia/Dockerfile](Dockerfile).

Use [my-jupyter-with-julia/docker_build_and_push.sh](docker_build_and_push.sh) to build an image for this and push it to Dockerhub.

## Apply this workspace as arbitrary container (for user)

To build user's workspace, modify [my-jupyter-with-julia/data.json](data.json) and use [my-jupyter-with-julia/create_project.sh](create_project.sh) to export `.devcontainer` files based on [data.json](data.json). For example,

```bash
# After set up my-jupyter-with-julia/data.json

. my-jupyter-with-julia/create_project.sh TEMP
```

creates `my-jupyter-with-julia/TEMP`, that you can:

```bash
cp -r my-jupyter-with-julia/TEMP/. ../projects/MyProject/
```

Remeber to restore the current workspace.

```bash
rm -rv my-jupyter-with-julia/TEMP
```


```bash
git restore my-jupyter-with-julia/data.json
git restore my-jupyter-with-julia/.devcontainer/devcontainer.json
git restore my-jupyter-with-julia/.devcontainer/docker-compose.yml
```
