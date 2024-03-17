#!/usr/bin/env python
from __future__ import annotations

import asyncio
import contextlib
import dataclasses as dc
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(cmd: Any, tee: Any = True, **kwargs):
    # https://stackoverflow.com/questions/2996887/how-to-replicate-tee-behavior-in-python-when-using-subprocess
    @dc.dataclass
    class RunOutput:
        returncode: int
        stdout: Any
        stderr: Any

    async def _stream_subprocess(cmd, quiet=False) -> RunOutput:
        exe = subprocess.list2cmdline(
            [cmd] if isinstance(cmd, str) else [str(c) for c in cmd]
        )
        p = await asyncio.create_subprocess_shell(
            exe,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )
        out: list[str] = []
        err: list[str] = []

        async def _read_stream(stream, sink, pipe, label=""):
            while line := await stream.readline():
                line = line.decode("utf-8")
                line = line[:-2] if line.endswith("\r\n") else line
                line = line[:-1] if line.endswith("\n") else line
                sink.append(line)
                if tee is True:
                    print(label, line, file=pipe)
                elif tee:
                    tee(line)

        tasks = [
            asyncio.create_task(_read_stream(p.stdout, out, sys.stdout, label="OUT:")),
            asyncio.create_task(_read_stream(p.stderr, err, sys.stderr, label="ERR:")),
        ]
        await asyncio.gather(*tasks)
        return RunOutput(await p.wait(), out, err)

    async def runme() -> RunOutput:
        task = asyncio.create_task(_stream_subprocess(cmd))
        return (await asyncio.gather(task))[0]

    result = asyncio.run(runme())
    if not result.returncode:
        return "\n".join(result.stdout)

    msg = [
        f"************* FAILED RUN (code {result.returncode}) *************",
        "STDOUT",
        *[f"|=  {line}" for line in result.stdout],
        "STDERR",
        *[f"|+  {line}" for line in result.stderr],
    ]
    raise RuntimeError("\n".join(msg))


def zextract(path: Path | str, items: list[str] | None = None) -> dict[str, Any]:
    """extracts from path (a zipfile/tarball) all data in a dictionary"""
    from tarfile import TarFile, is_tarfile
    from zipfile import ZipFile, is_zipfile

    path = Path(path)
    result = {}
    if is_tarfile(path):
        with TarFile.open(path) as tfp:
            for member in tfp.getmembers():
                fp = tfp.extractfile(member)
                if not fp:
                    continue
                result[member.name] = str(fp.read(), encoding="utf-8")
    elif is_zipfile(path):
        with ZipFile(path) as tfp:
            for zinfo in tfp.infolist():
                if items and zinfo.filename not in items:
                    continue
                with tfp.open(zinfo.filename) as fp:
                    result[zinfo.filename] = str(fp.read(), encoding="utf-8").replace(
                        "\r", ""
                    )

    return result


class Repo:
    def __init__(self, workdir):
        from toml import loads  # type: ignore

        self.workdir = workdir
        self.curdir = Path.cwd()
        self.gitdir = self.workdir / ".git"
        self.exe = "git"
        self.cfg = loads((self.workdir / "pyproject.toml").read_text())

    def __call__(self, cmd):
        cmds = cmd if isinstance(cmd, list) else [cmd]
        arguments = [self.exe]
        arguments.extend(
            [
                "--work-tree",
                str(self.workdir),
                "--git-dir",
                str(self.gitdir),
            ]
        )
        arguments.extend(str(c) for c in cmds)
        env = os.environ.copy()
        # env["GIT_DIR"] = str(self.workdir)
        # env["GIT_WORK_TREE"] = str(self.gitdir)
        return run(arguments, cwd=str(self.workdir), env=env)


