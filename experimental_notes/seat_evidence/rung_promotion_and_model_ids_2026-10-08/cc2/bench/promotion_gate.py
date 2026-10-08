# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a327a92259510e641a4efb1528396ee500a551e66d76618da2e4a6a90f412b52
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Promotion gate for the rung ladder - parameters DERIVED, not chosen.

WHAT THIS REPLACES. `bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py`
measures two promotion criteria and reports both as inadequate:

  * promote on ONE success per rung: a model with true per-rung resolve rate
    p=0.90 reaches the top of a 5-rung ladder 0.59049 of the time;
  * promote on a Wilson lower bound over 10 attempts at a floor of 0.50
    (which needs 9 of 10): the same model reaches the top 0.21611302 of the
    time, which that script reads as the bound gate being the worse rule.

THAT READING IS A COMPARISON AT UNMATCHED ERROR RATES. The two rules sit at
different operating points: the one-success rule also admits a p=0.50 model to
the top 0.03125 of the time, where the n=10 bound gate admits it 1.43e-10 of the
time. Comparing only the true-positive rate of two rules whose false-positive
rates differ by 8 orders of magnitude cannot order them. Scanned over
(n, floor) with n<=30, 138 bound-gate parameterisations beat the one-success
rule on BOTH rates at once; the cheapest is n=4, floor=0.20 (k*=3), at
TPR 0.764459 against 0.590490 and FPR 2.980e-03 against 3.125e-02. So the
defect is the parameterisation n=10, floor=0.50 - which forces k*=9, i.e. an
implied point-estimate threshold of 0.90 exactly equal to the good model's true
rate, putting the test at its own coin-flip point - and not the mechanism.

WHAT IS DERIVED HERE, from a stated false-negative target:

  1. `attempts_per_rung` - from (p_good, floor, beta, rungs). No parameter is
     chosen; the scan is required rather than a closed form because k*(n, floor)
     steps, so Q(p_good) is NOT monotone in n (n=16 gives k*=12 and
     Q=0.982996; n=18 gives k*=14 and Q=0.971806 - more attempts, worse power).
  2. `window_z` - from the multiplicity of a sliding window re-evaluated on
     every attempt. A fixed z=1.96 re-evaluated this way is a sequential test
     with no correction: a p=0.50 model clears a floor of 0.50 somewhere in 190
     attempts with probability 0.6572. Bonferroni over the M-W+1 overlapping
     windows gives the z below; it is conservative, and the measured rate at it
     is reported by the falsifier rather than asserted.

WHY A SLIDING WINDOW AND NOT A POOLED RECORD, measured rather than judged. Both
restore bidirectionality (no absorbing rung, no re-test schedule: the gate is
re-read on every attempt). They differ on detecting capability LOST, which is the
founder's bidirectional requirement. On a model held at 0.90 for 100 attempts and
then dropped to 0.30, median attempts to demote: pooled 293.0, never demoted in
0.0195 of runs; sliding window W=19, 20.0 attempts, never demoted in 0.0000.
The window dominates on the named property at no cost in true-positive rate, so
it is used ALONE - the two are not composed, because composing them would add
surface without a demonstrated advantage over the window by itself.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

Z95 = 1.959963984540054


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval for k successes in n trials."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def successes_required(n: int, floor: float, z: float = Z95) -> int | None:
    """Smallest k whose Wilson lower bound at n trials exceeds `floor`.

    None when no k<=n clears it - the sample size cannot decide the rung at all,
    which is a result and not an error.
    """
    for k in range(n + 1):
        if wilson(k, n, z)[0] > floor:
            return k
    return None


def required_per_rung_pass(beta: float, rungs: int) -> float:
    """Per-rung pass probability needed for a total false-negative rate <= beta.

    The rungs are independent gates, so P(reach top) = Q**rungs. Requiring
    Q**rungs >= 1-beta gives Q >= (1-beta)**(1/rungs). This multiplicative
    compounding is the whole reason a per-rung gate must be tighter than the
    end-to-end target: at beta=0.05 and rungs=5 the per-rung gate must pass a
    capable model 0.9897937816869885 of the time, not 0.95.
    """
    if not 0.0 < beta < 1.0:
        raise ValueError("beta must be in (0,1)")
    if rungs < 1:
        raise ValueError("rungs must be >= 1")
    return (1.0 - beta) ** (1.0 / rungs)


@dataclass(frozen=True)
class GateParameters:
    attempts_per_rung: int
    successes_per_rung: int
    floor: float
    rungs: int
    beta_target: float
    p_good: float
    per_rung_pass_required: float
    per_rung_pass_achieved: float
    p_reaches_top: float
    attempts_to_climb: int


