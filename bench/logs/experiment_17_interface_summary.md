# Experiment 17 — Immune Subsystem Dependency Interface Summary

**Purpose:** Reference for all models reviewing `dynamic_management.py` under Experiment 17.
The analytical boundary is the immune subsystem. This document lists everything the immune
subsystem touches outside that boundary.

---

## 1. External Functions Called by Immune Subsystem

### From FailureHandler (within boundary, calls config)
| Function | Signature | Contract |
|----------|-----------|----------|
| `config.get_baseline(role)` | `(Role) → NDArray` | Returns expected performance baseline for a role |
| `event_callback(event)` | `(ManagerEvent) → None` | Emits event to event stream for logging |

### From process_round() → Outside Boundary
| Function | Signature | Contract |
|----------|-----------|----------|
| `role_assignment.record_failure(model_id, failed)` | `(str, bool) → None` | Records model success/failure for role scoring |
| `convergence_detector.add_round_findings(r, findings, dur, delta)` | `(int, List[Finding], float, float) → None` | Feeds findings into convergence tracking |
| `convergence_detector.kappa(r)` | `(int) → float` | Returns convergence stability metric [0,1] |
| `convergence_detector.converged(r)` | `(int) → bool` | True if kappa >= tau_kappa and round >= min_rounds |
| `convergence_detector.get_cumulative_classes(r)` | `(int) → Set` | Returns all flaw classes seen up to round r |
| `convergence_detector._novel_classes(r)` | `(int) → Set` | Returns flaw classes new in round r |
| `diminishing_returns.add_round_from_findings(r, cum, new, cost)` | `(int, List, List, float) → None` | Feeds per-round data into DR detector |
| `diminishing_returns.add_model_round(mid, r, findings, cost)` | `(str, int, List, float) → None` | Feeds per-model data into DR detector |
| `diminishing_returns.marginal_value(r)` | `(int) → float` | Returns mu(r) = cognitive yield per cost unit |
| `diminishing_returns.stop(r)` | `(int) → bool` | Returns True if exhaustion AND abstraction_ok |
| `diminishing_returns.novelty_rate(r)` | `(int) → float` | Fraction of findings that are novel |
| `diminishing_returns.vocab_growth_rate(r)` | `(int) → float` | Fractional increase in unique finding terms |
| `fsm.select_event(conv, dim, crit, complete)` | `(bool, bool, bool, bool) → str` | FSM event selection from round outcomes |
| `fsm.transition(event)` | `(str) → str` | FSM state transition, returns new state |
| `fsm.is_terminal` | `→ bool` | True if FSM in terminal state |
| `self.update_fingerprints(r, findings, responses)` | `(int, List, Dict) → None` | Updates capability fingerprints from round data |

### From apply_diagnosis() → health_monitor
| Function | Signature | Contract |
|----------|-----------|----------|
| `health_monitor.recommended_chain_start(key)` | `(str) → int` | Returns recommended starting step in remediation chain |
| `health_monitor.record_chain_exhaustion(key)` | `(str) → None` | Records that all steps in a chain were exhausted |
| `health_monitor.p_pass_remediation(key, idx, desc, metric, target, name, models)` | `(...) → Tuple[bool, str]` | P-pass gate: returns (approved, reason) |
| `health_monitor.set_remediation_state(key, idx, round, metric, target)` | `(...) → None` | Records current remediation progress |

---

## 2. Shared Mutable State

| State | Type | Location | Read/Write | Purpose |
|-------|------|----------|------------|---------|
| `self.capability_scores` | `Dict[str, Dict[str, float]]` | DynamicManager | R/W | Per-model capability scores by role |
| `self.config.tau_sim` | `float` | DynamicManagementConfig | W | Immune can lower convergence threshold |
| `self.config.tau_vocab_growth` | `float` | DynamicManagementConfig | W | Immune can lower vocab saturation threshold |
| `self.config.per_model_directives` | `Dict[str, str]` | DynamicManagementConfig | R/W | Immune can inject per-model prompt text |
| `self.config.pre_decompose_models` | `Set[str]` | DynamicManagementConfig | R/W | Immune can add models to decomposition set |
| `self.models` | `List[ModelSpec]` | DynamicManager | R | Model pool (read for directive injection) |
| `self._immune_adjustments` | `List[Dict]` | DynamicManager | W | Log of all immune adjustments made |
| `self._deferred_remediations` | `List[Dict]` | DynamicManager | W | Remediations deferred by P-pass gate |
| `self._pre_fix_snapshots` | `List[Dict]` | DynamicManager | W | Pre-adjustment config snapshots |
| `self._round_results` | `List[RoundResult]` | DynamicManager | W | Accumulated round results |

---

## 3. Config Parameters Affecting Immune Behaviour

| Parameter | Default | Line | Effect |
|-----------|---------|------|--------|
| `immune_feedback_enabled` | `True` | 166 | Master switch for autonomous adjustment |
| `immune_damping_rounds` | `2` | 168 | Minimum rounds between adjustments to same parameter |
| `max_per_model_directive_chars` | `500` | 170 | Length bound for injected directives |
| `timeout_multiplier` | `2.0` | 149 | Failure detection: response time threshold |
| `theta_under` | `0.3` | 150 | Underperformance threshold |
| `n_fail` | `3` | 151 | Consecutive failures before escalation |
| `persistence_window` | `3` | 152 | Window for persistent failure detection |
| `eta_underperform` | `0.5` | 153 | Underperformance severity threshold |
| `k_min` | `2` | 156 | Minimum active models before abort |

---

## 4. Dataclasses/Types Used Across Boundary

| Type | Line | Role in Immune Subsystem |
|------|------|--------------------------|
| `ModelResponse` | 2418 | Input: model output data |
| `Finding` | 347 | Input: structured finding with severity, flaw_class, abstraction_index |
| `Task` | 332 | Input: task definitions |
| `RoundResult` | 4785 | Output: includes recovery_actions, active_models, state |
| `FailureType` (enum) | 2381 | EMPTY, TIMEOUT, MALFORMED, FORMAT, UNDERPERFORM |
| `RecoveryAction` (enum) | 2391 | RETRY, RETRY_EXTENDED, REALLOCATE, EXCLUDE, ABORT, LOG_ONLY |
| `ManagerEvent` | 4697 | Emitted for logging/monitoring |
| `ManagerEventType` (enum) | 4668 | Event type classification |
| `CapabilityFingerprint` | 271 | (D_decay, v_bar, A, C) per model |
| `ModelSpec` | 309 | Model configuration including fingerprint |
| `Role` (enum) | 262 | COL, PM, PARTICIPANT |
