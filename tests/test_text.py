from hatch_ci import text


def test_indent():
    txt = """\
     An unusually complicated text
    with un-even indented lines
   that make life harder
"""
    assert (
        text.indent(txt, pre="..")
        == """\
..  An unusually complicated text
.. with un-even indented lines
..that make life harder
"""
    )


def test_indent_another():
    txt = """
    This is a simply
       indented text
      with some special
         formatting
"""
    expected = """
..This is a simply
..   indented text
..  with some special
..     formatting
"""

    found = text.indent(txt[1:], "..")
    assert f"\n{found}" == expected


def test_lstrip():
    assert text.lstrip("/a/b/c/d/e", "/a/b") == "/c/d/e"
