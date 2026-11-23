#!/usr/bin/env python3
"""Does the B164 ratchet guard go RED? 5 mutations, 1 per contract.

★ R2 WAS RE-AIMED. Its first form applied cc2's remedy as that seat STATED it --
`min` over the same trailing window -- and C1 stayed GREEN. That was not a blind
spot: a windowed min still grows with the series, so the ratchet genuinely
persists and C1 was right to say so. The remedy that works is an UNWINDOWED
statistic, and R2 now applies that one. A mutation aimed at a change that does
not alter the behaviour tests nothing.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SUBJECT = REPO / "scripts" / "does_the_ratchet_need_an_endogenous_record_2026-11-13.py"
GUARD = "bench/tests/test_the_ratchet_needs_both_conditions_2026-11-13.py"

MUTATIONS = [
    ("R1 the record discipline stops filtering",
     "test_c4_the_endogenous_record_only_ever_holds_admitted_values",
     "        if endogenous:\n            if ok:\n                record.append(v)\n"
     "        else:\n            record.append(v)",
     "        record.append(v)",
     "endogenous and exogenous become the same run, so every other contract "
     "compares a thing with itself"),

    ("R2 the remedy that WORKS is applied: an unwindowed statistic",
     "test_c1_a_growing_series_defeats_the_bound_whatever_the_record",
     "    return max(FLOOR, HEADROOM * max(record[-WINDOW:]))",
     "    return max(FLOOR, HEADROOM * min(record))",
     "the ratchet STOPS, so C1 must notice -- a contract that cannot see the "
     "remedy working is not measuring the defect"),

    ("R3 the bound refuses nothing",
     "test_c3_the_bound_still_refuses_a_genuine_excursion",
     "    if not record:\n        return FLOOR",
     "    return float('inf')\n    if not record:\n        return FLOOR",
     "a bound that admits everything is decorative"),

    ("R4 half the conclusion is dropped from the record",
     "test_c5_neither_half_alone_is_recorded_as_sufficient",
     "  Neither constraint is redundant",
     "  (the second constraint is optional)",
     "a reader takes 1 half and builds a bound that ratchets"),

    ("R5 the windowed-defeat condition inverted",
     "test_c6_a_windowed_statistic_is_not_non_increasing",
     "    return growth_per_step ** window < headroom",
     "    return growth_per_step ** window > headroom",
     "the predicate stops agreeing with the measurement it was derived from"),
]


def run(selector: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", GUARD, "-k", selector,
                        "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr)[-300:]


def main() -> int:
    original = SUBJECT.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    print(f"subject : {SUBJECT.relative_to(REPO)}  sha256 {digest[:16]}\n")
    rc, tail = run(" or ".join(m[1] for m in MUTATIONS))
    if rc != 0:
        print(f"REFUSED: baseline is already red (rc={rc}).\n{tail}")
        return 2
    print("BASELINE GREEN\n")
    red, results = 0, []
    try:
        for name, selector, old, new, why in MUTATIONS:
            src = original.decode()
            if old not in src:
                print(f"  {name}: ANCHOR NOT FOUND -- proves nothing")
                results.append((name, "ANCHOR MISSING"))
                continue
            SUBJECT.write_text(src.replace(old, new, 1))
            rc, tail = run(selector)
            ok = rc != 0
            red += ok
            results.append((name, "RED" if ok else "STILL GREEN"))
            print(f"  {name}\n    target  : {selector}\n    why     : {why}")
            print(f"    verdict : {'RED (caught)' if ok else 'STILL GREEN -- BLIND'}")
            if not ok:
                print(f"    tail    : {tail.strip()[:200]}")
            SUBJECT.write_bytes(original)
    finally:
        SUBJECT.write_bytes(original)
        back = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
        print(f"\nrestore verified: {back[:16]} == {digest[:16]} -> {back == digest}")
        assert back == digest, "THE RESTORE FAILED -- the subject is left mutated"
    print(f"\nmutations_red = {red} of {len(MUTATIONS)}")
    for n, v in results:
        print(f"    {v:<14} {n}")
    rc, _ = run(" or ".join(m[1] for m in MUTATIONS))
    print(f"\npost-restore baseline: {'GREEN' if rc == 0 else f'RED (rc={rc})'}")
    return 0 if red == len(MUTATIONS) and rc == 0 else 1


if __name__ == "__main__":
    # A `--help` MUST NOT run: this script WRITES, mutating a tracked file
    # in place and restoring it from the bytes it read first.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
