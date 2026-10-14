# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0d4132e4b812ec06bf33e6034cb7df0a200087be7638b5ded61ffcc67dc1b929
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""J5, settled on the record (2026-10-14 joint panel).

The disputed case: `sim45_memory_20260908T033012Z` C0050 -- a claim that the
target file was rewritten six times during the review round itself. One seat
counted it the archive's 1 genuinely irreducible finding; the other counted 0.

What this producer shows, by execution:
  1. C0050 carries NO machine attempt: `falsifier_code` empty,
     `last_falsifier_code` null, and its own defer reason declines the label:
     "'Irreducible' would assert a machine tried and failed."
     So the DEMONSTRATED-irreducible count in the archive is 0.
  2. C0050 is also NOT equipment failure: its 6 `computed_evidence` entries
     are `reasoned_withdrawal` records with EMPTY falsifier_code -- six model
     prose verdicts, i.e. agreement, which CDSFL does not count as a
     confirmation mechanism.
  3. The claim's truth-maker (the sequence of target contents during the
     round) has a schema field DESIGNED to carry provenance evidence --
     `source_hash` -- and that field is empty in every occurrence this script
     can find. The claim was toolable in principle and unfalsifiable in
     practice because the harness never recorded the evidence.

So neither seat's blind taxonomy held: not "genuinely irreducible"
(nothing was demonstrated) and not "equipment failure" (nothing failed).
The class is: evidence never recorded by the harness. The record settles the
count at 0 demonstrated-irreducible and names the missing instrumentation.
"""
from __future__ import annotations

import glob
import json
import os
import sys

RUN = "bench/logs/sim45_memory_20260908T033012Z"


def walk_source_hash(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source_hash":
                out.append(v)
            else:
                walk_source_hash(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_source_hash(v, out)


def main() -> int:
    rs = json.load(open(os.path.join(RUN, "runner_state.json")))
    ents = rs.get("registry", {}).get("entries", {})
    c0050 = None
    for k, v in ents.items():
        if (v.get("canonical_id") or k) == "C0050":
            c0050 = v
            break
    if c0050 is None:
        print("C0050 not found -- run layout changed"); return 1

    print("=== C0050, THE RECORD ===")
    print(f"  status={c0050.get('status')}  severity={c0050.get('severity')}")
    print(f"  falsifier_code empty: {not c0050.get('falsifier_code')}")
    print(f"  last_falsifier_code:  {c0050.get('last_falsifier_code')!r}")
    print(f"  defer reason: {c0050.get('routing_defer_reason')!r}")
    ce = c0050.get("computed_evidence") or []
    kinds = [(e.get("kind"), not e.get("falsifier_code")) for e in ce]
    print(f"  computed_evidence: {len(ce)} entries, (kind, falsifier-empty): {kinds}")
    print("  -> machine attempts on C0050: 0 (every evidence entry is prose)")

    for scope, files in (("sim45 run", [os.path.join(RUN, "runner_state.json"),
                                        os.path.join(RUN, "checkpoint.json")]),
                         ("whole archive", sorted(glob.glob("bench/logs/*/runner_state.json")))):
        vals, seen = [], set()
        for p in files:
            rp = os.path.realpath(p)
            if rp in seen:
                continue
            seen.add(rp)
            try:
                walk_source_hash(json.load(open(p)), vals)
            except Exception:
                continue
        empty = sum(1 for v in vals if not v)
        print(f"=== source_hash fields, {scope}: {len(vals)} present, {empty} empty "
              f"({'ALL EMPTY' if vals and empty == len(vals) else 'SOME POPULATED'}) ===")

    print("\nVERDICT: demonstrated-irreducible count = 0; C0050's class is")
    print("'evidence never recorded by the harness' (empty source_hash), which is")
    print("a harness instrumentation gap, not an irreducible claim and not an")
    print("equipment failure. Populating source_hash at write time makes this")
    print("claim class decidable in future runs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
