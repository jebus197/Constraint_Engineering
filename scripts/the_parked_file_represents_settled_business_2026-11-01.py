#!/usr/bin/env python3
"""PRODUCER for his `pf` of 2026-11-01 on the generated morning report.

HIS WORDS, verbatim: *"The vast majority of these have already been discussed
and ruled on. Please carefully reassess them all ... But you are again
presenting me just with ticket labels like B21, C0037, C0036, without giving any
meaningful indication what these are? This does not match the recently agreed
tts presentation standard for issues of this type. Please fix. pf"*

THIS SCRIPT ESTABLISHES WHAT IS TRUE BEFORE ANYTHING IS CHANGED, because his
claim is a quantitative one -- "the vast majority" -- and the project's own rule
is that a rate cited without a producer is a claim about evidence rather than
evidence. It also separates 3 faults that his single sentence names together,
since they have 3 different fixes:

  1. SETTLED BUSINESS REACHING HIM. `parked_items()` in
     `scripts/morning_report_build_2026-10-12.py` drops a heading only when it
     NAMES a task-list entry recorded DONE or WITHDRAWN. A heading that says in
     its OWN TEXT that it is resolved, superseded or closed has no rule at all,
     so it survives.
  2. REPETITION. Several task-list entries own MANY parked headings, so one
     subject is presented repeatedly as though it were several.
  3. BARE CODES. A heading that leads with an identifier and no description
     tells him nothing, which is Rule 19 of the note standard -- name the
     subject -- applied to this report.

WHAT THIS SCRIPT DOES NOT DO. It does not judge whether a question is
substantively settled. It measures what the DOCUMENTS say. Where a heading
declares its own closure that is the document's own word and is counted as
such; where it does not, the item is reported as still live, because absence of
a closure marker is not evidence of openness either and the residue is an UPPER
BOUND on what needs him.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

PARKED = REPO / "experimental_notes" / "PARKED_FOR_THE_FOUNDER.md"
FAILURES: list[str] = []

#: A heading that says, in its own words, that it is finished. Matched on the
#: HEADING only, never on the body, because a body may discuss a closure that
#: has not happened.
SELF_CLOSED = re.compile(
    r"\b(RESOLVED|SUPERSEDED|IS CLOSED|NOTHING LEFT TO RULE ON|"
    r"NOT A BLOCKER|NO LONGER|ALREADY (?:DONE|BUILT|FIXED))\b", re.I)

CODE = re.compile(r"\b([A-Z]{1,2}\d{1,4}[a-z]?)\b")


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_mp, hi_mp = float((c - h) / d), float((c + h) / d)
    _check("wilson cross-check", abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9,
           f"statsmodels ({lo_sm},{hi_sm}) vs mpmath ({lo_mp},{hi_mp})")
    return float(lo_sm), float(hi_sm)


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    import importlib.util

    def _load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m
        spec.loader.exec_module(m)
        return m

    gen = _load(REPO / "scripts" / "morning_report_build_2026-10-12.py", "mrb")

    all_heads = [l[3:].strip() for l in
                 PARKED.read_text(encoding="utf-8").splitlines()
                 if l.startswith("## ")]
    live = gen.parked_items()

    print("=" * 72)
    print("M1. HOW MANY HEADINGS, AND HOW MANY THE EXISTING FILTER DROPS")
    print("=" * 72)
    print(f"headings in the parked file : {len(all_heads)}")
    print(f"surviving the live filter   : {len(live)}")
    print(f"dropped by the live filter  : {len(all_heads) - len(live)}")
    _check("the filter does something", len(live) < len(all_heads),
           "the filter dropped nothing, so it is inert")

    print()
    print("=" * 72)
    print("M2. SETTLED BUSINESS THE FILTER CANNOT SEE")
    print("=" * 72)
    self_closed = [h for h in live if SELF_CLOSED.search(h)]
    lo, hi = wilson(len(self_closed), len(live))
    print(f"live headings that declare their OWN closure: {len(self_closed)} of "
          f"{len(live)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    for h in self_closed:
        word = SELF_CLOSED.search(h).group(0)
        print(f"   says {word!r}: {h[:110]}")
    print()
    print("The existing filter keys on the TASK LIST's marker, so a heading")
    print("whose own text says it is finished survives unless it also names a")
    print("closed entry. That is the mechanical cause of settled business")
    print("reaching him, and it is 1 predicate away from fixed.")
    _check("self-closed items exist", len(self_closed) >= 1,
           "none found -- this half of the finding would be withdrawn")

    print()
    print("=" * 72)
    print("M3. REPETITION: ONE SUBJECT PRESENTED MANY TIMES")
    print("=" * 72)
    owner = collections.Counter()
    for h in live:
        for c in sorted(set(CODE.findall(h))):
            owner[c] += 1
    repeated = {c: n for c, n in owner.items() if n > 1}
    print(f"entry codes owning more than 1 live heading: {len(repeated)}")
    for c, n in sorted(repeated.items(), key=lambda kv: -kv[1]):
        print(f"   {c}: {n} headings")
        for h in live:
            if c in set(CODE.findall(h)):
                print(f"      - {h[:100]}")
    collapsible = sum(n - 1 for n in repeated.values())
    lo, hi = wilson(collapsible, len(live))
    print()
    print(f"headings removable by collapsing to 1 per subject: {collapsible} of "
          f"{len(live)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    _check("repetition exists", len(repeated) >= 1,
           "no code owns 2 headings -- the repetition half would be withdrawn")

    print()
    print("=" * 72)
    print("M4. BARE CODES: HEADINGS THAT NAME AN IDENTIFIER AND LITTLE ELSE")
    print("=" * 72)
    # A heading is BARE when, after removing its codes and punctuation, fewer
    # than 6 words of description remain. 6 is a threshold and is stated as one.
    def _desc_words(h: str) -> int:
        stripped = CODE.sub(" ", h)
        return len(re.findall(r"[A-Za-z]{3,}", stripped))
    bare = [(h, _desc_words(h)) for h in live
            if CODE.search(h) and _desc_words(h) < 6]
    coded = [h for h in live if CODE.search(h)]
    print(f"live headings naming at least 1 code: {len(coded)} of {len(live)}")
    print(f"of those, carrying fewer than 6 descriptive words: {len(bare)}")
    for h, n in bare:
        print(f"   {n} descriptive word(s): {h}")
    if coded:
        lo, hi = wilson(len(bare), len(coded))
        print(f"   Wilson 95% [{lo:.6f}, {hi:.6f}] of coded headings")
    print()
    print("THE THRESHOLD IS A CHOICE AND IS REPORTED AS ONE. The point is not")
    print("the exact count but that his complaint names real items: a heading")
    print("reading `B21 three role-layer questions` tells a reader who does not")
    print("hold the project in their head nothing about what B21 is.")

    print()
    print("=" * 72)
    print("M5. DO THEY CARRY A KIND LABEL IN THE TICKET STORE?")
    print("=" * 72)
    # His diagnosis: most predate the store, so they have no kind. Checked
    # against the store's own rows by entry code.
    store = REPO / "bench" / "tickets" / "tickets.jsonl"
    seen_codes = collections.Counter()
    kinds_by_code = collections.defaultdict(set)
    if store.is_file():
        for line in store.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                row = json.loads(line)
            except Exception:
                continue
            ref = str(row.get("task_ref") or "")
            if ref:
                seen_codes[ref] += 1
                if row.get("kind"):
                    kinds_by_code[ref].add(row["kind"])
    live_codes = sorted({c for h in live for c in CODE.findall(h)})
    with_label = [c for c in live_codes if kinds_by_code.get(c)]
    without = [c for c in live_codes if not kinds_by_code.get(c)]
    print(f"distinct entry codes named by live headings: {len(live_codes)}")
    print(f"  carrying a kind label in the store: {len(with_label)} {with_label}")
    print(f"  carrying NO kind label           : {len(without)} {without}")
    if live_codes:
        lo, hi = wilson(len(without), len(live_codes))
        print(f"  unlabelled share Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("HIS DIAGNOSIS IS TESTABLE AND THIS IS THE TEST. He wrote that the")
    print("confusion comes from items predating the ticket store and so having")
    print("no position and no issue type. The figure above is that claim")
    print("measured against the store rather than accepted.")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
