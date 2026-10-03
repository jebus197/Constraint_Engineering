#!/bin/bash
# Open a Terminal window on the FOUNDER'S OWN MACHINE tailing a live run.
#
# WHY A SCRIPT FILE AND NOT AN INLINE COMMAND. Founder standing rule: terminal
# windows run on his machine, never in the assistant's pane, because the pane
# throws permission prompts that stop the assistant monitoring anything. And
# `osascript -e 'do script "..."'` with a long inline string is where quoting
# breaks; a file has no quoting to get wrong.
#
# Usage: scripts/local/open_run_tail.sh <path-to-run-log>
set -u
LOG="${1:-}"
if [ -z "$LOG" ]; then
  echo "usage: $0 <path-to-run-log>" >&2
  exit 2
fi
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cat > /tmp/cdsfl_tail_cmd.sh <<INNER
cd "$REPO"
echo "CDSFL live run — tailing:"
echo "  $LOG"
echo
tail -n 40 -F "$LOG"
INNER
chmod +x /tmp/cdsfl_tail_cmd.sh
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    do script "/tmp/cdsfl_tail_cmd.sh"
end tell
APPLESCRIPT
