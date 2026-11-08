#!/usr/bin/env python3
"""The invocation that is BOTH simulated and resumable, which B20 lacked.

B20'S MEASURED BLOCKER, found 2026-11-04 and built 2026-11-08. The bound
orchestrator's actuator resumes by re-invoking its launch command with
`--resume` appended -- `bench/tools/cy_actuator_2026-11-03.py:drive()` is itself
the bounded unattended loop: it runs, classifies against the pulse, records with
evidence, resumes under `--act`, degrades to HOLD at `max_resumes` and breaks on
any non-RESUME decision. So the launch command MUST accept `--resume`.

`bench/reference_runner_v3.py` declares it on its `run` subcommand at :22497 and
`bench/launch_exp39.py` forwards it, but `bench/tools/run_simulated_experiment.py`
declared it 0 times and COULD NOT: the protection that stops a simulated run
billing anything was a `getaddrinfo` patch installed inside that file's `main()`,
and an in-process network block cannot survive the subprocess boundary a resume
requires. So NO INVOCATION WAS BOTH SIMULATED AND RESUMABLE -- the resumable path
dispatched for real and cost money, which he has refused, and the free path could
not be resumed. That is why 0 of 352 archived run directories declare the arm,
and it was a missing seam rather than his deferral or neglect.

WHAT THIS FILE IS. The wrapper the actuator drives. It installs the tripwire
through `run_simulated_experiment.install_paid_tripwire` -- the SAME installer,
lifted to module level in the same commit, because a billing guard that exists
twice can be repaired once -- then sets `sys.argv` and calls the runner's own
`main()` IN-PROCESS. `main()` takes no arguments and lets argparse read
`sys.argv`, which is what makes the in-process call possible, and the tripwire is
installed in THIS process so it holds for everything `main()` reaches.

WHAT IT DELIBERATELY DOES NOT DO. It does not re-implement the loop. `drive()`
already is that loop, bounded and recording; a claim of mine on 2026-11-04 that
the chaining was the missing component was wrong, and checking before building
is what `feedback_three_artefacts_before_calling_it_untracked_2026-10-17` exists
for. It also does not pass `--act`: enabling the actuator is his ruling, and this
wrapper only makes the pause REACHABLE.

EXIT 42 IS PROPAGATED, NOT TREATED AS A FAILURE. That code is the HIL review
pause the actuator waits for -- `launch_exp39.py:87` reads
`return self.exit_code == 42` -- so swallowing it or remapping it would make the
actuator blind to the very state it exists to act on.

Exit: whatever the runner returns, with 42 passed through unchanged.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (REPO / "bench", HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

#: The pause the actuator classifies on. Named rather than written as a bare 42.
HIL_PAUSE_EXIT = 42


def build_argv(config: str, *, resume: bool = False,
               hil_review: bool = True) -> list:
    """The `sys.argv` the runner's own argparse will read.

    Separated from `main` so a test can assert the shape WITHOUT launching a
    run -- `execute-do-not-grep` applied to the thing most expensive to execute.
    `--hil-review` is what CREATES the pause the actuator waits for, so a
    wrapper that omitted it would be resumable and never have anything to
    resume from.
    """
    argv = ["reference_runner_v3", "run", "--config", str(config)]
    if hil_review:
        argv.append("--hil-review")
    if resume:
        argv.append("--resume")
    return argv


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True,
                    help="the run config the runner's `run` subcommand takes")
    ap.add_argument("--resume", action="store_true",
                    help="what the actuator appends when it drives a resume")
    ap.add_argument("--no-hil-review", action="store_true",
                    help="omit the pause; the actuator then has nothing to act on")
    a = ap.parse_args(argv)

    import run_simulated_experiment as RSE                     # noqa: PLC0415
    original = RSE.install_paid_tripwire()
    try:
        import reference_runner_v3 as R                        # noqa: PLC0415
        saved = sys.argv[:]
        sys.argv = build_argv(a.config, resume=a.resume,
                              hil_review=not a.no_hil_review)
        print(f"=== SIMULATED AND RESUMABLE === argv: {' '.join(sys.argv[1:])}",
              flush=True)
        try:
            rc = R.main()
        except SystemExit as exc:
            # `main()` may return OR raise; 42 must survive both paths.
            rc = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
        finally:
            sys.argv = saved
        rc = 0 if rc is None else int(rc)
        if rc == HIL_PAUSE_EXIT:
            print(f"    paused for review, exit {HIL_PAUSE_EXIT} propagated",
                  flush=True)
        return rc
    finally:
        import socket as _sock                                 # noqa: PLC0415
        _sock.getaddrinfo = original


if __name__ == "__main__":
    raise SystemExit(main())
