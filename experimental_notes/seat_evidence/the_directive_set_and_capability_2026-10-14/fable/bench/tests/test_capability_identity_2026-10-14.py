# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 89aa145ce9089f878946c1176c82503bde5f407162621631d5122d9f92335a47
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Executes every function of bench/capability_identity.py (additive-standard wiring test)."""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.capability_identity import (  # noqa: E402
    RETIREMENT_MIN_OUTCOMES,
    CapabilityRecord,
    MissingIdentityError,
    rank_writers,
    stable_identity,
)


def _rec(ident, name, n, k, cost):
    return CapabilityRecord(ident, name, n, k, cost)


def test_identity_is_stable_and_name_free():
    a = stable_identity("anthropic", "claude-opus", "4.6")
    assert a == stable_identity("Anthropic", " claude-opus ", "4.6")
    assert a != stable_identity("anthropic", "claude-opus", "4.7")  # version bump = new identity


def test_single_success_is_not_capability():
    """R6: 1/1 cold-start cannot outrank a seasoned mid-rate identity."""
    seasoned = _rec("s", "A", RETIREMENT_MIN_OUTCOMES, 22, cost=1.0)  # ~0.512 rate
    lucky = _rec("l", "B", 1, 1, cost=0.1)
    assert seasoned.wilson_lower() > lucky.wilson_lower()
    order = rank_writers(["l", "s"], {"s": seasoned, "l": lucky})
    assert order == ["s", "l"]  # measured first, despite lucky's 100% point estimate


def test_cold_start_orders_by_measured_cost_not_name():
    recs = {
        "x": _rec("x", "Zebra", 0, 0, cost=3.0),
        "y": _rec("y", "Aardvark", 0, 0, cost=1.0),
    }
    assert rank_writers(["x", "y"], recs) == ["y", "x"]  # cost, not alphabet


def test_measured_rank_by_wilson_lower_bound():
    recs = {
        "a": _rec("a", "A", 100, 80, cost=5.0),
        "b": _rec("b", "B", 50, 40, cost=0.1),  # same 0.8 rate, wider interval
    }
    assert rank_writers(["b", "a"], recs) == ["a", "b"]


def test_missing_identity_is_loud():
    """The 2026-08-30 Fable failure class: absent entry must REFUSE, not default."""
    with pytest.raises(MissingIdentityError):
        rank_writers(["ghost"], {})


def test_retirement_threshold_derivation():
    """n >= z^2/delta^2 at delta=0.3 -> 42.68 -> 43; Wilson half-width check."""
    import math
    z = 1.959963984540054
    assert math.ceil(z * z / 0.3 ** 2) == RETIREMENT_MIN_OUTCOMES
    n, p = RETIREMENT_MIN_OUTCOMES, 0.5
    d = 1 + z * z / n
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    assert h <= 0.15
