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
import subprocess
import re as _re
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

# ─────────────────────────────────────────────────────────────────────────────
# ★ RULE 27 IN FULL, ON HIS RULING OF 2026-10-19: "Verdict: Enforce going
# forward only." Entry B24.
#
# WHAT WAS UNDER-ENFORCED. `WORD_NUMBER` above requires a MULTI-WORD number, so
# a hyphenated compound is caught while a SINGLE number word standing before a
# noun is not. His ruling of 2026-09-04 admits no such distinction: "Digits
# only, in every context without exception". Found 2026-10-17 by linting a note
# written to his standard -- 0 findings reported on a file holding 22 of them.
#
# WHY IT IS DATE-GATED AND NOT RETROSPECTIVE. A bare detector over all 562 notes
# returns about 16,743 occurrences across 522 of them, which would either block
# every commit or force a re-baseline of the ratchet -- and re-baselining a
# ratchet to accommodate a detector change is lowering a number by changing the
# policy rather than the work, which entry C29 exists to refuse. His ruling is
# the same shape as his 2026-10-16 one on vendor names: "We normalise going
# forward ... I am not suggesting rewriting history."
#
# AND THE SCOPE IS FAR SMALLER THAN THE HEADLINE, MEASURED 2026-10-29. Of the
# 688 bare occurrences in notes dated on or after his ruling, 0.662791 are
# INSIDE verbatim regions -- another model's words, quoted. Rule 27 governs what
# this project WRITES, not a record of what someone else wrote, and the verbatim
# machinery already exempts them. In the notes' OWN voice the count is 232
# across 20 files, and the heaviest 3 panel records fall from 136, 116 and 110
# to 6, 3 and 3.
BARE_WORD_NUMBER = re.compile(rf"\b{_NW}\b", re.I)

#: IDIOMS WHERE A NUMBER WORD IS NOT A NUMBER. "no one", "one another", "at one
#: with" and the ordinals are English, not data, and his own rule exempts
#: ordinals and dates that read naturally aloud. Listed explicitly rather than
#: inferred, so a reader can see exactly what is forgiven.
#: ★ A PRONOMINAL `one` CARRYING A MODIFIER, added 2026-11-03. The list
#: below already exempts `the one`, `this one`, `each one` and `the only
#: one`, but not an adjective sitting between the article and the word, so
#: `the expensive one`, `an inherited one` and `a varying one` were
#: reported on correct English prose. Measured on the generated morning
#: report: 8 of its 13 spelled-number findings are this shape.
#:
#: IT CANNOT HIDE A NUMBER, and that is the reason it is safe rather than
#: convenient: the pattern matches only the token `one`, so a spelled
#: `two`, `three` or higher is untouched. Checked by running it over the
#: report and listing every token it silenced -- `one` and nothing else.
_PRONOUN_ONE_WITH_MODIFIER = re.compile(
    r"\b(?:the|a|an|that|this|another|its|his|her|their|our|my|every|"
    r"each|any|no|some|first|last|next|only)\s+(?:[a-z-]+\s+){1,2}one\b",
    re.I)

BARE_WORD_NUMBER_OK = re.compile(
    r"\b(?:no one|one another|one-off|one by one|one or (?:two|more|the other)|"
    r"at one|in one|as one|the one|this one|that one|each one|every one|"
    r"any one|some one|which one|the only one|not one|more than one|"
    #: ★ `one[- ]way` and `the same one` added 2026-11-02, on the ground this
    #: list already states for `one-line`, `one-off`, `two-sided` and
    #: `leave-one-out`: a hyphenated number word qualifying a noun is English,
    #: not data. `one-way` is the technical term for a guarantee that holds in
    #: a single direction -- the property a roster-aware convergence fix is
    #: measured against -- and rewriting it as `1-way` would be unreadable.
    #: `the same one` is a PRONOUN standing for a previously named run, exactly
    #: as `the one`, `this one` and `that one` already are in this list.
    r"one[- ]way|the same one|"
    r"one of (?:two|three|four|five|the|his|her|its|my|our|their|them|these|"
    r"those)|one another's|zero[- ]plant|zero[- ]day|one[- ]line|one[- ]off|"
    #: ★ `<digit>-zero` added 2026-11-02, on the ground this list already
    #: states for `two-sided` and `leave-one-out`: a hyphenated number word
    #: qualifying a noun is English, not data. It fired on this project's own
    #: phrase "the earliest 3-zero window", where the COUNT is already the
    #: digit 3 and `zero` names the value being counted. Rewriting it as
    #: "3-0 window" would be unreadable, and the alternative -- editing the
    #: authored detail to avoid the term -- would change a report's prose to
    #: satisfy a checker, which is the guard-accusing-correct-code shape
    #: recorded on 2026-10-28 where 9 of 36 failures were guards punishing the
    #: repair. `zero[- ]plant` was already here for the experiment's own name.
    r"\d+[- ]zeros?\b|"
    r"one[- ]sided|one[- ]way|one[- ]to[- ]one|ten[- ]fold|"
    #: ★ COMPOUND ADJECTIVES BUILT ON A NUMBER WORD ARE NOT COUNTS, added
    #: 2026-10-29 when the detector fired on this project's own term
    #: "two-sided gate". `one-off` and `one-sided` were already here; the gap
    #: was that only `one-` compounds had been enumerated. A hyphenated
    #: number word qualifying a noun is English, not data, which is the same
    #: ground on which his ruling exempts ordinals.
    #: ★ `leave-one-out` added 2026-10-31, same ground as `two-sided` above: it
    #: is the standard name of a resampling procedure, not a count of anything,
    #: and it fired on this project's own phrase "Leave-one-out on the live
    #: registry". A term is not data.
    r"leave[- ]one[- ]out|"
    r"two[- ]sided|two[- ]tier|two[- ]way|two[- ]fold|two[- ]part|"
    r"three[- ]fold|three[- ]way|three[- ]part|four[- ]fold|five[- ]fold|"
    r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[ -]"
    r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth))\b",
    re.I)

