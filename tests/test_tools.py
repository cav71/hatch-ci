# ruff: noqa: E501
import pytest

from hatch_ci import code, tools

# this is the output from ${{ toJson(github) }}
GITHUB = {
    "beta": {
        "ref": "refs/heads/beta/0.3.10",
        "sha": "507c657056d1a66520ec6b219a64706e70b0ff15",
        "run_number": "98",
        "run_id": "5904313530",
    },
    "release": {
        "ref": "refs/tags/release/0.3.9",
        "sha": "2b79a3669cd06e21741f6ee7a271903482344e76",
        "run_number": "22",
        "run_id": "5789585760",
    },
    "master": {
        "ref": "refs/heads/master",
        "sha": "9df889992f422a62cdd3ced41323eaba6e855ae3",
        "run_number": "257",
        "run_id": "5789314202",
    },
}


def splitter(txt):
    result = {}
    for line in txt.split("\n"):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if len(kv := line.split("=")) == 2:
            result[kv[0].strip()] = kv[1].strip()
    return result


#
#
# def T(txt):
#     from textwrap import dedent
#
#     txt = dedent(txt)
#     if txt.startswith("\n"):
#         txt = txt[1:]
#     return txt
#
#
# def T1(txt):
#     return T(txt).rstrip("\n")


def test_list_of_paths():
    from pathlib import Path

    assert tools.list_of_paths([]) == []
    assert tools.list_of_paths("hello") == [Path("hello")]
    assert tools.list_of_paths(["hello", Path("world")]) == [
        Path("hello"),
        Path("world"),
    ]


def test_replace():
    fixers = {
        "abc": "def",
    }
    assert tools.replace("abcdef abc123", fixers) == "defdef def123"
    fixers = {
        "re:([ab])cde": "x\\1",
    }
    assert tools.replace("acde bcde123", fixers) == "xa xb123"

    fixers = {
        # for the github actions
        "re:(https://github.com/.+/actions/workflows/)(master)(.yml/badge.svg)": "\\1{{ ctx.workflow }}\\3",
        "re:(https://github.com/.+/actions)/(workflows/)(master.yml)(?!/)": "\\1/runs/{{ ctx.runid }}",
        # for the codecov part
        "re:(https://codecov.io/gh/.+/tree)/master(/graph/badge.svg[?]token=.+)": "\\1/{{ ctx.branch|urlquote }}\\2",
        "re:(https://codecov.io/gh/.+/tree)/master(?!/)": "\\1/{{ ctx.branch|urlquote }}",
    }

    txt = "https://github.com/cav71/setuptools-github/actions/workflows/master.yml/badge.svg"
    expected = "https://github.com/cav71/setuptools-github/actions/workflows/{{ ctx.workflow }}.yml/badge.svg"
    assert tools.replace(txt, fixers) == expected

    txt = "https://github.com/cav71/setuptools-github/actions/workflows/master.yml"
    expected = "https://github.com/cav71/setuptools-github/actions/runs/{{ ctx.runid }}"
    assert tools.replace(txt, fixers) == expected

    txt = "https://codecov.io/gh/cav71/setuptools-github/tree/master/graph/badge.svg?token=RANDOM123"
    expected = "https://codecov.io/gh/cav71/setuptools-github/tree/{{ ctx.branch|urlquote }}/graph/badge.svg?token=RANDOM123"
    assert tools.replace(txt, fixers) == expected

    txt = "https://codecov.io/gh/cav71/setuptools-github/tree/master"
    expected = (
        "https://codecov.io/gh/cav71/setuptools-github/tree/{{ ctx.branch|urlquote }}"
    )
    assert tools.replace(txt, fixers) == expected


def test_bump_version():
    "bump version test"
    assert tools.bump_version("0.0.1", "micro") == "0.0.2"
    assert tools.bump_version("0.0.2", "micro") == "0.0.3"
    assert tools.bump_version("0.0.2", "minor") == "0.1.0"
    assert tools.bump_version("1.2.3", "major") == "2.0.0"
    assert tools.bump_version("1.2.3", "release") == "1.2.3"


def test_update_version_master(git_project_factory):
    "test the update_version processing on the master branch"

    repo = git_project_factory().create("1.2.3")
    assert code.get_module_var(repo.initfile) == "1.2.3"

    # verify nothing has changed
    assert "1.2.3" == tools.update_version(repo.initfile, abort=False)
    assert code.get_module_var(repo.initfile) == "1.2.3"
    assert (
        code.get_module_var(repo.initfile, "__hash__")
        == repo(["rev-parse", "HEAD"])[:7]
    )

    assert "1.2.3" == tools.update_version(repo.initfile, GITHUB["master"], abort=False)
    assert code.get_module_var(repo.initfile) == "1.2.3"
    assert code.get_module_var(repo.initfile, "__hash__") == GITHUB["master"]["sha"][:7]


