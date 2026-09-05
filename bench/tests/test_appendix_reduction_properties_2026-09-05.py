"""Every reduction property the appendix CLAIMS, executed — and each test proves
it can FAIL.

WHY THIS FILE EXISTS. `docs/MATHEMATICAL_APPENDIX.md` carries many statements
that something was "SymPy verified", and 18 statements of the form "X reduces to
Y under condition Z". Measured 2026-09-05: exactly 1 test file in `bench/tests/`
imports sympy, and it tests a calibrator rather than any appendix identity. The
model's verification lived in prose, which is the source-text defect one level
up: a sentence saying a thing was verified is a claim ABOUT evidence.

WHY IT WAS REWRITTEN THE SAME DAY. The first version was REFUTED by cc2 in panel
review, and the refutation was right. Three of its assertions were SUBSTITUTION
TAUTOLOGIES: `expr.subs(X, Y) - expr_with_Y` is 0 for ANY expression, so the test
passed with the model replaced by the constant 42, by `sin(R)+q**7`, and by
`atan(R*q)`. Executed and confirmed before rewriting. The accompanying P-pass
could not detect this, because it perturbed the SUBSTITUTION POINT and not the
EXPRESSION — cc2 demonstrated it certifying a deliberately garbage model as
non-vacuous. And the P-pass itself existed only as prose in a commit message,
with no committed script, one day after this project adopted the rule that a
measured result must travel with the code that produced it.

THE FIX, AND IT IS STRUCTURAL. Every test below asserts TWO things: that the
residual is exactly 0 under the appendix's stated condition, AND that it is
non-zero for at least one WRONG model. A test that cannot fail is not evidence,
so the discrimination lives in the test rather than in a separate script that can
be lost or left uncommitted.

WHAT IS NOT CLAIMED. The earlier version cited "32 SymPy verifications" in the
appendix. cc2 could not reproduce 32 under any counting rule it tried (43, 39,
41, 68, 22 depending on the rule), and this file states no such figure. The 18
reduction statements are reproducible from a stated regex and that figure stands.
"""

import itertools
import math
import sys

import sympy as sp


# ── helpers ──────────────────────────────────────────────────────────────────

def _zero(expr):
    return sp.simplify(sp.together(expr)) == 0


def _witness_closed(expr):
    """An off-condition residual that is already fully substituted.

    The call sites pin the off-condition point inside the expression itself, so
    there are no free symbols left that matter: nsimplify gives an exact value.
    Where free symbols DO remain, they are positive reals and the expression is a
    product or sum in them, so a non-zero exact coefficient is a witness.
    """
    val = sp.together(expr)
    free = val.free_symbols
    if free:
        point = {s: sp.Rational(1, 3 + i) for i, s in enumerate(sorted(free, key=str))}
        val = val.subs(point)
    return sp.nsimplify(sp.simplify(val)) != 0


def _witness(expr, point):
    """Discrimination by an EXACT RATIONAL WITNESS, not by failure to simplify.

    REFUTED BY fable, panel review 2026-09-05, and the refutation is deep.
    The previous helper was `simplify(expr) != 0`, which means "simplify did not
    reduce this to 0" and NOT "this is provably non-zero". Under Richardson's
    theorem, equality involving exp, log and trigonometric functions is
    undecidable in general, so a genuinely ZERO residual can survive simplify and
    be certified as discrimination -- a wrong-model check that passes while
    proving nothing. Executed: simplify DOES return 0 for exp(log(x)) - x and for
    cos(x)**2 + sin(x)**2 - 1, so the hazard is not hypothetical, it is only that
    those particular cases happen to be easy.

    That is the Q4 rule of this very panel applied to the test suite's own
    epistemics: an UNDISCHARGED result was being used to CONFIRM.

    A discrimination claim is an EXISTS-claim -- "there is a point where S and F
    differ" -- so ONE exact rational witness discharges it completely. Rationals,
    not floats: a float comparison reintroduces the tolerance question this whole
    module exists to remove.
    """
    val = sp.nsimplify(sp.together(expr).subs(point))
    return val != 0


