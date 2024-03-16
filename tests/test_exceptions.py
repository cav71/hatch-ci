from hatch_ci import exceptions


def test_abort_exception():
    "test the AbortExecution exception"
    a = exceptions.AbortExecutionError(
        "a one-line error message",
        """
        A multi line
          explanation of
           what happened
         with some detail
    """,
        """
    Another multiline hint how
      to fix the issue
    """,
    )

    assert a.message == "a one-line error message"
    assert (
        f"\n{a.explain}\n"
        == """
A multi line
  explanation of
   what happened
 with some detail
"""
    )
    assert (
        f"\n{a.hint}\n"
        == """
Another multiline hint how
  to fix the issue
"""
    )

    assert (
        f"\n{a!s}\n"
        == """
a one-line error message
  A multi line
    explanation of
     what happened
   with some detail
hint:
  Another multiline hint how
    to fix the issue
"""
    )

    a = exceptions.AbortExecutionError("hello world")
    assert a.message == "hello world"
    assert a.explain == ""
    assert a.hint == ""
    assert str(a) == "hello world"
