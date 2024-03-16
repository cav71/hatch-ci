# see https://pypi.org/project/setuptools-github
# copy of setuptools_github.tools
from __future__ import annotations

import argparse
import functools
import json
import logging
import re
from pathlib import Path
from typing import Any

import jinja2

from . import code, common, fileos, scm, text

log = logging.getLogger(__name__)


class ToolsError(Exception):
    pass


class ValidationError(ToolsError):
    pass


class InvalidVersionError(ToolsError):
    pass


class MissingVariableError(ToolsError):
    pass


class _NO:
    pass


class _Context(argparse.Namespace):
    def items(self):
        for name, value in self.__dict__.items():
            if name.startswith("_"):
                continue
            yield (name, value)


def list_of_paths(paths: str | Path | list[str | Path] | None) -> list[Path]:
    if not paths:
        return []
    return [Path(s) for s in ([paths] if isinstance(paths, (str, Path)) else paths)]


backup = functools.partial(fileos.backup, ext=common.BACKUP_SUFFIX)
unbackup = functools.partial(fileos.unbackup, ext=common.BACKUP_SUFFIX)


def get_option(
    config: dict[str, str], var: str, typ: Any = _NO, fallback: Any = _NO
) -> Any:
    """extract an option value from the hatch config dict

    Eg.
        get_options(self.config, "key")
    """
    value = config.get(var, fallback)
    if value is _NO:
        raise ValidationError(f"cannot find variable '{var}' for plugin 'ci'")
    try:
        new_value = typ(value) if typ is not _NO else value
    except Exception as exc:
        raise ValidationError(f"cannot convert to {typ=} the {value=}") from exc
    return new_value


def replace(txt: str, replacements: dict[str, str] | None = None) -> str:
    result = txt
    for src, dst in (replacements or {}).items():
        if src.startswith("re:"):
            result = re.sub(src[3:], dst, result)
        else:
            result = result.replace(src, dst)
    return result


def bump_version(version: str, mode: str) -> str:
    """given a version str will bump it according to mode

    Arguments:
        version: text in the N.M.O form
        mode: major, minor or micro

    Returns:
        increased text

    >>> bump_version("1.0.3", "micro")
    "1.0.4"
    >>> bump_version("1.0.3", "minor")
    "1.1.0"
    """
    newver = [int(n) for n in version.split(".")]
    if mode == "major":
        newver[-3] += 1
        newver[-2] = 0
        newver[-1] = 0
    elif mode == "minor":
        newver[-2] += 1
        newver[-1] = 0
    elif mode == "micro":
        newver[-1] += 1
    return ".".join(str(v) for v in newver)


def _validate_gdata(
    gdata: dict[str, Any], abort: bool = True
) -> tuple[set[str], set[str]]:
    keys = {
        "ref",
        "sha",
        "run_id",
        "run_number",
    }
    missing = keys - set(gdata)
    extra = set(gdata) - keys
    if abort and missing:
        raise ToolsError(
            f"missing keys from gdata '{','.join(missing)}'", missing, extra, gdata
        )
    return missing, extra


def get_data(
    version_file: str | Path,
    github_dump: str | None = None,
    record_path: Path | None = None,
    abort: bool = True,
) -> dict[str, str | None]:
    """extracts version information from github_dump and updates version_file in-place

    This gather version, branch, commit and other info from:

    - version_file (eg. the __init__.py file containing __version__)
    - github_dump *a json encoded dictionary in GITHUB_DUMP
    - a record file (eg. _build.py)
    - the git checkout (using git)

    Args:
        version_file (str, Path): path to a file  with a __version__ variable
        github_dump (str): the os.getenv("GITHUB_DUMP") value (a json structure)
        record: pull data from a _build.py file

    Returns:
        dict[str,str|None]: a dict with the current config
        dict[str,str|None]: a dict with the github dump data

    Example:
        for github data:
            {
                "ref": "refs/heads/beta/0.3.10",
                "run_id": "5904313530",
                "run_number": "98",
                "sha": "507c657056d1a66520ec6b219a64706e70b0ff15",
            }
        for data:
            {
                "branch": "beta/0.3.10",
                "build": "98",
                "current": "0.3.10",
                "ref": "refs/heads/beta/0.3.10",
                "runid": "5904313530",
                "sha": "507c657056d1a66520ec6b219a64706e70b0ff15",
                "version": "0.3.10b98",
                "workflow": "beta",
            }
    """

    # we fill this structure getting data from these sources:
    #  github_dump -> record_path (eg. _build.py) -> repo infos (eg. the git checkout)
    data = {
        "version": code.get_module_var(version_file, "__version__"),
        "current": code.get_module_var(version_file, "__version__"),
        "ref": None,
        "branch": None,
        "sha": None,
        "build": None,
        "runid": None,
        "workflow": None,
    }

    path = Path(version_file)
    repo = scm.lookup(path)
    record = record_path.exists() if record_path else None

    if not (repo or github_dump or record):
        if abort:
            raise scm.InvalidGitRepoError(
                f"cannot figure out settings (no repo in {path}, "
                f"a GITHUB_DUMP or a _build.py file)"
            )
        return data

    dirty = False
    if github_dump:
        gdata = json.loads(github_dump) if isinstance(github_dump, str) else github_dump
    elif record_path and record_path.exists():
        mod = fileos.loadmod(record_path)
        gdata = {
            "ref": mod.ref,
            "sha": mod.sha,
            "run_number": mod.build,
            "run_id": mod.runid,
        }
    elif repo:
        gdata = {
            "ref": repo.head.name,
            "sha": repo.head.target.hex,
            "run_number": 0,
            "run_id": 0,
        }
        dirty = repo.dirty()
    else:
        raise RuntimeError(
            "Unable to retrieve data from GITHUB_DUMP or " "{record_path=} or {repo=}"
        )

    # make sure we have all keys
    _validate_gdata(gdata)

    expr = re.compile(r"/(?P<what>beta|release)/(?P<version>\d+([.]\d+)*)$")
    expr1 = re.compile(r"(?P<version>\d+([.]\d+)*)(?P<num>b\d+)?$")

    # update/fill the data values
    data["ref"] = gdata["ref"]
    data["sha"] = gdata["sha"] + ("*" if dirty else "")
    data["build"] = gdata["run_number"]  # unless in GITHUB_DUMP these are likely None
    data["runid"] = gdata["run_id"]  # unless in GITHUB_DUMP these are likely None

    data["branch"] = text.lstrip(gdata["ref"], ["refs/heads/", "refs/tags/"])
    data["workflow"] = data["branch"]

    current = data["current"]
    if match := expr.search(gdata["ref"]):
        # setuptools double calls the update_version,
        # this fixes the issue
        match1 = expr1.search(current or "")
        if not match1:
            raise InvalidVersionError(f"cannot parse current version '{current}'")
        if match1.group("version") != match.group("version"):
            raise InvalidVersionError(
                f"building package for {current} from '{gdata['ref']}' "
                f"branch ({match.groupdict()} mismatch {match1.groupdict()})"
            )
        if match.group("what") == "beta":
            data["version"] = f"{match1.group('version')}b{gdata['run_number']}"
            data["workflow"] = "beta"
        else:
            data["workflow"] = "tags"

    assert len(data) == 8, "cannot change the data structure shape"  # noqa: S101
    return data


