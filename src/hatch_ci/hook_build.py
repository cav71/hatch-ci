import os
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from . import common


class CIBuildHook(BuildHookInterface):
    PLUGIN_NAME = common.PLUGIN_NAME

    def initialize(self, version, build_data):
        from . import code, tools

        version_file = Path(self.root) / tools.get_option(self.config, "version-file")
        record_path = (Path(version_file).parent / common.RECORD_NAME).absolute()
        env = tools.get_environment(version_file, os.getenv("GITHUB_DUMP"), record_path)

        tools.generate_build_record(record_path, env.globals["ctx"])

        tools.backup(version_file, abort=False)
        code.set_module_var(version_file, "__version__", env.globals["ctx"].version)
        code.set_module_var(
            version_file, "__hash__", (env.globals["ctx"].sha or "")[:7]
        )

        paths = [
            Path(self.root) / path
            for path in tools.get_option(self.config, "process-paths", fallback=[])
        ]
        replacements = tools.get_option(
            self.config, "process-replace", fallback=[], typ=dict
        )
        for path in paths:
            txt = tools.replace(path.read_text(), replacements)
            out = env.from_string(txt).render()
            tools.backup(path, abort=False)
            path.write_text(out)

    def finalize(self, version, build_data, artifact_path):
        from . import tools

        version_file = Path(self.root) / tools.get_option(self.config, "version-file")
        record_path = (Path(version_file).parent / common.RECORD_NAME).absolute()

        paths = [
            Path(self.root) / path
            for path in tools.get_option(self.config, "process-paths", fallback=[])
        ]
        for path in paths:
            tools.unbackup(path)
        tools.unbackup(version_file, abort=False)
        record_path.unlink()


if __name__ == "__main__":
    import toml

    from . import tools

    cfg = toml.loads(Path("pyproject.toml").read_text())
    replacements = dict(cfg["tool"]["hatch"]["build"]["hooks"]["ci"]["process-replace"])
    env = tools.get_environment(Path("src/hatch_ci/__init__.py"))

    path = Path("README.md")
    txt = tools.replace(path.read_text(), replacements)
    out = env.from_string(txt).render()
    Path("out.txt").write_text(out)
