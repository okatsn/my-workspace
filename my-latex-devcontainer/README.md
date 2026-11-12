# README
This builds a final workspace that supports LaTeX utilities provide by provided by [MyTeXLife](https://github.com/okatsn/MyTeXLife) `FROM` [okatsn/my-tex-life](https://hub.docker.com/repository/docker/okatsn/my-tex-life/general) and julia utilities provided by `../julia-debian-build`.

The content of this folder is migrated from [okatsn/MyTeXLifeWithJulia](https://github.com/okatsn/MyTeXLifeWithJulia); please refer to this archive for older history.

## Use with Dev Containers extension of VSCode

Use with Dev Containers extension of VSCode (`ms-vscode-remote.remote-containers`)
- `WSL: Open folder in WSL` and open `my-workspace/my-latex-devcontainer`
- `Dev Containers: Rebuild and Reopen in Container`


For more information, see the comments in Dockerfile.

## Create the same environment but in different name


Option 1:
- Modify the contents in `data.json`.
- `my-latex-devcontainer/create_project.sh --target ~/projects/HelloWorld` in bash (run from anywhere).

Option 2:
- Modify the contents in `data.json`.
- `node render.js`.
- Copy `.devcontainer` folder to the directory of your project.


## Apply this workspace as arbitrary container (for user)

To build user's workspace, modify [my-latex-devcontainer/data.json](data.json) and use [my-latex-devcontainer/create_project.sh](create_project.sh) to export `.devcontainer` files based on [data.json](data.json). The script is path stable (run it from anywhere, executed rather than sourced), and renders in a temporary directory, so this template directory is never modified.

```bash
create_project.sh --target DIR [--source data.json] [--force]
```

- `--target`: the project directory. It must not exist unless `--force` is given.
- `--source`: the `data.json` to populate the templates with; default to `data.json` next to the script.
- `--force`: allow an existing target and overwrite everything the script copies (including `manuscript/`, `chapters/`, `contents/`, `AGENTS.md`).

For example, to create a project, or to update one with its own `data.json`:

```bash
my-latex-devcontainer/create_project.sh --target ~/projects/MyProject
cd ~/projects/MyProject && ~/projects/my-workspace/my-latex-devcontainer/create_project.sh --source ./data.json --target . --force
```
