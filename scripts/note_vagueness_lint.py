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
import ast
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
    # 3 CONDITIONS, AND NONE OF THEM SUBSUMES THE OTHERS. The original check was
    # the tally alone and missed a stray close before an unclosed open, which
    # balances at 1 and 1. Replacing it with the ordered walk alone then missed 2
    # begins and 1 end, which is ordered-consistent -- the second begin changes
    # no state and the single end closes -- and yet counts 2 against 1. The tally
    # was not WRONG, it was INSUFFICIENT, so it is restored beside the other 2
    # rather than in place of them.
    if state["unclosed"] or state["stray_closes"] or state["opens"] != state["closes"]:
        why = []
        if state["unclosed"]:
            where = state["opened_at"]
            why.append(f"a region opened at paragraph {where} is still open at "
                       f"end of file, so every paragraph after it is silently "
                       f"exempt")
        if state["opens"] != state["closes"] and not state["unclosed"]:
            why.append(f"{state['opens']} begin marker(s) against "
                       f"{state['closes']} end marker(s), which is malformed even "
                       f"though no region is left open -- 2 begins in 1 paragraph "
                       f"is the shape that does this")
        if state["stray_closes"]:
            why.append(f"{state['stray_closes']} verbatim-end marker(s) close "
                       f"nothing, which is how a tally of markers can look "
                       f"balanced while a region is open")
        counted.insert(0, (1, "UNBALANCED VERBATIM REGION (Rule: an unclosed "
                              "region exempts every paragraph after it)",
                           f"{state['opens']} begin, {state['closes']} end",
                           "; ".join(why)))
    return (counted, exempted)


#: The note standard a delivered note or TTS file must name. Bumped WITH the standard.
CURRENT_NOTE_STANDARD = "v1.7"
NOTE_STANDARD_STAMP = re.compile(r"note standard\s+v(\d+(?:\.\d+)?)", re.I)


def missing_standard_stamp(path) -> list:
    """A delivered note or TTS file must name the CDSFL note standard it was written under.

    HIS INSTRUCTION, 2026-10-11: *"You have returned again to not printing the CDSFL notes
    standard used to produce these files. This is a small glitch, but meaningful and should be
    fixed (prerably mechanically so you don't forget again), as it helps me to track which notes
    standards you are using across files."*

    MECHANICAL IS THE OPERATIVE WORD. The stamp was present on the notes of 2026-10-08 and
    2026-10-09 and absent from BOTH files delivered on 2026-10-11, which is precisely the
    forget-again he is describing. Remembering is not a mechanism; a blocking check is.

    SCOPE, deliberately narrow. Only files under `experimental_notes/` and a `*_tts/` folder are
    DELIVERED artefacts. A README, a registry, a producer's own output and a source file are not
    notes and are not stamped, so checking them would make the rule noise and get it switched off.
    """
    pth = pathlib.Path(path)
    parts = {q.lower() for q in pth.parts}
    is_note = ("experimental_notes" in parts
               or any(q.endswith("_tts") for q in parts))
    if not is_note or pth.suffix.lower() not in (".md", ".txt"):
        return []
    try:
        text = pth.read_bytes().decode("utf-8", errors="ignore")
    except OSError:
        return []
    m = NOTE_STANDARD_STAMP.search(text)
    if not m:
        return [(0, "MISSING NOTE STANDARD STAMP", "note standard",
                 f"name the standard in the file, e.g. 'Written under CDSFL note standard "
                 f"{CURRENT_NOTE_STANDARD}.' He tracks which standard produced which file.")]
    found = "v" + m.group(1)
    if found != CURRENT_NOTE_STANDARD:
        return [(0, f"NOTE STANDARD STAMP IS {found}, CURRENT IS {CURRENT_NOTE_STANDARD}",
                 "note standard",
                 "either update the file, or say explicitly why it is pinned to an older one.")]
    return []


