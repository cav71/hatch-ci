import pytest

from hatch_ci import code


def test_get_module_var(tmp_path):
    "pulls variables from a file"
    path = tmp_path / "in0.txt"
    path.write_text(
        """
# a test file
A = 12
B = 3+5
C = "hello"
# end of test
"""
    )
    assert 12 == code.get_module_var(path, "A")
    assert "hello" == code.get_module_var(path, "C")
    pytest.raises(code.ValidationError, code.get_module_var, path, "B")
    pytest.raises(code.MissingVariableError, code.get_module_var, path, "X1")

    path.write_text(
        """
# a test file
A = 12
B = 3+5
C = "hello"
C = "hello2"
# end of test
"""
    )
    pytest.raises(code.ValidationError, code.get_module_var, path, "C")


def test_set_module_var(tmp_path):
    "handles set_module_var cases"
    path = tmp_path / "in2.txt"

    path.write_text(
        """
# a fist comment line
__hash__ = "4.5.6"
# end of test
"""
    )

    version, txt = code.set_module_var(path, "__version__", "1.2.3")
    assert not version
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "1.2.3"
""".rstrip()
    )

    version, txt = code.set_module_var(path, "__version__", "6.7.8")
    assert version == "1.2.3"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "4.5.6"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )

    version, txt = code.set_module_var(path, "__hash__", "9.10.11")
    assert version == "4.5.6"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "9.10.11"
# end of test
__version__ = "6.7.8"
""".rstrip()
    )

    version, txt = code.set_module_var(path, "__version__", "9.10.11")
    assert version == "6.7.8"
    assert (
        txt.rstrip()
        == """
# a fist comment line
__hash__ = "9.10.11"
# end of test
__version__ = "9.10.11"
""".rstrip()
    )


def test_set_module_var_empty_file(tmp_path):
    "check set_module_var creates a new file if not present"
    path = tmp_path / "in1.txt"

    assert not path.exists()
    code.set_module_var(path, "__version__", "1.2.3")

    assert path.exists()
    path.write_text("# a fist comment line\n" + path.read_text().strip())

    code.set_module_var(path, "__hash__", "4.5.6")
    assert (
        path.read_text().strip()
        == """
# a fist comment line
__version__ = "1.2.3"
__hash__ = "4.5.6"
""".strip()
    )
