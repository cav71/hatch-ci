from hatchling.plugin import hookimpl

from hatch_ci.version_hook import CIVersionSource


@hookimpl
def hatch_register_version_source():
    return CIVersionSource
