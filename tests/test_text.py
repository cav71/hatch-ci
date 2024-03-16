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
