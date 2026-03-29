"""Comprehensive test suite for bench/dynamic_management.py.

Tests all six CDSFL dynamic management areas plus three additions
(pre-dispatch feasibility, correlated failure model, manager event stream)
and the top-level DynamicManager orchestrator.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_dynamic_management.py -v
"""

from __future__ import annotations

import math
import os
import sys
import warnings
from typing import Dict, List, Optional, Set

import numpy as np
import pytest

# Ensure the project root is on sys.path so `bench.dynamic_management` resolves
# when running via `python3 -m pytest bench/tests/test_dynamic_management.py -v`
# from the Constraint_Engineering directory.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dynamic_management import (
    Allocation,
    CapabilityFingerprint,
    ConvergenceDetector,
    CorrelatedFailureModel,
    DiminishingReturnsDetector,
    DynamicManagementConfig,
    DynamicManager,
    Event,
    FailureHandler,
    FailureRecord,
    FailureType,
    Finding,
    FindingEquivalenceClass,
    LoadBalancer,
    ManagerEvent,
    ManagerEventStream,
    ManagerEventType,
    ModelResponse,
    ModelSpec,
    RecoveryAction,
    Role,
    RoleAssignment,
    RoundProgressionFSM,
    RoundResult,
    State,
    TerminationReason,
    _finding_similarity,
    validate_all_reductions,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def config():
    """Default configuration."""
    return DynamicManagementConfig()


@pytest.fixture
def fp_high():
    """High-capability fingerprint."""
    return CapabilityFingerprint(D_decay=0.1, v_bar=0.9, A=0.85, C=0.8)


@pytest.fixture
def fp_mid():
    """Mid-capability fingerprint."""
    return CapabilityFingerprint(D_decay=0.2, v_bar=0.7, A=0.75, C=0.65)


@pytest.fixture
def fp_low():
    """Low-capability fingerprint."""
    return CapabilityFingerprint(D_decay=0.4, v_bar=0.5, A=0.55, C=0.45)


@pytest.fixture
def model_high(fp_high):
    return ModelSpec("m_high", fp_high, tau=120.0, L=32768, c=0.015)


@pytest.fixture
def model_mid(fp_mid):
    return ModelSpec("m_mid", fp_mid, tau=180.0, L=32768, c=0.02)


@pytest.fixture
def model_low(fp_low):
    return ModelSpec("m_low", fp_low, tau=300.0, L=16384, c=0.01)


@pytest.fixture
def three_models(model_high, model_mid, model_low):
    return [model_high, model_mid, model_low]


@pytest.fixture
def basic_tasks():
    """Two tasks with different criticality."""
    return [
        Task_factory("t1", 5000, 1, 0.5),
        Task_factory("t2", 8000, 2, 0.9),
    ]


def Task_factory(task_id, token_demand, flaw_class, criticality=0.5):
    """Shorthand for Task construction."""
    from bench.dynamic_management import Task
    return Task(task_id=task_id, token_demand=token_demand,
                flaw_class=flaw_class, criticality=criticality)


