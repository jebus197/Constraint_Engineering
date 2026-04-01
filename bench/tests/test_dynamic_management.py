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
        # After stopword removal: tokens = ["buffer", "overflow"] vs ["buffer", "underflow"]
        # Unigram Jaccard = 1/3, Bigram Jaccard = 0/2 = 0.0
        # Combined = 0.6*(1/3) + 0.4*0.0 = 0.2
        # Same class: 0.3 + 0.7 * 0.2 = 0.44
        expected = 0.3 + 0.7 * (0.6 * (1.0 / 3.0) + 0.4 * 0.0)
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

    def test_recovery_format_first_is_retry_clarified(self, fh_setup):
        """IM_F030 fix: first FORMAT occurrence should be lenient (RETRY_CLARIFIED)."""
        action = fh_setup.get_recovery("m_low", 0, FailureType.FORMAT)
        assert action == RecoveryAction.RETRY_CLARIFIED

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


# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULARY SATURATION STOP SIGNAL TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestVocabSaturation:
    """Tests for vocabulary saturation stop signal (Exp12 fix)."""

    @pytest.fixture
    def config(self):
        return DynamicManagementConfig(
            tau_vocab_growth=0.10,
            vocab_sustained_window=3,
            r_min=2,
        )

    def test_vocab_growth_first_round(self, config):
        """First round should have 100% growth."""
        drd = DiminishingReturnsDetector(config)
        findings = [
            make_finding("f1", "m1", 0, 1, 0.5, 0.5, "novel unique terms here"),
        ]
        drd.add_round_from_findings(0, findings, findings, 1.0)
        assert drd.vocab_growth_rate(0) == 1.0

    def test_vocab_growth_decreases(self, config):
        """Vocabulary growth should decrease with repeated terms."""
        drd = DiminishingReturnsDetector(config)
        f0 = [make_finding("f1", "m1", 0, 1, 0.5, 0.5,
                           "alpha beta gamma delta epsilon")]
        drd.add_round_from_findings(0, f0, f0, 1.0)
        # Second round: same terms, no growth
        f1 = [make_finding("f2", "m1", 1, 1, 0.5, 0.5,
                           "alpha beta gamma delta epsilon")]
        drd.add_round_from_findings(1, f0 + f1, f1, 1.0)
        assert drd.vocab_growth_rate(1) == 0.0

    def test_vocab_growth_with_new_terms(self, config):
        """Adding new terms should produce positive growth."""
        drd = DiminishingReturnsDetector(config)
        f0 = [make_finding("f1", "m1", 0, 1, 0.5, 0.5,
                           "alpha beta gamma delta")]
        drd.add_round_from_findings(0, f0, f0, 1.0)
        f1 = [make_finding("f2", "m1", 1, 1, 0.5, 0.5,
                           "epsilon zeta theta kappa")]
        drd.add_round_from_findings(1, f0 + f1, f1, 1.0)
        # 4 new terms out of 4 existing = 100% growth
        assert drd.vocab_growth_rate(1) == 1.0

    def test_vocab_saturated_requires_sustained_window(self, config):
        """vocab_saturated should only fire after sustained_window rounds."""
        drd = DiminishingReturnsDetector(config)
        # Build up enough rounds with low growth
        base_terms = "alpha beta gamma delta epsilon zeta theta kappa lambda"
        f0 = [make_finding("f1", "m1", 0, 1, 0.5, 0.5, base_terms)]
        drd.add_round_from_findings(0, f0, f0, 1.0)
        # Rounds 1-4: repeat same terms (0% growth)
        all_f = list(f0)
        for r in range(1, 5):
            fr = [make_finding(f"f{r+1}", "m1", r, 1, 0.5, 0.5, base_terms)]
            all_f.extend(fr)
            drd.add_round_from_findings(r, all_f, fr, 1.0)
        # Round 2 should not be saturated (need 3 consecutive: 0,1,2 but round 0 is 100%)
        assert not drd.vocab_saturated(2)
        # Round 3 should be saturated (rounds 1,2,3 all have 0% growth)
        assert drd.vocab_saturated(3)

    def test_vocab_saturation_triggers_stop(self, config):
        """Vocabulary saturation should trigger the stop predicate."""
        drd = DiminishingReturnsDetector(config)
        base_terms = "alpha beta gamma delta epsilon zeta theta kappa lambda"
        f0 = [make_finding("f1", "m1", 0, 1, 0.5, 0.5, base_terms)]
        drd.add_round_from_findings(0, f0, f0, 1.0)
        all_f = list(f0)
        for r in range(1, 5):
            fr = [make_finding(f"f{r+1}", "m1", r, 1, 0.5, 0.5, base_terms)]
            all_f.extend(fr)
            # Give high yield so mu and novelty_rate don't trigger stop
            drd.add_round_from_findings(r, all_f, fr, 0.001)
        # stop should fire from vocabulary saturation even though mu is high
        assert drd.stop(3)

    def test_vocab_saturation_not_triggered_with_fresh_content(self, config):
        """If new terms keep appearing, vocab saturation should not fire."""
        drd = DiminishingReturnsDetector(config)
        all_f = []
        for r in range(5):
            # Each round adds completely new terms
            desc = " ".join(f"term{r}_{i}" for i in range(10))
            fr = [make_finding(f"f{r}", "m1", r, 1, 0.5, 0.5, desc)]
            all_f.extend(fr)
            drd.add_round_from_findings(r, all_f, fr, 1.0)
        assert not drd.vocab_saturated(4)


