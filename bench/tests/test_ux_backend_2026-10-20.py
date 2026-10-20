"""The UX backend projects harness state and enforces the pack's 2 rules.

HIS INSTRUCTION, 2026-10-20: "you can build the UX backend, so that the eventual
UX can map cleanly on to it", and on the pack: "you have the ability to look at
the code and decide on sane choices, rather than run verbatim".

THE TWO RULES ARE ENFORCED RATHER THAN DECORATED. The pack asks for a banner
reading "Discussion cannot clear claims" and states "Humans accept residual;
models do not clear by prose". The harness already records what settled every
status, so these are checkable. Measured 2026-10-20 over 62 archived runs and
3,237 findings: 0 clearance violations, Wilson [0.0000%, 0.1185%]. The rule
already holds; this makes a regression visible.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD = ROOT / "bench" / "ux_backend_2026-10-20.py"


def _ux():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("_ux", MOD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_ux"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def ux():
    return _ux()


@pytest.fixture(scope="module")
def a_run(ux):
    rs = ux.runs()
    if not rs:
        pytest.skip("no archived runs in this checkout")
    for r in reversed(rs):
        try:
            if ux._findings(ux.load(r)):
                return r
        except Exception:                                      # noqa: BLE001
            continue
    pytest.skip("no archived run carries findings")


# ── the shell matches what he ruled ────────────────────────────────────────

def test_the_tab_set_is_the_readme_chrome_with_discourse_renamed(ux):
    """His instruction: "The discussions section should simply be named
    "Discourse"". The README names 01_orchestrator.jpg as the canonical chrome;
    02_findings.jpg shows a different shell entirely and he warned the pack is
    rough, so the README wins."""
    assert ux.TABS == ("Orchestrator", "Findings", "Evidence", "Explorer",
                       "Discourse", "Recipes", "Advanced", "HIL")
    assert "Discussions" not in ux.TABS


def test_light_is_the_default_and_dark_exists(ux):
    """His instruction: "Some screens are done in dark mode (and thee probably
    should be a dark mode), but by default they should all be in light mode"."""
    s = ux.shell()
    assert s["default_theme"] == "light"
    assert "dark" in s["themes"]


def test_simple_and_advanced_modes_both_exist(ux):
    """His instruction: "There should also probably be a simple and advanced
    mode"."""
    assert set(ux.shell()["modes"]) == {"simple", "advanced"}


def test_discourse_is_in_shell_and_carries_his_stem_areas(ux):
    """His instruction: "the Discourse resource will be an integrated tab along
    the top with the other tabs, not a standalone/separate resource", and the
    pack's area list verbatim."""
    d = ux.discourse()
    assert d["in_shell"] is True
    assert d["name"] == "Discourse"
    for area in ("Mathematics", "Physics", "Chemistry", "Biology", "Software",
                 "Engineering", "Statistics", "Cross-domain",
                 "Protocol & residual risk", "Registry & tooling"):
        assert area in d["areas"], f"the pack names {area} and it is missing"


# ── the 2 rules, enforced ──────────────────────────────────────────────────

def test_no_claim_in_any_archived_run_was_cleared_by_prose(ux):
    """THE RULE. Measured over the whole archive rather than one run, because a
    violation anywhere is a claim settled by something that may not settle one."""
    bad, runs_seen, findings_seen = [], 0, 0
    for r in ux.runs():
        try:
            st = ux.load(r)
        except Exception:                                      # noqa: BLE001
            continue
        runs_seen += 1
        findings_seen += len(ux._findings(st))
        bad += [{**v, "run": r} for v in ux.clearance_violations(st)]
    if not runs_seen:
        pytest.skip("no archived runs in this checkout")
    assert findings_seen >= 100, (
        f"only {findings_seen} findings across {runs_seen} runs; the check is "
        f"too thin to mean anything")
    assert not bad, (
        f"{len(bad)} claim(s) were cleared by something that is neither a tool, "
        f"the runner, nor a human: {bad[:3]}")


def test_a_model_clearing_a_claim_is_refused(ux):
    """EXECUTED AGAINST A CONSTRUCTED STATE, because the archive contains no
    violation and a guard that only ever sees clean data cannot show it would
    object. This is the mutation the rule exists to catch."""
    state = {"registry": {"entries": [{
        "canonical_id": "C9001",
        "status_log": [{"from": "OPEN", "to": "CONFIRMED", "round": 1,
                        "adjudicator": "model", "evidence": "it looks right to me"}],
    }]}}
    bad = ux.clearance_violations(state)
    assert len(bad) == 1, "a model clearing a claim by prose was not refused"
    assert bad[0]["finding"] == "C9001"
    assert ux.CLEARANCE_BANNER in bad[0]["why"]


