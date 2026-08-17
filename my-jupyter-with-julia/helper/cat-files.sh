#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Description:
#   Prints a header with the file name and cats the content for a single file
#   or all files inside a specified directory.
#
# Usage Examples:
#
#   1. Display a single file:
#      ./cat-files.sh path/to/script.jl
#
#   2. Display all files in a directory:
#      ./cat-files.sh path/to/directory
#
#   3. Use with `find` to process matching patterns:
#      find . -name 'hypothesis_quadgk_mass_*.jl' -exec bash cat-files.sh {} \;
# ==============================================================================

# Print the file header and stream its contents
display_file() {
    local file_path="${1:-}"

    if [[ -f "$file_path" ]]; then
        printf '# === %s ===\n' "$file_path"
        cat "$file_path"
        printf '\n'
    fi
}

# Iterate through all items in a directory
display_directory() {
    local target_dir="${1:-}"

    # Enable nullglob so the loop does nothing if the directory is empty
    shopt -s nullglob
    for file_path in "$target_dir"/*; do
        display_file "$file_path"
    done
}

main() {
    local target_path="${1:-}"

    # Validate that an argument was provided
    if [[ -z "$target_path" ]]; then
        printf 'Error: A target file or directory is required.\nUsage: %s <file|directory>\n' "$0" >&2
        exit 1
    fi

    # Dispatch based on whether the target is a file or a directory
    if [[ -f "$target_path" ]]; then
        display_file "$target_path"
    elif [[ -d "$target_path" ]]; then
        display_directory "$target_path"
    else
        printf 'Error: "%s" is not a valid file or directory.\n' "$target_path" >&2
        exit 1
    fi
}

main "${1:-}"