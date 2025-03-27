# Example: In my-workspace run `. my-jupyter-with-julia/create_project.sh HelloWorld`

newproj=$1

# Navigate to the directory
cd ./my-jupyter-with-julia || { echo "Error: Failed to change directory. Your current directory seems to be incorrect. The terminal will be closed soon."; sleep 5; exit 1; }


# Attempt to create the directory. 
# If target directory already exists, exit and raise error to prevent the later unintended `cp` behaviors.
if mkdir "$newproj"; then
  echo "Directory '$newproj' created successfully."
else
  echo "Error: Failed to create directory '$newproj'. The terminal will be closed soon." >&2
  sleep 5 # Wait before exiting to allow user to see the error message.
  exit 1
fi

# The following `cp` commands will create an extra folder if there already is, for example, resulting in NewProject/.vscode/.vscode/settings.json if NewProject/.vscode already exists.

node render.js
cp -r .devcontainer "$newproj/.devcontainer"
cp -r .vscode "$newproj/.vscode"
cp -r copilot-instructions "$newproj/copilot-instructions"
cp data.json "$newproj/data.json" 

cd ..