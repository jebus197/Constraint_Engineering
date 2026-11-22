#!/usr/bin/env python3
"""Stop hook: THE SESSION MAY NOT GO IDLE WHILE AN EXPERIMENT IS RUNNING.

HIS INSTRUCTION, 2026-11-02: *"First fix cy so it can't fail again."* And,
the turn before: *"under full cy protocol, it should not be possible for you to
drop monitoring."*

HE IS RIGHT, AND THE REASON IT WAS POSSIBLE IS THAT `cy` NAMES A RATE, NOT A
DEADLINE. The standing directive of 2026-05-18 says to monitor a running
experiment "~every 60 s". A rate is satisfiable at the median with an unbounded
worst case, and that is exactly what happened on 2026-11-02: inter-check
intervals had a median of 54.3 s and a p90 of 465 s, 48 of 72 inside 90 s
(0.666667, Wilson 95% [0.551796, 0.764654]) -- and then 5 h 07 min of nothing.
Nothing was ever violated, because nothing was ever a deadline.

WHAT ALREADY WORKED, SO THIS IS NOT A SECOND DETECTOR. `scripts/cy_watchdog_2026-10-02.py`
is spawned by the runner itself (`bench/tools/run_simulated_experiment.py:569`),
so detection arms by construction. On 2026-11-02 it detected the run's end 49
seconds after it happened and recorded `OUTCOME CLEAN` with the convergence
reason. It wrote that to `cy_watchdog.log`, which nothing was reading. DETECTION
WAS NEVER THE FAILURE; DELIVERY WAS.

SO THIS HOOK ADDS THE ONE THING MISSING: a refusal. While a watched run is live
it blocks the stop, so the session cannot be elsewhere when the run ends. The
notification channel then becomes an EFFICIENCY (so the wait is one tool call
instead of many) rather than the safety mechanism -- which matters, because the
channel is the part that kept failing. `tail -f | grep` under a background shell
delivered 0 notifications in 6 h 01 min, because Bash background notifies on
EXIT and `tail -f` never exits; and a single `ScheduleWakeup` must be re-armed
every turn, which is the same single point of failure that broke.

IT IS DELIBERATELY NOT CLEVER ABOUT WHETHER A NOTIFIER IS ARMED. It cannot see
the session's background shells or wake-ups, so any such test would reduce to
"did the assistant SAY it armed one", and a gate that tests an assertion tests
nothing. It tests a FACT instead: is a run alive.

MUST BE FAST. The sibling Stop hook `work_not_narrate.py` decided correctly for
weeks and was KILLED by the 15 s hook timeout 153 times in 360 invocations
(0.425000, Wilson 95% [0.374991, 0.476593]) because it read a 653 MiB transcript
three times. This hook reads a handful of small JSON files and never touches the
transcript.

PARKING. `~/.claude/hooks/.cy_monitor_gate_PARKED` disables it the moment the
file exists, checked per invocation -- because Claude Code reads hook
configuration once at session start, so renaming a settings key does NOT take
effect until the next session. The founder was told a hook was parked once when
it was not.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


def logs_dir() -> pathlib.Path:
    """The directory of run logs, overridable so this hook can be TESTED.

    `execute-do-not-grep` (2026-09-04): a test asserting on a hook's SOURCE TEXT
    establishes only that the file describes itself consistently. A hard-coded
    path would leave no way to EXECUTE this gate against a planted pulse, so the
    only available guard would be exactly that useless kind. The default is
    unchanged; the override is read only when set and non-empty. Same device as
    `study_pulse.py`'s `CDSFL_STUDY_REGISTER`, for the same reason.
    """
    o = os.environ.get("CDSFL_CY_LOGS", "").strip()
    return pathlib.Path(o) if o else REPO / "bench" / "logs"
def state_path() -> pathlib.Path:
    o = os.environ.get("CDSFL_CY_STATE", "").strip()
    return pathlib.Path(o) if o else (
        pathlib.Path.home() / ".claude" / "hooks" / ".cy_monitor_gate_state.json")
PARKED = pathlib.Path.home() / ".claude" / "hooks" / ".cy_monitor_gate_PARKED"


def parked_path() -> pathlib.Path:
    o = os.environ.get("CDSFL_CY_PARKED", "").strip()
    return pathlib.Path(o) if o else PARKED

#: A pulse older than this means the WATCHDOG died, not that the run ended.
#: 3x the watchdog's 60 s interval, so one slow cycle is not a false alarm --
#: `feedback_a_guard_can_accuse_correct_code_2026-10-28`, 9 of 36 failures in the
#: 2026-10-28 baseline were guards accusing correct code.
PULSE_STALE_SECONDS = 180

#: Bounded so a finished session cannot be trapped. The watchdog gives up at
#: 24 h and a Monitor window is 30 min, so 60 refusals covers a maximal run with
#: headroom. The founder is not always at the keyboard to break a loop.
MAX_REFUSALS = 60

#: Runs older than this are not candidates whatever their pulse says, so an
#: abandoned pulse file from a crashed machine cannot refuse stops for ever.
MAX_PULSE_AGE_HOURS = 36


def parked() -> bool:
    try:
        return parked_path().exists()
    except Exception:                                        # noqa: BLE001
        return False                 # fails toward firing


def pid_alive(pid) -> bool:
    """Unknown or unreadable counts as ALIVE. See the watchdog's own note."""
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


