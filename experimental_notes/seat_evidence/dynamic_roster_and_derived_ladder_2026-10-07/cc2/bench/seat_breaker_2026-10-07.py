# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'dynamic_roster_and_derived_ladder_2026-10-07', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 169402de7d0d363ca93ff8770abb2093c92a90a44103cd8b6397e20ec6ef48cb
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The third seat state: a circuit breaker whose OPEN state is transient by construction.

THE NAME IS NOT COINED. The state the design needs between "available" and
"benched" is the OPEN state of a CIRCUIT BREAKER -- the standard
software-engineering construct for a route that has failed and must be retried
after a backoff rather than abandoned (Nygard, *Release It!*, 2007; the same
CLOSED / OPEN / HALF_OPEN naming used by Hystrix, Polly, resilience4j and
Envoy). HALF_OPEN is the readmission trial. I am using the established term
rather than inventing project vocabulary, per the naming rule: a coined label
reads as agreed terminology to the next reader and is nobody's agreed term.

WHAT IT REPAIRS, with the conflation quoted from the code itself. `refusal_for`
in `bench/seat_aliveness_2026-10-06.py` documents itself as returning *"a
REFUSAL rather than a filtered roster, because dropping a seat is benching it
and the standing rule forbids that."* That treats one condition as two
conditions' worth of consequence. The founder's requirement 9 separates them:
*"Benching a model is setting it aside permanently. A model might come back if
it recovers from a technical issue, or a network outage. They are different
conditions."*

  * BENCHING is a permanent POLICY choice: the seat is removed from the declared
    roster and will not be asked again. Forbidden, and UNREACHABLE HERE -- there
    is no transition in this module that leads to it, and no method that removes
    a seat from `declared`. That is the structural answer to "how is this not
    benching by another name": not by promising, but by having no state to
    bench into.
  * The OPEN state is a transient FACT about a route: it failed its probe now,
    it is not dispatched this round, and it is re-probed automatically after a
    backoff. The seat remains in the declared roster the whole time, which is
    exactly what `bench/degraded_convergence_2026-10-07.py` compares the live
    roster against -- so an OPEN seat makes a convergence DEGRADED rather than
    silently shrinking the denominator.

WHY THE EXISTING PRE-ROUND-1 REFUSAL IS KEPT AND NOT REPLACED. Before round 1
nothing has been spent, so refusing and retrying is cheap and loses no work; the
probe was measured establishing a route in 5.91 s against the 2423.7 s a failed
round took to establish the same fact. MID-RUN the trade reverses: refusing
discards every round already paid for, and the founder's requirement 8 is
explicit that a dropout *"should not block an experimental run until completion,
or convergence."* So this module governs the mid-run case only and leaves
`_refuse_if_a_route_is_dead` (reference_runner_v3.py line 15109) untouched. That
is an addition beside an existing feature, not a removal of one.

THE PROBE IS REUSED, NOT REWRITTEN. `probe_seat` already implements the
founder's 3-attempt Ready! check and already distinguishes an answer from a
non-empty reply. HALF_OPEN calls it. A second probe implementation would be a
second thing to drift.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

#: Standard circuit-breaker state names. There is DELIBERATELY no fourth,
#: terminal state: benching is not representable in this type.
CLOSED = "CLOSED"        # route healthy, seat dispatched normally
OPEN = "OPEN"            # route failed, seat not dispatched this round, retried
HALF_OPEN = "HALF_OPEN"  # backoff elapsed, a probe is being allowed through

#: Rounds to wait before the first readmission probe, then doubling. Bounded so a
#: long outage does not push the next probe past the end of the run, which would
#: BE benching by arithmetic rather than by decision.
DEFAULT_BACKOFF_ROUNDS = 1
DEFAULT_MAX_BACKOFF_ROUNDS = 4


