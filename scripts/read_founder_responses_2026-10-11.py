#!/usr/bin/env python3
"""Read the founder's annotated TTS responses. Format-aware, because a naive reader is BLIND.

HIS FOLDER, named by him 2026-10-11: `/Users/georgejackson/Developer_Projects/Responses`.
*"This is the folder I use to keep all my tts responses in, so my original tts folder remains
uncluttered/readable. You should probably mark it as one of your available resources."*

WHY THIS SCRIPT EXISTS, AND WHAT IT COST TO LEARN. On 2026-10-11 an assistant reported that the
founder's verdicts of 2026-10-08 were LOST. They were not. `grep -E "^#"` returned nothing on
`Division_Count_And_Relegation_Panel_2026-10-08.txt` and that silence was read as absence. The
file is `ISO-8859 text, with CR line terminators`: Word writes plain text with Mac-classic `\\r`
endings and his smart quotes as high bytes, so `grep` sees ONE 3,790-character line, decides the
file is BINARY, and exits 1 saying nothing. Python's `splitlines()` splits on `\\r`, so it found
all 9 annotations immediately. The byte count had said so all along -- 21,698 against the
unannotated original's 11,370.

THE BLAST RADIUS WAS NOT ONE FILE. Measured across the folder on 2026-10-11: 14 of 76 files
carry CR-only line endings and 15 of 76 are not valid UTF-8, and **15 of 40 ANNOTATED FILES --
0.3750, Wilson [0.2422, 0.5297] -- are invisible to a naive grep**, carrying 221 of his
responses, 219 of them dated between 2026-09-30 and 2026-10-09. That is the exact window of the
inventory he had commissioned, so the inventory was built from the assistant's own documents
while a third of his verdicts sat unread.

HIS FORMAT CHANGE IS THE PROXIMATE CAUSE AND IT IS NOT HIS FAULT. He moved from `.rtf` to `.txt`
believing plain text would parse more easily. Measured: a raw grep misses 3 of 19 annotated
`.rtf` files (0.1579) against 12 of 14 `.txt` (0.8571); Fisher odds ratio 0.031250 at
p = 9.108e-05, Barnard p = 4.727e-05, statsmodels odds-ratio interval [0.004493, 0.217339]. The
switch dates to the end of September: `.rtf` median 2026-08-27 against `.txt` median 2026-10-02,
Mann-Whitney U = 75.0 at p = 5.044e-08 and a permutation test on the median gap of 36 days at
p = 5.000e-05. **But `.txt` is not the defect** -- Word's plain-text encoding is. `.rtf` survives
only by accident, being a 7-bit container that escapes high bytes. The fix therefore belongs
here, in the reader, and he changes nothing.

Run:  python3 scripts/read_founder_responses_2026-10-11.py
      python3 scripts/read_founder_responses_2026-10-11.py --since 2026-09-29
      python3 scripts/read_founder_responses_2026-10-11.py --json
      python3 scripts/read_founder_responses_2026-10-11.py --verify
          exit 3 if ANY file looks annotated in its raw bytes but reads as unannotated.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import math
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

RESPONSES = Path("/Users/georgejackson/Developer_Projects/Responses")
Z = 1.959963984540054

#: Extensions this reader understands. Anything else is REPORTED as unreadable rather than
#: silently skipped, because silent skipping is the whole defect being fixed.
TEXTISH = {".txt", ".md", ".markdown", ".csv", ".log"}
RICH = {".rtf", ".doc"}
ZIPPED = {".docx"}


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


#: FILES IN THAT FOLDER THAT ARE NOT HIS ANNOTATED RESPONSES, named one by one
#: with the evidence, because every shape-based discriminator tried for this was
#: MEASURED AND REFUTED on 2026-10-17:
#:
#:   * a dated-filename filter would drop 8 of 598 annotations, 1.3378%,
#:     Wilson [0.6794%, 2.6174%];
#:   * a markdown-structure test (fences, '##' heading density) marks
#:     FINAL_REPORT_FOR_OPUS_2026-08-27.md, which carries a real verdict, and
#:     does NOT mark design_brief.txt, which carries none;
#:   * removing the `.md`-only gate on `_looks_like_a_markdown_heading` so it
#:     applies to `.txt` as well would drop 18 of 598, 3.0100%,
#:     Wilson [1.9123%, 4.7076%] -- 12 of them REAL verdicts of his, including
#:     "Verdict: y", "Go with option B" and "Go with option A". That is exactly
#:     the failure `no-ruling-is-dropped-for-being-short` exists to prevent.
#:
#: So the exclusion is EXPLICIT and PER FILE. It cannot lose a verdict by
#: accident, because nothing is excluded unless it is named here with a reason,
#: and `--verify` reports what was skipped rather than dropping it silently.
#: Measured by scripts/what_would_partitioning_the_register_buy_2026-10-17.py's
#: sibling check and recorded in experimental_notes/.
#:
#: WHY THE GATE FAILED IN THE FIRST PLACE. `_looks_like_a_markdown_heading` was
#: applied only to `.md` and `.markdown`, on the stated assumption that "he
#: annotates .txt, .rtf and .docx in Word". That assumption held until he began
#: dropping FOREIGN DOCUMENTS into the folder -- a Gemini design brief, a
#: YouTube auto-transcript, a pasted chat log -- whose own title lines open with
#: a hash. The filter was correct; the set of files it reached was not.
#: The extensions his annotated replies actually use. Measured 2026-10-20
#: over the whole folder: .txt 425, .rtf 256, .md 1, and 0 real annotations
#: in any other kind of file. A new extension is a deliberate addition here,
#: which is the point -- the old exclusion list admitted everything by default.
TEXT_SUFFIXES = {".txt", ".rtf", ".md"}

#: `Name_2026-10-13.txt` -> 2026-10-13. See `_file_date`.
_NAME_DATE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")


NOT_HIS_ANNOTATIONS = {
    #: Gemini Web's register design brief, attached by him 2026-10-17. Its 3
    #: '#' lines are the document's own title block: "DESIGN BRIEF: CHRONOS
    #: MEMORY SYSTEM (CMS)", "TARGET AGENT: ...", "SPECIFICATION VERSION: 2.0".
    "design_brief.txt": "a design brief from another model, not his annotation",
    #: A YouTube auto-transcript. Its 3 '#' lines are the transcript tool's
    #: header: "tactiq.io free youtube transcript", the video title, the URL.
    "tactiq-free-transcript-4S8I22ybG2c.txt":
        "an auto-generated transcript header, not his annotation",
    #: A pasted chat log. Its 2 '#' lines open "Me: Does DeepSeek API support
    #: tool calls?Gemini:..." -- a transcript of someone else's exchange.
    "DeepSeek Tool use.docx":
        "a pasted chat transcript, not his annotation",
}


def is_one_of_his_annotated_responses(path: Path) -> bool:
    """A response file he actually annotated, excluding foreign documents.

    SEPARATE FROM `is_a_response_file` DELIBERATELY. That predicate answers
    "can the reader read this file at all?" and the reader-gap check depends on
    it: narrowing it would make a file the reader cannot parse stop being
    reported as a gap, which is the opposite of what is wanted.

    ★ AND IT NOW REQUIRES A TEXT-BEARING EXTENSION, 2026-10-20. The name-based
    exclusion above admits every NEW kind of file by default. He added
    `CDSFL_UX_Mockup_Pack_Light_2026-10-20.zip` and **65 lines of compressed
    binary came back as his annotations**, with anchors like `...zip#10077`.
    Binary noise in the record of his words corrupts every count taken over it,
    and the verdict-coverage guard duly demanded rows for 65 annotations he
    never wrote.

    AN EXCLUSION LIST CANNOT HOLD: `.DS_Store` was excluded by name, then `~$`
    by prefix, and `.zip` would have been the third patch of the same shape.
    The ALLOW list is decidable. Measured over the folder on 2026-10-20, every
    real annotation lives in 3 extensions -- 425 in .txt, 256 in .rtf, 1 in .md,
    682 in all -- against 65 in the single .zip and 0 in any .docx.
    """
    return (is_a_response_file(path)
            and path.suffix.lower() in TEXT_SUFFIXES
            and path.name not in NOT_HIS_ANNOTATIONS)


def is_a_response_file(path: Path) -> bool:
    """One predicate, three call sites, so they cannot drift apart.

    EXCLUDES dotfiles. `Path.glob("*")` returns them where shell globbing does not, and
    `.DS_Store` contains a `#` byte, so it was reported as a reader gap on the first run --
    a false positive of exactly the `check the predicate before the result` shape. It also
    excludes Word's `~$` lock files, which carry no content.

    ★ THE TEXT-SUFFIX RULE WAS PUT HERE ON 2026-10-20 AND MOVED OUT THE SAME
    DAY, because this predicate's job is READABILITY and narrowing it hides a
    reader gap instead of fixing one. `bench/tests/test_a_foreign_document_is_
    not_his_annotation_2026-10-17.py` caught it: with the suffix rule here,
    `DeepSeek Tool use.docx` stopped being considered readable, so a genuine
    failure to parse it would no longer be reported. The rule belongs in
    `is_one_of_his_annotated_responses`, which answers a different question,
    and that is where it now lives.
    """
    return (path.is_file()
            and not path.name.startswith("~$")
            and not path.name.startswith("."))


#: `#`, 1 to 6 of them, then a space, then a short title-case-ish phrase and no sentence
#: punctuation. That is a heading. His annotations are conversational prose, usually long,
#: and frequently begin without a space after the hash.
_MD_HEADING = re.compile(r"^#{1,6}\s+\S")

#: Where this project's own generated TTS reports live. An annotated response
#: file is a COPY of one of these with his '#' insertions, so the original is an
#: EXACT oracle for which lines are the report's and which are his -- better
#: than any shape heuristic. Consulted when a same-named original exists.
_TTS_ORIGINALS = Path.home() / "Desktop" / "CDSFL_tts"

#: FALLBACK ONLY, for a response file whose original no longer exists: a line
#: opening with a run of capitals followed by a digit or a stop is how the
#: reports write their headings ("DECISION 2.", "SECTION 1."). Measured over his
#: 522 annotations, exactly 1 of HIS OWN lines opens with 4+ capitals -- 0.1916%,
#: Wilson 95% [0.0338%, 1.0771%] -- so it is nearly safe and not exactly safe,
#: which is why the oracle is preferred wherever it survives.
_REPORT_SHAPE = re.compile(r"^[A-Z]{4,}[\s0-9.]")


def _report_lines_for(p: "Path") -> set:
    """Lines belonging to the GENERATED report this response file annotates."""
    orig = _TTS_ORIGINALS / p.name
    if not orig.is_file():
        return set()
    try:
        return {l.strip() for l in read_any(orig).splitlines() if l.strip()}
    except Exception:                                     # noqa: BLE001
        return set()


def _looks_like_a_markdown_heading(line: str) -> bool:
    if not _MD_HEADING.match(line):
        return False
    body = line.lstrip("#").strip()
    # A heading rarely runs past a clause and rarely ends in sentence punctuation.
    return len(body) <= 120 and not body.rstrip().endswith((".", "?", "!"))


def read_any(path: Path) -> str:
    """Decode a response file whatever Word did to it.

    `errors="ignore"` is deliberate and is the point: an undecodable byte must cost ONE
    character, never the whole file. `splitlines()` then handles CR, LF and CRLF alike.
    """
    ext = path.suffix.lower()
    try:
        if ext in ZIPPED:
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
            xml = re.sub(r"</w:p>", "\n", xml)
            return re.sub(r"<[^>]+>", "", xml)
        if ext in RICH:
            r = subprocess.run(["textutil", "-stdout", "-convert", "txt", str(path)],
                               capture_output=True, text=True, timeout=120)
            return r.stdout or ""
        return decode_bytes(path.read_bytes())
    except Exception:
        return ""


#: Curly-quote byte ranges that DISCRIMINATE the two single-byte codecs Word may write.
#: Mac OS Roman puts the smart quotes at 0xD2-0xD5; Windows-1252 puts them at 0x91-0x94.
#: Both codecs decode EVERY byte, so "try until one works" always succeeds and proves nothing.
#: The question is which is CORRECT, and the quote bytes are what answer it.
_MAC_QUOTES = range(0xD2, 0xD6)
_CP1252_QUOTES = range(0x91, 0x95)


def decode_bytes(raw: bytes) -> str:
    """Decode a response file WITHOUT dropping a single character of his writing.

    WHY THIS REPLACED `errors="ignore"`, measured 2026-10-11 on his own instruction *"take care
    you are using the correct encodings to parse my outputs fully."* The lossy decode READ the
    files but MANGLED them: every curly apostrophe vanished, so *"I don't get it"* arrived as
    *"I dont get it"*. Measured across his plain-text files: **256 characters of his writing
    dropped across 14 of 29 files, 0.4828, Wilson [0.3139, 0.6557]** -- every one recoverable.

    THE CODEC IS MAC OS ROMAN AND THAT IS NOT A GUESS. His Word save dialog shows
    "Mac OS (Default)" with "Western (Mac OS Roman)" selected and "End lines with: CR only".
    In his files 0xD5 appears 11 times and 0xD4 3 times, which are the right and left single
    quotes in Mac OS Roman; under Windows-1252 the same bytes render as O-with-circumflex.

    Order: UTF-8 strict first, because a genuinely UTF-8 file must not be reinterpreted. Then
    whichever single-byte codec the quote bytes point at. `errors="replace"` is the last resort
    and it SHOWS the damage rather than hiding it, which is the opposite of what was there.
    """
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    mac = sum(1 for b in raw if b in _MAC_QUOTES)
    win = sum(1 for b in raw if b in _CP1252_QUOTES)
    order = ("mac_roman", "cp1252") if mac >= win else ("cp1252", "mac_roman")
    for enc in order + ("iso-8859-1",):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def file_shape(path: Path) -> dict:
    raw = path.read_bytes()
    cr_only = b"\r" in raw.replace(b"\r\n", b"")
    try:
        raw.decode("utf-8")
        utf8 = True
    except UnicodeDecodeError:
        utf8 = False
    return {"bytes": len(raw), "cr_only_line_endings": cr_only, "valid_utf8": utf8,
            "grep_would_treat_as_binary": (not utf8) or cr_only}


#: A LINE THAT IS NOTHING BUT MARKER TOKENS. His command markers -- `fr` a
#: feature request, `pf` a proposed fix, `qs` a question (his instruction of
#: 2026-10-19) -- are written on their OWN LINE after the annotation they belong
#: to, never inside it. Measured 2026-10-19 across every reply file: 30 markers,
#: 30 of them own-line following an annotation, 0 inline. So the reader must
#: associate that line with the annotation above it or the marker is lost, which
#: is exactly what was happening: the harvester reported "explicitly marked: 0"
#: while his files carried 30, because a marker line has no leading hash and was
#: therefore never part of any annotation's text.
_MARKER_LINE = re.compile(
    r"^\s*(fr|pf|qs|wr|ds)(?:\s*,\s*(?:fr|pf|qs|wr|ds))*\s*$", re.I)


#: ★ A TRAILING MARKER, WRITTEN AT THE END OF THE ANNOTATION ITSELF. Added
#: 2026-10-30, because his style changed and the own-line rule above stopped
#: covering it. The comment above records its own basis honestly -- 30 of 30
#: own-line, 0 inline, measured 2026-10-19 -- and that was true of the files
#: that existed then. MEASURED 2026-10-30 over all 752 annotations: 59 carry an
#: own-line marker, 693 carry none, and 13 of those 693 END in a marker token,
#: 0.018759 with a 95% Wilson interval [0.010995, 0.031829] and an exact
#: interval [0.010025, 0.031865]. Every one of the 13 is dated 2026-10-29.
#:
#: WHY IT MATTERS MORE THAN 13 SOUNDS. The 13 include the 2 rulings this project
#: has leaned on hardest -- "Build and implement option 1. fr" and "I accept
#: your recommendation. fr" -- which closed entries B47 and C1. Their markers
#: were invisible here and survived only because the harvester re-derives the
#: kind from the text. He has since said he will rely on marking questions `qs`
#: in his replies, so a marker field that cannot see his current style is a
#: silent loss of his instructions.
#:
#: THE MARKER MUST TRAIL, and that requirement is not a preference. Measured in
#: `scripts/which_open_entries_already_have_his_ruling_2026-10-30.py`: matching
#: an MC marker ANYWHERE in a quotation gave 4 of 19 hits and 3 were the bare
#: English article "a" matching mid-prose; requiring it to trail gave exactly
#: the 1 true positive. The 4 ticket kinds here are not English words, so the
#: risk is smaller, but the shape is the one that was measured to work.
#:
#: THE TEXT IS NOT ALTERED. Only this field is filled. `tid_of` digests a
#: ticket's verbatim, so stripping the marker out of the annotation would move
#: every identity derived from it -- a far larger change than the defect.
_MARKER_TRAILING = re.compile(
    r"(?:^|[\s.,;:!?)\]\"'’”])((?:fr|pf|qs|wr|ds)(?:\s*,\s*(?:fr|pf|qs|wr|ds))*)"
    r"[\s.!?]*$", re.I)


#: ★ THE OTHER 5 SEATS, so a trailing `ds` that is the DeepSeek seat is not
#: read as his discussion marker. `ds` is BOTH a ticket kind (founder ruling
#: 2026-10-30) and the DeepSeek V4 Pro seat in the dispatch table, and the
#: collision is realised in exactly 1 shape: a dispatch instruction naming
#: several seats where `ds` lands last. Measured in
#: `scripts/the_ds_label_and_the_kind_allowlist_2026-10-30.py`: 0 of his 794
#: annotations do this today, Wilson [0.000000, 0.004815], so this guard is
#: PRECAUTIONARY and says so -- but 46 of 53 user-role transcript entries
#: carrying the token use it as a seat, Wilson [0.751597, 0.934521], so the
#: shape is not hypothetical, only absent from this source.
_SEAT_BEFORE = re.compile(r"\b(cc2|cx|ge|cgpt|fable)\s*[, ]\s*$", re.I)


def _marker_of(body: str) -> str:
    """His marker read from the END of the annotation, or "" if there is none."""
    body = (body or "").strip()
    m = _MARKER_TRAILING.search(body)
    if not m:
        return ""
    found = [x.strip().lower() for x in m.group(1).split(",") if x.strip()]
    if found == ["ds"] and _SEAT_BEFORE.search(body[:m.start(1)]):
        return ""
    return ",".join(found)


#: 2 DATES, NAMED FOR WHAT THEY ARE -- repair 2026-10-28, and the first attempt
#: at it was WRONG in an instructive way.
#:
#: A response file carries 2 different facts and they must not be conflated.
#: The DATE IN THE NAME is the date of the report HE WAS ANNOTATING, written by
#: this project. The MTIME is approximately when HE WROTE the annotation, which
#: is necessarily later. Asking "which report is this against?" and "when did he
#: write it?" are different questions.
#:
#: MY FIRST FIX REPLACED mtime WITH THE NAME EVERYWHERE, and that silently
#: changed the meaning of every `--since` window in the project. It immediately
#: orphaned 12 verdict rows: `Intelligence_First_Take_Home_2026-09-30.txt` moved
#: from October into September and left the verdict record's window while its 12
#: rows stayed behind. Widening the window to compensate would have surfaced 35
#: annotations with no verdict row -- real work, created by a change of meaning
#: nobody asked for.
#:
#: SO BOTH ARE RECORDED AND `date` IS UNCHANGED. `report_date` is new, `by=`
#: selects which one a window filters on, and the default is `mtime`, so every
#: existing caller behaves exactly as before.
#:
#: WHY ANY OF THIS WAS NEEDED. mtime is MUTABLE -- anything touching a file moves
#: it, and task B42 established that Word rewrites his .txt files on save.
#: Measured 2026-10-28: of 90 annotated files carrying a date in the name, 37 had
#: an mtime that disagreed with it, 0.411111 Wilson [0.315132, 0.514368], drifting
#: LATER by up to 5 days. A window built on mtime therefore cannot be closed, which
#: is what `test_the_corpus_count_is_unchanged_by_the_fix` needs; it now asks for
#: `by="report"` and gets a population that an mtime change cannot move.
#:
#: WHAT WAS WRONG. Every annotation was dated by `st_mtime`, which is MUTABLE:
#: anything that touches a file moves it, and this project has already
#: established that Word rewrites his .txt files on save (task B42, 35 of 106
#: files carry the CR-only signature). So his words drifted to whatever day a
#: tool last touched them.
#:
#: MEASURED 2026-10-28, which is why this is a repair and not a preference:
#: of 90 annotated files carrying a date in the name, 37 had an mtime that
#: DISAGREED with it -- 0.411111, Wilson [0.315132, 0.514368] -- and 299
#: annotations were being read under the wrong date. The drift is always LATER,
#: by up to 5 days.
#:
#: HOW IT SURFACED. `test_the_corpus_count_is_unchanged_by_the_fix` pins 522
#: annotations dated on or before 2026-10-13 and read 517. Its docstring states
#: the window is closed because "`until` filters on the date in each response
#: file's name" -- which was NOT what the code did. The 5 missing were not lost:
#: `The_Directive_Set_2026-10-13.txt` has mtime 2026-10-14 18:07, so its 11
#: annotations left the window while other in-window files gained 6. The
#: manifest confirms 0 files lost an annotation.
#:
#: CHECKED BEFORE CHANGING IT. Name-dating moves annotations EARLIER, which could
#: push one out of the freshness gate's window and silently excuse an unread
#: ruling of his. Measured: 12 annotations leave the window and ALL 12 already
#: carry a verdict row, so nothing unread is excused.
def _report_date(p: Path) -> _dt.date:
    """The date of the REPORT he annotated, from the file's name.

    Falls back to mtime when the name carries no date, so every file has one.
    """
    m = _NAME_DATE.search(p.name)
    if m:
        try:
            return _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return _dt.date.fromtimestamp(p.stat().st_mtime)


def _written_date(p: Path) -> _dt.date:
    """Approximately when HE WROTE the annotation. Mutable; see the note above."""
    return _dt.date.fromtimestamp(p.stat().st_mtime)


def annotations(since: _dt.date | None = None, until: _dt.date | None = None,
                by: str = "mtime") -> list:
    """Every `#`-prefixed annotation the founder wrote, with its file and date."""
    out = []
    for p in sorted(RESPONSES.glob("*")):
        if not is_one_of_his_annotated_responses(p):
            continue
        d = _written_date(p)
        rd = _report_date(p)
        # `by` SELECTS WHICH FACT THE WINDOW FILTERS ON. Default "mtime"
        # keeps every existing caller unchanged; "report" gives a window an
        # mtime change cannot move.
        key = rd if by == "report" else d
        if since and key < since:
            continue
        if until and key > until:
            continue
        out.extend(_annotations_in(p, d, rd))
    return out


def _annotations_in(p: Path, d: _dt.date | None = None,
                    rd: _dt.date | None = None) -> list:
    """Every annotation in ONE file. The single definition of what counts as one."""
    out = []
    if d is None:
        d = _written_date(p)
    if rd is None:
        rd = _report_date(p)
    text = read_any(p)
    if text:
        _lines = text.splitlines()
        for i, line in enumerate(_lines):
            s = line.strip()
            if not (s.startswith("#") and len(s) > 2):
                continue
            # A MARKDOWN HEADING IS NOT ONE OF HIS ANNOTATIONS. Found 2026-10-11 by READING
            # the extract rather than trusting its count: entries 81-87 of a 258-row pull were
            # headings from `CDSFL_Panel_Advice_and_Shakedown_Readiness_2026-09-29.md` --
            # "Recommendation", "Explorer interpretation". The `.md` files in this folder are
            # saved web pages and machine-generated exports (one is literally
            # "asymptote curve meaning - Google Search.md"); he annotates .txt, .rtf and .docx
            # in Word. Counting headings inflated his 480 real annotations to 691.
            if p.suffix.lower() in (".md", ".markdown") and _looks_like_a_markdown_heading(s):
                continue
            body = s.lstrip("# ").strip()
            # AN ANNOTATION CAN SPAN LINES, AND HIS TRAILING HASH SAYS SO.
            # FOUND 2026-10-13 ON HIS OWN INSTRUCTION -- "Make sure you can
            # parse my responses in full" -- the SECOND time he has had to say
            # it. The first was `errors="ignore"` eating his curly apostrophes,
            # 256 characters across 14 files. THIS one: a line-by-line walk
            # treated each '#' line as a whole annotation, so an annotation
            # continuing on later lines lost everything after the first.
            #
            # MEASURED ON THE FILE THAT EXPOSED IT. His first annotation on
            # Morning_Report_2026-10-13.txt occupies lines 23, 25 and 27 (the
            # hash line, his re-quoted ruling, then its tail) and the reader
            # returned 97 of 1,053 characters. The lost text carried the
            # operative clause -- "But propose your own fixes first" -- which
            # changes the ORDER of the work, and it survived only because the
            # file was also read directly.
            #
            # THE RULE IS HIS OWN CONVENTION: a LEADING hash opens an
            # annotation, a TRAILING hash says a quotation follows. The
            # continuation then runs until THE REPORT RESUMES, read from the
            # generated original where one survives, so the boundary is an
            # oracle rather than a guess. Measured across the corpus: 1 of 522
            # annotations ends with a trailing hash, 0.1916%, Wilson 95%
            # [0.0338%, 1.0771%]; a rule capturing ANY following prose line
            # would have swallowed 367 further lines, mostly the reports' own
            # sentences. Producer:
            # scripts/an_annotation_can_span_lines_2026-10-13.py.
            _last = i
            if s.endswith("#"):
                _report = _report_lines_for(p)
                _parts = [body.rstrip("# ").rstrip()]
                for _j in range(i + 1, len(_lines)):
                    _nxt = _lines[_j].strip()
                    if not _nxt:
                        continue
                    if _nxt.startswith("#"):
                        break
                    if _report:
                        if _nxt in _report:
                            break
                    elif _REPORT_SHAPE.match(_nxt):
                        break
                    _parts.append(_nxt)
                    _last = _j
                body = " ".join(x for x in _parts if x).strip()
            # HIS MARKER, if he wrote one. Skip blank lines only; the first
            # non-blank line after the annotation either IS the marker or
            # there is none. Stopping at the first non-blank is what keeps a
            # marker belonging to a LATER annotation from being stolen here.
            _marker = ""
            for _k in range(_last + 1, len(_lines)):
                _cand = _lines[_k].strip()
                if not _cand:
                    continue
                if _MARKER_LINE.match(_cand):
                    _marker = ",".join(
                        x.strip().lower() for x in _cand.split(",") if x.strip())
                break
            #: FALL BACK TO A TRAILING MARKER inside the annotation's own text.
            #: The own-line form is tried FIRST and wins, because it is the form
            #: 59 of his markers use and it is unambiguous.
            if not _marker:
                _marker = _marker_of(body)
            out.append({"file": p.name, "ext": p.suffix.lower(), "date": d.isoformat(),
                        "report_date": rd.isoformat(),
                        "line_index": i, "text": body, "marker": _marker})
    return out


def claim_a_naive_grep_is_blind_to_some_of_them() -> dict:
    """The measurement that justifies this script, recomputed rather than quoted."""
    files = [p for p in RESPONSES.glob("*") if is_a_response_file(p)]
    annotated, blind, blind_count, total_count = 0, 0, 0, 0
    cr, nonutf8 = 0, 0
    for p in files:
        try:
            shape = file_shape(p)
        except OSError:
            continue
        if shape["cr_only_line_endings"]:
            cr += 1
        if not shape["valid_utf8"]:
            nonutf8 += 1
        # ONE CODE PATH. This counter originally re-implemented the annotation test inline
        # and the two drifted the moment markdown headings were excluded from `annotations()`:
        # the window pull correctly fell to 248 while this function still reported 691. A
        # producer and a consumer that disagree is the defect `execute-do-not-grep` names, so
        # the count now comes from the same function that yields the annotations.
        n = len(_annotations_in(p))
        if not n:
            continue
        annotated += 1
        total_count += n
        if shape["grep_would_treat_as_binary"]:
            blind += 1
            blind_count += n
    nf = len(files)
    return {
        "files": nf,
        "cr_only": cr, "cr_only_rate": round(cr / nf, 4) if nf else None,
        "cr_only_wilson": wilson(cr, nf),
        "not_valid_utf8": nonutf8, "not_valid_utf8_wilson": wilson(nonutf8, nf),
        "annotated_files": annotated,
        "annotated_files_a_naive_grep_misses": blind,
        "blind_rate": round(blind / annotated, 4) if annotated else None,
        "blind_wilson": wilson(blind, annotated),
        "annotations_total": total_count,
        "annotations_in_blind_files": blind_count,
        "blind_share_of_annotations": (round(blind_count / total_count, 4)
                                       if total_count else None),
    }


def unreadable_but_annotated() -> list:
    """Files whose RAW BYTES contain an annotation marker but which the reader cannot read.

    THIS IS THE GUARD CONDITION. It is what turns a silent miss into a loud failure: if a new
    Word format, a new encoding or a new extension ever defeats `read_any`, this lists the file
    instead of letting the inventory quietly shrink.
    """
    bad = []
    for p in sorted(RESPONSES.glob("*")):
        if not is_a_response_file(p):
            continue
        try:
            raw = p.read_bytes()
        except OSError as e:
            bad.append({"file": p.name, "why": f"unreadable: {type(e).__name__}"})
            continue
        if b"#" not in raw:
            continue
        text = read_any(p)
        found = sum(1 for l in text.splitlines()
                    if l.strip().startswith("#") and len(l.strip()) > 2)
        if found:
            continue
        # A '#' in the bytes but none at a line start after decoding. For a known format that
        # is fine (a '#' mid-sentence); for an UNKNOWN extension it is a reader gap.
        ext = p.suffix.lower()
        if ext in ARCHIVES:
            # ★ AN ARCHIVE IS OPENED RATHER THAN GUESSED AT -- repair 2026-10-28.
            #
            # `CDSFL_UX_Design_Brief_AUTHORITATIVE.zip` was reported as a gap
            # every run, with the reason "extension unknown to this reader", and
            # that reason was WRONG in a way that got the flag dismissed -- by me
            # among others, on 2026-10-28, when I called it a false positive.
            #
            # IT WAS NOT A FALSE POSITIVE. The archive holds 5 markdown documents
            # he supplied, one of them an authoritative design brief, and a
            # tree-wide grep found 0 files referencing any of them: the content
            # had never reached the record. That is a real gap of a DIFFERENT
            # kind, now recorded on the runway as 0C.24a and raised as
            # pf:7410dc26b49c.
            #
            # WHAT THIS CHECK OWNS IS ANNOTATIONS, AND THOSE ARE 2 DIFFERENT
            # FACTS. The 41 line-initial hash lines inside that archive are
            # MARKDOWN HEADINGS, not his annotations -- a distinction this reader
            # already knows how to make for a loose file and simply never applied
            # inside a container. So the members are read and the SAME predicate
            # is applied. An archive whose members carry none of his annotations
            # is not an annotation gap; one that does is, and will now say so.
            inner = _annotations_inside_archive(p)
            if inner:
                bad.append({"file": p.name, "ext": ext,
                            "why": f"an archive holding {inner} annotation(s) of "
                                   f"his that no reader reaches",
                            "bytes": len(raw)})
            continue
        if ext not in TEXTISH | RICH | ZIPPED:
            bad.append({"file": p.name, "ext": ext,
                        "why": "extension unknown to this reader, and its bytes contain '#'",
                        "bytes": len(raw)})
    return bad


#: Containers whose MEMBERS may carry his words. `.docx` is already handled as a
#: document by `read_any`; these are opened and looked into instead.
ARCHIVES = {".zip"}


def _annotations_inside_archive(p: Path) -> int:
    """How many of HIS annotations sit inside this archive, by the same predicate.

    Returns 0 for an archive of markdown whose hash lines are headings, which is
    the common case and is NOT an annotation gap. Returns a count when his words
    really are sealed inside one, which is the case this exists for.
    """
    import zipfile
    try:
        with zipfile.ZipFile(p) as z:
            total = 0
            for name in z.namelist():
                suffix = Path(name).suffix.lower()
                if suffix not in TEXTISH:
                    continue
                try:
                    text = z.read(name).decode("utf-8", errors="replace")
                except Exception:                                  # noqa: BLE001
                    continue
                for line in text.splitlines():
                    t = line.strip()
                    if not t.startswith("#") or len(t) <= 2:
                        continue
                    # A markdown heading is not an annotation. Same call the
                    # loose-file path makes, so the 2 cannot disagree.
                    if suffix in (".md", ".markdown") and \
                            _looks_like_a_markdown_heading(t):
                        continue
                    total += 1
            return total
    except (zipfile.BadZipFile, OSError):
        # A container this reader cannot open IS a gap worth reporting, and
        # reporting it as 1 is honest: the count is unknown and non-zero is the
        # safe direction for a check about his words going unread.
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", metavar="YYYY-MM-DD")
    ap.add_argument("--until", metavar="YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="exit 3 if a file looks annotated but cannot be read")
    args = ap.parse_args()

    if not RESPONSES.is_dir():
        print(f"  the responses folder is not present: {RESPONSES}", file=sys.stderr)
        return 0 if not args.verify else 3

    since = _dt.date.fromisoformat(args.since) if args.since else None
    until = _dt.date.fromisoformat(args.until) if args.until else None
    anns = annotations(since, until)
    shape = claim_a_naive_grep_is_blind_to_some_of_them()
    gaps = unreadable_but_annotated()

    if args.json:
        print(json.dumps({"annotations": anns, "coverage": shape, "reader_gaps": gaps},
                         indent=1))
    else:
        print(f"== the founder's annotations in {RESPONSES} ==")
        print(f"   annotations read: {len(anns)}"
              + (f"  (since {since})" if since else ""))
        by_file = {}
        for a in anns:
            by_file.setdefault((a["date"], a["file"]), 0)
            by_file[(a["date"], a["file"])] += 1
        for (d, f), n in sorted(by_file.items()):
            print(f"     {d}  {n:>3}  {f}")
        print("\n== why a naive grep is not enough ==")
        for k, v in shape.items():
            print(f"   {k}: {v}")
        print("\n== reader gaps (the guard condition) ==")
        print(f"   {len(gaps)} file(s) look annotated but cannot be read")
        for g in gaps:
            print(f"     {g}")

    if args.verify and gaps:
        print(f"\nREFUSED: {len(gaps)} response file(s) carry an annotation marker in their raw "
              f"bytes but read as unannotated. A silent miss here is how 221 of the founder's "
              f"verdicts went unread for 11 days.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
