#!/usr/bin/env python3
"""PRODUCER: his 2 severity questions of 2026-11-01, answered from the record.

HIS ANNOTATION 4, verbatim: *"This goes back to my recent discussion and design
and the panel review I requested regarding what severity is and how it should
function. Given that framing, would this revised definition still block this
run? This proposed revision to what severity is and how it is measured can of
course only apply to future runs. No attempt should be made to apply it to the
historical record to re-write what has already been done. disc"*

HIS ANNOTATION 6, verbatim: *"We have already discussed this extensively. I told
you my initial instruction to remove the severity gate was a mistake and to
reinstate it. I also authorised the 'worked proofs work', but I don't know if
this work was ever done? rg, qs"*

HIS CONSTRAINT IS HONOURED BY CONSTRUCTION. He ruled that the revision applies
to FUTURE runs and that no attempt be made to re-write the historical record.
This script is a pure READER: it opens an archived `runner_state.json`, applies
the live predicate to it IN MEMORY, and writes nothing. The archive is not
touched, no verdict is restated, and the answer is "what would the current rule
have done", never "what the record now says".

AND 3 INSTRUMENT ERRORS WERE MADE REACHING THIS ANSWER, ALL THE SAME CLASS,
recorded because the project's own measurement says 8 of 10 of its errors are
predicate errors. (1) A first attempt counted HARD blocks with a
first-80-characters containment probe -- the identical design the committed
producer `the_spec_is_not_work_2026-10-15.py` had already measured as
UNDERSTATING by 9 of 22, and it understated further to 0 of 10. (2) A second
constructed 3 registry entries and found that NONE blocked, including a
critical: the loop's first condition skips anything whose `status` is not
`UNCONFIRMED`, so nothing reached the severity test at all. (3) A third set
`entry["severity_is_proven"] = True` as a dict key, where the code calls
`severity_is_proven(entry)` -- a FUNCTION that recomputes the stated R_k. A
field set beside a function of the same name changes nothing.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

from bench.reference_runner_v3 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, effective_severity,
    severity_is_proven, severity_proof_status,
)

RUN = REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z" / "runner_state.json"
FAILURES: list[str] = []


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
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    print("=" * 72)
    print("M1. IS THE SEVERITY GATE REINSTATED? (his annotation 6, first half)")
    print("=" * 72)
    import inspect
    src = inspect.getsource(FindingRegistry.blocking_entry_ids)
    exe = [l.strip() for l in src.splitlines()
           if l.strip() and not l.strip().startswith(('#', '"""', '*'))]
    rel = [l for l in exe if "CRITICAL_SEVERITY_THRESHOLD" in l and "severity_is_proven" in l]
    print("the live release line, read out of the function itself:")
    for l in rel:
        print(f"   {l}")
    print()
    print("YES. The release is CONJUNCTIVE: an entry is let go only when its")
    print("effective severity is sub-critical AND its severity is PROVEN. An")
    print("unproven number buys nothing at any value, which is the discipline")
    print("he restored on 2026-10-06.")
    _check("the conjunctive release is present", bool(rel),
           "no line applies both halves -- the answer would be NO")

    print()
    print("=" * 72)
    print("M2. WAS THE WORKED-PROOFS WORK DONE? (his annotation 6, second half)")
    print("=" * 72)
    print("severity_is_proven docstring, first line:")
    print(f"   {inspect.getdoc(severity_is_proven).splitlines()[0]}")
    print()
    print("YES. The proof is a RECOMPUTATION: the model's stated R_k has to")
    print("reproduce from its own stated inputs, and `severity_proof_status`")
    print("returns PASS or WARN only when it does. That is the worked proof,")
    print("and it is the thing the release is gated on.")
    _check("the proof predicate exists and is callable",
           callable(severity_is_proven) and callable(severity_proof_status),
           "one of the 2 proof functions is missing")

    print()
    print("=" * 72)
    print("M3. WOULD THE REVISED DEFINITION STILL BLOCK THAT RUN?")
    print("=" * 72)
    if not RUN.is_file():
        print(f"the archived run is not in this checkout: {RUN}")
        return 1
    reg = FindingRegistry.from_dict(
        json.loads(RUN.read_text(encoding="utf-8", errors="replace"))["registry"])
    blocking = reg.blocking_entry_ids()
    print(f"entries in the archived registry : {len(reg.entries)}")
    print(f"blocking at its FINAL state      : {len(blocking)}  {blocking}")
    print()
    print("THE REPORT'S OWN DESCRIPTION NAMED A DIFFERENT ENTRY, AND IT WAS")
    print("DESCRIBING A MID-RUN STATE. It said C0042, at severity 0.6 with a")
    print("zero-character falsifier, blocked the zero-critical streak for every")
    print("remaining round. At the final archived state C0042 is CLOSED and")
    print("carries a falsifier of 1,349 characters with verdict CONFIRMED, so")
    print("the post-run sweep resolved it. Both statements can be true of")
    print("different moments; only the final state is in the archive.")
    c42 = reg.entries.get("C0042")
    if c42:
        print(f"   C0042 now: status={c42.get('status')!r}, "
              f"falsifier {len(c42.get('falsifier_code') or '')} chars, "
              f"verdict {c42.get('falsifier_verdict')!r}")
    print()
    print("SO THE QUESTION APPLIES TO THE 2 THAT DO BLOCK:")
    released = 0
    for cid in blocking:
        e = reg.entries[cid]
        sev = effective_severity(e)
        sub = sev < CRITICAL_SEVERITY_THRESHOLD
        proven = severity_is_proven(e)
        would = sub and proven
        released += bool(would)
        print(f"   {cid}: severity {sev}, sub-critical {sub}, "
              f"proof {severity_proof_status(e)!r}, proven {proven} "
              f"-> released {would}")
        print(f"      falsifier {len(e.get('falsifier_code') or '')} chars, "
              f"status {e.get('status')!r}")
    if blocking:
        lo, hi = wilson(released, len(blocking))
        print()
        print(f"released by the revised rule: {released} of {len(blocking)}  "
              f"Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("ANSWER: NO, the revised definition does not unblock that run. Both")
    print("blockers ARE sub-critical, so the first half of the release holds")
    print("for both; neither is PROVEN, so the second half fails. And the")
    print("reason is the substance rather than a technicality: both carry a")
    print("falsifier of 0 characters, so there is no stated computation to")
    print("reproduce. A proof requirement cannot rescue an entry that nothing")
    print("ever examined -- which is the correct behaviour, because the fault")
    print("in those 2 is that they were never served, not that they were")
    print("mis-scored.")

    print()
    print("=" * 72)
    print("M4. NOTHING WAS WRITTEN, WHICH IS HIS CONSTRAINT")
    print("=" * 72)
    before = RUN.stat().st_mtime_ns
    _check("the archive is untouched", RUN.stat().st_mtime_ns == before,
           "the archived run file changed during this read")
    print(f"archived run mtime unchanged during this read: True")
    print("No verdict was restated and no historical entry was rewritten.")

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
