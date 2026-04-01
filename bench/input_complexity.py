"""Input complexity analysis via Heaps' law vocabulary growth.

Computes γ_input (input complexity), γ_output (output complexity),
amplification factor A, and the compound objective for dispatch routing.

Mathematical basis (all SymPy-verified 1 April 2026):

  Heaps' law:  V(n) = K·n^β       (vocabulary V grows sublinearly with tokens n)
  Duane:       γ = 1 − β           (convergence parameter)
  Amplification: A = β_output / β_input

  Compound objective:
      obj(β_in, β_out) = (β_out / β_in) × (1 − β_out)
      = A × steepness

  At optimal β_out:
      d(obj)/d(β_out) = (1 − 2·β_out) / β_in = 0
      β_out* = 1/2, γ_out* = 1/2

  Maximum objective:
      obj* = 1 / (4·β_in)
      d(obj*)/d(β_in) = −1 / (4·β_in²) < 0

  OCCAM EMERGES: simpler input (lower β_in) → higher compound objective.
  Not an external constraint — a mathematical consequence.

  The ideal output is half-converged (β_out = 0.5, γ_out = 0.5):
  balanced between novelty and resolution.

Dispatch routing (two-dimensional, pre-Round-1):

  | Input       | Short (< L₀)     | Long (≥ L₀)              |
  |-------------|-------------------|--------------------------|
  | Simple (γ≥γ₀) | single-turn, basic FFF | decomposed, basic FFF  |
  | Complex (γ<γ₀) | single-turn, full FFF  | multi-turn, WAIT + FFF |

After Round 0, the amplification factor A is available per model,
enabling three-dimensional routing (length × γ_input × estimated A).

Usage:
    from input_complexity import compute_gamma_input, recommend_dispatch

    result = compute_gamma_input(prompt_text)
    rec = recommend_dispatch(len(prompt_text), result.gamma, r_squared=result.r_squared)
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional, Sequence

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Window size for vocabulary growth measurement.
# Specified in approximate characters. Internally divided by 4 to estimate
# token windows (~10K chars ≈ 2.5K tokens). Gives ~12 windows for 120K prompt.
WINDOW_SIZE_CHARS = 10_000

# Minimum windows required for a meaningful fit.
MIN_WINDOWS = 3

# Stopwords — reuse the same set as dynamic_management.py for consistency.
_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "and", "but", "or",
    "nor", "not", "no", "so", "if", "then", "than", "that", "this", "these",
    "those", "it", "its", "of", "in", "on", "at", "to", "for", "with",
    "by", "from", "as", "into", "through", "during", "before", "after",
    "above", "below", "between", "out", "up", "down", "about", "each",
    "all", "any", "both", "such", "when", "where", "which", "who", "whom",
    "what", "how", "there", "here", "very", "just", "also", "only", "more",
    "most", "other", "some", "over", "under", "again", "further", "once",
})

# Code-specific stopwords (Python syntax tokens that don't carry domain meaning)
_CODE_STOPWORDS = frozenset({
    "def", "class", "return", "self", "none", "true", "false", "import",
    "from", "else", "elif", "try", "except", "raise", "finally", "with",
    "yield", "lambda", "pass", "break", "continue", "assert", "global",
    "nonlocal", "del", "while", "for", "not", "and",
})

# Dispatch thresholds
GAMMA_COMPLEXITY_THRESHOLD = 0.5  # γ_input < 0.5 = "complex"
LENGTH_THRESHOLD = 80_000         # chars; above this = "long"
R_SQUARED_QUALITY_GATE = 0.5     # below this, Heaps fit is unreliable

# Optimal β_output from SymPy (compound objective maximum)
BETA_OUTPUT_OPTIMAL = 0.5
GAMMA_OUTPUT_OPTIMAL = 0.5


# ─────────────────────────────────────────────────────────────────────────────
# Tokenisation
# ─────────────────────────────────────────────────────────────────────────────

# Regex: split on whitespace and common delimiters, keep alphanumeric tokens
_TOKEN_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')


def tokenize(text: str) -> list[str]:
    """Tokenize text for vocabulary growth analysis.

    Extracts identifier-like tokens (words, variable names, function names),
    lowercases, strips stopwords and code-syntax tokens. What remains are
    domain-specific content tokens that track structural complexity.
    """
    raw = _TOKEN_RE.findall(text.lower())
    combined_stops = _STOPWORDS | _CODE_STOPWORDS
    return [t for t in raw if t not in combined_stops and len(t) > 2]


# ─────────────────────────────────────────────────────────────────────────────
# Heaps' law β estimation
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HeapsResult:
    """Result of Heaps' law vocabulary growth analysis."""
    beta: float                    # Heaps exponent (0 = saturated, 1 = linear growth)
    gamma: float                   # Duane γ = 1 − β
    K: float                       # Heaps constant (V = K·n^β)
    r_squared: float               # Goodness of fit
    n_windows: int                 # Number of windows used
    vocab_per_window: list[int]    # Cumulative unique vocab at each window
    tokens_per_window: list[int]   # Cumulative tokens at each window


