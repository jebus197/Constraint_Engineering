"""Task 2.2: the falsifier exp42 C0001 never got. The highest severity of the set.

THE FINDING, CC2, severity 0.90, recorded UNCONFIRMED / UNTOOLABLE with an empty
falsifier_code, and recovered here from the raw reply
`r0_cc2_20260606T185335Z.json`:

    "`_prune_for_coherence()` is counterproductive. It removes SOFT text to lower
    constraint density, but density = `_count_constraints(policy)` /
    `token_estimate`. `_count_constraints` counts from the TOML policy dict
    (fixed, independent of packet text). Removing text shrinks `token_estimate`
    while `constraint_count` stays constant, so density INCREASES after every
    prune. The early-exit condition `if density <= budget` can never become true
    through pruning."

CONFIRMED, AND PROVED UNREACHABLE RATHER THAN MERELY OBSERVED.

SymPy: d(C/t)/dt = -C/t**2, negative for positive C and t, so density rises as
tokens fall. z3: with C fixed, t1 <= t0, and the entry condition C/t0 > budget,
asking whether C/t1 <= budget can hold returns UNSAT. Both early exits in
`_prune_for_coherence` are dead code.

THE CONTROL THAT SHOWS THE FIXED NUMERATOR IS THE CAUSE. The same z3 query with a
RECOMPUTED count that may fall returns SAT. So the unreachability is not a
property of the loop's shape; it is caused precisely by counting constraints from
the policy dict, which pruning cannot touch.

DEMONSTRATED ON A REAL COMPOSITION (deepseek_v3, software): 7,090 chars and
density 0.011851 before, 3,994 chars and density 0.021042 after -- 1.7756 times
WORSE against a budget of 0.01 -- with every prunable packet exhausted and the
domain directive deleted outright.

THE HARM RATE, AND MY FIRST FRAMING OF IT WAS WRONG. 10 of the 50 compositions
that HAD a domain directive lose it entirely: 20.0000%, Wilson
[11.2438%, 33.0371%], Clopper-Pearson [10.0302%, 33.7183%], statsmodels and scipy
agreeing to 0.0e+00. A first pass counted 50 of 90 compositions "without a domain
packet afterwards" and would have reported 55.5556%, but 40 of those never had
one -- no directive file exists for that domain. Absent is not deleted, and the
overstatement would have been 2.8-fold.

NO FIX APPLIED. The repair is real but it changes which packets survive
composition, so it changes the prompt every model receives and invalidates replay
of archived runs -- the same class as C0040, C0037 and C0036. Parked.
"""
from __future__ import annotations

import itertools
import pathlib
import sys
import warnings

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bench.cdsfl_registry.composer import (  # noqa: E402
    MODEL_COHERENCE_BUDGETS,
    _count_constraints,
    _load_domain_directive,
    _load_universal_directive,
    _prune_for_coherence,
    build_interaction_pattern,
    compose,
)
from bench.cdsfl_registry.registry import DOMAIN_MAP, load_effective_policy  # noqa: E402


class TestTheEarlyExitIsUnreachable:
    def test_sympy_says_density_rises_as_text_is_removed(self):
        import sympy as sp
        C, t = sp.symbols("C t", positive=True)
        d = sp.diff(C / t, t)
        assert sp.simplify(d + C / t**2) == 0, d
        assert sp.ask(sp.Q.negative(d), sp.Q.positive(C) & sp.Q.positive(t)), (
            "d(C/t)/dt is no longer negative, so removing text no longer raises "
            "density and the finding's mechanism is gone")

    def test_z3_says_the_exit_condition_can_never_hold(self):
        from z3 import Reals, Solver, unsat
        C, t0, t1, b = Reals("C t0 t1 b")
        s = Solver()
        s.add(C > 0, t0 > 0, t1 > 0, b > 0)
        s.add(t1 <= t0)          # pruning never grows the text
        s.add(C / t0 > b)        # the loop is only entered when over budget
        s.add(C / t1 <= b)       # and the early exit requires this
        assert s.check() == unsat, (
            "z3 found a state where the early exit fires; the branch is "
            "reachable after all and C0001 is refuted")

    def test_the_control_shows_the_FIXED_numerator_is_the_cause(self):
        """Without this, 'unreachable' might be a property of the loop's shape."""
        from z3 import Reals, Solver, sat
        C0, C1, t0, t1, b = Reals("C0 C1 t0 t1 b")
        s = Solver()
        s.add(C0 > 0, C1 > 0, t0 > 0, t1 > 0, b > 0, t1 <= t0, C1 <= C0)
        s.add(C0 / t0 > b, C1 / t1 <= b)
        assert s.check() == sat, (
            "even with a recomputed count the exit is unreachable, so the "
            "diagnosis that the fixed numerator causes it is wrong")


class TestItHappensOnRealPackets:
    def test_pruning_makes_the_metric_it_optimises_worse(self):
        model, domain = "deepseek_v3", "software"
        pkts = [_load_universal_directive(model)]
        dp = _load_domain_directive(domain)
        if dp is None:
            pytest.skip("no software domain directive in this clone")
        pkts.append(dp)
        pkts.append(build_interaction_pattern("meta_structured"))
        policy = load_effective_policy(domain=domain, model=model)
        budget = MODEL_COHERENCE_BUDGETS[model]
        C = _count_constraints(policy)
        before = C / max(sum(len(p.text) for p in pkts) // 4, 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out, pruned = _prune_for_coherence(pkts, policy, budget)
        after = C / max(sum(len(p.text) for p in out) // 4, 1)
        assert before > budget, "this fixture no longer triggers pruning"
        assert after > before, (
            f"density improved, {before:.6f} -> {after:.6f}; the inversion is "
            f"gone and C0001 may be fixed")
        assert pruned, "nothing was pruned, so the fixture proves nothing"

    def test_the_constraint_count_really_is_independent_of_the_text(self):
        """The premise. If pruning could lower it, the inversion would not follow."""
        policy = load_effective_policy(domain="software", model="deepseek_v3")
        a = _count_constraints(policy)
        b = _count_constraints(policy)
        assert a == b == _count_constraints(dict(policy)), (
            "the count is not a pure function of the policy dict")
        assert a > 0


class TestTheHarmRateIsNotOverstated:
    def test_only_compositions_that_HAD_a_domain_directive_are_counted(self):
        """Absent is not deleted. A first pass conflated them and inflated 2.8x."""
        had = lost = 0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for d, m in itertools.product(list(DOMAIN_MAP), MODEL_COHERENCE_BUDGETS):
                if _load_domain_directive(d) is None:
                    continue
                had += 1
                c = compose(task_domain=d, model=m,
                            situation=build_interaction_pattern("meta_structured"))
                if "domain" not in {p.layer for p in c.packets}:
                    lost += 1
        assert had >= 20, f"only {had} compositions had a domain directive"
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(lost, had, method="wilson")
        lo_c, hi_c = proportion_confint(lost, had, method="beta")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, lost, had - lost + 1) if lost else 0.0
        assert abs(slo - lo_c) < 1e-9, "statsmodels and scipy disagree"
        assert lost > 0, "no domain directive is deleted any more; recheck the finding"
        assert hi < 0.6, (
            f"the deletion rate rose to [{lo:.4%}, {hi:.4%}]; the parked "
            f"disposition should be revisited at that scale")
