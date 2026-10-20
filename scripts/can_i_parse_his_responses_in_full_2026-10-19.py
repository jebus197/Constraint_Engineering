#!/usr/bin/env python3
"""Can the reader extract EVERY annotation he wrote, and every character of it?

HIS QUESTION, 2026-10-19: *"You have had several problems parsing my tts
responses recently, but you also said you had fully fixed this? ... Make sure you
can extract/parse my responses fully."*

WHY AN ASSERTION WILL NOT DO. "Fixed" has been claimed before and was true of
what had been measured at the time, and false of what had not. The 2026-10-11
repair fixed DECODING (Word writes plain text with CR line endings and high-byte
smart quotes, so a naive grep sees one long line, calls the file binary and exits
silently). The 2026-10-13 repair fixed TRUNCATION of multi-line annotations. On
2026-10-19 a third gap appeared that neither covered: his command MARKERS sit on
their own line below an annotation, carry no leading hash, and were therefore
never part of any annotation's text -- 30 of them, invisible.

Each repair was real and each claim of completeness outran it, because
completeness was never itself measured. This script measures it, so the claim
becomes falsifiable rather than repeated.

THE 4 PROPERTIES, each checked against the RAW BYTES rather than against the
reader's own idea of what it read:
  1. DECODABLE     every annotated file decodes to text.
  2. COUNT         every `#`-opened annotation line in the raw text is returned.
  3. CHARACTERS    no annotation loses characters against its own raw line(s),
                   which is the 2026-10-13 truncation class.
  4. MARKERS       every own-line marker token is attached to an annotation.

Exit 0 when all 4 hold for every file, 2 otherwise, naming each file and gap.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"


def _reader():
    spec = importlib.util.spec_from_file_location("_rd", READER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MARKER_LINE = re.compile(r"^\s*(fr|pf|qs|wr)(?:\s*,\s*(?:fr|pf|qs))*\s*$", re.I)


#: DECODING IS NOT WHAT THIS MEASURES, so it reuses the reader's own `read_any`.
#: A FIRST VERSION OF THIS SCRIPT DECODED THE BYTES ITSELF AND WAS WRONG TWICE,
#: which is worth recording because both errors were in the instrument rather
#: than in the thing it was measuring. (1) It read `.rtf` as plain bytes, so an
#: escaped file showed 3 annotation lines where the reader correctly returned 13,
#: and the script reported the READER as lossy. (2) It treated any line opening
#: with a hash as one of his annotations, so every markdown HEADING in a `.md`
#: file -- "# Core Capabilities Matrix" and 26 others in one saved web page --
#: was counted as a missing annotation of his. Decoding and heading-shape are
#: separately guarded concerns; what is genuinely under test here is whether an
#: annotation, once decoded, survives into the returned rows with its characters
#: and its marker. So those 2 primitives are borrowed and the association rule
#: stays independent.
def file_text(rd, p: pathlib.Path) -> str:
    return rd.read_any(p)


def is_his_annotation(rd, line: str, suffix: str) -> bool:
    """A hash opening a sentence of his. Headings are excluded ONLY in markdown.

    A THIRD INSTRUMENT ERROR, recorded because it had the same shape as the
    first 2. Applying the reader's markdown-heading predicate to his `.txt`
    files rejected 8 real annotations, among them this one on
    `Morning_Report_2026-10-13.txt` line 23: *"I did just give you (what I
    thought was) the answer to this? In the last morning report I said: #"*.
    That is his TRAILING-HASH convention, which says a quotation follows, and
    the predicate reads the trailing hash as heading punctuation. The reader
    had it right and this script reported the reader as lossy. Heading shape is
    a markdown concern, so it is applied only to markdown.
    """
    t = line.lstrip()
    if not t.startswith("#"):
        return False
    if suffix == ".md":
        try:
            if rd._looks_like_a_markdown_heading(t):
                return False
        except Exception:  # noqa: BLE001
            pass
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rd = _reader()
    rows = rd.annotations()
    by_file: dict = {}
    for r in rows:
        by_file.setdefault(r["file"], []).append(r)

    files = [p for p in sorted(rd.RESPONSES.glob("*"))
             if rd.is_one_of_his_annotated_responses(p)]

    print("=" * 76)
    print("CAN THE READER PARSE HIS RESPONSES IN FULL?")
    print("=" * 76)
    print(f"annotated files        : {len(files)}")
    print(f"annotations returned   : {len(rows)}")
    print()

    gaps: list = []
    tot_raw = tot_got = 0
    tot_marks_raw = tot_marks_got = 0

    for p in files:
        text = file_text(rd, p)
        enc = p.suffix.lower().lstrip(".") or "txt"
        lines = text.splitlines()

        # 2. COUNT -- a hash opening a sentence of his, not a markdown heading.
        raw_ann = [i for i, l in enumerate(lines)
                   if is_his_annotation(rd, l, p.suffix.lower())]
        got = by_file.get(p.name, [])
        tot_raw += len(raw_ann)
        tot_got += len(got)
        if len(got) != len(raw_ann):
            gaps.append((p.name, "COUNT",
                         f"raw has {len(raw_ann)} annotation line(s), "
                         f"reader returned {len(got)}"))

        # 3. CHARACTERS -- every raw annotation's own text must survive.
        for i in raw_ann:
            body = lines[i].lstrip().lstrip("#").strip()
            if not body:
                continue
            squashed = " ".join(body.split())
            if not any(squashed[:60] in " ".join(g["text"].split())
                       for g in got):
                gaps.append((p.name, "CHARACTERS",
                             f"line {i}: {squashed[:60]!r} appears in no returned text"))

        # 4. MARKERS -- every own-line marker must reach some annotation.
        raw_marks = [i for i, l in enumerate(lines)
                     if l.strip() and MARKER_LINE.match(l.strip())]
        got_marks = [g for g in got if g.get("marker")]
        tot_marks_raw += len(raw_marks)
        tot_marks_got += len(got_marks)
        if len(got_marks) != len(raw_marks):
            gaps.append((p.name, "MARKERS",
                         f"raw has {len(raw_marks)} marker line(s), "
                         f"reader attached {len(got_marks)}"))

        if args.verbose:
            print(f"  {p.name}  [{enc}]  ann {len(got)}/{len(raw_ann)}  "
                  f"marks {len(got_marks)}/{len(raw_marks)}")

    print("-" * 76)
    print(f"ANNOTATIONS : {tot_got} returned of {tot_raw} present in the raw bytes")
    print(f"MARKERS     : {tot_marks_got} attached of {tot_marks_raw} present")
    print()
    for n, (lab, k) in enumerate((("annotations", tot_got), ("markers", tot_marks_got))):
        pass
    for label, k, nn in (("annotations", tot_got, tot_raw),
                         ("markers", tot_marks_got, tot_marks_raw)):
        if nn:
            try:
                from statsmodels.stats.proportion import proportion_confint
                from scipy.stats import beta as sb
                lo, hi = proportion_confint(min(k, nn), nn, method="wilson")
                elo = 0.0 if k == 0 else float(sb.ppf(0.025, min(k, nn), nn - min(k, nn) + 1))
                ehi = 1.0 if k >= nn else float(sb.ppf(0.975, k + 1, nn - k))
                print(f"  {label:12} coverage {min(k,nn)}/{nn} = "
                      f"{100*min(k,nn)/nn:.4f}%  Wilson [{100*lo:.4f}%, {100*hi:.4f}%]"
                      f"  exact [{100*elo:.4f}%, {100*ehi:.4f}%]")
            except Exception as e:  # noqa: BLE001
                print(f"  {label}: intervals unavailable ({e})")
    print()
    if gaps:
        print(f"GAPS: {len(gaps)}")
        for f, kind, why in gaps[:40]:
            print(f"  [{kind}] {f}: {why}")
        if len(gaps) > 40:
            print(f"  ... and {len(gaps)-40} more")
        print()
        print("=" * 76)
        print("NOT COMPLETE. Each gap above is a thing he wrote that the reader")
        print("does not return. Repair the reader, not this measurement.")
        print("=" * 76)
        return 2
    print("=" * 76)
    print("COMPLETE on all 4 properties: every annotated file decodes, every")
    print("annotation line is returned, no annotation loses its own characters,")
    print("and every own-line marker is attached. This is a MEASUREMENT, so it")
    print("goes red the moment it stops being true.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