@dataclass
class SeatBreaker:
    """One seat's route health. Never removes the seat from the roster."""
    seat: str
    state: str = CLOSED
    consecutive_failures: int = 0
    opened_at_round: int | None = None
    next_probe_round: int | None = None
    backoff: int = DEFAULT_BACKOFF_ROUNDS
    max_backoff: int = DEFAULT_MAX_BACKOFF_ROUNDS
    history: list = field(default_factory=list)   # [(round, event, detail)]

    # ── transitions ──────────────────────────────────────────────────────────
    def record_failure(self, round_idx: int, detail: str = "") -> str:
        """The seat did not answer this round. CLOSED/HALF_OPEN -> OPEN."""
        self.consecutive_failures += 1
        if self.state != OPEN:
            self.opened_at_round = round_idx
        else:
            self.backoff = min(self.backoff * 2, self.max_backoff)
        self.state = OPEN
        self.next_probe_round = round_idx + self.backoff
        self.history.append((round_idx, "FAILURE->OPEN", detail))
        return self.state

    def record_success(self, round_idx: int, detail: str = "") -> str:
        """The seat answered. Any state -> CLOSED, and the backoff resets."""
        self.consecutive_failures = 0
        was = self.state
        self.state = CLOSED
        self.opened_at_round = None
        self.next_probe_round = None
        self.backoff = DEFAULT_BACKOFF_ROUNDS
        self.history.append((round_idx, f"{was}->CLOSED", detail))
        return self.state

    def due_for_probe(self, round_idx: int) -> bool:
        """Is the backoff elapsed? An OPEN seat is ALWAYS eventually due."""
        if self.state == CLOSED:
            return False
        return self.next_probe_round is None or round_idx >= self.next_probe_round

    def enter_half_open(self, round_idx: int) -> str:
        self.state = HALF_OPEN
        self.history.append((round_idx, "OPEN->HALF_OPEN", "backoff elapsed"))
        return self.state

    def dispatchable(self, round_idx: int) -> bool:
        """Should this seat receive this round's brief?

        CLOSED always. OPEN only once the backoff elapses, and then it is probed
        first -- a 1-word probe, not the full brief, so an outage costs seconds
        rather than the 2423.7 s a full dispatch on a dead route cost on
        2026-10-06.
        """
        return self.state == CLOSED or self.due_for_probe(round_idx)


class BreakerBoard:
    """Every declared seat's breaker. The declared roster is IMMUTABLE here."""

    def __init__(self, declared: list, max_backoff: int = DEFAULT_MAX_BACKOFF_ROUNDS):
        self.declared = sorted({str(s) for s in declared})
        self.breakers = {s: SeatBreaker(s, max_backoff=max_backoff)
                         for s in self.declared}

    # There is deliberately NO remove()/bench()/drop() method. Benching is a
    # permanent policy choice and is not representable.

    def live(self, round_idx: int) -> list:
        """Seats to dispatch this round, in declared order."""
        return [s for s in self.declared if self.breakers[s].dispatchable(round_idx)]

    def open_seats(self) -> list:
        return [s for s in self.declared if self.breakers[s].state == OPEN]

    def states(self) -> dict:
        return {s: self.breakers[s].state for s in self.declared}

    def readmit_due(self, round_idx: int, probe_fn: Callable[[str], bool]) -> list:
        """Probe every OPEN seat whose backoff has elapsed; readmit those that answer.

        `probe_fn(seat) -> bool` is injected so this is testable without a network
        and so it cannot drift from the dispatcher's own routing -- the same reason
        `probe_seat` injects its caller. In production it wraps
        `seat_aliveness_2026-10-06.probe_seat`, whose `.alive` IS the boolean.

        Returns the seats readmitted this round.
        """
        readmitted = []
        for s in self.open_seats():
            b = self.breakers[s]
            if not b.due_for_probe(round_idx):
                continue
            b.enter_half_open(round_idx)
            try:
                ok = bool(probe_fn(s))
            except Exception as exc:  # noqa: BLE001 - a raising route is a dead route
                b.record_failure(round_idx, f"probe raised {type(exc).__name__}")
                continue
            if ok:
                b.record_success(round_idx, "readmitted on aliveness probe")
                readmitted.append(s)
            else:
                b.record_failure(round_idx, "readmission probe did not answer")
        return readmitted

    def never_benched(self) -> bool:
        """Every declared seat is still in the roster, whatever its route did.

        An invariant, asserted rather than documented: the whole point of the
        third state is that this cannot become false.
        """
        return set(self.breakers) == set(self.declared)


def probe_fn_from_aliveness(callers: dict, attempts: int = 3, timeout: int = 60):
    """Wrap the EXISTING probe so HALF_OPEN reuses it rather than reimplementing it."""
    def _probe(seat: str) -> bool:
        import importlib.util as iu
        import sys
        from pathlib import Path
        p = Path(__file__).resolve().parent / "seat_aliveness_2026-10-06.py"
        spec = iu.spec_from_file_location("cdsfl_seat_aliveness_breaker", p)
        AL = iu.module_from_spec(spec)
        sys.modules["cdsfl_seat_aliveness_breaker"] = AL
        spec.loader.exec_module(AL)
        caller = callers.get(seat)
        if caller is None:
            return False
        return AL.probe_seat(seat, caller, attempts=attempts, timeout=timeout).alive
    return _probe
