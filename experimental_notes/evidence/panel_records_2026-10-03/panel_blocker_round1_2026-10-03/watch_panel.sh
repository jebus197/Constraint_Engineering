#!/bin/bash
# Founder-facing watch window (standing `cy` directive): a terminal kept open on
# the panel's full current output, on the local machine and not in the assistant's
# UX. Closes itself when the dispatch ends, so a quiet tail cannot be mistaken
# for a finished one.
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
D=bench/logs/panel_blocker_round1_2026-10-03
PID=$(cat "$D/panel.pid" 2>/dev/null)
echo "=== FREE PANEL: blocker round 1, 2026-10-03 ==="
echo "=== seats: cc2 + fable (free, Max plan). 0 paid dispatches. ==="
echo "=== PID $PID   log: $D/panel.log ==="
echo
tail -n +1 -F "$D/panel.log" &
TAILPID=$!
while kill -0 "$PID" 2>/dev/null; do sleep 5; done
sleep 3
kill $TAILPID 2>/dev/null
echo
echo "=== PANEL DISPATCH ENDED (pid $PID gone) ==="
