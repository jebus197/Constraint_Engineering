"""_manager.py — DynamicManager orchestrator.

Extracted from bench/dynamic_management.py (lines ~5275–6768).
Top-level orchestrator connecting all six areas of CDSFL dynamic management.
"""

from __future__ import annotations

import logging
import time
from collections import Counter, defaultdict
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
)

from bench.dm._types import (
    DynamicManagementConfig,
    Role,
    CapabilityFingerprint,
    ModelSpec,
    Task,
    Finding,
    FailureType,
    RecoveryAction,
    FailureRecord,
    ModelResponse,
    DetectorDiagnosis,
    RoundResult,
    State,
    Event,
    ManagerEventType,
    ManagerEvent,
)
from bench.dm._role_assignment import RoleAssignment
from bench.dm._load_balancer import LoadBalancer, Allocation
from bench.dm._fsm import RoundProgressionFSM
from bench.dm._convergence import ConvergenceDetector
from bench.dm._diminishing_returns import DiminishingReturnsDetector
from bench.dm._immune import DetectorHealthMonitor
from bench.dm._failure_handler import FailureHandler, CorrelatedFailureModel
from bench.dm._events import ManagerEventStream


# ---------------------------------------------------------------------------
# Similarity helpers (used by DynamicManager.update_fingerprints)
# ---------------------------------------------------------------------------

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


def _tokenize_for_similarity(text: str) -> list[str]:
    """Tokenize text for similarity comparison: lowercase, strip stopwords."""
    words = text.lower().split()
    return [w for w in words if w not in _STOPWORDS and len(w) > 2]


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    """Generate bigram set from token list."""
    return {(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)}


def _finding_similarity(f1: Finding, f2: Finding) -> float:
    """Compute similarity between two findings.

    Uses flaw-class match + combined unigram/bigram Jaccard on description
    words (stopwords removed). Bigrams capture phrase-level semantic overlap
    that raw word sets miss — "race condition" and "condition race" are
    different bigrams, but "race condition" and "race condition" match.

    The combined score weights unigrams 0.6 and bigrams 0.4. This provides
    a middle ground between the original raw Jaccard (too strict for
    semantic duplicates) and embedding-based similarity (too complex for
    the current infrastructure).

    When flaw classes differ, the combined Jaccard alone determines the score
    (no class bonus). This prevents models that assign different integer
    labels to the same concept from appearing maximally novel.

    Self-healing note: if this function fails to detect convergence (kappa
    stuck at 0.0 for consecutive rounds), the DetectorHealthMonitor will
    flag the pathology. See §immune_response below.

    Args:
        f1, f2: Findings to compare.

    Returns:
        Similarity in [0, 1].
    """
    class_match = f1.flaw_class == f2.flaw_class

    # Tokenize with stopword removal
    tokens1 = _tokenize_for_similarity(f1.description)
    tokens2 = _tokenize_for_similarity(f2.description)

    # Handle empty descriptions
    if not tokens1 and not tokens2:
        return 0.8 if class_match else 0.2
    if not tokens1 or not tokens2:
        return 0.3 if class_match else 0.1

    # Unigram Jaccard (on content words only)
    words1 = set(tokens1)
    words2 = set(tokens2)
    uni_inter = len(words1 & words2)
    uni_union = len(words1 | words2)
    uni_jaccard = uni_inter / uni_union if uni_union else 0.0

    # Bigram Jaccard (phrase-level overlap)
    bg1 = _bigrams(tokens1)
    bg2 = _bigrams(tokens2)
    if bg1 or bg2:
        bg_inter = len(bg1 & bg2)
        bg_union = len(bg1 | bg2)
        bg_jaccard = bg_inter / bg_union if bg_union else 0.0
    else:
        bg_jaccard = uni_jaccard  # single-word descriptions: fall back to unigram

    # Combined similarity: 60% unigram + 40% bigram
    combined = 0.6 * uni_jaccard + 0.4 * bg_jaccard

    if class_match:
        # 0.3 base from class match + 0.7 from combined Jaccard
        return 0.3 + 0.7 * combined
    else:
        # No class match bonus — combined Jaccard only.
        # Confer consensus: raw Jaccard at tau_sim=0.8 was too strict.
        # Stopword removal + bigrams increase similarity for genuine
        # duplicates while maintaining discrimination.
        return combined


