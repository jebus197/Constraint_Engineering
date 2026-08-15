"""The closing-window audit must flag the two known cases and nothing else.

The location-keyed convergence counter is blind to a second distinct defect in
an already-flagged function — its own docstring says so and forbids gating on it.
Gating was enabled anyway, and the blindness fired twice, at closing rounds, on
CONFIRMED criticals:

    Exp 45  C0031  sev 0.75  opened r3   converged r3
    Exp 47  C0070  sev 0.85  opened r13  converged r13

`bench/audit_closing_window.py` does not fix the gate. It removes the silence.
These tests pin its selectivity in both directions, because an audit that flags
everything is as useless as one that flags nothing — the first draft flagged
7 of 36 runs by counting findings that had been demonstrated AND resolved inside
the window, which is the machinery working, not failing.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import pytest

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.audit_closing_window import (  # noqa: E402
    _RESOLVED_STATUSES, _infer_gate, audit_all, audit_run,
)

KNOWN = {"exp45_memory_statistics_live": "C0031",
         "exp47_divergence_locationkey_live": "C0070"}


def _run_dir(prefix):
    hits = sorted(glob.glob(str(_root / "bench" / "logs" / f"{prefix}_2026*")))
    if not hits:
        pytest.skip(f"{prefix} not present on this machine")
    return hits[0]


class TestTheTwoKnownCases:
    @pytest.mark.parametrize("prefix,cid", sorted(KNOWN.items()))
    def test_each_known_case_is_flagged(self, prefix, cid):
        out = audit_run(_run_dir(prefix))
        ids = [f["id"] for f in out["findings"]]
        assert cid in ids, f"{prefix}: expected {cid} flagged, got {ids}"

    @pytest.mark.parametrize("prefix,cid", sorted(KNOWN.items()))
    def test_the_flagged_finding_is_confirmed_and_unresolved(self, prefix, cid):
        """Both properties are load-bearing. Neither alone is the failure mode."""
        out = audit_run(_run_dir(prefix))
        f = next(x for x in out["findings"] if x["id"] == cid)
        assert f["severity"] >= 0.7
        assert f["status"] not in _RESOLVED_STATUSES
        assert f["opened_round"] == out["converged_at"], (
            "both known cases opened at the exact closing round")


class TestSelectivity:
    def test_exactly_the_known_runs_are_flagged_across_the_whole_archive(self):
        flagged = {r["run"] for r in audit_all() if r.get("findings")}
        assert flagged == set(KNOWN), (
            f"audit selectivity drifted. expected {set(KNOWN)}, got {flagged}")

    def test_a_resolved_finding_in_the_window_is_not_flagged(self):
        """The filter that took the audit from 7 runs to 2.

        A demonstrated critical that the ladder CLOSED inside the window is the
        system working. Flagging it buries the two cases that matter in noise.
        """
        run = _run_dir("exp45_memory_statistics_live")
        data = json.loads(next(Path(run).glob("*_report.json")).read_text())
        conv, win = data["converged_at"], 3
        entries = data["registry"]["entries"]
        resolved_in_window = [
            cid for cid, e in entries.items()
            if e.get("open_since_round") is not None
            and conv - win + 1 <= e["open_since_round"] <= conv
            and float(e.get("severity") or 0) >= 0.7
            and e.get("falsifier_verdict") == "CONFIRMED"
            and e.get("status") in _RESOLVED_STATUSES]
        assert resolved_in_window, (
            "this run no longer contains a resolved critical in its window — the "
            "test can no longer prove the filter does anything")
        flagged = {f["id"] for f in audit_run(run)["findings"]}
        assert not (flagged & set(resolved_in_window)), (
            f"resolved findings leaked into the audit: "
            f"{flagged & set(resolved_in_window)}")

    def test_a_subcritical_finding_in_the_window_is_not_flagged(self):
        for r in audit_all():
            for f in r.get("findings", []):
                assert f["severity"] >= 0.7, f"{r['run']}/{f['id']} is sub-critical"

    def test_a_non_converged_run_is_not_flagged(self):
        nonconv = [r for r in audit_all() if r.get("converged_at") is None]
        assert nonconv, "no non-converged runs present — this test is blind"
        for r in nonconv:
            assert not r.get("findings")
            assert "closing window undefined" in r.get("note", "")


class TestGateInference:
    """The report does not record which counting rule closed the run.

    `convergence_config` carries four keys, none of them the location flag. That
    is a reproducibility defect in the runner, reported separately. The audit
    must be honest about inferring rather than asserting.
    """

    def test_an_explicit_flag_is_believed(self):
        assert _infer_gate({"convergence_config":
                            {"location_keyed_convergence": True}}) == "location-keyed"
        assert _infer_gate({"convergence_config":
                            {"location_keyed_convergence": False}}) == "id-proxy"

    def test_absent_evidence_is_reported_as_unrecorded_not_guessed(self):
        assert _infer_gate({}) == "unrecorded"
        assert _infer_gate({"convergence_reason": "converged"}) == "unrecorded"

    def test_an_inference_is_marked_as_an_inference(self):
        g = _infer_gate({"location_crit_shadow_history": [4, 0, 0, 0],
                         "convergence_reason": "... history tail=[0, 0, 0] ..."})
        assert g.endswith("?"), (
            "an inference from agreeing series must not be reported as fact")

    def test_a_malformed_reason_does_not_crash_the_audit(self):
        assert _infer_gate({"location_crit_shadow_history": [1],
                            "convergence_reason": "tail=[not, ints]"}) == "unrecorded"


class TestExitStatus:
    def test_the_audit_exits_nonzero_when_something_is_flagged(self):
        import subprocess
        r = subprocess.run([sys.executable,
                            str(_root / "bench" / "audit_closing_window.py")],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 1, (
            "two runs are flagged; the audit must exit 1 so a report step can "
            f"act on it. got {r.returncode}")
        assert "C0031" in r.stdout and "C0070" in r.stdout
