#!/usr/bin/env python3
"""D13: reproduce the rubric human-queue partition, and test whether the 4
remaining escalations are genuinely irreducible.

WHY THIS SCRIPT EXISTS
----------------------
The figures "roughly 82% of the disputed band is already tool-settled" and "the
genuine human queue is 4 of 33 rather than 259" were produced by panel reviewers
on 2026-09-04 and reported to the founder twice. Measured 2026-09-05: NO
COMMITTED SCRIPT REPRODUCED THEM. They existed only inside a panel transcript and
as prose in the operational tracker.

That is the same breach as the S_k gate figure found the same morning, and the
same rule: `measured-rate-travels-with-its-script`, founder ruling 2026-09-04.
A number nobody can recompute cannot support a decision about who does the work.

THE FOUNDER'S TWO QUESTIONS, WHICH THIS SCRIPT EXISTS TO ANSWER
---------------------------------------------------------------
Verbatim, 2026-09-05:

  "You are asking me to adjudicate? Again too vague. Or the models will
   adjudicate? And are those 4 HIL escalations genuinely irreducible, given
   everything we have discussed in the past?"

QUESTION 1 -- who adjudicates? NEITHER, and that is the finding. The separating
test is a LOOKUP IN THE EXISTING SCHEMA, not a judgement by anyone:

  1. falsifier_verdict in {CONFIRMED, REFUTED}  -> DECIDED. The runner already
     re-executed it. A rubric-versus-numeric disagreement about severity
     LABELLING is downstream of a settled existence question.
  2. status == MERGED                           -> DECIDED by the parent.
     Adjudicating a duplicate twice is double-counting.
  3. falsifier_verdict in {ERROR, UNTOOLABLE}   -> EQUIPMENT, not a person.
     The equipment-failure guard routes these to re-instrumentation. Sending a
     broken instrument to a human is queue inflation.
  4. no falsifier and none commissionable       -> QUEUE.

Only class 4 reaches a person, and it reaches them as a DECISION (commission a
falsifier, or accept the finding as-is), never as a judgement about severity.

QUESTION 2 -- are the 4 irreducible? NO, AND THE PANEL SAID SO WITHOUT SAYING SO.
Its own wording files them as "a residual named and bounded, whose own claim is
'commission falsifiers for these four'". A residual with an open action against
it is a TO-DO, not a floor. This script prints the 4 with their run and finding
id so the commissioning question can actually be asked of each one. That matters
because the standing project position is HIL-is-by-design with a MINIMAL-HIL
target and never a zero-HIL target: 4 is only defensible as a floor if each of
the 4 has been shown untoolable, and none has.

WHAT THIS SCRIPT CANNOT DO. It resolves audit items to live registry entries by
(run directory, canonical id). Where an archived run predates the
`falsifier_verdict` field entirely, the entry is reported as SCHEMA_PREDATES and
excluded rather than counted as "no falsifier" -- counting a missing field as a
missing falsifier would be a schema artefact reported as a measurement, which is
the error this project keeps finding.

Usage:
    python3 scripts/reproduce_rubric_human_queue_partition.py [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT = (REPO_ROOT / "experimental_notes" / "adversarial_records"
         / "rubric_adherence_audit_0C8_2026-09-02.json")
LOGS = REPO_ROOT / "bench" / "logs"

CRITICAL_SEVERITY_THRESHOLD = 0.7   # live value in reference_runner_v3.py
TOOL_SETTLED = {"CONFIRMED", "REFUTED"}
EQUIPMENT = {"ERROR", "UNTOOLABLE"}


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _walk_entries(obj):
    """Yield dicts that look like registry entries (carry a canonical id)."""
    if isinstance(obj, dict):
        if any(k in obj for k in ("canonical_id", "finding_id", "cid")):
            yield obj
        for v in obj.values():
            yield from _walk_entries(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_entries(v)


def build_registry_index():
    """Map (run_dir_name, canonical_id) -> entry, across every archived report."""
    index = {}
    runs_with_field = set()
    for path in sorted(LOGS.rglob("*.json")):
        run = path.parent.name
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        for e in _walk_entries(data):
            cid = e.get("canonical_id") or e.get("finding_id") or e.get("cid")
            if not isinstance(cid, str):
                continue
            if "falsifier_verdict" in e:
                runs_with_field.add(run)
            index.setdefault((run, cid), e)
    return index, runs_with_field


def classify(entry, run, runs_with_field):
    """The 4-way lookup. Returns (class_letter, label)."""
    if entry is None:
        return ("UNRESOLVED", "audit item did not resolve to a registry entry")
    fv = entry.get("falsifier_verdict")
    if fv is None:
        if run not in runs_with_field:
            return ("SCHEMA_PREDATES",
                    "this run's schema has no falsifier_verdict field at all")
        return ("D", "no falsifier produced -> genuine human queue")
    if fv in TOOL_SETTLED:
        return ("A", f"already tool-settled (falsifier {fv})")
    if str(entry.get("status", "")).upper() == "MERGED":
        return ("B", "settled by merge; the parent's verdict governs")
    if fv in EQUIPMENT:
        return ("C", f"instrument fault ({fv}) -> re-instrumentation, not a person")
    return ("D", f"no usable falsifier verdict ({fv!r})")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not AUDIT.is_file():
        print(f"missing audit file: {AUDIT}", file=sys.stderr)
        return 2

    audit = json.loads(AUDIT.read_text())
    first = audit["first_pass"]
    gt = audit["ground_truth"]

    judgeable = [x for x in first if x.get("verdict") != "UNJUDGEABLE"]
    n_judgeable = len(judgeable)

    agree = disagree = 0
    disagreements = []
    for row in judgeable:
        i = str(row["item"])
        if i not in gt:
            continue
        severity, run, cid = gt[i]
        numeric_critical = float(severity) >= CRITICAL_SEVERITY_THRESHOLD
        reader_critical = row["verdict"] == "CRITICAL"
        if numeric_critical == reader_critical:
            agree += 1
        else:
            disagree += 1
            disagreements.append({"item": int(i), "severity": float(severity),
                                  "run": run, "cid": cid,
                                  "reader": row["verdict"]})

    lo, hi = wilson(agree, agree + disagree)
    print("D13 — rubric human-queue partition, reproduced")
    print("=" * 68)
    print(f"  audit items                : {len(first)}")
    print(f"  UNJUDGEABLE                : {len(first) - n_judgeable}")
    print(f"  judgeable                  : {n_judgeable}")
    print(f"  reader agrees with numeric : {agree} = {100.0*agree/(agree+disagree):.2f}%"
          f"  Wilson 95% [{100*lo:.1f}%, {100*hi:.1f}%]")
    print(f"  DISAGREEMENTS              : {disagree}   <- the disputed band")
    print()

    index, runs_with_field = build_registry_index()
    print(f"  archived runs carrying falsifier_verdict: {len(runs_with_field)}")

    buckets = Counter()
    queue = []
    for d in disagreements:
        entry = index.get((d["run"], d["cid"]))
        letter, why = classify(entry, d["run"], runs_with_field)
        buckets[letter] += 1
        d["class"] = letter
        d["why"] = why
        if letter == "D":
            queue.append(d)

    era = [d for d in disagreements if d["class"] not in ("SCHEMA_PREDATES", "UNRESOLVED")]
    n_era = len(era)
    print(f"  disagreements in the falsifier era      : {n_era}")
    print(f"  excluded, schema predates the field     : {buckets['SCHEMA_PREDATES']}")
    print(f"  excluded, did not resolve               : {buckets['UNRESOLVED']}")
    print()
    print("  THE 4-WAY LOOKUP (a schema lookup, NOT an adjudication by anyone)")
    for letter, name in [("A", "already tool-settled"),
                         ("B", "settled by merge"),
                         ("C", "instrument fault -> re-instrumentation"),
                         ("D", "no falsifier -> genuine human queue")]:
        k = buckets[letter]
        if n_era:
            l2, h2 = wilson(k, n_era)
            print(f"    {letter}  {name:38s} {k:3d}  {100.0*k/n_era:5.1f}%"
                  f"  Wilson [{100*l2:.1f}%, {100*h2:.1f}%]")
        else:
            print(f"    {letter}  {name:38s} {k:3d}")
    print()
    settled = buckets["A"] + buckets["B"] + buckets["C"]
    if n_era:
        print(f"  PROGRAMMATICALLY DECIDED: {settled} of {n_era} = {100.0*settled/n_era:.1f}%")
        print(f"  REACHES A HUMAN         : {buckets['D']} of {n_era}")
    print()
    print("  ARE THE HUMAN-QUEUE ITEMS IRREDUCIBLE? Each is listed so the")
    print("  commissioning question can be asked of it individually. An item is")
    print("  irreducible ONLY if a falsifier cannot be written for it; none of")
    print("  these has been shown untoolable, so they are a TO-DO, not a floor.")
    for d in queue:
        print(f"    item {d['item']:>4}  severity {d['severity']:.2f}  "
              f"{d['run']}  {d['cid']}  reader={d['reader']}")
    if not queue:
        print("    (none in the falsifier era)")

    if args.json:
        print(json.dumps({"agree": agree, "disagree": disagree,
                          "buckets": dict(buckets), "queue": queue}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