class TestSection1_1_TheUnifiedEquation:

    def test_the_recursion_reproduces_the_batch_posterior(self):
        """L182/L184 — THE REAL THEOREM, and the one the first version missed.

        Unrolling the recursive update one factor at a time must reproduce the
        batch posterior with m = prod(1 - q_j). The first version asserted
        `step(step(pi,q1),q2) == step(Rk,q2).subs(Rk, step(pi,q1))`, which is the
        SAME EXPRESSION TREE and therefore true for any `step` whatsoever.
        """
        pi = sp.Symbol('pi', positive=True)
        q = sp.symbols('q_1 q_2 q_3', positive=True)
        step = lambda R, k: R * (1 - k) / (1 - k * R)
        for n in (1, 2, 3):
            R = pi
            for j in range(n):
                R = step(R, q[j])
            m = sp.prod([(1 - q[j]) for j in range(n)])
            assert _zero(R - (pi * m) / ((1 - pi) + pi * m)), f"failed at n={n}"

    def test_that_theorem_FAILS_for_a_wrong_update(self):
        """The discrimination. Includes a plausible-but-wrong update, not only
        obvious nonsense, because `R*(1-q)` is the mistake a reader might make."""
        pi = sp.Symbol('pi', positive=True)
        q1, q2 = sp.symbols('q_1 q_2', positive=True)
        m = (1 - q1) * (1 - q2)
        batch = (pi * m) / ((1 - pi) + pi * m)
        for bad, label in ((lambda R, k: sp.Integer(42), "42"),
                           (lambda R, k: sp.sin(R) + k ** 7, "sin(R)+q^7"),
                           (lambda R, k: R * (1 - k), "R*(1-q), plausible but wrong")):
            R = bad(bad(pi, q1), q2)
            assert _witness_closed(R - batch), f"a wrong update passed: {label}"

    def test_the_closed_form_at_a_symmetric_prior(self):
        """L107: K=1, d_i=1, all p_ik=p, pi=1/2 -> R_n = (1-p)^n / (1+(1-p)^n).

        This is the BATCH-form reduction. It is a weaker statement than the
        recursion theorem above and is kept as a separate test rather than a
        replacement for it — cc2's point, and correct: the two are different
        theorems and the earlier commit quietly retargeted from the harder to
        the easier one while presenting it as a simplification.
        """
        p, n, pi = sp.symbols('p n pi', positive=True)
        m = (1 - p) ** n
        posterior = (pi * m) / ((1 - pi) + pi * m)
        assert _zero(posterior.subs(pi, sp.Rational(1, 2)) - m / (1 + m))
        assert _witness_closed(posterior.subs(pi, sp.Rational(1, 4)) - m / (1 + m))

    def test_perfect_detection_drives_residual_risk_to_zero(self):
        """L77: m_k -> 0 implies R_n -> 0 regardless of the prior."""
        pi, m = sp.symbols('pi m', positive=True)
        R = (pi * m) / ((1 - pi) + pi * m)
        assert sp.limit(R, m, 0) == 0
        assert sp.limit(R, m, 1) == pi            # L78: total miss leaves the prior
        # DISCRIMINATION, added after fable identified this test as lacking it
        # (panel review 2026-09-05). Both limits above are true of the appendix's
        # posterior; neither would fail for a WRONG posterior that happens to
        # share its endpoints. The interior value is what separates them.
        wrong = pi * m                             # same endpoints, wrong interior
        assert sp.limit(wrong, m, 0) == 0 and sp.limit(wrong, m, 1) == pi
        assert _witness_closed(R.subs({pi: sp.Rational(1, 2), m: sp.Rational(1, 2)})
                               - wrong.subs({pi: sp.Rational(1, 2), m: sp.Rational(1, 2)}))


class TestSection0_1_TheIsingBranch:

    def test_zero_coupling_reduces_to_the_independent_product(self):
        """L36: psi_ij = 0 -> exponent 1, Z = 1, independent product."""
        q1, q2, psi = sp.symbols('q_1 q_2 psi', positive=True)
        assert _zero((q1 * q2 * sp.exp(psi)).subs(psi, 0) - q1 * q2)
        assert _witness_closed((q1 * q2 * sp.exp(psi)).subs(psi, 2) - q1 * q2)
        Z = sum((q1 ** a * (1 - q1) ** (1 - a)) * (q2 ** b * (1 - q2) ** (1 - b))
                * sp.exp(psi * a * b) for a in (0, 1) for b in (0, 1))
        assert _zero(Z.subs(psi, 0) - 1)
        assert _witness_closed(Z.subs(psi, 2) - 1)


