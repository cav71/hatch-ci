from __future__ import annotations

from hatchling.version.source.plugin.interface import VersionSourceInterface

from . import common


class ValidationError(Exception):
    pass


class CIVersionSource(VersionSourceInterface):
    PLUGIN_NAME = common.PLUGIN_NAME

    def get_version_data(self):
        from os import getenv
        from pathlib import Path

        from hatch_ci import tools

        # paths = extract(self.config, "paths", typ=tools.list_of_paths, fallback=[])
        # fixers = extract(self.config, "fixers", typ=get_fixers, fallback={})

        version_file = Path(self.root) / tools.get_option(self.config, "version-file")
        record_path = (Path(version_file).parent / common.RECORD_NAME).absolute()

        if not version_file.exists():
            raise ValidationError(
                f"no 'version-file' key foun in plugin {self.PLUGIN_NAME}"
            )

        gdata = tools.get_data(version_file, getenv("GITHUB_DUMP"), record_path)

        # gdata = tools.process(
        #    version_file, getenv("GITHUB_DUMP"), paths=paths, fixers=fixers
        # )
        return {"version": gdata["version"]}
