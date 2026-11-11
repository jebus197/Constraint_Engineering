# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'tonights_build_review_b22_b88_b105_2026-11-10_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e2b3b4627980815574c9c06134a0552c9e0cebc0186c661f13d475e50d39ddaa
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Removing the launcher's default suite disabled fold-fixes-back on default runs.

WHAT CHANGED. `bench/tools/run_simulated_experiment.py:328` used to declare
`--test-cmd` with the immune-memory suite as its default, so a run naming no
suite inherited a suite unrelated to its target and the e2 regression gate
returned a constant 0.9454545454545454 on prose. The default is now `None` and
the gate is EXCLUDED rather than faked -- correct, and `_run_effect_regression`
(`bench/reference_runner_v3.py:15447`) abstains cleanly while `compute_sk`
renormalises the remaining gate weights at `:16186-16191`.

WHAT NOBODY CHECKED. `test_cmd` is not only the e2 gate's input. It is also the
gate on FOLD-FIXES-BACK. `_apply_back_gate` (`bench/reference_runner_v3.py:12975`)
returns at `:13201-13202`

    if not test_cmd:
        return False, "no test_cmd configured (cannot gate)"

for every PYTHON target. So a run that names no suite now REFUSES 100% of
promotions: every CLOSED finding is rejected and the artefact is never updated.
The faked gate was replaced not by an excluded gate but, on this path, by a
DISABLED FEATURE. Under the additive standard that is a removal, and no
committed measurement shows the replacement dominates on the fold-back
property. The guard shipped with the change,
`bench/tests/test_the_launcher_substitutes_no_suite_2026-11-11.py`, stops at
the parser namespace and at a NON-Python target (`:95` passes `""` with
`domain=""`); it never asserts what happens to a Python target's promotions.

THE SECOND, SIMPLER BREAKAGE. `scripts/falsifier_supply_fable_2026-09-30.py:181-183`
asserts that the launcher's `--test-cmd` declaration still names
`test_immune_memory_consumption.py` and `test_immune_memory_evaluation.py -q`.
It does not. That rescued falsifier now asserts the opposite of the truth. It
is not executed by `bench/tests/`, so nothing goes red; it fails only by hand.

THE FIX THIS ARGUES FOR is not restoring a wrong default. It is that a run
whose target is Python and which names no suite should REFUSE TO START, the
way `bench/reference_runner_v3.py` already refuses to start when no plaintext
scoring key check is available -- fail loud, not fail silent-and-promote-nothing.
That is a launcher-level ruling and is reported, not taken unilaterally.

FALSIFIER CONTRACT. Imports the real modules; nothing is retyped. Prints
FALSIFIED and raises AssertionError when either breakage is present.

Run:  python3 scripts/a_default_run_now_folds_nothing_back_2026-11-11.py
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

import importlib                                             # noqa: E402

PY_TARGET = "bench/thing.py"


def main() -> int:
    rr = importlib.import_module("bench.reference_runner_v3")
    broken = []

    print("A. fold-fixes-back on a PYTHON target, by named suite")
    rows = []
    for tc, label in ((None, "no suite named (the new default)"),
                      ("", "empty suite"),
                      ("python3 -m pytest -q", "a suite IS named")):
        ok, why = rr._apply_back_gate("repaired", PY_TARGET, tc or "",
                                      finding={"description": "x"}, domain="")
        rows.append((tc, ok))
        print(f"   test_cmd={tc!r:24s} promotes={ok!s:5s}  {label}")
        print(f"      reason: {why[:72]!r}")
    no_suite_ok = rows[0][1]
    named_ok = rows[2][1]
    if (not no_suite_ok) and named_ok:
        broken.append(
            "a Python-target run naming no suite promotes NOTHING, while the "
            "same run with a suite promotes -- fold-fixes-back is disabled by "
            "the default removal, not merely ungated")

    print("\nB. the rescued falsifier's pinned assertion about the launcher")
    src = (ROOT / "bench/tools/run_simulated_experiment.py").read_text(
        encoding="utf-8")
    i = src.index('dest="test_cmd"')
    frag = src[i:i + 400]
    names_old = ("test_immune_memory_consumption.py" in frag
                 and "test_immune_memory_evaluation.py -q" in frag)
    print(f"   launcher still names the immune-memory suite : {names_old}")
    print(f"   scripts/falsifier_supply_fable_2026-09-30.py:181 asserts it does")
    if not names_old:
        broken.append(
            "scripts/falsifier_supply_fable_2026-09-30.py:181-183 asserts the "
            "launcher names the immune-memory suite; it does not, so that "
            "rescued falsifier now asserts the opposite of the truth and no "
            "test in bench/tests/ executes it")

    if broken:
        print("\nFALSIFIED")
        for b in broken:
            print(f"  - {b}")
        raise AssertionError("; ".join(broken))

    print("\nCLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
