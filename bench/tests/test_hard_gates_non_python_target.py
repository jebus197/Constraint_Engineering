"""The S_k hard gates must check a target's CODE, not its prose.

THE DEFECT
----------
g1 (`ast.parse`) and g2 (`py_compile`) were handed the WHOLE modified target.
Correct for a Python module. On the zero-plant control — a markdown design
reference — `ast.parse` chokes on the prose itself ("leading zeros in decimal
integer literals are not permitted", raised by a table of byte offsets like 032
and 0100) and returns 0.

Since `A = g1 * g2` and `A == 0` rejects outright, EVERY proposed fix scored
A=0.0 and was REJECTED. Fifty rejections on the 2026-08-01 run. No fix could be
admitted, so no finding could be resolved, so the irreducible queue filled with
criticals the machinery was structurally unable to close, and the run could not
converge. This is the dominant cause of that halt — the close-the-loop failure
found the same hour was the smaller half of it.

WHY IT MATTERS BEYOND ONE RUN
-----------------------------
This is the fourth instance in one day of a single class: the instrument was
built for code review and is now being pointed at prose.
  * `_anchor_dir_for` — a scratch .py file written beside a read-only markdown
    target, EPERM one second into the first control launch.
  * `run_verification` — ruff/mypy/bandit run on markdown.
  * `max_irreducible_queue` — a bound calibrated for code review, where a real
    defect is nearly always demonstrable.
  * these hard gates.
The remaining arc is prose-heavy, so the class will keep producing instances.
Each one costs a halted run, and each fails differently, so a single guard will
not catch them; what catches them is asking, of any target-touching mechanism,
"what does this do when the target is not Python?"
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.reference_runner_v3 import (  # noqa: E402
    _gateable_source, _run_hard_gate_ast, _run_hard_gate_compile,
)

MD = """# Reference

| Symbol | Value |
|---|---|
| offset | 032 |
| block  | 0100 |

```python
class TokenBucket:
    def allow(self, cost=1.0):
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
```

**ZC-02.** The offsets above are 032 and 0100.

```python
def backoff_delay(attempt, base_ms=250):
    return base_ms * (2 ** attempt)
```
"""
MD_PATH = "/staged/SW-21-REF-04.md"


def _A(text, path):
    return (_run_hard_gate_ast(text, path)[0]
            * _run_hard_gate_compile(text, path)[0])


class TestTheDefect:
    def test_the_prose_alone_is_not_parseable_python(self):
        """The premise. If this stops raising, the guard is obsolete."""
        import ast
        with pytest.raises(SyntaxError):
            ast.parse(MD)

    def test_an_unmodified_prose_target_is_nonetheless_admissible(self):
        assert _A(MD, MD_PATH) == 1, (
            "a fix that changed nothing was being rejected because the DOCUMENT "
            "is not Python — 50 rejections on the 2026-08-01 control run")

    def test_a_prose_only_edit_is_admissible(self):
        assert _A(MD.replace("The offsets above", "The offsets listed above"),
                  MD_PATH) == 1


class TestItStillCatchesRealBreakage:
    """The gates must not become decorative — that was the failure mode of the
    first attempt to fix the sibling defect in bugzilla_loop."""

    def test_a_fix_that_breaks_a_listing_is_rejected(self):
        broken = MD.replace("def allow(self, cost=1.0):", "def allow(self, cost=1.0:")
        assert _A(broken, MD_PATH) == 0

    def test_a_fix_that_breaks_the_SECOND_listing_is_rejected(self):
        broken = MD.replace("return base_ms * (2 ** attempt)",
                            "return base_ms * (2 ** attempt")
        assert _A(broken, MD_PATH) == 0

    def test_the_rejection_says_it_gated_the_listings(self):
        broken = MD.replace("def allow(self, cost=1.0):", "def allow(self, cost=1.0:")
        _, detail = _run_hard_gate_ast(broken, MD_PATH)
        assert "fenced listing" in detail, detail


class TestPythonTargetsAreUnchanged:
    def test_valid_python_admissible(self):
        assert _A("def f(a: int) -> int:\n    return a + 1\n", "/x/m.py") == 1

    def test_broken_python_rejected(self):
        assert _A("def f(a: int -> int:\n", "/x/m.py") == 0

    def test_an_empty_source_path_is_treated_as_python(self):
        """Back-compat: callers that pass no path get the old behaviour."""
        src, why = _gateable_source("x = 1\n", "")
        assert src == "x = 1\n" and "python" in why


class TestPureProse:
    """A target with no code at all: the gates cannot speak, and must say so
    rather than reporting a failure they did not observe."""

    def test_pure_prose_is_not_rejected_by_a_syntax_gate(self):
        assert _A("**ZC-01.** Offsets are 032 and 0100.\n", "/x/prose.md") == 1

    def test_and_the_detail_says_the_gate_was_not_applicable(self):
        _, detail = _run_hard_gate_ast("**ZC-01.** Offsets are 032.\n", "/x/prose.md")
        assert "not applicable" in detail, detail

    def test_close_the_loop_still_refuses_such_a_target(self, tmp_path):
        """The pair matters: the syntax gate abstains, but close-the-loop must
        still refuse to CLOSE a finding it cannot verify, or a prose target
        would close everything silently."""
        from bench.bugzilla_loop import run_verification
        p = tmp_path / "prose.md"
        p.write_text("**ZC-01.** Offsets are 032.\n", encoding="utf-8")
        assert run_verification(p, None, baseline_path=p).passed is False
