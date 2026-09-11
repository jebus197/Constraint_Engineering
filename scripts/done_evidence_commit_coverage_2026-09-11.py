#!/usr/bin/env python3
"""Task V7: at the moment a DONE marker is written, how much of its evidence runs?

THE V3 INCIDENT V7 EXISTS TO CLOSE. Task V3 was marked DONE naming a test file
that was 10 of 10 RED at that moment, and the DONE-evidence guard stayed green
because it checks that the named file EXISTS, ASSERTS and is COLLECTED -- never
that it PASSES. V7 added `unsupported_done_entries`, which attributes a session's
failures back to the DONE entries that named them.

THE LIMIT V7'S OWN DOCSTRING CONCEDES, MEASURED HERE. It maps failures the
session ALREADY PRODUCED and runs nothing itself. A DONE marker is written in a
COMMIT, and the only thing a commit runs is `hooks/pre-commit`'s GUARDS list. So
the question is: how many DONE-evidence files are in that list?

The answer is the size of the concession, and nobody had measured it. Found
2026-09-11 by the cc2 seat in panel round 11; reproduced here before acceptance.

WHAT IS NOT FIXED HERE, and why. The right repair is a gate that runs the
evidence of any entry whose marker is newly DONE in `git diff --cached`. The seat
could not write it -- the panel sandbox has no `.git` -- and an untested hook
edit is the addition-nothing-reaches class. It is recorded as a recommendation
with its size attached, which is what a measurement is for.

THE SEAT MEASURED 3 OF 52 AND THIS MEASURES 2 OF 52, and the difference is not a
disagreement. Entries 4.2 and 7.3 named `test_recovery_memory_doc_repairs.py` --
a GUARD file, so it counted as covered -- while that test contains ZERO
references to either entry's subject. Re-pointing them at evidence that is
actually about them, the same night and on the other seat's finding, removed the
only covered file that was covered vacuously. **The coverage figure went DOWN by
0.19 percentage points because a lie was removed from the numerator**, which is
the honest direction and worth saying out loud: a guard listed in the hook does
not make an entry checked at commit time unless it checks that entry.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import task_list_markers as tlm  # noqa: E402

HOOK = REPO / "hooks" / "pre-commit"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def guard_files() -> list[str]:
    """The hook's GUARDS list, READ from the hook rather than restated here.

    Two representations of one list with no comparator is what
    `test_precommit_guard_2026-09-09.py` was caught doing on its first pass.
    """
    text = HOOK.read_text(encoding="utf-8")
    m = re.search(r'GUARDS="([^"]*)"', text, re.S)
    assert m, "hooks/pre-commit no longer carries a GUARDS list"
    return [t for t in m.group(1).split() if t.endswith(".py")]


def done_evidence() -> list[str]:
    out = set()
    for e in tlm.parse_entries(LIST):
        if e.state == "DONE":
            out.update(e.evidence)
    return sorted(out)


def main() -> int:
    guards = set(guard_files())
    evidence = done_evidence()
    covered = sorted(e for e in evidence if e in guards)
    n, k = len(evidence), len(covered)

    print(f"  DONE evidence files          : {n}")
    print(f"  hook GUARDS files            : {len(guards)}")
    print(f"  run at COMMIT time           : {k}")
    for c in covered:
        print(f"      {c}")
    print(f"  NOT run at commit time       : {n - k}")

    if not n:
        print("  no DONE entries name evidence; nothing to report")
        return 0

    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    from scipy.stats import beta as sbeta
    hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
    # ROUND OUTWARD. An interval reported narrower than it is overstates
    # confidence, which is the one direction that matters here.
    import math
    print(f"  commit-time coverage         : {k}/{n} = {k / n:.4%}")
    print(f"    Wilson 95%          : [{math.floor(lo * 1e6) / 1e4:.4f}%, "
          f"{math.ceil(hi * 1e6) / 1e4:.4f}%]  (statsmodels)")
    print(f"    Clopper-Pearson 95% : [{lo_c:.4%}, {hi_c:.4%}]  (statsmodels/beta)")
    print(f"    Clopper-Pearson 95% : [{lo_c:.4%}, {hi_s:.4%}]  (scipy cross-check, "
          f"upper agrees to {abs(hi_s - hi_c):.1e})")
    print(f"\n  So the V3 window is open for {n - k} of {n} DONE entries: mark "
          f"DONE, commit,\n  the hook runs {len(guards)} files that are green, "
          f"and the full suite is minutes away.")
    print("  THE FIX IS A GATE THAT RUNS THE EVIDENCE OF ANY ENTRY NEWLY DONE IN "
          "`git diff --cached`.\n  It is recommended, not enacted: an untested "
          "hook edit is an addition nothing reaches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
