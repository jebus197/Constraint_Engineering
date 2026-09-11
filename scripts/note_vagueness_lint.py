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


#: A double-quoted span, which may run across sentence boundaries.
_QUOTED_SPAN = re.compile(r'"[^"]*"', re.DOTALL)


def mask_quoted(flat: str) -> str:
    """Blank every double-quoted span, preserving length and sentence structure.

    THE EXEMPTION HAS TO BE APPLIED BEFORE THE SENTENCE SPLIT, and applying it
    after was a real defect. `lint` stripped balanced `"..."` pairs from each
    SENTENCE, but a quotation spanning more than 1 sentence is split first, so
    each fragment carries an unbalanced quote character and matches nothing --
    the exemption silently lapses on exactly the longest quotations, which are
    the founder's. Measured 2026-09-09 on the master task list: 1 of 3 findings
    was a fragment of a verbatim founder quote.

    THIS MATTERS MORE SINCE 2026-09-09 than when it was first recorded, because
    the linter became BLOCKING at commit time that day. A false positive inside
    a quotation would leave 2 choices, editing the founder's words or bypassing
    the guard, and the standing rule is that the linter is NEVER applied to his
    words and never gates his input.

    Sentence terminators inside the quote are blanked too, so the quote cannot
    fragment the sentences around it. SINGLE quotes are deliberately NOT masked:
    the founder's convention is that single quotes mark paraphrase or emphasis
    and double quotes mark verbatim quotation, so only the latter is exempt.
    """
    return _QUOTED_SPAN.sub(lambda m: " " * len(m.group(0)), flat)


#: The ONE paragraph break. Written once because 2 expressions of it is what
#: broke the verbatim exemption -- see `paragraphs`.
PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")


def paragraphs(text: str) -> list[str]:
    """Split into blank-line-separated blocks. THE ONLY splitter in this module.

    FOUND 2026-09-11 BY BOTH PANEL SEATS INDEPENDENTLY, in separate sandboxes,
    and reproduced here before either fix was accepted. `sentences()` split on a
    literal 2-newline string and `verbatim_paragraphs()` on a whitespace-tolerant
    regular expression. A blank
    line carrying ONE SPACE is a paragraph break to the second and not to the
    first, so the two paragraph NUMBERINGS drift apart -- and the exempt set,
    computed by the second, is applied to findings numbered by the first.

    THE CONSEQUENCE IS AMNESTY FOR THE NOTE'S OWN PROSE. Measured on a fixture
    whose Rule 27 violation sits AFTER `verbatim-end`, in the note's own voice:

        before: `amnesty.md: 0 finding(s)` with the sentence tagged [verbatim]
        control, same bytes without the space: `1 finding(s)`

    The count is what the blocking pre-commit ratchet reads, so the note commits.
    `verbatim_paragraphs`' docstring asserted the 2 numberings *"agree by
    construction rather than by coincidence"*. They agreed by coincidence, on
    files whose blank lines happen to be byte-exact: **20 of 730 markdown files
    in this tree already break that coincidence, 2.7397%, Wilson [1.7804%,
    4.1938%], Clopper-Pearson [1.6814%, 4.1997%]**.

    THE REGEX FORM IS THE CORRECT ONE, not merely the surviving one: a line
    holding only whitespace IS a paragraph break to every markdown renderer, and
    to a reader.
    """
    return PARAGRAPH_BREAK.split(text)


def sentences(text: str):
    """Yield (paragraph number, sentence) with quotes kept WHOLE.

    THE MASK GUIDES THE SPLIT AND NOTHING ELSE, and getting that wrong was a
    measured regression rather than a hypothetical one. A first version yielded
    the MASKED text, which deleted the nouns and figures living inside a
    quotation -- so `NAMED` stopped seeing them and sentences whose specificity
    was carried by the quote were reported as vague. Measured across 379 notes:
    it removed 8 false positives and INTRODUCED 3, among them "The [blank] above
    is withdrawn as a confirmed count", which names its subject perfectly well
    inside the quotation the mask had erased.

    `mask_quoted` preserves length, so offsets in the masked string index the
    original exactly. The split points come from the mask; the text comes from
    the original. `lint` then does its own per-sentence quote handling on a
    sentence that now contains the whole quotation rather than a fragment of it.
    """
    for para_no, para in enumerate(paragraphs(text), 1):
        flat = " ".join(para.split())
        if not flat or flat.startswith(("|", "#", "```")):
            continue
        masked = mask_quoted(flat)
        start = 0
        for brk in re.finditer(r"(?<=[.!?])\s+", masked):
            seg = flat[start:brk.start()]
            if len(seg.split()) >= 5:
                yield para_no, seg
            start = brk.end()
        seg = flat[start:]
        if len(seg.split()) >= 5:
            yield para_no, seg


