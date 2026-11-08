"""Does the composed producer rule actually REFUSE? 7 reversions, each made red.

A guard that has never been seen to fail is a hypothesis. This reverses 7
specific properties of the 2 halves built on 2026-11-08 and requires the
relevant guard to go RED for each, then restores the exact bytes and verifies
the restore by sha256.

RESTORATION IS BY SAVED BYTES, NOT BY ``git checkout --``. That command has
destroyed uncommitted work in this project's record, and these 3 files are
uncommitted while this harness first runs. Each subject's bytes are read before
the mutation and written back afterwards, and the sha256 is compared; a failure
to restore is reported as a REFUSAL rather than passed over, because leaving a
mutated guard in the tree is worse than any finding here.

WHAT EACH MUTATION REVERSES, and why that property is the load-bearing one:
  1. A drops a producer from MUST_RUN -> the accounting must report it
     UNDECLARED, which is the test that caught 13 unlisted producers in the
     2026-11-03 sibling.
  2. A's decision returns an empty list for every input -> a checker that
     decides nothing is this project's most-confirmed defect shape, so the
     decision's own anti-vacuity partner must fire.
  3. A's exemption reason is reduced to 1 character -> an exemption nobody can
     argue with is not an exemption.
  4. A carries a timeout for a producer it does not run -> an addition nothing
     reaches.
  5. B's verdict returns no refusal for any input -> the ratchet becomes a
     rubber stamp.
  6. B's pin is emptied -> the ratchet must then refuse the whole backlog, which
     proves the comparison is live rather than short-circuited.
  7. The pin is padded with names that are not on disk -> a pin can otherwise
     admit arbitrary debt by listing files that never existed.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
if not REPO.is_dir():
    REPO = pathlib.Path(__file__).resolve().parents[1]

A = REPO / "bench/tests/test_tonights_producers_are_reached_2026-11-08.py"
B = REPO / "bench/tests/test_an_unreached_producer_set_cannot_grow_2026-11-08.py"
PIN = REPO / "experimental_notes/data/unreached_producers_2026-11-08.json"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _run(target: pathlib.Path, node: str) -> tuple[int, str]:
    argv = [sys.executable, "-m", "pytest", f"{target}::{node}",
            "-q", "-p", "no:randomly", "--no-header", "-x"]
    r = subprocess.run(argv, capture_output=True, text=True,
                       timeout=900, cwd=str(REPO))
    return r.returncode, (r.stdout + r.stderr)[-500:]


#: (label, subject, find, replace, guard, node that must go red)
MUTATIONS = (
    ("1 A drops a producer from MUST_RUN", A,
     '    "a4_doors_are_shared_2026-11-08.py",\n', "",
     A, "test_every_2026_11_08_producer_is_accounted_for"),
    ("2 A's decision refuses nothing", A,
     "    out: list[str] = []\n",
     "    out: list[str] = []\n    return out\n",
     A, "test_the_decision_can_actually_refuse"),
    ("3 A's exemption states no reason", A,
     '"the_line_reference_mutations_2026-11-08.py": "invokes pytest; would recurse"',
     '"the_line_reference_mutations_2026-11-08.py": "x"',
     A, "test_the_exemptions_each_state_a_mechanical_reason"),
    ("4 A times out a producer it does not run", A,
     '    "a_rule_excluded_from_blocking_still_blocks_2026-11-08.py": 600,\n',
     '    "a_rule_excluded_from_blocking_still_blocks_2026-11-08.py": 600,\n'
     '    "a_producer_this_guard_never_runs_2026-11-08.py": 600,\n',
     A, "test_the_timeout_overrides_name_a_listed_producer"),
    ("5 B's verdict refuses nothing", B,
     "    return (set(now) - set(pin), set(pin) - set(now))",
     "    return (set(), set(pin) - set(now))",
     B, "test_a_swap_at_a_constant_total_is_refused"),
    ("6 B's pin is emptied", B,
     '    return set(json.loads(PIN.read_text())["unreached"])',
     "    return set()",
     B, "test_no_producer_is_unreached_outside_the_pin"),
    ("7 the pin is padded with absent names", PIN,
     '"unreached": [',
     '"unreached": [\n  '
     + ",\n  ".join(f'"a_file_that_does_not_exist_{i}_2026-01-01.py"'
                    for i in range(400)) + ",",
     B, "test_the_pin_is_not_padded_with_names_that_do_not_exist"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", type=int, default=None,
                    help="run just one mutation, by its leading number")
    args = ap.parse_args()

    for p in (A, B, PIN):
        if not p.is_file():
            print(f"REFUSED: {p} is not in this checkout")
            return 1

    print("BASELINE: both guards must be GREEN before anything is reversed.")
    for g in (A, B):
        argv = [sys.executable, "-m", "pytest", str(g), "-q",
                "-p", "no:randomly", "--no-header"]
        r = subprocess.run(argv, capture_output=True, text=True,
                           timeout=1800, cwd=str(REPO))
        print(f"  {g.name}: exit {r.returncode}  "
              f"{(r.stdout.strip().splitlines() or ['(no output)'])[-1]}")
        if r.returncode != 0:
            print("REFUSED: a baseline is red, so a red after a mutation would "
                  "prove nothing. Fix the baseline first.")
            return 1

    red = 0
    ran = 0
    for label, subject, find, repl, guard, node in MUTATIONS:
        if args.only is not None and not label.startswith(str(args.only)):
            continue
        ran += 1
        original = subject.read_bytes()
        before = _sha(original)
        text = original.decode()
        if text.count(find) < 1:
            print(f"  {label}: REFUSED -- anchor not found in {subject.name}; "
                  f"the mutation would have been a no-op reported as green")
            continue
        mutated = text.replace(find, repl, 1)
        if mutated == text:
            print(f"  {label}: REFUSED -- replacement changed nothing")
            continue
        try:
            subject.write_text(mutated)
            rc, tail = _run(guard, node)
            ok = rc != 0
            red += int(ok)
            print(f"  {label}: {'RED (good)' if ok else 'STILL GREEN -- the '
                  'property is NOT guarded'}  [{guard.name}::{node}]")
            if not ok:
                print(f"      tail: {tail.strip()[-220:]}")
        finally:
            subject.write_bytes(original)
            after = _sha(subject.read_bytes())
            if after != before:
                print(f"  REFUSED: {subject.name} did NOT restore "
                      f"({before[:12]} -> {after[:12]}). FIX THIS BY HAND.")
                return 2

    print()
    print(f"  {red} of {ran} reversions turn the relevant guard red")
    if red == ran:
        print("  every reversed property is guarded")
        return 0
    print("  AT LEAST 1 PROPERTY IS UNGUARDED -- see the STILL GREEN lines")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
