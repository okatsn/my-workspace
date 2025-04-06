# README.md

# Create Container Script

This project provides a shell script to facilitate the creation of project containers using predefined templates. The main entry point is `create.sh`, which allows users to generate `.devcontainer` files based on two different container setups: one for Jupyter with Julia and another for TeX with Julia.

## Usage

To use the script, navigate to the `src` directory and run the `create.sh` script with the desired options and a target directory where files should be copied.

### Flags

- `--container`: Specifies the type of container to create (required). Options:
  - `jupyter`: For Jupyter with Julia setup
  - `tex`: For TeX with Julia setup
- `--gc`: This flag triggers garbage collection, which removes the temporary "TEMP" directories created during the project setup.
- `--force`: This flag allows overwriting existing target directories without prompting for confirmation.


### Examples

1. To create a new Jupyter with Julia setup in "my-project" directory:
   ```bash
   ./create.sh --container jupyter my-project
   ```

2. To create a new TeX with Julia setup in "my-thesis" directory, overwriting if it exists:
   ```bash
   ./create.sh --container tex --force my-thesis
   ```

3. To generate files for a Jupyter container and perform garbage collection:
   ```bash
   ./create.sh --container jupyter my-project --gc
   ```

4. To just perform garbage collection without creating any project:
   ```bash
   ./create.sh --gc --container jupyter
   ```

## Directory Structure

- `src/`: Contains the main scripts and helper functions.
  - `create.sh`: The main entry point for creating project containers.
  - `functions/`: Contains helper and validation scripts.
    - `helpers.sh`: Helper functions for various tasks.
    - `validation.sh`: Validation functions for input parameters.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.