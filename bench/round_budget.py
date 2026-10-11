"""How many rounds are worth running? n* = (a/theta)^(1/gamma), computed PER RUN.

HIS ORDER, 2026-10-11: *"9: Then yes, do this also."* With the constraint that
settles the design: *"there is a case to be considered at where that average
number might sit in experiments ran by other researchers."* So this must NOT ship
a constant. The round count a run deserves is a property of THAT run's artefact
and THAT researcher's stopping threshold, and it is computed from the run's own
observed novelty series.

THE FORMULA, AND IT IS THE PROJECT'S OWN
----------------------------------------
From this project's Duane intensity ``lambda(n) = a * n**(-gamma)`` and the
appendix's stopping rule at line 205 (*"continue while sum w_k*dR_k > theta"*,
8 April 2026), stopping when the expected per-round yield falls to theta gives

    a * n**(-gamma) = theta   =>   n* = (a / theta)**(1 / gamma)

  a     = round-1 finding rate       -> the COMPLEXITY of the artefact
  gamma = decay exponent             -> how fast the space depletes
  theta = stopping threshold         -> THE RESEARCHER'S cost/value call

Verified symbolically 2026-10-11: SymPy solves ``lambda(n) = theta`` to exactly
that root; ``d n*/d gamma < 0`` for a > theta, so a faster-depleting space earns
fewer rounds, which is the right direction; at gamma -> 1 it reduces to a/theta;
and at gamma -> 0+ with a > theta it DIVERGES, which is reported rather than
clamped (see below). Cross-checked numerically by python, numpy and mpmath
agreeing to 3.55e-15.

** THIS DOES NOT USE `_estimate_gamma`, AND THAT IS THE LOAD-BEARING DECISION **
------------------------------------------------------------------------------
The obvious wiring -- feed the runner's existing gamma into the formula -- IS
WRONG, and it is what this project's own 2026-09-20 proposal specified. Measured
2026-10-11:

  * `_estimate_gamma` fits the CUMULATIVE series and returns ``1 - slope``.
  * The formula's gamma is the exponent of the PER-ROUND intensity.

These coincide only asymptotically. On EXACT counts from a known power law at
gamma = 0.709, the intensity fit recovers 0.709000 at every round count tested,
while the cumulative fit returns 0.3525 at n=4, 0.4129 at n=10, 0.5121 at n=50
and 0.6100 at n=500 -- still 0.099 short at 500 rounds, because the log-linear
form drops the ``-1`` in ``N(n) = a*(n**(1-gamma) - 1)/(1-gamma)``. At the round
counts this project actually runs, 3 to 21, the cumulative estimator is biased low
by roughly 0.30 to 0.36.

Consequence, on the project's own early data [5, 3, 2, 2]: the intensity fit gives
a = 4.8900, gamma = 0.7094, n* = 9.3695 -- reproducing the a = 4.89, gamma = 0.709,
n* = 9.37 recorded in March 2026.

The 2026-09-20 proposal said to feed `_estimate_gamma` into the formula and did NOT
say where ``a`` comes from, because `_estimate_gamma` returns only gamma and throws
its intercept away. Three wirings were therefore available and **all three
overestimate**:

    cumulative a AND cumulative gamma  ->  n* = 22.3759   2.3882x
    intensity a with cumulative gamma  ->  n* = 71.5436   7.6358x
    round-1 count as a                 ->  n* = 75.9566   8.1068x

So the SMALLEST error available from the proposal as written is 2.3882x, and
wiring it would have shipped a round recommendation between 2 and 8 times too high.

**GAMMA IS NOT DEMOTED AND IS NOT TOUCHED.** `_estimate_gamma` and the convergence
gate's thresholds (0.30 soft, 0.45 hard) are a MATCHED PAIR calibrated on that
estimator's own scale -- which is precisely why 0.30 is the right cutoff there and
would be far too low here. This module adds a SECOND estimator for a DIFFERENT
question (how many more rounds are worth running) and changes nothing the gate
reads. The gate keeps its gamma; the ruler gets its own.

ADVISORY, NEVER A TRIGGER
-------------------------
`n_star` is reported. It does not gate convergence, does not cap rounds, and does
not open or close anything. Three reasons, all of them this project's own record:
gamma from 4 points is weak; ``a`` confounds artefact complexity with reviewer
aggressiveness; and no archived run has tested whether stopping at n* loses
anything. Until a run tests it, a number that acted would be a number trusted
beyond its evidence.

A --help COSTS NOTHING: pure arithmetic, no dispatch, no network, no filesystem.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence

#: The researcher's stopping threshold, in findings per round. 1.0 reads as
#: "stop when the next round is expected to yield fewer than one new finding".
#: It is a COST/VALUE CALL and belongs to whoever runs the experiment, which is
#: why it is a parameter and not a constant.
DEFAULT_THETA = 1.0

#: The intensity fit needs at least 3 non-zero rounds to be anything but a line
#: through 2 points. Matches `_estimate_gamma`'s own `min_rounds` default.
MIN_ROUNDS = 3

#: Below this the decay exponent is indistinguishable from no decay at all, and
#: n* either diverges or is meaninglessly large. Reported, not clamped.
GAMMA_FLOOR = 1e-6


@dataclass
class RoundBudget:
    """A per-run round recommendation, with the fit it rests on."""

    status: str
    n_star: float | None = None
    a: float | None = None
    gamma: float | None = None
    theta: float = DEFAULT_THETA
    rounds_observed: int = 0
    r_squared: float | None = None
    detail: str = ""
    #: Rounds still worth running, given how many have already been run. Never
    #: negative, and None whenever n_star is None.
    rounds_remaining: int | None = None

    def as_dict(self) -> dict:
        return {
            "round_budget_status": self.status,
            "round_budget_n_star": self.n_star,
            "round_budget_a": self.a,
            "round_budget_gamma_intensity": self.gamma,
            "round_budget_theta": self.theta,
            "round_budget_rounds_observed": self.rounds_observed,
            "round_budget_r_squared": self.r_squared,
            "round_budget_rounds_remaining": self.rounds_remaining,
            "round_budget_detail": self.detail,
            "round_budget_is_advisory": True,
        }

    def line(self) -> str:
        """One human-readable line for the round log."""
        if self.n_star is None:
            return f"  round budget: {self.status} — {self.detail}"
        return (f"  round budget: n*={self.n_star:.2f} rounds "
                f"(a={self.a:.3f}, gamma={self.gamma:.4f}, theta={self.theta:g}, "
                f"R^2={self.r_squared:.3f}); {self.rounds_remaining} more worth "
                f"running — ADVISORY, gates nothing")


def _intensity_fit(counts: Sequence[float]) -> tuple[float, float, float]:
    """Least squares on log(count) against log(round). Returns (a, gamma, r2).

    Rounds with a zero count carry no information in log space and are dropped,
    which is the same choice `_estimate_gamma` makes for the cumulative series.
    """
    lx: List[float] = []
    ly: List[float] = []
    for i, c in enumerate(counts):
        if c > 0:
            lx.append(math.log(i + 1))
            ly.append(math.log(float(c)))
    n = len(lx)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    sx, sy = sum(lx), sum(ly)
    sxy = sum(x * y for x, y in zip(lx, ly))
    sx2 = sum(x * x for x in lx)
    denom = n * sx2 - sx * sx
    if abs(denom) < 1e-12:
        return float("nan"), float("nan"), float("nan")
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    # r^2, so a caller can see when the power law simply does not describe the run
    ybar = sy / n
    ss_tot = sum((y - ybar) ** 2 for y in ly)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(lx, ly))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
    return math.exp(intercept), -slope, r2


def project_optimal_rounds(
    novelty_counts: Sequence[float],
    theta: float = DEFAULT_THETA,
    min_rounds: int = MIN_ROUNDS,
) -> RoundBudget:
    """Project the round count this run's own novelty series justifies.

    Every refusal below is a CONSEQUENCE of the formula rather than a special
    case bolted on, which is why each names what it observed.
    """
    counts = list(novelty_counts)
    observed = len(counts)
    if theta <= 0:
        return RoundBudget("INVALID_THETA", theta=theta, rounds_observed=observed,
                           detail=f"theta must be positive; got {theta}")
    nonzero = sum(1 for c in counts if c > 0)
    if observed < min_rounds or nonzero < min_rounds:
        return RoundBudget(
            "TOO_EARLY", theta=theta, rounds_observed=observed,
            detail=(f"{nonzero} round(s) with a non-zero count against the {min_rounds} "
                    f"the fit needs; no projection is possible yet"))

    a, gamma, r2 = _intensity_fit(counts)
    if not (a == a) or not (gamma == gamma):           # NaN check
        return RoundBudget("UNFITTABLE", theta=theta, rounds_observed=observed,
                           detail="the novelty series admits no log-log fit")

    if gamma <= GAMMA_FLOOR:
        # NOT a failure of the instrument. A run whose yield is not falling has no
        # optimal round count, and the formula says so: n* -> infinity as gamma -> 0.
        return RoundBudget(
            "NO_DECAY", a=a, gamma=gamma, theta=theta, rounds_observed=observed,
            r_squared=r2,
            detail=(f"gamma={gamma:.6f} is indistinguishable from no decay, so n* "
                    f"diverges — this run is churning rather than depleting, and "
                    f"the question 'how many more rounds' has no answer"))

    if a <= theta:
        return RoundBudget(
            "ALREADY_BELOW_THRESHOLD", n_star=None, a=a, gamma=gamma, theta=theta,
            rounds_observed=observed, r_squared=r2, rounds_remaining=0,
            detail=(f"the fitted round-1 rate a={a:.3f} is already at or below "
                    f"theta={theta:g}, so the series never rose above the stopping "
                    f"threshold"))

    n_star = (a / theta) ** (1.0 / gamma)
    if not math.isfinite(n_star):
        return RoundBudget(
            "OVERFLOW", a=a, gamma=gamma, theta=theta, rounds_observed=observed,
            r_squared=r2,
            detail=(f"n* overflowed at a={a:.3f}, gamma={gamma:.6f}; the decay is "
                    f"too shallow to project a finite budget"))

    return RoundBudget(
        "OK", n_star=n_star, a=a, gamma=gamma, theta=theta,
        rounds_observed=observed, r_squared=r2,
        rounds_remaining=max(0, int(math.ceil(n_star)) - observed),
        detail=(f"fitted on {observed} observed round(s); ADVISORY only — it gates "
                f"nothing and caps nothing"))


def main(argv: Sequence[str]) -> int:
    if len(argv) > 1 and argv[1] in ("-h", "--help"):
        print(f"usage: {argv[0].split('/')[-1]} [-h|--help] [count count ...] [--theta T]")
        print()
        print(__doc__)
        return 0
    args = list(argv[1:])
    theta = DEFAULT_THETA
    if "--theta" in args:
        i = args.index("--theta")
        theta = float(args[i + 1])
        del args[i:i + 2]
    counts = [float(a) for a in args] if args else [5, 3, 2, 2]
    b = project_optimal_rounds(counts, theta=theta)
    print(f"novelty counts : {counts}")
    print(b.line())
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
