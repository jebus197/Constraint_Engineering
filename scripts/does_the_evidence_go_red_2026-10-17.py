#!/usr/bin/env python3
"""Does a DONE entry's evidence FAIL when the fix it claims is undone?

TASK V9, proposed 2026-09-17 and APPROVED BY THE FOUNDER 2026-09-18: *"V9:
Approved."* Task V1 set 3 conditions on a DONE marker's evidence. 2 are
implemented and guarded -- the evidence must exist, and it must pass. The 3rd,
that undoing the fix makes that same evidence FAIL, was implemented nowhere.

WHY IT MATTERS. A test that stays green against its own reverted fix is
DECORATIVE: it shows the evidence file runs, not that it would notice the
absence of the thing the entry claims. R3 is the worked example -- its evidence
passed against a reverted fix on 2026-09-17 and a HUMAN noticed, not a
mechanism. This is the step the assistant has been performing by hand on every
repair; mechanising it is the point of V9.

HOW IT REVERTS THE FIX WITHOUT GUESSING. It does not try to undo a patch. For
entry X it finds the commit that introduced `task: X | state: DONE` into the
master task list -- that is the commit which CLAIMED the work -- and checks out
its PARENT, which is the tree as it stood before. The entry's CURRENT evidence
files are then copied into that old tree and run there. So today's test meets
yesterday's code, which is exactly the question V9 asks.

THE OUTCOMES, and the third is the one that makes this honest:

  DISCRIMINATES   the evidence FAILS on an assertion at the parent commit. The
                  test notices the fix is absent, which is what V9 requires.
  DECORATIVE      the evidence PASSES at the parent commit. It would not have
                  noticed the fix missing, so it is not evidence FOR the fix.
  INCONCLUSIVE    the evidence fails to COLLECT at the parent -- an import
                  error, a missing module, a syntax error. That is not
                  discrimination, it is the test being unable to run at all, and
                  counting it as a pass for V9 would be the same error as
                  counting a crashed check as a passing one.

MEASURED RATES ARE REPORTED WITH AN INTERVAL and the sample is named, because
running all 114 costs a worktree and a pytest invocation each and this machine
is a fixed resource.
"""
from __future__ import annotations

import argparse
import pathlib
import random
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
SCRATCH = pathlib.Path("/private/tmp/claude-501") / "v9_worktrees"


def _entries():
    sys.path.insert(0, str(REPO / "scripts"))
    import task_list_markers as T
    out = []
    for e in T.parse_entries(LIST):
        if getattr(e, "state", "") != "DONE":
            continue
        tests = [t for t in (getattr(e, "evidence", ()) or ())
                 if isinstance(t, str) and t.endswith(".py")
                 and (REPO / t).is_file()]
        if tests:
            out.append((e.ident, tests))
    return out


