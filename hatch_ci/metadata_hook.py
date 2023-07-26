from collections import ChainMap

from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.utils.context import ContextStringFormatter

from .common import PLUGIN_NAME


class GitHubMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = PLUGIN_NAME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__config_urls = None

    @property
    def config_urls(self):
        if self.__config_urls is None:
            urls = self.config.get('urls', {})
            if not isinstance(urls, dict):
                raise TypeError('option `urls` must be a table')

            for key, url in urls.items():
                if not isinstance(url, str):
                    raise TypeError(f'URL `{key}` in option `urls` must be a string')

            self.__config_urls = urls

        return self.__config_urls

    def update(self, metadata):
        import inspect
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__.__name__
        the_method = stack[1][0].f_code.co_name
        print(f"2. {the_class}->{the_method}")
        print(f"  {self.__class__.__name__}->update")
        formatter = ContextStringFormatter(
            ChainMap(
                {
                    'commit_hash': lambda *args: vcs_utils.get_commit_hash(self.root),
                },
            )
        )
        urls = self.config_urls.copy()
        for key, url in urls.items():
            urls[key] = formatter.format(url)

        metadata['urls'] = urls