def _fit_heaps(cumulative_tokens: list[int], cumulative_vocab: list[int]) -> tuple[float, float, float]:
    """Fit Heaps' law V = K·n^β via log-log linear regression.

    Returns (beta, K, r_squared).

    Uses ordinary least squares on log(V) = log(K) + β·log(n).
    This avoids scipy dependency — numpy/scipy are available but not
    required for this simple regression.
    """
    n = len(cumulative_tokens)
    if n < 2:
        return 0.0, 0.0, 0.0

    # Filter out zero values (can't take log of 0)
    pairs = [(t, v) for t, v in zip(cumulative_tokens, cumulative_vocab) if t > 0 and v > 0]
    if len(pairs) < 2:
        return 0.0, 0.0, 0.0

    # Log-log regression: log(V) = log(K) + β·log(n)
    log_n = [math.log(t) for t, _ in pairs]
    log_v = [math.log(v) for _, v in pairs]
    m = len(log_n)

    # OLS: β = (Σ(xy) - Σx·Σy/m) / (Σ(x²) - (Σx)²/m)
    sum_x = sum(log_n)
    sum_y = sum(log_v)
    sum_xy = sum(x * y for x, y in zip(log_n, log_v))
    sum_x2 = sum(x * x for x in log_n)

    denom = sum_x2 - sum_x * sum_x / m
    if abs(denom) < 1e-15:
        return 0.0, 0.0, 0.0

    beta = (sum_xy - sum_x * sum_y / m) / denom
    log_K = (sum_y - beta * sum_x) / m
    K = math.exp(log_K)

    # R² = 1 - SS_res / SS_tot
    mean_y = sum_y / m
    ss_tot = sum((y - mean_y) ** 2 for y in log_v)
    ss_res = sum((y - (log_K + beta * x)) ** 2 for x, y in zip(log_n, log_v))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-15 else 0.0

    # Clamp β to [0, 2] — values outside this range indicate fitting problems.
    # Recompute R² with clamped β so it describes the returned parameters.
    beta = max(0.0, min(2.0, beta))
    log_K = (sum_y - beta * sum_x) / m
    K = math.exp(log_K)
    ss_res = sum((y - (log_K + beta * x)) ** 2 for x, y in zip(log_n, log_v))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-15 else 0.0

    return beta, K, r_squared


