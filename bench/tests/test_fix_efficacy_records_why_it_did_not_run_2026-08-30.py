"""The fix-efficacy probe must leave a trace when it cannot run.

THE DEFECT, MEASURED 2026-08-30
-------------------------------
On the v3.1 simulated run the probe reached 0 of 19 registry entries and wrote
NOTHING. "The probe is wired" and "the probe is unreachable" were
indistinguishable in the artefact.

The guard required ``proposed_fix`` AND ``falsifier_code``. All 19 entries
carried a fix; NONE carried a falsifier. An earlier repair had widened a
DIFFERENT gate (the status branch) and left this one in place -- one gate
widened while a tighter gate remained, which is the check-the-whole-set failure.

The probe genuinely cannot run without a falsifier: all three of its passes
(tripwire, baseline, patched) execute the falsifier. So the repair is not to run
it anyway -- it is to RECORD the absence, and to do so without consuming the
per-round probe budget and without marking the entry tried, so a falsifier
arriving in a later round is still probeable.
"""
import sys, json, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import reference_runner_v3 as R
import fix_efficacy as FE

REPO = pathlib.Path(__file__).resolve().parents[2]


class TestTheDecision:
    def test_fix_and_falsifier_probes(self):
        assert R.fix_efficacy_decision(
            {"proposed_fix": "x", "falsifier_code": "assert False"}, 0) == "PROBE"

    def test_fix_without_falsifier_is_recorded_not_silently_skipped(self):
        assert R.fix_efficacy_decision({"proposed_fix": "x"}, 0) == "NO_FALSIFIER"

    def test_no_fix_at_all_is_skipped(self):
        assert R.fix_efficacy_decision({"falsifier_code": "assert False"}, 0) == "SKIP"

    def test_the_per_round_cap_still_binds_for_real_probes(self):
        e = {"proposed_fix": "x", "falsifier_code": "y"}
        assert R.fix_efficacy_decision(e, R.FIX_EFFICACY_PER_ROUND_LIMIT - 1) == "PROBE"
        assert R.fix_efficacy_decision(e, R.FIX_EFFICACY_PER_ROUND_LIMIT) == "SKIP"

    def test_a_no_falsifier_entry_does_NOT_consume_the_cap(self):
        """Otherwise 5 fix-only entries starve the budget and block real probes."""
        calls = 0
        for _ in range(50):
            if R.fix_efficacy_decision({"proposed_fix": "x"}, calls) == "PROBE":
                calls += 1
        assert calls == 0
        # ...and a real probe is still admitted afterwards
        assert R.fix_efficacy_decision(
            {"proposed_fix": "x", "falsifier_code": "y"}, calls) == "PROBE"

    def test_a_no_falsifier_entry_stays_probeable_later(self):
        """It must not be marked attempted, or a later falsifier is never probed."""
        e = {"proposed_fix": "x"}
        assert R.fix_efficacy_decision(e, 0) == "NO_FALSIFIER"
        assert not e.get("fix_efficacy_attempted")
        e["falsifier_code"] = "assert False"
        assert R.fix_efficacy_decision(e, 0) == "PROBE"

    def test_an_attempted_entry_is_not_re_probed(self):
        assert R.fix_efficacy_decision(
            {"proposed_fix": "x", "falsifier_code": "y",
             "fix_efficacy_attempted": True}, 0) == "SKIP"


class TestTheOutcomeExists:
    def test_no_falsifier_is_a_named_outcome(self):
        assert FE.NO_FALSIFIER == "NOT_PROBED_NO_FALSIFIER"

    def test_it_is_not_confusable_with_a_verdict(self):
        """It must not read as 'the fix failed'."""
        assert "NOT_PROBED" in FE.NO_FALSIFIER
        assert FE.NO_FALSIFIER not in (FE.FIX_CURES, FE.FIX_INEFFECTIVE)


class TestAgainstTheRealRun:
    def test_the_v31_run_would_now_be_fully_explained(self):
        """The run that reached 0 of 19 must now record a reason for all 19."""
        rp = (REPO / "bench" / "logs" / "sim45_memory_20260830T161215Z"
              / "sim45_memory_report.json")
        if not rp.is_file():
            import pytest
            pytest.skip(f"reference run artefact not present: {rp}")
        E = json.loads(rp.read_text())["registry"]["entries"]
        E = list(E.values()) if isinstance(E, dict) else E
        calls = 0
        out = collections.Counter()
        for e in E:
            d = R.fix_efficacy_decision(e, calls)
            out[d] += 1
            if d == "PROBE":
                calls += 1
        assert out["SKIP"] == 0, f"still silently skipping {out['SKIP']} entries"
        assert out["NO_FALSIFIER"] == len(E)