def update_version(
    version_file: str | Path, github_dump: str | None = None, abort: bool = True
) -> str | None:
    """extracts version information from github_dump and updates version_file in-place

    Args:
        version_file (str, Path): path to a file with a __version__ variable
        github_dump (str): the os.getenv("GITHUB_DUMP") value

    Returns:
        str: the new version for the package
    """

    data = get_data(version_file, github_dump, abort=abort)
    code.set_module_var(version_file, "__version__", data["version"])
    code.set_module_var(version_file, "__hash__", (data["sha"] or "")[:7])
    return data["version"]


def get_environment(
    version_file: str | Path,
    github_dump: str | None = None,
    record_path: Path | None = None,
    abort: bool = True,
) -> jinja2.Environment:
    """returns a context object"""

    from urllib.parse import quote

    env = jinja2.Environment(autoescape=True)
    env.filters["urlquote"] = functools.partial(quote, safe="")
    env.globals = {
        "dir": dir,
        "len": len,
        "sorted": sorted,
        "reversed": reversed,
    }
    data = get_data(version_file, github_dump, record_path, abort)
    env.globals["ctx"] = _Context(**data)
    return env


def generate_build_record(record_path: Path, data: dict[str, Any]) -> Path:
    record_path.parent.mkdir(parents=True, exist_ok=True)
    with record_path.open("w") as fp:
        print("# autogenerate build file", file=fp)
        for key, value in sorted((data or {}).items()):
            value = f"'{value}'" if isinstance(value, str) else value
            print(f"{key} = {value}", file=fp)
    return record_path


# def process(
#     version_file: str | Path,
#     github_dump: str | None = None,
#     record: str | Path = "_build.py",
#     paths: str | Path | list[str | Path] | None = None,
#     fixers: dict[str, str] | None = None,
#     backup: Callable[[Path | str], None] | None = None,
#     abort: bool = True,
# ) -> dict[str, str | None]:
#     """get version from github_dump and updates version_file/paths
#
#     Args:
#         version_file (str, Path): path to a file with __version__ variable
#         github_dump (str): the os.getenv("GITHUB_DUMP") value
#         paths (str, Path): path(s) to files jinja2 processeable
#         fixers (dict[str,str]): fixer dictionary
#         record: set to True will generate a _build.py sibling of version_file
#
#     Returns:
#         str: the new version for the package
#
#     Example:
#         {'branch': 'beta/0.3.1',
#          'build': 0,
#          'current': '0.3.1',
#          'hash': 'c9e484a*',
#          'version': '0.3.1b0',
#          'runid': 0
#         }
#     """
#     from argparse import Namespace
#     from functools import partial
#     from urllib.parse import quote
#
#     from jinja2 import Environment
#
#     class Context(Namespace):
#         def items(self):
#             for name, value in self.__dict__.items():
#                 if name.startswith("_"):
#                     continue
#                 yield (name, value)
#
#     record_path = (Path(version_file).parent / record).absolute() if record else None
#     data = get_data(version_file, github_dump, record_path, abort)
#
#     if not backup:
#
#         def backup(_: Path | str) -> None:
#             pass
#
#     breakpoint()
#     # backup(version_file)
#
#     # set_module_var(version_file, "__version__", data["version"])
#     # set_module_var(version_file, "__hash__", (data["sha"] or "")[:7])
#
#     # env = Environment(autoescape=True)
#     # env.filters["urlquote"] = partial(quote, safe="")
#     # for path in list_of_paths(paths):
#     #     txt = replace(path.read_text(), fixers)
#     #     tmpl = env.from_string(txt)
#     #     backup(path)
#     #     path.write_text(tmpl.render(ctx=Context(**data)))
#     #
#     # if record_path:
#     #     generate_build_record(record_path, data)
#
#     return data
#
#
