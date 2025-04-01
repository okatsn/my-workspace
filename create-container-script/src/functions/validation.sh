#!/bin/bash

# Function to validate the input parameters
validate_input() {
    if [ -z "$1" ]; then
        echo "Error: No project name provided."
        exit 1
    fi

    if [[ "$1" =~ [^a-zA-Z0-9_-] ]]; then
        echo "Error: Project name can only contain alphanumeric characters, underscores, and hyphens."
        exit 1
    fi

    if [ -d "$1" ]; then
        if [ "$FORCE" != true ]; then
            echo "Error: Directory '$1' already exists. Use --force to overwrite."
            exit 1
        fi
    fi

    if [ ! -f "data.json" ]; then
        echo "Error: Required file 'data.json' not found."
        exit 1
    fi
}