# rberga06-matrix

Terminal screensaver with _Matrix_-like raindrop effect, written in Python.

> **Warning**
> This is _not_ an actual 'screen saver', because it's not trivial to render;
> hence, while this program is in execution, the computer will try and render the effect as fast as possible.
> This might have a negative impact on the system resources (such as RAM or VRAM) in use.

## Installation

In a Python 3.11 (or later) virtual environment, run:
```bash
python -m pip install "rberga06-matrix @ git+https://github.com/RBerga06/python-matrix-savescreen"
```
You will then be able to run the project with the simple command:
```bash
matrix
```

### Development

If you also want to play around with the project, we recommend cloning this repo and using [`poetry`](https://python-poetry.org/):
```bash
# Clone this repo (via GitHub CLI)
gh repo clone RBerga06/python-matrix-savescreen
cd python-matrix-savescreen
# Build and install the project in a dedicated venv
poetry install  # pure Python project
poetry install  # Cython
# Run the project
poetry run matrix
```
