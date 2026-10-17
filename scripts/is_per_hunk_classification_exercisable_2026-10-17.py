#!/usr/bin/env python3
"""A19's last sub-part: per-hunk scoring, measured against the whole archive.

A19's design point is his, 2026-09-10, verbatim: *"Having the admissibility
switch off for prose targets is also questionable, as clearly it should simply
mark a purely prose input as 'inadmissible', while still solving any
computationally reducible elements within that prose! This is STEM. No one will
be using CDSFL to write poetry!"*

THE PER-FIX HALF WAS BUILT ON 2026-10-17: `_fix_touches_reducible` asks whether
a given fix edits a fenced listing or only the prose around it, so a prose edit
inside a markdown target is unscored while a code edit inside the same target
is scored. What remained named on the entry was finer still: PER-HUNK
classification, where one fix carries several SEARCH/REPLACE blocks and they do
not all touch the same kind of thing.

THIS MEASURES WHETHER THAT CAN EVER HAPPEN, rather than judging whether it is
worth building. Parsed with the PROJECT'S OWN parser,
`bench.build_acceptance.SEARCH_REPLACE`, rather than a second copy of the
pattern -- which matters, because the first version of this measurement used
`<{5,7}\\s*SEARCH` and the real marker is 4 angle brackets, so it matched
NOTHING and reported 0 single-hunk and 0 multi-hunk fixes across 25,445 texts.
A predicate that returns 0 for everything looks exactly like a clean result.

Costs nothing: reads the local archive and dispatches to no model.

Usage: python3 scripts/is_per_hunk_classification_exercisable_2026-10-17.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LOGS = ROOT / "bench" / "logs"
FIX_KEYS = ("fix", "proposed_fix", "fix_text", "patch")
FENCE = re.compile(r"^```", re.M)


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def _say(label, p):
    if p is None:
        print(f"  {label}: no denominator")
        return
    print(f"  {label}: {p['k']} of {p['n']} = {p['pct']:.4f}%")
    print(f"      Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"Clopper-Pearson [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%]  "
          f"scipy agrees {p['agrees']}")


def survey() -> dict:
    """Every fix text in the archive, bucketed by how many hunks it parses."""
    from bench.build_acceptance import SEARCH_REPLACE

    counts = {"total": 0, "one": 0, "many": 0, "none": 0, "mixed": 0}
    for path in sorted(LOGS.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8",
                                             errors="replace"))
        except (OSError, ValueError):
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    if (key in FIX_KEYS and isinstance(value, str)
                            and value.strip()):
                        counts["total"] += 1
                        hunks = SEARCH_REPLACE.findall(value)
                        if len(hunks) > 1:
                            counts["many"] += 1
                            paths = {h[0].strip() for h in hunks}
                            if len(paths) > 1 or FENCE.search(value):
                                counts["mixed"] += 1
                        elif len(hunks) == 1:
                            counts["one"] += 1
                        else:
                            counts["none"] += 1
                    else:
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)
    return counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.parse_args(argv)

    if not LOGS.exists():
        print("  no archive in this checkout; nothing can be measured and")
        print("  nothing will be claimed.")
        return 1

    c = survey()
    print("EVERY FIX TEXT IN THE ARCHIVE, BY HUNK COUNT")
    print(f"  fix texts found            : {c['total']}")
    print(f"  parsing exactly 1 hunk     : {c['one']}")
    print(f"  parsing more than 1 hunk   : {c['many']}")
    print(f"  parsing 0 hunks            : {c['none']}")
    if not c["total"]:
        print("  nothing to measure.")
        return 1

    _say("fixes with MORE THAN ONE hunk", _proportion(c["many"], c["total"]))
    _say("multi-hunk fixes of MIXED scope", _proportion(c["mixed"], c["total"]))

    parseable = c["one"] + c["many"]
    _say("single-hunk among PARSEABLE patches",
         _proportion(c["one"], max(parseable, 1)))

    print("\nWHAT THE 0-HUNK TEXTS ARE, so the figure is not left unexplained.")
    print("  They are prose fix PROPOSALS, some carrying a bare `<<<<` code")
    print("  block with no `SEARCH <path>` header, which the canonical parser")
    print("  correctly refuses. That is the named outcome REJECTED_NO_PATCH in")
    print("  `bench/build_acceptance.py`, not a hidden defect: a proposal that")
    print("  is not an applicable patch is a different thing from a patch that")
    print("  fails to apply, and this project's rule is that those 2 must")
    print("  never render identically.")

    print("\nTHE ANSWER")
    if c["many"] == 0:
        print("  PER-HUNK CLASSIFICATION IS NOT EXERCISABLE. Not one fix in the")
        print("  archive carries 2 hunks, so for every patch that exists,")
        print("  per-hunk classification and per-fix classification give the")
        print("  SAME answer -- and the per-fix half is built and guarded.")
        print("  A19's remaining sub-part is therefore covered by construction")
        print("  rather than deferred by judgement, which is a stronger claim")
        print("  and a checkable one: the moment a 2-hunk fix appears, the")
        print("  guard beside this script fails and says to build it.")
    else:
        print(f"  PER-HUNK CLASSIFICATION IS NOW EXERCISABLE: {c['many']} fix(es)")
        print("  carry more than 1 hunk, so per-fix and per-hunk can disagree.")
        print("  A19's remaining sub-part should be built.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
