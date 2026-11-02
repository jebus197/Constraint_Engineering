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


def runner_processes() -> list[str]:
    """Live runner processes, for runs started BEFORE the pulse file existed.

    Without this the gate would be vacuous on exactly the run that motivated it,
    since that run has no pulse. ANY match counts as live: over-refusing is
    recoverable, under-refusing is the defect being closed.
    """
    if os.environ.get("CDSFL_CY_NO_PGREP", "").strip():
        return []            # test seam: isolate the pulse path from the machine
    try:
        out = subprocess.run(
            ["pgrep", "-f", "run_simulated_experiment.py"],
            capture_output=True, text=True, timeout=4)
        return [x for x in (out.stdout or "").split() if x.strip()]
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
    out.append(
        "\nDO NOT go idle. Arm a BOUNDED wait that wakes on the watchdog's own "
        "events, in ONE call, rather than polling by hand:\n"
        "    Monitor on the run's cy_watchdog.log, matching "
        "'OUTCOME|CLOSED|TROUBLE|PROCESS GONE|HEARTBEAT'\n"
        "The watchdog keeps the ~60 s cadence; the Monitor delivers it. A "
        "`tail -f | grep` under a background shell delivers NOTHING, because "
        "Bash background notifies on exit and `tail -f` never exits — that is "
        "the exact failure of 2026-11-02, 0 notifications in 6 h 01 min.")
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
