#!/usr/bin/env python3
"""Would promoting the section 7.7 severity specification to DECIDING reach anything?

WHY THIS EXISTS, AND IT IS THE PREDICATE-FIRST QUESTION. The founder ruled on
2026-10-15 that a mechanism must not be run in shadow during a simulated run:
*"why run them in shadow in a simulated run, when the purpose of a simulated run
is to test how they will behave in a real experiment and to fix any
deficiencies/issues you encounter so that we don't run into those same issues in
a paid run, and risk pointlessly burning money we don't have?"*

So the severity specification shadow is to be PROMOTED before the 2nd free run.
Before building that, this script asks whether the promotion would change any
decision at all -- because the A4 counter's severity door is CONJUNCTIVE:

    release  <=>  severity < 0.7  AND  severity_is_proven(entry)

The promotion lowers the severity (by the verification factor V), which can only
ever make the FIRST half easier. If `severity_is_proven` is almost never true,
the promotion is an addition nothing reaches -- the half of the additive standard
this project has tripped over 11 times since 2026-08-01.

MEASURED OVER THE WHOLE ARCHIVE. Every `runner_state.json` and every finding
registry the archive holds, read through the runner's own predicates.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from statsmodels.stats.proportion import proportion_confint      # noqa: E402
from scipy.stats import beta as scipy_beta                       # noqa: E402

import reference_runner_v3 as rr                                 # noqa: E402

CRIT = rr.CRITICAL_SEVERITY_THRESHOLD


def interval(k: int, n: int) -> str:
    if n == 0:
        return "n=0"
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_cp = 0.0 if k == 0 else float(scipy_beta.ppf(0.025, k, n - k + 1))
    hi_cp = 1.0 if k == n else float(scipy_beta.ppf(0.975, k + 1, n - k))
    return (f"{100.0 * k / n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%]"
            f"  Clopper-Pearson [{100*lo_cp:.4f}%, {100*hi_cp:.4f}%]")


def _v_factor(entry: dict) -> float:
    """Section 7.7's V, from THIS harness's own falsifier verdict."""
    verdict = str(entry.get("falsifier_verdict") or "").strip().upper()
    if verdict == "CONFIRMED":
        return 1.0
    if verdict == "REFUTED":
        return 0.0
    return 0.5


def _states():
    seen = set()
    for p in sorted(REPO.glob("bench/logs/**/runner_state.json")):
        if "sandbox_harvest" in str(p) or "/seat_evidence/" in str(p):
            continue
        if p.resolve() in seen:
            continue
        seen.add(p.resolve())
        yield p


def main() -> int:
    entries = []
    runs = 0
    for path in _states():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        # ★ THE KEY IS `registry.entries`, AND THE FIRST VERSION GUESSED
        # `finding_registry`, FINDING 0 ENTRIES ACROSS 59 RUNS. The existing
        # shadow reads 3,298, so 0 was an instrument result and not an archive
        # result -- check the predicate before believing an empty answer.
        # Read from `scripts/the_verification_factor_shadow_2026-10-12.py:75`,
        # which is the producer already committed against this archive.
        reg = ((data or {}).get("registry") or {}).get("entries") or {}
        if not isinstance(reg, dict):
            continue
        runs += 1
        for cid, e in reg.items():
            if isinstance(e, dict):
                entries.append((path.parent.name, cid, e))

    print("=" * 78)
    print("WOULD THE SEVERITY PROMOTION REACH ANY DECISION?")
    print("=" * 78)
    print(f"runs read: {runs}   entries: {len(entries)}")

    scored = [(r, c, e) for r, c, e in entries
              if isinstance(e.get("severity"), (int, float))]
    print(f"entries carrying a numeric severity: {len(scored)} of {len(entries)}"
          f" — {interval(len(scored), len(entries))}")

    proven = [(r, c, e) for r, c, e in scored if rr.severity_is_proven(e)]
    print(f"\nseverity_is_proven TRUE: {len(proven)} of {len(scored)} — "
          f"{interval(len(proven), len(scored))}")
    if not proven:
        print("  ★ THE CONJUNCTIVE DOOR IS SHUT ON THE ARCHIVE: the promotion "
              "could not change a single A4 release, because the proof half of "
              "the condition never holds. Promoting it as an A4 severity would "
              "be an addition nothing reaches.")

    # Where the promotion WOULD bite if the proof door were open.
    a4 = [(r, c, e) for r, c, e in scored if e.get("status") == "UNCONFIRMED"]
    print(f"\nUNCONFIRMED entries (the A4 population): {len(a4)} of {len(scored)}"
          f" — {interval(len(a4), len(scored))}")
    would_cross = [(r, c, e) for r, c, e in a4
                   if float(e["severity"]) >= CRIT
                   and float(e["severity"]) * _v_factor(e) < CRIT]
    print(f"  of those, asserted-critical that the specification makes "
          f"sub-critical: {len(would_cross)} of {len(a4)} — "
          f"{interval(len(would_cross), len(a4))}")
    both = [t for t in would_cross if rr.severity_is_proven(t[2])]
    print(f"  AND proven, so actually released: {len(both)} of {len(would_cross)}"
          f" — {interval(len(both), len(would_cross))}")

    print("\nV-FACTOR DISTRIBUTION over the A4 population:")
    dist = collections.Counter(_v_factor(e) for _r, _c, e in a4)
    for v in (1.0, 0.5, 0.0):
        print(f"  V={v}: {dist[v]:>5} — {interval(dist[v], len(a4))}")

    print("\nTHE KEY PROPERTY of section 7.7 (a disproved finding scores 0):")
    refuted = [(r, c, e) for r, c, e in scored if _v_factor(e) == 0.0]
    violations = [t for t in refuted if float(t[2]["severity"]) != 0.0]
    print(f"  disproved findings: {len(refuted)}; carrying a non-zero severity: "
          f"{len(violations)} — {interval(len(violations), len(refuted))}")

    print("\n" + "=" * 78)
    print("CONCLUSION, STATED AS A PREDICATE RESULT RATHER THAN A PLAN:")
    if not proven:
        print("  Promoting the specification INSIDE the A4 severity door changes")
        print("  0 decisions on the archive. The door is `sub-critical AND proven`,")
        print("  and the proof half holds for 0 entries. The promotion that WOULD")
        print("  reach decisions is at the sites that read severity WITHOUT the")
        print("  proof conjunction — the halt bound, the critical-count reporting")
        print("  and the settled-novelty series — and that is a wider change than")
        print("  the A4 door.")
    else:
        print(f"  {len(both)} A4 releases would change. The promotion is reached.")
    print("=" * 78)
    return 0


def _answer_help_without_measuring(doc: str) -> None:
    """A `--help` MUST NEVER COST ANYTHING, and that is a founder-standing rule:
    15 of 17 runners once billed a live dispatch on any unrecognised argument.
    This script's measurement is free, but the rule is about the SHAPE: a flag
    that silently runs the whole measurement is indistinguishable from a flag
    that silently spends. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`.
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(doc or "").strip().splitlines()[0] if doc else None,
        epilog="Takes no arguments: run it with none to produce the measurement.",
    )
    ap.parse_args()


if __name__ == "__main__":
    _answer_help_without_measuring(__doc__)
    raise SystemExit(main())