def live_runs() -> tuple[list[dict], list[dict]]:
    """(runs live and watched, runs live whose WATCH has died).

    Both are reasons to refuse and they are DIFFERENT reasons, so they are
    returned separately rather than summed -- a stale pulse means the watchdog
    is gone and the run is unobserved, which is worse than a healthy watch and
    needs different words.
    """
    live, unwatched = [], []
    now = time.time()
    try:
        pulses = sorted(logs_dir().glob("*/cy_pulse.json"))
    except Exception:                                        # noqa: BLE001
        return live, unwatched
    for p in pulses:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:                                    # noqa: BLE001
            continue
        age = now - float(d.get("written_at") or 0)
        if age > MAX_PULSE_AGE_HOURS * 3600:
            continue                 # long abandoned; not a live run
        if d.get("ended"):
            continue                 # the watch said so itself
        if not pid_alive(d.get("pid")):
            continue                 # the run's process is gone
        row = {"dir": p.parent.name, "pulse": str(p), "age": age,
               "rounds": d.get("rounds"), "pid": d.get("pid"),
               "log": d.get("log") or ""}
        (unwatched if age > PULSE_STALE_SECONDS else live).append(row)
    return live, unwatched


#: ★ SHELLS ARE EXCLUDED FROM A `pgrep -f` MATCH, 2026-11-08 on his ruling
#: ("Repair the gate."). `-f` matches the WHOLE COMMAND LINE, so a process whose
#: ARGUMENTS merely name the runner was reported as a live run. Observed twice
#: with 2 different pids: 2026-11-04T05:40 named pid 21974, which was the
#: `git commit` shell itself, carrying a commit message describing this very
#: blocker -- writing about the runner was indistinguishable from running it --
#: and the next commit at 05:54:24 named pid 28697, `comm` `/bin/zsh`, whose
#: command line named the runner twice.
#:
#: WHAT IS REMOVED IS CATEGORICALLY IMPOSSIBLE, NOT MERELY DOUBTFUL, so the
#: author's intent above is kept intact: a shell cannot execute a `.py`
#: in-process, and a shell that SPAWNED a runner has a child that matches on its
#: own with a non-shell `comm`. REQUIRING PYTHON WOULD UNDER-REFUSE for a runner
#: started by any other route, which is the failure this gate exists to prevent,
#: so the test is on the shell and not on the interpreter. A pid whose `comm`
#: cannot be read is KEPT, for the same reason.
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "csh", "tcsh", "fish"})


def _shell_name(comm: str) -> str:
    """The bare program name from a `ps -o comm=` value.

    ★ THE BASENAME IS LOAD-BEARING, measured on this machine 2026-11-08:
    `ps -p <pid> -o comm=` returns FULL PATHS -- `/bin/sh`, `/bin/zsh`, and for
    python `/Library/Frameworks/Python.framework/.../MacOS/Python`. Comparing
    the raw string against a set of bare shell names would match NOTHING and
    the exclusion would ship inert, which is the addition-nothing-reaches half
    of `additive-standard`. A login shell reports `-zsh`, so the leading dash
    is stripped too.
    """
    return pathlib.PurePosixPath(comm.strip()).name.lstrip("-")


