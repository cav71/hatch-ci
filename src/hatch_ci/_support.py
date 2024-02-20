# This file is not mean to be used!!!
# ONLY FOR INTERNAL DEBUG

# wraps each method in a derived class of:
# - VersionSourceInterface
# - BuildHookInterface
# etc.

# wraps this:
# site-packages\pyproject_hooks\_impl.py ->
# def _call_hook(self, hook_name, kwargs):
#   ...
#   from hatch_ci._support import tracer
#   with tracer.decorator(_in_proc_script_path)() as script:

# change the OUTPUT below
from __future__ import annotations

import functools
import inspect
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

OUTPUT = None  # eg. r"C:\Users\antonio\Projects\github\hatch-ci\NOTES.txt"


def is_scm(path: Path) -> str:
    return "<git>" if (Path(path) / ".git").exists() else "<plain>"


def jformat(data: Any, pre: str) -> str:
    return json.dumps(data, indent=2, sort_keys=True).replace(
        "\n", f"\n{' ' * len(pre)}"
    )


class Tracer:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else None

    def decorator(self, fn):
        if fn.__name__ == "_in_proc_script_path":
            return self.wraps__in_proc_script_path(fn)
        else:
            return self.wraps_interface(fn)

    def append(self, txt):
        if not self.path:
            return
        with self.path.open("a") as fp:
            fp.write(txt.getvalue() if hasattr(txt, "getvalue") else txt)

    def wraps__in_proc_script_path(self, fn):
        # this is mean to wrap the _in_proc_script_path function
        @functools.wraps(fn)
        def _fn(*args, **kwargs):
            # ok, looking to wrap _call_hook in _impl.py
            frames = [
                f
                for f in inspect.getouterframes(inspect.currentframe())
                if "_impl.py" in f.filename and f.function == "_call_hook"
            ]
            if len(frames) != 1:
                raise RuntimeError("cannot find _call_hook in _impl.py frame")
            variables = frames[0].frame.f_locals

            if not self.path:
                fp = io.StringIO()
                print("", file=fp)
                print(f"[pid={os.getpid()}]", file=fp)
                print(f"<hook> '{variables['hook_name']}'", file=fp)
                scm = (
                    "<git>"
                    if (Path(variables["self"].source_dir) / ".git").exists()
                    else "<plain>"
                )
                print(
                    f"  cwd (self.source_dir): {variables['self'].source_dir} {scm}",
                    file=fp,
                )
                print(f"  kwargs: {variables['kwargs']}", file=fp)
                print(f"  extra_environ: {variables['extra_environ']}", file=fp)
                print("  input.json:", file=fp)
                pre = "  input.json: "
                print(f"{pre}{jformat(variables['hook_input'], pre=pre)}", file=fp)
                self.append(fp)

            return fn(*args, **kwargs)

        return _fn

    def wraps_interface(self, method):
        # a method decorator
        # you should wrap methods of subclasses of:
        # - VersionSourceInterface
        # - BuildHookInterface
        # etc.
        @functools.wraps(method)
        def _fn(slf, *args, **kwargs):
            if self.path:
                fp = io.StringIO()
                print("", file=fp)
                print(f"[pid={os.getpid()}] {sys.argv=}", file=fp)
                print(
                    f"!callback! '{method.__name__}' {slf.__class__.__name__}", file=fp
                )
                print(f"  self.root: {slf.root} {is_scm(slf.root)}", file=fp)
                print(f"  config: {jformat(slf.config, '  config: ')}", file=fp)
                self.append(fp)
            return method(slf, *args, **kwargs)

        return _fn if self.path else method


tracer = Tracer()  # r"C:\Users\antonio\Projects\github\hatch-ci\NOTES.txt")
