"""Regression tests for the primary/secondary route fallback
architecture (2026-05-22, founder-directed).

Every model in the panel carries a secondary route used as a one-shot
in-round fallback when its primary route returns empty / raises after
retries. The fallback is per-turn (next turn reverts to primary unless
empty again). This preserves the `feedback_no_benching.md` protocol:
no model misses a round. The prior EXCLUDE-on-repeated-EMPTY policy
in FailureHandler is removed — that was functionally benching by
another name.

These tests pin:
  - ModelConfig carries optional secondary_api / secondary_model_id.
  - dispatch(use_secondary=True) swaps in secondary fields and routes
    via the secondary api; raises if no secondary configured.
  - All 5 models in load_default_config() have secondaries configured.
  - FailureHandler EMPTY policy never returns EXCLUDE (no benching).
  - Source-truth: no EXCLUDE token in the FailureHandler EMPTY branch.
  - Runner exposes _secondary_route_usage and _persistent_empty_flags
    accumulators (HIL signal surface for route-degradation review).
"""

from __future__ import annotations

import dataclasses
import inspect
from pathlib import Path
from unittest.mock import patch

import pytest

from bench.experiment_11_orchestrator import (
    ModelConfig,
    dispatch,
    load_default_config,
)
from bench.dm._failure_handler import FailureHandler


# ────────────────────────────────────────────────────────────────────────────
# 1. ModelConfig schema
# ────────────────────────────────────────────────────────────────────────────


class TestModelConfigSecondaryFields:
    def test_secondary_fields_default_to_none(self):
        mc = ModelConfig(
            label="Test", model_id="test/model", api="openrouter",
            role="participant", system_prompt_path=None,
        )
        assert mc.secondary_api is None
        assert mc.secondary_model_id is None

    def test_secondary_fields_settable(self):
        mc = ModelConfig(
            label="Test", model_id="test/model", api="openrouter",
            role="participant", system_prompt_path=None,
            secondary_api="codex_exec", secondary_model_id="gpt-5.5",
        )
        assert mc.secondary_api == "codex_exec"
        assert mc.secondary_model_id == "gpt-5.5"

    def test_dataclasses_replace_swaps_primary_secondary(self):
        """The runner uses dataclasses.replace to construct a one-shot
        ModelConfig promoting secondary fields to primary for the
        fallback dispatch. Pin that this works."""
        mc = ModelConfig(
            label="Gemini", model_id="google/gemini-3.1-pro-preview",
            api="openrouter", role="participant",
            system_prompt_path=None,
            secondary_api="google",
            secondary_model_id="gemini-3.1-pro-preview",
        )
        swapped = dataclasses.replace(
            mc, api=mc.secondary_api, model_id=mc.secondary_model_id,
            extra_body=None, secondary_api=None, secondary_model_id=None,
        )
        assert swapped.api == "google"
        assert swapped.model_id == "gemini-3.1-pro-preview"
        assert swapped.label == "Gemini"  # label preserved for logs/HIL
        assert swapped.secondary_api is None  # no recursive fallback


# ────────────────────────────────────────────────────────────────────────────
# 2. All 5 panel models have secondaries
# ────────────────────────────────────────────────────────────────────────────


class TestPanelSecondaryRoutes:
    def test_every_model_in_default_config_has_secondary(self):
        cfg = load_default_config()
        for mc in cfg.models:
            assert mc.secondary_api is not None, (
                f"{mc.label}: secondary_api must be configured "
                f"(founder rule 2026-05-22: every model has a secondary)"
            )
            assert mc.secondary_model_id is not None, (
                f"{mc.label}: secondary_model_id must be configured"
            )

    def test_cc2_secondary_is_openrouter(self):
        cfg = load_default_config()
        cc2 = next(m for m in cfg.models if m.label == "CC2")
        assert cc2.secondary_api == "openrouter"
        assert "anthropic/claude-opus" in cc2.secondary_model_id

    def test_codex_and_chatgpt_share_codex_exec_secondary(self):
        # Both Codex and ChatGPT use the codex CLI as secondary —
        # same GPT-5.5 backend, one subscription covers both.
        cfg = load_default_config()
        codex = next(m for m in cfg.models if m.label == "Codex")
        chatgpt = next(m for m in cfg.models if m.label == "ChatGPT")
        assert codex.secondary_api == "codex_exec"
        assert chatgpt.secondary_api == "codex_exec"

    def test_gemini_secondary_is_google_direct(self):
        cfg = load_default_config()
        gemini = next(m for m in cfg.models if m.label == "Gemini")
        assert gemini.secondary_api == "google"

    def test_deepseek_secondary_is_openrouter(self):
        # DeepSeek primary is direct (post 2026-05-20 reroute);
        # OpenRouter slug is the cheap backup.
        cfg = load_default_config()
        ds = next(m for m in cfg.models if m.label == "DeepSeek")
        assert ds.secondary_api == "openrouter"
        assert "deepseek" in ds.secondary_model_id


# ────────────────────────────────────────────────────────────────────────────
# 3. dispatch(use_secondary=...) behaviour
# ────────────────────────────────────────────────────────────────────────────


