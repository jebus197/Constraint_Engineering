"""The cap-confound classification must not depend on a chosen tolerance.

P-PASS of `scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py`,
2026-10-08. Its first version classified a duration as a cap hit when it sat
within 10% of a cap. 1956.0 s is +8.67% of the 1800 s cap, so it qualified only
because the window was drawn that wide: tighten the tolerance below 8.67% and 2
of the 3 co-failures become "genuine", which restores most of the contention
case the script exists to question.

THE ARCHIVE SETTLES IT INSTEAD. `elapsed_s` on a seat file is CUMULATIVE ACROSS
ATTEMPTS and the companion `.tools.json` carries the per-attempt breakdown. For
`panel_convergence_blockers_2026-10-03`: cc2 total 1956.0 s over 2 attempts with
attempt 2 at 110.4 s and 37 tool calls; fable total 1956.2 s with attempt 2 at
110.8 s and 11 tool calls. Attempt 1 therefore consumed about 1845 s in both
cases, against the 1800 s cap in force on that date, confirmed from git at commit
cd19903a.

These tests CALL the script and assert the conclusion is INVARIANT to the
tolerance, which is the property the first version lacked.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def S():
    spec = importlib.util.spec_from_file_location(
        "cap_conf",
        REPO / "scripts" / "the_contention_evidence_is_cap_confounded_2026-10-07.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["cap_conf"] = m
    spec.loader.exec_module(m)
    return m


class TestTheConclusionIsInvariantToTheTolerance:
    @pytest.mark.parametrize("tol", [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15])
    def test_exactly_one_co_failure_is_unexplained_at_every_tolerance(self, S, tol):
        import scripts  # noqa: F401 — only to keep import ordering stable
        pairs = {}
        for rnd, seat, t in S.EVENTS:
            pairs.setdefault(rnd, []).append((seat, t))
        pairs = {r: v for r, v in pairs.items() if len(v) == 2}
        genuine = [r for r, v in pairs.items()
                   if not all(S.at_a_cap(t, tol, round_name=r) for _s, t in v)]
        assert len(genuine) == 1, (
            f"at tol={tol} there are {len(genuine)} unexplained co-failures; the "
            "conclusion still depends on the tolerance, which is the defect this "
            f"guard exists to prevent: {genuine}")
        assert genuine == ["founder_verdicts_2026-09-28"], genuine

    def test_the_tight_tolerance_would_have_broken_the_first_version(self, S):
        """MUTATION: without the record, 1956 stops being a cap hit under 8%."""
        naive = any(abs(1956.0 - c) / c <= 0.05 for c in S.CAPS)
        assert naive is False, (
            "1956.0 s is within 5% of some cap, so the tolerance was never the "
            "weak point and this guard is testing nothing")
        informed = S.at_a_cap(
            1956.0, 0.05, round_name="panel_convergence_blockers_2026-10-03")
        assert informed is True, (
            "the archived per-attempt record no longer rescues the "
            "classification, so the conclusion is back to resting on a tolerance")


class TestTheRecordSaysWhatTheScriptClaims:
    def test_the_archived_attempt_breakdown_is_still_on_disk(self):
        d = REPO / "bench" / "logs" / "panel_convergence_blockers_2026-10-03"
        if not d.is_dir():
            pytest.skip("round directory not present in this checkout")
        for seat, want_total, want_a2 in (("cc2", 1956.0, 110.4),
                                          ("fable", 1956.2, 110.8)):
            main = json.loads((d / f"{seat}.json").read_text())
            tools = json.loads((d / f"{seat}.tools.json").read_text())
            assert abs(float(main["elapsed_s"]) - want_total) < 0.5, seat
            assert len(main["attempts"]) == 2, (
                f"{seat} no longer records 2 attempts, so the cumulative reading "
                "of elapsed_s cannot be checked")
            per = tools["per_attempt"]
            assert abs(float(per[0]["elapsed_s"]) - want_a2) < 0.5, seat

    def test_attempt_one_sat_at_the_cap_in_force(self):
        d = REPO / "bench" / "logs" / "panel_convergence_blockers_2026-10-03"
        if not d.is_dir():
            pytest.skip("round directory not present in this checkout")
        main = json.loads((d / "cc2.json").read_text())
        tools = json.loads((d / "cc2.tools.json").read_text())
        a1 = float(main["elapsed_s"]) - float(tools["per_attempt"][0]["elapsed_s"])
        assert abs(a1 - 1800) / 1800 < 0.05, (
            f"attempt 1 took {a1:.1f}s, which is not the 1800s cap in force on "
            "2026-10-03 (git commit cd19903a); the confound argument needs "
            "re-deriving")