#: A region reproducing someone else's words UNALTERED. Between these markers
#: the linter reports but does not COUNT, because the only way to satisfy it
#: would be to edit the record.
#:
#:     <!-- verbatim-begin: <who or what> -->
#:     ... their words, exactly as produced ...
#:     <!-- verbatim-end -->
#:
#: WHY THIS EXISTS. The founder's standing rule is that the linter is never
#: applied to his words and never gates his input. `mask_quoted` already carries
#: that for inline double quotes. It cannot carry a 20,000-character panel
#: transcript, and the Personalisation directive requires those to be preserved
#: in full and unfiltered -- *"Never summarise in place of the full output"*.
#:
#: Demonstrated 2026-09-10: `Panel_Round4_FULL_RECORD_2026-09-10.md` reproduces 2
#: seats verbatim and carries 4 findings, every one inside quoted model output --
#: including a seat writing "nine figures", which violates `no-word-numbers`.
#: The commit hook's per-file ratchet refuses any NEW note whose count rises
#: above 0, so the record could not be committed without editing what the models
#: actually said. Editing it would falsify the record, which is worse than any
#: vagueness in it.
#:
#: THE EXEMPTION IS NOT SILENT AND IT IS NOT WHOLE-FILE. Findings inside a
#: verbatim region are still printed, under their own heading, with their own
#: count. Prose OUTSIDE the markers is linted normally, so a note cannot buy
#: amnesty for its own writing by quoting someone.
def partition(path) -> tuple[list, list]:
    """(counted, exempted) for one note: everything `lint` reports plus the
    structural findings, split on whether it sits inside a verbatim region.

    WHY THIS IS A FUNCTION AND NOT 4 LINES IN `main`. The exemption used to live
    only in `main`, so every other consumer had to re-derive it -- and one did
    not. `test_note_standard_v17_enforced_2026-08-26.py` called `lint()` raw and
    failed the suite on a sentence a panel seat wrote inside a verbatim region.
    Task V8 exists precisely so a seat's words reach the record unedited; a guard
    that blocks on them defeats it.

    `main` CALLS this rather than reimplementing it, so the CLI and every test
    cannot drift apart. That is the `execute-do-not-grep` shape: 1 implementation
    with 2 callers, never 2 implementations asserted to agree.

    THE 2 STRUCTURAL FINDINGS ARE ADDED AFTER THE SPLIT, NEVER BEFORE. A report
    ABOUT a region must not be swallowed BY that region. The future-stamp finding
    was added before the split until panel round 15 (fable) showed a note whose
    FIRST paragraph opens a region buying amnesty for its own Rule 1 violation --
    the unbalanced finding was region-immune and the future-stamp finding was
    not, and that inconsistency was the defect.
    """
    hits = lint(path)
    text = path.read_text(encoding="utf-8")
    state = region_state(text)
    exempt = state["marked"]
    counted = [h for h in hits if h[0] not in exempt]
    exempted = [h for h in hits if h[0] in exempt]

    # `is not None`, not a bare truth test. future_stamp returns Optional
    # tuple, so `if fs:` is correct -- but it is INDISTINGUISHABLE at a glance
    # from the (bool, message) pattern that this project's own guard
    # test_no_script_discards_a_verdict_by_testing_the_tuple exists to catch,
    # and that guard flagged this line within twenty minutes of it being
    # written. Being right is not the same as being readable.
    fs = future_stamp(path)
    if fs is not None:
        counted.insert(0, (1, "FUTURE TIMESTAMP (Rule 1: read the clock, do not "
                              "extrapolate)", fs[0],
                           f"note claims {fs[0]}; the file was written at {fs[1]}"))

    # AN UNCLOSED REGION EXEMPTS TO END OF FILE, AND SAYS NOTHING WHILE IT DOES.
    # Gated on the ORDERED state, not on `opens != closes`: a stray close before
    # an unclosed open balances the tally while a region is genuinely open.
    if state["unclosed"] or state["stray_closes"]:
        why = []
        if state["unclosed"]:
            why.append("a region is still open at end of file, so every "
                       "paragraph after it is silently exempt")
        if state["stray_closes"]:
            why.append(f"{state['stray_closes']} verbatim-end marker(s) close "
                       f"nothing, which is how a tally of markers can look "
                       f"balanced while a region is open")
        counted.insert(0, (1, "UNBALANCED VERBATIM REGION (Rule: an unclosed "
                              "region exempts every paragraph after it)",
                           f"{state['opens']} begin, {state['closes']} end",
                           "; ".join(why)))
    return (counted, exempted)


