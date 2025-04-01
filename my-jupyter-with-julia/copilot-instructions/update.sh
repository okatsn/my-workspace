#!/bin/sh

# How to use:
# . copilot-instructions/update.sh
# . copilot-instructions/update.sh --empty   (to clear the instructions file)

if [ "$1" = "--empty" ]; then
    # Empty the instructions file
    echo "" > .github/copilot-instructions.md
    echo "Instructions file has been emptied."
else
    # Run the original command to update instructions
    docker run --rm -v "${PWD}":/workspace okatsn/my-util-box 'stitchmd -no-toc -o .github/copilot-instructions.md copilot-instructions/copilot-instructions.md'
    echo "Output successfully built."
fi