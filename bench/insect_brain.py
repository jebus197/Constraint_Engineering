"""Insect Brain — Reactive mechanical relay for multi-model CDSFL coordination.

The insect brain is NOT a deliberative orchestrator. It is a reactive nervous
system that gathers stimuli (model outputs), processes them through fixed
patterns (parsing, metrics, convergence), commits results to external memory
(persistence layer), and relays information between models. It does not
evaluate content quality, direct conversation, or apply FFF — that is the
models' job under CDSFL.

Design principles (from Insect_Brain_Architecture_2026-04-03.md):
1. Reactive, not deliberative: stimulus → response, no reasoning
2. Mechanical relay: parse → store → relay with pointers, no editorial changes
3. Persistence-as-memory: external storage, not in-prompt accumulation
4. Constraint box sealed: brain cannot modify CDSFL constraints or model behaviour

Core functions:
- relay()           — format and pass findings between models
- persist()         — write round data to external storage (JSON logs)
- read_context()    — retrieve windowed context for relay
- compute_metrics() — convergence signals (kappa, gamma, VCR)
- check_convergence() — threshold comparison (mechanical)
- run_immune_pipeline() — hand findings to 6-cell immune verification
- signal_complete() — emit convergence or failure signal

Integration: called by orchestrator between rounds, replaces monolithic
context assembly in run_baseline_confer.py.
"""

from __future__ import annotations

import enum
import json
import logging
import os
import re
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bench.dm._types import DynamicManagementConfig, Finding
from bench.dm._convergence import ConvergenceDetector


def _enum_safe_default(obj: Any) -> Any:
    """JSON serialization default that extracts .value from Enums.

    Without this, ``json.dumps(default=str)`` converts ``CellType.CYTOTOXIC_T``
    to the repr string ``"CellType.CYTOTOXIC_T"`` instead of the clean value
    ``"cytotoxic_t"``.  Codex 5.3 confer, 13 April 2026.
    """
    if isinstance(obj, enum.Enum):
        return obj.value
    return str(obj)

logger = logging.getLogger("insect_brain")


# ═══════════════════════════════════════════════════════════════════════════════
# Data types
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RelayPayload:
    """What the brain sends to a model for the next round.

    Contains pointers to prior findings (not full text) plus a
    budget-constrained summary. The model receives this as context
    for its next round of work.
    """
    model_label: str
    round_idx: int
    findings_text: str           # formatted findings within budget
    finding_count: int           # total findings available
    context_reset: bool          # True if budget forced summary-only mode
    convergence_summary: str     # one-line convergence status
    active_models: List[str]     # models still participating


@dataclass
class RoundRecord:
    """Immutable record of one round's results.

    Written to persistence layer by persist(). Never modified after creation.
    """
    round_idx: int
    timestamp: str
    model_responses: Dict[str, str]      # model_label → raw output text
    findings: List[Finding]              # parsed findings from all models
    finding_count: int
    immune_response: Optional[Any] = None  # ImmuneResponse if pipeline ran
    metrics: Dict[str, float] = field(default_factory=dict)
    failures: Dict[str, str] = field(default_factory=dict)
    duration_s: float = 0.0


@dataclass
class DirectedMessage:
    """A directed inter-model message extracted from response text.

    The brain extracts these mechanically by pattern-matching @tags,
    QUESTION_FOR:, DIRECTED:, and RESPONSE_TO: blocks. It does not
    evaluate the content — it routes it.
    """
    sender: str              # model_label of the sender
    recipient: str           # model_label of the intended recipient
    content: str             # the message body
    round_idx: int           # round in which the message was produced
    message_type: str        # question | challenge | response | extension


@dataclass
class BrainState:
    """Current state of the insect brain. Minimal working memory.

    The brain holds only what it needs for the current operation:
    pointers to external storage, current metrics, and active model list.
    Full history lives in the persistence layer, not here.
    """
    current_round: int = 0
    all_findings: List[List[Finding]] = field(default_factory=list)
    round_records: List[RoundRecord] = field(default_factory=list)
    active_models: List[str] = field(default_factory=list)
    directed_messages: List[DirectedMessage] = field(default_factory=list)
    converged: bool = False
    convergence_reason: str = ""
    failed: bool = False
    failure_reason: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# Insect Brain
# ═══════════════════════════════════════════════════════════════════════════════

