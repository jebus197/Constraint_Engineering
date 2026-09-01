#!/bin/bash
# Watch the canonical repo for mutation BY A PANEL AGENT during a run.
#
# 2026-09-01. Panel agents inherit the repo as cwd for code experiments, by
# design (reference_runner_v2.py:9836 — "unset for code runs, where the panel
# legitimately needs this repo"). Reading it is intended. Nothing stops a write.
# Measured this night: bench/dm/_memory.py, the experiment's own target, was
# written at 01:17:34 during a run, and an agent reported having run
# `git checkout --` on it. The filesystem corroborated the account.
#
# This restores any mutated TRACKED file from HEAD and records what happened,
# so an integrity failure is loud and recovered instead of silent. bench/logs is
# excluded: the run writes its artefacts there legitimately.
cd "$(dirname "$0")/../.." || exit 1
REC="${1:-/tmp/repo_integrity.log}"

# REFUSE TO START ON A DIRTY TREE. This watcher restores with `git checkout --`,
# which cannot tell an agent's scribble from the operator's unfinished work. If
# the tree is dirty when the run begins, every uncommitted change is at risk of
# being reverted by the guard meant to protect the run. Commit or stash first.
DIRTY_AT_START=$(git status --porcelain -- . ':(exclude)bench/logs')
if [ -n "$DIRTY_AT_START" ]; then
  echo "REFUSING TO WATCH: the working tree is dirty. This guard restores from" >&2
  echo "HEAD and would discard the following. Commit or stash, then re-run:" >&2
  echo "$DIRTY_AT_START" >&2
  exit 2
fi
while true; do
  DIRTY=$(git status --porcelain -- . ':(exclude)bench/logs' | head -40)
  if [ -n "$DIRTY" ]; then
    echo "=== $(date -Iseconds) REPO MUTATED DURING RUN ===" >> "$REC"
    echo "$DIRTY" >> "$REC"
    git diff -- . ':(exclude)bench/logs' >> "$REC" 2>&1
    git checkout -- . 2>>"$REC"
    echo "--- restored from HEAD ---" >> "$REC"
    echo "REPO MUTATION DETECTED AND RESTORED — see $REC"
  fi
  sleep 3
done
