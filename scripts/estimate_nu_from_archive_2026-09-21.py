#!/usr/bin/env python3
"""An empirical re-injection rate, from data the archive already holds.

WHY THIS EXISTS. `nu`, the re-injection rate, is load-bearing in 3 places and has
never been estimated in this project. It sets the substrate ceiling (the reachable
floor is `nu/q`, corrected 2026-09-21). It sets the break-even rate `nu*` above
which a cycle is net harmful. And it is the quantity whose independent measurement
would RETIRE the section 7.12 confound: `D* = eps*/(1-nu)` forbids nothing while
both parameters are free, and fixing `nu` from something other than the run being
fitted makes the fixed point a prediction rather than a description.

THE METHOD, AND WHY IT IS NOT THE ONE PROPOSED. The ds seat proposed, correctly:
"apply each fix to its target, run the test suite, count how many introduce new
test failures". That is the right definition. Its literal form is infeasible --
902 archived fixes against a suite that takes over half an hour each.

IT DOES NOT NEED RE-RUNNING, BECAUSE THE RUNNER ALREADY DID IT. `_run_effect_
regression` copies the repository into a sandbox, overlays the modified source,
and runs the configured test command -- exactly the proposed experiment -- and
stores the result as `e2_regression`, `passed/total`. Every archived fix that was
scored with a test command configured carries its own answer.

*** THE ARCHIVE CANNOT ESTIMATE nu, AND THAT IS THIS SCRIPT'S ACTUAL RESULT. ***

A first version of this script reported nu_lower = 214/762 = 0.280840 and drew
the conclusion that the shipped default nu_b = 0.05 is 5.62x too optimistic.
**That conclusion is withdrawn.** It rests on reading `e2 < 1.0` as "the fix broke
something", and `e2` does not mean that.

`_run_effect_regression` computes `score = passed / total` with NO BASELINE
COMPARISON -- verified by reading the function, which contains no reference to a
baseline at all. So `e2 < 1.0` conflates 2 different facts:
  * the fix broke previously-passing tests  (genuine re-injection), and
  * the suite was ALREADY failing before the fix -- which is frequently WHY a
    defect was under review in the first place.

The confound runs in both directions. Already-red suites make 214 an OVERCOUNT of
re-injection; fixes that introduce a flaw no existing test covers score 1.0 and
make it an UNDERCOUNT. It is therefore neither an upper nor a lower bound, and
quoting it as either would be a claim the data cannot carry.

WHAT FOLLOWS, AND IT IS USEFUL. The ds seat's proposed measurement is CORRECT --
apply each fix, run the suite, count NEW failures -- and the archive cannot
substitute for it, because the stored quantity answers a different question.
**nu therefore requires the commissioning run**, exactly as the scorer's
non-circular validation does. 2 of the project's open questions now need the same
instrument, which is an argument for running it rather than for more analysis.

AND A SMALL ADDITIVE FIX THAT WOULD MAKE nu MEASURABLE IN FUTURE. If
`_run_effect_regression` recorded the baseline pass rate alongside the post-fix
one, the delta would be recoverable and this measurement would need no new run.
That is 1 extra field on an existing record, it removes nothing, and it is
proposed rather than applied because it changes what the runner writes.
"""
from __future__ import annotations

import glob
import json
import os
from math import sqrt
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def wilson(k: int, n: int) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n)))
    return ((c - h) / d, (c + h) / d)


def collect():
    rows = []
    for f in sorted(glob.glob(str(REPO / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > 60_000_000:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "e2_regression" not in raw:
            continue
        try:
            doc = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue

        def walk(node):
            if isinstance(node, dict):
                sk = node.get("sk_result")
                if isinstance(sk, dict) and sk.get("tristate") == "ADMISSIBLE":
                    e2 = (sk.get("gate_details") or {}).get("e2_regression")
                    if isinstance(e2, dict) and e2.get("score") is not None:
                        rows.append((float(e2["score"]), str(e2.get("detail"))))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(doc)
    return rows


def main() -> None:
    import numpy as np
    from statsmodels.stats.proportion import proportion_confint

    rows = collect()
    n = len(rows)
    if not n:
        print("no archived e2_regression readings found")
        return
    broke = [s for s, _ in rows if s < 1.0]
    k = len(broke)
    lo, hi = wilson(k, n)
    a, b = proportion_confint(k, n, method="wilson")
    cp = proportion_confint(k, n, method="beta")

    print("=" * 74)
    print("AN EMPIRICAL LOWER BOUND ON nu, THE RE-INJECTION RATE")
    print("=" * 74)
    print(f"\n  archived fixes scored with a test command : {n}")
    print(f"  fixes that left the suite failing         : {k}")
    print(f"\n  nu_lower = {k}/{n} = {k/n:.6f}")
    print(f"    Wilson 95%          : [{lo:.6f}, {hi:.6f}]   "
          f"(hand and statsmodels agree: {abs(lo-a) < 1e-12})")
    print(f"    Clopper-Pearson 95% : [{cp[0]:.6f}, {cp[1]:.6f}]")

    sev = np.array(broke, dtype=float)
    if sev.size:
        print(f"\n  among those that broke something, how badly:")
        print(f"    mean e2 = {sev.mean():.6f}   median = {np.median(sev):.6f}   "
              f"min = {sev.min():.6f}")
        print(f"    a fix scoring e2 = s left {s_pct(sev.mean())} of the suite passing")

    print("\n  *** THIS IS NOT nu, AND THE ARCHIVE CANNOT GIVE nu ***")
    print("    `e2` is `passed / total` with NO baseline -- verified by reading the")
    print("    function, which never mentions one. So e2 < 1.0 conflates:")
    print("      * the fix broke previously-passing tests  (real re-injection), and")
    print("      * the suite was ALREADY red before the fix (often WHY a defect existed).")
    print("    Already-red suites make this an OVERCOUNT; flaws no test covers make it")
    print("    an UNDERCOUNT. Neither bound holds. The figure above is reported so the")
    print("    confound is visible, NOT as an estimate of nu.")

    print("\n  WHAT WOULD CHANGE IF IT WERE nu -- shown only to size the question")
    import sympy as sp
    q = sp.Symbol('q', positive=True)
    nu_hat = sp.nsimplify(round(k / n, 6), rational=True)
    print(f"    the substrate floor nu/q at q=0.3 : "
          f"{float(nu_hat / sp.Rational(3,10)):.6f}   (against the default nu_b=0.05 -> "
          f"{0.05/0.3:.6f})")
    print(f"    the shipped default is nu_b = 0.05; this estimate is "
          f"{k/n/0.05:.2f}x that.")
    print("    -> IF this were nu the shipped default would be optimistic and the")
    print("       floor far higher. It is NOT nu. nu needs the commissioning run,")
    print("       and so does the scorer's non-circular validation: 2 open questions,")
    print("       1 instrument.")
    print("\n  PROPOSED, NOT APPLIED: record the BASELINE pass rate beside the post-fix")
    print("  one in `_run_effect_regression`. 1 extra field, removes nothing, and it")
    print("  would make nu recoverable from the archive without a new run.")


def s_pct(x: float) -> str:
    return f"{x:.1%}"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description=("Estimate a lower bound on the re-injection rate nu from "
                     "archived e2_regression readings. Reads bench/logs, writes "
                     "nothing, costs nothing."),
        epilog="Prints the bound with Wilson and Clopper-Pearson intervals, and "
               "what it would change if adopted as the run's nu.")
    ap.parse_args()
    main()
