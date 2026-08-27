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
# CORRECTED 2026-08-26. This comment previously read "TTS files write numbers as
# words by standard". THAT WAS NEVER THE STANDARD. v1.5 says a value may be
# "spelled or in digits", and Rule 11 governs SCIENTIFIC-NOTATION EXPONENTS ONLY.
# The blanket practice was invented by generalising Rule 11, then written into
# this file as fact -- so the tool taught the habit back to whoever read it.
#
# The founder, who reads by text-to-speech, has asked repeatedly for it to stop:
# "three thousand eight hundred and seventy eight passed" for 3878, and
# "five six four" for rho = 0.564, are HARDER to follow aloud, not easier.
# Rule 27 (v1.7) now requires digits. WORD_NUMBER below reports the violation.
#
# A spelled value still SATISFIES the quantity test, because an old compliant
# note is not retroactively vague. Rule 27 is reported separately.
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

# RULE 27 (v1.7) -- NUMERALS STAY NUMERALS.
# Only COMPOUND spelled numbers are flagged: two or more number-words joined, or
# any use of hundred/thousand/million with a companion. "one command" and "three
# fixes" are prose and stay; "twenty seven", "one hundred and seventy eight
# thousand", "five six four" are DATA wearing a costume. Keeping the test to
# compounds is what stops this becoming a linter nobody runs.
_NW = (r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
       r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
       r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)")
WORD_NUMBER = re.compile(rf"\b{_NW}(?:[ -](?:and[ -])?{_NW})+\b", re.I)
# Ordinals and dates read naturally aloud and are NOT data: "the twenty sixth of
# August", "the first of three". Excluded so the check keeps its credibility.
WORD_NUMBER_OK = re.compile(
    r"\b(?:twenty|thirty)[ -](?:first|second|third|fourth|fifth|sixth|seventh|"
    r"eighth|ninth)\b|\bone of (?:two|three|four|five)\b", re.I)

# RULE 28 (v1.7) -- CALL IT WHAT THE FOUNDER CALLS IT.
# A category noun standing where the project's own name belongs. Rule 19 bans
# "the mechanism"; this is the same fault one level up, where a thing that HAS a
# short name the founder types daily is described by its job instead.
CATEGORY_NOUN = {
    "the save routine": "sv", "the save script": "sv",
    "the state save routine": "sv", "the state-save script": "sv",
    "the recovery script": "rs", "the quality control script": "qc",
    "the decay curve measure": "gamma", "the convergence measure": "gamma",
}


# RULE 1 GUARD -- A NOTE MAY NOT CLAIM A TIME IT HAS NOT REACHED.
# Added 2026-08-27 01:12 BST, immediately after writing two notes stamped 01:30
# and 01:35 when the clock read 01:11. That is 18 and 23 minutes in the FUTURE.
#
# THIS IS A DIFFERENT DEFECT FROM THE ONE FIXED ON 2026-08-26, and the difference
# is the whole point. That night, five timestamps were TYPED instead of read, and
# the UserPromptSubmit clock hook was written to fix it. The hook worked: it gave
# the time at turn start, 00:40.
#
# Tonight the failure was extrapolation. The time was known once and then guessed
# forward across a 30-minute turn. A hook that fires at turn START cannot fix a
# turn that runs for half an hour. Only comparing the claim against the file
# itself can.
STAMP_LINE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})[,]?\s+(\d{2}):(\d{2})\s+([A-Z]{2,5})", re.M)


def future_stamp(path: pathlib.Path):
    """Return (claimed, actual) when the note's own stamp is ahead of its mtime."""
    import datetime as _dt
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        mtime = _dt.datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None
    m = STAMP_LINE.search(text[:800])
    if not m:
        return None
    try:
        claimed = _dt.datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}",
                                        "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    # 2 minutes of slack: writing a file takes a moment, and rounding to the
    # minute can legitimately land one minute ahead.
    if claimed > mtime + _dt.timedelta(minutes=2):
        return (claimed.strftime("%Y-%m-%d %H:%M"), mtime.strftime("%Y-%m-%d %H:%M"))
    return None


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
        # Quote-stripping applies to EVERY rule, not only 27 and 28. A note that
        # quotes someone else's vagueness in order to name it is not being vague.
        # Applying it to only some rules was an inconsistency in this fix,
        # caught by running the linter on the first note written under v1.7.
        unquoted = re.sub(r'"[^"]*"', " ", s)
        low = unquoted.lower()
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
        # QUOTED VIOLATIONS ARE NOT VIOLATIONS. A note that names a bad form in
        # order to correct it -- the standard file itself, or any note quoting
        # what was written before -- is doing the opposite of committing the
        # fault. Found immediately: the first v1.7 note reported 4 findings, all
        # four being the sentences that QUOTE the wording they are banning. A
        # linter that fires on the document explaining the rule gets ignored,
        # which this file's own header warns about.
        m = WORD_NUMBER.search(unquoted)
        if m and not WORD_NUMBER_OK.search(m.group(0)):
            out.append((para_no, "SPELLED NUMBER (Rule 27: use digits)",
                        m.group(0), s))
        for phrase, name in CATEGORY_NOUN.items():
            if phrase in low:
                out.append((para_no, f"CATEGORY NOUN (Rule 28: say {name!r})",
                            phrase, s)); break
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
        # `is not None`, not a bare truth test. future_stamp returns Optional
        # tuple, so `if fs:` is correct -- but it is INDISTINGUISHABLE at a
        # glance from the (bool, message) pattern that this project's own guard
        # test_no_script_discards_a_verdict_by_testing_the_tuple exists to catch,
        # and that guard flagged this line within twenty minutes of it being
        # written. Being right is not the same as being readable.
        fs = future_stamp(p)
        if fs is not None:
            hits = [(1, "FUTURE TIMESTAMP (Rule 1: read the clock, do not extrapolate)",
                     fs[0], f"note claims {fs[0]}; the file was written at {fs[1]}")] + hits
        total += len(hits)
        print(f"\n  {p.name}: {len(hits)} finding(s)")
        for para_no, kind, token, s in hits:
            print(f"    para {para_no}  {kind}  ({token!r})")
            print(f"      {s[:150]}{'...' if len(s) > 150 else ''}")
    print(f"\n  {total} finding(s). Reported, not enforced — read before delivering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
