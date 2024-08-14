newproj=$1
mkdir "$newproj"
node render.js
cp -r .devcontainer "$newproj/.devcontainer"
cp -r ltex-dictionary "$newproj/ltex-dictionary"