class TestSection1_6_Stage6ReducesToStage5:

    def _eta(self):
        ei, ce, nk = sp.symbols('eta_int c_ext nu_k', positive=True)
        return ei * (1 - ce * (1 - nk)), ei, ce, nk

    def test_fully_novel_carries_no_penalty(self):
        eta, ei, ce, nk = self._eta()
        assert _zero(eta.subs(nk, 1) - ei)
        assert _witness_closed(eta.subs({nk: sp.Rational(1, 2), ce: sp.Rational(1, 2)}) - ei)

    def test_no_search_degrades_to_stage_5(self):
        eta, ei, ce, nk = self._eta()
        assert _zero(eta.subs(ce, 0) - ei)
        assert _witness_closed(eta.subs({ce: sp.Rational(1, 2), nk: sp.Rational(1, 2)}) - ei)

    def test_the_stated_partial_derivatives(self):
        """L290/L291, found by cc2 as untested and cheap."""
        eta, ei, ce, nk = self._eta()
        assert _zero(sp.diff(eta, nk) - ce * ei)
        assert _zero(sp.diff(eta, ce) - ei * (nk - 1))
        # DISCRIMINATION, added after fable identified this test as lacking it.
        # A wrong eta with the same value at one point would still fail these,
        # so the check is on the DERIVATIVE of a wrong model.
        wrong = ei * (1 - ce * (1 - nk) ** 2)      # differs only in the exponent
        assert _witness_closed(sp.diff(wrong, nk) - ce * ei)


class TestTheDetectionExtensions:

    def test_delivery_feasibility_at_one(self):
        f, d, p = sp.symbols('f_del d p', positive=True)
        assert _zero((f * d * p).subs(f, 1) - d * p)
        assert _witness_closed((f * d * p).subs(f, sp.Rational(1, 2)) - d * p)

    def test_delivery_and_format_both_at_one(self):
        f, ph, d, p = sp.symbols('f_del phi d p', positive=True)
        assert _zero((f * ph * d * p).subs({f: 1, ph: 1}) - d * p)
        assert _witness_closed((f * ph * d * p).subs({f: 1, ph: sp.Rational(1, 2)}) - d * p)

    def test_class_specific_diversity_collapses_ACROSS_CLASSES(self):
        """L420 — CORRECTED. cc2 refuted the first version, which collapsed the
        PASS index inside a single class. The appendix sums over classes k and
        multiplies over passes i, so the claim is about d_ik -> d_i FOR ALL k.
        Built here with 2 passes and 2 classes so the class index exists at all.
        """
        w1, w2, di = sp.symbols('w_1 w_2 d_i', positive=True)
        p11, p12, p21, p22 = sp.symbols('p_11 p_12 p_21 p_22', positive=True)
        d11, d12, d21, d22 = sp.symbols('d_11 d_12 d_21 d_22', positive=True)
        general = (w1 * (1 - (1 - d11 * p11) * (1 - d21 * p21))
                   + w2 * (1 - (1 - d12 * p12) * (1 - d22 * p22)))
        structured = (w1 * (1 - (1 - di * p11) * (1 - di * p21))
                      + w2 * (1 - (1 - di * p12) * (1 - di * p22)))
        collapse = {d11: di, d12: di, d21: di, d22: di}
        assert _zero(general.subs(collapse) - structured)
        partial = {d11: di, d12: di, d21: di, d22: di / 2}   # one class differs
        assert _witness_closed(general.subs(partial) - structured)

    def test_zero_deferral(self):
        tau, Fd, Ff = sp.symbols('tau F_d F_f', positive=True)
        assert _zero((sp.exp(-tau) * (Fd / Ff)).subs(tau, 0) - Fd / Ff)
        assert _witness_closed((sp.exp(-tau) * (Fd / Ff)).subs(tau, 1) - Fd / Ff)

    def test_neutral_decomposition(self):
        e, d, p = sp.symbols('eta_dec d p', positive=True)
        assert _zero((e * d * p).subs(e, 1) - d * p)
        assert _witness_closed((e * d * p).subs(e, sp.Rational(1, 2)) - d * p)


