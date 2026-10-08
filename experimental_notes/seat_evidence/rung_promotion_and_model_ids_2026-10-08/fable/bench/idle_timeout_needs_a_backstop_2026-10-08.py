# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5329f0888539f97f54471228773a5a8b6fde5f5162a4ff36eb6729bff64c3b23
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""An idle timeout on the stream is right -- and insufficient alone. Two
adversaries break idle-only harvesting, and both are demonstrated live:

  1. HEARTBEAT: a process emitting 1 byte/s never goes idle, so an idle-only
     policy runs it FOREVER. A total-cap backstop is required.
  2. BLOCK BUFFERING: a genuinely working child writing to a pipe without
     flushing emits NOTHING until its stdio buffer fills, so an idle-only
     policy kills a working process. The stream must be unbuffered (python -u
     or a pty) or the idle clock measures the buffer, not the model.

The composed policy (idle timeout + generous total cap + unbuffered stream) is
justified under the composability rule because each component alone FAILS a
demonstrated case: total-alone killed the brief's slow-but-working process at
5.0 s that completed at 8.1 s under idle; idle-alone never terminates the
heartbeat, measured below. Composition is the measurement, not a judgement.

Run: python3 bench/idle_timeout_needs_a_backstop_2026-10-08.py
Exits non-zero / prints FALSIFIED iff either adversary fails to break idle-only.
"""
import os
import select
import subprocess
import sys
import time

fails = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FALSIFIED'}: {name} {detail}")
    if not cond:
        fails.append(name)


def idle_harvest(cmd, idle_cap, total_cap=None):
    """Harvest stdout; kill when no bytes for idle_cap (or total_cap exceeded).
    Returns (bytes_read, elapsed, why)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    fd, buf, t0, last = p.stdout.fileno(), b"", time.monotonic(), time.monotonic()
    why = "eof"
    while True:
        now = time.monotonic()
        if total_cap and now - t0 >= total_cap:
            why = "total_cap"; break
        if now - last >= idle_cap:
            why = "idle_cap"; break
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            buf += chunk; last = time.monotonic()
        if p.poll() is not None and not select.select([fd], [], [], 0)[0]:
            break
    p.kill(); p.wait()
    return buf, time.monotonic() - t0, why


# ---- adversary 1: heartbeat never goes idle; only the total cap stops it ----
hb = [sys.executable, "-u", "-c",
      "import time\n"
      "while True: print('.', flush=True); time.sleep(0.5)"]
_, el, why = idle_harvest(hb, idle_cap=2.0, total_cap=6.0)
print(f"  heartbeat: stopped by {why} at {el:.1f}s (idle cap 2.0s never fired)")
check("idle-only never terminates a heartbeat; total cap is the backstop",
      why == "total_cap" and el >= 5.9)

# ---- adversary 2: block buffering makes a WORKING process look idle ----
worker_src = ("import sys, time\n"
              "for i in range(6): print('line', i); time.sleep(0.5)\n"
              "print('DONE')\n")
buffered = [sys.executable, "-c", worker_src]          # pipe => block-buffered
buf_b, el_b, why_b = idle_harvest(buffered, idle_cap=2.0)
unbuffered = [sys.executable, "-u", "-c", worker_src]  # -u => line-visible
buf_u, el_u, why_u = idle_harvest(unbuffered, idle_cap=2.0)
print(f"  buffered worker: {len(buf_b)}B seen, stopped by {why_b} at {el_b:.1f}s")
print(f"  unbuffered same: {len(buf_u)}B seen, stopped by {why_u} at {el_u:.1f}s")
check("block buffering starves the idle clock and kills a working process",
      why_b == "idle_cap" and b"DONE" not in buf_b)
check("the identical worker completes once the stream is unbuffered",
      b"DONE" in buf_u and why_u in ("eof",))

print()
if fails:
    print("FALSIFIED:", fails)
    raise SystemExit(1)
print("BOTH ADVERSARIES CONFIRMED -- idle timeout is the right primary, and it "
      "requires an unbuffered stream plus a total-cap backstop.")
