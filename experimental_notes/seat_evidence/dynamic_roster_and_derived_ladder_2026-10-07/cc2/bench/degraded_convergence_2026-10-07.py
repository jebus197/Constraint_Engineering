# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 825b0dbcd91a875d73fdf567d481a085ad6de7a052be8f347cdad1a99f41b7d8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Roster-aware convergence: a degraded panel may converge, but never as a clean one.

THE DEFECT THIS REPAIRS. `_check_gamma_alt_convergence` in
`bench/reference_runner_v3.py` (line 8070) takes `round_idx, gamma,
novel_critical_history, cfg, unresolved_critical, contested, rho_churn,
irreducible_queue, gamma_critical, total_findings` and NOTHING that names the
roster. Its count side -- K consecutive rounds with 0 new criticals -- gets easier
as the roster shrinks, because fewer seats generate fewer findings, and the gate
cannot see the difference. z3 settles that the observed count alone cannot separate
the two causes (`bench/a_shrinking_roster_converges_sooner_2026-10-07.py`:
`search_for_a_distinguishing_value: unsat`): 0 new criticals from a healthy panel
and 0 from a depleted one are the same integer.

The only other place the runner knows a roster is incomplete is the RESUME guard at
line 15650, which refuses a partial round. `active_models` appears exactly once in
the whole runner and that is where.

────────────────────────── THE DERIVATION ──────────────────────────

Let q be the per-seat-per-round probability of a new critical, and let the seats in
a round share a per-round latent factor u (every seat gets a byte-identical brief
and the same target, so a round is plausibly productive or barren for all of them
together). Given u the seats are conditionally independent with probability p(u),
and E[p(u)] = q. Rounds are i.i.d.

    A(n) := E_u[(1 - p(u))^n]            # P(a round of n seats is quiet)
    P_quiet(n, K) = A(n)^K               # K consecutive quiet rounds

To hold the spurious-convergence probability of a degraded run at or below the
level the DECLARED roster was pre-registered at:

    A(n_live)^K' <= A(n_dec)^K
 => K' >= K * ln A(n_dec) / ln A(n_live)                 (both logs < 0)

Write f(n) := -ln A(n), so the requirement is K' >= K * f(n_dec)/f(n_live).

Now A(n) = E[exp(n * ln(1-p))] is the moment generating function of the random
variable X := ln(1-p) <= 0, evaluated at n. The cumulant generating function
ln A(n) is CONVEX in n for every distribution of X (standard: it is the log of an
MGF). Hence f(n) = -ln A(n) is CONCAVE, with f(0) = -ln A(0) = -ln 1 = 0.

A concave function through the origin has non-increasing f(n)/n. So for
n_live < n_dec:

    f(n_dec)/n_dec <= f(n_live)/n_live
 => f(n_dec)/f(n_live) <= n_dec/n_live

THEREFORE the independence-derived window

    K_required = ceil(K * n_dec / n_live)

is SUFFICIENT AT EVERY CORRELATION, and is tight exactly at independence (where
p(u) = q is degenerate, f(n) = -n*ln(1-q), and the bound holds with equality).

WHY THAT MATTERS TO THIS BRIEF. The brief records that the spurious-convergence
factor moves by 7.7915x across a plausible correlation range on a parameter this
project has never measured, and treats that as setting the URGENCY of the repair.
It also sets a bound on the repair's own validity, and the bound is favourable: the
window above never under-corrects, because independence is the worst case and the
magnitude uncertainty lies entirely on the conservative side. The unmeasured
correlation does NOT block this fix. Measuring it (see
`scripts/measure_intra_round_correlation_2026-10-07.py`) would let the window be
RELAXED from this bound toward f(n_dec)/f(n_live); it is not needed to apply it.

TWO GUARDS ON THE ARITHMETIC, both of which a naive implementation gets wrong:

  * n_live == 0 -> no window makes the evidence exist. Convergence is impossible,
    not merely scaled.
  * n_live > n_dec (a readmitted seat, or a roster larger than declared) would give
    K_required < K and WEAKEN a pre-registered threshold mid-run. Clamped to
    max(K, ...). Lowering a declared bound because the run happens to be going well
    is the pattern that suppressed this repository's own irreducible-queue alarm
    twice on 2026-08-01 while it was right both times.

