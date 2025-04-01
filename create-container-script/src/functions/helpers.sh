# filepath: /create-container-script/create-container-script/src/functions/helpers.sh

# Helper functions for create.sh

# Function to check if a directory exists
check_directory_exists() {
    if [ -d "$1" ]; then
        return 0  # Directory exists
    else
        return 1  # Directory does not exist
    fi
}

# Function to display usage information
display_usage() {
    echo "Usage: ./create.sh [options] <project_name>"
    echo "Options:"
    echo "  --gc        Perform garbage collection"
    echo "  --force     Force overwrite existing project"
    echo "  --jupyter   Create a project using my-jupyter-with-julia"
    echo "  --tex       Create a project using my-tex-life-with-julia"
}

# Function to handle command-line arguments
parse_arguments() {
    while [[ "$1" != "" ]]; do
        case $1 in
            --gc )         garbage_collection=true
                           ;;
            --force )      force_overwrite=true
                           ;;
            --jupyter )    container_type="jupyter"
                           ;;
            --tex )        container_type="tex"
                           ;;
            * )            project_name="$1"
                           ;;
        esac
        shift
    done
}