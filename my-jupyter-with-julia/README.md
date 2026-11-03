- [README](#readme)
  - [Dockerfile for building this workspace (for developer)](#dockerfile-for-building-this-workspace-for-developer)
    - [Convention](#convention)
    - [Version bump (Julia / Quarto / Typst)](#version-bump-julia--quarto--typst)
  - [Apply this workspace as arbitrary container (for user)](#apply-this-workspace-as-arbitrary-container-for-user)
  - [Security Guidelines](#security-guidelines)
    - [Pass GDrive token to docker](#pass-gdrive-token-to-docker)
  - [Trouble Shooting log](#trouble-shooting-log)


# README

## Dockerfile for building this workspace (for developer)

The Dockerfile script for building this workspace is [my-jupyter-with-julia/Dockerfile](Dockerfile).

Use [my-jupyter-with-julia/docker_build_and_push.sh](docker_build_and_push.sh) (run as `./docker_build_and_push.sh`, not sourced) to build an image for this and push it to Dockerhub.

### Convention

Every image is pushed with an immutable tag `v[yyyy][a-z].[n]` and a channel tag `v[yyyy][a-z]` that always refers the largest `n`.
The versions, releases and revisions (`n`) are all in [release.env](../release.env); the tags are derived from it by [shscripts/release_vars.sh](../shscripts/release_vars.sh).
Never use a channel tag as the input of another image: this Dockerfile takes the three build images as immutable tags (`JULIA_BUILD_REF`, `QUARTO_BUILD_REF` and `TYPST_BUILD_REF`).

### Version bump (Julia / Quarto / Typst)

1. Edit [release.env](../release.env): the version and `*_RELEASE` of what changed, with `*_REV=0` (or only bump `*_REV` to rebuild the same release). Bump `JUPYTER_RELEASE` (and `JUPYTER_REV=0`) as well.
2. Build and push in this order; each step fails loudly, pushing nothing, if a check fails (invalid `release.env`, existing immutable tag, missing build image, failed smoke test):
    ```bash
    (cd ../julia-debian-build && ./docker_build_and_push.sh)
    (cd ../quarto-debian-build && ./docker_build_and_push.sh)
    (cd ../typst-mirror && ./docker_build_and_push.sh)  # mirrors ghcr.io/typst/typst:[TYPST_VERSION]; nothing is built
    ./docker_build_and_push.sh
    ```
    Only run the steps for what changed.
3. Set the `FROM` line of [.devcontainer/Dockerfile](.devcontainer/Dockerfile) (the distributed Dockerfile) to the printed tag, run `../shscripts/check_release.sh`, and commit.

## Apply this workspace as arbitrary container (for user)

Use [my-jupyter-with-julia/create_project.sh](create_project.sh) to populate the templates with a `data.json` and export `.devcontainer`, `.vscode`, `data.json` and `helper/` to a project. It is path stable (run it from anywhere, executed rather than sourced) and renders in a temporary directory, so this template directory is never modified.

```bash
create_project.sh --target DIR [--source data.json] [--force]
```

- `--target`: the project directory. It must not exist unless `--force` is given.
- `--source`: the `data.json` to populate the templates with; default to [data.json](data.json) next to the script.
- `--force`: allow an existing target and overwrite its files (`cp -rf`; `helper/` is mirrored with `rsync --delete`, `test_*` excluded).

### Create a new project

```bash
~/projects/my-workspace/my-jupyter-with-julia/create_project.sh --target ~/projects/NewProject
```

Then edit `NewProject/data.json` as needed.

### Update an existing project to the latest template

In the project (e.g., `~/projects/Project1`, whose `data.json` is the one to populate with), run

```bash
cd ~/projects/Project1
bash helper/update-devcontainer.sh
```

[helper/update-devcontainer.sh](helper/update-devcontainer.sh) is synced to the project's `helper/`; it calls `create_project.sh --source ./data.json --target . --force` of the template in `$MY_WORKSPACE/my-jupyter-with-julia` (default to the template in `~/projects/my-workspace`, or the one containing the script itself when run inside my-workspace). An optional argument sets the project directory: `bash helper/update-devcontainer.sh ~/projects/Project1`.

Beware that `--force` overwrites `.devcontainer/`, `.vscode/` and `helper/` in the project (files only in the project's `helper/` are deleted); review with `git diff` in the project afterwards.

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


[The Read-Only Service Account](https://gemini.google.com/app/f38854df52155b00)
If you want the AI agent to be able to autonomously dvc pull data to run experiments, but absolutely block it from pushing or deleting data:
- Create a Google Cloud Service Account and grant it Viewer (Read-Only) access to the specific Google Drive folder where your DVC remote lives.
- Download that Service Account's JSON key file and mount only that specific file into the container.
- Configure the container's DVC to use the Service Account for authentication (dvc remote modify myremote gdrive_use_service_account true).
- The Result: The container (and the agent) can pull data freely without bothering you. If the agent attempts a dvc push or dvc gc -c, Google Drive's API will reject the request.


## Trouble Shooting log

There is an issue where docker buildx v0.38.1 blocks `/tmp/devcontainercli-okatsn/.../Dockerfile-with-features` generated by Dev Containers; [see this for the full report](https://gemini.google.com/app/cdb0edd93922091d).
Adding `"updateRemoteUserUID": false,` to prevent Dev Containers from generating a /tmp wrapper Dockerfile to rewrite jovyan's UID DOESN'T WORK.

Currently the solution is to downgrade docker buildx to v0.37.1 and wait for Dev Containers' update.

```bash
# To get TARGET_VER manually:
apt-cache madison docker-buildx-plugin
```

The one-shot downgrade script:

```bash
## The one-shot

# Example if using Ubuntu 26.04:
# TARGET_VER="0.37.1-1~ubuntu.26.04~resolute"
TARGET_VER=$(apt-cache madison docker-buildx-plugin | grep '0.37.1' | head -n1 | awk '{print $3}')

sudo apt install --allow-downgrades -y docker-buildx-plugin="$TARGET_VER"
```