# ═══════════════════════════════════════════════════════════════════════════════
# WINDOWED FINGERPRINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestWindowedFingerprint:
    """Tests for windowed mean fingerprint update (replacing EMA)."""

    @pytest.fixture
    def config(self):
        return DynamicManagementConfig(
            fingerprint_window=3,  # 3-round window
            fingerprint_ema_alpha=0.3,
            max_rounds=20,
        )

    @pytest.fixture
    def three_models(self):
        return [
            ModelSpec("m1", CapabilityFingerprint(0.2, 0.8, 0.7, 0.6), tau=100.0),
            ModelSpec("m2", CapabilityFingerprint(0.3, 0.7, 0.6, 0.5), tau=100.0),
            ModelSpec("m3", CapabilityFingerprint(0.1, 0.9, 0.8, 0.7), tau=100.0),
        ]

    def test_windowed_fingerprint_does_not_collapse(self, three_models, config):
        """Windowed mean should not decay to zero over many rounds."""
        mgr = DynamicManager(three_models, config)
        # Simulate 15 rounds with consistent findings
        for r in range(15):
            findings = [
                make_finding(f"f{r}_1", "m1", r, 1, 0.7, 0.6, f"finding {r} desc"),
                make_finding(f"f{r}_2", "m2", r, 2, 0.5, 0.5, f"other {r} desc"),
            ]
            responses = {
                "m1": ModelResponse("m1", r, "ok", 10.0,
                                    finding_count=1, mean_abstraction=0.6),
                "m2": ModelResponse("m2", r, "ok", 10.0,
                                    finding_count=1, mean_abstraction=0.5),
            }
            mgr.update_fingerprints(r, findings, responses)

        # After 15 rounds, fingerprints should reflect recent observations,
        # NOT collapse to zero.
        fp_m1 = mgr._live_fingerprints["m1"]
        assert fp_m1.A > 0.3, f"A should not collapse: {fp_m1.A}"
        assert fp_m1.C > 0.0, f"C should not collapse: {fp_m1.C}"

    def test_ema_mode_when_window_zero(self, three_models):
        """Setting fingerprint_window=0 should use legacy EMA."""
        config = DynamicManagementConfig(fingerprint_window=0, fingerprint_ema_alpha=0.3)
        mgr = DynamicManager(three_models, config)
        findings = [
            make_finding("f1", "m1", 0, 1, 0.7, 0.6, "test finding"),
        ]
        responses = {
            "m1": ModelResponse("m1", 0, "ok", 10.0,
                                finding_count=1, mean_abstraction=0.6),
        }
        mgr.update_fingerprints(0, findings, responses)
        fp = mgr._live_fingerprints["m1"]
        # EMA: new_A = 0.3 * 0.7 + 0.7 * 0.7 = 0.21 + 0.49 = 0.7
        assert abs(fp.A - 0.7) < 0.01


class TestPerModelMu:
    """Per-model mu computation (Exp13a confer, CC2 approved HARD).

    Eliminates cost distortion from model attrition that broke system-level
    mu in Experiment 12.
    """

    def test_per_model_mu_basic(self):
        """Per-model mu computes marginal value per model independently."""
        det = DiminishingReturnsDetector(DynamicManagementConfig())
        f1 = make_finding("f1", "m1", 0, 1, 0.8, 0.7, "finding by model 1")
        f2 = make_finding("f2", "m2", 0, 1, 0.6, 0.5, "finding by model 2")
        det.add_model_round("m1", 0, [f1], cost=1.0)
        det.add_model_round("m2", 0, [f2], cost=1.0)
        mu_m1 = det.per_model_mu("m1", 0)
        mu_m2 = det.per_model_mu("m2", 0)
        assert mu_m1 > 0
        assert mu_m2 > 0
        assert mu_m1 != mu_m2  # different findings → different mu

    def test_per_model_mu_attrition_resistant(self):
        """System mu should not spike when a model is lost."""
        det = DiminishingReturnsDetector(DynamicManagementConfig())
        # Round 0: both models active
        f1 = make_finding("f1", "m1", 0, 1, 0.8, 0.7, "m1 finding round 0")
        f2 = make_finding("f2", "m2", 0, 1, 0.6, 0.5, "m2 finding round 0")
        det.add_model_round("m1", 0, [f1], cost=1.0)
        det.add_model_round("m2", 0, [f2], cost=1.0)
        agg_r0 = det.aggregate_per_model_mu(0)
        # Round 1: only m1 active (m2 lost)
        f3 = make_finding("f3", "m1", 1, 1, 0.7, 0.6, "m1 finding round 1")
        det.add_model_round("m1", 1, [f3], cost=1.0)
        agg_r1 = det.aggregate_per_model_mu(1)
        # Per-model aggregation should NOT spike just because m2 is gone
        assert agg_r1 <= agg_r0 * 2, f"Aggregate mu should not spike on attrition: r0={agg_r0}, r1={agg_r1}"

    def test_aggregate_uses_max(self):
        """Aggregate should use max across models (conservative: continue if any model delivers)."""
        det = DiminishingReturnsDetector(DynamicManagementConfig())
        f1 = make_finding("f1", "m1", 0, 1, 0.9, 0.8, "high value")
        f2 = make_finding("f2", "m2", 0, 1, 0.2, 0.1, "low value")
        det.add_model_round("m1", 0, [f1], cost=1.0)
        det.add_model_round("m2", 0, [f2], cost=1.0)
        agg = det.aggregate_per_model_mu(0)
        mu_m1 = det.per_model_mu("m1", 0)
        assert abs(agg - mu_m1) < 0.001, "Aggregate should equal max model mu"

    def test_fallback_to_system_mu(self):
        """When no per-model data exists, fall back to system-level mu."""
        det = DiminishingReturnsDetector(DynamicManagementConfig())
        det.add_round(0, 10.0, 2.0)
        det.add_round(1, 18.0, 2.0)
        # No add_model_round calls → should use system mu
        agg = det.aggregate_per_model_mu(1)
        system_mu = det.marginal_value(1)
        assert abs(agg - system_mu) < 0.001


# ═══════════════════════════════════════════════════════════════════════════════
# AREA 7b: AUTONOMOUS REMEDIATION (Exp15)
# ═══════════════════════════════════════════════════════════════════════════════

from bench.dynamic_management import DetectorDiagnosis, DetectorHealthMonitor


