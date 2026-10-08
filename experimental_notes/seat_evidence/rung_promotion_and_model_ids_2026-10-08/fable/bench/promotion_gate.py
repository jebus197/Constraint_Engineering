# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 391dd7a3b508ba117293d55be203d4c0de782996b0d2c34ea5c7b0e7884c530c
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A calibrated, bidirectional, non-absorbing promotion gate for the rung ladder.

WHAT THIS REPLACES. The founder's promote-on-one-success rule (2026-10-08) is
broken under BOTH of its possible readings:
  * absorbing (one attempt per rung ever): a p=0.90 model is kept below the top
    40.951% of the time by luck alone (1 - 0.9**5);
  * with retries (stay on a rung = keep receiving its tasks): every model with
    p > 0 reaches the top with probability 1 (geometric waits per rung), so the
    rule excludes NOTHING and the ladder is a monotone ratchet.
And the obvious Wilson-floor repair at (n=10, floor=0.50) requires 9/10 per rung
and admits a p=0.90 model to the top only 21.6% of the time -- worse. Both
failures have the same root: the parameters were CHOSEN, not derived.

THE DESIGN. Each rung holds a per-rung attempt record (this is also the
difficulty stratification: attempts at rung r are never pooled with attempts at
rung r'). Three rules:

  PROMOTE  after a block of n_gate attempts at the candidate rung with
           successes >= k_gate.
  DEMOTE   when, over the sliding window of the last W_demote attempts at the
           HELD rung, successes <= j_demote.
  STAY     otherwise. Blocks repeat indefinitely: failure is never absorbing,
           which restores the founder's bidirectional rule, and demotion is
           evidence-driven, which stops the ratchet.

EVERY PARAMETER IS DERIVED FROM A STATED ERROR TARGET, never chosen:

  Promotion gate (n_gate, k_gate): smallest n admitting a threshold k with
      P(Bin(n, p_good) >= k) >= (1 - BETA_TOTAL) ** (1/R)     [good pass rate]
      P(Bin(n, p_bad ) >= k) <= ALPHA_TOP ** (1/R)            [bad  pass rate]
  so that per CAMPAIGN (one gate block per rung, R rungs) a p_good model tops
  out with prob >= 1 - BETA_TOTAL and a p_bad model with prob <= ALPHA_TOP.

  Demotion window (W_demote, j_demote): smallest W admitting a threshold j with
      P(Bin(W, p_good) <= j) <= HOLD_SAFETY       [healthy model not demoted]
      P(Bin(W, p_drop) <= j) >= DROP_DETECT       [degraded model caught]

With retries a p_bad model still eventually passes any fixed gate (pass prob
per block is positive), so the honest guarantee is ERGODIC, not absolute: the
demotion rule bounds the fraction of time a bad model OCCUPIES a rung it cannot
hold. The falsifier measures that occupancy directly.

Run: python3 bench/test_promotion_gate_2026-10-08.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

# ------------------------- stated targets (the inputs) -------------------------
R_RUNGS = 5          # ladder depth used throughout the 2026-10-08 brief
P_GOOD = 0.90        # per-rung success rate of a model that SHOULD top out
P_BAD = 0.50         # per-rung success rate of a model that should NOT
P_DROP = 0.40        # post-degradation rate the demotion rule must catch
BETA_TOTAL = 0.05    # P(good model fails to top out per campaign) <= 5%
ALPHA_TOP = 0.001    # P(bad model tops out per campaign)          <= 0.1%
HOLD_SAFETY = 1e-3   # P(healthy model demoted per window)         <= 0.1%
DROP_DETECT = 0.95   # P(degraded model demoted per window)        >= 95%


def derive_promotion_gate(r_rungs: int = R_RUNGS, p_good: float = P_GOOD,
                          p_bad: float = P_BAD, beta_total: float = BETA_TOTAL,
                          alpha_top: float = ALPHA_TOP,
                          n_max: int = 200) -> tuple[int, int]:
    """Smallest (n, k): promote on >= k successes in a block of n attempts."""
    from scipy.stats import binom
    q_good_req = (1.0 - beta_total) ** (1.0 / r_rungs)
    q_bad_max = alpha_top ** (1.0 / r_rungs)
    for n in range(1, n_max + 1):
        for k in range(n, 0, -1):
            good = float(binom.sf(k - 1, n, p_good))
            bad = float(binom.sf(k - 1, n, p_bad))
            if good >= q_good_req and bad <= q_bad_max:
                return n, k
    raise ValueError("no gate within n_max; targets are jointly infeasible")


def derive_demotion_window(p_good: float = P_GOOD, p_drop: float = P_DROP,
                           hold_safety: float = HOLD_SAFETY,
                           drop_detect: float = DROP_DETECT,
                           w_max: int = 400) -> tuple[int, int]:
    """Smallest (W, j): demote on <= j successes in the last W held-rung attempts."""
    from scipy.stats import binom
    for w in range(1, w_max + 1):
        for j in range(w):
            healthy = float(binom.cdf(j, w, p_good))
            degraded = float(binom.cdf(j, w, p_drop))
            if healthy <= hold_safety and degraded >= drop_detect:
                return w, j
    raise ValueError("no window within w_max; targets are jointly infeasible")


@dataclass
class RungLadderState:
    """Per-model ladder state. Records are PER RUNG -- never pooled across
    rungs, so a model's record is difficulty-stratified by construction and
    attempts harvested at the back of a deep routing order (hard residuals)
    cannot poison its easy-rung record."""
    rung: int = 0
    gate_attempts: int = 0
    gate_successes: int = 0
    held_window: list = field(default_factory=list)   # 1/0, most recent last

    def observe_gate(self, success: bool, n_gate: int, k_gate: int,
                     r_rungs: int) -> None:
        """One attempt at the CANDIDATE rung (rung+1 tasks)."""
        self.gate_attempts += 1
        self.gate_successes += int(success)
        if self.gate_attempts == n_gate:
            if self.gate_successes >= k_gate and self.rung < r_rungs:
                self.rung += 1
                self.held_window = []
            self.gate_attempts = 0
            self.gate_successes = 0          # block over; next block is fresh

    def observe_held(self, success: bool, w_demote: int, j_demote: int) -> None:
        """One attempt at the HELD rung (its routine work)."""
        self.held_window.append(int(success))
        if len(self.held_window) > w_demote:
            self.held_window.pop(0)
        if (len(self.held_window) == w_demote
                and sum(self.held_window) <= j_demote and self.rung > 0):
            self.rung -= 1
            self.held_window = []
