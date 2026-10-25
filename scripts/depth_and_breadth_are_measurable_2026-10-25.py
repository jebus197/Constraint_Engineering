#!/usr/bin/env python3
"""How much reasoning effort went to DEPTH and how much to BREADTH.

WHY THIS SCRIPT EXISTS. On 2026-10-25 CC1 quoted two figures to the founder --
fan-out calls falling from 1.2750 to 0.4286 per day, and 13 of 16 session errors
being breadth failures -- and neither had a committed producer. A grep for the
figures across `scripts/`, `bench/` and `experimental_notes/` returned only
coincidental matches inside experiment logs. Under
`measured-rate-travels-with-its-script` those numbers were therefore CLAIMS ABOUT
EVIDENCE, not evidence. This script is the producer they were owed.

WHAT IS AND IS NOT MEASURABLE. There is no counter that labels a thought "depth"
or "breadth", so a token-level split between them CANNOT be measured from inside
a session. What CAN be counted exactly, from the session transcripts, is the
number of FAN-OUT calls -- `Agent`, `Task`, `Workflow` -- and the number of tool
calls overall. Breadth is therefore measured directly; depth is the residual, and
that asymmetry is stated rather than hidden. Any claim of the form "70% of the
allowance went to depth" is outside what this instrument can support.

DEFINITIONS USED HERE, both of them about REASONING:
  BREADTH = reasoning effort DISTRIBUTED across parallel contexts. Each `Agent`,
            `Task` or `Workflow` call opens a context that reasons separately and
            reports back a summary. Counted exactly.
  DEPTH   = reasoning effort CONCENTRATED in one context on one problem. Not
            directly countable; its observable trace is the volume of ordinary
            tool work done without fanning out, which this script reports as the
            non-fan-out call count.

HIS MACHINE IS A FIXED RESOURCE (8 GiB). The current transcript is ~485 MB, so
every file is STREAMED line by line and nothing is held whole in memory.

USAGE
    python3 scripts/depth_and_breadth_are_measurable_2026-10-25.py
    python3 scripts/depth_and_breadth_are_measurable_2026-10-25.py --json
    python3 scripts/depth_and_breadth_are_measurable_2026-10-25.py --pivot 2026-10-05
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

TRANSCRIPTS = (pathlib.Path.home() / ".claude" / "projects"
               / "-Users-georgejackson-Developer-Projects")

#: Calls that open a SEPARATE reasoning context. These are breadth by definition.
FANOUT = frozenset({"Agent", "Task", "Workflow"})

#: The day he asked for the depth-over-breadth balance. The directive in
#: `.claude/CLAUDE.md` records the ask as 2026-10-05 and its recording as
#: 2026-10-11, 6 days later, because it sat in a file `grep` read as binary.
DEFAULT_PIVOT = "2026-10-05"


def per_day() -> tuple[dict[str, collections.Counter], list[str]]:
    """Stream every transcript and count tool calls per calendar day.

    Returns (counts, files_read). `counts[day]` is a Counter over tool names.
    A line that will not parse is skipped and counted, never guessed at.
    """
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    files, bad = [], 0
    if not TRANSCRIPTS.is_dir():
        return counts, files
    for f in sorted(TRANSCRIPTS.glob("*.jsonl")):
        files.append(f.name)
        with f.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"tool_use"' not in line:          # cheap prefilter; 221k lines
                    continue
                try:
                    d = json.loads(line)
                except Exception:                     # noqa: BLE001
                    bad += 1
                    continue
                ts = str(d.get("timestamp") or "")[:10]
                if not ts:
                    continue
                msg = d.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        counts[ts][str(c.get("name") or "?")] += 1
    if bad:
        print(f"  note: {bad} unparseable line(s) skipped", file=sys.stderr)
    return counts, files


def split(counts, pivot: str):
    """Fan-out calls per day before and from the pivot date."""
    before = [(d, c) for d, c in sorted(counts.items()) if d < pivot]
    after = [(d, c) for d, c in sorted(counts.items()) if d >= pivot]

    def rate(rows):
        if not rows:
            return 0.0, 0, 0, []
        fan = [sum(c[n] for n in FANOUT) for _, c in rows]
        tot = sum(sum(c.values()) for _, c in rows)
        return sum(fan) / len(rows), sum(fan), tot, fan

    return rate(before), rate(after), [d for d, _ in before], [d for d, _ in after]


def mann_whitney(a: list[int], b: list[int]) -> dict:
    """Two-sided test that the two day-level fan-out distributions differ.

    Cross-verified across scipy and a NumPy normal approximation, per the
    project's >=2-tools-per-claim rule. A rank test is used rather than a t-test
    because daily counts are small integers with a hard floor at 0.
    """
    out = {}
    try:
        from scipy.stats import mannwhitneyu
        u, p = mannwhitneyu(a, b, alternative="two-sided")
        out["scipy"] = {"U": float(u), "p": float(p)}
    except Exception as e:                            # noqa: BLE001
        out["scipy"] = {"error": f"{type(e).__name__}: {e}"}
    try:
        import numpy as np
        na, nb = len(a), len(b)
        if na and nb:
            allv = np.array(a + b, dtype=float)
            order = allv.argsort()
            ranks = np.empty_like(order, dtype=float)
            ranks[order] = np.arange(1, len(allv) + 1)
            # average ranks within ties
            for v in np.unique(allv):
                m = allv == v
                ranks[m] = ranks[m].mean()
            ra = ranks[:na].sum()
            u1 = ra - na * (na + 1) / 2
            mu = na * nb / 2
            # tie-corrected variance
            _, cnt = np.unique(allv, return_counts=True)
            n = na + nb
            tie = (cnt ** 3 - cnt).sum()
            var = na * nb / 12 * ((n + 1) - tie / (n * (n - 1)))
            z = (u1 - mu) / var ** 0.5 if var > 0 else 0.0
            from math import erfc
            out["numpy_normal_approx"] = {
                "U": float(u1), "z": float(z),
                "p": float(erfc(abs(z) / 2 ** 0.5))}
    except Exception as e:                            # noqa: BLE001
        out["numpy_normal_approx"] = {"error": f"{type(e).__name__}: {e}"}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--pivot", default=DEFAULT_PIVOT)
    a = ap.parse_args()

    counts, files = per_day()
    if not counts:
        print("no transcripts found; nothing measured", file=sys.stderr)
        return 1
    (rb, fb, tb, sb), (ra, fa, ta, sa), days_b, days_a = split(counts, a.pivot)
    stats = mann_whitney(sb, sa) if (sb and sa) else {}

    res = {
        "pivot": a.pivot,
        "transcripts": files,
        "days_before": len(days_b), "days_from_pivot": len(days_a),
        "fanout_calls_before": fb, "fanout_calls_from_pivot": fa,
        "all_calls_before": tb, "all_calls_from_pivot": ta,
        "fanout_per_day_before": round(rb, 4),
        "fanout_per_day_from_pivot": round(ra, 4),
        "fanout_share_before": round(fb / tb, 6) if tb else None,
        "fanout_share_from_pivot": round(fa / ta, 6) if ta else None,
        "per_day_fanout_before": dict(zip(days_b, sb)),
        "per_day_fanout_from_pivot": dict(zip(days_a, sa)),
        "test": stats,
        "what_this_cannot_measure":
            "A token-level depth:breadth ratio. No counter labels a thought. "
            "Breadth is counted exactly; depth is the residual.",
    }
    if a.json:
        print(json.dumps(res, indent=2))
        return 0

    print(f"  pivot: {a.pivot}   transcripts: {len(files)}")
    print(f"  BEFORE  {len(days_b):3d} day(s): {fb:4d} fan-out of {tb:6d} calls "
          f"= {rb:.4f}/day" + (f", share {fb/tb:.6f}" if tb else ""))
    print(f"  FROM    {len(days_a):3d} day(s): {fa:4d} fan-out of {ta:6d} calls "
          f"= {ra:.4f}/day" + (f", share {fa/ta:.6f}" if ta else ""))
    for k, v in stats.items():
        print(f"    {k}: {v}")
    print(f"\n  NOT MEASURABLE HERE: {res['what_this_cannot_measure']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
