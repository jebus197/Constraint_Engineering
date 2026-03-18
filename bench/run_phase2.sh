#!/usr/bin/env bash
# Phase 2 orchestrator — designed for unattended overnight execution.
#
# Usage:
#   # Foreground (watch progress)
#   bash bench/run_phase2.sh
#
#   # Background (overnight)
#   nohup bash bench/run_phase2.sh > bench/results/phase2/overnight.log 2>&1 &
#
#   # Resume after crash
#   nohup bash bench/run_phase2.sh --resume > bench/results/phase2/overnight.log 2>&1 &
#
#   # Pilot only (3 tasks, one model)
#   bash bench/run_phase2.sh --pilot

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$REPO_DIR/.env"
RESULTS_DIR="$SCRIPT_DIR/results/phase2"

echo "============================================================"
echo "CDSFL Phase 2 — Frontier Test"
echo "Started: $(date -Iseconds)"
echo "============================================================"
echo ""

# Source environment
if [ -f "$ENV_FILE" ]; then
    echo "[env] Loading $ENV_FILE"
    source "$ENV_FILE"
else
    echo "[env] ERROR: $ENV_FILE not found"
    exit 1
fi

# Create output directory
mkdir -p "$RESULTS_DIR"

# Pass through all arguments
cd "$SCRIPT_DIR"
echo "[run] python3 run_phase2.py $@"
echo ""

python3 run_phase2.py "$@"

EXIT_CODE=$?

echo ""
echo "============================================================"
echo "Phase 2 finished at: $(date -Iseconds)"
echo "Exit code: $EXIT_CODE"
if [ -f "$RESULTS_DIR/cost_ledger.json" ]; then
    echo "Cost summary:"
    python3 -c "import json; d=json.load(open('$RESULTS_DIR/cost_ledger.json')); print(f'  Total: \${d[\"total_usd\"]:.4f} / \${d[\"cap_usd\"]:.2f} (\${d[\"remaining_usd\"]:.4f} remaining)')"
fi
echo "============================================================"

exit $EXIT_CODE
