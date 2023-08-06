from __future__ import annotations

from typing import Any

from hatchling.version.source.plugin.interface import VersionSourceInterface

from .common import PLUGIN_NAME


class ValidationError(Exception):
    pass


class _NO:
    pass


def extract(
    config: dict[str, str], var: str, typ: Any = _NO, fallback: Any = _NO
) -> Any:
    value = config.get(var, fallback)
    if value is _NO:
        raise ValidationError(f"cannot find variable '{var}' for plugin 'ci'")
    try:
        new_value = typ(value) if typ is not _NO else value
    except Exception as exc:
        raise ValidationError(f"cannot convert to {typ=} the {value=}") from exc
    return new_value


def get_fixers(txt: str) -> dict[str, str]:
    if not txt:
        return {}
    if not isinstance(txt, list):
        raise ValidationError("fixers must be list of dicts")
    if not all(isinstance(t, list) for t in txt):
        raise ValidationError("fixers elements must be lists")
    if not all(len(t) == 2 for t in txt):
        raise ValidationError("all fixers list elements must be of length 2")
    return dict(txt)


class CIVersionSource(VersionSourceInterface):
    PLUGIN_NAME = PLUGIN_NAME

    def get_version_data(self):
        from os import getenv
        from pathlib import Path

        from hatch_ci import tools

        paths = extract(self.config, "paths", typ=tools.list_of_paths, fallback=[])
        fixers = extract(self.config, "fixers", typ=get_fixers, fallback={})
        version_file = Path(self.root) / extract(self.config, "version-file")

        if not version_file.exists():
            raise ValidationError(
                f"no 'version-file' key for plugin {self.PLUGIN_NAME}"
            )
        gdata = tools.process(
            version_file, getenv("GITHUB_DUMP"), paths=paths, fixers=fixers
        )
        return {"version": gdata["version"]}
