import sys
from pathlib import Path

from hatch_ci import fileos


def test_rmtree(tmp_path):
    target = tmp_path / "abc" / "def"
    target.mkdir(parents=True, exist_ok=True)
    assert target.exists()

    fileos.rmtree(target)
    assert not target.exists()
    assert target.parent.exists()


def test_mkdir(tmp_path):
    target = tmp_path / "abc"
    assert not target.exists()
    assert fileos.mkdir(target)
    assert target.exists()
    assert target.is_dir()


def test_touch(tmp_path):
    target = tmp_path / "abc"
    assert not target.exists()
    assert fileos.touch(target)
    assert target.exists()
    assert target.is_file()


def test_which():
    exe = "cmd" if sys.platform == "win32" else "sh"

    path = fileos.which(exe)
    assert path
    assert isinstance(path, Path)

    path = fileos.which(exe, kind=list)
    assert path
    assert isinstance(path, list)
    assert path[0] == fileos.which(exe)