class InsectBrain:
    """Reactive mechanical relay for multi-model CDSFL coordination.

    The brain is the nervous system connecting models, not the consciousness
    directing them. It moves information and tracks metrics. It does not
    evaluate content or direct conversation.

    Usage::

        brain = InsectBrain(
            config=dm_config,
            logs_dir=Path("bench/logs/exp29"),
            source_paths=["bench/immune_agents.py"],
        )
        brain.initialise(model_labels=["CC2", "Gemini", "DeepSeek", "Codex", "ChatGPT"])

        for round_idx in range(max_rounds):
            # Get relay payloads for each model
            payloads = brain.relay(round_idx)

            # Dispatch models (external — brain doesn't call models)
            responses = dispatch_models(payloads)

            # Feed results back to brain
            findings = parse_findings(responses)
            brain.persist(round_idx, responses, findings)

            # Run immune pipeline
            immune_result = brain.run_immune_pipeline(findings)

            # Check convergence
            if brain.check_convergence(round_idx):
                brain.signal_complete()
                break
    """

    def __init__(
        self,
        config: DynamicManagementConfig,
        logs_dir: Path,
        source_paths: List[str],
        convergence_detector: Optional[ConvergenceDetector] = None,
    ):
        self.config = config
        self.logs_dir = Path(logs_dir)
        self.source_paths = source_paths
        self.state = BrainState()

        # Convergence detector — reuse existing implementation
        self.conv_detector = convergence_detector or ConvergenceDetector(config)

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def initialise(self, model_labels: List[str]) -> None:
        """Set up the brain for a new experiment run.

        Args:
            model_labels: Labels of all participating models.
        """
        self.state = BrainState(
            active_models=list(model_labels),
        )
        logger.info(
            "Insect brain initialised: %d models, logs at %s",
            len(model_labels), self.logs_dir,
        )

    # ───────────────────────────────────────────────────────────────────────
    # Core function 1: relay()
    # ───────────────────────────────────────────────────────────────────────

    def relay(self, round_idx: int) -> Dict[str, RelayPayload]:
        """Prepare relay payloads for each active model.

        Mechanical formatting only — no editorial changes to findings.
        Each model receives other models' findings (cross-pollination),
        constrained by the per-model context budget.

        Returns dict of model_label → RelayPayload.
        """
        payloads: Dict[str, RelayPayload] = {}

        for model_label in self.state.active_models:
            findings_text, context_reset = self._format_findings_for_model(
                model_label, round_idx,
            )

            # Convergence summary (one line, mechanical)
            if round_idx > 0:
                try:
                    kappa = self.conv_detector.kappa(round_idx - 1)
                    conv_summary = f"Convergence: kappa={kappa:.3f} (threshold={self.config.tau_kappa})"
                except Exception:
                    conv_summary = "Convergence: insufficient data"
            else:
                conv_summary = "Round 0: blind round (no prior data)"

            total_findings = sum(len(rnd) for rnd in self.state.all_findings)

            payloads[model_label] = RelayPayload(
                model_label=model_label,
                round_idx=round_idx,
                findings_text=findings_text,
                finding_count=total_findings,
                context_reset=context_reset,
                convergence_summary=conv_summary,
                active_models=list(self.state.active_models),
            )

        logger.info(
            "Relay prepared for round %d: %d models, %d total findings",
            round_idx, len(payloads),
            sum(len(rnd) for rnd in self.state.all_findings),
        )
        return payloads

    def _format_findings_for_model(
        self,
        model_label: str,
        round_idx: int,
    ) -> Tuple[str, bool]:
        """Format prior findings for a specific model.

        Cross-pollination: exclude model's own findings.
        Budget-aware: switch to summary-only if over budget.

        Returns (formatted_text, context_reset_flag).
        """
        if not self.state.all_findings:
            return "", False

        # Budget for this model
        budget = self.config.context_budget_overrides.get(
            model_label, self.config.context_budget_chars,
        )

        # Cross-pollination: other models' findings only
        cross_findings: List[Finding] = []
        for rnd in self.state.all_findings:
            for f in rnd:
                if f.model_id != model_label:
                    cross_findings.append(f)

        if not cross_findings:
            return "", False

        # Try full format first
        full_text = self._format_findings_full(cross_findings)
        if len(full_text) <= budget:
            return full_text, False

        # Over budget — try last round only
        if self.state.all_findings:
            last_round = [
                f for f in self.state.all_findings[-1]
                if f.model_id != model_label
            ]
            last_text = self._format_findings_full(last_round)
            if len(last_text) <= budget:
                header = (
                    f"(CONTEXT BUDGET: showing last round only. "
                    f"{len(cross_findings)} total prior findings exist.)\n\n"
                )
                return header + last_text, False

        # Still over — summary-only mode (context reset)
        summary = self._format_findings_summary(cross_findings)
        return summary, True

    @staticmethod
    def _format_findings_full(findings: List[Finding]) -> str:
        """Format findings as full text. Mechanical — no editorial changes."""
        lines = []
        for f in findings:
            lines.append(
                f"[{f.finding_id}] model={f.model_id} round={f.round_idx} "
                f"severity={f.severity:.2f}\n"
                f"  {f.description}\n"
                f"  Fix: {f.proposed_fix}\n"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_findings_summary(findings: List[Finding]) -> str:
        """Format findings as summary only (ID + severity + one line).

        Used when full text exceeds context budget. This is a context reset.
        Findings with accepted fixes are marked CLOSED — models must not
        relitigate these. First sufficient fix wins (Occam's razor).
        """
        # CLOSED = fix exists AND programmatically verified (tools passed)
        closed = [f for f in findings if f.proposed_fix.strip() and f.verified]
        # ESCALATED = no programmatic fix possible, awaiting human decision
        escalated = [f for f in findings if f.escalated and not f.verified]
        # PENDING = fix proposed but not yet verified by tools
        pending = [f for f in findings
                   if f.proposed_fix.strip() and not f.verified and not f.escalated]
        # OPEN = no fix proposed, not escalated
        open_findings = [f for f in findings
                         if not f.proposed_fix.strip() and not f.escalated and not f.verified]

        lines = []
        lines.append(
            f"(CONTEXT RESET: {len(findings)} prior findings exist. "
            f"{len(closed)} CLOSED, {len(escalated)} ESCALATED, "
            f"{len(pending)} PENDING, {len(open_findings)} OPEN. "
            f"Do NOT relitigate CLOSED or ESCALATED bugs. "
            f"Find NEW issues only.)\n"
        )

        if closed:
            lines.append("── CLOSED (verified fix — do not relitigate) ──")
            for f in closed:
                desc_clean = f.description.replace("\n", " ")
                desc_short = desc_clean[:57] + "..." if len(desc_clean) > 60 else desc_clean
                lines.append(
                    f"  [CLOSED] {f.finding_id} (sev={f.severity:.2f}): {desc_short}"
                )
            lines.append("")

        if escalated:
            lines.append("── ESCALATED (awaiting human decision — do not attempt to fix) ──")
            for f in escalated:
                desc_clean = f.description.replace("\n", " ")
                desc_short = desc_clean[:57] + "..." if len(desc_clean) > 60 else desc_clean
                lines.append(
                    f"  [ESCALATED] {f.finding_id} (sev={f.severity:.2f}): {desc_short}"
                )
            lines.append("")

        if pending:
            lines.append("── PENDING (fix proposed, awaiting tool verification) ──")
            for f in pending:
                desc_clean = f.description.replace("\n", " ")
                desc_short = desc_clean[:67] + "..." if len(desc_clean) > 70 else desc_clean
                lines.append(
                    f"  [PENDING] {f.finding_id} (sev={f.severity:.2f}): {desc_short}"
                )
            lines.append("")

        if open_findings:
            lines.append("── OPEN (no fix yet — contributions welcome) ──")
            for f in open_findings:
                desc_clean = f.description.replace("\n", " ")
                desc_short = desc_clean[:77] + "..." if len(desc_clean) > 80 else desc_clean
                lines.append(
                    f"  {f.finding_id} (sev={f.severity:.2f}): {desc_short}"
                )

        return "\n".join(lines)

    # ───────────────────────────────────────────────────────────────────────
    # Core function 1b: relay_conversational()
    # ───────────────────────────────────────────────────────────────────────

    def relay_conversational(self, round_idx: int) -> Dict[str, RelayPayload]:
        """Prepare conversational relay payloads — full model responses.

        Like relay(), but passes raw response text from other models instead
        of parsed findings. Models see each other's full FFF reasoning chains,
        not just the extracted conclusions.

        Still mechanical: no editorial changes. Budget-constrained per model.
        Cross-pollination: each model sees other models' responses only.
        """
        payloads: Dict[str, RelayPayload] = {}

        for model_label in self.state.active_models:
            text, context_reset = self._format_responses_for_model(
                model_label, round_idx,
            )

            if round_idx > 0:
                try:
                    kappa = self.conv_detector.kappa(round_idx - 1)
                    conv_summary = f"Convergence: kappa={kappa:.3f} (threshold={self.config.tau_kappa})"
                except Exception:
                    conv_summary = "Convergence: insufficient data"
            else:
                conv_summary = "Round 0: blind round (no prior data)"

            total_findings = sum(len(rnd) for rnd in self.state.all_findings)

            payloads[model_label] = RelayPayload(
                model_label=model_label,
                round_idx=round_idx,
                findings_text=text,
                finding_count=total_findings,
                context_reset=context_reset,
                convergence_summary=conv_summary,
                active_models=list(self.state.active_models),
            )

        logger.info(
            "Conversational relay for round %d: %d models",
            round_idx, len(payloads),
        )
        return payloads

    def _format_responses_for_model(
        self,
        model_label: str,
        round_idx: int,
    ) -> Tuple[str, bool]:
        """Format other models' full responses for a specific model.

        Cross-pollination: exclude model's own responses.
        Budget-aware: degrade gracefully when over budget.
        Degradation ladder: full text → last round only → findings summary.
        """
        if not self.state.round_records:
            return "", False

        budget = self.config.context_budget_overrides.get(
            model_label, self.config.context_budget_chars,
        )

        # Collect all other models' responses, attributed
        all_sections: List[Tuple[int, str, str]] = []  # (round, label, text)
        for record in self.state.round_records:
            for resp_label, resp_text in record.model_responses.items():
                if resp_label != model_label and resp_text:
                    all_sections.append((record.round_idx, resp_label, resp_text))

        if not all_sections:
            return "", False

        # Try full responses
        full_text = self._render_response_sections(all_sections)
        if len(full_text) <= budget:
            return full_text, False

        # Over budget — last round only
        last_round_idx = self.state.round_records[-1].round_idx
        last_sections = [(r, label, txt) for r, label, txt in all_sections if r == last_round_idx]
        last_text = self._render_response_sections(last_sections)

        if len(last_text) <= budget:
            n_earlier = len(all_sections) - len(last_sections)
            header = (
                f"(CONTEXT BUDGET: showing last round responses only. "
                f"{n_earlier} earlier responses from other models exist.)\n\n"
            )
            return header + last_text, False

        # Still over — fall back to findings summary (context reset)
        cross_findings: List[Finding] = []
        for rnd in self.state.all_findings:
            for f in rnd:
                if f.model_id != model_label:
                    cross_findings.append(f)
        return self._format_findings_summary(cross_findings), True

    @staticmethod
    def _render_response_sections(
        sections: List[Tuple[int, str, str]],
    ) -> str:
        """Render attributed response sections. Mechanical formatting only."""
        parts = []
        for round_idx, label, text in sections:
            parts.append(
                f"──── {label} (Round {round_idx}) ────\n"
                f"{text}\n"
            )
        return "\n".join(parts)

    # ───────────────────────────────────────────────────────────────────────
    # Core function 1c: Directed messaging
    # ───────────────────────────────────────────────────────────────────────

    # Patterns that models can use to direct messages to specific peers.
    # The brain matches these mechanically — it does not evaluate content.
    _DIRECTED_PATTERNS = [
        # @ModelName followed by content (up to end of paragraph or next @tag)
        # Captures: (recipient, content)
        re.compile(
            r"@(\w+)\s*[:\-—]?\s*(.+?)(?=\n@\w|\n\n|\Z)",
            re.DOTALL,
        ),
        # QUESTION_FOR: ModelName\n content block
        re.compile(
            r"QUESTION_FOR:\s*(\w+)\s*\n(.+?)(?=\nQUESTION_FOR:|\nDIRECTED:|\nRESPONSE_TO:|\n\n\n|\Z)",
            re.DOTALL,
        ),
        # DIRECTED: ModelName: content block
        re.compile(
            r"DIRECTED:\s*(\w+)\s*[:\-—]\s*(.+?)(?=\nQUESTION_FOR:|\nDIRECTED:|\nRESPONSE_TO:|\n\n\n|\Z)",
            re.DOTALL,
        ),
        # RESPONSE_TO: ModelName content block
        re.compile(
            r"RESPONSE_TO:\s*(\w+)\s*[:\-—]?\s*(.+?)(?=\nQUESTION_FOR:|\nDIRECTED:|\nRESPONSE_TO:|\n\n\n|\Z)",
            re.DOTALL,
        ),
    ]

    # Maps pattern index to message_type
    _PATTERN_TYPE_MAP = {
        0: "question",    # @tag — default to question (most common use case)
        1: "question",    # QUESTION_FOR
        2: "challenge",   # DIRECTED — generic directed, default challenge
        3: "response",    # RESPONSE_TO
    }

    def extract_directed_messages(
        self,
        model_label: str,
        response_text: str,
        round_idx: int,
    ) -> List[DirectedMessage]:
        """Extract directed messages from a model's response text.

        Mechanical pattern-matching only. Matches @tags, QUESTION_FOR:,
        DIRECTED:, and RESPONSE_TO: blocks.

        Rules:
        - Self-directed messages (sender == recipient) are discarded.
        - Unknown model names (not in active_models) are discarded.
        - Duplicate recipient+content pairs within a round are deduped.

        Returns list of DirectedMessages, stored in state.directed_messages.
        """
        messages: List[DirectedMessage] = []
        seen: set[Tuple[str, str]] = set()  # (recipient, content_hash)
        active = set(self.state.active_models)

        for pat_idx, pattern in enumerate(self._DIRECTED_PATTERNS):
            for match in pattern.finditer(response_text):
                recipient_raw = match.group(1).strip()
                content = match.group(2).strip()

                # Strip leading separator punctuation that leaked into content
                content = content.lstrip(":—- \t")

                if not content:
                    continue

                # Resolve recipient — case-insensitive match against active models
                recipient = self._resolve_model_name(recipient_raw, active)
                if recipient is None:
                    continue

                # Skip self-directed messages
                if recipient == model_label:
                    continue

                # Dedup within this extraction
                content_key = (recipient, content[:200])
                if content_key in seen:
                    continue
                seen.add(content_key)

                msg_type = self._PATTERN_TYPE_MAP.get(pat_idx, "extension")
                messages.append(DirectedMessage(
                    sender=model_label,
                    recipient=recipient,
                    content=content,
                    round_idx=round_idx,
                    message_type=msg_type,
                ))

        # Store in brain state
        self.state.directed_messages.extend(messages)

        if messages:
            logger.info(
                "Extracted %d directed messages from %s (round %d): %s",
                len(messages), model_label, round_idx,
                ", ".join(f"{m.recipient}({m.message_type})" for m in messages),
            )

        return messages

    @staticmethod
    def _resolve_model_name(
        raw_name: str,
        active_models: set[str],
    ) -> Optional[str]:
        """Resolve a raw model name to an active model label.

        Case-insensitive match. Returns None if no match found.
        """
        # Exact match first
        if raw_name in active_models:
            return raw_name

        # Case-insensitive match
        lower_map = {m.lower(): m for m in active_models}
        if raw_name.lower() in lower_map:
            return lower_map[raw_name.lower()]

        return None

    def relay_directed(self, round_idx: int) -> Dict[str, RelayPayload]:
        """Prepare relay payloads with directed message priority injection.

        Like relay_conversational(), but:
        1. Directed messages TO a model appear first with ADDRESSED TO YOU header
        2. Budget priority: directed > own prior > latest round broadcast > older
        3. Models with no directed messages get standard conversational relay

        This is the recommended relay mode once models are aware of @tagging.
        """
        payloads: Dict[str, RelayPayload] = {}

        for model_label in self.state.active_models:
            text, context_reset = self._format_responses_with_directed(
                model_label, round_idx,
            )

            if round_idx > 0:
                try:
                    kappa = self.conv_detector.kappa(round_idx - 1)
                    conv_summary = f"Convergence: kappa={kappa:.3f} (threshold={self.config.tau_kappa})"
                except Exception:
                    conv_summary = "Convergence: insufficient data"
            else:
                conv_summary = "Round 0: blind round (no prior data)"

            total_findings = sum(len(rnd) for rnd in self.state.all_findings)

            payloads[model_label] = RelayPayload(
                model_label=model_label,
                round_idx=round_idx,
                findings_text=text,
                finding_count=total_findings,
                context_reset=context_reset,
                convergence_summary=conv_summary,
                active_models=list(self.state.active_models),
            )

        logger.info(
            "Directed relay for round %d: %d models",
            round_idx, len(payloads),
        )
        return payloads

    def _format_responses_with_directed(
        self,
        model_label: str,
        round_idx: int,
    ) -> Tuple[str, bool]:
        """Format context with directed message priority injection.

        Priority order (highest to lowest):
        1. Directed messages addressed to this model
        2. Broadcast: other models' responses (latest round first)
        3. Broadcast: older rounds

        Budget allocation: directed messages get first claim on budget.
        Broadcast fills the remainder.
        """
        if not self.state.round_records and not self.state.directed_messages:
            return "", False

        budget = self.config.context_budget_overrides.get(
            model_label, self.config.context_budget_chars,
        )

        # ── Priority 1: Directed messages to this model (last round only) ──
        # Only inject messages from the immediately preceding round to prevent
        # unbounded accumulation. Historical messages remain in state for
        # diagnostics via get_directed_messages_for_model().
        # E31-06 fix: use round_idx parameter (the round being built), not
        # self.state.current_round which is stale (set by previous round's
        # persist call). With the stale value, >= (current_round - 1) included
        # TWO rounds of messages instead of one.
        directed_to_me = [
            m for m in self.state.directed_messages
            if m.recipient == model_label and m.round_idx == round_idx - 1
        ]
        directed_text = ""
        if directed_to_me:
            directed_text = self._render_directed_messages(directed_to_me)
            # Truncate directed text if it alone exceeds budget
            if len(directed_text) > budget:
                directed_text = directed_text[:max(0, budget - 80)] + (
                    "\n\n[TRUNCATED: directed messages exceed context budget]"
                )

        # Reserve budget for directed messages (they get first claim)
        directed_cost = len(directed_text)
        broadcast_budget = max(0, budget - directed_cost)

        # ── Priority 2+3: Broadcast (other models' responses) ──
        broadcast_text = ""
        context_reset = False
        if self.state.round_records:
            broadcast_text, context_reset = self._format_broadcast_within_budget(
                model_label, broadcast_budget,
            )

        # Assemble final text: directed first, then broadcast
        parts = []
        if directed_text:
            parts.append(directed_text)
        if broadcast_text:
            parts.append(broadcast_text)

        return "\n\n".join(parts), context_reset

    @staticmethod
    def _render_directed_messages(messages: List[DirectedMessage]) -> str:
        """Render directed messages with ADDRESSED TO YOU header."""
        if not messages:
            return ""

        lines = [
            "╔══════════════════════════════════════════════════════════╗",
            "║  MESSAGES ADDRESSED TO YOU — respond to these directly  ║",
            "╚══════════════════════════════════════════════════════════╝",
            "",
        ]
        for msg in messages:
            type_label = msg.message_type.upper()
            lines.append(
                f"──── FROM {msg.sender} (Round {msg.round_idx}, {type_label}) ────"
            )
            lines.append(msg.content)
            lines.append("")

        return "\n".join(lines)

    def _format_broadcast_within_budget(
        self,
        model_label: str,
        budget: int,
    ) -> Tuple[str, bool]:
        """Format broadcast responses within a given budget.

        Degradation ladder: all rounds → last round → findings summary.
        """
        # Collect all other models' responses
        all_sections: List[Tuple[int, str, str]] = []
        for record in self.state.round_records:
            for resp_label, resp_text in record.model_responses.items():
                if resp_label != model_label and resp_text:
                    all_sections.append((record.round_idx, resp_label, resp_text))

        if not all_sections:
            return "", False

        # Try full responses
        full_text = self._render_response_sections(all_sections)
        if len(full_text) <= budget:
            return full_text, False

        # Over budget — last round only
        last_round_idx = self.state.round_records[-1].round_idx
        last_sections = [
            (r, label, txt) for r, label, txt in all_sections
            if r == last_round_idx
        ]
        last_text = self._render_response_sections(last_sections)

        if len(last_text) <= budget:
            n_earlier = len(all_sections) - len(last_sections)
            header = (
                f"(CONTEXT BUDGET: showing last round responses only. "
                f"{n_earlier} earlier responses from other models exist.)\n\n"
            )
            return header + last_text, False

        # Still over — fall back to findings summary (context reset)
        cross_findings: List[Finding] = []
        for rnd in self.state.all_findings:
            for f in rnd:
                if f.model_id != model_label:
                    cross_findings.append(f)
        return self._format_findings_summary(cross_findings), True

    def get_directed_messages_for_model(
        self,
        model_label: str,
        round_idx: Optional[int] = None,
    ) -> List[DirectedMessage]:
        """Get all directed messages addressed to a specific model.

        Optionally filter by round_idx.
        """
        messages = [
            m for m in self.state.directed_messages
            if m.recipient == model_label
        ]
        if round_idx is not None:
            messages = [m for m in messages if m.round_idx == round_idx]
        return messages

    def get_directed_messages_from_model(
        self,
        model_label: str,
        round_idx: Optional[int] = None,
    ) -> List[DirectedMessage]:
        """Get all directed messages sent by a specific model.

        Optionally filter by round_idx.
        """
        messages = [
            m for m in self.state.directed_messages
            if m.sender == model_label
        ]
        if round_idx is not None:
            messages = [m for m in messages if m.round_idx == round_idx]
        return messages

    # ───────────────────────────────────────────────────────────────────────
    # Core function 2: persist()
    # ───────────────────────────────────────────────────────────────────────

    def persist(
        self,
        round_idx: int,
        model_responses: Dict[str, str],
        findings: List[Finding],
        duration_s: float = 0.0,
        failures: Optional[Dict[str, str]] = None,
    ) -> RoundRecord:
        """Write round data to external storage.

        Creates an immutable RoundRecord and saves it as JSON.
        Updates internal state with new findings for relay.

        Args:
            round_idx: Current round index.
            model_responses: Raw text output from each model.
            findings: Parsed findings from all models this round.
            duration_s: Wall-clock duration of this round.
            failures: Any model failures this round.

        Returns:
            The created RoundRecord.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        record = RoundRecord(
            round_idx=round_idx,
            timestamp=timestamp,
            model_responses=dict(model_responses),
            findings=list(findings),
            finding_count=len(findings),
            duration_s=duration_s,
            failures=dict(failures or {}),
        )

        # Update internal state
        self.state.current_round = round_idx
        self.state.all_findings.append(findings)
        self.state.round_records.append(record)

        # Feed findings to convergence detector
        self.conv_detector.add_round_findings(
            round_idx, findings, duration=duration_s,
        )

        # Write to disk
        self._save_round_json(record)
        self._save_checkpoint()

        logger.info(
            "Persisted round %d: %d findings, %.1fs, %d failures",
            round_idx, len(findings), duration_s, len(record.failures),
        )

        return record

    def _atomic_write_json(self, filepath: Path, data: Any) -> None:
        """Write JSON atomically via temp file + rename (Bug#62)."""
        dir_name = str(filepath.parent)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, str(filepath))
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _save_round_json(self, record: RoundRecord) -> None:
        """Save a single round's data as JSON."""
        filepath = self.logs_dir / f"round_{record.round_idx:02d}.json"
        data = {
            "round_idx": record.round_idx,
            "timestamp": record.timestamp,
            "finding_count": record.finding_count,
            "duration_s": record.duration_s,
            "failures": record.failures,
            # Codex 5.3 confer fix (13 April 2026): provenance fields were
            # defined on Finding but never serialised to per-round JSON.
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "model_id": f.model_id,
                    "round_idx": f.round_idx,
                    "flaw_class": f.flaw_class,
                    "severity": f.severity,
                    "abstraction_index": f.abstraction_index,
                    "description": f.description,
                    "proposed_fix": f.proposed_fix,
                    "target_file": f.target_file,
                    "verified": f.verified,
                    "escalated": f.escalated,
                    "falsification_present": f.falsification_present,
                    "pm_verdict": f.pm_verdict,
                    "dedup_of": f.dedup_of,
                    "origin_type": f.origin_type,
                    "source_ref": f.source_ref,
                    "retrieval_query": f.retrieval_query,
                    "retrieved_at": f.retrieved_at,
                    "source_hash": f.source_hash,
                    "source_diversity": f.source_diversity,
                }
                for f in record.findings
            ],
            "model_responses": {
                # Bug#48: truncate long responses for JSON serialisation
                # E31-14 fix: marker in metadata, not appended to text
                # (appending made receiving models attribute it to the sender)
                label: text[:10000]
                for label, text in record.model_responses.items()
            },
            "model_responses_truncated": {
                label: len(text) > 10000
                for label, text in record.model_responses.items()
                if len(text) > 10000
            },
        }
        self._atomic_write_json(filepath, data)

    def _save_checkpoint(self) -> None:
        """Save full state checkpoint for recovery."""
        filepath = self.logs_dir / "checkpoint.json"
        serialised_findings = []
        for rnd in self.state.all_findings:
            serialised_findings.append([
                {
                    "finding_id": f.finding_id,
                    "model_id": f.model_id,
                    "round_idx": f.round_idx,
                    "flaw_class": f.flaw_class,
                    "severity": f.severity,
                    "abstraction_index": f.abstraction_index,
                    "description": f.description,
                    "proposed_fix": f.proposed_fix,
                    "target_file": f.target_file,
                    "verified": f.verified,
                    "escalated": f.escalated,
                    "falsification_present": f.falsification_present,
                    "pm_verdict": f.pm_verdict,
                    "dedup_of": f.dedup_of,
                    # Provenance fields (pre-launch review fix, 13 April 2026)
                    "origin_type": f.origin_type,
                    "source_ref": f.source_ref,
                    "retrieval_query": f.retrieval_query,
                    "retrieved_at": f.retrieved_at,
                    "source_hash": f.source_hash,
                    "source_diversity": f.source_diversity,
                }
                for f in rnd
            ])

        serialised_round_records = []
        for rr in self.state.round_records:
            rr_data: Dict[str, Any] = {
                "round_idx": rr.round_idx,
                "timestamp": rr.timestamp,
                "finding_count": rr.finding_count,
                "duration_s": rr.duration_s,
                "failures": rr.failures,
                "metrics": rr.metrics,
                # model_responses intentionally omitted — large, already in round_XX.json
            }
            # Bug#13: Serialise immune_response if present
            if rr.immune_response is not None:
                try:
                    from dataclasses import asdict
                    ir_dict = asdict(rr.immune_response)
                    # Round-trip through JSON with _enum_safe_default to get
                    # clean enum values ("cytotoxic_t") not repr strings
                    # ("CellType.CYTOTOXIC_T").  Codex 5.3 confer fix.
                    rr_data["immune_response"] = json.loads(
                        json.dumps(ir_dict, default=_enum_safe_default)
                    )
                except Exception:
                    rr_data["immune_response"] = str(rr.immune_response)
            serialised_round_records.append(rr_data)

        serialised_directed = [
            {
                "sender": dm.sender,
                "recipient": dm.recipient,
                "content": dm.content,
                "round_idx": dm.round_idx,
                "message_type": dm.message_type,
            }
            for dm in self.state.directed_messages
        ]

        checkpoint = {
            "completed_round": self.state.current_round,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "all_findings": serialised_findings,
            "round_records": serialised_round_records,
            "directed_messages": serialised_directed,
            "active_models": self.state.active_models,
            "converged": self.state.converged,
            "convergence_reason": self.state.convergence_reason,
            "failed": self.state.failed,
            "failure_reason": self.state.failure_reason,
        }
        # Pre-launch review fix: use atomic write to prevent checkpoint
        # corruption on interruption (Bug#62 pattern, already used in
        # signal_complete but was missing here).
        self._atomic_write_json(filepath, checkpoint)

    # ───────────────────────────────────────────────────────────────────────
    # Core function 3: read_context()
    # ───────────────────────────────────────────────────────────────────────

    def read_context(
        self,
        round_idx: int,
        window: int = 3,
    ) -> List[RoundRecord]:
        """Retrieve windowed context from persistence.

        Returns the last `window` rounds of records. Does not return
        full history — that lives in the persistence layer.

        Args:
            round_idx: Current round (for reference).
            window: Number of prior rounds to include.

        Returns:
            List of RoundRecords within the window.
        """
        start = max(0, len(self.state.round_records) - window)
        return self.state.round_records[start:]

    # ───────────────────────────────────────────────────────────────────────
    # Core function 4: compute_metrics()
    # ───────────────────────────────────────────────────────────────────────

    def compute_metrics(self, round_idx: int) -> Dict[str, float]:
        """Compute convergence signals. Pure arithmetic — no evaluation.

        Returns dict of metric_name → value:
        - kappa: combined convergence metric (0=diverging, 1=converged)
        - kappa_set: set-theoretic stability
        - kappa_rate: rate-based stability (Duane connection)
        - gamma_hat: Duane reliability growth parameter
        - novel_count: number of novel equivalence classes this round
        - total_findings: cumulative finding count
        - findings_this_round: count for current round
        """
        metrics: Dict[str, float] = {}

        try:
            metrics["kappa"] = self.conv_detector.kappa(round_idx)
        except Exception:
            metrics["kappa"] = 0.0

        try:
            metrics["kappa_set"] = self.conv_detector.kappa_set(round_idx)
        except Exception:
            metrics["kappa_set"] = 0.0

        try:
            metrics["kappa_rate"] = self.conv_detector.kappa_rate(round_idx)
        except Exception:
            metrics["kappa_rate"] = 0.0

        # Gamma estimate (Duane model)
        # Bug#6: Need round_idx >= 2 for meaningful growth rate (3+ data points)
        try:
            import math
            if round_idx >= 2:
                cum_classes = self.conv_detector.get_cumulative_classes(round_idx)
                cum_1 = len(self.conv_detector.get_cumulative_classes(0))
                if cum_1 > 0 and len(cum_classes) > 0:
                    gamma = 1.0 - (
                        (math.log(len(cum_classes)) - math.log(cum_1))
                        / math.log(round_idx + 1)
                    )
                    metrics["gamma_hat"] = gamma
                else:
                    metrics["gamma_hat"] = 0.0
            else:
                metrics["gamma_hat"] = 0.0
        except Exception:
            metrics["gamma_hat"] = 0.0

        # Novel count this round
        # Bug#19: Use public interface; let AttributeError propagate (code bug)
        try:
            novel = self.conv_detector._novel_classes(round_idx)
            metrics["novel_count"] = float(len(novel))
        except (ValueError, IndexError):
            metrics["novel_count"] = 0.0

        # Totals
        metrics["total_findings"] = float(
            sum(len(rnd) for rnd in self.state.all_findings)
        )
        if round_idx < len(self.state.all_findings):
            metrics["findings_this_round"] = float(
                len(self.state.all_findings[round_idx])
            )
        else:
            metrics["findings_this_round"] = 0.0

        # Update the round record with metrics if it exists
        if round_idx < len(self.state.round_records):
            self.state.round_records[round_idx].metrics = metrics

        logger.info(
            "Metrics for round %d: kappa=%.3f gamma=%.3f novel=%d total=%d",
            round_idx,
            metrics.get("kappa", 0),
            metrics.get("gamma_hat", 0),
            int(metrics.get("novel_count", 0)),
            int(metrics.get("total_findings", 0)),
        )

        return metrics

    # ───────────────────────────────────────────────────────────────────────
    # Core function 5: check_convergence()
    # ───────────────────────────────────────────────────────────────────────

    def check_convergence(self, round_idx: int) -> bool:
        """Threshold comparison — mechanical, no evaluation.

        Returns True if the convergence predicate is satisfied:
        kappa >= tau_kappa AND round >= min_rounds AND NOT veto.

        Also checks for maximum rounds reached. Convergence is evaluated
        BEFORE the budget hard-stop so that genuine convergence on the
        final round is reported correctly (not masked as BUDGET_EXHAUSTED).
        """
        # Fail-fast: if all models have failed, terminate immediately
        if self.state.failed:
            return True

        # Minimum rounds gate
        if round_idx < self.config.min_rounds_for_convergence:
            # Even below min rounds, budget can still be exhausted
            # Bug#36: Guard against max_rounds <= 0
            if self.config.max_rounds > 0 and round_idx >= self.config.max_rounds - 1:
                self.state.converged = False
                self.state.convergence_reason = f"BUDGET_EXHAUSTED({self.config.max_rounds})"
                return True
            return False

        # Convergence detector (delegates to existing implementation)
        # Evaluated BEFORE budget check so genuine convergence on the
        # final round is not falsely classified as budget exhaustion.
        try:
            converged = self.conv_detector.converged(round_idx)
            if converged:
                kappa = self.conv_detector.kappa(round_idx)
                self.state.converged = True
                self.state.convergence_reason = f"kappa_converged({kappa:.3f})"
                return True
        except Exception as e:
            logger.warning("Convergence check failed: %s", e)

        # Maximum rounds hard stop — budget exhaustion, NOT convergence.
        # Only reached if the convergence detector did NOT fire above.
        # Bug#36: Guard against max_rounds <= 0
        if self.config.max_rounds > 0 and round_idx >= self.config.max_rounds - 1:
            self.state.converged = False
            self.state.convergence_reason = f"BUDGET_EXHAUSTED({self.config.max_rounds})"
            return True

        return False

    # ───────────────────────────────────────────────────────────────────────
    # Core function 6: run_immune_pipeline()
    # ───────────────────────────────────────────────────────────────────────

    def run_immune_pipeline(
        self,
        findings: List[Finding],
        observation_only: bool = False,
    ) -> Any:
        """Hand findings to the 6-cell immune verification pipeline.

        The brain does not evaluate the results — it stores them and
        passes through whatever the pipeline produces. Prior findings
        are supplied from all_findings for NK cell deduplication.

        Args:
            findings: Findings from current round.
            observation_only: If True, pipeline logs but doesn't filter.
                Defaults to False.

        Returns:
            ImmuneResponse from the pipeline.
        """
        from bench.immune_agents import run_immune_pipeline

        # Exp 40 fix 1c (post-continuation 15 May 2026): persistent
        # per-model bias-window state. Lives on the brain so it spans
        # the whole experiment (the brain is the only object that
        # persists across rounds at this layer). Passed into the
        # Regulatory T v2 meta-check so a model's ≥85%-removal AUTOIMMUNE
        # flag only fires after the condition holds for N consecutive
        # rounds — preventing per-round HIL noise in converged-state
        # runs where one model reasonably produces mostly known
        # findings (continuation Anomaly 4).
        if not hasattr(self, "_rt_bias_window_state"):
            self._rt_bias_window_state: Dict[str, int] = {}

        # Prior findings for NK cell dedup
        prior = [f for rnd in self.state.all_findings[:-1] for f in rnd] if self.state.all_findings else []

        t0 = time.monotonic()
        # NK dedup threshold is decoupled from convergence tau_sim.
        # Convergence uses 0.33 (loose: "similar enough to cluster").
        # NK immune uses 0.50 (strict: "similar enough to REJECT").
        # Different questions, different thresholds.
        response = run_immune_pipeline(
            new_findings=findings,
            prior_findings=prior,
            source_paths=self.source_paths,
            observation_only=observation_only,
            ct_enabled=True,
            ct_timeout=600,  # Allow CT v2 full investigation time (was 300, timed out)
            domain=getattr(self.config, "domain", ""),
            rt_bias_window_state=self._rt_bias_window_state,
            rt_bias_window_rounds=3,
        )
        elapsed = time.monotonic() - t0

        logger.info(
            "Immune pipeline: %d/%d survived (%.1fs), rejection_rate=%.2f, autoimmune=%s",
            len(response.filtered_findings),
            len(findings),
            elapsed,
            response.rejection_rate,
            response.autoimmune_flag,
        )

        # ── E31-01 fix: propagate verified/escalated flags back ──────
        # The immune pipeline deep-copies findings for NK thread safety.
        # Stage 4 and 5 set verified/escalated on the copies. Without
        # this propagation, the originals in all_findings never see the
        # flags, making the bug-closed gate dead code.
        flag_map: Dict[str, Dict[str, bool]] = {}
        for f in response.filtered_findings:
            if f.verified or f.escalated:
                flag_map[f.finding_id] = {
                    "verified": f.verified,
                    "escalated": f.escalated,
                }
        if flag_map:
            propagated = 0
            for rnd_findings in self.state.all_findings:
                for f in rnd_findings:
                    flags = flag_map.get(f.finding_id)
                    if flags:
                        if flags["verified"] and not f.verified:
                            object.__setattr__(f, 'verified', True)
                            propagated += 1
                        if flags["escalated"] and not f.escalated:
                            object.__setattr__(f, 'escalated', True)
                            propagated += 1
            if propagated:
                logger.info(
                    "E31-01: propagated %d verified/escalated flags to canonical findings",
                    propagated,
                )

        # Store immune response in the round record
        if self.state.round_records:
            self.state.round_records[-1].immune_response = response

        # E31-13 fix: re-save checkpoint after immune pipeline so
        # verified/escalated flags are captured. The initial persist()
        # runs BEFORE the immune pipeline (it must — convergence detector
        # needs findings first). This second write ensures the checkpoint
        # reflects post-immune state.
        if flag_map:
            self._save_checkpoint()

        return response

    # ───────────────────────────────────────────────────────────────────────
    # Core function 7: signal_complete()
    # ───────────────────────────────────────────────────────────────────────

    def signal_complete(self) -> Dict[str, Any]:
        """Emit convergence or failure signal.

        Returns a summary dict suitable for logging and reporting.
        This is the final output of the brain for the experiment.
        """
        total_findings = sum(len(rnd) for rnd in self.state.all_findings)
        total_rounds = len(self.state.round_records)

        # Determine status — FAILED must precede BUDGET_EXHAUSTED so that
        # a fatal crash is never masked as normal budget exhaustion.
        if self.state.converged:
            status = "CONVERGED"
        elif self.state.failed:
            status = "FAILED"
        elif "BUDGET_EXHAUSTED" in self.state.convergence_reason:
            status = "BUDGET_EXHAUSTED"
        else:
            status = "INCOMPLETE"

        signal = {
            "status": status,
            "reason": self.state.convergence_reason or self.state.failure_reason,
            "total_rounds": total_rounds,
            "total_findings": total_findings,
            "active_models": list(self.state.active_models),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Compute final metrics if possible
        if total_rounds > 0:
            try:
                signal["final_kappa"] = self.conv_detector.kappa(total_rounds - 1)
            except Exception:
                signal["final_kappa"] = None

        # Per-model finding counts
        model_counts: Dict[str, int] = {}
        for rnd in self.state.all_findings:
            for f in rnd:
                model_counts[f.model_id] = model_counts.get(f.model_id, 0) + 1
        signal["per_model_findings"] = model_counts

        # Per-round finding counts
        signal["per_round_counts"] = [len(rnd) for rnd in self.state.all_findings]

        # Save completion signal (Bug#62: atomic write)
        filepath = self.logs_dir / "completion_signal.json"
        self._atomic_write_json(filepath, signal)

        logger.info(
            "Brain signal: %s — %d rounds, %d findings, reason: %s",
            signal["status"], total_rounds, total_findings, signal["reason"],
        )

        return signal

    # ───────────────────────────────────────────────────────────────────────
    # Recovery: load from checkpoint
    # ───────────────────────────────────────────────────────────────────────

    def load_checkpoint(self) -> bool:
        """Attempt to restore state from a checkpoint file.

        Returns True if checkpoint was loaded successfully.
        """
        filepath = self.logs_dir / "checkpoint.json"
        if not filepath.exists():
            return False

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load checkpoint: %s", e)
            return False

        # Restore findings
        self.state.all_findings = []
        for rnd_data in data.get("all_findings", []):
            findings = []
            for fd in rnd_data:
                findings.append(Finding(
                    finding_id=fd["finding_id"],
                    model_id=fd["model_id"],
                    round_idx=fd["round_idx"],
                    flaw_class=fd.get("flaw_class", 0),
                    severity=fd.get("severity", 0.5),
                    abstraction_index=fd.get("abstraction_index", 0.5),
                    description=fd.get("description", ""),
                    proposed_fix=fd.get("proposed_fix", ""),
                    target_file=fd.get("target_file", ""),
                    verified=fd.get("verified", False),
                    escalated=fd.get("escalated", False),
                    falsification_present=fd.get("falsification_present", False),
                    pm_verdict=fd.get("pm_verdict", ""),
                    dedup_of=fd.get("dedup_of", ""),
                    # Provenance fields (pre-launch review fix, 13 April 2026)
                    origin_type=fd.get("origin_type", ""),
                    source_ref=fd.get("source_ref", ""),
                    retrieval_query=fd.get("retrieval_query", ""),
                    retrieved_at=fd.get("retrieved_at", ""),
                    source_hash=fd.get("source_hash", ""),
                    source_diversity=fd.get("source_diversity", 0.0),
                ))
            self.state.all_findings.append(findings)

        self.state.current_round = data.get("completed_round", 0)
        self.state.active_models = data.get("active_models", [])
        self.state.converged = data.get("converged", False)
        self.state.convergence_reason = data.get("convergence_reason", "")
        self.state.failed = data.get("failed", False)
        self.state.failure_reason = data.get("failure_reason", "")

        # Restore directed messages
        self.state.directed_messages = []
        for dm_data in data.get("directed_messages", []):
            self.state.directed_messages.append(DirectedMessage(
                sender=dm_data["sender"],
                recipient=dm_data["recipient"],
                content=dm_data["content"],
                round_idx=dm_data["round_idx"],
                message_type=dm_data.get("message_type", "question"),
            ))

        # Restore round records from checkpoint
        self.state.round_records = []
        rr_by_idx = {
            r["round_idx"]: r
            for r in data.get("round_records", [])
            if isinstance(r, dict) and "round_idx" in r
        }

        # Replay findings into a fresh convergence detector with persisted durations
        self.conv_detector = ConvergenceDetector(self.config)
        for round_idx, findings in enumerate(self.state.all_findings):
            rr = rr_by_idx.get(round_idx, {})
            duration = float(rr.get("duration_s", 0.0))

            # Bug#2/#3: Restore model_responses from round_XX.json files
            model_responses: Dict[str, str] = {}
            round_file = self.logs_dir / f"round_{round_idx:02d}.json"
            if round_file.exists():
                try:
                    round_data = json.loads(round_file.read_text(encoding="utf-8"))
                    model_responses = round_data.get("model_responses", {})
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Failed to load round %d responses: %s", round_idx, e)

            # Codex 5.3 confer fix (13 April 2026): immune_response was
            # serialised to checkpoint.json but never restored into
            # RoundRecord on resume.  Pass the dict back so post-hoc
            # analysis can access immune verdicts and cell decisions.
            ir_data = rr.get("immune_response", None)

            self.state.round_records.append(RoundRecord(
                round_idx=round_idx,
                timestamp=rr.get("timestamp", ""),
                model_responses=model_responses,
                findings=findings,
                finding_count=len(findings),
                immune_response=ir_data,
                metrics=rr.get("metrics", {}),
                failures=rr.get("failures", {}),
                duration_s=duration,
            ))
            self.conv_detector.add_round_findings(round_idx, findings, duration=duration)

        logger.info(
            "Checkpoint loaded: round %d, %d total findings, %d models, %d round records",
            self.state.current_round,
            sum(len(rnd) for rnd in self.state.all_findings),
            len(self.state.active_models),
            len(self.state.round_records),
        )
        return True

    # ───────────────────────────────────────────────────────────────────────
    # Model failure handling
    # ───────────────────────────────────────────────────────────────────────

    def handle_model_failure(self, model_label: str, reason: str) -> None:
        """Record a model failure. Mechanical — no evaluation of severity.

        If all models fail, signals brain failure.
        Saves checkpoint after state change (Bug#22).
        """
        logger.warning("Model failure: %s — %s", model_label, reason)

        if model_label in self.state.active_models:
            self.state.active_models.remove(model_label)

        if not self.state.active_models:
            self.state.failed = True
            self.state.failure_reason = "all_models_failed"
            logger.error("All models failed — brain signalling failure")

        # Bug#22: Persist state change so checkpoint reflects model removal
        self._save_checkpoint()
