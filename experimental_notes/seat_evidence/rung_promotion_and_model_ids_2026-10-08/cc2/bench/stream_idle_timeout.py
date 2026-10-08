# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8b1ceb2d8d0388ed78eb4493e98346ada0c9a57e41172180158302489a438a66
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Harvesting a model's output: an idle timeout on the stream, with a ceiling.

OPEN QUESTION 6. The founder's position is that output should be harvested when a
model is done rather than at an arbitrary wall clock. An idle timeout on the
stream implements that: the clock measures time since the last byte, so a slow
but progressing process is never killed for being slow.

WHAT BREAKS AN IDLE TIMEOUT ALONE, and both failures are demonstrated by
`bench/test_stream_idle_timeout.py` against real subprocesses:

  1. A HUNG PROCESS THAT KEEPS TALKING. An idle timer is reset by any byte, so a
     retry loop printing a warning, a progress bar, or a keepalive never trips
     it. The process is dead and the harness waits forever. This is the exact
     failure mode a total cap catches and an idle cap cannot.
  2. BLOCK-BUFFERED OUTPUT. A child whose stdout is a pipe gets a 4-8 KiB block
     buffer, so a working process can emit nothing at all until it exits. The
     idle timer then measures the whole run as idleness and kills a healthy
     process. The repair is to force line buffering in the child (`python3 -u`
     or PYTHONUNBUFFERED=1) AND to treat process exit, not stream silence, as
     the end of the stream - which `harvest` does by polling the child.

SO THE MECHANISM IS AN IDLE TIMEOUT **AND** A CEILING, and that composition is
justified by measurement rather than by the fact that the two can coexist:
neither alone covers both cases. Measured in the falsifier - idle-only does not
terminate the chatty hang within the ceiling; ceiling-only kills the slow-but-
working process before it finishes. The ceiling is NOT the primary control and
is set far above any legitimate run; it exists only to bound case 1.

THE CEILING IS DERIVED, NOT CHOSEN. Given a measured distribution of completion
times for legitimate runs, the ceiling is the quantile at which the tolerated
rate of killing good work equals `kill_budget`. `derive_ceiling` computes it
from observed durations with a one-sided upper confidence allowance, so the
ceiling errs long - the direction that preserves work.
"""
from __future__ import annotations

import math
import os
import subprocess
import time


def min_samples_for_ceiling(kill_budget: float, z: float = 1.959963984540054) -> int:
    """Observed legitimate runs needed before a ceiling can be placed below the max.

    The one-sided allowance on the (1-kill_budget) quantile is
    z*sqrt(q(1-q)/m) with q = 1-kill_budget. The allowance must be smaller than
    kill_budget itself, or q_hi reaches 1 and the ceiling degenerates to the
    observed maximum. Solving z*sqrt(q(1-q)/m) < kill_budget gives

        m > z**2 * q * (1-q) / kill_budget**2

    At kill_budget=0.05 that is m >= 73; at 0.20, m >= 16. So a ceiling cannot
    be set from a handful of runs, and `derive_ceiling` returns the observed
    maximum until the sample reaches this size - erring long, which preserves
    work rather than discarding it.
    """
    if not 0.0 < kill_budget < 1.0:
        raise ValueError("kill_budget must be in (0,1)")
    q = 1.0 - kill_budget
    return int(math.floor(z * z * q * (1.0 - q) / (kill_budget * kill_budget))) + 1


def derive_ceiling(observed_durations, kill_budget: float, z: float = 1.959963984540054) -> float:
    """Absolute ceiling from observed legitimate completion times.

    The ceiling must kill at most `kill_budget` of legitimate runs. With m
    observed durations, the empirical (1-kill_budget) quantile is itself
    estimated, so the ceiling is placed at that quantile inflated by a one-sided
    allowance for the quantile's own standard error, sqrt(q(1-q)/m) in
    probability space. That makes the ceiling a bound rather than a point
    estimate, and it errs long. Below `min_samples_for_ceiling` the allowance
    exceeds `kill_budget` and the result degenerates to the observed maximum;
    that is reported by `min_samples_for_ceiling`, not hidden.

    Raises ValueError on an empty sample: a ceiling cannot be derived from no
    data, and inventing one is the arbitrary wall clock this replaces.
    """
    d = sorted(float(x) for x in observed_durations)
    if not d:
        raise ValueError("no observed durations: the ceiling cannot be derived")
    if not 0.0 < kill_budget < 1.0:
        raise ValueError("kill_budget must be in (0,1)")
    m = len(d)
    q = 1.0 - kill_budget
    q_hi = min(1.0, q + z * math.sqrt(q * (1.0 - q) / m))
    idx = min(m - 1, max(0, int(math.ceil(q_hi * m)) - 1))
    return d[idx]


def harvest(argv, idle_timeout: float, ceiling: float,
            env: dict | None = None) -> dict:
    """Run `argv`, harvesting lines until the child is done.

    Terminates on whichever comes first:
      * the child exiting (the normal case - output is harvested, not truncated);
      * `idle_timeout` seconds with no byte on the stream;
      * `ceiling` seconds of total wall clock.

    The child is run with PYTHONUNBUFFERED=1 so that block buffering cannot
    present a working process as an idle one.

    Returns {"lines", "reason", "elapsed", "returncode"} with `reason` in
    {"exit", "idle", "ceiling"}. The reason is recorded because an idle kill and
    a ceiling kill are different diagnoses and must not be collapsed.
    """
    e = dict(os.environ if env is None else env)
    e["PYTHONUNBUFFERED"] = "1"
    t0 = time.monotonic()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, bufsize=1, env=e)
    import selectors
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    lines, last = [], time.monotonic()
    reason = "exit"
    try:
        while True:
            now = time.monotonic()
            if now - t0 >= ceiling:
                reason = "ceiling"
                break
            if now - last >= idle_timeout:
                reason = "idle"
                break
            slice_s = min(0.05, max(0.0, idle_timeout - (now - last)),
                          max(0.0, ceiling - (now - t0)))
            for _k, _m in sel.select(timeout=max(slice_s, 0.01)):
                line = proc.stdout.readline()
                if line:
                    lines.append(line.rstrip("\n"))
                    last = time.monotonic()
            if proc.poll() is not None:
                for line in proc.stdout:               # drain, do not truncate
                    lines.append(line.rstrip("\n"))
                reason = "exit"
                break
    finally:
        sel.close()
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        try:
            proc.stdout.close()
        except Exception:
            pass
    return {"lines": lines, "reason": reason,
            "elapsed": round(time.monotonic() - t0, 2),
            "returncode": proc.returncode}
