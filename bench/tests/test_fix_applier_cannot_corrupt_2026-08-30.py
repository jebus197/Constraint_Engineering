"""A fix that would leave the target unparseable must not be applied.

Found by the fix-efficacy sweep on 2026-08-30. `_apply_fix_to_source` matched
SEARCH text as a RAW SUBSTRING, so a block whose first line lost its indentation
matched INSIDE the indentation of the real line. The replacement was spliced in
and the original line survived.

Measured on exp42 C0051 in bench/cdsfl_registry/composer.py, whose source is:

    def _block_is_hard(block: str) -> bool:
        \"\"\"Determine if a directive block contains HARD constraint content.\"\"\"

The model's SEARCH began at the docstring with no indent, matched four
characters into the line, and produced a file with the `def` line duplicated.

12 of 313 archived fixes were corrupted this way. Every one is the applier's
doing, not the model's, and each was then judged by the next step as though the
wreckage were the model's proposal.
"""
import ast
import sys
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

from endocrine import _apply_fix_to_source, _still_parses   # noqa: E402

SRC = 'def f():\n    """doc."""\n    x = 1\n'


def _blk(search: str, replace: str) -> str:
    return f"<<<< SEARCH {search}\n==== REPLACE\n{replace}\n>>>>"


def test_a_fix_that_would_break_the_file_is_refused():
    """The known-BAD case, taken verbatim in shape from exp42 C0051."""
    fix = '<<<< SEARCH def f():\n"""doc."""\n    x = 1\n==== REPLACE\ndef f():\n    """doc."""\n    x = 2\n>>>>'
    assert _apply_fix_to_source(SRC, fix) is None, (
        "a fix producing an unparseable file was applied; the corrupted result "
        "is then judged as though it were the model's proposal")


def test_a_sound_fix_still_applies():
    """The known-GOOD half. Without it the guard could be `return None` always."""
    out = _apply_fix_to_source(SRC, "<<<< SEARCH\n    x = 1\n==== REPLACE\n    x = 2\n>>>>")
    assert out == 'def f():\n    """doc."""\n    x = 2\n'
    ast.parse(out)


def test_the_guard_abstains_on_a_target_that_is_not_python():
    """Prose and markdown targets exist in this project. Refusing every fix on
    them because `ast.parse` fails would be a new defect, not a guard."""
    prose = "Some prose.\nA claim.\n"
    out = _apply_fix_to_source(prose, "<<<< SEARCH\nA claim.\n==== REPLACE\nA better claim.\n>>>>")
    assert out == "Some prose.\nA better claim.\n"


def test_the_guard_abstains_on_a_target_that_was_already_broken():
    broken = "def f(\n"
    out = _apply_fix_to_source(broken, "<<<< SEARCH\ndef f(\n==== REPLACE\ndef g(\n>>>>")
    assert out == "def g(\n", "a target that never parsed must not be held to parsing"


@pytest.mark.parametrize("before,after,expected", [
    ("x = 1\n", "x = 2\n", True),
    ("x = 1\n", "x = (\n", False),
    ("not python (\n", "still not python (\n", True),   # abstains
])
def test_still_parses_directly(before, after, expected):
    assert _still_parses(before, after) is expected


def test_the_marker_line_may_carry_the_first_line_of_the_search():
    """Separate defect fixed the same day: the marker line was skipped WHOLE, so
    code sharing it was dropped from the search text. The applier's own comment
    records 207 archive blocks that carry code there."""
    src = "def foo():\n    return 1\n"
    out = _apply_fix_to_source(
        src, "<<<< SEARCH def foo():\n    return 1\n==== REPLACE\ndef foo():\n    return 99\n>>>>")
    assert out is not None and "return 99" in out
    ast.parse(out)
    assert out.count("def foo():") == 1, "the def line was duplicated"
