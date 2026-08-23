#!/usr/bin/env python3
"""Catch the vagueness the note standard already forbids but could not detect.

WHY A LINTER AND NOT ANOTHER RULE. The standard has said since v1.2 that the failure
mode is never "too technical", it is "too vague to identify what is being discussed",
and v1.4's Rule 19 says to name the subject. The rule was in force on 2026-08-23 and
the note written that day still contained "all eight defects debited the models'
measured competence -- the very quantity this project exists to measure", on which the
founder's response was "I have no clear idea at all what you are referring to", adding
that the same fix had been promised several times already. A rule that has been
restated and re-violated does not need restating. It needs a check that fails.

THE TWO PATTERNS, BOTH TAKEN FROM REAL VIOLATIONS.

  A. UNNAMED SUBJECT. A generic noun standing where a name belongs -- "the mechanism",
     "one component", "the quantity", "the system" -- in a sentence that names nothing
     concrete. The reader designed this project; they do not need the concept
     explained, they need to know WHICH ONE is being discussed.

  B. QUANTITY WITHOUT A VALUE. A claim about a rate, score, count or measure with no
     number anywhere in the sentence. "Debited the models' measured competence" says
     something moved without saying what it is called, which way it went, or by how
     much. The compliant form names the quantity as the system names it, the
     direction, and one real value.

DELIBERATELY NOT A GATE. It reports; it does not block. A linter that blocks gets
worked around, and the point is to be read before delivery, not obeyed after.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Generic nouns that stand in for a name. Each has appeared in a real violation.
VAGUE_SUBJECTS = (
    "the mechanism", "this mechanism", "one component", "a component",
    "the component", "the quantity", "the measure", "the system", "the process",
    "the machinery", "one element", "the element", "the thing", "some part",
    "the relevant", "the appropriate", "certain aspects", "various components",
)
# Words that assert a measurement. A claim built on one needs a value beside it.
QUANTITY_WORDS = (
    "rate", "score", "count", "competence", "coverage", "accuracy", "precision",
    "throughput", "latency", "proportion", "percentage", "ratio", "frequency",
)
# Proper-noun-ish evidence that the sentence does name something.
NAMED = re.compile(
    r"\b(?:[A-Z][a-z]+[A-Z]\w*"                    # CamelCase
    r"|[a-z_]+\.(?:py|md|json|toml|txt)"           # a filename
    r"|[a-z_]{3,}_[a-z_]{3,}"                      # snake_case
    r"|gamma|rho|nu|Exp\s*\d+|CT-\d+|C\d{4}|H\d{2}"
    r"|Codex|Gemini|DeepSeek|ChatGPT|CC1|CC2|Fable)\b")
# A VALUE MAY BE SPELLED. TTS files write numbers as words by standard ("twenty nine
# of thirty four"), so a bare digit test misfires on exactly the file type this linter
# exists to check. Found by running the linter on its own motivating example.
# "one", "none", "half", "twice" are DELIBERATELY ABSENT. Including them made the
# linter miss its own motivating sentence -- "Every ONE of them debited the models'
# measured competence" read as though it carried a value. A word that is this common
# in ordinary prose cannot serve as evidence that a measurement was quoted.
_NUMWORDS = ("zero two three four five six seven eight nine ten eleven twelve "
             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty "
             "thirty forty fifty sixty seventy eighty ninety hundred thousand million "
             "billion").split()
DIGIT = re.compile(r"\d|\b(?:" + "|".join(_NUMWORDS) + r")\b", re.I)
HEDGE = ("somewhat", "essentially", "in some sense", "to some extent",
         "relatively speaking", "more or less", "fairly clearly")


def sentences(text: str):
    for para_no, para in enumerate(text.split("\n\n"), 1):
        flat = " ".join(para.split())
        if not flat or flat.startswith(("|", "#", "```")):
            continue
        for s in re.split(r"(?<=[.!?])\s+", flat):
            if len(s.split()) >= 5:
                yield para_no, s


def lint(path: pathlib.Path) -> list:
    out = []
    for para_no, s in sentences(path.read_text()):
        low = s.lower()
        named = bool(NAMED.search(s))
        for v in VAGUE_SUBJECTS:
            # WORD BOUNDARY. A substring test matched "the measure" inside "the
            # measurement", which is a real noun with a real referent and not vague
            # at all. False positives are how a report-only linter becomes ignored.
            if re.search(rf"{re.escape(v)}\b", low) and not named:
                out.append((para_no, "UNNAMED SUBJECT", v, s)); break
        if not DIGIT.search(s):
            for q in QUANTITY_WORDS:
                # NOUN CONTEXT ONLY. "counts substitutions" is a verb and says nothing
                # about a measurement; "the count", "its rate", "a coverage of" do.
                # Without this the linter fired on ordinary prose and would have been
                # ignored, which is the failure mode of every linter nobody reads.
                if re.search(rf"\b(?:the|a|an|its|their|our|this|that|measured|"
                             rf"model-|\w+'s)\s+(?:\w+\s+){{0,2}}{q}s?\b", low) \
                        or re.search(rf"\b{q}s?\s+(?:of|for|at)\b", low):
                    out.append((para_no, "QUANTITY WITHOUT A VALUE", q, s)); break
        for h in HEDGE:
            if h in low:
                out.append((para_no, "HEDGE", h, s)); break
    return out


def main() -> int:
    paths = [pathlib.Path(a) for a in sys.argv[1:]]
    if not paths:
        print("  usage: note_vagueness_lint.py <file> [file ...]"); return 1
    total = 0
    for p in paths:
        if not p.is_file():
            print(f"  missing: {p}"); continue
        hits = lint(p)
        total += len(hits)
        print(f"\n  {p.name}: {len(hits)} finding(s)")
        for para_no, kind, token, s in hits:
            print(f"    para {para_no}  {kind}  ({token!r})")
            print(f"      {s[:150]}{'...' if len(s) > 150 else ''}")
    print(f"\n  {total} finding(s). Reported, not enforced — read before delivering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
