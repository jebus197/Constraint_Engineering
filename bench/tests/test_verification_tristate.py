"""A3: verification is a tri-state, and a finding closes on PASS alone.

THE CONFLATION
--------------
`run_verification` returned one boolean. That boolean carried two entirely
different meanings at once:

    passed=False  ->  "an applicable check ran and the fix failed it"
    passed=False  ->  "nothing applicable could be run at all"

The first is a verdict on the fix. The second is a report on the instrument.
On a prose target the second is the ONLY thing that ever happened, so every
log line, every report field and every human reading them said "this fix is
bad" about fixes no tool had looked at.

WHY NOT JUST FLIP IT
--------------------
Because that repair was made, on 2026-08-01, and it was worse than the bug.
`attempt_close` did `if verify.passed: closed = True`. A "nothing could be
checked" result that reported passed=True would have marked EVERY finding on
a prose target verified with nothing checked at all. A jammed queue is
recoverable. A run full of findings stamped verified by an instrument that
never looked is not.

So the third state is explicit, `passed` is derived from it and cannot be set
independently, and the close decision names PASS rather than negating FAIL.

WHAT THESE TESTS PIN
--------------------
  * NO_APPLICABLE_CHECKS is distinguishable from FAIL, and reads False for
    `passed` — the existing "a no-code target does not close" behaviour is
    preserved exactly, and is asserted here as well as in
    test_verification_non_python_target.py.
  * The construction-time invariants: PASS with nothing in `checks_run` is
    unrepresentable, and a CloseAttempt cannot be closed on anything but PASS.
    These are the guards that make the dangerous repair impossible to write
    rather than merely discouraged.
  * The Python path, which already works, is unchanged in outcome.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.bugzilla_loop import (  # noqa: E402
    CloseAttempt,
    FixExtractResult,
    VerificationOutcome,
    VerificationResult,
    attempt_close,
    is_python_target,
    run_verification,
)

# A markdown target carrying real Python listings — the shape of every Exp
# 48-53 target: claims in prose, code in fences.
DOC_WITH_CODE = """# Reference SW-21-REF-04

The section imports `time`; offsets are 032 and 0100 in the table.

```python
class TokenBucket:
    def allow(self, cost=1.0):
        now = time.monotonic()
        return self.tokens >= cost
```
"""

DOC_NO_CODE = """# Reference SW-21-REF-04

