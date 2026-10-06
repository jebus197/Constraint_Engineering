#!/usr/bin/env python3
"""Ask each seat to print Ready! before handing it real work.

THE FOUNDER'S ASK, 2026-10-06: *"perhaps we should build a simple 'aliveness test',
where the models get up to 3 attempts, by simply asking it to print 'Ready!'"*

WHY IT EARNS ITS PLACE, MEASURED THE SAME NIGHT. The cc2 seat was dispatched on a
1236-word brief at 03:41 and returned `ok: False` with a response of 0 words after
**2423.7 seconds** across 2 dispatcher attempts, because the founder's network dropped
mid-round. The full brief was sent, the full reply window was waited out, and the round
produced nothing. A 1-word probe would have reached the same verdict in seconds.
That is the whole case: the expensive thing is not the failure, it is discovering the
failure at the END of a 40-minute dispatch instead of the start.

WHAT A FAILED PROBE DOES, and it is NOT benching the seat. `feedback_no_benching` is
standing: models are never rested, skipped or dropped. So a dead seat does not get
quietly removed from the roster and the round does not proceed without it -- the round
is REFUSED, naming the seat and what its probe returned. The operator (or
`scripts/panel_round_watchdog_2026-10-06.py`) then retries, and the retry is cheap
precisely because the probe fails fast. Probe plus watchdog is the composition the
founder asked for when he said to retry over a few-minute intervals until the network
resolves.

WHAT COUNTS AS ALIVE. The reply must contain "ready", case-insensitively. Not
"non-empty": a route that returns an error string, a usage notice or a holding note is
answering, but it is not answering THIS question, and the project has already been bitten
by a reply accepted on the sole condition of being non-empty.

THE PROBE IS DELIBERATELY NOT A CAPABILITY TEST. It establishes that the route carries
a request and returns an answer. It says nothing about whether the model is any good,
and it must never be read as a capability signal -- that is what the measured ladder is
for.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

#: The whole prompt. Kept to 1 line because its cost is the point.
PROBE_PROMPT = "Reply with exactly one word: Ready!"

#: What a live route must say. Substring, case-insensitive.
PROBE_TOKEN = "ready"

#: The founder's number.
DEFAULT_ATTEMPTS = 3

#: Short, because a probe that waits as long as a real dispatch saves nothing.
DEFAULT_TIMEOUT_S = 60


@dataclass
class AliveResult:
    seat: str
    alive: bool
    attempts_used: int
    elapsed_s: float
    detail: str
    replies: list = field(default_factory=list)


def probe_seat(seat: str, caller, attempts: int = DEFAULT_ATTEMPTS,
               timeout: int = DEFAULT_TIMEOUT_S) -> AliveResult:
    """Ask 1 seat to print Ready!, up to `attempts` times.

    `caller` is a 0-argument callable returning the seat's reply as a string, or
    raising. It is injected rather than selected here so the probe can be tested
    without a network and so it cannot drift from the dispatcher's own routing.
    """
    t0 = time.time()
    replies = []
    for n in range(1, max(1, attempts) + 1):
        try:
            reply = caller()
        except Exception as exc:  # noqa: BLE001 — a raising route is a dead route
            replies.append(f"attempt {n}: {type(exc).__name__}: {exc}")
            continue
        text = reply if isinstance(reply, str) else ""
        replies.append(f"attempt {n}: {text[:120]!r}")
        if PROBE_TOKEN in text.lower():
            return AliveResult(seat, True, n, round(time.time() - t0, 2),
                               f"answered on attempt {n} of {attempts}", replies)
        if not text.strip():
            continue  # empty is a transport failure, not an answer
    return AliveResult(seat, False, max(1, attempts), round(time.time() - t0, 2),
                       f"no reply containing {PROBE_TOKEN!r} in {attempts} attempt(s)",
                       replies)


def probe_roster(callers: dict, attempts: int = DEFAULT_ATTEMPTS,
                 timeout: int = DEFAULT_TIMEOUT_S, serialise: bool = True) -> dict:
    """Probe every seat. Returns {seat: AliveResult}.

    SERIALISED BY DEFAULT, and that is not an efficiency choice. Every
    `claude_cli` seat authenticates against the SAME Max subscription, and the
    project has already measured concurrent free seats failing each other
    (p = 1.6e-7 against chance). A probe that fires the whole roster at once would
    manufacture the very failure it is testing for.
    """
    out = {}
    for seat, caller in callers.items():
        out[seat] = probe_seat(seat, caller, attempts=attempts, timeout=timeout)
        if not serialise:
            continue
    return out


def refusal_for(results: dict) -> str | None:
    """A refusal message naming every dead seat, or None if all answered.

    Returns a REFUSAL rather than a filtered roster, because dropping a seat is
    benching it and the standing rule forbids that.
    """
    dead = [r for r in results.values() if not r.alive]
    if not dead:
        return None
    lines = [f"REFUSED: {len(dead)} of {len(results)} seat(s) did not answer the "
             f"aliveness probe."]
    for r in dead:
        lines.append(f"  {r.seat}: {r.detail} ({r.elapsed_s}s)")
        for line in r.replies[:3]:
            lines.append(f"      {line}")
    lines.append("  The roster is NOT reduced: a seat is never benched. Retry when "
                 "the route is back, or re-run under the panel watchdog.")
    return "\n".join(lines)


def claude_cli_caller(model_id: str, timeout: int = DEFAULT_TIMEOUT_S):
    """A caller for a `claude_cli` seat, built from the dispatcher's own route.

    Imported lazily so this module can be tested, and its guard run, without the
    orchestrator's import cost or any credential being touched.
    """
    def _call() -> str:
        from experiment_11_orchestrator import call_claude_cli
        return call_claude_cli(
            model_id=model_id,
            system_prompt=None,
            user_prompt=PROBE_PROMPT,
            max_tokens=16,
            timeout=timeout,
            max_retries=1,   # the probe does its OWN attempts; see probe_seat
        )
    return _call
