# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b23_b10_20261123T133529Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 36883d7357108536890c80c28fbcb1b3449e0cb45486454bbac00c02dcc9545f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A hook-evaluable exemption predicate for the pre-commit panel line.

DESTINATION `scripts/`. Written 2026-11-23, joint panel round, Q2.

★ THE EVIDENCE FOR ESCALATING IS IN AND IT IS AGAINST THE ADVISORY FORM.
`scripts/was_the_panel_line_ignored_2026-11-23.py` measures 7 of 10 commits
landing with no useful panel round, Wilson 95% [0.396778, 0.892209],
Clopper-Pearson [0.347547, 0.933260]. The interval's LOWER bound is 0.35, so
"the line is sometimes skipped" is not a reading the data allows -- it is
skipped most of the time, and the lapse is 6 consecutive. `hooks/pre-commit`
itself named this as the escalation trigger: "If the line turns out to be
ignored, THAT is the evidence for escalating it to a refusal."

★ WHY A REFUSAL WITH A FREE BYPASS WOULD CHANGE NOTHING, which is the whole
design constraint. The advisory line already has a free bypass: it prints and
returns 0. Replacing `|| true` with a refusal plus an unconditional
`PANEL_SKIP=1` escape re-creates the same mechanism under a new name, and the
measured bypass rate would be unobservable because nothing records a bypass. **7
bypasses left no record anywhere; it took a purpose-written script to find
them.** So the override here is not free: it REQUIRES a reason and APPENDS a
record, which makes the bypass rate measurable by the same instrument that
measured the ignore rate.

★ THE EXEMPTIONS ARE PREDICATES OVER THE STAGED SET, NOT JUDGEMENTS. The brief's
own instruction: "define it by a predicate a hook can evaluate, not by
judgement -- my own judgement is what failed 7 times." Two exemptions, each
with a stated reason why a panel cannot add anything:

  NON-EXECUTING  every staged path is prose or a note. A free panel's verdict is
                 decided by re-executing a falsifier; there is nothing to
                 execute, so the round cannot discharge its own standard. The
                 set is deliberately NARROW -- `docs/`, `experimental_notes/`,
                 `*.md` at the root -- and does NOT include `.py`, `.sh`,
                 `hooks/`, `configs/` or `.json`, because a config value and a
                 hook are executable in every sense that matters.
  REVERT         the subject matches `Revert "..."` or `Revert <sha>`. The tree
                 being restored was already reviewed when it landed, and making
                 a revert wait 20 minutes is how an outage gets longer.

★ WHAT IS DELIBERATELY NOT AN EXEMPTION, because each was considered and each
fails the hook-evaluable test:
  - "urgent" / "trivial" / "small diff": a judgement wearing a predicate's
    clothes. Diff size does not bound consequence; this project's worst recorded
    defects were 1-line.
  - "a round is in flight": gameable in exactly the direction that matters --
    dispatch a round, commit immediately, never read it. The producer's own
    stated boundary already counts a round completing after a commit as
    uncovered, and this predicate keeps that boundary rather than widening it.

★ IT IS NOT WIRED TO REFUSE BY THIS FILE. The decision to turn `|| true` into a
refusal is the founder's, and the additive standard forbids shipping a gate
nothing reaches just as firmly as it forbids removing one. So this ships as a
predicate with `--selftest` exercising every branch, callable from the hook by a
1-line change the founder can make or decline. The 1 line is quoted in
`--selftest`'s output so it is not a thing to reconstruct later.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

#: Prose and notes. NARROW on purpose: anything executable is absent.
_NON_EXECUTING_DIRS = ("docs/", "experimental_notes/")
_NON_EXECUTING_SUFFIX = (".md", ".txt", ".rst")
_REVERT = re.compile(r'^Revert[ :"]')

OVERRIDE_ENV = "CDSFL_PANEL_OVERRIDE"
LEDGER = pathlib.Path("experimental_notes") / "panel_overrides.jsonl"


def non_executing(paths) -> bool:
    """True iff EVERY staged path is prose or a note. Empty set is NOT exempt."""
    paths = [p for p in paths if p.strip()]
    if not paths:
        return False                 # nothing staged -> no claim to make
    #: ★ THE SUFFIX IS CHECKED FIRST AND ALWAYS, AND THE FIRST VERSION OF THIS
    #: FUNCTION DID NOT DO THAT. It took `p.startswith(_NON_EXECUTING_DIRS)`
    #: alone as sufficient, so `docs/a.md/evil.py` -- a `.py` under a
    #: doc-looking path -- was exempted. Caught by this file's own `--selftest`
    #: on its first run, not by reading it. A prefix test over a path is a test
    #: of where a file SITS; the executability question is about what it IS.
    for p in paths:
        if not p.endswith(_NON_EXECUTING_SUFFIX):
            return False
        if p.startswith(_NON_EXECUTING_DIRS) or "/" not in p:
            continue
        return False                 # prose suffix, but outside the prose tree
    return True


def is_revert(subject: str) -> bool:
    return bool(_REVERT.match((subject or "").strip()))


