#!/usr/bin/env python3
"""The commissioning study's arms, as data, with a caller and a test.

WHY THIS FILE EXISTS, IN THE PROGRAMME'S OWN WORDS.
`CDSFL_Programme_of_Study_2026-09-17.txt` observes that the simulated harness
"accepts no configuration file", that it "builds its own run", and concludes:
"The run this programme describes, 3 arms on the registry engine for 8 rounds,
has no launcher." Its proposed remedy ends: "It needs a caller and a test that
asserts the settings the runner actually received."

This is that caller. The arms are DATA here, so a test can assert on the same
object the launcher uses rather than on a copy of it -- the 2-copies-drift-apart
failure that `execute-do-not-grep` names, and which this project has already
found 4 separate times by running 2 forms against each other.

WHAT IT DOES NOT DO. It does not launch anything by itself and it spends no
money: every seat is a `-SIM` stand-in with `api="sim"`. `--print` emits the
command lines for review; `--run` executes them one at a time through
`run_simulated_experiment_sandboxed.sh`, which is the founder's 2026-09-01
ruling that "a simulation runs in its own sandbox with a copy of the
current/most recent repo to work on, not the live repo itself".

TARGETS. Arms 1, 2, 3 and 5 take the registry engine,
`bench/cdsfl_registry/engine.py`, as the 17 September programme specifies.
Arm 4 takes `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, the candidate that
programme names -- 3,498 bytes with 2 fenced Python listings -- because A19
cannot be commissioned on a Python target: `_gateable_source` returns Python
unchanged, so `sk_score_prose_listings` reports "enabled" while proving nothing.
Verified 2026-09-21 by executing `compute_sk` against that file: 2 listings
extracted, ruff baseline 4, which reproduces the figure A19 records.

THE DOMAIN STAYS `statistics` AND THAT IS DELIBERATE. `software` is the better
description of a Python target, and `--domain` now exists to say so. It is NOT
used here because arm 5 compares this bundle against a pre-window run that used
`statistics`, and changing the briefing would confound the one arm whose whole
purpose is that comparison.

WHAT THIS RUN CANNOT CONCLUDE, STATED UP FRONT. No canary catalogue is
available, so no ground-truth defects are seeded. A CRITICAL_QUIESCENCE
convergence therefore cannot distinguish "the target is genuinely clean" from
"the panel is dead" -- the sandboxed launcher's own note records exactly that
happening on 2026-09-01 with a vacuous curve, zero critical findings across a
whole run. The catalogue is answer-key material and is the founder's in person,
and generating one alone is refused by design, because `Canary.generator` is
load-bearing and `detection_rate` will not report on a single-generator
held-out set.
"""

from __future__ import annotations

import argparse
import dataclasses
import shlex
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SANDBOXED = "bench/tools/run_simulated_experiment_sandboxed.sh"

#: The registry engine, as the 17 September programme names it.
ENGINE = "bench/cdsfl_registry/engine.py"

#: The prose target for arm 4. Named by that programme as the candidate, and
#: confirmed by execution to carry 2 fenced Python listings.
PROSE = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"

#: e2_regression runs this. Chosen to EXERCISE THE TARGET: 40 tests over the
#: registry engine, 0.19 s. The runner's default test command is the immune
#: memory suite, which is tied to `bench/dm/_memory.py` and would have measured
#: regressions in a module these arms never touch.
ENGINE_TESTS = "python3 -m pytest bench/tests/test_policy_engine.py -q"


@dataclasses.dataclass(frozen=True)
class Arm:
    key: str
    name: str
    seats: str
    target: str
    purpose: str
    #: None where the gate is unavailable by construction rather than by choice.
    test_cmd: str | None = ENGINE_TESTS
    rounds: int = 8

    def argv(self) -> list[str]:
        a = ["--target", self.target, "--seats", self.seats,
             "--rounds", str(self.rounds), "--name", self.name]
        if self.test_cmd:
            a += ["--test-cmd", self.test_cmd]
        return a


#: Arm 5 is NOT here. It requires running the harness as it stood at `a2a0197`
#: (2026-09-06, pre-window) against the same target and seed, which is a
#: checkout of a different commit rather than a flag on this one. Listing it
#: with the others would imply this launcher can produce it, and it cannot.
ARMS = [
    Arm("arm1", "commissioning_arm1_panel",
        "CC2,Codex,Gemini,DeepSeek,ChatGPT", ENGINE,
        "the repairs in a panel shape; 5 seats, as the 17 September programme lists them"),
    Arm("arm2", "commissioning_arm2_single",
        "CC2", ENGINE,
        "the repairs in a single-seat shape"),
    Arm("arm3", "commissioning_arm3_contrast",
        "Codex,ChatGPT", ENGINE,
        "seat contrast; WEAK BY CONSTRUCTION in simulation, both seats being the "
        "same stand-in model under different labels, and reported as weak"),
    Arm("arm4", "commissioning_arm4_prose",
        "CC2,Codex,Gemini,DeepSeek,ChatGPT", PROSE,
        "commissions A19; e2_regression is UNAVAILABLE on prose by construction, "
        "so no test command is passed and the gate is excluded rather than faked",
        test_cmd=None),
]


def command(arm: Arm) -> list[str]:
    return ["bash", SANDBOXED, *arm.argv()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print", action="store_true",
                    help="emit the command lines and exit (default)")
    ap.add_argument("--run", action="store_true",
                    help="execute the arms sequentially through the sandboxed launcher")
    ap.add_argument("--only", default=None,
                    help="restrict to one arm key, e.g. arm1")
    args = ap.parse_args()

    arms = [a for a in ARMS if args.only in (None, a.key)]
    if not arms:
        print(f"no arm matches {args.only!r}; keys are "
              + ", ".join(a.key for a in ARMS), file=sys.stderr)
        return 2

    if not args.run:
        for a in arms:
            print(f"# {a.key}: {a.purpose}")
            # shlex.join, NOT " ".join: --test-cmd carries spaces, and an
            # unquoted printed line would split it into 4 arguments if a
            # reader copied it. Execution was always correct (subprocess
            # takes a list); only the printed form was misleading.
            print(shlex.join(command(a)))
            print()
        return 0

    rc_total = 0
    for a in arms:
        print(f"=== {a.key} — {a.purpose}", flush=True)
        rc = subprocess.call(command(a), cwd=REPO)
        print(f"=== {a.key} exit code {rc}", flush=True)
        rc_total = rc_total or rc
    return rc_total


if __name__ == "__main__":
    sys.exit(main())