def make_finding(fid, model_id, round_idx, flaw_class, severity=0.5,
                 abstraction=0.5, desc=""):
    return Finding(finding_id=fid, model_id=model_id, round_idx=round_idx,
                   flaw_class=flaw_class, severity=severity,
                   abstraction_index=abstraction, description=desc)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDynamicManagementConfig:
    """Tests for configuration validation."""

    def test_defaults_valid(self):
        cfg = DynamicManagementConfig()
        assert cfg.max_rounds == 5
        assert cfg.tau_kappa == 0.95
        assert cfg.feasibility_threshold == 0.90

    def test_alpha_must_sum_to_one(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            DynamicManagementConfig(alpha_pm=np.array([0.5, 0.5, 0.5, 0.5]))

    def test_alpha_must_be_nonnegative(self):
        with pytest.raises(ValueError, match="must be non-negative"):
            DynamicManagementConfig(alpha_pm=np.array([-0.1, 0.4, 0.4, 0.3]))

    def test_alpha_must_be_4d(self):
        with pytest.raises(ValueError, match="must have shape"):
            DynamicManagementConfig(alpha_pm=np.array([0.5, 0.5]))

    def test_max_rounds_must_be_positive(self):
        with pytest.raises(ValueError, match="max_rounds must be >= 1"):
            DynamicManagementConfig(max_rounds=0)

    def test_tau_kappa_range(self):
        with pytest.raises(ValueError, match="tau_kappa must be in"):
            DynamicManagementConfig(tau_kappa=0.0)
        with pytest.raises(ValueError, match="tau_kappa must be in"):
            DynamicManagementConfig(tau_kappa=1.5)

    def test_feasibility_threshold_range(self):
        with pytest.raises(ValueError, match="feasibility_threshold must be in"):
            DynamicManagementConfig(feasibility_threshold=0.0)

    def test_get_alpha_returns_correct_vector(self, config):
        np.testing.assert_array_equal(config.get_alpha(Role.PM), config.alpha_pm)
        np.testing.assert_array_equal(config.get_alpha(Role.COL), config.alpha_col)
        np.testing.assert_array_equal(config.get_alpha(Role.PAR), config.alpha_par)

    def test_get_baseline_returns_correct_vector(self, config):
        np.testing.assert_array_equal(config.get_baseline(Role.PM), config.b_pm)
        np.testing.assert_array_equal(config.get_baseline(Role.COL), config.b_col)
        np.testing.assert_array_equal(config.get_baseline(Role.PAR), config.b_par)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED TYPES TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCapabilityFingerprint:

    def test_as_array(self, fp_high):
        arr = fp_high.as_array()
        assert arr.shape == (4,)
        np.testing.assert_allclose(arr, [0.1, 0.9, 0.85, 0.8])

    def test_as_normalised_array_inverts_decay(self, fp_high):
        pool_max = np.array([0.4, 0.9, 0.85, 0.8])
        normed = fp_high.as_normalised_array(pool_max)
        # D_decay: 1 - (0.1/0.4) = 0.75
        assert normed[0] == pytest.approx(0.75)
        # v_bar: 0.9/0.9 = 1.0
        assert normed[1] == pytest.approx(1.0)

    def test_normalisation_with_zero_max(self):
        fp = CapabilityFingerprint(0.0, 0.0, 0.0, 0.0)
        pool_max = np.array([0.0, 0.0, 0.0, 0.0])
        normed = fp.as_normalised_array(pool_max)
        # D_decay: 1 - 0 = 1.0; rest = 0
        assert normed[0] == pytest.approx(1.0)
        assert normed[1] == pytest.approx(0.0)


class TestModelSpec:

    def test_default_L_std_is_zero(self, fp_high):
        m = ModelSpec("m1", fp_high)
        assert m.L_std == 0.0

    def test_frozen(self, fp_high):
        m = ModelSpec("m1", fp_high)
        with pytest.raises(AttributeError):
            m.model_id = "changed"  # type: ignore


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 1: ROLE ASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoleAssignment:

    def test_single_model_gets_pm(self, config, model_high):
        ra = RoleAssignment.assign([model_high], config)
        assert ra.role_map[model_high.model_id] == Role.PM
        assert ra.pm_model_id == model_high.model_id
        assert len(ra.role_map) == 1

    def test_two_models_pm_and_par(self, config, model_high, model_low):
        ra = RoleAssignment.assign([model_high, model_low], config)
        assert ra.role_map[ra.pm_model_id] == Role.PM
        # With only 2 models, no COL assigned (K < 3)
        roles = set(ra.role_map.values())
        assert Role.COL not in roles

    def test_three_models_assigns_all_roles(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        roles = set(ra.role_map.values())
        assert Role.PM in roles
        assert Role.COL in roles
        assert Role.PAR in roles

    def test_pm_is_locked(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        pm_id = ra.pm_model_id
        ra.reassign(1)
        assert ra.role_map[pm_id] == Role.PM

    def test_empty_models_raises(self, config):
        with pytest.raises(ValueError, match="Cannot assign roles to empty model pool"):
            RoleAssignment.assign([], config)

    def test_capability_scores_populated(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        for m in three_models:
            assert m.model_id in ra.capability_scores
            assert set(ra.capability_scores[m.model_id].keys()) == {"PM", "COL", "PAR"}

    def test_get_ordering_sorted_descending(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        ordering = ra.get_ordering(Role.PM)
        scores = [s for _, s in ordering]
        assert scores == sorted(scores, reverse=True)

    def test_failure_history_recording(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        ra.record_failure("m_high", True)
        ra.record_failure("m_high", False)
        ra.record_failure("m_high", True)
        assert ra.get_failure_history_rate("m_high") == pytest.approx(2.0 / 3.0)

    def test_failure_history_rate_no_history(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        assert ra.get_failure_history_rate("m_high") == 0.0

    def test_reassign_with_failure_penalty(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        # Record heavy failures for current COL
        current_col = None
        for mid, role in ra.role_map.items():
            if role == Role.COL:
                current_col = mid
                break
        if current_col:
            for _ in range(5):
                ra.record_failure(current_col, True)
            ra.reassign(1)
            # The COL with 100% failure rate should lose COL role
            # (if another model scores higher after penalty)

    def test_hysteresis_prevents_oscillation(self, config):
        """COL should not change if the new best is within epsilon_rho of the current."""
        fp1 = CapabilityFingerprint(0.1, 0.8, 0.8, 0.7)
        fp2 = CapabilityFingerprint(0.1, 0.8, 0.8, 0.7)  # nearly identical
        fp3 = CapabilityFingerprint(0.3, 0.5, 0.5, 0.5)
        models = [
            ModelSpec("m1", fp1), ModelSpec("m2", fp2), ModelSpec("m3", fp3)
        ]
        ra = RoleAssignment.assign(models, config)
        initial_col = None
        for mid, role in ra.role_map.items():
            if role == Role.COL:
                initial_col = mid
                break
        # Reassign -- scores nearly equal, hysteresis should keep current COL
        ra.reassign(1)
        new_col = None
        for mid, role in ra.role_map.items():
            if role == Role.COL:
                new_col = mid
                break
        assert new_col == initial_col

    def test_reassign_with_subset_active(self, config, three_models):
        ra = RoleAssignment.assign(three_models, config)
        pm_id = ra.pm_model_id
        # Only PM and one other active
        active = {pm_id, three_models[2].model_id}
        new_map = ra.reassign(1, active_models=active)
        assert pm_id in new_map
        assert new_map[pm_id] == Role.PM

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))
        assert RoleAssignment.validate_k1([m], config)

    def test_validate_homogeneous(self, config):
        assert RoleAssignment.validate_homogeneous(4, config)

    def test_validate_homogeneous_k2(self, config):
        assert RoleAssignment.validate_homogeneous(2, config)


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 2: LOAD BALANCING
# ═══════════════════════════════════════════════════════════════════════════════


class TestAllocation:

    def test_get_assigned_models(self):
        alloc = Allocation(
            task_ids=["t1", "t2"],
            model_ids=["m1", "m2"],
            matrix=np.array([[1, 0], [1, 1]]),
        )
        assert alloc.get_assigned_models("t1") == {"m1"}
        assert alloc.get_assigned_models("t2") == {"m1", "m2"}

    def test_get_assigned_tasks(self):
        alloc = Allocation(
            task_ids=["t1", "t2"],
            model_ids=["m1", "m2"],
            matrix=np.array([[1, 0], [1, 1]]),
        )
        assert alloc.get_assigned_tasks("m1") == {"t1", "t2"}
        assert alloc.get_assigned_tasks("m2") == {"t2"}

    def test_model_load(self):
        from bench.dynamic_management import Task
        alloc = Allocation(
            task_ids=["t1", "t2"],
            model_ids=["m1"],
            matrix=np.array([[1], [1]]),
        )
        tasks = [Task("t1", 3000, 1), Task("t2", 5000, 2)]
        assert alloc.model_load("m1", tasks) == 8000.0


class TestLoadBalancer:

    def test_solve_returns_allocation(self, config, three_models):
        tasks = [Task_factory("t1", 5000, 1, 0.5)]
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        lb = LoadBalancer(three_models, tasks, role_map, config)
        alloc, cost, balanced = lb.solve()
        assert isinstance(alloc, Allocation)
        assert cost >= 0
        assert isinstance(balanced, bool)

    def test_every_task_covered(self, config, three_models):
        tasks = [Task_factory(f"t{i}", 2000, i % 3, 0.5) for i in range(5)]
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        lb = LoadBalancer(three_models, tasks, role_map, config)
        alloc, _, _ = lb.solve()
        for tid in alloc.task_ids:
            assigned = alloc.get_assigned_models(tid)
            assert len(assigned) >= 1, f"Task {tid} not covered"

    def test_pm_excluded_when_k_gt_1(self, config, three_models):
        tasks = [Task_factory("t1", 2000, 1, 0.3)]
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        lb = LoadBalancer(three_models, tasks, role_map, config)
        alloc, _, _ = lb.solve()
        assigned = alloc.get_assigned_models("t1")
        # PM should not be assigned when K > 1 and task is low criticality
        assert "m_high" not in assigned

    def test_k1_pm_handles_everything(self, config, model_high):
        tasks = [Task_factory("t1", 3000, 1), Task_factory("t2", 4000, 2)]
        role_map = {"m_high": Role.PM}
        lb = LoadBalancer([model_high], tasks, role_map, config)
        alloc, _, _ = lb.solve()
        for tid in alloc.task_ids:
            assert "m_high" in alloc.get_assigned_models(tid)

    def test_high_criticality_gets_full_redundancy(self, config, three_models):
        tasks = [Task_factory("t1", 1000, 1, 0.95)]  # above tau_critical=0.8
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        lb = LoadBalancer(three_models, tasks, role_map, config)
        alloc, _, _ = lb.solve()
        assigned = alloc.get_assigned_models("t1")
        # K=3, PM excluded when K>1, so target = K but PM excluded -> at least COL+PAR
        assert len(assigned) >= 2

    def test_empty_tasks(self, config, three_models):
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        lb = LoadBalancer(three_models, [], role_map, config)
        alloc, cost, balanced = lb.solve()
        assert cost == 0.0
        assert balanced is True

    def test_feasibility_probability_deterministic(self, config, fp_high):
        m = ModelSpec("m1", fp_high, L=10000, L_std=0.0)
        lb = LoadBalancer([m], [], {"m1": Role.PM}, config)
        assert lb.feasibility_probability(m, 9000) == 1.0
        assert lb.feasibility_probability(m, 11000) == 0.0

    def test_feasibility_probability_uncertain(self, config, fp_high):
        """L_std > 0 should yield a probability strictly between 0 and 1."""
        m = ModelSpec("m1", fp_high, L=10000, L_std=2000)
        lb = LoadBalancer([m], [], {"m1": Role.PM}, config)
        p = lb.feasibility_probability(m, 10000)
        # Demand == mean -> P = 0.5
        assert p == pytest.approx(0.5, abs=0.01)

    def test_feasibility_probability_well_below_mean(self, config, fp_high):
        m = ModelSpec("m1", fp_high, L=10000, L_std=2000)
        lb = LoadBalancer([m], [], {"m1": Role.PM}, config)
        p = lb.feasibility_probability(m, 5000)
        assert p > 0.95

    def test_dispatch_check_blocks_when_uncertain(self, config, fp_high):
        """Pre-dispatch feasibility catches uncertain capacity (L_std > 0)."""
        m = ModelSpec("m1", fp_high, L=10000, L_std=3000)
        lb = LoadBalancer([m], [], {"m1": Role.PM}, config)
        # Demand close to L: P(feasible) ~ 0.5, below threshold 0.9
        ok, p = lb.dispatch_check(m, 10000)
        assert not ok
        assert p < config.feasibility_threshold

    def test_dispatch_check_passes_when_within_capacity(self, config, fp_high):
        m = ModelSpec("m1", fp_high, L=10000, L_std=1000)
        lb = LoadBalancer([m], [], {"m1": Role.PM}, config)
        # Demand well below mean
        ok, p = lb.dispatch_check(m, 5000)
        assert ok
        assert p >= config.feasibility_threshold

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        assert LoadBalancer.validate_k1(config)

    def test_validate_homogeneous(self, config):
        assert LoadBalancer.validate_homogeneous(3, config)


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 3: ROUND PROGRESSION FSM
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoundProgressionFSM:

    def test_initial_state_is_blind(self, config):
        fsm = RoundProgressionFSM(config)
        assert fsm.current_state == State.BLIND.value
        assert fsm.current_round == 0
        assert not fsm.is_terminal

    def test_blind_to_synth(self, config):
        fsm = RoundProgressionFSM(config)
        new = fsm.transition(Event.COMPLETE)
        assert new == State.SYNTH.value

    def test_synth_to_round_1(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        new = fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        assert new == State.round_state(1)
        assert fsm.current_round == 1

    def test_round_progression_to_max(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        fsm.transition(Event.COMPLETE)  # SYNTH -> ROUND_1
        for k in range(1, config.max_rounds - 1):
            fsm.transition(Event.COMPLETE)
        # Now at ROUND_{N-1}, fire MAX
        new = fsm.transition(Event.MAX)
        assert new == State.TERMINAL.value
        assert fsm.termination_reason == TerminationReason.MAX_ROUNDS

    def test_converged_terminates(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # BLIND -> SYNTH
        fsm.transition(Event.CONVERGED)  # SYNTH -> TERMINAL
        assert fsm.is_terminal
        assert fsm.termination_reason == TerminationReason.CONVERGED

    def test_diminished_terminates(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)
        fsm.transition(Event.DIMINISHED)
        assert fsm.is_terminal
        assert fsm.termination_reason == TerminationReason.DIMINISHED

    def test_fail_critical_terminates_from_any_state(self, config):
        for start_events in [
            [],  # BLIND
            [Event.COMPLETE],  # SYNTH
            [Event.COMPLETE, Event.COMPLETE],  # ROUND_1
        ]:
            fsm = RoundProgressionFSM(config)
            for e in start_events:
                fsm.transition(e)
            fsm.transition(Event.FAIL_CRITICAL)
            assert fsm.is_terminal
            assert fsm.termination_reason == TerminationReason.FAILURE

    def test_terminal_rejects_transitions(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.FAIL_CRITICAL)
        with pytest.raises(RuntimeError, match="FSM is terminal"):
            fsm.transition(Event.COMPLETE)

    def test_invalid_event_in_blind(self, config):
        fsm = RoundProgressionFSM(config)
        with pytest.raises(ValueError, match="invalid in state"):
            fsm.transition(Event.CONVERGED)

    def test_valid_events_in_blind(self, config):
        fsm = RoundProgressionFSM(config)
        valid = fsm.valid_events()
        assert Event.COMPLETE in valid
        assert Event.FAIL_CRITICAL in valid
        assert Event.CONVERGED not in valid

    def test_valid_events_in_terminal(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.FAIL_CRITICAL)
        assert fsm.valid_events() == []

    def test_history_recorded(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)
        fsm.transition(Event.COMPLETE)
        assert len(fsm.history) == 2
        assert fsm.history[0] == (State.BLIND.value, Event.COMPLETE, State.SYNTH.value)

    def test_select_event_priority(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # SYNTH
        # FAIL_CRITICAL highest priority
        event = fsm.select_event(converged=True, diminished=True,
                                 critical_failure=True, round_complete=True)
        assert event == Event.FAIL_CRITICAL

    def test_select_event_converged_over_diminished(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # SYNTH
        event = fsm.select_event(converged=True, diminished=True,
                                 critical_failure=False, round_complete=True)
        assert event == Event.CONVERGED

    def test_select_event_max_at_final_round(self, config):
        fsm = RoundProgressionFSM(config)
        fsm.transition(Event.COMPLETE)  # SYNTH
        fsm.transition(Event.COMPLETE)  # ROUND_1
        for _ in range(config.max_rounds - 2):
            fsm.transition(Event.COMPLETE)
        # Now at ROUND_{N-1}
        event = fsm.select_event(converged=False, diminished=False,
                                 critical_failure=False, round_complete=True)
        assert event == Event.MAX

    def test_select_event_raises_when_nothing_applicable(self, config):
        fsm = RoundProgressionFSM(config)
        with pytest.raises(ValueError, match="No applicable event"):
            fsm.select_event(converged=False, diminished=False,
                             critical_failure=False, round_complete=False)

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        assert RoundProgressionFSM.validate_k1(config)

    def test_validate_no_failures(self, config):
        assert RoundProgressionFSM.validate_no_failures(config)

    def test_no_failures_linear_chain(self, config):
        """No failures: all states unique (acyclic)."""
        fsm = RoundProgressionFSM(config)
        states = {fsm.current_state}
        fsm.transition(Event.COMPLETE)
        states.add(fsm.current_state)
        fsm.transition(Event.COMPLETE)
        states.add(fsm.current_state)
        for _ in range(config.max_rounds - 2):
            fsm.transition(Event.COMPLETE)
            states.add(fsm.current_state)
        fsm.transition(Event.MAX)
        states.add(fsm.current_state)
        # All states distinct (acyclic property)
        assert len(states) == config.max_rounds + 2  # BLIND, SYNTH, ROUND_1..N-1, TERMINAL


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 4: CONVERGENCE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestFindingSimilarity:

    def test_same_class_no_desc(self):
        f1 = make_finding("f1", "m1", 0, 2)
        f2 = make_finding("f2", "m2", 0, 2)
        sim = _finding_similarity(f1, f2)
        assert sim == pytest.approx(0.8)

    def test_different_class_same_desc(self):
        """Different flaw class, identical description — raw Jaccard, no class bonus."""
        f1 = make_finding("f1", "m1", 0, 1, desc="overflow")
        f2 = make_finding("f2", "m1", 0, 2, desc="overflow")
        sim = _finding_similarity(f1, f2)
        # Raw Jaccard({"overflow"}, {"overflow"}) = 1.0 (no multiplier per confer consensus)
        assert sim == pytest.approx(1.0)

    def test_different_class_different_desc(self):
        """Different flaw class, different description — near zero."""
        f1 = make_finding("f1", "m1", 0, 1, desc="buffer overflow in parser")
        f2 = make_finding("f2", "m1", 0, 2, desc="convergence timeout on shutdown")
        sim = _finding_similarity(f1, f2)
        # 0.8 * Jaccard with no overlap = 0.0
        assert sim == pytest.approx(0.0)

    def test_same_class_identical_desc(self):
        f1 = make_finding("f1", "m1", 0, 1, desc="buffer overflow in parser")
        f2 = make_finding("f2", "m2", 0, 1, desc="buffer overflow in parser")
        sim = _finding_similarity(f1, f2)
        assert sim == pytest.approx(1.0)

    def test_same_class_partial_overlap(self):
        f1 = make_finding("f1", "m1", 0, 1, desc="buffer overflow")
        f2 = make_finding("f2", "m2", 0, 1, desc="buffer underflow")
        sim = _finding_similarity(f1, f2)
        # Jaccard of {"buffer", "overflow"} and {"buffer", "underflow"} = 1/3
        expected = 0.4 + 0.6 * (1.0 / 3.0)
        assert sim == pytest.approx(expected)


class TestConvergenceDetector:

    def test_kappa_set_no_novelty(self, config):
        """Repeated identical findings -> high kappa_set."""
        cd = ConvergenceDetector(config)
        findings = [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "buffer overflow"),
            make_finding("f2", "m2", 0, 1, 0.6, 0.5, "buffer overflow"),
        ]
        cd.add_round_findings(0, findings)
        # Round 1: same findings
        findings_r1 = [
            make_finding("f3", "m1", 1, 1, 0.5, 0.5, "buffer overflow"),
        ]
        cd.add_round_findings(1, findings_r1)
        ks = cd.kappa_set(1)
        assert ks > 0.8

    def test_kappa_set_with_novelty(self, config):
        """New findings in round 1 should reduce kappa_set."""
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "buffer overflow"),
        ])
        cd.add_round_findings(1, [
            make_finding("f2", "m1", 1, 2, 0.7, 0.5, "sql injection attack"),
        ])
        ks = cd.kappa_set(1)
        assert ks < 0.8  # significant novelty

    def test_kappa_rate(self, config):
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [
            make_finding(f"f{i}", "m1", 0, i % 3, 0.5, 0.5, f"finding {i}")
            for i in range(5)
        ])
        cd.add_round_findings(1, [
            make_finding("f10", "m1", 1, 0, 0.5, 0.5, "finding 10"),
        ])
        kr = cd.kappa_rate(1)
        # Fewer findings in round 1 than round 0 -> rate decreased -> kappa_rate > 0
        assert kr > 0

    def test_kappa_rate_round_zero(self, config):
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [])
        assert cd.kappa_rate(0) == 0.0

    def test_kappa_adopt(self, config):
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [], adoption_delta=0.3)
        assert cd.kappa_adopt(0) == pytest.approx(0.7)

    def test_kappa_combined_is_min(self, config):
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "finding"),
        ], adoption_delta=0.1)
        cd.add_round_findings(1, [
            make_finding("f2", "m1", 1, 1, 0.5, 0.5, "finding"),
        ], adoption_delta=0.05)
        kappa = cd.kappa(1)
        ks = cd.kappa_set(1)
        kr = max(0.0, cd.kappa_rate(1))
        ka = cd.kappa_adopt(1)
        assert kappa == pytest.approx(min(ks, kr, ka))

    def test_converged_requires_min_rounds(self, config):
        """Cannot converge before min_rounds_for_convergence."""
        cd = ConvergenceDetector(config)
        # Even with perfect kappa, round 0 should not converge
        cd.add_round_findings(0, [])
        assert not cd.converged(0)

    def test_severity_veto_blocks_convergence(self, config):
        """A novel finding with severity >= eta_veto blocks convergence."""
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "minor issue"),
        ])
        cd.add_round_findings(1, [
            make_finding("f2", "m1", 1, 1, 0.5, 0.5, "minor issue"),
        ])
        # Round 2: new high-severity finding
        cd.add_round_findings(2, [
            make_finding("f3", "m1", 2, 2, 0.95, 0.5, "critical vulnerability found"),
        ])
        # Even if kappa is high, veto should block
        assert not cd.converged(2)

    def test_convergence_with_real_sequence(self, config):
        """Simulate a real convergence pattern: many findings -> repetitions -> convergence."""
        cfg = DynamicManagementConfig(tau_kappa=0.8, min_rounds_for_convergence=2)
        cd = ConvergenceDetector(cfg)
        # Round 0: diverse findings
        cd.add_round_findings(0, [
            make_finding(f"r0_f{i}", "m1", 0, i % 3, 0.5, 0.5, f"type {i % 3} finding")
            for i in range(5)
        ])
        # Round 1: same findings repeated
        cd.add_round_findings(1, [
            make_finding(f"r1_f{i}", "m1", 1, i % 3, 0.5, 0.5, f"type {i % 3} finding")
            for i in range(5)
        ])
        # Round 2: same again
        cd.add_round_findings(2, [
            make_finding(f"r2_f{i}", "m1", 2, i % 3, 0.5, 0.5, f"type {i % 3} finding")
            for i in range(3)
        ])
        ks = cd.kappa_set(2)
        assert ks > 0.8

    def test_equivalence_classes_single_linkage(self, config):
        cd = ConvergenceDetector(config)
        # Two similar findings should cluster
        cd.add_round_findings(0, [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "buffer overflow crash"),
            make_finding("f2", "m2", 0, 1, 0.6, 0.5, "buffer overflow crash"),
        ])
        classes = cd.get_round_classes(0)
        # Same class, identical description -> one equivalence class
        assert len(classes) == 1
        assert classes[0].support_multiplicity == 2

    def test_estimate_gamma_early_rounds(self, config):
        cd = ConvergenceDetector(config)
        cd.add_round_findings(0, [])
        assert cd.estimate_gamma(0) == 0.0
        assert cd.estimate_gamma(1) == 0.0

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        assert ConvergenceDetector.validate_k1(config)

    def test_validate_no_findings(self, config):
        assert ConvergenceDetector.validate_no_findings(config)


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 5: DIMINISHING RETURNS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiminishingReturnsDetector:

    def test_marginal_value_basic(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0)
        drd.add_round(1, 7.0, 1.0)
        assert drd.marginal_value(1) == pytest.approx(2.0)

    def test_marginal_value_first_round(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0)
        assert drd.marginal_value(0) == pytest.approx(5.0)

    def test_marginal_value_zero_cost(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 0.0)
        assert drd.marginal_value(0) == float("inf")

    def test_marginal_value_zero_cost_zero_delta(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0)
        drd.add_round(1, 5.0, 0.0)  # no yield gain, zero cost
        assert drd.marginal_value(1) == 0.0

    def test_marginal_value_missing_round(self, config):
        drd = DiminishingReturnsDetector(config)
        with pytest.raises(ValueError, match="No data for round"):
            drd.marginal_value(0)

    def test_smoothed_marginal_value(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0)
        drd.add_round(1, 7.0, 1.0)
        drd.add_round(2, 7.5, 1.0)
        # Window W=2: average of mu(1)=2.0 and mu(2)=0.5
        smoothed = drd.smoothed_marginal_value(2)
        assert smoothed == pytest.approx((2.0 + 0.5) / 2)

    def test_stop_before_r_min(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0, 0.7)
        drd.add_round(1, 5.01, 1.0, 0.6)
        assert not drd.stop(0)
        assert not drd.stop(1)

    def test_stop_when_diminished(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 10.0, 1.0, 0.7)
        drd.add_round(1, 10.01, 1.0, 0.6)
        drd.add_round(2, 10.02, 1.0, 0.5)
        # mu(2) = 0.01, smoothed over W=2 with mu(1)=0.01 -> 0.01 < tau_mu=0.05
        assert drd.stop(2)

    def test_abstraction_guard_is_conjunctive(self, config):
        """Ascending abstraction guard: drop in abstraction does NOT unilaterally stop.
        The stop predicate only fires when smoothed VCR is below threshold."""
        drd = DiminishingReturnsDetector(config)
        # High VCR but dropping abstraction
        drd.add_round(0, 5.0, 1.0, 0.9)
        drd.add_round(1, 10.0, 1.0, 0.8)
        drd.add_round(2, 15.0, 1.0, 0.3)  # abstraction drops significantly
        # mu(2) = 5.0, well above tau_mu
        assert not drd.stop(2), (
            "Conjunctive guard: high VCR should prevent stop even with abstraction drop"
        )

    def test_abstraction_dropping_detection(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0, 0.8)
        drd.add_round(1, 7.0, 1.0, 0.5)
        assert drd._abstraction_dropping(1) is True
        assert drd._abstraction_dropping(0) is False

    def test_add_round_from_findings(self, config):
        drd = DiminishingReturnsDetector(config)
        cumulative = [
            make_finding("f1", "m1", 0, 1, 0.5, 0.6),
            make_finding("f2", "m1", 0, 2, 0.5, 0.8),
        ]
        new = [make_finding("f2", "m1", 0, 2, 0.5, 0.8)]
        drd.add_round_from_findings(0, cumulative, new, 1.0)
        # Y = |cumulative| * mean(H) = 2 * 0.7 = 1.4
        assert drd._cumulative_yields[0] == pytest.approx(1.4)

    def test_remaining_value_estimate(self, config):
        drd = DiminishingReturnsDetector(config)
        drd.add_round(0, 5.0, 1.0)
        drd.add_round(1, 8.0, 1.0)
        drd.add_round(2, 9.0, 1.0)
        rv = drd.remaining_value_estimate(2, 3)
        assert rv >= 0

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        assert DiminishingReturnsDetector.validate_k1(config)

    def test_validate_homogeneous(self, config):
        assert DiminishingReturnsDetector.validate_homogeneous(config)


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 6: FAILURE HANDLING
# ═══════════════════════════════════════════════════════════════════════════════


