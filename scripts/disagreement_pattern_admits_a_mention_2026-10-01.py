#!/usr/bin/env python3
"""THE WIDENED DISAGREEMENT PATTERN STILL ADMITS A MENTION, AND REJECTS ASSERTIONS.

FREE PANEL, 2026-10-01, Q4. The 2026-10-01 widening excluded a bare
`disagreement with` BECAUSE it matched "a model's disagreement with a CONFIRMED
finding would vanish" -- a mention, not an assertion. The exclusion is right and
the reasoning beside it is right. The problem is that it was applied to the ONE
observed instance, while two of the alternatives that WERE added admit mentions
by the identical mechanism:

  alt 3  `(?:^|\\n)\\s*#{0,4}\\s*\\**\\s*(?:\\d+[.)]\\s*)?disagreements?\\b`
         matches ANY line beginning with the word, including
         "Disagreement between seats is information and is preserved."
  alt 5  `(?:my|our)\\s+(?:strongest\\s+|...)*disagreements?\\b`
         matches "My disagreement detector has the same shape of defect."

The project's own comment on this pattern names the defect class exactly -- "the
substring-versus-token defect wearing a different hat -- the same shape that has
now cost this project 4 separate findings". Fixing the instance and leaving the
class is how it reaches 5.

THE OTHER DIRECTION IS WORSE AND UNMEASURED. The pattern keys on the LEXEME
"disagree". Every genuine disagreement phrased without it is invisible: "CC1 is
wrong about X", "contrary to the brief", "I do not accept the framing". A guard
that counts P5 compliance will read a seat that disagreed in plain English as
having lost its disagreement.

WHAT THIS FILE IS. A LABELLED SET -- the thing the brief says the admissibility
classifier got today and this guard did not -- plus a CANDIDATE tightening and
its measured effect on every archived reply, so a change is licensed by a
committed measurement rather than by my say-so. IT DOES NOT CHANGE THE LIVE
PATTERN: `DISAGREEMENT_RE` feeds the declared figure "4 gained, 0 lost over 306
replies", and moving a live measurement is the human's call.

Run:  python3 scripts/disagreement_pattern_admits_a_mention_2026-10-01.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "bench"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: THE LABELLED SET. `True` = a genuine assertion of the seat's own position.
#: `False` = a MENTION: the word used about the mechanism, not as a position.
LABELLED = [
    # ── mentions: must NOT count ──────────────────────────────────────────
    ("Disagreement between seats is information and is preserved by the "
     "harness, so nothing is lost.", False),
    ("Our disagreement pattern was widened today to recognise a mid-sentence "
     "statement.", False),
    ("The latent tagger matched a mention. My disagreement detector has the "
     "same shape of defect.", False),
    ("a model's disagreement with a CONFIRMED finding would vanish", False),
    ("Section P requires a disagreement section. Disagreements are counted by "
     "a regex over the archive.", False),
    ("strongest_disagreement: none", False),
    ("I disagree with nothing.", False),
    ("## Disagreements\n\nNone.", False),
    # ── assertions: MUST count ────────────────────────────────────────────
    ("strongest_disagreement: the brief's 0 of 560 is a property of the "
     "corpus, not of the patterns.", True),
    ("**Strongest disagreement:** the seat-evidence figure is "
     "environment-dependent.", True),
    ("I disagree with CC1 on the round cap floor.", True),
    ("My strongest disagreement is with the brief's framing of Q2.", True),
    ("This is a disagreement with the brief: the ledger is a relabelling.", True),
    ("## Disagreement\n\nThe 46 of 251 does not reproduce; I measure 251 of 251.", True),
    # these carry no form of the lexeme at all
    ("CC1 is wrong about the 560-shape corpus: list-item fences are "
     "unreachable by construction.", True),
    ("Contrary to the brief, the enumeration cannot reach a non-whitespace "
     "prefix.", True),
    ("I do not accept the framing of Q5; the guard measures the environment.", True),
]

#: A CANDIDATE THAT THIS FILE'S OWN MEASUREMENT REFUTES. It is kept, labelled,
#: because a refuted candidate is the useful artefact here: the next attempt
#: must beat the labelled set AND lose 0 archived replies, and this one shows
#: the second half is where the difficulty is.
#:
#: MEASURED: accuracy 14 of 17 on the labelled set (0 mentions admitted, so it
#: fixes the class the live pattern admits) but it LOSES 13 of 306 archived
#: replies -- 4.2484%, Wilson 95% [2.4993%, 7.1319%] -- including genuine
#: sections headed "## DISAGREEMENTS (with CC1 and the other seats)", where the
#: label is followed by a parenthetical rather than by `:` or a line end. Under
#: the additive standard a replacement must dominate on a named property; this
#: one does not, so IT MUST NOT BE PROMOTED. Reported, not applied.
#:
#: Two changes, each aimed at a class:
#:  * the line-initial form must be a LABEL (`:`, end of line, or closing
#:    markup), not the first word of a sentence that continues as prose;
#:  * `my/our ... disagreement` must be FOLLOWED BY a position marker
#:    (`with`, `is`, `are`, `:`, `,`, `.`, end) rather than by a noun it
#:    qualifies ("my disagreement DETECTOR").
CANDIDATE = re.compile(
    r"strongest[_ ]disagreements?"
    r"|where\s+i\s+disagree"
    r"|(?:^|\n)\s*#{0,4}\s*\**\s*(?:\d+[.)]\s*)?disagreements?\b"
    r"(?=\s*\**\s*(?::|$|\n))"
    r"|i\s+disagree\s+with"
    r"|(?:my|our)\s+(?:strongest\s+|likely\s+|named\s+|own\s+)*disagreements?\b"
    r"(?=\s*(?:with\b|is\b|are\b|was\b|:|,|\.|$|\n))"
    r"|this\s+is\s+a\s+disagreement\b"
    r"|(?<!no )disagreements?\s+with\s+(?:cc1|me\b|the\s+(?:brief|panel|"
    r"other\s+seat|earlier\s+seat|first\s+seat))",
    re.I)


def _load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, str(REPO / path))
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def _score(decide, rows) -> dict:
    tp = fp = tn = fn = 0
    wrong = []
    for text, label in rows:
        got = bool(decide(text))
        if label and got:
            tp += 1
        elif label and not got:
            fn += 1
            wrong.append(("MISSED ASSERTION", text))
        elif not label and got:
            fp += 1
            wrong.append(("ADMITTED MENTION", text))
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "wrong": wrong,
            "n": len(rows), "correct": tp + tn}


def main() -> int:
    pcc = _load("scripts/panel_condition_compliance_2026-09-10.py", "pcc_probe")
    live = pcc.carries_disagreement

    def candidate(text: str) -> bool:
        """The candidate, run through the SAME null-body filter as the live one."""
        for m in CANDIDATE.finditer(text or ""):
            body = pcc._introduced_body(text, m).strip(pcc._MARKUP + ".!;,")
            if body and not pcc._NULL_BODY.fullmatch(body):
                return True
        return False

    print("DOES THE WIDENED PATTERN SEPARATE A MENTION FROM AN ASSERTION?")
    print("=" * 74)
    from statsmodels.stats.proportion import proportion_confint

    for label, decide in (("LIVE carries_disagreement", live),
                          ("CANDIDATE", candidate)):
        s = _score(decide, LABELLED)
        lo, hi = proportion_confint(s["correct"], s["n"], method="wilson")
        print(f"\n  {label}")
        print(f"    accuracy {s['correct']} of {s['n']}  "
              f"Wilson 95% [{lo:.4%}, {hi:.4%}]")
        print(f"    mentions ADMITTED (false positive) : {s['fp']}")
        print(f"    assertions MISSED (false negative) : {s['fn']}")
        for kind, text in s["wrong"]:
            print(f"      {kind}: {text[:66]!r}")

    # ── the committed measurement: effect on the REAL archive ─────────────
    pcm = _load("bench/tests/test_panel_conditions_are_met_2026-09-10.py",
                "pcm_probe")
    rows = [d.get("response", "") for _rnd, d in pcm._replies()]
    lost = [r for r in rows if live(r) and not candidate(r)]
    gained = [r for r in rows if candidate(r) and not live(r)]
    print(f"\n  EFFECT ON THE ARCHIVE ({len(rows)} replies)")
    print(f"    replies the candidate would LOSE   : {len(lost)}")
    print(f"    replies the candidate would GAIN   : {len(gained)}")
    if rows:
        lo, hi = proportion_confint(len(lost), len(rows), method="wilson")
        print(f"      loss rate Wilson 95% [{lo:.4%}, {hi:.4%}]")
    # STATE THE REMAINDER. Caught by this project's own
    # `TestTruncatedListsStateTheirRemainder` guard on this very file: it
    # printed 3 of 13 under a heading that reads as complete, and the withheld
    # 10 are the ones that decide whether the candidate may be promoted.
    SHOW = 3
    for r in lost[:SHOW]:
        m = re.search(r"disagree\w*", r, re.I)
        a = max(0, (m.start() if m else 0) - 40)
        b = (m.end() if m else 60) + 40
        print(f"      LOST near: {r[a:b].strip()[:100]!r}")
    if len(lost) > SHOW:
        print(f"      ... and {len(lost) - SHOW} more not shown")

    s_live = _score(live, LABELLED)
    print()
    if s_live["fp"] or s_live["fn"]:
        print(f"  FALSIFIED: the live pattern admits {s_live['fp']} mention(s) "
              f"and misses {s_live['fn']} genuine assertion(s) on a labelled "
              f"set of {s_live['n']}.")
        print(f"  The candidate scores {_score(candidate, LABELLED)['correct']}"
              f" of {s_live['n']} and would lose {len(lost)} of {len(rows)} "
              f"archived replies. REFERRED TO THE HUMAN: changing "
              f"DISAGREEMENT_RE moves a declared figure.")
        raise AssertionError(
            f"DISAGREEMENT_RE admits {s_live['fp']} mentions and misses "
            f"{s_live['fn']} assertions of {s_live['n']} labelled cases")
    print("  CLEAN.")
    return 0


if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
