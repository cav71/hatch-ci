from hatchling.version.source.plugin.interface import VersionSourceInterface

from .common import PLUGIN_NAME


class ValidationError(Exception):
    pass


class CIVersionSource(VersionSourceInterface):
    PLUGIN_NAME = PLUGIN_NAME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


#
#    @property
#    def config_tag_pattern(self):
#        if self.__config_tag_pattern is None:
#            tag_pattern = self.config.get('tag-pattern', '')
#            if not isinstance(tag_pattern, str):
#                raise TypeError('option `tag-pattern` must be a string')
#
#            self.__config_tag_pattern = tag_pattern
#
#        return self.__config_tag_pattern
#
#    @property
#    def config_fallback_version(self):
#        if self.__config_fallback_version is None:
#            fallback_version = self.config.get('fallback-version', '')
#            if not isinstance(fallback_version, str):
#                raise TypeError('option `fallback-version` must be a string')
#
#            self.__config_fallback_version = fallback_version
#
#        return self.__config_fallback_version
#
#    @property
#    def config_raw_options(self):
#        if self.__config_raw_options is None:
#            raw_options = self.config.get('raw-options', {})
#            if not isinstance(raw_options, dict):
#                raise TypeError('option `raw-options` must be a table')
#
#            self.__config_raw_options = raw_options
#
#        return self.__config_raw_options
#
#    def construct_setuptools_scm_config(self):
#        from copy import deepcopy
#        
#        config = deepcopy(self.config_raw_options)
#        config.setdefault('root', self.root)
#
#        config.setdefault('tag_regex', self.config_tag_pattern)
#
#        # Only set for non-empty strings
#        if self.config_fallback_version:
#            config['fallback_version'] = self.config_fallback_version
#
#        # Writing only occurs when the build hook is enabled
#        config.pop('write_to', None)
#        config.pop('write_to_template', None)
#        return config

    def get_version_data(self):
        from pathlib import Path
        from os import getenv
        from setuptools_github import tools
        from setuptools_scm import get_version
        try:
            initfile = Path(self.root) / self.config["version-file"]
        except KeyError as exc:
            raise ValidationError(f"no 'version-file' key for plugin {self.PLUGIN_NAME}") from exc

        if getenv("GITHUB_DUMP"):
            pass
        else:
            version = get_version(self.root)
            pass
        breakpoint()
        try:
            version = tools.update_version(initfile, getenv("GITHUB_DUMP"))
        except tools.MissingVariable as exc:
            raise RuntimeError("xxx") from exc
        return {'version': "123"}
        from setuptools_scm import get_version
        from setuptools_scm.tools import MissingVariable
        import inspect
        stack = inspect.stack()
        try:
            the_class = stack[2][0].f_locals["self"].__class__.__name__
            the_method = stack[2][0].f_code.co_name
            print(f"1. {the_class}->{the_method}")
        except:
            print(f"1. ???")
            print(f"  {self.__class__.__name__}->get_version_data")
        breakpoint()

        version = get_version(**self.construct_setuptools_scm_config())
        breakpoint()
        return {'version': version}
