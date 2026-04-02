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


# ─────────────────────────────────────────────────────────────────────────────
# Layer 3: Adaptive Question Optimisation
#
# Learns which prompt characteristics produce high Ω per model, then
# generates focus directives that steer the next round toward productive
# territory.
#
# Three features (from the 1 April P-pass):
#   1. Referential density: how many distinct domain concepts the prompt connects
#   2. Novelty: how much new content vs. prior rounds (measured via vocab overlap)
#   3. Specificity: targeted vs. broad (measured via topic concentration)
#
# The compound objective Ω = A × γ_output is both the convergence signal
# (Layer 2) and the fitness function for question optimisation (Layer 3).
# Same mathematical object, two purposes.
#
# Active/passive switch: when passive, recommendations are logged but not
# injected. When active, a focus directive is prepended to the prompt.
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PromptFeatures:
    """Structural features of a prompt that may predict productive output."""
    referential_density: float   # unique domain concepts per 1K tokens
    novelty_score: float         # fraction of vocab NOT seen in prior rounds
    specificity: float           # Herfindahl index of concept frequency (0=uniform, 1=concentrated)
    token_count: int             # total content tokens (after stopword removal)
    concept_count: int           # unique domain concepts


@dataclass
class QuestionOutcome:
    """A (features, outcome) pair for one round."""
    round_idx: int
    features: PromptFeatures
    per_model_omega: dict[str, float]   # model → Ω for this round
    mean_omega: float                   # mean across models


@dataclass
class FocusDirective:
    """A steering recommendation for the next round's prompt."""
    directive_text: str          # human-readable text to inject into prompt
    reasoning: str               # why this directive was generated
    confidence: float            # 0–1, based on data quality
    predicted_omega_lift: float  # estimated improvement over baseline


def _extract_concepts(tokens: list[str], min_freq: int = 2) -> dict[str, int]:
    """Extract domain concepts from content tokens.

    A 'concept' is a token that appears at least min_freq times (not a
    one-off variable name). Returns {concept: frequency}.
    """
    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    return {t: c for t, c in freq.items() if c >= min_freq}


def extract_prompt_features(
    prompt_text: str,
    prior_vocab: Optional[set[str]] = None,
) -> PromptFeatures:
    """Extract structural features from a prompt.

    Args:
        prompt_text: The full prompt text.
        prior_vocab: Cumulative vocabulary from all prior rounds. If None,
            novelty_score is 1.0 (no prior context → everything is novel).

    Returns:
        PromptFeatures with referential density, novelty, and specificity.
    """
    tokens = tokenize(prompt_text)
    if not tokens:
        return PromptFeatures(
            referential_density=0.0, novelty_score=1.0, specificity=0.0,
            token_count=0, concept_count=0,
        )

    concepts = _extract_concepts(tokens)
    token_count = len(tokens)
    concept_count = len(concepts)

    # Referential density: concepts per 1K tokens
    referential_density = (concept_count / max(1, token_count)) * 1000

    # Novelty: fraction of unique tokens not seen in prior rounds
    unique_tokens = set(tokens)
    if prior_vocab and unique_tokens:
        new_tokens = unique_tokens - prior_vocab
        novelty_score = len(new_tokens) / len(unique_tokens)
    else:
        novelty_score = 1.0  # no prior data → everything is novel

    # Specificity: Herfindahl index on concept frequencies
    # HHI = Σ(share_i²). Uniform distribution → 1/N → low. One dominant → 1.
    if concepts:
        total_freq = sum(concepts.values())
        shares = [c / total_freq for c in concepts.values()]
        hhi = sum(s * s for s in shares)
        # Normalise: raw HHI ranges from 1/N to 1. Map to [0, 1].
        min_hhi = 1.0 / len(concepts) if len(concepts) > 0 else 0.0
        specificity = (hhi - min_hhi) / (1.0 - min_hhi) if (1.0 - min_hhi) > 1e-10 else 0.0
    else:
        specificity = 0.0

    return PromptFeatures(
        referential_density=round(referential_density, 3),
        novelty_score=round(novelty_score, 3),
        specificity=round(specificity, 3),
        token_count=token_count,
        concept_count=concept_count,
    )


