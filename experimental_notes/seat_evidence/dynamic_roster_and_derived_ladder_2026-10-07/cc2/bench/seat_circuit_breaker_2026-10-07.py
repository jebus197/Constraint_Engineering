# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3e53b226e7aa10db70f05a4422bcd486706281c8b8557c8b72c8dae5f80b715f
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The third seat state between available and benched: a CIRCUIT BREAKER.

NAMING -- THIS IS NOT A COINED LABEL. The standard software-engineering construct
for "a route temporarily excluded from dispatch, re-probed on a deadline, and
readmitted automatically on a successful probe" is the CIRCUIT BREAKER (Nygard,
*Release It!*, 2007). Its states have standard names, used verbatim here:

    CLOSED     -- requests flow; the seat is dispatched normally.
    OPEN       -- requests are not sent. Set by a failed aliveness probe or a
                  dispatch failure. Carries a re-probe deadline. NOT permanent.
    HALF_OPEN  -- the deadline passed; exactly ONE probe is allowed through.
                  It answers -> CLOSED. It does not -> OPEN again, longer backoff.

So "the third state" is: the seat's breaker is OPEN. Term, state names and
transition semantics are all off-the-shelf; nothing is invented.

WHY THIS IS NOT BENCHING (founder requirement 9):
    benching     = a POLICY decision, operator-set, with NO readmission path.
                   Forbidden by the standing rule. NOT REPRESENTED HERE AT ALL.
    breaker OPEN = a MEASURED transport fact with a readmission path that fires
                   without an operator.

Enforced STRUCTURALLY, not documented: every non-CLOSED state must carry
`reprobe_at` (__post_init__ raises otherwise), `open_breaker` has no parameter that
can suppress the deadline, and backoff is capped at MAX_BACKOFF_S so the interval
grows but never becomes infinite -- an infinite re-probe interval IS benching, and
this module cannot express it.

WHAT IT DOES NOT REMOVE (additive standard). `bench/seat_aliveness_2026-10-06.py`
`refusal_for` is kept. A run may still legitimately refuse; `should_refuse_run`
below is the roster-floor-aware decision point, and it refuses on the LIVE roster
falling below a floor rather than on any single seat failing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

CLOSED = "CLOSED"
OPEN = "OPEN"
HALF_OPEN = "HALF_OPEN"

#: First re-probe deadline, seconds. Short because the measured failure this guards
#: was a network drop that resolved in minutes (the cc2 seat, 2026-10-06).
DEFAULT_BACKOFF_S = 120
#: Ceiling on the backoff. Finite BY DESIGN: an unbounded interval is benching.
MAX_BACKOFF_S = 1800


@dataclass
class SeatBreaker:
    seat: str
    state: str = CLOSED
    reprobe_at: Optional[float] = None
    backoff_s: int = DEFAULT_BACKOFF_S
    consecutive_failures: int = 0
    #: Every transition, so the convergence record can show when the seat was down.
    history: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.state != CLOSED and self.reprobe_at is None:
            raise ValueError(
                f"{self.seat}: a non-CLOSED breaker with no re-probe deadline is "
                f"benching, which is forbidden")

    def is_benched(self) -> bool:
        """Always False. No state this module can construct is permanent."""
        return False

    def dispatchable(self, now: float) -> bool:
        return self.state == CLOSED

    def probe_due(self, now: float) -> bool:
        return (self.state in (OPEN, HALF_OPEN)
                and self.reprobe_at is not None and now >= self.reprobe_at)


def open_breaker(b: SeatBreaker, now: float, detail: str) -> SeatBreaker:
    """Transport failed. OPEN the breaker WITH a mandatory re-probe deadline."""
    b.consecutive_failures += 1
    if b.state in (OPEN, HALF_OPEN):
        b.backoff_s = min(MAX_BACKOFF_S, b.backoff_s * 2)
    b.state = OPEN
    b.reprobe_at = now + b.backoff_s
    b.history.append((now, OPEN, detail, b.backoff_s))
    return b


def half_open(b: SeatBreaker, now: float) -> SeatBreaker:
    if b.state != OPEN:
        return b
    b.state = HALF_OPEN
    b.history.append((now, HALF_OPEN, "re-probe window", b.backoff_s))
    return b


def close_breaker(b: SeatBreaker, now: float) -> SeatBreaker:
    """The re-probe answered. READMIT the seat and reset the backoff."""
    b.state = CLOSED
    b.reprobe_at = None
    b.backoff_s = DEFAULT_BACKOFF_S
    b.consecutive_failures = 0
    b.history.append((now, CLOSED, "readmitted on a successful probe", 0))
    return b


def reprobe_and_readmit(breakers: dict, now: float,
                        probe_fn: Callable[[str], bool]) -> dict:
    """Re-probe every seat whose deadline passed; readmit the ones that answer.

    THIS IS THE MISSING MID-RUN RE-PROBE. `_refuse_if_a_route_is_dead`
    (bench/reference_runner_v3.py:15109) runs ONCE, before round 1, and returns a
    refusal dict that makes `run_experiment` return without starting. There is no
    re-probe anywhere in that runner, so a seat that drops at one moment and
    recovers minutes later can never rejoin. Called at the top of each round, this
    closes that gap. `probe_fn` is injected so this is testable without a network
    and cannot drift from the dispatcher's own routing.
    """
    moved = {}
    for seat, b in breakers.items():
        if not b.probe_due(now):
            continue
        half_open(b, now)
        try:
            alive = bool(probe_fn(seat))
        except Exception:  # noqa: BLE001 -- a raising route is a dead route
            alive = False
        if alive:
            close_breaker(b, now)
            moved[seat] = CLOSED
        else:
            open_breaker(b, now, "re-probe did not answer")
            moved[seat] = OPEN
    return moved


def live_roster(breakers: dict, now: float) -> list:
    return [s for s, b in breakers.items() if b.dispatchable(now)]


def should_refuse_run(breakers: dict, now: float, floor: int = 1) -> Optional[str]:
    """Refuse only when the LIVE roster falls below the floor.

    Requirement 8: a dropped seat *"should not block an experimental run until
    completion, or convergence"*. So one OPEN breaker does NOT refuse.
    """
    live = live_roster(breakers, now)
    if len(live) >= max(1, floor):
        return None
    down = [(s, b.state, b.reprobe_at) for s, b in breakers.items()
            if not b.dispatchable(now)]
    return (f"REFUSED: live roster {len(live)} < floor {max(1, floor)}. Seats with "
            f"an OPEN breaker (each WILL be re-probed, none benched): {down}")
