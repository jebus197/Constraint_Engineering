"""Exp 40 plan-D decomposition slice — the feedback-record cluster.

A standalone extraction of the tightly-coupled feedback-record
subsystem from the plan-E cleaned `_feedback.py` baseline: the
`FindingFeedback` dataclass and the four functions that all reference
it — `build_feedback_records`, `build_feedback_sections`,
`_render_single_record`, `_rebuild_section`. AST dependency analysis
shows these five cannot be separated without stubbing the dataclass
and fabricating calling contexts; they are one natural unit (~420
lines), the third and largest review target of the hardened-gate
convergence campaign.

The leaf `detect_finding_id_collisions` is imported from the Unit B
collision-detector slice rather than duplicated — this mirrors the
real module exactly (where `build_feedback_records` calls the
module-level detector) and keeps a single source of truth.

Provenance: verbatim from bench/exp40_baseline/_feedback_cleaned.py
(lines 112-533), itself the cumulative test-gated baseline built by
bench/exp40_fix_collation.py. The repo bench/dm/_feedback.py is left
pristine; this slice is the experiment artefact only.

KNOWN SEED DEFECT (deliberately preserved, not cooked away): the
`finding_by_id = {f.finding_id: f for f in findings}` comprehension in
`build_feedback_records` is the old last-wins map. When two findings in
one round share a finding_id it silently drops all but the last and
mis-routes corrective feedback to the wrong model — a verification-
integrity / silent-evidence-loss defect (F6 critical/structural clause
4). The cleaned baseline carries this; the founder-directed collision-
safe fix landed only in live bench/dm/_feedback.py. It is retained here
as a legitimate convergence target the apply-fixes-back Ouroboros loop
can fold if the panel drives a verified fix. The focused-test gate
(test_feedback_records_slice.py) is collision-agnostic, so a correct
collision-safe fix keeps the suite green and is promotable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from bench.exp40_baseline._feedback_collision_slice import (
    detect_finding_id_collisions,
)


# ─────────────────────────────────────────────────────────────────────────────
# Data carriers
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class FindingFeedback:
    """Per-finding feedback record for one model's round K+1 prompt.

    Produced by :func:`build_feedback_records` from round K's schema outputs.
    Ranked by :meth:`priority_score` — higher = more urgent.
    """

    finding_id: str
    model_origin: str  # finding.model_id — which model produced the finding
    severity_claimed: float  # finding.severity (model's self-report)
    final_verdict: str  # immune pipeline: CONFIRMED | REJECTED | UNCERTAIN
    refutations: List[Tuple[str, str, str]] = field(default_factory=list)
    # (tool_used, verdict, evidence) — one entry per refuting specialist verdict
    admissibility_failures: List[str] = field(default_factory=list)
    # e.g. ["S_min", "G-completeness"] — gate names that failed
    duplicates: List[Tuple[str, float]] = field(default_factory=list)
    # [(prior_finding_id, cosine_similarity), ...]
    rk_discrepancy: Optional[Tuple[float, float]] = None
    # (model_claimed_R_k, aggregate_R_k) if meaningful gap

    @property
    def action(self) -> str:
        """Imperative action the model must take on this finding.

        Ordered by precedence: refutation beats admissibility beats duplicate
        beats R_k discrepancy. This mirrors the priority of the underlying
        schema checks — a refuted finding is wrong about its claim; an
        inadmissible one may be right but cannot be verified; a duplicate
        wastes compute; an R_k discrepancy is a calibration issue.
        """
        if self.refutations or self.final_verdict == "REJECTED":
            return "RECALCULATE"
        if self.admissibility_failures:
            return "ADD_ADMISSIBILITY_OR_WITHDRAW"
        if self.duplicates:
            return "DIFFERENTIATE_OR_WITHDRAW"
        if self.rk_discrepancy is not None:
            return "RECALIBRATE_RK"
        return "NONE"

    def priority_score(self) -> float:
        """Higher = more urgent for top-K selection.

        Scoring rationale:
          * REFUTED by a specialist tool: +3.0 (tool contradicts the claim)
          * Admissibility failure count: +0.8 per failed gate (max 4.0)
          * Near-duplicate (max similarity × 2.0): up to +2.0
          * R_k discrepancy (|delta|): up to +1.0

        Severity acts as a tie-breaker — a high-severity flagged finding is
        more important to correct than a low-severity one.
        """
        score = 0.0
        if self.refutations or self.final_verdict == "REJECTED":
            score += 3.0
        score += 0.8 * len(self.admissibility_failures)
        if self.duplicates:
            score += 2.0 * max(s for _, s in self.duplicates)
        if self.rk_discrepancy is not None:
            claimed, aggregate = self.rk_discrepancy
            score += min(1.0, abs(claimed - aggregate))
        severity = self.severity_claimed if self.severity_claimed is not None else 0.0
        score += 0.1 * severity  # tie-breaker
        return score


# ─────────────────────────────────────────────────────────────────────────────
# Builder
# ─────────────────────────────────────────────────────────────────────────────


def build_feedback_records(
    *,
    round_idx: int,
    findings: List,  # list of Finding (from bench.dm._types)
    immune_result,  # ImmuneResponse (from bench.immune_agents)
    rk_validation: Optional[Dict[str, List[Tuple[str, str, str, str]]]] = None,
    duplicate_pairs: Optional[List[Tuple[str, str, float]]] = None,
    admissibility_failures: Optional[Dict[str, List[str]]] = None,
) -> List[FindingFeedback]:
    """Build a list of FindingFeedback records from round-K schema outputs.

    Parameters
    ----------
    round_idx : int
        The round that just ended (K). Feedback records describe round K's
        findings for injection into round K+1's prompt.
    findings : List[Finding]
        All findings from round K, across all models.
    immune_result : ImmuneResponse
        The immune pipeline's verdict structure (cell_verdicts,
        final_verdicts, rejected_findings).
    rk_validation : Dict[model_id, List[(finding_id, status, claimed, aggregate)]]
        Output of ``validate_round_rk()`` — per-model R_k validation records.
        status ∈ {PASS, WARN, FAIL, SKIP}. Optional; absent ⇒ no R_k feedback.
    duplicate_pairs : List[(finding_id_a, finding_id_b, similarity)]
        Pairs of findings flagged as near-duplicates by the NK-Cell /
        similarity stage. Optional.
    admissibility_failures : Dict[finding_id, List[str]]
        Per-finding list of failed FFAFP gate names. Optional; absent ⇒ no
        admissibility feedback (e.g. for models that don't yet emit the
        block). Populated by :func:`parse_admissibility_block`.

    Returns
    -------
    List[FindingFeedback]
        One record per finding that has any flag raised. Findings with no
        flags are omitted (no feedback needed).
    """
    records_by_id: Dict[str, FindingFeedback] = {}
    # Exp 40 timing re-confer (2026-05-16): observation-only collision
    # detection — the next line's comprehension silently drops a
    # finding when two share a finding_id. The detector records the
    # event so the deferred UUID-namespace decision (Exp 41) is
    # evidence-gated; it deliberately does NOT change the comprehension.
    detect_finding_id_collisions(findings, round_idx)
    finding_by_id = {f.finding_id: f for f in findings}

    # 1. Specialist refutations + immune pipeline verdicts
    final_verdicts = getattr(immune_result, "final_verdicts", {}) or {}
    cell_verdicts = getattr(immune_result, "cell_verdicts", {}) or {}

    for fid, verdict_list in cell_verdicts.items():
        finding = finding_by_id.get(fid)
        if finding is None:
            continue

        refutations: List[Tuple[str, str, str]] = []
        for v in verdict_list:
            # A refutation is a REJECTED verdict backed by a tool. CONFIRMED
            # and UNCERTAIN don't generate corrective feedback — the model
            # isn't wrong, the evidence just isn't conclusive.
            if v.verdict == "REJECTED":
                refutations.append((v.tool_used, v.verdict, v.evidence))

        final_v = final_verdicts.get(fid, "UNCERTAIN")

        if refutations or final_v == "REJECTED":
            records_by_id[fid] = FindingFeedback(
                finding_id=fid,
                model_origin=finding.model_id,
                severity_claimed=finding.severity,
                final_verdict=final_v,
                refutations=refutations,
            )

    # 2. Admissibility failures
    if admissibility_failures:
        for fid, failed_gates in admissibility_failures.items():
            if not failed_gates:
                continue
            finding = finding_by_id.get(fid)
            if finding is None:
                continue
            rec = records_by_id.get(fid)
            if rec is None:
                rec = FindingFeedback(
                    finding_id=fid,
                    model_origin=finding.model_id,
                    severity_claimed=finding.severity,
                    final_verdict=final_verdicts.get(fid, "UNCERTAIN"),
                )
                records_by_id[fid] = rec
            rec.admissibility_failures = list(failed_gates)

    # 3. Near-duplicates — fid_a is the flagged (newer) finding,
    #    fid_b is the prior/canonical finding it duplicates.
    #    Only fid_a receives feedback (it must differentiate or withdraw).
    if duplicate_pairs:
        for fid_a, fid_b, sim in duplicate_pairs:
            finding = finding_by_id.get(fid_a)
            if finding is None:
                continue
            rec = records_by_id.get(fid_a)
            if rec is None:
                rec = FindingFeedback(
                    finding_id=fid_a,
                    model_origin=finding.model_id,
                    severity_claimed=finding.severity,
                    final_verdict=final_verdicts.get(fid_a, "UNCERTAIN"),
                )
                records_by_id[fid_a] = rec
            rec.duplicates.append((fid_b, sim))

    # 4. R_k discrepancies — only flag WARN or FAIL from validator
    if rk_validation:
        for model_id, validation_records in rk_validation.items():
            for fid, status, claimed_str, aggregate_str in validation_records:
                if status not in ("WARN", "FAIL"):
                    continue
                finding = finding_by_id.get(fid)
                if finding is None or finding.model_id != model_id:
                    continue
                try:
                    claimed = float(claimed_str)
                    aggregate = float(aggregate_str)
                except (ValueError, TypeError):
                    continue  # skip if numbers don't parse
                rec = records_by_id.get(fid)
                if rec is None:
                    rec = FindingFeedback(
                        finding_id=fid,
                        model_origin=finding.model_id,
                        severity_claimed=finding.severity,
                        final_verdict=final_verdicts.get(fid, "UNCERTAIN"),
                    )
                    records_by_id[fid] = rec
                # Keep the worst (largest delta) R_k discrepancy
                if rec.rk_discrepancy is None or abs(claimed - aggregate) > abs(rec.rk_discrepancy[0] - rec.rk_discrepancy[1]):
                    rec.rk_discrepancy = (claimed, aggregate)

    return list(records_by_id.values())


# ─────────────────────────────────────────────────────────────────────────────
# Per-model prompt section rendering
# ─────────────────────────────────────────────────────────────────────────────


def build_feedback_sections(
    records: List[FindingFeedback],
    *,
    round_idx: int,
    top_k: int = 10,
    max_chars_per_model: int = 8000,
) -> Dict[str, str]:
    """Render per-model feedback sections for round K+1 prompts.

    Returns a mapping ``model_id → feedback_section_text``. Only models that
    have at least one flagged finding appear in the output; callers should
    default to empty-string when a model is absent.

    Parameters
    ----------
    records : List[FindingFeedback]
        Output of :func:`build_feedback_records` for round K.
    round_idx : int
        The round that just ended (K). Used in the section header so the
        model sees "feedback on your round K output" unambiguously.
    top_k : int
        Maximum detailed items per model. Remaining items are summarised in
        an aggregate line. Default 10.
    max_chars_per_model : int
        Hard cap on section length, to prevent prompt blow-up. If exceeded
        after top_k truncation, the section is further trimmed (items
        dropped from the bottom) until within the cap.
    """
    if not records:
        return {}

    top_k = max(1, top_k)

    # Group by model
    by_model: Dict[str, List[FindingFeedback]] = {}
    for rec in records:
        by_model.setdefault(rec.model_origin, []).append(rec)

    sections: Dict[str, str] = {}
    for model_id, model_recs in by_model.items():
        # Sort by priority descending
        model_recs.sort(key=lambda r: r.priority_score(), reverse=True)

        safe_top_k = max(1, top_k)
        top_items = model_recs[:safe_top_k]
        overflow_count = len(model_recs) - len(top_items)

        lines = [
            f"=== SCHEMA FEEDBACK ON YOUR ROUND {round_idx} OUTPUT ===",
            "",
            "The schema has evaluated your prior-round findings and flagged "
            "the items below. You MUST address each flagged item in this round:",
            "",
            "  - If a specialist tool REFUTED your claim, re-run your own tools "
            "and either agree with the tool output (withdraw / correct the "
            "finding) OR provide counter-receipts showing the schema's tool "
            "was wrong. Self-reported confidence is not accepted.",
            "  - If an ADMISSIBILITY gate failed, supply the missing block "
            "(S_min, G-completeness, d_tool, σ_measured, q_retest per §15) "
            "or withdraw the finding.",
            "  - If a finding was flagged as a NEAR-DUPLICATE, either prove "
            "it is distinct from the cited prior finding or withdraw.",
            "  - If your R_k self-assessment is inconsistent with the "
            "aggregate, recompute using the operational equation (§3) or "
            "justify the discrepancy.",
            "",
            "Do NOT resubmit a flagged finding unchanged. That is inadmissible "
            "under §17 of the operational directive.",
            "",
        ]

        for rec in top_items:
            lines.append(_render_single_record(rec))
            lines.append("")

        if overflow_count > 0:
            lines.append(
                f"  (+ {overflow_count} further flagged finding"
                f"{'s' if overflow_count != 1 else ''} "
                f"not detailed here — see round log)"
            )
            lines.append("")

        lines.append("=== END SCHEMA FEEDBACK ===")
        lines.append("")
        section = "\n".join(lines)

        # Hard cap — drop items until we fit, even if that means
        # dropping all items.  If the section is still over the cap
        # after dropping everything, return a minimal placeholder.
        while len(section) > max_chars_per_model and top_items:
            top_items = top_items[:-1]
            if not top_items:
                section = (
                    f"=== SCHEMA FEEDBACK ON YOUR ROUND {round_idx} OUTPUT ===\n"
                    "\n"
                    "Feedback truncated: all items exceeded the per-model "
                    "character limit.\n"
                    "\n"
                    "=== END SCHEMA FEEDBACK ===\n"
                )
                if len(section) > max_chars_per_model:
                    section = section[:max_chars_per_model]
                break
            section = _rebuild_section(
                top_items,
                model_recs,
                round_idx,
                len(model_recs) - len(top_items),
            )

        if len(section) > max_chars_per_model:
            section = section[: max(0, max_chars_per_model)]

        sections[model_id] = section

    return sections


def _render_single_record(rec: FindingFeedback) -> str:
    """Format one feedback record as a prompt sub-block."""
    severity = f"{rec.severity_claimed:.2f}" if rec.severity_claimed is not None else "N/A"
    header = (
        f"{rec.finding_id} (your severity {severity}, "
        f"pipeline verdict: {rec.final_verdict}) — action: {rec.action}"
    )
    body_lines = [header]

    if rec.refutations:
        body_lines.append("  REFUTED by:")
        for tool, _verdict, evidence in rec.refutations[:3]:
            # Truncate evidence — one long tool output shouldn't dominate
            evidence_str = str(evidence) if evidence is not None else "No evidence provided"
            evidence_snip = (evidence_str[:400] + "…") if len(evidence_str) > 400 else evidence_str
            evidence_snip = evidence_snip.replace("\n", "\n      ")
            body_lines.append(f"    {tool}: {evidence_snip}")
        if len(rec.refutations) > 3:
            body_lines.append(
                f"    (+ {len(rec.refutations) - 3} additional refutation"
                f"{'s' if len(rec.refutations) - 3 != 1 else ''})"
            )

    if rec.admissibility_failures:
        body_lines.append(
            "  ADMISSIBILITY FAIL: "
            + ", ".join(rec.admissibility_failures)
            + " (see §15)"
        )

    if rec.duplicates:
        # Show strongest match only to keep it short
        top_dup = max(rec.duplicates, key=lambda t: t[1])
        body_lines.append(
            f"  NEAR-DUPLICATE: cosine {top_dup[1]:.2f} to {top_dup[0]}"
        )
        if len(rec.duplicates) > 1:
            body_lines.append(
                f"    (+ {len(rec.duplicates) - 1} other similar prior finding"
                f"{'s' if len(rec.duplicates) - 1 != 1 else ''})"
            )

    if rec.rk_discrepancy is not None:
        claimed, aggregate = rec.rk_discrepancy
        body_lines.append(
            f"  R_k INCONSISTENT: you reported {claimed:.2f}; "
            f"aggregate = {aggregate:.2f} (Δ = {abs(claimed - aggregate):.2f})"
        )

    return "\n".join(body_lines)


def _rebuild_section(
    top_items: List[FindingFeedback],
    all_recs: List[FindingFeedback],
    round_idx: int,
    overflow_count: int,
) -> str:
    """Helper for the max-chars fallback path."""
    lines = [
        f"=== SCHEMA FEEDBACK ON YOUR ROUND {round_idx} OUTPUT ===",
        "",
        "The schema has evaluated your prior-round findings and flagged "
        "the items below. You MUST address each flagged item in this round:",
        "",
        "  - If a specialist tool REFUTED your claim, re-run your own tools "
        "and either agree with the tool output (withdraw / correct the "
        "finding) OR provide counter-receipts showing the schema's tool "
        "was wrong. Self-reported confidence is not accepted.",
        "  - If an ADMISSIBILITY gate failed, supply the missing block "
        "(S_min, G-completeness, d_tool, σ_measured, q_retest per §15) "
        "or withdraw the finding.",
        "  - If a finding was flagged as a NEAR-DUPLICATE, either prove "
        "it is distinct from the cited prior finding or withdraw.",
        "  - If your R_k self-assessment is inconsistent with the "
        "aggregate, recompute using the operational equation (§3) or "
        "justify the discrepancy.",
        "",
        "Do NOT resubmit a flagged finding unchanged. That is inadmissible "
        "under §17 of the operational directive.",
        "",
    ]
    for rec in top_items:
        lines.append(_render_single_record(rec))
        lines.append("")
    if overflow_count > 0:
        lines.append(
            f"  (+ {overflow_count} further flagged finding"
            f"{'s' if overflow_count != 1 else ''} — truncated for prompt size)"
        )
        lines.append("")
    lines.append("=== END SCHEMA FEEDBACK ===")
    lines.append("")
    return "\n".join(lines)
