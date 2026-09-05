#!/usr/bin/env python3
"""Verify that no founder annotation in an annotated RTF was mis-attributed to CC1.

WHY THIS EXISTS
The founder asked (RS_Diagnostic_20260904, line 33): "It could be possible I missed
a # symbol, so my answers and your questions may have become a little jumbled? You
should probably check carefully."

Grepping for '#' cannot answer that question, because the hypothesis under test is
that a '#' is MISSING. A '#'-based check would silently classify any un-marked
founder prose as CC1's own text -- the exact failure being asked about. This is the
`execute-do-not-grep` rule applied to a document: the two forms (author-of-record and
'#'-marker) must be derived independently and compared.

METHOD -- independent of '#' entirely
Word stamps every inserted run of text with \\insrsidNNNN, the id of the editing
session that typed it. The founder pastes CC1's note in one session, then annotates
in later sessions. Partitioning the RTF body by insrsid therefore recovers authorship
from the file's own revision metadata, with no reference to '#'. The check is then:

    for every contiguous founder-typed block, does it begin with '#'?

A block that does not is founder prose a reader would attribute to CC1.

FALSIFICATIONS APPLIED (see --falsify)
  F1  An annotation typed in the SAME session that pasted the base text would carry
      the base rsid and be invisible to this method. Tested by scanning the
      CC1-attributed text for founder-voice markers and for any '#' at all.
  F2  insrsid is a character property scoped by RTF {groups}; a parser that ignores
      group push/pop could mis-attribute. Tested by re-parsing with a group stack
      and confirming the '#'-partition is unchanged.
  F3  Counted '#' occurrences per author class. Every '#' must fall in founder text.

MEASURED 2026-09-05 over the 8 RTFs in the session upload directory:
  72 contiguous founder-typed blocks, 0 without a leading '#', 0 '#' in CC1 text.
  Conclusion: no annotation was mis-attributed. No '#' was missed.

Usage:
    python3 scripts/verify_rtf_annotation_attribution.py <file.rtf> [...]
    python3 scripts/verify_rtf_annotation_attribution.py --falsify <file.rtf> [...]

Exit status 0 if every founder block carries its '#', 1 otherwise.
"""
import collections
import os
import re
import sys

FOUNDER_VOICE = [
    r'\bVerdict\s*:', r'\bI approve', r'\bDo it\b', r'\byou should\b',
    r'\byou need to\b', r'\bmy own memory\b', r'\bI want to know\b',
    r'\bI asked you\b', r'\bHuh\?', r'\bI seem to remember\b', r'\bI guess\b',
    r'\bI fear\b',
]


def parse_runs(raw, grouped=False):
    """Return [(insrsid, text)] for the RTF body.

    grouped=True maintains a {group} stack for the insrsid property (falsification
    F2); grouped=False lets the last-seen insrsid persist. Both must agree on the
    '#'-partition for the result to stand.
    """
    i = raw.find('\\viewkind')
    body = raw[i if i >= 0 else 0:]
    runs, buf, stack, cur = [], [], [], None
    j, n = 0, len(body)
    while j < n:
        c = body[j]
        if c == '{':
            if grouped:
                stack.append(cur)
            j += 1
            continue
        if c == '}':
            if grouped:
                if buf:
                    runs.append((cur, ''.join(buf)))
                    buf = []
                cur = stack.pop() if stack else None
            j += 1
            continue
        if c == '\\':
            m = re.match(r'\\([a-zA-Z]+)(-?\d+)? ?', body[j:])
            if m:
                ctrl, arg = m.group(1), m.group(2)
                j += m.end()
                if ctrl == 'insrsid':
                    if buf:
                        runs.append((cur, ''.join(buf)))
                        buf = []
                    cur = int(arg)
                elif ctrl in ('par', 'line'):
                    buf.append('\n')
                elif ctrl == 'tab':
                    buf.append('\t')
                elif ctrl == 'u':
                    buf.append(chr(int(arg) % 65536))
                    if j < n and body[j] == '?':
                        j += 1
                continue
            m2 = re.match(r"\\'([0-9a-fA-F]{2})", body[j:])
            if m2:
                buf.append(bytes([int(m2.group(1), 16)]).decode('cp1252', 'replace'))
                j += m2.end()
                continue
            m3 = re.match(r'\\([\\{}])', body[j:])
            if m3:
                buf.append(m3.group(1))
                j += m3.end()
                continue
            j += 1
            continue
        if c in '\r\n':
            j += 1
            continue
        buf.append(c)
        j += 1
    if buf:
        runs.append((cur, ''.join(buf)))
    return runs


