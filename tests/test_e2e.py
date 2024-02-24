# noqa: I001
import re
from pathlib import Path

import pytest

import hatch_ci
from build.__main__ import main as build
from hatch_ci import tools


@pytest.fixture(scope="function")
def project(git_project_factory, monkeypatch):
    """creates a project with this structure
        ├── .git/
        ├── pyproject.toml
        └── src/
            └── <name>>/
                ├── __init__.py  <- contains <version>
                └── xyz.py
    """
    def _make(name, version, cwd=True, use_hatchci_from_env=False):
        repo = git_project_factory(name=name).create(version)
        if cwd:
            monkeypatch.chdir(repo.workdir if cwd is True else cwd)

        paths = []

        # xyz module
        paths.append(repo.workdir / "src" / name / "template.jinja2")
        paths[-1].write_text("""
# This is a file that will be jinjia2 processed during build
        """)

        # pyproject
        # in use_hatchci_from_env we use the hatch-ci from the current env
        # (eg. pip editable installed)
        srcdir = str(Path(hatch_ci.__file__).parent.parent.parent).replace("\\", "/")
        hatch_src = "hatch-ci" if use_hatchci_from_env else f"-e file://{srcdir}"
        paths.append(repo.workdir / "pyproject.toml")
        paths[-1].write_text(f"""
[build-system]
requires = [
    "hatchling>=1.1.0",
    "typing-extensions",
    "jinja2",
    "{hatch_src}"
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

[tool.hatch.build.hooks.hatch-ci-build]
version-file = "src/{name}/__init__.py"
    """)
        repo.commit(paths, "init")
        return repo
    return _make


def match_version(txt):
    result = re.search(r"""
__version__ = "(?P<version>\d+([.]\d+)*)(?P<tag>[a-zA-Z].*)?"
__hash__ = "(?P<sha>[0-9abcdef]{7})"
""".strip(), txt.strip().replace("\r", ""))
    return result.groupdict() if result else None


def match_build(txt):
    result = re.search(r"""
branch = '(?P<branch>[^']+)'
build = 0
current = '(?P<current>\d+([.]\d+)*)(?P<ctag>[a-zA-Z].*)?'
ref = '(?P<ref>[^']+)'
runid = 0
sha = '(?P<sha>[0-9abcdef]{40})'
version = '(?P<version>\d+([.]\d+)*)(?P<tag>[a-zA-Z].*)?'
workflow = '(?P<workflow>[^']+)'
    """.strip(), txt.strip().replace("\r", ""))
    return result.groupdict() if result else None


def test_master_branch(project):
    isolated = False # hatch-ci from the current python env if False
    repo = project("foobar", "0.0.0", use_hatchci_from_env=not isolated)

    assert repo.status() == {}
    build(["."] if isolated else ["-n", "."], "pytest")

    # 1. verify we don't have leftovers
    assert repo.status() == {"dist/": 128, }

    # 2. verify the sdist contains the right files
    tarball = repo.workdir / "dist" / f"{repo.name}-{repo.version()}.tar.gz"

    contents = tools.zextract(tarball)
    assert set(contents) == {
        "foobar-0.0.0/.gitignore",
        "foobar-0.0.0/PKG-INFO",
        "foobar-0.0.0/pyproject.toml",
        "foobar-0.0.0/src/foobar/__init__.py",
        "foobar-0.0.0/src/foobar/__init__.py.from.source",
        "foobar-0.0.0/src/foobar/_build.py",
        "foobar-0.0.0/src/foobar/template.jinja2",
    }

    assert match_version(contents["foobar-0.0.0/src/foobar/__init__.py"]) == {
        "version": "0.0.0", "sha": repo.head.target.hex[:7], "tag": None,
    }
    assert match_build(contents["foobar-0.0.0/src/foobar/_build.py"]) == {
        "branch": "master", "current": "0.0.0",
        "sha":    repo.head.target.hex,
        "version": "0.0.0", "tag": None, "workflow": "master",
        "ref": "refs/heads/master", "ctag": None,
    }

    # 3. verify the wheel contains the right files
    wheel = repo.workdir / "dist" / f"{repo.name}-{repo.version()}-py3-none-any.whl"

    contents = tools.zextract(wheel)
    assert set(contents) == {
        "foobar-0.0.0.dist-info/METADATA",
        "foobar-0.0.0.dist-info/RECORD",
        "foobar-0.0.0.dist-info/WHEEL",
        "foobar/__init__.py",
        "foobar/__init__.py.from.source",
        "foobar/_build.py",
        "foobar/template.jinja2",
    }

    assert match_version(contents["foobar/__init__.py"]) == {
        "version": "0.0.0", "sha": repo.head.target.hex[:7], "tag": None,
    }
    assert match_build(contents["foobar/_build.py"]) == {
        "branch": "master", "current": "0.0.0",
        "sha":    repo.head.target.hex, "version": "0.0.0", "tag": None,
        "workflow": "master",
        "ref": "refs/heads/master", "ctag": None,
    }


