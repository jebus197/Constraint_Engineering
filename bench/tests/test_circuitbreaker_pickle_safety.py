"""Regression: CircuitBreakerTripped must survive the multiprocessing
boundary in runner_core.dispatch_to_model (Exp 40 Unit B->C seam fix,
2026-05-18).

Root cause (found live during Unit B's hardened-gate run): the
exception's custom __init__(condition, model, phase, detail="") calls
super().__init__(<single formatted string>), so self.args == (one
string,). Default Exception pickling reconstructs via
cls(*self.args) -> a 1-arg __init__ call -> "TypeError: __init__()
missing 2 required positional arguments: 'model' and 'phase'".
dispatch_to_model runs each model in a multiprocessing.Process and does
`raise payload` on the worker's exception (pickled across an mp.Queue),
so every orchestrator-raised CircuitBreakerTripped arrived as a
TypeError, was swallowed by the broad except, and the circuit breaker
was silently inoperative arc-wide. Fix: __reduce__ reconstructs from
the 4 original args.

These tests pin the fix at the exact failure mechanism.
"""
from __future__ import annotations

import multiprocessing as mp
import pickle

import pytest

from bench.experiment_11_orchestrator import CircuitBreakerTripped


def test_pickle_round_trip_preserves_all_four_args():
    e = CircuitBreakerTripped(
        "empty_response", "google/gemini-3.1-pro-preview", "dispatch",
        "0 chars after 3 attempts",
    )
    r = pickle.loads(pickle.dumps(e))
    assert isinstance(r, CircuitBreakerTripped)
    assert r.condition == "empty_response"
    assert r.model == "google/gemini-3.1-pro-preview"
    assert r.phase == "dispatch"
    assert r.detail == "0 chars after 3 attempts"
    assert str(r) == str(e)


def test_pickle_round_trip_default_detail():
    e = CircuitBreakerTripped("halt_cond", "CC2", "round_3")
    r = pickle.loads(pickle.dumps(e))
    assert (r.condition, r.model, r.phase, r.detail) == (
        "halt_cond", "CC2", "round_3", "")
    assert isinstance(r, CircuitBreakerTripped)


def _worker(q):
    try:
        raise CircuitBreakerTripped(
            "empty_response", "DeepSeek", "dispatch", "CoT budget exhausted")
    except Exception as ex:  # noqa: BLE001
        q.put(("error", ex))


def test_real_multiprocessing_queue_round_trip_reraises_intact():
    """The exact dispatch_to_model path: worker raises, parent gets the
    pickled exception off an mp.Queue and re-raises it. Pre-fix this
    raised TypeError; post-fix CircuitBreakerTripped propagates intact."""
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(q,))
    p.start()
    p.join(timeout=30)
    assert not p.is_alive()
    status, payload = q.get_nowait()
    assert status == "error"
    with pytest.raises(CircuitBreakerTripped) as ei:
        raise payload
    assert ei.value.model == "DeepSeek"
    assert ei.value.phase == "dispatch"
    assert ei.value.condition == "empty_response"


def test_reduce_returns_four_arg_reconstruction():
    e = CircuitBreakerTripped("c", "m", "p", "d")
    cls, args = e.__reduce__()
    assert cls is CircuitBreakerTripped
    assert args == ("c", "m", "p", "d")
    # The reconstruction call must itself succeed (the pre-fix bug was
    # exactly that cls(*one_string_arg) failed).
    assert isinstance(cls(*args), CircuitBreakerTripped)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
