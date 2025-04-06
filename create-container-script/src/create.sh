#!/bin/bash

# Function to display usage information
usage() {
  echo "Usage: $0 [--gc] [--force] --container <container_name> [target_directory]"
  echo "Options:"
  echo "  --gc                Perform garbage collection (remove TEMP directory)"
  echo "  --force             Force overwrite existing target directory"
  echo "  --container         Specify the container type (jupyter or tex)"
  echo "Arguments:"
  echo "  target_directory    The directory where files will be copied (optional)"
  sleep 5
  exit 1
}

# Parse command-line arguments
gc=false
force=false
container=""

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --gc) gc=true ;;
    --force) force=true ;;
    --container) container="$2"; shift ;;
    -*) usage ;;
    *) target_dir="$1"; break ;;
  esac
  shift
done

# Validate input
if [[ -z "$container" ]]; then
  echo "Error: Container type must be specified."
  sleep 5
  usage
fi

# Always use TEMP as the project directory
TEMP_DIR="TEMP"

# Function to call the appropriate create_project.sh script
create_project() {
  if [[ "$container" == "jupyter" ]]; then
    # Remove existing TEMP directory if it exists
    if [[ -d "./my-jupyter-with-julia/$TEMP_DIR" ]]; then
      rm -rf "./my-jupyter-with-julia/$TEMP_DIR"
    fi
    . ./my-jupyter-with-julia/create_project.sh "$TEMP_DIR"
  elif [[ "$container" == "tex" ]]; then
    # Remove existing TEMP directory if it exists
    if [[ -d "./my-tex-life-with-julia/$TEMP_DIR" ]]; then
      rm -rf "./my-tex-life-with-julia/$TEMP_DIR"
    fi
    . ./my-tex-life-with-julia/create_project.sh "$TEMP_DIR"
  else
    echo "Error: Unknown container type '$container'."
    sleep 5
    exit 1
  fi
}

# Create the project in TEMP directory
create_project

# Copy files to target directory if specified
if [[ -n "$target_dir" ]]; then
  # Check if target directory exists and --force is not set
  if [[ -d "$target_dir" && "$force" != true ]]; then
    echo "Error: Target directory '$target_dir' already exists. Use --force to overwrite."
    sleep 5
    exit 1
  fi
  
  # Create or overwrite target directory
  if [[ "$force" == true ]]; then
    echo "Copying files to $target_dir (with force)..."
    cp -rf "./my-${container}-with-julia/$TEMP_DIR/"* "$target_dir"
  else
    echo "Copying files to $target_dir..."
    mkdir -p "$target_dir"
    cp -r "./my-${container}-with-julia/$TEMP_DIR/"* "$target_dir"
  fi
  
  echo "Files successfully copied to $target_dir"
fi

# Perform garbage collection if requested
if [[ "$gc" == true ]]; then
  echo "Performing garbage collection..."
  rm -rf "./my-jupyter-with-julia/$TEMP_DIR"
  rm -rf "./my-tex-life-with-julia/$TEMP_DIR"
  echo "TEMP directories removed."
fi