class TestDispatchUseSecondary:
    def test_use_secondary_true_routes_via_secondary_api(self):
        """When use_secondary=True, dispatch routes via the secondary
        fields, not the primary. Verified by mocking out the route
        functions and asserting the secondary one was called."""
        mc = ModelConfig(
            label="Test", model_id="primary/model", api="openrouter",
            role="participant", system_prompt_path=None,
            secondary_api="deepseek", secondary_model_id="secondary-model",
        )
        with patch("bench.experiment_11_orchestrator.call_deepseek",
                   return_value="secondary-response") as mock_secondary, \
             patch("bench.experiment_11_orchestrator.call_openrouter",
                   return_value="primary-response") as mock_primary:
            result = dispatch(
                mc, "user prompt", "system prompt", use_secondary=True
            )
        assert result == "secondary-response"
        mock_secondary.assert_called_once()
        mock_primary.assert_not_called()

    def test_use_secondary_false_routes_via_primary_api(self):
        mc = ModelConfig(
            label="Test", model_id="primary/model", api="openrouter",
            role="participant", system_prompt_path=None,
            secondary_api="deepseek", secondary_model_id="secondary-model",
        )
        with patch("bench.experiment_11_orchestrator.call_openrouter",
                   return_value="primary-response") as mock_primary, \
             patch("bench.experiment_11_orchestrator.call_deepseek",
                   return_value="secondary-response") as mock_secondary:
            result = dispatch(mc, "user prompt", "system prompt")
        assert result == "primary-response"
        mock_primary.assert_called_once()
        mock_secondary.assert_not_called()

    def test_use_secondary_raises_when_not_configured(self):
        mc = ModelConfig(
            label="NoSecondary", model_id="primary/model", api="openrouter",
            role="participant", system_prompt_path=None,
        )
        with pytest.raises(RuntimeError, match="No secondary route"):
            dispatch(mc, "user prompt", "system prompt", use_secondary=True)

    def test_secondary_drops_primary_extra_body(self):
        """The primary's extra_body (e.g. reasoning.effort for openrouter)
        is route-specific and must NOT carry over to the secondary.
        Pinning via Gemini's openrouter→google fallback."""
        mc = ModelConfig(
            label="Gemini", model_id="google/gemini-3.1-pro-preview",
            api="openrouter", role="participant", system_prompt_path=None,
            extra_body={"reasoning": {"effort": "high"}},
            secondary_api="google",
            secondary_model_id="gemini-3.1-pro-preview",
        )
        captured_extra_body = []
        def mock_gemini(**kw):
            captured_extra_body.append(kw.get("extra_body"))
            return "ok"
        # call_gemini signature does NOT have extra_body — confirms the
        # secondary path correctly does not try to pass it. Pin by
        # mocking call_gemini and verifying it's invoked without
        # extra_body (would TypeError otherwise).
        with patch("bench.experiment_11_orchestrator.call_gemini",
                   return_value="ok") as mock_g:
            result = dispatch(mc, "user", "sys", use_secondary=True)
        assert result == "ok"
        kwargs = mock_g.call_args.kwargs
        assert "extra_body" not in kwargs, (
            "primary extra_body must not be forwarded to secondary route"
        )


# ────────────────────────────────────────────────────────────────────────────
# 4. FailureHandler EMPTY policy — never EXCLUDE
# ────────────────────────────────────────────────────────────────────────────


class TestFailureHandlerEmptyNoExclude:
    """Pin that EMPTY never produces EXCLUDE (no benching).

    Uses a minimal FailureHandler setup; the existing test_dynamic
    fixtures cover the wider behaviour. These tests are the new
    invariant pin specifically for the 2026-05-22 change.
    """

    def test_no_exclude_token_in_empty_branch_source(self):
        """Source-truth pin: the EMPTY branch in get_recovery must
        not contain RecoveryAction.EXCLUDE. Future refactors can't
        silently reintroduce the bench."""
        src = Path(inspect.getsourcefile(FailureHandler)).read_text()
        # Find the EMPTY branch — between the "if failure_type ==
        # FailureType.EMPTY:" line and the next "elif".
        i_start = src.index("if failure_type == FailureType.EMPTY:")
        # Walk forward to the next elif at the same indent level.
        i_end = src.index("\n        elif failure_type ==", i_start)
        empty_branch = src[i_start:i_end]
        assert "RecoveryAction.EXCLUDE" not in empty_branch, (
            "EMPTY policy must not produce EXCLUDE (no benching). "
            "Reintroducing EXCLUDE here would violate "
            "feedback_no_benching.md."
        )
        assert "RecoveryAction.RETRY" in empty_branch, (
            "EMPTY policy should return RETRY (model keeps participating; "
            "in-round secondary route handles the per-turn response)"
        )


# ────────────────────────────────────────────────────────────────────────────
# 5. Runner HIL accumulators exist and are clearable
# ────────────────────────────────────────────────────────────────────────────


class TestRunnerHILAccumulators:
    def test_secondary_route_usage_accumulator_exists(self):
        import bench.reference_runner_v2 as rr
        assert hasattr(rr, "_secondary_route_usage")
        assert isinstance(rr._secondary_route_usage, list)

    def test_persistent_empty_flags_accumulator_exists(self):
        import bench.reference_runner_v2 as rr
        assert hasattr(rr, "_persistent_empty_flags")
        assert isinstance(rr._persistent_empty_flags, list)

    def test_accumulators_clearable(self):
        import bench.reference_runner_v2 as rr
        rr._secondary_route_usage.append({"test": "value"})
        rr._persistent_empty_flags.append({"test": "value"})
        rr._secondary_route_usage.clear()
        rr._persistent_empty_flags.clear()
        assert rr._secondary_route_usage == []
        assert rr._persistent_empty_flags == []

    def test_report_surface_includes_accumulators(self):
        """Source-truth: the result dict assigned at end of
        run_experiment must include both accumulators so post-mortem /
        HIL review can read them."""
        src = Path(__import__("bench").reference_runner_v2.__file__).read_text()
        assert 'result["secondary_route_usage"]' in src, (
            "result must surface _secondary_route_usage for HIL review"
        )
        assert 'result["persistent_empty_flags"]' in src, (
            "result must surface _persistent_empty_flags for HIL review"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
