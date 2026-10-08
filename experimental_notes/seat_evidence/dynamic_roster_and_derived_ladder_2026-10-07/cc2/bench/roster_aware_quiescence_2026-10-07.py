# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2f62c953bc2621a97f4050c093fbaa29df5e014955aafa981fdf4e30c5f3b738
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Hold the spurious-convergence probability CONSTANT as the roster shrinks, and
make a degraded convergence formally distinguishable from a clean one.

THE DEFECT. `_check_gamma_alt_convergence` (bench/reference_runner_v3.py:8069)
takes `novel_critical_history: List[int]` and requires
`cfg.gamma_alt_consecutive_zero_crit` (3) consecutive zero-new-critical rounds. Its
signature carries NO roster size, so the quiet-round count is read identically
whether it came from 6 seats or 2. Because P(a round is quiet) rises as the roster
shrinks, a FIXED K means the gate's false-convergence rate rises with every seat
that drops out. z3 (bench/a_shrinking_roster_converges_sooner_2026-10-07.py) returns
unsat on the search for an observed count that separates the two causes: 0 from a
healthy panel and 0 from a depleted one are the same integer.

TWO INDEPENDENT FAILURE MODES, HENCE TWO PARTS. They are composed here only because
each addresses a failure the other provably cannot -- `falsify_roster_aware_
quiescence_2026-10-07.py` measures that, it is not asserted:
  (1) STOPPING TOO SOON. Cured by `quiet_rounds_required`, which raises K as the
      roster shrinks so P_spurious is held at its full-roster value. A record alone
      cannot cure this: labelling a run degraded does not stop it converging early.
  (2) REPORTING A DEGRADED RUN AS CLEAN. Cured by `convergence_roster_record`,
      which carries the per-round live roster and derives the label. A roster-aware
      K alone cannot cure this: it fixes the threshold but leaves the report
      indistinguishable from a full-roster one.

THE MODEL IS THE COMMITTED ONE, AND CALIBRATED ON MEASURED PARAMETERS. Rounds are
beta-binomial: a latent round quality p ~ Beta(a, b), a = q*s, b = (1-q)*s,
s = 1/rho - 1, matching `the_spurious_convergence_ratio_depends_on_correlation_
2026-10-07.py`. Here P(round quiet | n) is evaluated in CLOSED FORM,

    Q(n) = E[(1-p)^n] = B(a, b+n) / B(a, b),

which is an independent derivation of that artefact's numeric `mp.quad` and agrees
with it (checked in the falsifier). Defaults are the ARCHIVE-MEASURED q and rho from
`the_intra_round_correlation_measured_2026-10-07.py` (q = 0.2337 over 1968
seat-rounds, rho = 0.4060), NOT the q = 0.3, rho = 0 pair in the design brief. That
matters for requirement 7: calibrating at rho = 0 would demand K = 9 at a 2-seat
roster where the measured correlation demands far fewer, burning rounds the
researcher waits through to buy protection against a correlation the archive
rejects.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

#: Archive-measured, not assumed. See the module docstring.
Q_MEASURED = 0.233740
RHO_MEASURED = 0.405989


def _log_quiet_one_round(n: int, q: float, rho: float) -> float:
    """log P(a round of n seats raises 0 new criticals), beta-binomial.

    Closed form: E[(1-p)^n] = B(a, b+n)/B(a, b) with p ~ Beta(a, b).
    Computed via lgamma so large n cannot overflow.
    """
    if n <= 0:
        return 0.0                      # a 0-seat round is quiet with probability 1
    if rho <= 0:
        return n * math.log1p(-q)       # independence
    s = (1.0 / rho) - 1.0
    a, b = q * s, (1.0 - q) * s
    # log B(a, b+n) - log B(a, b)
    return ((math.lgamma(b + n) - math.lgamma(a + b + n))
            - (math.lgamma(b) - math.lgamma(a + b)))


def quiet_rounds_required(n_live: int, n_declared: int,
                          k_declared: int,
                          q: float = Q_MEASURED,
                          rho: float = RHO_MEASURED) -> int:
    """How many consecutive quiet rounds a roster of `n_live` must show to carry
    the SAME evidential weight as `k_declared` quiet rounds at the full roster.

    Derivation. P_spurious(n, K) = Q(n)^K. Hold it at the declared-roster value:
        Q(n_live)^K = Q(n_declared)^k_declared
    =>  K = k_declared * log Q(n_declared) / log Q(n_live),  rounded UP.
    Q is decreasing in n, so for n_live < n_declared this returns K > k_declared;
    it is the identity when n_live == n_declared, and it never returns less than
    `k_declared` -- a larger-than-declared roster does not get a discount, because
    the declared K is also a floor set by other considerations.
    """
    if n_live >= n_declared:
        return k_declared
    if n_live <= 0:
        raise ValueError("a 0-seat roster cannot evidence quiescence")
    lo_live = _log_quiet_one_round(n_live, q, rho)
    lo_decl = _log_quiet_one_round(n_declared, q, rho)
    if lo_live >= 0.0 or lo_decl >= 0.0:
        return k_declared
    return max(k_declared, math.ceil(k_declared * lo_decl / lo_live - 1e-12))


