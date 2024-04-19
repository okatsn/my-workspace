target_page=$(curl -sI https://github.com/retorquere/zotero-better-bibtex/releases/latest | grep -i location | tr -d '\r' | cut -d ' ' -f2)

version=$(echo $target_page | sed 's|.*tag/v||') 
#  delete everything before tag/v, which returns 6.7.174 for https://github.com/retorquere/zotero-better-bibtex/releases/tag/v6.7.174

target_file="${target_page}/zotero-better-bibtex-${version}.xpi"

if [ -z "$target_file" ]; then
    echo "Failed to find the download URL."
    exit 1
fi

# Extract filename from URL for saving
filename=$(basename $target_file)
output_path="/tmp/${filename}"
# Download the file
curl -sL $target_file -o $output_path

echo "Downloaded ${filename} to ${output_path}."