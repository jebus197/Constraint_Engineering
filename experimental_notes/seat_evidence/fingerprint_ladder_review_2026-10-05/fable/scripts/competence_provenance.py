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

TWO LIMITS, MEASURED 2026-10-05 (panel review of the fingerprint-falsification
proposal; producer `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`):

1. REPAIRED HERE: the UNSAFE rule used to aggregate per MODEL -- `confirmed > 0 and
   reads == 0` -- so one reading falsifier anywhere in a model's set (even on a
   REFUTED finding) marked every detached CONFIRMED as safe. Demonstrated by
   execution: 2 detached CONFIRMED + 1 reading REFUTED scored `unsafe=False`. The
   rule is now per CONFIRMATION: a model is UNSAFE TO RANK ON when any of its
   confirmations rests on a falsifier that is not `reads`-style.

2. STILL OPEN, BY DESIGN STATED NOT PAPERED OVER: `falsifier_style` is a source-text
   proxy. `open("/dev/null")` as a decoy, or the word `open(` inside a comment, both
   classify as `reads` -- demonstrated by execution on 2026-10-05. A detached
   falsifier can therefore still pass this check. Provenance strong enough to GATE
   anything (rather than advise) must be execution-derived: record the files the
   falsifier actually opened while `reverify_falsifier` runs it (an audit hook on
   file opens), or re-run it against a perturbed copy of the target and treat a
   verdict invariant to the target's content as detached. Until that exists, this
   script is an advisory instrument, and
   `bench/tests/test_defect_rate_and_competence_provenance_2026-08-23.py` pins it as
   RECORD ONLY.
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
        style = falsifier_style(e.get("falsifier_code"))
        per[m][style] += 1
        per[m]["n"] += 1
        if e.get("falsifier_verdict") == "CONFIRMED":
            per[m]["confirmed"] += 1
            # Per-CONFIRMATION provenance (2026-10-05). The per-model aggregate
            # alone let one reading falsifier on a REFUTED finding vouch for a
            # model whose every CONFIRMED was detached.
            per[m]["confirmed_" + style] += 1
    return per




def _print_usage_and_exit() -> "None":
    """Answer `--help` instead of consuming it as data.

    FOUND 2026-09-11 BY TASK A16'S SURVEY, which is exactly what that survey was
    for. All 5 measurement scripts that failed `--help` failed the SAME way: the
    flag was not recognised, so it was taken as a positional argument -- a report
    path, a note to lint, a log to read. One crashed with FileNotFoundError on
    the literal string `--help`; the others silently ran a full measurement when
    the caller asked for usage.

    This project already carries the rule in its strong form -- "a `--help` must
    never cost money", written after 15 of 17 runners billed a live dispatch on
    an unrecognised argument. These are measurements and cost nothing but time.
    The principle is the same: a flag the program does not understand must not be
    read as data.
    """
    import sys as _sys
    print((__doc__ or "").strip())
    print()
    print(f"usage: {_sys.argv[0].split('/')[-1]} [paths...]")
    raise SystemExit(0)


def _help_requested() -> bool:
    import sys as _sys
    return any(a in ("-h", "--help") for a in _sys.argv[1:])


def main() -> int:
    if _help_requested():
        _print_usage_and_exit()
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
            # A rate is safe to rank on only if EACH confirmation rests on a
            # falsifier that actually consulted the target. Per-confirmation,
            # not per-model (2026-10-05): the old `reads == 0` over the model's
            # whole set let a reading falsifier on a REFUTED finding vouch for
            # detached CONFIRMED ones.
            unread = s["confirmed"] - s["confirmed_reads"]
            unsafe = s["confirmed"] > 0 and unread > 0
            any_unsafe |= unsafe
            basis = (("UNSAFE TO RANK ON — every confirmation rests on a falsifier "
                      "that never read the target") if unsafe and s["confirmed_reads"] == 0 else
                     (f"UNSAFE TO RANK ON — {unread} of {s['confirmed']} confirmation(s) "
                      f"rest on a falsifier that never read the target") if unsafe else
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