#: ★ THE CUTOFF IS THE DATE ENFORCEMENT BEGINS, NOT THE DATE HE RULED, and the
#: difference is 20 notes. His ruling of 2026-10-19 was "Enforce going forward
#: only", given on an entry whose option (2) proposed "files written after a
#: cutoff" without fixing which cutoff.
#:
#: WHY THE LATER DATE IS THE FAITHFUL ONE. Between his ruling and this detector
#: landing, 20 notes were written while NO CHECKER EXISTED to hold them to the
#: full rule. Measured through the command line on 2026-10-29: those 20 carry
#: 165 COUNTED findings, with 317 more correctly exempted inside verbatim
#: regions. Holding them to a rule nothing enforced at the time is the
#: retrospection his ruling refuses, and the project's own precedent is his
#: 2026-10-16 wording on vendor names: "We normalise going forward ... I am not
#: suggesting rewriting history."
#:
#: AND THE ALTERNATIVE WAS TRIED BEFORE BEING REJECTED, which is why the figure
#: above exists. A cleaner driven off the linter's own findings was built and
#: DRY-RUN over all 20 notes. It cannot touch quoted material by construction --
#: matches come from text with double-quoted spans already removed, and verbatim
#: regions are never counted -- but the substitutions it proposed included
#: several that damage ordinary English, because a bare number word before a
#: noun is sometimes a count and sometimes idiom, and no whitelist enumerates
#: every idiom. Mass-applying 165 of those unread would trade a reporting gap
#: for a prose defect across delivered notes.
#:
#: THIS IS VISIBLE RATHER THAN QUIET, and he can move it in 1 edit. The 165 are
#: recorded here so the choice is auditable; if he wants the gap cleaned, the
#: cleaner exists and the figure is known.
RULE_27_FULL_FROM = "2026-10-29"

#: ─────────────────────────── v1.9, 2026-11-01 ───────────────────────────
#:
#: HIS INSTRUCTION, verbatim: *"We already discussed that you should not simply
#: print issue IDs like B21, B20 etc. without offering any clear explanation of
#: what they are? These identifiers are meaningless to me? I don't carry a store
#: of what these issues are in my head, and I can't easily look them up. But you
#: do. ... If your v1.8 notes standard need formally updating to reflect this
#: previously agreed notes standard, then you should do it, and perhaps make a
#: version bump to 1.9, so there is no future confusion, and no temptation to
#: again revert."*
#:
#: IT WAS ALREADY AGREED AND ALREADY WRITTEN DOWN, WHICH IS THE POINT. The format
#: he endorsed on 2026-10-30 -- *"this format of tts is easier for me to deal
#: with. Please lean and use it going forward"* -- already states *"Never an
#: identifier without its subject named in the same breath."* v1.9 does not
#: invent a rule; it gives that one a CHECKER, because a rule restated for the
#: 3rd time and enforced by nothing is the thing this project's record says
#: fails.
RULE_32_FROM = "2026-11-01"

#: THE SUBJECT DICTIONARY IS THE TASK LIST'S OWN HEADINGS, not a word list of
#: mine. An identifier's subject is what its entry calls itself, so the check
#: cannot be satisfied by waffle: "Entry B21 carries a ruling of yours dated 17
#: October" has prose and names no subject, and that is the exact sentence he
#: objected to.
_ENTRY_IDENT = re.compile(r"\b((?:[A-Z]\d{1,4}|C00\d{2}|\d{1,2}\.\d{1,2}[a-z]?))\b")

_SUBJ_STOP = frozenset("""the a an and or but if then of for to in on at by with
from that this those these is are was were be been being it its their his her
not no cannot may must should would could will can has have had do does did as
into than when where which who whom what why how all any both each few more
most other some such only own same so too very just now also still yet about
above after again against because before below between during further here once
through under over while without within across among toward upon needs need
asks ask rule ruling decision entry task list project""".split())


def _subject_words(s: str) -> set[str]:
    """Content words of a heading or a sentence, for subject matching."""
    return {w for w in re.findall(r"[A-Za-z][A-Za-z_-]{4,}", s.lower())
            if w not in _SUBJ_STOP}


_ENTRY_SUBJECTS: dict[str, frozenset[str]] | None = None