class AdaptiveQuestionOptimiser:
    """Learns which prompt features predict high Ω and generates focus directives.

    Passive mode (default): logs recommendations, does not modify prompts.
    Active mode: generates a focus directive to prepend to the next prompt.

    The fitness function is Ω = A × γ_output (the compound objective).
    Features are: referential_density, novelty_score, specificity.

    After MIN_OBSERVATIONS rounds, the optimiser can identify which feature
    directions correlate with higher Ω and recommend adjustments.
    """

    # Minimum observations before making recommendations
    MIN_OBSERVATIONS = 3

    def __init__(self, active: bool = False) -> None:
        """Initialise the optimiser.

        Args:
            active: If True, generate directives for prompt injection.
                    If False (default), log recommendations only.
        """
        self.active = active
        self.history: list[QuestionOutcome] = []
        self.cumulative_vocab: set[str] = set()
        self._feature_omega_pairs: list[tuple[PromptFeatures, float]] = []

    def observe(
        self,
        round_idx: int,
        prompt_text: str,
        per_model_omega: dict[str, float],
    ) -> QuestionOutcome:
        """Record a (features, outcome) observation after a round completes.

        Call this AFTER computing Ω for all models in a round.

        Args:
            round_idx: The round that just completed.
            prompt_text: The prompt that was sent.
            per_model_omega: {model_id: Ω} for this round.

        Returns:
            The QuestionOutcome recorded.
        """
        features = extract_prompt_features(
            prompt_text,
            prior_vocab=self.cumulative_vocab if self.cumulative_vocab else None,
        )

        # Update cumulative vocab for novelty tracking in future rounds
        tokens = tokenize(prompt_text)
        self.cumulative_vocab.update(tokens)

        mean_omega = (
            sum(per_model_omega.values()) / len(per_model_omega)
            if per_model_omega else 0.0
        )

        outcome = QuestionOutcome(
            round_idx=round_idx,
            features=features,
            per_model_omega=per_model_omega,
            mean_omega=round(mean_omega, 4),
        )
        self.history.append(outcome)
        self._feature_omega_pairs.append((features, mean_omega))

        return outcome

    def _compute_feature_correlations(self) -> dict[str, float]:
        """Compute Pearson-like correlation between each feature and mean Ω.

        Returns {feature_name: correlation} where positive means the feature
        predicts higher Ω.

        Uses a simplified correlation: (mean_feature_in_top_half_Ω -
        mean_feature_in_bottom_half_Ω) / pooled_std. This avoids scipy
        dependency and is robust enough for 3-10 observations.
        """
        if len(self._feature_omega_pairs) < self.MIN_OBSERVATIONS:
            return {}

        # Sort by Ω
        sorted_pairs = sorted(self._feature_omega_pairs, key=lambda p: p[1])
        mid = len(sorted_pairs) // 2
        bottom = sorted_pairs[:mid]
        top = sorted_pairs[mid:]

        correlations: dict[str, float] = {}
        for feature_name in ("referential_density", "novelty_score", "specificity"):
            bottom_vals = [getattr(f, feature_name) for f, _ in bottom]
            top_vals = [getattr(f, feature_name) for f, _ in top]

            if not bottom_vals or not top_vals:
                correlations[feature_name] = 0.0
                continue

            mean_bottom = sum(bottom_vals) / len(bottom_vals)
            mean_top = sum(top_vals) / len(top_vals)

            # Pooled std (simplified — just range-based to avoid edge cases)
            all_vals = bottom_vals + top_vals
            val_range = max(all_vals) - min(all_vals)
            if val_range < 1e-10:
                correlations[feature_name] = 0.0
            else:
                correlations[feature_name] = round(
                    (mean_top - mean_bottom) / val_range, 3
                )

        return correlations

    def recommend(self) -> Optional[FocusDirective]:
        """Generate a focus directive based on learned feature-Ω correlations.

        Returns None if insufficient data (< MIN_OBSERVATIONS rounds).
        Returns a FocusDirective with the recommended prompt adjustment.

        The directive targets the feature with the strongest positive
        correlation to Ω, suggesting the prompt emphasise that dimension.
        """
        if len(self._feature_omega_pairs) < self.MIN_OBSERVATIONS:
            return None

        correlations = self._compute_feature_correlations()
        if not correlations:
            return None

        # Find strongest positive correlation
        best_feature = max(correlations, key=correlations.get)  # type: ignore
        best_corr = correlations[best_feature]

        if best_corr <= 0.05:
            # No feature has a meaningful positive correlation
            return FocusDirective(
                directive_text="",
                reasoning=(
                    f"No prompt feature shows strong correlation with Ω. "
                    f"Correlations: {correlations}. No adjustment recommended."
                ),
                confidence=0.0,
                predicted_omega_lift=0.0,
            )

        # Generate directive based on which feature correlates most
        confidence = min(1.0, best_corr * 2)  # scale to [0, 1]

        # Compute predicted lift: mean Ω of top-half minus mean Ω overall
        sorted_pairs = sorted(self._feature_omega_pairs, key=lambda p: p[1])
        mid = len(sorted_pairs) // 2
        top_omega = [o for _, o in sorted_pairs[mid:]]
        all_omega = [o for _, o in sorted_pairs]
        lift = (
            (sum(top_omega) / len(top_omega)) - (sum(all_omega) / len(all_omega))
            if top_omega and all_omega else 0.0
        )

        directive_map = {
            "referential_density": (
                "## Focus Directive (adaptive)\n"
                "Higher-Ω rounds in this session correlated with prompts that "
                "connected MORE existing concepts. For this round: look for "
                "cross-cutting issues that span multiple subsystems. Trace "
                "interactions between components. Findings that reference "
                "multiple code areas are more valuable than isolated ones.\n\n"
            ),
            "novelty_score": (
                "## Focus Directive (adaptive)\n"
                "Higher-Ω rounds in this session correlated with prompts that "
                "contained MORE novel content. For this round: focus on areas "
                "NOT yet examined. Avoid re-examining previously reported "
                "findings. Seek unexplored code paths, untested edge cases, "
                "and assumptions not yet challenged.\n\n"
            ),
            "specificity": (
                "## Focus Directive (adaptive)\n"
                "Higher-Ω rounds in this session correlated with MORE targeted "
                "prompts. For this round: focus deeply on ONE specific area "
                "rather than scanning broadly. Depth over breadth. Pick the "
                "most complex untested subsystem and analyse it thoroughly.\n\n"
            ),
        }

        directive_text = directive_map.get(best_feature, "")
        reasoning = (
            f"Feature '{best_feature}' has strongest correlation with Ω "
            f"(r={best_corr:.3f}). Correlations: {correlations}. "
            f"Based on {len(self._feature_omega_pairs)} observations."
        )

        return FocusDirective(
            directive_text=directive_text,
            reasoning=reasoning,
            confidence=round(confidence, 3),
            predicted_omega_lift=round(lift, 4),
        )

    def get_directive_text(self) -> str:
        """Convenience: return directive text if active and available, else empty.

        This is the method the runner calls. If passive, always returns "".
        If active but insufficient data, returns "".
        If active with sufficient data, returns the focus directive text.
        """
        if not self.active:
            return ""
        rec = self.recommend()
        if rec is None or not rec.directive_text:
            return ""
        return rec.directive_text

    def summary(self) -> dict:
        """Return a JSON-serialisable summary of the optimiser state."""
        correlations = self._compute_feature_correlations()
        rec = self.recommend()
        return {
            "observations": len(self._feature_omega_pairs),
            "active": self.active,
            "correlations": correlations,
            "recommendation": {
                "directive": rec.directive_text[:100] + "..." if rec and rec.directive_text else None,
                "reasoning": rec.reasoning if rec else None,
                "confidence": rec.confidence if rec else None,
                "predicted_lift": rec.predicted_omega_lift if rec else None,
            } if rec else None,
            "feature_history": [
                {
                    "round": o.round_idx,
                    "referential_density": o.features.referential_density,
                    "novelty_score": o.features.novelty_score,
                    "specificity": o.features.specificity,
                    "mean_omega": o.mean_omega,
                }
                for o in self.history
            ],
        }
