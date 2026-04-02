"""CDSFL Dynamic Management — Manager Event Stream.

Buffered event stream for the PM real-time monitoring interface.
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

from typing import Callable, List, Optional

from bench.dm._types import (
    ManagerEvent,
    ManagerEventType,
)


class ManagerEventStream:
    """Buffered event stream for the PM monitoring interface.

    Supports both callback-based (push) and polling-based (pull) consumption.

    Example::

        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 0))
        events = stream.drain()  # returns and clears buffer
    """

    def __init__(
        self,
        callback: Optional[Callable[[ManagerEvent], None]] = None,
    ) -> None:
        self._callback = callback
        self._buffer: List[ManagerEvent] = []
        self._all_events: List[ManagerEvent] = []  # permanent log

    def emit(self, event: ManagerEvent) -> None:
        """Emit an event. Calls callback if registered, always buffers.

        Args:
            event: The event to emit.
        """
        self._buffer.append(event)
        self._all_events.append(event)
        if self._callback is not None:
            self._callback(event)

    def drain(self) -> List[ManagerEvent]:
        """Return and clear the event buffer (pull-based consumption).

        Returns:
            List of events since last drain.
        """
        events = self._buffer
        self._buffer = []
        return events

    def peek(self) -> List[ManagerEvent]:
        """Return the event buffer without clearing it."""
        return list(self._buffer)

    @property
    def all_events(self) -> List[ManagerEvent]:
        """Return the complete event log (never cleared)."""
        return list(self._all_events)

    def events_by_type(self, event_type: ManagerEventType) -> List[ManagerEvent]:
        """Filter all events by type."""
        return [e for e in self._all_events if e.event_type == event_type]

    def events_by_model(self, model_id: str) -> List[ManagerEvent]:
        """Filter all events by model."""
        return [e for e in self._all_events if e.model_id == model_id]
