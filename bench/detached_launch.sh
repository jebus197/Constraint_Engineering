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
# NAME THE MONITOR HERE, because this is the only moment the operator has both
# the log path and the process id in front of them. The standing `cy` directive
# requires a terminal kept open on the run's full current output, and until
# 2026-09-09 nothing tied that terminal's lifetime to the run -- so a quiet tail
# could not be told from a finished one. bench/tail_until_done.sh closes when
# the run does and never signals it.
echo "monitor:  bash bench/tail_until_done.sh \"$LOG\""