def p_spurious(n: int, k: int, q: float = Q_MEASURED,
               rho: float = RHO_MEASURED) -> float:
    """P(k consecutive quiet rounds arise by chance alone) at roster size n."""
    return math.exp(k * _log_quiet_one_round(n, q, rho))


@dataclass
class ConvergenceRosterRecord:
    """What the convergence record MUST carry so a degraded convergence cannot be
    reported as a clean one.

    `seats_declared` is the roster the experiment config declares; `live_by_round`
    is who could actually be dispatched each round -- which the runner already has:
    `models_responded` is written per round at reference_runner_v3.py:17818 and the
    per-round response files are described in that file as the ground truth of who
    answered. Nothing new has to be measured; it has to be CARRIED.
    """
    seats_declared: int
    live_by_round: list = field(default_factory=list)
    breaker_open_by_round: list = field(default_factory=list)

    @property
    def window_live(self) -> list:
        return self.live_by_round

    def degraded_rounds(self) -> list:
        return [i for i, n in enumerate(self.live_by_round)
                if n < self.seats_declared]

    def min_live_in_window(self, k: int) -> int:
        tail = self.live_by_round[-k:] if k else self.live_by_round
        return min(tail) if tail else 0

    def label(self, k_used: int) -> str:
        """CONVERGED_FULL_ROSTER or CONVERGED_DEGRADED_ROSTER. Derived, never set.

        z3 shows these are mutually exclusive once the live roster is recorded
        ("can_a_round_be_both_intact_and_degraded: unsat"), so the label is a
        function of the record rather than a claim about it.
        """
        tail = self.live_by_round[-k_used:] if k_used else self.live_by_round
        if tail and all(n >= self.seats_declared for n in tail):
            return "CONVERGED_FULL_ROSTER"
        return "CONVERGED_DEGRADED_ROSTER"


def assess(record: ConvergenceRosterRecord,
           novel_critical_history: list,
           k_declared: int,
           q: float = Q_MEASURED,
           rho: float = RHO_MEASURED) -> dict:
    """Roster-aware quiescence verdict plus the evidence a reader needs.

    MAY A DEGRADED RUN CONVERGE AT ALL? Yes -- requirement 8 is that a dropped seat
    *"should not block an experimental run until completion, or convergence"*, so
    refusing convergence outright would violate it, and would also hand the
    researcher a run that can never finish. It converges against the roster-aware K
    and is LABELLED, so the weaker evidence is priced rather than hidden. The one
    case that does NOT converge is a live roster of 0, which has no evidence at all.
    """
    n_live_now = record.live_by_round[-1] if record.live_by_round else 0
    k_needed = (quiet_rounds_required(record.min_live_in_window(k_declared) or 1,
                                      record.seats_declared, k_declared, q, rho)
                if record.live_by_round else k_declared)
    tail = novel_critical_history[-k_needed:]
    enough = len(novel_critical_history) >= k_needed
    quiet = enough and all(n == 0 for n in tail)
    converged = bool(quiet and n_live_now > 0)
    label = record.label(k_needed) if converged else "NOT_CONVERGED"
    return {
        "converged": converged,
        "label": label,
        "k_declared": k_declared,
        "k_required": k_needed,
        "seats_declared": record.seats_declared,
        "live_by_round": list(record.live_by_round),
        "min_live_in_window": record.min_live_in_window(k_needed),
        "degraded_rounds": record.degraded_rounds(),
        "p_spurious_at_k_required": p_spurious(
            record.min_live_in_window(k_needed) or record.seats_declared,
            k_needed, q, rho),
        "p_spurious_if_k_were_declared": p_spurious(
            record.min_live_in_window(k_declared) or record.seats_declared,
            k_declared, q, rho),
        "q_used": q,
        "rho_used": rho,
        "reason": (
            f"{label}: {k_needed} consecutive zero-new-critical rounds required at "
            f"min live roster {record.min_live_in_window(k_needed)} of "
            f"{record.seats_declared} declared (declared K {k_declared}); "
            f"tail={tail}"),
    }
