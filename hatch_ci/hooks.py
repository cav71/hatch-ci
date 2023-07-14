from hatchling.plugin import hookimpl

from hatch_ci.build_hook import GitHubBuildHook
from hatch_ci.metadata_hook import GitHubMetadataHook
from hatch_ci.version_hook import GitHubVersionSource


@hookimpl
def hatch_register_version_source():
    return GitHubVersionSource


@hookimpl
def hatch_register_build_hook():
    return GitHubBuildHook


@hookimpl
def hatch_register_metadata_hook():
    return GitHubMetadataHook
