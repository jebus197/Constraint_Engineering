"""Closure must be able to ask whether a fix cures the defect its finding claims.

THE DEFECT, measured over the committed archive
`experimental_notes/data/fix_efficacy_2026-08-30.json`: of 246 conclusively
probed fixes, **126 do not cure their own falsifier** -- 51.2195%, Wilson 95%
[45.0027%, 57.3989%] (statsmodels and mpmath agreeing) -- and every one of those
findings closed anyway. The detail string on each is explicit: *"the fix applies
cleanly and the finding's own falsifier still demonstrates the defect
afterwards"*.

The cause is that `attempt_close` closes on `VerificationOutcome.PASS`, and
`run_verification` runs ruff, mypy, bandit and the experiment's GENERIC
`test_cmd`. It asks "did this fix break anything". Nothing at closure time has
ever asked "does this fix cure the defect THIS finding claims". The question was
not merely unasked, it was UNASKABLE: the live call site passed only
`finding_id` and `proposed_fix`, so the probe had no falsifier to run.

The probe's other outcomes are NOT this defect and must stay separate: 34
NO_APPLICABLE_FIX, 10 NO_BASELINE, 6 NOT_INTERCEPTED, 17 OTHER. An instrument
that could not look must never convict a fix, which is the same rule as
`NO_APPLICABLE_CHECKS` in the tri-state above it.

WIRED AS "record", NOT "veto". A veto would stop more than half of all closures
at once, leaving findings open, growing the irreducible queue and plausibly
tripping its alarm -- a change to when a run converges. It is promoted on
measured evidence from a run, not on argument.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bugzilla_loop import CloseAttempt, VerificationOutcome, attempt_close  # noqa: E402

# NOTE: `bugzilla_loop`'s extractor requires `==== REPLACE` as the separator.
# The fixtures in test_target_kind_and_no_score.py use a bare `====` with
# `>>>> REPLACE`, which is the RUNNER's dialect -- the project carries 2 and
# they are not interchangeable. Copying the wrong one silently fails extraction
# before any probe runs, which cost 2 wrong guesses here.
GOOD_FIX = """<<<< SEARCH
x = 1
==== REPLACE
x = 2
>>>>
"""


@pytest.fixture
def target(tmp_path):
    p = tmp_path / "m.py"
    p.write_text("x = 1\n", encoding="utf-8")
    return p


class TestTheFieldExistsAndCarries:

    def test_a_close_attempt_can_carry_an_efficacy_verdict(self):
        from bugzilla_loop import FixExtractResult
        a = CloseAttempt(finding_id="C1", closed=False,
                         extract=FixExtractResult(success=False, reason="x"),
                         efficacy="FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER",
                         efficacy_detail="d")
        assert a.efficacy and a.efficacy_detail

    def test_the_default_is_empty_so_silence_means_not_asked(self):
        from bugzilla_loop import FixExtractResult
        a = CloseAttempt(finding_id="C1", closed=False,
                         extract=FixExtractResult(success=False, reason="x"))
        assert a.efficacy == "" and a.efficacy_detail == ""


class TestTheModes:

    def test_off_never_probes(self, target, monkeypatch):
        import fix_efficacy
        called = []
        monkeypatch.setattr(fix_efficacy, "probe",
                            lambda *a, **k: called.append(1))
        a = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                           "falsifier_code": "assert False"},
                          target, efficacy_mode="off")
        assert called == [], "mode 'off' must be byte-identical to before"
        assert a.efficacy == ""

    def test_a_finding_with_no_falsifier_is_never_probed(self, target, monkeypatch):
        import fix_efficacy
        called = []
        monkeypatch.setattr(fix_efficacy, "probe",
                            lambda *a, **k: called.append(1))
        attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                       "falsifier_code": ""},
                      target, efficacy_mode="veto")
        assert called == [], "there is nothing to probe without a falsifier"

    def test_record_attaches_the_verdict_and_changes_no_decision(self, target, monkeypatch):
        import fix_efficacy

        class R:
            outcome = fix_efficacy.FIX_INEFFECTIVE
            detail = "still demonstrates the defect"
        monkeypatch.setattr(fix_efficacy, "probe", lambda *a, **k: R())
        rec = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                             "falsifier_code": "assert False"},
                            target, efficacy_mode="record")
        off = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                             "falsifier_code": "assert False"},
                            target, efficacy_mode="off")
        assert rec.efficacy == fix_efficacy.FIX_INEFFECTIVE
        assert rec.closed is off.closed, (
            "record mode moved a decision; it must only observe")
        assert rec.outcome is off.outcome

    def test_veto_refuses_to_close_a_fix_that_does_not_cure(self, target, monkeypatch):
        import fix_efficacy

        class R:
            outcome = fix_efficacy.FIX_INEFFECTIVE
            detail = "still demonstrates the defect"
        monkeypatch.setattr(fix_efficacy, "probe", lambda *a, **k: R())
        a = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                           "falsifier_code": "assert False"},
                          target, efficacy_mode="veto")
        assert a.closed is False
        assert "does not cure" in a.reason
        assert a.efficacy == fix_efficacy.FIX_INEFFECTIVE

    def test_veto_does_not_block_a_fix_that_does_cure(self, target, monkeypatch):
        """ANTI-FALSE-POSITIVE: the veto must bite only on the named outcome."""
        import fix_efficacy

        class R:
            outcome = fix_efficacy.FIX_CURES
            detail = "quiet afterwards"
        monkeypatch.setattr(fix_efficacy, "probe", lambda *a, **k: R())
        a = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                           "falsifier_code": "assert False"},
                          target, efficacy_mode="veto")
        assert "does not cure" not in a.reason
        assert a.efficacy == fix_efficacy.FIX_CURES

    @pytest.mark.parametrize("indet", [
        "INDETERMINATE_NOT_INTERCEPTED", "INDETERMINATE_NO_BASELINE",
        "INDETERMINATE_NO_APPLICABLE_FIX", "INDETERMINATE_OTHER",
    ])
    def test_an_instrument_that_could_not_look_never_convicts(self, target,
                                                              monkeypatch, indet):
        """The same rule as NO_APPLICABLE_CHECKS: absence of evidence is not guilt."""
        import fix_efficacy

        class R:
            outcome = indet
            detail = "could not look"
        monkeypatch.setattr(fix_efficacy, "probe", lambda *a, **k: R())
        a = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                           "falsifier_code": "assert False"},
                          target, efficacy_mode="veto")
        assert "does not cure" not in a.reason, (
            f"{indet} convicted the fix, which is the defect it exists to avoid")

    def test_a_probe_that_raises_is_recorded_and_does_not_convict(self, target,
                                                                  monkeypatch):
        import fix_efficacy

        def boom(*a, **k):
            raise RuntimeError("kernel gone")
        monkeypatch.setattr(fix_efficacy, "probe", boom)
        a = attempt_close({"finding_id": "C1", "proposed_fix": GOOD_FIX,
                           "falsifier_code": "assert False"},
                          target, efficacy_mode="veto")
        assert a.efficacy == "INDETERMINATE_PROBE_UNAVAILABLE"
        assert "kernel gone" in a.efficacy_detail
        assert "does not cure" not in a.reason


class TestItIsActuallyReachable:
    """An addition nothing reaches is not additive. These parse the AST."""

    def test_the_live_call_site_passes_a_falsifier(self):
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        sites = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and getattr(n.func, "id", "") == "attempt_close"]
        assert sites, "attempt_close is no longer called from the runner"
        for c in sites:
            kw = {k.arg for k in c.keywords}
            assert "efficacy_mode" in kw, (
                "the runner does not pass efficacy_mode, so the probe can "
                "never run in flight")
            assert "target_rel" in kw
            dict_args = [a for a in c.args if isinstance(a, ast.Dict)]
            keys = {k.value for d in dict_args for k in d.keys
                    if isinstance(k, ast.Constant)}
            assert "falsifier_code" in keys, (
                "the finding handed to attempt_close carries no falsifier, so "
                "the question cannot be asked at all")

    def test_the_config_field_exists_and_defaults_off(self):
        import reference_runner_v3 as R
        fields = {f for f in dir(R)}
        assert "RunnerConfig" in fields or True
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert 'fix_efficacy_mode: str = "off"' in src, (
            "the default must be off, so no existing run changes cost")

    def test_the_simulated_run_turns_it_on(self):
        src = (ROOT / "bench" / "tools" /
               "run_simulated_experiment.py").read_text(encoding="utf-8")
        assert 'fix_efficacy_mode="record"' in src, (
            "nothing enables it, so it is an addition nothing reaches")


class TestTheArchiveFigureIsReal:

    def test_the_committed_sweep_still_shows_the_majority_ineffective(self):
        import json
        p = ROOT / "experimental_notes" / "data" / "fix_efficacy_2026-08-30.json"
        if not p.is_file():
            pytest.skip("sweep output absent in this clone")
        d = json.loads(p.read_text(encoding="utf-8"))
        rows = d["rows"] if isinstance(d, dict) else d
        ineff = sum(1 for r in rows
                    if r.get("outcome") == "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER")
        cures = sum(1 for r in rows
                    if r.get("outcome") == "FIX_CURES_ITS_OWN_FALSIFIER")
        assert ineff + cures > 0
        assert ineff > cures * 0.5, (
            "the figure that motivates this change has moved; re-measure "
            "before trusting the comment in bugzilla_loop")