def test_beta_branch(project):
    isolated = False # hatch-ci from the current python env if False
    tag = "b0" # we build with an index of 0 (the fallback)

    repo = project("foobar", "0.0.0", use_hatchci_from_env=not isolated)
    repo.branch("beta/0.0.0")
    assert repo.branch() == "beta/0.0.0"

    assert repo.status() == {}
    build(["."] if isolated else ["-n", "."], "pytest")

    # 1. verify we don't have leftovers
    assert repo.status() == {"dist/": 128, }


    # 2. verify the sdist contains the right files
    tarball = repo.workdir / "dist" / f"{repo.name}-{repo.version()}{tag}.tar.gz"

    contents = tools.zextract(tarball)
    assert set(contents) == {
        f"foobar-0.0.0{tag}/.gitignore",
        f"foobar-0.0.0{tag}/PKG-INFO",
        f"foobar-0.0.0{tag}/pyproject.toml",
        f"foobar-0.0.0{tag}/src/foobar/__init__.py",
        f"foobar-0.0.0{tag}/src/foobar/__init__.py.from.source",
        f"foobar-0.0.0{tag}/src/foobar/_build.py",
        f"foobar-0.0.0{tag}/src/foobar/template.jinja2",
    }

    assert match_version(contents[f"foobar-0.0.0{tag}/src/foobar/__init__.py"]) == {
        "version": "0.0.0", "sha": repo.head.target.hex[:7], "tag": tag,
    }
    assert match_build(contents[f"foobar-0.0.0{tag}/src/foobar/_build.py"]) == {
        "branch": "beta/0.0.0", "current": "0.0.0",
        "sha":    repo.head.target.hex, "version": "0.0.0",
        "tag": tag, "ref": "refs/heads/beta/0.0.0",
        "workflow": "beta", "ctag": None,
    }

    # 3. verify the wheel contains the right files
    wheel = (
            repo.workdir / "dist" /
            f"{repo.name}-{repo.version()}{tag}-py3-none-any.whl"
    )

    contents = tools.zextract(wheel)
    assert set(contents) == {
        f"foobar-0.0.0{tag}.dist-info/METADATA",
        f"foobar-0.0.0{tag}.dist-info/RECORD",
        f"foobar-0.0.0{tag}.dist-info/WHEEL",
        "foobar/__init__.py",
        "foobar/__init__.py.from.source",
        "foobar/_build.py",
        "foobar/template.jinja2",
    }

    assert match_version(contents["foobar/__init__.py"]) == {
        "version": "0.0.0", "sha": repo.head.target.hex[:7], "tag": "b0",
    }
    assert match_build(contents["foobar/_build.py"]) == {
        "branch": "beta/0.0.0", "current": "0.0.0", "ref": "refs/heads/beta/0.0.0",
        "sha":    repo.head.target.hex, "version": "0.0.0",
        "tag": "b0", "workflow": "beta",
        "ctag": tag,
    }