# ---------------------------------------------------------------------------
# RULE 30 (2026-10-15) — A TERM THAT EXISTS NOWHERE IN THE PROJECT.
#
# THE FOUNDER'S COMPLAINT, TWICE IN ONE DAY. "You are using non-project terms
# again. You said you had fixed it so you would stop." And, on the preceding
# note: "What is the 'discrimination guard'? I am unfamiliar with this term. Is
# it official project terminology?"
#
# AND HIS TEST OF WHETHER A FIX IS A FIX: "Is 'the lesson is recorded' the same
# as saying the problem that caused it has now been fixed? Because if not you
# should probably also fix the cause rather than just record the symptom."
#
# THE CAUSE, MEASURED. 4 terms used to him in 2 notes on 2026-10-15, checked
# against the glossary and the project's documentation:
#
#   coherence budget      0 glossary hits,  4 docs files  -> REAL but UNDEFINED
#   discrimination guard  0 glossary hits,  0 docs files  -> MINTED HERE
#   paired baseline       0 glossary hits,  0 docs files  -> MINTED HERE
#   consequence gate      0 glossary hits,  0 docs files  -> MINTED HERE
#
# So the cause has 2 halves and this rule treats both. 3 of the 4 terms exist
# NOWHERE in the project: they were invented in a note and then used to him as
# though they were the project's vocabulary. The 4th is a genuine term the
# composer emits at run time that was never written into the glossary, so a
# reader who meets it has nowhere to look it up.
#
# ★ THE VOCABULARY DELIBERATELY EXCLUDES `experimental_notes/`. A term invented
# in a note yesterday must not legitimise itself today, which is the same trap
# as a test asserting on a module's own source text: each description is
# individually consistent and the pair can still be wrong. The vocabulary is
# therefore the glossary, the documentation, the project and global directive
# files, and the SOURCE CODE -- because a term the code emits is a real term
# whatever the glossary omits.
_TERM_NOUNS = (
    "guard", "gate", "budget", "baseline", "barrier", "cell", "ladder",
    "sweep", "probe", "arm", "band", "tagger", "envelope", "ratchet",
    "tripwire", "harness", "seam", "rung", "stamp", "gateway", "filter",
    "threshold", "composer", "classifier", "verifier", "falsifier",
)

#: A first word that makes the phrase ordinary English rather than a term.
_TERM_STOP_FIRST = frozenset("""
the this that these those each every same other another next last first second
third final whole single real only new old its his her their our your my a an
any no none one two three more most such which what some both either neither
own very much many few several all most least best worst main key core
and or but not now also then still already again even just very only
existing current done test sole internal external above below here there
""".split())

#: ★ THE DEFINITE ARTICLE IS THE PREDICATE, AND IT WAS FITTED RATHER THAN
#: CHOSEN. A bare "<word> <noun>" test gave 2,841 findings across 426 of 523
#: notes -- unusable, and most of it grammatical accident: "and gate", "now
#: gate", "test baseline". A COINED term is introduced as a DEFINITE noun
#: phrase, which is exactly how the founder met all 4 of them: "What is the
#: 'discrimination guard'?" So the pattern requires "the". Measured on the same
#: 523 notes: 745 findings across 247, and it still catches both terms he
#: challenged while correctly passing `coherence budget` and `skin barrier`,
#: which are real.
TERM_PHRASE = re.compile(r"\bthe\s+([a-z][a-z-]{2,})\s+("
                         + "|".join(_TERM_NOUNS) + r")s?\b")


#: ★ THE FOURTH SELF-LEGITIMISING PATH, and the one that only appears once the
#: rule works. Documenting a coinage in order to deprecate it ADMITS IT AS
#: VOCABULARY: writing in `docs/GLOSSARY.md` that a mechanism "had been referred
#: to as the confinement guard, which is not its name" made `confinement guard`
#: pass the rule. The 3 earlier paths were the rule's own explanatory comment,
#: the producer scripts, and its own test fixtures.
#:
#: So a line may mark itself as naming a coinage rather than using one, with the
#: marker below, and the vocabulary drops that line. This is the only way the
#: glossary can tell a reader "this is not what it is called" without thereby
#: making it what it is called.
_COINAGE_MARKER = "[coinage]"


def _drop_coinage_lines(text: str) -> str:
    return "\n".join(l for l in text.split("\n") if _COINAGE_MARKER not in l)


