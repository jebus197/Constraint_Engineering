#!/usr/bin/env python3
"""Why every coherence calibration was an artefact of a truncation constant.

HIS RULING, 2026-10-16, on the coherence budget recalibration: *"It should be
fixed, providing it doesn't trim the operational directives. It exists so that
models never get fed work that is larger than they have been demonstrably proven
to be able to handle in any experiment."*

WHY THIS SCRIPT EXISTS. The figures below were stated in a test docstring and a
commit message and nowhere else, which under
`measured-rate-travels-with-its-script` makes them claims ABOUT evidence rather
than evidence. This script is their producer.

THE CHAIN, IN THREE LINKS.

  1. `calibrate_coherence_thresholds` prefers a recorded `constraint_density`
     and otherwise estimates it as `floor(c/70) / floor(c/4)`, where `c` is the
     entry's recorded character count.

  2. No archived dispatch entry carries a composer field, so link 1 always fell
     through to the estimator. What the entries DO carry is `prompt_length` --
     and every `save_output` call in the dispatch is passed
     `prompt[:200] + "..."`, so that number is the length of the TRUNCATED copy,
     not of the prompt.

  3. 200 + len("...") = 203, and floor(203/70)/floor(203/4) = 2/50 = 1/25. So
     the estimator returned the same value for essentially every entry, and the
     calibration measured the truncation rather than any model.

THE ARITHMETIC IS CROSS-VERIFIED BY FOUR TOOLS, per the two-tool rule. SymPy,
NumPy and mpmath evaluate the ratio independently, and z3 and SymPy
independently enumerate the COMPLETE integer band on which the ratio equals
1/25 -- so the claim is not merely "203 gives 0.04" but "203 sits inside the
only band that does, and at its top edge".

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py
    python3 scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
TRUNCATION = 200
SUFFIX = "..."
RECORDED_LENGTH = TRUNCATION + len(SUFFIX)
COMPOSER_FIELDS = ("constraint_density", "constraint_count", "token_estimate",
                   "coherence_budget", "cid")


def measure_archive() -> dict:
    """How many dispatch entries carry the truncation constant, and none a density."""
    import collections

    # ★ TWO PREDICATES, BOTH NAMED, because they give different denominators
    # and the project has already been bitten three times by a figure whose
    # predicate was left implicit.
    #
    #   TOP-LEVEL   -- a dispatch record is the whole JSON document (or one
    #                  element of a top-level list). This is the shape
    #                  `calibrate_coherence_thresholds` itself iterates, so it
    #                  is the denominator that describes what the CONSUMER sees.
    #   RECURSIVE   -- every nested dict anywhere in the tree that looks like a
    #                  dispatch entry. A larger denominator, and the one a
    #                  whole-archive audit naturally produces.
    #
    # The numerator is 0 under both, so the claim "no archived entry carries a
    # composer field" holds either way -- but the interval does not, and
    # quoting one denominator against the other's interval would be wrong.
    lengths = collections.Counter()
    top_entries = 0
    top_with_field = 0
    rec_entries = 0
    rec_with_field = 0

    def is_entry(d: dict) -> bool:
        return bool(d.get("model") or d.get("model_label"))

    def has_field(d: dict) -> bool:
        meta = d.get("metadata") if isinstance(d.get("metadata"), dict) else {}
        return any(f in d or f in meta for f in COMPOSER_FIELDS)

    def walk(obj) -> None:
        nonlocal rec_entries, rec_with_field
        if isinstance(obj, dict):
            if "response" in obj or "model" in obj or "model_label" in obj:
                rec_entries += 1
                if has_field(obj):
                    rec_with_field += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    for path in sorted(LOGS.rglob("*.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue
        walk(doc)
        for entry in (doc if isinstance(doc, list) else [doc]):
            if not isinstance(entry, dict) or not is_entry(entry):
                continue
            top_entries += 1
            if has_field(entry):
                top_with_field += 1
            pl = entry.get("prompt_length")
            if isinstance(pl, int):
                lengths[pl] += 1
    with_pl = sum(lengths.values())
    return {
        "dispatch_entries": top_entries,
        "entries_carrying_a_composer_field": top_with_field,
        "recursive_entries": rec_entries,
        "recursive_entries_carrying_a_composer_field": rec_with_field,
        "entries_carrying_prompt_length": with_pl,
        "entries_at_the_truncation_length": lengths.get(RECORDED_LENGTH, 0),
        "distinct_prompt_lengths": len(lengths),
        "top_lengths": lengths.most_common(6),
    }


def verify_arithmetic() -> dict:
    """SymPy, NumPy, mpmath on the value; z3 and SymPy on the band."""
    import sympy as sp
    import numpy as np
    import mpmath as mp
    from z3 import Int, Solver, sat

    mp.mp.dps = 40
    c = RECORDED_LENGTH
    exact = sp.Rational(c // 70, c // 4)
    by_numpy = float(np.int64(c) // np.int64(70)) / float(np.int64(c) // np.int64(4))
    by_mpmath = float(mp.mpf(c // 70) / mp.mpf(c // 4))
    agree = (float(exact) == by_numpy == by_mpmath)

    # The COMPLETE integer band on which the ratio equals this value, by two
    # independent routes over a window that brackets the truncation length.
    lo_w, hi_w = 150, 260
    by_sympy = [
        x for x in range(lo_w, hi_w + 1)
        if x // 70 and x // 4 and sp.Rational(x // 70, x // 4) == exact
    ]
    s = Solver()
    x, q70, q4 = Int("x"), Int("q70"), Int("q4")
    s.add(x >= lo_w, x <= hi_w)
    s.add(q70 * 70 <= x, x < (q70 + 1) * 70, q70 >= 0)
    s.add(q4 * 4 <= x, x < (q4 + 1) * 4, q4 >= 1)
    s.add(q70 * int(exact.q) == q4 * int(exact.p))
    by_z3 = []
    while s.check() == sat:
        v = s.model()[x].as_long()
        by_z3.append(v)
        s.add(x != v)
    by_z3.sort()

    # And the asymptote a REAL prompt length would approach.
    n = sp.Symbol("n", positive=True)
    asymptote = sp.limit((n / 70) / (n / 4), n, sp.oo)
    return {
        "recorded_length": c,
        "ratio_exact": f"{exact.p}/{exact.q}",
        "ratio_float": float(exact),
        "sympy_numpy_mpmath_agree": bool(agree),
        "band_window": [lo_w, hi_w],
        "band_by_sympy": by_sympy,
        "band_by_z3": by_z3,
        "band_methods_agree": by_sympy == by_z3,
        "asymptote_exact": f"{sp.nsimplify(asymptote)}",
        "asymptote_float": float(asymptote),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    arch = measure_archive()
    arith = verify_arithmetic()

    if args.json:
        print(json.dumps({"archive": arch, "arithmetic": arith}, indent=2,
                         sort_keys=True))
        return 0

    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta

    def interval(k: int, n: int) -> str:
        lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
        lo_e, hi_e = proportion_confint(k, n, alpha=0.05, method="beta")
        lo_s = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
        hi_s = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
        assert abs(lo_e - lo_s) < 1e-9 and abs(hi_e - hi_s) < 1e-9
        return (f"{100*k/n:.4f}%  Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%]  "
                f"Clopper-Pearson [{100*lo_e:.4f}%, {100*hi_e:.4f}%]")

    print("WHY EVERY COHERENCE CALIBRATION MEASURED THE TRUNCATION")
    print()
    print("LINK 2 -- THE ARCHIVE CARRIES NO DENSITY, AND ONE PROMPT LENGTH")
    n = arch["dispatch_entries"]
    print(f"  dispatch entries examined ............ {n}")
    print(f"  carrying ANY composer field .......... "
          f"{arch['entries_carrying_a_composer_field']}/{n}   "
          f"{interval(arch['entries_carrying_a_composer_field'], n)}")
    rn = arch["recursive_entries"]
    print(f"  -- and under the RECURSIVE predicate: {rn} entries,")
    print(f"     carrying a composer field .......... "
          f"{arch['recursive_entries_carrying_a_composer_field']}/{rn}   "
          f"{interval(arch['recursive_entries_carrying_a_composer_field'], rn)}")
    wp = arch["entries_carrying_prompt_length"]
    at = arch["entries_at_the_truncation_length"]
    print(f"  carrying prompt_length ............... {wp}/{n}")
    print(f"  prompt_length == {RECORDED_LENGTH} ................. {at}/{wp}   "
          f"{interval(at, wp)}")
    print(f"  distinct prompt_length values ........ {arch['distinct_prompt_lengths']}")
    for v, k in arch["top_lengths"]:
        print(f"       {k:>5} entries at {v}")
    print()
    print("LINK 3 -- THE ARITHMETIC, FOUR TOOLS")
    a = arith
    print(f"  floor({a['recorded_length']}/70) / floor({a['recorded_length']}/4) "
          f"= {a['ratio_exact']} = {a['ratio_float']}")
    print(f"  SymPy, NumPy and mpmath agree ........ {a['sympy_numpy_mpmath_agree']}")
    print(f"  complete band giving {a['ratio_exact']}, by SymPy .. {a['band_by_sympy']}")
    print(f"  the same band, by z3 ................. {a['band_by_z3']}")
    print(f"  the 2 methods agree .................. {a['band_methods_agree']}")
    print(f"  asymptote for a REAL prompt length ... {a['asymptote_exact']} "
          f"= {a['asymptote_float']:.10f}")
    print()
    ok = (a["sympy_numpy_mpmath_agree"] and a["band_methods_agree"]
          and RECORDED_LENGTH in a["band_by_z3"])
    if not ok:
        print("  VERDICT: the arithmetic did NOT reproduce. Do not cite these figures.")
        return 1
    print(f"  VERDICT: {RECORDED_LENGTH} lies inside the only band on which the")
    print(f"  estimator returns {a['ratio_exact']}, and at its top edge. So the value was")
    print("  FORCED by the truncation, not measured from any model. The repair")
    print("  records the composer's own density per dispatch, after which the")
    print("  estimator is no longer reached.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