def entry_subjects() -> dict[str, frozenset[str]]:
    """{identifier: content words of its own task-list heading}, read once."""
    global _ENTRY_SUBJECTS
    if _ENTRY_SUBJECTS is not None:
        return _ENTRY_SUBJECTS
    out: dict[str, frozenset[str]] = {}
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import task_list_markers as _TLM            # noqa: PLC0415
        for e in _TLM.parse_entries():
            #: THE TITLE, NOT THE BODY. `Entry.text` is the heading LINE, and
            #: several entries have had paragraphs APPENDED to that same line on
            #: purpose, because `parse_entries` requires the marker to sit at
            #: `lines[i + 1]` and inserting a paragraph between them would
            #: orphan the marker. So `e.text` can run to thousands of
            #: characters of history, and taking all of it made B21's subject
            #: set include "added", "absent" and "accepted" -- words that
            #: appear near any identifier, so the rule would have passed on
            #: anything. The subject is the entry's TITLE: the first sentence,
            #: after the leading identifier.
            title = re.sub(r"^\**\s*[A-Z]?\d*[\w.]*\.\s*", "", e.text.lstrip("*").strip())
            title = re.split(r"(?<=[a-z0-9])\.\s|\.\*\*", title)[0][:220]
            words = frozenset(_subject_words(title))
            if words:
                out[e.ident] = words
    except Exception:                                # noqa: BLE001
        #: FAILS OPEN. If the task list cannot be read the rule reports nothing
        #: rather than accusing every identifier in the document, because a
        #: checker that fires hardest when its own input is missing is the
        #: false-zero shape this project has met repeatedly.
        out = {}
    _ENTRY_SUBJECTS = out
    return out


#: WHICH DOCUMENTS, and the scope is HIS: *"scoped to the documents you read and
#: binding going forward only"*.
#:
#: MEASURED BEFORE SHIPPING, which is what kept the rule narrow. Unscoped, it
#: fires on 412 of 1,187 notes for 2,328 findings, the worst offenders being the
#: master task list itself at 119 -- where the rule is CIRCULAR, since that file
#: IS the dictionary -- and verbatim panel transcripts at 49, 45, 44 and 40,
#: which may not be edited at all. That is the guard-accuses-correct-material
#: class measured at 9 of 36 on 2026-10-28, and it is avoided here by scope
#: rather than discovered later by a red board.
_DELIVERED = re.compile(r"^(Morning_Report|Decisions_|Answers_|Board_"
                        r"|Progress_Report|Outstanding_Rulings|Overnight_)")


def _is_delivered_doc(path: pathlib.Path) -> bool:
    logical = pathlib.Path(_LOGICAL_PATH or path)
    name = logical.name
    if "FULL_RECORD" in name or name.startswith("CDSFL_MASTER_TASK_LIST"):
        return False
    if any(q.endswith("_tts") for q in logical.parts):
        return True
    return bool(_DELIVERED.match(name))


def rule_32_applies(path: pathlib.Path) -> bool:
    """Rule 32 binds a DELIVERED document first seen from his ruling onward."""
    if not _is_delivered_doc(path):
        return False
    seen = note_first_seen(pathlib.Path(_LOGICAL_PATH or path))
    return seen is None or seen >= RULE_32_FROM


#: RULE 33 -- A DECISION CARRIES A RECOMMENDATION, AND IT NAMES A STANDARD.
#: The file he rejected on 2026-10-29 carried 0 recommendations across 6 open
#: decisions and used the words additive, composability and simplest sufficient
#: 0 times. Both halves are counted rather than hoped for.
#: ★ THE SECTION, NOT THE TITLE — corrected 2026-11-01, and the defect was in
#: this rule's FIRST USE on the first file it judged. The pattern listed
#: `DECISIONS AWAITING YOU`, which is the TITLE of the decisions file, so the
#: search anchored on line 1, the next `PART` heading closed the window 2 lines
#: later, and the scan found 0 numbered items. `if items and recs < items` is
#: then False and the rule PASSED — reporting 0 findings while measuring
#: nothing. A rule built to stop vacuous decision reporting was itself vacuous.
#:
#: SO THE ANCHOR IS THE LAST MATCH, NOT THE FIRST, and a title-only phrase is
#: excluded: a document may legitimately name itself after its subject, and the
#: section that holds the decisions is the one to scan. The same "last mention,
#: not first" correction the note-standard stamp rule already carries, for the
#: same reason.
_DECISION_SECTION = re.compile(
    r"^(?:#+\s*)?(?:PART\s+\d+[.:]\s*)?(?:\*\*)?\s*"
    r"(?:WHAT NEEDS YOUR VERDICT|DECISIONS? THAT NEED|WHAT I NEED FROM YOU"
    r"|THE DECISIONS? THAT (?:ARE|IS) STILL YOURS|DECISIONS? STILL YOURS)",
    re.I | re.M)

#: A NUMBERED DECISION, in either form a report actually uses: a bare `3.` or a
#: labelled `DECISION 3.`. The first version knew only the bare form, so the
#: file written under this very standard scored 0 items.
_NUMBERED_ITEM = re.compile(
    r"^\s*(?:#+\s*)?(?:\*\*)?(?:DECISION\s+)?(\d{1,2})\.(?:\*\*)?\s+\S",
    re.I | re.M)
#: ★ THE FORMS A REPORT ACTUALLY USES — widened 2026-11-01. The first version
#: knew only `my recommendation`, `I recommend` and `RECOMMENDATION:`, and the
#: decisions file written under this very standard labels each one
#: `Recommendation, and why.` So the rule found 4 decisions, 0 recommendations
#: and would have accused a compliant file. That is the
#: guard-accusing-correct-material class, caught here by driving the rule over
#: the first real document rather than over a fixture.
_RECOMMENDS = re.compile(
    r"my recommendation|I recommend|^\s*(?:\*\*)?recommendation\b"
    r"|recommendation,? and why|recommendation is\b|is my recommendation",
    re.I | re.M)
_THE_3_STANDARDS = re.compile(r"additive|composab|simplest sufficient", re.I)


