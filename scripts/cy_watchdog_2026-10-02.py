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
    r"Traceback|Exception|FATAL|(?-i:CRITICAL)|Segmentation|MemoryError|"
    r"\bKilled\b|OOM|RecursionError|PermissionError|"
    r"HALTED|ALARM|(?-i:REFUSED)|UNRECORDED_STOP|"
    # BARE STATUS CODES ARE GONE, and that is a removal with a measurement
    # behind it. `401|403|429` matched inside the timestamp `20261002T064011Z`
    # -- the "4011" of an ordinary "Saved:" line -- so every artefact written
    # at such a second raised an alarm. Adding digit boundaries fixed the
    # timestamp and still matched "429 findings total", because a boundary
    # cannot tell a status code from a count, and context matching for 3 codes
    # is more machinery than the signal is worth.
    #
    # WHAT IS GIVEN UP, stated rather than discovered: a line whose ONLY
    # evidence of trouble is a bare status code no longer wakes anyone. The
    # transport failures that actually occur here are covered by the
    # `api error:` family below, by `rate limit`, `quota`, `5xx Server`, and by
    # Traceback and Exception -- the measured stall of 2026-10-02 carried
    # "API Error: Response stalled mid-stream" and no status code at all.
    #
    # Third pattern-calibration defect in this file, all the same shape: a
    # pattern matching more than it means, in a channel whose only value is
    # being believed.
    r"rate.?limit|quota|5\d\d Server|"
    # `(?-i:...)` turns IGNORECASE OFF for this alternative alone. With
    # `re.I` applied to the whole pattern, the uppercase marker `FAILED`
    # also matched the lower-case word in "0 failed" — which is how a GREEN
    # result became an alarm. pytest writes the marker in capitals, so
    # requiring capitals here keeps the real signal and drops the false one.
    # `could not` AND `cannot ` ARE GONE, on a census of the only live
    # evidence there is. Over the 476 lines of run 1b's log the 28 matching
    # lines break down as: `cannot ` 6, `could not` 4 -- and all 10 are
    # ORDINARY ENGLISH inside the run's own explanatory prose ("the control
    # cannot reach the target it reads", "the original passage could not be
    # located", "Covariance of the parameters could not be estimated"). Zero
    # were failures. The same census indicted two more tokens, both fixed
    # above by the `(?-i:)` precedent rather than by deletion, because both
    # have a real UPPERCASE machine form:
    #
    #   REFUSED   2 true tokens ("corrected copy REFUSED C0007"), 12 prose
    #             matches -- three of which read "0 refused", which is the
    #             zero-count principle below for a third time.
    #   CRITICAL  0 true tokens, 4 matches inside `gamma_critical` and
    #             `critical-quiescence`, so it fired EVERY ROUND OF EVERY RUN.
    #
    # WHAT IS GIVEN UP: a failure whose only evidence is the phrase "cannot"
    # or "could not", with no error token anywhere on the line, no longer
    # wakes anyone. `Error:`, `Traceback`, `Exception`, `PermissionError`,
    # `MemoryError` and the rest are untouched, and a C-style "fatal error:"
    # still speaks through `Error:`.
    #
    # NOT NARROWED, deliberately: `[1-9]\d*\s+(?:failed|error|errors)` fires
    # on "Skin barrier (v2): 5 passed, 15 failed out of 20 findings", a routine
    # per-round census, roughly twice a run. It shares its exact lexical shape
    # with "3 failed, 9372 passed in 3217.53s", which
    # `test_a_real_failure_count_still_wakes_the_model` pins as a line that
    # MUST speak. Separating them needs the phrase "out of N findings", which
    # is over-fitting to one log. The 2 noise events are the accepted price of
    # catching a red suite, and saying so beats discovering it again.
    r"(?-i:FAILED)|Error:|"
    # A COUNT OF ZERO IS NOT TROUBLE. The bare word `failed` matched
    # "8,878 passed, 0 failed" on this watchdog's first live outing, which is a
    # GREEN result reported as an alarm. A channel that cries wolf teaches its
    # reader to ignore it, and an ignored alarm is the 9-hour hole again by
    # another route. So a failure count must be NON-ZERO to speak, while
    # pytest's uppercase per-test `FAILED` marker above still speaks always.
    r"[1-9]\d*\s+(?:failed|error|errors)\b",
    re.I)
