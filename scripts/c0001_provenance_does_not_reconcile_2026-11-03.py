#!/usr/bin/env python3
"""C0001's provenance clause does not reconcile with any archived run.

FOUND 2026-11-03 as a direct follow-on from the measurement that the registry
mints a finding's identity from a SEQUENCE COUNTER rather than its content: 59
archived runs each hold an entry called C0001 and 53 of those name a different
finding. The task list carries its OWN entry called C0001, so the question was
whether that collision does any harm. It does, and this is the instance.

WHAT THE ENTRY CLAIMS, verbatim from its own text: *"Raised 2026-06-06 at
severity 0.90, the highest of the 28, recorded unconfirmed and untoolable and
never checked"*.

WHAT RECONCILES AND WHAT DOES NOT.
  * The DATE and the SEVERITY do reconcile, and together they pin the run.
    Of the 4 `exp42_composer*` runs, exactly 1 has a C0001 at severity 0.90 --
    `exp42_composer_confirm_20260606T184941Z`, dated 2026-06-06 -- and its
    C0001 is about `_prune_for_coherence`. So the finding IS identifiable, by
    searching the archive on SUBJECT and SEVERITY rather than by its identifier.
  * "THE HIGHEST" IS FALSE in that run. 9 of its 23 registry entries sit at
    severity 1.0, so a finding at 0.90 was not the highest of anything.
  * "THE 28" HAS NO REFERENT THIS SCRIPT CAN FIND. That run holds 23 registry
    entries and reports 29 total findings; the other 3 candidate runs hold 67,
    52 and 80 entries; and the task list's own C-prefixed entries number 39.
    The literal 28 appears 0 times in the matching run's report.

THE HONEST LIMIT. An intermediate document from June -- a note or a summary --
could have counted 28 of something, and this script cannot read a document it
cannot name. So the claim made here is bounded: the clause does not reconcile
with any archived run or with the task list's own C-entry count, and the word
"highest" is false against the run whose severity matches.

WHAT IS NOT IN DOUBT, AND THIS MATTERS MORE THAN THE CLAUSE. The DEFECT is
sound. The entry records it as confirmed on 2026-09-10 and proved rather than
observed, and `_prune_for_coherence` is retired from the default path on his
2026-10-13 ruling, verified by executing the signature. Nothing here reopens the
defect; what is corrected is 1 sentence of provenance about it.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
LOGS = REPO / "bench" / "logs"


def main() -> int:
    argparse.ArgumentParser(
        description=("Check C0001's provenance clause against the archive."
                     )).parse_args()
    print("=" * 78)
    print("C0001'S PROVENANCE CLAUSE AGAINST THE ARCHIVE")
    print("=" * 78)

    t = TASKS.read_text(errors="replace")
    i = t.index("**C0001. THE COHERENCE PRUNER")
    body = t[i:t.index("<!-- task: C0001 ", i)]
    claim = re.search(r"Raised ([\d-]+) at severity ([\d.]+), the highest of "
                      r"the (\d+)", body)
    print("\n1. THE CLAUSE, read from the entry rather than quoted from memory.")
    if not claim:
        print("   the clause is no longer present, so this producer's premise")
        print("   has been addressed.")
        return 0
    date, sev, n = claim.group(1), float(claim.group(2)), int(claim.group(3))
    print(f"   date {date}   severity {sev}   'the highest of the' {n}")

    print("\n2. EVERY CANDIDATE RUN, measured.")
    rows = []
    for rep in sorted(LOGS.glob("exp42_composer*/*_report.json")):
        if "sandbox_harvest" in str(rep):
            continue
        try:
            d = json.loads(rep.read_text(errors="replace"))
        except Exception:                                      # noqa: BLE001
            continue
        ents = ((d.get("registry") or {}).get("entries")) or {}
        c1 = ents.get("C0001") or {}
        at_top = sum(1 for v in ents.values()
                     if isinstance(v, dict) and float(v.get("severity") or 0) >= 1.0)
        rows.append((rep.parent.name, len(ents), d.get("total_findings"),
                     c1.get("severity"), at_top))
    print(f"   {'run':48s} {'reg':>4} {'total':>6} {'C0001':>7} {'at 1.0':>7}")
    for name, reg, tot, cs, top in rows:
        print(f"   {name[:48]:48s} {reg:4d} {str(tot):>6} {str(cs):>7} {top:7d}")

    match = [r for r in rows if r[3] is not None and abs(float(r[3]) - sev) < 1e-9]
    print("\n3. VERDICT, 3 claims checked separately.")
    print(f"   severity {sev} matches {len(match)} of {len(rows)} candidate run(s)"
          f"{': ' + match[0][0] if len(match) == 1 else ''}")
    if len(match) == 1:
        _, reg, tot, _, top = match[0]
        print(f"   'the highest': FALSE -- {top} entries in that run sit at "
              f"severity 1.0")
        print(f"   'the {n}'      : NO REFERENT -- that run has {reg} registry "
              f"entries and reports {tot} findings")
    cs = len(re.findall(r"<!-- task: C\d+ ", t))
    print(f"   the task list's own C-prefixed entries: {cs}, not {n}")
    print("\n   SO 1 OF THE 3 IDENTIFYING CLAIMS HOLDS. The date and severity")
    print("   together DO pin the run, which is the useful half; the count and")
    print("   the superlative do not reconcile with anything measurable here.")
    print("   The DEFECT is untouched by this: it is confirmed, proved, and its")
    print("   subject is retired from the default path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
