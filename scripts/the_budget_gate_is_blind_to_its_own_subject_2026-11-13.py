#!/usr/bin/env python3
"""The resource gate refuses legitimate briefs and misses 0.84 of real ones.

`~/.claude/hooks/local_resource_budget.py` is a PreToolUse gate on Agent, Task
and Workflow. It exists to stop delegated work from launching the project's
heavy verification on a machine with 8 GiB and a measured heavy budget of 1.

FOUND 2026-11-13, WHILE BEING REFUSED BY IT. 2 adversarial-review briefs were
refused. Both FORBADE delegated heavy runs in as many words. The gate's own
docstring already records that failure mode from 2026-10-17 and claims to have
fixed it by requiring an IMPERATIVE mention outside a negation.

★ THE FIX HOLDS FOR NEGATION AND FAILS FOR EVERYTHING ELSE. Driving the
predicate over a SYSTEMATIC GRID -- 5 ordinary verbs of execution x 10 noun
phrases this project uses for its own suite x 3 sentence tails, 150 cells,
every one a genuine instruction that SHOULD be refused -- 126 pass straight
through.

8 of the 10 noun phrases are COMPLETELY blind, including `bench/tests/`, which
is the literal path a brief would name, and "the full test suite", which is how
the instruction is most naturally written. Only "the suite" and "the full
board" are caught at all, and those are the 2 phrasings the gate's author
tested. That is the shape this project already records as "the passing input
cannot test a defence".

★ THE 2 FAULTS POINT OPPOSITE WAYS AND THE SECOND IS THE DANGEROUS ONE. Over-
refusal is visible: the author sees it and reroutes. Under-catching is silent,
and the gate's own docstring says why that matters -- an author who cannot
state a limit either drops it or reroutes around the matcher, and a delegated
agent with no stated limit is MORE likely to invoke the tooling. A gate that is
0.84 blind provides assurance it cannot deliver.

NOT FIXED HERE. This measures; it does not edit the hook. The hook shares an
inode with its repository copy and `bench/tests/test_the_local_resource_budget_
binds_2026-10-11.py` carries a deliberate tripwire so a hook edit cannot arrive
without the founder's permission on record. Raising the measurement is the
whole of this script's job.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import pathlib
import sys

VERBS = ["run", "execute", "please run", "kick off", "start"]
NOUNS = ["the suite", "the test suite", "the full test suite",
         "the entire test suite", "the whole test suite",
         "the full suite", "bench/tests/", "the full board",
         "the commit board", "the verification board"]
TAILS = ["", " and report the result", " and tell me what fails"]

HOOK = pathlib.Path.home() / ".claude" / "hooks" / "local_resource_budget.py"


def load_predicate():
    """Import the LIVE hook and return its predicate, not a copy of it."""
    spec = importlib.util.spec_from_file_location("lrb_under_test", HOOK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lrb_under_test"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m._instructs_heavy_verification


def grid() -> list[str]:
    return [f"{v} {n}{t}" for v, n, t in itertools.product(VERBS, NOUNS, TAILS)]


def measure() -> dict:
    fn = load_predicate()
    cases = grid()
    through = [c for c in cases if not fn(c.lower())]
    by_noun = {}
    for noun in NOUNS:
        sub = [f"{v} {noun}{t}" for v, t in itertools.product(VERBS, TAILS)]
        by_noun[noun] = (sum(1 for c in sub if not fn(c.lower())), len(sub))
    # the negation half, which the 2026-10-17 fix DOES get right
    prohibitions = [
        "do not run pytest under any circumstances",
        "do not execute the project's test runner or any test file",
        "never run the full test suite in delegated work",
    ]
    neg_ok = sum(1 for p in prohibitions if not fn(p.lower()))
    return {"cases": cases, "through": through, "by_noun": by_noun,
            "neg_ok": neg_ok, "neg_n": len(prohibitions)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()
    r = measure()
    k, n = len(r["through"]), len(r["cases"])
    print(f"  grid: {len(VERBS)} verbs x {len(NOUNS)} nouns x {len(TAILS)} tails = {n} cells")
    print(f"  every cell is a GENUINE instruction and SHOULD be refused")
    print(f"  LET THROUGH: {k} of {n} = {k / n:.6f}\n")

    import numpy as np
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta, binom
    w1 = proportion_confint(k, n, method="wilson")
    p, z = k / n, 1.959963984540054
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    w2 = (ctr - half, ctr + half)
    cp1 = proportion_confint(k, n, method="beta")
    cp2 = (float(sbeta.ppf(0.025, k, n - k + 1)) if k else 0.0,
           float(sbeta.ppf(0.975, k + 1, n - k)) if k < n else 1.0)
    print(f"  Wilson statsmodels  [{w1[0]:.6f}, {w1[1]:.6f}]")
    print(f"  Wilson closed form  [{w2[0]:.6f}, {w2[1]:.6f}]  "
          f"agree {max(abs(w1[0]-w2[0]), abs(w1[1]-w2[1])):.3e}")
    print(f"  C-P    statsmodels  [{cp1[0]:.6f}, {cp1[1]:.6f}]")
    print(f"  C-P    scipy.beta   [{cp2[0]:.6f}, {cp2[1]:.6f}]  "
          f"agree {max(abs(cp1[0]-cp2[0]), abs(cp1[1]-cp2[1])):.3e}")
    print(f"  exact binomial p vs a 'gate works' null of 0.01: "
          f"{binom.sf(k - 1, n, 0.01):.6e}\n")

    print("  blind spots, collapsed over verb and tail:")
    for noun, (miss, tot) in r["by_noun"].items():
        tag = "BLIND" if miss == tot else ("partial" if miss else "caught")
        print(f"    {miss:2d}/{tot:2d} through  {tag:7s}  {noun!r}")
    print(f"\n  the NEGATION half, which the 2026-10-17 fix does get right: "
          f"{r['neg_ok']} of {r['neg_n']} prohibitions correctly NOT refused")
    print("\n  ★ This measures the LIVE hook by importing it. It edits nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
