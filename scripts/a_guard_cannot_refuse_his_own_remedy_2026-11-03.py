#!/usr/bin/env python3
"""A guard tested UNCONFIRMED where it meant NOT SETTLED, so it refused `reopen`.

THE FIND. On 2026-11-03 the founder instructed, verbatim: *"Reopen 86a5a9f182c2
and commit everything."* `reopen` is the founder-only route out of a terminal
status and it sets REOPENED. The guard
`test_a_tracked_row_whose_entry_is_open_has_not_settled_its_ticket` in
bench/tests/test_every_annotation_verdict_names_its_evidence_2026-10-17.py tested
membership of `store.unconfirmed()`, which admits exactly ONE status. REOPENED is
LIVE and is not UNCONFIRMED, so the guard went on refusing a ticket he had
personally put back into live work, and his instruction and his demand for a
green board could not both be satisfied.

THE PROPERTY THE GUARD STATES, in its own docstring and in its own assertion
message, is *"their tickets have been SETTLED anyway"*. Settled is the complement
of live. The code asked a narrower question than the specification it carries,
which is the `execute-do-not-grep` / `verify-the-deciding-layer` shape: a
producer and a consumer that each describe themselves correctly and disagree.

WHY `live` AND NOT `not settled`. They are not interchangeable here. A verdict
row with NO TICKET AT ALL is in neither set. Keying off `live` leaves such a row
flagged, exactly as the old predicate did. Keying off `not settled` would
silently excuse it, which would be a real weakening.

WHAT THIS SCRIPT COMMITS TO, so none of it is prose-only:
  1. settled and live PARTITION the status space -- 2 routes, set algebra + z3.
  2. The new predicate flags a strict SUBSET of the old: the set
     {s : new(s) and not old(s)} is EMPTY. So 0 true positives are lost.
  3. The 6 statuses the old predicate flagged wrongly, named.
  4. The LIVE incidence of that false positive today, with an interval, because
     a rate of 0 must be reported as 0 and not as an argument.
  5. That CLOSED -- the case the guard exists for -- is STILL flagged.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "scripts"))

VERDICTS = REPO / "experimental_notes" / "data" / "annotation_verdicts_2026-10-17.json"
#: The one row the founder's reopen was issued for.
SUBJECT_TID = "86a5a9f182c2"


def _two_route_wilson(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Wilson 95%, computed twice and compared, per the 2-tool rule."""
    if n == 0:
        return (0.0, 0.0), 0.0
    from scipy.stats import norm
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    hand = ((c - h) / d, (c + h) / d)
    try:
        from statsmodels.stats.proportion import proportion_confint
        lib = tuple(proportion_confint(k, n, alpha=0.05, method="wilson"))
    except Exception:
        return hand, float("nan")
    return hand, max(abs(hand[0] - lib[0]), abs(hand[1] - lib[1]))


def _clopper(k: int, n: int) -> tuple[tuple[float, float], float]:
    """Clopper-Pearson 95% via scipy.beta, cross-checked on mpmath."""
    if n == 0:
        return (0.0, 0.0), 0.0
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    try:
        import mpmath as mp
        mp.mp.dps = 40
        mlo = 0.0 if k == 0 else float(
            mp.findroot(lambda x: mp.betainc(k, n - k + 1, 0, x, regularized=True) - 0.025,
                        mp.mpf(max(lo, 1e-12))))
        mhi = 1.0 if k == n else float(
            mp.findroot(lambda x: mp.betainc(k + 1, n - k, 0, x, regularized=True) - 0.975,
                        mp.mpf(min(hi, 1 - 1e-12))))
    except Exception:
        return (lo, hi), float("nan")
    return (lo, hi), max(abs(lo - mlo), abs(hi - mhi))