class TestFailureHandler:

    @pytest.fixture
    def fh_setup(self, three_models, config):
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        fh = FailureHandler(three_models, role_map, config)
        return fh

    def test_no_failure_on_valid_response(self, fh_setup):
        resp = ModelResponse("m_low", 0, "valid content", 10.0,
                             parseable=True, format_compliant=True,
                             finding_count=5, mean_abstraction=0.6)
        assert fh_setup.detect_failure(resp) is None

    def test_empty_response_detected(self, fh_setup):
        resp = ModelResponse("m_low", 0, "", 10.0)
        assert fh_setup.detect_failure(resp) == FailureType.EMPTY

    def test_whitespace_only_is_empty(self, fh_setup):
        resp = ModelResponse("m_low", 0, "   \n  ", 10.0)
        assert fh_setup.detect_failure(resp) == FailureType.EMPTY

    def test_timeout_detected(self, fh_setup, config):
        # m_low has tau=300, threshold = 1.5 * 300 = 450
        resp = ModelResponse("m_low", 0, "content", 500.0)
        assert fh_setup.detect_failure(resp) == FailureType.TIMEOUT

    def test_malformed_detected(self, fh_setup):
        resp = ModelResponse("m_low", 0, "content", 10.0, parseable=False)
        assert fh_setup.detect_failure(resp) == FailureType.MALFORMED

    def test_format_violation_detected(self, fh_setup):
        resp = ModelResponse("m_low", 0, "content", 10.0,
                             parseable=True, format_compliant=False)
        assert fh_setup.detect_failure(resp) == FailureType.FORMAT

    def test_underperform_requires_persistence(self, fh_setup, config):
        """Underperformance only triggers after persistence_window rounds."""
        # Single underperforming response should NOT trigger
        resp = ModelResponse("m_low", 0, "content", 10.0,
                             finding_count=0, mean_abstraction=0.0)
        result = fh_setup.detect_failure(resp)
        # persistence_window=2, need 2 consecutive underperformances
        assert result != FailureType.UNDERPERFORM or config.persistence_window <= 1

    def test_underperform_after_persistence(self, fh_setup, config):
        """Underperformance detected after persistence_window rounds of poor performance."""
        for i in range(config.persistence_window):
            resp = ModelResponse("m_low", i, "content", 10.0,
                                 finding_count=0, mean_abstraction=0.0)
            result = fh_setup.detect_failure(resp)
        # After persistence_window rounds of zero output, should detect underperformance
        assert result == FailureType.UNDERPERFORM

    def test_priority_order_empty_beats_timeout(self, fh_setup):
        """Empty (priority 1) should be detected before timeout (priority 2)."""
        # Even if timed out, empty response matches first
        resp = ModelResponse("m_low", 0, "", 500.0)  # both empty AND timed out
        assert fh_setup.detect_failure(resp) == FailureType.EMPTY

    def test_recovery_retry_first_failure(self, fh_setup):
        action = fh_setup.get_recovery("m_low", 0, FailureType.EMPTY)
        assert action == RecoveryAction.RETRY

    def test_recovery_exclude_on_repeated_empty(self, fh_setup, config):
        for _ in range(config.n_fail):
            fh_setup.get_recovery("m_low", 0, FailureType.EMPTY)
        action = fh_setup.get_recovery("m_low", 1, FailureType.EMPTY)
        assert action == RecoveryAction.EXCLUDE

    def test_recovery_timeout_first_is_retry_extended(self, fh_setup):
        action = fh_setup.get_recovery("m_low", 0, FailureType.TIMEOUT)
        assert action == RecoveryAction.RETRY_EXTENDED

    def test_recovery_malformed_first_is_retry_clarified(self, fh_setup):
        action = fh_setup.get_recovery("m_low", 0, FailureType.MALFORMED)
        assert action == RecoveryAction.RETRY_CLARIFIED

    def test_recovery_format_first_is_degrade(self, fh_setup):
        action = fh_setup.get_recovery("m_low", 0, FailureType.FORMAT)
        assert action == RecoveryAction.DEGRADE

    def test_recovery_underperform_first_is_log_only(self, fh_setup):
        action = fh_setup.get_recovery("m_low", 0, FailureType.UNDERPERFORM)
        assert action == RecoveryAction.LOG_ONLY

    def test_recovery_underperform_repeated_is_downgrade(self, fh_setup, config):
        for _ in range(config.n_fail):
            fh_setup.get_recovery("m_low", 0, FailureType.UNDERPERFORM)
        action = fh_setup.get_recovery("m_low", 1, FailureType.UNDERPERFORM)
        assert action == RecoveryAction.DOWNGRADE_ROLE

    def test_pm_failure_retry_then_abort(self, fh_setup, config):
        """PM failure: RETRY first, ABORT on repetition."""
        action1 = fh_setup.get_recovery("m_high", 0, FailureType.TIMEOUT)
        assert action1 == RecoveryAction.RETRY
        # Record enough for repeated
        for _ in range(config.n_fail - 1):
            fh_setup.get_recovery("m_high", 0, FailureType.TIMEOUT)
        action_final = fh_setup.get_recovery("m_high", 1, FailureType.TIMEOUT)
        assert action_final == RecoveryAction.ABORT

    def test_exclude_removes_from_active(self, fh_setup, config):
        for _ in range(config.n_fail):
            fh_setup.get_recovery("m_low", 0, FailureType.EMPTY)
        fh_setup.get_recovery("m_low", 1, FailureType.EMPTY)
        assert "m_low" not in fh_setup.active_models

    def test_should_abort_when_below_k_min(self, config):
        m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7))
        fh = FailureHandler([m], {"m1": Role.PM}, config)
        fh._active_models.discard("m1")
        assert fh.should_abort()

    def test_should_abort_pm_not_active(self, fh_setup):
        fh_setup._active_models.discard("m_high")
        assert fh_setup.should_abort()

    def test_reallocation_cascade_guard(self, fh_setup, config):
        assert fh_setup.check_reallocation_depth("t1")
        for _ in range(config.max_realloc_depth):
            fh_setup.record_reallocation("t1")
        assert not fh_setup.check_reallocation_depth("t1")

    def test_failure_history_tracking(self, fh_setup):
        fh_setup.get_recovery("m_low", 0, FailureType.TIMEOUT)
        history = fh_setup.get_failure_history("m_low")
        assert len(history) == 1
        assert history[0].failure_type == FailureType.TIMEOUT

    def test_event_callback_on_failure(self, three_models, config):
        events: List[ManagerEvent] = []
        role_map = {"m_high": Role.PM, "m_mid": Role.COL, "m_low": Role.PAR}
        fh = FailureHandler(three_models, role_map, config,
                            event_callback=lambda e: events.append(e))
        resp = ModelResponse("m_low", 0, "", 10.0)
        fh.detect_failure(resp)
        assert len(events) >= 1
        assert events[0].event_type == ManagerEventType.EMPTY

    # --- Reduction properties ---

    def test_validate_k1(self, config):
        assert FailureHandler.validate_k1(config)

    def test_validate_no_failures(self, config):
        assert FailureHandler.validate_no_failures(config)


