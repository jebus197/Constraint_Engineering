#!/bin/bash
# Follow a run's log and EXIT WHEN THE RUN EXITS. Task 6.5.
#
# WHY THIS EXISTS. The standing `cy` directive requires a terminal kept open on
# the running experiment's full current output. Nothing tied that terminal's
# lifetime to the run: 0 launchers clean up a monitor, and the only process-id
# file written -- by bench/detached_launch.sh:11 -- is read by
# scripts/cdsfl_recover.py to REPORT whether an experiment is running, never to
# stop anything. So a monitor outlives its run, and a founder looking at a quiet
# tail cannot tell "the run is thinking" from "the run ended an hour ago".
#
# WHY A WRAPPER RATHER THAN A FLAG. GNU tail has `--pid`, which does exactly
# this. macOS tail does not: measured on this machine, `tail --pid=1 /dev/null`
# returns "unrecognized option" and the flag appears 0 times in `man tail`.
# No gtail is installed. So the tie has to be polled.
#
# USAGE
#   bench/tail_until_done.sh <logfile> [pid | pidfile]
# With no second argument the pidfile is derived the way detached_launch.sh
# writes it: "${LOG%.log}.pid".
#
# EXIT STATUS
#   0  the run finished and the tail was closed after a final flush
#   2  the log does not exist
#   3  no process id could be resolved, so nothing could be tied to
#
# IT KILLS ONLY THE TAIL IT STARTED. The run is never signalled; this is a
# monitor, and a monitor that can stop an experiment is a hazard, not a feature.
set -uo pipefail

# IS THE RUN STILL RUNNING? `kill -0` alone is NOT enough, and the difference is
# the whole defect in a new guise. A process that has exited but whose parent has
# not reaped it is a ZOMBIE: it keeps its slot in the process table, so `kill -0`
# SUCCEEDS and a monitor polling on that alone waits for ever -- outliving its
# run, which is what this script exists to prevent. Measured on this machine: a
# child that has exited and not been waited on reports `ps -o state=` as "Z"
# while `kill -0` returns 0; after reaping, `kill -0` fails.
#
# It matters in practice whenever the monitor is started from the same shell that
# launched the run. A run detached through bench/detached_launch.sh is reparented
# and reaped promptly, so the plain check would usually work -- "usually" being
# the word this project has learned to distrust.
run_is_alive() {
  kill -0 "$1" 2>/dev/null || return 1
  local state
  state="$(ps -o state= -p "$1" 2>/dev/null | tr -d ' ')"
  case "$state" in
    Z*) return 1 ;;   # exited, awaiting reaping
    "") return 1 ;;   # gone between the two checks
    *)  return 0 ;;
  esac
}

POLL_SECONDS="${POLL_SECONDS:-2}"
FLUSH_SECONDS="${FLUSH_SECONDS:-2}"
TAIL_LINES="${TAIL_LINES:-80}"
WAIT_FOR_PIDFILE="${WAIT_FOR_PIDFILE:-10}"

LOG="${1:-}"
if [ -z "$LOG" ]; then
  echo "usage: $(basename "$0") <logfile> [pid | pidfile]" >&2
  exit 3
fi
if [ ! -f "$LOG" ]; then
  echo "no such log: $LOG" >&2
  exit 2
fi

RUN_PID=""
ARG2="${2:-}"
if [ -n "$ARG2" ] && [ "$ARG2" -eq "$ARG2" ] 2>/dev/null; then
  RUN_PID="$ARG2"
else
  PIDFILE="${ARG2:-${LOG%.log}.pid}"
  # The launcher writes the pidfile immediately after backgrounding, but a
  # monitor started in the same breath can still lose the race.
  waited=0
  while [ ! -f "$PIDFILE" ] && [ "$waited" -lt "$WAIT_FOR_PIDFILE" ]; do
    sleep 1
    waited=$((waited + 1))
  done
  if [ -f "$PIDFILE" ]; then
    RUN_PID="$(tr -dc '0-9' < "$PIDFILE")"
  fi
fi

if [ -z "$RUN_PID" ]; then
  echo "no process id resolved for $LOG (looked for ${PIDFILE:-a pid argument})" >&2
  echo "refusing to tail untethered: an untied monitor is the defect this fixes" >&2
  exit 3
fi

if ! run_is_alive "$RUN_PID"; then
  echo "run $RUN_PID is not alive; showing the tail of $LOG and exiting"
  tail -n "$TAIL_LINES" "$LOG"
  exit 0
fi

echo "tailing $LOG, tied to run $RUN_PID (exits when the run does)"
tail -n "$TAIL_LINES" -f "$LOG" &
TAIL_PID=$!
# CLEAN UP ON EVERY EXIT PATH -- AND ACTUALLY EXIT ON A SIGNAL.
#
# A first version used one trap for EXIT, INT and TERM that killed the tail and
# nothing else. Bash then RESUMED THE POLLING LOOP, so the monitor ignored
# ctrl-C and outlived the founder closing the window, waiting until the run
# ended on its own. Measured: SIGTERM at t=1.5s, the wrapper returned at
# t=13.5s, exactly when the 12-second stand-in run finished. That is this
# script's own defect wearing its own name -- a monitor that will not stop.
#
# So the signal traps exit explicitly, and EXIT keeps the cleanup only.
# 130 and 143 are the conventional codes for a shell killed by INT and TERM.
cleanup() { kill "$TAIL_PID" 2>/dev/null; }
trap cleanup EXIT
trap 'cleanup; echo; echo "monitor closed by signal; the run was NOT touched."; exit 130' INT
trap 'cleanup; echo; echo "monitor closed by signal; the run was NOT touched."; exit 143' TERM

while run_is_alive "$RUN_PID"; do
  sleep "$POLL_SECONDS"
done

# The run has gone. Give tail a moment to pick up whatever it wrote last,
# because the most interesting lines in this project are usually the final ones.
sleep "$FLUSH_SECONDS"
kill "$TAIL_PID" 2>/dev/null
wait "$TAIL_PID" 2>/dev/null
echo
echo "run $RUN_PID has exited; monitor closed."
exit 0
