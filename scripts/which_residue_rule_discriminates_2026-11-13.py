#!/usr/bin/env python3
"""Object rule, subject rule, or both: which separates a residue from a rule?

ENTRY B169 reported that `_residue_is_his` matched B168's record of his general
rule -- "only he may REJECT one" -- and so moved an entry that is mine to build
off the movable set. It proposed requiring the sentence's SUBJECT to be the
entry rather than a rule.

★ A DIFFERENT FIX WAS IMPLEMENTED THE SAME DAY: suppress when the OBJECT is
indefinite (`a`, `an`, `one`, `any`), on the reasoning that an indefinite object
means a class. That fix is live and B168 now classifies correctly.

★ BUT IT UNDER-REPORTS, AND UNDER-REPORTING IS THE WORSE DIRECTION. Driven
directly, `only he may authorise a paid panel dispatch, and this entry needs
one` returns False -- a genuine residue read as mine to do, so the gate would
prod the session to do work that needs his permission. A false POSITIVE stalls
work; a false NEGATIVE acts without him.

This measures the 2 rules separately and composed, against a labelled set, so
the choice rests on counts rather than on which argument reads better. Per
`composability-requires-a-measurement`, composing is recommended only if the
pair dominates either part alone.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "hooks").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")

#: An attributive frame: the sentence REPORTS a rule rather than stating this
#: entry's residue. Subject-side, which is what B169 asked for.
_ATTRIBUTIVE = re.compile(
    r"\b(?:his|the)\s+(?:rule|ruling|instruction|directive|standard|policy)\b"
    r"|\brecords?\s+that\b|\bstates?\s+that\b|\bsays?\s+that\b"
    r"|\bper\s+his\b|\bunder\s+his\s+(?:rule|ruling)\b", re.I)

#: LABELLED CASES. Each label is defensible from the entry text it imitates, and
#: the 2 from B169 are quoted from the entry itself.
CASES = [
    ("only he may reject a feature request", False,
     "B169's own case: a class statement standing alone"),
    ("his rule is that only he may reject a feature request, which is why the kind matters",
     False, "B169's own case: a sentence DESCRIBING his authority"),
    ("only he may authorise a paid panel dispatch, and this entry needs one", True,
     "a genuine residue whose object happens to be indefinite"),
    ("only he may approve this particular change", True,
     "a genuine residue with a definite object"),
    # ★ CASE 9, AND IT WAS ADDED AFTER THE ABLATION, WHICH IS SAID OUT LOUD
    # BECAUSE ADDING A CASE THAT SAVES A PATTERN IS THE SHAPE OF A FLATTERING
    # MEASURE. What the ablation showed: `_ATTRIBUTIVE` changed the verdict on
    # 0 of the first 8 cases AND on 0 of 181 live entries, so on that corpus
    # the narrowed object rule ALONE scored 8 of 8 and the subject rule was
    # decorative. The reason was a HOLE in the corpus, not a redundant rule --
    # every attributive case written had an INDEFINITE object, which the object
    # rule already suppresses, so no case reached the subject rule at all.
    # This case is the MINIMAL PAIR of the one directly above it: identical
    # shape, definite object, differing ONLY in the attributive frame, and
    # carrying the opposite label. Its label is not contestable in the way
    # case 1's is -- a sentence opening "his rule is that" reports a rule,
    # and no reading makes it this entry asking him for something.
    ("his rule is that only he may approve this change", False,
     "attributive frame, DEFINITE object -- the minimal pair of case 4, and "
     "the only case either candidate rule separates them on"),
    ("the rule records that only he may reject one", False,
     "attributive frame, indefinite object"),
    ("only he can release the credential store for this entry", True,
     "a genuine residue, definite"),
    ("his ruling of 2026-10-17 is that only he may reject a feature request", False,
     "attributive, dated"),
    ("only he may authorise any paid dispatch, and that is what this item needs", True,
     "genuine residue, indefinite object, tied to this item"),
]


def load():
    spec = importlib.util.spec_from_file_location(
        "wnn_rules", REPO / "hooks" / "work_not_narrate.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["wnn_rules"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


#: ★ THE NARROWING, ADDED 2026-11-13 AFTER AN ABLATION. The object rule reads an
#: indefinite object as naming a CLASS. That is right only when nothing else in
#: the sentence binds the class to the item in hand: "only he may authorise a
#: paid dispatch, and THIS ENTRY needs one" names a class AND claims it.
_THIS_ITEM = re.compile(
    r"\bthis\s+(?:entry|item|change|one)\b|\bwhat\s+this\s+(?:entry|item)\b", re.I)


def decide(m, sent: str, object_rule: bool, subject_rule: bool,
           narrow: bool = False) -> bool:
    """`_residue_is_his` for 1 sentence, with each suppressor switched on or off.

    `narrow` makes the object rule yield when the sentence ties its class to
    this item, which is the difference between the shipped rule and the one
    that was live this morning.
    """
    for mm in m._HIS_RESIDUE.finditer(sent):
        starts_only_he = mm.group(0).lower().startswith("only he")
        if starts_only_he and object_rule and m._CLASS_OBJECT.search(sent) \
                and not (narrow and _THIS_ITEM.search(sent)):
            continue
        if starts_only_he and subject_rule and _ATTRIBUTIVE.search(sent):
            continue
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    m = load()
    variants = {
        "neither suppressor": (False, False, False),
        "OBJECT rule only (live this morning)": (True, False, False),
        "SUBJECT rule only (B169's proposal)": (False, True, False),
        "BOTH composed, object unnarrowed": (True, True, False),
        "NARROWED object only": (True, False, True),
        "NARROWED object + subject (SHIPPED)": (True, True, True),
    }
    composed = "NARROWED object + subject (SHIPPED)"
    print(f"  labelled cases: {len(CASES)}\n")
    best = {}
    for name, (o, s, nw) in variants.items():
        wrong = []
        for text, want, why in CASES:
            got = decide(m, text, o, s, nw)
            if got != want:
                wrong.append((text, want, got, why))
        correct = len(CASES) - len(wrong)
        best[name] = correct
        print(f"  {name:38s} {correct} of {len(CASES)} correct")
        for text, want, got, why in wrong:
            kind = ("MISSED a residue" if want else "FALSE POSITIVE")
            print(f"      {kind:16s} {why}")
            print(f"          {text[:84]}")
    print()
    from statsmodels.stats.proportion import proportion_confint
    for name, k in best.items():
        n = len(CASES)
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        print(f"  {name:38s} {k}/{n} = {k/n:.6f}  "
              f"Wilson [{w[0]:.6f}, {w[1]:.6f}]  C-P [{c[0]:.6f}, {c[1]:.6f}]")
    print()
    top = max(best.values())
    winners = [k for k, v in best.items() if v == top]
    print(f"  best: {top} of {len(CASES)} -- {', '.join(winners)}")
    # ★ THE DOMINANCE TEST IS COMPUTED, NOT ASSERTED, and it names the parts the
    # composition is made of rather than any variant that happens to tie. His
    # standard asks whether the PAIR beats EITHER PART ALONE -- so the parts of
    # the shipped rule are the narrowed object rule and the subject rule, and a
    # tie with either of those is a refusal to compose.
    parts = ("NARROWED object only", "SUBJECT rule only (B169's proposal)")
    if composed in best:
        pair = best[composed]
        alone = max(best[p] for p in parts if p in best)
        if pair > alone:
            print(f"  ★ COMPOSING DOMINATES: {pair} against {alone} for the better part "
                  f"alone,")
            print("    which is what `composability-requires-a-measurement` asks for.")
        else:
            print(f"  ★ COMPOSING DOES NOT DOMINATE: {pair} against {alone} for a part "
                  f"alone, so")
            print("    `composability-requires-a-measurement` says PREFER THE SINGLE FIX.")
    print()
    print(f"  ★ n = {len(CASES)} CONSTRUCTED cases, not a sample of live entries.")
    print("    2 are quoted from B169; the rest are written to probe the boundary,")
    print("    so this measures DISCRIMINATION on hard cases and not a base rate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
