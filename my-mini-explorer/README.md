# README

## Dockerfile for building this workspace (for developer)

The Dockerfile script for building this workspace is [my-mini-explorer/Dockerfile](Dockerfile).

Use [my-mini-explorer/docker_build_and_push.sh](docker_build_and_push.sh) to build an image and push it to Dockerhub.

> **Note:** The DVC installation modifies multiple files/folders across the system to work seamlessly with sftp, git, etc. It is impractical to cherry-pick individual modifications to `COPY`, so the whole image is used as a base.

## Apply this workspace as arbitrary container (for user)

To build a user workspace, modify [my-mini-explorer/data.json](data.json) and use [my-mini-explorer/create_project.sh](create_project.sh) to export `.devcontainer` files based on [data.json](data.json). For example,

```bash
# After setting up my-mini-explorer/data.json
cd my-mini-explorer
. create_project.sh TEMP
```

creates `TEMP` in the current directory, then you can:

```bash
cp -r TEMP/. ../../MyProject/
```

Remember to restore the current workspace afterwards.

```bash
rm -rv TEMP
git restore data.json
git restore .devcontainer/devcontainer.json
git restore .devcontainer/docker-compose.yml
cd ..
```

### `data.json` variables

| Variable              | Description                                             |
|-----------------------|---------------------------------------------------------|
| `devcontainer_name`   | Unique name shown in VS Code's remote container picker  |
| `service`             | Docker Compose service name (must match `devcontainer.json`) |
| `image`               | Docker image name for the built container               |
| `docker_compose_name` | Docker container name (must be unique on the host)      |
| `dind`                | `true` to enable Docker-in-Docker; `false` to use host socket |

### `.devcontainer/Dockerfile`

The generated `.devcontainer/Dockerfile` extends `okatsn/my-mini-explorer:latest`. Add any project-specific tools there:

```dockerfile
FROM okatsn/my-mini-explorer:latest

# Example: install additional apt packages
RUN apt-get update && apt-get install -y \
    your-package \
    && rm -rf /var/lib/apt/lists/*
```

### Starship prompt

Copy `starship.toml` inside the container to activate the Pastel Powerline prompt:

```bash
cp /root/workspace/.devcontainer/starship.toml ~/.config/starship.toml
```

## How to build the image solely from the Dockerfile:

```bash
cd ./my-mini-explorer

docker compose --env-file ../my-build.env build --no-cache

# tag the image
docker tag dvcbuild okatsn/my-mini-explorer:latest

# push it to dockerhub
docker push okatsn/my-mini-explorer:latest
```

Or use the helper script:

```bash
./docker_build_and_push.sh v2026a
```

