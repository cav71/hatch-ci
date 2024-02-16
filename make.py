#!/usr/bin/env python
import os
import sys
from pathlib import Path

import build.__main__


def rm(path: Path):
    from shutil import rmtree

    if not path.exists():
        return
    if path.is_dir():
        rmtree(workdir / "dist")
    else:
        path.unlink()


def co(path: Path):
    from subprocess import DEVNULL, call

    call(["git", "co", str(path)], stderr=DEVNULL)  # noqa: S603, S607


def cleanup(workdir: Path):
    rm(workdir / "dist")
    rm(workdir / "src/hatch_ci/_build.py")
    co(workdir / "TEMPLATE.md")
    co(workdir / "src/hatch_ci/__init__.py")


if __name__ == "__main__":
    workdir = Path(__file__).parent
    os.chdir(workdir)
    if sys.argv[1] in {"clean", "build"}:
        cleanup(workdir)

    if sys.argv[1] in "build":
        build.__main__.main(["."], "python -m build")