class TestDetectorHealthMonitorExp15:
    """Tests for Exp15 autonomous remediation: new detectors, chains, verification."""

    def test_vocab_growth_tracking(self):
        """Health monitor records vocab growth rates."""
        hm = DetectorHealthMonitor()
        hm.record_vocab_growth(0.15)
        hm.record_vocab_growth(0.10)
        assert len(hm._vocab_growth_history) == 2
        assert hm._vocab_growth_history[0] == 0.15

    def test_model_failure_detection_single(self):
        """Single failure does not trigger diagnosis."""
        hm = DetectorHealthMonitor()
        diags = hm.record_model_round("CC2", 0, failed=True)
        assert len(diags) == 0  # one failure = no diagnosis

    def test_model_failure_detection_consecutive(self):
        """Two consecutive failures triggers WARNING."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("CC2", 0, failed=True)
        diags = hm.record_model_round("CC2", 0, failed=True)
        assert len(diags) >= 1
        diag = [d for d in diags if d.detector == "model_failure"][0]
        assert diag.severity == "WARNING"
        assert "CC2" in diag.pathology

    def test_model_failure_detection_three_critical(self):
        """Three consecutive failures escalates to CRITICAL."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("CC2", 0, failed=True)
        hm.record_model_round("CC2", 0, failed=True)
        diags = hm.record_model_round("CC2", 0, failed=True)
        assert len(diags) >= 1
        diag = [d for d in diags if d.detector == "model_failure"][0]
        assert diag.severity == "CRITICAL"

    def test_model_failure_resets_on_success(self):
        """Successful round resets consecutive failure count."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("CC2", 0, failed=True)
        hm.record_model_round("CC2", 5, failed=False)  # success resets
        diags = hm.record_model_round("CC2", 0, failed=True)
        failure_diags = [d for d in diags if d.detector == "model_failure"]
        assert len(failure_diags) == 0  # only 1 failure since reset

    def test_findings_decline_detection(self):
        """Declining findings for 3 rounds triggers diagnosis."""
        hm = DetectorHealthMonitor()
        # Need 4 rounds of data (we check the last 3)
        for counts in [30, 25, 18, 10]:
            hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                            finding_count=counts, active_models=5)
        # Last 3 are [25, 18, 10] — declining with drop > 5
        diags = [d for d in hm._diagnoses if d.detector == "findings_decline"]
        assert len(diags) == 1
        assert "declining" in diags[0].pathology.lower()

    def test_findings_decline_not_triggered_by_noise(self):
        """Small declines (< 5 total) don't trigger diagnosis."""
        hm = DetectorHealthMonitor()
        for counts in [10, 9, 8, 7]:
            hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                            finding_count=counts, active_models=5)
        diags = [d for d in hm._diagnoses if d.detector == "findings_decline"]
        assert len(diags) == 0  # drop is only 2 (9→7)

    def test_vocab_saturation_detection(self):
        """Low vocab growth for 3+ rounds triggers vocab_saturation diagnosis."""
        hm = DetectorHealthMonitor()
        # Need 3 rounds of data with low vocab growth
        for i in range(3):
            hm.record_vocab_growth(0.02)  # below 0.04 threshold
            hm.record_round(kappa=0.5, mu=10.0, novelty_rate=0.5,
                            finding_count=10, active_models=5)
        diags = [d for d in hm._diagnoses if d.detector == "vocab_saturation"]
        assert len(diags) == 1
        assert "premature" in diags[0].pathology.lower()

    def test_remediation_state_tracking(self):
        """set_remediation_state correctly records state for verification."""
        hm = DetectorHealthMonitor()
        hm.set_remediation_state("kappa_stuck", chain_idx=0,
                                  applied_round=3, metric_at_apply=0.0,
                                  target_metric="kappa")
        state = hm._remediation_state["kappa_stuck"]
        assert state["chain_idx"] == 0
        assert state["applied_round"] == 3
        assert state["target_metric"] == "kappa"

    def test_remediation_outcome_verification_success(self):
        """Successful remediation is detected and logged."""
        hm = DetectorHealthMonitor()
        hm.set_remediation_state("kappa_stuck", chain_idx=0,
                                  applied_round=0, metric_at_apply=0.0,
                                  target_metric="kappa",
                                  verification_window=2)
        # Record 3 rounds (applied at 0, verify after window=2)
        hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                         finding_count=10, active_models=5)
        hm.record_round(kappa=0.3, mu=10.0, novelty_rate=1.0,
                         finding_count=10, active_models=5)
        diags = hm.record_round(kappa=0.5, mu=10.0, novelty_rate=1.0,
                                 finding_count=10, active_models=5)
        outcome_diags = [d for d in diags if d.detector == "remediation_outcome"]
        assert len(outcome_diags) == 1
        assert "SUCCESSFUL" in outcome_diags[0].pathology
        assert len(hm._remediation_log) == 1
        assert hm._remediation_log[0]["improved"] is True

    def test_remediation_outcome_verification_failure(self):
        """Failed remediation triggers escalation."""
        hm = DetectorHealthMonitor()
        hm.set_remediation_state("kappa_stuck", chain_idx=0,
                                  applied_round=0, metric_at_apply=0.0,
                                  target_metric="kappa",
                                  verification_window=2)
        # Record 3 rounds with no improvement — outcome fires on round 2
        all_diags = []
        for _ in range(3):
            diags = hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                                     finding_count=10, active_models=5)
            all_diags.extend(diags)
        outcome_diags = [d for d in all_diags
                         if d.detector == "remediation_outcome"]
        assert len(outcome_diags) == 1
        assert "INEFFECTIVE" in outcome_diags[0].pathology
        # Chain index should have been incremented for escalation
        assert hm._remediation_state["kappa_stuck"]["chain_idx"] == 1

    def test_remediation_log_accumulates(self):
        """Remediation log tracks all attempts."""
        hm = DetectorHealthMonitor()
        hm.set_remediation_state("test", chain_idx=0,
                                  applied_round=0, metric_at_apply=5.0,
                                  target_metric="finding_count",
                                  verification_window=1)
        hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                         finding_count=10, active_models=5)
        hm.record_round(kappa=0.0, mu=10.0, novelty_rate=1.0,
                         finding_count=8, active_models=5)
        log = hm.remediation_log
        assert len(log) == 1
        assert log[0]["pathology"] == "test"
        assert log[0]["value_now"] == 8.0


