# README

This is a folder of instructions for copilot.

Instruction on how to use:

1. Create pieces of prompts in markdown files.
2. Include the markdown files in 1. in the `copilot-instructions/copilot-instructions.md`.
3. Run `. copilot-instructions/update.sh`, which update the current `.github/copilot-instructions.md` for the dialog context according to the files in 1 and 2.
4. Run 3 every time before asking a context-based question.

Suggested git settings

- Create an empty `.github/copilot-instructions.md` but do not track it, since it is much more frequent to ask an off-topic question than a context-based question.