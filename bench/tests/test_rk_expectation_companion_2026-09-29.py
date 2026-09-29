"""Both use cases, and the gate keeps the conservative one (item 4, 2026-09-29).

THE QUESTION. The shipped recursion tracks the NON-DETECTION branch:
`A = sigma*B_minus + (1-sigma)*R` with `B_minus = R(1-q)/(1-qR)`. Astra proposed
the branch-weighted expectation `M = R(1-q*sigma)`. The founder's answer is that
BOTH matter -- measurement of an expended run, and prediction before one.

THE ANSWER, DERIVED IN `scripts/branch_form_semantics_2026-09-29.py` (SymPy + z3,
cross-checked with Wolfram Language): they are not rival estimators of one
quantity. `B_minus` IS `P(flaw | not detected)` by Bayes, so A is a CONDITIONAL;
`M` is the unconditional survival probability, so M is the pre-pass EXPECTATION.
At sigma=1, `A = M / P(not detected)`.

WHY THE GATE IS NOT CHANGED. `A - M = sigma*q*R^2*(1-q)/(1-qR) >= 0` everywhere on
the unit cube, so swapping M in lowers reported residual risk on every archived
triple and makes every convergence threshold easier to pass. A measurement change
that can only loosen gates is not additive. So M is written beside `R_new` as
`R_new_expectation` and no gate reads it.

Every test below EXECUTES the runner. The wiring test drives the real evaluator,
because a keyword typo would grep green.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))

import reference_runner_v3 as R  # noqa: E402

TARGET = "bench/_sk_efficacy_probe_target.py"
SOURCE = 'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
GOOD_FIX = (
    "<<<< SEARCH\n"
    'def divide(a, b):\n    """BUG: no zero check."""\n    return a / b\n'
    "====\n"
    'def divide(a, b):\n    """Guarded."""\n    if b == 0:\n'
    '        raise ZeroDivisionError("b must not be 0")\n    return a / b\n'
    ">>>> REPLACE\n"
)

GRID = [i / 8 for i in range(1, 8)]


class TestItIsTheExpectationForm:
    def test_it_is_the_marginal_survival_probability(self):
        """M = R[(1-q) + q(1-sigma)], with re-injection off."""
        for r0 in GRID:
            for qq in GRID:
                for ss in GRID:
                    want = r0 * ((1 - qq) + qq * (1 - ss))
                    got = R.compute_rk_expectation(r0, qq, ss,
                                                   nu_b=0.0, nu_f=0.0)
                    assert got == pytest.approx(want, abs=1e-12), (r0, qq, ss)

    def test_the_brief_s_worked_pair(self):
        assert R.compute_rk(0.5, 0.8, 1.0, nu_b=0.0, nu_f=0.0) == \
            pytest.approx(1 / 6, abs=1e-12)
        assert R.compute_rk_expectation(0.5, 0.8, 1.0, nu_b=0.0, nu_f=0.0) == \
            pytest.approx(1 / 10, abs=1e-12)

    def test_the_expectation_is_never_above_the_shipped_form(self):
        """The direction that decides the gate question. Strict wherever every
        factor of A - M = sigma*q*R^2*(1-q)/(1-qR) is positive."""
        strict = 0
        for r0 in GRID:
            for qq in GRID:
                for ss in GRID:
                    a = R.compute_rk(r0, qq, ss, nu_b=0.0, nu_f=0.0)
                    m = R.compute_rk_expectation(r0, qq, ss, nu_b=0.0, nu_f=0.0)
                    assert m <= a + 1e-15, (r0, qq, ss, a, m)
                    if m < a - 1e-15:
                        strict += 1
        assert strict == len(GRID) ** 3, strict

    def test_re_injection_is_applied_identically(self):
        """At sigma=0 and q=0 the 2 forms must coincide exactly, re-injection and
        all -- the only way to show phase 3 was not re-derived differently."""
        for nb, nf in ((0.05, 0.20), (0.0, 0.0), (0.6, 0.7)):
            for r0 in GRID:
                assert R.compute_rk(r0, 0.0, 0.5, nu_b=nb, nu_f=nf) == \
                    pytest.approx(R.compute_rk_expectation(
                        r0, 0.0, 0.5, nu_b=nb, nu_f=nf), abs=1e-15)
                assert R.compute_rk(r0, 0.7, 0.0, nu_b=nb, nu_f=nf) == \
                    pytest.approx(R.compute_rk_expectation(
                        r0, 0.7, 0.0, nu_b=nb, nu_f=nf), abs=1e-15)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"),
                                     float("-inf"), "not a number", None])
    def test_non_finite_inputs_resolve_to_the_conservative_end(self, bad):
        """`_rk_finite` duplicates `compute_rk`'s inline clamp, so the clamp is
        EXECUTED rather than assumed. Each slot must resolve to its documented
        worst case -- unknown risk to MAXIMUM, unknown detection and efficacy to
        ZERO -- which can only make the number stricter."""
        worst = [1.0, 0.0, 0.0, 1.0, 1.0]
        finite = [0.5, 0.5, 0.5, 0.05, 0.20]
        for slot in range(5):
            bad_args = list(finite); bad_args[slot] = bad
            worst_args = list(finite); worst_args[slot] = worst[slot]
            got = R.compute_rk_expectation(*bad_args)
            assert got == pytest.approx(
                R.compute_rk_expectation(*worst_args), abs=1e-12), (slot, bad)
            assert got >= R.compute_rk_expectation(*finite) - 1e-12, (slot, bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), None])
    def test_a_corrupt_q_or_efficacy_collapses_both_forms_together(self, bad):
        """Where the 2 forms MUST coincide: at q=0 or sigma=0 no detection branch
        exists, so conditional and expectation are the same number. A clamp that
        drifted between the 2 functions would break this."""
        for slot in (1, 2):
            args = [0.5, 0.5, 0.5, 0.05, 0.20]
            args[slot] = bad
            assert R.compute_rk(*args) == pytest.approx(
                R.compute_rk_expectation(*args), abs=1e-12), (slot, bad)


class TestItIsWired:
    def test_the_evaluator_records_the_expectation_beside_the_gated_number(self):
        """THE WIRING, CALLED not grepped. An addition nothing reaches is not
        additive."""
        registry = R.FindingRegistry()
        registry.entries["C-EXP"] = {
            "status": "OPEN",
            "proposed_fix": GOOD_FIX,
            "severity": "critical",
            "model": "SIM-A",
            "round": 0,
        }
        baseline = R._capture_baseline(SOURCE, source_path=TARGET)
        R._evaluate_sk_for_findings(
            registry, SOURCE, TARGET, baseline, round_idx=0, test_cmd=None,
        )
        res = registry.entries["C-EXP"]["sk_result"]
        assert "R_new" in res, res
        assert "R_new_expectation" in res, (
            "the expectation is not reaching the report; the call site is not "
            f"wired: {sorted(res)}")
        assert res["R_new_expectation"] <= res["R_new"] + 1e-12, res

    def test_both_fields_come_from_the_2_forms_at_the_SAME_q(self):
        """The gated number is still the CONDITIONAL form, and the companion is
        the expectation of the same update.

        `q` is not in the record, so it is recovered by bisection (compute_rk is
        monotone decreasing in q) from `R_new`, and the recovered value must then
        reproduce `R_new_expectation` through the OTHER function. Nothing here is
        read from source text, and the 2 fields cannot both satisfy this if either
        formula moved.
        """
        registry = R.FindingRegistry()
        registry.entries["C-EXP"] = {
            "status": "OPEN",
            "proposed_fix": GOOD_FIX,
            "severity": "critical",
            "model": "SIM-A",
            "round": 0,
        }
        baseline = R._capture_baseline(SOURCE, source_path=TARGET)
        R._evaluate_sk_for_findings(
            registry, SOURCE, TARGET, baseline, round_idx=0, test_cmd=None,
        )
        res = registry.entries["C-EXP"]["sk_result"]
        R_old, sk = res["R_old"], res["sk"]
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if R.compute_rk(R_old, mid, sk) > res["R_new"]:
                lo = mid
            else:
                hi = mid
        q = (lo + hi) / 2
        assert R.compute_rk(R_old, q, sk) == pytest.approx(res["R_new"], abs=1e-9), q
        assert R.compute_rk_expectation(R_old, q, sk) == pytest.approx(
            res["R_new_expectation"], abs=1e-9), (q, res)
        assert res["R_new_expectation"] < res["R_new"], (
            "the 2 fields are equal, so either q or sigma collapsed and the "
            "companion is not exercising the branch weighting")


class TestTheDerivationIsReachedBySuite:
    def test_the_stored_derivation_runs_clean(self):
        """The falsifier behind this item is EXECUTED by the suite, not archived
        beside it. An addition nothing reaches is not additive, and that applies
        to a stored derivation as much as to a flag."""
        import subprocess
        script = BENCH.parent / "scripts" / "branch_form_semantics_2026-09-29.py"
        assert script.is_file(), script
        r = subprocess.run([sys.executable, str(script)], cwd=BENCH.parent,
                           capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        assert r.returncode == 0, out[-1500:]
        assert "FALSIFIER-CLEAN" in out, out[-1500:]
        assert "A >= M proved" in out, out[-1500:]
