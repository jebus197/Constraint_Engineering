#!/usr/bin/env python3
"""Measurement 10 is answerable now, and its checker is not vacuous.

WHY THE MEASUREMENT HAD NO SCRIPT, which was upstream of the script. The
programme of study lists measurement 10 -- does what the launcher DECLARES match
what actually FIRES -- as having no committed producer. Nothing recorded the
declaration: `bench/tools/run_simulated_experiment.py` wrote the runner's
results and not one field of the config that produced them. Measured by
`scripts/declared_vs_observed_2026-10-03.py --all` on 2026-10-03: 81 archived
reports, 0 carrying a declaration. Writing a comparison script without fixing
that would have produced a checker that reports agreement on an empty set.

SO THE TWO THINGS THESE TESTS HOLD ARE: the launcher records its declaration,
and the checker CAN return DISAGREE. The second is the one that matters -- a
checker that cannot fail is the defect class this project has recorded
repeatedly, and an UNOBSERVABLE verdict must never be counted as agreement.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import types

REPO = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "declared_vs_observed_2026-10-03.py"
LAUNCHER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def _mod() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("dvo_under_test", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def _report(**over) -> dict:
    rep = {
        "_declared_config": {"extension_cap": 8, "pattern": "four_layer",
                             "topology": "star", "sk_score_prose_listings": True,
                             "fix_efficacy_mode": "record",
                             "discrimination_control_blocks": False,
                             "gamma_alt_threshold": 0.30},
        "pattern": "four_layer", "topology": "star",
        "gamma_critical_history": [0.0, 0.1, 0.4],
        "convergence_reason": "gamma_critical 0.4 >= 0.3",
        "registry": {"entries": {}},
    }
    rep.update(over)
    return rep


def test_the_launcher_records_its_declaration():
    src = LAUNCHER.read_text(encoding="utf-8")
    assert 'result["_declared_config"]' in src, (
        "the launcher does not record the config it was built with, so "
        "measurement 10 has nothing to compare against")
    assert 'result["_declared_argv"]' in src, (
        "the argv that produced the run is not recorded")
    assert "credential pattern" in src, (
        "nothing filters credential-shaped field names out of the recorded "
        "declaration")


def test_a_report_without_a_declaration_is_unobservable_not_agreement():
    m = _mod()
    res = m.check({"registry": {"entries": {}}})
    assert len(res) == 1 and res[0]["verdict"] == m.UNOBSERVABLE, (
        f"a report with no declaration produced a verdict: {res}")


def test_a_matching_run_agrees():
    m = _mod()
    res = {c["check"]: c["verdict"] for c in m.check(_report())}
    assert res["rounds_within_cap"] == m.AGREE
    assert res["pattern_fired"] == m.AGREE
    assert res["topology_fired"] == m.AGREE
    assert m.DISAGREE not in res.values(), f"a clean run disagreed: {res}"


def test_more_rounds_than_the_cap_is_caught():
    """ANTI-VACUITY 1: the checker must be able to say DISAGREE."""
    m = _mod()
    rep = _report(gamma_critical_history=[0.0] * 9)   # cap is 8
    res = {c["check"]: c["verdict"] for c in m.check(rep)}
    assert res["rounds_within_cap"] == m.DISAGREE, (
        f"9 rounds against a declared cap of 8 was not caught: {res}")


def test_a_pattern_that_did_not_fire_is_caught():
    """ANTI-VACUITY 2: a declaration contradicted by the run's own record."""
    m = _mod()
    rep = _report(pattern="two_layer")
    res = {c["check"]: c["verdict"] for c in m.check(rep)}
    assert res["pattern_fired"] == m.DISAGREE


def test_blocking_declared_off_but_applied_is_caught():
    """ANTI-VACUITY 3: the check that would catch a back-door arming.

    This is not hypothetical. On 2026-10-03 a fix withheld `verified` on a
    voided instrument with blocking declared OFF, which the project's own
    oracles identified as the blocking behaviour. A declared-vs-observed check
    is the run-level instrument for exactly that mistake.
    """
    m = _mod()
    rep = _report(registry={"entries": {
        "C0001": {"falsifier_verdict": "NON_DISCRIMINATING",
                  "status": "UNCONFIRMED"}}})
    res = {c["check"]: c for c in m.check(rep)}
    assert res["blocking_fired"]["verdict"] == m.DISAGREE, (
        f"a demotion under declared-off blocking was not caught: "
        f"{res['blocking_fired']}")
    assert "demoted anyway" in res["blocking_fired"]["note"]


def test_blocking_declared_on_but_not_applied_is_caught():
    """The other direction: declared armed, nothing demoted."""
    m = _mod()
    rep = _report(registry={"entries": {
        "C0001": {"falsifier_verdict": "NON_DISCRIMINATING",
                  "status": "CONFIRMED"}}})
    rep["_declared_config"]["discrimination_control_blocks"] = True
    res = {c["check"]: c for c in m.check(rep)}
    assert res["blocking_fired"]["verdict"] == m.DISAGREE
    assert "stayed terminal" in res["blocking_fired"]["note"]


def test_the_archive_state_is_reported_honestly(tmp_path):
    """The script must say that nothing can be compared yet, and not imply pass."""
    import subprocess
    p = subprocess.run([sys.executable, str(SCRIPT), "--all"],
                       capture_output=True, text=True, cwd=str(REPO),
                       timeout=600)
    assert p.returncode == 0
    assert "unobservable is NEVER counted as agreement" in p.stdout, (
        "the output does not state that unobservable is not agreement")
