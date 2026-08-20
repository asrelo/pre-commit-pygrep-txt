## Requirements

A workflow must check out the repository and set up Python before calling this action. The current directory must contain a Python project with a valid `pyproject.toml`.

The action installs `build` and `twine`, so the runner must be able to access PyPI (and any build dependencies required by the project).
