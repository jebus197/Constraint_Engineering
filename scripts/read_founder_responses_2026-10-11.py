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
import functools
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
#:     FINAL_REPORT_FOR_OPUS_2026-08-27.md, and does NOT mark
#:     design_brief.txt, which carries none. ★ CORRECTED 2026-11-04: that
#:     report carries NO verdict of his either. Its 1 counted annotation was
#:     a 2-hash markdown heading in a report authored by another model, and
#:     commit a0eb9d00 of 2026-11-03 correctly reclassified it. THE
#:     REFUTATION SURVIVES ON ITS OTHER LEG: design_brief.txt has 3 one-hash
#:     lines and 0 two-hash lines, so a heading-density discriminator still
#:     misses it, while this report has 8 two-hash headings and 0 of his
#:     words. The conclusion stands; its first stated reason does not;
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
#: in any other kind of file. ★ THE .md 1 FELL TO 0 ON 2026-11-03 (commit
#: a0eb9d00): it was a 2-hash heading in another model's report, never his.
#: `.md` IS RETAINED HERE DELIBERATELY AT 0, because this module's own
#: docstring records that the dangerous direction is UNDER-reach, and
#: narrowing the allow list would silently drop a future .md annotation of
#: his. A 0 is not a reason to remove an entry; it is a reason to keep it
#: and say why. A new extension is a deliberate addition here,
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
    682 in all -- against 65 in the single .zip and 0 in any .docx. CORRECTED
    2026-11-04: 2 extensions, 425 in .txt and 256 in .rtf, 681 in all. The
    .md 1 was a 2-hash heading in another model's report and was never his;
    425 + 256 = 681 exactly, so the total is derived and not adjusted to fit.
    """
    return (is_a_response_file(path)
            and path.suffix.lower() in TEXT_SUFFIXES
            and path.name not in NOT_HIS_ANNOTATIONS
            # ★ 2026-11-03: the allow list above trusts the EXTENSION, and an
            # 11 MB PNG named `.md` walked through it and contributed 780
            # annotations he never wrote. See `is_binary_file`.
            and not is_binary_file(path))


#: Byte signatures of formats that are NOT text, for files that reach the first
#: 4 KiB with no NUL. A PDF is the case that matters: `%PDF` then ASCII, so a
#: NUL test alone does not see it.
_BINARY_MAGIC = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"%PDF", b"BM",
                 b"RIFF", b"\x1f\x8b", b"PK\x03\x04", b"\x00\x00\x01\x00")


def is_binary_file(path: Path, probe: int = 4096) -> bool:
    """Is this file binary? Decided by its BYTES, never by its extension.

    ★ ADDED 2026-11-03. THIS IS THE 4TH FILE OF THE SAME SHAPE TO CORRUPT THE
    RECORD OF HIS WORDS, and the first 3 were each patched by NAME or by
    EXTENSION.

    THE HISTORY, from this module's own comments. `.DS_Store` was excluded by
    name. Word's `~$` lock files were excluded by prefix. Then
    `CDSFL_UX_Mockup_Pack_Light_2026-10-20.zip` returned 65 lines of compressed
    binary as his annotations, and the repair of 2026-10-20 was the ALLOW LIST
    `TEXT_SUFFIXES = {.txt, .rtf, .md}`, recorded here with the words *"AN
    EXCLUSION LIST CANNOT HOLD"* and *"The ALLOW list is decidable."*

    THE ALLOW LIST IS DECIDABLE AND IT WAS ALSO DEFEATED, because an extension
    is a CLAIM ABOUT CONTENT rather than content. `Google Search Discussion on
    severity- 2026-09-28_10-28.md` is an 11,076,291-byte PNG -- it opens
    `\x89PNG`, `IHDR`, `IDAT` -- and `.md` is on the allow list. It decoded to
    249,610 lines of which 780 began with `#`, so the reader returned 780
    annotations he never wrote: 0.481779 of the entire 1,619-annotation corpus.
    3 guards went red on it and the reader slowed from 3.576 s to 684.25 s,
    which took every commit with it.

    SO THE PREDICATE HAS TO READ THE FILE. That is `execute-do-not-grep` applied
    to file typing: a name describes itself consistently whatever it contains.

    WHY BOTH TESTS AND NOT 1, measured, because his composability standard wants
    a figure rather than a pair of ideas that fit together. Over the 348 files in
    his folder: a NUL byte in the first 4 KiB catches 39, a magic number catches
    28, and 26 are caught by both. 2 are caught by MAGIC ONLY -- both PDFs,
    which have no early NUL -- so the NUL test alone misses 2 of the 30 binaries
    it is aimed at. Today those 2 wear `.pdf` and the allow list stops them
    anyway; a PDF saved as `.md` is the case the pair exists for, and it is the
    same accident that produced the PNG. Neither test is redundant, which is the
    condition the standard sets.

    IT CANNOT DROP A VERDICT OF HIS. Every shape-based discriminator tried on
    this folder was measured and REFUTED in 2026-10-17 -- a dated-filename
    filter lost 8 of 598, a markdown-structure test lost 12 real verdicts
    including "Verdict: y". Those all guessed whether PROSE was his. This asks
    whether the file is TEXT AT ALL, which is a different question with a hard
    answer: 0 of his legitimate .txt and .md files carry a NUL byte. The only 3
    that do are this PNG and 2 `~$ok` Word lock files already excluded by prefix.
    """
    try:
        head = path.open("rb").read(probe)
    except OSError:
        return False                   # unreadable is a REPORTED gap, not a skip
    return b"\x00" in head or head.startswith(_BINARY_MAGIC)


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

#: His ticket markers, as a trailing token. Sourced from `ticket_store.KINDS`
#: so the 2 declarations cannot drift; falls back to the literal set only when
#: the import is unavailable, and the guard asserts the 2 agree.
try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from bench.ticket_store import KINDS as _HIS_KINDS
except Exception:                                         # noqa: BLE001
    _HIS_KINDS = ("fr", "pf", "qs", "wr", "stm", "disc", "dis", "ds")
_ENDS_IN_HIS_MARKER = re.compile(
    r"\b(?:" + "|".join(sorted(_HIS_KINDS, key=len, reverse=True)) + r")\b\s*$",
    re.IGNORECASE)

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
    stripped = line.lstrip()
    # ★ 2 OR MORE HASHES IS ALWAYS A HEADING, NEVER HIS MARKER. Added 2026-11-02
    # after 2 markdown headings in an EXTERNAL note leaked through as his
    # annotations and the commit gate refused the commit for 2 verdict rows it
    # could not find. Both had defeated the shape test below for the same
    # reason: they are headings PHRASED AS QUESTIONS, so they end in "?" while
    # the shape test assumes a heading does not.
    #
    # HIS CONVENTION IS EXACTLY 1 HASH, AND THAT IS MEASURED RATHER THAN
    # ASSUMED. Across the 45 response files where a generated original survives
    # as an ORACLE -- so his lines are known rather than guessed -- 583 of his
    # annotations open with exactly 1 hash and 0 open with 2 or more, Wilson 95%
    # [0.000000, 0.006546]. In the live reporting window, 568 of 570
    # annotations open with 1 hash and the only 2 with more are the 2 leaking
    # headings, 0.003509, Wilson 95% [0.000963, 0.012702]. So this rule removes
    # exactly those 2, keeps all 568, and orphans no verdict row.
    #
    # The shape test is KEPT for the single-hash case, where it is still the
    # only available signal and where the oracle is preferred over it anyway.
    if len(stripped) - len(stripped.lstrip("#")) >= 2:
        return True
    body = line.lstrip("#").strip()
    # ★ A LINE ENDING IN ONE OF HIS TICKET MARKERS IS NEVER A HEADING. Added
    # 2026-11-08 on his ruling (B105). His commonest annotation form is
    # "I accept your recommendation. stm" -- and it defeated the shape test
    # below in the WORST possible way: it ends in a marker rather than in
    # sentence punctuation, so `endswith((".", "?", "!"))` is False, and it is
    # short, so `len(body) <= 120` is True. Both conditions for "this is a
    # heading" were therefore met by the single most common thing he writes,
    # and the line was discarded as not his.
    #
    # THE MARKER SET IS IMPORTED, NOT SPELLED HERE, so a 7th kind added to
    # `ticket_store.KINDS` is recognised without editing this file -- the
    # addition-nothing-reaches failure in reverse. A WORD BOUNDARY is required
    # on both sides, which is what keeps `disc` out of "discussion" and `ds`
    # out of "Methods"; checked by execution in the guard rather than reasoned
    # about here. The match is CASE-INSENSITIVE because 3 of his annotations
    # carry `Qs` and `Stm` with a leading capital, and a case-sensitive
    # pattern drops exactly those.
    if _ENDS_IN_HIS_MARKER.search(body):
        return False
    # A heading rarely runs past a clause and rarely ends in sentence punctuation.
    return len(body) <= 120 and not body.rstrip().endswith((".", "?", "!"))


def read_any(path: Path) -> str:
    """Decode a response file whatever Word did to it.

    `errors="ignore"` is deliberate and is the point: an undecodable byte must cost ONE
    character, never the whole file. `splitlines()` then handles CR, LF and CRLF alike.

    ★ DECODED ONCE PER (path, mtime, size), 2026-11-03, on his instruction *"have
    you/can you fix them, and do so in such a way that any researcher/model using
    the CDSFL harness to do real work, would be unlikely to run into similar
    issues?"*

    WHAT IT COST TO NOT CACHE. `context_for` calls this once per ANNOTATION, and
    780 of his 1,619 annotations live in one 11.08 MB file, so that file was
    decoded 780 times. Measured on the live corpus by 2 independent routes that
    agree to 99.5%: a strided sample of 63 of the 1,619 annotations costs 420.63 ms
    each and PROJECTS the loop at 680.995 s, against a pinned CLI wall of 684.25 s
    for the same arguments. The library call alone is 3.576 s, so essentially the
    whole cost was re-decoding. 2 guards that shell out to this CLI then died on
    `pytest.ini`'s 300 s timeout and NO COMMIT COULD LAND.

    A HEAD-OF-LIST SAMPLE WOULD HAVE HIDDEN IT. The first 40 annotations sit in
    small files and cost 18.68 ms each, projecting 30.241 s -- 22.5x too low. The
    sample has to be strided so every file is drawn in proportion to its share.

    WHY HERE AND NOT IN `context_for`. 11 call sites across 7 files reach this
    function and 4 of them call it inside a loop over his files, so the quadratic
    term is removed for every caller rather than for the one that exposed it.
    That is what makes the repair general rather than local to the failure found.

    THE INVALIDATION KEY IS (path, mtime_ns, size), so a file edited mid-run is
    re-decoded rather than served stale. THE HONEST HOLE: a write that preserves
    BOTH size and mtime_ns -- an mtime-restoring tool, say -- would be missed. No
    caller in this repo does that; a researcher's might, and `read_any.cache_clear`
    is the escape hatch for one that does.
    """
    try:
        st = path.stat()
    except OSError:
        return ""
    return _decode_cached(str(path), st.st_mtime_ns, st.st_size)


#: Small on purpose. His corpus is 18.77 MB on disk and decodes larger, and his
#: machine's 8 GiB is a FIXED RESOURCE that work may never be refused for. 8
#: entries is enough for the access pattern that matters -- consecutive
#: annotations from the same file -- and caps the cache at a handful of files
#: rather than the whole folder.
@functools.lru_cache(maxsize=8)
def _decode_cached(path_str: str, mtime_ns: int, size: int) -> str:
    """The body of `read_any`, keyed so a changed file is decoded again."""
    path = Path(path_str)
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


#: The escape hatch the `read_any` docstring names. An attribute, not a second
#: public name, so there is exactly 1 way to reach it and it cannot drift.
read_any.cache_clear = _decode_cached.cache_clear          # type: ignore[attr-defined]
read_any.cache_info = _decode_cached.cache_info            # type: ignore[attr-defined]


def lines_of(path: Path) -> tuple[str, ...]:
    """The lines of a response file, split ONCE per (path, mtime, size).

    ★ ADDED 2026-11-03, because caching the DECODE fixed only half the cost.

    THE HALF THAT WAS LEFT, measured. With `read_any` cached, the reader still
    took 51.23 s where the library call is 3.576 s. `splitlines()` on his 11.08 MB
    severity file costs 56.48 ms and produces 249,610 lines, and `context_for`
    ran it once per annotation -- 780 times for that file alone. 56.48 ms x 780
    = 44.05 s, which is 94% of the 47 s that remained. The decode was never the
    only quadratic term; it was the VISIBLE one.

    WHY A TUPLE AND NOT A LIST. A cache that hands out a mutable object hands
    every later caller the first caller's edits. The tuple makes that
    impossible rather than merely discouraged.

    SAME KEY AS `read_any`, so a file edited mid-run is re-split, and the same
    honest hole applies: a write preserving both size and mtime_ns is missed.
    """
    try:
        st = path.stat()
    except OSError:
        return ()
    return _lines_cached(str(path), st.st_mtime_ns, st.st_size)


#: 4, not 8. The hit rate measured over his whole corpus is 1,557 of 1,619 at
#: maxsize 8, so locality is high and a smaller cache loses almost nothing --
#: and the split lines of his biggest file cost about as much again as its
#: decoded text, on a machine whose 8 GiB is a fixed resource.
@functools.lru_cache(maxsize=4)
def _lines_cached(path_str: str, mtime_ns: int, size: int) -> tuple[str, ...]:
    """The body of `lines_of`, keyed so a changed file is split again."""
    return tuple(read_any(Path(path_str)).splitlines())


lines_of.cache_clear = _lines_cached.cache_clear           # type: ignore[attr-defined]
lines_of.cache_info = _lines_cached.cache_info             # type: ignore[attr-defined]


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
#: ★ `stm` ADDED 2026-11-01, HIS 6th KIND. This reader is the 5th place the
#: marker vocabulary is spelled out -- after `KINDS` and the harvester's 3
#: patterns -- and the guard that the 2 readers here agree on EVERY live kind
#: is what found the omission, by iterating `KINDS` rather than a list of its
#: own. Without it, `stm` would have been readable by the harvester and
#: invisible to the reader that actually parses his annotations.
_MARKER_LINE = re.compile(
    r"^\s*(fr|pf|qs|wr|stm|disc|dis|ds)(?:\s*,\s*(?:fr|pf|qs|wr|stm|disc|dis|ds))*\s*$", re.I)


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
    r"(?:^|[\s.,;:!?)\]\"'’”])((?:fr|pf|qs|wr|stm|disc|dis|ds)(?:\s*,\s*(?:fr|pf|qs|wr|stm|disc|dis|ds))*)"
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
#: His rename of 2026-10-30: `ds` -> `dis`. Kept so his already-written
#: annotations stay readable; see LEGACY_KIND_ALIASES in bench/ticket_store.py.
#: His 2 renames of 2026-10-30, flat: `ds` and `dis` both became `disc`.
#: See LEGACY_KIND_ALIASES in bench/ticket_store.py for the measurement.
_LEGACY_MARKERS = {"ds": "disc", "dis": "disc"}

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
    # ★ `ds` NORMALISES TO `dis`, his rename of 2026-10-30. His annotations
    # written earlier that day carry `ds` and must keep working; nothing new is
    # filed under it. The seat-adjacency guard above still applies to the
    # legacy spelling and is NOT needed for `dis`, which appears 0 times in all
    # 794 of his annotations.
    found = [_LEGACY_MARKERS.get(x, x) for x in found]
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
            #: ★ WHICH FORM THE MARKER CAME FROM, added 2026-10-31. Without it a
            #: consumer cannot compare like with like:
            #: `can_i_parse_his_responses_in_full_2026-10-19.py` counted own-line
            #: marker LINES on the raw side against own-line PLUS trailing
            #: markers on this side, so the moment a file carried a trailing
            #: marker and no own-line one the measurement reported the reader as
            #: inventing markers it had correctly read. 4 files did, carrying 38
            #: markers between them. The field is the association rule's own
            #: output, so it is the only place that knows the answer.
            _marker_form = ""
            for _k in range(_last + 1, len(_lines)):
                _cand = _lines[_k].strip()
                if not _cand:
                    continue
                if _MARKER_LINE.match(_cand):
                    # ★ NORMALISE HERE TOO. Until 2026-10-31 the legacy-spelling
                    # map was applied ONLY in `_marker_of`, the trailing-marker
                    # path, so an OWN-LINE `ds` or `dis` came back raw while the
                    # same marker written inline came back as `disc`. 2 readers,
                    # 1 normalised. Found by
                    # `TestTheOwnLineMarkerReaderSeesDiscToo`, which exists
                    # because a mutation removing `disc` from `_MARKER_LINE`
                    # left the guard green -- the own-line path had no coverage
                    # at all. It is the form 59 of his markers use, so the gap
                    # covered most of the corpus.
                    _marker = ",".join(
                        _LEGACY_MARKERS.get(x.strip().lower(), x.strip().lower())
                        for x in _cand.split(",") if x.strip())
                    if _marker:
                        _marker_form = "own_line"
                break
            #: FALL BACK TO A TRAILING MARKER inside the annotation's own text.
            #: The own-line form is tried FIRST and wins, because it is the form
            #: 59 of his markers use and it is unambiguous.
            if not _marker:
                _marker = _marker_of(body)
                if _marker:
                    _marker_form = "trailing"
            out.append({"file": p.name, "ext": p.suffix.lower(), "date": d.isoformat(),
                        "report_date": rd.isoformat(),
                        "line_index": i, "text": body, "marker": _marker,
                        "marker_form": _marker_form})
    return out


def claim_a_naive_grep_is_blind_to_some_of_them() -> dict:
    """The measurement that justifies this script, recomputed rather than quoted.

    ★★★ TWO DENOMINATORS LIVE HERE AND THEY ANSWER DIFFERENT QUESTIONS, 2026-11-04.
    The READABILITY figures (`files`, `cr_only`, `not_valid_utf8`) are properties
    of the folder, so they are counted over every file `is_a_response_file`
    admits. The ANNOTATION figures are claims about HIS WRITING, so they are
    counted over `is_one_of_his_annotated_responses` only.

    UNTIL TODAY ALL OF THEM USED THE BROAD PREDICATE, AND THE FIRST LINE READ
    AFTER `rs` CARRIED THE CONSEQUENCE. `scripts/cdsfl_recover.py` quotes
    `annotations_total` and `annotations_in_blind_files` in the FIRST READ
    banner, so every session was told he had written **1,953** verdicts of which
    1,688 were invisible to grep. He wrote **839**, of which 583 are. The gap
    decomposes exactly: 1953 = 839 + 1114, verified in plain integers and in
    SymPy, and **1,114 of 1,953 -- 0.570405, Wilson [0.548333, 0.592199] -- was
    not his writing at all**. 1,103 of those 1,114 came from 2 files: an 11 MiB
    PNG wearing a `.md` extension (780) and a `.zip` (323).

    THE 2026-11-03 REPAIR FIXED THE DECIDING LAYER AND LEFT THIS ONE. That
    morning `is_binary_file` was added to the narrow predicate precisely to
    exclude that PNG, and `annotations()` duly fell. This function never
    consulted the narrow predicate, so it went on reporting the PNG's 780.

    AND THE BROAD PREDICATE IS *NOT* NARROWED TO FIX IT, deliberately. Its other
    2 call sites are the module's gap detectors, and narrowing readability would
    make an unparseable file stop being reported as a gap --
    `test_the_readability_predicate_was_not_narrowed` enforces that on purpose.
    So the residue is EXCLUDED FROM THE COUNTS AND REPORTED BY NAME in
    `annotations_excluded_as_not_his` and `excluded_files`, because an exclusion
    nobody can see is the shape this project's own record warns about.

    Producer: `scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py`.
    """
    files = [p for p in RESPONSES.glob("*") if is_a_response_file(p)]
    annotated, blind, blind_count, total_count = 0, 0, 0, 0
    excluded_count, excluded = 0, []
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
        # ★ AN ANNOTATION COUNT IS A CLAIM ABOUT HIS WRITING. A file the reader
        # can READ but which is not HIS is tallied separately and named, never
        # folded into the totals the FIRST READ banner quotes. The readability
        # counters above have already seen it, which is the point: 2 questions,
        # 2 denominators, 1 pass over the folder.
        if not is_one_of_his_annotated_responses(p):
            try:
                size = p.stat().st_size
            except OSError:
                size = -1
            excluded_count += n
            excluded.append({"file": p.name, "annotations": n, "bytes": size,
                             "suffix": p.suffix.lower() or "(none)"})
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
        # ★ THE RESIDUE, REPORTED RATHER THAN DROPPED (2026-11-04). Readable
        # files bearing a marker that `is_one_of_his_annotated_responses`
        # excludes. If one of these is ever actually his writing, this is where
        # it surfaces -- which a silent `continue` would never have allowed.
        "annotations_excluded_as_not_his": excluded_count,
        "excluded_files": sorted(excluded, key=lambda r: -r["annotations"]),
    }


def binaries_wearing_a_text_extension() -> list:
    """Files the allow list would have accepted and `is_binary_file` excluded.

    A SILENT SKIP IS THE DEFECT THIS MODULE EXISTS TO PREVENT, so an exclusion
    decided by content is reported by name, with its size and signature. If one
    of these is actually his writing, this list is where that shows up.
    """
    out = []
    for p in sorted(RESPONSES.glob("*")):
        if not is_a_response_file(p):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if p.name in NOT_HIS_ANNOTATIONS:
            continue
        if not is_binary_file(p):
            continue
        try:
            head = p.open("rb").read(8)
            size = p.stat().st_size
        except OSError:
            head, size = b"", -1
        out.append({"file": p.name, "bytes": size,
                    "signature": head.hex(), "why": "binary, not text"})
    return out


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


def context_for(ann: dict, before: int = 6, after: int = 1) -> list[str]:
    """The report lines an annotation ATTACHES TO. Added 2026-11-02.

    HIS COMPLAINT, 2026-11-02, verbatim: *"And this thing about you not fully
    reading my annotations, or the subjects they attach to remains both
    frustrating and weird. Why are you not doing this?"*

    THE ANSWER IS MECHANICAL AND IT IS THIS FUNCTION'S ABSENCE. Every annotation
    record has carried `line_index` since this reader was written on 2026-10-11 --
    the exact line of the report it was written against -- and nothing ever read
    the lines around it. The JSON mode emitted the annotation TEXT with no
    surroundings, and the plain mode emitted only COUNTS BY FILE, so neither
    output could answer "what is he talking about". An annotation reading "Has
    this now been done?" is unresolvable without the line above it, and 4 such
    were reported to him as needing their context before this existed.

    SO THE DEFECT WAS NOT INATTENTION. The subject was one field away and no
    code path fetched it. That is the same shape as the other 2 failures found
    this session: the decision was available and the delivery was absent.

    CONTEXT IS THE DEFAULT, NOT A FLAG. A flag that must be remembered is the
    same failure mode as a notification channel that must be armed by hand --
    which is precisely what cost 4 h 31 min on 2026-11-02. `--context 0` turns
    it off for callers that genuinely want the old output.
    """
    f = RESPONSES / str(ann.get("file") or "")
    i = ann.get("line_index")
    if not f.is_file() or not isinstance(i, int):
        return []
    try:
        # `lines_of`, NOT `read_any(...).splitlines()`: the SPLIT was 94% of the
        # cost once the decode was cached. See `lines_of`.
        #
        # `read_any` underneath, NOT a plain read_text. These files include .docx and
        # .zip-backed formats that grep treats as binary -- 908 of 1,174 of his
        # annotations live in files a naive reader cannot see, which is the
        # whole reason this script exists. A first draft of this function
        # called a `_read_any` that DOES NOT EXIST in this module; it parsed
        # fine and would have returned [] for every annotation, i.e. silently
        # restored the exact defect it was written to fix.
        lines = lines_of(f)
    except Exception:                                        # noqa: BLE001
        return []
    if not lines:
        return []
    lo = max(0, i - before)
    hi = min(len(lines), i + 1 + after)
    out = []
    for j in range(lo, hi):
        mark = ">>" if j == i else "  "
        out.append(f"{mark} {j:>5}  {str(lines[j]).rstrip()}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", metavar="YYYY-MM-DD")
    ap.add_argument("--until", metavar="YYYY-MM-DD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="exit 3 if a file looks annotated but cannot be read")
    ap.add_argument("--context", type=int, default=6, metavar="N",
                    help="report lines of CONTEXT to show above each annotation, "
                         "so the subject it attaches to is visible (default 6; "
                         "0 restores the old counts-only output)")
    #: ★ THE DEFAULT WAS INVERTED 2026-11-06, ON HIS OBSERVATION THAT I WAS
    #: READING HIS ANNOTATIONS WITHOUT THE TEXT THEY ANSWERED. He was right and
    #: the cause was this default, not any single turn: printing the annotations
    #: with their context was opt-in, so the reader's default output was a tally
    #: of counts carrying none of his words. Measured over 1 session: 572
    #: invocations, 12 passing `--text`, 0.020979, Wilson [0.012041, 0.036308].
    #:
    #: `--text` IS RETAINED AND ACCEPTED, deliberately. It now names the
    #: default rather than requesting it, so every recorded command and every
    #: test that passes it keeps working. Removing it would break callers to no
    #: purpose, and `additive-standard` forbids removing a feature when nothing
    #: replaces it.
    ap.add_argument("--counts", action="store_true",
                    help="print ONLY the per-file tally, without the "
                         "annotations. This was the default until 2026-11-06 "
                         "and is now opt-in.")
    ap.add_argument("--text", action="store_true",
                    help="accepted and no longer needed: printing every "
                         "annotation with its context is the default. Retained "
                         "so existing callers do not break.")
    args = ap.parse_args()

    if not RESPONSES.is_dir():
        print(f"  the responses folder is not present: {RESPONSES}", file=sys.stderr)
        return 0 if not args.verify else 3

    since = _dt.date.fromisoformat(args.since) if args.since else None
    until = _dt.date.fromisoformat(args.until) if args.until else None
    anns = annotations(since, until)
    shape = claim_a_naive_grep_is_blind_to_some_of_them()
    gaps = unreadable_but_annotated()
    binaries = binaries_wearing_a_text_extension()

    if args.json:
        if args.context > 0:
            for a in anns:
                a["context"] = context_for(a, before=args.context)
        print(json.dumps({"annotations": anns, "coverage": shape, "reader_gaps": gaps,
                          "excluded_binaries": binaries},
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
        #: CONTENT BY DEFAULT. `--counts` is the only way to get the old
        #: tally-only output, and `--text` is accepted as a no-op.
        if not args.counts:
            print("\n== every annotation, with the report lines it attaches to ==")
            for k, a in enumerate(anns, 1):
                print(f"\n--- [{k}] {a['file']} line {a.get('line_index')} "
                      f"marker={a.get('marker') or '(none)'} ---")
                for ln in context_for(a, before=args.context):
                    print(f"   {ln}")
                print(f"   HIS WORDS: {a['text']}")
        print("\n== why a naive grep is not enough ==")
        for k, v in shape.items():
            print(f"   {k}: {v}")
        print("\n== reader gaps (the guard condition) ==")
        print(f"   {len(gaps)} file(s) look annotated but cannot be read")
        for g in gaps:
            print(f"     {g}")
        print("\n== excluded for being BINARY, not text (a loud skip) ==")
        print(f"   {len(binaries)} file(s) wear a text extension but are not text")
        for b in binaries:
            print(f"     {b['file']}  {b['bytes']:,} bytes  sig={b['signature']}")

    if args.verify and gaps:
        print(f"\nREFUSED: {len(gaps)} response file(s) carry an annotation marker in their raw "
              f"bytes but read as unannotated. A silent miss here is how 221 of the founder's "
              f"verdicts went unread for 11 days.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
