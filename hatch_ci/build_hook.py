from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from .common import PLUGIN_NAME
from hatch_vcs.build_hook import VCSBuildHook

class CIBuildHook(VCSBuildHook):
    PLUGIN_NAME = PLUGIN_NAME

    def initialize(self, version, build_data):
        from setuptools_scm import dump_version

        import inspect
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__.__name__
        the_method = stack[1][0].f_code.co_name
        print(f"3. {the_class}->{the_method}")
        print(f"  {self.__class__.__name__}->initialize({build_data=})")
        # HERE
        #breakpoint()
        dump_version(self.root, self.metadata.version, self.config_version_file, template=self.config_template)

        build_data['artifacts'].append(f'/{self.config_version_file}')
