#!/bin/sh
# ★ THE SWEEP THAT MUST RUN BEFORE A COMMIT, 2026-10-16.
#
# WHY THIS EXISTS. The citation guard has a repair mode and the project knows to
# run it. On 2026-10-16 it was run, the lesson "it must run after the LAST edit
# to a cited file and before the commit" was written into a commit message, and
# then the SAME omission happened again 40 minutes later because the next body
# of work shifted the runner again. A lesson recorded in prose is not a
# mechanism. This is the mechanism.
#
# It is a SCRIPT and not a git hook deliberately: a hook is invisible to review
# and would run for every commit in every checkout. This is invoked explicitly
# and its output is read.
#
# Free: reads and repairs local files, dispatches nothing, spends nothing.
set -e
cd "$(dirname "$0")/.."
# ★ EVERY STEP BELOW IS FATAL. `set -e` is the whole mechanism: on 2026-10-16
# this sweep was written, run, SEEN TO FAIL on an orphaned task marker, and the
# commit went out anyway, because the invocation was `sh sweep | tail` and a
# pipeline reports the exit status of `tail`. Run it as `sh scripts/...` with no
# pipe, or capture the status explicitly. A gate whose exit code is discarded is
# not a gate.
echo "== citation anchors =="
python3 scripts/citation_content_guard_2026-09-10.py --fix
python3 scripts/citation_content_guard_2026-09-10.py
echo "== task-list markers =="
# `set -e` at the top makes a non-zero exit here fail the sweep. The marker
# summary ASSERTS that its state counts sum to the entry total, so an entry
# whose marker has been orphaned -- by an edit that split its heading line, for
# instance -- fails here instead of reaching a commit.
python3 scripts/task_list_markers.py --summary
echo "== desktop mirror the founder reads =="
cp experimental_notes/CDSFL_MASTER_TASK_LIST.md "$HOME/Desktop/CDSFL_MASTER_TASK_LIST.md"
cmp -s experimental_notes/CDSFL_MASTER_TASK_LIST.md "$HOME/Desktop/CDSFL_MASTER_TASK_LIST.md" \
  && echo "  mirror byte-identical" || { echo "  MIRROR DIVERGED"; exit 1; }
echo "all clear"
