#!/usr/bin/env python3
"""THE MECHANICAL `cy` TRIGGER: poll a run every 60 s and SPEAK only when it matters.

WHY THIS EXISTS, and it is the founder's own instruction of 2026-10-02: *"you may
have to create a mechanical trigger for cy to wake you up so this cannot happen
again."* What happened was that on the night of 2026-09-29 into 2026-09-30 a
detached run proceeded for hours while nothing watched it, and the assistant
explained this by saying its monitors cap at 30 minutes.

THAT EXPLANATION WAS HALF TRUE AND WHOLLY MISLEADING. The Monitor tool does cap
one arming at 1,800,000 ms. It also notifies at expiry so it can be re-armed,
and that notification is itself a wake-up, so the cap bounds one arming and not
the watch. The assistant had the mechanism and did not use it. Worse, a 60-second
cadence was never the model's job to do by hand: 9 hours at 60 s is 540 checks,
and a model polling 540 times is both unaffordable and exactly the kind of
"addition nothing reaches" this project keeps finding.

SO THE WORK IS SPLIT, which is what makes the cadence real:

  * MECHANICAL, here, every `--interval` seconds, costing nothing: is the process
    alive, has the log advanced, has a round landed, did an error line appear.
  * ESCALATION, to the model, only on an event worth waking for. Each line this
    script prints to stdout is one such event. Armed under the Monitor tool, each
    line becomes a notification; re-arm on expiry and the watch is unbounded.
  * A SECOND, INDEPENDENT PATH, because the failure being prevented is precisely
    a watcher that went quiet: a cron heartbeat that fires whether or not this
    script or that Monitor is alive. Two paths that fail independently.

SILENCE IS NOT SUCCESS, and that is the whole design point. The 9-hour hole was
not an absent alarm, it was an alarm with nothing to say. A watchdog that greps
only for a success marker stays mute through a crashloop, a hang, or a kill, and
mute is indistinguishable from healthy. So this script treats ABSENCE as a
reportable event: `--stall-seconds` without the log advancing is an event, and
the death of the process is an event, and neither depends on the run choosing to
write anything.

IT EXITS WHEN THE RUN EXITS. `bench/tail_until_done.sh` already closes with the
run for the founder's terminal; this does the same for the machine channel, so a
quiet watchdog can be told from a finished one by its exit code alone.

Run:
  python3 scripts/cy_watchdog_2026-10-02.py --log bench/logs/run.log --pid-file bench/logs/run.pid
  python3 scripts/cy_watchdog_2026-10-02.py --log X --once      # single probe, for tests
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import signal
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]

# Lines worth waking a model for. Deliberately WIDE: a missed crashloop costs
# hours, a spurious wake costs one notification.
TROUBLE = re.compile(
    r"Traceback|Exception|FATAL|CRITICAL|Segmentation|MemoryError|"
    r"\bKilled\b|OOM|RecursionError|PermissionError|"
    r"HALTED|ALARM|REFUSED|UNRECORDED_STOP|"
    r"rate.?limit|quota|401|403|429|5\d\d Server|"
    r"could not|cannot |failed|FAILED|Error:",
    re.I)
# Progress markers: worth one line each, because a run that is moving is news
# after a stall and the absence of them is the stall signal.
PROGRESS = re.compile(r"ROUND\s+(\d+)|round_(\d+)\.json|CONVERGED|convergence|"
                      r"writing report|completion_signal", re.I)


def _alive(pid: int | None) -> bool:
    if not pid:
        return True            # no pid supplied: liveness is judged by the log
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True            # exists, owned by someone else
    return True


def _read_pid(pid_file: pathlib.Path | None) -> int | None:
    if not pid_file or not pid_file.is_file():
        return None
    try:
        return int(pid_file.read_text(encoding="utf-8").strip().split()[0])
    except (ValueError, IndexError, OSError):
        return None


def _round_count(log: pathlib.Path) -> int:
    """Rounds landed, read from the run's own artefacts, not from its prose."""
    d = log.parent
    n = len(list(d.glob("round_*.json")))
    for state in (d / "runner_state.json",):
        if state.is_file():
            try:
                s = json.loads(state.read_text(encoding="utf-8"))
                n = max(n, len(s.get("gamma_history") or []))
            except (ValueError, OSError):
                pass
    return n


def say(kind: str, msg: str) -> None:
    """One event, one stdout line, flushed. The Monitor tool turns it into a wake."""
    print(f"[cy {time.strftime('%H:%M:%S')}] {kind}: {msg}", flush=True)


