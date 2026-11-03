#!/usr/bin/env python3
"""Revert the asking-is-not-answering fix and require its guard to go red.

THE DEFECT THE FIX CLOSES. In
`scripts/which_entries_ask_for_a_ruling_he_has_given_2026-11-01.py`, `ASKS`
matches `NEEDS HIS RULING` and `GAVE` matches `HIS RULING` -- a SUBSTRING of it.
So the sentence asking him to rule satisfied the pattern for him having ruled,
and the producer reported entries as recording a ruling whose only "ruling" was
the request for one. Measured before the repair: of 35 entries matching `ASKS`,
31 matched `GAVE` somewhere and **6 matched it ONLY inside the asking phrase, 6
of 31, 0.193548, Wilson 95% [0.091870, 0.362803]**. 3 of those 6 -- B82, B83 and
B87 -- are entries genuinely awaiting his decision, so the error ran in the
direction that tells a reader he has already ruled where he has not. After the
repair the "also recording a ruling" count falls from 9 to 5 across the live
entries, and the 5 that remain are checked by hand in the guard's own notes.

A FIX I HAVE NOT TRIED TO BREAK IS A HYPOTHESIS. Each mutation below undoes one
property and runs
`bench/tests/test_asking_is_not_answering_2026-11-02.py` against it. A mutation
that leaves the guard GREEN is a GAP, named as such, because it identifies a
property the guard does not actually hold.

THE SUBJECT IS RESTORED BY HASH, NOT BY HOPE.
`feedback_a_harness_must_restore_what_it_found_2026-11-01` records a harness that
destroyed the work it was measuring. The original bytes are held in memory,
written back in a `finally`, and the sha256 compared before the exit code is
decided. `git checkout --` is deliberately not used.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBJECT = (REPO / "scripts"
           / "which_entries_ask_for_a_ruling_he_has_given_2026-11-01.py")
GUARD = REPO / "bench" / "tests" / "test_asking_is_not_answering_2026-11-02.py"

#: (name, what it reverts, find, replace). Each `find` must occur exactly once.
MUTATIONS = [
    (
        "M1 the caller goes back to the raw GAVE pattern",
        "the masking entirely, which is the pre-repair behaviour",
        "    both = [e for e in asking if gave_outside_the_ask(e.text)]",
        "    both = [e for e in asking if GAVE.search(e.text)]  # MUTANT",
    ),
    (
        "M2 the mask covers only the FIRST asking phrase",
        "masking every ask, so a 2nd ask in one entry is unmasked",
        "    spans = [m.span() for m in ASKS.finditer(text)]",
        "    spans = [m.span() for m in list(ASKS.finditer(text))[:1]]  # MUTANT",
    ),
    (
        "M3 the mask is emptied, so nothing is ever masked",
        "the mask's contents while keeping its shape -- the vacuity floor",
        "    for g in GAVE.finditer(text):\n"
        "        if not any(s <= g.start() < e for s, e in spans):\n"
        "            return g\n"
        "    return None",
        "    for g in GAVE.finditer(text):  # MUTANT: mask ignored\n"
        "        return g\n"
        "    return None",
    ),
    (
        "M4 the mask is built from a hand-written literal, not from ASKS",
        "the derivation from the other pattern's own matches, which is what "
        "stops the 2 drifting apart",
        "    spans = [m.span() for m in ASKS.finditer(text)]\n",
        "    import re as _m  # MUTANT: a separate literal list\n"
        "    spans = [m.span() for m in _m.finditer(r'NEEDS HIS RULING', text)]\n",
    ),
]


def measure_self_match() -> tuple[int, int, list]:
    """How many entries matched GAVE ONLY inside their asking phrase?

    ★ ADDED 2026-11-02 BECAUSE THE FIGURE WAS QUOTED TO HIM WITH NO PRODUCER.
    `measured-rate-travels-with-its-script` makes a rate cited from prose a
    claim about evidence rather than evidence, and 6 of 31 was exactly that
    until this function existed. It reconstructs the PRE-FIX behaviour from the
    2 patterns rather than from a saved number, so it cannot drift: an entry
    counts when `GAVE` finds a match and every one of those matches falls
    inside a span `ASKS` matched.
    """
    import re as _re
    ns: dict = {"__name__": "_m", "__file__": str(SUBJECT)}
    exec(compile(SUBJECT.read_text(), str(SUBJECT), "exec"), ns)
    ASKS, GAVE = ns["ASKS"], ns["GAVE"]
    text = (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
        errors="replace")
    blocks = _re.split(r"(?=^\*\*[A-Z]*[0-9]+\.)", text, flags=_re.M)
    gave_any, only_inside, names = 0, 0, []
    for b in blocks:
        if not ASKS.search(b):
            continue
        spans = [m.span() for m in ASKS.finditer(b)]
        gs = list(GAVE.finditer(b))
        if not gs:
            continue
        gave_any += 1
        if not any(not any(s <= g.start() < e for s, e in spans) for g in gs):
            only_inside += 1
            c = _re.match(r"\*\*([A-Z]*[0-9]+)\.", b)
            names.append(c.group(1) if c else "?")
    return only_inside, gave_any, names


def _run_guard() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(GUARD), "-q", "--no-header",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(REPO), timeout=600,
    )
    lines = [ln for ln in (r.stdout + r.stderr).strip().splitlines() if ln.strip()]
    return r.returncode == 0, (lines[-1] if lines else "")


def main() -> int:
    argparse.ArgumentParser(
        description=("Revert the asking-is-not-answering fix and require its "
                     "guard to go red.")).parse_args()

    original = SUBJECT.read_bytes()
    h0 = hashlib.sha256(original).hexdigest()
    results: list[tuple[str, bool, str]] = []
    try:
        green, tail = _run_guard()
        results.append(("the UNMUTATED subject passes the guard", green, tail))
        if not green:
            print("  The guard fails on the unmutated subject; mutating it would")
            print(f"  prove nothing. {tail}")
            return 1
        text = original.decode()
        for name, reverts, find, repl in MUTATIONS:
            n = text.count(find)
            if n != 1:
                results.append((f"{name} [NOT APPLIED]", False,
                                f"its anchor occurs {n} times, not 1"))
                continue
            SUBJECT.write_text(text.replace(find, repl, 1), encoding="utf-8")
            red, tail = _run_guard()
            SUBJECT.write_bytes(original)
            results.append((name, not red,
                            tail if not red else
                            f"GAP: the guard stayed GREEN, so it does not hold "
                            f"{reverts}."))
    finally:
        SUBJECT.write_bytes(original)

    h1 = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()
    restored = h0 == h1
    print("=" * 76)
    print("DOES THE GUARD NOTICE THE ASK-MASKING BEING UNDONE?")
    print("=" * 76)
    k, n, names = measure_self_match()
    print(f"\n  THE RATE THIS FIX ADDRESSES, measured now rather than quoted:")
    print(f"    entries matching GAVE somewhere          : {n}")
    print(f"    ... matching it ONLY inside the asking phrase: {k}  {names}")
    if n:
        from scipy import stats
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        clo = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
        chi = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
        print(f"    {k} of {n}, {k/n:.6f}")
        print(f"      Wilson 95%          [{lo:.6f}, {hi:.6f}]")
        print(f"      Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]")
    print()
    for name, ok, tail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {tail[:150]}")
    n_ok = sum(1 for _n, ok, _t in results if ok)
    print()
    print(f"  subject restored byte-for-byte : {restored}")
    print(f"    sha256 {h0[:16]} -> {h1[:16]}")
    print(f"  {n_ok} of {len(results)} propert(ies) hold")
    if not restored:
        print("  THE SUBJECT WAS NOT RESTORED. Fix that before anything else.")
    return 0 if (n_ok == len(results) and restored) else 1


if __name__ == "__main__":
    raise SystemExit(main())
