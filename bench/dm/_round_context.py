"""Round-context helpers for reference_runner_v2.

Implements three Exp 40 plan items from Part 1D (lessons-forward):

* 1D.1 — ``build_prior_fix_summary`` — enumerate confirmed/applied fixes
  from prior rounds so the current-round dispatch prompts include
  'what has already been fixed'. Prevents model re-surfacing of
  already-closed findings.

* 1D.2 — ``build_consolidation_preamble`` — emit a consolidation-mode
  preamble during the final ``consolidation_rounds`` rounds of a run.
  The preamble instructs models to prioritise closing open challenges
  over surfacing new findings.

* 1D.4 — ``build_windowed_context`` — for long runs (> ``window_full_rounds``),
  summarise older rounds' finding lists rather than repeating them
  verbatim, so the prompt stays below dispatch thresholds without
  discarding context entirely.

All three return plain strings that the dispatcher prepends to the
base prompt. They are side-effect-free and config-driven; a runner
can disable any of them by passing an empty/zero config value.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


def build_prior_fix_summary(
    registry: Any,
    round_idx: int,
    max_entries: int = 20,
    max_chars: int = 4000,
) -> str:
    """Build a plain-English summary of fixes confirmed in prior rounds.

    Args:
        registry: FindingRegistry (or any object exposing ``.entries`` as
            an iterable of dicts with ``status`` and ``proposed_fix`` keys).
        round_idx: The current round index. Entries with
            ``round_closed < round_idx`` and status in
            ``{"CONFIRMED", "RESOLVED"}`` are included.
        max_entries: Cap the number of listed fixes.
        max_chars: Cap total output size so injection never blows the
            prompt budget.

    Returns:
        A multiline string starting with ``PRIOR FIXES APPLIED (N):`` and
        listing canonical IDs with one-line descriptions. Returns empty
        string when no prior fixes exist.
    """
    if round_idx <= 0 or registry is None or not hasattr(registry, "entries"):
        return ""

    eligible: List[Dict[str, Any]] = []
    entries = registry.entries
    # FindingRegistry.entries is a dict[canonical_id, dict]; iterate values
    if isinstance(entries, dict):
        iterable = entries.items()
    else:
        iterable = [(e.get("canonical_id", ""), e) for e in entries]

    for cid, entry in iterable:
        status = entry.get("status", "")
        if status not in ("CONFIRMED", "RESOLVED"):
            continue
        round_closed = entry.get("round_closed", entry.get("round", -1))
        if round_closed >= round_idx:
            continue
        eligible.append({
            "canonical_id": cid,
            "description": str(entry.get("description", ""))[:150],
            "severity": float(entry.get("severity", 0.0)),
            "round_closed": round_closed,
        })

    if not eligible:
        return ""

    # Sort by severity desc, then round_closed desc (most recent severe first)
    eligible.sort(key=lambda e: (-e["severity"], -e["round_closed"]))
    shown = eligible[:max_entries]

    lines = [
        f"PRIOR FIXES APPLIED ({len(eligible)} confirmed across "
        f"rounds 0..{round_idx - 1}):",
        "",
    ]
    for e in shown:
        lines.append(
            f"  {e['canonical_id']} [sev={e['severity']:.2f}, "
            f"r={e['round_closed']}]: {e['description']}"
        )
    if len(eligible) > max_entries:
        lines.append(f"  ... and {len(eligible) - max_entries} more")
    lines.append("")
    lines.append(
        "Do not re-surface any of the above. If a fix above is wrong or "
        "incomplete, file a CHALLENGE verdict on its canonical ID."
    )
    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[:max_chars] + "\n  [truncated]\n"
    return out + "\n"


def build_consolidation_preamble(
    round_idx: int,
    max_rounds: int,
    consolidation_rounds: int = 3,
) -> str:
    """Build a consolidation-mode preamble for the final N rounds.

    Args:
        round_idx: Current round index (0-based).
        max_rounds: Total planned rounds for the experiment.
        consolidation_rounds: How many rounds at the end run in
            consolidation mode. Default 3 matches Exp 36 Ground Truth.

    Returns:
        A multiline preamble string if the current round is in the
        consolidation window; empty string otherwise.
    """
    if consolidation_rounds <= 0 or max_rounds <= 0:
        return ""
    first_consolidation_round = max_rounds - consolidation_rounds
    if round_idx < first_consolidation_round:
        return ""

    position = round_idx - first_consolidation_round + 1
    return (
        f"CONSOLIDATION MODE (round {position}/{consolidation_rounds} of "
        f"final phase):\n"
        f"This is one of the final rounds of the experiment. Shift "
        f"emphasis from surfacing new findings to CLOSING OPEN CHALLENGES. "
        f"Priority order:\n"
        f"  1. Issue CONFIRM/CHALLENGE verdicts on open registry entries.\n"
        f"  2. Verify applied fixes are correct (via S_k when possible).\n"
        f"  3. Close genuine duplicates with MERGE verdicts.\n"
        f"  4. Only then file new DISCOVERY findings, and only for bugs "
        f"with concrete evidence and proposed fixes.\n"
        f"The goal this phase is CONVERGENCE, not exhaustive search.\n\n"
    )


def build_windowed_context(
    per_round_summaries: Sequence[Dict[str, Any]],
    round_idx: int,
    window_full_rounds: int = 2,
    max_chars: int = 6000,
) -> str:
    """Build a windowed context block: recent rounds full, older summarised.

    Args:
        per_round_summaries: Ordered list of per-round summary dicts. Each
            dict should have keys ``round``, ``findings_count``,
            ``open_crit_high``, ``novel_this_round``, ``gamma``, ``rho``.
        round_idx: Current round index (used to compute which summaries
            are "recent" vs "older").
        window_full_rounds: How many recent rounds get their full data;
            anything older than that is compressed to a single line.
        max_chars: Overall cap for the returned context block.

    Returns:
        A multiline string prefixed with ``ROUND HISTORY:`` or empty string
        if no history is available.
    """
    if not per_round_summaries:
        return ""

    lines = ["ROUND HISTORY:"]
    sorted_summaries = sorted(
        per_round_summaries, key=lambda s: s.get("round", 0)
    )
    cutoff = round_idx - window_full_rounds

    older = [s for s in sorted_summaries if s.get("round", 0) < cutoff]
    recent = [s for s in sorted_summaries if s.get("round", 0) >= cutoff]

    if older:
        total_findings = sum(s.get("findings_count", 0) for s in older)
        total_novel = sum(s.get("novel_this_round", 0) for s in older)
        first = older[0].get("round", 0)
        last = older[-1].get("round", 0)
        lines.append(
            f"  Rounds {first}..{last} (summarised): "
            f"{total_findings} findings total, {total_novel} novel."
        )

    for s in recent:
        lines.append(
            f"  Round {s.get('round', '?')}: "
            f"{s.get('findings_count', 0)} findings "
            f"({s.get('novel_this_round', 0)} novel), "
            f"open_crit_high={s.get('open_crit_high', 0)}, "
            f"gamma={s.get('gamma', 0.0):.3f}, "
            f"rho={s.get('rho', 0.0):.3f}"
        )

    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[:max_chars] + "\n  [truncated]\n"
    return out + "\n"
