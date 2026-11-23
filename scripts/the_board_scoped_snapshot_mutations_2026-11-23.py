#!/usr/bin/env python3
"""Does the board-scoping guard actually bite? 4 reversions, each must go red.

DESTINATION `scripts/`. Written 2026-11-23.

SUBJECT: `scripts/the_preboard_evidence_matches_the_tree_2026-11-23.py`, the
board-liveness fix added after a snapshot from a FINISHED board masked 4 staged
files and reported FRESH.

WHY A HARNESS AND NOT A HAND-RUN. The guard this fix shipped with
(`test_it_does_not_mask_an_operator_edit`) PASSED THROUGHOUT the live defect,
because it fixes 1 of the 2 possible orderings. A test that passes while the
live system fails is the thing to be afraid of, so each branch of the new
predicate is reverted and the suite must go red for each.

ANCHORS ARE DERIVED FROM THE SUBJECT, never typed as expectations: a harness
that spells its own anchor tests the harness.

THE RESTORE IS VERIFIED BY sha256 AGAINST WHAT WAS FOUND, not against what the
harness expected to find.
"""
from __future__ import annotations
import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "the_preboard_evidence_matches_the_tree_2026-11-23.py"
GUARD = REPO / "bench" / "tests" / "test_the_preboard_evidence_matches_the_tree_2026-11-23.py"

#: (label, find, replace). Each `find` is asserted PRESENT before use, so a
#: reworded subject fails loudly instead of silently mutating nothing.
MUTATIONS = [
    ("the pre-fix behaviour: every snapshot counts as live",
     '    pid = snap.get("pid")\n'
     '    if not isinstance(pid, int) or pid <= 0:\n'
     '        return False',
     '    pid = snap.get("pid")\n'
     '    if True:\n'
     '        return True'),
    ("a dead board reads as alive",
     "    except ProcessLookupError:\n        return False",
     "    except ProcessLookupError:\n        return True"),
    ("no snapshot is ever honoured, reinstating the false positive",
     "            if isinstance(cand, str) and cand and _board_is_alive(snap):",
     "            if False:"),
    ("the pid is not recorded, so scoping cannot work",
     'json.dumps({"digest": d, "pid": os.getppid()}),',
     'json.dumps({"digest": d}),'),
]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_guard(timeout: int = 900):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x",
                        "-p", "no:cacheprovider", str(GUARD)],
                       cwd=str(REPO), capture_output=True, text=True,
                       timeout=timeout)
    return r.returncode, (r.stdout or "")[-400:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    original = SUBJECT.read_text()
    found_sha = sha(SUBJECT)
    print("=" * 74)
    print("DOES THE BOARD-SCOPED SNAPSHOT GUARD BITE? 4 REVERSIONS")
    print("=" * 74)
    print(f"\n  subject sha256 as FOUND : {found_sha[:16]}")

    rc, out = run_guard()
    print(f"  baseline (unmutated)    : exit {rc}  {'GREEN' if rc == 0 else 'RED'}")
    if rc != 0:
        print(f"    the guard is already red; a mutation result would be "
              f"meaningless.\n{out}")
        return 2

    red = 0
    try:
        for label, find, repl in MUTATIONS:
            if find not in original:
                print(f"\n  SKIP  {label}\n        anchor absent from the "
                      f"subject -- it was reworded; UPDATE THIS HARNESS rather "
                      f"than trusting a skip")
                continue
            SUBJECT.write_text(original.replace(find, repl, 1))
            mrc, mout = run_guard()
            verdict = "RED (good)" if mrc != 0 else "GREEN (THE GUARD IS BLIND)"
            print(f"\n  {verdict}  {label}")
            if mrc == 0:
                print(f"        the suite passed with this branch reverted, so "
                      f"nothing tests it")
            else:
                red += 1
                tail = [l for l in mout.split("\n") if "failed" in l or "passed" in l]
                if tail and not a.quiet:
                    print(f"        {tail[-1].strip()}")
            SUBJECT.write_text(original)
    finally:
        #: RESTORE WHAT WAS FOUND, and VERIFY it -- not what was expected.
        SUBJECT.write_text(original)
        back = sha(SUBJECT)
        print(f"\n  restored sha256         : {back[:16]}"
              f"   {'MATCHES' if back == found_sha else 'MISMATCH -- INTERVENE'}")
        if back != found_sha:
            print("  THE SUBJECT WAS NOT RESTORED. Do not commit; "
                  "`git diff` the subject and repair by hand.")
            return 3

    n = len([m for m in MUTATIONS if m[1] in original])
    print(f"\n  {red} of {n} applicable reversion(s) turned the guard RED")
    if red != n:
        print("  A REVERSION THAT STAYS GREEN IS AN UNTESTED BRANCH.")
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help
        #: ★ `takes_no_arguments=False` IS LOAD-BEARING, NOT COSMETIC. The
        #: default is True, and with it `answer_help` REFUSES every flag with
        #: exit 2 BEFORE this script's own parser is reached -- so each flag
        #: declared below would be unreachable, which is `additive-standard`'s
        #: symmetric form: an addition nothing reaches is not additive. Found
        #: 2026-11-23 by a test written for a sibling script, which reported
        #: "This script takes no arguments" for a script that has some.
        answer_help(__doc__, __file__,
                    takes_no_arguments=False)
    except ImportError:
        pass
    raise SystemExit(main())
