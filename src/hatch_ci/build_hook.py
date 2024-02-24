import os
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CIBuildHook(BuildHookInterface):
    PLUGIN_NAME = "hatch-ci-build"
    BACKUP_SUFFIX = ".from.source"

    def _backup(self, path: Path) -> None:
        from shutil import copyfile, copymode

        path2 = path.parent / f"{path.name}{self.BACKUP_SUFFIX}"
        copyfile(path, path2)
        copymode(path, path2)

    def _un_backup(self, path: Path) -> None:
        from shutil import move

        path2 = path.parent / f"{path.name}{self.BACKUP_SUFFIX}"
        if path2.exists():
            move(path2, path)

    def initialize(self, version, build_data):
        from . import tools
        from .common import RECORD_NAME

        version_file = Path(self.root) / tools.get_option(self.config, "version-file")
        record_path = (Path(version_file).parent / RECORD_NAME).absolute()

        data, _ = tools.get_data(version_file, os.getenv("GITHUB_DUMP"), record_path)

        tools.process(
            version_file,
            os.getenv("GITHUB_DUMP"),
            record_path,
            None,
            None,
            backup=self._backup,
        )

    def finalize(self, version, build_data, artifact_path):
        from . import tools
        from .common import RECORD_NAME

        version_file = Path(self.root) / tools.get_option(self.config, "version-file")

        self._un_backup(version_file)

        record_path = (Path(version_file).parent / RECORD_NAME).absolute()
        record_path.unlink()
