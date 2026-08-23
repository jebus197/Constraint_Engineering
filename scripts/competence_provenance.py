#!/usr/bin/env python3
"""A confirm rate is not a competence measure unless the falsifiers read the target.

WHY THIS EXISTS. Founder observation, 2026-08-23, which neither external reviewer
raised: measured model competence is not a reporting statistic in this project, it is
wired into the mechanics. `bench/routing.py` orders the falsifier-resolution ladder by
capability, and that order is documented as coming from "Exp-42 EMPIRICAL
falsifier-confirm rates". So a contaminated confirm rate does not merely mislead a
reader -- it re-orders which model is asked to resolve the hardest findings.

THE SPECIFIC HAZARD, MEASURED ON EXP 55. While the falsifier gate ran every falsifier
in an empty working directory, a DETACHED falsifier (one that opens nothing and
restates the document's numbers from memory) confirmed cleanly, and a falsifier that
actually opened the target ERRORed. Per-model on that run: Gemini 2 of 2 CONFIRMED,
both falsifiers detached; DeepSeek 0 of 2, both falsifiers genuine readers. Re-deriving
the ladder from that run would have promoted Gemini to FIRST and demoted DeepSeek to
LAST -- ranking the models by their willingness to ignore the evidence.

The current ladder is NOT contaminated: Exp 42's target was `composer.py`, and a code
falsifier reaches its target by `import`, which PYTHONPATH carries regardless of
working directory. The hazard is forward-looking, and this script is the check that
must run before any future re-derivation.

WHAT IT DOES. For each run, per model: the confirm rate, and beside it the provenance
of the falsifiers that rate is built from. A rate whose falsifiers do not read the
target is reported as UNSAFE TO RANK ON, not as a number.
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def falsifier_style(code: str) -> str:
    c = (code or "").strip()
    if not c:
        return "none"
    return "reads" if re.search(r"open\s*\(|read_text|\.read\s*\(|linecache|getlines", c) else "detached"


def analyse(report: pathlib.Path) -> dict:
    ents = (json.loads(report.read_text()).get("registry") or {}).get("entries") or {}
    per = collections.defaultdict(lambda: collections.Counter())
    for e in ents.values():
        m = e.get("source_model") or "?"
        per[m][falsifier_style(e.get("falsifier_code"))] += 1
        per[m]["n"] += 1
        if e.get("falsifier_verdict") == "CONFIRMED":
            per[m]["confirmed"] += 1
    return per


def main() -> int:
    reports = ([pathlib.Path(a) for a in sys.argv[1:]] or
               sorted(REPO.glob("bench/logs/*/*_report.json")))
    reports = [p for p in reports if p.is_file()]
    if not reports:
        print("  no report found"); return 1
    any_unsafe = False
    for rep in reports:
        per = analyse(rep)
        if not per:
            continue
        print(f"\n  {rep.parent.name}")
        print(f"    {'model':<10} {'n':>3} {'conf':>5} {'rate':>6}  {'reads':>6} {'detach':>7} {'none':>5}  ranking basis")
        for m, s in sorted(per.items(), key=lambda kv: -(kv[1]['confirmed'] / max(kv[1]['n'], 1))):
            rate = s["confirmed"] / s["n"] if s["n"] else 0.0
            # A rate is safe to rank on only if the confirmations rest on falsifiers
            # that actually consulted the target.
            unsafe = s["confirmed"] > 0 and s["reads"] == 0
            any_unsafe |= unsafe
            basis = ("UNSAFE TO RANK ON — every confirmation rests on a falsifier "
                     "that never read the target" if unsafe else
                     "no confirmations to rank on" if s["confirmed"] == 0 else
                     "safe")
            print(f"    {m:<10} {s['n']:>3} {s['confirmed']:>5} {rate:>5.0%}  "
                  f"{s['reads']:>6} {s['detached']:>7} {s['none']:>5}  {basis}")
    print("\n  RULE: do not re-derive bench/routing.py's DEFAULT_FALSIFIER_STRENGTH from any")
    print("  run this script marks UNSAFE TO RANK ON. Doing so ranks models by their")
    print("  willingness to ignore the document, which is the exact inversion the")
    print("  discrimination control exists to detect.")
    return 2 if any_unsafe else 0


if __name__ == "__main__":
    raise SystemExit(main())