def _marker_is_committed(ident: str) -> bool:
    """Is this entry's DONE marker already in HEAD, or only in the working tree?

    THE DISTINCTION V9'S COVERAGE CHECK WAS MISSING, found 2026-10-29 by hitting
    it. `_closing_commit` locates the commit that INTRODUCED a DONE marker, by
    searching the task list's history for the marker text. For an entry marked
    DONE for the FIRST time that commit cannot exist until the commit writing
    the marker has landed -- so the check refused the very commit that would
    satisfy it, and the only escape offered was to bypass the whole hook.

    A marker that is not yet committed is NOT a blind spot in V9's coverage. It
    is a not-yet, and this module already draws exactly that distinction for a
    test that could not be collected: "has not noticed the fix missing -- it has
    failed to run", which is counted as INCONCLUSIVE rather than as a pass. The
    same honesty applies here, in the other direction: absence of a closing
    commit for an UNCOMMITTED marker is uninformative, while absence for a
    COMMITTED one is the real fault the check exists to catch.

    Returns False when HEAD cannot be read at all, which keeps a fresh clone or
    a detached state from being treated as "committed" and failing loudly for a
    reason that has nothing to do with the markers.
    """
    r = subprocess.run(
        ["git", "show", f"HEAD:{LIST.relative_to(REPO)}"],
        cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        return False
    return f"task: {ident} | state: DONE" in r.stdout


def _closing_commit(ident: str) -> str | None:
    r = subprocess.run(
        ["git", "log", "--format=%H", "-S", f"task: {ident} | state: DONE",
         "--", str(LIST.relative_to(REPO))],
        cwd=REPO, capture_output=True, text=True)
    shas = [s for s in r.stdout.split() if s]
    return shas[-1] if shas else None       # the EARLIEST such commit


def check(ident: str, tests: list, keep: bool = False) -> dict:
    sha = _closing_commit(ident)
    if not sha:
        return {"ident": ident, "outcome": "NO_CLOSING_COMMIT"}
    par = subprocess.run(["git", "rev-parse", f"{sha}^"], cwd=REPO,
                         capture_output=True, text=True).stdout.strip()
    if not par:
        return {"ident": ident, "outcome": "NO_PARENT", "closing": sha[:12]}
    wt = SCRATCH / f"{ident.replace('.', '_')}_{par[:8]}"
    if wt.exists():
        shutil.rmtree(wt, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    add = subprocess.run(["git", "worktree", "add", "-q", "--detach",
                          str(wt), par], cwd=REPO, capture_output=True, text=True)
    if add.returncode != 0:
        return {"ident": ident, "outcome": "WORKTREE_FAILED",
                "detail": add.stderr.strip()[:160]}
    try:
        copied = []
        for t in tests:
            dst = wt / t
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / t, dst)
            copied.append(t)
        r = subprocess.run([sys.executable, "-m", "pytest", *copied, "-q",
                            "--no-header", "-p", "no:cacheprovider"],
                           cwd=wt, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        collected = not re.search(r"error|ERROR|ImportError|ModuleNotFound", out) \
            or "passed" in out or "failed" in out
        if re.search(r"\berrors?\b", out) and "failed" not in out and "passed" not in out:
            outcome = "INCONCLUSIVE"
        elif r.returncode == 0:
            outcome = "DECORATIVE"
        elif "failed" in out:
            outcome = "DISCRIMINATES"
        else:
            outcome = "INCONCLUSIVE"
        tail = [l for l in out.splitlines() if l.strip()][-1:] or [""]
        return {"ident": ident, "outcome": outcome, "closing": sha[:12],
                "parent": par[:12], "tests": len(copied), "tail": tail[0][:90]}
    except subprocess.TimeoutExpired:
        return {"ident": ident, "outcome": "TIMEOUT", "parent": par[:12]}
    finally:
        if not keep:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=REPO, capture_output=True)
            subprocess.run(["git", "worktree", "prune"], cwd=REPO,
                           capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--entry", action="append",
                    help="check only this entry (repeatable)")
    ap.add_argument("--limit", type=int, default=0,
                    help="check at most this many, sampled deterministically")
    ap.add_argument("--seed", type=int, default=20261017)
    ap.add_argument("--keep", action="store_true",
                    help="leave the worktrees in place for inspection")
    a = ap.parse_args()

    all_entries = _entries()
    print(f"DONE entries naming an existing test file: {len(all_entries)}")
    if a.entry:
        chosen = [(i, t) for i, t in all_entries if i in set(a.entry)]
        if not chosen:
            print(f"no DONE entry matches {a.entry}")
            return 2
    elif a.limit:
        rnd = random.Random(a.seed)
        chosen = rnd.sample(all_entries, min(a.limit, len(all_entries)))
        print(f"sampling {len(chosen)} of them, seed {a.seed} so the sample is "
              f"reproducible")
    else:
        chosen = all_entries
        print("checking ALL of them; this costs a worktree and a pytest run each")

    rows = []
    for ident, tests in sorted(chosen):
        res = check(ident, tests, keep=a.keep)
        rows.append(res)
        print(f"  {ident:<6} {res['outcome']:<15} {res.get('tail','')}")

    print()
    from collections import Counter
    c = Counter(r["outcome"] for r in rows)
    for k, v in c.most_common():
        print(f"  {k:<16} {v}")

    decided = c["DISCRIMINATES"] + c["DECORATIVE"]
    if decided:
        try:
            from statsmodels.stats.proportion import proportion_confint
            lo, hi = proportion_confint(c["DECORATIVE"], decided, method="wilson")
            blo, bhi = proportion_confint(c["DECORATIVE"], decided, method="beta")
            print(f"\nDECORATIVE rate among entries that could be decided: "
                  f"{c['DECORATIVE']} of {decided} = "
                  f"{100*c['DECORATIVE']/decided:.4f}%")
            print(f"  Wilson          [{lo*100:.4f}%, {hi*100:.4f}%]")
            print(f"  Clopper-Pearson [{blo*100:.4f}%, {bhi*100:.4f}%]")
        except Exception as exc:                        # noqa: BLE001
            print(f"\ninterval unavailable: {exc}")
    if c["INCONCLUSIVE"]:
        print(f"\n{c['INCONCLUSIVE']} INCONCLUSIVE: the evidence could not be "
              f"COLLECTED at the parent commit, which is not discrimination. "
              f"Counting those as passes would repeat the error of reading a "
              f"crashed check as a passing one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
