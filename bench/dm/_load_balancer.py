"""CDSFL Dynamic Management — Load Balancing (Area 2).

Implements multi-objective constrained task allocation (GAP variant).
Extracted from ``bench/dynamic_management.py``.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Set, Tuple

import numpy as np
from numpy.typing import NDArray

from bench.dm._types import (
    CapabilityFingerprint,
    DynamicManagementConfig,
    ModelSpec,
    Role,
    Task,
)
from bench.dm._role_assignment import RoleAssignment


@dataclass(frozen=True)
class Allocation:
    """Task allocation A : T -> 2^M, represented as indicator matrix.

    Example::

        alloc = Allocation(
            task_ids=["t1", "t2"],
            model_ids=["m1", "m2"],
            matrix=np.array([[1, 0], [1, 1]]),
        )
        print(alloc.get_assigned_models("t1"))  # {"m1"}
    """

    task_ids: List[str]
    model_ids: List[str]
    matrix: NDArray[np.int_]  # a_{jm}, shape (J, K)

    def get_assigned_models(self, task_id: str) -> Set[str]:
        """Return set of model IDs assigned to a task."""
        j = self.task_ids.index(task_id)
        return {
            self.model_ids[m]
            for m in range(len(self.model_ids))
            if self.matrix[j, m] == 1
        }

    def get_assigned_tasks(self, model_id: str) -> Set[str]:
        """Return set of task IDs assigned to a model."""
        m = self.model_ids.index(model_id)
        return {
            self.task_ids[j]
            for j in range(len(self.task_ids))
            if self.matrix[j, m] == 1
        }

    def model_load(self, model_id: str, tasks: Sequence[Task]) -> float:
        """Return total token load on a model: sum_j a_{jm} * b_j."""
        m = self.model_ids.index(model_id)
        task_map = {t.task_id: t for t in tasks}
        total = 0.0
        for j, tid in enumerate(self.task_ids):
            if self.matrix[j, m] == 1:
                total += task_map[tid].token_demand
        return total

    def model_load_fraction(
        self, model_id: str, tasks: Sequence[Task], models: Sequence[ModelSpec]
    ) -> float:
        """Return load fraction: sum_j a_{jm} * b_j / L_m."""
        m_idx = self.model_ids.index(model_id)
        model = next(ms for ms in models if ms.model_id == model_id)
        load = self.model_load(model_id, tasks)
        if model.L <= 0:
            return float("inf") if load > 0 else 0.0
        return load / model.L


class LoadBalancer:
    """Multi-objective constrained task allocation (GAP variant).

    Implements the merged formulation from §3 of the converged plan:
    - Multi-model allocation A : T -> 2^M
    - Cost objective J(A) with monetary, latency, and balance terms
    - Feasibility constraints F1 (token), F2 (coverage), F3 (role admissibility)
    - Redundancy targets based on criticality
    - Connection to D(n) through allocation

    The solver uses a greedy heuristic (practical for K <= 10, J <= 50).
    For larger instances, replace _solve_greedy with an ILP solver.

    Example::

        models = [
            ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7), L=10000, c=0.01),
            ModelSpec("m2", CapabilityFingerprint(0.2, 0.7, 0.8, 0.6), L=10000, c=0.02),
        ]
        tasks = [Task("t1", 3000, 1, 0.5), Task("t2", 4000, 2, 0.9)]
        role_map = {"m1": Role.PAR, "m2": Role.PAR}
        cfg = DynamicManagementConfig()
        lb = LoadBalancer(models, tasks, role_map, cfg)
        alloc, cost, is_balanced = lb.solve()
    """

    def __init__(
        self,
        models: Sequence[ModelSpec],
        tasks: Sequence[Task],
        role_map: Dict[str, Role],
        config: DynamicManagementConfig,
    ) -> None:
        self.models = list(models)
        self.tasks = list(tasks)
        self.role_map = role_map
        self.config = config
        self._model_idx = {m.model_id: i for i, m in enumerate(self.models)}
        self._task_idx = {t.task_id: i for i, t in enumerate(self.tasks)}
        self._allocation_warnings: List[str] = []  # Exp15 fix: feasibility warnings

    def _admissibility_mask(self) -> NDArray[np.int_]:
        """Compute role admissibility matrix ell^adm_{jm}.

        Default: PM excluded from standard tasks unless K=1.
        Returns shape (J, K).
        """
        J = len(self.tasks)
        K = len(self.models)
        mask = np.zeros((J, K), dtype=np.int_)
        k_total = sum(1 for r in self.role_map.values() if r in (Role.COL, Role.PAR, Role.PM))

        for j in range(J):
            for m_idx, model in enumerate(self.models):
                role = self.role_map.get(model.model_id, Role.PAR)
                if k_total == 1:
                    # K=1: PM does everything
                    mask[j, m_idx] = 1
                elif role in (Role.COL, Role.PAR):
                    mask[j, m_idx] = 1
                # PM excluded from standard tasks when K > 1
        return mask

    def _redundancy_target(self, task: Task) -> int:
        """Compute redundancy target r(t_j) based on criticality.

        Returns:
            Number of models that should cover this task.
        """
        K = len(self.models)
        if task.criticality >= self.config.tau_critical:
            return K
        elif task.criticality >= self.config.tau_moderate:
            return max(1, math.ceil(K / 2))
        else:
            return 1

    def _objective(
        self,
        matrix: NDArray[np.int_],
    ) -> float:
        """Compute J(A) = monetary_cost + lambda_lat * bottleneck + lambda_bal * variance.

        Args:
            matrix: Allocation matrix a_{jm}, shape (J, K).

        Returns:
            Total cost J(A).
        """
        J, K = matrix.shape
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        costs = np.array([m.c for m in self.models], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        taus = np.array([m.tau for m in self.models], dtype=np.float64)

        # Per-model load: sum_j a_{jm} * b_j
        # LB_F002: Each redundant copy independently consumes full token_demand.
        # This is intentional: redundancy is a reliability mechanism where all
        # copies execute (not just one). Monetary cost reflects actual spend.
        loads = matrix.T.astype(np.float64) @ demands  # shape (K,)

        # Monetary cost: sum_m c_m * load_m
        monetary = float(np.dot(costs, loads))

        # Load fractions
        with np.errstate(divide="ignore", invalid="ignore"):
            fractions = np.where(limits > 0, loads / limits, 0.0)

        # Bottleneck: max_m tau_m * fraction_m
        bottleneck = float(np.max(taus * fractions)) if K > 0 else 0.0

        # Variance of load fractions
        variance = float(np.var(fractions)) if K > 1 else 0.0

        return (
            monetary
            + self.config.lambda_lat * bottleneck
            + self.config.lambda_bal * variance
        )

    def _check_feasibility(
        self,
        matrix: NDArray[np.int_],
        admissibility: NDArray[np.int_],
    ) -> Tuple[bool, List[str]]:
        """Check all HARD feasibility constraints.

        LB_F009: F1 violations from force-assign fallback are expected (tagged
        in _allocation_warnings). This method reports all violations uniformly;
        callers should cross-reference _allocation_warnings to distinguish
        intentional force-assign violations from unexpected solver bugs.

        Returns:
            (feasible, list_of_violations)
        """
        violations: List[str] = []
        J, K = matrix.shape
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)

        # F1: Token feasibility — sum_j a_{jm} * b_j <= L_m
        loads = matrix.T.astype(np.float64) @ demands
        for m_idx in range(K):
            if loads[m_idx] > limits[m_idx]:
                violations.append(
                    f"F1: model {self.models[m_idx].model_id} overloaded "
                    f"({loads[m_idx]:.0f} > {limits[m_idx]:.0f})"
                )

        # F2: Coverage — every task assigned to at least one model
        for j in range(J):
            if matrix[j].sum() < 1:
                violations.append(f"F2: task {self.tasks[j].task_id} unassigned")

        # F3: Role consistency — a_{jm} <= ell^adm_{jm}
        role_violations = matrix & ~admissibility
        if role_violations.any():
            for j, m_idx in zip(*np.where(role_violations)):
                violations.append(
                    f"F3: task {self.tasks[j].task_id} assigned to "
                    f"inadmissible model {self.models[m_idx].model_id}"
                )

        return len(violations) == 0, violations

    def _balanced(self, matrix: NDArray[np.int_]) -> bool:
        """Check balance predicate: Var(load_fractions) <= epsilon_bal.

        LB_F011: Uses population variance (np.var, ddof=0). For small K this is
        more permissive than sample variance. epsilon_bal should be interpreted
        accordingly — it bounds the mean squared deviation from mean load fraction.

        LB_F003: When redundancy_target > 1, task demand is charged to all assigned
        models. Balance is meaningful only when most tasks have target=1; with high
        redundancy, variance reflects redundancy distribution, not imbalance.
        """
        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        loads = matrix.T.astype(np.float64) @ demands
        with np.errstate(divide="ignore", invalid="ignore"):
            fractions = np.where(limits > 0, loads / limits, 0.0)
        if len(fractions) <= 1:
            return True
        return float(np.var(fractions)) <= self.config.epsilon_bal

    def _solve_greedy(self) -> NDArray[np.int_]:
        """Greedy allocation heuristic.

        Strategy:
        1. Sort tasks by criticality (descending), then token_demand (descending)
           within tier (LB_F001: first-fit-decreasing).
        2. For each task, assign to admissible models with lowest current load
           fraction, up to redundancy target.
        3. Respect token limits (F1) when possible. When no model can fit a task
           within limits, force-assign to the model with most remaining capacity
           (LB_F006/LB_F013: F1 violation reported, coverage F2 maintained).

        Returns:
            Allocation matrix a_{jm}, shape (J, K).
        """
        J = len(self.tasks)
        K = len(self.models)
        matrix = np.zeros((J, K), dtype=np.int_)
        admissibility = self._admissibility_mask()

        demands = np.array([t.token_demand for t in self.tasks], dtype=np.float64)
        limits = np.array([m.L for m in self.models], dtype=np.float64)
        current_loads = np.zeros(K, dtype=np.float64)

        # LB_F001: Sort by criticality descending, then token_demand descending
        # within same criticality tier (first-fit-decreasing heuristic).
        task_order = sorted(
            range(J),
            key=lambda j: (self.tasks[j].criticality, self.tasks[j].token_demand),
            reverse=True,
        )

        for j in task_order:
            target = self._redundancy_target(self.tasks[j])
            admissible = [m_idx for m_idx in range(K) if admissibility[j, m_idx] == 1]

            if not admissible:
                # No admissible model — assign to least-loaded model as fallback
                # (this can only happen if all models are PM and K > 1, which
                # shouldn't occur, but handle gracefully)
                admissible = list(range(K))

            # Sort admissible models by current load fraction (ascending)
            admissible.sort(
                key=lambda m_idx: (
                    current_loads[m_idx] / limits[m_idx] if limits[m_idx] > 0 else float("inf")
                )
            )

            # Exp15 fix: upfront feasibility check before allocation attempt
            feasible_count = sum(
                1 for m_idx in admissible
                if current_loads[m_idx] + demands[j] <= limits[m_idx]
            )
            if feasible_count < target:
                # Log degraded allocation — target can't be fully met
                self._allocation_warnings.append(
                    f"Task {self.tasks[j].task_id}: target={target}, "
                    f"feasible={feasible_count}/{len(admissible)} admissible"
                )

            assigned = 0
            # LB_F006: If no model can fit this task within limits, skip the
            # normal loop and go directly to capacity-aware force-assign.
            if feasible_count == 0 and admissible:
                # Force-assign to model with most remaining capacity
                best_m = max(
                    admissible,
                    key=lambda m_idx: limits[m_idx] - current_loads[m_idx],
                )
                matrix[j, best_m] = 1
                current_loads[best_m] += demands[j]
                assigned = 1
                self._allocation_warnings.append(
                    f"Task {self.tasks[j].task_id}: force-assigned to "
                    f"{self.models[best_m].model_id} (F1 violation, no feasible model)"
                )
            else:
                for m_idx in admissible:
                    if assigned >= target:
                        break
                    # Check F1: would this assignment exceed token limit?
                    if current_loads[m_idx] + demands[j] <= limits[m_idx]:
                        matrix[j, m_idx] = 1
                        current_loads[m_idx] += demands[j]
                        assigned += 1

                # If we couldn't meet redundancy target, ensure at least coverage (F2)
                if assigned == 0:
                    # Force-assign to least-loaded admissible model even if over limit
                    # (F1 violation is reported but coverage is maintained)
                    if admissible:
                        m_idx = admissible[0]
                        matrix[j, m_idx] = 1
                        current_loads[m_idx] += demands[j]

        return matrix

    def solve(self) -> Tuple[Allocation, float, bool]:
        """Solve the allocation problem.

        Returns:
            (allocation, cost, is_balanced)

        Example::

            alloc, cost, balanced = lb.solve()
            print(f"Cost: {cost:.4f}, Balanced: {balanced}")
        """
        if not self.tasks:
            alloc = Allocation([], [m.model_id for m in self.models], np.zeros((0, len(self.models)), dtype=np.int_))
            return alloc, 0.0, True

        matrix = self._solve_greedy()
        admissibility = self._admissibility_mask()
        feasible, violations = self._check_feasibility(matrix, admissibility)

        if not feasible:
            warnings.warn(
                f"Allocation has feasibility violations: {violations}",
                stacklevel=2,
            )

        cost = self._objective(matrix)
        balanced = self._balanced(matrix)

        alloc = Allocation(
            task_ids=[t.task_id for t in self.tasks],
            model_ids=[m.model_id for m in self.models],
            matrix=matrix,
        )
        return alloc, cost, balanced

    def feasibility_probability(
        self,
        model: ModelSpec,
        task_load: float,
    ) -> float:
        """Pre-dispatch probabilistic feasibility estimate.

        P(task fits within model capacity) when L_m is uncertain.
        If L_std = 0, returns 1.0 if feasible, 0.0 otherwise.

        Uses a normal approximation: L_m ~ N(L, L_std^2).
        P(feasible) = P(task_load <= L_m) = Phi((L - task_load) / L_std).

        This addresses the Codex timeout gap: CLI delivery mechanisms may not
        expose exact token limits.

        Args:
            model: Model specification (with L and L_std).
            task_load: Total token demand to be dispatched.

        Returns:
            Probability in [0, 1] that the task fits.

        Example::

            m = ModelSpec("codex", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7),
                          L=32768, L_std=5000)
            p = lb.feasibility_probability(m, 30000)
            print(f"P(feasible) = {p:.3f}")
        """
        if model.L_std <= 0:
            return 1.0 if task_load <= model.L else 0.0

        # Standard normal CDF via error function
        z = (model.L - task_load) / model.L_std
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    def dispatch_check(
        self,
        model: ModelSpec,
        task_load: float,
    ) -> Tuple[bool, float]:
        """Check whether to dispatch to a model given uncertainty.

        Returns:
            (should_dispatch, p_feasible)

        Example::

            ok, p = lb.dispatch_check(model, 30000)
            if not ok:
                print(f"Skip dispatch: P(feasible) = {p:.3f} < {cfg.feasibility_threshold}")
        """
        p = self.feasibility_probability(model, task_load)
        return p >= self.config.feasibility_threshold, p

    # --- Reduction property validators ---

    @staticmethod
    def validate_k1(config: DynamicManagementConfig) -> bool:
        """Validate K=1 reduction: A(t_j) = {m1} for all j, feasibility = sum b_j <= L1.

        Example::

            assert LoadBalancer.validate_k1(DynamicManagementConfig())
        """
        m = ModelSpec("m1", CapabilityFingerprint(0.1, 0.8, 0.9, 0.7), L=10000, c=0.01)
        tasks = [Task("t1", 3000, 1, 0.5), Task("t2", 4000, 2, 0.9)]
        role_map = {"m1": Role.PM}
        lb = LoadBalancer([m], tasks, role_map, config)
        alloc, _, _ = lb.solve()
        # Every task assigned to m1
        for j in range(len(tasks)):
            if alloc.matrix[j, 0] != 1:
                return False
        return True

    @staticmethod
    def validate_homogeneous(k: int, config: DynamicManagementConfig) -> bool:
        """Validate homogeneous reduction: equal distribution optimal.

        Example::

            assert LoadBalancer.validate_homogeneous(3, DynamicManagementConfig())
        """
        fp = CapabilityFingerprint(0.5, 0.5, 0.5, 0.5)
        models = [ModelSpec(f"m{i}", fp, L=10000, c=0.01) for i in range(k)]
        tasks = [Task(f"t{j}", 1000, j % 3, 0.3) for j in range(k)]
        role_map = {f"m0": Role.PM}
        for i in range(1, k):
            role_map[f"m{i}"] = Role.PAR
        lb = LoadBalancer(models, tasks, role_map, config)
        alloc, _, balanced = lb.solve()
        # With homogeneous models and equal tasks, should be balanced
        return balanced