A DEGRADED RUN DOES CONVERGE, and that is the founder's requirement 8, not a
concession: *"if a model drops off the list ... it should not block an experimental
run until completion, or convergence."* Refusing outright would block it. Reporting
it as clean would corrupt the measurement machinery, which is a HARD-class
violation under cdsfl_core section 10 category 3. So it converges, with the window
scaled and the verdict labelled DEGRADED, carrying the roster evidence that makes
the two cases formally separable.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence


#: The verdict's integrity class. These are the two cases z3 shows are
#: indistinguishable from the count alone and separable once the roster is carried.
CLEAN = "CLEAN"
DEGRADED = "DEGRADED"
IMPOSSIBLE = "NO_LIVE_SEATS"
#: The declared roster was edited after dispatch. See `roster_fingerprint`.
TAMPERED = "DECLARED_ROSTER_CHANGED"


def roster_fingerprint(roster) -> str:
    """A stable hash of the DECLARED roster, to be taken once at dispatch.

    WHY THIS IS NEEDED, and it is the one hole the UX design opens.
    `experimental_notes/CDSFL_UX_Vision_Sketch_2026-03-28.md` line 50 offers the
    user three choices when a model fails: *"fix and resume, re-run the phase, or
    proceed without the failed model."* The third is the OPEN state and is
    correct. But the integrity class above is computed by comparing the LIVE
    roster against the DECLARED one, so if the declared roster can be edited
    mid-run -- which "proceed without the failed model" invites, and which the
    sketch's own extensibility promise at line 42 makes easy -- then a researcher
    can turn a DEGRADED convergence into a CLEAN one by deleting the absent seat
    from the declared list. The guard would report CLEAN and be right about the
    arithmetic and wrong about the run.

    That is not hypothetical mischief: it is the obvious way to make a red run go
    green, it requires no bad intent (the seat really was down), and it is
    indistinguishable in the report from a run that never had that seat. So the
    declared roster is fingerprinted at dispatch and the fingerprint travels with
    the record. A changed fingerprint is reported as TAMPERED, which is neither
    clean nor degraded but a third thing: the denominator moved.
    """
    import hashlib
    payload = "|".join(sorted({str(m) for m in roster}))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def required_quiet_window(n_declared: int, n_live: int, k_declared: int) -> int:
    """K consecutive quiet rounds needed from `n_live` seats to match `n_declared`.

    Returns the ceiling derived above. Never returns less than `k_declared`.
    Raises ValueError when there is no live seat, because no window repairs that.
    """
    if k_declared <= 0:
        raise ValueError(f"k_declared must be positive, got {k_declared}")
    if n_declared <= 0:
        raise ValueError(f"n_declared must be positive, got {n_declared}")
    if n_live <= 0:
        raise ValueError(
            "n_live == 0: a quiet round from an empty panel is not evidence of "
            "quiescence, so no window scaling applies. Convergence is impossible.")
    return max(k_declared, math.ceil(k_declared * n_declared / n_live))


def p_quiet_independent(n: int, k: int, q: float) -> float:
    """P(K consecutive quiet rounds | n seats, per-seat-per-round rate q), independent.

    The worst case of the family, by the concavity argument in the module
    docstring. Used to EXHIBIT that the scaled window holds the probability at or
    below the declared level, not to assume independence holds in the field.
    """
    return (1.0 - q) ** (n * k)


@dataclass
class ConvergenceRecord:
    """What a convergence verdict must carry so a degraded one cannot read as clean.

    Every field here answers a question the current report cannot answer. The
    runner already records `models_responded` per round (reference_runner_v3.py
    line 17818) and its own code calls the per-round response files the ground
    truth of who answered -- so `live_by_round` costs no new measurement, only a
    wire.
    """
    integrity: str                       # CLEAN / DEGRADED / NO_LIVE_SEATS
    roster_declared: list = field(default_factory=list)
    live_by_round: list = field(default_factory=list)   # [[labels], ...] per round
    n_declared: int = 0
    n_live_binding: int = 0              # the SMALLEST live roster in the window
    k_declared: int = 0
    k_required: int = 0
    k_observed: int = 0
    absent_seats: list = field(default_factory=list)
    breaker_states: dict = field(default_factory=dict)
    quiet_tail: list = field(default_factory=list)
    declared_fingerprint: str = ""
    expected_fingerprint: str = ""
    reason: str = ""

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["reportable_as_clean"] = self.integrity == CLEAN
        return d