def _is_shell(pid: str) -> bool:
    """True only when `ps` POSITIVELY reports this pid as a shell."""
    try:
        out = subprocess.run(["ps", "-p", str(pid), "-o", "comm="],
                             capture_output=True, text=True, timeout=4)
    except Exception:                                        # noqa: BLE001
        return False                 # unreadable -> KEEP, fail toward refusing
    if out.returncode != 0:
        return False                 # gone or denied -> KEEP
    return _shell_name(out.stdout or "") in _SHELLS


#: ★ ENTRY B180, HIS RULING 2026-11-21: widen it to see a full-suite run.
#:
#: WHAT IT COULD NOT SEE. This gate enforces his standing directive of
#: 2026-05-18 -- a long-running process must have a terminal showing its full
#: current output -- and it watched for exactly 1 string,
#: `run_simulated_experiment.py`. So it was INERT through both 3-hour
#: measurements of 2026-11-13, which are precisely the kind of run the
#: directive is about. A full suite is a long-running process by any reading;
#: it simply was not a simulated experiment.
#:
#: WHY A SUITE RUN BELONGS HERE AND A 2-SECOND GUARD RUN DOES NOT: the cost is
#: the point. `pytest.*bench/tests` matches a board or a suite sweep, which is
#: where the 31-minute and 3-hour waits live. The flags-between form is used
#: deliberately -- `pytest bench/tests` requires those words ADJACENT and a
#: real invocation reads `pytest -q -p no:cacheprovider bench/tests/...`, which
#: is the same adjacency defect found in `scripts/blocker_triage.py` on
#: 2026-11-21 under B205.
#:
#: AND THE ANCESTRY EXCLUSION IS NOT OPTIONAL HERE. Widening to a pytest
#: pattern makes this gate see the suite that TESTS it, so a run that is my own
#: ancestor is excluded: it is the process EXERCISING me, not one I would
#: disturb. Established by execution in blocker_triage before being copied
#: here, where a sibling pytest was still detected and the harness was not.
_RUNNER_PATTERNS = ("run_simulated_experiment.py", "pytest.*bench/tests")


def _own_process_chain() -> set:
    """This process and every ancestor, as strings. Entry B180.

    FAIL-SAFE TOWARD DETECTING A RUN: any failure returns just this pid, so a
    fault can only make the gate MORE cautious. That direction is deliberate --
    this function's whole purpose is to stop the gate refusing against its own
    harness, and the harm of refusing too often is a prod, while the harm of
    refusing too rarely is an unobserved 3-hour run.
    """
    chain = {str(os.getpid())}
    try:
        pid = os.getpid()
        for _ in range(16):                 # bounded: no cycle can trap this
            out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=4)
            parent = (out.stdout or "").strip()
            if not parent or not parent.isdigit() or int(parent) <= 1:
                break
            chain.add(parent)
            pid = int(parent)
    except Exception:                                        # noqa: BLE001
        pass
    return chain


def runner_processes() -> list[str]:
    """Live runner processes, for runs started BEFORE the pulse file existed.

    Without this the gate would be vacuous on exactly the run that motivated it,
    since that run has no pulse. ANY match counts as live: over-refusing is
    recoverable, under-refusing is the defect being closed -- EXCEPT a shell,
    for the reason recorded above this function.
    """
    if os.environ.get("CDSFL_CY_NO_PGREP", "").strip():
        return []            # test seam: isolate the pulse path from the machine
    try:
        pids: list[str] = []
        for _pat in _RUNNER_PATTERNS:
            out = subprocess.run(["pgrep", "-f", _pat],
                                 capture_output=True, text=True, timeout=4)
            pids += [x for x in (out.stdout or "").split() if x.strip()]
        mine = _own_process_chain()
        return [p for p in dict.fromkeys(pids)
                if p not in mine and not _is_shell(p)]
    except Exception:                                        # noqa: BLE001
        return []


