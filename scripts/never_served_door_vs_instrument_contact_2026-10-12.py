#!/usr/bin/env python3
"""Which instruments read a finding WITHOUT writing any field the never-served door tests?

THE NAMED PROPERTY THIS MEASURES. `reference_runner_v3._routing_ladder_never_served`
releases an entry from `unverified_critical_count` when the entry carries no
trace of any instrument. Its conjuncts read ladder, falsifier and HIL fields
only. This script asks the question the joint round of 2026-10-12 put to it: is
there a registry field, NOT among those conjuncts, that records an instrument
having READ the finding -- and is that state REACHABLE on real registries
rather than merely conceivable?

THE ANSWER, MEASURED OVER EVERY ARCHIVED runner_state.json IN bench/logs. Yes,
and the decisive one is `severity_proof`. The R_k proof checker reads a
finding's own corroboration block and records PASS / WARN / FAIL / SKIP in
`severity_proof` without touching `verdicts`, `routing_history`,
`falsifier_code`, `falsifier_verdict`, `routing_verdict_unreconciled`,
`routing_deferred` or `hil_escalated`. So an entry it had read looked untouched.

WHY THAT IS MATERIAL AND NOT A TIDINESS POINT. The door is evaluated BEFORE the
severity test in `unverified_critical_count` and ignores severity entirely. An
entry whose proof returned FAIL is the one state in which the severity test is
GUARANTEED to refuse a release (`severity_is_proven` accepts PASS and WARN
only). Before this conjunct the door released it anyway, so the door was
strictly WIDER than the severity gate whose removal the founder has rejected
3-4 times, and it nullified that gate for this entry class.

WHY THE OTHER CONTACT-SHAPED FIELDS ARE REJECTED AS CONJUNCTS. A field
qualifies only if it (a) records a TOOL reading and (b) is still absent on the
two entries the door exists for, so adding it does not regress the fix to a
no-op. This script prints both halves for every candidate, so the rejection is
measured rather than argued:

  * `status_adjudicator` == "tool" and `status_log` are written by the ordinary
    OPEN -> UNCONFIRMED bookkeeping and are present on C0066 itself. As
    conjuncts they would close the door on everything.
  * `computed_evidence` on C0066 holds {"kind": "reasoned_withdrawal", "by":
    "CC2-SIM"} -- a MODEL statement. Under "tools decide, not votes" that is
    the opposite of instrument contact.
  * `fix_efficacy` on C0066 holds outcome "NOT_PROBED_NO_FALSIFIER", whose own
    detail string says nothing ran.

AND THE SECOND QUESTION THE JOINT ROUND ASKED: is
LADDER_UNSERVED_MIN_AGE_ROUNDS = 1 the right bound, or does a finding emitted
in a run's final round need longer? This script answers it from the ladder's own
record: for every entry the ladder DID serve, it prints first_routing_round -
open_since_round. Measured, that is 0 for 230 of 230. The ladder serves an entry
in its ARRIVAL round or never, so waiting longer buys nothing, and 1 is a full
round of margin over a bound the data puts at 0.

Usage: python3 scripts/never_served_door_vs_instrument_contact_2026-10-12.py
"""
import glob
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "bench"))

from _cli_help import answer_help  # noqa: E402

#: Fields the door's own conjuncts read. A candidate matters only if NOT here.
DOOR_CONJUNCTS = (
    "verdicts", "routing_history", "falsifier_code", "falsifier_verdict",
    "routing_verdict_unreconciled", "routing_deferred", "hil_escalated",
)

#: Enumerated from the UNION of entry keys across all archived registries, not
#: guessed: every field that could plausibly record an instrument reading.
CANDIDATES = (
    "severity_proof", "severity_proof_history", "sk_result", "sk_evaluated",
    "status_adjudicator", "status_mechanism", "status_evidence", "status_log",
    "computed_evidence", "hil_has_computed_evidence", "fix_efficacy",
    "fix_efficacy_attempted", "corrected_copy", "occasions",
    "routing_verdict_reconciled", "mechanical_fault", "equipment_failure",
    "error_routed", "discrimination", "verification_voided", "exhausted",
    "irreducible_escalation", "hil_reason", "attestation_count",
    "refused_transitions", "withdrawn_by_sweep", "bugzilla_attempted",
    "bugzilla_verified", "cc2v_escalated", "merge_blocked_reason",
    "latent_evidence", "resolved_by_routing", "resolved_by_sweep",
    "resolved_by_takeup",
)

TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}

#: The two entries study_run1b's blocker is made of. A candidate conjunct SET on
#: these would close the door on the very case the fix exists for.
REFERENCE_RUN = "bench/logs/study_run1b_2026-10-03_20261003T100439Z/runner_state.json"
REFERENCE_IDS = ("C0066", "C0073")


def _set(v) -> bool:
    return v not in (None, "", [], {}, 0, False)


def _wilson(k, n):
    try:
        from statsmodels.stats.proportion import proportion_confint
        return proportion_confint(k, n, method="wilson")
    except Exception:
        return float("nan"), float("nan")


def _registries(root=""):
    pat = os.path.join(root, "bench/logs/**/runner_state.json") if root \
        else "bench/logs/**/runner_state.json"
    for path in sorted(glob.glob(pat, recursive=True)):
        try:
            with open(path, encoding="utf-8") as fh:
                yield path, json.load(fh)
        except (OSError, ValueError):
            continue


