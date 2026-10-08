# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6f8337965f099704fe2d0eac5f85751ffa4f24b4da13df39441ac6aeacfb3d83
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Per-seat circuit breaker: the third state between available and benched.

THE NAME IS THE STANDARD SOFTWARE-ENGINEERING TERM, not a coinage: this is the
circuit-breaker stability pattern (Nygard, "Release It!"), whose states are
CLOSED (requests flow), OPEN (requests withheld after failure), and HALF_OPEN
(a trial request probes whether the fault has cleared). Mapped onto seats:

  CLOSED    -- the seat is available and is dispatched normally.
  OPEN      -- the seat is TRANSIENTLY UNREACHABLE: its last dispatch or probe
               failed. It is withheld from dispatch for the current round so
               the round proceeds (founder requirement 8: "any model" dropping
               out must not block the run), and the round is recorded as
               degraded (see bench/degradation_aware_convergence.py).
  HALF_OPEN -- at every subsequent round boundary the seat is re-probed with
               the existing aliveness probe (PROBE_PROMPT / PROBE_TOKEN from
               bench/seat_aliveness_2026-10-06.py -- reused, not duplicated).
               A passing probe CLOSES the breaker and the seat is dispatched
               again from that round on.

WHY THIS IS NOT BENCHING BY ANOTHER NAME (founder requirement 9: "Benching a
model is setting it aside permanently. A model might come back if it recovers
from a technical issue, or a network outage. They are different conditions."):
  1. There is NO terminal state and NO removal API. The dataclass has no
     'benched' value and no method deletes a seat; the falsifier asserts both.
  2. An OPEN seat is re-probed at EVERY round boundary, unconditionally --
     readmission is automatic on recovery, never an operator policy choice.
  3. The outage is NEVER a capability signal (requirement 6, and the standing
     note in seat_aliveness: "it must never be read as a capability signal").
     A seat rejoins at exactly the ladder position its measured capability
     gives it; nothing here writes to the capability estimator.

DIVISION OF LABOUR WITH THE EXISTING ONE-SHOT PROBE, which is kept unchanged
(additive standard): `_refuse_if_a_route_is_dead` still refuses to START a run
with a dead route -- before anything is spent, the founder decides. This module
governs MID-RUN failures, where refusing would discard the rounds already paid
for. `refusal_for`'s rule that "dropping a seat is benching it" is a statement
about permanent removal; withholding one round's dispatch from a seat that is
re-probed next round is a different condition, which is requirement 9 verbatim.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


class BreakerState(enum.Enum):
    CLOSED = "closed"          # available
    OPEN = "open"              # transiently unreachable; re-probed each round
    HALF_OPEN = "half_open"    # probe in flight at a round boundary
    # Deliberately no terminal member: benching is forbidden, so the type
    # cannot express it.


@dataclass
class SeatBreaker:
    seat: str
    state: BreakerState = BreakerState.CLOSED
    opened_at_round: Optional[int] = None
    reopened_count: int = 0
    history: List[str] = field(default_factory=list)

    def record_dispatch_failure(self, round_idx: int, detail: str) -> None:
        """A real dispatch (or probe) failed: withhold until a probe passes."""
        self.state = BreakerState.OPEN
        self.opened_at_round = round_idx
        self.history.append(f"r{round_idx}: OPEN ({detail[:80]})")

    def round_boundary_probe(self, round_idx: int,
                             probe: Callable[[], bool]) -> bool:
        """Re-probe an OPEN seat at a round boundary. CLOSED seats skip the
        probe (their liveness is evidenced by answering rounds). Returns True
        iff the seat is dispatchable this round."""
        if self.state is BreakerState.CLOSED:
            return True
        self.state = BreakerState.HALF_OPEN
        ok = bool(probe())
        if ok:
            self.state = BreakerState.CLOSED
            self.history.append(f"r{round_idx}: readmitted (probe passed)")
        else:
            self.state = BreakerState.OPEN
            self.reopened_count += 1
            self.history.append(f"r{round_idx}: still OPEN (probe failed)")
        return ok


class RosterBreakers:
    """Breakers for a whole roster. `dispatchable(round_idx, probes)` is what
    the runner consults at each round boundary; its complement is what the
    round's attendance record carries."""

    def __init__(self, seats) -> None:
        self._b: Dict[str, SeatBreaker] = {s: SeatBreaker(s) for s in seats}

    def __getitem__(self, seat: str) -> SeatBreaker:
        return self._b[seat]

    def dispatchable(self, round_idx: int,
                     probes: Dict[str, Callable[[], bool]]) -> List[str]:
        out = []
        for seat, br in self._b.items():
            probe = probes.get(seat, lambda: False)
            if br.round_boundary_probe(round_idx, probe):
                out.append(seat)
        return out

    def states(self) -> Dict[str, str]:
        return {s: b.state.value for s, b in self._b.items()}
