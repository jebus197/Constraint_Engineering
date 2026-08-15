"""Close-the-loop must verify a non-Python target, not skip it and not fake it.

WHAT WENT WRONG, AND WHY THREE FIXES WERE WRONG BEFORE THIS ONE
---------------------------------------------------------------
`run_verification` ran ruff, mypy and bandit on the sandbox file whatever its
type. The zero-plant control is a markdown design reference, so mypy parsed the
prose as source and reported "Leading zeros in decimal integer". Every
close-the-loop attempt therefore FAILED, no finding could be validated, no
finding could close, and the irreducible queue filled with criticals the
machinery was structurally unable to resolve. That is what halted the control
run six hours in on 2026-08-01.

Three repairs were attempted and each failed differently. All three are pinned
below, because each is a plausible thing for someone to try again:

  1. SKIP the tools when the suffix is not .py.
     Worse than the bug. `attempt_close` does `if verify.passed: closed=True`,
     so skipping turns "cannot verify" into "verified" and every finding closes
     with nothing checked. A jammed queue is recoverable; a run full of findings
     marked verified when nothing was is not.

  2. EXTRACT the listings and require them to pass ruff/mypy.
     The listings reference imports the document declares in PROSE, so an
     extracted fragment always has undefined names. Nothing ever passes, which
     is the original jam wearing a different hat.

  3. EXTRACT and compare DIAGNOSTIC COUNTS against the unmodified target.
     Right instinct — the S_k pipeline judges a fix against a baseline for
     exactly this reason. But `_run_tool` truncates its output, so a fix that
     introduced a fresh syntax error counted the same as the baseline (3 vs 3)
     and was waved through. Measuring on a truncated measurement.

AMENDED 2026-08-01 21:30 — A FOURTH REPAIR, AND WHY THESE THREE MOVED
--------------------------------------------------------------------
The parse check above was itself the third instance of the same error. A clean
parse returned PASS, and `attempt_close` closes on PASS — so a fix injecting
subprocess.call(..., shell=True) into a fenced listing CLOSED the finding and was
recorded "verified by ast.parse of 7 fenced Python listing(s)". Measured against
the real Exp 53 control document.

A syntax check is a statement about the LISTING, never about the FIX. Every
harmful fix is syntactically valid, so a "sound" prose edit and a shell injection
travel the identical path: PASS for one is PASS for the other. The parse is now a
VETO — it may return FAIL, and a clean parse returns NO_APPLICABLE_CHECKS with the
veto recorded in `vetoes_run` rather than `checks_run`.

The three tests below asserted `.passed is True` for a harmless prose edit. Their
INTENT was right and is unchanged: an edit that touches only prose, or introduces
only an undefined name, must not be reported as a FAULT IN THE FIX. What moved is
the outcome that expresses it — NO_APPLICABLE_CHECKS rather than PASS — because
nothing applicable to the fix was ever run.


WHAT IS ACTUALLY VERIFIABLE
---------------------------
Narrow, and saying so beats inventing signal. ruff and mypy cannot speak to a
fragment without its imports. What can be determined, deterministically and with
no baseline, is whether the code still PARSES — which catches the failure that
matters, a fix that mangles a listing. Anything subtler about a prose claim is
not a static-analysis question and belongs with the falsifier or with HIL.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.bugzilla_loop import (  # noqa: E402
    VerificationOutcome, run_verification,
)

DOC = """# Reference

The section imports `time` and `random`.

```python
class TokenBucket:
    def allow(self, cost=1.0):
        now = time.monotonic()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
```

**ZC-01.** Offsets are 032 and 0100 in the table, and the value is 1.0.

