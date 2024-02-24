#!/usr/bin/env python
import json
import os

# import subprocess
import sys
from pathlib import Path
from unittest import mock

import pyproject_hooks._in_process._in_process

import build.__main__


def rm(path: Path):
    from shutil import rmtree

    if not path.exists():
        return
    if path.is_dir():
        rmtree(path)
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


def create_sdist_env(
    workdir: Path, builddir: Path, key: str
) -> tuple[list[str | None], dict[str, str]]:
    (builddir / "xyz").mkdir(parents=True, exist_ok=True)
    (builddir / "xyz-dist").mkdir(parents=True, exist_ok=True)
    (builddir / "xyz" / "input.json").write_text(
        json.dumps(
            {
                "kwargs": {
                    key: str((builddir / "xyz-dist").absolute()),
                    "config_settings": {},
                },
            }
        )
    )

    cmd = [
        Path(pyproject_hooks._in_process._in_process.__file__),
        None,
        (workdir / "build" / "xyz").absolute(),
    ]
    env = {"PEP517_BUILD_BACKEND": "hatchling.build"}
    return [c if c is None else str(c) for c in cmd], env


def run_inprocess(target: str, workdir: Path, builddir: Path, sdist: bool):
    cmd, env = create_sdist_env(
        workdir, builddir, key="sdist_directory" if sdist else "wheel_directory"
    )
    assert cmd[1] is None  # noqa: S101
    cmd[1] = target

    old = sys.argv[:]
    with mock.patch.dict(os.environ, env):
        sys.argv = [str(c) for c in cmd]
        try:
            pyproject_hooks._in_process._in_process.main()
        finally:
            sys.argv = old


if __name__ == "__main__":
    workdir = Path(os.environ.get("SOURCE_DIR", Path(__file__).parent)).absolute()
    builddir = workdir / "build"

    os.chdir(workdir)
    mode = sys.argv[1]
    if mode in {"clean", "clean-all", "build", "sdist", "wheel"}:
        cleanup(workdir)
        if mode in {"clean-all", "sdist", "build_wheel"}:
            rm(builddir / "xyz")
            rm(builddir / "xyz-dist")
    else:
        raise NotImplementedError(f"mod [{mode}] not implemented")

    if mode == "build":
        build.__main__.main(["."], "python -m build")
    elif mode == "sdist":
        run_inprocess("build_sdist", workdir, builddir, sdist=True)
        print(f" results under -> {builddir}")  # noqa: T201
    elif mode == "wheel":
        run_inprocess("build_wheel", workdir, builddir, sdist=False)
        print(f" results under -> {builddir}")  # noqa: T201
