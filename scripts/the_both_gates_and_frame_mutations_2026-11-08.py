"""Do B76's AND and B121's de-duplication actually REFUSE? 5 reversions.

A guard that has never been seen to fail is a hypothesis. This reverses 5
specific properties of the 2 repairs built on his rulings of 2026-11-08 and
requires the relevant guard to go RED for each, restoring the exact bytes
afterwards and verifying the restore by sha256.

RESTORATION IS BY SAVED BYTES, NOT BY ``git checkout --``, which has destroyed
uncommitted work in this project's record. One of the subjects here is
``bench/reference_runner_v3.py``, the live runner, so a failed restore is
reported as a REFUSAL and the harness stops rather than carrying on with a
mutated runner in the tree.

WHAT EACH REVERSION TARGETS:
  1. B76's composition becomes an OR again -- the exact defect, where a pair of
     criteria is strictly WEAKER than either member and the state gate alone
     stopped the 2026-11-02 run while the hardened gate logged "not met".
  2. The live loop stops calling the composition -- an addition nothing reaches
     is not additive, and this project has confirmed that shape 11 times.
  3. The reason stops naming which side dissented -- a run that declines to
     stop for an unnamed reason cannot be retraced, which is his standing
     requirement.
  4. B121's de-duplication is removed -- and this is the reversion that matters
     most, because the 3 re-derived FLOORS cannot catch it. Dropping the
     resolve step RAISES every count, so a `>=` floor passes happily on a
     double-counted frame. The property had to be asserted on the FRAME.
  5. A floor is put back to its pre-correction value -- so that the floors are
     shown to be load-bearing too, and not merely decorative beside the frame
     assertion.
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

RUNNER = REPO / "bench/reference_runner_v3.py"
PRODUCER = REPO / "scripts/the_severity_proxy_was_never_tested_2026-10-28.py"
G76 = REPO / "bench/tests/test_both_gates_must_agree_2026-11-08.py"
G121 = REPO / "bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py"


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _run(target: pathlib.Path, node: str) -> tuple[int, str]:
    sel = f"{target}::{node}" if node else str(target)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", sel, "-q", "-p", "no:randomly",
         "--no-header", "-x"],
        capture_output=True, text=True, timeout=900, cwd=str(REPO))
    return r.returncode, (r.stdout + r.stderr)[-400:]


MUTATIONS = (
    ("1 the composition becomes an OR again", RUNNER,
     "    if state_converged and gamma_converged:",
     "    if state_converged or gamma_converged:",
     G76, "test_it_is_an_and_and_not_an_or"),
    ("2 the live loop stops calling it", RUNNER,
     "        converged, conv_reason = both_gates_agree(",
     "        _unused_converged, _unused_reason = both_gates_agree(",
     G76, "test_the_live_site_calls_it"),
    ("3 the reason stops naming the dissenter", RUNNER,
     'f"[{state_reason}]; gamma gate DISSENTS [{gamma_reason}]")',
     'f"[{state_reason}]; gamma gate [{gamma_reason}]")',
     G76, "test_the_state_gate_alone_no_longer_terminates"),
    ("4 B121's de-duplication is removed", PRODUCER,
     "        if _key in _seen:\n            continue\n",
     "        if False:\n            continue\n",
     G121, "TestTheCorpusIsABoundaryBand::test_the_sampling_frame_counts_no_run_twice"),
    ("5 a floor goes back to its pre-correction value", G121,
     'assert produced["archive_n"] >= 3094, (',
     'assert produced["archive_n"] >= 3237, (',
     G121, "TestTheCorpusIsABoundaryBand::test_the_archive_spans_the_full_range"),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", type=int, default=None)
    args = ap.parse_args()

    for p in (RUNNER, PRODUCER, G76, G121):
        if not p.is_file():
            print(f"REFUSED: {p} is not in this checkout")
            return 1

    print("NODE PATHS ARE VERIFIED FIRST, because a node that does not exist")
    print("makes pytest exit non-zero and a reversion then reads as RED for")
    print("the wrong reason -- which is what the first draft of this harness did.")
    for label, _s, _f, _r, guard, node in MUTATIONS:
        if not node:
            continue
        chk = subprocess.run(
            [sys.executable, "-m", "pytest", f"{guard}::{node}",
             "--collect-only", "-q", "-p", "no:randomly"],
            capture_output=True, text=True, timeout=300, cwd=str(REPO))
        if chk.returncode != 0 or "no tests ran" in (chk.stdout + chk.stderr):
            print(f"  REFUSED: {guard.name}::{node} does not collect, so "
                  f"reversion {label.split()[0]} would prove nothing")
            return 1
    print("  all node paths collect\n")

    print("BASELINE: both guards must be GREEN before anything is reversed.")
    for g in (G76, G121):
        rc, tail = _run(g, "")
        print(f"  {g.name}: exit {rc}")
        if rc != 0:
            print(f"REFUSED: a baseline is red, so a red after a mutation "
                  f"would prove nothing.\n{tail}")
            return 1

    red = ran = 0
    for label, subject, find, repl, guard, node in MUTATIONS:
        if args.only is not None and not label.startswith(str(args.only)):
            continue
        ran += 1
        original = subject.read_bytes()
        before = _sha(original)
        text = original.decode()
        if text.count(find) != 1:
            print(f"  {label}: REFUSED -- anchor appears {text.count(find)} "
                  f"time(s) in {subject.name}; a no-op would report as green")
            continue
        try:
            subject.write_text(text.replace(find, repl, 1))
            rc, tail = _run(guard, node)
            ok = rc != 0
            red += int(ok)
            print(f"  {label}: {'RED (good)' if ok else 'STILL GREEN -- NOT GUARDED'}"
                  f"  [{guard.name}::{node.split('::')[-1]}]")
            if not ok:
                print(f"      tail: {tail.strip()[-200:]}")
        finally:
            subject.write_bytes(original)
            if _sha(subject.read_bytes()) != before:
                print(f"  REFUSED: {subject.name} did NOT restore. FIX BY HAND.")
                return 2

    print(f"\n  {red} of {ran} reversions turn the relevant guard red")
    if red == ran:
        print("  every reversed property is guarded")
        return 0
    print("  AT LEAST 1 PROPERTY IS UNGUARDED -- see the STILL GREEN lines")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
