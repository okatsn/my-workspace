# README


## A simple python package

[Initiate a Python project](https://youtu.be/PwGKhvqJCQM?si=TZRDzbXqnfrTq-v5&t=511):

```bash
cd my_project
uv init --no-workspace
```

> - It creates `pyproject.toml`.
> - It creates `hello.py`.


Make `my_project` a python package:

```bash
mkdir src
mv hello.py src/main.py
touch __init__.py
```



## Pytest

[Install pytest using `uv`](https://youtu.be/PwGKhvqJCQM?si=-wIaChXqTed0esEl&t=617):

```bash
uv add --dev pytest

```

> 💡Keynote: PyTest is added as a [development dependency](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies) since it is *not* a requirement and no need to be included in the `[project]` table.


Create directory `tests` and put your test scripts there:

```bash
mkdir tests
```

You have to add the followings to the `pyproject.toml` for pytest to initiate the package and doing unit tests:

```toml
[tool.pytest.ini_options]
pythonpath = "src"
```

## VSCode settings:

[In `.vscode/settings.json`, you may need to set the pytest path](https://youtu.be/PwGKhvqJCQM?si=RRIwudapyCWimnMc&t=1238):
```json
{
    // Python settings
    "python.analysis.autoSearchPaths": true,
    "python.envFile": "${workspaceFolder}/.env",
    "python.terminal.activateEnvironment": true,
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    // Pytest settings
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.cwd": "${workspaceFolder}/tests",
    "python.testing.pytestPath": "${workspaceFolder}/.venv/bin/pytest",
}
```

Hint: If `Ctrl+Enter` doesn't execute the current line with the python of `defaultInterpreterPath`, please try `Ctrl+Shift+P`, select `Python: Create Environment`, then choose `Venv`, then choose `Use existing`.
> Referring Vscode documentation: https://code.visualstudio.com/docs/python/environments#_using-the-create-environment-command


## UV setup virtual environment

CHECKPOINT:

- Use `uv sync` to make sure all project dependencies are installed. See https://docs.astral.sh/uv/reference/cli/#uv-sync
- https://docs.astral.sh/uv/reference/cli/#uv-build
- https://docs.astral.sh/uv/reference/cli/#uv-venv
- https://docs.astral.sh/uv/reference/cli/#uv-cache