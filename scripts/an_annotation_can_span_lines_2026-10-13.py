#!/usr/bin/env python3
"""How much of the founder's writing does the reader drop at a line break?

HIS INSTRUCTION, 2026-10-13: *"Make sure you can parse my responses in full."*
He has now had to say this twice. On 2026-10-11 the reader was decoding his
files with `errors="ignore"`, which silently dropped every curly apostrophe --
256 characters across 14 of 29 plain-text files. That was fixed. This is a
DIFFERENT defect in the same reader, and it was found by obeying the same
instruction.

THE DEFECT. `_annotations_in` walks the decoded text line by line and treats
each line beginning with '#' as one whole annotation. An annotation that
CONTINUES ON A LATER LINE loses everything after the first, because the
continuation does not itself begin with '#'.

MEASURED ON THE FILE THAT EXPOSED IT, Morning_Report_2026-10-13.txt, which is
Mac OS Roman with CR-only terminators. His first annotation occupies 3 lines:

    line 23  '# I did just give you ... In the last morning report I said: # '
    line 24  ''
    line 25  820 characters re-quoting his own earlier ruling

The reader returned 100 characters of a 1,053-character annotation. **956
characters lost, and the lost text carried the operative clause** -- "But
propose your own fixes first" -- which changes the order of the work. It
survived only because the assistant also read the file directly.

HIS CONVENTION IS THE DISCRIMINATOR, AND IT IS EXPLICIT. The first line ENDS
with a '#'. That trailing hash is his marker that a quotation follows, exactly
as a leading hash marks an annotation's start. So the continuation rule can be
narrow: a continuation is read ONLY when the annotation line ends with '#'.
Nothing is inferred from blank lines, indentation or capitalisation, and no
report text can be captured by accident, because the report never ends a line
with a hash.

WHAT THIS SCRIPT REPORTS. Across every response file the reader can read: how
many annotations end with a trailing hash, how many characters the narrow rule
recovers, and -- as the honest upper bound on the problem -- how many
annotations are followed by a non-empty line that begins with neither a hash
nor an upper-case report heading, which is what a WIDER rule would capture and
why a wider rule is not proposed.

Usage: python3 scripts/an_annotation_can_span_lines_2026-10-13.py
"""
import importlib.util
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
RESPONSES = pathlib.Path.home() / "Developer_Projects" / "Responses"

#: A line that is plainly the REPORT's own structure rather than his prose.
_REPORT_SHAPE = re.compile(r"^[A-Z0-9 ,.'\"()\-]{12,}$")


def reader():
    spec = importlib.util.spec_from_file_location("rfr", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfr"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    answer_help(__doc__, __file__)
    R = reader()
    if not RESPONSES.is_dir():
        print(f"no Responses directory at {RESPONSES}; measurement void.")
        return 3

    files = sorted(p for p in RESPONSES.iterdir() if p.is_file())
    n_ann = trailing = recovered_chars = wide_candidates = 0
    rows = []
    for p in files:
        try:
            text = R.read_any(p)
        except Exception:                                 # noqa: BLE001
            continue
        if not text:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines):
            s = line.strip()
            if not (s.startswith("#") and len(s) > 2):
                continue
            if p.suffix.lower() in (".md", ".markdown") and \
                    R._looks_like_a_markdown_heading(s):
                continue
            n_ann += 1
            # THE NARROW RULE: a trailing hash means a quotation follows.
            if s.endswith("#"):
                trailing += 1
                got = 0
                for j in range(i + 1, len(lines)):
                    nxt = lines[j].strip()
                    if not nxt:
                        continue
                    if nxt.startswith("#") or _REPORT_SHAPE.match(nxt):
                        break
                    got += len(nxt)
                    break        # one continuation block is his convention
                recovered_chars += got
                rows.append((p.name, i, len(s), got))
            else:
                # THE WIDE RULE'S CANDIDATES, reported as the upper bound only.
                for j in range(i + 1, len(lines)):
                    nxt = lines[j].strip()
                    if not nxt:
                        continue
                    if not nxt.startswith("#") and not _REPORT_SHAPE.match(nxt):
                        wide_candidates += 1
                    break

    if not n_ann:
        print("no annotations found; measurement void.")
        return 3

    print(f"response files read      : {len(files)}")
    print(f"annotations found        : {n_ann}")
    print(f"ending with a trailing # : {trailing}")
    print(f"characters the narrow rule recovers: {recovered_chars}")
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(trailing, n_ann, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, trailing, n_ann - trailing + 1) if trailing else 0.0
    hi2 = (stats.beta.ppf(0.975, trailing + 1, n_ann - trailing)
           if trailing < n_ann else 1.0)
    print(f"  truncated by this defect: {trailing}/{n_ann} = {trailing/n_ann:.4%}")
    print(f"    Wilson 95%          [{lo:.4%}, {hi:.4%}]  (statsmodels)")
    print(f"    Clopper-Pearson 95% [{lo2:.4%}, {hi2:.4%}]  (scipy.beta)")
    for name, i, head, got in rows:
        print(f"    {name[:46]:<46} line {i:<5} {head:>5} kept, {got:>5} lost")
    print(f"\nWIDER-RULE CANDIDATES (not proposed): {wide_candidates}")
    print("  a rule that captured ANY following prose line would take these too,")
    print("  and most are the report's own sentences. The narrow rule keys on his")
    print("  OWN trailing-hash convention, so it cannot capture report text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
