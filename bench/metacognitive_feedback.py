"""Metacognitive feedback block builder for CDSFL experiment rounds.

Phase B5: presents per-round metrics to each model as an informational block.
Data only — no instructions, no authority, no guidance on what to do next.
The model sees facts and decides for itself.

Usage:
    block = build_metacognitive_block(
        round_data, registry, novelty_counts, raw_counts,
        gamma, gamma_history, gate_history, model_label,
    )
    # Inject `block` into the model's prompt for the next round.
"""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from run_exp36_evidence import FindingRegistry


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

_MIN_ROUNDS = 3          # Not enough data for meaningful metrics before round 3
_RHO_ROLLING_WINDOW = 3  # Must match runner's RHO_ROLLING_WINDOW

# Registry windowing categories (must match FindingRegistry.build_summary)
_ACTIVE_STATUSES = ("OPEN", "CONTESTED", "REOPENED")
_SETTLED_STATUSES = ("CONFIRMED", "UNCONFIRMED", "CLOSED", "MERGED")
_HIDDEN_STATUSES = ("REFUTED", "DUPLICATE")


# ─────────────────────────────────────────────────────────────────────────────
# Rho trend
# ─────────────────────────────────────────────────────────────────────────────

def _rho_trend(novelty_counts: List[int], raw_counts: List[int]) -> str:
    """Classify the rho trend over the last 3 rounds as improving/declining/stable."""
    window = _RHO_ROLLING_WINDOW
    if len(raw_counts) < window + 1:
        return "insufficient data"

    def _rho_at(idx: int) -> float:
        if raw_counts[idx] == 0:
            return 0.0
        return novelty_counts[idx] / raw_counts[idx]

    # Compare current rolling avg to the rolling avg one round earlier
    end = len(raw_counts)
    current_window = range(end - window, end)
    prior_window = range(end - window - 1, end - 1)

    current_avg = sum(_rho_at(i) for i in current_window) / window
    prior_avg = sum(_rho_at(i) for i in prior_window) / window

    delta = current_avg - prior_avg
    if delta > 0.02:
        return "improving"
    elif delta < -0.02:
        return "declining"
    return "stable"


# ─────────────────────────────────────────────────────────────────────────────
# Novelty rate
# ─────────────────────────────────────────────────────────────────────────────

def _novelty_avg_prior(novelty_counts: List[int], window: int = 3) -> float:
    """Mean novel findings over the last `window` rounds, excluding current."""
    if len(novelty_counts) < 2:
        return 0.0
    prior = novelty_counts[-(window + 1):-1]
    if not prior:
        return 0.0
    return sum(prior) / len(prior)


# ─────────────────────────────────────────────────────────────────────────────
# Registry counts
# ─────────────────────────────────────────────────────────────────────────────

def _registry_counts(registry: "FindingRegistry") -> Dict[str, int]:
    """Return total, active, settled, hidden counts from the registry."""
    total = len(registry.entries)
    active = sum(1 for e in registry.entries.values()
                 if e["status"] in _ACTIVE_STATUSES)
    settled = sum(1 for e in registry.entries.values()
                  if e["status"] in _SETTLED_STATUSES)
    hidden = sum(1 for e in registry.entries.values()
                 if e["status"] in _HIDDEN_STATUSES)
    return {"total": total, "active": active, "settled": settled, "hidden": hidden}


# ─────────────────────────────────────────────────────────────────────────────
# Convergence gate summary
# ─────────────────────────────────────────────────────────────────────────────

