#!/bin/bash
# Arm the mechanical `cy` watch on the current free run, and open the founder's tail.
#
# HIS INSTRUCTION, 2026-10-15: *"You also built machinery previously to ensure
# cy ran mechanically and re-prompted you every minute to ensure you stayed on
# top of things. You should probably make sure you reuse this."* So this reuses
# `scripts/cy_watchdog_2026-10-02.py` rather than hand-polling: the 60-second
# cadence is MECHANICAL and costs nothing, and only an EVENT reaches the model.
#
# 3 CHANNELS, FAILING INDEPENDENTLY, because the failure being prevented is a
# watcher that went quiet:
#   1. the watchdog, every 60 s: process alive, log advancing, round landed,
#      error line appeared, stall exceeded.
#   2. a real Terminal window on the founder's own machine tailing the run, via
#      `scripts/local/open_run_tail.sh` -- a script FILE through osascript,
#      never the assistant's pane, which throws permission prompts that stop a
#      watch dead.
#   3. the assistant arms a Monitor on this watchdog's stdout, so each printed
#      event becomes a wake-up. Re-armed on expiry.
#
# SILENCE IS NOT SUCCESS. `--stall-seconds` makes ABSENCE reportable, so a hang
# and a crash are both events rather than quiet.
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"
LOG="${1:-$(cat /tmp/cdsfl_current_free_run.log 2>/dev/null || true)}"
if [ -z "${LOG:-}" ] || [ ! -f "$LOG" ]; then
  echo "usage: $0 [run-log]   (default: the log named in /tmp/cdsfl_current_free_run.log)" >&2
  exit 2
fi
PIDFILE="${LOG%.log}.pid"
echo "watching : $LOG"
echo "pid file : $PIDFILE"
bash scripts/local/open_run_tail.sh "$LOG" >/dev/null 2>&1 \
  && echo "tail     : opened on the founder's own Terminal" \
  || echo "tail     : FAILED to open (osascript refused) — report it, do not retry blind"
exec python3 scripts/cy_watchdog_2026-10-02.py \
     --log "$LOG" --pid-file "$PIDFILE" \
     --interval 60 --stall-seconds 900 --heartbeat-minutes 30 --max-hours 12