class TestSeverityAndScope:

    def test_severity_equal_to_weighting_reduces_L_n_to_R_n(self):
        """L598 — CORRECTED. The first version asserted (s_k*R).subs(s_k, w_k)
        equals w_k*R, which holds for cos(R)+B**5 as well. The claim is about
        SUMS over classes, so it is tested as a sum and shown to fail when the
        severities are not the weights.
        """
        w1, w2, s1, s2, R1, R2 = sp.symbols('w_1 w_2 s_1 s_2 R_1 R_2', positive=True)
        L_n = s1 * R1 + s2 * R2
        R_n = w1 * R1 + w2 * R2
        assert _zero(L_n.subs({s1: w1, s2: w2}) - R_n)
        assert _witness_closed(L_n.subs({s1: w1, s2: 2 * w2}) - R_n)

    def test_no_domain_variables(self):
        E, M, al, lam, V = sp.symbols('E M alpha lam V_s', positive=True)
        base = E * (al + (1 - al) * M)
        assert _zero((base * (1 + lam * V)).subs(V, 0) - base)
        assert _witness_closed((base * (1 + lam * V)).subs(V, 1) - base)

    def test_no_follow_step_reduces_FFF_to_standard_confer(self):
        sig, D = sp.symbols('sigma D_found', positive=True)
        assert _zero((D * (1 + sig)).subs(sig, 0) - D)
        assert _witness_closed((D * (1 + sig)).subs(sig, 1) - D)


class TestSection7_1_TheDuaneRelationship:
    """L828 — cc2 refuted its exclusion as untestable, and was right."""

    def test_the_inverse_square_root_law_is_the_beta_one_half_case(self):
        """lambda(t) = (beta/eta)(t/eta)^(beta-1) is proportional to t^(-1/2)
        exactly at beta = 1/2, with sigma = 1/(2*sqrt(eta)).
        """
        t, eta, beta = sp.symbols('t eta beta', positive=True)
        lam = (beta / eta) * (t / eta) ** (beta - 1)
        at_half = sp.simplify(lam.subs(beta, sp.Rational(1, 2)))
        sigma = 1 / (2 * sp.sqrt(eta))
        assert _zero(at_half - sigma / sp.sqrt(t))
        assert _witness_closed(sp.simplify(lam.subs(beta, sp.Rational(3, 4))) - sigma / sp.sqrt(t))


class TestSection7_2_TheAbstractionIndex:

    def test_a_bare_finding_reduces_the_index_to_confidence_alone(self):
        c, g1, g2, We, Wc, Ncm, Dref = sp.symbols(
            'c c_G1 c_G2 W_e W_c N_cm D_ref', positive=True)
        H = c * 1 * sp.log(sp.E + We / (Wc + 1)) * (
            1 + g1 * sp.log(1 + Ncm) + g2 * sp.log(1 + Dref))
        assert _zero(H.subs({We: 0, Ncm: 0, Dref: 0}) - c)
        assert _witness_closed(H.subs({We: 0, Ncm: 1, Dref: 0}) - c)

    def test_the_density_term_is_one_ONLY_at_zero_evidence(self):
        """SOLVED rather than spot-checked. The first version sampled
        (W_e, W_c) = (4, 4), which contradicted this file's own header.
        """
        # W_e MUST be nonnegative, not positive. Declaring it positive excludes
        # 0 from the solution domain, so sympy correctly returns [] and the test
        # fails against a true claim — the assumption contradicted the thing
        # being proved. Caught by running it, 2026-09-05.
        We = sp.Symbol('W_e', nonnegative=True)
        Wc = sp.Symbol('W_c', positive=True)
        rho = sp.log(sp.E + We / (Wc + 1))
        assert sp.solve(sp.Eq(rho, 1), We) == [0]
        # and it is strictly greater than 1 anywhere evidence exists
        assert sp.simplify(rho.subs({We: 4, Wc: 4})) > 1

