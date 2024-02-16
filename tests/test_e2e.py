import re
import subprocess
import zipfile
from pathlib import Path

import pytest

import hatch_ci


@pytest.fixture(scope="function")
def project(git_project_factory):
    """creates a project with this structure
        ├── .git/
        ├── pyproject.toml
        └── src/
            └── <name>>/
                ├── __init__.py  <- contains <version>
                └── xyz.py
    """
    def _make(name, version):
        repo = git_project_factory(name=name).create(version)
        paths = [repo.workdir / "src" / name / "xyz.py" ]
        paths[-1].write_text("""
def hello():
    pass
        """)

        srcdir = str(Path(hatch_ci.__file__).parent.parent.parent).replace("\\", "/")
        paths.append(repo.workdir / "pyproject.toml")
        paths[-1].write_text(f"""
[build-system]
requires = [
    "hatchling>=1.1.0",
    "typing-extensions",
    "jinja2",
    "-e file://{srcdir}"
]
build-backend = "hatchling.build"

[project]
name = "{name}"
dynamic = ["version"]
description = "test project"
requires-python = ">= 3.8"
packages = ["src/{name}"]

[tool.hatch.version]
source = "ci"
version-file = "src/{name}/__init__.py"
    """)
        repo.commit(paths, "init")
        return repo
    return _make


def extract(path, items):
    result = {}
    with zipfile.ZipFile(path) as zfp:
        for zinfo in zfp.infolist():
            if items and zinfo.filename not in items:
                continue
            with zfp.open(zinfo.filename) as fp:
                result[zinfo.filename] = (
                    str(fp.read(), encoding="utf-8").replace("\r", "")
                )
    return result


def test_master_branch(project):
    repo = project("foobar", "0.0.0")

    subprocess.check_call(["python", "-m", "build",],  # noqa: S603,S607
                          cwd=repo.workdir)

    path = repo.workdir / "dist" / f"{repo.name}-{repo.version()}-py3-none-any.whl"
    assert path.exists()

    result = extract(path, [
        "foobar/__init__.py",
        "foobar/_build.py",
    ])

    match = re.search(r"""
__version__ = "(?P<version>\d+([.]\d+)*)"
__hash__ = "(?P<sha>[0-9abcdef]{7})"
""".strip(), result["foobar/__init__.py"].strip())
    assert match
    assert match.group("version") == "0.0.0"

    match = re.search(r"""
branch = '(?P<branch>[^']+)'
build = 0
current = '(?P<current>\d+([.]\d+)*)'
ref = 'refs/heads/master'
runid = 0
sha = '(?P<sha>[0-9abcdef]{40})'
version = '(?P<version>\d+([.]\d+)*)'
workflow = 'master'
""".strip(), result["foobar/_build.py"].strip())

    assert match
    assert match.group("version") == "0.0.0"
