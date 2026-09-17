#!/usr/bin/env python3
"""Probe whether a model seat's shell can see a secret-named variable the dispatcher holds.

Measured 2026-09-17 on the Max plan, before and after `seat_environment()` was
wired into every place a seat is started:

    BEFORE (inherited environment): KEY_PRESENT PLAIN_PRESENT
    AFTER  (seat_environment):      KEY_ABSENT  PLAIN_PRESENT

The marker is FAKE and its value is never printed: the seat is asked only whether
each variable is present. It makes 2 `claude -p` calls on the Max subscription, so
it runs only with --live; without it, it describes the probe and exits.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROMPT = ("Run exactly this one shell command and reply with nothing but its output. It prints only "
          "PRESENT or ABSENT words and never prints any value: "
          "printenv CDSFL_PROBE_API_KEY >/dev/null && echo KEY_PRESENT || echo KEY_ABSENT; "
          "printenv CDSFL_PROBE_PLAIN >/dev/null && echo PLAIN_PRESENT || echo PLAIN_ABSENT")


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe whether a seat's shell can see a secret-named "
                                             "variable held by the dispatcher (2 free Max-plan calls).")
    ap.add_argument("--live", action="store_true", help="actually make the 2 claude -p calls")
    args = ap.parse_args()
    if not args.live:
        print("Not run. Pass --live to make 2 claude -p calls on the Max subscription.")
        return 0
    sys.path.insert(0, str(REPO / "bench"))
    import experiment_11_orchestrator as orch
    os.environ["CDSFL_PROBE_API_KEY"] = "fake-probe-not-a-real-key"
    os.environ["CDSFL_PROBE_PLAIN"] = "plain-visible"
    cmd = ["claude", "-p", PROMPT, "--model", "sonnet", "--output-format", "text",
           "--no-session-persistence", "--setting-sources", "", "--allowedTools", "Bash"]
    ok = True
    for label, env, want in (("BEFORE (inherited)", None, "KEY_PRESENT"),
                             ("AFTER  (seat_environment)", orch.seat_environment(), "KEY_ABSENT")):
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=180,
                           stdin=subprocess.DEVNULL, cwd="/tmp")
        out = " ".join(r.stdout.split())
        print(f"{label}: exit {r.returncode} -> {out[:200]}")
        ok = ok and want in out and "PLAIN_PRESENT" in out
    print("RESULT:", "the fix holds" if ok else "UNEXPECTED -- read the lines above")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
