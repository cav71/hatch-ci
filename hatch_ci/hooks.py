from hatchling.plugin import hookimpl

from hatch_github.build_hook import GitHubBuildHook
from hatch_github.metadata_hook import GitHubMetadataHook
from hatch_github.version_hoock import GitHubVersionSource


@hookimpl
def hatch_register_version_source():
    return GitHubVersionSource


@hookimpl
def hatch_register_build_hook():
    return GitHubBuildHook


@hookimpl
def hatch_register_metadata_hook():
    return GitHubMetadataHook
