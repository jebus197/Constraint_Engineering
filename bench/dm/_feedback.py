"""Feedback channel — close the loop between schema judgment and model behaviour.

The schema computes a rich per-finding signal each round (B-Cell verdicts,
FFAFP admissibility, near-duplicate similarity, R_k consistency). Without a
feedback channel, that signal is logged and discarded — models never see it
and can re-submit the same refuted claim in the next round.

This module takes the schema's round-K outputs and produces a per-model
feedback section to prepend to round K+1's prompt. The feedback is
imperative, not advisory (cdsfl_operational.md §17): models MUST address
flagged findings before resubmitting, and may only refute a schema tool
output by providing their own counter-receipts.

Design notes:

* The feedback payload is capped at `top_k` items per model (default 10),
  ranked by schema disagreement magnitude (REJECTED > FFAFP-FAIL > DUPLICATE
  by similarity > R_k discrepancy). The rest are summarised in aggregate so
  the prompt does not blow up at high finding counts.
* The channel is advisory by construction when `feedback_channel_enabled =
  False` — existing prompt wiring is untouched. Switch is in
  `bench/cdsfl_registry/universal.toml`.
* Models may refute schema tool output with their own receipts. The
  directive wording is explicit: "agree with tool output OR show it wrong
  with your own tool output". There is no self-reported-confidence path.
* No schema math changes. No new convergence thresholds. Pure plumbing
  from data already on the floor.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

_LOG = logging.getLogger("cdsfl.feedback")

# ─────────────────────────────────────────────────────────────────────────────
# Finding-ID collision detector (Exp 40 timing re-confer, 2026-05-16)
# ─────────────────────────────────────────────────────────────────────────────
#
# The 2026-05-16 neutral confer converged that the UUID-namespace
# architectural change is real but unobserved, and deferred it to
# pre-Exp-41 ON CONDITION that R17-R21 is instrumented to convert the
# theoretical collision-overwrite risk into an observable. This
# detector is that instrument: it is OBSERVATION-ONLY. It does NOT
# alter the `{f.finding_id: f for f in findings}` comprehension or any
# dedup/merge behaviour — changing reconciliation behaviour pre-resume
# is precisely the risky work being deferred. It only detects and
# records when two findings in the same round share a finding_id (the
# silent-overwrite condition the panel diagnosed) so the Exp 40-54
# canonical plan's Q2/UUID deferral is evidence-gated, not blind.
#
# Module-level accumulator mirrors the established `_itc_hil_flags`
# pattern so post-mortem tooling can quantify collisions across a run.
# The runner clears it at experiment start.
_finding_id_collisions: List[Dict[str, Any]] = []


def detect_finding_id_collisions(
    findings: List[Any], round_idx: int = -1,
) -> List[Dict[str, Any]]:
    """Detect (do not repair) duplicate finding_id within one round.

    Returns a list of collision records; each record is
    ``{"round", "finding_id", "count", "model_ids"}``. A non-empty
    return means the `{f.finding_id: f for f in findings}` map would
    silently drop ``count - 1`` finding(s) for that id. model_ids
    distinguishes the cross-model case (two different models, the
    case UUID-namespace specifically targets) from the same-model
    case (one model emitting a duplicate id), which informs the
    Exp 41 UUID-namespace go/no-go.

    Observation-only: callers must NOT change behaviour based on this;
    it exists to gather the evidence the deferred UUID decision needs.
    """
    ids = [getattr(f, "finding_id", None) for f in findings]
    counts = Counter(i for i in ids if i is not None)
    collisions: List[Dict[str, Any]] = []
    for fid, n in counts.items():
        if n > 1:
            model_ids = sorted({
                getattr(f, "model_id", "?")
                for f in findings
                if getattr(f, "finding_id", None) == fid
            })
            rec = {
                "round": round_idx,
                "finding_id": fid,
                "count": n,
                "model_ids": model_ids,
                "cross_model": len(model_ids) > 1,
            }
            collisions.append(rec)
            _finding_id_collisions.append(rec)
            _LOG.warning(
                "FINDING_ID_COLLISION round=%s id=%r count=%d "
                "model_ids=%s cross_model=%s — silent-overwrite "
                "condition (UUID-namespace evidence gate, Q2 confer "
                "2026-05-16)",
                round_idx, fid, n, model_ids, len(model_ids) > 1,
            )
    return collisions


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
        if self.refutations:
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
        if self.refutations:
            score += 3.0
        score += 0.8 * len(self.admissibility_failures)
        if self.duplicates:
            score += 2.0 * max(s for _, s in self.duplicates)
        if self.rk_discrepancy is not None:
            claimed, aggregate = self.rk_discrepancy
            score += min(1.0, abs(claimed - aggregate))
        score += 0.1 * self.severity_claimed  # tie-breaker
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
    final_verdicts = immune_result.final_verdicts if immune_result else {}
    cell_verdicts = immune_result.cell_verdicts if immune_result else {}

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

    # 3. Near-duplicates
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
                if finding is None:
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

    # Group by model
    by_model: Dict[str, List[FindingFeedback]] = {}
    for rec in records:
        by_model.setdefault(rec.model_origin, []).append(rec)

    sections: Dict[str, str] = {}
    for model_id, model_recs in by_model.items():
        # Sort by priority descending
        model_recs.sort(key=lambda r: r.priority_score(), reverse=True)

        top_items = model_recs[:top_k]
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

        # Hard cap — if we're still over, drop bottom items until we fit.
        # This is belt-and-braces; the top_k cap should normally suffice.
        while len(section) > max_chars_per_model and len(top_items) > 1:
            top_items = top_items[:-1]
            # Rebuild with one fewer item
            section = _rebuild_section(
                top_items,
                model_recs,
                round_idx,
                len(model_recs) - len(top_items),
            )

        sections[model_id] = section

    return sections


def _render_single_record(rec: FindingFeedback) -> str:
    """Format one feedback record as a prompt sub-block."""
    severity = f"{rec.severity_claimed:.2f}"
    header = (
        f"{rec.finding_id} (your severity {severity}, "
        f"pipeline verdict: {rec.final_verdict}) — action: {rec.action}"
    )
    body_lines = [header]

    if rec.refutations:
        body_lines.append("  REFUTED by:")
        for tool, _verdict, evidence in rec.refutations[:3]:
            # Truncate evidence — one long tool output shouldn't dominate
            evidence_snip = (evidence[:400] + "…") if len(evidence) > 400 else evidence
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
        "The schema has flagged the items below. Address each in this round.",
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


# ─────────────────────────────────────────────────────────────────────────────
# FFAFP admissibility parser
# ─────────────────────────────────────────────────────────────────────────────
#
# Extracts PASS/FAIL status for each of the five §15 gates from a model's
# raw finding text. Returns a list of failed gate names.
#
# The parser is permissive by design (per runner_core.py:333 convention):
# a missing ADMISSIBILITY block yields all five gates as "FAIL" (model did
# not report), but absence is not treated as a crash. This mirrors how
# other CDSFL parsers handle format drift.


ADMISSIBILITY_GATES = ("S_min", "G-completeness", "d_tool", "σ_measured", "q_retest")


def parse_admissibility_block(finding_text: str) -> List[str]:
    """Extract failed gate names from a finding's ADMISSIBILITY block.

    Expected block format (from `cdsfl_operational.md` §15 and
    `reference_runner.py` prompt template)::

        ADMISSIBILITY:
          S_min: PASS (location=bench/foo.py:42, ...)
          G-completeness: PASS (verifier can reproduce ...)
          d_tool: PASS (pytest ran, ...)
          σ_measured: FAIL (no post-fix measurement available)
          q_retest: PASS (η from similarity, ...)

    Returns the list of gate names whose status is not "PASS". If the block
    is missing entirely, returns all five gates (total failure — the
    §17 feedback will tell the model to supply it).

    Parser is forgiving:
      * Case-insensitive for PASS/FAIL
      * Accepts either ':' or '-' or '=' between gate name and status
      * Accepts the σ character or the ASCII 'sigma' spelling
      * Whitespace-tolerant

    This is deliberately simple — a regex-plus-split, not a full grammar.
    The output feeds the feedback channel; format-strict rejection lives
    downstream in whatever gate we implement in Python, not here.
    """
    import re

    if not finding_text:
        return list(ADMISSIBILITY_GATES)

    # Find the ADMISSIBILITY: marker and extract the following block. The
    # block ends at the next all-caps section header (NOVELTY, VERIFIED,
    # CORROBORATION, etc.) or end of string.
    marker_match = re.search(r"ADMISSIBILITY\s*:?", finding_text, re.IGNORECASE)
    if not marker_match:
        return list(ADMISSIBILITY_GATES)

    # Extract everything after the marker until next all-caps header. We
    # use a permissive boundary — any line starting with a known section
    # name in caps terminates the block.
    tail = finding_text[marker_match.end():]
    # FINDING_ID added to the alternation 15 May 2026 per Exp 40 panel
    # consensus. Four of five models (CC2, ChatGPT, Codex, DeepSeek)
    # independently produced findings reporting this terminator gap:
    # when the next finding's marker is FINDING_ID:, the regex fails
    # to match because `_ID` appears between FINDING and `:`. Result:
    # the ADMISSIBILITY block consumes text from the subsequent
    # finding, producing the parser-runaway pattern that polluted
    # canonical finding identifiers throughout Exp 40 (e.g.
    # 'Gemini_` has `_ID` before the colon...'). Reconciliation
    # canonical: C0008.
    section_terminator = re.search(
        r"^\s*(NOVELTY|VERIFIED|CORROBORATION|FALSIFICATION|FIX|ANALYSE|"
        r"FOLLOW|FIND|FLAW_CLASS|ABSTRACTION_INDEX|SEVERITY|"
        r"FINDING_ID|FINDING)\s*:",
        tail,
        re.MULTILINE,
    )
    block = tail[: section_terminator.start()] if section_terminator else tail

    failed: List[str] = []
    for gate in ADMISSIBILITY_GATES:
        # Permissive match: gate name, optional separator, then PASS or FAIL.
        # σ_measured has a unicode char; treat both σ and 'sigma' forms.
        gate_patterns = [re.escape(gate)]
        if gate == "σ_measured":
            gate_patterns.append(r"sigma[_\s]*measured")
        elif gate == "G-completeness":
            gate_patterns.extend([r"G[_\s]*completeness", r"G completeness"])
        elif gate == "d_tool":
            gate_patterns.append(r"d[_\s]*tool")
        elif gate == "q_retest":
            gate_patterns.append(r"q[_\s]*retest")
        elif gate == "S_min":
            gate_patterns.append(r"S[_\s]*min")

        found_pass = False
        found_any = False
        for pat in gate_patterns:
            # Find "gate_name [:|-|=] PASS|FAIL"
            match = re.search(
                pat + r"\s*[:\-=]?\s*(PASS|FAIL)",
                block,
                re.IGNORECASE,
            )
            if match:
                found_any = True
                if match.group(1).upper() == "PASS":
                    found_pass = True
                break

        if not found_pass:
            failed.append(gate)
            if not found_any:
                # Gate wasn't mentioned at all. Still count as FAIL — models
                # are required by §15 to report PASS/FAIL for every gate.
                pass

    return failed
