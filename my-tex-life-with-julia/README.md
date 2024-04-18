# README
This builds a final workspace that supports LaTeX utilities provide by provided by [MyTeXLife](https://github.com/okatsn/MyTeXLife) `FROM` [okatsn/my-tex-life](https://hub.docker.com/repository/docker/okatsn/my-tex-life/general) and julia utilities provided by `../julia-debian-build`.

## Use with Dev Containers extension of VSCode

Use with Dev Containers extension of VSCode (`ms-vscode-remote.remote-containers`)
- `WSL: Open folder in WSL` and open `my-workspace/my-tex-life-with-julia`
- `Dev Containers: Rebuild and Reopen in Container`

## Trouble shooting

Use the following command if it fails to build in one machine but success in the other with exactly the same script.
- `docker builder prune`:  Clear Build Cache
- `docker volume prune`: Remove Unused Volumes

For more information, see the comments in Dockerfile.