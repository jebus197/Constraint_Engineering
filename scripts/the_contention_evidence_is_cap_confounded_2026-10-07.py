#!/usr/bin/env python3
"""The serialisation's justifying p-value is confounded by a SHARED CAP.

THE FOUNDER'S CHALLENGE, 2026-10-07: *"Is back to back necessary? It doubles the
duration of a panel review. Isn't it the case that all that is needed is a few
seconds between dispatching each model?"*

WHAT JUSTIFIED SERIALISING THE FREE SEATS. The 2026-10-05 finding that panel seat
failures are not independent: of the 5 rounds that lost a seat, 3 lost BOTH at
near-identical durations -- 1956.0/1956.2, 902.0/902.0 and 18.7/18.8 seconds --
giving p = 1.556646e-07 against an independence model.

THE CONFOUND. Two seats given the SAME DEADLINE fail at that deadline. That is
arithmetic, not contention. The cap history is 300 -> 900 -> 1800 -> (3600,
reverted) seconds, and checked against those caps:

    1956.2 / 1956.0  are +8.68% / +8.67% of the 1800 s cap   -> AT THE CAP
     902.0 /  902.0  are +0.22% / +0.22% of the  900 s cap   -> AT THE CAP
      18.8 /   18.7  are -97.91% / -97.92% of any cap        -> NOT at a cap

So 2 of the 3 co-failures are both seats hitting one deadline. Only 1 is genuine
simultaneity, and recomputed honestly that is 1 of 5, Wilson [0.0362, 0.6245],
one-sided exact p = 0.107550 -- NOT significant.

WHAT THAT MEANS FOR THE FOUNDER'S QUESTION. The single unexplained co-failure
sits at 18.7 seconds, which is session-ESTABLISHMENT time, not mid-flight. A
stagger of a few seconds prevents exactly that collision, at a fraction of the
cost of holding a lock across the whole dispatch. Full serialisation also
prevents it, but it bounds a free panel by the SUM rather than the MAX of its
seats. On the evidence available, the stagger is at least as well supported as
the lock and strictly cheaper.

NEITHER IS DEMONSTRATED. `bench/confer_maths_panel_2026-09-05.py` says so itself:
*"It has NOT been tested by running a panel both ways ... this change is a
scheduling change with a stated reason, not a demonstrated cure."* The
interventional test is cheap, because both seats are free.

Run: python3 scripts/the_contention_evidence_is_cap_confounded_2026-10-07.py
"""
from __future__ import annotations

import argparse

#: The 8 recorded timeouts, from scripts/why_cc2_times_out_2026-10-05.py.
EVENTS = [
    ("fingerprint_ladder_review_2026-10-05", "cc2", 3628.5),
    ("panel_convergence_blockers_2026-10-03", "fable", 1956.2),
    ("panel_convergence_blockers_2026-10-03", "cc2", 1956.0),
    ("severity_enforcement_review_20260907", "cc2", 902.0),
    ("severity_enforcement_review_20260907", "fable", 902.0),
    ("panel_maths_20260905T032107Z", "cc2", 900.0),
    ("founder_verdicts_2026-09-28", "fable", 18.8),
    ("founder_verdicts_2026-09-28", "cc2", 18.7),
]
CAPS = (900, 1800, 3600)
ROUNDS_LOSING_A_SEAT = 5
PER_SEAT_RECENT_LOSS = 0.15


