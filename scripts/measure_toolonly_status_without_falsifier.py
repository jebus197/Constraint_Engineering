#!/usr/bin/env python3
"""Count archived findings carrying a TOOL-ONLY status with no falsifier behind it.

WHY THIS EXISTS, AND IT IS THE FOURTH REPEAT
--------------------------------------------
The figure "118 of 864 archived findings with a tool-only status have no
falsifier code, 13.66 percent, Wilson [11.53%, 16.11%]" was written into
experimental_notes/Morning_Report_2026-09-05.md line 216 and delivered to the
founder. It was computed in a throwaway shell heredoc and never committed.

That is the FOURTH breach of `measured-rate-travels-with-its-script` in this
session, and the most embarrassing of them, because it sits in the same report
that criticises the first three. The rule is a founder ruling of 2026-09-04: a
measured rate may be cited only if the script that produced it is committed
alongside it. A number nobody can recompute is a claim about evidence.

WHAT IS BEING COUNTED, AND WHY IT MATTERS
-----------------------------------------
TERMINAL_STATUSES and TOOL_ONLY_STATUSES in reference_runner_v3.py are the same
5 values: CONFIRMED, REFUTED, CLOSED, MERGED, DUPLICATE. The vocabulary defines
CONFIRMED as "a falsifier was executed by the runner and fired against the
target" and CLOSED as "a proposed fix was applied to a scratch copy and the
falsifier stopped firing". Both are declared assertable by ('tool',) alone.

So a finding whose status is one of these, but which carries NO falsifier code,
was given a tool-only status without a tool. On 2026-09-05 that was traced to a
concrete instance: 4 findings in the rubric human queue whose CONFIRMED came
from model verdicts -- "CC2: CONFIRM", "DeepSeek: CONFIRM", "Codex/ChatGPT:
CONFIRM". That is confirmation by model vote, which this project forbids.

THE ENFORCEMENT THAT PREVENTS THIS LANDED 2026-08-23 (commit b312b84), which
refuses a model-asserted tool-only status and substitutes a model-assertable
one. Every instance counted here predates it. New runs cannot produce them; the
archive still carries them, and any figure computed over "confirmed" findings
inherits them.

MERGED IS REPORTED SEPARATELY AND DELIBERATELY. A merge is settled by its
parent's verdict, so a MERGED entry legitimately has no falsifier of its own.
Counting it among the concerning population would inflate the figure. The
headline number includes it for continuity with what was already reported to the
founder; the per-status breakdown is what should be acted on.

Usage:
    python3 scripts/measure_toolonly_status_without_falsifier.py [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS = REPO_ROOT / "bench" / "logs"

# Mirrors TOOL_ONLY_STATUSES in bench/reference_runner_v3.py. Asserted equal by
# the test beside this script rather than imported, so that a change to the
# runner's vocabulary shows up as a failing test instead of silently altering a
# published figure.
TOOL_ONLY_STATUSES = frozenset({"CONFIRMED", "REFUTED", "CLOSED", "MERGED", "DUPLICATE"})

# MERGED is settled by the parent, so it needs no falsifier of its own.
NEEDS_NO_FALSIFIER_OF_ITS_OWN = frozenset({"MERGED", "DUPLICATE"})


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _walk(obj):
    if isinstance(obj, dict):
        if any(k in obj for k in ("canonical_id", "finding_id", "cid")):
            yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def measure(logs: Path):
    seen = set()
    total = 0
    missing = 0
    by_status_missing = Counter()
    by_status_total = Counter()
    examples = []

    for path in sorted(logs.rglob("*.json")):
        run = path.parent.name
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        for e in _walk(data):
            cid = e.get("canonical_id") or e.get("finding_id") or e.get("cid")
            if not isinstance(cid, str):
                continue
            key = (run, cid)
            if key in seen:
                continue
            seen.add(key)
            status = str(e.get("status", "")).upper()
            if status not in TOOL_ONLY_STATUSES:
                continue
            # Only entries whose SCHEMA has the field can be judged. An entry
            # from a run predating the field would otherwise be counted as
            # "missing", which would be a schema artefact reported as a finding.
            if "falsifier_code" not in e:
                continue
            total += 1
            by_status_total[status] += 1
            if not str(e.get("falsifier_code") or "").strip():
                missing += 1
                by_status_missing[status] += 1
                if len(examples) < 8:
                    examples.append({"run": run, "cid": cid, "status": status})

    return {
        "total": total,
        "missing": missing,
        "by_status_missing": dict(by_status_missing),
        "by_status_total": dict(by_status_total),
        "examples": examples,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--logs-dir", type=Path, default=LOGS)
    args = ap.parse_args(argv)

    if not args.logs_dir.is_dir():
        print(f"no such logs dir: {args.logs_dir}", file=sys.stderr)
        return 2

    r = measure(args.logs_dir)
    n, k = r["total"], r["missing"]
    lo, hi = wilson(k, n)

    if args.json:
        print(json.dumps({**r, "wilson_95_ci": [lo, hi]}, indent=2))
        return 0

    print("Tool-only status with no falsifier behind it")
    print("=" * 66)
    print(f"  findings with a tool-only status AND a falsifier_code field : {n}")
    print(f"  of those, falsifier_code EMPTY                              : {k}")
    if n:
        print(f"    = {100.0*k/n:.2f}%   Wilson 95% CI [{100*lo:.2f}%, {100*hi:.2f}%]")
    print()
    print("  by status (missing / total for that status):")
    for st in sorted(r["by_status_total"], key=lambda s: -r["by_status_missing"].get(s, 0)):
        miss = r["by_status_missing"].get(st, 0)
        tot = r["by_status_total"][st]
        note = "  <- settled by parent; needs none" if st in NEEDS_NO_FALSIFIER_OF_ITS_OWN else ""
        print(f"    {st:10s} {miss:4d} / {tot:4d}{note}")
    concerning = sum(v for s, v in r["by_status_missing"].items()
                     if s not in NEEDS_NO_FALSIFIER_OF_ITS_OWN)
    print()
    print(f"  CONCERNING population (excluding merge-settled): {concerning}")
    print()
    print("  examples:")
    for e in r["examples"]:
        print(f"    {e['status']:10s} {e['cid']:8s} {e['run']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
