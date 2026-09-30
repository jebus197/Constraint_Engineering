#!/usr/bin/env python3
"""FALSIFIER: the brief's "INADMISSIBLE" is the figures script's word, not the
harness's verdict -- and repairing the fence-detector cannot reach ADMISSIBLE.

Run from the repository root:

    python3 scripts/inadmissible_is_not_a_harness_verdict_2026-09-30.py

THE CLAIM UNDER TEST (brief, 2026-09-30, Fact 1):

    "THE TRIAGE TESTS FOR FENCED PYTHON ... a markdown document carrying a
     computable FALSE claim returns INADMISSIBLE -- the identical verdict to a
     document about the mood in a room."

THREE SEPARATE PROPOSITIONS ARE BUNDLED THERE AND THEY HAVE DIFFERENT TRUTH
VALUES. This script separates them and decides each by CALLING the live code,
per `execute-do-not-grep`.

  P1 (the observation)  `_gateable_source` returns None for both documents.
                        EXPECTED TRUE. A true statement about an extractor.

  P2 (the label)        that shared outcome is a harness VERDICT named
                        INADMISSIBLE.
                        EXPECTED FALSE. `_gateable_source` returns
                        `(Optional[str], reason)` -- a source or None -- never
                        a verdict. The brief's own producer,
                        scripts/intelligence_first_brief_figures_2026-09-30.py,
                        prints `'ADMISSIBLE' if red else 'INADMISSIBLE'`: the
                        words are the SCRIPT'S, applied to a truthiness test on
                        an extractor's return value. The live verdict for both
                        documents is SK_NO_SCORE, which docs/GLOSSARY.md:237
                        defines as "the statement that S_k has no opinion" --
                        the CORRECT answer for a prose target, not a defect.

  P3 (the consequence)  repairing the detector so prose-embedded computables
                        are seen would let such a document reach ADMISSIBLE.
                        EXPECTED FALSE, and this is the load-bearing one.
                        `_prose_one_sided` (reference_runner_v3.py:11656)
                        rewrites EVERY would-be ADMISSIBLE on a prose target
                        into REJECTED or NO_SCORE. The S_k tristate range on a
                        prose target is therefore bounded by
                        {REJECTED, NO_SCORE} whatever the detector does.
                        Detector repair alone buys 0 reachable states.

A FALSIFIER, NOT A DEMO: it raises AssertionError iff the three propositions
hold as stated, and exits cleanly if the brief's reading is right. It imports
the REAL module; no logic is retyped.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))


# Documents are held here as DATA. The code under test is imported.
DOC_COMPUTABLE_FALSE = (
    "# Report\n\nThe mean of 2, 4 and 6 is 4.5 and the standard deviation "
    "is 2.0.\n"
)
DOC_MOOD = "# Reflections\n\nThe mood in the room improved.\n"
DOC_FENCED = "# S\n\n```python\nx = 1\nassert x == 1\n```\n"

FIX_FENCED_BENIGN = (
    "<<<<<<< SEARCH\nx = 1\n=======\nx = 1  # annotated\n>>>>>>> REPLACE\n"
)


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="Falsifier for the brief's INADMISSIBLE framing. Writes "
                    "nothing, dispatches nothing, costs nothing.")
    ap.parse_args(argv)

    from reference_runner_v3 import (
        _gateable_source,
        compute_sk,
        resolve_target_kind,
        SK_ADMISSIBLE,
        SK_NO_SCORE,
        SK_REJECTED,
        SK_ESCALATE,
    )
    import reference_runner_v3 as RR

    failures = []

    # ---- P1: the observation is TRUE ------------------------------------
    print("P1  the extractor returns None for both documents")
    red_false, why_false = _gateable_source(DOC_COMPUTABLE_FALSE, "doc.md")
    red_mood, why_mood = _gateable_source(DOC_MOOD, "doc.md")
    print(f"    computable-false  -> {red_false!r}  ({why_false})")
    print(f"    mood-in-the-room  -> {red_mood!r}  ({why_mood})")
    p1 = (red_false is None and red_mood is None)
    print(f"    P1 holds = {p1}")
    if not p1:
        failures.append("P1 refuted: extractor did not return None for both")

    # ---- P2: the LABEL is not a harness verdict --------------------------
    print("\nP2  'INADMISSIBLE' is not a value the harness can emit")
    vocabulary = {SK_ADMISSIBLE, SK_REJECTED, SK_ESCALATE, SK_NO_SCORE}
    print(f"    live S_k tristate vocabulary = {sorted(vocabulary)}")
    has_inadmissible = "INADMISSIBLE" in vocabulary
    has_const = any("INADMISSIBLE" in n for n in dir(RR))
    print(f"    'INADMISSIBLE' in vocabulary = {has_inadmissible}; "
          f"as a module attribute = {has_const}")

    verdicts = {}
    for label, doc in (("computable-false", DOC_COMPUTABLE_FALSE),
                       ("mood-in-the-room", DOC_MOOD)):
        kind, _ = resolve_target_kind("doc.md", doc)
        r = compute_sk(fix_text="", source=doc, source_path="doc.md")
        verdicts[label] = r.tristate
        print(f"    {label:17s} kind={kind:6s} tristate={r.tristate}")
    p2 = (not has_inadmissible and not has_const
          and set(verdicts.values()) == {SK_NO_SCORE})
    print(f"    P2 holds = {p2}   (both return {SK_NO_SCORE}, which "
          f"GLOSSARY.md:237 defines as 'S_k has no opinion')")
    if not p2:
        failures.append(f"P2 refuted: verdicts={verdicts} "
                        f"has_inadmissible={has_inadmissible}")

    # ---- P3: ADMISSIBLE is unreachable on a prose target ------------------
    print("\nP3  ADMISSIBLE is unreachable on a prose target, fences or not")
    observed = set()
    for doc_label, doc in (("no fence", DOC_COMPUTABLE_FALSE),
                           ("fenced", DOC_FENCED)):
        for flag in (False, True):
            for fix_label, fix in (("no fix", ""),
                                   ("benign fix", FIX_FENCED_BENIGN)):
                r = compute_sk(
                    fix_text=fix, source=doc, source_path="doc.md",
                    score_prose_listings=flag)
                observed.add(r.tristate)
                one_sided = r.gate_details.get("_prose_one_sided", {})
                note = one_sided.get("computed_sk", "")
                print(f"    doc={doc_label:9s} score_prose={str(flag):5s} "
                      f"{fix_label:11s} -> {r.tristate:10s}"
                      + (f"  (gates would have said sk={note})"
                         if note != "" else ""))
    print(f"    tristates observed over the sweep = {sorted(observed)}")
    p3 = SK_ADMISSIBLE not in observed
    print(f"    P3 holds = {p3}")
    if not p3:
        failures.append(f"P3 refuted: ADMISSIBLE was reachable; "
                        f"observed={sorted(observed)}")

    print("\nCONSEQUENCE")
    print("    Fact 1's observation (P1) is true; its LABEL (P2) is the")
    print("    producer script's own word, not a harness verdict; and the")
    print("    remedy it motivates (P3) cannot change the reachable verdict")
    print("    set on a prose target, because `_prose_one_sided` bounds that")
    print("    set to {REJECTED, NO_SCORE} downstream of every detector.")

    if failures:
        print("\nNOT FALSIFIED -- the brief's reading survives:")
        for f in failures:
            print("   ", f)
        return 0

    print("\nFALSIFIED")
    raise AssertionError(
        "The brief's Fact 1 conflates an extractor's None-return with a "
        "harness verdict named INADMISSIBLE (no such verdict exists; both "
        "documents return NO_SCORE), and the remedy it motivates cannot "
        "reach ADMISSIBLE on any prose target because `_prose_one_sided` "
        "bounds the reachable set to {REJECTED, NO_SCORE}."
    )


if __name__ == "__main__":
    sys.exit(main())
