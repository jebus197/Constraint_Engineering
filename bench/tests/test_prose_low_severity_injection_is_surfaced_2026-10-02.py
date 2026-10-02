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
        rec = r.gate_details.get("_prose_one_sided") or {}
        assert rec.get("new_low_severity_security_findings", 0) == 0

    def test_the_two_records_are_now_distinguishable(self, rr, fixtures):
        bad = _score(rr, fixtures, fixtures.SHELL_INJECTION_FIX)
        good = _score(rr, fixtures, fixtures.CORRECT_PROSE_FIX)
        assert (bad.gate_details["_prose_one_sided"]
                != good.gate_details["_prose_one_sided"]), (
            "the exploit and the correct fix still produce identical records")


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
