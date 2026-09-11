#!/bin/bash
# RESTART THE DESKTOP APP AND COME BACK TO THIS SESSION, FROM ANYWHERE.
#
# Put this on the hotel machine and run it. It reaches the Mac mini over
# Tailscale, restarts the Claude desktop application, and reopens the working
# session so you can carry on immediately.
#
# WHY IT EXISTS. The desktop app force-restarts to apply a pending update the
# moment the session goes IDLE -- measured twice, 2026-09-04 23:10:45 after 76
# hours and 2026-09-08 16:52:11 after 85 hours, with 48 consecutive deferrals
# each logged as "Claude is working". It waits for the first quiet moment, which
# is exactly when a remote user is least able to notice, and the session does not
# reconnect by itself. Until now the only known remedy was to be physically at
# the machine. That is what this removes.
#
#   ./restart_claude_from_hotel.sh              restart the app and resume
#   ./restart_claude_from_hotel.sh --dry-run    check everything, change nothing
#   ./restart_claude_from_hotel.sh --resume-only    do not touch the app
#   ./restart_claude_from_hotel.sh --check      reachability only
#
# IT DELETES NOTHING and touches no git ref, no key, and no paid service.

set -uo pipefail

HOST="${CLAUDE_MAC_HOST:-georgejackson@mac-mini.tail8b628c.ts.net}"
PROJECT="${CLAUDE_PROJECT_DIR:-~/Developer_Projects/Constraint_Engineering}"
SESSION="${CLAUDE_SESSION_ID:-a07b3790-0a2a-4978-aedb-bd842c0493d3}"
SSH_OPTS="-o ConnectTimeout=15 -o BatchMode=yes"

DRY=0; RESUME_ONLY=0; CHECK_ONLY=0
for a in "$@"; do
  case "$a" in
    --dry-run)     DRY=1 ;;
    --resume-only) RESUME_ONLY=1 ;;
    --check)       CHECK_ONLY=1 ;;
    -h|--help)     sed -n '2,26p' "$0"; exit 0 ;;
    # AN UNRECOGNISED FLAG MUST NOT READ AS SUCCESS. This project spent 118 days
    # on that defect; a script you run from a hotel is the last place to repeat it.
    *) echo "unknown option: $a" >&2
       echo "try: $0 --help" >&2
       # NOTHING HAS RUN AT THIS POINT, so the reassurance is true here and is
       # the one a reader most needs after a typo. Entry 10.1 claimed "every
       # failure path says NOTHING WAS CHANGED" and this path did not -- found by
       # the adversarial audit of 2026-09-11. Making the universal TRUE is worth
       # more than narrowing it. It is deliberately NOT added after the restart
       # step, where it would be false.
       echo "  NOTHING WAS CHANGED." >&2
       exit 2 ;;
  esac
done

say()  { printf '  %s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }

step "1. Is the Mac reachable?"
if ! command -v tailscale >/dev/null 2>&1; then
  say "tailscale CLI not found on this machine -- skipping the tailnet check."
  say "The SSH attempt below is still the real test."
else
  if tailscale status 2>/dev/null | grep -q "mac-mini"; then
    say "tailnet: mac-mini is listed."
  else
    say "tailnet: mac-mini is NOT listed. It may be asleep or off the tailnet."
    say "Nothing else here will work until it is back. Not an error in this script."
  fi
fi

_probe=$(ssh $SSH_OPTS "$HOST" 'echo ok' 2>&1)
if [ "$_probe" != "ok" ]; then
  # THE FIRST-RUN CASE, AND IT WOULD HAVE BITTEN YOU IN THE HOTEL.
  # BatchMode=yes is right -- it stops the script hanging on a password prompt
  # you cannot see -- but it also means the very first connection to a host
  # fails outright instead of offering the usual "continue connecting?" question.
  # Found by running this script before shipping it, not by reasoning about it.
  if printf '%s' "$_probe" | grep -qi "host key verification failed"; then
    echo "  FIRST CONNECTION FROM THIS MACHINE: the Mac's host key is not yet" >&2
    echo "  trusted here, and this script deliberately refuses to auto-accept it." >&2
    echo "" >&2
    echo "  Run this ONCE, answer yes, then re-run this script:" >&2
    echo "" >&2
    echo "      ssh $HOST 'echo ok'" >&2
    echo "" >&2
    echo "  NOTHING WAS CHANGED." >&2
    exit 3
  fi
  echo "  CANNOT REACH $HOST over SSH." >&2
  printf '  ssh said: %s\n' "$_probe" >&2
  echo "  Check: the Mac is awake, Tailscale is up on both ends, and your key is" >&2
  echo "  loaded (ssh-add -l). NOTHING WAS CHANGED." >&2
  exit 1
fi
say "SSH: reachable."

step "2. Is an update pending? (this is what causes the restart)"
ssh $SSH_OPTS "$HOST" \
  "grep -h 'updater' ~/Library/Logs/Claude/main.log 2>/dev/null | tail -3" \
  | sed 's/^/  /' || say "(no updater lines found; that is fine)"

if [ "$CHECK_ONLY" = "1" ]; then
  step "--check given: stopping here. Nothing was changed."
  exit 0
fi

if [ "$RESUME_ONLY" = "0" ]; then
  step "3. Restart the desktop application"
  if [ "$DRY" = "1" ]; then
    say "DRY RUN: would quit and reopen Claude.app on the Mac."
  else
    ssh $SSH_OPTS "$HOST" 'osascript -e "quit app \"Claude\"" 2>/dev/null; sleep 4; open -a Claude' \
      && say "restarted." || say "restart command returned non-zero; continuing to the resume step anyway."
    sleep 6
  fi
else
  step "3. --resume-only given: the application is left alone."
fi

step "4. Reopen the working session"
say "session id: $SESSION"
if [ "$DRY" = "1" ]; then
  say "DRY RUN: would run, on the Mac:"
  say "  cd $PROJECT && claude --resume $SESSION"
  say "and fall back to 'claude --continue' if that id is gone."
  step "DRY RUN COMPLETE. Nothing was changed."
  exit 0
fi

# `--resume <id>` restores THIS conversation. `--continue` takes the most recent
# one in that directory, which is the right fallback if the id has aged out.
echo
echo "  Handing you an interactive session. Ctrl-D or /exit to leave it."
echo
exec ssh -t $SSH_OPTS "$HOST" \
  "cd $PROJECT && (claude --resume $SESSION || claude --continue)"
