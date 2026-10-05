# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: f565286ee09d04874dddd1afa30391631a79b68dcd69b0977eb045733ad52ebe
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Mutation harness: `co_names`/`co_consts` wiring probes, false pass and false fail.

WHY THIS EXISTS (panel review 2026-10-05, claude seat). CC1 converted 3 source-text
assertions into checks that read `run_experiment.__code__.co_names` and `.co_consts`,
and the brief asks whether that is genuinely stronger or a swapped proxy. This script
answers it by MUTATING `bench/reference_runner_v3.py` in place, running
`bench/tests/test_in_round_falsifier_clears_only_on_execution_2026-10-05.py`, and
restoring the file byte-for-byte (sha256 compared).

RESULTS, 2026-10-05, Python 3.x on this checkout:

  baseline                                                   18 passed
  M1  persist key DELETED outright                            1 failed  (caught)
  M2  call site severed (callee renamed)                      1 failed  (caught)
  M3  persist DELETED, key kept as a live top-level literal
      in a neighbouring expression                           18 passed  <-- FALSE PASS
  M4  persist key hoisted to a module constant
      (`_KEY_REATTACH = "round_..."`), a CORRECT refactor      1 failed  <-- FALSE FAIL

So `co_consts` membership is a check on the PRESENCE OF A STRING LITERAL in a
syntactic role it cannot distinguish, not on the record being persisted. M3 drops the
per-round record from the state payload and every test still passes.

Two corrections to things said about this check in the panel round:

  * `x in code.co_consts` is EQUALITY membership on a tuple, not substring. A longer
    log-message literal CONTAINING the key does NOT satisfy it (measured: 1 entry
    exactly equal to the key, 0 entries containing-but-unequal). The claim that any
    log message containing the token would satisfy the check is wrong.
  * `run_experiment.__code__.co_consts[0]` IS the docstring (measured True), but for
    an equality check that only matters if the docstring IS the key, so the docstring
    hole as stated does not exist either.
  * The real brittleness runs the other way and is broader than reported: any literal
    moved inside a tuple/set literal, a nested comprehension, or a module constant
    becomes a NESTED constant object and vanishes from the top-level `co_consts`.
    Confirmed: wrapping the key in a 2-tuple also produced a false fail.

MUTATION COUNT. Each mutation failed EXACTLY ONE test, not two. The brief's "2 tests
fail per mutation" does not reproduce here; the fable seat reported the same.

WARNING: this script WRITES to bench/reference_runner_v3.py and restores it. It
refuses to run if the file is not restorable. Pass --run to execute.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
TARGET = REPO / "bench" / "reference_runner_v3.py"
TEST = "bench/tests/test_in_round_falsifier_clears_only_on_execution_2026-10-05.py"
PERSIST = ('            "round_falsifier_reattachments": '
           'round_falsifier_reattachments,\n')

MUTATIONS = [
    ("M1 persist key DELETED outright", lambda s: s.replace(PERSIST, "")),
    ("M2 call site severed (callee renamed)",
     lambda s: s.replace(
         "            _fr = record_in_round_falsifier_reattachments(\n",
         "            _fr = _severed_for_mutation_test(\n").replace(
         "def record_in_round_falsifier_reattachments(",
         'def _severed_for_mutation_test(*a, **k):\n'
         '    return {"executed": 0, "cleared": 0, "seen": 0}\n\n\n'
         "def record_in_round_falsifier_reattachments(", 1)),
    ("M3 persist DELETED, key kept as a live top-level literal",
     lambda s: s.replace(
         PERSIST,
         '            "migrated": bool(round_falsifier_reattachments) and '
         'bool("round_falsifier_reattachments"),\n')),
    ("M4 key hoisted to a module constant (a CORRECT refactor)",
     lambda s: s.replace(
         PERSIST, "            _KEY_REATTACH: round_falsifier_reattachments,\n"
     ).replace("def record_in_round_falsifier_reattachments(",
               '_KEY_REATTACH = "round_falsifier_reattachments"\n\n\n'
               "def record_in_round_falsifier_reattachments(", 1)),
]


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _run() -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", TEST, "-q"],
                       cwd=REPO, capture_output=True, text=True)
    tail = [ln for ln in r.stdout.splitlines() if "passed" in ln or "failed" in ln]
    return r.returncode, (tail[-1] if tail else "(no summary)")


def main() -> int:
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        print(f"\nusage: {sys.argv[0].split('/')[-1]} --run")
        return 0
    # AN UNRECOGNISED FLAG IS REFUSED LOUDLY, not read as data and not exited 0
    # on. Caught by `bench/tests/test_operational_scripts.py::
    # TestUsageTextAdvertisesOnlyImplementedFlags` against this very file: the
    # first form tested only `"--run" not in argv` and exited 0 on anything else,
    # so a typo'd flag reported "refusing to mutate" and a caller would believe a
    # clean exit meant the harness had run.
    unknown = [a for a in sys.argv[1:] if a not in ("--run",)]
    if unknown:
        print(f"  unrecognised argument(s): {unknown}")
        print(f"  usage: {sys.argv[0].split('/')[-1]} [--run]")
        return 2
    if "--run" not in sys.argv[1:]:
        print("  refusing to mutate the tree without --run")
        print(f"  usage: {sys.argv[0].split('/')[-1]} --run")
        return 0

    original = TARGET.read_text(encoding="utf-8")
    if original.count(PERSIST) != 1:
        print("  the persist line is no longer present exactly once; this harness "
              "describes a shape that has changed. Refusing to mutate.")
        return 1
    with tempfile.TemporaryDirectory() as td:
        bak = pathlib.Path(td) / "rr3.bak"
        shutil.copy2(TARGET, bak)
        before = _sha(TARGET)
        rc, summary = _run()
        print(f"  {'baseline':<58} {summary}")
        verdicts = []
        try:
            for name, mut in MUTATIONS:
                TARGET.write_text(mut(original), encoding="utf-8")
                rc, summary = _run()
                flag = "CAUGHT" if rc != 0 else "*** NOT CAUGHT ***"
                print(f"  {name:<58} {summary:<28} {flag}")
                verdicts.append((name, rc != 0))
                TARGET.write_text(original, encoding="utf-8")
        finally:
            shutil.copy2(bak, TARGET)
        assert _sha(TARGET) == before, "FAILED TO RESTORE the target file"
        print(f"\n  target restored, sha256 identical: {_sha(TARGET) == before}")
    missed = [n for n, caught in verdicts if not caught]
    print()
    print("  READING IT. A mutation NOT CAUGHT is a FALSE PASS of the probe: the")
    print("  record is no longer persisted and the test is green. A CORRECT refactor")
    print("  that IS caught (M4) is a FALSE FAIL. The probe has both, so it is one")
    print("  rung stronger than source-text matching -- immune to comments -- and")
    print("  still a static reference proxy, not evidence of execution.")
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
