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

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from bench.dm._types import DynamicManagementConfig, Finding
from bench.dm._convergence import ConvergenceDetector

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
        """
        header = (
            f"(CONTEXT RESET: {len(findings)} prior findings exist. "
            f"Showing ID + severity + one-line summary only. "
            f"Do NOT repeat these — find NEW issues.)\n"
        )
        lines = [header]
        for f in findings:
            # First 80 chars of description
            desc_short = f.description[:80].replace("\n", " ")
            if len(f.description) > 80:
                desc_short += "..."
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
        last_sections = [(r, l, t) for r, l, t in all_sections if r == last_round_idx]
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
            model_responses=model_responses,
            findings=findings,
            finding_count=len(findings),
            duration_s=duration_s,
            failures=failures or {},
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

    def _save_round_json(self, record: RoundRecord) -> None:
        """Save a single round's data as JSON."""
        filepath = self.logs_dir / f"round_{record.round_idx:02d}.json"
        data = {
            "round_idx": record.round_idx,
            "timestamp": record.timestamp,
            "finding_count": record.finding_count,
            "duration_s": record.duration_s,
            "failures": record.failures,
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
                    "verified": f.verified,
                }
                for f in record.findings
            ],
            "model_responses": {
                label: text[:10000]  # cap raw text to prevent bloat
                for label, text in record.model_responses.items()
            },
        }
        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")

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
                    "verified": f.verified,
                }
                for f in rnd
            ])

        checkpoint = {
            "completed_round": self.state.current_round,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "all_findings": serialised_findings,
            "active_models": self.state.active_models,
            "converged": self.state.converged,
            "convergence_reason": self.state.convergence_reason,
        }
        filepath.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

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
        try:
            cum_classes = self.conv_detector.get_cumulative_classes(round_idx)
            if round_idx > 0 and len(cum_classes) > 0:
                import math
                cum_1 = len(self.conv_detector.get_cumulative_classes(0))
                if cum_1 > 0 and round_idx > 0:
                    gamma = 1.0 - (
                        (math.log(len(cum_classes)) - math.log(cum_1))
                        / max(math.log(round_idx + 1), 0.001)
                    )
                    metrics["gamma_hat"] = gamma
                else:
                    metrics["gamma_hat"] = 0.0
            else:
                metrics["gamma_hat"] = 0.0
        except Exception:
            metrics["gamma_hat"] = 0.0

        # Novel count this round
        try:
            novel = self.conv_detector._novel_classes(round_idx)
            metrics["novel_count"] = float(len(novel))
        except Exception:
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

        Also checks for maximum rounds reached.
        """
        # Maximum rounds hard stop
        if round_idx >= self.config.max_rounds - 1:
            self.state.converged = True
            self.state.convergence_reason = f"max_rounds_reached({self.config.max_rounds})"
            return True

        # Minimum rounds gate
        if round_idx < self.config.min_rounds_for_convergence:
            return False

        # Convergence detector (delegates to existing implementation)
        try:
            converged = self.conv_detector.converged(round_idx)
            if converged:
                kappa = self.conv_detector.kappa(round_idx)
                self.state.converged = True
                self.state.convergence_reason = f"kappa_converged({kappa:.3f})"
                return True
        except Exception as e:
            logger.warning("Convergence check failed: %s", e)

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
        passes through whatever the pipeline produces.

        Args:
            findings: Findings from current round.
            observation_only: If True, pipeline logs but doesn't filter.

        Returns:
            ImmuneResponse from the pipeline.
        """
        from bench.immune_agents import run_immune_pipeline

        # Prior findings for NK cell dedup
        prior = [f for rnd in self.state.all_findings[:-1] for f in rnd] if self.state.all_findings else []

        t0 = time.monotonic()
        response = run_immune_pipeline(
            new_findings=findings,
            prior_findings=prior,
            source_paths=self.source_paths,
            observation_only=observation_only,
            ct_enabled=True,
            tau_sim=self.config.tau_sim,
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

        # Store immune response in the round record
        if self.state.round_records:
            self.state.round_records[-1].immune_response = response

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

        signal = {
            "status": "CONVERGED" if self.state.converged else (
                "FAILED" if self.state.failed else "INCOMPLETE"
            ),
            "reason": self.state.convergence_reason or self.state.failure_reason,
            "total_rounds": total_rounds,
            "total_findings": total_findings,
            "active_models": self.state.active_models,
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

        # Save completion signal
        filepath = self.logs_dir / "completion_signal.json"
        filepath.write_text(json.dumps(signal, indent=2), encoding="utf-8")

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
                    verified=fd.get("verified", False),
                ))
            self.state.all_findings.append(findings)

        self.state.current_round = data.get("completed_round", 0)
        self.state.active_models = data.get("active_models", [])
        self.state.converged = data.get("converged", False)
        self.state.convergence_reason = data.get("convergence_reason", "")

        # Replay findings into convergence detector
        for round_idx, findings in enumerate(self.state.all_findings):
            self.conv_detector.add_round_findings(round_idx, findings, duration=0.0)

        logger.info(
            "Checkpoint loaded: round %d, %d total findings, %d models",
            self.state.current_round,
            sum(len(rnd) for rnd in self.state.all_findings),
            len(self.state.active_models),
        )
        return True

    # ───────────────────────────────────────────────────────────────────────
    # Model failure handling
    # ───────────────────────────────────────────────────────────────────────

    def handle_model_failure(self, model_label: str, reason: str) -> None:
        """Record a model failure. Mechanical — no evaluation of severity.

        If all models fail, signals brain failure.
        """
        logger.warning("Model failure: %s — %s", model_label, reason)

        if model_label in self.state.active_models:
            self.state.active_models.remove(model_label)

        if not self.state.active_models:
            self.state.failed = True
            self.state.failure_reason = "all_models_failed"
            logger.error("All models failed — brain signalling failure")
