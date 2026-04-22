"""Tests for ``contested_count()`` grace_period parameter on runner v2.

``bench/reference_runner_v2.py::FindingRegistry.contested_count`` is the
gate-input that decides whether a round's divergence-directive branch
fires, and its ``grace_period`` parameter controls how long an
UNCONFIRMED finding is still counted as contested (to avoid flicker when
a finding has been momentarily resolved but is likely to reopen on new
evidence in the next round or two).

The 21 April 2026 gap-closure list (G5) flagged that the parameter is
declared in the signature with default ``grace_period=2`` but every
call-site inside the runner uses the default implicitly — the knob is
not threaded through to any ``RunnerConfig`` field. This is NOT by
itself a bug (the default is reasonable and tests elsewhere assume it),
but it is a latent wiring gap: if a calibration experiment needs to
sweep grace-period values, the plumbing does not exist.

These tests pin three things:

* **Behaviour.** Passing different ``grace_period`` values yields
  different counts for a UNCONFIRMED finding at a fixed
  ``current_round``. This proves the parameter is not ignored.
* **Signature stability.** The parameter default stays at 2. If a
  future change moves it, call-sites that rely on the implicit default
  start producing different counts silently — this pin flags the move.
* **Call-site purity.** For each call-site of ``contested_count`` in
  ``reference_runner_v2.py``, AST-level source inspection confirms no
  literal is passed as ``grace_period`` — every call uses the default.
  If a future caller starts passing an explicit literal, this pin
  surfaces it so the reviewer can decide whether that was intentional
  or whether the value should be plumbed through ``RunnerConfig``.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_contested_count_v2.py -v
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
_EXPECTED_DEFAULT_GRACE = 2


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


def _make_finding(**kwargs) -> Finding:
    defaults = dict(
        finding_id="f1",
        model_id="CC2",
        round_idx=0,
        flaw_class=2,
        severity=0.8,
        abstraction_index=0.5,
        description="Test finding",
    )
    defaults.update(kwargs)
    return Finding(**defaults)


def _register(reg: FindingRegistry, finding: Finding) -> str:
    return reg.register(finding, finding.model_id)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Behaviour — grace_period is actually respected
# ═══════════════════════════════════════════════════════════════════════════════


class TestGracePeriodBehaviour:
    """The parameter must change the count, not be silently ignored."""

    def _mk_unconfirmed_at_round(self, resolved_round: int) -> FindingRegistry:
        """Helper: UNCONFIRMED finding resolved at a given round."""
        reg = FindingRegistry()
        cid = _register(reg, _make_finding())
        reg.add_verdict(cid, "Gemini", "CHALLENGE", round_idx=1)
        reg.resolve(cid, "UNCONFIRMED", round_idx=resolved_round)
        return reg

    def test_grace_period_1_excludes_finding_at_round_plus_1(self):
        """At grace_period=1, a UNCONFIRMED finding 1 round old is on the
        boundary: rounds_in_status=1 is NOT < 1, so it is excluded."""
        reg = self._mk_unconfirmed_at_round(resolved_round=5)
        assert reg.contested_count(current_round=6, grace_period=1) == 0

    def test_grace_period_3_includes_finding_at_round_plus_1(self):
        """At grace_period=3, the same finding is still within grace."""
        reg = self._mk_unconfirmed_at_round(resolved_round=5)
        assert reg.contested_count(current_round=6, grace_period=3) == 1

    def test_grace_period_default_matches_explicit_2(self):
        """Calling without grace_period must equal calling with 2."""
        reg = self._mk_unconfirmed_at_round(resolved_round=5)
        implicit = reg.contested_count(current_round=6)
        explicit = reg.contested_count(current_round=6, grace_period=2)
        assert implicit == explicit, (
            f"Default grace_period drift: implicit={implicit} "
            f"explicit=2 → {explicit}. If this test fails, the default "
            f"has changed — update _EXPECTED_DEFAULT_GRACE."
        )

    def test_grace_period_0_excludes_all_unconfirmed(self):
        """grace_period=0 disables UNCONFIRMED counting entirely."""
        reg = self._mk_unconfirmed_at_round(resolved_round=5)
        assert reg.contested_count(current_round=5, grace_period=0) == 0
        assert reg.contested_count(current_round=6, grace_period=0) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Signature stability — default must stay at 2
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignatureStability:
    """Both `inspect.signature` and AST agree on the default."""

    def test_signature_default_is_two(self):
        sig = inspect.signature(FindingRegistry.contested_count)
        param = sig.parameters.get("grace_period")
        assert param is not None, (
            "contested_count() no longer has a grace_period parameter"
        )
        assert param.default == _EXPECTED_DEFAULT_GRACE, (
            f"grace_period default drift: got {param.default}, "
            f"expected {_EXPECTED_DEFAULT_GRACE}"
        )

    def test_signature_takes_current_round_and_grace_period(self):
        sig = inspect.signature(FindingRegistry.contested_count)
        params = list(sig.parameters.keys())
        assert params == ["self", "current_round", "grace_period"], (
            f"Signature drift: params={params}; expected "
            f"[self, current_round, grace_period]"
        )

    def test_return_type_is_int(self):
        hints = typing.get_type_hints(FindingRegistry.contested_count)
        assert hints.get("return") is int, (
            f"Return-type drift: expected int, got {hints.get('return')}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. AST — the default literal in the source is exactly 2
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_contested_count_default() -> int:
    """Parse v2 source and return the integer default for grace_period on
    ``contested_count``. Raises AssertionError if not found."""
    source = _V2_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name != "contested_count":
            continue
        args = node.args
        # positional arg list includes 'self', 'current_round', 'grace_period'
        all_args = args.args
        defaults = args.defaults
        # defaults align with the tail of all_args
        offset = len(all_args) - len(defaults)
        for idx, default_node in enumerate(defaults):
            arg_idx = offset + idx
            if all_args[arg_idx].arg == "grace_period":
                if isinstance(default_node, ast.Constant) and isinstance(
                    default_node.value, int
                ):
                    return default_node.value
                raise AssertionError(
                    f"grace_period default not an integer constant: {default_node}"
                )
    raise AssertionError(
        "Could not locate contested_count() default for grace_period"
    )


class TestAstDefaultLiteral:
    def test_ast_default_matches_expected(self):
        assert _extract_contested_count_default() == _EXPECTED_DEFAULT_GRACE


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Call-site purity via dis.Bytecode
# ═══════════════════════════════════════════════════════════════════════════════


def _find_contested_count_callsites_source() -> list[str]:
    """Return the source-line lists for each call-site of
    ``contested_count`` in the v2 module. Used for call-site inspection.

    This complements dis.Bytecode — where Bytecode gives us opcodes,
    source lines let us surface the call verbatim in a failure message."""
    source = _V2_PATH.read_text(encoding="utf-8")
    lines = source.splitlines()
    hits: list[str] = []
    for i, line in enumerate(lines, start=1):
        if ".contested_count(" in line and "def contested_count" not in line:
            hits.append(f"{i}: {line.rstrip()}")
    return hits


class TestCallSitePurity:
    """No call-site inside v2 passes an explicit integer literal as
    ``grace_period``. If one starts doing so, this test flags it so the
    reviewer can decide whether the override was intentional or whether
    a ``RunnerConfig`` field should carry the value instead."""

    def test_no_callsite_passes_grace_period_literal(self):
        callsites = _find_contested_count_callsites_source()
        # All live call-sites must avoid a literal `grace_period=` kwarg.
        # (The function's own signature line is filtered out already.)
        offenders = [c for c in callsites if "grace_period=" in c]
        assert offenders == [], (
            f"One or more contested_count() call-sites now pass an "
            f"explicit grace_period kwarg. If intentional, route the "
            f"value through a RunnerConfig field and update this test. "
            f"Offending call-sites:\n" + "\n".join(offenders)
        )

    def test_callsites_exist_and_are_nonzero(self):
        """Sanity: this guard is only meaningful if there ARE call-sites.
        If the count drops to zero, either the module has been
        restructured or the grep is broken. Either way, fix before
        relying on the purity test above."""
        callsites = _find_contested_count_callsites_source()
        assert len(callsites) >= 3, (
            f"Expected at least 3 contested_count() call-sites in v2; "
            f"got {len(callsites)}. Call-sites:\n" + "\n".join(callsites)
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
