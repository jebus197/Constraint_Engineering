"""Tests for ``open_crit_high_count()`` REOPENED-status handling on runner v2.

``bench/reference_runner_v2.py::FindingRegistry.open_crit_high_count`` is the
active gate-input for Exp 40–54 (runner v1 is frozen). The v2 and v1 bodies
were identical at the 22 April 2026 baseline; the risk addressed here is
silent drift — if a future refactor drops ``REOPENED`` from the v2
``_NON_TERMINAL`` tuple, a high-severity claim that moved OPEN → CLOSED →
REOPENED would stop counting toward the critical/high gate and launch
conditions would tighten silently.

These tests pin three things:

* **Behaviour.** A synthetic REOPENED high-severity finding must be counted
  by ``open_crit_high_count()`` exactly like an OPEN finding of the same
  severity, with no mutation of registry state.
* **Signature.** ``open_crit_high_count()`` takes no parameters beyond
  ``self`` and returns ``int``. ``contested_count()`` keeps its
  ``current_round`` + ``grace_period=2`` signature (the sister function at
  line 464 used by G5 downstream).
* **Source truth.** ``ast.parse`` on the v2 source confirms that the
  ``_NON_TERMINAL`` tuple literal inside ``open_crit_high_count`` contains
  ``"REOPENED"``. This catches a regression that mutates the tuple's
  content even if the behaviour test somehow passes.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_open_crit_high_count_v2.py -v
"""

from __future__ import annotations

import ast
import inspect
import os
import sys
import typing
from pathlib import Path

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._types import Finding
from bench.reference_runner_v2 import FindingRegistry


_V2_PATH = Path(_project_root) / "bench" / "reference_runner_v2.py"


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures — minimal Finding + Registry set-up
# ═══════════════════════════════════════════════════════════════════════════════


def _make_finding(**kwargs) -> Finding:
    defaults = dict(
        finding_id="f1",
        model_id="CC2",
        round_idx=0,
        flaw_class=2,
        severity=0.8,  # above the 0.7 crit/high threshold
        abstraction_index=0.5,
        description="Test finding",
    )
    defaults.update(kwargs)
    return Finding(**defaults)


def _register(reg: FindingRegistry, finding: Finding) -> str:
    return reg.register(finding, finding.model_id)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Behavioural pins — REOPENED high-severity must be counted
# ═══════════════════════════════════════════════════════════════════════════════


class TestReopenedHighSeverityCounted:
    """REOPENED findings at or above the 0.7 severity threshold must count."""

    def test_reopened_high_severity_counts_as_open(self):
        """The core G4 regression — REOPENED must count."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        # Path to REOPENED: open → closed → reopened
        reg.resolve(cid, "CLOSED", round_idx=2)
        reg.resolve(cid, "REOPENED", round_idx=5)
        assert reg.entries[cid]["status"] == "REOPENED"
        assert reg.open_crit_high_count() == 1

    def test_reopened_below_severity_threshold_excluded(self):
        """REOPENED claims below 0.7 severity must NOT count (threshold holds)."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.5))
        reg.resolve(cid, "CLOSED", round_idx=2)
        reg.resolve(cid, "REOPENED", round_idx=5)
        assert reg.entries[cid]["status"] == "REOPENED"
        assert reg.open_crit_high_count() == 0

    def test_reopened_and_open_counted_together(self):
        """Multiple high-severity claims in mixed OPEN/REOPENED states all count."""
        reg = FindingRegistry()
        cid1 = _register(reg, _make_finding(finding_id="f1", severity=0.85))
        cid2 = _register(reg, _make_finding(finding_id="f2", severity=0.9))
        # f2: push to REOPENED
        reg.resolve(cid2, "CLOSED", round_idx=2)
        reg.resolve(cid2, "REOPENED", round_idx=5)
        # f1 stays OPEN
        assert reg.entries[cid1]["status"] == "OPEN"
        assert reg.entries[cid2]["status"] == "REOPENED"
        assert reg.open_crit_high_count() == 2

    def test_exhausted_reopened_excluded(self):
        """REOPENED + exhausted: still excluded (exhaustion wins)."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        reg.resolve(cid, "CLOSED", round_idx=2)
        reg.resolve(cid, "REOPENED", round_idx=5)
        # Hand-set exhaustion (mirrors what _update_finding_statuses would do)
        reg.entries[cid]["exhausted"] = True
        assert reg.open_crit_high_count() == 0

    def test_closed_high_severity_excluded(self):
        """Sanity check: CLOSED is terminal and must NOT count."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        reg.resolve(cid, "CLOSED", round_idx=2)
        assert reg.entries[cid]["status"] == "CLOSED"
        assert reg.open_crit_high_count() == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Purity pin — function must not mutate state (R3-5 regression adjacent)
