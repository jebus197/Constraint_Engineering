"""A machine-wide observer failure must not let a run converge verifying nothing.

`_integrity_violation_excluded` returns False for `integrity_unobserved`, and
its docstring states the safety property that depends on it: "a broken
sitecustomize would make EVERY falsifier return INTEGRITY_VIOLATION, and if
this predicate swallowed them all a run could CONVERGE with zero verified
criticals ... so `integrity_unobserved` entries keep blocking."

THE DEFECT (2026-10-03). They did not keep the A4 blocker blocking.
`_apply_routing`'s key-access branch carries `and not
e.get("integrity_unobserved")`, so an UNOBSERVED refusal fell through to the
`else` and was stamped `irreducible_escalation` -- which
`unverified_critical_count` skips BEFORE it calls the predicate. Measured by
driving the real function: 2 UNCONFIRMED criticals under a machine-wide
observer failure gave A4 = 0, irreducible queue 2 against a bound of 2 so the
alarm stayed silent, and an empty advisory. The carve-out never executed.

The 48-combination grid in test_one_predicate_excludes_and_reports could not
see it: the grid exercises the PREDICATE, and the defect is in a CONSUMER's
statement ordering.

THE FIX IS AT THE STAMP, NOT IN THE COUNTER. `irreducible_escalation` asserts
"a machine tried and failed"; when the observer never installed, no machine
tried. An unobserved refusal now joins the equipment-failure branch and is
stamped `routing_deferred`, which is what the 2026-09-07 "NEVER ASSESSED IS NOT
IRREDUCIBLE" repair established for every other no-reading verdict.

Run:  python3 -m pytest bench/tests/test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py -q
"""
from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import bench.routing as _routing          # noqa: E402
from bench import reference_runner_v3 as rr  # noqa: E402


class _Res:
    verdict = "ERROR"
    resolved = False
    model_used = "Codex"
    duplicate_of = None
    falsifier_code = ""
    rungs_tried = 1


@pytest.fixture
def drive(monkeypatch):
    """Run the REAL `_apply_routing` over one UNCONFIRMED critical."""
    def _route(finding, models, confirmed, resolve_fn, reverify, sim, **kw):
        # Reach a model, as a live ladder does, so the transport-dead guard
        # does not short-circuit the branch chain under test.
        for m in models:
            resolve_fn(m, finding)
        return _Res()

    monkeypatch.setattr(_routing, "route", _route)
    monkeypatch.setattr(rr, "dispatch_to_model",
                        lambda mc, p, s, enable_tools=False: ("", {}))

    def _go(**flags):
        e = {"status": "UNCONFIRMED", "severity": 0.9, "escalated": True,
             "description": "a claim", "source_model": "CC2",
             "falsifier_code": "assert False",
             "falsifier_verdict": "INTEGRITY_VIOLATION"}
        e.update(flags)
        reg = rr.FindingRegistry()
        reg.entries["C0001"] = e
        cfg = rr.RunnerConfig(routing_enabled=True)
        cfg.models = ["CC2", "Codex"]
        exp = SimpleNamespace(models=[SimpleNamespace(label="CC2"),
                                      SimpleNamespace(label="Codex")])
        rr._apply_routing(reg, 4, exp, cfg=cfg, repo_root=str(rr.REPO_ROOT))
        return e
    return _go


def test_the_verdict_is_in_neither_routable_set():
    """Why the else-branch was reachable at all. If this ever changes the
    branch ordering above must be re-derived rather than assumed."""
    assert rr.INTEGRITY_REFUSED_VERDICT not in rr.EQUIPMENT_FAILURE_VERDICTS
    assert rr.INTEGRITY_REFUSED_VERDICT not in rr.ROUTABLE_INSTRUMENT_FAULTS


def test_an_unobserved_refusal_is_not_called_ladder_exhausted(drive):
    e = drive(integrity_unobserved=True)
    assert not e.get("irreducible_escalation"), (
        "the observer never installed, so no machine tried and failed; "
        "`irreducible_escalation` asserts that it did")
    assert e.get("routing_deferred") is True
    assert "equipment failure" in (e.get("routing_defer_reason") or ""), (
        "the record must name the fault it actually observed")


def test_a_key_access_refusal_still_takes_the_reporting_branch(drive):
    """ANTI-VACUITY, and the founder's 2026-10-02 ruling. Without this the test
    above could pass because the routing loop never ran at all."""
    e = drive()
    assert e.get("integrity_refused") is True
    assert not e.get("irreducible_escalation")
    assert not e.get("routing_deferred")


def test_a_machine_wide_observer_failure_keeps_a4_blocking(drive):
    """THE SAFETY PROPERTY, measured at the bound where it used to fail."""
    e = drive(integrity_unobserved=True)
    bound = rr.RunnerConfig().max_irreducible_queue
    reg = rr.FindingRegistry()
    for i in range(bound):                 # a queue AT the bound: alarm silent
        reg.entries[f"C{i:04d}"] = dict(e)
    assert reg.irreducible_queue_count() <= bound, (
        "this fixture must sit below the alarm, or A4 is not the thing on test")
    assert reg.unverified_critical_count() == bound, (
        "a run with zero verified criticals and a dead observer can converge")


def test_a_genuinely_exhausted_ladder_is_still_irreducible(drive):
    """THE CAPABILITY THAT MUST NOT BE REMOVED. A critical whose ladder really
    did run out still earns the HIL stamp; only the unobserved case moved."""
    e = drive(falsifier_verdict="NON_RESOLVING_VERDICT")
    assert e.get("irreducible_escalation") is True
    assert e.get("hil_escalated") is True