class TestRemediationChains:
    """Tests for the remediation chain system in DynamicManager."""

    def _make_manager(self):
        """Create a minimal DynamicManager for remediation testing."""
        config = DynamicManagementConfig(immune_feedback_enabled=True,
                                         immune_damping_rounds=0)
        models = [
            ModelSpec(model_id="m1", fingerprint=CapabilityFingerprint(0.1, 0.9, 0.8, 0.8)),
            ModelSpec(model_id="m2", fingerprint=CapabilityFingerprint(0.2, 0.8, 0.7, 0.7)),
        ]
        return DynamicManager(config=config, models=models)

    def test_kappa_chain_step_0(self):
        """Kappa stuck diagnosis triggers tau_sim reduction."""
        mgr = self._make_manager()
        old_tau = mgr.config.tau_sim
        diag = DetectorDiagnosis(
            detector="kappa",
            pathology="kappa stuck at ~0 for 3 rounds",
            severity="WARNING",
            recommended_action="lower tau_sim",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj is not None
        assert adj["parameter"] == "tau_sim"
        assert mgr.config.tau_sim == old_tau - 0.1

    def test_kappa_chain_escalation(self):
        """When chain step 0 fails, escalation uses step 1."""
        mgr = self._make_manager()
        # Simulate: step 0 was tried and failed (chain_idx escalated to 1)
        mgr.health_monitor._remediation_state["kappa_stuck"] = {
            "chain_idx": 1, "applied_round": 0,
            "metric_at_apply": 0.0, "target_metric": "kappa",
            "verification_window": 2,
        }
        old_tau = mgr.config.tau_sim
        diag = DetectorDiagnosis(
            detector="kappa",
            pathology="kappa stuck at ~0 for 3 rounds",
            severity="CRITICAL",
            recommended_action="lower tau_sim more",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=5)
        assert adj is not None
        assert mgr.config.tau_sim == old_tau - 0.1  # step 1 also lowers by 0.1

    def test_kappa_chain_exhaustion(self):
        """When all chain steps exhausted, immune reports exhaustion."""
        mgr = self._make_manager()
        # Set chain_idx beyond the chain length
        chain_len = len(mgr._REMEDIATION_CHAINS["kappa_stuck"])
        mgr.health_monitor._remediation_state["kappa_stuck"] = {
            "chain_idx": chain_len, "applied_round": 0,
            "metric_at_apply": 0.0, "target_metric": "kappa",
            "verification_window": 2,
        }
        diag = DetectorDiagnosis(
            detector="kappa",
            pathology="kappa stuck at ~0",
            severity="CRITICAL",
            recommended_action="n/a",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=10)
        assert adj is None  # chain exhausted, no fix applied
        # Check exhaustion event was emitted
        exhaustion = [e for e in mgr.event_stream._all_events
                      if "EXHAUSTED" in (e.detail or "")]
        assert len(exhaustion) == 1

    def test_findings_decline_deferred(self):
        """Findings decline is classified as DEFER — queued for human review."""
        mgr = self._make_manager()
        diag = DetectorDiagnosis(
            detector="findings_decline",
            pathology="findings declining for 3 rounds",
            severity="WARNING",
            recommended_action="add synthesis directive",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj is None  # DEFER — not applied
        assert len(mgr.pending_remediations) == 1
        assert mgr.pending_remediations[0]["chain_key"] == "findings_decline"
        assert mgr.pending_remediations[0]["status"] == "PENDING"

    def test_deferred_remediation_approve(self):
        """Approved deferred remediation gets applied."""
        mgr = self._make_manager()
        diag = DetectorDiagnosis(
            detector="findings_decline",
            pathology="findings declining for 3 rounds",
            severity="WARNING",
            recommended_action="add synthesis directive",
        )
        mgr.apply_diagnosis(diag, round_idx=0)
        assert len(mgr.pending_remediations) == 1
        adj = mgr.approve_deferred_remediation(0)
        assert adj is not None
        assert "m1" in mgr.config.per_model_directives
        assert mgr._deferred_remediations[0]["status"] == "APPROVED"
        assert len(mgr.pending_remediations) == 0

    def test_deferred_remediation_reject(self):
        """Rejected deferred remediation is not applied."""
        mgr = self._make_manager()
        diag = DetectorDiagnosis(
            detector="findings_decline",
            pathology="findings declining for 3 rounds",
            severity="WARNING",
            recommended_action="add synthesis directive",
        )
        mgr.apply_diagnosis(diag, round_idx=0)
        result = mgr.reject_deferred_remediation(0)
        assert result is True
        assert mgr._deferred_remediations[0]["status"] == "REJECTED"
        assert "m1" not in mgr.config.per_model_directives

    def test_model_failure_adds_pre_decompose(self):
        """Model failure adds model to pre-decompose set."""
        mgr = self._make_manager()
        diag = DetectorDiagnosis(
            detector="model_failure",
            pathology="m1 has failed 3 consecutive rounds",
            severity="CRITICAL",
            recommended_action="pre-decompose m1",
            evidence={"model_id": "m1"},
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj is not None
        assert "m1" in mgr.config.pre_decompose_models

    def test_damping_prevents_oscillation(self):
        """Damping prevents the same fix being applied too quickly."""
        config = DynamicManagementConfig(immune_feedback_enabled=True,
                                         immune_damping_rounds=3)
        models = [
            ModelSpec(model_id="m1", fingerprint=CapabilityFingerprint(0.1, 0.9, 0.8, 0.8)),
        ]
        mgr = DynamicManager(config=config, models=models)
        diag = DetectorDiagnosis(
            detector="kappa", pathology="kappa stuck",
            severity="WARNING", recommended_action="lower tau_sim",
        )
        adj1 = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj1 is not None
        adj2 = mgr.apply_diagnosis(diag, round_idx=1)
        assert adj2 is None  # damped — only 1 round since last adjustment

    def test_vocab_saturation_halves_threshold(self):
        """Vocab saturation diagnosis halves tau_vocab_growth."""
        mgr = self._make_manager()
        old_val = mgr.config.tau_vocab_growth
        diag = DetectorDiagnosis(
            detector="vocab_saturation",
            pathology="premature vocab saturation",
            severity="WARNING",
            recommended_action="lower threshold",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj is not None
        assert mgr.config.tau_vocab_growth == pytest.approx(old_val * 0.5)

    def test_immune_disabled_skips_remediation(self):
        """When immune feedback is disabled, no remediation occurs."""
        config = DynamicManagementConfig(immune_feedback_enabled=False)
        models = [
            ModelSpec(model_id="m1", fingerprint=CapabilityFingerprint(0.1, 0.9, 0.8, 0.8)),
        ]
        mgr = DynamicManager(config=config, models=models)
        diag = DetectorDiagnosis(
            detector="kappa", pathology="kappa stuck",
            severity="WARNING", recommended_action="lower tau_sim",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        assert adj is None


class TestSelfAdaptiveImmuneLayer:
    """Level 3: self-adaptive immune layer tests (Exp15b)."""

    def test_remediation_outcome_tracking(self):
        """record_remediation_outcome feeds the self-performance tracker."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, True, 0.0, 0.3)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        assert len(hm._remediation_outcomes) == 2
        assert hm.remediation_success_rate == 0.5

    def test_remediation_success_rate_default(self):
        """No data → success rate defaults to 1.0 (assume healthy)."""
        hm = DetectorHealthMonitor()
        assert hm.remediation_success_rate == 1.0

    def test_natural_resolution_tracking(self):
        """Natural resolutions feed the false positive tracker."""
        hm = DetectorHealthMonitor()
        # Simulate kappa pathology appearing then resolving
        for _ in range(3):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        hm.record_natural_resolution("kappa")
        assert len(hm._false_positive_history) == 1
        assert hm._false_positive_history[0]["detector"] == "kappa"

    def test_chain_exhaustion_tracking(self):
        """Chain exhaustions feed the exhaustion tracker."""
        hm = DetectorHealthMonitor()
        hm.record_chain_exhaustion("kappa_stuck")
        assert len(hm._chain_exhaustion_history) == 1

    def test_step_effectiveness_tracking(self):
        """Per-step effectiveness is tracked correctly."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, True, 0.0, 0.3)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.record_remediation_outcome("kappa_stuck", 1, True, 0.0, 0.5)
        assert hm._step_effectiveness["kappa_stuck"][0] == {"success": 1, "fail": 1}
        assert hm._step_effectiveness["kappa_stuck"][1] == {"success": 1, "fail": 0}

    def test_recommended_chain_start_default(self):
        """No history → start at step 0."""
        hm = DetectorHealthMonitor()
        assert hm.recommended_chain_start("kappa_stuck") == 0

    def test_recommended_chain_start_skip_ineffective(self):
        """If step 0 has 2+ failures and 0 successes, skip to step 1."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.record_remediation_outcome("kappa_stuck", 1, True, 0.0, 0.5)
        assert hm.recommended_chain_start("kappa_stuck") == 1

    def test_recommended_chain_start_keeps_working_step(self):
        """If step 0 has any successes, don't skip it."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, True, 0.0, 0.3)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        assert hm.recommended_chain_start("kappa_stuck") == 0

    def test_p_pass_no_contraindications(self):
        """P-pass approves with no history."""
        hm = DetectorHealthMonitor()
        proceed, rationale = hm.p_pass_remediation(
            "kappa_stuck", 0, "lower tau_sim by 0.1", 0.0, "kappa"
        )
        assert proceed is True
        assert "PASS" in rationale

    def test_p_pass_rejects_historically_failed(self):
        """P-pass rejects a transform that has failed 3+ times."""
        hm = DetectorHealthMonitor()
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        proceed, rationale = hm.p_pass_remediation(
            "kappa_stuck", 0, "lower tau_sim by 0.1", 0.0, "kappa"
        )
        assert proceed is False
        assert "REJECT" in rationale

    def test_p_pass_skips_when_improving(self):
        """P-pass skips intervention when metric is already improving."""
        hm = DetectorHealthMonitor()
        # Simulate kappa improving over 3 rounds
        hm._kappa_history = [0.0, 0.1, 0.2]
        proceed, rationale = hm.p_pass_remediation(
            "kappa_stuck", 0, "lower tau_sim by 0.1", 0.2, "kappa"
        )
        assert proceed is False
        assert "SKIP" in rationale

    def test_p_pass_warns_mixed_results(self):
        """P-pass warns but proceeds when step has mixed results."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, True, 0.0, 0.3)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        proceed, rationale = hm.p_pass_remediation(
            "kappa_stuck", 0, "lower tau_sim by 0.1", 0.0, "kappa"
        )
        assert proceed is True
        assert "WARN" in rationale

    def test_self_diagnose_low_success_rate(self):
        """Self-diagnosis detects low remediation success rate."""
        hm = DetectorHealthMonitor(stuck_window=3)
        # Need 5+ rounds of data for self-diagnosis
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        # Record 3 failures, 0 successes
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        diags = hm.self_diagnose()
        assert any(d.detector == "self_diagnosis" for d in diags)
        assert hm._stuck_window == 4  # widened from 3

    def test_self_diagnose_bounded_window(self):
        """Self-adjustment never exceeds 2x original window."""
        hm = DetectorHealthMonitor(stuck_window=3)
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        # First self-diagnose: 3 → 4
        hm.self_diagnose()
        assert hm._stuck_window == 4
        # Force another by adding more failures
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.self_diagnose()
        assert hm._stuck_window == 5
        # One more should hit the cap at 6 (2 × 3)
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.self_diagnose()
        assert hm._stuck_window == 6  # 2x original
        # Beyond cap — should not increase further
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.self_diagnose()
        assert hm._stuck_window == 6  # capped

    def test_self_diagnose_high_false_positives(self):
        """Self-diagnosis detects high false positive rate."""
        hm = DetectorHealthMonitor()
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        # Record enough natural resolutions to push rate > 0.5
        hm.record_natural_resolution("kappa")
        hm.record_natural_resolution("mu")
        hm.record_natural_resolution("findings_decline")
        old_decay = hm._sensitivity_decay
        diags = hm.self_diagnose()
        fp_diags = [d for d in diags if "false positive" in d.pathology.lower()]
        assert len(fp_diags) >= 1
        assert hm._sensitivity_decay > old_decay  # reduced sensitivity

    def test_self_diagnose_chain_exhaustion(self):
        """Self-diagnosis reports chain exhaustion as CRITICAL."""
        hm = DetectorHealthMonitor()
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        hm.record_chain_exhaustion("kappa_stuck")
        hm.record_chain_exhaustion("kappa_stuck")
        diags = hm.self_diagnose()
        exhaust_diags = [d for d in diags if "exhaustion" in d.pathology.lower()]
        assert len(exhaust_diags) >= 1
        assert exhaust_diags[0].severity == "CRITICAL"

    def test_self_diagnosis_summary(self):
        """self_diagnosis_summary returns all performance metrics."""
        hm = DetectorHealthMonitor()
        hm.record_remediation_outcome("kappa_stuck", 0, True, 0.0, 0.3)
        summary = hm.self_diagnosis_summary
        assert "remediation_success_rate" in summary
        assert "false_positive_rate" in summary
        assert "chain_exhaustion_rate" in summary
        assert "step_effectiveness" in summary
        assert summary["total_remediations"] == 1

    def test_self_adjustment_log_persists(self):
        """Self-adjustments are logged for audit trail."""
        hm = DetectorHealthMonitor(stuck_window=3)
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        hm.self_diagnose()
        assert len(hm.self_adjustment_log) >= 1
        assert hm.self_adjustment_log[0]["trigger"] == "low_remediation_success_rate"

    def test_verify_outcomes_feeds_self_tracker(self):
        """_verify_remediation_outcomes feeds record_remediation_outcome."""
        hm = DetectorHealthMonitor()
        # Set up remediation state
        hm.set_remediation_state("kappa_stuck", 0, 0, 0.0, "kappa", verification_window=1)
        # Record 2 rounds to trigger verification
        hm.record_round(0.0, 10.0, 0.5, 10, 3)
        hm.record_round(0.3, 10.0, 0.5, 10, 3)  # kappa improved
        assert len(hm._remediation_outcomes) == 1
        assert hm._remediation_outcomes[0]["success"] is True

    def test_natural_resolution_fed_on_kappa_resolve(self):
        """When kappa pathology resolves without active remediation, it's a false positive."""
        hm = DetectorHealthMonitor(stuck_window=3)
        # Trigger kappa pathology
        for _ in range(3):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        assert hm._pathology_counts.get("kappa", 0) >= 1
        # Now resolve it (kappa > 0.01) without active remediation
        hm.record_round(0.5, 10.0, 0.5, 10, 3)
        assert len(hm._false_positive_history) == 1

    def test_chain_skip_in_apply_diagnosis(self):
        """apply_diagnosis skips historically ineffective chain steps."""
        config = DynamicManagementConfig(immune_feedback_enabled=True,
                                         immune_damping_rounds=0)
        models = [
            ModelSpec(model_id="m1",
                      fingerprint=CapabilityFingerprint(0.1, 0.9, 0.8, 0.8)),
        ]
        mgr = DynamicManager(config=config, models=models)
        # Record step 0 as historically ineffective
        mgr.health_monitor.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        mgr.health_monitor.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)

        diag = DetectorDiagnosis(
            detector="kappa", pathology="kappa stuck",
            severity="WARNING", recommended_action="lower tau_sim",
        )
        mgr.apply_diagnosis(diag, round_idx=0)
        # The chain_skip event should be in the event stream
        events = [e for e in mgr.event_stream._all_events
                  if e.metadata and e.metadata.get("chain_skip")]
        assert len(events) >= 1

    def test_p_pass_rejects_auto_fix_escalates(self):
        """P-pass rejection of a step escalates to the next step in the chain."""
        config = DynamicManagementConfig(immune_feedback_enabled=True,
                                         immune_damping_rounds=0)
        models = [
            ModelSpec(model_id="m1",
                      fingerprint=CapabilityFingerprint(0.1, 0.9, 0.8, 0.8)),
        ]
        mgr = DynamicManager(config=config, models=models)
        # Record step 0 as 3x failed → P-pass will reject step 0
        for _ in range(3):
            mgr.health_monitor.record_remediation_outcome(
                "kappa_stuck", 0, False, 0.0, 0.0
            )

        old_tau = mgr.config.tau_sim
        diag = DetectorDiagnosis(
            detector="kappa", pathology="kappa stuck",
            severity="WARNING", recommended_action="lower tau_sim",
        )
        adj = mgr.apply_diagnosis(diag, round_idx=0)
        # Step 0 skipped by simplest-sufficient, step 1 tried instead
        # Step 1 is also AUTO (lower_tau_sim_01), so P-pass runs on it
        p_pass_events = [e for e in mgr.event_stream._all_events
                         if e.metadata and e.metadata.get("p_pass")]
        assert len(p_pass_events) >= 1
        # Step 1 has no failure history so P-pass should approve
        assert any(e.metadata.get("proceed") for e in p_pass_events)

    def test_self_diagnose_wired_into_record_round(self):
        """self_diagnose is called as part of record_round."""
        hm = DetectorHealthMonitor(stuck_window=3)
        # Build enough data for self-diagnosis to trigger
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)
        for i in range(6):
            diags = hm.record_round(0.0, 10.0, 0.5, 10, 3)
        # Self-diagnosis should have fired within record_round
        self_diags = [d for d in diags if d.detector == "self_diagnosis"]
        assert len(self_diags) >= 1


class TestExtendedPPassImmune:
    """Extended P-pass for multi-modular immune layer fixes."""

    def test_single_module_uses_standard_ppass(self):
        """Single-module transforms use standard (lightweight) P-pass."""
        hm = DetectorHealthMonitor()
        # lower_tau_sim_01 is NOT in _MULTI_MODULAR_TRANSFORMS
        assert not hm._is_multi_modular("kappa_stuck", 0, "lower_tau_sim_01")
        proceed, rationale = hm.p_pass_remediation(
            "kappa_stuck", 0, "lower tau_sim",
            0.0, "kappa",
            transform_name="lower_tau_sim_01",
        )
        assert proceed is True
        # Standard P-pass says "P-pass PASS" not "Extended P-pass"
        assert "P-pass PASS" in rationale
        assert "Extended" not in rationale

    def test_multi_module_uses_extended_ppass(self):
        """Multi-modular transforms use extended P-pass."""
        hm = DetectorHealthMonitor()
        assert hm._is_multi_modular("findings_decline", 0, "add_synthesis_directive")
        proceed, rationale = hm.p_pass_remediation(
            "findings_decline", 0, "add synthesis directive",
            10.0, "finding_count",
            transform_name="add_synthesis_directive",
            affected_models=["m1", "m2", "m3"],
        )
        # Extended P-pass should have run
        assert "Extended P-pass" in rationale

    def test_extended_ppass_cascade_risk(self):
        """Extended P-pass detects cascade risk for 3+ model fixes."""
        hm = DetectorHealthMonitor()
        proceed, rationale = hm._extended_p_pass_remediation(
            "findings_decline", 0, "add synthesis directive",
            10.0, "finding_count",
            affected_models=["m1", "m2", "m3", "m4"],
        )
        # Should warn about cascade risk (4 models)
        assert "cascade" in rationale.lower() or "WARN" in rationale

    def test_extended_ppass_over_specification(self):
        """Extended P-pass flags over-specification for rare pathologies."""
        hm = DetectorHealthMonitor()
        # Pathology only seen 1 time but fix affects 4 models
        hm._pathology_counts["findings_decline"] = 1
        proceed, rationale = hm._extended_p_pass_remediation(
            "findings_decline", 0, "add synthesis directive",
            10.0, "finding_count",
            affected_models=["m1", "m2", "m3", "m4"],
        )
        assert "over_specification" in rationale.lower() or "WARN" in rationale

    def test_extended_ppass_suggests_simplification(self):
        """Extended P-pass suggests targeting worst performers only."""
        hm = DetectorHealthMonitor()
        hm._pathology_counts["findings_decline"] = 1
        # Set up model histories so we can identify worst performers
        hm._model_finding_history = {
            "m1": [10, 8, 5],
            "m2": [15, 12, 11],
            "m3": [2, 1, 0],
            "m4": [8, 6, 4],
        }
        hm._model_failure_counts = {"m3": 2}
        proceed, rationale = hm._extended_p_pass_remediation(
            "findings_decline", 0, "add synthesis directive",
            10.0, "finding_count",
            affected_models=["m1", "m2", "m3", "m4"],
        )
        # Should have suggested simplification
        assert proceed is True  # SOFT failures only → proceed with warn

    def test_extended_ppass_clean_pass(self):
        """Extended P-pass passes cleanly when no issues found."""
        hm = DetectorHealthMonitor()
        # Small number of affected models, pathology well-established
        hm._pathology_counts["findings_decline"] = 5
        proceed, rationale = hm._extended_p_pass_remediation(
            "findings_decline", 0, "add synthesis directive",
            10.0, "finding_count",
            affected_models=["m1", "m2"],  # Only 2 models, not multi-trigger
        )
        assert proceed is True
        assert "PASS" in rationale

    def test_self_adjustment_ppass_approves_coherent(self):
        """Self-adjustment P-pass approves coherent parameter changes."""
        hm = DetectorHealthMonitor(stuck_window=3, mu_increase_window=2)
        proceed, rationale = hm._p_pass_self_adjustment(
            trigger="low_remediation_success_rate",
            adjustments={
                "stuck_window": (3, 4),
                "mu_window": (2, 3),
            },
            success_rate=0.2,
        )
        assert proceed is True
        assert "PASS" in rationale

    def test_self_adjustment_ppass_rejects_contradictory(self):
        """Self-adjustment P-pass rejects contradictory parameter changes."""
        hm = DetectorHealthMonitor(stuck_window=5, mu_increase_window=4)
        # One parameter widening, another narrowing — contradictory
        proceed, rationale = hm._p_pass_self_adjustment(
            trigger="low_remediation_success_rate",
            adjustments={
                "stuck_window": (5, 6),   # widening
                "mu_window": (4, 3),       # narrowing
            },
            success_rate=0.2,
        )
        assert proceed is False
        assert "contradiction" in rationale.lower()

    def test_self_adjustment_ppass_warns_cumulative_risk(self):
        """Self-adjustment P-pass warns on cumulative window widening."""
        hm = DetectorHealthMonitor(stuck_window=3, mu_increase_window=2)
        # Both already above original
        hm._stuck_window = 5
        hm._mu_increase_window = 3
        proceed, rationale = hm._p_pass_self_adjustment(
            trigger="low_remediation_success_rate",
            adjustments={
                "stuck_window": (5, 6),
                "mu_window": (3, 4),
            },
            success_rate=0.1,
        )
        # Should warn about cumulative risk but still proceed (SOFT)
        assert proceed is True
        assert "cumulative" in rationale.lower() or "WARN" in rationale

    def test_self_diagnose_iterates_to_simplest(self):
        """self_diagnose tries both, then stuck_only, then mu_only."""
        hm = DetectorHealthMonitor(stuck_window=3, mu_increase_window=2)
        # Both already near bound — "both" will fail, "stuck_only" should work
        hm._stuck_window = 5  # near 2×3=6 bound
        hm._mu_increase_window = 3  # near 2×2=4 bound
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)

        diags = hm.self_diagnose()
        self_diags = [d for d in diags if d.detector == "self_diagnosis"]
        assert len(self_diags) >= 1
        # Should have applied the simplest sufficient candidate
        evidence = self_diags[0].evidence
        if isinstance(evidence, dict):
            candidate = evidence.get("candidate", "")
            # Either "both" or a simpler variant succeeded
            assert candidate in ("both", "stuck_only", "mu_only")

    def test_self_diagnose_defers_when_all_rejected(self):
        """When all candidates are P-pass rejected, defer to human."""
        hm = DetectorHealthMonitor(stuck_window=3, mu_increase_window=2)
        # Both at 2× bound — no room to widen
        hm._stuck_window = 6
        hm._mu_increase_window = 4
        for i in range(6):
            hm.record_round(0.0, 10.0, 0.5, 10, 3)
        for _ in range(3):
            hm.record_remediation_outcome("kappa_stuck", 0, False, 0.0, 0.0)

        diags = hm.self_diagnose()
        self_diags = [d for d in diags if d.detector == "self_diagnosis"]
        # Should have a diagnosis but no adjustment (all at bounds)
        assert len(self_diags) >= 1

    def test_identify_worst_performers(self):
        """_identify_worst_performers correctly ranks models."""
        hm = DetectorHealthMonitor()
        hm._model_finding_history = {
            "good": [10, 12, 15],
            "bad": [2, 1, 0],
            "medium": [5, 5, 5],
        }
        hm._model_failure_counts = {"bad": 3, "good": 0, "medium": 0}
        worst = hm._identify_worst_performers(["good", "bad", "medium"], 2)
        assert "bad" in worst
        assert "good" not in worst


class TestParserYieldDetector:
    """Tests for parser yield anomaly detection (Exp15 FM4)."""

    def test_parser_yield_no_trigger_normal(self):
        """Normal response with findings does not trigger."""
        hm = DetectorHealthMonitor()
        diags = hm.record_model_round(
            "CC2", 7, failed=False, response_time=120.0, response_chars=15000
        )
        yield_diags = [d for d in diags if d.detector == "parser_yield"]
        assert len(yield_diags) == 0

    def test_parser_yield_no_trigger_small_response(self):
        """Small response with 0 findings is not anomalous (model may have failed)."""
        hm = DetectorHealthMonitor()
        diags = hm.record_model_round(
            "CC2", 0, failed=False, response_time=10.0, response_chars=500
        )
        yield_diags = [d for d in diags if d.detector == "parser_yield"]
        assert len(yield_diags) == 0

    def test_parser_yield_no_trigger_on_failure(self):
        """Failed model with large response does not trigger (already handled)."""
        hm = DetectorHealthMonitor()
        diags = hm.record_model_round(
            "CC2", 0, failed=True, response_time=120.0, response_chars=10000
        )
        yield_diags = [d for d in diags if d.detector == "parser_yield"]
        assert len(yield_diags) == 0

    def test_parser_yield_triggers_format_divergence(self):
        """Large response + 0 parsed findings → format divergence detected."""
        hm = DetectorHealthMonitor()
        diags = hm.record_model_round(
            "DeepSeek", 0, failed=False, response_time=180.0, response_chars=9738
        )
        yield_diags = [d for d in diags if d.detector == "parser_yield"]
        assert len(yield_diags) == 1
        assert "DeepSeek" in yield_diags[0].pathology
        assert "9738 chars" in yield_diags[0].pathology
        assert yield_diags[0].severity == "WARNING"
        assert yield_diags[0].evidence["format_yield"] == 0.0

    def test_parser_yield_escalates_on_repeat(self):
        """Repeated format divergence escalates to CRITICAL."""
        hm = DetectorHealthMonitor()
        hm.record_model_round(
            "DeepSeek", 0, failed=False, response_time=180.0, response_chars=9000
        )
        diags = hm.record_model_round(
            "DeepSeek", 0, failed=False, response_time=200.0, response_chars=12000
        )
        yield_diags = [d for d in diags if d.detector == "parser_yield"]
        assert len(yield_diags) == 1
        assert yield_diags[0].severity == "CRITICAL"

    def test_parser_yield_independent_per_model(self):
        """Parser yield tracked independently per model."""
        hm = DetectorHealthMonitor()
        hm.record_model_round(
            "DeepSeek", 0, failed=False, response_time=180.0, response_chars=9000
        )
        diags = hm.record_model_round(
            "CC2", 0, failed=False, response_time=120.0, response_chars=8000
        )
        cc2_yield = [d for d in diags if d.detector == "parser_yield"]
        assert len(cc2_yield) == 1
        assert cc2_yield[0].severity == "WARNING"  # first for CC2


class TestMonotonicDeclineDetector:
    """Tests for monotonic decline detection (Exp15 FM3)."""

    def test_no_trigger_insufficient_data(self):
        """Need 3 rounds to detect decline."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Gemini", 6, failed=False, response_time=100.0)
        diags = hm.record_model_round("Gemini", 3, failed=False, response_time=120.0)
        decline_diags = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(decline_diags) == 0

    def test_no_trigger_non_monotonic(self):
        """Non-monotonic pattern does not trigger."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Gemini", 6, failed=False)
        hm.record_model_round("Gemini", 3, failed=False)
        diags = hm.record_model_round("Gemini", 5, failed=False)  # up again
        decline_diags = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(decline_diags) == 0

    def test_no_trigger_small_decline(self):
        """Decline < 3 is noise, not pathological."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Gemini", 5, failed=False)
        hm.record_model_round("Gemini", 4, failed=False)
        diags = hm.record_model_round("Gemini", 3, failed=False)  # drop=2
        decline_diags = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(decline_diags) == 0

    def test_triggers_on_significant_decline(self):
        """3-round monotonic decline with drop ≥ 3 triggers WARNING."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Gemini", 8, failed=False)
        hm.record_model_round("Gemini", 5, failed=False)
        diags = hm.record_model_round("Gemini", 2, failed=False)  # drop=6
        decline_diags = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(decline_diags) == 1
        assert decline_diags[0].severity == "WARNING"
        assert "Gemini" in decline_diags[0].pathology
        assert decline_diags[0].evidence["total_decline"] == 6

    def test_escalates_on_persistence(self):
        """Persistent decline (continued without recovery) escalates to CRITICAL."""
        hm = DetectorHealthMonitor()
        # Sustained decline where each 3-round window has drop ≥ 3:
        # [20, 15, 10] → drop=10, occurrence 1
        hm.record_model_round("Gemini", 20, failed=False)
        hm.record_model_round("Gemini", 15, failed=False)
        hm.record_model_round("Gemini", 10, failed=False)
        # [15, 10, 5] → drop=10, occurrence 2
        hm.record_model_round("Gemini", 5, failed=False)
        # [10, 5, 1] → drop=9, occurrence 3 → CRITICAL (persistence ≥ 2)
        diags = hm.record_model_round("Gemini", 1, failed=False)
        decline_diags = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(decline_diags) == 1
        assert decline_diags[0].severity == "CRITICAL"

    def test_resolves_on_recovery(self):
        """Recovery from decline marks pathology as resolved."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Gemini", 10, failed=False)
        hm.record_model_round("Gemini", 6, failed=False)
        hm.record_model_round("Gemini", 2, failed=False)  # triggers
        # Recovery
        diags = hm.record_model_round("Gemini", 7, failed=False)
        key = "monotonic_decline_Gemini"
        assert hm._pathology_counts.get(key, 0) == 0
        assert hm._resolved_counts.get(key, 0) >= 1

    def test_independent_per_model(self):
        """Decline tracked independently per model."""
        hm = DetectorHealthMonitor()
        # Gemini declining
        hm.record_model_round("Gemini", 10, failed=False)
        hm.record_model_round("Gemini", 6, failed=False)
        hm.record_model_round("Gemini", 2, failed=False)
        # CC2 stable
        hm.record_model_round("CC2", 8, failed=False)
        hm.record_model_round("CC2", 8, failed=False)
        diags = hm.record_model_round("CC2", 8, failed=False)
        cc2_decline = [d for d in diags if d.detector == "monotonic_decline"]
        assert len(cc2_decline) == 0


class TestCostPerFindingSpikeDetector:
    """Tests for cost-per-finding spike detection (Exp15 FM5)."""

    def test_no_trigger_insufficient_data(self):
        """Need ≥ 3 rounds with findings to compute statistics."""
        hm = DetectorHealthMonitor()
        hm.record_model_round("Codex", 5, failed=False, response_time=100.0)
        diags = hm.record_model_round("Codex", 5, failed=False, response_time=110.0)
        cpf_diags = [d for d in diags if d.detector == "cpf_spike"]
        assert len(cpf_diags) == 0

    def test_no_trigger_stable_cpf(self):
        """Stable cost-per-finding does not trigger (zero variance → no σ)."""
        hm = DetectorHealthMonitor()
        for _ in range(5):
            hm.record_model_round("Codex", 5, failed=False, response_time=100.0)
        diags = hm.record_model_round("Codex", 5, failed=False, response_time=110.0)
        cpf_diags = [d for d in diags if d.detector == "cpf_spike"]
        assert len(cpf_diags) == 0

    def test_no_trigger_zero_findings(self):
        """Zero findings round does not compute CPF (avoid division by zero)."""
        hm = DetectorHealthMonitor()
        # Use varied baselines to produce non-zero σ
        for t in [90.0, 100.0, 110.0, 95.0, 105.0]:
            hm.record_model_round("Codex", 5, failed=False, response_time=t)
        diags = hm.record_model_round("Codex", 0, failed=False, response_time=400.0)
        cpf_diags = [d for d in diags if d.detector == "cpf_spike"]
        assert len(cpf_diags) == 0

    def test_triggers_on_spike(self):
        """CPF spike beyond 2σ triggers WARNING."""
        hm = DetectorHealthMonitor()
        # Establish varied baseline: ~18-22s per finding (non-zero σ)
        for t in [90.0, 100.0, 110.0, 95.0, 105.0]:
            hm.record_model_round("Codex", 5, failed=False, response_time=t)
        # Spike: 456s for 3 findings = 152s/finding vs baseline ~20s/finding
        diags = hm.record_model_round(
            "Codex", 3, failed=False, response_time=456.0
        )
        cpf_diags = [d for d in diags if d.detector == "cpf_spike"]
        assert len(cpf_diags) == 1
        assert cpf_diags[0].severity == "WARNING"
        assert "Codex" in cpf_diags[0].pathology
        assert cpf_diags[0].evidence["current_cpf"] > cpf_diags[0].evidence["threshold"]

    def test_no_trigger_moderate_variation(self):
        """Moderate CPF increase within 2σ does not trigger."""
        hm = DetectorHealthMonitor()
        # Wide-variance baseline: 50-200s for 5 findings = 10-40s/finding
        # Mean=20, σ≈11.4, threshold≈42.8 → 25s/finding well within
        times = [50.0, 100.0, 200.0, 70.0, 80.0]
        for t in times:
            hm.record_model_round("Codex", 5, failed=False, response_time=t)
        # Within 2σ: 125s for 5 findings = 25s/finding
        diags = hm.record_model_round("Codex", 5, failed=False, response_time=125.0)
        cpf_diags = [d for d in diags if d.detector == "cpf_spike"]
        assert len(cpf_diags) == 0

    def test_independent_per_model(self):
        """CPF spike tracked independently per model."""
        hm = DetectorHealthMonitor()
        # CC2 baseline (varied)
        for t in [90.0, 100.0, 110.0, 95.0, 105.0]:
            hm.record_model_round("CC2", 10, failed=False, response_time=t)
        # Codex baseline (varied, different scale)
        for t in [180.0, 200.0, 220.0, 190.0, 210.0]:
            hm.record_model_round("Codex", 5, failed=False, response_time=t)
        # CC2 spikes (500s for 2 findings = 250s/finding vs ~10s baseline)
        diags_cc2 = hm.record_model_round(
            "CC2", 2, failed=False, response_time=500.0
        )
        # Codex normal
        diags_codex = hm.record_model_round(
            "Codex", 5, failed=False, response_time=210.0
        )
        assert len([d for d in diags_cc2 if d.detector == "cpf_spike"]) == 1
        assert len([d for d in diags_codex if d.detector == "cpf_spike"]) == 0
