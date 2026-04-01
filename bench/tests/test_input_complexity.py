"""Tests for input_complexity.py — γ_input, amplification, dispatch routing."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from input_complexity import (
    tokenize,
    compute_gamma_input,
    compute_gamma_output,
    compute_amplification,
    recommend_dispatch,
    AmplificationHistory,
    HeapsResult,
    GAMMA_COMPLEXITY_THRESHOLD,
    LENGTH_THRESHOLD,
    BETA_OUTPUT_OPTIMAL,
    R_SQUARED_QUALITY_GATE,
)


# ─────────────────────────────────────────────────────────────────────────────
# Tokenisation
# ─────────────────────────────────────────────────────────────────────────────

class TestTokenize:
    def test_strips_stopwords(self):
        tokens = tokenize("the quick brown fox jumps over the lazy dog")
        assert "the" not in tokens
        assert "over" not in tokens
        assert "quick" in tokens
        assert "brown" in tokens

    def test_strips_code_stopwords(self):
        tokens = tokenize("def my_function(self, value): return value")
        assert "def" not in tokens
        assert "self" not in tokens
        assert "return" not in tokens
        assert "my_function" in tokens
        assert "value" in tokens

    def test_strips_short_tokens(self):
        tokens = tokenize("a b cd xyz hello")
        assert "a" not in tokens
        assert "cd" not in tokens  # len <= 2
        assert "xyz" in tokens
        assert "hello" in tokens

    def test_lowercases(self):
        tokens = tokenize("DynamicManager ModelSpec CapabilityFingerprint")
        assert "dynamicmanager" in tokens
        assert "modelspec" in tokens

    def test_empty_input(self):
        assert tokenize("") == []
        assert tokenize("   ") == []

    def test_code_identifiers(self):
        code = "class DynamicManager:\n    def process_round(self, responses):\n        pass"
        tokens = tokenize(code)
        assert "dynamicmanager" in tokens
        assert "process_round" in tokens
        assert "responses" in tokens


# ─────────────────────────────────────────────────────────────────────────────
# γ_input computation
# ─────────────────────────────────────────────────────────────────────────────

class TestGammaInput:
    def test_simple_repetitive_text(self):
        """Repetitive text should have high γ (vocabulary saturates fast)."""
        # Same 10 words repeated 100 times
        text = " ".join(["alpha bravo charlie delta echo foxtrot golf hotel india juliet"] * 100)
        result = compute_gamma_input(text, window_size=400)
        assert result.gamma > 0.5, f"Repetitive text γ={result.gamma:.3f}, expected > 0.5"

    def test_diverse_text(self):
        """Text with high lexical diversity should have lower γ."""
        # Generate text with many unique words
        words = [f"unique_word_{i}" for i in range(2000)]
        text = " ".join(words)
        result = compute_gamma_input(text, window_size=400)
        assert result.gamma < 0.5, f"Diverse text γ={result.gamma:.3f}, expected < 0.5"

    def test_empty_text(self):
        result = compute_gamma_input("")
        assert result.gamma == 1.0
        assert result.beta == 0.0
        assert result.n_windows == 0

    def test_short_text_defaults(self):
        """Text too short for meaningful fit should return moderate defaults."""
        result = compute_gamma_input("short text", window_size=10000)
        assert result.n_windows < 3
        assert result.beta == 0.5  # default

    def test_beta_domain(self):
        """β should be in [0, 2] (clamped)."""
        # Normal text
        text = " ".join([f"word_{i}" for i in range(5000)])
        result = compute_gamma_input(text, window_size=400)
        assert 0.0 <= result.beta <= 2.0

    def test_gamma_is_one_minus_beta(self):
        text = " ".join([f"word_{i}" for i in range(5000)])
        result = compute_gamma_input(text, window_size=400)
        assert abs(result.gamma - (1.0 - result.beta)) < 1e-10

    def test_real_code_complexity(self):
        """Real Python code should produce a meaningful γ."""
        # Simulate code with mixed identifiers
        code_lines = []
        for i in range(50):
            code_lines.append(
                f"class Module{i}:\n"
                f"    def method_{i}(self, param_{i}):\n"
                f"        result_{i} = self.compute_{i}(param_{i})\n"
                f"        return result_{i}\n"
            )
        code = "\n".join(code_lines)
        # After stopword stripping, ~350 tokens remain.  Use small window
        # so we get enough data points for a meaningful Heaps fit.
        result = compute_gamma_input(code, window_size=50)
        # Code with 50 unique classes should have moderate-to-low γ
        assert result.n_windows >= 3
        assert 0.0 < result.beta < 1.5
        assert result.r_squared > 0.5, f"Poor fit: R²={result.r_squared:.3f}"


# ─────────────────────────────────────────────────────────────────────────────
# γ_output computation
# ─────────────────────────────────────────────────────────────────────────────

class TestGammaOutput:
    def test_diverse_findings(self):
        """Findings covering different topics should have high β (low γ)."""
        findings = [
            "The z-score threshold is set too high for small model populations",
            "False positive rate computation does not window the denominator",
            "Correlated failure probability uses independent assumption incorrectly",
            "Effective window decay is additive but should be multiplicative",
            "FORMAT recovery actions are swapped between first and repeated",
        ]
        result = compute_gamma_output(findings)
        assert result.n_windows == 5

    def test_repetitive_findings(self):
        """Findings that repeat the same content should have low β (high γ)."""
        findings = [
            "The threshold value is wrong in the detection function",
            "The threshold value is incorrect in the detection method",
            "The threshold setting is wrong in the detector module",
            "The threshold parameter is incorrect in detection logic",
        ]
        result = compute_gamma_output(findings)
        assert result.gamma > 0.3  # More saturated than diverse findings

    def test_empty_findings(self):
        result = compute_gamma_output([])
        assert result.gamma == 1.0
        assert result.n_windows == 0

    def test_single_finding(self):
        result = compute_gamma_output(["Only one finding about z-scores"])
        assert result.n_windows == 1
        assert result.beta == 0.5  # default for insufficient data

    def test_two_findings_returns_default(self):
        """Two findings is degenerate for OLS (2 points, 2 unknowns = R²≡1).
        Should return moderate defaults, not a spurious perfect fit."""
        result = compute_gamma_output([
            "The z-score threshold is wrong in detection function",
            "False positive rate computation omits the window denominator",
        ])
        assert result.n_windows == 2
        assert result.beta == 0.5  # default — not enough data
        assert result.r_squared == 0.0  # no fit attempted


# ─────────────────────────────────────────────────────────────────────────────
# Amplification factor
# ─────────────────────────────────────────────────────────────────────────────

class TestAmplification:
    def test_basic_computation(self):
        input_r = HeapsResult(beta=0.3, gamma=0.7, K=10.0, r_squared=0.95,
                              n_windows=12, vocab_per_window=[], tokens_per_window=[])
        output_r = HeapsResult(beta=0.6, gamma=0.4, K=5.0, r_squared=0.90,
                               n_windows=5, vocab_per_window=[], tokens_per_window=[])
        amp = compute_amplification(input_r, output_r)
        assert abs(amp.A - 2.0) < 0.01  # 0.6 / 0.3 = 2.0
        assert abs(amp.compound_objective - 0.8) < 0.01  # 2.0 × (1 - 0.6) = 0.8

    def test_optimal_output(self):
        """When β_output = 0.5 (optimal), distance should be 0."""
        input_r = HeapsResult(beta=0.25, gamma=0.75, K=10.0, r_squared=0.95,
                              n_windows=12, vocab_per_window=[], tokens_per_window=[])
        output_r = HeapsResult(beta=0.5, gamma=0.5, K=5.0, r_squared=0.90,
                               n_windows=5, vocab_per_window=[], tokens_per_window=[])
        amp = compute_amplification(input_r, output_r)
        assert amp.distance_from_optimal == 0.0
        # At optimal: compound = (0.5/0.25) × (1 - 0.5) = 2.0 × 0.5 = 1.0
        assert abs(amp.compound_objective - 1.0) < 0.01

    def test_occam_preference(self):
        """Simpler input (lower β_in) should yield higher compound at optimal."""
        # SymPy proved: obj* = 1/(4·β_in)
        for beta_in in [0.1, 0.3, 0.5, 0.8]:
            input_r = HeapsResult(beta=beta_in, gamma=1-beta_in, K=10.0,
                                  r_squared=0.95, n_windows=12,
                                  vocab_per_window=[], tokens_per_window=[])
            output_r = HeapsResult(beta=0.5, gamma=0.5, K=5.0,
                                   r_squared=0.90, n_windows=5,
                                   vocab_per_window=[], tokens_per_window=[])
            amp = compute_amplification(input_r, output_r)
            expected = 1.0 / (4.0 * beta_in)
            assert abs(amp.compound_objective - expected) < 0.02, \
                f"β_in={beta_in}: got {amp.compound_objective}, expected {expected:.4f}"

    def test_zero_input_beta(self):
        """Zero β_input should not cause division by zero."""
        input_r = HeapsResult(beta=0.0, gamma=1.0, K=0.0, r_squared=0.0,
                              n_windows=0, vocab_per_window=[], tokens_per_window=[])
        output_r = HeapsResult(beta=0.5, gamma=0.5, K=5.0, r_squared=0.90,
                               n_windows=5, vocab_per_window=[], tokens_per_window=[])
        amp = compute_amplification(input_r, output_r)
        # β_input clamped to 0.01
        assert amp.A == round(0.5 / 0.01, 4)


# ─────────────────────────────────────────────────────────────────────────────
# Compound objective — SymPy-verified properties
# ─────────────────────────────────────────────────────────────────────────────

class TestCompoundObjective:
    def test_optimal_beta_output_is_half(self):
        """Compound objective is maximised at β_output = 0.5 (SymPy claim 3)."""
        beta_in = 0.3
        input_r = HeapsResult(beta=beta_in, gamma=1-beta_in, K=10.0,
                              r_squared=0.95, n_windows=12,
                              vocab_per_window=[], tokens_per_window=[])

        objectives = {}
        for beta_out_x10 in range(1, 10):
            beta_out = beta_out_x10 / 10.0
            output_r = HeapsResult(beta=beta_out, gamma=1-beta_out, K=5.0,
                                   r_squared=0.90, n_windows=5,
                                   vocab_per_window=[], tokens_per_window=[])
            amp = compute_amplification(input_r, output_r)
            objectives[beta_out] = amp.compound_objective

        # Maximum should be at β_out = 0.5
        max_beta = max(objectives, key=objectives.get)
        assert max_beta == 0.5, f"Maximum at β_out={max_beta}, expected 0.5"

    def test_occam_monotonicity(self):
        """At optimal β_out=0.5, objective decreases with β_input (SymPy claim 4)."""
        prev_obj = float('inf')
        for beta_in_x10 in range(1, 10):
            beta_in = beta_in_x10 / 10.0
            input_r = HeapsResult(beta=beta_in, gamma=1-beta_in, K=10.0,
                                  r_squared=0.95, n_windows=12,
                                  vocab_per_window=[], tokens_per_window=[])
            output_r = HeapsResult(beta=0.5, gamma=0.5, K=5.0,
                                   r_squared=0.90, n_windows=5,
                                   vocab_per_window=[], tokens_per_window=[])
            amp = compute_amplification(input_r, output_r)
            assert amp.compound_objective < prev_obj, \
                f"Not monotonically decreasing at β_in={beta_in}"
            prev_obj = amp.compound_objective


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch recommendation
# ─────────────────────────────────────────────────────────────────────────────

class TestDispatchRecommendation:
    def test_short_simple(self):
        rec = recommend_dispatch(50_000, gamma_input=0.7)
        assert rec.strategy == "single_basic"

    def test_short_complex(self):
        rec = recommend_dispatch(50_000, gamma_input=0.2)
        assert rec.strategy == "single_full_fff"

    def test_long_simple(self):
        rec = recommend_dispatch(120_000, gamma_input=0.7)
        assert rec.strategy == "decomposed_basic"

    def test_long_complex(self):
        rec = recommend_dispatch(120_000, gamma_input=0.2)
        assert rec.strategy == "multiturn_fff"

    def test_boundary_length(self):
        # At threshold boundary
        rec = recommend_dispatch(LENGTH_THRESHOLD, gamma_input=0.7)
        assert rec.strategy == "decomposed_basic"  # ≥ threshold = long

    def test_boundary_gamma(self):
        # At threshold boundary
        rec = recommend_dispatch(50_000, gamma_input=GAMMA_COMPLEXITY_THRESHOLD)
        assert rec.strategy == "single_basic"  # ≥ threshold = simple (not <)

    def test_high_A_upgrade(self):
        """High-A model should upgrade from basic to full FFF."""
        history = AmplificationHistory()
        amp = compute_amplification(
            HeapsResult(beta=0.3, gamma=0.7, K=10, r_squared=0.95,
                        n_windows=12, vocab_per_window=[], tokens_per_window=[]),
            HeapsResult(beta=0.8, gamma=0.2, K=5, r_squared=0.90,
                        n_windows=5, vocab_per_window=[], tokens_per_window=[]),
        )
        history.record("CC2", amp)  # A = 0.8/0.3 ≈ 2.67

        rec = recommend_dispatch(50_000, gamma_input=0.7, model_id="CC2", history=history)
        assert rec.strategy == "single_full_fff"  # upgraded from single_basic
        assert rec.estimated_A is not None
        assert rec.estimated_A > 2.0

    def test_low_A_downgrade(self):
        """Low-A model should downgrade from multiturn to decomposed."""
        history = AmplificationHistory()
        amp = compute_amplification(
            HeapsResult(beta=0.3, gamma=0.7, K=10, r_squared=0.95,
                        n_windows=12, vocab_per_window=[], tokens_per_window=[]),
            HeapsResult(beta=0.1, gamma=0.9, K=5, r_squared=0.90,
                        n_windows=5, vocab_per_window=[], tokens_per_window=[]),
        )
        history.record("ChatGPT", amp)  # A = 0.1/0.3 ≈ 0.33

        rec = recommend_dispatch(120_000, gamma_input=0.2, model_id="ChatGPT", history=history)
        assert rec.strategy == "decomposed_basic"  # downgraded from multiturn_fff

    def test_no_history_no_adjustment(self):
        """Without history, recommendation should be two-dimensional only."""
        rec = recommend_dispatch(50_000, gamma_input=0.7, model_id="CC2", history=None)
        assert rec.strategy == "single_basic"
        assert rec.estimated_A is None

    def test_low_r_squared_forces_complex(self):
        """Bad Heaps fit (low R²) should assume complex (safer default)."""
        # γ=0.7 would normally be "simple", but R²=0.1 means the fit is junk
        rec = recommend_dispatch(50_000, gamma_input=0.7, r_squared=0.1)
        assert rec.strategy == "single_full_fff"  # forced to complex path

    def test_good_r_squared_respects_gamma(self):
        """Good R² should not override the γ classification."""
        rec = recommend_dispatch(50_000, gamma_input=0.7, r_squared=0.95)
        assert rec.strategy == "single_basic"  # γ=0.7 = simple, respected

    def test_no_r_squared_no_gate(self):
        """When r_squared is not provided, quality gate is inactive."""
        rec = recommend_dispatch(50_000, gamma_input=0.7, r_squared=None)
        assert rec.strategy == "single_basic"