def assess_roster(
    roster_declared: Sequence[str],
    live_by_round: Sequence[Sequence[str]],
    novel_critical_history: Sequence[int],
    k_declared: int,
    breaker_states: dict | None = None,
    expected_fingerprint: str | None = None,
) -> ConvergenceRecord:
    """Build the convergence record and the window the count side must actually meet.

    `live_by_round` is the per-round responder list, newest LAST -- the runner's
    `models_responded`. The binding roster size is the MINIMUM over the rounds the
    streak is claimed from, because the weakest round in the window is the one that
    made the streak cheap.

    This function does NOT decide convergence on its own. It returns the record and
    `k_required`; the gate still requires its own gamma side, its A4 fail-safe and
    its contested check. It can only ever make the count side HARDER.
    """
    declared = sorted({str(m) for m in roster_declared})
    n_dec = len(declared)
    fp = roster_fingerprint(declared)
    # The observed quiet streak, from the tail of the settled critical series.
    k_obs = 0
    for n in reversed(list(novel_critical_history)):
        if n == 0:
            k_obs += 1
        else:
            break

    # Rounds the streak is claimed from: the last k_obs rounds for which we have a
    # responder list. Fall back to the whole list when the runner gave us fewer.
    window_rounds = [list(r) for r in live_by_round][-k_obs:] if k_obs else []
    live_sets = [sorted({str(m) for m in r}) for r in window_rounds]
    sizes = [len(s) for s in live_sets]
    n_live = min(sizes) if sizes else n_dec

    absent = sorted({m for m in declared
                     for s in live_sets if m not in s}) if live_sets else []

    if n_live <= 0:
        return ConvergenceRecord(
            integrity=IMPOSSIBLE, roster_declared=declared, live_by_round=live_sets,
            n_declared=n_dec, n_live_binding=0, k_declared=k_declared,
            k_required=0, k_observed=k_obs, absent_seats=absent,
            breaker_states=dict(breaker_states or {}),
            quiet_tail=list(novel_critical_history)[-k_obs:] if k_obs else [],
            reason=("NO LIVE SEATS in the quiet window: a quiet round from an empty "
                    "panel is the absence of evidence, not evidence of quiescence. "
                    "Convergence is refused and no window scaling applies."))

    k_req = required_quiet_window(n_dec, n_live, k_declared)
    degraded = bool(absent) or n_live < n_dec
    tampered = bool(expected_fingerprint) and expected_fingerprint != fp
    integrity = TAMPERED if tampered else (DEGRADED if degraded else CLEAN)
    if tampered:
        reason = (
            f"DECLARED ROSTER CHANGED since dispatch: fingerprint {fp} != "
            f"{expected_fingerprint}. The integrity class is computed by comparing "
            f"the live roster against the declared one, so an edited declared "
            f"roster can turn a degraded convergence into a clean-looking one by "
            f"deleting the absent seat. Convergence is NOT reportable. Re-declare "
            f"the roster and re-run, or resume against the original declaration.")
    elif degraded:
        reason = (
            f"DEGRADED ROSTER: {n_live} of {n_dec} seat(s) answered in the binding "
            f"round of the quiet window (absent: {absent or 'none named'}). The "
            f"K-consecutive-zero-critical condition is cheaper for a smaller panel, "
            f"so the window is scaled from K={k_declared} to K={k_req} "
            f"(= ceil(K * {n_dec} / {n_live})), which holds the spurious-convergence "
            f"probability at or below the declared-roster level at EVERY intra-round "
            f"correlation -- independence is the worst case and the scaling is tight "
            f"there. This verdict is NOT reportable as a clean convergence.")
    else:
        reason = (
            f"CLEAN ROSTER: all {n_dec} declared seat(s) answered in every round of "
            f"the quiet window; K={k_declared} stands unscaled.")

    return ConvergenceRecord(
        integrity=integrity, roster_declared=declared, live_by_round=live_sets,
        n_declared=n_dec, n_live_binding=n_live, k_declared=k_declared,
        k_required=k_req, k_observed=k_obs, absent_seats=absent,
        breaker_states=dict(breaker_states or {}),
        quiet_tail=list(novel_critical_history)[-k_obs:] if k_obs else [],
        declared_fingerprint=fp,
        expected_fingerprint=expected_fingerprint or "",
        reason=reason)


def count_side_is_met(record: ConvergenceRecord) -> bool:
    """Does the observed quiet streak meet the roster-scaled window?

    This is the ONLY behavioural change: it replaces `len(history) >= window and
    all(n == 0 ...)` with the same test against `k_required`. On an intact roster
    `k_required == k_declared` and the test is byte-identical to today's.
    """
    if record.integrity in (IMPOSSIBLE, TAMPERED):
        return False
    return record.k_observed >= record.k_required
