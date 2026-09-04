"""Every reduction property the appendix CLAIMS, executed rather than read.

WHY THIS FILE EXISTS. `docs/MATHEMATICAL_APPENDIX.md` carries 32 statements that
something was "SymPy verified" or "SymPy + Wolfram cross-validated", and 18
statements of the form "X reduces to Y under condition Z". Measured 2026-09-05:
exactly 1 test file in `bench/tests/` imports sympy at all, and it is
`test_shadow_stage6_calibrator.py`, which tests a calibrator rather than any
appendix identity. So the verification of the mathematical model lived entirely
in prose.

That is the same defect as a test asserting on source text, one level up. A
sentence saying a thing was verified is a claim ABOUT evidence, not evidence.
Both panel reviewers raised it independently on 2026-09-04 -- cc2: "26 lines
claiming SymPy verified, and zero test files execute any of them ... the
verification lives in prose, which is the source-text pattern C1/C4 just
abolished for code"; fable: "one parametrized identity-test executing S against
F over declared D".

WHAT IS AND IS NOT ASSERTED HERE. Each test states the appendix's condition and
checks the identity SYMBOLICALLY, for all values of the free symbols, not at
sampled points. Where an identity holds for all n or all p, that is what is
checked -- a spot check at n=1..8 would be the sampling the reduction criterion
says can refute but never admit.

Four of the 18 statements are NOT testable as identities and are deliberately
absent: "each stage is a strict generalisation of the previous" (L157), "every
simpler model is a special case of G_n" (L684), the Duane/inverse-square-root
relationship (L828), and the Bayesian-provenance note (L1991). Those are
architectural or historical claims, not equations. Their absence is stated so
that a reader does not mistake 13 for 18.
"""

import sympy as sp


class TestSection1_1_TheUnifiedEquation:
    """§1.1, the equation the whole model rests on."""

    def test_the_recursive_form_collapses_to_the_closed_form_for_ALL_n(self):
        """L107: K=1, d_i=1, all p_ik=p, pi=0.5  ->  R_n = (1-p)^n / (1+(1-p)^n).

        Checked as an algebraic identity in n and p simultaneously, not sampled.
        cc2 made this point on 2026-09-04: an earlier verification used n=1..8
        plus an induction step plus mpmath at 30 dp, when substituting
        m = (1-p)^n into the appendix's own posterior gives it in one line. The
        elaborate check was weaker than the theorem deserved.
        """
        p, n, pi = sp.symbols('p n pi', positive=True)
        m = (1 - p) ** n
        posterior = (pi * m) / ((1 - pi) + pi * m)          # appendix line 71
        closed = m / (1 + m)                                 # appendix line 107
        assert sp.simplify(posterior.subs(pi, sp.Rational(1, 2)) - closed) == 0

    def test_the_prior_vanishes_from_the_update(self):
        """L184: once R_k(i) exists, the update depends only on R and the next q."""
        pi, q1, q2, Rk = sp.symbols('pi q_1 q_2 R_k', positive=True)
        step = lambda R, q: R * (1 - q) / (1 - q * R)
        via_prior = step(step(pi, q1), q2)
        via_state = step(Rk, q2).subs(Rk, step(pi, q1))
        assert sp.simplify(via_prior - via_state) == 0
        # and pi appears nowhere in the update rule itself
        assert pi not in step(Rk, q2).free_symbols


class TestSection0_1_TheIsingBranch:
    def test_zero_coupling_reduces_to_the_independent_product(self):
        """L36: psi_ij = 0 for all pairs -> the exponent is 1 and Z = 1."""
        q1, q2, psi = sp.symbols('q_1 q_2 psi', positive=True)
        # two passes, both failing: x_1 = x_2 = 1
        coupled = q1 * q2 * sp.exp(psi * 1 * 1)
        independent = q1 * q2
        assert sp.simplify(coupled.subs(psi, 0) - independent) == 0
        # Z sums over all 2^n states; at psi=0 it is the product of normalised
        # Bernoullis, which is 1 by construction.
        Z = sum(
            (q1 ** a * (1 - q1) ** (1 - a)) * (q2 ** b * (1 - q2) ** (1 - b))
            * sp.exp(psi * a * b)
            for a in (0, 1) for b in (0, 1)
        )
        assert sp.simplify(Z.subs(psi, 0) - 1) == 0


class TestSection1_6_Stage6NoveltyReducesToStage5:
    """L306, checked against the formula at appendix line 260."""

    def _eta(self):
        eta_int, c_ext, nu_k = sp.symbols('eta_int c_ext nu_k', positive=True)
        return eta_int * (1 - c_ext * (1 - nu_k)), eta_int, c_ext, nu_k

    def test_a_fully_novel_finding_carries_no_penalty(self):
        eta, eta_int, c_ext, nu_k = self._eta()
        assert sp.simplify(eta.subs(nu_k, 1) - eta_int) == 0

    def test_no_search_performed_degrades_to_stage_5(self):
        eta, eta_int, c_ext, nu_k = self._eta()
        assert sp.simplify(eta.subs(c_ext, 0) - eta_int) == 0


