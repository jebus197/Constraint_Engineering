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
import subprocess
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
    # `(?-i:...)` turns IGNORECASE OFF for this alternative alone. With
    # `re.I` applied to the whole pattern, the uppercase marker `FAILED`
    # also matched the lower-case word in "0 failed" — which is how a GREEN
    # result became an alarm. pytest writes the marker in capitals, so
    # requiring capitals here keeps the real signal and drops the false one.
    r"could not|cannot |(?-i:FAILED)|Error:|"
    # A COUNT OF ZERO IS NOT TROUBLE. The bare word `failed` matched
    # "8,878 passed, 0 failed" on this watchdog's first live outing, which is a
    # GREEN result reported as an alarm. A channel that cries wolf teaches its
    # reader to ignore it, and an ignored alarm is the 9-hour hole again by
    # another route. So a failure count must be NON-ZERO to speak, while
    # pytest's uppercase per-test `FAILED` marker above still speaks always.
    r"[1-9]\d*\s+(?:failed|error|errors)\b",
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


def _cpu_seconds(pid: int | None) -> float | None:
    """Cumulative CPU time the process has consumed, or None if unknown.

    THE DISCRIMINATOR A STALL ALARM NEEDS, added 2026-10-02 after this script's
    own first live false positive. It fired STALLED on a panel dispatch whose 2
    seats were healthy: `claude -p` writes nothing to the dispatcher's log until
    a seat finishes, and the previous round measured 1720.7 s to first output,
    so 900 s of silence is NORMAL for that workload and not a fault.

    RAISING THE THRESHOLD WOULD HAVE BEEN THE WRONG FIX. It buys quiet by going
    blind: a seat that hangs at second 30 then looks identical to one thinking
    at second 1700. What distinguishes them is not elapsed time, it is whether
    the process is still DOING anything. CPU% is useless here because a seat
    blocked on network I/O sits near 0.3%, indistinguishable from idle. But
    cumulative CPU TIME still advances for a streaming process and does not
    advance for a hung one.

    So silence remains an event, and the event now carries the one fact that
    tells the operator which kind of silence it is.
    """
    if not pid:
        return None
    try:
        r = subprocess.run(["ps", "-o", "cputime=", "-p", str(pid)],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    raw = (r.stdout or "").strip()
    if not raw:
        return None
    # macOS prints [[dd-]hh:]mm:ss
    days = 0
    if "-" in raw:
        d, raw = raw.split("-", 1)
        try:
            days = int(d)
        except ValueError:
            days = 0
    parts = raw.split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    secs = 0.0
    for n in nums:
        secs = secs * 60 + n
    return secs + days * 86400


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


#: What the run actually ENDED AS, which is not the same question as whether it
#: ended. Kept as 4 values, not 2.
OUTCOME_CLEAN = "CLEAN"
OUTCOME_BAD = "BAD"
OUTCOME_NO_SIGNAL = "NO_SIGNAL"
OUTCOME_UNREADABLE = "UNREADABLE"

#: Exit codes, so a caller can branch without parsing prose.
_EXIT = {OUTCOME_CLEAN: 0, OUTCOME_BAD: 2, OUTCOME_NO_SIGNAL: 3,
         OUTCOME_UNREADABLE: 4}


def read_outcome(log: pathlib.Path) -> tuple:
    """What the run ended AS. Returns (verdict, detail).

    THE DEFECT THIS FIXES, found by the cc2 seat in the free panel of
    2026-10-02 and reproduced on live code before being fixed: *"it goes silent
    whenever the run TERMINATES WITHOUT WRITING A TROUBLE TOKEN INTO THE LOG --
    and then it reports that silence as success. A halted-INCOMPLETE run and a
    clean convergence produced byte-identical output and the same exit code
    0."*

    Measured here: a run whose `completion_signal.json` said
    `HALTED_IRREDUCIBLE_QUEUE_ALARM` and one that said
    `CRITICAL_QUIESCENCE_CONVERGED` produced the SAME 3 stdout lines and the
    same exit 0, because this watchdog read only the log and the round files and
    never the signal. The worst outcome was announced exactly like the best.

    That is the defect class this whole script exists to prevent -- silence read
    as success -- reproduced inside the fix for it, within an hour of its own
    tests claiming it could not happen. The lesson is not about this file: a
    watcher must read the thing that RECORDS the verdict, never infer the
    verdict from the absence of complaint.

    NO_SIGNAL IS A THIRD VERDICT AND NOT A KIND OF BAD, on the seat's argument
    and the same principle as `stop_reason_recorded`: a run that ended without
    recording why is worse than any NAMED halt, because a named halt can be
    acted on and an unrecorded one cannot even be classified.
    """
    d = log.parent
    sig = d / "completion_signal.json"
    reports = sorted(d.glob("*_report.json"))
    if not sig.is_file() and not reports:
        return OUTCOME_NO_SIGNAL, ("no completion_signal.json and no report: "
                                   "the run recorded no verdict at all")
    status = reason = None
    for src in ([sig] if sig.is_file() else []) + reports:
        try:
            s = json.loads(src.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            return OUTCOME_UNREADABLE, f"{src.name} will not parse: {exc}"
        if not isinstance(s, dict):
            continue
        status = status or s.get("status")
        reason = reason or s.get("reason") or s.get("convergence_reason")
        if status or reason:
            break
    blob = f"{status or ''} {reason or ''}".upper()
    if not blob.strip():
        return OUTCOME_NO_SIGNAL, "a verdict file exists but names no status or reason"
    if "CONVERGED" in blob and "HALT" not in blob:
        return OUTCOME_CLEAN, f"status={status!r} reason={reason!r}"
    return OUTCOME_BAD, f"status={status!r} reason={reason!r}"


def say(kind: str, msg: str) -> None:
    """One event, one stdout line, flushed. The Monitor tool turns it into a wake."""
    print(f"[cy {time.strftime('%H:%M:%S')}] {kind}: {msg}", flush=True)


def probe(log: pathlib.Path, pid: int | None, offset: int, last_size: int,
          last_change: float, rounds: int, stall_s: int,
          last_cpu: float | None = None) -> tuple:
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
        return offset, last_size, last_change, rounds, True, last_cpu

    stalled_for = now - last_change
    if stalled_for > stall_s:
        cpu = _cpu_seconds(pid)
        advanced = (cpu is not None and last_cpu is not None
                    and cpu > last_cpu + 0.5)
        if not advanced and cpu is not None:
            # NO PRIOR SAMPLE, OR NONE RECENT ENOUGH TO DECIDE ON. The first
            # stall candidate arrives before any CPU delta can have
            # accumulated, so deciding from probe history alone reports a
            # STALL on a healthy process every time the alarm first trips.
            # Measure it here instead: 2 samples a second apart answer the
            # question without reference to when this watchdog happened to
            # start. A second is affordable because a stall candidate is rare
            # by construction.
            time.sleep(1.0)
            again = _cpu_seconds(pid)
            if again is not None and again > cpu + 0.02:
                advanced = True
                last_cpu, cpu = cpu, again
        if advanced:
            say("QUIET BUT WORKING",
                f"no log growth for {int(stalled_for)} s, but pid {pid} has "
                f"consumed {cpu - last_cpu:.1f} s more CPU since the last "
                f"check, so it is running and not hung. A panel seat writes "
                f"nothing until it finishes.")
        else:
            say("STALLED", f"no log growth for {int(stalled_for)} s "
                           f"(threshold {stall_s} s) AND no CPU progress"
                           + (f" (cputime {cpu:.1f} s, unchanged)" if cpu is not None
                              else " (CPU time unavailable)")
                           + ". SILENCE IS NOT SUCCESS — pause, diagnose, "
                             "repair, resume.")
        last_change = now      # report once per stall window, not every tick
    return offset, last_size, last_change, rounds, False, _cpu_seconds(pid)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None)
    # NOT `required=True`. argparse reports a MISSING required argument before
    # it reports an UNRECOGNISED one, so with --log required an unknown flag
    # produced "the following arguments are required: --log" and never the
    # "unrecognized arguments" that `test_an_unknown_flag_is_rejected_loudly`
    # requires of every operational script. The flag is still mandatory; its
    # absence is reported below, after argparse has had its say about unknown
    # flags. Same family of defect as the --help sweep of 2026-10-01.
    ap.add_argument("--log", help="the run's log file (required)")
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
    if not args.log:
        ap.error("--log is required: name the log file to watch")

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
    last_cpu = _cpu_seconds(pid)

    stop = {"now": False}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, lambda *_a: stop.__setitem__("now", True))
        except (ValueError, OSError):
            pass

    while not stop["now"]:
        offset, last_size, last_change, rounds, ended, last_cpu = probe(
            log, pid, offset, last_size, last_change, rounds, args.stall_seconds,
            last_cpu)
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

    # EVERY EXIT PATH SPEAKS THE OUTCOME. One more stdout line is one more
    # Monitor wake, which is exactly what a halt deserves and what it did not
    # get before.
    verdict, detail = read_outcome(log)
    say(f"OUTCOME {verdict}", detail)
    say("CLOSED", f"watchdog exiting; {rounds} round(s) landed; "
                  f"run_ended={ended}; outcome={verdict}")
    if not ended:
        return 1
    return _EXIT.get(verdict, 2)


if __name__ == "__main__":
    raise SystemExit(main())
