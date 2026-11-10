#!/usr/bin/env python3
"""The actuator: drive the RESUME of a run that paused itself for human review.

WHAT IT IS. A thin outer supervisor. It watches a launched run, classifies what
happened when the run stopped, RECORDS that classification with its evidence,
and -- only under `--act` -- re-invokes the same launch command with `--resume`.
It changes 0 lines of the runner.

WHY OUTER AND NOT INSIDE THE RUNNER. Traced before it was written. The simulated
runner calls `R.run_experiment(...)` IN-PROCESS at
`bench/tools/run_simulated_experiment.py:1066`, inside a `try` whose only
companion clause is `finally` -- there is no `except`. So the pause's
`sys.exit(42)` raises `SystemExit(42)`, which is not an `Exception`, propagates
out through `main()`, and becomes the PROCESS exit code, while the `finally`
still harvests the panel worktree first. The pause is therefore observable from
outside with no runner change at all, and anything built inside the runner would
have been a second mechanism for a signal that already crosses the boundary.

ASSUMES (A1-A4). Declared, because a component that does not state what it
relies on cannot be checked against the thing it relies on.
  A1  The run has a log directory; the actuator writes its decisions there.
  A2  The run was launched with `--hil-review`. There are 2 pause sites and
      each sits behind its OWN `if cfg.hil_review`: the per-round gate and the
      phase-boundary gate, which reach `sys.exit(42)` separately. The field
      defaults to False. Without the flag the pause is unreachable and this
      actuator has nothing to drive -- so A2 is a precondition, not a
      preference. EVERY LINE NUMBER FOR THIS LIVES IN `CITATIONS` BELOW AND IS
      CHECKED BY `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py`,
      because the 4 numbers previously written into this paragraph drifted: 2
      of them by 23 and 7 lines, onto a logging call and a phase-name log.
  A3  Exit code 42 means PAUSED FOR REVIEW. This is not a new convention:
      `bench/launch_exp39.py` already reads 42, as the property `hil_paused`,
      and propagates it with `sys.exit(42)`. The earlier wording here named
      `is_hil_paused()`, which exists nowhere in the project outside this
      sentence; the real symbol is `hil_paused`.
  A4  The launch command is supplied verbatim, so a resume re-invokes the SAME
      command with `--resume` appended rather than a reconstruction of it.

GUARANTEES (G1-G5).
  G1  No resume without a recorded decision carrying its evidence. Same rule as
      `TicketStore.close()`, which refuses without a verification.
  G2  Never resumes while the run's own process is still alive.
  G3  Bounded. At most `max_resumes`, so it cannot drive a loop for ever.
  G4  Any state it cannot classify HOLDS, and the record names what was seen.
      This is the load-bearing guarantee: the default on uncertainty is to stop,
      never to act.
  G5  The decision log is append-only JSONL beside the run.

WHAT IT DELIBERATELY DOES NOT DO. It does not review. It decides whether a
paused run may CONTINUE, which is a mechanical question about process state. The
review itself -- whether the run's findings are right -- is the human's, and
`--act` is opt-in precisely so the mechanism is reachable and testable without
the acting being automatic.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

#: THE CONTRACT AS DATA, NOT AS PROSE. The docstring above states it for a
#: reader; this states it for a machine. A declaration that lives only in a
#: docstring is an addition nothing reaches, which `additive-standard`'s
#: symmetric form forbids -- 11 confirmed defects in this project were additions
#: that did nothing. Here the guard ITERATES these keys and fails if any
#: guarantee has no executing test, and `--contract` prints them, so the
#: declaration has 2 callers.
#:
#: This is ONE component carrying an explicit assume/guarantee declaration. It
#: is NOT a project-wide standard and must not be reported as one.
ASSUMES = {
    "A1": "the run has a log directory, where decisions are written",
    "A2": ("the run was launched with --hil-review; both pause sites sit behind "
           "`if cfg.hil_review` (reference_runner_v3.py:21297), each "
           "gate reaching sys.exit(42) separately -- every line number "
           "for this is in CITATIONS and checked -- and the field "
           "defaults to False (:2308), so without the flag the pause is "
           "unreachable"),
    "A3": ("exit code 42 means PAUSED FOR REVIEW; launch_exp39.py:86 already "
           "reads it that way"),
    "A4": "the launch command is supplied verbatim, so a resume re-invokes it",
}

GUARANTEES = {
    "G1": "no resume without a recorded decision carrying its evidence",
    "G2": "never resumes while the run's own process is alive",
    "G3": "bounded: at most max_resumes, so it cannot loop for ever",
    "G4": "any state it cannot classify HOLDS, and the record says what it saw",
    "G5": "the decision log is append-only JSONL beside the run",
}


# EVERY LINE NUMBER THIS DECLARATION RELIES ON, AS DATA RATHER THAN PROSE.
#
# WHY. The 4 line numbers formerly written into A2's prose drifted: `:21274`
# by 23 lines onto a `_log("")` call and `:21368` by 7 onto a phase-name log,
# while `:21298` sat 1 line off on the comment that explains the gate. A2 also
# named `is_hil_paused()`, a symbol that appeared nowhere in the project except
# in that sentence. None of it was checked by anything, in a declaration whose
# entire purpose is to be checkable.
#
# Each entry is (path, line, a substring that line MUST contain). The guard
# `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py` reads this
# dict and fails when a line no longer holds its substring, so drift is caught
# at the commit that causes it rather than by a reader months later.
# ★ ALL 6 A2 CITATIONS MOVED +144 LINES, 2026-11-09, AND THE SHIFT IS THE
# EVIDENCE THAT THE MAPPING IS RIGHT. Work of 2026-11-08 added 2 functions to
# `bench/reference_runner_v3.py` -- `both_gates_agree` for B76 and
# `pre_run_target_description` for B84 -- which pushed everything below them
# down. Every one of the 6 moved by exactly the same 144 lines, and each new
# line holds the substring it is declared with, so this is a uniform
# translation and not 6 separate guesses.
#
# THE 2 `sys.exit(42)` CITATIONS WERE AMBIGUOUS AND WERE RESOLVED BY ORDER,
# not by taking the first match. The guard reported the text at BOTH 21498 and
# 21568; the round block precedes the phase block in the file, so 21498 is
# `A2.exit.round` and 21568 is `A2.exit.phase`. Picking the first for both
# would have left 1 citation pointing at the wrong site while the guard went
# green -- a citation that resolves is not the same as a citation that is
# right.
CITATIONS = {
    "A2.default":      ("bench/reference_runner_v3.py", 2308,
                        "hil_review: bool = False"),
    "A2.gate.round":   ("bench/reference_runner_v3.py", 21589,
                        "if cfg.hil_review and not"),
    "A2.pause.round":  ("bench/reference_runner_v3.py", 21603,
                        "if _hil_verdict.should_pause:"),
    "A2.exit.round":   ("bench/reference_runner_v3.py", 21613,
                        "sys.exit(42)"),
    "A2.gate.phase":   ("bench/reference_runner_v3.py", 21653,
                        "if cfg.hil_review:"),
    "A2.pause.phase":  ("bench/reference_runner_v3.py", 21658,
                        "if not _hil_verdict.should_pause:"),
    "A2.exit.phase":   ("bench/reference_runner_v3.py", 21683,
                        "sys.exit(42)"),
    "A3.property":     ("bench/launch_exp39.py", 85,
                        "def hil_paused"),
    "A3.propagates":   ("bench/launch_exp39.py", 457,
                        "sys.exit(42)"),
}

#: Exit code the runner uses for "paused, checkpoint saved, resume with
#: --resume". Not invented here -- see A3.
PAUSED = 42

#: A pulse older than this means the WATCH died, not that the run ended. Same
#: constant and same reasoning as `hooks/cy_monitor_gate.py:88`: 3x the
#: watchdog's 60 s cadence, so one slow cycle is not a false alarm.
PULSE_STALE_SECONDS = 180


def _pid_alive(pid) -> bool:
    """Unknown or unreadable counts as ALIVE, so G2 fails toward HOLDING."""
    if not pid:
        return True
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:                                        # noqa: BLE001
        return True


def read_pulse(log_dir: pathlib.Path) -> dict:
    """The watchdog's pulse for this run, or {} if there is none.

    Returns {} rather than raising, because a missing pulse is a STATE the
    classifier must decide about (it HOLDS), not an error that should abort.
    """
    p = pathlib.Path(log_dir) / "cy_pulse.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:                                        # noqa: BLE001
        return {}


def classify(exit_code, pulse: dict, now: float | None = None) -> dict:
    """PURE. What happened, and may the run be resumed?

    Returns {"decision", "reason", "evidence"} where decision is one of
    RESUME, HOLD, DONE. Pure so it can be executed directly by a guard against
    every state, rather than inferred from the source text of the loop that
    calls it -- `execute-do-not-grep`.

    THE TABLE IS DELIBERATELY NARROW. RESUME requires BOTH that the run said it
    paused AND that its process is gone. Everything else HOLDS or is DONE, which
    is G4: the default on anything unrecognised is to stop.
    """
    now = time.time() if now is None else now
    pid = pulse.get("pid")
    # KNOWN-ALIVE AND UNKNOWN ARE DIFFERENT FACTS AND MUST NOT SHARE A REASON.
    # `_pid_alive(None)` returns True as a fail-safe so G2 errs toward holding,
    # which is correct -- but reporting that fail-safe as "the process is alive"
    # states something unmeasured. The P-pass of this file found exactly that:
    # with no pulse on disk the decision was right and the recorded reason was
    # false. So the two cases are separated here and reported separately.
    pid_known = pid is not None and pid != 0
    alive = _pid_alive(pid)
    age = now - float(pulse.get("written_at") or 0) if pulse else None
    ev = {"exit_code": exit_code, "pid": pid, "pid_alive": alive,
          "pid_known": pid_known,
          "pulse_present": bool(pulse), "pulse_age_s": None if age is None else round(age, 1),
          "pulse_ended": pulse.get("ended"),
          "rounds": pulse.get("rounds"),
          # The watchdog's event channel, added 2026-11-03. Its 10 event kinds
          # reached stdout only, so a reader had the outcome and none of the
          # reasoning behind it.
          "events": pulse.get("events") or []}

    if exit_code == PAUSED:
        if alive and pid_known:
            return {"decision": "HOLD",
                    "reason": ("the run reported PAUSED but its process is still "
                               "alive, which is a contradiction; nothing is driven "
                               "until it is understood"),
                    "evidence": ev}
        if alive:
            return {"decision": "HOLD",
                    "reason": ("the run reported PAUSED but no pulse names a "
                               "process, so whether it has exited is UNKNOWN "
                               "rather than known; a resume could collide with a "
                               "live run and is not driven on an unknown"),
                    "evidence": ev}
        return {"decision": "RESUME",
                "reason": ("the run saved a checkpoint and paused for review, and "
                           "its process has exited, so a resume cannot collide "
                           "with a live run"),
                "evidence": ev}

    if exit_code == 0:
        if pulse and not pulse.get("ended"):
            return {"decision": "HOLD",
                    "reason": ("the run exited cleanly but its watch never "
                               "recorded an end, so the two disagree about what "
                               "happened"),
                    "evidence": ev}
        return {"decision": "DONE",
                "reason": ("the run completed and its watch agrees" if pulse else
                           "the run completed; NO watch pulse exists, so the "
                           "exit code is the only evidence and nothing "
                           "corroborates it"),
                "evidence": ev}

    return {"decision": "HOLD",
            "reason": (f"the run exited {exit_code}, which is a failure and not a "
                       f"pause; a failure is the human's to read, not the "
                       f"actuator's to drive past"),
            "evidence": ev}


def record(log_dir: pathlib.Path, row: dict) -> pathlib.Path:
    """Append one decision row. G1 and G5.

    The timestamp is taken from the clock at the moment of writing, never typed
    or interpolated -- `feedback_a_linter_cannot_catch_an_invented_time`.
    """
    d = pathlib.Path(log_dir)
    d.mkdir(parents=True, exist_ok=True)
    out = d / "actuator_decisions.jsonl"
    row = dict(row)
    row["recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    row["recorded_at_epoch"] = time.time()
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return out


def drive(launch: list[str], log_dir: pathlib.Path, cwd: pathlib.Path,
          max_resumes: int = 3, act: bool = False,
          _runner=None) -> dict:
    """Launch, classify, record, and under `act` resume -- at most max_resumes.

    `_runner` is a seam so a guard can EXECUTE this loop against a scripted
    sequence of exit codes without launching anything. The default is the real
    subprocess call.
    """
    run = _runner if _runner is not None else (
        lambda argv: subprocess.run(argv, cwd=str(cwd)).returncode)
    rows, resumes = [], 0
    argv = list(launch)
    while True:
        code = run(argv)
        row = classify(code, read_pulse(log_dir))
        row["launch"] = list(argv)
        row["resume_index"] = resumes
        row["acted"] = False
        if row["decision"] == "RESUME" and resumes >= max_resumes:
            row["decision"] = "HOLD"
            row["reason"] = (f"the run is resumable but {resumes} resume(s) have "
                             f"already been driven, which is the budget "
                             f"({max_resumes}); stopping rather than looping")
        if row["decision"] == "RESUME" and act:
            row["acted"] = True
        record(log_dir, row)
        rows.append(row)
        if row["decision"] != "RESUME" or not act:
            break
        resumes += 1
        argv = list(launch) + (["--resume"] if "--resume" not in launch else [])
    return {"rows": rows, "resumes_driven": resumes,
            "final": rows[-1]["decision"] if rows else "NONE"}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Drive the resume of a run that paused itself for human "
                     "review. Classifies and records by default; --act is "
                     "required before it re-invokes anything."))
    ap.add_argument("--log-dir", default=None,
                    help="the run's log directory; decisions are written here")
    ap.add_argument("--cwd", default=".", help="working directory for the launch")
    ap.add_argument("--max-resumes", type=int, default=3)
    ap.add_argument("--act", action="store_true",
                    help="actually re-invoke with --resume on a RESUME decision")
    ap.add_argument("--classify-only", action="store_true",
                    help="classify a given exit code against the pulse on disk "
                         "and record it, launching nothing")
    ap.add_argument("--exit-code", type=int,
                    help="with --classify-only: the exit code to classify")
    ap.add_argument("--contract", action="store_true",
                    help="print what this actuator assumes and guarantees, then "
                         "exit; the same dicts the guard iterates")
    ap.add_argument("launch", nargs=argparse.REMAINDER,
                    help="the launch command, verbatim (A4)")
    args = ap.parse_args()

    if args.contract:
        print("ASSUMES")
        for k in sorted(ASSUMES):
            print(f"  {k}  {ASSUMES[k]}")
        print("\nGUARANTEES")
        for k in sorted(GUARANTEES):
            print(f"  {k}  {GUARANTEES[k]}")
        return 0

    if args.log_dir is None:
        print("--log-dir is required (A1)", file=sys.stderr)
        return 2
    log_dir = pathlib.Path(args.log_dir).expanduser()

    if args.classify_only:
        if args.exit_code is None:
            print("--classify-only needs --exit-code", file=sys.stderr)
            return 2
        row = classify(args.exit_code, read_pulse(log_dir))
        row["launch"] = []
        row["resume_index"] = 0
        row["acted"] = False
        out = record(log_dir, row)
        print(f"{row['decision']}: {row['reason']}")
        print(f"  recorded -> {out}")
        return 0

    launch = [a for a in (args.launch or []) if a != "--"]
    if not launch:
        print("no launch command given; pass it after the options (A4)",
              file=sys.stderr)
        return 2

    res = drive(launch, log_dir, pathlib.Path(args.cwd).expanduser(),
                max_resumes=args.max_resumes, act=args.act)
    print("=" * 76)
    print("ACTUATOR")
    print("=" * 76)
    for r in res["rows"]:
        print(f"  [{r['decision']}] resume {r['resume_index']}, "
              f"acted={r['acted']}")
        print(f"      {r['reason']}")
    print(f"\n  resumes driven : {res['resumes_driven']}")
    print(f"  final          : {res['final']}")
    print(f"  acting enabled : {args.act}")
    if not args.act:
        print("  (--act was NOT given, so nothing was re-invoked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