def note_first_seen(path: pathlib.Path) -> str | None:
    """The date a note ENTERED the repository, or None when it cannot be dated.

    GIT, NOT THE MTIME, and the difference decides cases. An mtime moves every
    time a file is touched, so a 2026-09 note edited tonight would be held to a
    rule written after it -- which is exactly the retrospection his ruling
    refuses. The first-commit date does not move.

    FAILS OPEN, deliberately. An undatable file -- not yet committed, or no git
    -- returns None and is treated as NEW, because a note being written right
    now is the one case the rule is certainly meant to cover.
    """
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%aI", "--", str(path)],
            cwd=str(pathlib.Path(__file__).resolve().parents[1]),
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    stamps = [x for x in r.stdout.split() if x]
    if stamps:
        return stamps[-1][:10]
    # ★ THE FILENAME DATE IS EVIDENCE, AND IT IS CONSULTED BEFORE FAILING OPEN.
    # "Uncommitted means new" was too crude: it held 3 generated morning reports
    # dated 2026-10-16, 2026-10-19 and 2026-10-28 to a rule that began on
    # 2026-10-29, purely because they had never been committed. This project
    # names its notes with their date, so that date is a better witness to when
    # a note was WRITTEN than the absence of a git record is. Only a file with
    # neither a git date nor a dated name falls open as new.
    m = re.search(r"(20\d\d)-(\d\d)-(\d\d)", path.name)
    if m:
        return m.group(0)
    return None


def rule_27_in_full(path: pathlib.Path) -> bool:
    """Is this note held to Rule 27 in full? His ruling: going forward only."""
    seen = note_first_seen(path)
    return seen is None or seen >= RULE_27_FULL_FROM

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

#: ★ A BARE CLOCK TIME IN THE HEADER, WITH NO DATE BESIDE IT, added 2026-10-30.
#:
#: WHY. `STAMP_LINE` requires a date AND a time, so a header reading
#: "Written overnight, finished at 01:45 GMT" matched nothing and the
#: future-stamp check never ran. MEASURED: a note written at 01:18 claimed
#: 01:45, 27 minutes ahead, and this linter passed it -- 2 hours after the same
#: author had recorded a commit carrying a stamp 2.1 minutes ahead as a defect.
#: The rule existed, the checker existed, and the checker had a blind spot in the
#: shape the author actually writes.
#:
#: SCOPED TO THE FIRST 3 LINES, deliberately. A bare time anywhere in a note is
#: usually a measurement being reported or a source being quoted -- "the run
#: finished at 23:43 GMT" is a fact about the run, not a claim about the note.
#: Only the HEADER makes a claim about when the note itself was written, which is
#: what Rule 1 governs, so only the header is read. A wider scan would accuse
#: every note that mentions a time.
_BARE_CLOCK_IN_HEADER = re.compile(r"\b(\d{1,2}):(\d{2})\s*(?:GMT|BST|UTC)\b")

#: A PROSE DATE IN THE HEADER, e.g. "15 April 2026" or "2 November 2026", which
#: is the form every note in this project actually writes. `STAMP_LINE` wants an
#: ISO date at the START of a line and only 145 of 639 notes satisfy it, so the
#: bare-clock branch is the one that runs in practice and it needs a date.
_PROSE_DATE_IN_HEADER = re.compile(
    r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{4})\b")


