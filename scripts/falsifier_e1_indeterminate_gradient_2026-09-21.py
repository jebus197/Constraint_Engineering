#!/usr/bin/env python3
"""Falsifier: the e1_efficacy repair rewards crashing the probe.

Panel seat (Claude, free), 2026-09-21. Defect demonstrated:

  With clean ruff+bandit baselines, a fix whose falsifier RUNS on the
  patched copy and still fires (FIX_INEFFECTIVE) scores sk = 0.6, while
  a fix that makes its own falsifier CRASH on the patched copy
  (INDETERMINATE_OTHER, reached only AFTER a CONFIRMED baseline, so the
  fix itself is the change that broke the probe) drops the gate and
  scores sk = 1.0. The repair therefore pays +0.4 sk for breaking the
  measuring instrument -- in a project whose archive holds a documented
  reward-hacking incident (Exp 48 C0012). NO_BASELINE / NOT_INTERCEPTED
  / NO_FIX are genuine apparatus outcomes decided before or without the
  fix and are correctly unavailable; INDETERMINATE_OTHER is the one
  outcome the fix can manufacture.

Raises AssertionError (FALSIFIED) iff the gradient is present.
Imports the real target: bench.reference_runner_v3.compute_sk.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, "bench"))
from reference_runner_v3 import compute_sk  # noqa: E402  (real target)
from fix_efficacy import FIX_INEFFECTIVE, INDETERMINATE  # noqa: E402

SRC = "def f(x):\n    return x + 1\n"
FIX = ("<<<< SEARCH target.py\n    return x + 1\n====\n"
       "    return x + 2\n>>>> REPLACE\n")
BASELINE = {"ruff_violations": 0, "bandit_findings": {"high": 0, "medium": 0}}


def main():
    fail = compute_sk(FIX, SRC, "target.py", baseline=BASELINE,
                      fix_efficacy_outcome=FIX_INEFFECTIVE)
    crash = compute_sk(FIX, SRC, "target.py", baseline=BASELINE,
                       fix_efficacy_outcome=INDETERMINATE)
    print(f"probe runs, still fires : sk={fail.sk}  {fail.tristate}")
    print(f"probe crashed by the fix: sk={crash.sk}  {crash.tristate}")
    assert crash.sk <= fail.sk, (
        f"FALSIFIED: crashing the probe pays +{crash.sk - fail.sk:.4f} sk "
        f"over letting it run ({crash.sk} vs {fail.sk})")
    print("CLEAN: no incentive to break the probe")


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
    # ran the whole measurement. A help flag must ANSWER, never ACT.
    from _cli_help import answer_help  # noqa: E402
    answer_help(__doc__, __file__)
    main()