def probe(log: pathlib.Path, pid: int | None, offset: int, last_size: int,
          last_change: float, rounds: int, stall_s: int) -> tuple:
    """One mechanical check. Returns new state and emits events for what changed."""
    now = time.time()
    exists = log.is_file()
    size = log.stat().st_size if exists else 0

    if exists and size > offset:
        try:
            with log.open("r", errors="ignore") as fh:
                fh.seek(offset)
                chunk = fh.read()
                offset = fh.tell()
        except OSError as exc:
            say("WATCHDOG", f"cannot read the log ({exc}); treating as stalled")
            chunk = ""
        for line in chunk.splitlines():
            if TROUBLE.search(line):
                say("TROUBLE", line.strip()[:300])
        # NOT `last_change = now` HERE. Reading bytes that were already on disk
        # when this watchdog attached is not the log ADVANCING, and treating it
        # as advance is how a watchdog inherits a false assumption of health:
        # attached to a run that died an hour ago it would stay silent for a
        # further `--stall-seconds`. Growth is judged below, against last_size.

    if size != last_size:
        last_change = now
        last_size = size

    r = _round_count(log)
    if r > rounds:
        say("PROGRESS", f"round {r} landed (was {rounds})")
        rounds = r

    if not _alive(pid):
        say("PROCESS GONE", f"pid {pid} is no longer running; the run has ended")
        return offset, last_size, last_change, rounds, True

    stalled_for = now - last_change
    if stalled_for > stall_s:
        say("STALLED", f"no log growth for {int(stalled_for)} s "
                       f"(threshold {stall_s} s). SILENCE IS NOT SUCCESS — "
                       f"pause, diagnose, repair, resume.")
        last_change = now      # report once per stall window, not every tick
    return offset, last_size, last_change, rounds, False


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None)
    ap.add_argument("--log", required=True, help="the run's log file")
    ap.add_argument("--pid-file", default=None)
    ap.add_argument("--pid", type=int, default=None)
    ap.add_argument("--interval", type=int, default=60,
                    help="seconds between mechanical checks (cy cadence)")
    ap.add_argument("--stall-seconds", type=int, default=900,
                    help="log silence this long is an EVENT, not a non-event")
    ap.add_argument("--heartbeat-minutes", type=int, default=30,
                    help="say something even when all is well, so a dead "
                         "watchdog can be told from a quiet one")
    ap.add_argument("--max-hours", type=float, default=24.0)
    ap.add_argument("--once", action="store_true", help="single probe, then exit")
    args = ap.parse_args()

    log = pathlib.Path(args.log)
    pid = args.pid or _read_pid(pathlib.Path(args.pid_file) if args.pid_file else None)

    say("ARMED", f"log={log} pid={pid or 'unknown'} interval={args.interval}s "
                 f"stall={args.stall_seconds}s heartbeat={args.heartbeat_minutes}m")
    if not log.is_file():
        say("WATCHDOG", f"the log does not exist yet: {log}. Waiting for it — "
                        f"a run that never starts is itself an event.")

    # SEEDED FROM THE FILE, NOT FROM THE CLOCK. `last_size` starts at the size
    # already on disk so the first probe does not mistake existing bytes for
    # growth, and `last_change` starts at the log's own mtime so a run that
    # stalled BEFORE this watchdog armed is reported on the first probe rather
    # than `--stall-seconds` later. Caught by this script's own guard, which
    # failed until this was fixed.
    offset = 0
    try:
        last_size = log.stat().st_size if log.is_file() else 0
        last_change = log.stat().st_mtime if log.is_file() else time.time()
    except OSError:
        last_size, last_change = 0, time.time()
    started = last_beat = time.time()
    rounds = _round_count(log)
    ended = False

    stop = {"now": False}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, lambda *_a: stop.__setitem__("now", True))
        except (ValueError, OSError):
            pass

    while not stop["now"]:
        offset, last_size, last_change, rounds, ended = probe(
            log, pid, offset, last_size, last_change, rounds, args.stall_seconds)
        if ended or args.once:
            break
        if (time.time() - last_beat) > args.heartbeat_minutes * 60:
            say("HEARTBEAT", f"alive; {rounds} round(s) landed; log "
                             f"{last_size} bytes; "
                             f"{int(time.time()-started)} s elapsed")
            last_beat = time.time()
        if (time.time() - started) > args.max_hours * 3600:
            say("WATCHDOG", f"giving up after {args.max_hours} h — re-arm if the "
                            f"run is still expected to be alive")
            break
        time.sleep(max(1, args.interval))

    say("CLOSED", f"watchdog exiting; {rounds} round(s) landed; "
                  f"run_ended={ended}")
    return 0 if ended else 1


if __name__ == "__main__":
    raise SystemExit(main())
