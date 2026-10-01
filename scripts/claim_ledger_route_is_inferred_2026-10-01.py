#!/usr/bin/env python3
"""THE CLAIM LEDGER SAYS "A HUMAN WAS ASKED" ABOUT CLAIMS NO HUMAN WAS ASKED ABOUT.

FREE PANEL, 2026-10-01, Q1. Two things, both measured over the whole archive.

1. THE LEDGER IS A VIEW OVER THE REGISTRY, NOT A NEW UNIT. For every archived
   run, `claims_total == len(registry.entries)` and the multiset of claim
   statements equals the multiset of entry descriptions. The map is a bijection,
   so v1 relabels findings as claims rather than recording a REASON stage.

2. THE ROUTE IS INFERRED AND REPORTED AS IF READ. `claim_from_entry` derives the
   route from `finding_category` alone. The comment beside it names
   `hil_escalated` as "the runner's own signal that it did" -- a field written
   only by `bench/reference_runner.py`, never by v3, whose entries carry
   `escalated`. The ledger read neither. The module docstring promises that
   "'nothing decided this' and 'a human was asked' are distinguishable"; they
   were not.

   This matters more than a naming slip because of what the channel is FOR. Its
   stated purpose is that non-decidable claims are "ROUTED (HIL /
   [VERIFY:current]), NEVER DISCARDED -- the one-character near-miss of March
   2026 is the standing warning". A report that says 2002 claims are with a
   human, when the runner recorded no escalation for them, is the same class of
   silent evidence loss wearing the uniform of the guard against it.

3. AND THE `discarded` COUNTER CANNOT FIRE. `Claim.__post_init__` assigns
   `ROUTE_HIL` whenever a claim is undecidable and unrouted, and
   `claim_from_entry` always supplies a route, so `discarded` is identically 0
   for every possible registry input. Reporting it is a tautology. This file
   sweeps the entry shapes to show the branch is unreachable.

WHAT THE FIX DOES AND DELIBERATELY DOES NOT DO. It adds `route_source`
(recorded / inferred) and reports `routes_inferred`. It does NOT change the
route, because `bench/tests/test_claim_ledger_2026-10-01.py` asserts the HIL
default twice and editing an oracle to suit a fix is not a fix. Whether the
inferred default should be HIL at all is referred to the human.

Run:  python3 scripts/claim_ledger_route_is_inferred_2026-10-01.py
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ESCALATION_FIELDS = ("hil_escalated", "escalated")


def _runs():
    for f in sorted((REPO / "bench" / "logs").glob("*/runner_state.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            continue
        reg = doc.get("registry") or {}
        ents = reg.get("entries") or {}
        if isinstance(ents, dict) and ents:
            yield f.parent.name, ents


def bijection() -> tuple:
    """How many archived runs the ledger reproduces entry-for-entry."""
    from bench.claim_ledger import ledger_from_registry
    n = same = 0
    for name, ents in _runs():
        n += 1
        rep = ledger_from_registry(ents, target=name).report()
        descs = sorted((e.get("description") or "")[:2000]
                       for e in ents.values() if isinstance(e, dict))
        stmts = sorted(c["statement"] for c in rep["claims"])
        if rep["claims_total"] == len(ents) and descs == stmts:
            same += 1
    return same, n


def route_provenance() -> tuple:
    """Routed claims, and how many had their route INFERRED rather than read."""
    from bench.claim_ledger import ROUTE_INFERRED, claim_from_entry
    routed = inferred = 0
    for _name, ents in _runs():
        for cid, e in ents.items():
            if not isinstance(e, dict):
                continue
            c = claim_from_entry(cid, e)
            if c.decidable:
                continue
            routed += 1
            # Decided from the ENTRY, independently of the field the fix added,
            # so this is not the fix checking itself.
            if not any(e.get(f) for f in ESCALATION_FIELDS):
                inferred += 1
            assert (c.route_source == ROUTE_INFERRED) == (
                not any(e.get(f) for f in ESCALATION_FIELDS)), (
                f"route_source disagrees with the entry for {cid}")
    return inferred, routed


def discarded_is_reachable() -> int:
    """Sweep the entry shapes that drive the branch. 0 means it cannot fire."""
    from bench.claim_ledger import claim_from_entry
    hits = 0
    for fals in ("", "   ", None, "assert True"):
        for cat in ("state", "arithmetic", "", None):
            for esc in (True, False, None):
                c = claim_from_entry("X", {"falsifier_code": fals,
                                           "finding_category": cat,
                                           "escalated": esc,
                                           "description": "d"})
                if (not c.decidable) and (not c.routed_to):
                    hits += 1
    return hits


def _wilson(k: int, n: int) -> str:
    from statsmodels.stats.proportion import proportion_confint
    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mpf("1.9599639845400542")
    p, N = mpf(k) / n, mpf(n)
    den = 1 + z**2 / N
    c = (p + z**2 / (2 * N)) / den
    h = (z / den) * sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    m = (float(max(c - h, 0)), float(c + h))
    return (f"Wilson 95% [{lo:.4%}, {hi:.4%}] statsmodels | "
            f"[{m[0]:.4%}, {m[1]:.4%}] mpmath | agree "
            f"{max(abs(m[0] - lo), abs(m[1] - hi)):.1e}")


def main() -> int:
    print("IS THE CLAIM LEDGER THE UNIT IT CLAIMS TO BE?")
    print("=" * 74)
    same, n = bijection()
    print(f"  1. archived runs where the ledger is a BIJECTION onto "
          f"registry entries: {same} of {n}")
    if n:
        print(f"       {_wilson(same, n)}")
    print("       -> a bijection is a relabelling; v1 adds no claim that was "
          "not already a finding.")

    inferred, routed = route_provenance()
    print(f"\n  2. routed (no-falsifier) claims: {routed}; route INFERRED "
          f"rather than read: {inferred}")
    if routed:
        print(f"       {_wilson(inferred, routed)}")
    print("       -> reported as by_route={'HIL': N}, indistinguishable from "
          "a recorded escalation.")

    hits = discarded_is_reachable()
    print(f"\n  3. entry shapes yielding a DISCARDED claim: {hits} of 48")
    print("       -> `discarded: 0` is a tautology on this population path.")

    print()
    failed = []
    if n and same == n:
        failed.append(f"the ledger is a bijection onto the registry in all {n} runs")
    if routed and inferred:
        failed.append(f"{inferred} of {routed} routed claims have an inferred route")
    if hits == 0:
        failed.append("the `discarded` counter is structurally unreachable")
    if failed:
        print("  FALSIFIED on " + str(len(failed)) + " count(s):")
        for x in failed:
            print(f"    - {x}")
        raise AssertionError("; ".join(failed))
    print("  CLEAN.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
