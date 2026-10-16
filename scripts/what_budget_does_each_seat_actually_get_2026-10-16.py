#!/usr/bin/env python3
"""Which coherence budget does each live seat actually receive, and from where?

WHAT THIS SCRIPT MEASURES, BY CALLING THE RESOLUTION CHAIN RATHER THAN READING
IT. A seat's budget is resolved in TWO hops, and the second one is easy to miss:

    base   = base_model_label(seat)                      # Gemini-SIM -> Gemini
    cmodel = COMPOSER_MODEL_MAP.get(base, base)          # Gemini -> gemini_3_1_pro
    budget = MODEL_COHERENCE_BUDGETS.get(cmodel, DEFAULT)

THE RECORDED MISTAKE THIS SCRIPT EXISTS TO PREVENT. On 2026-10-16 the committed
2026-10-13 claim -- *"the 5 seats carry 4 DISTINCT density budgets (0.01, 0.012,
0.015, 0.02), so the deletion set differs BY SEAT"* -- was challenged by
measuring only the FIRST and THIRD lines above. Dropping the
`COMPOSER_MODEL_MAP` hop makes every key look unreachable and every seat look
identical, and the claim was wrongly withdrawn on that basis. Measured through
the full chain the claim is CORRECT: 4 distinct budgets, with Fable alone
falling through to the default. The withdrawal was itself withdrawn and the
original claim restored.

So this script always prints BOTH resolutions side by side. A future reader
cannot repeat the error without seeing the two disagree.

`execute-do-not-grep`: nothing below asserts on source text. The budget table,
the label function and the composer map are imported and invoked.

THE LIVE ISSUE IT REPORTS, which is separate and needs his ruling rather than a
repair: the chain keys a per-model CAPABILITY number on a model NAME --
`opus_4_6: 0.020  # handles dense instructions well` is the clearest case -- and
4 of the 5 keys name SUPERSEDED versions against the current roster. His ruling
of 2026-10-07: *"Names are recorded for provenance only!"*

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/what_budget_does_each_seat_actually_get_2026-10-16.py
    python3 scripts/what_budget_does_each_seat_actually_get_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load():
    sys.path.insert(0, str(REPO / "bench"))
    from cdsfl_registry import composer  # noqa: PLC0415
    import reference_runner_v3 as runner  # noqa: PLC0415

    return composer, runner


def measure() -> dict:
    composer, runner = _load()
    roster = dict(getattr(runner, "MODEL_ROSTER", {}))
    suffix = "-SIM"
    labels: list[str] = []
    for base in sorted(roster) + ["Fable"]:
        labels.extend([base, f"{base}{suffix}"])
    labels = sorted(dict.fromkeys(labels))

    rows = []
    for label in labels:
        base = runner.base_model_label(label)
        cmodel = composer.COMPOSER_MODEL_MAP.get(base, base)
        budget = composer.MODEL_COHERENCE_BUDGETS.get(
            cmodel, composer.DEFAULT_COHERENCE_BUDGET)
        # The naive resolution that caused the 2026-10-16 mis-withdrawal, kept
        # beside the real one so the two can never be confused again.
        naive = composer.MODEL_COHERENCE_BUDGETS.get(
            base, composer.DEFAULT_COHERENCE_BUDGET)
        rows.append(
            {
                "seat_label": label,
                "base_label": base,
                "composer_model": cmodel,
                "budget": budget,
                "budget_if_hop_dropped": naive,
                "key_declared": cmodel in composer.MODEL_COHERENCE_BUDGETS,
            }
        )

    declared = dict(composer.MODEL_COHERENCE_BUDGETS)
    reachable = sorted({r["composer_model"] for r in rows if r["key_declared"]})
    distinct = sorted({r["budget"] for r in rows})
    distinct_naive = sorted({r["budget_if_hop_dropped"] for r in rows})

    # Which declared keys name a version the roster no longer carries? The test
    # is deliberately crude and stated: a declared key is matched against the
    # roster descriptions, lowercased, with separators normalised.
    def norm(t: str) -> str:
        return t.lower().replace("-", " ").replace("_", " ").replace(".", " ")

    roster_blob = norm(" ".join(roster.values()))
    stale = []
    for key in sorted(declared):
        parts = norm(key).split()
        # A key is CURRENT only if every one of its tokens appears in the roster
        # text -- `gemini 3 1 pro` does, `opus 4 6` does not against Opus 4.7.
        if not all(tok in roster_blob.split() for tok in parts):
            stale.append(key)

    return {
        "roster": roster,
        "declared_budgets": declared,
        "default_budget": composer.DEFAULT_COHERENCE_BUDGET,
        "rows": rows,
        "reachable_keys": reachable,
        "distinct_budgets_in_force": distinct,
        "distinct_budgets_if_hop_dropped": distinct_naive,
        "stale_declared_keys": stale,
        "composer_model_map": dict(composer.COMPOSER_MODEL_MAP),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()
    m = measure()

    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
        return 0

    print("WHICH COHERENCE BUDGET EACH LIVE SEAT ACTUALLY RECEIVES")
    print(f"  DEFAULT_COHERENCE_BUDGET = {m['default_budget']}")
    print(f"  declared per-model keys ({len(m['declared_budgets'])}):")
    for k, v in sorted(m["declared_budgets"].items()):
        mark = "  STALE vs roster" if k in m["stale_declared_keys"] else ""
        print(f"       {k:<16} {v}{mark}")
    print()
    print(f"  {'seat label':<14}{'base':<11}{'composer model':<17}"
          f"{'budget':<9}{'if hop dropped':<15}key declared?")
    for r in m["rows"]:
        print(f"       {r['seat_label']:<14}{r['base_label']:<11}"
              f"{r['composer_model']:<17}{r['budget']:<9}"
              f"{r['budget_if_hop_dropped']:<15}"
              f"{'yes' if r['key_declared'] else 'NO'}")
    print()
    print(f"  declared keys reachable through the FULL chain ... "
          f"{len(m['reachable_keys'])} of {len(m['declared_budgets'])}  "
          f"{m['reachable_keys']}")
    print(f"  distinct budgets in force ........................ "
          f"{m['distinct_budgets_in_force']}")
    print(f"  distinct budgets if the map hop is dropped ....... "
          f"{m['distinct_budgets_if_hop_dropped']}  <- the 2026-10-16 error")
    print(f"  declared keys naming a superseded version ........ "
          f"{len(m['stale_declared_keys'])} of {len(m['declared_budgets'])}  "
          f"{m['stale_declared_keys']}")
    print()
    n = len(m["distinct_budgets_in_force"])
    print(f"  VERDICT on the 2026-10-13 claim of 4 distinct per-seat budgets: "
          f"{'UPHELD' if n == 4 else 'NOT UPHELD (' + str(n) + ' distinct)'}.")
    if m["stale_declared_keys"]:
        print(f"  NEEDS HIS RULING: {len(m['stale_declared_keys'])} of "
              f"{len(m['declared_budgets'])} keys name superseded versions, and a "
              f"live seat")
        print(f"  inherits a capability allowance from that name. His ruling of "
              f"2026-10-07 is that")
        print(f"  names are recorded for provenance only. Not changed here.")
    return 0 if n == 4 else 1


if __name__ == "__main__":
    raise SystemExit(main())
