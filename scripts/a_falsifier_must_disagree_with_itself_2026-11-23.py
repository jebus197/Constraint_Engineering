# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_joint_b23_b10_20261123T133529Z', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 4b3891fc508071d70878aa39e1c89dc8eb26553b07c094edd47100cce342ad2d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A falsifier that gives the SAME verdict with and without the defect is VOID.

DESTINATION `scripts/`. Written 2026-11-23 for the joint panel round, Q5.

★ THE FAILURE SHAPE, AND IT HAS NOW HAPPENED 3 TIMES IN ONE SESSION.
A falsifier is written, RUN, and its result is read as evidence -- when in fact
the run could not have come out any other way, so it measured nothing:

  1. B211 (the question that prompted this). A repair was exercised on an
     ALREADY-REPAIRED tree. Nothing could move, the falsifier "refuted" the
     diagnosis, and the diagnosis was one sentence from being recorded as wrong.
  2. 2026-11-23, this round, Q3. A mutation harness was run with `--help` in a
     throwaway clone to test whether `--help` writes. It did not write -- but it
     exited at `REFUSED: the guard is RED before any mutation`, i.e. for an
     unrelated reason. Reported as-is it would have COLLAPSED a true premise.
  3. The same check again, by tree hash. Before/after sha256 of the subject were
     IDENTICAL while a write tracer recorded 13 writes to it, because the
     harness restores what it mutates. The observable was wrong, not the run.

★ WHY "ASSERT THE PRECONDITION" IS NOT THE RULE THAT FIXES THIS, which is the
question put to the panel. A precondition assertion requires the author to have
ALREADY NAMED the way the run could be vacuous. In all 3 cases above the author
had not -- in case 2 the vacuity came from a guard in a file the author was not
looking at, and in case 3 from the choice of observable. A rule that fires only
when you anticipated the failure cannot catch the failures you did not
anticipate, and this project has now broken that rule twice in one session,
which its own standard says means it is not a rule.

★ THE RULE THAT DOES BIND IS DIFFERENTIAL, AND IT NEEDS NO FORESIGHT. Run the
falsifier TWICE -- once against a tree where the defect is present, once against
a tree where it is absent -- and require the 2 verdicts to DISAGREE. Agreement
in EITHER direction is vacuity:

    defect present -> FAIL,  absent -> PASS   : the falsifier discriminates. OK.
    both FAIL                                 : it fails for an unrelated reason.
    both PASS                                 : it cannot see the defect at all.

This is `fails_iff_defect` from the CDSFL falsifier-gate specification, with the
second half actually EXECUTED. The gate as it stands re-runs a falsifier ONCE,
on the tree as found, and reads AssertionError-or-`FALSIFIED` as CONFIRMED. That
is the first half only, so every one of the 3 cases above would pass through it.

★ A DISAGREEMENT IS NOT A VERDICT ON THE DEFECT -- it is a licence to report one.
This tool answers "is this falsifier capable of being wrong", not "is the defect
real". Those are different questions and conflating them would be the same error
one level up.

★ IT RESTORES THE TARGET FROM BYTES CAPTURED BEFORE THE FIRST EDIT, and verifies
the restore by comparing bytes, because a restore is a mutation too. Never
`git checkout --`, which in this project once ate the file under test.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