def step_1_partition() -> dict:
    """settled and live partition STATUSES. Set algebra, then z3."""
    from ticket_store import TERMINAL, LIVE, REJECTED, STATUSES
    settled = set(TERMINAL) | {REJECTED}
    live = set(LIVE)
    route1 = {"intersection_empty": not (settled & live),
              "union_is_everything": (settled | live) == set(STATUSES)}

    from z3 import Solver, Bool, Or, And, Not, unsat
    s = Solver()
    bits = {st: Bool(f"is_{st}") for st in STATUSES}
    s.add(Or(*bits.values()))
    names = sorted(STATUSES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            s.add(Not(And(bits[a], bits[b])))
    in_settled = Or(*[bits[x] for x in settled])
    in_live = Or(*[bits[x] for x in live])
    s.push(); s.add(And(in_settled, in_live))
    both = s.check(); s.pop()
    s.push(); s.add(And(Not(in_settled), Not(in_live)))
    neither = s.check(); s.pop()
    route2 = {"both_unsat": both == unsat, "neither_unsat": neither == unsat}

    print("=" * 74)
    print("1. settled AND live PARTITION THE STATUS SPACE -- 2 ROUTES")
    print("=" * 74)
    print(f"  TERMINAL  : {sorted(TERMINAL)}")
    print(f"  LIVE      : {sorted(LIVE)}")
    print(f"  REJECTED  : {REJECTED!r}")
    print(f"  route 1 (set algebra): intersection empty = {route1['intersection_empty']}, "
          f"union == STATUSES = {route1['union_is_everything']}")
    print(f"  route 2 (z3)        : 'both' unsat = {route2['both_unsat']}, "
          f"'neither' unsat = {route2['neither_unsat']}")
    agree = (route1["intersection_empty"] == route2["both_unsat"]
             and route1["union_is_everything"] == route2["neither_unsat"])
    print(f"  the 2 routes AGREE  : {agree}")
    assert route1["intersection_empty"] and route1["union_is_everything"]
    assert route2["both_unsat"] and route2["neither_unsat"]
    return {"route1": route1, "route2": route2, "agree": agree,
            "settled": sorted(settled), "live": sorted(live)}


def step_2_subset() -> dict:
    """The new predicate flags a strict subset of the old. 0 true positives lost."""
    from ticket_store import LIVE, STATUSES
    old = lambda st: st != "UNCONFIRMED"            # noqa: E731
    new = lambda st: st not in set(LIVE)            # noqa: E731
    only_old = sorted(st for st in STATUSES if old(st) and not new(st))
    only_new = sorted(st for st in STATUSES if new(st) and not old(st))
    print()
    print("=" * 74)
    print("2. THE NEW PREDICATE FLAGS A STRICT SUBSET -- 0 TRUE POSITIVES LOST")
    print("=" * 74)
    print(f"  flagged by OLD only (false positives removed): {only_old}")
    print(f"  flagged by NEW only (regressions introduced) : {only_new}")
    print(f"  CLOSED still flagged under NEW               : {new('CLOSED')}")
    print(f"  REOPENED flagged under NEW                   : {new('REOPENED')}")
    print("  a row with NO ticket is in neither set, so it stays flagged under")
    print("  both -- which is why the predicate is `live` and not `not settled`.")
    assert not only_new, f"the change would introduce regressions on {only_new}"
    assert new("CLOSED") and not new("REOPENED")
    return {"false_positives_removed": only_old, "regressions": only_new}


def step_3_incidence() -> dict:
    """How often that false positive actually bites TODAY. A 0 is reported as a 0."""
    from ticket_store import TicketStore, LIVE
    import task_list_markers as tlm

    rows = json.loads(VERDICTS.read_text())
    rows = rows if isinstance(rows, list) else rows.get("rows", [])
    store = TicketStore()

    def key(f, text):
        return (str(f).split("#")[0], " ".join(str(text).split()).lower())

    latest = {}
    for t in store.all():
        latest[key(t.anchor, t.verbatim or t.title)] = t

    entries = {e.ident: e for e in tlm.parse_entries()}
    finished = {"DONE", "WITHDRAWN", "DEFERRED"}

    def named_entries(row) -> list[str]:
        ev = row.get("evidence") or ""
        out: list[str] = []
        for clause in re.findall(
                r"entr(?:y|ies)\s+((?:[A-Z]?\d+[A-Za-z0-9.]*[,\s]*(?:and\s+)?)+)", ev):
            out += re.findall(r"[A-Z]?\d+[A-Za-z0-9.]*", clause)
        return out

    tracked = [r for r in rows if r.get("verdict") == "TRACKED"]
    no_entry = [r for r in tracked if not named_entries(r)]
    status_of = collections.Counter()
    for r in tracked:
        t = latest.get(key(r["file"], r["text"]))
        status_of[t.status if t else "(no ticket)"] += 1

    live_not_unconf = [s for s in status_of
                       if s in set(LIVE) and s != "UNCONFIRMED"]
    k = sum(status_of[s] for s in live_not_unconf)
    n = len(tracked)
    (wlo, whi), wdiff = _two_route_wilson(k, n)
    (clo, chi), cdiff = _clopper(k, n)

    print()
    print("=" * 74)
    print("3. HOW OFTEN THE REMOVED FALSE POSITIVE BITES TODAY")
    print("=" * 74)
    print(f"  TRACKED verdict rows                        : {n}")
    print(f"  of those, naming NO governing entry at all  : {len(no_entry)}")
    print("  ticket status of each TRACKED row's ticket:")
    for s, c in status_of.most_common():
        print(f"      {c:>4}  {s}")
    print(f"  rows whose ticket is LIVE but not UNCONFIRMED: {k} of {n} = "
          f"{k / n if n else 0:.6f}")
    print(f"      Wilson 95%          [{wlo:.6f}, {whi:.6f}]  (2-route |diff| {wdiff:.1e})")
    print(f"      Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]  (2-route |diff| {cdiff:.1e})")
    print("  STATED PLAINLY: before the founder's reopen this count was 0, so the")
    print("  false positive was LATENT and not realised. It became realised the")
    print("  moment he used `reopen`, which is the only route that produces one of")
    print("  the 6 statuses on a settled ticket. The repair is therefore justified")
    print("  by the specification mismatch, NOT by a pre-existing error count.")
    return {"tracked": n, "no_entry": len(no_entry),
            "status_of": dict(status_of), "live_not_unconfirmed": k,
            "wilson95": [wlo, whi], "clopper95": [clo, chi]}


def step_4_the_subject() -> dict:
    """The one ticket this was all about, and its state now."""
    from ticket_store import TicketStore, LIVE, TERMINAL
    store = TicketStore()
    t = store.get(SUBJECT_TID)
    print()
    print("=" * 74)
    print("4. THE TICKET HIS INSTRUCTION NAMED")
    print("=" * 74)
    if t is None:
        print(f"  {SUBJECT_TID}: ABSENT from the store")
        return {"present": False}
    print(f"  tid      : {t.tid}")
    print(f"  kind     : {t.kind}")
    print(f"  status   : {t.status}   (live={t.status in set(LIVE)}, "
          f"terminal={t.status in set(TERMINAL)})")
    print(f"  verbatim : {' '.join((t.verbatim or '').split())[:150]}")
    print("  HIS QUESTION HAS 2 HALVES AND ONLY 1 WAS ANSWERED AT CLOSE TIME:")
    print("    (a) 'Do we have a closed status that prevents repetition?' -> YES,")
    print("        answered and verified by execution on a copy of the store.")
    print("    (b) 'So if it is closed, why did it come up again?' -> NOT answered.")
    print("        The reopen keeps (b) visible instead of recording it as handled.")
    assert t.status == "REOPENED", (
        f"expected REOPENED after his instruction, found {t.status}")
    return {"present": True, "status": t.status, "kind": t.kind}


def main() -> int:
    # A `--help` must answer without doing the work -- his standing rule, and
    # the reachability guard checks for the usage line. This producer was
    # written without one and that guard caught it the same evening.
    import argparse
    argparse.ArgumentParser(
        description=("Show that the settled-ticket guard tested UNCONFIRMED "
                     "where it meant NOT SETTLED, so it refused the founder's "
                     "own `reopen`. Reads only; writes nothing.")).parse_args()
    out = {"partition": step_1_partition(),
           "subset": step_2_subset(),
           "incidence": step_3_incidence(),
           "subject": step_4_the_subject()}
    print()
    print("ALL ASSERTIONS PASSED.")
    return 0 if out else 1


if __name__ == "__main__":
    raise SystemExit(main())