class DynamicManager:
    """Top-level orchestrator connecting all six areas.

    This class wires together Role Assignment, Load Balancing, Round Progression,
    Convergence Detection, Diminishing Returns, and Failure Handling into a
    coherent management layer.

    It does NOT perform actual model dispatch (that's the orchestrator's job).
    It provides the decision logic: what to dispatch, how to interpret results,
    when to stop.

    Example::

        models = [
            ModelSpec("m1", CapabilityFingerprint(0.1, 0.9, 0.8, 0.7), L=32768, c=0.01),
            ModelSpec("m2", CapabilityFingerprint(0.2, 0.7, 0.9, 0.8), L=32768, c=0.02),
            ModelSpec("m3", CapabilityFingerprint(0.3, 0.6, 0.7, 0.6), L=32768, c=0.015),
        ]
        cfg = DynamicManagementConfig()
        mgr = DynamicManager(models, cfg)

        # Get initial allocation
        tasks = [Task("t1", 5000, 1, 0.5), Task("t2", 8000, 2, 0.9)]
        alloc, cost, balanced = mgr.get_allocation(tasks)

        # After receiving responses, process them
        responses = {...}  # Dict[str, ModelResponse]
        findings = [...]   # List[Finding]
        result = mgr.process_round(responses, findings, tasks, round_cost=1.5)

        # Check if we should continue
        if mgr.fsm.is_terminal:
            print(f"Done: {mgr.fsm.termination_reason}")
    """

    def __init__(
        self,
        models: Sequence[ModelSpec],
        config: Optional[DynamicManagementConfig] = None,
        event_callback: Optional[Callable[[ManagerEvent], None]] = None,
    ) -> None:
        self.config = config or DynamicManagementConfig()
        self.models = list(models)
        self.event_stream = ManagerEventStream(callback=event_callback)

        # Area 1: Role Assignment
        self.role_assignment = RoleAssignment.assign(self.models, self.config)

        # Area 3: Round Progression FSM
        self.fsm = RoundProgressionFSM(self.config)

        # Area 4: Convergence Detection
        self.convergence_detector = ConvergenceDetector(
            self.config, similarity_fn=_finding_similarity
        )

        # Area 5: Diminishing Returns
        self.diminishing_returns = DiminishingReturnsDetector(self.config)

        # Area 6: Failure Handling
        self.failure_handler = FailureHandler(
            self.models,
            self.role_assignment.role_map,
            self.config,
            event_callback=self.event_stream.emit,
        )

        # Correlated failure model
        self.correlated_failures = CorrelatedFailureModel()

        # Area 7: Detector Health Monitor (immune response layer)
        self.health_monitor = DetectorHealthMonitor(config=self.config)

        # Round results history
        self._round_results: List[RoundResult] = []

        # Live fingerprint store: tracks observed capability per model across rounds.
        # Initial values come from ModelSpec.fingerprint. Updated after each round
        # from actual output metrics. This is the adaptive routing feedback loop:
        # observe performance → update fingerprint → reallocate next round.
        self._live_fingerprints: Dict[str, CapabilityFingerprint] = {
            m.model_id: m.fingerprint for m in self.models
        }
        # Per-model per-round metrics for fingerprint estimation
        self._round_metrics: Dict[str, List[Dict[str, float]]] = {
            m.model_id: [] for m in self.models
        }

        # --- Phase A: Per-model registry policies ---
        # Load Layer 4 TOML per model via cdsfl_registry.  The registry
        # enforces monotonicity: per-model layers cannot weaken HARD
        # constraints from the universal layer.
        self._per_model_policies: Dict[str, Dict[str, Any]] = {}
        self._load_per_model_policies()

        # --- Phase B: Immune feedback loop state ---
        # Tracks which parameters were last adjusted and when, to enforce
        # the damping rule (no param adjusted more than once per N rounds).
        self._immune_adjustments: List[Dict[str, Any]] = []
        # Log of all parameter adjustments for auditability.
        self._adjustment_log: List[Dict[str, Any]] = []
        # Deferred remediations: fixes classified as DEFER that need human
        # approval before application.  Each entry contains the full adjustment
        # that would be applied, plus rationale.
        self._deferred_remediations: List[Dict[str, Any]] = []
        # Regression snapshots: metric values captured before each AUTO fix,
        # used to detect if the fix made things worse.
        self._pre_fix_snapshots: List[Dict[str, Any]] = []
        # PR-3 fix: flag to defer autonomous remediation after regression
        self._regression_defer: bool = False

        # --- Phase E: Dispatch health tracking ---
        # Records dispatch blocking events per model for false-positive detection.
        self._dispatch_blocks: Dict[str, List[int]] = {
            m.model_id: [] for m in self.models
        }
        self._dispatch_successes_after_block: Dict[str, List[int]] = {
            m.model_id: [] for m in self.models
        }
        # Per-model verification rates for miscalibration detection.
        self._per_model_verification: Dict[str, List[float]] = {
            m.model_id: [] for m in self.models
        }

    def get_allocation(
        self, tasks: Sequence[Task]
    ) -> Tuple[Allocation, float, bool]:
        """Get task allocation for the current round.

        Uses Area 2 (Load Balancing) with LIVE fingerprints — allocation
        adapts to observed performance, not just initial estimates. Every
        active model gets work matched to its demonstrated capability.
        No model is excluded for being "weaker."

        Args:
            tasks: Tasks to allocate.

        Returns:
            (allocation, cost, is_balanced)
        """
        active_models = self.get_live_models()
        if not active_models:
            raise RuntimeError("No active models available for allocation")

        lb = LoadBalancer(
            active_models,
            tasks,
            self.role_assignment.role_map,
            self.config,
        )
        return lb.solve()

    def check_dispatch_feasibility(
        self, model: ModelSpec, task_load: float
    ) -> Tuple[bool, float]:
        """Pre-dispatch feasibility check with uncertainty.

        Args:
            model: Target model.
            task_load: Total token demand.

        Returns:
            (should_dispatch, p_feasible)
        """
        # Use a temporary LoadBalancer for the feasibility check
        lb = LoadBalancer(
            [model], [], self.role_assignment.role_map, self.config
        )
        ok, p = lb.dispatch_check(model, task_load)
        if not ok:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.DISPATCH_BLOCKED,
                    model_id=model.model_id,
                    round_idx=self.fsm.current_round,
                    detail=f"P(feasible)={p:.3f} < threshold={self.config.feasibility_threshold}",
                    metadata={"p_feasible": p, "task_load": task_load},
                )
            )
            # Wire into Phase E dispatch health tracking (Exp14 fix:
            # ChatGPT F003, sev 0.94 — record_dispatch_block was never called)
            self.record_dispatch_block(model.model_id, self.fsm.current_round)
        elif p < 0.99 and model.L_std > 0:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.FEASIBILITY_WARNING,
                    model_id=model.model_id,
                    round_idx=self.fsm.current_round,
                    detail=f"P(feasible)={p:.3f} (uncertain L: {model.L}±{model.L_std})",
                    metadata={"p_feasible": p, "task_load": task_load},
                )
            )
        return ok, p

    def process_round(
        self,
        responses: Dict[str, ModelResponse],
        findings: List[Finding],
        tasks: Sequence[Task],
        round_cost: float,
        duration: float = 1.0,
        adoption_delta: float = 0.0,
    ) -> RoundResult:
        """Process a completed round: detect failures, update metrics, advance FSM.

        This is the main entry point after the orchestrator has dispatched tasks
        and collected responses.

        Args:
            responses: Model responses keyed by model_id.
            findings: All findings extracted from responses.
            tasks: Tasks that were allocated this round.
            round_cost: Total cost of this round.
            duration: Wall-clock duration of this round.
            adoption_delta: Delta_r from existing schema.

        Returns:
            RoundResult with all metrics and decisions.
        """
        # The FSM advances current_round at the END of this method (via
        # select_event → COMPLETE).  So reading fsm.current_round here gives
        # the PREVIOUS round's index for rounds > 0.  Track the actual count
        # of process_round calls instead.
        if not hasattr(self, '_process_round_count'):
            self._process_round_count = 0
        round_idx = self._process_round_count
        self._process_round_count += 1

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.ROUND_COMPLETE,
                model_id="system",
                round_idx=round_idx,
                detail=f"Processing round {round_idx} with {len(findings)} findings",
            )
        )

        # --- Area 6: Failure detection ---
        failures: Dict[str, Optional[FailureType]] = {}
        recovery_actions: Dict[str, str] = {}  # Exp15 fix: propagate to RoundResult
        critical_failure = False

        for model_id, response in responses.items():
            failure_type = self.failure_handler.detect_failure(response)
            failures[model_id] = failure_type

            if failure_type is not None:
                action = self.failure_handler.get_recovery(
                    model_id, round_idx, failure_type
                )
                recovery_actions[model_id] = action.value
                self.role_assignment.record_failure(model_id, True)

                if action == RecoveryAction.ABORT:
                    critical_failure = True
            else:
                self.role_assignment.record_failure(model_id, False)

        # Check abort condition
        if self.failure_handler.should_abort():
            critical_failure = True

        # --- Area 4: Convergence detection ---
        self.convergence_detector.add_round_findings(
            round_idx, findings, duration, adoption_delta
        )
        kappa = self.convergence_detector.kappa(round_idx)
        is_converged = self.convergence_detector.converged(round_idx)

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.CONVERGENCE_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=f"kappa={kappa:.4f}, converged={is_converged}",
                metadata={"kappa": kappa, "converged": is_converged},
            )
        )

        # --- Area 5: Diminishing returns ---
        # Compute cumulative yield
        cumulative_classes = self.convergence_detector.get_cumulative_classes(round_idx)
        cum_findings_flat = []
        for ec in cumulative_classes:
            cum_findings_flat.extend(ec.members)

        novel_classes = self.convergence_detector._novel_classes(round_idx)
        new_findings_flat = []
        for ec in novel_classes:
            new_findings_flat.extend(ec.members)

        self.diminishing_returns.add_round_from_findings(
            round_idx, cum_findings_flat, new_findings_flat, round_cost
        )

        # Per-model mu: group findings by model and register each model's
        # contribution independently (Exp13a, CC2 approved HARD).
        # Exp14 fix (CC2 F013/F015, sev 0.75): cost is now proportional to
        # each model's response content, not uniformly divided.  A model that
        # produced 10K chars of output should bear more cost than one that
        # produced 2K chars.  Uniform division distorts per-model mu when
        # output sizes vary (which they always do — CC2 ~38K, Gemini ~5K).
        per_model_findings: Dict[str, List[Finding]] = defaultdict(list)
        for f in new_findings_flat:
            per_model_findings[f.model_id].append(f)
        active = self.failure_handler.active_models
        # Weight cost by response content length
        total_content = sum(
            len(responses.get(mid, ModelResponse(
                model_id=mid, round_idx=round_idx, content="",
                response_time=0, parseable=False, format_compliant=False,
                finding_count=0, mean_abstraction=0,
            )).content)
            for mid in active
        )
        for model_id in active:
            model_findings = per_model_findings.get(model_id, [])
            resp = responses.get(model_id)
            if total_content > 0 and resp:
                model_cost = round_cost * len(resp.content) / total_content
            else:
                model_cost = round_cost / max(len(active), 1)
            self.diminishing_returns.add_model_round(
                model_id, round_idx, model_findings, model_cost
            )

        mu = self.diminishing_returns.marginal_value(round_idx) if round_idx in self.diminishing_returns._cumulative_yields else 0.0
        is_diminished = self.diminishing_returns.stop(round_idx)

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.STOP_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=f"mu={mu:.4f}, stop={is_diminished}",
                metadata={"mu": mu, "stop": is_diminished},
            )
        )

        # --- Area 7: Detector Health Monitor (immune response) ---
        novelty = self.diminishing_returns.novelty_rate(round_idx)

        # Feed vocab_growth to health monitor for saturation detection (Exp15)
        vg_rate = self.diminishing_returns.vocab_growth_rate(round_idx)
        self.health_monitor.record_vocab_growth(vg_rate)

        # Feed per-model round data for failure pattern detection (Exp15)
        _model_finding_counts = Counter(f.model_id for f in findings)
        for model in self.models:
            mid = model.model_id
            fc = _model_finding_counts.get(mid, 0)
            failed = mid not in responses or not responses[mid].parseable
            resp = responses.get(mid)
            model_diags = self.health_monitor.record_model_round(
                mid, fc, failed,
                response_time=resp.response_time if resp and hasattr(resp, 'response_time') else 0.0,
                response_chars=len(resp.content) if resp and resp.content else 0,
            )
            # DC-2 fix: consolidate per-model diagnoses into health monitor
            self.health_monitor.register_diagnoses(model_diags)
            for model_diag in model_diags:
                self.event_stream.emit(
                    ManagerEvent(
                        event_type=ManagerEventType.STOP_CHECK,
                        model_id=mid,
                        round_idx=round_idx,
                        detail=f"[IMMUNE:{model_diag.severity}] {model_diag.detector}: "
                               f"{model_diag.pathology}",
                        metadata={
                            "immune_response": True,
                            "detector": model_diag.detector,
                            "severity": model_diag.severity,
                            "action": model_diag.recommended_action,
                            "evidence": model_diag.evidence,
                        },
                    )
                )
                self.apply_diagnosis(model_diag, round_idx)

        diagnoses = self.health_monitor.record_round(
            kappa=kappa,
            mu=mu,
            novelty_rate=novelty,
            finding_count=len(findings),
            active_models=len(self.failure_handler.active_models),
        )
        for diag in diagnoses:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.STOP_CHECK,
                    model_id="system",
                    round_idx=round_idx,
                    detail=f"[IMMUNE:{diag.severity}] {diag.detector}: {diag.pathology}",
                    metadata={
                        "immune_response": True,
                        "detector": diag.detector,
                        "severity": diag.severity,
                        "action": diag.recommended_action,
                        "evidence": diag.evidence,
                    },
                )
            )
            # Phase B: Close the feedback loop — apply diagnosis automatically.
            self.apply_diagnosis(diag, round_idx)

        # --- Phase E: Per-model verification tracking ---
        _vr_by_model: Dict[str, List[bool]] = defaultdict(list)
        for f in findings:
            _vr_by_model[f.model_id].append(f.verified)
        for mid, vlist in _vr_by_model.items():
            rate = sum(vlist) / len(vlist) if vlist else 0.0
            self.record_model_verification_rate(mid, rate)

        # --- Phase E: Dispatch health monitoring ---
        dispatch_diagnoses = self.health_monitor.check_dispatch_health(
            self._dispatch_blocks,
            self._dispatch_successes_after_block,
            self._per_model_verification,
            round_idx,
        )
        for diag in dispatch_diagnoses:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.STOP_CHECK,
                    model_id="system",
                    round_idx=round_idx,
                    detail=f"[IMMUNE:{diag.severity}] {diag.detector}: {diag.pathology}",
                    metadata={
                        "immune_response": True,
                        "detector": diag.detector,
                        "severity": diag.severity,
                        "action": diag.recommended_action,
                        "evidence": diag.evidence,
                    },
                )
            )
            # Close the feedback loop for dispatch diagnoses too.
            self.apply_diagnosis(diag, round_idx)

        # --- Regression detection (Exp15) ---
        # Check if any AUTO fix made metrics worse.  If a fix caused a
        # regression (target metric declined AND another metric dropped
        # significantly), log and defer future fixes for human review.
        if self._pre_fix_snapshots and round_idx >= 2:
            for snap in self._pre_fix_snapshots:
                if round_idx - snap["round"] < 2:
                    continue  # too early to judge
                current_metrics = {
                    "kappa": self._get_current_metric("kappa"),
                    "mu": self._get_current_metric("mu"),
                    "finding_count": self._get_current_metric("finding_count"),
                    "vocab_growth": self._get_current_metric("vocab_growth"),
                }
                pre_metrics = snap["metrics"]
                # Check for regression: finding_count dropped by >30%
                pre_fc = pre_metrics.get("finding_count", 0)
                cur_fc = current_metrics.get("finding_count", 0)
                if pre_fc > 0 and cur_fc < pre_fc * 0.7:
                    self.event_stream.emit(
                        ManagerEvent(
                            event_type=ManagerEventType.STOP_CHECK,
                            model_id="system",
                            round_idx=round_idx,
                            detail=(
                                f"[IMMUNE:REGRESSION] Fix at round {snap['round']} "
                                f"({snap['chain_key']} step {snap['chain_idx']}) "
                                f"may have caused regression: finding_count "
                                f"{pre_fc:.0f} → {cur_fc:.0f} (-{(1-cur_fc/pre_fc)*100:.0f}%). "
                                f"Deferring further autonomous fixes for human review."
                            ),
                            metadata={
                                "regression": True,
                                "pre_fix": pre_metrics,
                                "post_fix": current_metrics,
                                "fix_round": snap["round"],
                            },
                        )
                    )
                    # PR-3 fix: set regression defer flag
                    self._regression_defer = True
            # Clean up checked snapshots
            self._pre_fix_snapshots = [
                s for s in self._pre_fix_snapshots
                if round_idx - s["round"] < 2
            ]

        # --- Area 3: FSM transition ---
        event = self.fsm.select_event(
            converged=is_converged,
            diminished=is_diminished,
            critical_failure=critical_failure,
            round_complete=True,
        )
        new_state = self.fsm.transition(event)

        # --- PR-1 fix: update fingerprints BEFORE role reassignment ---
        # Role reassignment uses _live_fingerprints, so fingerprints must be
        # current before reassign() reads them.
        # CRITICAL: update fingerprints BEFORE appending the RoundResult.
        # update_fingerprints() builds prior_findings from self._round_results.
        # If the current round is already appended, every finding matches itself
        # via similarity, driving D_decay to 1.0 regardless of actual duplication.
        # CX identified this in the confer round (confidence 0.98).
        if not self.fsm.is_terminal:
            self.update_fingerprints(round_idx, findings, responses)

        # --- Area 1: Role reassignment (if continuing) ---
        if not self.fsm.is_terminal:
            self.role_assignment.reassign(
                round_idx, self.failure_handler.active_models,
                live_fingerprints=self._live_fingerprints,
            )
            # Update failure handler's role map
            self.failure_handler.role_map = self.role_assignment.role_map

        result = RoundResult(
            round_idx=round_idx,
            findings=findings,
            responses=responses,
            allocation=None,  # Caller retains allocation reference
            convergence_metric=kappa,
            marginal_value=mu,
            converged=is_converged,
            stop=is_diminished,
            failures=failures,
            recovery_actions=recovery_actions,
            active_models=self.failure_handler.active_models,
            state=new_state,
        )
        self._round_results.append(result)

        return result

    def update_fingerprints(
        self,
        round_idx: int,
        findings: List[Finding],
        responses: Dict[str, ModelResponse],
    ) -> None:
        """Update live fingerprints from observed round performance.

        This is the adaptive routing feedback loop. After each round, we compute
        observed capability metrics from actual output and update each model's
        fingerprint. The next round's allocation uses the updated fingerprints.

        The update uses exponential moving average (EMA) to smooth over rounds,
        preventing a single bad round from drastically changing allocation while
        still adapting to sustained performance patterns.

        Observed metrics per model per round:
            D_decay: proportion of findings that are duplicates of prior rounds
                     (higher = more repetitive = faster decay)
            v_bar:   proportion of findings with verified=True
            A:       mean severity of findings (proxy for accuracy/depth)
            C:       number of distinct flaw classes covered / total classes seen

        Every model that produced output gets updated. Models that produced no
        findings still get a valid (low) fingerprint — they are not excluded.
        The 386 principle: even minimal output contributes to coverage.

        Args:
            round_idx: Current round index.
            findings: All findings from this round.
            responses: Model responses keyed by model_id.
        """
        alpha_ema = self.config.fingerprint_ema_alpha if hasattr(self.config, 'fingerprint_ema_alpha') else 0.3

        # Group findings by model
        findings_by_model: Dict[str, List[Finding]] = {}
        for f in findings:
            findings_by_model.setdefault(f.model_id, []).append(f)

        # All flaw classes seen across all models this round
        all_classes_this_round = set()
        for f in findings:
            all_classes_this_round.add(f.flaw_class)
        total_classes = max(len(all_classes_this_round), 1)

        # Prior findings for similarity-based duplicate detection
        prior_findings: List[Finding] = []
        for prev_result in self._round_results:
            prior_findings.extend(prev_result.findings)

        for model_id in self.failure_handler.active_models:
            model_findings = findings_by_model.get(model_id, [])
            old_fp = self._live_fingerprints[model_id]

            if not model_findings:
                # Model produced no findings this round. Give it a minimal
                # but non-zero observed fingerprint. It still participates.
                obs = {
                    "D_decay": 0.5,  # neutral — no data to judge decay
                    "v_bar": 0.0,    # no findings to verify
                    "A": 0.0,        # no severity to measure
                    "C": 0.0,        # no classes covered
                }
            else:
                # D_decay: fraction of findings that are similar to prior rounds.
                # Uses the same similarity function as convergence detection
                # rather than finding_id string matching (which only catches
                # coincidental label reuse, not actual content duplication).
                if prior_findings:
                    duplicates = 0
                    for f in model_findings:
                        for pf in prior_findings:
                            if _finding_similarity(f, pf) >= self.config.tau_sim:
                                duplicates += 1
                                break
                    obs_d = duplicates / len(model_findings)
                else:
                    obs_d = 0.0  # first round, nothing is duplicate

                # v_bar: fraction verified
                verified = sum(1 for f in model_findings if f.verified)
                obs_v = verified / len(model_findings)

                # A: mean severity (depth proxy)
                obs_a = sum(f.severity for f in model_findings) / len(model_findings)

                # C: distinct flaw classes / total classes
                model_classes = set(f.flaw_class for f in model_findings)
                obs_c = len(model_classes) / total_classes

                obs = {"D_decay": obs_d, "v_bar": obs_v, "A": obs_a, "C": obs_c}

            # Store round metrics
            self._round_metrics[model_id].append(obs)

            # Fingerprint update: windowed mean (default) or EMA (legacy).
            # EMA with alpha=0.3 collapses all dimensions to ~0 over 20 rounds
            # (Exp12 finding: 0.9 * 0.7^20 ≈ 0.0007).  Windowed mean over
            # the last W rounds prevents this by only using recent observations.
            window = self.config.fingerprint_window
            if window > 0 and len(self._round_metrics[model_id]) > 0:
                # Use windowed mean over last W observations
                recent = self._round_metrics[model_id][-window:]
                new_fp = CapabilityFingerprint(
                    D_decay=sum(o["D_decay"] for o in recent) / len(recent),
                    v_bar=sum(o["v_bar"] for o in recent) / len(recent),
                    A=sum(o["A"] for o in recent) / len(recent),
                    C=sum(o["C"] for o in recent) / len(recent),
                )
            else:
                # Legacy EMA: new = alpha * observed + (1 - alpha) * old
                new_fp = CapabilityFingerprint(
                    D_decay=alpha_ema * obs["D_decay"] + (1 - alpha_ema) * old_fp.D_decay,
                    v_bar=alpha_ema * obs["v_bar"] + (1 - alpha_ema) * old_fp.v_bar,
                    A=alpha_ema * obs["A"] + (1 - alpha_ema) * old_fp.A,
                    C=alpha_ema * obs["C"] + (1 - alpha_ema) * old_fp.C,
                )
            self._live_fingerprints[model_id] = new_fp

        # CX_FFF_005: Check if PM has degraded below worst PAR (LB_F005)
        active_ids = {m.model_id for m in self.models if m.model_id in responses}
        pm_warn = self.role_assignment.pm_performance_warning(
            live_fingerprints=self._live_fingerprints,
            active_models=active_ids,
        )
        if pm_warn:
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.ROUND_COMPLETE,
                    model_id="system",
                    round_idx=round_idx,
                    detail=pm_warn,
                )
            )

        # Emit event with updated fingerprints
        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.ROUND_COMPLETE,
                model_id="system",
                round_idx=round_idx,
                detail="Fingerprints updated from observed performance",
                metadata={
                    mid: {
                        "D_decay": round(fp.D_decay, 4),
                        "v_bar": round(fp.v_bar, 4),
                        "A": round(fp.A, 4),
                        "C": round(fp.C, 4),
                    }
                    for mid, fp in self._live_fingerprints.items()
                },
            )
        )

    def get_live_models(self) -> List[ModelSpec]:
        """Return model specs with live-updated fingerprints.

        This replaces the static initial fingerprints with observed ones
        for allocation purposes. The original ModelSpec objects are immutable
        (frozen dataclass) so we create new ones with updated fingerprints.

        Every active model gets a spec. No model is excluded based on
        capability — only transport failures (EMPTY, TIMEOUT, MALFORMED)
        after repeated occurrences can remove a model from the active set.
        """
        live_models = []
        for m in self.models:
            if m.model_id in self.failure_handler.active_models:
                live_fp = self._live_fingerprints.get(m.model_id, m.fingerprint)
                # Create new spec with updated fingerprint
                live_models.append(ModelSpec(
                    model_id=m.model_id,
                    fingerprint=live_fp,
                    tau=m.tau,
                    L=m.L,
                    c=m.c,
                    L_std=m.L_std,
                ))
        return live_models

    # --- Phase A: Per-model registry wiring ---

    def _load_per_model_policies(self) -> None:
        """Load Layer 4 TOML configs for each model via the CDSFL registry.

        The registry enforces monotonicity: per-model modifications cannot
        weaken HARD constraints from the universal layer.  If the registry
        is unavailable (e.g. running outside the bench directory), logs a
        warning and continues with empty policies.
        """
        try:
            from bench.cdsfl_registry.registry import load_effective_policy
        except ImportError:
            try:
                from cdsfl_registry.registry import load_effective_policy
            except ImportError:
                logging.warning(
                    "CDSFL registry not available — per-model policies disabled"
                )
                return

        # Map model_id to registry model config name.
        # Convention: model_id uses hyphens, TOML filenames use underscores.
        for model in self.models:
            config_name = model.model_id.replace("-", "_").replace(".", "_")
            try:
                policy = load_effective_policy(
                    domain="code",  # dynamic_management.py is code review
                    model=config_name,
                )
                self._per_model_policies[model.model_id] = policy

                # Extract per-model directives if present.
                model_section = policy.get("model", {})
                directive = model_section.get("adaptive_directive", "")
                if directive and len(directive) <= self.config.max_per_model_directive_chars:
                    self.config.per_model_directives[model.model_id] = directive

            except FileNotFoundError:
                logging.debug(f"No registry config for model {model.model_id}")
            except Exception as e:
                logging.warning(
                    f"Failed to load policy for {model.model_id}: {e}"
                )

    def get_model_directive(self, model_id: str) -> str:
        """Return any per-model prompt directive for adaptive dispatch.

        Returns empty string if no directive exists for this model.
        This is used by the orchestrator to prepend model-specific
        instructions to the CDSFL system prompt.
        """
        return self.config.per_model_directives.get(model_id, "")

    # --- Phase B: Immune feedback loop ---

    # --- Remediation chains (Exp15) ---
    # Each pathology has a prioritised sequence of fixes. The immune layer
    # tries fix 0 first, verifies the outcome, and escalates to fix 1 if
    # the metric didn't improve within the verification window.
    #
    # Chain format: list of (parameter, transform_fn, metric_to_verify) tuples.
    # transform_fn: (config, old_value) → new_value
    # Returns None if no further escalation is possible (chain exhausted).

    # Risk levels for remediation steps:
    #   AUTO  — safe to apply without human review (bounded parameter tweaks)
    #   DEFER — requires human approval before application (structural changes,
    #           multi-parameter modifications, or anything that could cause
    #           regression cascades)
    #
    # The immune layer applies AUTO fixes immediately.  DEFER fixes are queued
    # in _deferred_remediations with full rationale.  The experiment report
    # surfaces them for human review.

    _REMEDIATION_CHAINS: ClassVar[Dict[str, List[Dict[str, Any]]]] = {
        "kappa_stuck": [
            # Step 0: Lower tau_sim by 0.1 — bounded, reversible
            {"parameter": "tau_sim", "transform": "lower_tau_sim_01",
             "target_metric": "kappa", "description": "lower tau_sim by 0.1",
             "risk": "AUTO"},
            # Step 1: Lower tau_sim again — still bounded but second adjustment
            {"parameter": "tau_sim", "transform": "lower_tau_sim_01",
             "target_metric": "kappa", "description": "lower tau_sim by 0.1 again",
             "risk": "AUTO"},
            # Step 2: Floor tau_sim — aggressive, could cause false convergence
            {"parameter": "tau_sim", "transform": "lower_tau_sim_to_floor",
             "target_metric": "kappa",
             "description": "lower tau_sim to floor (0.3)",
             "risk": "DEFER"},
        ],
        "vocab_saturation": [
            # Step 0: Halve tau_vocab_growth — bounded
            {"parameter": "tau_vocab_growth", "transform": "halve_tau_vocab",
             "target_metric": "vocab_growth",
             "description": "halve tau_vocab_growth",
             "risk": "AUTO"},
            # Step 1: Quarter it — getting aggressive
            {"parameter": "tau_vocab_growth", "transform": "halve_tau_vocab",
             "target_metric": "vocab_growth",
             "description": "halve tau_vocab_growth again",
             "risk": "DEFER"},
        ],
        "findings_decline": [
            # Step 0: Add cross-area synthesis directive — modifies all models
            {"parameter": "per_model_directives", "transform": "add_synthesis_directive",
             "target_metric": "finding_count",
             "description": "add cross-area synthesis directive to all models",
             "risk": "DEFER"},
        ],
        "model_failure": [
            # Step 0: Add model to pre-decompose set — safe structural change
            {"parameter": "pre_decompose_models", "transform": "add_to_pre_decompose",
             "target_metric": "finding_count",
             "description": "pre-decompose failing model",
             "risk": "AUTO"},
        ],
        # PK-3 fix: missing remediation chains for new pathology types
        "mu_distortion": [
            # Step 0: Widen mu window — bounded, reversible
            {"parameter": "mu_increase_window", "transform": "widen_mu_window",
             "target_metric": "mu",
             "description": "widen mu detection window by 1",
             "risk": "AUTO"},
            # Step 1: Flag mu as unreliable, prefer novelty_rate
            {"parameter": "stop_signal_priority", "transform": "prefer_novelty",
             "target_metric": "mu",
             "description": "prefer novelty_rate over mu for stop signal",
             "risk": "DEFER"},
        ],
        "mu_novelty_disagree": [
            # Step 0: Advisory — prefer novelty_rate
            {"parameter": "stop_signal_priority", "transform": "prefer_novelty",
             "target_metric": "mu",
             "description": "prefer novelty_rate over mu (disagreement detected)",
             "risk": "AUTO"},
            # Step 1: Widen mu window to reduce sensitivity
            {"parameter": "mu_increase_window", "transform": "widen_mu_window",
             "target_metric": "mu",
             "description": "widen mu detection window by 1",
             "risk": "AUTO"},
        ],
        "parser_yield": [
            # Step 0: Add parsing directive to affected model
            {"parameter": "per_model_directives", "transform": "add_parsing_directive",
             "target_metric": "finding_count",
             "description": "add structured-output parsing directive",
             "risk": "AUTO"},
            # Step 1: Pre-decompose model to reduce output complexity
            {"parameter": "pre_decompose_models", "transform": "add_to_pre_decompose",
             "target_metric": "finding_count",
             "description": "pre-decompose model with low parser yield",
             "risk": "AUTO"},
        ],
        "monotonic_decline": [
            # Step 0: Add cross-area synthesis directive
            {"parameter": "per_model_directives", "transform": "add_synthesis_directive",
             "target_metric": "finding_count",
             "description": "add synthesis directive to counter decline",
             "risk": "AUTO"},
            # Step 1: Widen stuck window to tolerate temporary dips
            {"parameter": "stuck_window", "transform": "widen_stuck_window",
             "target_metric": "kappa",
             "description": "widen stuck detection window by 1",
             "risk": "DEFER"},
        ],
        "cpf_spike": [
            # Step 0: Flag model for closer verification scrutiny
            {"parameter": "per_model_directives", "transform": "add_verification_directive",
             "target_metric": "finding_count",
             "description": "add verification scrutiny directive after CPF spike",
             "risk": "AUTO"},
            # Step 1: Pre-decompose to reduce failure cascades
            {"parameter": "pre_decompose_models", "transform": "add_to_pre_decompose",
             "target_metric": "finding_count",
             "description": "pre-decompose model after CPF spike",
             "risk": "AUTO"},
        ],
        "dispatch_false_positive": [
            # Step 0: Pre-decompose blocked model
            {"parameter": "pre_decompose_models", "transform": "add_to_pre_decompose",
             "target_metric": "finding_count",
             "description": "pre-decompose model that was falsely blocked",
             "risk": "AUTO"},
            # Step 1: Lower feasibility threshold for this model
            {"parameter": "feasibility_threshold", "transform": "lower_feasibility_threshold",
             "target_metric": "finding_count",
             "description": "lower feasibility threshold to reduce false blocking",
             "risk": "DEFER"},
        ],
        "verification_miscalibration": [
            # Step 0: Add verification re-examination directive
            {"parameter": "per_model_directives", "transform": "add_verification_directive",
             "target_metric": "finding_count",
             "description": "add verification re-examination directive",
             "risk": "AUTO"},
            # Step 1: Flag model's VERIFIED field as unreliable system-wide
            {"parameter": "verification_trust", "transform": "flag_verification_unreliable",
             "target_metric": "finding_count",
             "description": "flag model verification as unreliable",
             "risk": "DEFER"},
        ],
    }

    def _apply_transform(
        self, transform_name: str, diagnosis: DetectorDiagnosis
    ) -> Optional[Dict[str, Any]]:
        """Execute a named transform on the config. Returns adjustment dict."""
        if transform_name == "lower_tau_sim_01":
            old_val = self.config.tau_sim
            new_val = max(0.3, old_val - 0.1)
            if new_val != old_val:
                self.config.tau_sim = new_val
                return {"parameter": "tau_sim", "old": old_val, "new": new_val,
                        "reason": diagnosis.pathology}

        elif transform_name == "lower_tau_sim_to_floor":
            old_val = self.config.tau_sim
            new_val = 0.3
            if new_val != old_val:
                self.config.tau_sim = new_val
                return {"parameter": "tau_sim", "old": old_val, "new": new_val,
                        "reason": diagnosis.pathology}

        elif transform_name == "halve_tau_vocab":
            old_val = self.config.tau_vocab_growth
            new_val = max(0.01, old_val * 0.5)
            if new_val != old_val:
                self.config.tau_vocab_growth = new_val
                return {"parameter": "tau_vocab_growth", "old": old_val,
                        "new": new_val, "reason": diagnosis.pathology}

        elif transform_name == "add_synthesis_directive":
            directive = (
                "Previous rounds show declining findings. Look for "
                "cross-cutting issues that span multiple areas: interface "
                "contracts, shared state, assumption mismatches between "
                "components. Focus on system-level rather than local flaws."
            )
            added_to: List[str] = []
            for model in self.models:
                if model.model_id not in self.config.per_model_directives:
                    if len(directive) <= self.config.max_per_model_directive_chars:
                        self.config.per_model_directives[model.model_id] = directive
                        added_to.append(model.model_id)
            if added_to:
                return {"parameter": "per_model_directives",
                        "old": "none",
                        "new": f"synthesis directive added to {added_to}",
                        "reason": diagnosis.pathology}

        elif transform_name == "add_to_pre_decompose":
            model_id = diagnosis.evidence.get("model_id", "")
            if model_id and model_id not in self.config.pre_decompose_models:
                self.config.pre_decompose_models.add(model_id)
                return {"parameter": "pre_decompose_models",
                        "old": "not in set",
                        "new": f"added {model_id}",
                        "reason": diagnosis.pathology}

        # --- Run 6 bug 5: implement 7 missing transforms ---

        elif transform_name == "widen_mu_window":
            hm = self.health_monitor
            old_val = hm._mu_increase_window
            max_val = hm._original_mu_window * 2
            new_val = min(max_val, old_val + 1)
            if new_val != old_val:
                hm._mu_increase_window = new_val
                return {"parameter": "mu_increase_window", "old": old_val,
                        "new": new_val, "reason": diagnosis.pathology}

        elif transform_name == "prefer_novelty":
            hm = self.health_monitor
            if not getattr(hm, "_prefer_novelty_over_mu", False):
                hm._prefer_novelty_over_mu = True
                return {"parameter": "stop_signal_priority",
                        "old": "default (mu + novelty)",
                        "new": "prefer novelty_rate over mu",
                        "reason": diagnosis.pathology}

        elif transform_name == "add_parsing_directive":
            directive = (
                "Return findings in strict JSON format. Each finding must "
                "have: title, description, severity (0.0-1.0), location. "
                "Do not embed findings in prose or markdown tables."
            )
            model_id = diagnosis.evidence.get("model_id", "")
            if model_id and model_id not in self.config.per_model_directives:
                if len(directive) <= self.config.max_per_model_directive_chars:
                    self.config.per_model_directives[model_id] = directive
                    return {"parameter": "per_model_directives",
                            "old": "none",
                            "new": f"parsing directive added to {model_id}",
                            "reason": diagnosis.pathology}

        elif transform_name == "widen_stuck_window":
            hm = self.health_monitor
            old_val = hm._stuck_window
            max_val = hm._original_stuck_window * 2
            new_val = min(max_val, old_val + 1)
            if new_val != old_val:
                hm._stuck_window = new_val
                return {"parameter": "stuck_window", "old": old_val,
                        "new": new_val, "reason": diagnosis.pathology}

        elif transform_name == "add_verification_directive":
            directive = (
                "Re-examine findings marked VERIFIED in prior rounds. "
                "Cross-check verification claims against actual code. "
                "Flag any verification that lacks specific evidence."
            )
            model_id = diagnosis.evidence.get("model_id", "")
            if model_id and model_id not in self.config.per_model_directives:
                if len(directive) <= self.config.max_per_model_directive_chars:
                    self.config.per_model_directives[model_id] = directive
                    return {"parameter": "per_model_directives",
                            "old": "none",
                            "new": f"verification directive added to {model_id}",
                            "reason": diagnosis.pathology}

        elif transform_name == "lower_feasibility_threshold":
            old_val = self.config.feasibility_threshold
            new_val = max(0.70, old_val - 0.05)  # Floor at 0.70
            if new_val != old_val:
                self.config.feasibility_threshold = new_val
                return {"parameter": "feasibility_threshold", "old": old_val,
                        "new": new_val, "reason": diagnosis.pathology}

        elif transform_name == "flag_verification_unreliable":
            model_id = diagnosis.evidence.get("model_id", "")
            if not hasattr(self, "_verification_unreliable_models"):
                self._verification_unreliable_models: Set[str] = set()
            if model_id and model_id not in self._verification_unreliable_models:
                self._verification_unreliable_models.add(model_id)
                return {"parameter": "verification_trust",
                        "old": "trusted",
                        "new": f"{model_id} flagged as unreliable",
                        "reason": diagnosis.pathology}

        return None

    def apply_diagnosis(
        self,
        diagnosis: DetectorDiagnosis,
        round_idx: int,
    ) -> Optional[Dict[str, Any]]:
        """Act on an immune layer diagnosis using remediation chains.

        Autonomous remediation (Exp15): each pathology maps to a prioritised
        chain of fixes. The system tracks which step in the chain was last
        applied and escalates if the fix didn't work (verified by
        DetectorHealthMonitor._verify_remediation_outcomes).

        Damping rule: no parameter adjusted more than once every
        immune_damping_rounds rounds.

        Args:
            diagnosis: The diagnosis from DetectorHealthMonitor.
            round_idx: Current round index.

        Returns:
            Dict describing the adjustment made, or None if no action taken.
        """
        if not self.config.immune_feedback_enabled:
            return None

        # Skip remediation outcome reports — they're informational only
        if diagnosis.detector == "remediation_outcome":
            return None

        # PR-3 fix: skip autonomous remediation if regression detected
        if getattr(self, '_regression_defer', False):
            return None

        # Check damping: was this parameter adjusted recently?
        # Use composite key (detector + model_id if present) to prevent
        # per-model pathologies from interfering across models (IM_F005).
        diag_model = diagnosis.evidence.get("model_id", "")
        for adj in self._immune_adjustments:
            adj_model = adj.get("model_id", "")
            if (adj["detector"] == diagnosis.detector
                    and adj_model == diag_model
                    and round_idx - adj["round"] < self.config.immune_damping_rounds):
                return None  # Too soon — damping prevents oscillation

        # --- Map diagnosis to remediation chain ---
        # IM_F013: Use machine-readable pathology_key first, fall back to
        # string matching for backward compatibility with legacy diagnoses.
        chain_key = None
        if diagnosis.pathology_key and diagnosis.pathology_key in self._REMEDIATION_CHAINS:
            chain_key = diagnosis.pathology_key
        elif diagnosis.detector == "kappa" and "stuck" in diagnosis.pathology.lower():
            chain_key = "kappa_stuck"
        elif diagnosis.detector == "vocab_saturation" and "premature" in diagnosis.pathology.lower():
            chain_key = "vocab_saturation"
        elif diagnosis.detector == "findings_decline":
            chain_key = "findings_decline"
        elif diagnosis.detector == "model_failure":
            chain_key = "model_failure"

        if diagnosis.pathology_key == "dispatch_false_positive" or (
            not diagnosis.pathology_key and diagnosis.detector == "dispatch"
            and "false positive" in diagnosis.pathology.lower()
        ):
            # Direct fix, no chain needed
            model_id = diagnosis.evidence.get("model_id", "")
            if model_id and model_id not in self.config.pre_decompose_models:
                self.config.pre_decompose_models.add(model_id)
                adjustment = {
                    "parameter": "pre_decompose_models",
                    "old": "not in set",
                    "new": f"added {model_id}",
                    "reason": diagnosis.pathology,
                }
                self._record_adjustment(adjustment, diagnosis, round_idx)
                return adjustment
            return None
        elif diagnosis.pathology_key == "mu_novelty_disagree" or (
            not diagnosis.pathology_key and diagnosis.detector == "mu+novelty"
            and "disagree" in diagnosis.pathology.lower()
        ):
            # Advisory — no parameter to adjust
            adjustment = {
                "parameter": "stop_signal_priority",
                "old": "mu+novelty combined",
                "new": "novelty_rate preferred (mu unreliable)",
                "reason": diagnosis.pathology,
            }
            self._record_adjustment(adjustment, diagnosis, round_idx)
            return adjustment
        elif diagnosis.pathology_key == "verification_miscalibration" or (
            not diagnosis.pathology_key and diagnosis.detector == "verification"
            and "miscalibration" in diagnosis.pathology.lower()
        ):
            model_id = diagnosis.evidence.get("model_id", "")
            if model_id and model_id not in self.config.per_model_directives:
                directive = (
                    "Your self-verification output has been consistently "
                    "miscalibrated in prior rounds. For each finding, "
                    "re-examine the actual code location cited and explicitly "
                    "confirm whether the issue exists before marking "
                    "VERIFIED TRUE or FALSE."
                )
                if len(directive) <= self.config.max_per_model_directive_chars:
                    self.config.per_model_directives[model_id] = directive
                    adjustment = {
                        "parameter": "per_model_directives",
                        "old": "none",
                        "new": f"added directive for {model_id}",
                        "reason": diagnosis.pathology,
                    }
                    self._record_adjustment(adjustment, diagnosis, round_idx)
                    return adjustment
            return None

        if chain_key is None:
            return None  # Unknown pathology — no remediation available

        # --- Execute remediation chain step ---
        chain = self._REMEDIATION_CHAINS.get(chain_key, [])
        if not chain:
            return None

        # Get current chain index (may have been escalated by outcome verification)
        state = self.health_monitor._remediation_state.get(chain_key, {})
        chain_idx = state.get("chain_idx", 0)

        # Level 3: Simplest-sufficient preference — skip historically
        # ineffective early steps.
        if chain_idx == 0:
            recommended_start = self.health_monitor.recommended_chain_start(chain_key)
            if recommended_start > chain_idx:
                self.event_stream.emit(
                    ManagerEvent(
                        event_type=ManagerEventType.STOP_CHECK,
                        model_id="system",
                        round_idx=round_idx,
                        detail=(
                            f"[IMMUNE:LEARN] Skipping chain {chain_key} "
                            f"steps 0-{recommended_start - 1} (historically "
                            f"ineffective). Starting at step {recommended_start}."
                        ),
                        metadata={"chain_skip": True, "chain_key": chain_key,
                                  "skipped_to": recommended_start},
                    )
                )
                chain_idx = recommended_start

        if chain_idx >= len(chain):
            # Chain exhausted — log and feed Level 3 tracker
            self.health_monitor.record_chain_exhaustion(chain_key)
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.STOP_CHECK,
                    model_id="system",
                    round_idx=round_idx,
                    detail=(
                        f"[IMMUNE:EXHAUSTED] Remediation chain for {chain_key} "
                        f"exhausted after {len(chain)} steps. No further "
                        f"autonomous fixes available."
                    ),
                    metadata={"chain_exhausted": True, "pathology": chain_key},
                )
            )
            return None

        step = chain[chain_idx]
        risk = step.get("risk", "AUTO")

        # --- DEFER gate: risky fixes need human approval ---
        if risk == "DEFER":
            deferred = {
                "chain_key": chain_key,
                "chain_idx": chain_idx,
                "step": step,
                "diagnosis": {
                    "detector": diagnosis.detector,
                    "pathology": diagnosis.pathology,
                    "severity": diagnosis.severity,
                    "evidence": diagnosis.evidence,
                },
                "round": round_idx,
                "timestamp": time.time(),
                "status": "PENDING",
                "rationale": (
                    f"Remediation '{step['description']}' classified as DEFER "
                    f"(risk of regression or structural change). Awaiting human "
                    f"review before application."
                ),
            }
            self._deferred_remediations.append(deferred)
            self.event_stream.emit(
                ManagerEvent(
                    event_type=ManagerEventType.STOP_CHECK,
                    model_id="system",
                    round_idx=round_idx,
                    detail=(
                        f"[IMMUNE:DEFER] {step['description']} "
                        f"(chain {chain_key} step {chain_idx}) — "
                        f"requires human approval. Queued for review."
                    ),
                    metadata={"deferred_remediation": True, **deferred},
                )
            )
            return None  # Not applied — queued

        # --- Level 3: P-pass the remediation before applying ---
        # For multi-modular fixes (e.g. add_synthesis_directive → all models),
        # this routes to the extended P-pass with modular + adversarial passes.
        current_metric_val = self._get_current_metric(step["target_metric"])
        affected_model_ids = [m.model_id for m in self.models]
        proceed, rationale = self.health_monitor.p_pass_remediation(
            chain_key, chain_idx, step["description"],
            current_metric_val, step["target_metric"],
            transform_name=step.get("transform", ""),
            affected_models=affected_model_ids,
        )
        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.STOP_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=f"[IMMUNE:P-PASS] {rationale}",
                metadata={"p_pass": True, "proceed": proceed,
                          "chain_key": chain_key, "chain_idx": chain_idx},
            )
        )
        if not proceed:
            # P-pass rejected — escalate to next step
            state = self.health_monitor._remediation_state.get(chain_key, {})
            if state:
                state["chain_idx"] = chain_idx + 1
            else:
                self.health_monitor._remediation_state[chain_key] = {
                    "chain_idx": chain_idx + 1,
                    "applied_round": round_idx,
                    "metric_at_apply": current_metric_val,
                    "target_metric": step["target_metric"],
                    "verification_window": 2,
                }
            return None

        # --- AUTO: safe to apply ---
        # Capture pre-fix metric snapshot for regression detection
        snapshot = {
            "chain_key": chain_key,
            "chain_idx": chain_idx,
            "round": round_idx,
            "metrics": {
                "kappa": self._get_current_metric("kappa"),
                "mu": self._get_current_metric("mu"),
                "finding_count": self._get_current_metric("finding_count"),
                "vocab_growth": self._get_current_metric("vocab_growth"),
            },
        }

        adjustment = self._apply_transform(step["transform"], diagnosis)

        if adjustment:
            self._pre_fix_snapshots.append(snapshot)

            # Record the adjustment
            self._record_adjustment(adjustment, diagnosis, round_idx,
                                    chain_key=chain_key, chain_idx=chain_idx)

            # Set remediation state for outcome verification
            current_metric = self._get_current_metric(step["target_metric"])
            self.health_monitor.set_remediation_state(
                pathology_key=chain_key,
                chain_idx=chain_idx,
                applied_round=round_idx,
                metric_at_apply=current_metric,
                target_metric=step["target_metric"],
            )

        return adjustment

    def approve_deferred_remediation(self, index: int) -> Optional[Dict[str, Any]]:
        """Approve a deferred remediation for application.

        Called by the orchestrator or human operator after reviewing a queued fix.

        Args:
            index: Index into _deferred_remediations list.

        Returns:
            Adjustment dict if applied, None if index invalid or already applied.
        """
        if index < 0 or index >= len(self._deferred_remediations):
            return None
        deferred = self._deferred_remediations[index]
        if deferred["status"] != "PENDING":
            return None

        step = deferred["step"]

        # PR-2 fix: check immune_damping_rounds before applying deferred fix
        current_round = getattr(self, '_process_round_count', 0)
        for adj in self._immune_adjustments:
            if (adj.get("detector") == deferred["diagnosis"]["detector"]
                    and current_round - adj["round"] < self.config.immune_damping_rounds):
                return None  # Damping: too soon to apply this deferred fix

        diag = DetectorDiagnosis(
            detector=deferred["diagnosis"]["detector"],
            pathology=deferred["diagnosis"]["pathology"],
            severity=deferred["diagnosis"]["severity"],
            recommended_action=step["description"],
            evidence=deferred["diagnosis"].get("evidence", {}),
        )
        adjustment = self._apply_transform(step["transform"], diag)
        if adjustment:
            round_idx = deferred["round"]
            self._record_adjustment(
                adjustment, diag, round_idx,
                chain_key=deferred["chain_key"],
                chain_idx=deferred["chain_idx"],
            )
            deferred["status"] = "APPROVED"
            current_metric = self._get_current_metric(step["target_metric"])
            self.health_monitor.set_remediation_state(
                pathology_key=deferred["chain_key"],
                chain_idx=deferred["chain_idx"],
                applied_round=round_idx,
                metric_at_apply=current_metric,
                target_metric=step["target_metric"],
            )
        return adjustment

    def reject_deferred_remediation(self, index: int) -> bool:
        """Reject a deferred remediation.

        Args:
            index: Index into _deferred_remediations list.

        Returns:
            True if rejected, False if index invalid.
        """
        if index < 0 or index >= len(self._deferred_remediations):
            return False
        self._deferred_remediations[index]["status"] = "REJECTED"
        return True

    @property
    def deferred_remediations(self) -> List[Dict[str, Any]]:
        """All deferred remediations, including status."""
        return list(self._deferred_remediations)

    @property
    def pending_remediations(self) -> List[Dict[str, Any]]:
        """Only PENDING deferred remediations awaiting human review."""
        return [d for d in self._deferred_remediations if d["status"] == "PENDING"]

    def _get_current_metric(self, metric_name: str) -> float:
        """Get the current value of a named metric for remediation tracking."""
        hm = self.health_monitor
        if metric_name == "kappa" and hm._kappa_history:
            return hm._kappa_history[-1]
        elif metric_name == "mu" and hm._mu_history:
            return hm._mu_history[-1]
        elif metric_name == "novelty" and hm._novelty_history:
            return hm._novelty_history[-1]
        elif metric_name == "finding_count" and hm._finding_counts:
            return float(hm._finding_counts[-1])
        elif metric_name == "vocab_growth" and hm._vocab_growth_history:
            return hm._vocab_growth_history[-1]
        return 0.0

    def _record_adjustment(
        self,
        adjustment: Dict[str, Any],
        diagnosis: DetectorDiagnosis,
        round_idx: int,
        chain_key: Optional[str] = None,
        chain_idx: Optional[int] = None,
    ) -> None:
        """Record an adjustment in the log and emit an event."""
        record = {
            **adjustment,
            "detector": diagnosis.detector,
            "round": round_idx,
            "severity": diagnosis.severity,
            "timestamp": time.time(),
        }
        if chain_key is not None:
            record["chain_key"] = chain_key
            record["chain_idx"] = chain_idx
        self._immune_adjustments.append(record)
        self._adjustment_log.append(record)

        chain_info = ""
        if chain_key is not None:
            chain = self._REMEDIATION_CHAINS.get(chain_key, [])
            chain_info = f" [chain {chain_key} step {chain_idx}/{len(chain)}]"

        self.event_stream.emit(
            ManagerEvent(
                event_type=ManagerEventType.STOP_CHECK,
                model_id="system",
                round_idx=round_idx,
                detail=(
                    f"[IMMUNE:ADAPT] {adjustment['parameter']}: "
                    f"{adjustment['old']} → {adjustment['new']} "
                    f"(triggered by {diagnosis.detector}){chain_info}"
                ),
                metadata={"immune_adaptation": True, **record},
            )
        )

    # --- Phase E: Dispatch health tracking ---

    def record_dispatch_block(self, model_id: str, round_idx: int) -> None:
        """Record that a model was blocked from dispatch this round."""
        if model_id in self._dispatch_blocks:
            self._dispatch_blocks[model_id].append(round_idx)

    def record_dispatch_success_after_block(self, model_id: str, round_idx: int) -> None:
        """Record that a previously blocked model succeeded (via decomposition)."""
        if model_id in self._dispatch_successes_after_block:
            self._dispatch_successes_after_block[model_id].append(round_idx)

    def record_model_verification_rate(self, model_id: str, rate: float) -> None:
        """Record a model's self-verification rate for this round."""
        if model_id in self._per_model_verification:
            self._per_model_verification[model_id].append(rate)

    @property
    def adjustment_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of immune feedback parameter adjustments."""
        return list(self._adjustment_log)

    @property
    def round_results(self) -> List[RoundResult]:
        """Return all round results."""
        return list(self._round_results)
