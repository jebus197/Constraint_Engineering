#!/usr/bin/env python3
"""How many live `compose()` call sites inherit the coherence-pruning default?

WHY THIS EXISTS. C0001's inversion is PROVED and committed -- z3 returns UNSAT
for "pruning shortened the text AND density did not worsen", and SymPy gives the
derivative as 4*C*(L1-L2)/(L1*L2) > 0 for L2 < L1, because `_count_constraints`
reads only the merged TOML policy so the numerator is independent of the text.
The canonical runner is already protected: `RunnerConfig.composer_coherence_pruning`
defaults to False and 2 guards assert it.

WHAT WAS NOT KNOWN is how many OTHER callers inherit `compose()`'s own parameter
default, which is still True in order to preserve behaviour byte-for-byte. That
is the number the founder's decision turns on, and quoting it from a session log
would be the `measured-rate-travels-with-its-script` failure -- so it lives here.

WHY AST AND NOT GREP. A textual search for `coherence_pruning` cannot tell a call
that PASSES the argument from one that merely mentions it in a comment, and
cannot see a call that omits it entirely -- which is the case being counted. The
census walks the syntax tree and inspects each call's keywords, so a comment can
never be mistaken for an argument. This project has found 4 defects by executing
2 forms against each other and none by reading.

SCOPE, STATED. Tests and `seat_evidence/` are excluded: a test that pins the
hazardous default is evidence about it, not an inheritor of it, and sandbox
copies are preserved records rather than live code. `bench/logs/` is excluded for
the same reason. Those exclusions are the reason the denominator is small enough
to list in full, which the output does.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOTS = ("bench", "scripts")
KW = "coherence_pruning"


def census() -> list[dict]:
    out: list[dict] = []
    for root in ROOTS:
        for p in sorted((REPO / root).rglob("*.py")):
            sp = str(p.relative_to(REPO))
            if "/logs/" in sp or "/tests/" in sp or "seat_evidence" in sp:
                continue
            try:
                tree = ast.parse(p.read_text(errors="ignore"))
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call):
                    continue
                name = (getattr(n.func, "attr", None)
                        or getattr(n.func, "id", None) or "")
                if name != "compose":
                    continue
                passes = any(k.arg == KW for k in n.keywords if k.arg)
                out.append({"file": sp, "line": n.lineno, "passes": passes})
    return sorted(out, key=lambda r: (r["file"], r["line"]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = census()
    total = len(rows)
    inherit = [r for r in rows if not r["passes"]]
    k, n = len(inherit), total

    if args.json:
        print(json.dumps({"total": total, "inherit": k, "rows": rows}, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"live compose() call sites: {total}")
    print(f"  pass {KW} explicitly : {total - k}")
    print(f"  INHERIT the True default        : {k}")
    print()
    for r in rows:
        print(f"    {'passes ' if r['passes'] else 'INHERIT'} "
              f"{r['file']}:{r['line']}")
    if not n:
        print("\nno call sites found — the census predicate needs re-deriving")
        return 1
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 25
    z = mp.mpf("1.959963984540054")
    ph = mp.mpf(k) / n
    N = mp.mpf(n)
    den = 1 + z ** 2 / N
    ctr = (ph + z ** 2 / (2 * N)) / den
    hw = z * mp.sqrt(ph * (1 - ph) / N + z ** 2 / (4 * N ** 2)) / den
    print()
    print(f"  share inheriting the default: {k} of {n} = {k / n:.6f}")
    print(f"    Wilson 95% [statsmodels]: [{lo:.6f}, {hi:.6f}]")
    print(f"    Wilson 95% [mpmath     ]: [{float(ctr - hw):.6f}, "
          f"{float(ctr + hw):.6f}]")
    agree = (abs(float(lo) - float(ctr - hw)) < 1e-9
             and abs(float(hi) - float(ctr + hw)) < 1e-9)
    print(f"    agree to 1e-9: {agree}")
    print()
    print("WHAT THIS DOES AND DOES NOT ARGUE. It does NOT argue for flipping the")
    print("  default: doing so changes what those callers compose and therefore")
    print("  alters replay against anything they produced. It argues only that")
    print("  the exposure is a specific, listed set rather than an unknown, so")
    print("  the founder's decision can be made against names instead of a fear.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