#: Above this many problem lines ALREADY IN THE LOG when the watch arms, the
#: first probe summarises them instead of replaying one event each.
#:
#: MEASURED, 2026-10-02, on the re-arm of the watch over run 1b: the arming
#: probe read from byte 0 and emitted an event for all 28 matching lines of a
#: 42,695-byte log. The notification that carried them was CUT with
#: "...(truncated)" partway through -- and because the replay runs oldest-first,
#: the lines it dropped were the NEWEST ones, which are the only ones that
#: could still need acting on. So the flood was not merely noisy, it was LOSSY
#: in exactly the direction that matters. Re-arming is by design (one arming
#: caps at 30 minutes), so this recurred roughly every half hour.
#:
#: A small backlog is still replayed verbatim: a watch attached to a log
#: holding one Traceback should say so plainly, and the regex tests drive that
#: path, so narrowing it would have made 14 of them assert against a channel
#: nothing reaches.
BACKLOG_SUMMARY_THRESHOLD = 5

# Progress markers: worth one line each, because a run that is moving is news
# after a stall and the absence of them is the stall signal.
PROGRESS = re.compile(r"ROUND\s+(\d+)|round_(\d+)\.json|CONVERGED|convergence|"
                      r"writing report|completion_signal", re.I)


def _alive(pid: int | None) -> bool:
    """Whether the run is still running -- which is not "does the pid exist".

    A ZOMBIE PASSES `os.kill(pid, 0)`. An exited process whose parent has not
    yet reaped it keeps its pid in the table and accepts signal 0, so the
    kill-based check called it ALIVE after it had finished. Found 2026-10-02 by
    this file's own end-to-end test, which terminated its child and then hung
    for the full 30 s timeout waiting for a PROCESS GONE that could not come.

    The consequence was degradation, not silence: the log stops growing too, so
    the stall path eventually speaks -- but `--stall-seconds` later (1200 s as
    armed) and under the wrong name, reporting a finished run as a hung one.
    Shells reap background jobs promptly, so the window is normally brief; it is
    the END of a run, which is exactly the moment this watch exists to catch.

    `ps -o state=` is the same mechanism `_cpu_seconds` already uses, so the
    cost is one more short-lived process per poll -- at a 60 s cadence, nothing.
    """
    if not pid:
        return True            # no pid supplied: liveness is judged by the log
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True            # exists, owned by someone else
    try:
        state = subprocess.run(["ps", "-o", "state=", "-p", str(pid)],
                               capture_output=True, text=True,
                               timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return True            # cannot tell: assume alive, the log will judge
    if state.startswith("Z"):
        return False
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


def _round_count(log: pathlib.Path,
                 outcome_dir: pathlib.Path | None = None) -> int:
    """Rounds landed, read from the run's own artefacts, not from its prose.

    THE SAME WRONG DIRECTORY AS `read_outcome`, found 2026-10-02 from a
    heartbeat that said "0 round(s) landed" while the console showed the run in
    ROUND 1. The artefacts live in the run's own timestamped directory, not
    beside the console log, so this counted 0 forever. A monitoring channel
    reporting a false number is the defect this whole script exists to remove,
    and fixing `read_outcome` alone left its twin -- which is the shape this
    project keeps finding.
    """
    d = pathlib.Path(outcome_dir) if outcome_dir else log.parent
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



_SUITE_SUMMARY = re.compile(
    # `warnings` BELONGS IN THIS LIST. Without it the live green summary
    # `9668 passed, 7 skipped, 20 warnings in 2944.77s` did not match: the
    # alternation stopped at `7 skipped, ` and then required `in <seconds>s`
    # where `20 warnings` stood, so the best outcome of the day read NO_SIGNAL.
    # Caught by running this against the real log rather than by reading it.
    r"^(?P<body>(?:\d[\d,]*\s+(?:passed|failed|skipped|errors?|warnings?"
    r"|xfailed|xpassed|deselected)(?:,\s*)?)+)\s+in\s+[\d.]+s", re.M)
_SUITE_EXIT = re.compile(r"^EXIT=(?P<code>\d+)\b", re.M)
_SUITE_FAILED = re.compile(r"\b([1-9][\d,]*)\s+failed\b")


def _suite_outcome(log: pathlib.Path):
    """A pytest run's verdict, read from its own summary. None if not a suite.

    WHY THIS IS NOT A GUESS. Two independent anchors must agree that this log
    belongs to a test run: a pytest summary line of the exact shape
    `<counts> in <seconds>s`, and/or the `EXIT=<code>` line the suite launcher
    writes. A log that merely contains the word "passed" in prose matches
    neither, so an experiment log cannot be misread as a suite.
    """
    try:
        text = log.read_text(errors="ignore") if log.is_file() else ""
    except OSError:
        return None
    summary = None
    for m in _SUITE_SUMMARY.finditer(text):
        summary = m.group("body").strip().rstrip(",")
    exit_m = None
    for m in _SUITE_EXIT.finditer(text):
        exit_m = m
    if summary is None and exit_m is None:
        return None
    failed = _SUITE_FAILED.search(summary or "")
    code = int(exit_m.group("code")) if exit_m else None
    if failed or (code is not None and code != 0):
        return OUTCOME_BAD, (f"test suite: {summary or 'no summary line'}"
                             + (f" (EXIT={code})" if code is not None else "")
                             + " -- this is NOT a clean suite")
    if summary is None:
        return None          # EXIT=0 alone is not a suite verdict
    return OUTCOME_CLEAN, (f"test suite: {summary}"
                           + (f" (EXIT={code})" if code is not None else ""))


def read_outcome(log: pathlib.Path, outcome_dir: pathlib.Path | None = None) -> tuple:
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
    # THE VERDICT IS NOT ALWAYS BESIDE THE CONSOLE LOG, and assuming it was
    # would have manufactured a false NO_SIGNAL at the end of a 2-hour run.
    # `run_simulated_experiment.py` writes its artefacts into a TIMESTAMPED
    # directory it names itself, while the console log is wherever the operator
    # redirected it. Caught on the first real launch, 2026-10-02, before the
    # run ended rather than after.
    d = pathlib.Path(outcome_dir) if outcome_dir else log.parent
    sig = d / "completion_signal.json"
    reports = sorted(d.glob("*_report.json"))
    if not sig.is_file() and not reports:
        # A TEST SUITE RECORDS ITS VERDICT TOO, just not as a signal file.
        # Measured 2026-10-02 16:01: the confirming full suite finished
        # `9668 passed, 7 skipped, 0 failed` with `EXIT=0`, and this function
        # announced `OUTCOME NO_SIGNAL: the run recorded no verdict at all`.
        # That is the cry-wolf class this script spent the same morning
        # removing from its own TROUBLE channel, reappearing one function away:
        # a channel whose only value is being believed, reporting the best
        # possible outcome as an unrecorded one.
        #
        # ANCHORED, not loose. The summary must carry a pytest-shaped count
        # (`N passed` / `N failed`) or an explicit `EXIT=` written by the
        # launcher. Prose that merely contains the word "passed" does not
        # qualify, which `test_prose_mentioning_passed_is_not_a_verdict` pins.
        verdict = _suite_outcome(log)
        if verdict is not None:
            return verdict
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
          last_cpu: float | None = None,
          outcome_dir: pathlib.Path | None = None,
          first: bool = False) -> tuple:
    """One mechanical check. Returns new state and emits events for what changed."""
    now = time.time()
    exists = log.is_file()
    size = log.stat().st_size if exists else 0

    # TRUNCATION OR ROTATION, found by the fable seat in the free panel of
    # 2026-10-02 and reproduced before fixing. A run that reopens its log with
    # "w", or a supervisor that rotates it, leaves the file SHORTER than the
    # offset already read. `size > offset` was then false forever and this
    # watchdog stopped reading the log permanently -- going BLIND rather than
    # silent, which is worse than the seat's own framing.
    #
    # MEASURED: a `Traceback ... RuntimeError: seat crashed` written into a
    # freshly truncated log produced NO TROUBLE event at any point, because the
    # offset stood at 5018 bytes against a 62-byte file. A short stall
    # threshold masked it by catching the stall instead; at a realistic
    # --stall-seconds the crash was never mentioned. Verified formally
    # afterwards: z3 finds the old rule blind to every truncated state and
    # UNSAT for the new one, and an exhaustive sweep agrees at 79,800 of 79,800
    # against 0.
    #
    # The truncation is announced in its own right: a run rewriting its own log
    # is doing something unusual and the operator should hear it, not infer it
    # from a byte count going backwards.
    if exists and size < offset:
        say("LOG TRUNCATED", f"the log shrank from {offset} to {size} bytes, so "
                             f"it was rewritten or rotated. Re-reading from the "
                             f"start; anything written before this is already "
                             f"reported.")
        offset = 0
        last_size = 0

    if exists and size > offset:
        try:
            with log.open("r", errors="ignore") as fh:
                fh.seek(offset)
                chunk = fh.read()
                offset = fh.tell()
        except OSError as exc:
            say("WATCHDOG", f"cannot read the log ({exc}); treating as stalled")
            chunk = ""
        matches = [ln.strip()[:300] for ln in chunk.splitlines()
                   if TROUBLE.search(ln)]
        if first and len(matches) > BACKLOG_SUMMARY_THRESHOLD:
            say("BACKLOG", f"the log already held {len(matches)} problem "
                           f"line(s) written before this watch armed. They are "
                           f"summarised, not replayed: a replay of that many "
                           f"gets cut off, and it is the newest lines -- the "
                           f"only ones still worth acting on -- that get cut. "
                           f"Read the log for the rest. The 3 most recent:")
            for mt in matches[-3:]:
                say("BACKLOG LINE", mt)
        else:
            for mt in matches:
                say("TROUBLE", mt)
        # NOT `last_change = now` HERE. Reading bytes that were already on disk
        # when this watchdog attached is not the log ADVANCING, and treating it
        # as advance is how a watchdog inherits a false assumption of health:
        # attached to a run that died an hour ago it would stay silent for a
        # further `--stall-seconds`. Growth is judged below, against last_size.

    if size != last_size:
        last_change = now
        last_size = size

    r = _round_count(log, outcome_dir)
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
    ap.add_argument("--outcome-dir", default=None,
                    help="where the run writes completion_signal.json and its "
                         "report, when that is not the log's own directory")
    ap.add_argument("--once", action="store_true", help="single probe, then exit")
    args = ap.parse_args()
    if not args.log:
        ap.error("--log is required: name the log file to watch")

    log = pathlib.Path(args.log)
    outcome_dir = pathlib.Path(args.outcome_dir) if args.outcome_dir else None
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
    rounds = _round_count(log, outcome_dir)
    ended = False
    last_cpu = _cpu_seconds(pid)

    stop = {"now": False}
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, lambda *_a: stop.__setitem__("now", True))
        except (ValueError, OSError):
            pass

    first = True
    while not stop["now"]:
        offset, last_size, last_change, rounds, ended, last_cpu = probe(
            log, pid, offset, last_size, last_change, rounds, args.stall_seconds,
            last_cpu, outcome_dir, first=first)
        first = False
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
    verdict, detail = read_outcome(log, outcome_dir)
    say(f"OUTCOME {verdict}", detail)
    say("CLOSED", f"watchdog exiting; {rounds} round(s) landed; "
                  f"run_ended={ended}; outcome={verdict}")
    # THE EXIT CODE STAYS AS IT WAS, and that is the cc2 seat's call over this
    # assistant's. Its specification carried the verdict as one more stdout
    # line -- one more Monitor wake -- and deliberately did not touch the exit
    # contract; `test_the_exit_code_contract_is_untouched` pins that. The first
    # version here returned 0/2/3/4 by outcome, and the measurement settled it
    # against that: a NO_SIGNAL end returned 3 and the Monitor reported
    # "script failed (exit 3)" for an ordinary finish, manufacturing exactly
    # the misleading signal this work exists to remove. The verdict travels in
    # the OUTCOME line, which is what drives the wake.
    return 0 if ended else 1


if __name__ == "__main__":
    raise SystemExit(main())
