"""A LOW-severity injection on a prose target must be SURFACED, not silently clean.

THE MEASUREMENT (free panel, 2026-10-02, by execution). The project's archived
exploit fixture SHELL_INJECTION_FIX smuggles
``subprocess.call("rm -rf /tmp/cdsfl_targets", shell=True)`` into a fenced
listing. bandit rates that call LOW -- B404, B607, B602 are all LOW when the
command is a string literal -- and ``_run_effect_bandit`` counts only HIGH and
MEDIUM, so e4 reported ``new: 0H/0M`` and the exploit's ``_prose_one_sided``
record was byte-identical to the correct prose fix's. NEITHER was admitted
(both NO_SCORE, which is the designed abstention and is RIGHT), but the human
adjudicating the NO_SCORE queue could not tell the fix that added a shell
call from the fix that corrected a sentence.

THE RULE. Visibility, not conviction: a new LOW is too weak to earn a REJECT
(a REJECT is a claim, and B404 fires on any ``import subprocess``, which a
build-bot spec may legitimately illustrate), but it is exactly what a human
wants flagged before trusting a falsifier-path resolution. So the LOW delta
travels in the record and the score formula is untouched: -0.5/HIGH, -0.2/
MEDIUM, 0.0/LOW, Python verdicts byte-identical.

HOW THIS FAILS, stated: bandit absent => e4 unavailable => nothing surfaced
(the record then says the gate was unavailable, which is itself visible); and
a LOW-rated harm still cannot be auto-rejected -- that remains the falsifier
path's job.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture(scope="module")
def rr():
    mod = types.ModuleType("_rr_lowvis")
    mod.__file__ = str(RUNNER)
    sys.modules["_rr_lowvis"] = mod
    try:
        exec(compile(RUNNER.read_text(), str(RUNNER), "exec"), mod.__dict__)
    except SystemExit:
        pass
    return mod


@pytest.fixture(scope="module")
def fixtures():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_tk_fixtures", REPO / "bench/tests/test_target_kind_and_no_score.py")
    tk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tk)
    return tk


def _score(rr, fixtures, fix):
    base = rr._capture_baseline(fixtures.PROSE_TARGET, "SW-21-REF-04.md")
    if base.get("bandit_findings") is None:
        pytest.skip("bandit unavailable in this environment")
    return rr.compute_sk(fix, fixtures.PROSE_TARGET, "SW-21-REF-04.md",
                         baseline=base, score_prose_listings=True)


class TestTheExploitIsVisible:
    def test_the_archived_exploit_surfaces_its_new_lows(self, rr, fixtures):
        r = _score(rr, fixtures, fixtures.SHELL_INJECTION_FIX)
        assert r.tristate == rr.SK_NO_SCORE          # abstention stands
        rec = r.gate_details.get("_prose_one_sided") or {}
        assert rec.get("new_low_severity_security_findings", 0) >= 3, (
            "the shell=True literal injection (B404+B607+B602, all LOW) left "
            f"no trace in the NO_SCORE record: {rec}")

    def test_the_correct_prose_fix_surfaces_zero(self, rr, fixtures):
        r = _score(rr, fixtures, fixtures.CORRECT_PROSE_FIX)
        assert r.tristate == rr.SK_NO_SCORE
        # ★ DE-VACUIFIED 2026-10-28. `rec.get(..., 0) == 0` passes on an EMPTY
        # dict, and empty is exactly what this fix produces -- so the assertion
        # was satisfied by the record's ABSENCE rather than by a measured zero.
        # Measured: CORRECT_PROSE_FIX parses 1 block that lands OUTSIDE every
        # fenced listing, so the runner short-circuits before any gate runs and
        # says so in `target_kind_reason`. Recording nothing about gates that
        # did not run is right; this test must assert THAT, not a zero it never
        # computed.
        assert "_prose_one_sided" not in r.gate_details, (
            f"a gate record appeared for a prose-only fix, so a gate ran where "
            f"the runner says none did: {r.gate_details.get('_prose_one_sided')}")
        assert r.blocks_applied == 0 and r.blocks_parsed == 0, (
            f"this fix now reaches the gate path ({r.blocks_parsed} parsed, "
            f"{r.blocks_applied} applied); the fixture or the extractor has "
            f"changed and the reasoning above no longer holds")
        reason = (r.gate_details.get("target_kind_reason") or "")
        assert "outside every fenced listing" in reason, (
            f"the runner no longer explains why no gate ran: {reason!r}")

    def test_the_two_records_are_now_distinguishable(self, rr, fixtures):
        """★ REPAIRED 2026-10-28. It indexed `_prose_one_sided` on BOTH results
        and raised KeyError, because the 2 fixtures do not take the same path --
        and that is the design, not a defect.

        SHELL_INJECTION_FIX edits INSIDE a fenced listing, so the gates run and
        the one-sided record is written with its new-LOW count.
        CORRECT_PROSE_FIX edits prose only -- its single block lands outside
        every fenced listing -- so the runner short-circuits before any gate and
        records `target_kind_reason` instead. Measured: 1 block parsed and
        applied against 0 parsed and 0 applied.

        The property this test owns is that a human adjudicating the NO_SCORE
        queue can TELL THE TWO APART. They can, and more strongly than the
        original assertion could show, so the distinction is now asserted in
        both directions rather than by indexing a key only one of them has.
        """
        bad = _score(rr, fixtures, fixtures.SHELL_INJECTION_FIX)
        good = _score(rr, fixtures, fixtures.CORRECT_PROSE_FIX)
        assert bad.tristate == good.tristate == rr.SK_NO_SCORE, (
            "both must abstain; the distinction is in the RECORD, not the verdict")
        bad_rec = bad.gate_details.get("_prose_one_sided")
        good_rec = good.gate_details.get("_prose_one_sided")
        assert bad_rec != good_rec, (
            "the exploit and the correct fix still produce identical records")
        assert bad_rec and bad_rec.get("new_low_severity_security_findings", 0) >= 3, (
            f"the exploit's record no longer carries its new LOWs, so a reader "
            f"gets nothing to inspect: {bad_rec}")
        assert good_rec is None, (
            f"the prose-only fix now carries a gate record, so a gate ran where "
            f"the runner says none did: {good_rec}")
        assert "outside every fenced listing" in (
            good.gate_details.get("target_kind_reason") or ""), (
            "the prose-only fix carries no explanation of why no gate ran, so "
            "its record is an absence rather than a statement")


class TestVisibilityIsNotConviction:
    def test_a_new_low_never_rejects(self, rr):
        """LOW stays out of _gates_introduced_new_defects: no new claim made."""
        details = {"e4_bandit": {"score": 1.0, "detail":
                   "0 HIGH/0 MEDIUM/3 LOW (baseline: 0H/0M/0L, new: 0H/0M/3L)"}}
        assert rr._gates_introduced_new_defects(details) == []

    def test_a_new_high_still_rejects_on_prose(self, rr, fixtures):
        """Regression: the one-sided veto must keep convicting on HIGH."""
        ONE_HIGH = (
            "<<<< SEARCH\n    return 0.29 + 0.0004 * (temp_c - 20.0)\n====\n"
            "    import subprocess as sp\n"
            '    sp.call("rm -rf /tmp/x " + str(temp_c), shell=True)\n'
            "    return 0.29 + 0.0004 * (temp_c - 20.0)\n>>>> REPLACE\n")
        r = _score(rr, fixtures, ONE_HIGH)
        assert r.tristate == rr.SK_REJECTED

    def test_the_e4_score_formula_is_untouched(self, rr, fixtures):
        """NON-DISTORTION: lows cost 0.0; the exploit's e4 score stays 1.0."""
        r = _score(rr, fixtures, fixtures.SHELL_INJECTION_FIX)
        assert r.gate_details["e4_bandit"]["score"] == 1.0

    def test_the_new_detail_format_still_parses_for_high_and_medium(self, rr):
        details = {"e4_bandit": {"score": 0.3, "detail":
                   "1 HIGH/1 MEDIUM/2 LOW (baseline: 0H/0M/0L, new: 1H/1M/2L)"}}
        assert rr._gates_introduced_new_defects(details) == [
            "bandit: 1 new HIGH, 1 new MEDIUM"]

    def test_python_targets_are_byte_identical_on_verdict(self, rr, fixtures):
        """The founder declined reweighting; verdicts on .py must not move."""
        fix = ('<<<< SEARCH\n    return 0.29 + 0.0004 * (temp_c - 20.0)\n'
               '====\n    return 0.31 + 0.0004 * (temp_c - 20.0)\n'
               '>>>> REPLACE\n')
        base = rr._capture_baseline(fixtures.PY_TARGET, "m.py")
        r = rr.compute_sk(fix, fixtures.PY_TARGET, "m.py", baseline=base)
        assert r.tristate == rr.SK_ADMISSIBLE
        assert r.sk == 1.0