def spend(key: str) -> int:
    if not key:
        return MAX_REFUSALS + 1
    try:
        sp = state_path()
        st = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    except Exception:                                        # noqa: BLE001
        st = {}
    if st.get("key") != key:
        st = {"key": key, "n": 0}
    st["n"] = int(st.get("n", 0)) + 1
    try:
        state_path().write_text(json.dumps(st), encoding="utf-8")
    except Exception:                                        # noqa: BLE001
        return MAX_REFUSALS + 1      # cannot count -> allow the stop
    return st["n"]


def message(live: list[dict], unwatched: list[dict], pids: list[str]) -> str:
    out = ["A RUN IS STILL LIVE. `cy` is a standing directive and this stop is refused."]
    for r in unwatched:
        out.append(
            f"  WATCH DEAD: {r['dir']} — its pulse is {int(r['age'])} s old "
            f"(stale past {PULSE_STALE_SECONDS} s) but pid {r['pid']} is ALIVE. "
            f"The run is UNOBSERVED. Re-arm the watchdog on it now:\n"
            f"    python3 scripts/cy_watchdog_2026-10-02.py --log {r['log']} "
            f"--outcome-dir bench/logs/{r['dir']}")
    for r in live:
        out.append(
            f"  LIVE: {r['dir']} — pid {r['pid']}, {r['rounds']} round(s) landed, "
            f"pulse {int(r['age'])} s old. The watch is healthy.")
    if not live and not unwatched and pids:
        out.append(
            f"  LIVE: {len(pids)} runner process(es) {', '.join(pids[:4])} with NO "
            f"pulse file — a run started before the pulse existed, so nothing "
            f"machine-readable reports its state.")
    #: ★ THE ADVICE FOLLOWS THE RUN IT FOUND, 2026-11-22. Entry B180 widened
    #: detection to a full-suite run, and the first thing that widening did was
    #: refuse a stop over a `pytest` run and a panel dispatch -- NEITHER of
    #: which writes a `cy_watchdog.log`, because only
    #: `bench/tools/run_simulated_experiment.py` spawns the watchdog. So the
    #: refusal was right and its remedy was unfollowable, which is a guard
    #: telling the reader to do something impossible and is how a correct gate
    #: teaches people to ignore it.
    #:
    #: THE DISCRIMINATOR IS THE ARTEFACT, not the kind of run: if a watchdog log
    #: exists, name it, because it keeps the 60 s cadence the directive asks
    #: for. If none does, say so and point at what the run DOES produce. Both
    #: branches keep the `tail -f` warning, because that failure mode is about
    #: the DELIVERY channel and is identical either way.
    #: `logs_dir()` and not a constant: it is overridable so this hook can be
    #: TESTED against a scratch directory, and a hard-coded path here would
    #: silently read the real tree during a test.
    #: ★ A LIVE WATCHDOG, NOT ANY WATCHDOG, and the first version of this got it
    #: wrong. Globbing `*/cy_watchdog.log` matched 12 HISTORICAL logs from past
    #: runs, so the watchdog branch was taken every time and the advice stayed
    #: unfollowable for precisely the case it was written for -- `a mechanism
    #: can be inert at its default`, caught by asking which branch actually
    #: fires rather than by assuming the one intended did.
    #:
    #: FRESHNESS IS THE TEST because the watchdog writes on a ~60 s cadence by
    #: construction, so a log belonging to a live run cannot be minutes stale.
    #: The window is generous against a slow machine and still excludes every
    #: finished run.
    _ld = logs_dir()
    _fresh = 300.0                      # seconds; 5x the watchdog's own cadence
    _wd = []
    if _ld.is_dir():
        try:
            _now = time.time()

            #: ★ AGE COMES FROM THE PULSE'S OWN `written_at`, NOT FROM A FILE
            #: MTIME, AND THE 2 ARE NOT THE SAME QUESTION. The status line above
            #: already judges liveness by `written_at`; this branch judged it by
            #: the WATCHDOG LOG's mtime, so the gate's advice and its own status
            #: line could disagree about whether a watch was alive.
            #:
            #: WHY THE LOG'S MTIME IS THE WRONG CLOCK, MEASURED. The watchdog
            #: writes its PULSE every ~60 s by construction but writes its LOG
            #: only on an event, so between events the log goes quiet while the
            #: run is perfectly healthy. `scripts/the_gate_decides_on_the_pulse_2026-11-22.py`
            #: puts the share of a heartbeat cycle in which a HEALTHY watchdog
            #: reads as ABSENT at 5/6 = 0.833333, on 2 agreeing routes (sympy and
            #: fractions). So the old predicate gave artefact advice to 5 of 6
            #: live runs and named the cause 'no cy_watchdog.log exists'.
            #:
            #: THE FALLBACK IS DELIBERATE: a pulse written by an older watchdog
            #: carries no `written_at`, and mtime is then the only clock there
            #: is. Falling back is weaker than refusing, and the alternative --
            #: treating a field-less pulse as dead -- would silence the advice
            #: for exactly the runs least likely to be instrumented.
            def _pulse_age(_p):
                try:
                    _w = json.loads(_p.read_text()).get("written_at")
                    if isinstance(_w, (int, float)):
                        return _now - float(_w)
                except Exception:                            # noqa: BLE001
                    pass
                return _now - _p.stat().st_mtime

            _wd = sorted(p.parent / "cy_watchdog.log"
                         for p in _ld.glob("*/cy_pulse.json")
                         if _pulse_age(p) <= _fresh
                         and (p.parent / "cy_watchdog.log").is_file())
        except Exception:                                    # noqa: BLE001
            _wd = []                    # cannot tell -> give the artefact advice
    if _wd:
        _how = ("    Monitor on the run's cy_watchdog.log, matching "
                "'OUTCOME|CLOSED|TROUBLE|PROCESS GONE|HEARTBEAT'\n"
                "The watchdog keeps the ~60 s cadence; the Monitor delivers it.")
    else:
        _how = ("    Monitor on the artefact THIS run writes — no "
                "cy_watchdog.log exists, so there is no watchdog to tail.\n"
                "    A suite or board run: its output file, or `pgrep` on the "
                "invocation, emitting a line when it exits.\n"
                "    A panel round: its log directory, emitting a line as each "
                "seat's json appears.\n"
                "Emit on EVERY terminal state, not only success: a filter that "
                "matches the happy path alone is silent through a crash, and "
                "silence is indistinguishable from still running.")
    out.append(
        "\nDO NOT go idle. Arm a BOUNDED wait that wakes on the run's own "
        "events, in ONE call, rather than polling by hand:\n"
        + _how + "\nA `tail -f | grep` under a background shell delivers "
        "NOTHING, because Bash background notifies on exit and `tail -f` never "
        "exits — that is the exact failure of 2026-11-02, 0 notifications in "
        "6 h 01 min.")
    return "\n".join(out)


def main() -> int:
    if parked():
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:                                        # noqa: BLE001
        return 0                     # never break the session on a bad payload
    live, unwatched = live_runs()
    pids = runner_processes() if not (live or unwatched) else []
    if not (live or unwatched or pids):
        return 0                     # nothing running: silent, as it should be
    key = str(payload.get("session_id") or "") + "|" + \
        str(sorted(r["dir"] for r in live + unwatched) or pids)
    used = spend(key)
    if used > MAX_REFUSALS:
        print(f"cy_monitor_gate: {used - 1} refusals already for this run, which "
              f"is the budget ({MAX_REFUSALS}). Allowing the stop so a session "
              f"cannot be trapped. THE RUN MAY STILL BE LIVE — check it.",
              file=sys.stderr)
        return 0
    print(f"{message(live, unwatched, pids)}\n\n"
          f"(cy refusal {used} of {MAX_REFUSALS} for this run)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                 # noqa: BLE001
        # A GUARD THAT CRASHES MUST NOT BREAK THE SESSION, and it must not be
        # silent either -- `feedback_a_swallowed_exception_is_not_a_record`.
        print(f"cy_monitor_gate: internal error, allowing the stop: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(0)
