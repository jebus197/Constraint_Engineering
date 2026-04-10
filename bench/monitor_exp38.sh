#!/bin/bash
# Monitor Experiment 38 log — refresh every 60 seconds
# Usage: bash bench/monitor_exp38.sh
# Or: tail -f bench/logs/exp38_ouroboros/runner.log

LOG_DIR="bench/logs/exp38_ouroboros"
LOG_FILE="${LOG_DIR}/runner.log"

echo "=== Experiment 38 Monitor ==="
echo "Log: $(pwd)/${LOG_FILE}"
echo "Press Ctrl+C to stop monitoring"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "Waiting for experiment to start..."
    while [ ! -f "$LOG_FILE" ]; do
        sleep 2
    done
fi

tail -f "$LOG_FILE"
