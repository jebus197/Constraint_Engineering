#!/usr/bin/env python3
"""Print the text a founder annotation was attached to, so a question can be answered.

WHY THIS EXISTS. `scripts/read_founder_responses_2026-10-11.py` returns his
annotations and their anchors; it does not return what he was annotating. Several
of his questions are unanswerable without that context -- *"What is the
significance of this?"*, *"What ruling do you expect from me?"* -- because the
subject is in MY text above the `#`, not in his words. 11 of his questions were
outstanding on 2026-10-29 and 5 of them are of exactly this shape.

IT REUSES THE READER'S OWN DECODER rather than carrying a second one. 41 of 107
response files are not valid UTF-8 and 40 are CR-only, so a naive read sees
nothing: 820 of his 1,086 annotations live in files a naive grep treats as
binary. A second decoder would be a second description of 1 rule, which is the
defect shape this project has measured most often.

READ-ONLY.
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
    spec = importlib.util.spec_from_file_location("founder_reader", READER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["founder_reader"] = mod
    spec.loader.exec_module(mod)
    return mod


def context_for(filename: str, needle: str, before: int = 14,
                after: int = 2, ordinal: int = 0) -> list[str]:
    """The lines around the annotation whose text contains `needle`.

    ★ `ordinal` SELECTS WHICH OCCURRENCE, and ignoring it was a defect, found
    2026-10-29. He writes the same sentence more than once: "I accept your
    recommendation. fr" appears TWICE in `Decisions_Awaiting_You_2026-10-29.txt`,
    approving 2 DIFFERENT recommendations. The 2 annotations are distinguished
    only by the trailing ordinal of their anchor (`...#0`, `...#1`), and this
    tool read `anchor.split("#")[0]` -- the filename -- and threw the ordinal
    away, so it returned the FIRST occurrence's context for both and reported
    one approval's subject as the other's. That produced a wrong classification
    of what work was outstanding before it was caught.
    """
    r = _reader()
    path = r.RESPONSES / filename
    if not path.is_file():
        return [f"(no such response file: {path})"]
    text = r.read_any(path)
    #: ★ NORMALISE THE LINE ENDINGS BEFORE SPLITTING, and the first version of
    #: this tool did not. 40 of 107 response files are CR-ONLY, so splitting on
    #: "\n" returns the WHOLE FILE as 1 line and the search always "finds" the
    #: annotation at line 0 with the document's opening paragraph as its
    #: context. That is the identical blindness the reader module exists to
    #: prevent, reproduced inside a tool written to consume the reader -- which
    #: is why it is recorded here rather than silently corrected.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    key = " ".join(needle.split())[:60].lower()
    hits = [i for i, ln in enumerate(lines)
            if key and key in " ".join(ln.split()).lower()]
    if hits:
        if ordinal >= len(hits):
            return [f"(anchor names occurrence {ordinal} but only {len(hits)} "
                    f"match(es) of {key!r} exist in {filename}; the anchor and "
                    f"the file disagree, which is itself a finding)"]
        for i in [hits[ordinal]]:
            lo = max(0, i - before)
            hi = min(len(lines), i + after + 1)
            out = []
            for j in range(lo, hi):
                mark = ">>" if j == i else "  "
                out.append(f"{mark} {lines[j][:400]}")
            return out
    return [f"(annotation not located in {filename}; "
            f"searched for {key!r} across {len(lines)} line(s))"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tid", action="append", default=[],
                    help="a ticket id whose anchor names the file and whose "
                         "verbatim locates the annotation; repeatable")
    ap.add_argument("--before", type=int, default=14)
    ap.add_argument("--after", type=int, default=2)
    args = ap.parse_args()

    sys.path.insert(0, str(REPO))
    from bench.ticket_store import TicketStore
    store = TicketStore()
    store.load()

    if not args.tid:
        ap.error("give at least one --tid")
    for tid in args.tid:
        t = store.get(tid)
        if t is None:
            print(f"=== {tid}: no such ticket")
            continue
        _parts = (t.anchor or "").split("#")
        fname = _parts[0]
        #: the anchor is file#contenthash#ordinal; the ordinal is what tells 2
        #: identical annotations apart, so it is read rather than discarded.
        try:
            _ord = int(_parts[2]) if len(_parts) > 2 else 0
        except ValueError:
            _ord = 0
        print(f"=== {t.kind}:{t.tid}  file={fname or '(none)'}")
        print(f"    HIS WORDS: {' '.join((t.verbatim or '').split())[:300]}")
        print("    --- what he was annotating ---")
        for ln in context_for(fname, t.verbatim or "", args.before, args.after,
                              ordinal=_ord):
            print("   ", ln)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
