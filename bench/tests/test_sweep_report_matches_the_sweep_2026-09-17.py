"""Task 9.1, panel round 16: the report's sweep answer must match the sweep.

THE DEFECT. `study_programme_report` answered the scheduled question "why the
sweep cannot clear a critical" with: "the sweep only re-examines NON-terminal
entries; a critical already CONFIRMED or CLOSED is terminal to it, so the sweep
cannot clear one -- it was never able to", and listed CONFIRMED among the
terminal statuses. The sweep's own terminal set is MERGED, CLOSED, REFUTED and
DUPLICATE. A CONFIRMED finding is a residual, and a CONFIRMED runnable falsifier
clears a critical with no severity gate. What the sweep cannot do is RETIRE a
finding at or above the critical threshold: the REFUTED branch and the reasoned
withdrawal branch are severity-gated (founder ruling 2026-08-03). The guard test
asserted the report's own false literal, so it could not go red on the defect.

HOW THIS IS CHECKED. The REAL `_post_convergence_sweep` runs with only its 3
external edges stubbed: `dispatch_to_model` (no model is called),
`_declared_models` (1 stub seat) and `reverify_falsifier` (no subprocess). The
report is then compared with what the sweep did, status by status and at the
threshold, rather than with a string the report carries.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import reference_runner_v3 as rr  # noqa: E402
import bench.falsifier_verify as fv  # noqa: E402

REPLY = "FALSIFIER: C0001\n```python\nassert False\n```\n"
WITHDRAW = "WITHDRAW C0001: the cited line does not exist in the target\n"

#: Every status the registry can carry that this file exercises.
STATUSES = ("OPEN", "CONTESTED", "CONFIRMED", "UNCONFIRMED", "REOPENED",
            "MERGED", "CLOSED", "REFUTED", "DUPLICATE")


def sweep(monkeypatch, verdict="CONFIRMED", status="OPEN", sev=0.75, reply=REPLY):
    reg = rr.FindingRegistry()
    reg.entries["C0001"] = {"canonical_id": "C0001", "status": status,
                            "severity": sev, "source_model": "X"}
    cfg = types.SimpleNamespace(post_convergence_sweep_rounds=1,
                                test_article="bench/reference_runner_v3.py")
    calls = {"dispatch": 0}

    def fake_dispatch(mc, prompt, system, enable_tools=True):
        calls["dispatch"] += 1
        return reply, 0.0

    monkeypatch.setattr(rr, "dispatch_to_model", fake_dispatch)
    monkeypatch.setattr(rr, "_declared_models",
                        lambda e, c: [types.SimpleNamespace(label="STUB")])
    monkeypatch.setattr(fv, "reverify_falsifier", lambda code, repo_root=None: verdict)
    stats = rr._post_convergence_sweep(reg, {}, cfg, round_idx=5, repo_root=ROOT)
    return reg, stats, calls


def item():
    return rr.study_programme_report(rr.FindingRegistry())[
        "why_the_sweep_cannot_clear_a_critical"]


class TestWhatTheSweepDoes:
    def test_an_open_critical_with_a_confirmed_falsifier_is_cleared(self, monkeypatch):
        assert 0.75 >= rr.CRITICAL_SEVERITY_THRESHOLD
        reg, stats, calls = sweep(monkeypatch, "CONFIRMED")
        assert calls["dispatch"] == 1
        assert stats["cleared"] == 1
        assert reg.entries["C0001"]["status"] == "CONFIRMED"

    def test_an_open_critical_with_a_refuted_falsifier_is_not_withdrawn(self, monkeypatch):
        reg, stats, _ = sweep(monkeypatch, "REFUTED")
        assert stats["withdrawn"] == 0
        assert stats.get("computed_evidence") == 1
        assert reg.entries["C0001"]["status"] == "OPEN"

    def test_control_a_sub_critical_refuted_is_withdrawn(self, monkeypatch):
        """Without this, the 0 withdrawn above could be a stub that never withdraws."""
        reg, stats, _ = sweep(monkeypatch, "REFUTED", sev=0.5)
        assert stats["withdrawn"] == 1
        assert reg.entries["C0001"]["status"] == "REFUTED"

    def test_a_confirmed_critical_is_dispatched_again(self, monkeypatch):
        _, _, calls = sweep(monkeypatch, "CONFIRMED", status="CONFIRMED")
        assert calls["dispatch"] == 1, "a CONFIRMED entry was not offered to the panel"


class TestTheReportMatchesTheSweep:
    def test_every_status_the_report_calls_terminal_is_skipped_and_no_other(
            self, monkeypatch):
        """Both forms executed: the report's list, and whether the sweep dispatches."""
        terminal = set(item()["terminal_statuses"])
        for status in STATUSES:
            _, _, calls = sweep(monkeypatch, "ERROR", status=status)
            dispatched = calls["dispatch"] > 0
            assert dispatched is (status not in terminal), (
                f"status {status}: the report calls it "
                f"{'terminal' if status in terminal else 'a residual'}, but the "
                f"sweep {'dispatched' if dispatched else 'skipped'} it")

    def test_confirmed_is_not_reported_terminal(self):
        assert "CONFIRMED" not in item()["terminal_statuses"]

    def test_the_answer_does_not_say_the_sweep_cannot_clear_one(self):
        assert "cannot clear one" not in item()["answer"]

    def test_the_retire_threshold_the_report_names_is_the_one_the_sweep_applies(
            self, monkeypatch):
        """At the named threshold a REFUTED falsifier and a reasoned withdrawal
        retire nothing; just below it a REFUTED falsifier retires the finding."""
        t = item()["cannot_retire_at_or_above"]
        _, stats, _ = sweep(monkeypatch, "REFUTED", sev=t)
        assert stats["withdrawn"] == 0
        _, stats, _ = sweep(monkeypatch, "ERROR", sev=t, reply=WITHDRAW)
        assert stats["withdrawn"] == 0 and stats.get("computed_evidence") == 1
        _, stats, _ = sweep(monkeypatch, "REFUTED", sev=round(t - 0.01, 2))
        assert stats["withdrawn"] == 1

    def test_the_report_names_the_clearing_route(self, monkeypatch):
        """The report says a CONFIRMED falsifier clears a critical with no
        severity gate; at severity 1.0 the sweep clears it."""
        assert "CONFIRMED" in item()["clears_a_critical_by"]
        _, stats, _ = sweep(monkeypatch, "CONFIRMED", sev=1.0)
        assert stats["cleared"] == 1
