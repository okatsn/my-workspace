# README.md

# Create Container Script

This project provides a shell script to facilitate the creation of project containers using predefined templates. The main entry point is `create.sh`, which allows users to generate `.devcontainer` files based on two different container setups: one for Jupyter with Julia and another for TeX with Julia.

## Usage

To use the script, navigate to the `src` directory and run the `create.sh` script with the desired options.

### Flags

- `--gc`: This flag triggers garbage collection, which removes any temporary files or directories created during the project setup.
- `--force`: This flag allows overwriting existing project directories without prompting for confirmation.

### Examples

1. To create a new project container for Jupyter with Julia:
   ```bash
   ./create.sh --force jupyter
   ```

2. To create a new project container for TeX with Julia:
   ```bash
   ./create.sh --force tex
   ```

3. To perform garbage collection:
   ```bash
   ./create.sh --gc
   ```

## Directory Structure

- `src/`: Contains the main scripts and helper functions.
  - `create.sh`: The main entry point for creating project containers.
  - `functions/`: Contains helper and validation scripts.
    - `helpers.sh`: Helper functions for various tasks.
    - `validation.sh`: Validation functions for input parameters.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.