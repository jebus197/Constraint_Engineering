#!/usr/bin/env python3
"""How many live guards decide an identity with a predicate narrower than their class?

4 instances were found by hand on 2026-11-13, each while chasing something else:
a design triage keyed on (seat, path) when a seat can propose a path twice; a
parked filter keyed on a letter-and-digits code when 36 of 324 entries are
numeric; `blocker_triage` keyed on a commit board when a clean-suite run holds
the tree more strictly; `cy_monitor_gate` keyed on a simulated experiment when a
full-suite run is the longest process on the machine.

4 hand-found instances are OBSERVATIONS, not a rate. This enumerates the class
mechanically so the claim has a denominator.

★ WHAT IT CAN AND CANNOT DECIDE. It finds PROCESS detectors -- `pgrep -f
"<literal>"` -- and reports whether each takes 1 pattern or several. Whether a
1-pattern detector is WRONG depends on what else it should match, which is
judgement and is NOT decided here: the script reports the shape and names the
processes this project actually runs long enough to matter, and a reader
decides. Counting a 1-pattern detector as a defect would be the flattering
measure this project's record names 3 times.

★ ARCHIVED EVIDENCE IS EXCLUDED, by the lesson of 2026-11-13: a census over
"all live source" silently counted 359 archived files from 63 panel rounds and
moved a figure by 3 per cent.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
#: Named positively: the directories that hold LIVE code.
LIVE_DIRS = ("scripts", "bench", "hooks")
#: Excluded, and each for a stated reason.
EXCLUDE = (
    "bench/logs",                      # run output, not source
    "experimental_notes/seat_evidence",  # other models' sandbox output
    "experimental_notes/evidence",     # archived panel records
    "/tests/",                         # a guard's own guard
    "__pycache__",
)
PGREP = re.compile(r"""pgrep["'\s,\]]+.*?-f["'\s,\]]+["']([^"']+)["']""", re.S)

#: ★ THE PRODUCER AND ITS GUARD ARE APPARATUS, NOT POPULATION. This file holds
#: the detector pattern itself, so without naming it here the census counts
#: ITSELF and the figure moved 3 of 3 to 4 of 4 the moment it was committed --
#: the exact failure recorded on 2026-11-13 as "a population must exclude its
#: own instruments", walked into by the file describing it. BOTH figures are
#: printed below, excluded and included, so a reader sees the size of the
#: effect rather than a quietly smaller denominator.
APPARATUS = frozenset({
    "scripts/a_guards_predicate_can_be_narrower_than_its_class_2026-11-13.py",
})
PGREP_VAR = re.compile(r"""\[\s*["']pgrep["']\s*,\s*["']-f["']\s*,\s*([A-Za-z_][\w.\[\]]*)""")

#: Long-running things this project actually starts. Named so a reader can see
#: what a 1-pattern detector might be missing, NOT so the script can judge.
LONG_RUNNING = {
    "a full test suite":      "pytest bench/tests",
    "a commit board":         "cdsfl_sv.py --commit",
    "a simulated experiment": "run_simulated_experiment.py",
    "a panel round":          "confer_maths_panel",
}


def live_files() -> list[pathlib.Path]:
    out = []
    for d in LIVE_DIRS:
        for p in (REPO / d).rglob("*.py"):
            rel = str(p.relative_to(REPO))
            if any(x in rel for x in EXCLUDE):
                continue
            out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    files = live_files()
    print(f"  live python files examined : {len(files)}")
    print(f"  directories                : {', '.join(LIVE_DIRS)}")
    print(f"  excluded                   : {', '.join(EXCLUDE)}")
    print()

    detectors = []
    for p in files:
        src = p.read_text(encoding="utf-8", errors="replace")
        lits = PGREP.findall(src)
        vars_ = PGREP_VAR.findall(src)
        if not lits and not vars_:
            continue
        detectors.append((p.relative_to(REPO), sorted(set(lits)), sorted(set(vars_))))

    included = len(detectors)
    detectors = [d for d in detectors if str(d[0]) not in APPARATUS]
    print(f"  files containing a process detector: {len(detectors)} "
          f"(excluding apparatus; {included} including it)")
    one_pattern = 0
    for rel, lits, vars_ in detectors:
        n = len(lits) + len(vars_)
        shape = "1 pattern" if n == 1 else f"{n} patterns"
        if n == 1:
            one_pattern += 1
        print(f"    {str(rel):52s} {shape}")
        for lit in lits:
            missed = [name for name, pat in LONG_RUNNING.items() if pat != lit]
            print(f"        literal {lit!r}")
            print(f"          does NOT match: {', '.join(missed)}")
        for v in vars_:
            #: ★ A VARIABLE IS REPORTED AS A VARIABLE, NOT RESOLVED. A first
            #: attempt read the tuple it names and printed an arity; it saw a
            #: LOOP variable -- `blocker_triage.py` was widened to a tuple on
            #: 2026-11-13 and iterates `for _pat in _BOARD_PATTERNS` -- and
            #: printed the nonsense `_pat]`. Resolving a loop variable to its
            #: iterable needs the syntax tree, not a regex, and a wrong arity
            #: is worse than an absent one in a census whose whole subject is
            #: detectors narrower than they look.
            print(f"        via variable {v.rstrip(chr(93))} -- arity NOT resolved; read the "
                  f"file to see how many patterns it holds")
    print()
    print(f"  detectors taking exactly 1 pattern: {one_pattern} of {len(detectors)}")
    if detectors:
        from statsmodels.stats.proportion import proportion_confint
        import numpy as np
        k = one_pattern
        n = len(detectors)
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        z = 1.959963984540054
        pr = k / n
        d = 1 + z * z / n
        cc = (pr + z * z / (2 * n)) / d
        hh = z * np.sqrt(pr * (1 - pr) / n + z * z / (4 * n * n)) / d
        print(f"    share {k}/{n} = {pr:.6f}")
        print(f"    Wilson          statsmodels [{w[0]:.6f}, {w[1]:.6f}]  "
              f"numpy [{cc - hh:.6f}, {cc + hh:.6f}]")
        print(f"    Clopper-Pearson statsmodels [{c[0]:.6f}, {c[1]:.6f}]")
    print()
    print("  ★ A 1-PATTERN DETECTOR IS NOT AUTOMATICALLY A DEFECT. It is a defect")
    print("    only if something it should see is not in its pattern, which is a")
    print("    judgement about purpose. This reports the shape and what each")
    print("    literal does not match; it does not score them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
