#!/usr/bin/env python3
"""Does the A4 counter still admit a sub-critical UNCONFIRMED entry with no exit?

THE DEFECT UNDER TEST, `A4-counter-valve-severity-mismatch`, recorded
2026-10-03 and ruled by the founder 2026-10-16 with the words "Fix it all":
`unverified_critical_count()` has NO severity test, while the only site that
stamps `exhausted=True` requires severity >= 0.7, so a sub-critical UNCONFIRMED
entry can ENTER the counter and has no exit.

WHY THIS IS EXECUTED AND NOT READ. The counter's body was refactored on
2026-10-17 into a thin wrapper over `blocking_entry_ids`, and the docstrings now
claim 6 doors including a sub-critical severity test restored 2026-10-06. A
docstring claiming a door is not a door: this project has 2 recorded cases of a
docstring that was stale for over a month about this very predicate. So the
predicate is CALLED, on hand-built entries, and the answers compared.

4 CASES, chosen so the test can fail in either direction:
  A critical UNCONFIRMED, unproven        -> MUST block (the baseline)
  sub-critical UNCONFIRMED, PROVEN        -> MUST NOT block (the restored door)
  sub-critical UNCONFIRMED, UNPROVEN      -> MUST block (the stated design:
                                             "an unproven sub-critical still
                                             counts")
  sub-critical UNCONFIRMED, exhausted     -> MUST NOT block (the age valve)

AND THE SHARED-PREDICATE CLAIM IS TESTED SEPARATELY, because it is the half the
founder's ruling actually names: the counter and the routing reader must return
the SAME set, not merely similar counts.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
sys.path.insert(0, str(REPO))

#: ★ THE HELP FLAG IS ANSWERED BEFORE ANYTHING IS IMPORTED OR MEASURED.
#: This probe does its work at MODULE level rather than inside a main(), so a
#: handler at the foot of the file would never be reached -- the measurement
#: would already have run. `A --help must never cost money` is a standing rule
#: here, and importing the 22,000-line runner is not free either.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
except ImportError:                                 # pragma: no cover
    pass

from bench.reference_runner_v3 import (            # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD, FindingRegistry, severity_is_proven,
)

print("=" * 78)
print("A4: DOES A SUB-CRITICAL UNCONFIRMED ENTRY STILL BLOCK WITH NO EXIT?")
print("=" * 78)
print(f"  CRITICAL_SEVERITY_THRESHOLD = {CRITICAL_SEVERITY_THRESHOLD}")

SUB = 0.6          # the live instance C0042's severity
CRIT = 0.85


def _entry(cid, sev, **kw):
    e = {"id": cid, "status": "UNCONFIRMED", "severity": sev}
    e.update(kw)
    return e


#: A PROVEN severity needs whatever `severity_is_proven` actually reads. It is
#: probed rather than assumed, so this harness cannot silently build a case that
#: fails for the wrong reason -- the failure mode that made a probe's own
#: location manufacture a result earlier in this project.
import inspect                                      # noqa: E402
src = inspect.getsource(severity_is_proven)
print("\n  severity_is_proven reads these keys:")
keys = sorted({w.strip("\"'") for w in src.split() if w.startswith(('"', "'"))
               and len(w) > 2})
for k in keys[:14]:
    print(f"      {k}")

PROOF_SHAPES = [
    {"rk_validation": {"result": "PASS"}},
    {"rk_validation": "PASS"},
    {"severity_proof": {"status": "PASS"}},
    {"rk_proof": {"verdict": "PASS"}},
]
proven_kw = None
for shape in PROOF_SHAPES:
    if severity_is_proven(_entry("probe", SUB, **shape)):
        proven_kw = shape
        break
print(f"\n  a PROVEN sub-critical entry is built as: {proven_kw}")
if proven_kw is None:
    print("  REFUSED: no probed shape satisfies severity_is_proven, so this "
          "harness cannot build the PROVEN case and would report a block for "
          "the wrong reason. Read the function and add its shape before "
          "trusting any verdict below.")

CASES = [
    ("critical, unproven", _entry("C-crit", CRIT), True),
    ("sub-critical, UNPROVEN", _entry("C0042-like", SUB), True),
    ("sub-critical, exhausted", _entry("C-exh", SUB, exhausted=True), False),
]
if proven_kw is not None:
    CASES.insert(2, ("sub-critical, PROVEN",
                     _entry("C-proven", SUB, **proven_kw), False))

print("\n  CASE                      blocks?  expected  verdict")
ok = True
for label, e, expect_block in CASES:
    reg = FindingRegistry()
    reg.entries = {e["id"]: e}
    ids = reg.blocking_entry_ids()
    n = reg.unverified_critical_count()
    blocks = bool(ids)
    agree = "OK" if blocks == expect_block else "MISMATCH"
    if blocks != expect_block:
        ok = False
    print(f"  {label:<26}{str(blocks):<9}{str(expect_block):<10}{agree}"
          f"   (count={n}, ids={ids})")

print("\n  THE SHARED-PREDICATE HALF, which is what his ruling names:")
reg = FindingRegistry()
reg.entries = {e["id"]: e for _l, e, _x in CASES}
ids = set(reg.blocking_entry_ids())
cnt = reg.unverified_critical_count()
print(f"      blocking_entry_ids()        -> {sorted(ids)}")
print(f"      unverified_critical_count() -> {cnt}")
same = (cnt == len(ids))
print(f"      counter equals the set's size: {same}")
if hasattr(reg, "blockers_routing_cannot_serve"):
    try:
        other = reg.blockers_routing_cannot_serve()
        o = set(other) if not isinstance(other, int) else None
        print(f"      blockers_routing_cannot_serve() -> "
              f"{sorted(o) if o else other}")
        #: ★ CORRECTED EXPECTATION, 2026-11-08. The first version of this probe
        #: asserted the 2 sets were IDENTICAL and reported a MISMATCH. That was
        #: the PROBE's error, not the code's: this reader returns the SUBSET of
        #: blockers that `_apply_routing` would DECLINE to admit, which its own
        #: docstring states (73 of 167 across the archive). Entries built here
        #: carry no routing history, so routing WOULD serve them and the empty
        #: list is the correct answer. The claim the docstrings actually make is
        #: that both read the same DOOR predicate, so the testable relation is
        #: CONTAINMENT, not equality.
        if o is not None:
            print(f"      routing-unservable is a SUBSET of the blockers: "
                  f"{o <= ids}  ({len(o)} of {len(ids)})")
            ok = ok and (o <= ids)
    except TypeError as exc:
        print(f"      blockers_routing_cannot_serve needs arguments: {exc}")
else:
    print("      blockers_routing_cannot_serve: NOT PRESENT on this class")

print("\n" + "=" * 78)
print("VERDICT: " + ("every case behaves as the restored design states, and the "
                     "counter equals the shared set."
                     if ok and same else
                     "AT LEAST 1 CASE DISAGREES -- read the rows above."))
print("=" * 78)
raise SystemExit(0 if (ok and same) else 1)
