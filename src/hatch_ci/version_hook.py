from typing import Any

from hatchling.version.source.plugin.interface import VersionSourceInterface

from .common import PLUGIN_NAME


class ValidationError(Exception):
    pass


class _NO:
    pass


def extract(
    config: dict[str, str], var: str, typ: Any = _NO, optional: Any = _NO
) -> Any:
    value = config.get(var, optional)
    if value is _NO:
        raise ValidationError(f"cannot find variable '{var}' for plugin 'ci'")
    try:
        new_value = typ(value) if typ is not _NO else value
    except Exception as exc:
        raise ValidationError(f"cannot convert to {typ=} the {value=}") from exc
    return new_value


def get_fixers(txt: str) -> dict[str, str]:
    if not isinstance(txt, list):
        raise ValidationError("fixers must be list of dicts")
    if not all(isinstance(t, dict) for t in txt):
        raise ValidationError("fixers elements must be dicts")
    result = {}
    for item in txt:
        if len(item) != 1:
            raise ValidationError(f"cannot have an item with length != 1: {item}")
        key = next(iter(item))
        result[key] = item[key]
    return result


class CIVersionSource(VersionSourceInterface):
    PLUGIN_NAME = PLUGIN_NAME

    def get_version_data(self):
        from os import getenv
        from pathlib import Path

        from hatch_ci import tools

        paths = extract(self.config, "paths", typ=tools.list_of_paths)
        fixers = extract(self.config, "fixers", typ=get_fixers)
        version_file = Path(self.root) / extract(self.config, "version-file")
        if not version_file.exists():
            raise ValidationError(
                f"no 'version-file' key for plugin {self.PLUGIN_NAME}"
            )
        gdata = tools.process(
            version_file, getenv("GITHUB_DUMP"), paths=paths, fixers=fixers
        )
        return {"version": gdata["version"]}