```python
def backoff_delay(attempt, base_ms=250):
    return random.random() * base_ms * (2 ** attempt)
```
"""


@pytest.fixture
def doc(tmp_path):
    p = tmp_path / "SW-21-REF-04.md"
    p.write_text(DOC, encoding="utf-8")
    return p


class TestTheOriginalDefect:
    def test_prose_that_mypy_would_choke_on_does_not_fail_the_fix(self, doc, tmp_path):
        """'032' and '0100' are what made mypy report leading zeros.

        The document must verify cleanly despite carrying them, because they are
        prose, not source.
        """
        assert "032" in doc.read_text()
        same = tmp_path / "same.md"
        shutil.copy(doc, same)
        r = run_verification(same, None, baseline_path=doc)
        assert r.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS, (
            "prose that mypy would choke on must not read as a FAULT IN THE FIX")
        assert not r.failures


class TestItMustNotFakeSuccess:
    """Guards repair attempt 1, the dangerous one."""

    def test_a_target_with_no_code_is_refused_not_passed(self, tmp_path):
        p = tmp_path / "prose.md"
        p.write_text("**ZC-01.** Offsets are 032 and 0100.\n", encoding="utf-8")
        r = run_verification(p, None, baseline_path=p)
        assert r.passed is False, (
            "a target with nothing checkable must NOT report success — "
            "attempt_close closes the finding on verify.passed")
        assert "HIL" in " ".join(r.failures)

    def test_a_fix_that_breaks_a_listing_is_caught(self, doc, tmp_path):
        broken = tmp_path / "broken.md"
        broken.write_text(
            doc.read_text().replace("def allow(self, cost=1.0):",
                                    "def allow(self, cost=1.0:"), encoding="utf-8")
        r = run_verification(broken, None, baseline_path=doc)
        assert r.passed is False
        assert "unparseable" in " ".join(r.failures)

    def test_it_names_which_listing_broke(self, doc, tmp_path):
        """A bare failure is not actionable when a document holds several."""
        broken = tmp_path / "broken2.md"
        broken.write_text(
            doc.read_text().replace("return random.random()", "return random.random("),
            encoding="utf-8")
        r = run_verification(broken, None, baseline_path=doc)
        assert r.passed is False
        assert "listing 2" in " ".join(r.failures), (
            f"expected the second listing to be named, got {r.failures}")


class TestItMustNotOverReach:
    """Guards repair attempts 2 and 3 — demanding more than is knowable."""

    def test_undefined_names_do_not_fail_the_fix(self, doc, tmp_path):
        """`time` and `random` are declared in prose, never imported in a block.

        Every extracted fragment therefore has undefined names no matter what the
        fix did. Failing on that is repair attempt 2, and it re-jams the queue.
        """
        edited = tmp_path / "edited.md"
        edited.write_text(doc.read_text().replace("self.tokens -= cost",
                                                  "self.tokens -= cst"),
                          encoding="utf-8")
        r = run_verification(edited, None, baseline_path=doc)
        assert r.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert not r.failures, "an undefined name is not a fault in the fix"

    def test_a_prose_only_edit_passes(self, doc, tmp_path):
        edited = tmp_path / "prose_edit.md"
        edited.write_text(doc.read_text().replace("Offsets are 032",
                                                  "Offsets are 032 exactly"),
                          encoding="utf-8")
        r = run_verification(edited, None, baseline_path=doc)
        assert r.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert not r.failures


class TestPythonTargetsAreUnaffected:
    """The whole change must be invisible to the code experiments."""

    def test_a_type_error_in_a_py_target_still_fails(self, tmp_path):
        p = tmp_path / "t.py"
        p.write_text("x: int = 'not an int'\n", encoding="utf-8")
        r = run_verification(p, None)
        assert r.passed is False and r.mypy_passed is False

    def test_clean_python_still_passes(self, tmp_path):
        p = tmp_path / "ok.py"
        p.write_text("def f(a: int) -> int:\n    return a + 1\n", encoding="utf-8")
        assert run_verification(p, None).passed is True


class TestTheSourceDoesNotRegress:
    def test_the_static_tools_are_not_run_on_a_non_python_path(self):
        """Structural: the non-.py branch must return before reaching them."""
        src = (_root / "bench" / "bugzilla_loop.py").read_text(encoding="utf-8")
        i = src.index("if not is_python_target(sandbox_path):")
        j = src.index("ruff_ok, ruff_out = _run_tool(", i)
        branch = src[i:j]
        assert "return VerificationResult" in branch, (
            "the non-Python branch must return its own verdict, not fall through "
            "to tools that cannot read the target")
        assert "_ast.parse" in branch


class TestTheFourthRepair:
    """A clean parse must never license a close. Pinned where the other three are."""

    def test_a_clean_parse_is_a_veto_not_a_pass(self, doc, tmp_path):
        same = tmp_path / "same.md"
        shutil.copy(doc, same)
        r = run_verification(same, None, baseline_path=doc)
        assert r.outcome is not VerificationOutcome.PASS, (
            "a clean parse returning PASS is what closed a shell-injection fix")
        assert r.checks_run == [], (
            "a veto that passes must not appear as a check that ran")
        assert r.vetoes_run and "ast.parse" in r.vetoes_run[0], (
            "the veto must still be RECORDED — losing it is a different defect")

    def test_a_broken_listing_still_reads_as_a_fault_in_the_fix(self, doc, tmp_path):
        broken = tmp_path / "broken.md"
        broken.write_text(doc.read_text().replace("def allow(self, cost=1.0):",
                                                  "def allow(self, cost=1.0:"),
                          encoding="utf-8")
        r = run_verification(broken, None, baseline_path=doc)
        assert r.outcome is VerificationOutcome.FAIL