def _module_string_literals(src: str) -> str:
    """Every string the module can EMIT, with docstrings excluded.

    ★ WHY LITERALS AND NOT THE WHOLE FILE. A first version read every .py file
    whole and the rule came out VACUOUS: all 4 terms it was built to catch were
    "in vocabulary", because this rule's own explanatory comment names them, and
    so do the producer scripts written the same hour. A module's comments are
    CC1's narration, and admitting narration as vocabulary is the same defect as
    a test asserting on its own module's source text -- the description and the
    thing described agree with each other and can both be wrong.

    So the vocabulary is what the FOUNDER CAN LOOK UP (the glossary, the
    documentation, the directive files) plus what the PROGRAM ACTUALLY PRINTS
    (string literals in `bench/`). Docstrings are narration and are dropped.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return ""
    doc_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            body = getattr(node, "body", None) or []
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                doc_ids.add(id(body[0].value))
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in doc_ids):
            out.append(node.value)
    return "\n".join(out)


def _project_vocabulary() -> str:
    """Every place a LEGITIMATE project term can be defined or emitted.

    Notes are excluded on purpose, and so is this file: see the rule comment.
    """
    repo = pathlib.Path(__file__).resolve().parents[1]
    me = pathlib.Path(__file__).resolve()
    parts: list[str] = []
    # 1. What the founder can look up.
    for rel in ("docs", ".claude"):
        d = repo / rel
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix in (".md", ".toml"):
                    try:
                        parts.append(_drop_coinage_lines(f.read_text(errors="ignore")))
                    except OSError:
                        pass
    for extra in (repo / "README.md",
                  pathlib.Path.home() / ".claude" / "CLAUDE.md"):
        if extra.is_file():
            try:
                parts.append(extra.read_text(errors="ignore"))
            except OSError:
                pass
    # 2. What the program prints. `bench/` only -- `scripts/` holds producers
    #    whose prose is CC1's own narration, which is what half this defect was.
    d = repo / "bench"
    if d.is_dir():
        for f in d.rglob("*.py"):
            sp = str(f)
            # ★ TESTS ARE EXCLUDED, AND THIS RULE HAD TO BE DEFENDED AGAINST
            # THREE SUCCESSIVE SELF-LEGITIMISING PATHS. First its own
            # explanatory comment named all 4 coined terms, so reading whole .py
            # files made it vacuous. Then the producer scripts written the same
            # hour did. Then its own TEST FILE did, through the string fixtures
            # that feed it the coined phrases -- so the rule reported 0 findings
            # on a note the test had just handed it a coinage in.
            #
            # The principle that settles all 3: vocabulary is what the FOUNDER
            # CAN LOOK UP, or what the PROGRAM EMITS DURING A RUN. A test's
            # fixtures are neither.
            if ("/logs/" in sp or "harvest" in sp.lower()
                    or "/tests/" in sp or f.name.startswith("test_")
                    or f.resolve() == me):
                continue
            try:
                parts.append(_module_string_literals(f.read_text(errors="ignore")))
            except OSError:
                pass
    return "\n".join(parts).lower()


_VOCAB_CACHE: list = []


def project_vocabulary() -> str:
    if not _VOCAB_CACHE:
        _VOCAB_CACHE.append(_project_vocabulary())
    return _VOCAB_CACHE[0]


#: ★ A RATCHET, NOT A RETROSPECTIVE BLOCK. 745 instances already exist across
#: 247 notes, so blocking on the absolute count would refuse 47.23% of the
#: project's own archive and teach its reader that the checker is noise. The
#: enforcement that matters is on notes written FROM NOW: a note delivered to
#: the founder carries 0. Historical notes are reported and the baseline below
#: may only fall. Terms this rule surfaced that are REAL project mechanisms
#: belong in `docs/GLOSSARY.md` -- defining the vocabulary is the additive fix,
#: banning it is not.
#: Measured by the LIVE rule, not by an earlier draft of it: a baseline
#: produced by a different predicate is the like-for-like error this
#: project made with the lint ratchet earlier the same day.
#:
#: ★ MOVED FROM 734/243 TO 869/263 ON THE SAME DAY, and the increase is the
#: rule getting STRONGER rather than the archive getting worse. 734 was
#: measured BEFORE the `[coinage]` marker existed. Until then, the glossary
#: entry naming `confinement guard` in order to deprecate it was admitting
#: that phrase as vocabulary and masking it everywhere it appeared. Dropping
#: coinage-marked lines re-exposed it and others like it. A baseline measured
#: under a different predicate is not a baseline, which is the whole reason
#: this comment exists.
RULE30_RATCHET_BASELINE = 869
RULE30_RATCHET_NOTES = 263


def undefined_project_terms(path) -> list:
    """Findings for compound technical terms absent from the whole project."""
    try:
        text = pathlib.Path(path).read_text(errors="ignore")
    except OSError:
        return []
    vocab = project_vocabulary()
    out, seen = [], set()
    for para_no, para in enumerate(paragraphs(text), start=1):
        clean = INLINE_CODE.sub(" ", _strip_quoted(para))
        for m in TERM_PHRASE.finditer(clean.lower()):
            first, noun = m.group(1), m.group(2)
            if first in _TERM_STOP_FIRST:
                continue
            phrase = f"{first} {noun}"
            if phrase in seen:
                continue
            if phrase in vocab or f"{first}_{noun}" in vocab:
                continue
            seen.add(phrase)
            out.append((para_no, "undefined-project-term", phrase,
                        para.strip().replace("\n", " ")))
    return out


def blocking(path) -> list:
    """The findings that COUNT. What a guard must gate on."""
    # ★ RULE 30 IS REPORTED, NOT BLOCKING, AND THAT WAS DECIDED BY MEASUREMENT
    # AFTER IT REFUSED A COMPLIANT NOTE (2026-10-15).
    #
    # It was wired in here first, because this file's own comments warn that a
    # rule reached by nothing is not additive. Within the hour it blocked the
    # session's own technical note on 9 findings, of which the genuine coinages
    # were 1: the rest were ORDINARY DESCRIPTIVE ENGLISH that happens to end in
    # a term noun -- "pinned threshold", "committed baseline", "abstract
    # verifier", "baseline arm".
    #
    # MEASURED over the project's 523 notes: of 869 instances, a suffix
    # heuristic puts 544 in the noun-plus-noun class, 62.6007%, 95% Wilson
    # [59.3348%, 65.7557%], and 325 in the adjectival class, and the heuristic
    # itself misclassifies nouns ending in -ent. There is NO structural
    # difference between "pinned threshold" (a description) and "paired
    # baseline" (a coinage the founder challenged), so the rule cannot separate
    # them and must not pretend to.
    #
    # Gating on a check with that precision would refuse roughly 1 note in 2 and
    # teach its reader that the checker is noise -- which is the failure this
    # rule's own ratchet comment names. The founder's ruling of 2026-09-04 made
    # a SPELLED-NUMBER finding blocking; it did not make every rule blocking.
    #
    # SO THE CAPABILITY IS INTACT AND ONLY THE GATE COUPLING CHANGED: Rule 30
    # still runs, still reports through `main()`, and still carries a committed
    # ratchet. It returns here when it can tell a coinage from an adjective.
    return partition(path)[0] + missing_standard_stamp(path)


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
    opened_at: int | None = None
    for n, _off, kind in marker_events(text):
        # Every paragraph between the opening one and this one is inside.
        if inside:
            marked.update(range(last_para, n + 1))
        if kind == "begin":
            opens += 1
            marked.add(n)
            if not inside:
                opened_at = n
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
            "unclosed": inside, "stray_closes": stray,
            # WHERE it opened, not just THAT it did. A reader told only that a
            # region is unclosed still has to find it; the paragraph number is
            # the difference between a report and a diagnosis.
            "opened_at": opened_at if inside else None}


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
        # WIRED HERE, NOT ONLY IN `blocking()`. A first attempt added the stamp check to
        # `blocking()` alone and reported 0 findings on files that plainly lacked a stamp,
        # because `main()` calls `partition()` directly -- an UNWIRED ADDITION, which is the
        # exact defect the additive standard names and the one this whole session measured.
        # Rule 30 is wired HERE as well as in `blocking()`, for the reason the
        # comment above gives: `main()` calls `partition()` directly, so a rule
        # added only to `blocking()` reports 0 findings to a human reader.
        counted = (counted + missing_standard_stamp(p)
                   + undefined_project_terms(p))
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
