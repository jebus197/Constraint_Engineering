#!/usr/bin/env python3
"""Why 6 of 17 findings on a PROSE target came back UNTOOLABLE.

THE FOUNDER'S DESIGN, 2026-09-10. A target that is purely prose should be
recorded as having nothing to compute; any computationally accessible element
INSIDE a prose target should still be solved. His concern, restated 2026-09-22:
STEM material that also contains prose must not be written off as inadvisable
merely because prose surrounds it.

WHAT ARM 4 MEASURES. `commissioning_arm4_prose` ran 5 simulated seats against
`bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md` -- a written specification, not a
program. It is therefore the only archived run that exercises the prose path on
real data, and its registry records, per finding, the falsifier verdict, how
many routing rungs were tried, how many were available, and the last falsifier
source the ladder produced.

WHAT THIS SCRIPT ESTABLISHES, each measured rather than asserted.

1. THE PROSE PATH WORKS. The count of CONFIRMED verdicts on a prose target is
   not 0. Computable content inside prose WAS found and WAS falsified, which is
   the founder's design already operating.

2. UNTOOLABLE IS NOT "NOTHING TO COMPUTE". For each UNTOOLABLE entry this
   reports whether the routing ladder had produced falsifier source before
   giving up. Source produced but not stored is a mechanical loss, not a
   statement that the finding was uncomputable.

   THE RECORDED SOURCE IS TRUNCATED AND THIS SCRIPT SAYS SO RATHER THAN
   COUNTING IT. Every `last_falsifier_code` in this report is EXACTLY 600
   characters, none ends in a newline, and every one is cut mid-token -- so 600
   is a recorder ceiling, not a measurement of how much code was written. The
   claim this supports is therefore only that source EXISTED, never that it was
   complete or that it would have run. Asserted the other way round, "6 entries
   produced 600 bytes of falsifier" would be a fact about the archiver
   masquerading as a fact about the panel.

3. THE LADDER STOPS SHORT OF WHAT IT HAS. `rungs_tried` against
   `rungs_available` per entry. A ladder that stops at 2 of 5 has not
   established that rungs 3 to 5 would have failed.

Every proportion carries a Wilson and a Clopper-Pearson interval, from 2
independent routes, per `multi_tool_crossverify`.

Run:  python3 scripts/arm4_untoolable_anatomy_2026-09-22.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN = REPO / "bench" / "logs" / "commissioning_arm4_prose_20260922T053349Z"
REPORT = RUN / "commissioning_arm4_prose_report.json"


def interval(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    w = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    return w, cp


def pct(k: int, n: int, label: str) -> None:
    if not n:
        print(f"    {label}: no denominator")
        return
    (wlo, whi), (clo, chi) = interval(k, n)
    print(f"    {label}: {k}/{n} = {100*k/n:.4f}%")
    print(f"        Wilson 95%          [{100*wlo:.4f}%, {100*whi:.4f}%]")
    print(f"        Clopper-Pearson 95% [{100*clo:.4f}%, {100*chi:.4f}%]")


def main() -> int:
    if not REPORT.is_file():
        print(f"no arm 4 report at {REPORT}", file=sys.stderr)
        return 2
    d = json.loads(REPORT.read_text())
    ents = d["registry"]["entries"]
    n = len(ents)

    print("ARM 4 — the prose target, finding by finding")
    print(f"  target   : {d.get('experiment')}")
    print(f"  entries  : {n}")
    print()

    verdicts: dict[str, int] = {}
    for e in ents.values():
        v = (e.get("falsifier_verdict") or "(none)").strip() or "(none)"
        verdicts[v] = verdicts.get(v, 0) + 1
    print("  VERDICT DISTRIBUTION")
    for v, k in sorted(verdicts.items(), key=lambda x: -x[1]):
        print(f"    {v:14} {k}")
    print()

    confirmed = verdicts.get("CONFIRMED", 0)
    print("  1. DOES THE PROSE PATH PRODUCE ANY VERDICT AT ALL?")
    pct(confirmed, n, "CONFIRMED on a prose target")
    if confirmed:
        print("      -> computable content inside prose WAS found and falsified.")
        print("         The prose path is not inert; the founder's design operates.")
    print()

    print("  2. UNTOOLABLE ENTRIES: WAS SOURCE PRODUCED BEFORE GIVING UP?")
    unt = {c: e for c, e in ents.items()
           if (e.get("falsifier_verdict") or "").strip() == "UNTOOLABLE"}
    had_source = 0
    for cid, e in sorted(unt.items()):
        rh = e.get("routing_history") or []
        last = ""
        tried = avail = None
        for s in rh:
            if isinstance(s, dict):
                last = s.get("last_falsifier_code") or last
                tried = s.get("rungs_tried", tried)
                avail = s.get("rungs_available", avail)
        stored = len(e.get("falsifier_code") or "")
        if last.strip():
            had_source += 1
        trunc = "TRUNCATED@600" if len(last) == 600 and not last.endswith("\n") else f"{len(last)}ch"
        print(f"    {cid}: stored_code={stored:5}  source_in_record={trunc:>13}  "
              f"rungs {tried}/{avail}")
    print()
    pct(had_source, len(unt), "UNTOOLABLE entries with falsifier source in the record")
    if had_source:
        print("      -> source EXISTED and reached no stored falsifier_code.")
        print("         NARROWED 2026-09-22 after the paid seat `ge` refuted the")
        print("         stronger reading. Generated source proves only that the model")
        print("         ATTEMPTED a falsifier; a model can emit plausible code for a")
        print("         claim that is not computable at all. So this establishes that")
        print("         an attempt was made and discarded -- NOT that the target held")
        print("         computable content. Settling that would mean EXECUTING the")
        print("         source, which this archive forbids: it is truncated at 600.")
    # the truncation, stated as a measurement rather than a caveat
    allc = [s.get("last_falsifier_code") or ""
            for e in ents.values() for s in (e.get("routing_history") or [])
            if isinstance(s, dict) and s.get("last_falsifier_code")]
    at600 = sum(1 for c in allc if len(c) == 600 and not c.endswith("\n"))
    print()
    pct(at600, len(allc), "recorded falsifier bodies cut at exactly 600 chars")
    if allc and at600 == len(allc):
        print(f"      -> {len(set(allc))} DISTINCT bodies, every one exactly 600 chars and")
        print("         none ending in a newline. 600 is the recorder's ceiling. No")
        print("         claim about falsifier SIZE or completeness is available here.")
    print()

    print("  3. DID THE LADDER EXHAUST WHAT IT HAD?")
    # CORRECTED 2026-09-22 after the paid seat `cx` refuted the first version.
    # That version printed rungs ONLY for the 6 UNTOOLABLE entries, saw 2/5 in
    # every one, and generalised to "all 11 episodes are 2/5". C0014 is 1/5.
    # The count it reported -- 11 of 11 stopped before exhausting the rungs --
    # was true but MISLEADING, because stopping early is SUCCESS for an entry
    # that resolved and FAILURE for one that did not. Pooling them measures
    # nothing. The cap claim belongs only to the episodes that never resolved.
    import collections
    dist: collections.Counter = collections.Counter()
    unresolved_at_cap = unresolved = resolved_early = 0
    for cid, e in ents.items():
        verdict = (e.get("falsifier_verdict") or "").strip()
        for s in (e.get("routing_history") or []):
            if not isinstance(s, dict) or s.get("rungs_available") is None:
                continue
            tried, avail = s.get("rungs_tried") or 0, s["rungs_available"]
            dist[(tried, avail)] += 1
            if verdict == "CONFIRMED":
                if tried < avail:
                    resolved_early += 1
            else:
                unresolved += 1
                if tried < avail:
                    unresolved_at_cap += 1
    print("    rungs_tried/rungs_available distribution:")
    for (tr, av), c in sorted(dist.items()):
        print(f"      {tr}/{av}: {c}")
    print()
    print(f"    episodes that RESOLVED without using every rung : {resolved_early}")
    print("      -> for these the early stop is the ladder WORKING. Counting them")
    print("         as evidence of a cap is the error the first version made.")
    print()
    pct(unresolved_at_cap, unresolved,
        "UNRESOLVED episodes that stopped with rungs still available")
    if unresolved_at_cap:
        print("      -> THIS is the cap claim, and only this. These episodes ended")
        print("         without a verdict while untried rungs remained, so nothing")
        print("         here establishes that the remaining rungs would have failed.")
        print("      -> corroborated independently: the 2026-09-21 adjudication")
        print("         (scripts/panel_adjudication_cc_seat_2026-09-21.py, A6) finds")
        print("         max_rungs defaults to 2 with no config surface, and that NO")
        print("         archived run has ever entered rung 3 -- so what rung 3 buys")
        print("         is unmeasured rather than known to be nothing.")

    return 0


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
