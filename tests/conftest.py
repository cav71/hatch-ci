from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# this ficture generate a new brand python/git project
# Eg.
#     repo = git_project_factory().create()
from support.projects import git_project_factory  # noqa: F401

# this fixtures allows loading data from data subdir
# Eg.
#     resolver.lookup("foobar") ->
#       looks un under data/foobar or data/test_name/foobar
from support.resolver import datadir, resolver  # noqa: F401

# this ficture adds a scripter driver:
# Eg.
#     script = scripter / "script-file.py"
#     result = script.run(["--help"])
#     assert result.out and result.err
#     assert script.compare("some-output-dir")
from support.scripter import scripter  # noqa: F401

from hatch_ci import scm  # noqa: F401


@pytest.fixture(scope="function")
def mktree(tmp_path):
    """
    Args:
        tmp_path (str): The temporary path where the tree structure will be created.

    Returns:
        function: A nested function that creates a directory tree or
        files within the given temporary path.

    """

    def create(txt, mode=None, subpath=""):
        mode = mode or ("tree" if "─ " in txt else "txt")
        if mode == "tree":
            from hatch_ci import tree

            tree.write(Path(tmp_path) / subpath, tree.parse(txt))
        else:
            for path in [f for f in txt.split("\n") if f.strip()]:
                dst = Path(tmp_path) / subpath / path.strip()
                if path.strip().startswith("#"):
                    continue
                elif path.strip().endswith("/"):
                    dst.mkdir(exist_ok=True, parents=True)
                else:
                    dst.parent.mkdir(exist_ok=True, parents=True)
                    dst.write_text("")
        return Path(tmp_path) / subpath

    return create


#####################
# Main flags/config #
#####################


def pytest_configure(config):
    config.addinivalue_line("markers", "manual: test intented to run manually")


def pytest_collection_modifyitems(config, items):
    if config.option.keyword or config.option.markexpr:
        return  # let pytest handle this

    for item in items:
        if "manual" not in item.keywords:
            continue
        item.add_marker(pytest.mark.skip(reason="manual not selected"))
