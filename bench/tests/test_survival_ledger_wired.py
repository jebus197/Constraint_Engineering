"""T03: the survived-falsification ledger is WIRED, not merely built.

`SurvivedFalsificationLedger` (bench/evidence.py) shipped 2026-08-08 with a full
test suite and no caller. A ledger nothing feeds records nothing, so the zero-
plant control's clean run produced an ABSENCE indistinguishable from a dispatch
failure or a document nobody read. These tests pin the wiring itself:

  * a REFUTED re-execution writes a ledger row DURING the gate's own pass;
  * CONFIRMED, ERROR and UNTOOLABLE write no row (but are counted, so the
    denominator stays honest);
  * a ledger nothing fed reports NEVER_INVOKED, never a confident zero;
  * the run report carries the section, including on a gate-disabled run;
  * `run_experiment` actually passes a ledger to the gate and attaches it.

The last one is the whole defect: every other property was already true of the
class in isolation, and none of it reached a run.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from bench.evidence import SurvivedFalsificationLedger
from bench.dm._types import Finding
from bench.reference_runner_v3 import (
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    apply_falsifier_verdicts,
    attach_survival_ledger,
    run_experiment,
)

REPORT_KEY = SurvivedFalsificationLedger.REPORT_KEY


def _mk(fid: str, sev: float, fcode: str, desc: str) -> Finding:
    return Finding(finding_id=fid, model_id="SIM-A", round_idx=0, flaw_class=2,
                   severity=sev, abstraction_index=0.5, description=desc,
                   falsifier_code=fcode)


def _gate_on() -> RunnerConfig:
    return RunnerConfig(falsifier_gate_enabled=True)


# ── a clean exit is recorded as a survival ───────────────────────────────────

def test_refuted_falsifier_writes_a_ledger_row_during_the_gate():
    reg = FindingRegistry()
    cid = reg.register(_mk("f1", 0.5, "assert True", "Section 3 states k = 0.30"),
                       "SIM-A")
    led = SurvivedFalsificationLedger(experiment="t03")

    apply_falsifier_verdicts(reg, 4, cfg=_gate_on(), repo_root=".", ledger=led)

    assert reg.entries[cid]["falsifier_verdict"] == "REFUTED"
    rows = led.entries
    assert len(rows) == 1, f"a clean exit must write exactly one row, got {rows}"
    row = rows[0]
    assert row.finding_id == cid
    assert row.claim_under_test == "Section 3 states k = 0.30"
    assert row.falsifier_code == "assert True"
    assert row.authored_by == "SIM-A"
    assert row.runner_verdict == "REFUTED"
    assert row.round_idx == 4
    assert row.still_standing is True
    assert led.distinct_claims_standing() == [cid]


def test_refuted_critical_is_recorded_even_though_the_gate_escalates_it():
    """The ledger records the RE-EXECUTION, not the gate's disposition.

    A critical clean exit is escalated to HIL (CONFIRM-only) and is NOT dropped
    — but it was still tested and it still stood, and that is exactly the
    positive record this ledger exists to keep.
    """
    reg = FindingRegistry()
    sev = CRITICAL_SEVERITY_THRESHOLD + 0.1
    cid = reg.register(_mk("f1", sev, "assert True", "critical claim"), "SIM-B")
    led = SurvivedFalsificationLedger(experiment="t03")

    apply_falsifier_verdicts(reg, 2, cfg=_gate_on(), repo_root=".", ledger=led)

    assert reg.entries[cid]["escalated"] is True
    assert len(led.entries) == 1
    assert led.weak_evidence(), "a critical survival must raise the weak-evidence band"


# ── everything else is counted and writes nothing ────────────────────────────

def test_confirmed_error_and_untoolable_write_no_rows_but_are_counted():
    reg = FindingRegistry()
    sev = CRITICAL_SEVERITY_THRESHOLD + 0.1
    ids = {
        "confirmed": reg.register(_mk("f1", sev, "assert False, 'defect'", "d1"), "SIM-A"),
        "error": reg.register(_mk("f2", sev, "import nonexistent_module_xyz", "d2"), "SIM-A"),
        "untoolable": reg.register(_mk("f3", sev, "", "d3"), "SIM-A"),
    }
    led = SurvivedFalsificationLedger(experiment="t03")

    apply_falsifier_verdicts(reg, 1, cfg=_gate_on(), repo_root=".", ledger=led)

    assert reg.entries[ids["confirmed"]]["falsifier_verdict"] == "CONFIRMED"
    assert reg.entries[ids["error"]]["falsifier_verdict"] == "ERROR"
    assert reg.entries[ids["untoolable"]]["falsifier_verdict"] == "UNTOOLABLE"

    assert led.entries == [], "no verdict here is a survival"
    assert led.observations == 3, "all three must still count in the denominator"
    tally = led.verdict_tally
    assert tally["CONFIRMED"] == 1 and tally["ERROR"] == 1 and tally["UNTOOLABLE"] == 1
    assert tally["REFUTED"] == 0

    section = led.report_section()
    assert section["status"] == "ACTIVE"
    assert section["standing_claims"] == 0
    assert any("NO SURVIVALS" in a for a in section["alarms"])
    assert not any("NEVER INVOKED" in a for a in section["alarms"])


def test_a_later_demonstration_overturns_an_earlier_survival_across_rounds():
    """Same finding, two rounds, two falsifiers: the row must not stay clean."""
    reg = FindingRegistry()
    cid = reg.register(_mk("f1", 0.5, "assert True", "claim"), "SIM-A")
    led = SurvivedFalsificationLedger(experiment="t03")

    apply_falsifier_verdicts(reg, 1, cfg=_gate_on(), repo_root=".", ledger=led)
    assert led.standing() and led.standing()[0].round_idx == 1

    # A stronger falsifier arrives and demonstrates the defect on round 2.
    reg.entries[cid]["status"] = "OPEN"
    reg.entries[cid]["falsifier_code"] = "assert False, 'real defect'"
    apply_falsifier_verdicts(reg, 2, cfg=_gate_on(), repo_root=".", ledger=led)

    assert reg.entries[cid]["falsifier_verdict"] == "CONFIRMED"
    assert led.standing() == [], "the survival was contradicted and must not stand"
    assert len(led.overturned()) == 1
    assert any("OVERTURNED" in a for a in led.report_section()["alarms"])


# ── an un-fed ledger says so ─────────────────────────────────────────────────

def test_gate_disabled_feeds_nothing_and_the_report_says_never_invoked():
    reg = FindingRegistry()
    reg.register(_mk("f1", 0.5, "assert True", "claim"), "SIM-A")
    led = SurvivedFalsificationLedger(experiment="t03")

    apply_falsifier_verdicts(
        reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=False), ledger=led)

    assert led.observations == 0
    result: dict = {}
    attach_survival_ledger(result, led)
    section = result[REPORT_KEY]
    assert section["status"] == "NEVER_INVOKED"
    assert section["standing_claims"] == 0
    assert any("NEVER INVOKED" in a for a in section["alarms"]), (
        "zero survivals and zero measurements must never render alike")


def test_report_carries_the_ledger_even_with_no_ledger_object():
    result = attach_survival_ledger({})
    assert REPORT_KEY in result
    assert result[REPORT_KEY]["status"] == "NEVER_INVOKED"


def test_report_section_carries_the_rows_and_their_caveat():
    reg = FindingRegistry()
    cid = reg.register(_mk("f1", 0.5, "assert True", "claim text"), "SIM-A")
    led = SurvivedFalsificationLedger(experiment="exp53_zero_plant")
    apply_falsifier_verdicts(reg, 3, cfg=_gate_on(), repo_root=".", ledger=led)

    result: dict = {"experiment": "exp53_zero_plant"}
    returned = attach_survival_ledger(result, led)
    assert returned is result
    section = result[REPORT_KEY]
    assert section["status"] == "ACTIVE"
    assert section["experiment"] == "exp53_zero_plant"
    assert section["standing_claims"] == 1
    assert section["distinct_claims_standing"] == [cid]
    assert section["rows"][0]["finding_id"] == cid
    assert section["not_proof_of_truth"] is True
    assert "NOT proof the claim is true" in section["meaning"]


# ── the wiring itself: run_experiment must do both halves ────────────────────

def _run_experiment_ast() -> ast.FunctionDef:
    src = Path(inspect.getsourcefile(run_experiment)).read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_experiment":
            return node
    raise AssertionError("run_experiment not found in the runner source")


def _calls_named(fn: ast.FunctionDef, name: str):
    return [n for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == name]


def test_run_experiment_passes_a_real_ledger_to_the_falsifier_gate():
    calls = _calls_named(_run_experiment_ast(), "apply_falsifier_verdicts")
    assert calls, "run_experiment must call the falsifier gate"
    fed = []
    for call in calls:
        for kw in call.keywords:
            if kw.arg == "ledger":
                assert not (isinstance(kw.value, ast.Constant)
                            and kw.value.value is None), (
                    "ledger=None is not wiring")
                fed.append(kw)
    assert fed, ("run_experiment calls the falsifier gate without a ledger — "
                 "every verdict of the run is invisible to the survival record")


def test_run_experiment_attaches_the_ledger_to_the_report():
    calls = _calls_named(_run_experiment_ast(), "attach_survival_ledger")
    assert calls, ("run_experiment must attach the survival ledger to the run "
                   "report, or the record never reaches a human")