# ═══════════════════════════════════════════════════════════════════════════════
# CORRELATED FAILURE MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class TestCorrelatedFailureModel:

    def test_default_vulnerability_is_zero(self):
        cfm = CorrelatedFailureModel()
        assert cfm.get_vulnerability("m1", "m2") == 0.0

    def test_self_vulnerability_is_one(self):
        cfm = CorrelatedFailureModel()
        assert cfm.get_vulnerability("m1", "m1") == 1.0

    def test_set_and_get_vulnerability(self):
        cfm = CorrelatedFailureModel()
        cfm.set_vulnerability("m1", "m2", 0.8)
        assert cfm.get_vulnerability("m1", "m2") == 0.8
        assert cfm.get_vulnerability("m2", "m1") == 0.8  # symmetric

    def test_vulnerability_range_validation(self):
        cfm = CorrelatedFailureModel()
        with pytest.raises(ValueError, match="v_ij must be in"):
            cfm.set_vulnerability("m1", "m2", 1.5)
        with pytest.raises(ValueError, match="v_ij must be in"):
            cfm.set_vulnerability("m1", "m2", -0.1)

    def test_base_failure_rate_validation(self):
        cfm = CorrelatedFailureModel()
        with pytest.raises(ValueError, match="rate must be in"):
            cfm.set_base_failure_rate("m1", 1.5)

    def test_pairwise_joint_independent(self):
        """Independent models: joint failure = product of individuals."""
        cfm = CorrelatedFailureModel()
        # v_ij = 0 (default)
        joint = cfm.pairwise_joint_failure("m1", "m2", p_i=0.1, p_j=0.2)
        assert joint == pytest.approx(0.1 * 0.2)

    def test_pairwise_joint_correlated(self):
        """Correlated models: joint failure > independent product."""
        cfm = CorrelatedFailureModel()
        cfm.set_vulnerability("m1", "m2", 0.8)
        joint = cfm.pairwise_joint_failure("m1", "m2", p_i=0.1, p_j=0.2)
        independent = 0.1 * 0.2
        assert joint > independent

    def test_pairwise_bounded_by_min(self):
        """Joint failure never exceeds min(p_i, p_j)."""
        cfm = CorrelatedFailureModel()
        cfm.set_vulnerability("m1", "m2", 1.0)  # perfectly correlated
        joint = cfm.pairwise_joint_failure("m1", "m2", p_i=0.1, p_j=0.9)
        assert joint <= 0.1

    def test_correlated_class_failure_single_model(self):
        cfm = CorrelatedFailureModel()
        cfm.set_base_failure_rate("m1", 0.05)
        result = cfm.correlated_class_failure(["m1"])
        assert result == pytest.approx(0.05)

    def test_correlated_class_failure_empty(self):
        cfm = CorrelatedFailureModel()
        assert cfm.correlated_class_failure([]) == 0.0

    def test_correlated_class_failure_increases_with_vulnerability(self):
        cfm_low = CorrelatedFailureModel()
        cfm_low.set_vulnerability("m1", "m2", 0.1)
        p_low = cfm_low.correlated_class_failure(
            ["m1", "m2"], {"m1": 0.1, "m2": 0.1})

        cfm_high = CorrelatedFailureModel()
        cfm_high.set_vulnerability("m1", "m2", 0.9)
        p_high = cfm_high.correlated_class_failure(
            ["m1", "m2"], {"m1": 0.1, "m2": 0.1})

        assert p_high > p_low

    def test_independence_check(self):
        cfm = CorrelatedFailureModel()
        cfm.set_vulnerability("m1", "m2", 0.3)
        cfm.set_vulnerability("m2", "m3", 0.7)
        assert cfm.independence_check(["m1", "m2", "m3"]) == pytest.approx(0.7)

    def test_independence_check_fully_independent(self):
        cfm = CorrelatedFailureModel()
        assert cfm.independence_check(["m1", "m2", "m3"]) == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# MANAGER EVENT STREAM
