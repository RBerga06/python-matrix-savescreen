import os
from pathlib import Path
from typing import Any, Iterator
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize


def _cython_ext(root: Path, pyx: Path) -> Extension:
    return Extension(
        ".".join(pyx.with_suffix("").relative_to(root).parts),
        [str(pyx)],
        language="c++",
    )

def find_cython_exts(dir: Path, /, *, root: Path | None = None) -> Iterator[Extension]:
    root = dir if root is None else root
    for path in dir.iterdir():
        if path.is_dir():
            yield from find_cython_exts(path, root=root)
        elif path.is_file():
            if path.suffix == ".pyx":
                yield _cython_ext(root, path)
            elif path.suffix == ".py":
                if "\n# build.py: cythonize\n" in path.read_text():
                    yield _cython_ext(root, path)


SRC = Path(__file__).parent/"src"
CY_EXTS = [*find_cython_exts(SRC)]


def build(setup_kwargs: dict[Any]):
    # gcc arguments hack: enable optimizations
    os.environ['CFLAGS'] = '-O3'

    # Build
    setup_kwargs.update(dict(
        ext_modules=cythonize(
            CY_EXTS,
            annotate=True,
            language_level=3,
            compiler_directives=dict(linetrace=True),
            include_path=[
                str(SRC),
            ],
        ),
        cmdclass=dict(build_ext=build_ext)
    ))
