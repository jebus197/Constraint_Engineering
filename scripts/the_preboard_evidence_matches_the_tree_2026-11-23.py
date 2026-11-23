#!/usr/bin/env python3
"""A pre-board run describes the bytes that existed when it ran. Entry B211.

WHY THIS EXISTS, MEASURED. On 2026-11-22 the batch-3 commit board refused after
**2839.77 s = 47 min 19 s** on
`bench/tests/test_the_spoken_copy_is_not_older_than_its_record_2026-11-13.py`.
That guard was ALREADY in the deciding set and had ALREADY passed: the 64-guard
pre-board run returned 2116 passed, a single sentence was then reworded in the
task list, only the task-list guards were re-run, and the board was launched on
a tree the evidence no longer described. **The refusal cost 47 min 19 s; the
repair took 0.81 s.**

IT IS NOT A ONE-OFF, WHICH IS THE ARGUMENT FOR A MECHANISM RATHER THAN A RULE.
The same ordering failure occurred **4 times in 1 session**: once before it was
named, once in the batch that raised it as B211, and twice during the state
save, which edits ONBOARDING and RECOVERY and so re-stales the spoken report.
A discipline that is written down and then broken within hours is a discipline
that needs a checker.

WHAT IT COMPARES, AND WHY CONTENT AND NOT TIME. `--record` stores a digest of
the STAGED CONTENT at the moment a pre-board run passed. The default mode
recomputes that digest and reports whether the index has moved since. **An
mtime comparison was considered and rejected in B211's own falsifier: a tool
that rewrites a staged file without changing it would defeat a timestamp.** The
digest is taken from `git diff --cached --binary`, which is a function of HEAD
and the index only, so it is stable for an unchanged index and moves for any
staged edit including a mode change.

★ IT REPORTS. IT DOES NOT REFUSE, AND THAT IS DELIBERATE.
`feedback_a_false_positive_can_be_why_a_rule_is_unenforced_2026-11-02` records
that a semantic false positive is exactly how a rule ends up switched off. This
ships as a reported line in the same shape as the gate's panel line, which
falls open on every failure path. Escalating it to a refusal is a separate
decision, and the evidence for it is a record of the line being ignored.

★ EVERY FAILURE PATH FALLS OPEN. No digest, no evidence file, no git, a
corrupt record: all return OK with a stated reason. The cost of a false
"stale" is a commit refused for nothing; the cost of a false "fresh" is the
status quo, which is a 47-minute board. The asymmetry is why it fails open.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys

#: UNVERSIONED by design: it describes THIS checkout's index at a moment, and
#: committing it would make it a claim about every clone. `.cdsfl_tmp/` is
#: already the project's home for such records (the pre-commit duration ledger
#: lives there and is likewise untracked).
EVIDENCE = pathlib.Path(".cdsfl_tmp") / "preboard_evidence.json"

#: ★ THE STAGE-0 SNAPSHOT, ADDED 2026-11-23 AFTER THE FIRST LIVE USE REPORTED A
#: FALSE POSITIVE ON 4 OF 4 COMMITS -- including ones where the evidence was
#: recorded seconds before `git commit` with nothing touched in between.
#:
#: THE CAUSE, MEASURED, AND MY FIRST ATTEMPT TO FALSIFY IT WAS VACUOUS. The
#: gate REPAIRS and then RE-STAGES its own repairs before the reporting line
#: runs: the memory-ledger refresh rewrites `resources/MEMORY_EXCLUSIONS.md`
#: and leaves it UNSTAGED -- at which point the digest is still unchanged --
#: and a later stage stages everything, which moves it. Driven: a staged stale
#: ledger digests f16746db6bb17a37, survives the refresh unchanged, and becomes
#: 072e2b9d6a60440a once the repairs are re-staged. **An earlier run of this
#: same experiment showed NO movement and appeared to refute the diagnosis; it
#: was exercising the repair on an ALREADY-REPAIRED tree, so nothing could
#: move. A falsifier run on an already-satisfied precondition proves nothing.**
#:
#: SO THE COMPARISON HAS TO BE LIKE WITH LIKE: the evidence describes the index
#: AS THE OPERATOR LEFT IT, and that is what must be compared, not the index
#: after the gate has edited and re-staged on its own account. `--snapshot`,
#: called at the gate's stage 0 before any repair, records that index. When a
#: snapshot is present the verdict uses it; with none it falls back to the live
#: index, which is the standalone behaviour.
SNAPSHOT = pathlib.Path(".cdsfl_tmp") / "preboard_snapshot.json"


def _git(*args: str) -> "tuple[int, str]":
    """(exit code, stdout). Never raises: a missing git is a fall-open."""
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True,
                           timeout=120)
        return r.returncode, r.stdout
    except Exception:                                        # noqa: BLE001
        return 1, ""


def staged_digest(repo: pathlib.Path) -> "str | None":
    """A digest of the STAGED CONTENT, or None if it cannot be computed.

    `git diff --cached --binary` is a function of HEAD and the index alone. It
    moves for any staged change -- content, mode, addition or removal -- and
    holds still for an unchanged index, which is exactly the predicate B211
    needs. It is READ-ONLY: unlike `git write-tree` it creates no object.
    """
    code, out = _git("-C", str(repo), "diff", "--cached", "--binary")
    if code != 0:
        return None
    names_code, names = _git("-C", str(repo), "diff", "--cached", "--name-only")
    if names_code != 0:
        return None
    # The name list is folded in so that staging an EMPTY change -- a file
    # added with identical content -- still moves the digest.
    h = hashlib.sha256()
    h.update(out.encode("utf-8", "replace"))
    h.update(b"\x00--names--\x00")
    h.update(names.encode("utf-8", "replace"))
    return h.hexdigest()


def record(repo: pathlib.Path, guards: int, result: str) -> "dict | None":
    d = staged_digest(repo)
    if d is None:
        return None
    rec = {"digest": d, "guards": guards, "result": result,
           "staged": len([x for x in _git("-C", str(repo), "diff", "--cached",
                                          "--name-only")[1].split("\n") if x])}
    try:
        (repo / EVIDENCE).parent.mkdir(parents=True, exist_ok=True)
        (repo / EVIDENCE).write_text(json.dumps(rec, indent=1), encoding="utf-8")
    except Exception:                                        # noqa: BLE001
        return None
    return rec


def _board_is_alive(snap: dict) -> bool:
    """Is the gate process that wrote this snapshot still running?

    A snapshot is BOARD-SCOPED: it records the index as the operator left it at
    stage 0 so the gate's own later re-staging cannot be read as an operator
    edit. Once that board is over the snapshot describes nothing, and honouring
    it masks every subsequent edit.

    Fails toward NOT alive -- see the polarity note in `verdict`.
    """
    pid = snap.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        return False                 # old or hand-written snapshot: leftover
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False                 # the board is over
    except PermissionError:
        return True                  # alive, owned by someone else
    except OSError:
        return False
    return True


def verdict(repo: pathlib.Path) -> "tuple[str, str]":
    """(state, one-line reason). state is FRESH, STALE or UNKNOWN.

    UNKNOWN is a fall-open and is returned for every condition this cannot
    decide. It is never STALE on a doubt.
    """
    p = repo / EVIDENCE
    if not p.is_file():
        return "UNKNOWN", ("no pre-board evidence recorded; run the deciding "
                           "set and record it with --record")
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except Exception:                                        # noqa: BLE001
        return "UNKNOWN", "the evidence record is unreadable; ignoring it"
    was = rec.get("digest")
    if not isinstance(was, str) or not was:
        return "UNKNOWN", "the evidence record carries no digest"

    #: PREFER THE STAGE-0 SNAPSHOT over the live index. See SNAPSHOT above:
    #: inside the gate the live index has already been moved by the gate's own
    #: repair-and-re-stage, so comparing against it accuses the operator of an
    #: edit the GATE made. The snapshot is the index as the operator left it.
    #: ★ AND ONLY WHILE THE BOARD THAT WROTE IT IS STILL ALIVE. Added
    #: 2026-11-23 after the repair above was found to MASK a genuine operator
    #: edit in live use -- the mirror image of the defect it fixed, on the same
    #: day. The snapshot and the evidence were written in the same minute with
    #: IDENTICAL digests, so the comparison became a self-comparison that can
    #: never disagree, and 4 files staged afterwards were invisible.
    #:
    #: `test_it_does_not_mask_an_operator_edit` passed throughout, because it
    #: fixes the order record -> operator edits -> gate snapshots, where the
    #: snapshot captures the edit. Live hit the OTHER order: record -> gate
    #: snapshots -> operator edits. The test covered 1 order; both occur.
    #:
    #: A SNAPSHOT IS BOARD-SCOPED STATE, so it is honoured only while that
    #: board's process lives. `--clear-snapshot` existed for this and was
    #: WIRED TO NO CALLER, which is `additive-standard`'s symmetric form: an
    #: addition nothing reaches is not additive. It is wired now as hygiene;
    #: the pid check is what makes this CORRECT, because a board killed with
    #: SIGKILL runs no exit handler.
    #:
    #: POLARITY, STATED: this checker REPORTS and never refuses, so a false
    #: STALE costs 1 confusing line while a false FRESH costs a board of about
    #: 31 minutes run on evidence that does not describe the tree. It therefore
    #: fails TOWARD the live index: a snapshot with no pid, or an unreadable
    #: one, is treated as a leftover.
    #:
    #: RESIDUAL RISK, NAMED: pid reuse could make a finished board look alive,
    #: masking for at most 1 board -- no worse than the behaviour being fixed.
    now, source = None, "the live index"
    sp = repo / SNAPSHOT
    if sp.is_file():
        try:
            snap = json.loads(sp.read_text(encoding="utf-8"))
            cand = snap.get("digest")
            if isinstance(cand, str) and cand and _board_is_alive(snap):
                now, source = cand, "the stage-0 snapshot"
        except Exception:                                    # noqa: BLE001
            now = None                       # falls through to the live index
    if now is None:
        now = staged_digest(repo)
        source = "the live index"
    if now is None:
        return "UNKNOWN", "the staged digest could not be computed"
    if now == was:
        return "FRESH", (f"{source} is unchanged since {rec.get('guards', '?')} "
                         f"guard(s) ran: {rec.get('result', 'no result recorded')}")
    #: NAME THE COMPARISON SOURCE. A STALE line that does not say what it
    #: compared against cannot tell the operator whether the GATE moved the
    #: index or they did -- and the 2 call for opposite responses. Added
    #: 2026-11-23 when a test asserting the fallback had nothing to assert on.
    return "STALE", (
        f"THE INDEX HAS MOVED, measured against {source}, since the "
        f"pre-board run of "
        f"{rec.get('guards', '?')} guard(s). That run describes bytes that are "
        f"no longer staged, so it is not evidence about what is being "
        f"committed. Entry B211: this exact gap cost a 47 min 19 s refusal on "
        f"2026-11-22, on a guard already in the set and already passing. "
        f"Re-derive and re-run, or commit knowing the evidence is stale.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", action="store_true",
                    help="store the current staged digest as the evidence")
    ap.add_argument("--snapshot", action="store_true",
                    help="record the index AS IT IS NOW, for the gate's stage 0, "
                         "so a later check compares like with like")
    ap.add_argument("--clear-snapshot", action="store_true",
                    help="remove the stage-0 snapshot")
    ap.add_argument("--guards", type=int, default=0,
                    help="how many guards the pre-board run executed")
    ap.add_argument("--result", default="",
                    help="the run's own summary line")
    ap.add_argument("--quiet", action="store_true",
                    help="print 1 line only, for the gate")
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    repo = pathlib.Path(a.repo).resolve()

    if a.clear_snapshot:
        try:
            (repo / SNAPSHOT).unlink(missing_ok=True)
        except Exception as exc:                             # noqa: BLE001
            #: ★ A FAILED DELETION MUST LEAVE A TRACE. Swallowed, it leaves a
            #: STALE SNAPSHOT behind -- the mirror-image defect this file has
            #: a test against -- and the next verdict would compare fresh
            #: evidence to an old index. Caught 2026-11-23 by the FULL suite,
            #: which the commit board's 6th of it never runs.
            print(f"preboard-snapshot: could NOT remove {SNAPSHOT}: {exc}. "
                  f"A stale snapshot may now outlive its evidence; delete it "
                  f"by hand before trusting the next verdict.", file=sys.stderr)
        return 0

    if a.snapshot:
        d = staged_digest(repo)
        if d is None:
            return 0                      # falls open: no snapshot, no claim
        try:
            (repo / SNAPSHOT).parent.mkdir(parents=True, exist_ok=True)
            (repo / SNAPSHOT).write_text(
                json.dumps({"digest": d, "pid": os.getppid()}),
                                         encoding="utf-8")
        except Exception:                                    # noqa: BLE001
            return 0
        if not a.quiet:
            print(f"preboard-snapshot: stage-0 index digest {d[:12]}")
        return 0

    if a.record:
        #: A NEW RECORD INVALIDATES ANY OLD SNAPSHOT. Without this a snapshot
        #: left by a previous commit attempt would be compared against fresh
        #: evidence, which is the stale-verdict defect in mirror image.
        try:
            (repo / SNAPSHOT).unlink(missing_ok=True)
        except Exception as exc:                             # noqa: BLE001
            #: SAME REASON AS `--clear-snapshot` ABOVE: silence here is what
            #: lets a previous attempt's snapshot be compared against new
            #: evidence. Reported, not swallowed.
            print(f"preboard-evidence: could NOT clear the old snapshot "
                  f"{SNAPSHOT}: {exc}. The verdict after this may compare new "
                  f"evidence against a STALE index.", file=sys.stderr)
        rec = record(repo, a.guards, a.result)
        if rec is None:
            print("preboard-evidence: NOT recorded (no digest); nothing is "
                  "claimed", file=sys.stderr)
            return 0                      # falls open: recording is best-effort
        print(f"preboard-evidence: recorded {rec['staged']} staged file(s), "
              f"{rec['guards']} guard(s), digest {rec['digest'][:12]}")
        return 0

    state, why = verdict(repo)
    if a.quiet:
        print(f"preboard evidence: {state} — {why}")
    else:
        print("=" * 74)
        print("DOES THE PRE-BOARD EVIDENCE DESCRIBE THE TREE BEING COMMITTED?")
        print("=" * 74)
        print(f"  evidence file : {EVIDENCE}")
        print(f"  verdict       : {state}")
        print(f"  because       : {why}")
        if state == "STALE":
            print()
            print("  THIS DOES NOT REFUSE THE COMMIT. It is reported, because a")
            print("  semantic false positive is how a rule gets switched off --")
            print("  see feedback_a_false_positive_can_be_why_a_rule_is_unenforced.")
    #: EXIT 0 ON EVERY PATH. A non-zero exit here would make the gate's
    #: `|| true` the only thing standing between a false positive and a
    #: refused commit, and this ships as a REPORT.
    return 0


if __name__ == "__main__":
    sys.exit(main())