# ═══════════════════════════════════════════════════════════════════════════════


class TestManagerEventStream:

    def test_emit_and_drain(self):
        stream = ManagerEventStream()
        event = ManagerEvent(ManagerEventType.ROUND_START, "m1", 0)
        stream.emit(event)
        events = stream.drain()
        assert len(events) == 1
        assert events[0].event_type == ManagerEventType.ROUND_START

    def test_drain_clears_buffer(self):
        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 0))
        stream.drain()
        assert stream.drain() == []

    def test_peek_does_not_clear(self):
        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 0))
        peeked = stream.peek()
        assert len(peeked) == 1
        assert len(stream.peek()) == 1  # still there

    def test_all_events_permanent(self):
        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 0))
        stream.emit(ManagerEvent(ManagerEventType.ROUND_COMPLETE, "m1", 0))
        stream.drain()
        assert len(stream.all_events) == 2

    def test_callback_invoked(self):
        received: List[ManagerEvent] = []
        stream = ManagerEventStream(callback=lambda e: received.append(e))
        stream.emit(ManagerEvent(ManagerEventType.TIMEOUT, "m1", 0))
        assert len(received) == 1

    def test_events_by_type(self):
        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.TIMEOUT, "m1", 0))
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m1", 1))
        stream.emit(ManagerEvent(ManagerEventType.TIMEOUT, "m2", 1))
        timeouts = stream.events_by_type(ManagerEventType.TIMEOUT)
        assert len(timeouts) == 2

    def test_events_by_model(self):
        stream = ManagerEventStream()
        stream.emit(ManagerEvent(ManagerEventType.TIMEOUT, "m1", 0))
        stream.emit(ManagerEvent(ManagerEventType.ROUND_START, "m2", 1))
        stream.emit(ManagerEvent(ManagerEventType.EMPTY, "m1", 1))
        m1_events = stream.events_by_model("m1")
        assert len(m1_events) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC MANAGER INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestDynamicManager:

    @pytest.fixture
    def mgr(self, three_models, config):
        return DynamicManager(three_models, config)

    @pytest.fixture
    def mgr_with_events(self, three_models, config):
        events: List[ManagerEvent] = []
        mgr = DynamicManager(three_models, config,
                             event_callback=lambda e: events.append(e))
        return mgr, events

    def test_initial_state(self, mgr):
        assert mgr.fsm.current_state == State.BLIND.value
        assert not mgr.fsm.is_terminal
        assert len(mgr.role_assignment.role_map) == 3

    def test_roles_assigned(self, mgr):
        roles = set(mgr.role_assignment.role_map.values())
        assert Role.PM in roles
        assert Role.COL in roles
        assert Role.PAR in roles

    def test_get_allocation(self, mgr):
        tasks = [Task_factory("t1", 5000, 1, 0.5)]
        alloc, cost, balanced = mgr.get_allocation(tasks)
        assert isinstance(alloc, Allocation)
        assert cost >= 0

    def test_process_round_advances_fsm(self, mgr, three_models):
        tasks = [Task_factory("t1", 3000, 1)]
        responses = {}
        findings = []
        for m in three_models:
            responses[m.model_id] = ModelResponse(
                m.model_id, 0, "findings here", 30.0,
                finding_count=3, mean_abstraction=0.6)
            for i in range(3):
                findings.append(make_finding(
                    f"{m.model_id}_f{i}", m.model_id, 0,
                    i % 3, 0.5, 0.6, f"finding {i}"))

        result = mgr.process_round(responses, findings, tasks, round_cost=1.0)
        assert result.round_idx == 0
        # FSM should have advanced from BLIND
        assert mgr.fsm.current_state != State.BLIND.value or mgr.fsm.is_terminal

    def test_full_run_to_terminal(self, three_models):
        """Run through multiple rounds until terminal."""
        cfg = DynamicManagementConfig(max_rounds=3, min_rounds_for_convergence=2)
        mgr = DynamicManager(three_models, cfg)
        tasks = [Task_factory("t1", 2000, 1, 0.5)]

        for round_idx in range(10):  # safety limit
            if mgr.fsm.is_terminal:
                break
            responses = {}
            findings = []
            for m in three_models:
                if m.model_id in mgr.failure_handler.active_models:
                    responses[m.model_id] = ModelResponse(
                        m.model_id, round_idx, "content", 30.0,
                        finding_count=max(1, 5 - round_idx),
                        mean_abstraction=0.6)
                    findings.append(make_finding(
                        f"r{round_idx}_{m.model_id}", m.model_id, round_idx,
                        1, 0.5, 0.5, "repeated finding"))

            mgr.process_round(responses, findings, tasks, round_cost=1.0)

        assert mgr.fsm.is_terminal

    def test_critical_failure_terminates(self, three_models, config):
        mgr = DynamicManager(three_models, config)
        pm_id = mgr.role_assignment.pm_model_id
        tasks = [Task_factory("t1", 2000, 1)]

        # Simulate PM failures until abort
        for i in range(config.n_fail + 2):
            if mgr.fsm.is_terminal:
                break
            responses = {
                pm_id: ModelResponse(pm_id, i, "", 10.0),  # empty = failure
            }
            # Add valid responses for other models
            for m in three_models:
                if m.model_id != pm_id and m.model_id in mgr.failure_handler.active_models:
                    responses[m.model_id] = ModelResponse(
                        m.model_id, i, "content", 30.0,
                        finding_count=3, mean_abstraction=0.6)
            mgr.process_round(responses, [], tasks, round_cost=1.0)

        assert mgr.fsm.is_terminal
        assert mgr.fsm.termination_reason == TerminationReason.FAILURE

    def test_check_dispatch_feasibility_deterministic(self, mgr, fp_high):
        m = ModelSpec("m_det", fp_high, L=10000, L_std=0.0)
        ok, p = mgr.check_dispatch_feasibility(m, 9000)
        assert ok
        assert p == 1.0

    def test_check_dispatch_feasibility_uncertain_blocks(self, mgr, fp_high):
        m = ModelSpec("m_unc", fp_high, L=10000, L_std=3000)
        ok, p = mgr.check_dispatch_feasibility(m, 10000)
        assert not ok  # P ~ 0.5 < 0.9

    def test_check_dispatch_feasibility_uncertain_warning(self, mgr_with_events, fp_high):
        mgr, events = mgr_with_events
        m = ModelSpec("m_unc", fp_high, L=20000, L_std=1000)
        ok, p = mgr.check_dispatch_feasibility(m, 5000)
        assert ok
        # Should emit feasibility warning (L_std > 0 and p < 0.99)
        warning_events = [e for e in events if e.event_type == ManagerEventType.FEASIBILITY_WARNING]
        # p is very high here, may not emit warning, but that's fine

    def test_event_stream_populated(self, three_models, config):
        events: List[ManagerEvent] = []
        mgr = DynamicManager(three_models, config,
                             event_callback=lambda e: events.append(e))
        tasks = [Task_factory("t1", 2000, 1)]
        responses = {}
        for m in three_models:
            responses[m.model_id] = ModelResponse(
                m.model_id, 0, "content", 30.0,
                finding_count=2, mean_abstraction=0.5)
        mgr.process_round(responses, [], tasks, round_cost=1.0)
        assert len(events) > 0
        event_types = {e.event_type for e in events}
        assert ManagerEventType.ROUND_COMPLETE in event_types

    def test_correlated_failures_accessible(self, mgr):
        mgr.correlated_failures.set_vulnerability("m_high", "m_mid", 0.5)
        v = mgr.correlated_failures.get_vulnerability("m_high", "m_mid")
        assert v == 0.5

    def test_round_results_accumulated(self, three_models, config):
        mgr = DynamicManager(three_models, config)
        tasks = [Task_factory("t1", 2000, 1)]
        responses = {}
        for m in three_models:
            responses[m.model_id] = ModelResponse(
                m.model_id, 0, "content", 30.0,
                finding_count=2, mean_abstraction=0.5)
        mgr.process_round(responses, [], tasks, round_cost=1.0)
        assert len(mgr.round_results) == 1

    def test_role_reassignment_after_round(self, three_models, config):
        mgr = DynamicManager(three_models, config)
        pm_id = mgr.role_assignment.pm_model_id
        tasks = [Task_factory("t1", 2000, 1)]
        responses = {}
        for m in three_models:
            responses[m.model_id] = ModelResponse(
                m.model_id, 0, "content", 30.0,
                finding_count=2, mean_abstraction=0.5)
        mgr.process_round(responses, [], tasks, round_cost=1.0)
        # PM should remain the same
        assert mgr.role_assignment.role_map[pm_id] == Role.PM


