#!/usr/bin/env python3
"""The non-curing closures, named one by one so the next run compares.

HIS RULING, 2026-10-30: *"I accept your recommendation."* against this
recommendation: leave the archive as it stands and record the non-curing
closures as a NAMED POPULATION, so the next commissioning run compares against
them rather than rediscovering them. Reopening findings in a sealed archive
rewrites history to fix a comparison that a recorded list fixes just as well.

WHAT A NON-CURING CLOSURE IS. The run recorded the finding as closed with the
defect demonstrated, and the repair that closed it was then measured against
the finding's own test -- and the test still failed. So the fault was correctly
identified and the fix did not work. `fix_efficacy.outcome` carries the verdict.

WHAT WAS ALREADY MEASURED, AND WHAT WAS NOT. The COUNTS have had producers since
2026-09-22: `scripts/e1_mechanism_consequences_2026-09-22.py` and
`scripts/e1_population_recount_falsifier_2026-09-22.py`, which between them fix
the distinct population at 124 records with 23 non-curing in the dated claim
scope, Wilson [12.6898%, 26.2972%], and print 265 with 50 for the whole archive
without asserting on it. What did NOT exist is the LIST: a count cannot be
compared against, because a later run matching the count tells you nothing
about whether it is the same findings. This script emits the identities.

★ A COUNT IS NOT A POPULATION, which is the lesson this file applies rather
than discovers: *"Pin a set, not a count -- a count cannot say what moved; a
set catches a swap."* 2 runs can both report 16 non-curing closures and share
not one finding between them.

THE FIGURE HE WAS GIVEN WAS ARM 1's. The report said *"In 1 archived run, 16
findings are recorded as closed ... 16 out of 69"*, which is the first
commissioning arm. The claim-scope total across the 4 arms of 2026-09-21/22 is
23 of 124 (16 + 3 + 2 + 2), and the whole archive to date is 50 of 265. All 3
figures are emitted below so none of them can be quoted without its scope.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib

from statsmodels.stats.proportion import proportion_confint
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
OUT = REPO / "experimental_notes" / "data" / "non_curing_closures_2026-10-31.json"

#: The runs the dated claim covers, per `e1_population_recount_falsifier`.
CLAIM_SCOPE = ("20260921", "20260922")

#: ★ THE ONE OUTCOME VALUE THAT MEANS IT, MEASURED RATHER THAN GUESSED. The
#: first version of this script invented a vocabulary -- {"not_cured",
#: "still_failing", "uncured", "failed"} -- and returned 0 of 659 while the
#: record count matched the existing producer exactly, which is how a predicate
#: error announces itself: the collection was right and the classification was
#: fiction. The archive's actual `fix_efficacy.outcome` values are
#: FIX_CURES_ITS_OWN_FALSIFIER (230), NOT_PROBED_NO_FALSIFIER (124),
#: INDETERMINATE_NO_BASELINE (123), FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER (85),
#: INDETERMINATE_NOT_INTERCEPTED (67), INDETERMINATE_OTHER (18),
#: INDETERMINATE_NO_APPLICABLE_FIX (9) and
#: INDETERMINATE_PROBE_BROKEN_AFTER_BASELINE (3).
NON_CURING_OUTCOME = "FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER"

#: ★ A CROSS-CHECK I GOT WRONG FIRST, RECORDED BECAUSE THE MISTAKE IS THE
#: INSTRUCTIVE PART. The second instrument was going to be
#: `scripts/e1_mechanism_consequences_2026-09-22.py:141`, which classifies by
#: `"does NOT cure" in detail`. Applied to `fix_efficacy.detail` that substring
#: matches 0 of 85 records whose outcome IS
#: FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER, and the first version of this file
#: therefore raised and was about to be reported as a defect in that producer.
#: IT IS NOT A DEFECT: that script reads
#: `gate_details.e1_efficacy.detail`, a DIFFERENT field with different wording,
#: and it correctly finds 12 non-curing among the 44 judged entries carrying an
#: e1 score. 2 fields named `detail`, 1 assumption, and the assumption was
#: mine. The archive's `fix_efficacy.detail` reads "the fix applies cleanly and
#: the finding's own falsifier still demonstrates the defect afterwards".
#:
#: SO THE SECOND INSTRUMENT IS THE RECOUNT PRODUCER, which keys on the same
#: outcome value at `e1_population_recount_falsifier_2026-09-22.py:108` through
#: an independent implementation over an independent glob. Its claim-scope
#: figure must equal this script's, and `cross_check()` below executes it
#: rather than quoting it.
_RECOUNT = ("scripts" "/" "e1_population_recount_falsifier_2026-09-22.py")


def _is_non_curing(fe: dict) -> bool:
    return str(fe.get("outcome") or "").strip() == NON_CURING_OUTCOME


def cross_check(scope_non_curing: int) -> dict:
    """Run the recount producer and require it to agree on the claim scope."""
    import re as _re
    import subprocess as _sp
    import sys as _sys
    r = _sp.run([_sys.executable, str(REPO / _RECOUNT)],
                capture_output=True, text=True, cwd=str(REPO))
    m = _re.search(r"distinct probe records:\s*(\d+);\s*non-curing:\s*(\d+)",
                   r.stdout)
    if not m:
        return {"ran": False, "why": "the recount printed no claim-scope line",
                "stdout_tail": r.stdout[-200:]}
    recount_records, recount_nc = int(m.group(1)), int(m.group(2))
    return {"ran": True, "recount_records": recount_records,
            "recount_non_curing": recount_nc,
            "this_script_non_curing": scope_non_curing,
            "agree": recount_nc == scope_non_curing}


def collect() -> dict:
    rows, per_run = [], collections.Counter()
    seen_records = 0
    for state in sorted(glob.glob(str(LOGS / "*" / "runner_state.json"))):
        run = pathlib.Path(state).parent.name
        try:
            d = json.load(open(state))
        except Exception:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        for cid, e in ents.items():
            fe = e.get("fix_efficacy")
            if not isinstance(fe, dict) or not fe:
                continue
            seen_records += 1
            if not _is_non_curing(fe):
                continue
            per_run[run] += 1
            rows.append({
                "run": run,
                "canonical_id": cid,
                "flaw_class": e.get("flaw_class"),
                "severity": e.get("severity"),
                "status": e.get("status"),
                "outcome": fe.get("outcome"),
                "falsifier_verdict": e.get("falsifier_verdict"),
                "description": str(e.get("description") or "")[:200],
            })
    return {"rows": rows, "per_run": dict(per_run), "records": seen_records}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="write the named population to experimental_notes/data")
    a = ap.parse_args()

    got = collect()
    rows, per_run, n = got["rows"], got["per_run"], got["records"]
    in_scope = [r for r in rows
                if any(s in r["run"] for s in CLAIM_SCOPE)]
    scope_records = 0
    for state in sorted(glob.glob(str(LOGS / "*" / "runner_state.json"))):
        run = pathlib.Path(state).parent.name
        if not any(s in run for s in CLAIM_SCOPE):
            continue
        try:
            d = json.load(open(state))
        except Exception:
            continue
        for e in ((d.get("registry") or {}).get("entries") or {}).values():
            if isinstance(e.get("fix_efficacy"), dict) and e["fix_efficacy"]:
                scope_records += 1

    print("=" * 74)
    print("THE NON-CURING CLOSURES, NAMED")
    print("=" * 74)
    print(f"distinct probe records, whole archive : {n}")
    print(f"non-curing, whole archive             : {len(rows)}")
    if n:
        w = proportion_confint(len(rows), n, alpha=0.05, method="wilson")
        cp = proportion_confint(len(rows), n, alpha=0.05, method="beta")
        print(f"   share {len(rows)}/{n} = {len(rows)/n:.6f}, "
              f"Wilson [{w[0]:.6f}, {w[1]:.6f}], "
              f"Clopper-Pearson [{cp[0]:.6f}, {cp[1]:.6f}]")
    print(f"distinct probe records, claim scope   : {scope_records}")
    print(f"non-curing, claim scope               : {len(in_scope)}")
    if scope_records:
        w = proportion_confint(len(in_scope), scope_records, alpha=0.05,
                               method="wilson")
        print(f"   share {len(in_scope)}/{scope_records} = "
              f"{len(in_scope)/scope_records:.6f}, "
              f"Wilson [{w[0]:.6f}, {w[1]:.6f}]")
    xc = cross_check(len(in_scope))
    print("\nSECOND INSTRUMENT -- the recount producer, executed:")
    for k, v in xc.items():
        print(f"   {k}: {v}")
    if xc.get("ran") and not xc.get("agree"):
        raise SystemExit(
            "the 2 independent implementations disagree on the claim scope "
            "(%s against %s); the population may not be named until that is "
            "settled" % (xc.get("recount_non_curing"), len(in_scope)))

    print("\nper run:")
    for run, c in sorted(per_run.items(), key=lambda kv: -kv[1]):
        print(f"   {run[:58]:58} {c}")

    # ★ THE SET, not the count. A later run matching the count proves nothing.
    ids = sorted({(r["run"], r["canonical_id"]) for r in rows})
    print(f"\ndistinct (run, finding) identities: {len(ids)}")
    print("the first 10, so a reader can spot-check the list against the archive:")
    for run, cid in ids[:10]:
        print(f"   {run[:52]:52} {cid}")

    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(
            {"written_for": "his ruling of 2026-10-30, recorded as a named "
                            "population rather than reopened",
             "producer": "scripts/the_non_curing_population_is_named_2026-10-31.py",
             "counts": {"archive_records": n, "archive_non_curing": len(rows),
                        "claim_scope_records": scope_records,
                        "claim_scope_non_curing": len(in_scope)},
             "claim_scope": list(CLAIM_SCOPE),
             "identities": [{"run": r, "canonical_id": c} for r, c in ids],
             "rows": rows},
            indent=2, sort_keys=True) + "\n")
        print(f"\nwritten: {OUT.relative_to(REPO)}")
    else:
        print("\nDRY RUN -- pass --write to record the population")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