**ZC-01.** The retry budget is 3 attempts and the offsets are 032 and 0100.
No listing accompanies this claim.
"""


@pytest.fixture
def doc_with_code(tmp_path):
    p = tmp_path / "SW-21-REF-04.md"
    p.write_text(DOC_WITH_CODE, encoding="utf-8")
    return p


@pytest.fixture
def doc_no_code(tmp_path):
    p = tmp_path / "SW-21-REF-09.md"
    p.write_text(DOC_NO_CODE, encoding="utf-8")
    return p


# ═══════════════════════════════════════════════════════════════════════════
# 1. The three states are actually three
# ═══════════════════════════════════════════════════════════════════════════


class TestTheThirdStateExists:

    def test_nothing_checkable_is_not_a_failure_of_the_fix(self, doc_no_code):
        r = run_verification(doc_no_code, None)
        assert r.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS, (
            "a prose target with no listing gave the instrument nothing to "
            f"read; that is not a FAIL. Got {r.outcome}")
        assert r.outcome is not VerificationOutcome.FAIL

    def test_nothing_checkable_still_does_not_close(self, doc_no_code):
        """The behaviour that must be preserved, stated as its own test."""
        r = run_verification(doc_no_code, None)
        assert r.passed is False
        assert r.no_applicable_checks is True

    def test_a_broken_listing_is_a_failure_of_the_fix(self, doc_with_code, tmp_path):
        broken = tmp_path / "broken.md"
        broken.write_text(
            doc_with_code.read_text().replace("def allow(self, cost=1.0):",
                                              "def allow(self, cost=1.0:"),
            encoding="utf-8")
        r = run_verification(broken, None)
        assert r.outcome is VerificationOutcome.FAIL, (
            "a fix that mangles a listing IS a fault in the fix and must read "
            f"as FAIL, not as 'nothing could be checked'. Got {r.outcome}")
        assert "unparseable" in " ".join(r.failures)

    def test_a_sound_prose_fix_yields_no_applicable_checks(self, doc_with_code):
        r = run_verification(doc_with_code, None)
        # Amended 2026-08-01 21:25. There is no sound prose fix that the harness
        # can verify: ruff/mypy/bandit cannot read the document, no prose config
        # sets test_cmd, and the parse only vetoes. A "sound" fix and a shell
        # injection take the SAME path, so PASS here means PASS there.
        assert r.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS
        assert r.checks_run == []
        assert r.vetoes_run and "ast.parse" in r.vetoes_run[0], (
            "the veto must still be RECORDED — losing it entirely would be a "
            "different defect; what must never happen is it counting as "
            "evidence FOR the fix")

    def test_the_three_outcomes_are_mutually_exclusive(self, doc_with_code,
                                                       doc_no_code, tmp_path):
        broken = tmp_path / "b.md"
        broken.write_text(doc_with_code.read_text().replace("return self.tokens",
                                                            "return self.tokens ="),
                          encoding="utf-8")
        # PASS is reached via a PYTHON target, not a prose one. Amended
        # 2026-08-01 21:25: a clean parse of a prose target's listings used to
        # return PASS, and attempt_close closes on PASS — so a shell-injection
        # fix closed a finding and was recorded "verified" (measured on the real
        # control document). A syntax check is a statement about the LISTING,
        # not the FIX, so it is now a VETO: FAIL or NO_APPLICABLE_CHECKS, never
        # PASS. The property this test defends — all three states reachable and
        # distinct — is unchanged; only where PASS comes from has moved.
        code_target = tmp_path / "m.py"
        code_target.write_text("def f(a: int) -> int:\n    return a + 1\n",
                               encoding="utf-8")
        seen = {
            run_verification(code_target, None).outcome,
            run_verification(broken, None).outcome,
            run_verification(doc_no_code, None).outcome,
        }
        assert seen == {
            VerificationOutcome.PASS,
            VerificationOutcome.FAIL,
            VerificationOutcome.NO_APPLICABLE_CHECKS,
        }, f"the three cases must produce three distinct outcomes, got {seen}"


# ═══════════════════════════════════════════════════════════════════════════
# 2. attempt_close closes on PASS and on nothing else
# ═══════════════════════════════════════════════════════════════════════════


def _fix(old: str, new: str) -> dict:
    return {"finding_id": "C0031",
            "proposed_fix": f"<<<< SEARCH\n{old}\n==== REPLACE\n{new}\n>>>>"}


class TestCloseOnlyOnPass:

    def test_no_applicable_checks_does_not_close(self, doc_no_code):
        a = attempt_close(_fix("3 attempts", "4 attempts"), doc_no_code)
        assert a.closed is False, (
            "THE line. A finding the instrument could not look at must not "
            "close — this is the exact repair that would have marked every "
            "finding on the control run verified.")
        assert a.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS

    def test_and_it_does_not_blame_the_fix_when_it_declines_to_close(self,
                                                                    doc_no_code):
        a = attempt_close(_fix("3 attempts", "4 attempts"), doc_no_code)
        assert "not verifiable" in a.reason, a.reason
        assert "verification failed" not in a.reason, (
            "'verification failed' is a verdict on the fix. Nothing was "
            f"verified here, so nothing failed. Got: {a.reason}")

    def test_a_real_failure_still_reads_as_a_failure(self, doc_with_code):
        a = attempt_close(
            _fix("def allow(self, cost=1.0):", "def allow(self, cost=1.0:"),
            doc_with_code)
        assert a.closed is False
        assert a.outcome is VerificationOutcome.FAIL
        assert "verification failed" in a.reason

    def test_a_sound_prose_fix_does_not_close(self, doc_with_code):
        a = attempt_close(_fix("return self.tokens >= cost",
                               "return bool(self.tokens >= cost)"),
                          doc_with_code)
        # Amended 2026-08-01 21:25. Closing here would close on the identical
        # evidence that closed a shell-injection fix: a clean ast.parse. Nothing
        # about the FIX was checked, so nothing may be closed.
        assert a.closed is False
        assert a.outcome is VerificationOutcome.NO_APPLICABLE_CHECKS

    def test_the_close_decision_names_pass_rather_than_negating_fail(self):
        """Structural, and worth the ugliness.

        `if verify.passed` is the line the panel named. Written as a negation
        of failure it silently admits any future fourth state; written as an
        identity against PASS it admits nothing it was not told to admit.
        """
        src = (_root / "bench" / "bugzilla_loop.py").read_text(encoding="utf-8")
        i = src.index("def attempt_close(")
        j = src.index("def verify_and_close_fixes(", i)
        body = src[i:j]
        assert "verify.outcome is VerificationOutcome.PASS" in body
        assert "if verify.passed" not in body, (
            "close-the-loop must key on the PASS state explicitly, not on the "
            "truthiness of a derived boolean")


# ═══════════════════════════════════════════════════════════════════════════
# 3. The dangerous shapes are unrepresentable, not merely discouraged
# ═══════════════════════════════════════════════════════════════════════════


class TestTheGuardsAreStructural:

    def test_a_pass_that_checked_nothing_cannot_be_constructed(self):
        with pytest.raises(ValueError, match="no checks_run"):
            VerificationResult(outcome=VerificationOutcome.PASS, checks_run=[])

    def test_no_applicable_checks_cannot_claim_to_have_run_checks(self):
        with pytest.raises(ValueError, match="NO_APPLICABLE_CHECKS"):
            VerificationResult(
                outcome=VerificationOutcome.NO_APPLICABLE_CHECKS,
                checks_run=["mypy"],
            )

    def test_passed_is_derived_and_cannot_be_asserted_independently(self):
        """Reintroducing `passed=True` as a settable field must be loud."""
        with pytest.raises(TypeError):
            VerificationResult(passed=True)  # type: ignore[call-arg]

    def test_a_close_attempt_cannot_be_closed_on_a_non_pass(self):
        for bad in (VerificationOutcome.FAIL,
                    VerificationOutcome.NO_APPLICABLE_CHECKS):
            with pytest.raises(ValueError, match="closes on PASS"):
                CloseAttempt(finding_id="C0031", closed=True,
                             extract=FixExtractResult(success=True),
                             outcome=bad)

    def test_the_outcome_serialises_as_a_plain_string(self):
        """Reports are JSON; an enum that needs a custom encoder gets dropped."""
        import json
        assert json.dumps({"o": VerificationOutcome.NO_APPLICABLE_CHECKS}) == (
            '{"o": "NO_APPLICABLE_CHECKS"}')


# ═══════════════════════════════════════════════════════════════════════════
# 4. The Python path — which already works — is unchanged
# ═══════════════════════════════════════════════════════════════════════════


class TestPythonTargetsUnchanged:

    def test_clean_python_passes_and_names_three_checks(self, tmp_path):
        p = tmp_path / "ok.py"
        p.write_text("def f(a: int) -> int:\n    return a + 1\n", encoding="utf-8")
        r = run_verification(p, None)
        assert r.outcome is VerificationOutcome.PASS
        assert set(r.checks_run) == {"ruff", "mypy", "bandit"}

    def test_a_type_error_is_a_fail_not_a_shrug(self, tmp_path):
        p = tmp_path / "t.py"
        p.write_text("x: int = 'not an int'\n", encoding="utf-8")
        r = run_verification(p, None)
        assert r.outcome is VerificationOutcome.FAIL, (
            "a Python target always has applicable checks; a tool that ran and "
            "objected is a FAIL, never NO_APPLICABLE_CHECKS")
        assert r.mypy_passed is False

    def test_an_unavailable_tool_is_a_fail_not_a_free_pass(self, tmp_path,
                                                           monkeypatch):
        """Deliberate boundary, stated as a test so it is not lost.

        Demoting a missing tool to 'not applicable' would let a finding close
        on the surviving two checks — a weakening of the path that already
        works. NO_APPLICABLE_CHECKS means 'nothing could be read at all', not
        'one of my tools is missing'.
        """
        import bench.bugzilla_loop as bz
        real = bz._run_tool

        def flaky(cmd, timeout=60):
            if "mypy" in cmd:
                return False, "tool not installed: no module named mypy"
            return real(cmd, timeout=timeout)

        monkeypatch.setattr(bz, "_run_tool", flaky)
        p = tmp_path / "ok.py"
        p.write_text("def f(a: int) -> int:\n    return a + 1\n", encoding="utf-8")
        r = bz.run_verification(p, None)
        assert r.outcome is VerificationOutcome.FAIL
        assert r.passed is False


# ═══════════════════════════════════════════════════════════════════════════
# 5. The target-type predicate the two modules share
# ═══════════════════════════════════════════════════════════════════════════


class TestIsPythonTarget:

    @pytest.mark.parametrize("name", ["a.py", "/x/y/b.PY", "bench/immune_agents.py"])
    def test_python(self, name):
        assert is_python_target(name) is True

    @pytest.mark.parametrize(
        "name",
        ["SW-21-REF-04.md", "notes.txt", "paper.tex", "config.toml", "README"],
    )
    def test_not_python(self, name):
        assert is_python_target(name) is False

    def test_it_accepts_a_path_object(self, tmp_path):
        assert is_python_target(tmp_path / "x.py") is True
        assert is_python_target(tmp_path / "x.md") is False
