# README
This builds a final workspace that supports LaTeX utilities provide by provided by [MyTeXLife](https://github.com/okatsn/MyTeXLife) `FROM` [okatsn/my-tex-life](https://hub.docker.com/repository/docker/okatsn/my-tex-life/general) and julia utilities provided by `../julia-debian-build`.

The content of this folder is migrated from [okatsn/MyTeXLifeWithJulia](https://github.com/okatsn/MyTeXLifeWithJulia); please refer to this archive for older history.

## Use with Dev Containers extension of VSCode

Use with Dev Containers extension of VSCode (`ms-vscode-remote.remote-containers`)
- `WSL: Open folder in WSL` and open `my-workspace/my-tex-life-with-julia`
- `Dev Containers: Rebuild and Reopen in Container`


For more information, see the comments in Dockerfile.

## Create the same environment but in different name


Option 1:
- Modify the contents in `data.json`.
- `cd my-tex-life-with-julia` to navigate to the directory.
- `. create_project.sh HelloWorld` in bash.
- Copy all the contents in the HelloWorld folder to the directory of your project.

Option 2:
- Modify the contents in `data.json`.
- `node render.js`.
- Copy `.devcontainer` folder to the directory of your project.


## Apply this workspace as arbitrary container (for user)

To build user's workspace, modify [my-tex-life-with-julia/data.json](data.json) and use [my-tex-life-with-julia/create_project.sh](create_project.sh) to export `.devcontainer` files based on [data.json](data.json). For example,

```bash
# After set up my-tex-life-with-julia/data.json
cd my-tex-life-with-julia
. create_project.sh TEMP
```

creates `TEMP` in the current directory, that you can:

```bash
cp -r TEMP/. ../../projects/MyProject/
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
