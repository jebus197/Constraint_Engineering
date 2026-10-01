#!/usr/bin/env python3
"""Can anything decide "does this document contain a decidable claim"? Measured.

THE QUESTION, AND WHOSE IT IS. The free panel of 2026-09-30 recommended that
the boundary of inadmissibility become an OUTCOME rather than a gate -- a
document is judged to carry no decidable claims only after something has looked
for them. Neither seat would guess whether a small cheap classifier can draw
that boundary reliably; one specified a labelled test set with executable
ground truth instead of guessing. The founder's response: "Then do this work if
it hasn't already been done. But we previously did measure our classifier agent
(Haiku) and in general found it to be very reliable? Would composing both
approaches present any meaningful improvement over any single one?"

TWO THINGS THIS SCRIPT ESTABLISHES, AND ONE IT CANNOT.

  (1) THE STATUS-QUO ARM'S ERROR RATE, measured against known labels. The
      current triage is `_gateable_source`, which is FENCE SYNTAX. Its accuracy
      on this set is reported with intervals.

  (2) WHETHER AN ANCHOR-BASED CLAIM CHECK RECOVERS WHAT THE SYNTAX ARM MISSES,
      and whether composing the two beats either alone -- the founder's
      composability question, answered on the 2x2 rather than by preference.

  (3) WHAT IT CANNOT ESTABLISH, and this is the decision-relevant part. The
      claim arm here locates claims by their ANCHORS, and the anchors come from
      the corpus fixtures' own claim lists -- the ANSWER KEY. On a document the
      corpus does not describe, it has no claims to locate and returns False by
      construction. So its accuracy on this set is NOT a classifier's accuracy;
      it is a lookup's. Reporting it as a classifier result would be the
      answer-key leak this project has been bitten by before.

      THEREFORE the model arm cannot be skipped: deciding whether a cheap model
      can find claims in an UNSEEN document requires dispatching a model at
      documents whose labels it has not been given. That costs seat dispatches,
      which is the founder's call, so this script PREPARES that arm and does not
      run it. `--emit-model-set` writes the documents and the withheld labels to
      separate files so a dispatch can be scored without ever seeing the key.

ON THE HAIKU FIGURE. The founder recalls measuring the classifier agent (Haiku)
and finding it reliable. That measurement is NOT IN THE RECORD: Haiku is named
as the v2 classifier at `docs/ARCHITECTURE.md:93`, and searching the committed
scripts, the docs, the resources, the experimental notes and the project memory
returns no script that measured its agreement and no figure for it. Stated
plainly rather than assumed either way -- it may exist outside the repository,
and `feedback_ask_for_founder_held_evidence` says an unknown resolvable by
asking is an unasked question. If it exists it should be committed beside its
number; if it does not, this set is what would produce one.

Run:  python3 scripts/claim_classifier_labelled_set_2026-10-01.py
      python3 scripts/claim_classifier_labelled_set_2026-10-01.py --emit-model-set DIR
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench"), str(REPO / "bench/tests/fixtures/stem")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: MOOD PROSE: documents with claims nobody can compute, which is the only
#: state the founder's "genuinely non-computable" describes. Written here, not
#: harvested, because a NEGATIVE needs to be unambiguous to be a label.
MOOD_CONTROLS = {
    "mood_tone": (
        "The review read well. The opening section carried the argument with "
        "confidence and the closing paragraph landed. Reviewers will find the "
        "ordering natural, and the whole reads as the work of someone who has "
        "thought about the reader. Nothing in it feels rushed."),
    "mood_preference": (
        "I prefer the shorter form. The longer version is defensible but it "
        "asks more of the reader than the argument repays, and the tone drifts "
        "toward the defensive in the middle third. This is a matter of taste "
        "and I would not press it."),
    "mood_process": (
        "The team should meet earlier in the week. Monday afternoons leave too "
        "little room to act on what is agreed, and morale is better when the "
        "week opens with a decision rather than a discussion."),
    "mood_aesthetic": (
        "The figure is attractive but the colour choices fight each other. A "
        "quieter palette would let the trend carry itself, and the legend "
        "would be better on the right."),
    "mood_intent": (
        "The intention behind the directive was generous. Whether it reads that "
        "way to someone encountering it for the first time is a different "
        "matter, and worth asking someone outside the project."),
}

_FENCE = re.compile(r"^(?P<p>[ \t]*(?:>[ \t]*)*)(?P<f>```|~~~).*?^(?P=p)?(?P=f)",
                    re.S | re.M)


def _strip_fences(doc: str) -> str:
    """Remove fenced listings, leaving the prose. The claims STATED in prose
    survive; claims whose evidence lived inside the listing do not."""
    return _FENCE.sub("\n[listing removed]\n", doc)


def _documents():
    """The labelled set: (name, text, has_decidable_claim, note)."""
    import stem_fixtures as SF

    out = []
    for fx in SF.load_all():
        doc = fx.doc_name and getattr(fx, "document", None)
        # The fixture's document text is built by its own loader; fall back to
        # whichever attribute carries it rather than assuming one.
        text = None
        for attr in ("document", "text", "body", "doc"):
            val = getattr(fx, attr, None)
            if isinstance(val, str) and len(val) > 500:
                text = val
                break
        if text is None:
            continue
        out.append((f"{fx.key}_intact", text, True,
                    f"{len(fx.claims)} corpus claims, planted ground truth"))
        out.append((f"{fx.key}_prose", _strip_fences(text), True,
                    "same claims, fenced listings removed"))
    for name, text in MOOD_CONTROLS.items():
        out.append((name, text, False, "opinion prose, no computable claim"))
    return out


def _syntax_arm(text: str, name: str) -> bool:
    """THE STATUS QUO: does the current triage see anything to engage?"""
    try:
        from reference_runner_v3 import _gateable_source
    except ImportError:
        return False
    try:
        return _gateable_source(text, f"{name}.md")[0] is not None
    except Exception:                                         # noqa: BLE001
        return False


def _claim_arm(text: str) -> bool:
    """ANCHOR LOOKUP, and it uses the answer key -- see the module docstring.

    True iff any corpus claim's anchor is found verbatim in the document. It
    cannot generalise: a document the corpus does not describe has no anchors
    to find.
    """
    import stem_fixtures as SF

    for fx in SF.load_all():
        for c in fx.claims:
            anchor = (getattr(c, "anchor", "") or "").strip()
            if len(anchor) >= 12 and anchor in text:
                return True
    return False


def _rates(k: int, n: int) -> str:
    if not n:
        return "no denominator"
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    clo, chi = proportion_confint(k, n, method="beta")
    return (f"{k}/{n} = {k / n:.4%}  Wilson [{lo:.4%}, {hi:.4%}]  "
            f"Clopper-Pearson [{clo:.4%}, {chi:.4%}]")


def _score(rows, predict) -> dict:
    tp = sum(1 for _n, _t, label, _no in rows if label and predict(_n, _t))
    fn = sum(1 for _n, _t, label, _no in rows if label and not predict(_n, _t))
    fp = sum(1 for _n, _t, label, _no in rows if not label and predict(_n, _t))
    tn = sum(1 for _n, _t, label, _no in rows if not label and not predict(_n, _t))
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "correct": tp + tn, "n": tp + fn + fp + tn}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0])
    ap.add_argument("--emit-model-set", metavar="DIR", default=None,
                    help="write the documents and the WITHHELD labels to "
                         "separate files, so a model arm can be scored without "
                         "being shown the key")
    args = ap.parse_args(argv)

    rows = _documents()
    if not rows:
        print("the fixture corpus did not load; nothing to measure",
              file=sys.stderr)
        return 1

    if args.emit_model_set:
        out = pathlib.Path(args.emit_model_set)
        (out / "documents").mkdir(parents=True, exist_ok=True)
        for name, text, _label, _note in rows:
            (out / "documents" / f"{name}.md").write_text(text, encoding="utf-8")
        (out / "LABELS_WITHHELD.json").write_text(json.dumps(
            {name: {"has_decidable_claim": label, "note": note}
             for name, _t, label, note in rows}, indent=2), encoding="utf-8")
        (out / "README.md").write_text(
            "# Model arm, unscored\n\n"
            "`documents/` holds the labelled set with NO labels attached.\n"
            "`LABELS_WITHHELD.json` holds the answers and must NOT be shown to "
            "the model being scored.\n\n"
            "The question to put per document: does this document contain at "
            "least 1 claim that computation could settle? Answer yes or no, "
            "and name the claim where yes.\n",
            encoding="utf-8")
        print(f"wrote {len(rows)} documents and the withheld labels to {out}")
        return 0

    pos = sum(1 for *_x, label, _n in [(r[0], r[1], r[2], r[3]) for r in rows]
              if label)
    print("THE LABELLED SET")
    print(f"  documents           : {len(rows)}")
    print(f"  with decidable claims (positive): {pos}")
    print(f"  without (mood prose, negative)  : {len(rows) - pos}")
    print()

    arms = {
        "A  syntax triage (the STATUS QUO, `_gateable_source`)":
            lambda n, t: _syntax_arm(t, n),
        "B  anchor lookup (USES THE ANSWER KEY -- not a classifier)":
            lambda _n, t: _claim_arm(t),
        "A or B  composition":
            lambda n, t: _syntax_arm(t, n) or _claim_arm(t),
    }
    scored = {}
    for label, fn in arms.items():
        s = _score(rows, fn)
        scored[label] = s
        print(label)
        print(f"    accuracy    {_rates(s['correct'], s['n'])}")
        print(f"    sensitivity {_rates(s['tp'], s['tp'] + s['fn'])}"
              "   (positives it finds)")
        print(f"    specificity {_rates(s['tn'], s['tn'] + s['fp'])}"
              "   (negatives it leaves alone)")
        print(f"    tp={s['tp']} fn={s['fn']} fp={s['fp']} tn={s['tn']}")
        print()

    print("WHERE THE STATUS QUO FAILS, named per document:")
    for name, text, label, note in rows:
        a = _syntax_arm(text, name)
        if label and not a:
            print(f"  MISSED  {name:28s} {note}")
    print()

    a = scored["A  syntax triage (the STATUS QUO, `_gateable_source`)"]
    comp = scored["A or B  composition"]
    print("THE FOUNDER'S COMPOSABILITY QUESTION, on this set:")
    print(f"  status quo correct : {a['correct']} of {a['n']}")
    print(f"  composed correct   : {comp['correct']} of {comp['n']}")
    gain = comp["correct"] - a["correct"]
    print(f"  gain from composing: {gain} document(s)")
    print()
    print("  AND THE LIMIT, WHICH IS THE ANSWER THAT MATTERS. Arm B locates")
    print("  claims by anchors taken from the corpus's own claim lists -- the")
    print("  ANSWER KEY. On a document the corpus does not describe it has no")
    print("  anchors to find and returns False by construction, so its")
    print("  accuracy here is a lookup's and not a classifier's. Composing a")
    print("  syntax gate with a lookup cannot answer whether a cheap MODEL can")
    print("  find claims in an unseen document. That needs the model arm, on")
    print("  documents whose labels it has not been given, which costs seat")
    print("  dispatches and is the founder's decision. `--emit-model-set`")
    print("  prepares it with the labels held in a separate file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
