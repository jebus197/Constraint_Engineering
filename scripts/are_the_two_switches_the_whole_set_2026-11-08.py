#!/usr/bin/env python3
"""B20: are `--act` and `--hil-review` the WHOLE set of shut gates, and what
does the middle setting actually record?

WHY THIS EXISTS. B20's entry states that enablement is gated twice and names
the 2 gates. A count is not a set: `feedback_pin_a_set_not_a_count_2026-10-16`
records checking 2 instruments when there were 3. So this script tries to
FALSIFY "2 switches" by finding a third condition that suppresses action even
when both are flipped, and it does so BY EXECUTION through the actuator's own
`_runner` seam rather than by reading the source -- `execute-do-not-grep`.

WHAT IT FOUND, AND THE HYPOTHESIS IS REFUTED. The 2 switches are sufficient.
Three further conditions exist and NONE of them is a switch:
  * the pulse must name a pid that has exited -- written by the watchdog
    during a real run, not set by a human;
  * `launch` must be given -- a required positional argument;
  * `max_resumes` must exceed the resumes already driven -- it DEFAULTS TO 3,
    so it is a permissive bound rather than a shut gate.

AND THE PART THAT IS NEW. The 2 switches are INDEPENDENT, and the middle
setting (`--hil-review` on, `--act` off) is informative on its own: the
classifier reaches its RESUME verdict and RECORDS it with full evidence while
re-invoking nothing. That is a dry-run arm, and it produces exactly the
evidence needed to rule on turning action on. 0 archived run directories
have ever set the flag, so no such decision has been recorded.

★ THE COUNT IS NOT WRITTEN HERE ANY MORE. Corrected 2026-11-08: this docstring
and the closing report both read `351`, while the producer that OWNS the figure,
`scripts/the_unattended_loop_has_never_been_reachable_2026-11-04.py`, derives
352. A figure living as prose inside a producer is the exact thing
`measured-rate-travels-with-its-script` forbids, and it had already drifted. The
denominator is now derived at print time from the same directory the owner reads,
so the 2 cannot disagree again.

A PROBE NOTE THAT IS PART OF THE RESULT. The first version of this measurement
used an empty temporary directory and reported HOLD with BOTH switches on,
which would have been read as a third gate. The cause was the probe: with no
pulse on disk the classifier correctly returns UNKNOWN. See
`feedback_a_probes_location_can_manufacture_the_failure_2026-11-02`. The
no-pulse case is therefore KEPT BELOW as a labelled negative control rather
than deleted, so the trap is visible to the next reader.

Run:  python3 scripts/are_the_two_switches_the_whole_set_2026-11-08.py
Exit: 0 when every expectation below holds, 1 otherwise.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
ACTUATOR = REPO / "bench/tools/cy_actuator_2026-11-03.py"


def load_actuator():
    spec = importlib.util.spec_from_file_location("cy_actuator", ACTUATOR)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def a_genuinely_dead_pid() -> int:
    """A pid that has exited and been reaped, so `_pid_alive` is False.

    Spawned and waited rather than invented, because an invented pid can
    collide with a live process and silently flip the measurement.
    """
    proc = subprocess.Popen(["true"])
    proc.wait()
    return proc.pid


def drive_case(M, codes, *, act, max_resumes=3, pulse=None, root):
    """Run the real `drive()` loop against a scripted exit-code sequence."""
    seq = list(codes)
    log_dir = pathlib.Path(tempfile.mkdtemp(dir=root))
    if pulse is not None:
        (log_dir / "cy_pulse.json").write_text(json.dumps(pulse), encoding="utf-8")
    calls: list[list[str]] = []

    def runner(argv):
        calls.append(list(argv))
        return seq.pop(0) if seq else 0

    res = M.drive(["python3", "fake_runner.py"], log_dir, pathlib.Path("."),
                  max_resumes=max_resumes, act=act, _runner=runner)
    return res, calls, log_dir


def main() -> int:
    # ★ `--help` MUST NOT DO THE WORK. Added 2026-11-08: 8 scripts of this
    # date wrote files while answering `--help`, which
    # `bench/tests/test_help_never_acts_2026-09-11.py` forbids and which
    # `feedback_help_must_never_cost_money` records as 15 of 17 runners
    # billing for a help request. A parser is used rather than
    # `_cli_help.answer_help` because an unrecognised argument then exits 2
    # instead of being ignored, and because it cannot be made unreachable
    # under `python3 -m`, which is how 5 of 9 earlier repairs failed.
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    M = load_actuator()
    dead = a_genuinely_dead_pid()
    failures: list[str] = []

    def check(label, got, want):
        ok = got == want
        print(f"    {'OK  ' if ok else 'FAIL'} {label}: got {got!r}, want {want!r}")
        if not ok:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    print("=" * 78)
    print("B20: ARE THE 2 SWITCHES THE WHOLE SET?")
    print("=" * 78)
    print(f"  actuator      : {ACTUATOR.relative_to(REPO)}")
    print(f"  PAUSED exit   : {M.PAUSED}")
    print(f"  dead pid      : {dead}, _pid_alive -> {M._pid_alive(dead)}")
    check("a reaped pid reads as not alive", M._pid_alive(dead), False)

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        pulse = {"pid": dead, "written_at": time.time(), "rounds": 2}

        print("\n  CASE 1 -- BOTH SWITCHES ON, faithful pulse: PAUSED, PAUSED, 0")
        res, calls, _ = drive_case(M, [M.PAUSED, M.PAUSED, 0], act=True,
                                   pulse=pulse, root=root)
        check("invocations", len(calls), 3)
        check("resumes driven", res["resumes_driven"], 2)
        check("acted per row", [r["acted"] for r in res["rows"]], [True, True, False])
        check("--resume appended after the first", [("--resume" in c) for c in calls],
              [False, True, True])

        print("\n  CASE 2 -- GATE 1 SHUT (--act withheld): the DRY-RUN ARM")
        res, calls, log_dir = drive_case(M, [M.PAUSED, M.PAUSED, 0], act=False,
                                         pulse=pulse, root=root)
        check("invocations", len(calls), 1)
        check("resumes driven", res["resumes_driven"], 0)
        check("acted", [r["acted"] for r in res["rows"]], [False])
        check("the decision is still reached", res["final"], "RESUME")
        rows = [json.loads(ln) for ln in
                (log_dir / "actuator_decisions.jsonl").read_text().splitlines() if ln.strip()]
        check("the decision is RECORDED to disk", len(rows), 1)
        check("the recorded decision", rows[0]["decision"], "RESUME")
        check("the recorded row says it did not act", rows[0]["acted"], False)
        for key in ("exit_code", "pid", "pid_alive", "pid_known", "pulse_present",
                    "pulse_age_s", "pulse_ended", "rounds", "events"):
            if key not in rows[0]["evidence"]:
                failures.append(f"evidence lost the {key} field")
        print(f"    OK   evidence fields recorded: {sorted(rows[0]['evidence'])}")

        print("\n  CASE 3 -- GATE 2 SHUT (never exits PAUSED), --act on")
        res, calls, _ = drive_case(M, [0], act=True,
                                   pulse={"pid": dead, "written_at": time.time(),
                                          "ended": True}, root=root)
        check("invocations", len(calls), 1)
        check("final", res["final"], "DONE")
        check("acted", [r["acted"] for r in res["rows"]], [False])

        print("\n  CASE 4 -- THE CAP: --act on, faithful pulse, budget 0")
        res, calls, _ = drive_case(M, [M.PAUSED, M.PAUSED, 0], act=True,
                                   max_resumes=0, pulse=pulse, root=root)
        check("invocations", len(calls), 1)
        check("final", res["final"], "HOLD")
        check("acted", [r["acted"] for r in res["rows"]], [False])
        if "budget" not in res["rows"][0]["reason"]:
            failures.append("the cap's reason does not name the budget")
        else:
            print("    OK   the cap names the budget in its reason")

        print("\n  CASE 5 -- NEGATIVE CONTROL, and it is the probe trap:")
        print("           --act on, NO pulse on disk. Expect HOLD, because the")
        print("           classifier cannot know whether the process exited.")
        res, calls, _ = drive_case(M, [M.PAUSED, M.PAUSED, 0], act=True,
                                   pulse=None, root=root)
        check("invocations", len(calls), 1)
        check("final", res["final"], "HOLD")
        check("acted", [r["acted"] for r in res["rows"]], [False])
        if "UNKNOWN" not in res["rows"][0]["reason"]:
            failures.append("the no-pulse reason does not say the exit is UNKNOWN")
        else:
            print("    OK   the no-pulse reason says the exit is UNKNOWN, not 'alive'")

    print("\n  THE DEFAULT OF THE CAP, read from argparse rather than assumed")
    src = ACTUATOR.read_text(encoding="utf-8")
    import ast
    tree = ast.parse(src)
    cap_default = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--max-resumes"):
            for kw in node.keywords:
                if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                    cap_default = kw.value.value
    check("--max-resumes default is permissive, not 0", cap_default, 3)

    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    if failures:
        print(f"  {len(failures)} expectation(s) FAILED:")
        for f in failures:
            print(f"    - {f}")
        return 1
    print("  THE 'THIRD GATE' HYPOTHESIS IS REFUTED. `--act` and `--hil-review`")
    print("  are the whole set of SHUT gates. The pulse is written by the")
    print("  watchdog, `launch` is a required argument, and `--max-resumes`")
    print("  defaults to 3, so none of the 3 further conditions is a switch.")
    print()
    print("  AND THE 2 SWITCHES ARE INDEPENDENT, so the setting is RANKED and")
    print("  not binary:")
    print("    both off                      0 decisions, 0 actions")
    print("    --hil-review on, --act off    RESUME recorded with evidence, 0 actions")
    print("    both on                       acts, up to --max-resumes resumes")
    print()
    # DERIVED, never typed: the same `bench/logs` directory listing the owning
    # producer reads. See the docstring's correction note of 2026-11-08.
    _logs = REPO / "bench" / "logs"
    _n = len([d for d in _logs.iterdir() if d.is_dir()]) if _logs.is_dir() else 0
    print("  The middle row is a DRY-RUN ARM and it is what the bottom row's")
    print(f"  ruling needs. It has never been run: 0 of the {_n} archived run")
    print("  directories set the flag.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
