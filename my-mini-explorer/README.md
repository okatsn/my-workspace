# My Mini Explorer

!!!note 
    After dive into the image, it turns out the DVC installation involves modifications of multiple files/folders across the system, seeming to make dvc works seamlessly with such as sftp, git and so on. 
    Thus, it is impractical to identify all the modifications to be `COPY`ed.

This is a minimal machine for file editing and exploration with DVC utilities.



## How to build the image solely from the Dockerfile:

```bash
cd ./my-mini-explorer

docker-compose --env-file ../my-build.env build --no-cache

# tag the image 
docker tag dvcbuild okatsn/my-mini-explorer:latest

# push it to dockerhub
docker push okatsn/my-mini-explorer:latest
```

## How to use this image

### `Dockerfile`

```dockerfile
FROM temp-local:latest AS build-dvc

ENV NB_UID=1000\
    NB_GID=100 \
    NB_USER=okatsn

RUN useradd -m -u $NB_UID -g $NB_GID -s /bin/bash $NB_USER

USER $NB_USER
```

### `.devcontainer/devcontainer.json`

This script can be automatically generated if you `Ctrl+Shift+P` use "Reopen in Container" with VSCODE's interface.

```json
{
	"name": "Existing Dockerfile",
	"build": {
		"context": "..",
		"dockerfile": "../Dockerfile"
	}
}

```