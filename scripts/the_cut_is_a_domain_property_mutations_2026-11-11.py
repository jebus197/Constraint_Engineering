#!/usr/bin/env python3
"""Each mutation of the producer must turn its guard RED. A guard nothing can break is not a guard.

Mutates `scripts/the_cut_is_a_domain_property_not_a_constant_2026-11-11.py` in place, runs
`bench/tests/test_the_cut_is_a_domain_property_2026-11-11.py`, and RESTORES THE BYTES IT
FOUND -- not the bytes it expected, because a restore that writes an assumed original is
itself a mutation.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = REPO / "scripts" / "the_cut_is_a_domain_property_not_a_constant_2026-11-11.py"
GUARD = REPO / "bench" / "tests" / "test_the_cut_is_a_domain_property_2026-11-11.py"


def _anchor(src: str, text: str, what: str) -> str:
    n = src.count(text)
    if n != 1:
        raise SystemExit(f"ANCHOR NOT UNIQUE for {what}: {n} occurrence(s). "
                         "The subject moved; fix this harness rather than the count.")
    return text


MUTATIONS = [
    ("M1 the fixed-value cut is asserted invariant, so the central claim inverts",
     'solver.add(before != after)', 'solver.add(before == after)'),
    ("M2 the distinguished-element cut stops being order-preserving, so it becomes breakable",
     's2v.add(s1b < s2b, s2b < s3b, t1b < t2b, t2b < t3b)',
     's2v.add(s1b < s2b, s2b < s3b, t1b < t2b)'),
    ("M3 the re-scaling stops clearing the cut, so criticals survive",
     'a = (0.999 * CUT / mx) if mx > 0 else 0.5',
     'a = (1.001 * CUT / mx) if mx > 0 else 0.5'),
    #: ★ M4 WAS A BAD MUTATION AND IS REPLACED, 2026-11-11. It read
    #: `before_py = before_np`, collapsing the 2 counting routes into 1. The
    #: guard stayed GREEN and that was CORRECT: a collapsed route still returns
    #: the right NUMBER, and no test outside the producer can see how a correct
    #: number was reached. Mutating an unobservable is a defect in the harness,
    #: not a miss by the guard. What the routes exist to protect is the VALUE,
    #: so the replacement corrupts the value and the guard must catch that.
    ("M4 the pure-Python route counts the wrong side of the cut",
     'before_py = sum(1 for v in sevs if v >= CUT)',
     'before_py = sum(1 for v in sevs if v < CUT)'),
    ("M5 a domain config is reported as declaring a scale when none does",
     'rows.append((fp.relative_to(REPO).as_posix(), sorted(keys & SCALE_KEYS)))',
     'rows.append((fp.relative_to(REPO).as_posix(), ["severity_scale"]))'),
    ("M6 --help falls through and runs the whole archive walk",
     'if any(a in ("-h", "--help") for a in argv):',
     'if False:'),
]


def main() -> int:
    found = SUBJECT.read_bytes()
    src = found.decode("utf-8")
    red = 0
    try:
        print(f"{len(MUTATIONS)} mutations; each must turn its guard red\n")
        for label, a, b in MUTATIONS:
            _anchor(src, a, label)
            SUBJECT.write_text(src.replace(a, b, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q",
                                "-p", "no:cacheprovider"],
                               cwd=REPO, capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                red += 1
                tail = [ln for ln in r.stdout.splitlines() if ln.startswith("FAILED")]
                print(f"  RED    {label}")
                for t in tail[:3]:
                    print(f"           -> {t.split('::')[-1]}")
            else:
                print(f"  GREEN  {label}   <<< THE GUARD MISSED IT")
    finally:
        SUBJECT.write_bytes(found)
        same = SUBJECT.read_bytes() == found
        print(f"\nsubject restored byte-identical: {same} ({len(found)} bytes)")
    print(f"\n{red} of {len(MUTATIONS)} mutations red")
    return 0 if red == len(MUTATIONS) else 1


if __name__ == "__main__":
    sys.exit(main())
