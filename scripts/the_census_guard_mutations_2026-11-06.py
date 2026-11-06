#!/usr/bin/env python3
"""Does the census-producer guard actually DISCRIMINATE? Mutate and watch it fail.

A guard that passes on a healthy tree is a hypothesis. This harness copies the
committed producer, applies one defect at a time to the COPY -- never to the
tree, which a board is reading -- points the guard at the mutant through
`CENSUS_PRODUCER`, and requires the NAMED test to go red.

ANCHORS ARE DERIVED, NOT TYPED. Each mutation finds its target by searching the
producer's own source for the construct it must break, and refuses to run if the
construct is absent, so a producer that moves cannot leave a mutation silently
vacuous.
"""
from __future__ import annotations
import os, re, shutil, subprocess, sys
from pathlib import Path

SP = Path(__file__).resolve().parent
REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
SRC = REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"
#: THE GUARD LIVES IN `bench/tests/`, NOT BESIDE THIS HARNESS. The first
#: version resolved it as `SP / name`, which was true while both sat in a
#: scratchpad and false the moment they were installed -- the harness reported
#: BASELINE RED and refused, which is the correct failure but only because it
#: checks its baseline first.
GUARD = REPO / "bench" / "tests" / "test_the_census_producer_actually_runs_2026-11-04.py"

def mutate_exit(s: str) -> str:
    """Restore the defect's visible signature: a non-zero exit.

    THE ANCHOR IS THE PRODUCER'S OWN CONDITIONAL RETURN, found by search. My
    first version looked for a bare `return 0`, which this producer does not
    contain -- it returns `0 if ok else 1` -- and the harness correctly refused
    to run rather than reporting a vacuous pass.
    """
    m = re.search(r"\n(\s*)return 0 if ok else 1\s*\n", s)
    if not m:
        raise SystemExit("ANCHOR ABSENT: `return 0 if ok else 1` is gone")
    return s[:m.start()] + f"\n{m.group(1)}return 1\n" + s[m.end():]

def mutate_verdict_beside_failure(s: str) -> str:
    """Print a FAILED structural summary while still asserting the verdict.

    This is the shape the seat found: `All structural checks held: False`
    printed next to a verdict sentence a reader would quote.
    """
    m = re.search(r"ALL HELD:\s*\{([^}]+)\}", s)
    if not m:
        raise SystemExit("ANCHOR ABSENT: no `ALL HELD: {...}` to force False")
    return s[:m.start(1)] + "False" + s[m.end(1):]

def mutate_identity(s: str) -> str:
    """Corrupt the printed broad total so the recomputed identity fails.

    THE ANCHOR IS THE EXACT PRINT SITE. The figure is emitted as
    `report {s2['broad_total']}` inside a split f-string, so a pattern looking
    for `would report {` across the line break found nothing -- which the
    harness reported as an absent anchor instead of a pass.
    """
    m = re.search(r"report \{s2\['broad_total'\]\}", s)
    if not m:
        raise SystemExit("ANCHOR ABSENT: the broad-total print site has moved")
    return (s[:m.start()] + "report {s2['broad_total'] + 7}" + s[m.end():])

MUTATIONS = [
    ("exit flipped to 1",                  mutate_exit,
     "test_it_exits_zero"),
    ("verdict asserted beside a failure",  mutate_verdict_beside_failure,
     "test_the_verdict_is_asserted_XOR_withheld"),
    ("broad total inflated by 7",          mutate_identity,
     "test_his_plus_excluded_reconstructs_the_broad_total"),
]

def run_guard(target: Path) -> tuple[int, str]:
    env = {**os.environ, "CENSUS_PRODUCER": str(target)}
    p = subprocess.run([sys.executable, "-m", "pytest", str(GUARD), "-q"],
                       cwd=SP, capture_output=True, text=True, env=env, timeout=900)
    return p.returncode, p.stdout + p.stderr

def main() -> int:
    base = SRC.read_text(encoding="utf-8")
    print("0. BASELINE -- the guard must PASS on the committed producer")
    rc, out = run_guard(SRC)
    print(f"   exit {rc}: {out.strip().splitlines()[-1] if out.strip() else ''}")
    if rc != 0:
        print("   BASELINE RED -- the guard is not green on a healthy tree; stop.")
        return 1

    red, failures = 0, []
    for name, fn, expect in MUTATIONS:
        mutant = SP / "mutant_census_producer.py"
        try:
            mutant.write_text(fn(base), encoding="utf-8")
        except SystemExit as e:
            print(f"\n{name}: {e}")
            failures.append((name, "anchor absent")); continue
        rc, out = run_guard(mutant)
        named = expect in out
        ok = rc != 0 and named
        print(f"\n{name}")
        print(f"   guard exit {rc}   the NAMED test appears in the failures: {named}")
        print(f"   -> {'RED as required' if ok else 'DID NOT DISCRIMINATE'}")
        if ok: red += 1
        else: failures.append((name, f"exit {rc}, named={named}"))
        mutant.unlink(missing_ok=True)

    print(f"\n{red} of {len(MUTATIONS)} mutations turned the guard red.")
    if failures:
        print("NOT DISCRIMINATING:", failures)
        return 1
    print("the guard discriminates on every defect it claims to catch.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