class TestSection0_1_TheBoundednessConstraintIsMisjustified:
    """L38 carries a SymPy-attributed justification that does not hold.

    FOUND BY cc2, panel review 2026-09-05, and reproduced here before recording.
    The appendix states: "The coupling constants must satisfy
    sum(psi_ij) <= -sum(log(1 - q_i)) to ensure all state probabilities remain
    non-negative. (Verified by SymPy, March 2026.)"

    Non-negativity is UNCONDITIONAL. Each state weight is a product of
    non-negative Bernoulli factors times exp(sum psi x_i x_j), and exp(x) > 0 for
    every real x, so no real coupling can produce a negative weight. Measured at
    q = 0.9, where the stated bound is 4.6052: the minimum state weight is 0.01
    at psi = 0, at psi = 4.6052, and at psi = 1000 alike.

    Nor is the constraint needed for P(x) <= 1. Z is the sum of the same
    non-negative weights, so P(x) = w/Z <= 1 by construction, which the appendix
    itself says one line earlier at L34.

    THIS TEST DOES NOT DELETE THE CONSTRAINT. The constraint may well be needed
    for something else — numerical conditioning is the obvious candidate, since
    exp(1000) overflows a float and the probability computation returns NaN. What
    is refuted is the stated REASON. Amending the appendix is a founder decision,
    so this pins the fact and leaves the document alone.
    """

    def _weight(self, a, b, q, psi):
        return ((q ** a * (1 - q) ** (1 - a)) * (q ** b * (1 - q) ** (1 - b))
                * sp.exp(psi * a * b))

    def test_non_negativity_holds_far_beyond_the_stated_bound(self):
        q = sp.Rational(9, 10)
        bound = -2 * sp.log(1 - q)                     # the appendix's own bound
        for psi in (sp.Integer(0), bound, sp.Integer(1000)):
            weights = [self._weight(a, b, q, psi)
                       for a in (0, 1) for b in (0, 1)]
            assert all(w >= 0 for w in weights), f"a weight went negative at psi={psi}"


    def test_the_all_ones_bound_is_NOT_sufficient_for_n_at_least_3(self):
        """MY OWN PROPOSED FIX WAS WRONG. This test records the refutation.

        The 2026-09-05 pinned test derived, from the all-ones state, that an
        UNNORMALISED variant would need sum(psi) <= -sum(log q_i), and offered
        that as the correction to the appendix. A panel reviewer showed it is
        not sufficient once n >= 3, because a proper SUBSET can bind harder than
        the full state. Reproduced here with exact rationals, and cross-checked
        against mpmath and Wolfram on the same day, all returning 19 exactly.

        The construction: put the ENTIRE all-ones budget on a single pair. The
        all-ones inequality is then satisfied with equality, and yet the 2-element
        state carrying that pair has unnormalised weight (1-q)/q, which exceeds 1
        for every q < 1/2.
        """
        n = 3
        q = sp.Rational(1, 20)
        budget = -n * sp.log(q)                    # the all-ones bound
        psi = {(0, 1): budget}                     # whole budget on one pair

        def weight(S):
            pr = sp.Integer(1)
            for i in range(n):
                pr *= q if i in S else (1 - q)
            coupled = sum(psi.get((a, b), 0)
                          for a, b in itertools.combinations(sorted(S), 2))
            return pr * sp.exp(coupled)

        # the all-ones inequality is satisfied, with equality
        assert _zero(sum(psi.values()) - budget)
        assert _zero(weight({0, 1, 2}) - 1)

        # ...and yet a SUBSET exceeds 1, by a wide margin
        offender = sp.simplify(weight({0, 1}))
        assert offender == 19, f"expected exactly 19, got {offender}"
        assert _zero(offender - (1 - q) / q)

    def test_the_per_subset_condition_is_the_correct_one(self):
        """The necessary and sufficient form, which the appendix now states.

        w(S) <= 1  <=>  sum_{i<j in S} psi_ij
                        <= -sum_{i in S} log q_i - sum_{i not in S} log(1 - q_i)

        Checked as an identity on log w(S), so it holds for every S rather than
        for a sampled few -- the discharge rule this project adopted says a
        sampled agreement may never CONFIRM a universal claim.
        """
        n = 3
        qs = [sp.Symbol(f'q_{i}', positive=True) for i in range(n)]
        p01 = sp.Symbol('psi_01', real=True)
        S = {0, 1}

        pr = sp.Integer(1)
        for i in range(n):
            pr *= qs[i] if i in S else (1 - qs[i])
        log_w = sp.expand_log(sp.log(pr * sp.exp(p01)), force=True)

        slack = p01 + sp.log(qs[0]) + sp.log(qs[1]) + sp.log(1 - qs[2])
        assert _zero(log_w - slack)

        # discrimination: the ALL-ONES form is a different, weaker quantity
        all_ones = p01 + sp.log(qs[0]) + sp.log(qs[1]) + sp.log(qs[2])
        assert _witness_closed(slack - all_ones)

    def test_the_complement_error_crosses_over_at_one_half(self):
        """The stated bound is not uniformly conservative -- it flips at q = 1/2.

        Below 1/2 it over-constrains; ABOVE 1/2 it under-constrains, admitting
        couplings it was meant to exclude. That half is the reportable one, and
        neither panel seat reported it.
        """
        q = sp.Symbol('q', positive=True)
        stated = -sp.log(1 - q)          # what the appendix said
        derived = -sp.log(q)             # the all-ones requirement
        crossover = sp.solve(sp.Eq(stated, derived), q)
        assert crossover == [sp.Rational(1, 2)], crossover

        below = (stated - derived).subs(q, sp.Rational(1, 20))
        above = (stated - derived).subs(q, sp.Rational(19, 20))
        assert below < 0, "below 1/2 the stated bound should be the stricter one"
        assert above > 0, "above 1/2 the stated bound should be the looser one"

    def test_the_bound_is_not_an_overflow_guard_either(self):
        """The remaining candidate justification, also refuted.

        float64 exp overflows near 709.78; the stated bound at q=0.05, n=3 is
        0.1539. It is 3 orders of magnitude away from being an overflow guard.
        """
        overflow = math.log(sys.float_info.max)
        stated = float(-3 * sp.log(1 - sp.Rational(1, 20)))
        assert 709 < overflow < 710
        assert stated < 1
        assert overflow / stated > 1000

    def test_the_reason_is_exp_being_strictly_positive(self):
        """The one-line argument, stated symbolically so it cannot be mislaid."""
        x = sp.Symbol('x', real=True)
        assert sp.exp(x).is_positive is True

