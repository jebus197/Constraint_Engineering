#!/usr/bin/env python3
"""Restore after a compaction at the FIRST TASK BOUNDARY, not the first turn end.

HIS DESIGN CORRECTION, 2026-10-12, and it overrides the proposal made an hour earlier:
*"it's probably not heathy to interrupt a task that was running immediately before
compaction and that continues after compaction completes. But usually automated/unattended
work I assign you has several tasks, so it would need to fire at a safe point immediately
after the first task in any given task list completes after a compaction. Then it would
need to go back, and check that last before continuing with the rest of the work."*

He is right and the measurement agrees. A turn-end trigger would have fired 0.91 min after
the 2026-10-11 compaction -- in the middle of item 14, with the tree dirty and the task
half done. The FIRST COMMIT after that compaction landed at 16.89 min, exactly when item 14
completed, with the tree clean by construction.

WHY A COMMIT IS THE TASK BOUNDARY, and it is not an approximation
-----------------------------------------------------------------
A commit is this project's own definition of a completed unit of work: `sv` commits, every
item of his work order ended in one, and the pre-commit board must pass before one exists.
So "a commit happened" means the tree is consistent, the guards ran, and no task is
half-applied. Measured over the 7 commits following the 2026-10-11 compaction, the first 4
are precisely his 4 work-order items. Nothing else in the session is both mechanical and
task-aligned: prose saying "item N done" is unreliable, and the task list's own file is
edited mid-task.

WHAT IT IS WORTH, MEASURED OVER 43 COMPACTIONS IN THIS SESSION'S TRANSCRIPT
---------------------------------------------------------------------------
This hook does NOT replace the `UserPromptSubmit` path; the two compose and the restore
fires on whichever comes first. So the comparison that matters is min(commit, message)
against message alone:

    median lag   55.22 min  ->  13.18 min
    p90          420.30 min ->  54.95 min
    max         1543.13 min -> 293.36 min
    strictly improved on 27 of 43, 0.6279, Wilson [0.4786, 0.7562], CP [0.4673, 0.7702]
    Wilcoxon one-sided p = 2.803e-06

And on the case he actually described -- UNATTENDED work, taken as the 32 compactions where
his next message was more than 30 minutes away -- the median wait falls from 88.57 min to
22.71 min, a median saving of 42.39 min, improved on 23 of 32, Wilson [0.5463, 0.8444],
Wilcoxon p = 1.351e-05, for a total of 112.00 hours of degraded work avoided.

HONESTLY BOUNDED. A commit trigger ALONE is NOT reliably better than waiting for him:
median 35.67 min against 55.22, but sooner in only 27 of 43 and Wilcoxon p = 0.2164, with a
worse maximum (2034.99 min against 1543.13). The gain comes from COMPOSING the two triggers,
not from replacing one with the other. Producer:
`scripts/the_task_boundary_restore_is_sooner_2026-10-12.py`.

IT BLOCKS THE STOP, DELIBERATELY, AND THAT IS THE "GO BACK AND CHECK" HALF
--------------------------------------------------------------------------
A Stop hook that exits 0 is silent: the restore would run and the assistant would carry on
from the summary regardless, which is the defect rather than the fix. Exiting 2 feeds the
restored context back and the turn continues -- so the task just committed gets re-verified
against the real project record BEFORE the rest of the list proceeds, which is what he asked
for. It fires ONCE PER COMPACTION: the restore writes `last_recovery`, after which
`_recovery_ran_after` is true and every later Stop returns 0.

ONE CODE PATH. Every predicate here is IMPORTED from `compaction_watch.py` -- the transcript
scan (`load_state_and_scan`, extracted for this purpose), `_recovery_ran_after`,
`_auto_restore`, `parse_transcript_ts`. None is reimplemented. On 2026-10-11 an extraction
reimplemented the founder's annotation predicate inline and admitted 2 markdown headings
from a saved web page as his words, hours after that lesson was recorded.

IT CANNOT TRAP THE SESSION. `stop_hook_active` exits immediately, so at most one refusal per
turn; the marker bounds it to one per compaction; and every failure path returns 0. A
recovery mechanism that can break the session it protects is worse than none.
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys

HOOKS = pathlib.Path(__file__).resolve().parent
#: The repository whose commits mark a task boundary and whose recovery script runs.
REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")


def _watch():
    """Import compaction_watch WITHOUT running its main(), which is __main__-guarded."""
    spec = importlib.util.spec_from_file_location(
        "compaction_watch", str(HOOKS / "compaction_watch.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["compaction_watch"] = mod
    spec.loader.exec_module(mod)
    return mod


def commits_since(iso_ts: str) -> list[str]:
    """Commits on any ref since that instant — the task boundaries that have passed.

    `--all` so a compaction during work on another branch still finds its boundary.
    Returns newest-last. An empty list means no task has completed yet, so this hook
    stays silent and the work in flight is not interrupted.
    """
    try:
        r = subprocess.run(
            ["git", "log", "--all", "--since", iso_ts,
             "--pretty=%h %s", "--reverse"],
            cwd=str(REPO), capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    if r.returncode != 0:
        return []
    return [ln for ln in (r.stdout or "").splitlines() if ln.strip()]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                      # never break a session on a bad payload

    # AT MOST ONE REFUSAL PER TURN. Claude Code sets this once a stop has already
    # been blocked, so this cannot loop.
    if payload.get("stop_hook_active"):
        return 0

    sid = str(payload.get("session_id") or "").replace("/", "_")[:128]
    tp = payload.get("transcript_path") or ""
    if not tp:
        return 0
    tpath = pathlib.Path(os.path.expanduser(tp))
    if not tpath.is_file():
        return 0

    try:
        W = _watch()
    except Exception:
        return 0                      # the shared predicates are unavailable; stay silent

    try:
        sf, st, newest = W.load_state_and_scan(tpath, sid)
    except Exception:
        return 0
    if not newest:
        return 0

    # ALREADY HANDLED — by a manual `rs`, or by the UserPromptSubmit path, or by an
    # earlier firing of this hook. The marker is SHARED, which is what makes
    # "once per compaction" hold across both triggers.
    #
    # `fired_for` IS SEPARATE FROM THE RESTORE'S SUCCESS, AND THE P-PASS FOUND WHY.
    # The first version gated only on `_recovery_ran_after`, which is written by
    # `cdsfl_recover.py` itself. So if the restore FAILED for any reason -- script
    # absent from the checkout, a timeout, a non-zero exit -- no marker was written
    # and this hook would fire again at the next stop, and the next, refusing ONE
    # STOP PER TURN INDEFINITELY. `stop_hook_active` bounds it to one refusal per
    # turn, so it could not hard-loop, but it would nag forever. Caught by
    # `test_it_fires_only_once_per_compaction` against a repo with no recovery
    # script -- which is exactly the production failure mode it models.
    #
    # The two facts are now recorded separately, which is the point: `fired_for`
    # says "the assistant has been told once", and `last_recovery` says "context
    # was actually restored". When the restore fails, this hook falls silent AND
    # the UserPromptSubmit alarm stays armed, because a restore is still owed.
    try:
        if (st.get("acknowledged") == newest
                or st.get("fired_for") == newest
                or W._recovery_ran_after(newest)):
            return 0
    except Exception:
        return 0

    # THE SAFE POINT. No commit since the compaction means no task has finished, so
    # the work in flight is left alone. This is his correction, in one condition.
    done = commits_since(newest)
    if not done:
        return 0

    # RECORD THE FIRING BEFORE RUNNING THE RESTORE, so a restore that dies cannot
    # leave this hook re-arming on every turn. Written first, deliberately.
    st["fired_for"] = newest
    try:
        sf.write_text(json.dumps(st))
    except Exception:
        pass

    try:
        restored = W._auto_restore(REPO)
    except Exception:
        restored = ("  AUTO-RESTORE could not be attempted at all. A restore is still "
                    "OWED: python3 scripts/cdsfl_recover.py --record-restore")

    when = None
    try:
        when = W.parse_transcript_ts(newest)
    except Exception:
        pass
    stamp = when.strftime("%Y-%m-%d %H:%M:%S %Z") if when else str(newest)

    listing = "\n".join(f"      {c}" for c in done[:12])
    more = f"\n      ... and {len(done) - 12} more" if len(done) > 12 else ""
    msg = (
        f"[compaction-task-boundary] A COMPACTION OCCURRED AT {stamp} AND A TASK HAS NOW "
        f"COMPLETED.\n"
        f"  The restore has been RUN automatically at this safe point — the commit below "
        f"means the tree is consistent and no task is half-applied.\n\n"
        f"  COMMIT(S) MADE SINCE THAT COMPACTION, i.e. the work done from a SUMMARY of the "
        f"project rather than the project:\n{listing}{more}\n\n"
        f"  BEFORE CONTINUING WITH THE REST OF THE WORK, do both of these, in order "
        f"(founder's instruction, 2026-10-12):\n"
        f"    1. GO BACK AND CHECK the task just completed above, against the restored "
        f"record below — re-run its guards and re-run any producer whose figures you "
        f"quoted, because those were produced without the real project state.\n"
        f"    2. THEN carry on with the remaining tasks in the list.\n\n"
        f"{restored}"
    )
    print(msg, file=sys.stderr)
    return 2                          # block the stop so the context actually lands


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)                   # a recovery hook must never fell the session