def test_a_model_may_still_contest(ux):
    """CONTESTED is the one move a seat is allowed. All 5 model transitions in
    the archive go there, and refusing them would break the dispute path."""
    state = {"registry": {"entries": [{
        "canonical_id": "C9002",
        "status_log": [{"from": "CONFIRMED", "to": "CONTESTED", "round": 1,
                        "adjudicator": "model"}],
    }]}}
    assert ux.clearance_violations(state) == []


def test_the_runner_and_a_tool_may_both_settle(ux):
    """Both are code. Measured: `tool` 177 transitions and `runner` 34 in one
    run alone, so refusing either would report the whole archive as violating."""
    for who in ("tool", "runner", "human", "hil"):
        state = {"registry": {"entries": [{
            "canonical_id": "C9003",
            "status_log": [{"from": "OPEN", "to": "CONFIRMED", "adjudicator": who}],
        }]}}
        assert ux.clearance_violations(state) == [], f"{who} was refused"


def test_the_check_reads_the_log_not_the_summary_field(ux):
    """A claim cleared by prose and later re-stamped by a tool passes a check on
    `status_adjudicator`, which holds only the latest, and must fail this one."""
    state = {"registry": {"entries": [{
        "canonical_id": "C9004",
        "status_adjudicator": "tool",
        "status_log": [
            {"from": "OPEN", "to": "CONFIRMED", "adjudicator": "model"},
            {"from": "CONFIRMED", "to": "CLOSED", "adjudicator": "tool"},
        ],
    }]}}
    bad = ux.clearance_violations(state)
    assert len(bad) == 1, (
        "the prose clearance was hidden behind a later tool stamp, which is "
        "exactly what reading the summary field would miss")


# ── the projections are derived, not invented ──────────────────────────────

def test_residual_bands_are_derived_and_absent_severity_is_not_low(ux):
    assert ux.residual_band(0.9) == "High"
    assert ux.residual_band(0.7) == "High"
    assert ux.residual_band(0.5) == "Med"
    assert ux.residual_band(0.1) == "Low"
    assert ux.residual_band(None) == "UNKNOWN", (
        "a missing severity was banded as Low, which the mock-up labels "
        "'acceptable residual' -- that is a claim, not a default")
    assert ux.residual_band("not a number") == "UNKNOWN"


def test_tools_are_read_from_the_falsifier_source(ux):
    """A declared tool list would be a second description of one fact."""
    assert ux.tools_used({"falsifier_code": "import sympy\nimport z3"}) == ["SymPy", "Z3"]
    assert ux.tools_used({"falsifier_code": "from scipy import stats"}) == ["SciPy"]
    assert ux.tools_used({}) == []


def test_a_voided_verification_is_not_shown_as_tool_confirmed(ux):
    """The discrimination control voids a falsifier that fires against correct
    code too. Showing that as tool-confirmed would present a void as a pass."""
    f = {"status": "CLOSED", "status_adjudicator": "tool", "verified": True,
         "verification_voided": True}
    assert ux.display_status(f) == "closed"
    f2 = dict(f, verification_voided=False)
    assert ux.display_status(f2) == "tool-confirmed"


def test_hil_takes_precedence_over_every_other_status(ux):
    f = {"status": "CLOSED", "verified": True, "hil_escalated": True}
    assert ux.display_status(f) == "HIL"


def test_every_view_runs_against_a_real_archived_run(ux, a_run):
    """EXECUTED against real state, not a fixture. A projection that only works
    on constructed data is not a projection."""
    o = ux.orchestrator(a_run)
    assert o["run"] == a_run
    assert o["clearance_violations"] == 0
    rows = ux.findings(a_run)
    assert rows, "no findings projected from a run that has them"
    for r in rows:
        assert r["status"] in ("open", "closed", "tool-confirmed", "HIL")
        assert r["residual"] in ("Low", "Med", "High", "UNKNOWN")
    ev = ux.evidence(a_run, rows[0]["id"])
    assert ev["id"] == rows[0]["id"]
    ex = ux.explorer(a_run)
    assert ex["rounds"] == len(ex["gamma"])
    q = ux.hil(a_run)
    assert set(q["actions"]) == {"approve_fix", "reject", "request_evidence"}


def test_a_missing_run_says_so_rather_than_returning_an_empty_view(ux):
    """An empty view reads as 'nothing found'; a missing run is a different fact."""
    with pytest.raises(ux.NoSuchRun):
        ux.orchestrator("no_such_run_2026-10-20")
