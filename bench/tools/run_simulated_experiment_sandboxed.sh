#!/bin/bash
# Run a simulated experiment against a DISPOSABLE COPY of the repository.
#
# Founder ruling 2026-09-01: "A simulation is exactly that. It runs in its own
# sandbox with a copy of the current/most recent repo to work on, not the live
# repo itself."
#
# WHY THIS AND NOT A read-only TARGET. Making the target file read-only was
# measured on 2026-09-01 and blocks only three of four write routes: python
# open('w'), a shell redirect and `git checkout --` are all refused, but
# `sed -i` UNLINKS AND RECREATES the file, so it rewrites the content anyway.
# Permissions on a file cannot protect it when the directory is writable.
#
# WHY RUNNING FROM INSIDE THE COPY IS THE WHOLE FIX. Both harnesses derive their
# root from __file__ (reference_runner_v2.py:154, run_simulated_experiment.py:30)
# and repo_relative_target normalises every target against that root. Launching
# the runner from inside the worktree therefore redirects the target, the panel's
# inherited working directory and every derived path in one move, with no new
# path plumbing to get wrong.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

DIRTY=$(git status --porcelain -- . ':(exclude)bench/logs')
if [ -n "$DIRTY" ]; then
  echo "REFUSING: the working tree is dirty, so a HEAD worktree would not be a" >&2
  echo "copy of what you are actually running. Commit or stash first:" >&2
  echo "$DIRTY" >&2
  exit 2
fi

SANDBOX="$(mktemp -d -t cdsfl_sim)"
WT="$SANDBOX/repo"
echo "    sandbox  $WT"
# PATHSPEC STAGING, NOT A PLAIN WORKTREE (founder ruling 2026-09-01).
#
# THE BLINDING WAS DEFEATED BY CONSTRUCTION. A plain `git worktree add` carries
# every TRACKED file, and bench/logs holds the archived reports. Measured on this
# repository: a reviewer's sandbox exposed 149 run directories, 54 report JSONs,
# 325 experimental_notes files and 29,899 severity values -- including exp45's 12
# criticals WITH their exact severities. The agents are armed with Bash, Read,
# Grep and Glob (sim_panel_agents.py:104), so the answers to the experiment were
# sitting in the reviewers' working directory, readable.
#
# Every sim-versus-real severity comparison made before this was measured through
# that hole, so the -0.132 offset may be an anti-anchoring artefact rather than a
# calibration gap. Found by CC2 in panel review; it cited this script's own
# comment ("THE WHOLE ARCHIVE CAME WITH THE WORKTREE") as the evidence.
#
# Sparse-checkout excludes the answer surfaces while keeping everything the run
# needs. Verified: run directories 149 -> 0, reports 54 -> 0, notes 325 -> 0,
# severities 29,899 -> 0, with target, runner, directives and launcher all
# present and 455 python files checked out.
git worktree add --no-checkout --detach "$WT" HEAD >/dev/null 2>&1 || {
  echo "FATAL: could not create the sandbox worktree" >&2; exit 1; }
GITDIR="$(git -C "$WT" rev-parse --git-dir)"
git -C "$WT" sparse-checkout init --no-cone >/dev/null 2>&1
cat > "$GITDIR/info/sparse-checkout" <<'SPARSE'
/*
!/bench/logs/
!/bench/results/
!/experimental_notes/
SPARSE
git -C "$WT" checkout HEAD >/dev/null 2>&1 || {
  echo "FATAL: sparse checkout failed" >&2; exit 1; }
# The runner WRITES its run directory under bench/logs, which the exclusion has
# just removed. Recreate it empty: the run needs the directory, never its history.
mkdir -p "$WT/bench/logs"

# REFUSE TO RUN IF THE BLINDING DID NOT TAKE. A sandbox that silently keeps the
# answers is worse than no sandbox, because the resulting numbers look clean.
LEAKED=$(find "$WT/bench/logs" "$WT/experimental_notes" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$LEAKED" != "0" ]; then
  echo "FATAL: blinding failed -- $LEAKED answer-surface file(s) present in the sandbox" >&2
  git worktree remove --force "$WT" >/dev/null 2>&1; exit 1
fi
echo "    blinded: 0 archived reports, 0 notes reachable by the panel"

RC=0
( cd "$WT" && python3 bench/tools/run_simulated_experiment.py "$@" ) || RC=$?

# EXTRACT BEFORE TEARDOWN (founder, 2026-08-30: "sandboxes should be deleted
# after we are done with them and after you have extracted fixes, not before").
# TWO DEFECTS, both found 2026-09-01 before this ever ran to completion.
#
# 1. THE TRAILING SLASH. `for d in .../*/` yields paths ending in "/", and
#    `cp -R src/ dest/` copies the CONTENTS of src into dest rather than the
#    directory itself. Measured: report.json landed directly in dest/ instead of
#    dest/run_a/. Across a whole logs tree that scatters every run's files loose
#    into bench/logs, colliding on every same-named file, last one winning.
#
# 2. THE WHOLE ARCHIVE CAME WITH THE WORKTREE. bench/logs holds TRACKED report
#    and runner_state files, so a HEAD worktree checks out every archived run --
#    148 directories here. Copying them all back is at best 148 pointless
#    overwrites and at worst the scatter above applied to the entire archive.
#    Only directories the RUN created are new; everything else already exists
#    canonically and must be left alone.
COPIED=0
SKIPPED=0
if [ -d "$WT/bench/logs" ]; then
  for d in "$WT"/bench/logs/*/; do
    [ -d "$d" ] || continue
    name="$(basename "${d%/}")"
    if [ -e "$REPO/bench/logs/$name" ]; then
      SKIPPED=$((SKIPPED+1))
      continue
    fi
    cp -R "${d%/}" "$REPO/bench/logs/" && COPIED=$((COPIED+1))
  done
fi
echo "    extracted $COPIED new run director(ies); left $SKIPPED existing one(s) alone"

if [ "$RC" -eq 0 ]; then
  git worktree remove --force "$WT" >/dev/null 2>&1 || true
  rm -rf "$SANDBOX"
  echo "    sandbox removed"
else
  echo "    sandbox KEPT for inspection (exit $RC): $WT" >&2
fi
exit "$RC"
