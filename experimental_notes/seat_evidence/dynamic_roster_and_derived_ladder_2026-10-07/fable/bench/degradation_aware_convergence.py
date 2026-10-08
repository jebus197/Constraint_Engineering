# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 48585ad06d7426912aae54ec4487a52241fe411ba6ea88233f336d662395cee2
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Degradation-aware quiet-window for the hardened convergence gate.

THE DEFECT THIS REPAIRS, measured in `bench/a_shrinking_roster_converges_sooner_
2026-10-07.py`: the gate's condition (C) -- `gamma_alt_consecutive_zero_crit`
consecutive rounds with zero novel criticals -- gets easier as the roster
shrinks: P(quiet by chance) = (1-q)^(n*K) rises by (10/7)^6 = 8.49986 going
from 6 seats to 4 under independence (and by a smaller but still >1 factor at
every measured correlation). z3 shows the observed count alone cannot separate
"quiet because resolved" from "quiet because depleted" (unsat), so the roster
must be carried BESIDE the count. The hazard is worst exactly where the gate is
weakest: in `_check_hardened_convergence`'s sparsity fallback
(`bench/reference_runner_v3.py`, cum_critical < gamma_crit_min_cumulative),
closure rests on condition (C) ALONE, so a shrinking roster attacks the whole
gate, not half of it.

THE REPAIR IS DERIVED, NOT TUNED. In the gate's own hazard model the spurious-
quiet probability depends on n and K only through the product n*K: the
evidence unit is the SEAT-ROUND, not the round. So the window requirement is
restated as `n0 * K0` quiet seat-rounds (n0 = configured roster size, K0 =
gamma_alt_consecutive_zero_crit), accumulated over trailing consecutive quiet
rounds, each round contributing the number of seats that actually responded
(`models_responded`, already recorded per round and already described in the
runner as the ground truth of who answered). Consequences, each proved in the
falsifier:
  * full roster: identical behaviour to today (K0 full rounds = n0*K0
    seat-rounds) -- the additive standard holds, nothing existing changes;
  * degraded roster: more quiet rounds are required, ceil(n0*K0 / n_live),
    holding P(spurious quiet) at or below the design point for EVERY roster
    size 1..n0 under independence (exact rational arithmetic);
  * a dropped seat never BLOCKS convergence (founder requirement 8): the run
    still converges, on proportionally more evidence;
  * under positive intra-round correlation extra seats carry LESS information
    than independent ones, so conserving seat-rounds demands at least as much
    evidence as the correlated truth requires -- the error is on the safe side.

WHETHER A DEGRADED RUN SHOULD CONVERGE AT ALL (the panel's question 2): yes --
requirement 8 says any model's dropout must not block the run to completion or
convergence -- but never SILENTLY. The convergence record carries, per round,
who responded and how many were configured, and the verdict is marked degraded
whenever any window round was short. A degraded convergence is reportable; an
undeclared one is the verification-integrity defect.

A round where a seat produced a NOVEL CRITICAL still resets the window exactly
as today: a finding is evidence of non-quiet whatever the roster was.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class RoundAttendance:
    """Who actually answered one round, against who was configured."""
    round_idx: int
    configured: tuple          # labels configured for the run
    responded: tuple           # labels in this round's `models_responded`

    @property
    def n_live(self) -> int:
        return len(set(self.responded) & set(self.configured))

    @property
    def degraded(self) -> bool:
        return self.n_live < len(set(self.configured))


def required_seat_rounds(n_configured: int, k_rounds: int) -> int:
    """The gate's evidence requirement, in seat-rounds: n0 * K0."""
    return max(1, n_configured) * max(1, k_rounds)


def quiet_window_state(
    novel_crit_by_round: Sequence[int],
    attendance: Sequence[RoundAttendance],
    k_rounds: int,
) -> Dict[str, object]:
    """Evaluate condition (C) in seat-rounds over the trailing quiet streak.

    Returns a dict the runner can both gate on and write into the report:
      quiet_ok            -- condition (C), degradation-aware
      seat_rounds_quiet   -- evidence accumulated in the trailing quiet streak
      seat_rounds_needed  -- n0 * K0
      window_rounds       -- the trailing quiet rounds consumed
      degraded_in_window  -- rounds in the window that were short of seats
      min_live_in_window  -- smallest live roster inside the window
    """
    if len(novel_crit_by_round) != len(attendance):
        raise ValueError("novel_crit_by_round and attendance must align 1:1")
    n0 = len(set(attendance[-1].configured)) if attendance else 0
    needed = required_seat_rounds(n0, k_rounds)
    quiet_sr, window, degraded = 0, [], []
    for crit, att in zip(reversed(novel_crit_by_round), reversed(list(attendance))):
        if crit != 0:
            break                      # a novel critical resets, as today
        quiet_sr += att.n_live
        window.append(att.round_idx)
        if att.degraded:
            degraded.append(att.round_idx)
    return {
        "quiet_ok": quiet_sr >= needed and needed > 0,
        "seat_rounds_quiet": quiet_sr,
        "seat_rounds_needed": needed,
        "window_rounds": list(reversed(window)),
        "degraded_in_window": list(reversed(degraded)),
        "min_live_in_window": (min(a.n_live for a in attendance
                                   if a.round_idx in set(window))
                               if window else 0),
    }


def convergence_record(state: Dict[str, object],
                       attendance: Sequence[RoundAttendance]) -> Dict[str, object]:
    """What the report must carry so a degraded convergence cannot pass as
    clean: per-round live counts beside the per-round quiet counts, and an
    explicit flag. z3 (in the 2026-10-07 artefact) shows a round cannot be both
    intact and degraded, so these fields make the two causes formally
    separable, which the bare count is proved not to be (unsat)."""
    return {
        "convergence_evidence": dict(state),
        "roster_by_round": [
            {"round": a.round_idx, "n_live": a.n_live,
             "n_configured": len(set(a.configured)),
             "responded": sorted(set(a.responded) & set(a.configured))}
            for a in attendance],
        "degraded_convergence": bool(state["degraded_in_window"]),
        "verdict_suffix": ("_DEGRADED_ROSTER" if state["degraded_in_window"]
                           else ""),
    }


def equivalent_quiet_rounds(n_configured: int, n_live: int, k_rounds: int) -> int:
    """How many quiet rounds a roster of n_live must produce: ceil(n0*K0/n_live).
    Diagnostic for the operator; `quiet_window_state` already accumulates the
    general (round-by-round varying) case."""
    if n_live <= 0:
        raise ValueError("no live seats: no evidence is obtainable at all")
    return ceil(required_seat_rounds(n_configured, k_rounds) / n_live)
