#!/usr/bin/env python3
"""How many archived panel briefs would the committed validator refuse, and why?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

Task 5.1's entry cites "all 49 archived briefs would be refused, failing 1 to 7
checks, mean 2.4" and names no script. An adversarial review on 2026-09-10 could
not reproduce the spread from the committed validator, so this reproduces it -- or
corrects it -- from the artefacts.

THE COUNT COMES OFF THE VALIDATOR'S OWN REFUSAL LINE, which states the number of
failed checks explicitly. A first attempt counted occurrences of the words
"missing" and "fail" in the output and returned 1.00 for every brief, because the
header contains "fails" exactly once regardless of how many checks failed. That
was the ruler, not the briefs, and it is why this script parses the stated number
instead of inferring one.
"""
import pathlib
import re
import statistics
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "scripts" / "panel_brief_validate.py"
COUNT = re.compile(r"fails (\d+) required check\(s\)")


def main() -> int:
    briefs = sorted((REPO / "bench" / "logs").rglob("BRIEF.md"))
    if not briefs:
        print("no BRIEF.md found", file=sys.stderr)
        return 1
    refused, passed, per_brief = [], [], {}
    for b in briefs:
        r = subprocess.run([sys.executable, str(VALIDATOR), str(b)],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        m = COUNT.search(out)
        if m:
            n = int(m.group(1))
            refused.append(n)
            per_brief[b.parent.name] = n
        else:
            passed.append(b.parent.name)

    n_total = len(briefs)
    print(f"archived briefs                 : {n_total}")
    print(f"REFUSED by the committed validator: {len(refused)}")
    print(f"accepted                        : {len(passed)}  {passed}")
    if refused:
        print(f"failed checks per refused brief : min {min(refused)}, "
              f"max {max(refused)}, mean {statistics.mean(refused):.2f}, "
              f"median {statistics.median(refused)}")
        import collections
        for k, v in sorted(collections.Counter(refused).items()):
            print(f"   {v:3d} brief(s) fail {k} check(s)")

    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sb
    k, n = len(refused), n_total
    lo, hi = proportion_confint(k, n, method="wilson")
    lo2 = 0.0 if k == 0 else sb.ppf(0.025, k, n - k + 1)
    hi2 = 1.0 if k == n else sb.ppf(0.975, k + 1, n - k)
    print(f"\nrefusal rate: {k}/{n} = {k/n:.4f}")
    print(f"  Wilson 95%          [{lo*100:.1f}%, {hi*100:.1f}%]   (statsmodels)")
    print(f"  Clopper-Pearson 95% [{lo2*100:.1f}%, {hi2*100:.1f}%]   (scipy)")

    import numpy as np, mpmath as mp
    mp.mp.dps = 20
    if refused:
        print(f"  mean cross-check: numpy {np.mean(refused):.6f} | "
              f"mpmath {mp.nstr(mp.fsum([mp.mpf(x) for x in refused])/len(refused), 8)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
