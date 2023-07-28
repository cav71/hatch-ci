# hatch-ci

[![PyPI version](https://img.shields.io/pypi/v/hatch-ci.svg?color=blue)](https://pypi.org/project/hatch-ci)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-ci.svg)](https://pypi.org/project/hatch-ci)
[![Build](https://github.com/cav71/hatch-ci/actions/workflows/master.yml/badge.svg)](https://github.com/cav71/hatch-ci/actions)
[![Coverage](https://codecov.io/gh/cav71/hatch-ci/branch/master/graph/badge.svg)](Coverage)

[![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

-----

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

- ***hatch.toml***

    ```toml
    [version]
    source = "ci"
    ```

### Version source options

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    version-file = "src/hatch_ci/__init__.py"
    ```

- ***hatch.toml***

    ```toml
    [build.version]
    version-file = "src/hatch_ci/__init__.py"
    ```


| Option | Type | Default | Description                                          |
| --- | --- |---------|------------------------------------------------------|
| `version-file` | `str` | None    | A file where to write __version__/__hash__ variables |


## License

`hatch-ci` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