def derive_attempts_per_rung(
    p_good: float,
    floor: float,
    beta: float,
    rungs: int,
    z: float = Z95,
    max_n: int = 2000,
) -> GateParameters:
    """Smallest attempts-per-rung meeting a stated false-negative target.

    `p_good`  - the per-rung resolve rate that DEFINES capable at this rung.
    `floor`   - the rung's capability threshold; promotion means demonstrably
                above it, so the gate is a lower bound against `floor`.
    `beta`    - tolerated probability that a model at `p_good` fails to reach
                the top rung by luck alone.

    Raises ValueError if no n <= max_n meets the target: at p_good <= floor no
    sample size can, because the gate is then asking a model to demonstrate it
    is above a threshold it does not exceed.
    """
    if not 0.0 <= floor < 1.0:
        raise ValueError("floor must be in [0,1)")
    if not 0.0 < p_good <= 1.0:
        raise ValueError("p_good must be in (0,1]")
    need = required_per_rung_pass(beta, rungs)
    from scipy.stats import binom
    for n in range(1, max_n + 1):
        k = successes_required(n, floor, z)
        if k is None:
            continue
        q = float(binom.sf(k - 1, n, p_good))
        if q >= need:
            return GateParameters(
                attempts_per_rung=n, successes_per_rung=k, floor=floor,
                rungs=rungs, beta_target=beta, p_good=p_good,
                per_rung_pass_required=need, per_rung_pass_achieved=q,
                p_reaches_top=q ** rungs, attempts_to_climb=n * rungs,
            )
    raise ValueError(
        f"no attempts_per_rung <= {max_n} reaches beta={beta} for p_good={p_good} "
        f"against floor={floor}; p_good must exceed floor with room to measure")


def derive_window_z(window: int, horizon: int, alpha: float) -> float:
    """z for a sliding window re-evaluated on every attempt.

    A window of `window` attempts slid across `horizon` attempts offers
    horizon-window+1 overlapping decision points. Holding the probability that a
    model AT the floor is ever promoted at <= alpha over the horizon needs the
    per-decision level alpha/(horizon-window+1); Bonferroni, so conservative -
    the windows are positively dependent, and the achieved rate measured by
    `test_promotion_gate.py` is below alpha, which is the direction a bound
    should err in. Reported, not hidden: the conservatism costs nothing in
    true-positive rate at p_good=0.90 over horizon=190 (measured 1.0000).
    """
    if window < 1 or horizon < window:
        raise ValueError("need 1 <= window <= horizon")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0,1)")
    from scipy.stats import norm
    decisions = horizon - window + 1
    return float(norm.ppf(1.0 - alpha / decisions))


@dataclass
class RungRecord:
    """A model's record at ONE rung: the last `window` outcomes, nothing else.

    Q1 ANSWERED HERE. A failure at rung r+1 does not touch rung r's record, so a
    model does not lose the rung below on one bad attempt. What stops it
    accumulating rungs it can no longer hold is that a rung is HELD rather than
    granted: the record is re-read on every attempt, and the same record that
    promoted the model demotes it when the upper bound falls below the floor.
    There is no absorbing state and no re-test schedule - the re-test is the
    ordinary dispatch stream.
    """
    window: int
    outcomes: list = field(default_factory=list)

    def record(self, success: bool) -> None:
        self.outcomes.append(bool(success))
        if len(self.outcomes) > self.window:
            del self.outcomes[:-self.window]

    @property
    def attempts(self) -> int:
        return len(self.outcomes)

    @property
    def successes(self) -> int:
        return sum(self.outcomes)

    def promotes(self, floor: float, z: float) -> bool:
        """Full window of evidence AND a lower bound clear of the floor."""
        if self.attempts < self.window:
            return False
        return wilson(self.successes, self.attempts, z)[0] > floor

    def demotes(self, floor: float, z: float) -> bool:
        """Full window AND an upper bound below the floor - never on one failure."""
        if self.attempts < self.window:
            return False
        return wilson(self.successes, self.attempts, z)[1] < floor


def observed_difficulty(routing_result, max_rungs: int):
    """Resolution depth from a RoutingResult, WITH its censoring flag.

    `bench/routing.py` records `rungs_tried`, and the artefact's claim 4 reads
    that as "observed difficulty is available today and needs no classifier".
    The field exists; the value is not a usable difficulty label on its own, for
    two reasons visible in `routing.py`:

      * `resolve_via_routing` slices `list(rungs)[:_budget]` with
        `_budget = max_rungs` when max_rungs is non-zero, so every finding whose
        true depth exceeds the cap reports exactly `max_rungs`. Depths are
        RIGHT-CENSORED at the cap, and under the default max_rungs=2 every
        finding harder than rung 2 carries the same label as one resolved at
        rung 2.
      * `route` returns `rungs_tried=0` on the DUPLICATE path, which is not a
        depth of zero.

    Returns (depth, censored). A censored depth is a lower bound on difficulty
    and must enter any ordering as such - never as an equality.
    """
    depth = int(getattr(routing_result, "rungs_tried", 0) or 0)
    if getattr(routing_result, "verdict", "") == "DUPLICATE":
        return (0, False)
    censored = bool(
        not getattr(routing_result, "resolved", False)
        and max_rungs
        and depth >= max_rungs
    )
    return (depth, censored)


def main() -> int:
    g = derive_attempts_per_rung(p_good=0.90, floor=0.50, beta=0.05, rungs=5)
    print("DERIVED promotion gate (p_good=0.90, floor=0.50, beta=0.05, rungs=5):")
    for k, v in g.__dict__.items():
        print(f"   {k}: {v}")
    zw = derive_window_z(window=g.attempts_per_rung,
                         horizon=10 * g.attempts_per_rung, alpha=0.05)
    print(f"\nDERIVED window z (W={g.attempts_per_rung}, "
          f"horizon={10*g.attempts_per_rung}, alpha=0.05): {zw:.6f}")
    print(f"   successes required in-window at that z: "
          f"{successes_required(g.attempts_per_rung, 0.50, zw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
