#!/usr/bin/env python3
"""P-pass the apply-back baseline repair, and measure whether its 2 halves compose.

A FIX I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. This calls the live
`_apply_back_gate` on 4 candidate classes and requires a TRUE verdict on each:

  1. prose fed its own bytes          -> REJECT, naming prose as the reason
  2. prose sharing no content         -> REJECT, naming prose as the reason
  3. a Python no-op                   -> ACCEPT, noting the pre-existing failures
  4. a Python candidate that shadows  -> REJECT, naming the NEW failing node-ids
     the class the suite imports

Class 4 is the ANTI-VACUITY check. A gate repaired into accepting everything
would satisfy 1 to 3 and be worse than the defect it replaced.

THE COMPOSABILITY MEASUREMENT, because `composability-requires-a-measurement` is
a project standard and the founder's definition excludes the weak reading. His
words, 2026-10-02: *"Composability doesn't mean composing two solutions just
because they can be composed. It means this principle should be applied where two
composed solutions demonstrably provide a better, more robust and/or more
efficient solution than either fix in isolation."*

The repair has 2 parts, and each is simulated in isolation here rather than
asserted to be necessary:

  (A) the BASELINE comparison -- a failure present without the candidate is not
      blamed on it. Simulated OFF by seeding the cache with an empty baseline,
      which is exactly what the old code assumed.
  (B) the PROSE REFUSAL hoisted above the command check. Simulated OFF by making
      `is_python_target` return True, which is the state the old nesting left the
      function in whenever a command was configured.

NAMED PROPERTY: the number of the 4 classes receiving a verdict that is TRUE of
the candidate.

THE PREDICTION, THE APPARENT REFUTATION, AND WHY THE REFUTATION WAS THE
INSTRUMENT -- all 3 recorded, because the middle step was wrong and was reported.

PREDICTED: (A) alone FALSELY ACCEPTS prose, since prose cannot change a Python
suite's failure set and so its difference from the baseline is empty; (B) alone
FALSELY REJECTS a Python no-op, because without a baseline the sandbox's
pre-existing failures look new.

APPARENTLY REFUTED: the first run showed (A) alone REJECTING prose for
`ast:invalid syntax`, and that was written up here as the prediction being half
wrong.

THE REFUTATION WAS MY OWN SIMULATION. Disabling the hoisted refusal by making
`is_python_target` return True also re-enabled the `ast.parse` branch for prose,
which reproduces the pre-2026-10-17 defect instead of the half-fix under test.
`_apply_back_gate` makes exactly 2 consultations of that predicate per call,
always in the same order -- syntax branch first, hoisted refusal second -- which
was verified by execution rather than by reading. `_only_defeat_the_hoisted_refusal` now answers the first call
truthfully and the second with True.

CONFIRMED on the faithful simulation: (A) alone ACCEPTS both prose candidates,
reporting `ok (no new failures; 3 pre-existing, baseline rc1)`. The prediction
held. A FALSE ACCEPT is worse than the false reject it would replace, which is
the strongest part of the case for keeping both halves.

The lesson is the one in `feedback_a_correction_needs_checking_too_2026-10-11`:
a withdrawal needs the same scrutiny as the claim it withdraws.

Companion producer for the defect itself:
`scripts/the_apply_back_gate_has_no_baseline_2026-11-02.py`.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

TEST_CMD = ("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
            "bench/tests/test_immune_memory_evaluation.py -q")
PROSE_TARGET = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
PY_NOOP_TARGET = "bench/runner_core.py"
#: The suite imports `ImmuneMemory` from here, so shadowing it breaks real tests.
PY_BREAK_TARGET = "bench/dm/_memory.py"

#: Appended to the real module. Syntactically valid, so `ast.parse` passes it and
#: the refusal must come from the SUITE rather than from the syntax check.
SHADOW = '''

# PROBE ONLY -- shadows the class the gate's suite imports, so real tests fail.
class ImmuneMemory:  # noqa: F811
    def __init__(self, *a, **k):
        pass
'''


def _cases(repo: pathlib.Path):
    prose = (repo / PROSE_TARGET).read_text(encoding="utf-8")
    unrelated = ("# A DOCUMENT THAT IS NOT THE TARGET\n\n"
                 "This text shares no sentence with the specification "
                 "it replaces.\n" * 40)
    py_noop = (repo / PY_NOOP_TARGET).read_text(encoding="utf-8")
    py_break = (repo / PY_BREAK_TARGET).read_text(encoding="utf-8") + SHADOW
    return [
        ("1 prose fed its own bytes", prose, PROSE_TARGET,
         False, "no suite can gate a non-Python target"),
        ("2 prose sharing no content", unrelated, PROSE_TARGET,
         False, "no suite can gate a non-Python target"),
        ("3 a Python no-op", py_noop, PY_NOOP_TARGET,
         True, "no new failures"),
        ("4 a Python candidate shadowing ImmuneMemory", py_break, PY_BREAK_TARGET,
         False, "suite_regressed"),
    ]


def _only_defeat_the_hoisted_refusal(real):
    """Answer truthfully once per gate call, then True.

    `_apply_back_gate` consults `is_python_target` exactly twice and always in
    the same order: the syntax branch first, the hoisted prose refusal second.
    Patching the predicate outright defeats BOTH, which re-enables `ast.parse`
    on prose and simulates the pre-2026-10-17 defect instead of the half-fix
    under test. This wrapper leaves the syntax branch exactly as shipped.
    """
    state = {"n": 0}

    def wrapper(path):
        state["n"] += 1
        return real(path) if state["n"] % 2 == 1 else True

    return wrapper, state


def _verdicts(rr, *, baseline_on: bool, prose_refusal_on: bool):
    """Run all 4 classes under one configuration of the 2 halves."""
    saved_is_python = rr.is_python_target
    rows = []
    try:
        if not prose_refusal_on:
            wrapper, _state = _only_defeat_the_hoisted_refusal(saved_is_python)
            rr.is_python_target = wrapper
        for name, src, rel, want_ok, want_sub in _cases(REPO):
            if not prose_refusal_on:
                # RESTART THE PARITY PER CANDIDATE. One gate call makes exactly 2
                # consultations; carrying the counter across candidates would
                # invert which call is answered truthfully on every second one.
                wrapper, _state = _only_defeat_the_hoisted_refusal(saved_is_python)
                rr.is_python_target = wrapper
            rr._APPLY_BACK_BASELINE.clear()
            if not baseline_on:
                # What the old code assumed: the sandbox is green. Seeding an
                # empty baseline with a clean exit code reproduces that exactly.
                rr._APPLY_BACK_BASELINE[(rel, TEST_CMD)] = (frozenset(), 0)
            ok, detail = rr._apply_back_gate(src, rel, TEST_CMD)
            true_verdict = (ok == want_ok) and (want_sub in detail)
            rows.append((name, ok, detail, want_ok, want_sub, true_verdict))
    finally:
        rr.is_python_target = saved_is_python
        rr._APPLY_BACK_BASELINE.clear()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("P-pass the apply-back baseline repair and measure whether "
                     "its 2 halves compose."))
    ap.add_argument("--compose", action="store_true",
                    help=("also run the 2 half-fixes in isolation; this triples "
                          "the cost, so it is OFF by default"))
    args = ap.parse_args()

    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as rr

    print("=" * 76)
    print("DOES THE REPAIRED APPLY-BACK GATE GIVE A TRUE VERDICT ON EACH CLASS?")
    print("=" * 76)
    full = _verdicts(rr, baseline_on=True, prose_refusal_on=True)
    for name, ok, detail, want_ok, want_sub, good in full:
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
        print(f"         got    : {'ACCEPT' if ok else 'REJECT'} — {detail[:96]}")
        print(f"         wanted : {'ACCEPT' if want_ok else 'REJECT'} "
              f"containing {want_sub!r}")
    n_full = sum(1 for *_x, good in full if good)
    print(f"\n  BOTH HALVES: {n_full} of {len(full)} classes get a true verdict")

    rows = {"A+B (as shipped)": n_full}
    if args.compose:
        print("\n" + "=" * 76)
        print("DO THE 2 HALVES COMPOSE? EACH IN ISOLATION, SAME 4 CLASSES")
        print("=" * 76)
        for label, b_on, p_on in [
                ("A only  (baseline, no prose refusal)", True, False),
                ("B only  (prose refusal, no baseline)", False, True),
                ("neither (the pre-repair behaviour)", False, False)]:
            res = _verdicts(rr, baseline_on=b_on, prose_refusal_on=p_on)
            n = sum(1 for *_x, good in res if good)
            rows[label] = n
            print(f"\n  {label}: {n} of {len(res)} true")
            for name, ok, detail, want_ok, _ws, good in res:
                mark = "ok " if good else "BAD"
                print(f"    [{mark}] {name:44s} -> "
                      f"{'ACCEPT' if ok else 'REJECT'} (wanted "
                      f"{'ACCEPT' if want_ok else 'REJECT'})")
                if not good:
                    print(f"           {detail[:92]}")

        print("\n  --- the named property: classes with a TRUE verdict ---")
        for label, n in rows.items():
            print(f"    {label:40s} {n} of 4")
        best_single = max(rows.get("A only  (baseline, no prose refusal)", -1),
                          rows.get("B only  (prose refusal, no baseline)", -1))
        dominates = rows["A+B (as shipped)"] > best_single
        print(f"\n    composed > best single half : {dominates}")
        if dominates:
            print("    => The pair DOMINATES either half alone on the named")
            print("       property, which is what the composability standard asks")
            print("       for. Neither half is redundant.")
        else:
            print("    => The pair does NOT dominate. Under the composability")
            print("       standard the single better fix is to be PREFERRED, and")
            print("       this repair should be reduced to it.")

    bad = [n for n, _ok, _d, _w, _s, good in full if not good]
    print()
    if bad:
        print("  THE REPAIR DOES NOT HOLD ON:")
        for b in bad:
            print(f"    - {b}")
        return 1
    if args.compose and not dominates:
        print("  THE COMPOSED FIX IS NOT JUSTIFIED BY THIS MEASUREMENT.")
        return 1
    print("  Every class gets a true verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