class TestTheDetectionExtensions:
    """The q_ik multipliers, each claimed to vanish at its identity value."""

    def test_delivery_feasibility_at_one_reduces_to_the_existing_model(self):
        """L442: f_del(i) = 1  ->  q_ik = d_ik * p_ik."""
        f_del, d, p = sp.symbols('f_del d p', positive=True)
        assert sp.simplify((f_del * d * p).subs(f_del, 1) - d * p) == 0

    def test_delivery_and_format_both_at_one_reduce_to_the_existing_model(self):
        """L502: f_del(i) = 1 AND phi_fmt(i) = 1  ->  q_ik = d_ik * p_ik."""
        f_del, phi, d, p = sp.symbols('f_del phi_fmt d p', positive=True)
        q = f_del * phi * d * p
        assert sp.simplify(q.subs({f_del: 1, phi: 1}) - d * p) == 0

    def test_class_specific_diversity_collapsing_reduces_to_the_scalar_model(self):
        """L420: d_ik = d_i for all k  ->  F_n is the current structured model."""
        w, d_i, p1, p2 = sp.symbols('w d_i p_1 p_2', positive=True)
        d_i1, d_i2 = sp.symbols('d_i1 d_i2', positive=True)
        general = w * (1 - (1 - d_i1 * p1) * (1 - d_i2 * p2))
        structured = w * (1 - (1 - d_i * p1) * (1 - d_i * p2))
        assert sp.simplify(general.subs({d_i1: d_i, d_i2: d_i}) - structured) == 0

    def test_zero_deferral_reduces_the_decomposed_metric_to_the_simple_ratio(self):
        """L472: tau_defer = 0  ->  eta_dec = |F_decomposed| / |F_full|."""
        tau, Fd, Ff = sp.symbols('tau_defer F_dec F_full', positive=True)
        assert sp.simplify((sp.exp(-tau) * (Fd / Ff)).subs(tau, 0) - Fd / Ff) == 0

    def test_neutral_decomposition_reduces_to_the_existing_formulation(self):
        """L476: eta_dec(i) = 1 for all i  ->  q^dec = d * p."""
        eta, d, p = sp.symbols('eta_dec d p', positive=True)
        assert sp.simplify((eta * d * p).subs(eta, 1) - d * p) == 0


class TestSeverityAndScope:
    def test_severity_equal_to_weighting_reduces_L_n_to_R_n(self):
        """L598: s_k = w_k  ->  L_n = R_n, term by term."""
        s_k, w_k, R = sp.symbols('s_k w_k R', positive=True)
        assert sp.simplify((s_k * R).subs(s_k, w_k) - w_k * R) == 0

    def test_no_domain_variables_reduces_the_detection_function_to_its_base(self):
        """L671: V_s = 0 for all s  ->  the product term is 1."""
        E, M, alpha, lam, V = sp.symbols('E M alpha lambda_s V_s', positive=True)
        base = E * (alpha + (1 - alpha) * M)
        assert sp.simplify((base * (1 + lam * V)).subs(V, 0) - base) == 0

    def test_no_follow_step_reduces_FFF_to_standard_confer(self):
        """L1217/L1230: sigma = 0  ->  D_total = D_found."""
        sig, D = sp.symbols('sigma D_found', positive=True)
        assert sp.simplify((D * (1 + sig)).subs(sig, 0) - D) == 0


class TestSection7_2_TheAbstractionIndex:
    def test_a_bare_finding_reduces_the_index_to_confidence_alone(self):
        """L899: all indicators 0, W_e = 0, N_cm = D_ref = 0  ->  H(x) = c.

        The appendix's own note matters here and is asserted separately below:
        rho_info equals 1 only when W_e = 0, NOT when W_e = W_c.
        """
        c, cF1, cF2, cG1, cG2, We, Wc, Ncm, Dref = sp.symbols(
            'c c_F1 c_F2 c_G1 c_G2 W_e W_c N_cm D_ref', positive=True)
        F = 1 + cF1 * 0 + cF2 * 0
        rho = sp.log(sp.E + We / (Wc + 1))
        G = 1 + cG1 * sp.log(1 + Ncm) + cG2 * sp.log(1 + Dref)
        H = c * F * rho * G
        assert sp.simplify(H.subs({We: 0, Ncm: 0, Dref: 0}) - c) == 0

    def test_the_density_term_is_one_ONLY_at_zero_evidence(self):
        """The appendix flags this explicitly; it is easy to get backwards."""
        We, Wc = sp.symbols('W_e W_c', positive=True)
        rho = sp.log(sp.E + We / (Wc + 1))
        assert sp.simplify(rho.subs(We, 0) - 1) == 0
        # with evidence equal to claim length it is strictly greater than 1
        assert sp.simplify(rho.subs({We: 4, Wc: 4}) - 1) > 0
