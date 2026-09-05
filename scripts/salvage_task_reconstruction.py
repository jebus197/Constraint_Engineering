#!/usr/bin/env python3
"""Recover the outstanding-task reconstruction from a killed workflow's journal.

WHY THIS EXISTS
---------------
On 2026-09-05 a workflow was dispatched to read every CDSFL note, TTS file and
founder RTF from 2026-09-02 onward and verify each extracted task against the
repository. It ran from 05:19 to 12:04 and was killed by the founder's stop.

THE STOP WAS CORRECT, AND THE RUNAWAY WAS MINE. The design was 10 read agents,
one verify agent per DEDUPLICATED task, and 1 critic -- expected order 30 to 50
agents. It spawned 488. Cause: the dedup key was the first 7 normalised words of
a task title, which collapsed 541 raw candidates to roughly 473, only 12.6
percent. Near-duplicates phrased differently each got their own verify agent.
The session's stated workflow guideline was 15 agents; this exceeded it 32-fold
and ran for 4 hours 45 minutes.

NOTHING WAS LOST. The journal records one {"type":"result"} line per completed
agent with its full return value, so all 482 completed results survive the kill.
Only the final in-script dedup, the synthesis and the critic agent did not run.
This script does that final step offline, from the journal, spawning nothing.

WHAT IT DOES NOT DO. It cannot run the completeness critic, which was the agent
that would have said what the READ phase itself missed. That question is still
open and this script does not pretend otherwise.

Usage:
    python3 scripts/salvage_task_reconstruction.py [--json] [--status NOT_STARTED]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

JOURNAL = Path(
    "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"
    "/a07b3790-0a2a-4978-aedb-bd842c0493d3/subagents/workflows/wf_a33f50d2-519"
    "/journal.jsonl"
)

AUTHORITY_RANK = {
    "FOUNDER_RULED": 3,
    "FOUNDER_APPROVED": 2,
    "PROPOSED_BY_CC1": 1,
    "OPEN_QUESTION": 0,
}


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def norm(title: str) -> str:
    """Normalise a title for matching.

    THIS KEY IS NOT BETTER THAN THE WORKFLOW'S, AND SAYING SO WAS WRONG.

    The first version of this docstring claimed it was "deliberately STRONGER"
    than the workflow's first-7-words key. Measured on the same 473 verdicts:
    this key collapses 0 of them, against the workflow's roughly 12.6 percent.
    Dropping filler and then SORTING the unique words makes the key MORE
    discriminating, not less, so any two titles differing by a single content
    word stay apart. The claim was asserted from the shape of the code instead of
    from its output, which is the exact habit this project keeps catching.

    It is left in place, corrected rather than replaced, because a key that
    collapses nothing is honest about the data: it means the 473 titles really
    are 473 distinct strings, and any real merging needs semantic similarity
    rather than token identity. That is a bigger job than a salvage script should
    do, and pretending otherwise would put a fabricated collapse rate in front of
    the founder.
    """
    s = re.sub(r"[^a-z0-9 ]+", " ", str(title or "").lower())
    stop = {"the", "a", "an", "of", "to", "for", "and", "in", "on", "is", "it",
            "that", "this", "be", "should", "must", "run", "add"}
    words = [w for w in s.split() if w and w not in stop]
    return " ".join(sorted(set(words)))


def load(journal: Path):
    reads, verdicts = [], []
    for line in journal.read_text().splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "result":
            continue
        r = d.get("result")
        if not isinstance(r, dict):
            continue
        if "tasks" in r:
            reads.append(r)
        elif "actual_status" in r:
            verdicts.append(r)
    return reads, verdicts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--status", help="show only this actual_status")
    ap.add_argument("--journal", type=Path, default=JOURNAL)
    args = ap.parse_args(argv)

    if not args.journal.is_file():
        print(f"no journal at {args.journal}", file=sys.stderr)
        return 2

    reads, verdicts = load(args.journal)

    # Authority comes from the READ phase; the verify phase did not carry it.
    authority, quote, source = {}, {}, {}
    for r in reads:
        for t in r.get("tasks") or []:
            k = norm(t.get("title"))
            if not k:
                continue
            cur = authority.get(k)
            new = t.get("founder_authority")
            if cur is None or AUTHORITY_RANK.get(new, 0) > AUTHORITY_RANK.get(cur, 0):
                authority[k] = new
                quote[k] = t.get("verbatim_quote")
                source[k] = t.get("source")

    merged = {}
    for v in verdicts:
        k = norm(v.get("title"))
        if not k:
            continue
        prev = merged.get(k)
        if prev is None:
            merged[k] = dict(v, _n=1)
        else:
            prev["_n"] += 1
            # A disagreement between duplicate verifications is information.
            if prev.get("actual_status") != v.get("actual_status"):
                prev.setdefault("_disputed", set()).add(prev["actual_status"])
                prev["_disputed"].add(v["actual_status"])

    raw_tasks = sum(len(r.get("tasks") or []) for r in reads)
    print("Salvaged task reconstruction (offline, from the journal)")
    print("=" * 68)
    print(f"  read-phase agents that returned : {len(reads)}")
    print(f"  raw candidate tasks extracted   : {raw_tasks}")
    print(f"  verify-phase results in journal : {len(verdicts)}")
    print(f"  after stronger dedup            : {len(merged)}")
    collapse = 1 - len(merged) / len(verdicts) if verdicts else 0
    print(f"  collapse rate of this dedup     : {100*collapse:.1f}% "
          f"— WORSE than the workflow's ~12.6%; see norm() docstring")
    print()

    st = Counter(v["actual_status"] for v in merged.values())
    n = len(merged)
    print("  STATUS (deduplicated), with Wilson 95% intervals:")
    for k, c in st.most_common():
        lo, hi = wilson(c, n)
        print(f"    {k:16s} {c:4d}  {100*c/n:5.1f}%  [{100*lo:.1f}%, {100*hi:.1f}%]")

    contra = sum(1 for v in merged.values() if v.get("contradicts_claim"))
    lo, hi = wilson(contra, n)
    print()
    print(f"  the repo CONTRADICTS the note's own claim in {contra} of {n} "
          f"= {100*contra/n:.1f}%  Wilson [{100*lo:.1f}%, {100*hi:.1f}%]")

    disputed = [v for v in merged.values() if v.get("_disputed")]
    print(f"  tasks where duplicate verifications DISAGREED: {len(disputed)}")

    # What the founder actually needs: ruled/approved work that is not done.
    outstanding = []
    for k, v in merged.items():
        if v["actual_status"] in ("DONE_VERIFIED", "OBSOLETE"):
            continue
        auth = authority.get(k)
        if AUTHORITY_RANK.get(auth, 0) >= 2:      # RULED or APPROVED only
            outstanding.append((auth, v, k))
    outstanding.sort(key=lambda x: -AUTHORITY_RANK.get(x[0], 0))

    print()
    print(f"  FOUNDER-RULED OR APPROVED AND NOT DONE: {len(outstanding)}")
    shown = outstanding if not args.status else [
        o for o in outstanding if o[1]["actual_status"] == args.status]
    for auth, v, k in shown[:60]:
        print(f"    [{auth:16s}] [{v['actual_status']:12s}] {v['title'][:88]}")
        if v.get("remaining_work"):
            print(f"        remaining: {str(v['remaining_work'])[:150]}")
    if len(shown) > 60:
        print(f"    ... and {len(shown)-60} more (use --json for all)")

    print()
    print("  NOT RECOVERABLE: the completeness critic never ran, so the question")
    print("  'what did the READ phase itself miss?' remains open.")

    if args.json:
        out = [{"authority": a, **{kk: vv for kk, vv in v.items()
                                   if not kk.startswith("_")}}
               for a, v, _ in outstanding]
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