class TestTheReductionsTheRegexCouldNotSee:
    """L516, L838, L856 — labelled "Reduction property" but phrased "X = Y".

    Both reviewers found these independently on 2026-09-05. The enumeration
    regex looked for "reduces to | collapses to | special case | vanish", so
    three statements that carry the label but state an equation were invisible
    to it. The true count of reduction statements is therefore at least 21, not
    18, and the earlier figure is corrected here rather than left standing.
    """

    def test_distinct_operational_setups_leave_pure_architectural_diversity(self):
        """L516: d_config = 1 for all pairs -> d_ik = d_weight."""
        dw, dc = sp.symbols('d_weight d_config', positive=True)
        assert _zero((dw * dc).subs(dc, 1) - dw)
        assert _witness_closed((dw * dc).subs(dc, sp.Rational(1, 2)) - dw)

    def test_no_re_injection_gives_the_standard_duane_model(self):
        """L838: nu = 0 -> lambda_ext = lambda."""
        lam, nu, delta = sp.symbols('lambda nu Delta', positive=True)
        assert _zero((lam + nu * delta).subs(nu, 0) - lam)
        assert _witness_closed((lam + nu * delta).subs(nu, sp.Rational(1, 2)) - lam)

    def test_no_restart_reduces_the_full_model_to_the_extended_one(self):
        """L856, both clauses: I = 0 -> lambda_full = lambda_ext; and with
        nu = 0 as well -> lambda_full = lambda."""
        lam, nu, delta, mu, I, D = sp.symbols(
            'lambda nu Delta mu I D_seen', positive=True)
        ext = lam + nu * delta
        full = ext + mu * I * D
        assert _zero(full.subs(I, 0) - ext)
        assert _witness_closed(full.subs(I, 1) - ext)
        assert _zero(full.subs({I: 0, nu: 0}) - lam)

    def test_the_duane_intensity_decreases_for_beta_below_one(self):
        """L840, a SymPy-attributed claim the file did not cover."""
        n, eta, beta = sp.symbols('n eta beta', positive=True)
        lam = (beta / eta) * (n / eta) ** (beta - 1)
        d = sp.diff(lam, n)
        assert d.subs({beta: sp.Rational(1, 2), eta: 1, n: 2}) < 0
        assert d.subs({beta: 2, eta: 1, n: 2}) > 0          # and increases above 1


