#!/usr/bin/env python3
"""Reversion test for the parked-presentation guard.

RESTORE SEMANTICS, STATED BECAUSE THE FIRST SUCH HARNESS GOT THEM WRONG. The
original bytes are captured in memory and replayed between mutations. A harness
that restored with `git checkout --` deleted uncommitted work on 2026-11-01 --
and reported a full sweep before doing it -- because a guard is always built
against work that was just written, so git's copy is by construction the wrong
baseline. The subject is also checked for existence first, so a run against an
absent subject refuses instead of reporting success.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "morning_report_build_2026-10-12.py"
GUARD = ("bench/tests/"
         "test_the_parked_presentation_is_described_not_coded_2026-11-01.py")

MUTATIONS = [
    ("restore_ignorecase",
     "the re.I that hid a live Desktop warning is put back",
     lambda t: t.replace(
         'r"NOT A BLOCKER|ALREADY (?:DONE|BUILT|FIXED))\\b")',
         'r"NOT A BLOCKER|ALREADY (?:DONE|BUILT|FIXED))\\b", re.I)', 1)),
    ("never_bucket_settled",
     "self-declared closures stop being separated out",
     lambda t: t.replace("if _PARKED_SELF_CLOSED.search(h):",
                         "if False and _PARKED_SELF_CLOSED.search(h):", 1)),
    ("stop_collapsing_one_subject",
     "7 notes on 1 subject are listed 7 times again",
     lambda t: t.replace("grouped.setdefault(codes[0], []).append(h)",
                         "grouped.setdefault(h, []).append(h)", 1)),
    ("render_the_bare_code_as_the_subject",
     "his exact objection returns: an item named only by its code",
     lambda t: t.replace('"subject": entry.get("headline") or longest,',
                         '"subject": code,', 1)),
    ("drop_the_ruling_date",
     "a decided item becomes indistinguishable from an owed one",
     lambda t: t.replace('"ruled": entry.get("ruled"),',
                         '"ruled": None,', 1)),
    ("lose_a_true_positive_word",
     "RESOLVED stops being recognised as a declaration",
     lambda t: t.replace('r"\\b(RESOLVED|SUPERSEDED|IS CLOSED|',
                         'r"\\b(SUPERSEDED|IS CLOSED|', 1)),
    ("unwire_one_renderer",
     "the fix reaches the markdown path but not the TTS path",
     lambda t: t.replace("parked_presentation(", "_unused_pp(", 2)),
]


def guard_is_red() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q",
                        "-p", "no:randomly"],
                       capture_output=True, text=True, cwd=str(REPO))
    tail = [l for l in r.stdout.splitlines() if l.strip()]
    return r.returncode != 0, (tail[-1] if tail else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    original = SUBJECT.read_text(encoding="utf-8")
    if "def parked_presentation" not in original:
        print("REFUSING: no parked_presentation in the subject to mutate.")
        return 1

    baseline_red, baseline_line = guard_is_red()
    results = []
    try:
        for name, why, fn in MUTATIONS:
            mutated = fn(original)
            if mutated == original:
                results.append({"mutation": name, "why": why, "red": None,
                                "note": "pattern did not apply -- the subject "
                                        "has changed shape; re-derive it"})
                continue
            SUBJECT.write_text(mutated, encoding="utf-8")
            red, line = guard_is_red()
            results.append({"mutation": name, "why": why, "red": red,
                            "pytest": line})
            SUBJECT.write_text(original, encoding="utf-8")
    finally:
        SUBJECT.write_text(original, encoding="utf-8")
        assert SUBJECT.read_text(encoding="utf-8") == original, \
            "the restore did not reproduce the bytes this script found"

    caught = sum(1 for r in results if r.get("red") is True)
    applicable = sum(1 for r in results if r.get("red") is not None)

    if args.json:
        print(json.dumps({"baseline_green": not baseline_red, "caught": caught,
                          "applicable": applicable, "results": results},
                         indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"BASELINE: {'GREEN' if not baseline_red else 'RED -- ' + baseline_line}")
    if baseline_red:
        print("  A guard red before any mutation measures nothing.")
        return 1
    print()
    for r in results:
        mark = "n/a " if r.get("red") is None else ("RED " if r["red"] else "GREEN")
        print(f"  [{mark}] {r['mutation']}")
        print(f"          simulates: {r['why']}")
        if r.get("red") is False:
            print("          ** NOT CAUGHT -- this property is not pinned **")
        if r.get("note"):
            print(f"          {r['note']}")
    print()
    print(f"CAUGHT {caught} of {applicable} applicable mutations "
          f"({len(MUTATIONS)} written).")
    print("Subject restored byte-identically.")

    # ★ A FAILABLE CHECK AFTER THE FINAL RESTORE, 2026-11-01. The restore above
    # WRITES THE SUBJECT, so it is itself the turn's last mutation -- and the
    # Stop gate keys P-PASS on `any(i > last)`. A harness that ends by restoring
    # therefore leaves P-PASS unsatisfied no matter how many times it ran pytest
    # inside the sweep, which happened twice on the night this was added. One
    # run here puts the trace on the right side of `last`, and it doubles as the
    # proof that the restore really did put the subject back.
    _after = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q",
                             "-p", "no:randomly"],
                            capture_output=True, text=True, cwd=str(REPO))
    _line = [l for l in _after.stdout.splitlines() if l.strip()]
    print(f"post-restore check: {_line[-1] if _line else '(no output)'}")
    if _after.returncode != 0:
        print("  ** THE RESTORE DID NOT PUT THE SUBJECT BACK -- investigate **")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
