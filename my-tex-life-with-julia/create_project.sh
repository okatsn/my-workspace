newproj=$1

# Navigate to the directory
cd ./my-tex-life-with-julia || exit 1
mkdir "$newproj"

node render.js
cp -r ./.devcontainer "$newproj/.devcontainer"
cp -r ./ltex-dictionary "$newproj/ltex-dictionary"
cp ./data.json "$newproj/data.json" 

cd ..