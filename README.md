# hatch-ci

[![PyPI version](https://img.shields.io/pypi/v/hatch-ci.svg?color=blue)](https://pypi.org/project/hatch-ci)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-ci.svg)](https://pypi.org/project/hatch-ci)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

[![Build](https://github.com/cav71/hatch-ci/actions/workflows/master.yml/badge.svg)](https://github.com/cav71/hatch-ci/actions/runs/0)
[![codecov](https://codecov.io/gh/cav71/hatch-ci/branch/master/graph/badge.svg?token=521FB9K5KT)](https://codecov.io/gh/cav71/hatch-ci/branch/master)

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](Black)
[![Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


## Introduction
This is a [hatch-vcs](https://github.com/ofek/hatch-vcs) heavily inspired plugin: it captures values from
the build environment (eg. github) and it uses to modify source files during 
the wheel build phase.

This is a typical project (let's call it foobar):

```
└── foobar-project
    ├── pyproject.toml
    └── src
        └── foobar
            └── __init__.py (this contains __version__ and 
                             __hash__ variables that will be 
                             updated during the build)
```

Issuing the:
``
python -m build .
``

In the simplest way all you have to do is setting up the pyproject.toml as:
```text
[build-system]
requires = ["hatchling", "hatch-ci"]
build-backend = "hatchling.build"

[project]
dynamic = ["version"]

[tool.hatch.version]
version-file = "src/package/__init__.py"
```

### wheel version
During the wheel build the version is dynamically updated with information taken from
the `version-file` field (see "[Version source options](#version-source-options)").

Two variables will be overwritten/modified in `version-file`: the **__version__** 
containing the semgrep version and **__hash__** with the git commit for the build.

The version information is augmented with:
- a **bNNN** build number in creating the package foobar-1.0.0bNNNN (this can be sent to [PyPi](https://pypi.org))
- if there's a tag v1.0.0 on the repo, it will build foobar-1.0.0 release (this can be sent to [PyPi](https://pypi.org))

The last two steps are mean to be managed in a CI/CD system (github at the moment), to ensure *hands-off* releases.

In essence this pluging:
- manages the version information
- allows version replacement in text files using build information



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

This will enable the hatch-ci pluging:

- ***pyproject.toml***

    ```toml
    [project]
    ..
    dynamic = ["version"]  # this rerieves the version dynamically
    ..

    ```

### Version source options

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    source = "ci"  # this pulls the version using the hatch-ci hook

    # this will put/update __version__ and __hash__ info in version-file
    version-file = "src/hatch_ci/__init__.py"

    # these files will be jinja2 processed, the environment will
    # contains variables as: branch, build, current, ref, runid, 
    # sha, version, workflow etc.
    paths = [ "README.md" ]
    
    # the listed paths will undergo replacement before jinja2 processing and
    # the variables 'a' & 'b' listed below wil be replaced with ctx attributes.
    fixers = [
        { 'a': '{ctx.workflows}' },
        { 'd': '{ctx.branch}' }
    ]
    ```
    The complete list of attributes is available here [TEMPLATE.md](TEMPLATE.md).

| Option | Type | Default | Description                                          |
| --- | --- |---------|------------------------------------------------------|
| `version-file` | `str` | None    | A file where to write __version__/__hash__ variables |
| `paths` | `list[str]|str` | None | A list of paths to process |
| `fixers` | `list[dict[str,str]]` | None | A list of dict, each key is a string to replace with the value |


## License

`hatch-ci` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.