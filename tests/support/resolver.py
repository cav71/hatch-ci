"""adds a datadir and resolver fixtures"""

from __future__ import annotations

import dataclasses as dc
import os
from pathlib import Path

import pytest


@pytest.fixture()
def datadir(request):
    """return the Path object to the tests datadir

    Examples:
        # This will print the tests/data directory
        # (unless overridden using DATADIR env)
        >>> def test_me(datadir):
        >>>    print(datadir)
    """
    basedir = Path(__file__).parent.parent / "data"
    if os.getenv("DATADIR"):
        basedir = Path(os.getenv("DATADIR"))
    basedir = basedir / getattr(request.module, "DATADIR", "")
    return basedir


@pytest.fixture(scope="function")
def resolver(request, datadir):
    """return a resolver object to lookup for test data

    Examples:
        >>> def test_me(resolver):
        >>>     print(resolver.lookup("a/b/c"))
    """

    @dc.dataclass
    class Resolver:
        root: Path
        name: str

        def lookup(self, path: Path | str) -> Path:
            candidates = [
                self.root / self.name / path,
                self.root / path,
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
            raise FileNotFoundError(f"cannot find {path}", candidates)

    yield Resolver(datadir, request.module.__name__)