def future_stamp(path: pathlib.Path):
    """Return (claimed, actual) when the note's own stamp is ahead of its mtime."""
    import datetime as _dt
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        mtime = _dt.datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return None
    m = STAMP_LINE.search(text[:800])
    if m:
        try:
            claimed = _dt.datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}",
                                            "%Y-%m-%d %H:%M")
        except ValueError:
            return None
    else:
        #: FALL BACK TO A BARE CLOCK TIME IN THE HEADER, dated from the file's own
        #: mtime, because a header time with no date still claims when the note was
        #: written and was previously invisible to this check. Only the first 3
        #: lines are read, for the reason given at `_BARE_CLOCK_IN_HEADER`.
        header = "\n".join(text.splitlines()[:3])
        b = _BARE_CLOCK_IN_HEADER.search(header)
        if not b:
            return None
        #: ★ PREFER A PROSE DATE IN THE SAME HEADER OVER THE FILE'S MTIME,
        #: added 2026-11-03. The bare-clock branch dated the time from mtime,
        #: which is right only while a note is never touched again. Edit a note
        #: on a later day and the rule reports it as claiming a time it never
        #: claimed: `Divergence_Directive_Implementation_2026-04-15.md` says
        #: "15 April 2026, 22:40" and was accused of claiming 2026-07-28 22:40,
        #: because its mtime is 28 July. MEASURED over the 639 notes in
        #: experimental_notes/: the rule accuses 53, and 16 of those 53 carry a
        #: prose date in the very same header that exonerates them --
        #: 0.301887, Wilson 95% [0.195183, 0.435368]. Producer:
        #: scripts/a_bare_clock_was_dated_from_the_mtime_2026-11-03.py.
        #:
        #: IT DOES NOT WEAKEN THE RULE. The prose date REPLACES mtime's date in
        #: the claim, and the comparison against mtime is unchanged, so a note
        #: whose header genuinely claims a future day is still accused -- more
        #: accurately than before, because the accusation now quotes the day the
        #: note actually names. This is why the fix is additive: it reads a
        #: field the rule already had in front of it and ignored.
        _pd = _PROSE_DATE_IN_HEADER.search(header)
        _base = mtime
        if _pd:
            try:
                _base = _dt.datetime.strptime(
                    f"{int(_pd.group(1))} {_pd.group(2)} {_pd.group(3)}",
                    "%d %B %Y")
            except ValueError:
                _base = mtime
        try:
            claimed = _base.replace(hour=int(b.group(1)), minute=int(b.group(2)),
                                    second=0, microsecond=0)
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
def decisions_without_recommendations(path, text: str) -> list:
    """Rule 33: a delivered document presenting decisions must recommend on each.

    THE FILE HE REJECTED on 2026-10-29 carried **0** recommendations across 6
    open decisions, and used the words additive, composability and simplest
    sufficient **0** times. Both halves are counted here rather than hoped for,
    because the format he endorsed the next day requires every decision to carry
    "a recommendation argued against the 3 standards".
    """
    if not rule_32_applies(pathlib.Path(_LOGICAL_PATH or path)):
        return []
    hits = list(_DECISION_SECTION.finditer(text))
    if not hits:
        return []
    m = hits[-1]                 # the section, not an earlier mention of it
    section = text[m.end():]
    nxt = re.search(r"^(?:#+\s*)?(?:PART\s+\d+)[.:]", section, re.M)
    if nxt:
        section = section[:nxt.start()]
    items = len(set(_NUMBERED_ITEM.findall(section)))
    recs = len(_RECOMMENDS.findall(section))
    out = []
    if items and recs < items:
        out.append((0, f"DECISIONS WITHOUT RECOMMENDATIONS (Rule 33: {items} "
                    f"numbered decision(s), {recs} recommendation(s))",
                    "recommendation",
                    "the format he endorsed 2026-10-30 gives every decision what "
                    "it is, what it affects, what he decides, and a recommendation "
                    "argued against the 3 standards"))
    if items and not _THE_3_STANDARDS.search(section):
        out.append((0, "RECOMMENDATIONS NAME NO PROJECT STANDARD (Rule 33)",
                    "standards",
                    "name additive, simplest sufficient or composability where a "
                    "recommendation is made; the rejected file of 2026-10-29 used "
                    "all 3 words 0 times"))
    return out


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
    #: RULE 33 (v1.9) IS WHOLE-DOCUMENT, so it is added after the split and is
    #: region-immune: a document that presents decisions without recommending on
    #: them is a fault of the document, not of a quoted passage inside it.
    for r33 in decisions_without_recommendations(path, text):
        counted.insert(0, r33)

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
CURRENT_NOTE_STANDARD = "v1.9"

#: Standards this project has genuinely used. A note stamped with one of these
#: is correctly stamped, whatever the current standard is. Bumped WHEN a standard
#: is superseded, never when one is invented.
ARCHIVAL_NOTE_STANDARDS = frozenset({
    # SUPERSEDED BY v1.9 ON 2026-11-01, on his instruction that the format he
    # endorsed on 2026-10-30 be written into the standard so it cannot be
    # abandoned again. Moving v1.8 here is what keeps every note correctly
    # stamped v1.8 compliant rather than retrospectively wrong.
    "v1.8",
    "v1", "v1.0", "v1.1", "v1.2", "v1.3", "v1.4", "v1.5", "v1.6",
    # SUPERSEDED BY v1.8 ON 2026-10-17, which adds Rule 31 (name the subject,
    # name the quantity) on his instruction of 2026-10-04 that the standard
    # itself needed tweaking to cover vagueness by OMISSION. 191 notes carry
    # the v1.7 stamp and every one of them is correctly stamped; moving it here
    # is what keeps that true rather than making them retrospectively wrong.
    "v1.7",
})

