---
applyTo: '**/*.sh'
---

## Guiding Principle
All scripts are for my personal use. Prioritize **simplicity, readability, and maintainability** above all else. Avoid complexity.

## Best Practices
- **Use `set -euo pipefail`**: Start scripts with this line to make them more robust by exiting on errors.
- **Use Functions**: Break down logic into simple, single-purpose functions instead of nesting loops or conditionals.
- **Use Clear Variable Names**: Use `lowercase_with_underscores` for variable names (e.g., `file_path`).
- **Add Comments**: Briefly explain the "why" behind any non-obvious commands or logic.
- For custom error message, wait 5 seconds before exiting to allow user to see the error message.

## What to Avoid
- **Deep Nesting**: Avoid more than one level of nested `if` statements or `for`/`while` loops.
- **Complex Interfaces**: Don't build user-friendly argument parsing or fancy output unless it's the core goal. Simple positional parameters (`$1`, `$2`) are fine.
- **Obscure Commands**: Prefer common, portable POSIX commands over esoteric ones where possible.