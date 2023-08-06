# hatch-ci

[![PyPI version](https://img.shields.io/pypi/v/hatch-ci.svg?color=blue)](https://pypi.org/project/hatch-ci)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-ci.svg)](https://pypi.org/project/hatch-ci)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

[![Build](https://github.com/cav71/hatch-ci/actions/workflows/master.yml/badge.svg)](https://github.com/cav71/hatch-ci/actions/workflows/master.yml)
[![Coverage](https://codecov.io/gh/cav71/hatch-ci/branch/master/graph/badge.svg)](https://app.codecov.io/gh/cav71/hatch-ci/tree/master)

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](Black)
[![Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


This provides a plugin to [Hatch](https://github.com/pypa/hatch) leveraging a CI/CD system (github at the moment)
to deliver packages to [PyPi](https://pypi.org).

> **NOTE**: this is heavily inspired from  [hatch-vcs](https://github.com/ofek/hatch-vcs)


**Table of Contents**

- [Global dependency](#global-dependency)
- [Version source](#version-source)
  - [Version source options](#version-source-options)
- [License](#license)

## Global dependency

Ensure `hatch-ci` is defined within the `build-system.requires` field in your `pyproject.toml` file.

```toml
[build-system]
requires = ["hatchling", "hatch-ci"]
build-backend = "hatchling.build"
```

## Version source

The [version source plugin](https://hatch.pypa.io/latest/plugins/version-source/reference/) name is `ci`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    source = "ci"
    ```

### Version source options

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    source = "ci"

    # this will be updated with __version__ and __hash__ info
    version-file = "src/hatch_ci/__init__.py"

    # the files here will be jinja2 processed dynamicaly at build time
    paths = [ "README.md" ]
    
    # the paths will have the strings 'a' & 'b' replaced before
    # jinja2 processing
    fixers = [
        { 'a': '{ctx.workflows}' },
        { 'd': '{ctx.branch}' }
    ]
    ```

| Option | Type | Default | Description                                          |
| --- | --- |---------|------------------------------------------------------|
| `version-file` | `str` | None    | A file where to write __version__/__hash__ variables |
| `paths` | `list[str]|str` | None | A list of paths to process |
| `fixers` | `list[dict[str,str]]` | None | A list of dict, each key is a string to replace with the value |


## License

`hatch-ci` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
