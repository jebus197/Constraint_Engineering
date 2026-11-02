#!/usr/bin/env python3
"""How many archived runs declared a domain the composer ships no layer for?

FOUND BY WATCHING A LIVE RUN, 2026-11-02, which is why it exists. Relaunching
`study_run1b` under `cy`, the terminal tail carried:

    Composer: domain 'statistics' composes NO DOMAIN LAYER (no such directory
    under bench/directives). The manifest will still record domain='statistics',
    so this is the only notice.

The run declares `--domain statistics`; `bench/directives/` ships 11 layers and
`statistics` is not among them. So the manifest records a domain the composed
directive set never received.

WHAT WAS CHECKED BEFORE CALLING IT A DEFECT, because the first 2 explanations
were both wrong.
  * Was a `statistics` layer REMOVED? NO. `git log --all` over
    `bench/directives/statistics*` returns 0 commits: it never existed, so
    `additive-standard`'s removal clause is not engaged.
  * Did the 2026-10-03 run carry the same warning? NO -- 0 occurrences in its
    console log. The NOTICE was added later (commit 5f8f3b9c), so earlier runs
    carry the same condition SILENTLY. The warning did not create the gap; it
    revealed it.

WHY IT MATTERS BEYOND 1 RUN. `statistics` is not an incidental label: the
project's own tool-constraint notes place Exp 45 in `domain=statistics` scope. A
domain that reaches no directives means the per-domain half of the 4-layer
policy composition contributed nothing for those runs, while every manifest
records a domain as though it had.

TOOLS, 2 per the 2026-04-21 rule: the proportion carries a Wilson interval from
a closed form cross-checked against statsmodels, required to agree to 1e-12.
Counts come from each run's own `_declared_config`, not from a file name.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DIRECTIVES = REPO / "bench" / "directives"
LOGS = REPO / "bench" / "logs"


def _wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, c - h), min(1.0, c + h))


def shipped() -> set[str]:
    return {p.name for p in DIRECTIVES.iterdir() if p.is_dir()} if DIRECTIVES.is_dir() else set()


def declared() -> collections.Counter:
    out: collections.Counter = collections.Counter()
    for p in LOGS.rglob("*_report.json"):
        s = str(p)
        if "sandbox_harvest" in s or "panel_worktree" in s:
            continue
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:                                        # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        cfg = d.get("_declared_config") or {}
        dom = cfg.get("domain") or d.get("domain")
        if dom:
            out[str(dom)] += 1
    return out


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint

    ship, doms = shipped(), declared()
    total = sum(doms.values())
    print("=" * 74)
    print("HOW MANY RUNS DECLARED A DOMAIN THE COMPOSER SHIPS NO LAYER FOR?")
    print("=" * 74)
    print(f"\n  shipped layers ({len(ship)}): {sorted(ship)}")
    if total == 0:
        print("\n  0 runs record a domain -- VACUOUS.")
        return 1

    print(f"\n  declared by {total} archived run(s):")
    missing = 0
    for dom, n in doms.most_common():
        ok = dom in ship
        if not ok:
            missing += n
        print(f"      {dom:22} {n:3} run(s)   "
              f"{'shipped' if ok else '*** NO DOMAIN LAYER ***'}")

    lo_c, hi_c = _wilson(missing, total)
    lo_s, hi_s = proportion_confint(missing, total, alpha=0.05, method="wilson")
    agree = abs(lo_c - lo_s) < 1e-12 and abs(hi_c - hi_s) < 1e-12
    print(f"\n  runs with NO layer for their declared domain: {missing}/{total} "
          f"= {missing/total:.6f}")
    print(f"      closed form : Wilson 95% [{lo_c:.6f}, {hi_c:.6f}]")
    print(f"      statsmodels : Wilson 95% [{lo_s:.6f}, {hi_s:.6f}]  agree={agree}")
    if not agree:
        print("      ★ the 2 tools disagree, so no interval may be quoted.")
        return 4

    print("\nWHAT THIS IS AND IS NOT")
    print("  IT IS NOT a removal: `git log --all` over bench/directives/statistics*")
    print("  returns 0 commits, so no layer was ever deleted.")
    print("  IT IS NOT caused by the warning: the notice arrived after 2026-10-03,")
    print("  so the runs before it carry the identical condition in silence.")
    print("  IT IS a per-domain policy layer contributing 0 directives while every")
    print("  manifest records the domain as though it had contributed.")
    print("\n  NOT REPAIRED HERE: writing a domain layer is authoring experimental")
    print("  directives, which is the founder's, not a mechanical fix.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO / "scripts"))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
