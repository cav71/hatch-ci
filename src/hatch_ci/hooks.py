from hatchling.plugin import hookimpl

from hatch_ci.hook_build import CIBuildHook
from hatch_ci.hook_version import CIVersionSource


@hookimpl
def hatch_register_version_source():
    return CIVersionSource


@hookimpl
def hatch_register_build_hook():
    return CIBuildHook
