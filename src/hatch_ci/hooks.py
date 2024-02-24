from hatchling.plugin import hookimpl

from hatch_ci.build_hook import CIBuildHook
from hatch_ci.version_hook import CIVersionSource


@hookimpl
def hatch_register_version_source():
    return CIVersionSource


@hookimpl
def hatch_register_build_hook():
    return CIBuildHook
