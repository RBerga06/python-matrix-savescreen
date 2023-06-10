import os
from pathlib import Path
from typing import Any, Iterator

# See if Cython is installed
try:
    from Cython.Build import cythonize
# Do nothing if Cython is not available
except ImportError:
    # Got to provide this function. Otherwise, poetry will fail
    def build(setup_kwargs):
        pass
# Cython is installed. Compile
else:
    from setuptools import Extension
    from setuptools.dist import Distribution
    from distutils.command.build_ext import build_ext

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

    # This function will be executed in setup.py:
    def build(setup_kwargs: dict[Any]):
        # src directory path
        SRC = Path(__file__).parent/"src"

        # gcc arguments hack: enable optimizations
        os.environ['CFLAGS'] = '-O3'

        # Build
        setup_kwargs.update(dict(
            ext_modules=cythonize(
                [*find_cython_exts(SRC)],
                annotate=True,
                language_level=3,
                compiler_directives=dict(linetrace=True),
                include_path=[
                    str(SRC),
                ],
            ),
            cmdclass=dict(build_ext=build_ext)
        ))


if __name__ == "__main__":
    build()
