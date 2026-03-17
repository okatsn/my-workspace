# README

## Dockerfile for building this workspace (for developer)

The Dockerfile script for building this workspace is [my-jupyter-with-julia/Dockerfile](Dockerfile).

Use [my-jupyter-with-julia/docker_build_and_push.sh](docker_build_and_push.sh) to build an image for this and push it to Dockerhub.

## Apply this workspace as arbitrary container (for user)

To build user's workspace, modify [my-jupyter-with-julia/data.json](data.json) and use [my-jupyter-with-julia/create_project.sh](create_project.sh) to export `.devcontainer` files based on [data.json](data.json). For example,

```bash
# After set up my-jupyter-with-julia/data.json
cd my-jupyter-with-julia
. create_project.sh TEMP
```

creates `TEMP` in the current directory, that you can:

```bash
cp -r TEMP/. ../../MyProject/
```

Remeber to restore the current workspace.

```bash
rm -rv TEMP
```


```bash
git restore data.json
git restore .devcontainer/devcontainer.json
git restore .devcontainer/docker-compose.yml
cd ..
```

## Security Guidelines

### Pass GDrive token to docker

[Best practice: How to safely pass GDrive token to docker](https://gemini.google.com/app/51a92e0a510a700a)
KEYNOTE: the **Container** is not just storage, but a **Running process**
- (Risky) Using CLI to pass token as environment variable
- (acceptable but vulnerable to arbitrary code injection) Write token in a local env file and load it as environment variable
- (best practice) mount the secret file as volume
      Key points in the following Example:
- `rm` destroy the container immediately after the job is done
- `-v`: mount secret file in host machine to `/tmp/*.json`
```
  docker run --rm \
    -v ~/.secrets/dvc-gdrive.json:/tmp/gdrive-creds.json:ro \
    -v $(pwd)/data:/app/data \
    -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/gdrive-creds.json \
    my-dvc-image \
    dvc pull
```