# import pyproject_hooks._in_process._in_process
#
# import build.__main__
#
#
# def rm(path: Path):
#     from shutil import rmtree
#
#     if not path.exists():
#         return
#     if path.is_dir():
#         rmtree(path)
#     else:
#         path.unlink()
#
#
# def co(path: Path):
#     from subprocess import DEVNULL, call
#
#     call(["git", "co", str(path)], stderr=DEVNULL)
#
#
# def cleanup(workdir: Path):
#     rm(workdir / "dist")
#     rm(workdir / "src/hatch_ci/_build.py")
#     co(workdir / "TEMPLATE.md")
#     co(workdir / "src/hatch_ci/__init__.py")
#
#
# def create_sdist_env(
#     workdir: Path, builddir: Path, key: str
# ) -> tuple[list[str | None], dict[str, str]]:
#     (builddir / "xyz").mkdir(parents=True, exist_ok=True)
#     (builddir / "xyz-dist").mkdir(parents=True, exist_ok=True)
#     (builddir / "xyz" / "input.json").write_text(
#         json.dumps(
#             {
#                 "kwargs": {
#                     key: str((builddir / "xyz-dist").absolute()),
#                     "config_settings": {},
#                 },
#             }
#         )
#     )
#
#     cmd = [
#         Path(pyproject_hooks._in_process._in_process.__file__),
#         None,
#         (workdir / "build" / "xyz").absolute(),
#     ]
#     env = {"PEP517_BUILD_BACKEND": "hatchling.build"}
#     return [c if c is None else str(c) for c in cmd], env
#
#
# def run_inprocess(target: str, workdir: Path, builddir: Path, sdist: bool):
#     cmd, env = create_sdist_env(
#         workdir, builddir, key="sdist_directory" if sdist else "wheel_directory"
#     )
#     assert cmd[1] is None
#     cmd[1] = target
#
#     old = sys.argv[:]
#     with mock.patch.dict(os.environ, env):
#         sys.argv = [str(c) for c in cmd]
#         try:
#             pyproject_hooks._in_process._in_process.main()
#         finally:
#             sys.argv = old
#
@contextlib.contextmanager
def project(repo, uninstall=True):
    from toml import loads

    pyproject = repo.workdir / "tests" / "data" / "pyproject.toml"

    if "pyproject.toml" in repo(["status", "--porcelain"]):
        raise RuntimeError("pyproject.toml has modifications in it")
    name = loads((repo.workdir / "pyproject.toml").read_text())["project"]["name"]
    try:
        shutil.copyfile(pyproject, repo.workdir / "pyproject.toml")
        run(["python", "-m" "pip", "install", "-v", "-e", repo.workdir])
        yield
    finally:
        repo(["checkout", repo.workdir / "pyproject.toml"])
        if uninstall:
            run(["python", "-m" "pip", "uninstall", "-v", "--yes", name])


def build(repo):
    """build the sdist and wheel package"""
    with project(repo):
        run(["python", "-m" "build", repo.workdir])


def test_e2e(repo):
    """runs the e2e tests"""
    with project(repo):
        cmd = ["python", "-m", "pytest", "-vvs", repo.workdir / "tests" / "test_e2e.py"]
        print(" ".join(str(c) for c in cmd))  # noqa: T201
        run(cmd)


def install(repo):
    """install a local version of hatch-ci to run tests"""
    with project(repo, uninstall=False):
        pass


def package(repo):
    """create package for deployment"""
    install(repo)
    run(["python", "-m", "build", "-n", "."])
    wheel = next((repo.workdir / "dist").glob("*.whl"))
    out = zextract(wheel)
    print("== CHECKS! ==")  # noqa: T201
    content = out[next(key for key in out if "METADATA" in key)]
    for line in content.split("\n"):
        if "[Build]" in line or "[codecov]" in line:
            print(f"| {line}")  # noqa: T201


def uninstall(repo):
    """cleanup build artifacts"""
    name = repo.cfg["project"]["name"]
    run(["python", "-m" "pip", "uninstall", "-v", "--yes", name])


def dist_clean(repo):
    """restore the environemnt"""
    pass


COMMANDS = {
    "build": build,
    "package": package,
    "e2e": test_e2e,
    "install": install,
    "uninstall": uninstall,
    "dist-clean": dist_clean,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    def getdoc(fn):
        return (
            fn.__doc__.strip().partition("\n")[0] if fn.__doc__ else "no help available"
        )

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        txt = "\n".join(f"  {cmd} - {getdoc(fn)}" for cmd, fn in COMMANDS.items())
        print(  # noqa: T201
            f"""\
make.py <command> {{arguments}}

Commands:

{txt}
""",
            file=sys.stderr,
        )
        sys.exit()

    workdir = Path(__file__).parent
    COMMANDS[sys.argv[1]](Repo(workdir))
    pass
    # workdir = Path(os.environ.get("SOURCE_DIR", Path(__file__).parent)).absolute()
    # builddir = workdir / "build"
    #
    # os.chdir(workdir)
    # mode = sys.argv[1]
    # if mode in {"clean", "clean-all", "build", "sdist", "wheel"}:
    #     cleanup(workdir)
    #     if mode in {"clean-all", "sdist", "build_wheel"}:
    #         rm(builddir / "xyz")
    #         rm(builddir / "xyz-dist")
    # else:
    #     raise NotImplementedError(f"mod [{mode}] not implemented")
    #
    # if mode == "build":
    #     build.__main__.main(["."], "python -m build")
    # elif mode == "sdist":
    #     run_inprocess("build_sdist", workdir, builddir, sdist=True)
    #     print(f" results under -> {builddir}")
    # elif mode == "wheel":
    #     run_inprocess("build_wheel", workdir, builddir, sdist=False)
    #     print(f" results under -> {builddir}")
