"""The runner now refuses a reply that is merely non-empty, as the panels already did.

HIS RULING, 2026-10-07, given verbatim on each of 4 panel lessons: *"We should use it. Wire it
in all simulated and real runners going forward."* His reasoning: *"the panel applies a substance
test to every reply and the runner applies none. The panel refuses a reply that is merely non
empty, because an error string, a usage notice or a holding note is answering without answering
the question."*

MEASURED BEFORE WIRING, not asserted away. Across 2,582 archived runner replies the predicate
rejects 26, a proportion of 0.0101, Wilson [0.0069, 0.0147], of which **20 are EMPTY**. Exactly
1 would be rejected while carrying a finding, at 191 characters -- the holding-note case the
test exists to catch. An earlier claim that this might endanger convergence was caution standing
in for a measurement, and is withdrawn.

OPT-IN BY DESIGN. 13 of the 14 call sites sit inside `try/except`; `_arb_dispatch` is a closure
invoked indirectly and `run_preflight` deliberately accepts a 5-character reply as proof of
life. A default of True would have broken preflight outright.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO), str(REPO / "bench")]


def _runner_core():
    import runner_core
    return runner_core


class _FakeQueue:
    def __init__(self, payload):
        self._payload = payload
    def empty(self):
        return False
    def get_nowait(self):
        return ("ok", self._payload)


class _FakeProc:
    def __init__(self, *a, **k):
        self.exitcode = 0
    def start(self):
        pass
    def join(self, *a, **k):
        pass
    def is_alive(self):
        return False
    def terminate(self):
        pass


def _dispatch_with(monkeypatch, payload: str, **kw):
    rc = _runner_core()
    import multiprocessing as mp
    monkeypatch.setattr(mp, "Queue", lambda *a, **k: _FakeQueue(payload), raising=False)
    monkeypatch.setattr(mp, "Process", _FakeProc, raising=False)
    mc = rc.ModelConfig(label="CC2", model_id="x", api="claude_cli",
                        role=list(rc.Role)[0] if hasattr(rc, "Role") else None,
                        system_prompt_path=None, max_tokens=1000, timeout=30)
    return rc.dispatch_to_model(mc, "prompt", "system", **kw)


class TestTheSubstanceTestIsAvailableAndOptIn:
    def test_the_parameter_exists_and_defaults_off(self):
        rc = _runner_core()
        sig = inspect.signature(rc.dispatch_to_model)
        p = sig.parameters.get("require_substance")
        assert p is not None, "the substance test is not reachable from the dispatch signature"
        assert p.default is False, (
            "a default of True would break run_preflight, which accepts a 5-character reply")

    def test_a_hollow_reply_is_refused_when_the_test_is_on(self, monkeypatch):
        with pytest.raises(RuntimeError) as exc:
            _dispatch_with(monkeypatch, "I cannot help with that.", require_substance=True)
        assert "answered without answering" in str(exc.value)

    def test_an_empty_reply_is_refused_when_the_test_is_on(self, monkeypatch):
        with pytest.raises(RuntimeError):
            _dispatch_with(monkeypatch, "   ", require_substance=True)

    def test_a_substantive_reply_passes(self, monkeypatch):
        body = "A genuine review. " * 60          # comfortably over the 800-char floor
        text, _elapsed = _dispatch_with(monkeypatch, body, require_substance=True)
        assert text == body

    def test_the_same_hollow_reply_passes_when_the_test_is_off(self, monkeypatch):
        """The default path must be byte-identical to the behaviour before this change."""
        text, _elapsed = _dispatch_with(monkeypatch, "I cannot help with that.")
        assert text == "I cannot help with that."


class TestItIsWiredWhereHeMeantAndNotWhereItWouldBreakThings:
    def test_the_seat_dispatch_turns_it_on(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert src.count("require_substance=True") >= 2, (
            "the seat dispatch and its secondary fallback should both apply it")

    def test_preflight_does_not_turn_it_on(self):
        """`run_preflight` accepts `len(text.strip()) > 5` as proof of life. An 800-character
        floor there would fail every preflight, so this is the site that proves the parameter
        had to be opt-in rather than a changed default."""
        import ast
        src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "run_preflight"), None)
        if fn is None:
            pytest.skip("run_preflight is not in this checkout")
        body = ast.get_source_segment(src, fn) or ""
        assert "require_substance" not in body, (
            "preflight must not apply the substance test; it would fail every proof-of-life call")