#: Set by `--as` when the bytes being linted live somewhere other than the path
#: they represent. Only the PATH-SENSITIVE rules consult it; every content rule
#: reads the bytes it was given either way.
_LOGICAL_PATH: str = ""
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
    #: THE LOGICAL PATH, when the bytes are being read from somewhere else.
    #:
    #: THE DEFECT THIS CLOSES, measured 2026-10-17. The pre-commit ratchet copies
    #: the staged and HEAD versions of each note into a `mktemp -d` directory and
    #: lints THOSE paths. A temporary path contains neither `experimental_notes`
    #: nor a `*_tts` folder, so this rule returned [] for both sides of every
    #: comparison -- it never participated in the ratchet at all, and a note
    #: could lose its standard stamp with nothing to say so.
    #:
    #: His ruling of 2026-10-17 was "We fix going forward and leave the archive
    #: alone", so the archive is not rewritten. What changes is that from now on
    #: the rule is REACHED, and because both sides of the ratchet are linted with
    #: the same declared path, a commit still cannot make a note worse.
    logical = pathlib.Path(_LOGICAL_PATH or path)
    parts = {q.lower() for q in logical.parts}
    is_note = ("experimental_notes" in parts
               or any(q.endswith("_tts") for q in parts))
    if not is_note or logical.suffix.lower() not in (".md", ".txt"):
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

    #: THE STAMP BELONGS AT THE FOOT, NOT THE HEAD -- HIS OBJECTION, 2026-10-24.
    #:
    #: His words (annotation 4 of `Why_sv_Was_Blocked_And_Twelve_Lost_Annotations_2026-10-19.txt`):
    #: *"You also break with convention by listing the note standard at the head
    #: of this tts file, rather than at the end? If there is a valid reason for
    #: either of these, please discuss them with me."* There is no valid reason.
    #: It was an error, and the project's own vocabulary already called the
    #: convention the FOOT-LINE convention in
    #: `scripts/the_note_lint_ratchet_is_blind_to_the_stamp_2026-10-15.py`.
    #:
    #: MEASURED BEFORE THE THRESHOLD WAS CHOSEN, 2026-10-25, over every stamped
    #: note under `experimental_notes/` and every `*_tts/` folder: 582 carry a
    #: stamp, of which **559 (0.9605) place it in the final 10% of non-blank
    #: lines**, 13 in the middle, 1 in the first 10%, and 9 in the first 3 lines.
    #: So the foot is the overwhelming convention and this rule costs 23 findings
    #: across 582 files rather than the 357 of 536 that an earlier unmeasured rule
    #: produced -- the noise this module's own docstring warns gets a rule
    #: switched off. 2 of the 9 head-stamped files are the 2 he complained about.
    #:
    #: GOING FORWARD ONLY, per his ruling of 2026-10-17: *"We fix going forward
    #: and leave the archive alone"*. This reports; it does not rewrite anything.
    lines = text.splitlines()
    nonblank = [i for i, ln in enumerate(lines) if ln.strip()]
    #: THE LAST MENTION, NOT THE FIRST. A note may legitimately DISCUSS the
    #: standard in its prose -- the 2026-10-25 RECOVERY block does exactly that,
    #: and taking the first match reported its own stamp as misplaced at 52.94%
    #: when the real stamp sat correctly at the foot. By convention the stamp IS
    #: the last such mention, so that is what the placement check reads.
    stamp_ranks = [r for r, i in enumerate(nonblank)
                   if NOTE_STANDARD_STAMP.search(lines[i])]
    stamp_rank = stamp_ranks[-1] if stamp_ranks else None
    out = []
    if stamp_rank is not None and len(nonblank) >= 10:
        frac = stamp_rank / max(1, len(nonblank) - 1)
        if frac < 0.90:
            where = ("at the HEAD" if stamp_rank < 3 else
                     f"{frac:.2%} of the way through")
            out.append((lines[nonblank[stamp_rank]] and nonblank[stamp_rank] + 1,
                        f"NOTE STANDARD STAMP IS {where}, NOT AT THE FOOT",
                        "note standard placement",
                        "his objection of 2026-10-24: \"You also break with "
                        "convention by listing the note standard at the head of "
                        "this tts file, rather than at the end?\" Measured "
                        "2026-10-25: 559 of 582 stamped notes (0.9605) place it "
                        "in the final 10% of non-blank lines. Move it to the end."))

    if found == CURRENT_NOTE_STANDARD:
        return out
    #: A STAMP NAMING A REAL EARLIER STANDARD IS COMPLIANT, NOT A DEFECT.
    #:
    #: His instruction of 2026-10-11 asks for TRACEABILITY, not uniformity: the
    #: stamp exists because "it helps me to track which notes standards you are
    #: using across files". A note written in April under v1.3 and stamped v1.3
    #: does exactly that. Rewriting it to say v1.7 would make the record WORSE
    #: and is the retroactive editing he refused on 2026-10-17: "Going back and
    #: rewriting the archive, as I have said before could potentially be seen as
    #: dishonest, and as an attempt to rewrite history."
    #:
    #: MEASURED 2026-10-17, when `--as` first let this rule reach the archive:
    #: 357 of 536 notes produced a finding, 66.6045%, Wilson [62.5061%,
    #: 70.4665%] -- of which 161 were WRONG VERSION on correctly-stamped archive
    #: notes. Reporting those is the noise this module's own docstring warns
    #: gets a rule switched off, and it would have buried the 196 that are a
    #: real absence.
    if found in ARCHIVAL_NOTE_STANDARDS:
        return out
    return out + [(0, f"NOTE STANDARD STAMP IS {found}, WHICH IS NOT A STANDARD THIS "
                f"PROJECT HAS USED (current {CURRENT_NOTE_STANDARD})",
             "note standard",
             "a stamp must name a real standard. An earlier one is fine and is "
             "how he tracks which standard produced which file; an invented one "
             "tells him nothing.")]


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


#: ── RULE 30 WAS OUTSIDE THE VERBATIM EXEMPTION, AND THAT DEFEATED ITS PURPOSE ──
#:
#: MEASURED 2026-10-18 on `Panel_FULL_RECORD_Severity_Ruler_Coarseness_2026-10-18.md`,
#: a record carrying 2 seats' replies in full: `lint()` found 4 findings and
#: `partition()` exempted all 4, while `undefined_project_terms()` separately
#: found 6 -- every one of them inside a seat's own reply -- and `main()` appends
#: those AFTER the split, so they never reach the exemption. The commit ratchet
#: then refused the record for the seats' vocabulary.
#:
#: That is the exact failure the exemption exists to prevent, recorded in its own
#: comment for 2026-09-10: *"the record could not be committed without editing
#: what the models actually said. Editing it would falsify the record, which is
#: worse than any vagueness in it."* And task V8 exists so a seat's words reach
#: the record unedited.
#:
#: WHY THE TEST IS ON TEXT AND NOT ON A PARAGRAPH NUMBER. The 2 splitters
#: DISAGREE about numbering -- on that file `paragraphs()` yields 119 and
#: `verbatim_paragraphs()` 99 -- so filtering Rule 30 by the `marked` set would
#: exempt the wrong paragraphs. Containment in the region's own text is
#: numbering-independent and cannot drift.
def verbatim_spans(text: str) -> list:
    """Character ranges covered by `verbatim-begin` / `verbatim-end` markers."""
    spans, open_at = [], None
    for m in _re.finditer(r"<!--\s*verbatim-(begin|end)\b[^>]*-->", text):
        if m.group(1) == "begin":
            if open_at is None:
                open_at = m.end()
        else:
            if open_at is not None:
                spans.append((open_at, m.start()))
                open_at = None
    if open_at is not None:                     # unclosed region runs to the end
        spans.append((open_at, len(text)))
    return spans


