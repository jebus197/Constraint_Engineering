#!/usr/bin/env python3
"""Does the inverse-direction check on the decision surfaces actually DISCRIMINATE?

WHY THIS EXISTS. `bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py`
checked 1 direction: every LIVE decision must carry a `spoken_heading`, so he is
never asked about something the record does not track. On 2026-11-02 an audit of
the queue found the inverse unguarded -- 10 authored entries carried a heading
while the generator derived 9, and the 1 difference, C0001, was rendered nowhere.
That direction produces SILENCE rather than a wrong question, which is why a
guard written to catch divergence did not catch it.

A CHECK NOT TRIED AGAINST ITS OWN FAILURE MODE IS A HYPOTHESIS. This harness
mutates the authored detail and requires the new tests to go RED, then restores
the file and verifies the restoration by hash before exiting. `git checkout --`
is deliberately not used: this project's record holds a case where it ate the
subject of the work.
"""
from __future__ import annotations
import argparse

import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
GUARD = ("bench/tests/test_the_two_decision_surfaces_cannot_diverge_2026-11-01.py"
         "::TestTheInverseDirectionAlsoHolds")


def _run_guard() -> bool:
    """True when the guard class is RED."""
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-q"],
                       capture_output=True, text=True, cwd=str(REPO))
    return r.returncode != 0


def _summary() -> str:
    """The harness's own first docstring line, so `--help` needs no new prose."""
    doc = (__doc__ or "").strip()
    return doc.splitlines()[0] if doc else "mutation harness; writes and restores"


def main() -> int:
    # ★ `--help` MUST NOT MUTATE ANYTHING, 2026-11-03. This harness WRITES: it
    # reverses a property in the tree, runs the suite, then restores. With no
    # parser, `--help` fell straight through to that work, so asking what the
    # script does would have mutated the repository and then put it back -- a
    # write that leaves no diff is still a write, and a concurrent reader would
    # have seen the mutated state. His standing rule is that a `--help` must
    # never cost money; here it could have cost a tree.
    #
    # Measured by `scripts/help_writers_rate_2026-09-17.py`: 5 of 609 scripts
    # wrote and ignored the flag -- 0.8210%, Wilson 95% [0.3512%, 1.9074%],
    # Clopper-Pearson [0.2671%, 1.9055%] -- and all 5 were mutation harnesses
    # written on 2026-11-02, so this is 1 defect made 5 times in 1 day.
    argparse.ArgumentParser(
        description=_summary()).parse_args()
    original = DETAIL.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        base_red = _run_guard()
        results.append(("the UNMUTATED tree is GREEN", not base_red,
                        "red already" if base_red else "green"))

        # M1: an authored entry gains a heading while the generator renders
        # nothing for it. This is exactly the C0001 shape, on a fresh identifier
        # so the pin cannot absolve it.
        d = json.loads(original.decode())
        d["task:ZZ999"] = {
            "title": "ZZ999 - a decision the generator does not render",
            "what": "injected by the mutation harness", "why": "injected",
            "options": ["a", "b"], "evidence_line": "injected",
            "spoken_heading": "WHETHER THE MUTATION HARNESS IS DETECTED",
        }
        DETAIL.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        m1 = _run_guard()
        results.append(("M1 an unrendered authored heading on a NEW identifier",
                        m1, "caught" if m1 else "MISSED -- the check is blind "
                        "to the very shape it was written for"))

        # M2: the vacuity floor. Strip every heading and the first 2 tests pass
        # on nothing, so the anti-vacuity test must fire.
        d2 = {k: v for k, v in json.loads(original.decode()).items()
              if not (k.startswith("task:") and isinstance(v, dict))}
        DETAIL.write_text(json.dumps(d2, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        m2 = _run_guard()
        results.append(("M2 every authored heading removed (the vacuity floor)",
                        m2, "caught" if m2 else "MISSED -- the first 2 tests "
                        "would pass on nothing"))
    finally:
        DETAIL.write_bytes(original)
        after = hashlib.sha256(DETAIL.read_bytes()).hexdigest()

    print("=" * 74)
    print("DOES THE INVERSE-DIRECTION CHECK DISCRIMINATE?")
    print("=" * 74)
    for name, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    print()
    print(f"  authored detail restored byte-for-byte: {after == before}")
    print(f"    sha256 before {before[:16]}  after {after[:16]}")
    n = sum(1 for _, ok, _ in results if ok)
    print(f"  {n} of {len(results)} propert(ies) hold")
    return 0 if n == len(results) and after == before else 1


if __name__ == "__main__":
    raise SystemExit(main())
