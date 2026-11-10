"""`_asserts_something` cannot be satisfied by the WORD `raises` in prose.

★ CONSTRUCTED EXPLOIT, free panel 2026-11-10, against the dispatch brief's
own challenge. The fallback was a substring test over the function's source,
so `def test_x(): x = "raises"` -- zero assertions -- counted as asserting
something, and a DONE entry could name such a file as evidence. The fallback
now requires `raises` as an identifier or attribute in code. Measured before
the change: 0 verdicts over the live list's named evidence files differ.
"""
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from task_list_markers import _asserts_something  # noqa: E402


def _fn(src: str):
    return [n for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.FunctionDef)][0]


class TestProseIsNotAnAssertion:

    def test_a_string_literal_saying_raises_does_not_count(self):
        src = 'def test_x():\n    x = "raises"\n'
        assert _asserts_something(_fn(src), src) is False

    def test_a_docstring_saying_raises_does_not_count(self):
        src = 'def test_x():\n    """pytest.raises would be used here."""\n'
        assert _asserts_something(_fn(src), src) is False

    def test_pytest_raises_still_counts(self):
        src = ("def test_x():\n    import pytest\n"
               "    with pytest.raises(ValueError):\n        int('x')\n")
        assert _asserts_something(_fn(src), src) is True

    def test_a_real_assert_still_counts(self):
        src = "def test_x():\n    assert 1 + 1 == 2\n"
        assert _asserts_something(_fn(src), src) is True

    def test_assert_true_still_does_not_count(self):
        src = "def test_x():\n    assert True\n"
        assert _asserts_something(_fn(src), src) is False
