#!/bin/bash
# Experiment 38 launcher — ouroboros (self-review)
# Branch: exp38-experimental
# Date: 2026-04-11

set -e

cd /Users/georgejackson/Developer_Projects/Constraint_Engineering

echo "=== EXPERIMENT 38: OUROBOROS ==="
echo "Launched: $(date)"
echo "Branch: exp38-experimental"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Config: bench/exp38_config.json"
echo ""

python3 bench/reference_runner.py run \
    --test-article bench/reference_runner.py \
    --config bench/exp38_config.json \
    --experiment-name exp38_ouroboros \
    2>&1 | tee bench/logs/exp38_live_output.log
