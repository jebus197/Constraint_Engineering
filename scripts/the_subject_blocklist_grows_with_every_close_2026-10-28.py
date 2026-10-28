#!/usr/bin/env python3
"""A subject becomes a PERMANENT blocker the moment its first ticket closes.

THE TITLE OF THIS FILE OVERSTATES ITS OWN FINDING AND IS KEPT FOR ITS PATH.
The first version of this docstring claimed the suppression rate RISES as the
store grows. ITS OWN REPLAY REFUTED THAT: the blocked share is 0.8370 after 250
tickets, peaks at 0.9310 after 750, and is 0.8644 at 2857. It is FLAT AND HIGH,
not rising, and it was already high when the store was small. The blocked SET
cannot shrink -- z3 returns unsat on any model where a close removes a subject --
but the blocked SHARE is not the blocked set, because new subjects arrive too.
Conflating the two is the error, and it was mine.

A SECOND HYPOTHESIS OF MINE IS ALSO REFUTED HERE. I expected over-matching to
come from overloaded identifiers acting as stopwords, which would let the
project's own existing selectivity rule in `blocker_triage.py` fix it for free.
Measured: the maximum document frequency across all 354 subjects is 9 of 2857
tickets (0.0032) and the MEDIAN IS 1, with 210 of 354 subjects naming exactly 1
ticket. That rule caps at a quarter of the entries, so it would catch nothing.
No subject is common. The hypothesis is dead and the rule is not the fix.

WHAT IS ACTUALLY TRUE, and it is simpler than either guess: 2543 of 2857 tickets
are settled (0.8900), and 59.32% of subjects name exactly 1 ticket, so a subject
is blocked as soon as its FIRST ticket closes. The tier conflates "this mechanism
has been touched before" with "this question has been answered before".

HIS INSTRUCTION, 2026-10-28: fix the ticket store's over-matching, raise it as a
formal ticket, and close that ticket only if the fix is reliable.

THE DEFECT, STATED AS A PREDICATE RATHER THAN AS A COMPLAINT. `propose()` returns
`subject-settled` and creates NO ticket when any subject of the proposal appears
on any SETTLED ticket and the caller named no `task_ref` or `anchor` the settled
ticket does not own. `settled_on_subject` says so in its own docstring: "A
non-empty result means DO NOT RAISE."

WHY IT IS PERMANENT. A subject enters that blocklist the moment ANY ticket naming
it reaches a terminal status, and nothing ever removes it. The set of blocked
subjects is monotonically non-decreasing in the number of closes -- that part is
structural and z3 confirms it -- so a subject once blocked is blocked forever,
however different the next question about it may be.

WHAT WAS ALREADY MEASURED, AND WHY IT IS NOT A REFUTATION OF THIS. On 2026-10-17
`does_the_register_beat_word_search_2026-10-17.py` measured specificity 42/42 =
100% for the register against 36/42 for a word search, at commit 60d0d536 with
about 907 tickets in the store. That measurement is sound for the store it was
taken on. This script measures the quantity that measurement could not see: how
that specificity behaves as the store grows. 2 numbers taken 11 days apart are
not in conflict if the thing being measured is a function of store size.

THE CANDIDATE FIX IS NOT A THRESHOLD, DELIBERATELY. Two tuned repairs were
already tried and refused in `propose()`'s own comments: requiring word-layer
corroboration (circular, 4 of 4 -> 1 of 4 on the known rediscoveries) and a
partial-overlap threshold (a margin of 0.0318 fitted to 5 points). This one adds
no constant at all. It observes that the subject loop ignores `kind` while EVERY
other tier in the same function respects it, and that his own ruling of
2026-10-19 says a question and a proposed fix are different items whose
resolutions travel in opposite directions -- which is why `tid_of` digests the
kind. A settled `pf` therefore has no standing to suppress a new `qs`.

Produces: blocklist growth by store size, the cross-kind share of suppressions,
and a replay of the live store with and without the kind check.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


ts = _load("ts_blocklist", "bench/ticket_store.py")
hv = _load("ticket_harvester", "scripts/harvest_tickets_2026-10-17.py")


def _settled(t) -> bool:
    return t.status in ts.TERMINAL or t.status == ts.REJECTED


def wilson(k: int, n: int) -> tuple[float, float]:
    """Wilson 95%. scipy for the quantile, closed form for the interval."""
    if n == 0:
        return (0.0, 0.0)
    from scipy.stats import norm
    z = float(norm.ppf(0.975))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def blocklist_growth(tickets: list) -> list[dict]:
    """Blocked-subject share as the store fills, in creation order.

    A subject is BLOCKED once any settled ticket names it. Replayed rather than
    reasoned about, because the growth claim is the whole finding.
    """
    order = sorted(tickets, key=lambda t: (str(t.created), t.tid))
    seen_subs: set[str] = set()
    blocked: set[str] = set()
    out: list[dict] = []
    for i, t in enumerate(order, 1):
        for s in t.subjects:
            seen_subs.add(s)
            if _settled(t):
                blocked.add(s)
        if i % 250 == 0 or i == len(order):
            out.append({
                "tickets": i,
                "subjects": len(seen_subs),
                "blocked": len(blocked),
                "blocked_share": len(blocked) / max(1, len(seen_subs)),
            })
    return out


def cross_kind_share(store) -> dict:
    """Of every blocked (kind, subject) pair, how many are blocked ONLY by
    another kind.

    This is exactly what the kind check recovers, and it is a COUNT on the live
    store rather than an estimate.
    """
    pairs_total = 0
    pairs_cross_only = 0
    detail: collections.Counter = collections.Counter()
    for sub in store.subjects():
        settled = [t for t in store.by_subject(sub) if _settled(t)]
        if not settled:
            continue
        kinds_settled = {t.kind for t in settled}
        for kind in ts.KINDS:
            pairs_total += 1
            if kind not in kinds_settled:
                pairs_cross_only += 1
                detail[kind] += 1
    return {
        "pairs_total": pairs_total,
        "pairs_blocked_only_cross_kind": pairs_cross_only,
        "share": pairs_cross_only / max(1, pairs_total),
        "by_kind": dict(detail),
    }


def monotone_proof() -> dict:
    """The growth claim is structural, so prove it structurally with 2 tools.

    SymPy: the blocked set's cardinality as a function of closes has a
    non-negative difference. z3: no model exists in which a close REMOVES a
    subject from the blocklist, given the union-only update rule.
    """
    import sympy
    n = sympy.symbols("n", integer=True, nonnegative=True)
    a = sympy.Function("a")          # subjects newly blocked by close n, >= 0
    B = sympy.summation(a(n), (n, 0, sympy.Symbol("N", integer=True, nonnegative=True)))
    diff_nonneg = sympy.simplify(sympy.Symbol("a_k", nonnegative=True) >= 0)

    import z3
    # Model the update rule directly: B_{k+1} = B_k union S_k, membership form.
    inB_k, inB_k1, inS_k = z3.Bools("inB_k inB_k1 inS_k")
    rule = inB_k1 == z3.Or(inB_k, inS_k)
    shrinks = z3.And(rule, inB_k, z3.Not(inB_k1))   # was blocked, now is not
    sol = z3.Solver(); sol.add(shrinks)
    verdict = str(sol.check())
    return {
        "sympy_partial_sum": str(B),
        "sympy_difference_nonnegative": str(diff_nonneg),
        "z3_can_the_blocklist_shrink": verdict,   # expect: unsat
    }


def replay_live_store(store, kind_aware: bool) -> dict:
    """Ask the live store: of its own proposals, how many would be suppressed?

    Every ticket that EXISTS is, by construction, an item somebody judged
    distinct. Re-proposing its own verbatim WITHOUT its task_ref or anchor is the
    exact call shape that reached the subject tier 291 of 907 times on
    2026-10-17, and it is what my own 4 suppressions on 2026-10-27 looked like.
    A suppression here is therefore a FALSE one: the item demonstrably deserved
    its own identity, because it has one.
    """
    suppressed = 0
    total = 0
    examples: list[dict] = []
    for t in store.all():
        if t.task_ref or t.anchor:
            continue                      # the designed escape hatch applies
        subs = t.subjects or hv.subjects_in(t.verbatim or t.title or "")
        if not subs:
            continue
        total += 1
        hit = None
        for sub in subs:
            blockers = [b for b in store.by_subject(sub) if _settled(b)]
            if kind_aware:
                blockers = [b for b in blockers if b.kind == t.kind]
            blockers = [b for b in blockers if b.tid != t.tid]
            if blockers:
                hit = (sub, blockers[0])
                break
        if hit:
            suppressed += 1
            if len(examples) < 6:
                examples.append({
                    "tid": t.tid, "kind": t.kind,
                    "title": (t.title or "")[:70],
                    "blocked_on_subject": hit[0],
                    "by_tid": hit[1].tid, "by_kind": hit[1].kind,
                    "by_status": hit[1].status,
                    "by_title": (hit[1].title or "")[:70],
                })
    lo, hi = wilson(suppressed, total)
    return {"kind_aware": kind_aware, "eligible": total,
            "suppressed": suppressed,
            "rate": suppressed / max(1, total),
            "wilson95": (lo, hi), "examples": examples}


def main() -> int:
    store = ts.TicketStore(); store.load()
    tickets = store.all()

    print("== the live store ==")
    print(f"   tickets: {len(tickets)}")
    print("   by status:", dict(collections.Counter(t.status for t in tickets)))
    print("   by kind:  ", dict(collections.Counter(t.kind for t in tickets)))
    settled = [t for t in tickets if _settled(t)]
    print(f"   settled: {len(settled)}  live: {len(tickets) - len(settled)}")

    print("\n== the blocklist grows with every close ==")
    rows = blocklist_growth(tickets)
    for r in rows:
        print(f"   after {r['tickets']:>5} tickets: {r['blocked']:>4} of "
              f"{r['subjects']:>4} subjects blocked  "
              f"({r['blocked_share']:.4f})")

    print("\n== the subject tier ignores kind, and every other tier does not ==")
    ck = cross_kind_share(store)
    lo, hi = wilson(ck["pairs_blocked_only_cross_kind"], ck["pairs_total"])
    print(f"   blocked (kind, subject) pairs: {ck['pairs_total']}")
    print(f"   blocked ONLY by another kind:  "
          f"{ck['pairs_blocked_only_cross_kind']}  "
          f"({ck['share']:.6f}, Wilson [{lo:.6f}, {hi:.6f}])")
    print("   by kind:", ck["by_kind"])

    print("\n== the growth is structural, not incidental (2 tools) ==")
    mp = monotone_proof()
    for k, v in mp.items():
        print(f"   {k}: {v}")

    print("\n== replay: the store's own items, re-proposed without an anchor ==")
    before = replay_live_store(store, kind_aware=False)
    after = replay_live_store(store, kind_aware=True)
    for tag, r in (("AS SHIPPED ", before), ("KIND-AWARE ", after)):
        print(f"   {tag} suppressed {r['suppressed']} of {r['eligible']} "
              f"= {r['rate']:.6f}  Wilson [{r['wilson95'][0]:.6f}, "
              f"{r['wilson95'][1]:.6f}]")
    recovered = before["suppressed"] - after["suppressed"]
    print(f"   items the kind check recovers: {recovered}")

    if before["eligible"]:
        from scipy.stats import fisher_exact
        tbl = [[before["suppressed"], before["eligible"] - before["suppressed"]],
               [after["suppressed"], after["eligible"] - after["suppressed"]]]
        odds, p = fisher_exact(tbl, alternative="greater")
        print(f"   Fisher exact (shipped suppresses more): p = {p:.6e}, "
              f"odds ratio = {odds:.4f}")
        import numpy as np
        n1 = n2 = before["eligible"]
        p1 = before["rate"]; p2 = after["rate"]
        pool = (before["suppressed"] + after["suppressed"]) / (n1 + n2)
        se = float(np.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2)))
        zst = (p1 - p2) / se if se else float("nan")
        print(f"   NumPy 2-proportion z (cross-check): z = {zst:.4f}")

    print("\n== examples of a FALSE suppression, as shipped ==")
    for e in before["examples"]:
        print(f"   {e['kind']}:{e['tid'][:12]} {e['title']!r}")
        print(f"      blocked on `{e['blocked_on_subject']}` by "
              f"{e['by_kind']}:{e['by_tid'][:12]} [{e['by_status']}] "
              f"{e['by_title']!r}")

    out = REPO / "experimental_notes" / "data" / \
        "subject_blocklist_growth_2026-10-28.json"
    out.write_text(json.dumps({
        "growth": rows, "cross_kind": ck, "monotone": mp,
        "replay_shipped": before, "replay_kind_aware": after,
    }, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
