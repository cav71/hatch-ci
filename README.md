# hatch-ci

[![PyPI version](https://img.shields.io/pypi/v/hatch-ci.svg?color=blue)](https://pypi.org/project/hatch-ci)
[![Python versions](https://img.shields.io/pypi/pyversions/hatch-ci.svg)](https://pypi.org/project/hatch-ci)
[![Build](https://github.com/cav71/hatch-ci/actions/workflows/master.yml/badge.svg)](https://github.com/cav71/hatch-ci/actions)
[![Coverage](https://codecov.io/gh/cav71/hatch-ci/branch/master/graph/badge.svg)](Coverage)

[![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

-----

This provides a plugin for [Hatch](https://github.com/pypa/hatch) to help in delivering wheel
to [PyPi](https://pypi.org) using a CI/CD system.

> **NOTE**: this is heavily inspired from  [hatch-vcs](https://github.com/ofek/hatch-vcs)


**Table of Contents**

- [Global dependency](#global-dependency)
- [Version source](#version-source)
  - [Version source options](#version-source-options)
  - [Version source environment variables](#version-source-environment-variables)
- [Build hook](#build-hook)
  - [Build hook options](#build-hook-options)
  - [Editable installs](#editable-installs)
- [Metadata hook](#metadata-hook)
  - [Metadata hook options](#metadata-hook-options)
    - [URLs](#urls)
  - [Example](#example)
- [License](#license)

## Global dependency

Ensure `hatch-ci` is defined within the `build-system.requires` field in your `pyproject.toml` file.

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"
```

## Version source

The [version source plugin](https://hatch.pypa.io/latest/plugins/version-source/reference/) name is `vcs`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.version]
    source = "vcs"
    ```

- ***hatch.toml***

    ```toml
    [version]
    source = "vcs"
    ```

### Version source options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `tag-pattern` | `str` | see [code](https://github.com/pypa/setuptools_scm/blob/v6.4.0/src/setuptools_scm/config.py#L13) | A regular expression used to extract the version part from VCS tags. The pattern needs to contain either a single match group, or a group named `version`, that captures the actual version information. |
| `fallback-version` | `str` | | The version that will be used if no other method for detecting the version is successful. If not specified, unsuccessful version detection will raise an error. |
| `raw-options` | `dict` | | A table of [`setuptools-scm` parameters](https://github.com/pypa/setuptools_scm#configuration-parameters) that will override any of the options listed above. The `write_to` and `write_to_template` parameters are ignored. |

### Version source environment variables

- `SETUPTOOLS_SCM_PRETEND_VERSION`: When defined and not empty, it's used as the primary source for the version, in which case it will be an unparsed string.

## Build hook

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/reference/) name is `vcs`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.build.hooks.vcs]
    version-file = "_version.py"
    ```

- ***hatch.toml***

    ```toml
    [build.hooks.vcs]
    version-file = "_version.py"
    ```

Building or installing when the latest tag is ``v1.2.3`` will generate the file

- ***_version.py***

    ```python
    # coding: utf-8
    # file generated by setuptools_scm
    # don't change, don't track in version control
    __version__ = version = '1.2.3'
    __version_tuple__ = version_tuple = (1, 2, 3)
    ```

### Build hook options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `version-file` | `str` | ***REQUIRED*** | The relative path to the file that gets updated with the current version. |
| `template` | `str` | | The template used to overwrite the `version-file`. See the [code](https://github.com/pypa/setuptools_scm/blob/v6.4.0/src/setuptools_scm/__init__.py#L30-L39) for the default template for each file extension. |

### Editable installs

The version file is only updated upon install or build. Thus the version number in an [editable install](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs) (Hatch's [dev mode](https://hatch.pypa.io/latest/config/build/#dev-mode)) will be incorrect if the version changes and the project is not rebuilt. An unsupported workaround for keeping the version number up-to-date can be found at [hatch-vcs-footgun-example](https://github.com/maresb/hatch-vcs-footgun-example).

## Metadata hook

**Note:** only Git is supported

The [metadata hook plugin](https://hatch.pypa.io/latest/plugins/metadata-hook/reference/) is for inserting VCS data (currently the commit hash) into metadata fields other than `version`. Its name is `vcs`.

- ***pyproject.toml***

    ```toml
    [tool.hatch.metadata.hooks.vcs]
    ```

- ***hatch.toml***

    ```toml
    [metadata.hooks.vcs]
    ```

### Metadata hook options

#### URLs

The `urls` option is equivalent to [`project.urls`](https://hatch.pypa.io/latest/config/metadata/#urls) except that each URL supports [context formatting](https://hatch.pypa.io/latest/config/context/) with the following fields:

- `commit_hash` - the latest commit hash

Be sure to add `urls` to [`project.dynamic`](https://hatch.pypa.io/latest/config/metadata/#dynamic):

- ***pyproject.toml***

    ```toml
    [project]
    dynamic = [
      "urls",
    ]
    ```

### Example

- ***pyproject.toml***

    ```toml
    [tool.hatch.metadata.hooks.vcs.urls]
    Homepage = "https://www.example.com"
    source_archive = "https://github.com/org/repo/archive/{commit_hash}.zip"
    ```

- ***hatch.toml***

    ```toml
    [metadata.hooks.vcs.urls]
    Homepage = "https://www.example.com"
    source_archive = "https://github.com/org/repo/archive/{commit_hash}.zip"
    ```

## Migration tips

If you are migrating from [setuptools](https://setuptools.pypa.io), you may want access to
the version without performing a full build.

By default, `python -m setuptools_scm` will display the version and perform any side-effects
like writing to a file. `hatch` separates these functions.

### Display version

`hatch version` will print the version to the terminal without modifying the source directory.

```console
$ hatch version
23.0.0.dev17+g462372ba
```

### Write version to file

If `version-file` is defined, you can write it to the source directory with the `build` command,
using the `--hooks-only` flag to modify the source tree but skip creation of sdists or wheels.

```console
$ hatch build --hooks-only
$ cat package/_version.py
# file generated by setuptools_scm
# don't change, don't track in version control
__version__ = version = '23.0.0.dev17+g462372ba'
__version_tuple__ = version_tuple = (23, 0, 0, 'dev17', 'g462372ba')
```

## License

`hatch-vcs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
