# CHECKPOINT

To create a basic python project:
https://youtu.be/PwGKhvqJCQM?si=TZRDzbXqnfrTq-v5&t=511


Initiate a Python project:

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