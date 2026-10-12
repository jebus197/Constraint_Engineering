#!/usr/bin/env python3
"""Would denying falsifiers access to the evidence directories break any of them?

WHY THIS MEASUREMENT GATES THE FIX. Both free seats of 2026-10-12 found that a
sandboxed falsifier can read this project's own evidence: the repository root is
in the observer's rendered allow set, so `experimental_notes/` and `bench/logs/`
are readable, and `tempfile.gettempdir()` additionally exposes 472 sibling panel
sandboxes. The sealed scoring key store is NOT reachable. Both seats specified
the same fix -- a deny tier checked BEFORE the allow test, so it closes every
root at once -- and both declined to write it, giving the same reason: the
observer is the harness's most safety-critical component and narrowing an
allowlist can refuse HONEST falsifiers. cc2 stated the missing piece plainly:
"a scratch-path inventory across archived falsifiers ... One line of code, one
measurement I did not have time to take."

THE FOUNDER'S RULING, 2026-10-12: *"Then what is the fix? If the models didn't
suggest any, and you didn't devise any, then that is not an ideal outcome. ... A
better outcome would be to derive the optimal fix, then test it in the upcoming
simulated run and program of study. ... You appear to be implying here that no
resolution can exist? Is that accurate?"* It is not accurate. This is the
measurement that was missing.

WHAT THIS COUNTS. Every falsifier source the archive holds, scanned for any
reference to the evidence regions a deny tier would close. A falsifier that
names one would be REFUSED by the fix, so the count is the fix's blast radius.

Usage: python3 scripts/does_any_falsifier_read_the_evidence_2026-10-12.py
"""
import collections
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: The regions a deny tier would close. Matched as PATH SEGMENTS so the same
#: rule covers the real tree, a staged clone under the temp dir, and a sibling
#: sandbox -- which is what makes one tier close both roots the seats named.
EVIDENCE_PATTERNS = (
    re.compile(r"experimental_notes"),
    re.compile(r"bench/logs|bench\\\\logs"),
    re.compile(r"seat_evidence"),
    re.compile(r"sandbox_harvest"),
)


def falsifier_sources():
    """(run, canonical_id, source) for every archived falsifier with a body."""
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        for cid, e in (((d or {}).get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            for key in ("falsifier_code", "falsifier_code_full"):
                src = e.get(key)
                if isinstance(src, str) and src.strip():
                    yield fp.parent.name, cid, src
                    break


def main() -> int:
    answer_help(__doc__, __file__)
    n = 0
    hits = []
    per_pattern = collections.Counter()
    for run, cid, src in falsifier_sources():
        n += 1
        matched = [p.pattern for p in EVIDENCE_PATTERNS if p.search(src)]
        if matched:
            hits.append((run, cid, matched))
            for m in matched:
                per_pattern[m] += 1

    if not n:
        print("no archived falsifier carries a source body; measurement void.")
        return 3

    print(f"archived falsifier sources scanned: {n}")
    print(f"sources naming an evidence region  : {len(hits)}")
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    k = len(hits)
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    print(f"  rate {k}/{n} = {k/n:.4%}")
    print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"    Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
    if per_pattern:
        print("\n  by region:")
        for pat, c in per_pattern.most_common():
            print(f"    {pat:<34}{c:>6}")
        print("\n  first few:")
        for run, cid, matched in hits[:8]:
            print(f"    {run[:44]:<44} {cid:<8} {matched}")

    print()
    if k == 0:
        print("VERDICT: NO archived falsifier reads an evidence region, so a deny")
        print("  tier over those regions has a measured blast radius of ZERO on")
        print("  the whole archive. The fix is safe to build and to test in the")
        print("  upcoming simulated run.")
        return 0
    print("VERDICT: some falsifiers DO name an evidence region. Read them before")
    print("  denying: an honest falsifier that needs one is a reason to scope the")
    print("  tier more narrowly, not to abandon it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