def blocking(path) -> list:
    """The findings that COUNT. What a guard must gate on."""
    return partition(path)[0]


#: Rule 28's phrases, bounded so an inflection is not read as the noun.
#:
#: A BARE SUBSTRING TEST MATCHED THE VERB. `"the decay curve measure" in low`
#: fires on "the decay curve measureS the latter" and on "measureMENT" -- and it
#: did, on `Panel_Roster_Round2_FULL_RECORD_2026-09-09.md`, where the sentence is
#: a seat using the founder's own term "the decay curve" with a verb after it.
#: Rule 28 asks that gamma be CALLED gamma; it does not ban the founder's phrase
#: from appearing as a subject.
#:
#: MEASURED over 402 notes before the change: 28 substring matches, 27 bounded
#: matches. The fix drops exactly 1, and that 1 is the verb above.
CATEGORY_NOUN_RE = {ph: re.compile(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])")
                    for ph in CATEGORY_NOUN}

VERBATIM_BEGIN = re.compile(r"<!--\s*verbatim-begin:.*?-->")
VERBATIM_END = re.compile(r"<!--\s*verbatim-end\s*-->")


def marker_events(text: str):
    """Every verbatim marker, in DOCUMENT ORDER, as (paragraph, offset, kind).

    Markers that are SHOWN rather than used -- inside a code fence or an inline
    span -- are already gone, because `_strip_quoted` runs first.

    ORDER IS THE WHOLE POINT, and its absence was 2 defects. The previous walk
    kept 1 bool per paragraph (`opened`, `closed`) and applied `closed` last
    regardless of where it sat, so `verbatim-end` followed by `verbatim-begin` in
    a SINGLE paragraph ended the exemption when it should have opened one -- and
    a seat's quoted words were then COUNTED, which is precisely the V8 defeat the
    exemption exists to prevent. A second bool-per-paragraph counter made 2
    begins in 1 paragraph read as 1. Both found by panel round 15, independently,
    by both seats.
    """
    for n, para in enumerate(paragraphs(text), 1):
        scan = _strip_quoted(para)
        events = [(m.start(), "begin") for m in VERBATIM_BEGIN.finditer(scan)]
        events += [(m.start(), "end") for m in VERBATIM_END.finditer(scan)]
        for off, kind in sorted(events):
            yield n, off, kind


def region_state(text: str) -> dict:
    """One ordered walk; every consumer reads its answer from here.

    Returns `marked` (paragraphs inside a region), `opens`, `closes`,
    `unclosed` (a region still open at end of file) and `stray_closes` (a close
    with no region open).

    A TALLY IS ORDER-BLIND AND AN UNCLOSED REGION IS A FACT ABOUT ORDER. The
    balance check added earlier on 2026-09-11 compared `opens != closes`, so a
    stray `verbatim-end` BEFORE an unclosed `verbatim-begin` gave 1 and 1 and the
    guard said BALANCED while a region really was open and really did exempt to
    end of file -- the silent amnesty it was written to end, unchanged, inside
    the guard that was supposed to end it. cc2 put it exactly that way.
    """
    marked: set[int] = set()
    inside = False
    opens = closes = stray = 0
    last_para = 0
    for n, _off, kind in marker_events(text):
        # Every paragraph between the opening one and this one is inside.
        if inside:
            marked.update(range(last_para, n + 1))
        if kind == "begin":
            opens += 1
            marked.add(n)
            inside = True
            last_para = n
        else:
            closes += 1
            if inside:
                marked.add(n)
                inside = False
            else:
                stray += 1
        last_para = n
    if inside:
        total = len(list(paragraphs(text)))
        marked.update(range(last_para, total + 1))
    return {"marked": marked, "opens": opens, "closes": closes,
            "unclosed": inside, "stray_closes": stray}


