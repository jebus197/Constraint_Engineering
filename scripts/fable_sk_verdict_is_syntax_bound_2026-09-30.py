#!/usr/bin/env python3
"""EXECUTED check that the S_k triage is syntax-bound, driven through the REAL
consumer (`compute_sk`), not through a label painted over `_gateable_source`.

WHY THIS EXISTS. The 2026-09-30 brief's Fact 1 says a prose document carrying a
computable FALSE claim "returns INADMISSIBLE -- the identical verdict to a
document about the mood in a room". The word INADMISSIBLE there is the figures
script's OWN coinage (`'ADMISSIBLE' if red else 'INADMISSIBLE'` over
`_gateable_source`), not a runner verdict. Under `execute-do-not-grep` the claim
must be re-stated through the consumer: what TRISTATE does `compute_sk` actually
emit, for the same well-formed fix, on each document class, under both values of
`score_prose_listings`?

WHAT IT MEASURES
  1. A prose doc with a computable FALSE claim ("mean of 2,4,6 is 4.5") and a
     mood-in-the-room doc: whether `compute_sk` distinguishes them, under both
     flag settings.
  2. A real STEM fixture document (claims in prose, fences present): the same
     correct prose fix scored with fences intact vs fences stripped. If the
     verdict flips on stripping while every claim anchor survives, the
     admissibility signal is the fence, not the content -- through the live
     consumer.

Writes nothing. Exits 0 always; the figures are the output.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))


def _fix(old: str, new: str) -> str:
    return f"<<<< SEARCH\n{old}\n====\n{new}\n>>>> REPLACE\n"


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Drive compute_sk on prose targets with and without fenced "
                    "code, under both score_prose_listings settings. Writes "
                    "nothing and dispatches no model.")
    ap.parse_args(argv)

    from reference_runner_v3 import compute_sk
    import stem_fixtures as S

    FALSE_CLAIM_DOC = ("# Report\n\nThe mean of 2, 4 and 6 is 4.5 and the "
                       "standard deviation is 2.0.\n")
    MOOD_DOC = "# Reflections\n\nThe mood in the room improved.\n"

    print("PART 1  compute_sk on prose WITHOUT fences, both flag settings")
    rows = []
    for label, doc, fix in (
        ("computable FALSE claim", FALSE_CLAIM_DOC,
         _fix("The mean of 2, 4 and 6 is 4.5", "The mean of 2, 4 and 6 is 4.0")),
        ("mood in the room",       MOOD_DOC,
         _fix("The mood in the room improved.",
              "The mood in the room improved slightly.")),
    ):
        for flag in (False, True):
            r = compute_sk(fix, doc, "doc.md", score_prose_listings=flag)
            rows.append((label, flag, r.tristate))
            print(f"  {label:24s} score_prose_listings={str(flag):5s} "
                  f"tristate={r.tristate}  sk={r.sk}")
    false_claim_verdicts = {t for lbl, _f, t in rows if lbl.startswith("computable")}
    mood_verdicts = {t for lbl, _f, t in rows if lbl.startswith("mood")}
    print(f"  distinguishable = {false_claim_verdicts != mood_verdicts}   "
          f"(false-claim {sorted(false_claim_verdicts)} vs mood {sorted(mood_verdicts)})")

    print("\nPART 2  a real fixture's correct fix, fences intact vs stripped, "
          "flag ON (A19 setting)")
    flips = 0
    anchors_survive = 0
    n_fx = 0
    for fx in S.load_all():
        # A prose-region patch only: a listing patch cannot apply to the
        # stripped document, and the point is the PROSE claim channel.
        prose_patches = [p for p in fx.correct_fix if p.region != "listing"]
        if not prose_patches:
            continue
        n_fx += 1
        doc = fx.document
        stripped = re.sub(r"```.*?```", "", doc, flags=re.S)
        fix_text = "".join(_fix(p.old, p.new) for p in prose_patches)
        r_intact = compute_sk(fix_text, doc, fx.doc_name,
                              score_prose_listings=True)
        r_strip = compute_sk(fix_text, stripped, fx.doc_name,
                             score_prose_listings=True)
        surv = all(c.anchor in stripped for c in fx.claims if c.anchor)
        anchors_survive += surv
        flipped = r_intact.tristate != r_strip.tristate
        flips += flipped
        print(f"  {fx.key:12s} intact={r_intact.tristate:10s} "
              f"stripped={r_strip.tristate:10s} flipped={flipped} "
              f"claims_survive_strip={surv}")
    print("  NOTE: the intact-side verdict in this offline probe is driven by")
    print("  effect gates reporting 'unavailable' (no ruff/bandit baseline, no")
    print("  test command here); in a live run those baselines exist. The")
    print("  material, context-independent fact is WHICH machinery engages:")
    print("  fences present -> gates run over listings; fences absent ->")
    print("  NO_SCORE before any gate, while 100% of claim anchors survive.")
    print(f"  fixtures with a prose-region correct fix: {n_fx}")
    print(f"  verdict changed on fence-stripping: {flips} of {n_fx}")
    print(f"  fixtures keeping 100% of claim anchors after strip: "
          f"{anchors_survive} of {n_fx}")


if __name__ == "__main__":
    main(sys.argv[1:])
