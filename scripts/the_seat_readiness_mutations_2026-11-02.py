#!/usr/bin/env python3
"""Does the seat-readiness guard actually bite? 6 reversions, each expected RED.

A guard that has not been broken is a hypothesis about a guard. Each mutation
below reverses exactly 1 property the guard claims to hold, runs the guard, and
the mutation PASSES only if the guard turns red. The tree is restored and
verified byte-identical afterwards.

★ IT RESTORES WHAT IT FOUND, not what it assumes. `git checkout --` would discard
any uncommitted work in the same file, which this project has already paid for
once; the original bytes are read into memory first and written back.
"""
from __future__ import annotations
import argparse

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = "bench/tests/test_a_seat_declares_what_it_is_missing_2026-11-02.py"

SR = REPO / "bench" / "seat_readiness.py"
UX = REPO / "bench" / "ux_backend_2026-10-20.py"

#: (name, file, find, replace, why it must turn the guard red)
MUTATIONS = [
    ("credential value is returned instead of a boolean", SR,
     "    return credential_source(api) is not None",
     "    return os.environ.get(names[0]) or (credential_source(api) is not None)",
     "a leaked key would reach the payload"),
    ("the keying is copied back in, all on the composer key", SR,
     "    for table, key, _field, _decode, where in registration_targets(label, ckey):",
     "    from bench import runner_core as _rc\n"
     "    from bench.cdsfl_registry import composer as _co\n"
     "    _own = [(_co.COMPOSER_MODEL_MAP, ckey, '', None, 'composer.COMPOSER_MODEL_MAP'),\n"
     "            (_co.MODEL_COHERENCE_BUDGETS, ckey, '', None, 'composer.MODEL_COHERENCE_BUDGETS'),\n"
     "            (_co.PHENOTYPE_TRANSFORMS, ckey, '', None, 'composer.PHENOTYPE_TRANSFORMS'),\n"
     "            (_rc.INITIAL_FINGERPRINTS, ckey, '', None, 'runner_core.INITIAL_FINGERPRINTS'),\n"
     "            (_rc.MODEL_SPECS, ckey, '', None, 'runner_core.MODEL_SPECS')]\n"
     "    for table, key, _field, _decode, where in _own:",
     "the single declaration is bypassed and the original bug returns"),
    ("not-asked is reported as absent", SR,
     '            "has_route": (cfg is not None) if asked_about_routes else None,',
     '            "has_route": cfg is not None,',
     "absence of evidence would be reported as evidence of absence"),
    ("the removed second declaration comes back", SR,
     '    raise NotImplementedError(\n'
     '        "the table keying is declared once, in "\n'
     '        "model_admission.registration_targets; call registration_gaps")',
     "    return []",
     "a second home for the keying would be reachable again"),
    ("a credential name the dispatcher never reads is added", SR,
     '    "deepseek": ("DEEPSEEK_API_KEY",),',
     '    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_SECRET_TOKEN_XYZ"),',
     "a UX would report a configured seat as unconfigured"),
    ("the 2-roster check stops reporting BOTH directions", SR,
     '        "dispatched_not_counted": sorted(ds - cs),\n'
     '        "counted_not_dispatched": sorted(cs - ds),',
     '        "dispatched_not_counted": sorted(ds - cs),\n'
     '        "counted_not_dispatched": [],',
     "a seat counted but never dispatched would inflate a denominator "
     "unreported"),
    ("2 empty rosters are read as agreement", SR,
     '        "agree": bool(ds) and ds == cs,',
     '        "agree": ds == cs,',
     "the vacuity trap: 2 empty lists are equal and prove nothing"),
    ("a Seats tab is added to his interface", UX,
     'TABS = ("Orchestrator", "Findings", "Evidence", "Explorer",',
     'TABS = ("Seats", "Orchestrator", "Findings", "Evidence", "Explorer",',
     "wiring a function would re-specify the interface he set"),
]


def run_guard() -> bool:
    """True if the guard is GREEN."""
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def _summary() -> str:
    """The harness's own first docstring line, so `--help` needs no new prose."""
    doc = (__doc__ or "").strip()
    return doc.splitlines()[0] if doc else "mutation harness; writes and restores"


def main() -> int:
    # ★ `--help` MUST NOT MUTATE ANYTHING, 2026-11-03. This harness WRITES: it
    # reverses a property in the tree, runs the suite, then restores. With no
    # parser, `--help` fell straight through to that work, so asking what the
    # script does would have mutated the repository and then put it back -- a
    # write that leaves no diff is still a write, and a concurrent reader would
    # have seen the mutated state. His standing rule is that a `--help` must
    # never cost money; here it could have cost a tree.
    #
    # Measured by `scripts/help_writers_rate_2026-09-17.py`: 5 of 609 scripts
    # wrote and ignored the flag -- 0.8210%, Wilson 95% [0.3512%, 1.9074%],
    # Clopper-Pearson [0.2671%, 1.9055%] -- and all 5 were mutation harnesses
    # written on 2026-11-02, so this is 1 defect made 5 times in 1 day.
    argparse.ArgumentParser(
        description=_summary()).parse_args()
    print("=" * 74)
    print("MUTATION TEST: 6 reversions, each expected to turn the guard RED")
    print("=" * 74)

    if not run_guard():
        print("  BASELINE IS ALREADY RED. Fix that before mutating.")
        return 1
    print("  baseline: GREEN")
    print()

    originals = {SR: SR.read_text(), UX: UX.read_text()}
    red = 0
    try:
        for name, path, find, repl, why in MUTATIONS:
            src = originals[path]
            if find not in src:
                print(f"  [ANCHOR GONE] {name}")
                print(f"                the mutation could not be applied, so "
                      f"nothing was tested")
                continue
            path.write_text(src.replace(find, repl, 1))
            green = run_guard()
            path.write_text(src)                  # restore before the next one
            if green:
                print(f"  [GREEN -- BAD] {name}")
                print(f"                 {why}, and the guard did not notice")
            else:
                red += 1
                print(f"  [RED  -- GOOD] {name}")
    finally:
        for path, text in originals.items():
            path.write_text(text)

    ok = run_guard()
    print()
    print("=" * 74)
    print(f"  {red} of {len(MUTATIONS)} mutations turned the guard RED")
    print(f"  tree restored and guard green again: {ok}")
    if red == len(MUTATIONS) and ok:
        print("  EVERY CLAIMED PROPERTY BITES.")
        return 0
    print("  AT LEAST 1 PROPERTY IS NOT ENFORCED. The guard overstates itself.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
