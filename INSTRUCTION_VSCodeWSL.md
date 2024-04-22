## Instruction for developer
### Build the image based on files in .devcontainer
Make sure the following files are prepared:
- Dockerfile: Script for building the container
- docker-compose.yml: The Compose file that uses Dockerfile and set volumes up.
- devcontainer.json: The file for vscode set up.

#### In vscode 

Steps
- Install `Dev Containers` (as well as WSL and so on. See [this](https://github.com/okatsn/swc-forecast-TWAI-23a/blob/master/DEVELOPMENT.md#install-or-set-up-prerequisite) for more information)
- `Ctrl+Shift+P` and select **Dev Containers: Rebuild Container Without Cache**


## Instruction for users

### First-time use
For `OhMyREPL` to work: 
- `pkg> instantiate`
- close julia REPL and open it again; you should see julia syntax highlighted by colors (which means `startup.jl` successfully executed at the start up of julia REPL).