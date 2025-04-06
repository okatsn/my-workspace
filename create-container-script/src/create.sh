#!/bin/bash

# Function to display usage information
usage() {
  echo "Usage: $0 [--gc] [--force] [--container <container_name>]"
  echo "Options:"
  echo "  --gc                Perform garbage collection (remove temporary files)"
  echo "  --force             Force overwrite existing project directory"
  echo "  --container         Specify the container type (jupyter or tex)"
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
    *) usage ;;
  esac
  shift
done

# Validate input
if [[ -z "$container" ]]; then
  echo "Error: Container type must be specified."
  sleep 5
  usage
fi

# Function to call the appropriate create_project.sh script
create_project() {
  local proj_name=$1
  if [[ "$container" == "jupyter" ]]; then
    if [[ -d "./my-jupyter-with-julia/$proj_name" && "$force" == false ]]; then
      echo "Error: Project directory '$proj_name' already exists. Use --force to overwrite."
      sleep 5
      exit 1
    fi
    . ./my-jupyter-with-julia/create_project.sh "$proj_name"
  elif [[ "$container" == "tex" ]]; then
    if [[ -d "./my-tex-life-with-julia/$proj_name" && "$force" == false ]]; then
      echo "Error: Project directory '$proj_name' already exists. Use --force to overwrite."
      sleep 5
      exit 1
    fi
    . ./my-tex-life-with-julia/create_project.sh "$proj_name"
  else
    echo "Error: Unknown container type '$container'."
    sleep 5
    exit 1
  fi
}

# Perform garbage collection if requested
if [[ "$gc" == true ]]; then
  echo "Performing garbage collection..."
  rm -rv my-jupyter-with-julia/TEMP
  rm -rv my-tex-life-with-julia/TEMP
fi

# Create the project
create_project "TEMP"