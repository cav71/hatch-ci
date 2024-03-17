from __future__ import annotations


def indent(txt: str, pre: str = " " * 2) -> str:
    """simple text indentation"""

    from textwrap import dedent

    txt = dedent(txt)
    if txt.endswith("\n"):
        last_eol = "\n"
        txt = txt[:-1]
    else:
        last_eol = ""

    result = pre + txt.replace("\n", "\n" + pre) + last_eol
    return result if result.strip() else result.strip()


def lstrip(txt: str, ending: str | list[str]) -> str:
    endings = ending if isinstance(ending, list) else [ending]
    for left in endings:
        txt = txt[len(left) :] if txt.startswith(left) else txt
    return txt
