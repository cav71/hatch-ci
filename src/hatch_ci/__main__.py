from __future__ import annotations

import argparse
import functools
import logging
import sys
from typing import Any

from . import tools

log = logging.getLogger(__name__)


def parse_args(args: str | None = None, testmode: bool = False) -> dict[str, Any]:
    """parses args from the command line

    Args:
        args: command line arguments or None to pull from sys.argv
        testmode: internal flag, if set will not SystemExit but will
                  raises tools.AbortExecution
    """

    class F(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(formatter_class=F, description=__doc__)

    parser.add_argument("-n", "--dry-run", dest="dryrun", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")

    options = parser.parse_args(args)

    def error(message, explain="", hint="", parser=None, testmode=False):
        out = []
        if parser:
            out.extend(tools.indent(parser.format_usage()).split("\n"))
        if message:
            out.extend(tools.indent(message).split("\n"))
        if explain:
            out.append("reason:")
            out.extend(tools.indent(explain).split("\n"))
        if hint:
            out.append("hint:")
            out.extend(tools.indent(hint).split("\n"))

        if testmode:
            raise tools.AbortExecution(message, explain, hint)
        else:
            print()  # noqa: T201
            print("\n".join(out), file=sys.stderr)  # noqa: T201
            raise SystemExit(2)

    options.error = functools.partial(error, parser=parser, testmode=testmode)

    logging.basicConfig(
        format="%(levelname)s:%(name)s:(dry-run) %(message)s"
        if options.dryrun
        else "%(levelname)s:%(name)s:%(message)s",
        level=logging.DEBUG if options.verbose else logging.INFO,
    )

    for d in [
        "verbose",
    ]:
        delattr(options, d)
    return options.__dict__


def run():
    pass


def main():
    run(**parse_args())


if __name__ == "__main__":
    main()
