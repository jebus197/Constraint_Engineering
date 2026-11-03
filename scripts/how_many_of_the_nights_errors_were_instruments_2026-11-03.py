#!/usr/bin/env python3
"""How many of the night's recorded errors were in INSTRUMENTS, not subjects?

WHY THIS EXISTS: THE FIGURE WAS QUOTED TO HIM WITH NO PRODUCER. The `sv` commit
`40f213d9` carries "10 of the night's errors were in measuring instruments, not
their subjects" in its SUBJECT LINE, and the closing report of the same night
says 9. Neither number had a script behind it, which is exactly the
`measured-rate-travels-with-its-script` failure the project ruled on 2026-09-04:
a number existing only as prose is not evidence, it is a claim about evidence.
2 prose figures that disagree is the same defect twice.

WHAT IS MECHANICAL HERE AND WHAT IS NOT, STATED SO THE WEAK HALF IS NOT HIDDEN.
  MECHANICAL: the POPULATION. The night's recorded errors are the feedback
  memory files whose filename carries a date in the window. Nothing is
  hand-picked, and a file added to the window later joins the denominator.
  BY READING: the CLASSIFICATION. Whether a given error was in the instrument or
  in its subject is a judgement over the recorded text, so it is carried below as
  DATA with each item's own description quoted, item by item, rather than
  produced by a keyword rule. A keyword rule was considered and refused: this
  same night, classifying his annotations by keyword counted 46 instances of the
  English adverb "simply" as complaints about complexity, and the correction was
  his. A classifier that cannot be audited per item has no place in a figure
  quoted to him.

THE ANTI-DRIFT PROPERTY, which is the point of writing it as code. If a memory
file in the window carries no classification here, the script FAILS rather than
quietly reporting a smaller denominator. So the figure cannot be re-quoted after
the population changes without someone noticing.

DEFINITIONS.
  INSTRUMENT error: the thing that was wrong was a measuring thing -- a guard, a
  probe, a predicate, a status check, a verification, an audit, a detector, or
  the board's own reading of the tree. The subject it measured was correct, or
  its correctness was never the question.
  SUBJECT error: the thing that was wrong was the code or document being
  measured.
  PROCESS error: neither -- the instrument was right and the subject was right,
  and the fault was in how the work was sequenced.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re

MEMORY = (pathlib.Path.home() / ".claude" / "projects"
          / "-Users-georgejackson-Developer-Projects" / "memory")

#: The night's window. It spans 2 calendar dates because the session ran
#: through midnight, which is why a single-date count was wrong in both
#: directions.
WINDOW = ("2026-11-02", "2026-11-03")

#: Per-item classification, by READING each file. The key is the filename stem.
#: Each value is (class, what was actually wrong). A reader can check every row
#: against the file it names.
CLASSIFIED = {
    "feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02": (
        "INSTRUMENT",
        "a guard asserting a file does not mention an identifier failed on "
        "itself, because the identifier written as a literal entered the text "
        "being searched"),
    "feedback_a_false_positive_can_be_why_a_rule_is_unenforced_2026-11-02": (
        "INSTRUMENT",
        "a guard accused correct code, and that false positive was the stated "
        "reason a rule was only reported and never enforced"),
    "feedback_a_grep_verdict_cannot_see_its_subject_removed_2026-11-02": (
        "INSTRUMENT",
        "a status check greping for mentions could not tell existence from "
        "mention, so its verdict did not move when the subject was deleted"),
    "feedback_a_guard_can_be_outgrown_rather_than_broken_2026-11-02": (
        "INSTRUMENT",
        "a Stop hook deciding correctly was killed by the hook timeout as the "
        "transcript grew, so it stopped existing gradually rather than failing"),
    "feedback_a_probes_location_can_manufacture_the_failure_2026-11-02": (
        "INSTRUMENT",
        "a planted type error went unreported and the type checker was called "
        "vacuous; the probe's temp directory was itself the cause"),
    "feedback_a_swallowed_exception_is_not_a_record_2026-11-02": (
        "INSTRUMENT",
        "an exception caught and written into the output file read as data, so "
        "the field it was meant to fill reported nothing and nobody saw a "
        "failure"),
    "feedback_a_verification_can_pass_for_the_wrong_reason_2026-11-02": (
        "INSTRUMENT",
        "a fix re-run on different input gave a vacuous pass; the control is "
        "the SAME input returning a different verdict"),
    "feedback_never_edit_the_tree_while_a_commits_board_runs_2026-11-02": (
        "PROCESS",
        "2 of 8 guard refusals were tokenize and source-text failures caused "
        "by editing files while that commit's board was reading them -- the "
        "guards were RIGHT and the subject was right, so this is sequencing"),
    "feedback_when_a_surface_defeats_three_predicates_stop_2026-11-02": (
        "INSTRUMENT",
        "5 predicates failed on 1 surface, and the 5th established that the "
        "surface is not mechanisable with the data on hand"),
    "feedback_the_board_tests_the_tree_the_commit_records_the_index_2026-11-03": (
        "INSTRUMENT",
        "the pre-commit board reads the working tree while the commit records "
        "the index, and nothing checks the 2 agree"),
    "feedback_a_fail_safe_must_not_be_recorded_as_a_fact_2026-11-03": (
        "SUBJECT",
        "the actuator's own recorded reason asserted that a run's process was "
        "alive when no process identifier existed to check; the fail-safe was "
        "reported as an observation, and the actuator is the subject here, not "
        "the instrument"),
    "feedback_cap_the_test_that_hangs_not_the_one_you_suspect_2026-11-03": (
        "INSTRUMENT",
        "a mutation harness recorded a mutation as caught when the guard was "
        "killed by a pytest timeout, and the first repair capped the tests "
        "named for the mutation rather than the tests that were looping"),
    "feedback_two_library_names_can_be_one_route_2026-11-03": (
        "INSTRUMENT",
        "an audit of rigour by STEM import count ranked 4 of 7 producers "
        "backwards, because 2 library names can resolve to 1 verifier"),
}


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        def f(x):
            return mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(240):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def population() -> list[pathlib.Path]:
    """Every feedback memory file whose name carries a date in the window.

    DISCOVERED, never listed by hand. A hand-picked population is how a
    justifying measurement ends up excluding the very item it should examine --
    the same night, a list of 6 producers chosen by hand omitted one the session
    had itself repaired.
    """
    out = []
    for f in sorted(MEMORY.glob("feedback_*.md")):
        if any(d in f.stem for d in WINDOW):
            out.append(f)
    return out


def main() -> int:
    argparse.ArgumentParser(
        description=("Count how many of the night's recorded errors were in "
                     "measuring instruments rather than in their subjects."),
    ).parse_args()

    files = population()
    print("=" * 76)
    print("HOW MANY OF THE NIGHT'S ERRORS WERE IN THE INSTRUMENT?")
    print("=" * 76)
    print(f"  window                      : {' and '.join(WINDOW)}")
    print(f"  recorded errors in the window: {len(files)}")

    unclassified = [f.stem for f in files if f.stem not in CLASSIFIED]
    stale = [k for k in CLASSIFIED if k not in {f.stem for f in files}]
    if unclassified or stale:
        print()
        print("  THIS FIGURE IS REFUSED, because the population and the")
        print("  classification no longer match.")
        for s in unclassified:
            print(f"    NOT CLASSIFIED : {s}")
        for s in stale:
            print(f"    CLASSIFIED BUT ABSENT : {s}")
        print("  Classify the new items (or remove the stale rows) before")
        print("  quoting any count from this window.")
        return 1

    buckets: dict[str, list[tuple[str, str]]] = {}
    for f in files:
        cls, why = CLASSIFIED[f.stem]
        buckets.setdefault(cls, []).append((f.stem, why))

    for cls in sorted(buckets, key=lambda c: -len(buckets[c])):
        rows = buckets[cls]
        print()
        print(f"  {cls}: {len(rows)} of {len(files)}")
        for stem, why in rows:
            name = re.sub(r"^feedback_", "", stem)
            name = re.sub(r"_2026-11-0[23]$", "", name).replace("_", " ")
            print(f"    - {name}")
            print(f"        {why}")

    k = len(buckets.get("INSTRUMENT", []))
    n = len(files)
    (wl, wh), (cl, ch), d = _iv(k, n)
    print()
    print(f"  INSTRUMENT share : {k} of {n} = {k/n:.6f}")
    print(f"    Wilson 95%          [{wl:.6f}, {wh:.6f}]")
    print(f"    Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]  (2-route |diff| {d:.1e})")
    print()
    print(f"  SO THE FIGURE IS {k}, AND THE 2 PROSE FIGURES BOTH NEEDED CHECKING.")
    print("  The commit subject of 40f213d9 said 10 and the closing report said 9.")
    print(f"  On this population and this classification the answer is {k} of {n}.")
    # DERIVED, NOT TYPED. This sentence said "the remaining N is a PROCESS
    # error" while the data held 1 SUBJECT and 1 PROCESS -- hardcoded prose
    # failing to track the figures above it, which is the defect this script
    # exists to catch, committed inside the script itself.
    rest = {c: len(v) for c, v in buckets.items() if c != "INSTRUMENT"}
    if rest:
        parts = ", ".join(f"{v} {c}" for c, v in sorted(rest.items()))
        print(f"  The remaining {n - k} of {n} break down as: {parts}.")
    else:
        print(f"  Every one of the {n} was in an instrument.")
    print()
    print("  WHAT THIS DOES NOT ESTABLISH. It counts errors that were RECORDED.")
    print("  An error nobody wrote down is not in the denominator, so this is a")
    print("  rate over the night's record and not over the night's mistakes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
