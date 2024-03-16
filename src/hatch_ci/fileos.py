"""various file/dir related functions"""

import os
from pathlib import Path
from typing import overload


def rmtree(path: Path):
    """universal (win|*nix) rmtree"""

    from os import name
    from shutil import rmtree
    from stat import S_IWUSR

    if name == "nt":
        for p in path.rglob("*"):
            p.chmod(S_IWUSR)
    rmtree(path, ignore_errors=True)
    if path.exists():
        raise RuntimeError(f"cannot remove {path=}")


def mkdir(path: Path) -> Path:
    """make a path directory and returns if it has been created"""
    path.mkdir(exist_ok=True, parents=True)
    return path


def touch(path: Path) -> Path:
    """touch a new empty file"""
    mkdir(path.parent)
    path.write_text("")
    return path


@overload
def which(exe: Path | str, kind: type[list], abort: bool = True) -> list[Path]: ...


@overload
def which(exe: Path | str, kind: None, abort: bool = True) -> Path | None: ...


def which(
    exe: Path | str, kind: type[list] | None = None, abort: bool = True
) -> list[Path] | Path | None:
    candidates: list[Path] = []
    for srcdir in os.environ.get("PATH", "").split(os.pathsep):
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            path = srcdir / Path(exe).with_suffix(ext)
            if not path.exists():
                continue
            if kind is None:
                return path
            candidates.append(path)
    return candidates