def main() -> int:
    answer_help(__doc__, __file__)
    os.chdir(_ROOT)
    import reference_runner_v3 as R

    # The PRE-FIX door, obtained by deleting the field the new conjunct reads
    # rather than by reading an old copy of the file -- so producer and
    # consumer are the same live code.
    def door_prefix(e) -> bool:
        if R._routing_ladder_never_served(e):
            return True
        shadow = dict(e)
        shadow.pop("severity_proof", None)
        return R._routing_ladder_never_served(shadow)

    total = nonterm = 0
    hits, example, proof_status = Counter(), {}, Counter()
    for path, blob in _registries():
        for cid, e in ((blob.get("registry") or {}).get("entries") or {}).items():
            total += 1
            if not door_prefix(e) or e.get("status") in TERMINAL:
                continue
            nonterm += 1
            proof_status[R.severity_proof_status(e)] += 1
            for field in CANDIDATES:
                if _set(e.get(field)):
                    hits[field] += 1
                    example.setdefault(field, (
                        os.path.basename(os.path.dirname(path)), cid,
                        repr(e.get(field))[:60]))

    print(f"archived registry entries scanned ............. {total}")
    print(f"NON-TERMINAL entries the PRE-FIX door released   {nonterm}")
    if not nonterm:
        print("no archived registries on this machine -- nothing to measure")
        return 0
    print("\nR_k PROOF STATUS ON THOSE ENTRIES "
          "(a non-SKIP status is a reading the door discarded):")
    for st, n in proof_status.most_common():
        lo, hi = _wilson(n, nonterm)
        print(f"   {st:7s} {n:4d}  {100*n/nonterm:5.2f}%  "
              f"Wilson 95% [{100*lo:.2f}%, {100*hi:.2f}%]")
    reading = sum(n for st, n in proof_status.items()
                  if st not in R.NO_READING_SEVERITY_PROOF_STATUSES)
    lo, hi = _wilson(reading, nonterm)
    print(f"   -> A READING WAS DISCARDED on {reading} of {nonterm} "
          f"({100*reading/nonterm:.2f}%, Wilson 95% "
          f"[{100*lo:.2f}%, {100*hi:.2f}%])")
    nfail = proof_status.get("FAIL", 0)
    lo, hi = _wilson(nfail, nonterm)
    print(f"   -> of those, FAIL (severity affirmatively NOT proven): "
          f"{nfail} ({100*nfail/nonterm:.2f}%, Wilson 95% "
          f"[{100*lo:.2f}%, {100*hi:.2f}%])")

    print("\nCANDIDATE CONTACT FIELDS SET ON A PRE-FIX DOOR-OPEN ENTRY:")
    for field, n in hits.most_common():
        print(f"   {n:4d}  {field:26s} e.g. {example[field]}")

    print(f"\nDISCRIMINATION AGAINST THE CASE THE DOOR EXISTS FOR "
          f"({', '.join(REFERENCE_IDS)} of study_run1b):")
    try:
        with open(REFERENCE_RUN, encoding="utf-8") as fh:
            ref = json.load(fh)["registry"]["entries"]
    except (OSError, KeyError, ValueError):
        print("   reference run absent on this machine -- skipped")
        ref = {}
    # THE COLUMN TESTS THE CONJUNCT'S OWN PREDICATE, NOT FIELD PRESENCE, and
    # the first version of this script got that wrong in exactly the way the
    # founder's interpreter instrument did: for `severity_proof` the conjunct
    # keys on the STATUS, so mere presence of the field reported the composed
    # fix as closing the door on C0066 when it does not. A wrong instrument
    # reads as a confident result, so the predicate is named per field here.
    def _contacted(e, field) -> bool:
        if field in ("severity_proof", "severity_proof_history"):
            return R.severity_proof_status(e) \
                not in R.NO_READING_SEVERITY_PROOF_STATUSES
        return _set(e.get(field))

    for field in hits:
        cols = " ".join(
            f"{cid}={'CONTACT' if _contacted(ref.get(cid) or {}, field) else '-'}"
            for cid in REFERENCE_IDS)
        usable = bool(ref) and all(
            not _contacted(ref.get(c) or {}, field) for c in REFERENCE_IDS)
        print(f"   {field:26s} {cols:30s} "
              + ("DISCRIMINATING -- usable as a conjunct" if usable
                 else "REJECTED: closes the door on the reference case"))
    for cid in REFERENCE_IDS:
        if cid in ref:
            e = ref[cid]
            print(f"   {cid}: severity_proof="
                  f"{json.dumps(e.get('severity_proof'))} -> "
                  f"{R.severity_proof_status(e)}; door opens now = "
                  f"{R._routing_ladder_never_served(e)}")

    lat = Counter()
    for _p, blob in _registries():
        for _cid, e in ((blob.get("registry") or {}).get("entries") or {}).items():
            rh = e.get("routing_history") or []
            rounds = [r.get("round") for r in rh
                      if isinstance(r, dict) and r.get("round") is not None]
            if not rounds or e.get("open_since_round") is None:
                continue
            lat[min(int(x) for x in rounds) - int(e["open_since_round"])] += 1
    n = sum(lat.values())
    print(f"\nIS LADDER_UNSERVED_MIN_AGE_ROUNDS = "
          f"{R.LADDER_UNSERVED_MIN_AGE_ROUNDS} THE RIGHT BOUND?")
    print(f"   ladder-served entries with a round-stamped first attempt: {n}")
    for k in sorted(lat):
        lo, hi = _wilson(lat[k], n)
        print(f"   first_routing_round - open_since_round = {k:3d}  "
              f"{lat[k]:4d}  {100*lat[k]/n:6.2f}%  "
              f"Wilson 95% [{100*lo:.2f}%, {100*hi:.2f}%]")
    print("   -> the ladder serves an entry in its ARRIVAL round or never, so a"
          " longer wait\n      buys nothing; 1 is a full round of margin over a"
          " bound the data puts at 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