# ═══════════════════════════════════════════════════════════════════════════════


class TestReaderPurity:
    """``open_crit_high_count()`` is a pure reader — no state mutation."""

    def test_does_not_set_exhausted_flag(self):
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        reg.resolve(cid, "CLOSED", round_idx=2)
        reg.resolve(cid, "REOPENED", round_idx=5)
        pre_exhausted = reg.entries[cid].get("exhausted")
        reg.open_crit_high_count()
        post_exhausted = reg.entries[cid].get("exhausted")
        assert pre_exhausted == post_exhausted, (
            "open_crit_high_count() mutated exhausted flag — must stay pure reader"
        )

    def test_idempotent_under_repeated_call(self):
        reg = FindingRegistry()
        cid = _register(reg, _make_finding(severity=0.9))
        reg.resolve(cid, "CLOSED", round_idx=2)
        reg.resolve(cid, "REOPENED", round_idx=5)
        a = reg.open_crit_high_count()
        b = reg.open_crit_high_count()
        c = reg.open_crit_high_count()
        assert a == b == c, (
            f"open_crit_high_count() not idempotent: {a} -> {b} -> {c}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Signature pin — parameter contract must not drift silently
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignatureStability:
    """``inspect.signature`` pins the callable's public contract."""

    def test_open_crit_high_count_takes_no_positional_args(self):
        sig = inspect.signature(FindingRegistry.open_crit_high_count)
        # `self` only — no other parameters.
        params = list(sig.parameters.keys())
        assert params == ["self"], (
            f"Signature drift: open_crit_high_count now takes {params}; "
            f"expected [self]. If a param was added intentionally, update "
            f"this pin and every caller."
        )

    def test_open_crit_high_count_returns_int(self):
        # The v2 source uses `from __future__ import annotations`, so raw
        # `inspect.signature` returns the annotation as a string ("int").
        # Use typing.get_type_hints() to resolve it to the actual class.
        hints = typing.get_type_hints(FindingRegistry.open_crit_high_count)
        assert hints.get("return") is int, (
            f"Return-type drift: expected int, got {hints.get('return')}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AST source-truth pin — _NON_TERMINAL tuple literal contains REOPENED
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_non_terminal_tuple() -> tuple[str, ...]:
    """Parse runner v2 source and extract the ``_NON_TERMINAL`` tuple literal
    inside ``open_crit_high_count``. Raises AssertionError if not found."""
    source = _V2_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != "open_crit_high_count":
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Assign):
                continue
            if len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "_NON_TERMINAL"):
                continue
            if not isinstance(stmt.value, ast.Tuple):
                continue
            elts = []
            for e in stmt.value.elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    elts.append(e.value)
            return tuple(elts)
    raise AssertionError(
        "Could not locate _NON_TERMINAL tuple inside "
        "open_crit_high_count() in bench/reference_runner_v2.py"
    )


class TestAstSourceTruth:
    """Static-source guard against silent REOPENED drop."""

    def test_non_terminal_contains_reopened(self):
        elts = _extract_non_terminal_tuple()
        assert "REOPENED" in elts, (
            f"Regression: _NON_TERMINAL tuple no longer contains REOPENED. "
            f"Got {elts}. If this drop is intentional, update every gate-"
            f"input consumer in lockstep and then update this test."
        )

    def test_non_terminal_also_contains_open_and_contested(self):
        elts = _extract_non_terminal_tuple()
        assert "OPEN" in elts and "CONTESTED" in elts, (
            f"Regression: _NON_TERMINAL missing expected states. Got {elts}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