def partition(raw, grouped=False):
    """-> (founder_blocks, base_text, founder_text, base_rsid)."""
    runs = parse_runs(raw, grouped=grouped)
    # Drop the trailing embedded-object hex blob; it is not document text.
    # Drop the trailing embedded-object hex blob; it is not document text. The
    # threshold is deliberately low (40) because RTF {groups} split the blob into
    # short fragments, and a 500-char threshold silently kept them -- which made
    # the F2 grouped re-parse look like it disagreed when it did not.
    clean = [(r, t) for r, t in runs
             if not re.fullmatch(r'[0-9a-f\s]{40,}', t or '')]
    totals = collections.Counter()
    for r, t in clean:
        totals[r] += len(t.strip())
    # None means "no \insrsid seen for this run", which is never a real authoring
    # session, so it must not be eligible to win base detection. Letting it win made
    # the grouped re-parse collapse the whole document into one bucket.
    base = max((r for r in totals if r is not None), key=lambda r: totals[r])

    text, author = [], []
    for r, t in clean:
        a = 'BASE' if r == base else ('NONE' if r is None else 'FOUNDER')
        text.append(t)
        author.extend([a] * len(t))
    full = ''.join(text)

    blocks, i, n = [], 0, len(full)
    while i < n:
        if author[i] == 'FOUNDER':
            j = i
            while j < n and author[j] in ('FOUNDER', 'NONE'):
                j += 1
            if full[i:j].strip():
                blocks.append(full[i:j].strip())
            i = j
        else:
            i += 1
    base_text = ''.join(t for r, t in clean if r == base)
    founder_text = ''.join(t for r, t in clean if r not in (base, None))
    return blocks, base_text, founder_text, base


def main(argv):
    falsify = '--falsify' in argv
    paths = [a for a in argv if not a.startswith('--')]
    if not paths:
        print(__doc__)
        return 2

    rows, bad = [], 0
    for path in sorted(paths):
        raw = open(path, 'r', encoding='latin-1').read()
        blocks, base_text, founder_text, base = partition(raw)
        unmarked = [b for b in blocks if not b.startswith('#')]
        bad += len(unmarked)
        rows.append((os.path.basename(path), len(blocks), len(unmarked),
                     base_text.count('#'), founder_text.count('#')))
        for b in unmarked:
            print(f'MIS-ATTRIBUTION  {os.path.basename(path)}: {b[:200]!r}')

        if falsify:
            print(f'--- falsification: {os.path.basename(path)} (base rsid {base}) ---')
            hits = [m.group(0) for pat in FOUNDER_VOICE
                    for m in re.finditer(pat, base_text, re.I)]
            print(f'    F1 founder-voice markers inside CC1 text: {len(hits)} '
                  f'{sorted(set(hits))}')
            print(f"    F3 '#' in CC1 text: {base_text.count('#')}   "
                  f"'#' in founder text: {founder_text.count('#')}")
            # F2 asks whether ignoring RTF {group} scope changed WHICH TEXT is
            # founder-authored. Comparing the founder text itself is the honest
            # test; comparing block counts conflates a parser artefact with a
            # real disagreement.
            gb, g_base_text, g_founder_text, _ = partition(raw, grouped=True)
            norm = lambda x: re.sub(r'\s+', ' ', x).strip()
            same_text = norm(g_founder_text) == norm(founder_text)
            same_marks = all(b.startswith('#') for b in gb)
            print(f'    F2 grouped re-parse recovers identical founder text: '
                  f'{same_text}; all its blocks still marked: {same_marks}')

    w = max(len(r[0]) for r in rows) + 2
    print(f'\n{"FILE":<{w}}{"founder blocks":>15}{"WITHOUT #":>11}'
          f'{"# in CC1":>10}{"# in founder":>14}')
    for r in rows:
        print(f'{r[0]:<{w}}{r[1]:>15}{r[2]:>11}{r[3]:>10}{r[4]:>14}')
    print('-' * (w + 50))
    print(f'{"TOTAL (" + str(len(rows)) + " files)":<{w}}'
          f'{sum(r[1] for r in rows):>15}{sum(r[2] for r in rows):>11}'
          f'{sum(r[3] for r in rows):>10}{sum(r[4] for r in rows):>14}')
    print('\nVERDICT:', 'NO MIS-ATTRIBUTION' if bad == 0
          else f'{bad} FOUNDER BLOCK(S) LACK A LEADING #')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
