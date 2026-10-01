"""An INFERRED route must not be reported as a recorded escalation.

FREE PANEL, 2026-10-01, Q1. `bench/claim_ledger.py` promises in its own
docstring that "'nothing decided this' and 'a human was asked' are
distinguishable". `claim_from_entry` inferred the route from `finding_category`
and read no escalation field at all -- the comment beside it cites
`hil_escalated`, which only `bench/reference_runner.py` writes, while v3 entries
carry `escalated`. Over every archived run, 1978 of 2059 routed claims were
reported as HIL with no recorded escalation (96.0660%, Wilson 95%
[95.1370%, 96.8235%], statsmodels and mpmath agreeing to 1.1e-16).

THE ROUTE IS UNCHANGED BY THE FIX, DELIBERATELY. `test_claim_ledger_2026-10-01.py`
asserts the HIL default twice; an oracle is not something a fix gets to edit.
What is added is provenance, so the assumption is visible.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bench.claim_ledger import (  # noqa: E402
    ROUTE_HIL,
    ROUTE_INFERRED,
    ROUTE_RECORDED,
    ROUTE_SOURCES,
    Claim,
    ClaimLedger,
    claim_from_entry,
    ledger_from_registry,
)

ARCHIVE = ROOT / "bench" / "logs"


@pytest.mark.parametrize("field", ["hil_escalated", "escalated"])
def test_a_recorded_escalation_on_either_runner_reads_as_recorded(field):
    """BOTH runners' spellings count. v2 writes one, v3 the other."""
    c = claim_from_entry("C1", {"description": "d", field: True})
    assert c.decidable is False
    assert c.routed_to == ROUTE_HIL
    assert c.route_source == ROUTE_RECORDED, (
        f"{field}=True was not read as a recorded escalation")


@pytest.mark.parametrize("entry", [
    {"description": "d"},
    {"description": "d", "escalated": False},
    {"description": "d", "escalated": None},
    {"description": "d", "hil_escalated": False},
])
def test_no_recorded_escalation_reads_as_inferred(entry):
    c = claim_from_entry("C1", dict(entry))
    assert c.routed_to == ROUTE_HIL, "the route itself must not have moved"
    assert c.route_source == ROUTE_INFERRED, (
        f"an assumed route was reported as recorded: {entry!r}")


def test_a_decidable_claim_has_no_route_and_no_provenance():
    c = claim_from_entry("C1", {"description": "d",
                                "falsifier_code": "assert True",
                                "escalated": True})
    assert c.decidable is True
    assert c.routed_to == "" and c.route_source == ""


def test_the_report_carries_the_provenance_and_it_adds_up():
    led = ledger_from_registry({
        "C1": {"description": "a"},                            # inferred
        "C2": {"description": "b", "escalated": True},          # recorded
        "C3": {"description": "c", "falsifier_code": "assert 1"},  # decidable
    }, target="t")
    rep = led.report()
    assert set(rep["by_route_source"]) == set(ROUTE_SOURCES)
    assert rep["by_route_source"] == {ROUTE_RECORDED: 1, ROUTE_INFERRED: 1}
    assert rep["routes_inferred"] == 1
    assert sum(rep["by_route_source"].values()) == rep["routed"], (
        "every routed claim must have a provenance")
    assert rep["informative_only"] is True, (
        "v1 must stay informative-only; a channel that moves a verdict is a "
        "different thing from the one the seats designed")


@pytest.mark.skipif(not ARCHIVE.is_dir(), reason="no archive in this clone")
def test_provenance_agrees_with_the_entry_across_the_whole_archive():
    """The real population, not a constructed one."""
    routed = inferred = 0
    for f in sorted(ARCHIVE.glob("*/runner_state.json")):
        try:
            ents = (json.loads(f.read_text(encoding="utf-8")).get("registry")
                    or {}).get("entries") or {}
        except Exception:                                      # noqa: BLE001
            continue
        for cid, e in (ents or {}).items():
            if not isinstance(e, dict):
                continue
            c = claim_from_entry(cid, e)
            if c.decidable:
                continue
            routed += 1
            recorded = bool(e.get("hil_escalated") or e.get("escalated"))
            assert c.route_source == (ROUTE_RECORDED if recorded
                                      else ROUTE_INFERRED), cid
            inferred += 0 if recorded else 1
    if routed:
        assert inferred > 0, (
            "no inferred route anywhere would mean the archive changed shape; "
            "re-measure before trusting this guard")


class TestTheDiscardedCounterCanActuallyFire:
    """`discarded: 0` must be a measurement, not a tautology.

    THE CRITICISM, from the cc2 seat in the free day-review panel of
    2026-10-01, and it is the project's own dominant defect class turned on
    this module: *"its own alarm cannot fire. `discarded` is structurally
    unreachable: `claim_from_entry` always supplies a route and
    `__post_init__` back-fills `ROUTE_HIL`, so across 48 swept entry shapes, 0
    yield a discarded claim. `discarded: 0` is a tautology printed as a
    measurement -- an addition nothing reaches."*

    That is correct, and the answer is NOT to delete the counter. It is a
    defensive invariant: the March 2026 one-character near-miss was a routed
    claim silently becoming a discarded one, and a counter that would catch a
    future code path building a `Claim` by another route is worth keeping. What
    was missing is proof that it CAN fire, which is what makes the 0 evidence
    rather than arithmetic.

    So these tests reach past `__post_init__` deliberately -- which is the only
    way such a claim can exist -- and assert the counter notices.
    """

    def _unrouted(self):
        """A claim that is neither decidable nor routed, built past the guard."""
        c = Claim(tag="C9", statement="unreachable by the normal path")
        object.__setattr__(c, "routed_to", "")      # undo the back-fill
        return c

    def test_the_counter_fires_on_a_claim_that_is_neither_decided_nor_routed(self):
        led = ClaimLedger("t")
        led.add(self._unrouted())
        assert len(led.discarded()) == 1, (
            "the discarded counter cannot fire even when a discarded claim "
            "exists, so `discarded: 0` is a tautology rather than a result")
        assert led.report()["discarded"] == 1

    def test_the_normal_path_still_cannot_produce_one(self):
        """The invariant the counter guards: `__post_init__` routes by default."""
        led = ClaimLedger("t")
        led.add(Claim(tag="C1", statement="no falsifier here"))
        led.add(claim_from_entry("C2", {"description": "x"}))
        assert led.discarded() == [], (
            "a claim built by the ordinary path is unrouted, which breaks the "
            "guarantee that a claim is never silently dropped")
        assert all(c.routed_to for c in led.routed())

    def test_a_decidable_claim_is_not_counted_as_discarded(self):
        """ANTI-FALSE-POSITIVE: decidable claims legitimately carry no route."""
        led = ClaimLedger("t")
        led.add(Claim(tag="C1", statement="2+2=5", decidable=True,
                      falsifier="assert 2 + 2 == 5"))
        assert led.discarded() == []