def _gate_summary(
    round_data: Dict[str, Any],
    gate_history: List[bool],
) -> str:
    """Summarise convergence gate status from round_data and gate_history."""
    cg = round_data.get("convergence_gate", {})
    contested = cg.get("contested", 0)
    rho_churn = cg.get("rho_churn", False)

    # Count conditions met / total (6 conditions per _evaluate_gate_conditions)
    blockers = []
    if contested > 0:
        blockers.append(f"contested={contested}")
    if rho_churn:
        blockers.append("\u03c1 churn")
    if not round_data.get("gamma_passed", True):
        blockers.append(f"\u03b3={round_data.get('gamma', 0):.3f}")

    # open_ch increasing
    open_ch = cg.get("open_crit_high", 0)
    # Novel findings over threshold (MAX_NOVEL_FINDINGS = 2 in runner)
    novel = round_data.get("novel_this_round", 0)
    if novel > 2:
        blockers.append(f"novel={novel}")

    conditions_total = 6
    conditions_met = conditions_total - len(blockers)

    # Consecutive passes
    consecutive = 0
    for passed in reversed(gate_history):
        if passed:
            consecutive += 1
        else:
            break

    parts = [f"{conditions_met}/{conditions_total} conditions met"]
    if blockers:
        parts.append(f"(blocked: {', '.join(blockers)})")
    if consecutive > 0:
        parts.append(f"{consecutive} consecutive pass(es)")

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Gamma interpretation
# ─────────────────────────────────────────────────────────────────────────────

def _gamma_band(gamma: float) -> str:
    """Return concise band label for gamma value."""
    if gamma >= 0.45:
        return "strong depletion"
    elif gamma >= 0.30:
        return "moderate depletion"
    elif gamma >= 0.20:
        return "weak depletion"
    elif gamma > 0.0:
        return "low depletion"
    return "no signal"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def build_metacognitive_block(
    round_data: Dict[str, Any],
    registry: "FindingRegistry",
    novelty_counts: List[int],
    raw_counts: List[int],
    gamma: float,
    gamma_history: List[float],
    gate_history: List[bool],
    model_label: str,
) -> str:
    """Build the per-round metrics block for injection into a model's prompt.

    Returns the formatted metrics block, or empty string if round_idx < 3
    (not enough data for meaningful rolling metrics).

    The block is INFORMATIONAL ONLY. It contains no instructions, no guidance,
    and no directives. It presents facts; the model decides what to do.

    Args:
        round_data: The round_data dict from the current round (see runner).
        registry: The FindingRegistry instance.
        novelty_counts: Per-round novel canonical finding counts.
        raw_counts: Per-round raw finding counts (before dedup).
        gamma: Current Duane gamma estimate.
        gamma_history: Full gamma history across rounds.
        gate_history: Boolean list of convergence gate pass/fail per round.
        model_label: Label for the model receiving this block (e.g. "CC2").
    """
    round_idx = round_data.get("round", 0)
    if round_idx < _MIN_ROUNDS:
        return ""

    # Discovery efficiency
    cg = round_data.get("convergence_gate", {})
    rho = cg.get("rho", 0.0)
    rho_avg = cg.get("rho_rolling_avg", 0.0)
    rho_churn = cg.get("rho_churn", False)
    trend = _rho_trend(novelty_counts, raw_counts)

    # Novelty
    novel = round_data.get("novel_this_round", 0)
    avg_prior = _novelty_avg_prior(novelty_counts)

    # Registry
    counts = _registry_counts(registry)

    # Gate
    gate_str = _gate_summary(round_data, gate_history)

    # Gamma
    band = _gamma_band(gamma)

    # Model contribution
    per_model = round_data.get("per_model", {})
    model_count = per_model.get(model_label, 0)

    lines = [
        "=== ROUND METRICS (data only \u2014 do not act on these directly) ===",
        f"Discovery efficiency: \u03c1={rho:.3f}, \u03c1\u0304\u2083={rho_avg:.3f} ({trend})",
        f"Novel findings: {novel} this round (avg last 3: {avg_prior:.1f})",
        f"Registry: {counts['total']} total "
        f"({counts['active']} active, {counts['settled']} settled, "
        f"{counts['hidden']} hidden)",
        f"Convergence: {gate_str}",
        f"\u03b3={gamma:.3f} ({band})",
        f"Your contribution: {model_count} findings this round",
    ]

    if rho_churn:
        lines.append("Churn indicator: active")

    lines.append("=== END METRICS ===")

    return "\n".join(lines)
