#!/usr/bin/env python3
"""Can a pre-registration detect 'not functioning as expected' DURING a run?

HIS DEFINITION, 2026-11-02, verbatim: *"'Scewy' simply means not functioning as
expected."* (His "Scewy" is "screwy".) B20 names the monitoring judgement `cy`
encodes as its highest-risk arm precisely because no rule said what screwy meant,
and his definition supplies one: a comparison against a STATED EXPECTATION.

CC1'S PROPOSAL, MADE EARLIER TODAY AND TESTED HERE RATHER THAN SHIPPED: score the
pre-registration DURING the run, because the pre-registration files are the
project's expectation store and both the store and its scorer already exist. It
was logged against B20 as a composability claim REQUIRING a measurement, which is
his own standard, and this script is that measurement.

THE HYPOTHESIS: mid-run pre-registration scoring would catch divergences the
watchdog's absence detectors miss.

WHAT WOULD FALSIFY IT: if the pre-registered predictions are not DECIDABLE at a
round boundary, mid-run scoring cannot fire at all and the proposal is empty
regardless of what the absence detectors do. That is a property of the
predictions themselves and is checkable without running anything.

A PREDICTION IS ROUND-DECIDABLE only if its falsifier can be evaluated from the
state available at the end of some round N < the last. A falsifier naming the
FINAL state, the round CEILING, or the completed registry is TERMINAL: it has
exactly one evaluation point, the end, and a monitor that can only speak at the
end is not a monitor.
"""
from __future__ import annotations
import json, math, pathlib, re, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
DATA = REPO / "experimental_notes" / "data"
LOGS = REPO / "bench" / "logs"

#: Words in a falsifier that make it TERMINAL -- evaluable only once, at the end.
TERMINAL_MARKERS = (
    "final", "ceiling", "exhausts", "exits", "every finding", "the run reaches",
    "converged_at null", "completed", "at the end", "whole run",
)
#: Quantities the runner records PER ROUND, so a predicate over them has many
#: evaluation points. Taken from the report keys, not guessed.
ROUND_KEYED = ("gamma_history", "gate_history", "critical_novelty_series",
               "hierarchical_crit_series", "location_crit_series")


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def classify(falsifier: str) -> tuple[str, str]:
    f = (falsifier or "").lower().strip()
    if not f or f.startswith("n/a"):
        return "NOT SCORABLE", "the entry states it predicts and scores nothing"
    hit = [m for m in TERMINAL_MARKERS if m in f]
    if hit:
        return "TERMINAL", f"its falsifier names {hit[:3]}, evaluable only at the end"
    return "ROUND-DECIDABLE?", "no terminal marker found; needs a hand check"


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("CAN A PRE-REGISTRATION BE SCORED MID-RUN?")
    print("=" * 78)
    rows = []
    for f in sorted(DATA.glob("*prereg*.json")):
        d = json.loads(f.read_text())
        for p in (d.get("predictions") or []):
            kind, why = classify(str(p.get("falsified_if") or ""))
            rows.append({"file": f.name, "id": p.get("id"), "kind": kind,
                         "why": why,
                         "falsifier": str(p.get("falsified_if") or "")[:150]})
    print(f"\n  pre-registration files: "
          f"{len(sorted(DATA.glob('*prereg*.json')))}   predictions: {len(rows)}")
    print(f"\n  {'id':6s} {'verdict':18s} why")
    for r in rows:
        print(f"  {str(r['id']):6s} {r['kind']:18s} {r['why'][:70]}")
        print(f"         falsifier: {r['falsifier'][:104]}")

    term = sum(1 for r in rows if r["kind"] == "TERMINAL")
    nots = sum(1 for r in rows if r["kind"] == "NOT SCORABLE")
    maybe = sum(1 for r in rows if r["kind"] == "ROUND-DECIDABLE?")
    p, lo, hi = wilson(term + nots, len(rows))
    print(f"\n  TERMINAL or NOT SCORABLE: {term + nots} of {len(rows)} = "
          f"{p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print(f"  possibly round-decidable : {maybe}")

    print(f"\n  VERDICT ON THE PROPOSAL")
    if term + nots == len(rows):
        print("  FALSIFIED. Every pre-registered prediction is evaluable only at")
        print("  the end of a run, so scoring the pre-registration mid-run would")
        print("  fire 0 times. The expectation STORE exists; its CONTENTS are not")
        print("  mid-run predicates. The proposal is withdrawn as stated.")
    else:
        print(f"  NOT FALSIFIED: {maybe} prediction(s) may be round-decidable and")
        print(f"  each needs a hand check before any claim is made.")

    print(f"\n  WHAT IS ACTUALLY ROUND-DECIDABLE, from the archive's own keys")
    # ★ BOTH FILES, corrected 2026-11-02 WITHIN THE HOUR. A first version globbed
    # `*/*_report.json` ALONE and reported `gate_history` present in 0 reports,
    # which was written into the task list as a finding before being checked. It
    # is FALSE: `gate_history` is written at reference_runner_v3.py:20821 into
    # `runner_state.json`, not the report, and is present in 65 of 65 of them
    # (1.000000, Wilson 95% [0.944198, 1.000000]). A probe that looks in 1 of 2
    # files reports a false zero for the other, which is this project's single
    # most recorded error class -- and here it accused the code of discarding a
    # quantity the UX backend actively consumes.
    found = {}
    for rep in sorted(list(LOGS.glob("*/*_report.json"))
                      + list(LOGS.glob("*/runner_state.json"))):
        try:
            j = json.loads(rep.read_text(errors="ignore"))
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        s = json.dumps(j)
        for k in ROUND_KEYED:
            if f'"{k}"' in s:
                found.setdefault(k, 0)
                found[k] += 1
    for k in ROUND_KEYED:
        print(f"    {k:28s} present in {found.get(k, 0):3d} archived file(s) "
              f"(reports AND runner_state.json, which is the fix of 2026-11-02)")
    print()
    print("  SO A MID-RUN EXPECTATION MUST BE STATED OVER THESE, not over the")
    print("  terminal quantities a pre-registration names. That is a DESIGN")
    print("  REQUIREMENT this project does not yet meet, and it is the honest")
    print("  content of his definition: a per-round predicate, with its own")
    print("  falsifier, evaluable at every round boundary.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
