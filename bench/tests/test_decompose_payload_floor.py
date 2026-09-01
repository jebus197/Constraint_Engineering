"""Tests for Exp 40 1E.6 — payload-size dynamic decomposition.

Acceptance from the plan:
- On a synthetic 400K payload to a panel of five models, all five decompose
- On a synthetic 40K payload, none decompose

The fingerprint fixture simulates the Exp 39-0 condition where CC2, ChatGPT,
Gemini all had ``max_successful_prompt_chars = 465206``, which under the
90% safety margin meant payloads up to ~418K would *not* trigger
decomposition — the bug 1E.6 fixes.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from bench.reference_runner_v3 import (
    DECOMPOSE_HARD_FLOOR_CHARS,
    should_decompose_v2,
)


@pytest.fixture
def high_capacity_fingerprints():
    """Simulate the Exp 39-0 fingerprint state that triggered the bug."""
    fps = {
        "CC2":      {"max_successful_prompt_chars": 465206, "max_failed_prompt_chars": 0},
        "ChatGPT":  {"max_successful_prompt_chars": 465206, "max_failed_prompt_chars": 0},
        "Gemini":   {"max_successful_prompt_chars": 465206, "max_failed_prompt_chars": 0},
        "Codex":    {"max_successful_prompt_chars": 465206, "max_failed_prompt_chars": 0},
        "DeepSeek": {"max_successful_prompt_chars": 102942, "max_failed_prompt_chars": 0},
    }
    with patch("bench.run_exp17_immune._load_fingerprint_cache", return_value=fps):
        yield fps


@pytest.fixture
def mgr_with_empty_predecompose():
    """Minimal mgr stub with pre_decompose_models empty."""
    return SimpleNamespace(
        config=SimpleNamespace(pre_decompose_models=set()),
    )


class TestAcceptanceCriteria:

    def test_400k_payload_all_five_decompose(
        self, mgr_with_empty_predecompose, high_capacity_fingerprints,
    ):
        """400K payload → every model decomposes, regardless of fingerprint."""
        models = ["CC2", "ChatGPT", "Gemini", "Codex", "DeepSeek"]
        for model in models:
            assert should_decompose_v2(
                model, mgr_with_empty_predecompose, payload_chars=400_000,
            ), f"{model} should decompose at 400K (payload >> hard floor)"

    def test_40k_payload_none_decompose(
        self, mgr_with_empty_predecompose, high_capacity_fingerprints,
    ):
        """40K payload → no decomposition (below floor AND below observed limits)."""
        models = ["CC2", "ChatGPT", "Gemini", "Codex", "DeepSeek"]
        for model in models:
            assert not should_decompose_v2(
                model, mgr_with_empty_predecompose, payload_chars=40_000,
            ), f"{model} must NOT decompose at 40K"


class TestHardFloorOverridesFingerprint:
    """The regression scenario from Exp 39-0."""

    def test_369k_overrides_high_capacity_fingerprint(
        self, mgr_with_empty_predecompose, high_capacity_fingerprints,
    ):
        # 369K was the real Exp 39-0 payload that silently went monolithic.
        # With 1E.6's hard floor, this now decomposes.
        for model in ("CC2", "ChatGPT", "Gemini"):
            assert should_decompose_v2(
                model, mgr_with_empty_predecompose, payload_chars=369_000,
            ), f"{model} must decompose at 369K (the Exp 39-0 bug)"

    def test_just_above_floor(
        self, mgr_with_empty_predecompose, high_capacity_fingerprints,
    ):
        """Floor + 1 char triggers decomposition."""
        assert should_decompose_v2(
            "CC2", mgr_with_empty_predecompose,
            payload_chars=DECOMPOSE_HARD_FLOOR_CHARS + 1,
        )

    def test_at_floor_exactly(
        self, mgr_with_empty_predecompose, high_capacity_fingerprints,
    ):
        """The floor is strictly greater-than; exact-value is still below."""
        # At exactly 80K: no decomposition (matches acceptance for 40K case
        # but at the boundary, so 80001 triggers, 80000 does not).
        assert not should_decompose_v2(
            "CC2", mgr_with_empty_predecompose,
            payload_chars=DECOMPOSE_HARD_FLOOR_CHARS,
        )


class TestPreDecomposeOverrideStillWorks:

    def test_pre_decompose_forces_decompose_even_below_floor(
        self, high_capacity_fingerprints,
    ):
        """Explicit pre_decompose_models entries keep their override semantics."""
        mgr = SimpleNamespace(
            config=SimpleNamespace(pre_decompose_models={"Codex"}),
        )
        # Low payload, but Codex in pre_decompose_models → still decomposes
        assert should_decompose_v2("Codex", mgr, payload_chars=10_000)
        # Other models with low payload → no decompose
        assert not should_decompose_v2("CC2", mgr, payload_chars=10_000)


class TestNoFingerprintData:
    """Fresh models with no fingerprint data still see both layers."""

    def test_fresh_model_small_payload_no_decompose(
        self, mgr_with_empty_predecompose,
    ):
        with patch("bench.run_exp17_immune._load_fingerprint_cache", return_value={}):
            # Small payload, no fingerprint → falls through to 80K fallback
            # in _should_decompose, which says not to decompose at 40K.
            assert not should_decompose_v2(
                "NewModel", mgr_with_empty_predecompose, payload_chars=40_000,
            )

    def test_fresh_model_large_payload_decompose(
        self, mgr_with_empty_predecompose,
    ):
        with patch("bench.run_exp17_immune._load_fingerprint_cache", return_value={}):
            assert should_decompose_v2(
                "NewModel", mgr_with_empty_predecompose, payload_chars=400_000,
            )
