#!/usr/bin/env python3
"""Before building a producer, ask whether one already exists. 1 command.

DRAFTED 2026-11-22; destination `scripts/`.

WHY, MEASURED ON THE SESSION THAT WROTE IT. 9 times on 2026-11-22 this instance
re-derived a finding already in the record. The worst was the `cy` gate's
liveness proxy: `scripts/the_gate_decides_on_the_pulse_2026-11-22.py` already
held the diagnosis, the fix direction and the ratio, was STAGED IN THE SAME
BATCH, and its filename had appeared in this session's own artefact listing an
hour earlier. About 20 minutes went into reproducing it.

★ THE FIX IS AVAILABILITY, NOT RESOLVE, and that distinction is the whole point.
The rule "check the record first" has existed for weeks as
`feedback_check_the_record_before_declaring_a_gap`, and restating it a 10th time
would be the failure the founder's own ruling names: "The failure was never the
absence of a rule or a checker; it was never running the checker." Checking cost
a tool call and a guess at where to look. This makes it 1 command with no guess.

WHAT IT SEARCHES, in the order a finding is most likely to already live:
  1. scripts/      -- a producer with the measurement already in it
  2. bench/tests/  -- a guard already holding the property
  3. experimental_notes/CDSFL_MASTER_TASK_LIST.md -- an entry already raised
  4. the memory directory -- a lesson already written
  5. hooks/        -- a mechanism already enforcing it

IT DECIDES NOTHING. It prints what exists and leaves the judgement, because
"something mentions this subject" is not "this is already done" -- and a tool
that answered the second question would be guessing.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


def _repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _repo()
MEMORY = (pathlib.Path.home() / ".claude" / "projects"
          / "-Users-georgejackson-Developer-Projects" / "memory")

#: Searched in this order. The 2nd element is what a hit there MEANS, because a
#: bare path tells the reader nothing about whether to stop.
PLACES = [
    ("scripts", "a PRODUCER may already measure this -- read it before writing one"),
    ("bench/tests", "a GUARD may already hold this property"),
    ("hooks", "a MECHANISM may already enforce it"),
]


def _grep(root: pathlib.Path, terms: list[str], suffix: str) -> dict:
    """Files under `root` mentioning EVERY term. All, not any: 1 shared word
    matches half the repository and teaches the reader to ignore the output."""
    hits = {}
    if not root.is_dir():
        return hits
    for p in sorted(root.rglob(f"*{suffix}")):
        if "__pycache__" in p.parts:
            continue
        try:
            t = p.read_text(errors="ignore").lower()
        except OSError:
            continue
        if all(term in t for term in terms):
            hits[p] = sum(t.count(term) for term in terms)
    return hits


def _first_doc_line(p: pathlib.Path) -> str:
    try:
        for line in p.read_text(errors="ignore").splitlines():
            s = line.strip().strip('"').strip("'")
            if s and not s.startswith(("#!", "#", "from", "import")):
                return s[:96]
    except OSError:
        pass
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("terms", nargs="+",
                    help="words that must ALL appear; 2 or 3 is the useful number")
    ap.add_argument("--limit", type=int, default=6, help="hits shown per place")
    a = ap.parse_args()
    terms = [t.lower() for t in a.terms]

    print("=" * 76)
    print("HAS THIS ALREADY BEEN FOUND?   terms: " + ", ".join(repr(t) for t in terms))
    print("=" * 76)

    total = 0
    for rel, meaning in PLACES:
        hits = _grep(REPO / rel, terms, ".py")
        total += len(hits)
        print(f"\n  {rel}/  -- {meaning}")
        if not hits:
            print("      nothing")
            continue
        for p, n in sorted(hits.items(), key=lambda kv: -kv[1])[:a.limit]:
            print(f"      {p.relative_to(REPO)}  ({n} mention(s))")
            d = _first_doc_line(p)
            if d:
                print(f"          {d}")
        if len(hits) > a.limit:
            print(f"      ... and {len(hits)-a.limit} more")

    # the task list, by entry rather than by file
    tl = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
    print("\n  the master task list -- an ENTRY may already be raised")
    if tl.is_file():
        text = tl.read_text(errors="ignore")
        ents = re.split(r"\n(?=\*\*[AB]\d+\.)", text)
        found = [e for e in ents if all(t in e.lower() for t in terms)]
        total += len(found)
        if found:
            for e in found[:a.limit]:
                m = re.match(r"\*\*([AB]\d+)\.\s*(.{0,86})", e)
                if m:
                    print(f"      {m.group(1)}  {m.group(2)}")
        else:
            print("      nothing")
    else:
        print("      task list not found")

    mem = _grep(MEMORY, terms, ".md")
    total += len(mem)
    print("\n  memory -- a LESSON may already be written")
    if mem:
        for p, n in sorted(mem.items(), key=lambda kv: -kv[1])[:a.limit]:
            print(f"      {p.name}  ({n})")
    else:
        print("      nothing")

    print("\n" + "=" * 76)
    print(f"  {total} place(s) mention all of these terms.")
    print("  THIS DECIDES NOTHING. A mention is not a completed piece of work,")
    print("  and 0 mentions is not proof of absence -- the terms may be wrong.")
    print("  Read what it names before building anything that duplicates it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
