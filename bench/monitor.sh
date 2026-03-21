#!/usr/bin/env bash
# =============================================================================
# CDSFL Round-Robin Test Monitor — Live Activity Window
#
# Usage:
#   ./bench/monitor.sh                  # tail the latest log file
#   ./bench/monitor.sh --status         # show current status summary
#   ./bench/monitor.sh --follow FILE    # tail a specific log file
#
# To run the test with logging (recommended):
#   python3 bench/run_round_robin.py --smoke \
#       --log-file bench/logs/smoke_$(date +%Y%m%d_%H%M%S).log
#
#   python3 bench/run_round_robin.py \
#       --log-file bench/logs/full_$(date +%Y%m%d_%H%M%S).log
#
# Press Ctrl+C to stop monitoring (the test continues separately).
# =============================================================================

set -euo pipefail

BENCH_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$BENCH_DIR/results/round_robin"
LOGS_DIR="$BENCH_DIR/logs"

# Colours
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

header() {
    clear 2>/dev/null || true
    echo ""
    echo -e "${BOLD}================================================================${RESET}"
    echo -e "${BOLD}  CDSFL ROUND-ROBIN DISTRIBUTED COMPUTE TEST${RESET}"
    echo -e "${BOLD}  Monitor started: $(date '+%Y-%m-%d %H:%M:%S')${RESET}"
    echo -e "${BOLD}  Topology: Opus 4.6 (orchestrator) | Gemini 3 | Codex 5.3${RESET}"
    echo -e "${BOLD}================================================================${RESET}"
    echo ""
}

