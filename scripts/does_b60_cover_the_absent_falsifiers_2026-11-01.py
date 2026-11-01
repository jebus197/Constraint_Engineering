#!/usr/bin/env python3
"""Does B60's "guards lost nothing" claim extend to the ABSENT falsifiers?

B60 measured the unapplied-fix store and reported that the fold-back discipline
has lost no coverage: across **42 DIVERGED guards** the live copy carries the
same test count or MORE in every case, Wilson 95% [0.000000, 0.083799]. That
measurement is sound and is not disputed here.

THE QUESTION THIS SCRIPT ASKS IS NARROWER AND WAS NOT ASKED. "Diverged" means a
file that exists in BOTH the sandbox and the live tree. The store also holds
**36 falsifiers** which are ABSENT from the tree entirely, and an absent file has
no live counterpart to compare test counts against -- so the 42-guard
measurement is silent about them. B60's sentence is easy to read as "nothing was
lost", and this script exists to bound that reading rather than to overturn it.

THE CONCRETE CASE THAT PROMPTED IT. The joint round of 2026-10-31 produced
`falsifier_does_the_polarity_inversion_move_gamma_2026-10-31.py`, 153 lines,
absent from the tree. It imports the REAL runner and the REAL gate and asserts a
property: that driving proof-polarity falsifiers through `apply_falsifier_verdicts`
does NOT move the critical novelty series, gamma, or the round at which the
K-consecutive-zero convergence test first passes. The live tree's nearest file,
`test_the_polarity_hazard_reachability_2026-10-31.py`, has 10 tests -- and all 10
are about the REACHABILITY PRODUCER (which date arm a run falls in, whether an
entry is collected, whether the producer excludes its own lines). It shares
exactly 1 subject symbol with the falsifier and asserts nothing about gamma.

SO THE 2 FILES ARE NOT SUBSTITUTES, AND THE HONEST STATEMENT IS BOUNDED:
coverage was not lost among the DIVERGED guards, and at least 1 ABSENT falsifier
carries a property the live tree does not asserts anywhere. Whether that matters
is a separate question -- the property concerns a PROSPECTIVE state (cc2's
unmerged round-1 guard), and `is_the_polarity_hazard_reachable_2026-10-31.py`
returns PROSPECTIVE-ONLY -- so a falsifier for a defect the tree does not have is
correctly classified as evidence about a proposal rather than as missing
coverage. The point is that the classification does the work, not the count.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DIFFS = sorted(REPO.glob("bench/logs/**/seat_proposals.diff"))
LIVE_TESTS = REPO / "bench" / "tests"

_NEWFILE = re.compile(r"(?m)^\+\+\+ (?:b/)?(.*?)(?:\t|$)")
_DEFTEST = re.compile(r"(?m)^\+\s*def (test_[A-Za-z0-9_]+)")
_SYMS = re.compile(
    r"\b(_settled_novelty_series|spec_verification_factor|_estimate_gamma|"
    r"apply_falsifier_verdicts|effective_severity|_interpret_gamma)\b")


def proposed_test_files() -> dict[str, str]:
    """Map a proposed bench/tests path to the added body, across all rounds."""
    out: dict[str, str] = {}
    for d in DIFFS:
        try:
            text = d.read_text(errors="ignore")
        except OSError:
            continue
        for chunk in re.split(r"(?m)^--- ", text):
            m = _NEWFILE.search(chunk)
            if not m:
                continue
            path = m.group(1)
            if "/bench/tests/" not in path:
                continue
            name = path.split("/bench/tests/")[-1]
            if not name.endswith(".py"):
                name += ".py"
            body = "\n".join(l[1:] for l in chunk.splitlines()
                             if l.startswith("+") and not l.startswith("+++"))
            if len(body) > len(out.get(name, "")):
                out[name] = body
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    proposed = proposed_test_files()
    absent, diverged = {}, {}
    for name, body in proposed.items():
        (diverged if (LIVE_TESTS / name).exists() else absent)[name] = body

    rows = []
    for name, body in sorted(absent.items()):
        syms = sorted(set(_SYMS.findall(body)))
        rows.append({
            "file": name,
            "is_falsifier": name.startswith("falsifier_"),
            "lines": len(body.splitlines()),
            "declared_test_fns": sorted(set(_DEFTEST.findall(body))),
            "runner_symbols_asserted_on": syms,
        })

    if args.json:
        print(json.dumps({"absent": rows, "diverged": sorted(diverged)},
                         indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"proposed bench/tests files found across {len(DIFFS)} round diff(s): "
          f"{len(proposed)}")
    print(f"  DIVERGED (exist live, so B60's 42-guard comparison applies): "
          f"{len(diverged)}")
    print(f"  ABSENT   (no live counterpart, so it does NOT apply):        "
          f"{len(absent)}")
    print()
    if not rows:
        print("No absent proposed test files. B60's reading needs no bound.")
        return 0
    for r in rows:
        kind = "FALSIFIER" if r["is_falsifier"] else "GUARD"
        print(f"  [{kind}] {r['file']}  ({r['lines']} lines)")
        if r["declared_test_fns"]:
            print(f"        test fns: {', '.join(r['declared_test_fns'][:4])}")
        if r["runner_symbols_asserted_on"]:
            print("        asserts against real runner symbols: "
                  + ", ".join(r["runner_symbols_asserted_on"]))
        else:
            print("        asserts against no runner symbol this script knows")
    print()
    print("WHAT THIS DOES AND DOES NOT SHOW.")
    print("  It does NOT refute B60: the 42-diverged-guard result stands.")
    print("  It DOES bound it: an absent file has no live counterpart, so a")
    print("  test-count comparison cannot speak for it, and the sentence")
    print("  'the fold-back discipline has lost no coverage' must be read as")
    print("  'among the diverged guards'. For the absent falsifiers the")
    print("  justification is CLASSIFICATION -- a falsifier for a prospective")
    print("  defect is evidence about a proposal -- not a count.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