VACUOUS = "VACUOUS"
DISCRIMINATES = "DISCRIMINATES"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def run_falsifier(cmd: list[str], cwd: pathlib.Path) -> dict:
    """FAIL iff the falsifier signals the defect: non-zero exit, or the literal
    token `FALSIFIED` on either stream. Both routes, because the CDSFL
    specification names both and a falsifier may use either."""
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    blob = (r.stdout or "") + (r.stderr or "")
    return {"exit": r.returncode, "token": "FALSIFIED" in blob,
            "fail": r.returncode != 0 or "FALSIFIED" in blob,
            "tail": blob.strip().splitlines()[-3:]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--target", required=True,
                    help="the file whose defect is being toggled")
    ap.add_argument("--defect-file", required=True,
                    help="a copy of --target IN THE DEFECTIVE STATE; the "
                         "difference between the 2 is the defect under test")
    ap.add_argument("--cwd", default=".", help="working directory for the run")
    ap.add_argument("falsifier", nargs=argparse.REMAINDER,
                    help="the falsifier command, after `--`")
    a = ap.parse_args(argv)

    cmd = [x for x in a.falsifier if x != "--"]
    if not cmd:
        print("no falsifier command given", file=sys.stderr)
        return 2
    cwd = pathlib.Path(a.cwd).resolve()
    target = pathlib.Path(a.target)
    defect = pathlib.Path(a.defect_file).read_bytes()
    clean = target.read_bytes()

    if _sha(clean) == _sha(defect):
        print("REFUSING: --target and --defect-file are byte-identical, so "
              "there is no defect to toggle and this check would itself be "
              "vacuous.", file=sys.stderr)
        return 2

    print("=" * 74)
    print("CAN THIS FALSIFIER BE WRONG?  (differential vacuity check)")
    print("=" * 74)
    print(f"\n  target     : {target}")
    print(f"  clean sha  : {_sha(clean)}")
    print(f"  defect sha : {_sha(defect)}")
    print(f"  falsifier  : {' '.join(cmd)}\n")

    try:
        target.write_bytes(defect)
        arm_defect = run_falsifier(cmd, cwd)
        target.write_bytes(clean)
        arm_clean = run_falsifier(cmd, cwd)
    finally:
        target.write_bytes(clean)
        restored = target.read_bytes() == clean
    if not restored:
        print("RESTORE FAILED — the target is not what it was. Fix before "
              "trusting anything above.", file=sys.stderr)
        return 2

    for name, arm in (("DEFECT PRESENT", arm_defect), ("DEFECT ABSENT", arm_clean)):
        print(f"  {name:15s} exit={arm['exit']:<4} FALSIFIED-token={arm['token']}"
              f"  -> {'FAIL' if arm['fail'] else 'PASS'}")
        for line in arm["tail"]:
            print(f"                  | {line[:88]}")

    print(f"\n  target restored byte-for-byte : {restored}")

    if arm_defect["fail"] and not arm_clean["fail"]:
        print(f"\n  {DISCRIMINATES}: it FAILS with the defect and PASSES without "
              f"it, so\n  its verdict carries information. This is a licence to "
              f"report a\n  finding -- NOT a verdict that the defect is real.")
        return 0

    if arm_defect["fail"] and arm_clean["fail"]:
        why = ("it FAILS IN BOTH ARMS, so it is failing for a reason that has "
               "nothing to do\n  with the defect -- a bad import, a red "
               "precondition, the wrong tree state.")
    elif not arm_defect["fail"] and not arm_clean["fail"]:
        why = ("it PASSES IN BOTH ARMS, so it cannot see the defect at all -- "
               "it is\n  watching the wrong observable, or it exits before its "
               "assertions run.")
    else:
        why = ("it PASSES with the defect and FAILS without it -- its sense is "
               "INVERTED,\n  so every verdict it has ever returned is backwards.")
    print(f"\n  {VACUOUS}: {why}")
    print("\n  NO VERDICT IS AVAILABLE FROM THIS FALSIFIER. Under the CDSFL "
          "falsifier gate\n  this routes to HUMAN REVIEW. It must never "
          "auto-CONFIRM and it must never\n  be read as a REFUTATION, which is "
          "the error of all 3 recorded cases.")
    print("FALSIFIED")
    return 1


if __name__ == "__main__":
    # ★ NO `answer_help` HERE, DELIBERATELY, AND THIS SCRIPT DOES WRITE.
    # `_cli_help.answer_help` REFUSES any argument -- it is for scripts that
    # take none -- and this one is argument-driven, so calling it made every
    # real invocation fail with "This script takes no arguments". Found by
    # running it, on the first invocation. `argparse` answers `-h`/`--help`
    # itself and exits inside `parse_args()`, which is reached BEFORE any file
    # is read or written, so his rule that a `--help` must never act is
    # satisfied by construction and by the ordering, not by a bolted-on guard.
    raise SystemExit(main())
