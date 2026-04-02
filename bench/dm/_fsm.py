"""CDSFL Dynamic Management — Round Progression FSM (Area 3).

Deterministic acyclic finite state machine for round progression.
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from bench.dm._types import (
    DynamicManagementConfig,
    Event,
    State,
    TerminationReason,
)


@dataclass
class RoundProgressionFSM:
    """Deterministic acyclic FSM for round progression.

    States: {BLIND, SYNTH, ROUND_1, ..., ROUND_{N-1}, TERMINAL}
    Events: {sigma_complete, sigma_converged, sigma_diminished, sigma_max, sigma_fail_critical}

    The FSM is forward-only (acyclic). TERMINAL is the unique absorbing state.
    Terminates in at most N + 2 transitions.

    Example::

        fsm = RoundProgressionFSM(DynamicManagementConfig())
        print(fsm.current_state)  # "BLIND"
        fsm.transition(Event.COMPLETE)
        print(fsm.current_state)  # "SYNTH"
        fsm.transition(Event.COMPLETE)
        print(fsm.current_state)  # "ROUND_1"
    """

    config: DynamicManagementConfig
    current_state: str = field(init=False)
    current_round: int = field(init=False, default=-1)
    termination_reason: Optional[TerminationReason] = field(init=False, default=None)
    history: List[Tuple[str, Event, str]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.current_state = State.BLIND.value
        self.current_round = 0  # BLIND = round 0

    @property
    def is_terminal(self) -> bool:
        return self.current_state == State.TERMINAL.value

    @property
    def max_round_idx(self) -> int:
        """Maximum iterative round index (N-1)."""
        return self.config.max_rounds - 1

    def valid_events(self) -> List[Event]:
        """Return events valid in the current state."""
        if self.is_terminal:
            return []

        s = self.current_state
        events = [Event.FAIL_CRITICAL]  # Always valid from any non-terminal

        if s == State.BLIND.value:
            events.append(Event.COMPLETE)
        elif s == State.SYNTH.value:
            events.extend([Event.COMPLETE, Event.CONVERGED, Event.DIMINISHED])
        elif s.startswith("ROUND_"):
            k = int(s.split("_")[1])
            events.extend([Event.CONVERGED, Event.DIMINISHED])
            if k < self.max_round_idx:
                events.append(Event.COMPLETE)
            if k == self.max_round_idx:
                events.append(Event.MAX)

        return events

    def transition(self, event: Event) -> str:
        """Execute a state transition.

        Args:
            event: The event triggering the transition.

        Returns:
            The new state name.

        Raises:
            ValueError: If the event is invalid in the current state.
            RuntimeError: If the FSM is already terminal.
        """
        if self.is_terminal:
            raise RuntimeError(
                f"FSM is terminal (reason={self.termination_reason}). "
                f"No further transitions."
            )

        valid = self.valid_events()
        if event not in valid:
            raise ValueError(
                f"Event {event.value} invalid in state {self.current_state}. "
                f"Valid: {[e.value for e in valid]}"
            )

        old_state = self.current_state
        new_state: str

        if event == Event.FAIL_CRITICAL:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.FAILURE

        elif event == Event.CONVERGED:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.CONVERGED

        elif event == Event.DIMINISHED:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.DIMINISHED

        elif event == Event.MAX:
            new_state = State.TERMINAL.value
            self.termination_reason = TerminationReason.MAX_ROUNDS

        elif event == Event.COMPLETE:
            if old_state == State.BLIND.value:
                new_state = State.SYNTH.value
            elif old_state == State.SYNTH.value:
                new_state = State.round_state(1)
                self.current_round = 1
            elif old_state.startswith("ROUND_"):
                k = int(old_state.split("_")[1])
                new_state = State.round_state(k + 1)
                self.current_round = k + 1
            else:
                raise ValueError(f"Unexpected state for COMPLETE: {old_state}")
        else:
            raise ValueError(f"Unhandled event: {event}")

        self.history.append((old_state, event, new_state))
        self.current_state = new_state
        return new_state

    def select_event(
        self,
        converged: bool,
        diminished: bool,
        critical_failure: bool,
        round_complete: bool,
    ) -> Event:
        """Select the highest-priority applicable event.

        Implements event priority (HARD):
        FAIL_CRITICAL > CONVERGED > DIMINISHED > COMPLETE > MAX

        Args:
            converged: Whether convergence predicate holds.
            diminished: Whether diminishing returns predicate holds.
            critical_failure: Whether an unrecoverable failure occurred.
            round_complete: Whether all allocations are complete/handled.

        Returns:
            The highest-priority applicable event.
        """
        if critical_failure:
            return Event.FAIL_CRITICAL

        if converged and Event.CONVERGED in self.valid_events():
            return Event.CONVERGED

        if diminished and Event.DIMINISHED in self.valid_events():
            return Event.DIMINISHED

        if round_complete:
            s = self.current_state
            if s.startswith("ROUND_"):
                k = int(s.split("_")[1])
                if k == self.max_round_idx:
                    return Event.MAX
            return Event.COMPLETE

        # No event applicable — caller should wait for completion
        raise ValueError(
            f"No applicable event in state {self.current_state} with "
            f"converged={converged}, diminished={diminished}, "
            f"critical_failure={critical_failure}, round_complete={round_complete}"
        )

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """K=1: Same FSM. Single model's findings. Convergence/stop still apply."""
        fsm = RoundProgressionFSM(config)
        # Should be able to progress through all states
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        assert fsm.current_state == State.SYNTH.value
        fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        assert fsm.current_state == State.round_state(1)
        fsm.transition(Event.CONVERGED)  # ROUND_1 -> TERMINAL
        assert fsm.is_terminal
        assert fsm.termination_reason == TerminationReason.CONVERGED
        return True

    @staticmethod
    def validate_no_failures(config: DynamicManagementConfig) -> bool:
        """No failures: sigma_fail_critical never fires. Linear chain."""
        fsm = RoundProgressionFSM(config)
        states_visited = [fsm.current_state]
        # Walk through all rounds
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        states_visited.append(fsm.current_state)
        fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        states_visited.append(fsm.current_state)
        for k in range(1, config.max_rounds - 1):
            fsm.transition(Event.COMPLETE)
            states_visited.append(fsm.current_state)
        fsm.transition(Event.MAX)  # ROUND_{N-1} -> TERMINAL
        states_visited.append(fsm.current_state)
        # Verify linear chain (no repeated states)
        return len(states_visited) == len(set(states_visited))
