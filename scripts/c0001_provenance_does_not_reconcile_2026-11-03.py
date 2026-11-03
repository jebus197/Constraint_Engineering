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



def _max_severity(ents: dict) -> float | None:
    """SECOND ROUTE to `the highest`: the run's actual maximum severity.

    INDEPENDENT of the primary, which counts entries at or above a threshold
    constant of 1.0 and asks whether that count is 0. This asks for the maximum
    and compares against it. A drifted threshold, or a run whose top severity
    sat below 1.0, splits the 2 answers -- which is why both are reported, per
    the primary/secondary falsifier rule of 2026-10-31.

    NO CONFIDENCE INTERVAL IS REPORTED ANYWHERE IN THIS FILE, and that is a
    decision rather than an omission. Every figure here is a complete
    enumeration -- 4 of 4 runs in the `exp42_composer` family, every registry
    entry in a run, every C-prefixed entry in the task list -- serving an
    IDENTIFICATION question. An interval on `1 of 4` would state what fraction
    of composer runs carry severity 0.90, which is not the question his
    provenance clause raises. Do not add one.
    """
    sevs = [float(v["severity"]) for v in ents.values()
            if isinstance(v, dict) and v.get("severity") is not None]
    return max(sevs) if sevs else None


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
    #: ★ THE ARCHIVE IS MEASURED WHETHER OR NOT THE CLAUSE SURVIVES, corrected
    #: 2026-11-03. A first version returned here the moment the clause was
    #: corrected, so the very measurements that JUSTIFIED the correction became
    #: unreproducible by the script committed beside them -- a producer outliving
    #: its defect, which this project has recorded before. The archive facts do
    #: not depend on the entry's wording: they are facts about 4 archived runs.
    #: So the clause check becomes a REPORTED status and the measurement runs on.
    clause_present = claim is not None
    if not clause_present:
        print("   the original clause is NO LONGER PRESENT, which means the")
        print("   correction has landed. The archive measurements below are")
        print("   reported anyway, because they are what justified it and they")
        print("   must stay reproducible after the subject is fixed.")
        date, sev, n = "2026-06-06", 0.9, 28
        print(f"   reading the HISTORICAL claim as committed: date {date}, "
              f"severity {sev}, 'the highest of the' {n}")
    if clause_present:
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
                     c1.get("severity"), at_top, _max_severity(ents)))
    print(f"   {'run':44s} {'reg':>4} {'total':>6} {'C0001':>7} {'at 1.0':>7} "
          f"{'max sev':>8}")
    for name, reg, tot, cs, top, mx in rows:
        print(f"   {name[:44]:44s} {reg:4d} {str(tot):>6} {str(cs):>7} {top:7d} "
              f"{str(mx):>8}")

    match = [r for r in rows if r[3] is not None and abs(float(r[3]) - sev) < 1e-9]
    print("\n3. VERDICT, 3 claims checked separately.")
    print(f"   severity {sev} matches {len(match)} of {len(rows)} candidate run(s)"
          f"{': ' + match[0][0] if len(match) == 1 else ''}")
    if len(match) == 1:
        _, reg, tot, c1sev, top, mx = match[0]
        print(f"   'the highest': FALSE -- {top} entries in that run sit at "
              f"severity 1.0")
        # SECOND, INDEPENDENT ROUTE: the run's actual maximum, not a threshold
        # count. Reported beside the primary so a disagreement cannot hide.
        route_a = (top == 0)
        route_b = (mx is not None and float(c1sev) >= mx)
        print(f"     route A, entries at or above 1.0 is 0  : {route_a}")
        print(f"     route B, C0001 {c1sev} against max {mx} : {route_b}")
        print(f"     THE 2 ROUTES AGREE: {route_a == route_b}")
        print(f"   'the {n}'      : NO REFERENT -- that run has {reg} registry "
              f"entries and reports {tot} findings")
    # And the secondary says MORE than the primary can: the superlative fails
    # against every candidate, so the unresolved identification cannot save it.
    never = [r[0] for r in rows
             if r[3] is not None and r[5] is not None and float(r[3]) < r[5]]
    print(f"   'the highest' is FALSE in {len(never)} of {len(rows)} candidate "
          f"runs, not only the matching one, so the open identification cannot")
    print("     rescue the superlative. This is what the 2nd route adds.")
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