def verbatim_paragraphs(text: str) -> set[int]:
    """Paragraph numbers that fall inside a verbatim region.

    Paragraph numbering matches `sentences()` because both call `paragraphs()`.

    THAT SENTENCE USED TO READ "the 2 agree by construction rather than by
    coincidence" AND IT WAS FALSE. They were 2 hand-written expressions of one
    rule with no comparator -- the shape `execute-do-not-grep` names -- sitting
    inside the exemption whose entire claim is that it is scoped. Rewritten
    rather than deleted, so the claim's history stays visible.

    A MARKER INSIDE A CODE FENCE IS DOCUMENTATION, NOT AN INSTRUCTION, and so is
    one inside an inline span; `_strip_quoted` removes both. The fenced half was
    found 2026-09-11 by the fable seat, the inline half the same day by a
    paragraph of `CDSFL_OUTCOMES_LOG.md` describing the marker and silently
    exempting 12 paragraphs.

    DELEGATES to `region_state` so the exemption and the balance check cannot
    disagree about what a marker is: 1 implementation, 2 callers.
    """
    return region_state(text)["marked"]


def _strip_quoted(para: str) -> str:
    """Everything in the paragraph that is SHOWN rather than used.

    `_strip_fenced` removes fenced blocks. It does not remove INLINE code spans,
    and on 2026-09-11 a paragraph of `CDSFL_OUTCOMES_LOG.md` wrote the
    begin-marker inside single backticks while describing it. That opened a real
    region, nothing closed it, and **12 paragraphs from there to the end of the
    file stopped being linted** -- silently, because an exemption reports nothing
    when it swallows a file.

    A marker wrapped in backticks is being quoted, exactly as a fenced one is.
    The fenced rule was already right about this; it simply did not reach far
    enough. `_strip_fenced` is untouched and still used by this function.
    """
    return INLINE_CODE.sub(" ", _strip_fenced(para))


#: An inline code span: `like this`, or ``like `this` ``.
INLINE_CODE = re.compile(r"`+[^`\n]*`+")


def _strip_fenced(para: str) -> str:
    """Blank out ``` fenced spans, preserving line count so numbering is safe."""
    out, fenced = [], False
    for line in para.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


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
            if CATEGORY_NOUN_RE[phrase].search(low):
                out.append((para_no, f"CATEGORY NOUN (Rule 28: say {name!r})",
                            phrase, s)); break
    return out


def main() -> int:
    # ANSWER `--help` RATHER THAN LINTING IT. Found 2026-09-11 by task A16's
    # survey. The comment 6 lines below already anticipated this exactly -- "an
    # unrecognised flag, which lands here as a 'path'" -- and treating that as a
    # missing file is the right behaviour for a TYPO and the wrong one for a
    # request for usage. The distinction is that `--help` is a request this
    # program can satisfy, and a program that answers the wrong complaint first
    # teaches its reader that its diagnostics are unreliable.
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        print("\n  usage: note_vagueness_lint.py <file> [file ...]")
        return 0
    paths = [pathlib.Path(a) for a in sys.argv[1:]]
    if not paths:
        print("  usage: note_vagueness_lint.py <file> [file ...]"); return 1
    total = 0
    # A NAMED FILE THAT IS NOT THERE IS A FAILURE, NOT A SKIP (2026-08-30).
    # This returned 0 for a path it never opened, so a typo -- or an
    # unrecognised flag, which lands here as a "path" -- produced
    # "missing: X" followed by a clean exit. A caller sees success and
    # delivers an UNLINTED note believing it checked. Measured the same day:
    # `note_vagueness_lint.py --this-flag-does-not-exist` printed a missing
    # line and exited 0.
    missing = 0
    for p in paths:
        if not p.is_file():
            print(f"  missing: {p}"); missing += 1; continue
        counted, exempted = partition(p)
        total += len(counted)
        print(f"\n  {p.name}: {len(counted)} finding(s)")
        for para_no, kind, token, s in counted:
            print(f"    para {para_no}  {kind}  ({token!r})")
            print(f"      {s[:150]}{'...' if len(s) > 150 else ''}")
        if exempted:
            # PRINTED, NEVER HIDDEN. An exemption a reader cannot see is
            # indistinguishable from a checker that missed something.
            print(f"    ---- {len(exempted)} finding(s) inside a verbatim region, "
                  f"reported and NOT counted ----")
            for para_no, kind, token, s in exempted:
                print(f"    para {para_no}  {kind}  ({token!r})   [verbatim]")
                print(f"      {s[:150]}{'...' if len(s) > 150 else ''}")
    print(f"\n  {total} finding(s). Reported, not enforced — read before delivering.")
    if missing:
        # Findings stay advisory; a file that was never READ does not. Exiting 0
        # here told the caller the note had been checked when it had not.
        print(f"  {missing} named path(s) could not be read — NOTHING was linted "
              f"for those. Exiting non-zero so a typo cannot read as a clean note.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
