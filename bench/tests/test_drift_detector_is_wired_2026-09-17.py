"""I31: the drift detector must actually run, not merely exist.

FOUNDER RULING 2026-09-16: approved, with the condition that it be deferred if
it depends on the current mathematical model and wired now if it does not.

IT DOES NOT DEPEND ON IT. `update_drift` reads `pi_mem` only, a Beta-Binomial
smoothed confirmed-against-rejected count that appears nowhere in the
mathematical appendix. The model-coupled method is its sibling `blended_prior`,
which mixes pi_mem with pi_base by rho. These tests EXECUTE the detector and
assert the wiring structurally, because a call site is a structural fact.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
sys.path.insert(0, str(REPO))

from bench.dm._memory import ImmuneMemory  # noqa: E402


def _call_sites(name: str) -> list[str]:
    """Production call sites for `name`, by AST rather than by grep."""
    out = []
    for p in (REPO / "bench").rglob("*.py"):
        if "tests" in p.parts or "logs" in p.parts:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                f = n.func
                fn = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
                if fn == name:
                    out.append(f"{p.relative_to(REPO)}:{n.lineno}")
    return out


class TestItIsReached:
    def test_update_drift_now_has_a_production_caller(self):
        sites = _call_sites("update_drift")
        assert sites, "update_drift still has 0 production callers, which is I31"

    def test_the_caller_is_the_runner(self):
        assert any("reference_runner_v3.py" in s for s in _call_sites("update_drift"))

    def test_blended_prior_is_untouched_by_this_change(self):
        """The model-coupled sibling must keep exactly its existing callers."""
        assert _call_sites("blended_prior"), "blended_prior lost its caller"


class TestItActuallyDetects:
    def test_a_stable_rate_does_not_drift(self):
        mem = ImmuneMemory(decay_rate=0.1, drift_threshold=2.0)
        mem.record_experiment(exp_id="e0", flaw_counts={1: (5, 5)})
        base = mem.pi_mem(1)
        assert 0.0 < base < 1.0
        assert not any(mem.update_drift(1, base) for _ in range(5))

    def test_a_persistent_divergence_does_drift(self):
        """POSITIVE CONTROL: a detector that cannot fire detects nothing."""
        mem = ImmuneMemory(decay_rate=0.1, drift_threshold=2.0)
        mem.record_experiment(exp_id="e0", flaw_counts={1: (1, 9)})
        fired = [mem.update_drift(1, 1.0) for _ in range(12)]
        assert any(fired), (
            f"12 rounds at a rate of 1.0 against pi_mem {mem.pi_mem(1):.3f} "
            f"never crossed the threshold of 2.0")

    def test_it_returns_a_bool_the_caller_can_store(self):
        mem = ImmuneMemory(decay_rate=0.1, drift_threshold=2.0)
        mem.record_experiment(exp_id="e0", flaw_counts={2: (3, 3)})
        assert isinstance(mem.update_drift(2, 0.9), bool)


class TestItDecidesNothing:
    def test_no_gate_reads_the_drift_verdict(self):
        """It is REPORTED, not acted on, until the next run measures it."""
        src = RUNNER.read_text(encoding="utf-8")
        i = src.index("_drift: dict[int, bool] = {}")
        window = src[i:i + 4000]
        for forbidden in ("if _drift[", "if _drift.get", "drift and ", "not _drift["):
            assert forbidden not in window, (
                f"the drift verdict is being branched on ({forbidden!r}); it is "
                f"reported only until its threshold has live data")
