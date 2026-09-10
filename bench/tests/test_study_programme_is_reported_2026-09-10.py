"""Tasks 9.1 and 9.4: the 6 scheduled study items must be REPORTED.

HIS 2026-09-06 RULINGS scheduled 6 items for a run to report on: the
critical-severity ceiling; why the sweep cannot clear a critical; classifying
falsifier ERROR causes; the cross-architecture correlation; corrected S* values;
and both reach conditions. The entry recorded "Reported on: 0 of 6 in the last
run."

THAT WAS NEVER A FACT ABOUT THE RUN. Measured against the most recent archived
report: 1 of the 6 has any field at all (`post_convergence_sweep`) and 5 have
none. The report had nowhere to put the answers, so a run could not have reported
them however well it went.

IT EMITS STATE AND DECIDES NOTHING. No gate reads the block, no status turns on
it, and it changes no prompt -- so unlike the parked composer findings it does
not invalidate replay of archived runs.

AN UNANSWERABLE ITEM SAYS SO, AND SAYS WHY. Two of the 6 cannot be answered
today, and both are recorded as unanswerable with the reason rather than left
blank: the cross-architecture correlation needs genuinely distinct architectures
(task 9.4 -- every seat in the last run resolved to one model wearing several
labels, which is a PRECONDITION and not a measurement), and the reach question
rests on an unresolved panel split that is preserved rather than smoothed. A
blank is indistinguishable from a question nobody asked.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(ROOT))

import reference_runner_v3 as rr  # noqa: E402

RUNNER = ROOT / "bench" / "reference_runner_v3.py"

ITEMS = ("critical_severity_ceiling", "why_the_sweep_cannot_clear_a_critical",
         "falsifier_error_causes", "cross_architecture_correlation",
         "corrected_s_star", "both_reach_conditions")


class _Reg:
    def __init__(self, entries):
        self._e = entries

    def to_dict(self):
        return {"entries": self._e}


def _sample():
    return _Reg({
        "C0001": {"severity": 0.9, "status": "CONFIRMED", "source_model": "CC2",
                  "falsifier_verdict": "ERROR", "error_routed": True,
                  "sk_result": {"threshold_shadow": 0.5}},
        "C0002": {"severity": 0.6, "status": "OPEN", "source_model": "CC2",
                  "falsifier_verdict": "ERROR"},
    })


class TestAllSixAreReported:
    def test_every_scheduled_item_has_a_key(self):
        out = rr.study_programme_report(_sample())
        missing = [i for i in ITEMS if i not in out]
        assert not missing, f"study items with no field: {missing}"

    def test_each_item_states_its_question(self):
        out = rr.study_programme_report(_sample())
        for i in ITEMS:
            assert "question" in out[i], f"{i} does not say what it is asking"

    def test_the_block_declares_that_it_decides_nothing(self):
        assert rr.study_programme_report(_sample())["_decides_nothing"] is True


class TestTheUnanswerableSayWhy:
    def test_the_cross_architecture_item_refuses_on_one_model(self):
        """Task 9.4: one model wearing 6 labels cannot yield a correlation."""
        out = rr.study_programme_report(_sample())
        item = out["cross_architecture_correlation"]
        assert item["answerable"] is False
        assert item["distinct_source_models"] == ["CC2"]
        assert "PRECONDITION" in item["why_not"]

    def test_it_becomes_answerable_with_distinct_models(self):
        """The control. Without it, 'unanswerable' might be hardcoded."""
        reg = _Reg({"A": {"severity": 0.8, "source_model": "CC2"},
                    "B": {"severity": 0.8, "source_model": "Gemini"},
                    "C": {"severity": 0.8, "source_model": "DeepSeek"}})
        item = rr.study_programme_report(reg)["cross_architecture_correlation"]
        assert item["answerable"] is True
        assert item["why_not"] is None
        assert len(item["distinct_source_models"]) == 3

    def test_the_reach_split_is_preserved_not_resolved(self):
        item = rr.study_programme_report(_sample())["both_reach_conditions"]
        assert item["answerable"] is False
        assert "fable" in item["why_not"] and "cc2" in item["why_not"], (
            "the panel split is no longer recorded as a split, which would be "
            "smoothing a disagreement this project preserves deliberately")


class TestTheAnswerableCarryData:
    def test_the_severity_ceiling_is_measured_from_the_registry(self):
        item = rr.study_programme_report(_sample())["critical_severity_ceiling"]
        assert item["max_severity_observed"] == 0.9
        assert item["critical_count"] == 1
        assert item["n"] == 2
        assert item["threshold"] == rr.CRITICAL_SEVERITY_THRESHOLD

    def test_error_causes_are_tallied(self):
        item = rr.study_programme_report(_sample())["falsifier_error_causes"]
        assert item["total_error_verdicts"] == 2
        assert item["by_cause"] == {"error_routed": 1, "unrouted": 1}

    def test_the_sweep_answer_names_the_terminal_statuses(self):
        item = rr.study_programme_report(_sample())["why_the_sweep_cannot_clear_a_critical"]
        assert "CONFIRMED" in item["terminal_statuses"]
        assert "cannot clear one" in item["answer"]


class TestItIsWiredAndCannotBreakARun:
    def test_the_reporter_has_a_call_site(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "study_programme_report" in called, (
            "the reporter is defined and never called, so no run emits it")

    def test_the_call_site_is_guarded(self):
        src = RUNNER.read_text(encoding="utf-8")
        i = src.index('result["study_programme"] = study_programme_report')
        window = src[max(0, i - 400):i]
        assert "try:" in window, (
            "the reporter is not wrapped; an instrument that can break a run is "
            "worse than one that is absent")
        assert 'result["study_programme"] = {' in src, (
            "there is no failure branch, so a broken reporter would leave the "
            "block absent and a reader could not tell that from 'nothing to "
            "report'")

    def test_a_broken_registry_does_not_raise(self):
        class Bad:
            def to_dict(self):
                raise RuntimeError("registry unavailable")
        out = rr.study_programme_report(Bad())
        assert set(ITEMS) <= set(out), (
            "a failing registry lost the whole block instead of reporting empty "
            "items")
