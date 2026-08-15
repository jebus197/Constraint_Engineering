#!/bin/bash
# CDSFL detached experiment launcher (founder directive 2026-07-29):
# runners MUST survive the Claude Code host process. setsid-equivalent
# detachment via nohup + disown; logs are the only tether.
CONFIG="$1"; LOG="$2"; RESUME="$3"
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
nohup env -u ANTHROPIC_BASE_URL -u MallocNanoZone -u MallocStackLogging \
  python3 bench/launch_exp42.py --config "$CONFIG" $RESUME >> "$LOG" 2>&1 &
PID=$!
disown $PID
echo "$PID" > "${LOG%.log}.pid"
echo "detached PID $PID -> $LOG"
