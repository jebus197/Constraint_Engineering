#!/usr/bin/env python3
"""Task 7.1, BOUNDED SLICE: turn spelled quantities in the notes back into digits.

Founder ruling `no-word-numbers`, 2026-09-04, restated after repeated violation:
*"Never write a number in word form. Digits only, in every context without
exception."* Task 7.1's ruling gives the scope: *"Fix them all, or at least
those that a technical reader would be likely to find insufficient in the
interests of reproducibility."* A spelled quantity is squarely that -- "fifty
seven tests green" cannot be grepped, checked or compared; "57 tests green" can.

THE SCOPE IS SPLIT AT THE START, not at the debrief (`feedback_fix_all_scope_split`):

  BOUNDED, and this script does it   SPELLED NUMBER, 283 findings. Mechanically
                                     checkable: the linter names the token and
                                     the result is verifiable by re-linting.
  SPEC-ONLY, proposed not swept      UNNAMED SUBJECT, 558 findings. Naming the
                                     right subject needs per-instance judgement
                                     about what the sentence meant. A regex
                                     sweep here would be the mechanical rewrite
                                     `feedback_no_mechanical_tts` forbids.
  SWEEP LATER                        QUANTITY WITHOUT A VALUE, 296 findings.
                                     Mixed: some want a figure that exists, some
                                     want one nobody measured.

QUOTATIONS ARE SAFE BY CONSTRUCTION. Candidate sites come from the linter, whose
exemption masks double-quoted spans, so a verbatim quotation is never a
candidate. The founder's words are never edited by this script.

IT REFUSES WHAT IT CANNOT PARSE CLEANLY. "point seven one" is 0.71, not 71.
"Round-three five-panel review" is not a quantity at all. Those are reported for
a human rather than guessed at, because a wrong number is worse than a spelled
one -- it is a false figure that reads as a measurement.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "lint", REPO / "scripts" / "note_vagueness_lint.py")
LINT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LINT)

UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
         "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
         "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fourty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000}

#: Contexts in which a spelled word is NOT a plain integer, or is REQUIRED to
#: stay spelled, so the site is reported rather than converted.
#:
#: THE SCIENTIFIC-NOTATION CASE WAS A REAL ERROR, caught by reading the diff
#: after the first apply. Note standard Rule 11 REQUIRES the form
#: `1x10^N (number-words)`, so a sentence teaching that rule -- "verify
#: exponent-word correspondence before writing (10^7 = ten million)" -- has its
#: number-words as the SUBJECT of the sentence. Converting them broke the rule
#: the sentence exists to state. Reverted, and guarded here.
REFUSE_BEFORE = re.compile(
    r"(?:"
    r"\bpoint\s*$"                       # "point seven one" is 0.71, not 71
    r"|10\^\d+\s*=\s*$"                  # "10^7 = ten million" TEACHES the form
    r")", re.I)

#: Whole-SENTENCE contexts where number-words are the subject rather than a
#: quantity, so nothing in the sentence may be converted. Checked against the
#: full sentence because a prefix test cannot see past an abbreviation's full
#: stop: "use 1x10^N (number-words) format, e.g. 1x10^10 (ten billion)" ends its
#: prefix at "e.g." and the marker sits before that.
REFUSE_SENTENCE = re.compile(
    r"(?:number-words|exponent[-\s]?word|scientific notation)", re.I)


def parse_words(phrase: str):
    """Integer value of a spelled phrase, or None when it is not a clean one."""
    words = [w for w in re.split(r"[\s-]+", phrase.strip().lower()) if w and w != "and"]
    if not words:
        return None
    # REFUSE STACKED SCALES. "ten thousand million million" is 10^16, and a
    # left-to-right accumulator returns 2010000 for it -- a FALSE FIGURE, which
    # is worse than the spelled form it replaces because it reads as a
    # measurement. Caught on the first dry run over the corpus. A scale word
    # repeating, or scales not strictly decreasing, means the phrase is not the
    # simple "<units> <scale> <units> <scale>" shape this parser handles.
    # REFUSE TWO BARE UNITS IN A ROW. English has no "<unit> <unit>" numeral:
    # "twenty one" is tens-plus-unit and fine, "zero three" and "seven one" are
    # 2 separate words the linter happened to see side by side. Measured on the
    # corpus: "the location series reaches zero three times" would have become
    # "reaches 3 times", destroying the sentence, and "point seven one" is 0.71.
    raw = [w for w in re.split(r"[\s-]+", phrase.strip().lower()) if w]
    for a, b in zip(raw, raw[1:]):
        if a in UNITS and b in UNITS:
            return None

    # REFUSE "and" THAT IS NOT PART OF A SCALE. "one hundred and sixty five" is
    # 165; "between fifteen and twenty five thousand" is a RANGE and became
    # 40000, and "between one pound forty and two pounds thirty" is a price range
    # that became 42. Both were false figures, which is worse than the spelled
    # form because they read as measurements. "and" is only allowed immediately
    # after a scale word.
    for i, w in enumerate(raw):
        if w == "and" and (i == 0 or raw[i - 1] not in SCALES):
            return None

    scales_seen = [SCALES[w] for w in words if w in SCALES]
    if len(scales_seen) != len(set(scales_seen)):
        return None
    if any(a <= b for a, b in zip(scales_seen, scales_seen[1:])):
        return None
    total = current = 0
    seen = False
    for w in words:
        if w in UNITS:
            if current % 100 and current % 100 == current and seen and current < 20:
                return None            # "seven one": 2 bare units in a row
            current += UNITS[w]
        elif w in TENS:
            current += TENS[w]
        elif w in SCALES:
            if current == 0:
                current = 1
            if SCALES[w] == 100:
                current *= 100
            else:
                total += current * SCALES[w]
                current = 0
        else:
            return None
        seen = True
    return total + current


def sites(paths):
    """(path, token, sentence) for every spelled-number finding."""
    for p in paths:
        try:
            for f in LINT.lint(p):
                if "SPELLED" in str(f[1]):
                    yield p, str(f[2]), str(f[3])
        except Exception as exc:                       # pragma: no cover
            print(f"  ! {p.name}: {type(exc).__name__}: {exc}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write the changes; without it nothing is modified")
    ap.add_argument("paths", nargs="*", default=None)
    args = ap.parse_args()

    paths = ([pathlib.Path(p) for p in args.paths] if args.paths
             else sorted((REPO / "experimental_notes").rglob("*.md")))

    converted, refused, changed_files = [], [], {}
    for p, token, sentence in sites(paths):
        idx = sentence.lower().find(token.lower())
        before = sentence[:idx] if idx >= 0 else ""
        value = parse_words(token)
        if (value is None or REFUSE_BEFORE.search(before)
                or REFUSE_SENTENCE.search(sentence)):
            refused.append((p.name, token, sentence[:110]))
            continue
        converted.append((p.name, token, value, sentence[:96]))
        changed_files.setdefault(p, []).append((token, str(value), sentence))

    print(f"notes scanned          : {len(paths)}")
    print(f"spelled-number sites   : {len(converted) + len(refused)}")
    print(f"  convertible cleanly  : {len(converted)}")
    print(f"  REFUSED for a human  : {len(refused)}")

    if refused:
        SHOWN = 20
        print(f"\nREFUSED (reported, never guessed): {len(refused)} in total")
        for name, tok, s in refused[:SHOWN]:
            print(f"  {name[:48]:48s} {tok!r}")
            print(f"       {s}")
        if len(refused) > SHOWN:
            print(f"  ... and {len(refused) - SHOWN} more not listed; re-run "
                  f"with the paths you want to see in full")

    if not args.apply:
        print("\nDRY RUN. Nothing written. Re-run with --apply to write.")
        SHOWN = 12
        print(f"Sample of the conversions that would be made "
              f"({min(SHOWN, len(converted))} of {len(converted)}):")
        for name, tok, val, s in converted[:SHOWN]:
            print(f"  {name[:44]:44s} {tok!r} -> {val}")
        if len(converted) > SHOWN:
            print(f"  ... and {len(converted) - SHOWN} more not listed")
        return 0

    written, unlocated = 0, []
    for p, subs in changed_files.items():
        text = p.read_text(encoding="utf-8")
        original = text
        for tok, val, sentence in subs:
            # THE SITE IS LOCATED BY ITS SENTENCE, NOT BY THE FILE'S FIRST MATCH.
            # A first version substituted the first occurrence of the token
            # anywhere in the file. The same word can appear earlier inside a
            # VERBATIM QUOTATION -- which the linter exempted and which must
            # never be edited -- so the repair could have rewritten the founder's
            # words while reporting that it had fixed a note. Anchoring on the
            # flagged sentence removes the possibility rather than making it
            # unlikely.
            #
            # `sentences()` collapses whitespace, so the sentence is matched as a
            # whitespace-tolerant pattern against the original text.
            probe = r"\s+".join(re.escape(w) for w in sentence.split())
            m = re.search(probe, text)
            if not m:
                unlocated.append((p.name, tok, sentence[:80]))
                continue
            span = text[m.start():m.end()]
            fixed = re.sub(rf"\b{re.escape(tok)}\b", val, span, count=1,
                           flags=re.I)
            if fixed == span:
                unlocated.append((p.name, tok, sentence[:80]))
                continue
            text = text[:m.start()] + fixed + text[m.end():]
        if text != original:
            p.write_text(text, encoding="utf-8")
            written += 1
    print(f"\nwritten: {written} file(s)")
    if unlocated:
        SHOWN = 10
        print(f"NOT APPLIED, site could not be located exactly: {len(unlocated)}")
        for name, tok, s_ in unlocated[:SHOWN]:
            print(f"  {name[:44]:44s} {tok!r}  {s_}")
        if len(unlocated) > SHOWN:
            print(f"  ... and {len(unlocated) - SHOWN} more not listed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