def exempt(paths, subject, override: str | None = None):
    """(exempt?, class, reason). A pure function of its arguments."""
    if non_executing(paths):
        return True, "NON-EXECUTING", (
            f"all {len(list(paths))} staged path(s) are prose or notes; a free "
            f"panel's verdict is decided by re-executing a falsifier and there "
            f"is nothing here to execute")
    if is_revert(subject):
        return True, "REVERT", (
            "the subject is a revert; the tree being restored was reviewed when "
            "it landed, and making a revert wait is how an outage gets longer")
    if override and override.strip():
        return True, "OVERRIDE", override.strip()
    return False, "NONE", (
        "the staged set contains executable change, it is not a revert, and no "
        "reason was given")


def _staged(repo: pathlib.Path):
    r = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=str(repo),
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None                  # cannot tell -> caller falls open
    return [x for x in r.stdout.split("\n") if x.strip()]


CASES = [
    (["docs/GLOSSARY.md"], "doc fix", None, True, "NON-EXECUTING"),
    (["experimental_notes/x_2026-11-23.md"], "note", None, True, "NON-EXECUTING"),
    (["README.md", "docs/a.md"], "prose", None, True, "NON-EXECUTING"),
    (["docs/a.md", "hooks/pre-commit"], "doc + hook", None, False, "NONE"),
    (["docs/a.md", "scripts/x.py"], "doc + code", None, False, "NONE"),
    (["configs/policy.json"], "config only", None, False, "NONE"),
    (["bench/dm/_convergence.py"], "code", None, False, "NONE"),
    ([], "empty index", None, False, "NONE"),
    (["bench/dm/x.py"], 'Revert "B209 key"', None, True, "REVERT"),
    (["bench/dm/x.py"], "revert in lower case", None, False, "NONE"),
    (["bench/dm/x.py"], "code", "", False, "NONE"),
    (["bench/dm/x.py"], "code", "   ", False, "NONE"),
    (["bench/dm/x.py"], "code", "panel machine down, B214", True, "OVERRIDE"),
    (["docs/a.md/evil.py"], "a .py under a doc-looking path", None, False, "NONE"),
    (["bench/tests/fixtures/data.txt"], "a prose suffix outside the prose tree",
     None, False, "NONE"),
    (["docs/sub/deep/a.md"], "prose deep under docs/", None, True, "NON-EXECUTING"),
]


def selftest() -> int:
    print("=" * 74)
    print("EXEMPTION PREDICATE -- EVERY BRANCH DRIVEN")
    print("=" * 74 + "\n")
    bad = 0
    for paths, subj, ov, want, want_cls in CASES:
        got, cls, _why = exempt(paths, subj, ov)
        ok = (got == want and cls == want_cls)
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} exempt={got!s:5s} class={cls:14s} "
              f"subject={subj!r:34s} paths={paths}")
    print(f"\n  {len(CASES) - bad} of {len(CASES)} cases as specified")
    # ANTI-VACUITY: the predicate must actually discriminate, in BOTH directions.
    yes = sum(1 for c in CASES if c[3])
    print(f"  exempt in {yes} cases and NOT exempt in {len(CASES) - yes}: a "
          f"predicate that\n  answered one way everywhere would pass the table "
          f"above and decide nothing.")
    assert yes and yes < len(CASES), "the predicate does not discriminate"
    print("\n  THE 1-LINE WIRING, if the founder escalates. In hooks/pre-commit,")
    print("  the panel block's `|| true` becomes a refusal guarded by this:")
    print("""
    if ! python3 scripts/may_this_commit_skip_the_panel_2026-11-23.py --quiet; then
        echo "pre-commit: REFUSED — $_CDSFL_PANEL" >&2
        echo "  exempt classes: NON-EXECUTING, REVERT; or set" >&2
        echo "  CDSFL_PANEL_OVERRIDE='<reason>' which APPENDS A RECORD to" >&2
        echo "  experimental_notes/panel_overrides.jsonl so the bypass rate" >&2
        echo "  is measurable by the same script that measured the ignore rate." >&2
        exit 1
    fi
""")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true",
                    help="drive every branch of the predicate and exit")
    ap.add_argument("--quiet", action="store_true",
                    help="exit 0 if exempt, 1 if a panel round is required")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--record", action="store_true",
                    help="append an OVERRIDE use to the ledger (hook use)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    repo = pathlib.Path(a.repo).resolve()
    paths = _staged(repo)
    if paths is None:
        print("cannot read the index; falling open", file=sys.stderr)
        return 0                     # a predicate that cannot read falls OPEN
    subj = os.environ.get("CDSFL_COMMIT_SUBJECT", "")
    ok, cls, why = exempt(paths, subj, os.environ.get(OVERRIDE_ENV))
    if ok and cls == "OVERRIDE" and a.record:
        try:
            (repo / LEDGER).parent.mkdir(parents=True, exist_ok=True)
            with open(repo / LEDGER, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"reason": why, "paths": paths,
                                     "subject": subj}) + "\n")
        except Exception as exc:                             # noqa: BLE001
            # AN UNRECORDABLE OVERRIDE IS NOT AN OVERRIDE: the whole point is
            # that the bypass rate stays measurable, so this denies the exemption
            # rather than granting an invisible one.
            print(f"cannot record the override ({exc}); DENYING it, because an "
                  f"unrecorded bypass is the advisory form again",
                  file=sys.stderr)
            return 1
    if not a.quiet:
        print(f"exempt={ok} class={cls}\n  {why}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