class TestTheGnReductionTable:
    """L675-682 — excluded as "table rows", which dropped the appendix's
    strongest reductions. Both reviewers said so independently and both
    executed them. G_n is the human-in-the-loop model at L645.
    """

    def _G(self):
        w, CM, CH, rho = sp.symbols('w C_M C_H rho_MH', positive=True)
        return w * (1 - (1 - CM) * (1 - CH * (1 - rho))), w, CM, CH, rho

    def test_no_human_passes_reduces_G_n_to_F_n(self):
        """n_H = 0 makes C_H an empty product, so C_H = 1 - 1 = 0."""
        G, w, CM, CH, rho = self._G()
        assert _zero(G.subs(CH, 0) - w * CM)
        assert _witness_closed(G.subs(CH, sp.Rational(1, 2)) - w * CM)

    def test_the_exact_human_residual_and_its_complete_zero_set(self):
        """The appendix now STATES the residual instead of enumerating conditions.

        G_n - w*C_M = w * C_H * (1 - rho_MH) * (1 - C_M)

        My earlier claim that the row needs "n_H = 0" as a NECESSARY condition was
        wrong -- 3 panel seats said so independently on 2026-09-05 and they were
        right. n_H = 0 is one SUFFICIENT route (via C_H = 0) and never necessary.
        Wolfram's Reduce supplied a 4th branch, w = 0, that the enumeration missed;
        that is precisely why the appendix now gives the residual rather than a list.
        """
        G, w, CM, CH, rho = self._G()
        residual = sp.factor(sp.simplify(G - w * CM))
        assert _zero(residual - w * CH * (1 - rho) * (1 - CM))

        # every branch of the zero set, including the one enumeration missed
        for name, sub in [("C_H=0", {CH: 0}), ("rho_MH=1", {rho: 1}),
                          ("C_M=1", {CM: 1}), ("w=0", {w: 0})]:
            assert _zero(residual.subs(sub)), f"{name} should kill the residual"

        # discrimination: with none of them, the residual is genuinely non-zero
        assert _witness_closed(residual)

    def test_full_priming_reduces_G_n_to_F_n(self):
        """rho_MH = 1: the human's contribution is fully absorbed."""
        G, w, CM, CH, rho = self._G()
        assert _zero(G.subs(rho, 1) - w * CM)
        assert _witness_closed(G.subs(rho, sp.Rational(1, 2)) - w * CM)

    def test_full_independence_gives_the_multiplicative_combination(self):
        G, w, CM, CH, rho = self._G()
        assert _zero(G.subs(rho, 0) - w * (1 - (1 - CM) * (1 - CH)))
        assert _witness_closed(G.subs(rho, sp.Rational(1, 2))
                        - w * (1 - (1 - CM) * (1 - CH)))

    def test_no_methodology_reduces_human_detection_to_the_expertise_floor(self):
        """M = 0 -> p_H = alpha * E."""
        E, M, al = sp.symbols('E M alpha', positive=True)
        f = E * (al + (1 - al) * M)
        assert _zero(f.subs(M, 0) - al * E)
        assert _witness_closed(f.subs(M, sp.Rational(1, 2)) - al * E)

    def test_the_C_of_n_ROW_IS_DEFECTIVE_AS_STATED(self):
        """cc2's finding, reproduced: the row "K=1, d=1, uniform p -> C(n)"
        omits its necessary condition n_H = 0.

        With human passes present the G_n model retains the C_H term, so it does
        NOT reduce to the corroboration model. This test pins the defect rather
        than the claim: it asserts the row is WRONG without n_H = 0, and right
        with it. Amending the appendix is a founder decision.
        """
        G, w, CM, CH, rho = self._G()
        # with a human stream present AND no priming, G_n keeps a C_H term
        assert _witness_closed(G.subs({rho: 0, CH: sp.Rational(1, 2)}) - w * CM)
        # CORRECTED 2026-09-05 after cgpt and fable BOTH refuted the first fix
        # independently: n_H = 0 is SUFFICIENT but NOT NECESSARY. Full priming
        # removes the human contribution just as completely, because the term is
        # C_H * (1 - rho_MH) and rho_MH = 1 annihilates it whatever C_H is.
        # The row's missing condition is therefore a DISJUNCTION.
        assert _zero(G.subs({rho: 0, CH: 0}) - w * CM)                  # n_H = 0
        assert _zero(G.subs({rho: 1, CH: sp.Rational(1, 2)}) - w * CM)  # rho_MH = 1
        # and it holds for ANY C_H once fully primed, which is the point
        assert _zero(G.subs({rho: 1}) - w * CM)
