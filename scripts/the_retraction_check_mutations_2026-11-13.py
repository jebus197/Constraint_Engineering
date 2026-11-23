#!/usr/bin/env python3
"""Does the B174 retraction check actually go RED? 4 mutations, each correctly aimed.

A passing test proves nothing until it has been made to fail. This reverts each
behaviour the guard claims to hold and checks the NAMED test for that behaviour
turns red -- not merely that something somewhere failed.

★ ONE MUTATION WAS AIMED AT THE WRONG TEST ON ITS FIRST RUN, and the harness
reported it STILL GREEN rather than quietly scoring itself a pass. N3 breaks the
early exit in `_retraction_line` -- the check for whether a figure genuinely
prints on some unmarked line -- and that exit is load-bearing ONLY where the
figure appears on BOTH a marked and an unmarked line. The fixture it was first
aimed at puts the marker on a line that does not contain the token, so the exit
was never exercised there. Aiming a mutation at a test that cannot observe it
scores the harness on the wrong test, which is the defect
`feedback_cap_the_test_that_hangs_not_the_one_you_suspect_2026-11-03` names.

RESTORE DISCIPLINE: the original bytes are held in memory and written back, then
compared. Never `git checkout --`, which would also discard uncommitted work that
was present before this ran.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "panel_brief_validate.py"
GUARD = "bench/tests/test_a_retraction_is_not_a_reproduction_2026-11-13.py"

MUTATIONS = [
    ("N1 the retraction check removed entirely",
     "test_a_figure_printed_only_on_a_refuted_line_is_reported",
     "        _retracted = _retraction_line(want, _out)\n        if _retracted is not None:",
     "        _retracted = None\n        if _retracted is not None:",
     "a figure printed only inside its own retraction is accepted again, which "
     "is the defect B174 records"),

    ("N2 the retraction message collapsed into the absent message",
     "test_the_retraction_message_differs_from_the_absent_message",
     'f"declared figure {label!r}: {want!r} is {_retracted} by its own "\n'
     '                f"producer {rel} -- it appears only on a line retracting it. The "\n'
     '                f"brief cites a figure the project has withdrawn. Re-issue the "\n'
     '                f"brief without it, or with the replacement value; do NOT restore "\n'
     '                f"the figure to the producer"',
     'f"declared figure {label!r}: the brief says {want!r} and {rel} does not "\n'
     '                f"print it"',
     "the 2 messages send a reader to OPPOSITE actions: restore the figure, or "
     "re-issue the brief and leave the producer alone"),

    # ★ AIMED AT THE STATED-LIMIT TEST, not at the genuinely-prints one. See the
    # module docstring: only the stated-limit fixture puts the figure on BOTH a
    # marked and an unmarked line, which is where the early exit decides.
    ("N3 the early exit broken, so the detector over-matches",
     "test_the_stated_limit_holds_and_is_documented",
     "    if _figure_token_found(want, plain):\n"
     "        return None                      # it genuinely prints, somewhere real",
     "    if False:\n"
     "        return None                      # it genuinely prints, somewhere real",
     "a producer that still prints the figure is accused, which is the false "
     "positive that gets a guard switched off altogether"),

    ("N4 a retraction marker dropped from the vocabulary",
     "test_every_retraction_marker_is_recognised",
     '_RETRACTION_MARKERS = ("REFUTED", "WITHDRAWN", "SUPERSEDED")',
     '_RETRACTION_MARKERS = ("REFUTED", "WITHDRAWN")',
     "a figure SUPERSEDED rather than refuted slips through unreported"),
]


def run(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def main() -> int:
    original = SUBJECT.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    print(f"subject : {SUBJECT.relative_to(REPO)}")
    print(f"sha256  : {digest[:16]}  ({len(original)} bytes held in memory)\n")

    rc, tail = run(" or ".join(m[1] for m in MUTATIONS))
    if rc != 0:
        print(f"REFUSED: baseline is already red (rc={rc}). A mutation harness "
              f"cannot measure anything against a red baseline.\n{tail}")
        return 2
    print("BASELINE GREEN\n")

    red, results = 0, []
    try:
        for name, selector, old, new, why in MUTATIONS:
            src = original.decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- the mutation could not be "
                      f"applied, so it proves nothing. Fix the anchor.")
                results.append((name, "ANCHOR MISSING"))
                continue
            SUBJECT.write_text(src.replace(old, new, 1))
            rc, tail = run(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}")
            print(f"    target  : {selector}")
            print(f"    why     : {why}")
            print(f"    verdict : {'RED (caught)' if ok else 'STILL GREEN -- BLIND'}")
            if not ok:
                print(f"    tail    : {tail.strip()[:220]}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)
        back = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
        print(f"\nrestore verified: {back[:16]} == {digest[:16]} -> {back == digest}")
        assert back == digest, "THE RESTORE FAILED -- the subject is left mutated"

    print(f"\nmutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    rc, tail = run(" or ".join(m[1] for m in MUTATIONS))
    print(f"\npost-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    if rc != 0:
        print(tail)
        return 3
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