show_status() {
    echo -e "${BOLD}--- STATUS SUMMARY ---${RESET}"
    echo ""

    # Cost ledger
    if [ -f "$RESULTS_DIR/cost_ledger.json" ]; then
        echo -e "${CYAN}[COST]${RESET} $(python3 -c "
import json, sys
try:
    d = json.load(open('$RESULTS_DIR/cost_ledger.json'))
    providers = ', '.join(f'{k}: \${v:.4f}' for k, v in d.get('by_provider', {}).items())
    print(f\"Total: \${d['total_usd']:.4f} / \${d['cap_usd']:.2f} | {providers}\")
except: print('unavailable')
" 2>/dev/null)"
    else
        echo -e "${DIM}[COST] No cost ledger yet${RESET}"
    fi

    # Checkpoint
    if [ -f "$RESULTS_DIR/checkpoint.json" ]; then
        echo -e "${GREEN}[CHECKPOINT]${RESET} $(python3 -c "
import json, sys
try:
    d = json.load(open('$RESULTS_DIR/checkpoint.json'))
    completed = d.get('completed', {})
    n = len(completed)
    tasks = ', '.join(sorted(completed.keys()))
    print(f'{n} task(s) completed: {tasks}')
except: print('unavailable')
" 2>/dev/null)"
    else
        echo -e "${DIM}[CHECKPOINT] No checkpoint yet${RESET}"
    fi

    # Per-task results
    echo ""
    result_files=$(ls "$RESULTS_DIR"/ft-*_result.json 2>/dev/null || true)
    if [ -n "$result_files" ]; then
        echo -e "${BOLD}--- TASK RESULTS ---${RESET}"
        for f in $result_files; do
            python3 -c "
import json, sys
try:
    d = json.load(open('$f'))
    tid = d.get('task_id', '?')
    status = d.get('status', '?')
    rounds = d.get('rounds_completed', 0)
    hard = d.get('total_unique_hard_findings', 0)
    chain = 'VALID' if d.get('chain_valid', False) else 'BROKEN'
    merkle = d.get('merkle_root', '')[:16]
    colour = '\033[0;32m' if status == 'RESOLVED' else '\033[0;33m'
    print(f'  {colour}{tid}\033[0m: {status} | {rounds} rounds | {hard} HARD findings | chain: {chain} | merkle: {merkle}...')
except Exception as e:
    print(f'  \033[0;31m{f}: error reading\033[0m')
" 2>/dev/null
        done
    else
        echo -e "${DIM}No task results yet${RESET}"
    fi

    # Verification chain integrity
    if [ -f "$RESULTS_DIR/round_robin_results.json" ]; then
        echo ""
        echo -e "${BOLD}--- AGGREGATE METRICS ---${RESET}"
        python3 -c "
import json
try:
    d = json.load(open('$RESULTS_DIR/round_robin_results.json'))
    m = d.get('metrics', {})
    print(f'  Tasks: {m.get(\"total_tasks\", 0)} | Resolved: {m.get(\"tasks_resolved\", 0)} | Deferred: {m.get(\"tasks_deferred\", 0)}')
    print(f'  Total unique HARD findings: {m.get(\"total_unique_hard_findings\", 0)}')
    print(f'  Avg rounds/task: {m.get(\"avg_rounds_per_task\", 0)}')
    print(f'  Avg HARD/task: {m.get(\"avg_unique_hard_per_task\", 0)}')
except: pass
" 2>/dev/null
    fi

    # Deferred items
    if [ -f "$RESULTS_DIR/deferred_items.json" ]; then
        deferred_count=$(python3 -c "
import json
try:
    d = json.load(open('$RESULTS_DIR/deferred_items.json'))
    print(len(d))
except: print(0)
" 2>/dev/null)
        if [ "$deferred_count" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}[DEFERRED]${RESET} $deferred_count task(s) with deferred items — see deferred_items.json"
        fi
    fi

    echo ""
}

find_latest_log() {
    # Check for log files in logs dir
    local latest
    latest=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -1)
    if [ -n "$latest" ]; then
        echo "$latest"
        return
    fi
    # Fall back to smoke test output in tmp
    local smoke="/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/fb25320f-c06e-4af5-a224-c160c7adef6b/tasks/b1ryto9xa.output"
    if [ -f "$smoke" ]; then
        echo "$smoke"
        return
    fi
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

MODE="${1:---tail}"

case "$MODE" in
    --status|-s)
        header
        show_status
        ;;

    --follow|-f)
        FILE="${2:-}"
        if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
            echo -e "${RED}Usage: $0 --follow <log-file>${RESET}"
            exit 1
        fi
        header
        show_status
        echo -e "${CYAN}[MONITOR]${RESET} Tailing: $FILE"
        echo -e "${DIM}Press Ctrl+C to stop${RESET}"
        echo ""
        tail -f "$FILE" | while IFS= read -r line; do
            echo -e "${DIM}[$(date '+%H:%M:%S')]${RESET} $line"
        done
        ;;

    --tail|*)
        LOG=$(find_latest_log)
        if [ -z "$LOG" ]; then
            header
            show_status
            echo -e "${YELLOW}[MONITOR]${RESET} No active log file found."
            echo -e "Start a test with logging (auto-log is now default):"
            echo -e "  ${CYAN}python3 bench/run_round_robin.py --smoke${RESET}"
            echo -e "  ${CYAN}python3 bench/run_round_robin.py${RESET}"
            exit 0
        fi
        header
        show_status
        echo -e "${CYAN}[MONITOR]${RESET} Tailing: $LOG"
        echo -e "${DIM}Press Ctrl+C to stop${RESET}"
        echo ""
        tail -f "$LOG" | while IFS= read -r line; do
            # Colour-code by content
            if echo "$line" | grep -qE "FAILED|ERROR|FATAL"; then
                echo -e "${RED}[$(date '+%H:%M:%S')]${RESET} ${RED}$line${RESET}"
            elif echo "$line" | grep -qE "WARN|budget.*exhaust"; then
                echo -e "${YELLOW}[$(date '+%H:%M:%S')]${RESET} ${YELLOW}$line${RESET}"
            elif echo "$line" | grep -qE "done|COMPLETE|RESOLVED|chain.*valid"; then
                echo -e "${GREEN}[$(date '+%H:%M:%S')]${RESET} ${GREEN}$line${RESET}"
            elif echo "$line" | grep -qE "calling|starting|generating|telemetry"; then
                echo -e "${CYAN}[$(date '+%H:%M:%S')]${RESET} ${CYAN}$line${RESET}"
            elif echo "$line" | grep -qE "budget|Budget|Remaining"; then
                echo -e "${DIM}[$(date '+%H:%M:%S')]${RESET} $line"
            else
                echo -e "${DIM}[$(date '+%H:%M:%S')]${RESET} $line"
            fi
        done
        ;;
esac
