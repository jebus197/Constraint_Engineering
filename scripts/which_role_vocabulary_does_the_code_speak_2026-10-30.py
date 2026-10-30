#!/usr/bin/env python3
"""Which of the 2 role vocabularies the live code actually speaks.

WHY THIS EXISTS, AND WHAT IT DELIBERATELY DOES NOT DECIDE. Task entry B21 turns
on a design question the founder has not answered: are the STRUCTURAL roles that
exist in code and the FUNCTIONAL roles he named on 2026-10-19 one dimension to be
reconciled, or 2 orthogonal dimensions needing 2 layers?

  structural, `Role = Literal[...]` at bench/experiment_11_orchestrator.py:59 --
      collator, player_manager, participant: where a seat SITS in the topology.
  functional, his words -- worker, classifier, orchestrator: what a model DOES.

`classifier` has no counterpart in the enum and `collator` has none in his list,
so they overlap partially rather than cleanly.

THIS SCRIPT MEASURES INCUMBENCY, WHICH IS A COST AND NOT AN ARGUMENT. It counts
each role word where it appears as a QUOTED VALUE in live code, because a bare
word may be prose while a quoted one is a value some branch compares against. A
high structural count says reconciling into 1 dimension would touch many call
sites; it does NOT say the structural vocabulary is right. 63 to 4 is what any
vocabulary months old would show against one proposed 11 days ago, and choosing
on that basis is choosing the incumbent BECAUSE it is the incumbent -- the
reasoning this project exists to refuse. `measured-rate-travels-with-its-script`
is why the figure lives here rather than only in the entry that cites it.

THE LIMIT. A quoted occurrence is not necessarily a live comparison: a fixture, a
docstring example or a log message counts too. So this is an UPPER BOUND on the
reconciliation cost, not the exact number of branches that would change.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Where a seat SITS. The enum that exists, and is required with no default.
STRUCTURAL = ("collator", "player_manager", "participant")
#: What a model DOES. His vocabulary, 2026-10-19.
FUNCTIONAL = ("worker", "classifier", "orchestrator")
#: Directories whose contents are not live code: seat sandboxes and run logs.
_SKIP = ("logs", "seat_evidence", "__pycache__", ".git")


def quoted_uses(roots=("bench", "scripts")) -> dict:
    """{word: [(path, count)]} for each role word used as a quoted value."""
    out: dict[str, list] = {w: [] for w in STRUCTURAL + FUNCTIONAL}
    pats = {w: re.compile(rf'["\']{re.escape(w)}["\']') for w in out}
    for r in roots:
        for p in (REPO / r).rglob("*.py"):
            if any(x in p.parts for x in _SKIP):
                continue
            #: ★ EXCLUDE THIS FILE FROM ITS OWN SURVEY. Caught on first run:
            #: the figure came out 66 of 73 where an ad-hoc count minutes
            #: earlier gave 63 of 67, and the whole difference is this script,
            #: which quotes every role word in order to search for them. An
            #: instrument that measures its own text inflates whatever it
            #: measures -- the same defect the kappa census had to be repaired
            #: for on 2026-10-17, where it counted its own prose.
            if p.resolve() == pathlib.Path(__file__).resolve():
                continue
            try:
                txt = p.read_text(errors="ignore")
            except OSError:                                    # pragma: no cover
                continue
            for w, pat in pats.items():
                n = len(pat.findall(txt))
                if n:
                    out[w].append((str(p.relative_to(REPO)), n))
    return out


def totals(uses: dict) -> tuple[int, int]:
    s = sum(n for w in STRUCTURAL for _, n in uses[w])
    f = sum(n for w in FUNCTIONAL for _, n in uses[w])
    return s, f


def _interval(k: int, n: int) -> tuple[float, float]:
    """Wilson from statsmodels, re-derived in NumPy and ASSERTED equal."""
    import numpy as np
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    z = stats.norm.ppf(0.975)
    ph = k / n
    d = 1 + z * z / n
    ctr = (ph + z * z / (2 * n)) / d
    half = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    assert np.allclose([ctr - half, ctr + half], [lo, hi]), (
        "the 2 Wilson derivations disagree; the figure may not be quoted")
    return lo, hi


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the counts as JSON")
    args = ap.parse_args(argv)

    uses = quoted_uses()
    s, f = totals(uses)
    n = s + f
    if args.json:
        print(json.dumps({
            "structural": {w: sum(c for _, c in uses[w]) for w in STRUCTURAL},
            "functional": {w: sum(c for _, c in uses[w]) for w in FUNCTIONAL},
            "structural_total": s, "functional_total": f, "total": n,
            "structural_share": s / n if n else None,
            "structural_share_wilson": list(_interval(s, n)) if n else None,
            "files_touched_by_structural": sorted(
                {p for w in STRUCTURAL for p, _ in uses[w]}),
        }, indent=2))
        return 0

    print("role words as QUOTED VALUES in live code (bench/, scripts/)\n")
    for label, group in (("STRUCTURAL, the enum that exists", STRUCTURAL),
                         ("FUNCTIONAL, his words of 2026-10-19", FUNCTIONAL)):
        print(f"  {label}:")
        for w in group:
            c = sum(x for _, x in uses[w])
            print(f"    {w:16s} {c:>4} occurrence(s) across {len(uses[w])} file(s)")
    if not n:
        print("\n  no role words found at all, which cannot be right")
        return 1
    lo, hi = _interval(s, n)
    files = len({p for w in STRUCTURAL for p, _ in uses[w]})
    print(f"\n  structural share: {s}/{n} = {s/n:.6f}  Wilson [{lo:.6f}, {hi:.6f}]")
    print(f"  structural words appear in {files} distinct file(s)")
    print("\n  THIS IS A COST, NOT AN ARGUMENT. Reconciling into 1 dimension would")
    print(f"  touch those {s} quoted values; treating the 2 as orthogonal layers")
    print("  touches none of them. Which answer is RIGHT about what a role IS is")
    print(f"  his to decide, and a word count cannot settle it: {s} to {f} is what")
    print("  any months-old vocabulary shows against one proposed 11 days ago.")
    #: ★ DERIVED, NOT TYPED. This line read "63 to 4" as a literal and was
    #: already wrong by the time it printed, because the numbers above are
    #: computed and this one was remembered. A figure in the same breath as its
    #: own computation must come from that computation.
    print("\n  AND IT IS AN UPPER BOUND. A quoted occurrence may be a fixture, a")
    print("  docstring example or a log message rather than a live comparison.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
