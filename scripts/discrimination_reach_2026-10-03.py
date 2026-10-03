#!/usr/bin/env python3
"""How far the discrimination control reaches, before and after the widening.

WHY THIS EXISTS. `measured-rate-travels-with-its-script` (founder ruling
2026-09-04). The figures justifying the 2026-10-03 widening -- the control left
a record on 44 of 567 falsifier-bearing entries, and the other 523 returned
`NO_CONTROL` having decided nothing -- were produced inside a panel seat's
sandbox and quoted in a note. A number whose only home is prose is a claim about
evidence, not evidence, so this recomputes all of it from the tracked archive.

WHAT IT REPORTS.

  falsifier_bearing   entries across every archived report that carry a
                      non-empty `falsifier_code` (the population the control
                      could in principle reach).
  left_a_record       entries whose `discrimination` record carries an outcome:
                      the control's reach BEFORE the widening.
  no_control          entries stamped NO_CONTROL: the population that returned
                      having decided nothing, which the shadow invariance probe
                      now reaches.
  with_corrected      entries that actually carry a `corrected_copy`, which is
                      what the control requires and what bounds its reach.
  invariant_shadow    entries already carrying the new shadow outcome (0 until a
                      run executes with the widened code, which is the honest
                      state to print rather than a projection).

EVERY PROPORTION carries a Wilson interval from statsmodels and an independent
mpmath closed form, which must agree to 1e-9 or the script fails rather than
printing a number nobody checked.

Usage:  python3 scripts/discrimination_reach_2026-10-03.py [--json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9, (
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}")
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def harvest() -> dict:
    from bench.reference_runner_v3 import DISC_ABSENT, DISC_INVARIANT
    logs = REPO / "bench" / "logs"
    bearing = record = absent = corrected = shadow = 0
    outcomes: dict[str, int] = {}
    for report in sorted(logs.rglob("*_report.json")):
        try:
            data = json.loads(report.read_text(encoding="utf-8",
                                               errors="replace"))
        except (ValueError, OSError):
            continue
        for _cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            if not (e.get("falsifier_code") or "").strip():
                continue
            bearing += 1
            if (e.get("corrected_copy") or "").strip():
                corrected += 1
            oc = ((e.get("discrimination") or {}) or {}).get("outcome") or ""
            if oc:
                record += 1
                outcomes[oc] = outcomes.get(oc, 0) + 1
                if oc == DISC_ABSENT:
                    absent += 1
                if oc == DISC_INVARIANT:
                    shadow += 1
    return {"bearing": bearing, "record": record, "absent": absent,
            "corrected": corrected, "shadow": shadow, "outcomes": outcomes}


def main(argv: list[str] | None = None) -> int:
    # A REAL PARSER, NOT A HAND-ROLLED argv SCAN. The first version of this
    # script read `sys.argv` directly, which meant an unrecognised flag was
    # SILENTLY IGNORED and the script exited 0 -- the shape
    # `bench/tests/test_operational_scripts.py` calls "the 118-day no-op
    # again", and the reason the project's own rule is that a documented
    # command must either work or fail loudly.
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0],
        epilog="Every figure is recomputed from the archive on each run.")
    ap.add_argument("--json", action="store_true",
                    help="emit the full record as JSON instead of a report")
    a = ap.parse_args(argv)
    argv = ["--json"] if a.json else []
    h = harvest()
    n = h["bearing"]
    out = {
        "falsifier_bearing": n,
        "left_a_record": wilson(h["record"], n),
        "stamped_no_control": wilson(h["absent"], n),
        "carry_a_corrected_copy": wilson(h["corrected"], n),
        "invariant_shadow_outcomes": wilson(h["shadow"], n),
        "outcome_counts": h["outcomes"],
        "reach_before": ("entries the control could decide anything about: "
                         "those with a corrected copy"),
        "reach_after": ("every falsifier-bearing entry: the shadow probe runs "
                        "on the NO_CONTROL path, which is where the rest land"),
    }
    if "--json" in argv:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print("DISCRIMINATION CONTROL REACH")
    print(f"  falsifier-bearing entries      : {n}")
    for label, key in (("left a record", "left_a_record"),
                       ("stamped NO_CONTROL", "stamped_no_control"),
                       ("carry a corrected copy", "carry_a_corrected_copy"),
                       ("shadow invariant outcomes", "invariant_shadow_outcomes")):
        d = out[key]
        if d["pct"] is None:
            print(f"  {label:30s} : {d['k']} of {d['n']}")
        else:
            print(f"  {label:30s} : {d['k']} of {d['n']} = {d['pct']}%, "
                  f"Wilson [{d['wilson'][0]}%, {d['wilson'][1]}%]")
    print("  outcome counts:")
    for k in sorted(h["outcomes"]):
        print(f"    {k:40s} {h['outcomes'][k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
