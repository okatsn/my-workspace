# Example: In my-jupyter-with-julia run `. create_project.sh HelloWorld`

newproj=$1

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

# Guard: ensure node is available
if ! command -v node > /dev/null 2>&1; then
  echo "Error: 'node' is not installed. Please install Node.js before running this script." >&2
  exit 1
fi

# Guard: ensure mustache package is installed (install automatically if missing)
if [ ! -d node_modules ]; then
  echo "node_modules not found. Running npm install..." >&2
  npm install
fi

node render.js
cp -r .devcontainer "$newproj/.devcontainer"
cp -r .vscode "$newproj/.vscode"
cp data.json "$newproj/data.json"
# Helper scripts
cp -r helper/ "$newproj/helper"