#!/usr/bin/env python3
"""Does any REAL ladder record carry a verdict my no-reading sentinel set matches?

THE CLAIM UNDER TEST, AND IT IS MINE. On 2026-10-12 I repaired a cross-module
defect between the two free seats' blind-round fixes by distinguishing
SERVED-AND-NO-READING from SERVED-AND-RULED, keyed on
`NO_READING_ROUTING_VERDICTS = frozenset({"", "UNRESOLVED"})`. I measured three
outcomes and reported the repair as working. All three used a STUBBED ladder
result whose verdict I chose myself.

THE JOINT ROUND REFUTED IT. fable enumerated `bench.routing.route`'s reachable
verdicts and reported the intersection with my sentinel set as EMPTY. Reading
the source confirms the mechanism: `last_verdict` initialises to "UNTOOLABLE"
at bench/routing.py:207 and is only ever reassigned to "ERROR" or to whatever
`reverify_fn` returns. Nothing writes "" or "UNRESOLVED".

So the door never opens after a serve in production, and the composition defect
I reported as fixed is NOT fixed. A repair verified only against a mock I wrote
is a repair verified against my own expectations -- "verify the mechanism, not
the launch", and I did not.

THIS SCRIPT SETTLES IT ON THE ARCHIVE rather than on either reading: every
routing_history record in every archived registry, counted by verdict.

Usage: python3 scripts/my_sentinel_set_matched_nothing_2026-10-12.py
"""
import collections
import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def records():
    """Every routing_history record in every archived registry."""
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                 # noqa: BLE001
            continue
        reg = (d or {}).get("registry") or {}
        ents = reg.get("entries") or {}
        if not isinstance(ents, dict):
            continue
        for cid, e in ents.items():
            if not isinstance(e, dict):
                continue
            for r in (e.get("routing_history") or []):
                if isinstance(r, dict):
                    yield fp, cid, r


def main() -> int:
    answer_help(__doc__, __file__)
    import bench.reference_runner_v3 as rr
    sentinel = set(rr.NO_READING_ROUTING_VERDICTS)
    print(f"sentinel set under test: {sorted(sentinel)!r}")

    tally = collections.Counter()
    resolved_true = collections.Counter()
    n = 0
    for _fp, _cid, r in records():
        v = (r.get("verdict") or "").strip().upper()
        tally[v] += 1
        if r.get("resolved"):
            resolved_true[v] += 1
        n += 1

    if not n:
        print("NO archived ladder records found; the measurement is void.")
        return 3

    print(f"\narchived ladder records: {n}")
    print(f"{'verdict':<24}{'count':>8}{'of which resolved':>20}")
    for v, c in tally.most_common():
        print(f"  {v or '(empty)':<22}{c:>8}{resolved_true[v]:>20}")

    matched = sum(c for v, c in tally.items() if v in {s.upper() for s in sentinel})
    share = matched / n
    print(f"\nrecords my sentinel set MATCHES: {matched} of {n} = {share:.4%}")
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(matched, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, matched, n - matched + 1) if matched else 0.0
    hi2 = stats.beta.ppf(0.975, matched + 1, n - matched) if matched < n else 1.0
    print(f"  Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"  Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")

    if matched == 0:
        print("\nVERDICT: the sentinel set matches NOTHING in the archive.")
        print("  The door cannot open after any real serve. The repair is INERT")
        print("  in production and the composition defect STANDS.")
        return 0
    print("\nVERDICT: the sentinel set does match real records; the repair bites.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
