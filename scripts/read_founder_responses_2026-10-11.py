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


def is_a_response_file(path: Path) -> bool:
    """One predicate, three call sites, so they cannot drift apart.

    EXCLUDES dotfiles. `Path.glob("*")` returns them where shell globbing does not, and
    `.DS_Store` contains a `#` byte, so it was reported as a reader gap on the first run --
    a false positive of exactly the `check the predicate before the result` shape. It also
    excludes Word's `~$` lock files, which carry no content.
    """
    return (path.is_file()
            and not path.name.startswith("~$")
            and not path.name.startswith("."))


#: `#`, 1 to 6 of them, then a space, then a short title-case-ish phrase and no sentence
#: punctuation. That is a heading. His annotations are conversational prose, usually long,
#: and frequently begin without a space after the hash.
_MD_HEADING = re.compile(r"^#{1,6}\s+\S")


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
        return path.read_bytes().decode("utf-8", errors="ignore")
    except Exception:
        return ""


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


def annotations(since: _dt.date | None = None, until: _dt.date | None = None) -> list:
    """Every `#`-prefixed annotation the founder wrote, with its file and date."""
    out = []
    for p in sorted(RESPONSES.glob("*")):
        if not is_a_response_file(p):
            continue
        d = _dt.date.fromtimestamp(p.stat().st_mtime)
        if since and d < since:
            continue
        if until and d > until:
            continue
        out.extend(_annotations_in(p, d))
    return out


def _annotations_in(p: Path, d: _dt.date | None = None) -> list:
    """Every annotation in ONE file. The single definition of what counts as one."""
    out = []
    if d is None:
        d = _dt.date.fromtimestamp(p.stat().st_mtime)
    text = read_any(p)
    if text:
        for i, line in enumerate(text.splitlines()):
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
            out.append({"file": p.name, "ext": p.suffix.lower(), "date": d.isoformat(),
                        "line_index": i, "text": s.lstrip("# ").strip()})
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
        if ext not in TEXTISH | RICH | ZIPPED:
            bad.append({"file": p.name, "ext": ext,
                        "why": "extension unknown to this reader, and its bytes contain '#'",
                        "bytes": len(raw)})
    return bad


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
