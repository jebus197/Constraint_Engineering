#!/bin/bash
# Detached panel dispatch (standing detached-launch rule, founder 2026-07-29):
# a panel dispatch must survive the Claude Code host process, so nohup + disown
# and the log is the only tether. bench/detached_launch.sh is hardcoded to
# launch_exp42.py and does not fit a panel run, so this is its sibling.
# FREE SEATS ONLY -- verified before launch: MODELS resolved to ['cc2','fable'],
# 0 paid. There must be no paid dispatch without the founder's authorisation.
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
LOG="bench/logs/panel_blocker_round1_2026-10-03/panel.log"
nohup env -u ANTHROPIC_BASE_URL -u MallocNanoZone -u MallocStackLogging \
  python3 bench/confer_maths_panel_2026-09-05.py panel_blocker_round1_2026-10-03 \
  >> "$LOG" 2>&1 &
PID=$!
disown $PID
echo "$PID" > "bench/logs/panel_blocker_round1_2026-10-03/panel.pid"
echo "detached PID $PID -> $LOG"