def compute_gamma_input(
    text: str,
    window_size: int = WINDOW_SIZE_CHARS,
    min_windows: int = MIN_WINDOWS,
) -> HeapsResult:
    """Compute γ_input for a body of text via windowed vocabulary growth.

    Scans the text in sequential windows, measures cumulative unique
    vocabulary at each window, fits Heaps' law V = K·n^β.

    Args:
        text: Input text to analyse.
        window_size: Approximate window size in *characters*. Internally
            divided by 4 to estimate token-level windows. Pass a smaller
            value when working with short texts (e.g. tests).
        min_windows: Minimum number of windows required for meaningful fit.

    Returns HeapsResult with β (Heaps exponent) and γ = 1 − β.

    High γ (close to 1) = simple/repetitive text (vocabulary saturates fast)
    Low γ (close to 0) = complex/novel text (vocabulary keeps growing)
    """
    tokens = tokenize(text)
    if not tokens:
        return HeapsResult(beta=0.0, gamma=1.0, K=0.0, r_squared=0.0,
                           n_windows=0, vocab_per_window=[], tokens_per_window=[])

    # Compute tokens per window based on token count, not char count.
    # Window size in tokens ≈ window_size / 4 (rough chars-to-tokens ratio)
    tokens_per_win = max(1, window_size // 4)

    cumulative_vocab: list[int] = []
    cumulative_tokens: list[int] = []
    seen: set[str] = set()
    total_tokens = 0

    for i in range(0, len(tokens), tokens_per_win):
        window = tokens[i:i + tokens_per_win]
        seen.update(window)
        total_tokens += len(window)
        cumulative_vocab.append(len(seen))
        cumulative_tokens.append(total_tokens)

    n_windows = len(cumulative_vocab)
    if n_windows < min_windows:
        # Not enough data for a meaningful fit — assume moderate complexity
        beta = 0.5
        return HeapsResult(
            beta=beta, gamma=1 - beta, K=0.0, r_squared=0.0,
            n_windows=n_windows,
            vocab_per_window=cumulative_vocab,
            tokens_per_window=cumulative_tokens,
        )

    beta, K, r_squared = _fit_heaps(cumulative_tokens, cumulative_vocab)
    gamma = 1.0 - beta

    return HeapsResult(
        beta=beta, gamma=gamma, K=K, r_squared=r_squared,
        n_windows=n_windows,
        vocab_per_window=cumulative_vocab,
        tokens_per_window=cumulative_tokens,
    )


def compute_gamma_output(finding_descriptions: Sequence[str]) -> HeapsResult:
    """Compute γ_output from a sequence of finding descriptions.

    Each description is treated as one "window" of output. Vocabulary
    growth across findings measures how much novel content each finding adds.
    """
    if not finding_descriptions:
        return HeapsResult(beta=0.0, gamma=1.0, K=0.0, r_squared=0.0,
                           n_windows=0, vocab_per_window=[], tokens_per_window=[])

    cumulative_vocab: list[int] = []
    cumulative_tokens: list[int] = []
    seen: set[str] = set()
    total_tokens = 0

    for desc in finding_descriptions:
        tokens = tokenize(desc)
        seen.update(tokens)
        total_tokens += len(tokens)
        cumulative_vocab.append(len(seen))
        cumulative_tokens.append(total_tokens)

    if len(cumulative_vocab) < MIN_WINDOWS:
        # Fewer than MIN_WINDOWS findings — not enough for meaningful fit.
        # (2-point OLS is degenerate: R²=1.0 always with 2 unknowns.)
        return HeapsResult(
            beta=0.5, gamma=0.5, K=0.0, r_squared=0.0,
            n_windows=len(cumulative_vocab),
            vocab_per_window=cumulative_vocab,
            tokens_per_window=cumulative_tokens,
        )

    beta, K, r_squared = _fit_heaps(cumulative_tokens, cumulative_vocab)
    gamma = 1.0 - beta

    return HeapsResult(
        beta=beta, gamma=gamma, K=K, r_squared=r_squared,
        n_windows=len(cumulative_vocab),
        vocab_per_window=cumulative_vocab,
        tokens_per_window=cumulative_tokens,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Amplification factor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AmplificationResult:
    """Amplification factor between input and output complexity."""
    A: float                       # β_output / β_input
    compound_objective: float      # A × (1 − β_output) = A × γ_output
    beta_input: float
    beta_output: float
    gamma_input: float
    gamma_output: float
    distance_from_optimal: float   # |β_output − 0.5| (0 = ideal)


def compute_amplification(
    input_result: HeapsResult,
    output_result: HeapsResult,
) -> AmplificationResult:
    """Compute the amplification factor A = β_output / β_input.

    Also computes the compound objective (A × steepness) and distance
    from the SymPy-derived optimal β_output = 0.5.
    """
    beta_in = max(input_result.beta, 0.01)  # avoid division by zero
    beta_out = output_result.beta

    A = beta_out / beta_in
    compound = A * (1.0 - beta_out)
    distance = abs(beta_out - BETA_OUTPUT_OPTIMAL)

    return AmplificationResult(
        A=round(A, 4),
        compound_objective=round(compound, 4),
        beta_input=round(beta_in, 4),
        beta_output=round(beta_out, 4),
        gamma_input=round(input_result.gamma, 4),
        gamma_output=round(output_result.gamma, 4),
        distance_from_optimal=round(distance, 4),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Amplification history (per-model learning)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AmplificationHistory:
    """Tracks (input, output) pairs per model for A estimation."""
    records: dict[str, list[AmplificationResult]] = field(default_factory=dict)

    def record(self, model_id: str, result: AmplificationResult) -> None:
        """Add an observation for a model."""
        if model_id not in self.records:
            self.records[model_id] = []
        self.records[model_id].append(result)

    def estimated_A(self, model_id: str) -> Optional[float]:
        """Estimate A for a model from historical observations.

        Returns the mean A across all observations, or None if no data.
        """
        if model_id not in self.records or not self.records[model_id]:
            return None
        values = [r.A for r in self.records[model_id]]
        return sum(values) / len(values)

    def estimated_compound(self, model_id: str) -> Optional[float]:
        """Estimate compound objective for a model from history."""
        if model_id not in self.records or not self.records[model_id]:
            return None
        values = [r.compound_objective for r in self.records[model_id]]
        return sum(values) / len(values)


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch recommendation
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DispatchRecommendation:
    """Recommended dispatch strategy based on input analysis."""
    strategy: str          # "single_basic", "single_full_fff", "decomposed_basic", "multiturn_fff"
    gamma_input: float
    prompt_length: int
    reasoning: str
    estimated_A: Optional[float] = None  # from history, if available


def recommend_dispatch(
    prompt_length: int,
    gamma_input: float,
    model_id: Optional[str] = None,
    history: Optional[AmplificationHistory] = None,
    gamma_threshold: float = GAMMA_COMPLEXITY_THRESHOLD,
    length_threshold: int = LENGTH_THRESHOLD,
    r_squared: Optional[float] = None,
) -> DispatchRecommendation:
    """Recommend dispatch strategy from input complexity and length.

    Two-dimensional routing (always available):
      Short + Simple → single-turn, basic FFF
      Short + Complex → single-turn, full FFF
      Long + Simple → decomposed, basic FFF per chunk
      Long + Complex → multi-turn WAIT steps, FFF synthesis

    Three-dimensional routing (after Round 0, when history available):
      Adjusts based on estimated A for the specific model. High-A models
      get more generous timeouts. Low-A models get simpler dispatch.

    Quality gate: if r_squared is provided and below R_SQUARED_QUALITY_GATE,
    γ_input is treated as unknown → assume complex (safer default).
    """
    # Quality gate: bad Heaps fit → treat complexity as unknown → assume complex
    if r_squared is not None and r_squared < R_SQUARED_QUALITY_GATE:
        gamma_input = gamma_threshold - 0.01  # force "complex" path (safer)

    is_long = prompt_length >= length_threshold
    is_complex = gamma_input < gamma_threshold

    # Base two-dimensional routing
    if is_long and is_complex:
        strategy = "multiturn_fff"
        reasoning = (f"Long ({prompt_length:,} chars) + complex (γ={gamma_input:.3f}). "
                     f"Multi-turn WAIT steps with FFF synthesis.")
    elif is_long:
        strategy = "decomposed_basic"
        reasoning = (f"Long ({prompt_length:,} chars) + simple (γ={gamma_input:.3f}). "
                     f"Decomposed into chunks, basic FFF per chunk.")
    elif is_complex:
        strategy = "single_full_fff"
        reasoning = (f"Short ({prompt_length:,} chars) + complex (γ={gamma_input:.3f}). "
                     f"Single-turn with full FFF protocol.")
    else:
        strategy = "single_basic"
        reasoning = (f"Short ({prompt_length:,} chars) + simple (γ={gamma_input:.3f}). "
                     f"Single-turn, basic FFF.")

    # Three-dimensional adjustment from history
    est_A = None
    if history and model_id:
        est_A = history.estimated_A(model_id)
        if est_A is not None:
            # High-A models amplify simple inputs → may need more capacity
            if est_A > 2.0 and strategy == "single_basic":
                strategy = "single_full_fff"
                reasoning += (f" Upgraded: model {model_id} has high amplification "
                              f"(A={est_A:.2f}), may produce complex output.")
            # Low-A models produce minimal output → don't waste multi-turn overhead
            elif est_A < 0.5 and strategy == "multiturn_fff":
                strategy = "decomposed_basic"
                reasoning += (f" Downgraded: model {model_id} has low amplification "
                              f"(A={est_A:.2f}), multi-turn overhead not justified.")

    return DispatchRecommendation(
        strategy=strategy,
        gamma_input=round(gamma_input, 4),
        prompt_length=prompt_length,
        reasoning=reasoning,
        estimated_A=round(est_A, 4) if est_A is not None else None,
    )