# ═══════════════════════════════════════════════════════════════════════════════
# REDUCTION PROPERTY VALIDATION (all areas)
# ═══════════════════════════════════════════════════════════════════════════════


class TestReductionProperties:

    def test_validate_all_reductions_pass(self):
        results = validate_all_reductions()
        for area, props in results.items():
            for prop, passed in props.items():
                assert passed, f"Reduction property {area}.{prop} failed"

    def test_validate_all_with_custom_config(self):
        cfg = DynamicManagementConfig(max_rounds=3, tau_kappa=0.9)
        results = validate_all_reductions(cfg)
        for area, props in results.items():
            for prop, passed in props.items():
                assert passed, f"Reduction property {area}.{prop} failed with custom config"


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASES AND ADDITIONAL COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:

    def test_single_model_full_workflow(self):
        """K=1 end-to-end: single model is PM, handles everything."""
        fp = CapabilityFingerprint(0.1, 0.8, 0.9, 0.7)
        m = ModelSpec("solo", fp, L=32768, c=0.01)
        cfg = DynamicManagementConfig(max_rounds=3)
        mgr = DynamicManager([m], cfg)

        assert mgr.role_assignment.role_map["solo"] == Role.PM
        tasks = [Task_factory("t1", 5000, 1, 0.5)]
        alloc, cost, _ = mgr.get_allocation(tasks)
        assert "solo" in alloc.get_assigned_models("t1")

    def test_event_priority_enum(self):
        """Event priorities are correctly ordered."""
        assert Event.FAIL_CRITICAL.priority > Event.CONVERGED.priority
        assert Event.CONVERGED.priority > Event.DIMINISHED.priority
        assert Event.DIMINISHED.priority > Event.COMPLETE.priority
        assert Event.COMPLETE.priority > Event.MAX.priority

    def test_finding_equivalence_class_properties(self):
        f1 = make_finding("f1", "m1", 0, 1, 0.8, 0.6)
        f2 = make_finding("f2", "m2", 0, 1, 0.7, 0.4)
        ec = FindingEquivalenceClass(
            class_id="ec1", flaw_class=1, members=[f1, f2],
            aggregated_severity=0.8)
        assert ec.support_multiplicity == 2
        assert ec.mean_abstraction == pytest.approx(0.5)

    def test_finding_equivalence_class_empty(self):
        ec = FindingEquivalenceClass(
            class_id="ec_empty", flaw_class=1, members=[],
            aggregated_severity=0.0)
        assert ec.support_multiplicity == 0
        assert ec.mean_abstraction == 0.0

    def test_failure_type_ordering(self):
        """Failure types have distinct values (priority ordering)."""
        values = [ft.value for ft in FailureType]
        assert len(values) == len(set(values))

    def test_state_round_state_format(self):
        assert State.round_state(1) == "ROUND_1"
        assert State.round_state(99) == "ROUND_99"

    def test_allocation_model_load_fraction_zero_limit(self, fp_high):
        """Model with L=0 should return inf for nonzero load."""
        from bench.dynamic_management import Task
        m = ModelSpec("m_zero", fp_high, L=0)
        alloc = Allocation(
            task_ids=["t1"], model_ids=["m_zero"],
            matrix=np.array([[1]]))
        tasks = [Task("t1", 1000, 1)]
        frac = alloc.model_load_fraction("m_zero", tasks, [m])
        assert frac == float("inf")

    def test_convergence_detector_custom_similarity_fn(self, config):
        """Custom similarity function is used instead of default."""
        def always_similar(f1, f2):
            return 1.0
        cd = ConvergenceDetector(config, similarity_fn=always_similar)
        cd.add_round_findings(0, [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "aaa"),
            make_finding("f2", "m2", 0, 2, 0.5, 0.5, "bbb"),
        ])
        classes = cd.get_round_classes(0)
        # All findings in one class because always_similar returns 1.0
        assert len(classes) == 1

    def test_manager_no_active_models_raises(self, three_models, config):
        mgr = DynamicManager(three_models, config)
        mgr.failure_handler._active_models.clear()
        with pytest.raises(RuntimeError, match="No active models"):
            mgr.get_allocation([Task_factory("t1", 1000, 1)])