def test_update_version_beta(git_project_factory):
    "test the update_version processing on the master branch"

    repo = git_project_factory().create("0.3.10")
    assert code.get_module_var(repo.initfile) == "0.3.10"
    assert repo.branch() == "master"

    # branch
    repo.branch("beta/0.3.10", "master")
    assert repo.branch() == "beta/0.3.10"

    assert tools.update_version(repo.initfile, abort=False)
    assert code.get_module_var(repo.initfile) == "0.3.10b0"
    assert (
        code.get_module_var(repo.initfile, "__hash__")
        == repo(["rev-parse", "HEAD"])[:7]
    )
    repo.revert(repo.initfile)

    assert code.get_module_var(repo.initfile) == "0.3.10"
    assert tools.update_version(repo.initfile, GITHUB["beta"], abort=False)
    assert code.get_module_var(repo.initfile) == "0.3.10b98"
    assert code.get_module_var(repo.initfile, "__hash__") == "507c657"
    repo.revert(repo.initfile)

    # wrong branch
    repo.branch("beta/0.0.2", "master")
    assert repo.branch() == "beta/0.0.2"
    pytest.raises(
        tools.InvalidVersionError, tools.update_version, repo.initfile, abort=False
    )

    github_dump = GITHUB["beta"].copy()
    github_dump["ref"] = "refs/heads/beta/0.0.2"
    pytest.raises(
        tools.InvalidVersionError,
        tools.update_version,
        repo.initfile,
        github_dump,
        abort=False,
    )


def test_update_version_release(git_project_factory):
    repo = git_project_factory().create("0.3.9")
    assert code.get_module_var(repo.initfile) == "0.3.9"

    # branch
    repo.branch("beta/0.3.9", "master")
    assert repo.branch() == "beta/0.3.9"

    path = repo.workdir / "hello.txt"
    path.write_text("hello world\n")
    repo.commit(path, "initial")

    repo(["tag", "release/0.3.9", repo(["rev-parse", "HEAD"])[:7]])

    assert (
        tools.update_version(repo.initfile, GITHUB["release"], abort=False) == "0.3.9"
    )
    assert code.get_module_var(repo.initfile) == "0.3.9"
    assert (
        code.get_module_var(repo.initfile, "__hash__") == GITHUB["release"]["sha"][:7]
    )
    repo.revert(repo.initfile)


def test_get_environment(git_project_factory):
    repo = git_project_factory().create("0.3.9")
    assert repo.branch() == "master"
    assert code.get_module_var(repo.initfile) == "0.3.9"

    env = tools.get_environment(repo.initfile, None, None)
    out = (
        env.from_string("""
{% for key, value in sorted(ctx.items()) -%}
{{key}} = {{value}}
{% endfor %}
""")
        .render()
        .strip()
    )

    found = splitter(out)
    assert found == {
        "branch": "master",
        "build": "0",
        "current": "0.3.9",
        "ref": "refs/heads/master",
        "runid": "0",
        "sha": repo.head.target.hex,
        "version": "0.3.9",
        "workflow": "master",
    }

    repo.branch("beta/0.3.9", "master")
    assert repo.branch() == "beta/0.3.9"


def test_generate_build_record(tmp_path):
    dst = tmp_path / "abc.def"

    tools.generate_build_record(dst, {"a": 1, "b": 2})
    assert splitter(dst.read_text()) == {"a": "1", "b": "2"}


# def test_process(git_project_factory):
#
#     # generate the project
#     repo = git_project_factory().create("0.3.10")
#     assert repo.initfile.read_text() == '__version__ = "0.3.10"\n'
#
#     record = repo.initfile.parent / "_build.py"
#     assert not record.exists()
#
#     # we generate the build using a GITHUB_DUMP variable
#     tools.process(repo.initfile, json.dumps(GITHUB["beta"]), record)
#
#     assert repo.initfile.read_text() == f"""
# __version__ = "0.3.10b98"
# __hash__ = "{GITHUB['beta']['sha'][:7]}"
# """.strip()
#
#     assert record.read_text() == """
# # autogenerate build file
# branch = 'beta/0.3.10'
# build = '98'
# current = '0.3.10'
# ref = 'refs/heads/beta/0.3.10'
# runid = '5904313530'
# sha = '507c657056d1a66520ec6b219a64706e70b0ff15'
# version = '0.3.10b98'
# workflow = 'beta'
# """.lstrip()
#
#
# def test_process_fixers(git_project_factory):
#     def write_tfile(tfile):
#         tfile.write_text(
#             """
# {% for k, v in ctx.items() | sort -%}
# Key[{{k}}] = {{v}}
# {% endfor %}
# """
#         )
#         return tfile
#
#     repo = git_project_factory().create("1.2.3")
#
#     # tfile won't appear in the repo.status() because is untracked
#     tfile = write_tfile(repo.workdir / "test.txt")
#
#     data = tools.process(repo.initfile, None, "_build.py", tfile)
#
#     assert data["sha"][-1] != "*"
#
#     assert (
#         tfile.read_text()
#         == f"""
# Key[branch] = master
# Key[build] = 0
# Key[current] = 1.2.3
# Key[ref] = {data['ref']}
# Key[runid] = 0
# Key[sha] = {data['sha']}
# Key[version] = 1.2.3
# Key[workflow] = master
# """
#     )
#
#     # clean and switch to new branch
#     repo.revert(repo.initfile)
#     (repo.initfile.parent / "_build.py").unlink()
#
#     write_tfile(tfile)
#     repo.branch("beta/1.2.3", "master")
#
#     data = tools.process(repo.initfile, None, "_build.py", tfile)
#     assert data["sha"][-1] != "*"
#
#     assert (
#         tfile.read_text()
#         == f"""
# Key[branch] = beta/1.2.3
# Key[build] = 0
# Key[current] = 1.2.3
# Key[ref] = {data['ref']}
# Key[runid] = 0
# Key[sha] = {data['sha']}
# Key[version] = 1.2.3b0
# Key[workflow] = beta
# """
#     )