#: Durations EXPLAINED BY THE RECORD rather than by a tolerance. P-PASS
#: 2026-10-08: the first version classified a duration as a cap hit when it sat
#: within 10% of a cap, and 1956.0 s is +8.67% of the 1800 s cap -- inside the
#: window only because the window was chosen that way. Tighten the tolerance
#: below 8.67% and 2 of the 3 co-failures become "genuine", restoring most of
#: the contention case. So the classification could not rest on the tolerance.
#:
#: THE RECORD SETTLES IT. `elapsed_s` on a seat file is CUMULATIVE ACROSS
#: ATTEMPTS, and the companion `.tools.json` carries the per-attempt breakdown.
#: For panel_convergence_blockers_2026-10-03, measured from those files:
#:   cc2   : total 1956.0 s, 2 attempts, attempt 2 = 110.4 s with 37 tool calls
#:   fable : total 1956.2 s, 2 attempts, attempt 2 = 110.8 s with 11 tool calls
#: So attempt 1 consumed about 1845 s in both cases -- the 1800 s cap in force on
#: that date, confirmed from git at commit cd19903a, plus process overhead. Both
#: seats were capped on attempt 1, which is precisely the shared-deadline
#: arithmetic this script is about.
CAP_EXPLAINED_BY_RECORD = {
    # round -> (total_s, attempt_2_s, cap_in_force, source of the breakdown)
    "panel_convergence_blockers_2026-10-03":
        (1956.0, 110.4, 1800, "cc2.tools.json / fable.tools.json per_attempt"),
}


def at_a_cap(t: float, tol: float = 0.10, round_name: str | None = None) -> bool:
    """True if a duration is explained by a cap.

    Prefers the ARCHIVED per-attempt record over the tolerance. The tolerance
    remains for durations with no breakdown on disk, and is reported as such.
    """
    if round_name and round_name in CAP_EXPLAINED_BY_RECORD:
        total, a2, cap, _src = CAP_EXPLAINED_BY_RECORD[round_name]
        if abs(t - total) < 1.0:
            return abs((t - a2) - cap) / cap <= 0.05   # attempt 1 sat at the cap
    return any(abs(t - c) / c <= tol for c in CAPS)


def classify():
    both = {}
    for rnd, seat, t in EVENTS:
        both.setdefault(rnd, []).append((seat, t))
    pairs = {r: v for r, v in both.items() if len(v) == 2}
    genuine = {r: v for r, v in pairs.items()
               if not all(at_a_cap(t, round_name=r) for _s, t in v)}
    return pairs, genuine


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tol", type=float, default=0.10)
    a = ap.parse_args()
    from scipy.stats import binom
    from statsmodels.stats.proportion import proportion_confint

    print("EVERY RECORDED TIMEOUT, AGAINST THE CAPS THE PANEL HAS USED")
    for rnd, seat, t in EVENTS:
        near = min(CAPS, key=lambda c: abs(t - c))
        print(f"  {rnd:40s} {seat:6s} {t:8.1f}s  nearest {near:5d}  "
              f"{100 * (t - near) / near:+7.2f}%  "
              f"{'AT THE CAP' if at_a_cap(t, a.tol, round_name=rnd) else 'NOT at a cap'}")

    pairs, genuine = classify()
    print()
    print(f"rounds that lost BOTH seats: {len(pairs)}")
    print(f"co-failures NOT explained by a shared deadline: {len(genuine)}")
    for r, v in genuine.items():
        print(f"   {r}: {' / '.join(f'{t:.1f}s' for _s, t in v)}  "
              f"-> session-establishment time, which a stagger prevents")

    k, n = len(genuine), ROUNDS_LOSING_A_SEAT
    lo, hi = proportion_confint(k, n, method="wilson")
    p_co = PER_SEAT_RECENT_LOSS ** 2
    pval = 1 - binom.cdf(k - 1, n, p_co) if k > 0 else 1.0
    print()
    print(f"the note's figure, independence null, 3 of 5   : p = 1.556646e-07")
    print(f"recomputed with cap-explained pairs removed    : {k} of {n} = "
          f"{k / n:.4f}  Wilson [{lo:.4f}, {hi:.4f}]")
    print(f"  one-sided exact against p_co = {p_co:.4f}     : p = {pval:.6f}")
    print()
    print("CONCLUSION. The justification for holding a lock across the whole")
    print("dispatch rests on 3 co-failures; 2 of them are 2 seats meeting 1")
    print("deadline. The remaining evidence is 1 collision at establishment time,")
    print("not significant, and precisely the case a few seconds of stagger")
    print("prevents. Neither scheduling choice has been tested interventionally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
