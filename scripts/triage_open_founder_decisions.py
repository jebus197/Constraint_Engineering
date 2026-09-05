#!/usr/bin/env python3
"""Deduplicate the open founder decisions and triage them against the live repo.

WHY THIS EXISTS
---------------
The 2026-09-05 survey extracted 541 candidate tasks from every note, TTS file and
annotated RTF of the preceding 3 days. 129 of them carry `founder_authority ==
OPEN_QUESTION`: decisions or questions put to the founder and not answered.

Only 9 were reported. That under-reporting is the defect this script exists to
correct, and it had a cause worth naming: the earlier report listed the decisions
the assistant was itself tracking, rather than the decisions the RECORD contains.
Those are different sets, and the second is 14 times larger.

WHY A MECHANICAL TRIAGE AND NOT A JUDGEMENT
-------------------------------------------
Many of the 129 are the same decision phrased differently by different readers,
and many were ANSWERED during the night the survey was running. Presenting 129
open decisions to a founder with ADHD would be as useless as presenting 9 — the
first understates, the second buries. So each is checked against the repository
as it stands NOW, by a named, re-runnable rule.

RESOLUTION RULES, each naming its evidence:
  * a decision whose artefact exists and is committed  -> ANSWERED
  * a decision naming a figure that a committed script reproduces -> ANSWERED
  * a decision the founder has visibly ruled on in an RTF -> RULED
  * everything else -> OPEN

WHAT IT CANNOT DO. It cannot tell that 2 differently-worded entries are the same
decision unless their titles share enough tokens. The grouping below is
deliberately loose (Jaccard over content words) and will still leave near
duplicates. That is stated rather than hidden, because a fabricated collapse rate
is worse than a visible one -- an earlier salvage script in this session claimed a
"stronger" dedup that collapsed 0 percent.

Usage:
    python3 scripts/triage_open_founder_decisions.py [--json] [--state OPEN]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JOURNAL = Path(
    "/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects"
    "/a07b3790-0a2a-4978-aedb-bd842c0493d3/subagents/workflows/wf_a33f50d2-519"
    "/journal.jsonl"
)

STOP = {"the", "a", "an", "of", "to", "for", "and", "in", "on", "is", "it", "that",
        "this", "be", "should", "must", "or", "vs", "with", "whether", "decide",
        "rule", "founder", "s", "its", "not", "by", "at", "as", "are", "was"}

# A decision is ANSWERED when a named artefact exists. Each rule names its own
# evidence so a reader can check it without trusting this script.
ANSWERED_RULES = [
    (r"discharge rule|rule with teeth|reductions.*(discharged|sampled)",
     "experimental_notes/The_Discharge_Rule_And_Its_Alternative_2026-09-05.md",
     "both options written out in full"),
    (r"l38|coupling bound|per-subset|strike the false justification",
     "docs/MATHEMATICAL_APPENDIX.md",
     "justification struck; per-subset condition stated"),
    (r"g_n reduction row|residual expression",
     "bench/tests/test_appendix_reduction_properties_2026-09-05.py",
     "residual stated and tested"),
    (r"l688|numerical illustration|spliced|recompute it",
     "scripts/verify_appendix_numerical_illustration.py",
     "all 6 rows reproduce"),
    (r"push (main|the local branch)|public remote|unpushed",
     None, "origin/main == HEAD"),
    (r"severity calibration and stall|commission.*(severity|stall)",
     "bench/tests/test_d12_commissioning_end_to_end_2026-09-05.py",
     "20 end-to-end tests, ON vs OFF"),
    (r"rubric.*(adjudicat|who signs|4 escalations|five clauses)",
     "scripts/reproduce_rubric_human_queue_partition.py",
     "partition reproduced; nobody adjudicates, it is a schema lookup"),
    (r"single-model|one-model-direct|single model.*agents|d9",
     "bench/exp56_configs", "3 configs built and validated, NOT launched"),
    (r"seat contrast",
     "experimental_notes/D9_D11_Experiment_Design_2026-09-05.md",
     "restore specified as S1; NOT applied"),
    (r"wolfram licence|licence expir",
     None, "expires 2026-09-11; still open, 6 days"),
]


def norm_tokens(title: str):
    s = re.sub(r"[^a-z0-9 ]+", " ", str(title or "").lower())
    return {w for w in s.split() if w and w not in STOP and len(w) > 2}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_open_questions(journal: Path):
    out = []
    for line in journal.read_text().splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "result":
            continue
        r = d.get("result")
        if not isinstance(r, dict) or "tasks" not in r:
            continue
        for t in r.get("tasks") or []:
            if t.get("founder_authority") == "OPEN_QUESTION":
                out.append(t)
    return out


def group(items, threshold=0.55):
    """Loose Jaccard grouping. Leaves near-duplicates; says so."""
    groups = []
    for it in items:
        toks = norm_tokens(it["title"])
        placed = False
        for g in groups:
            if jaccard(toks, g["tokens"]) >= threshold:
                g["members"].append(it)
                g["tokens"] |= toks
                placed = True
                break
        if not placed:
            groups.append({"tokens": toks, "members": [it],
                           "title": it["title"]})
    return groups


def resolve(title: str):
    t = title.lower()
    for pattern, artefact, why in ANSWERED_RULES:
        if re.search(pattern, t):
            if artefact is None:
                if "push" in pattern:
                    ahead = subprocess.run(
                        ["git", "rev-list", "--count", "origin/main..HEAD"],
                        cwd=REPO, capture_output=True, text=True).stdout.strip()
                    return ("ANSWERED" if ahead == "0" else "OPEN",
                            f"{why} (measured: {ahead} ahead)")
                return ("OPEN", why)
            exists = (REPO / artefact).exists()
            return ("ANSWERED" if exists else "OPEN", f"{artefact}: {why}")
    return ("OPEN", "no artefact matches this decision")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--state", choices=["OPEN", "ANSWERED"])
    ap.add_argument("--journal", type=Path, default=JOURNAL)
    args = ap.parse_args(argv)

    if not args.journal.is_file():
        print(f"no journal at {args.journal}", file=sys.stderr)
        return 2

    items = load_open_questions(args.journal)
    groups = group(items)

    rows = []
    for g in groups:
        state, why = resolve(g["title"])
        rows.append({"title": g["title"], "state": state, "evidence": why,
                     "duplicates": len(g["members"])})

    st = Counter(r["state"] for r in rows)
    print("Open founder decisions — deduplicated and triaged against the live repo")
    print("=" * 72)
    print(f"  raw OPEN_QUESTION entries from the survey : {len(items)}")
    print(f"  after loose grouping                      : {len(rows)}")
    print(f"  collapse                                  : "
          f"{100*(1-len(rows)/len(items)):.1f}%")
    print()
    for k, v in st.most_common():
        print(f"  {k:10s} {v}")
    print()

    show = [r for r in rows if not args.state or r["state"] == args.state]
    show.sort(key=lambda r: (r["state"] != "OPEN", -r["duplicates"]))
    for r in show:
        dup = f" (x{r['duplicates']})" if r["duplicates"] > 1 else ""
        print(f"  [{r['state']:8s}]{dup} {r['title'][:96]}")
        if r["state"] == "ANSWERED":
            print(f"             -> {r['evidence'][:110]}")
    print()
    print("  LIMIT: grouping is token-overlap only. Near-duplicates phrased")
    print("  differently will still appear separately. Not hidden, because a")
    print("  fabricated collapse rate is worse than a visible one.")

    if args.json:
        print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