def _collapse_ws(s: str) -> tuple:
    """(collapsed, index_map) with every whitespace run reduced to 1 space.

    `index_map[j]` is the RAW index of the character that produced
    `collapsed[j]`, so a hit found in collapsed space can be tested against
    spans measured in raw space.
    """
    out, idx, prev_space = [], [], False
    for i, ch in enumerate(s):
        if ch.isspace():
            if not prev_space:
                out.append(" ")
                idx.append(i)
            prev_space = True
        else:
            out.append(ch)
            idx.append(i)
            prev_space = False
    return "".join(out), idx


def inside_verbatim(text: str, fragment: str) -> bool:
    """True when `fragment` sits wholly inside a verbatim region.

    WHY THE SECOND PASS EXISTS, measured 2026-10-18. The raw `str.find` below
    is exact and fast, and it FAILS SILENTLY on any paragraph the splitter
    joined across lines -- a markdown table or a list inside a seat's reply
    becomes one line of `| a | b |` joins that exists nowhere in the file, so
    `find` returns -1 and the paragraph is counted as if it were outside the
    region. The commit ratchet then refuses the record, and the only way to
    make it pass would be to EDIT WHAT A SEAT WROTE, which is exactly what the
    exemption exists to prevent. Found on
    `Panel_FULL_RECORD_Joint_Severity_Ruler_2026-10-18.md`, where all 4
    occurrences of the flagged term sat inside a verbatim region and the
    finding was still counted. The fallback collapses whitespace on BOTH sides
    and maps the hit back to raw coordinates, so the span test is unchanged.
    """
    frag = (fragment or "").strip()
    if not frag:
        return False
    spans = verbatim_spans(text)
    if not spans:
        return False
    probe = frag[:160]
    start = 0
    while True:
        i = text.find(probe, start)
        if i < 0:
            break
        if any(a <= i and i + len(probe) <= b for a, b in spans):
            return True
        start = i + 1

    # Second pass: whitespace-insensitive, for splitter-joined paragraphs.
    ctext, cmap = _collapse_ws(text)
    cfrag, _ = _collapse_ws(probe)
    cfrag = cfrag.strip()
    if not cfrag:
        return False
    start = 0
    while True:
        j = ctext.find(cfrag, start)
        if j < 0:
            return False
        raw_lo = cmap[j]
        raw_hi = cmap[min(j + len(cfrag) - 1, len(cmap) - 1)] + 1
        if any(a <= raw_lo and raw_hi <= b for a, b in spans):
            return True
        start = j + 1


def split_reported_terms(path) -> tuple:
    """(counted, exempted) for Rule 30, honouring the verbatim exemption.

    ONE implementation, so the command line and `blocking()` cannot drift -- the
    defect this repairs was 2 paths disagreeing about the same file.
    """
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="ignore")
    counted, exempted = [], []
    for hit in undefined_project_terms(path):
        (exempted if inside_verbatim(text, hit[3]) else counted).append(hit)
    return counted, exempted


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


#: PHONETIC PUNCTUATION -- Rule 14a (v1.3), reached for the first time 2026-10-28.
#:
#: HIS FINDING, 2026-10-28, on a TTS file of mine that carried "python3 scripts
#: slash register.py minus minus kind wr minus minus status OPEN minus minus
#: limit 0": *"This is a weird new kind of 'word numbering'? Is it justified here
#: for some reason? If not you should probably look at it and fix it, as per our
#: 'no word numbers' rule."*
#:
#: HIS DIAGNOSIS NAMES THE WRONG RULE AND THE FINDING IS STILL CORRECT, which is
#: worth recording because the 2 rules want different fixes. Nothing there spells
#: a NUMBER, so `no-word-numbers` does not apply. What is spelled is PUNCTUATION,
#: which Rule 14a of v1.3 governs: *"identifiers keep their name, lose the
#: punctuation"*, alongside the standing TTS no-underscores rule. The file passed
#: at 0 findings precisely because no check here could see phonetic punctuation.
#:
#: MEASURED BEFORE BEING ADDED, because a rule that reddens the corpus on the day
#: it lands gets switched off: 802 occurrences across 86 of 1,392 scanned files,
#: 0.061782 Wilson [0.050300, 0.075675]. So this is a long habit, not a one-off.
#: `minus minus` is the exception and is genuinely new -- 3 occurrences in 1 file,
#: the one he was reading. The commit ratchet is PER FILE, so the 86 are
#: grandfathered until something edits them, exactly as the 23 findings in the
#: master task list are.
#:
#: TTS ONLY. A markdown companion writes a path literally and must keep doing so,
#: so firing there would be a false positive on correct work. Scoped by the same
#: logical-path test `missing_standard_stamp` uses, so `--as` keeps working and
#: both sides of the ratchet are judged alike.
PHONETIC_PUNCT = {
    "a spoken path separator": re.compile(r"\b[\w.]+ slash [\w.]+"),
    "a spoken double dash": re.compile(r"\bminus minus\b"),
    "a spoken file extension": re.compile(
        r"\b\w+ dot (?:py|md|json|txt|sh|toml|ini|yml|yaml)\b"),
    "a spoken underscore": re.compile(r"\b\w+ underscore \w+"),
}


