# Example: `. create_project.sh HelloWorld`

newproj=$1

# Navigate to the directory
cd ./my-jupyter-with-julia || exit 1

mkdir "$newproj"

node render.js
cp -r ./.devcontainer "$newproj/.devcontainer"
cp -r ./ltex-dictionary "$newproj/ltex-dictionary"
cp -r ./.vscode "$newproj/.vscode"
cp ./data.json "$newproj/data.json" 

cd ..