def _is_tts(path) -> bool:
    """True for a delivered TTS file, by the same test the stamp rule applies."""
    logical = pathlib.Path(_LOGICAL_PATH or path)
    parts = {q.lower() for q in logical.parts}
    if logical.suffix.lower() != ".txt":
        return False
    return ("experimental_notes" in parts
            or any(q.endswith("_tts") for q in parts))


def lint(path: pathlib.Path) -> list:
    out = []
    _tts = _is_tts(path)
    # ★ RULE 27 IN FULL ONLY FOR NOTES DATED FROM HIS RULING. Entry B24, his
    # verdict of 2026-10-19: "Enforce going forward only."
    #
    # THE LOGICAL PATH, NOT THE PATH ON DISK, and the difference is a real
    # defect caught by FOLLOW rather than by reading. `hooks/pre-commit` lints a
    # STAGED COPY at a temporary location and passes `--as` to name the real
    # file -- which is why `_LOGICAL_PATH` exists and why 2 other rules already
    # read it. Dating the temp copy instead would ask git about a file that has
    # no history, fall back to the temp name, and hold an ARCHIVED note to a
    # rule he confined to new ones the moment that name carried no date. 2
    # declarations of one fact must not disagree, so this reads the same
    # `_LOGICAL_PATH or path` the rest of the module does.
    _full_27 = rule_27_in_full(pathlib.Path(_LOGICAL_PATH or path))
    #: RULE 32 (v1.9) binds only a DELIVERED document first seen from his ruling
    #: onward, and it is evaluated INSIDE this loop so that `partition()` can
    #: exempt a finding sitting in a verbatim region. His words and a seat's
    #: words reach these files unedited; accusing them would be the one thing
    #: task V8 exists to prevent.
    _full_32 = rule_32_applies(pathlib.Path(_LOGICAL_PATH or path))
    _subjects = entry_subjects() if _full_32 else {}
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
        elif _full_27:
            # THE BARE FORM, checked only when the compound form did not already
            # fire, so one sentence yields one finding rather than two. The
            # whitelist is consulted on a WINDOW around the match, not on the
            # match alone, because every idiom that forgives a bare number word
            # is a phrase: "no one", "at one", "one of the". Matching the word
            # in isolation could never see them.
            bm = BARE_WORD_NUMBER.search(unquoted)
            if bm:
                lo_i = max(0, bm.start() - 18)
                window = unquoted[lo_i:bm.end() + 18]
                #: The pronominal window is WIDER on purpose: an article plus up
                #: to 2 modifiers can sit further back than 18 characters, as in
                #: "the only measured one", which needs 21.
                wide = unquoted[max(0, bm.start() - 40):bm.end() + 18]
                if not (BARE_WORD_NUMBER_OK.search(window)
                        or _PRONOUN_ONE_WITH_MODIFIER.search(wide)):
                    out.append((para_no,
                                "SPELLED NUMBER (Rule 27 in full: use digits)",
                                bm.group(0), s))
        for phrase, name in CATEGORY_NOUN.items():
            if CATEGORY_NOUN_RE[phrase].search(low):
                out.append((para_no, f"CATEGORY NOUN (Rule 28: say {name!r})",
                            phrase, s)); break
        if _full_32:
            #: THE ASYMMETRY IS DELIBERATE. The IDENTIFIER is searched in the
            #: quote-stripped sentence, so quoting his words or a seat's reply
            #: is never accused; the SUBJECT is searched in the FULL sentence,
            #: because naming the subject inside a quotation still names it.
            for im in _ENTRY_IDENT.finditer(unquoted):
                subj = _subjects.get(im.group(1))
                if subj and not (subj & _subject_words(s)):
                    out.append((
                        para_no,
                        "BARE ENTRY CODE (Rule 32: name its subject in the "
                        "same breath)", im.group(1),
                        s))
                    break
        if _tts:
            for what, rx in PHONETIC_PUNCT.items():
                m = rx.search(unquoted)
                if m:
                    out.append((
                        para_no,
                        "PHONETIC PUNCTUATION (Rule 14a: identifiers keep "
                        f"their name, lose the punctuation -- {what})",
                        m.group(0), s))
                    break
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
        print("\n  usage: note_vagueness_lint.py [--as LOGICAL_PATH] <file> [file ...]")
        print("    --as declares the path the bytes REPRESENT, for the")
        print("        path-sensitive rules, when linting a copy.")
        return 0
    # `--as <path>` declares the LOGICAL path of the bytes being linted, for the
    # path-sensitive rules only. The pre-commit ratchet lints temporary copies of
    # the staged and HEAD versions, and a temporary path is under neither
    # `experimental_notes/` nor a `*_tts/` folder, so the standard-stamp rule
    # silently returned nothing for BOTH sides of every comparison and never
    # participated in the ratchet at all. Measured 2026-10-17.
    global _LOGICAL_PATH
    argv = list(sys.argv[1:])
    if "--as" in argv:
        i = argv.index("--as")
        if i + 1 >= len(argv):
            print("  --as needs a path"); return 1
        _LOGICAL_PATH = argv[i + 1]
        del argv[i:i + 2]
    paths = [pathlib.Path(a) for a in argv]
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
        _terms_counted, _terms_exempt = split_reported_terms(p)
        counted = counted + missing_standard_stamp(p) + _terms_counted
        exempted = list(exempted) + _terms_exempt
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
