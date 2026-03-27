# Blind Mathematical Review: CDSFL Formal Model

**Reviewer:** CC2 (Claude Opus 4.6)
**Timestamp:** 2026-03-27T13:16:42+00:00
**Source documents:** `docs/MATHEMATICAL_APPENDIX.md`, `bench/directives/universal/cdsfl_core_formal.md`
**Blind pass:** No other review files consulted.

---

## Findings

---

FINDING_ID: MATH-01
COMPONENT: §1 (Residual Risk Model, Reduction Property)
CLAIM: Under the stated simplifying assumptions (K=1, d_i=1, all p_ik=p, pi=0.5), R_n reduces to R_1 = (1-p)^n / (1 + (1-p)^n).
EVIDENCE: The subscript is wrong. Under these assumptions, the general formula yields R_n = (0.5 * (1-p)^n) / (0.5 + 0.5 * (1-p)^n) = (1-p)^n / (1 + (1-p)^n). This is correct mathematically. However, the left-hand side is labelled R_1, not R_n. Since K=1 (single flaw class), the subscript 1 appears to refer to the class index, but the quantity depends on n (number of passes). This is a notation collision: R_1 reads as "residual risk after 1 pass" when it means "residual risk for class 1 after n passes." The formula is stated as a function of n on the right-hand side but labelled with a fixed subscript on the left.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.92
VERIFIABLE_CLAIM: The reduction formula is algebraically correct; the issue is purely notational (subscript ambiguity between pass count and class index).
SYMPY_EXPRESSION: from sympy import *; p, n = symbols('p n', positive=True); pi_k = Rational(1,2); m = (1-p)**n; R = (pi_k * m) / ((1 - pi_k) + pi_k * m); assert simplify(R - (1-p)**n / (1 + (1-p)**n)) == 0
CROSS_MODULE_REFS: [§1, §6 Notation Summary]
SEVERITY: notation_cleanup
PROPOSED_FIX: Replace "R_1" with "R_n" in the reduction property. The sentence should read: "R_n reduces to R_n = (1-p)^n / (1 + (1-p)^n)".

---

FINDING_ID: MATH-02
COMPONENT: §7.2 (Abstraction Index H(x))
CLAIM: H(x) = c * F(x) * D(x) * G(x) degrades gracefully to c (confidence alone) when all Boolean indicators are 0 and word counts are equal.
EVIDENCE: When all indicators are 0: F(x) = 1. When W_e = W_c (equal word counts): D(x) = ln(e + W_e/(W_c + 1)). For this to equal 1, we need W_e/(W_c+1) = e^1 - e = 0 (approximately), which requires W_e = 0 and W_c = 0 (giving D = ln(e + 0) = ln(e) = 1). But "word counts are equal" does not imply "word counts are zero." If W_e = W_c = 100, then D(x) = ln(e + 100/101) = ln(e + 0.99) = ln(3.708) = 1.31, not 1. The stated reduction to c holds only when both word counts are zero, which is a degenerate case (a finding with no words). For any nonzero equal word counts, H(x) != c. The claimed reduction property is imprecise.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.95
VERIFIABLE_CLAIM: D(x) = ln(e + W_e/(W_c+1)) != 1 when W_e = W_c > 0.
SYMPY_EXPRESSION: from sympy import *; W_e, W_c = symbols('W_e W_c', positive=True); D = log(E + W_e/(W_c + 1)); print(D.subs([(W_e, 100), (W_c, 100)])); # should not equal 1
CROSS_MODULE_REFS: [§7.2, §7.3, §7.9]
SEVERITY: genuine_fix
PROPOSED_FIX: Either (a) restate the reduction condition as "When all Boolean indicators are 0, W_e = 0, W_c = 0, N_cm = 0, D_ref = 0, then H(x) = c" or (b) redesign D(x) so that equal word counts genuinely yield D=1, e.g., D(x) = ln(1 + W_e/(W_c + 1)) which gives D(0/0) = ln(1) = 0, which is worse, or D(x) = 1 + ln(1 + (W_e - W_c)/(W_c + 1)) which gives 1 when W_e = W_c. Option (a) is the honest fix.

---

FINDING_ID: MATH-03
COMPONENT: §7.2 (Abstraction Index H(x))
CLAIM: G(x) = 1 + gamma * ln(1 + N_cm) + delta * ln(1 + D_ref) reduces to 1 when N_cm = 0 and D_ref = 0.
EVIDENCE: G(0,0) = 1 + gamma * ln(1) + delta * ln(1) = 1 + 0 + 0 = 1. This is correct. No issue here; included for completeness during H(x) reduction analysis. The G(x) component does reduce properly. The reduction failure is isolated to D(x).
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: G(0,0) = 1 trivially.
SYMPY_EXPRESSION: from sympy import *; gamma, delta = symbols('gamma delta'); G = 1 + gamma*log(1+0) + delta*log(1+0); assert G == 1
CROSS_MODULE_REFS: [§7.2]
SEVERITY: style_preference
PROPOSED_FIX: None needed. G(x) reduction is correct.

---

FINDING_ID: MATH-04
COMPONENT: §6 (G_n Combined Detection)
CLAIM: p_{H,j,k} = f_k(E,M) * Pi_s(1 + lambda_s * V_s) is bounded in [0,1] as a probability.
EVIDENCE: f_k(E,M) = E*(alpha + (1-alpha)*M). With E in [0,1], M in [0,1], alpha in (0,1): f_k ranges in [0,1]. Now consider the product term Pi_s(1 + lambda_s * V_s) with V_s in [-1,1]. If lambda_s = 0.5 and V_s = 1 for two domain variables, the product is (1.5)^2 = 2.25. Then p_H = f_k * 2.25, which can exceed 1 when f_k > 0.444. For E=0.85, M=0.9, alpha=0.4: f_k = 0.85*(0.4 + 0.6*0.9) = 0.85*0.94 = 0.799. With two favorable domain factors: p_H = 0.799 * 2.25 = 1.798. This is not a valid probability. No clipping or saturation is specified. Conversely, if lambda_s > 1 and V_s = -1, the factor (1 + lambda_s * V_s) = 1 - lambda_s < 0, making the product negative. Again no guard.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.97
VERIFIABLE_CLAIM: p_{H,j,k} can exceed 1 or become negative under stated parameter ranges without a clipping constraint.
SYMPY_EXPRESSION: from sympy import *; E, M, alpha, lam, V = Rational(85,100), Rational(9,10), Rational(4,10), Rational(1,2), 1; f = E*(alpha + (1-alpha)*M); p = f * (1+lam*V)**2; print(f"p_H = {float(p)}, exceeds 1: {float(p) > 1}")
CROSS_MODULE_REFS: [§6, §7.7, §7.9]
SEVERITY: genuine_fix
PROPOSED_FIX: Add explicit constraint: p_{H,j,k} = clip(f_k(E,M) * Pi_s(1 + lambda_s * V_s), 0, 1). Additionally require lambda_s in [0,1) to prevent negative factors, or require (1 + lambda_s * V_s) > 0 for all s.

---

FINDING_ID: MATH-05
COMPONENT: §7.6 (Adoption Delta)
CLAIM: Delta(A->B) = (|A_adopt| + |A_drop|) / |B_A symmetric_difference B_B| with convention Delta = 0 when B_A symmetric_difference B_B = empty.
EVIDENCE: The denominator is the symmetric difference of the two blind sets. The numerator counts findings adopted from B and findings dropped after seeing B. Consider: B_A = {f1}, B_B = {f1, f2}, C_A = {f1, f2}. Then B_A symm_diff B_B = {f2}, |denom| = 1. A_adopt = C_A intersect (B_B \ B_A) = {f2} intersect {f2} = {f2}, |A_adopt| = 1. A_drop = (B_A \ B_B) \ C_A = empty \ C_A = empty, |A_drop| = 0. Delta = 1/1 = 1. But now if B_A = {f1}, B_B = {f1, f2, f3, f4}, C_A = {f1, f2}: A_adopt = {f2}, A_drop = empty. Symm_diff = {f2, f3, f4}. Delta = 1/3 = 0.33. Yet A adopted exactly the same finding (f2) in both cases. The metric's value depends on how many findings B had that A did not adopt, which conflates A's independence with B's productivity. A model paired with a prolific partner looks more independent than the same model paired with a parsimonious one, even with identical adoption behaviour.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.88
VERIFIABLE_CLAIM: Delta(A->B) is not invariant to the size of B_B \ B_A when A's adoption set is held constant.
SYMPY_EXPRESSION: from sympy import *; # Case 1: B_A={f1}, B_B={f1,f2}, C_A={f1,f2}; adopt1=1; drop1=0; denom1=1; d1 = Rational(adopt1+drop1, denom1); # Case 2: B_A={f1}, B_B={f1,f2,f3,f4}, C_A={f1,f2}; adopt2=1; drop2=0; denom2=3; d2=Rational(adopt2+drop2, denom2); print(f"Same adoption, Delta1={d1}, Delta2={d2}")
CROSS_MODULE_REFS: [§7.5, §7.6, §8.2]
SEVERITY: genuine_fix
PROPOSED_FIX: Either (a) normalise by |B_B \ B_A| (findings available to adopt) + |B_A \ B_B| (findings available to drop) separately, giving Delta = |A_adopt|/|B_B \ B_A| as adoption rate and |A_drop|/|B_A \ B_B| as drop rate, reported as a pair rather than conflated into a single scalar; or (b) document the confound explicitly and state that Delta is only meaningfully comparable across pairings where |B_A symm_diff B_B| is similar.

---

FINDING_ID: MATH-06
COMPONENT: §5 (Corroboration Model, cdsfl_core_formal.md)
CLAIM: dC/dn = -(1-p)^n * ln(1-p) > 0 (monotonically increasing).
EVIDENCE: C(n) = 1 - (1-p)^n. dC/dn = -(1-p)^n * ln(1-p). For p in (0,1): (1-p) in (0,1), so ln(1-p) < 0. Therefore -(1-p)^n * ln(1-p) = -(positive)*(negative) = positive. The claim is correct. However, C(n) is defined over discrete n (number of passes), so writing dC/dn treats n as continuous. This is standard practice for analysing monotonicity of discrete sequences via their continuous envelope, but the second derivative claim d^2C/dn^2 < 0 (concavity) should note that n is naturally discrete and the continuous extension is used for the property statement. Minor point.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.80
VERIFIABLE_CLAIM: The derivative expressions are correct for the continuous extension of C(n).
SYMPY_EXPRESSION: from sympy import *; p, n = symbols('p n', positive=True); C = 1 - (1-p)**n; dC = diff(C, n); print(simplify(dC))  # should give -(1-p)^n * log(1-p)
CROSS_MODULE_REFS: [§5 (core_formal), §1 (appendix)]
SEVERITY: style_preference
PROPOSED_FIX: Add parenthetical: "(treating n as continuous for the monotonicity argument; the properties hold a fortiori for the discrete sequence)".

---

FINDING_ID: MATH-07
COMPONENT: §3 (Falsification Loop, cdsfl_core_formal.md)
CLAIM: The falsification loop is a fixed-point iteration. Convergence is not guaranteed in theory but observed in practice.
EVIDENCE: The document honestly acknowledges non-guaranteed convergence. However, the termination condition Delta(k) = 0 with the stated budget of up to 5 passes (from CLAUDE.md p-pass-standard-budget) means the loop always terminates in practice, but not necessarily at a fixed point. If pass 5 still has Delta(5) > 0, the loop terminates by budget exhaustion, not convergence. The formal model should distinguish these two termination modes: convergence (Delta = 0) and budget exhaustion (k = k_max with Delta > 0). Budget-exhausted termination means surviving claims have NOT been fully falsified in the formal sense. This matters for the Corroboration Model (§5): C(n) assumes each pass is genuinely independent, but a budget-exhausted run may have stopped mid-cascade where later passes would have been highly correlated with earlier ones.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.85
VERIFIABLE_CLAIM: The formal model specifies only one termination mode (Delta=0) while the operational protocol has two (Delta=0 or k=k_max).
SYMPY_EXPRESSION: # Not algebraically verifiable - this is a logical completeness issue
CROSS_MODULE_REFS: [§3 (core_formal), §5 (core_formal), §1 (appendix R_n)]
SEVERITY: genuine_fix
PROPOSED_FIX: Add to §3: "Termination: (a) convergence: Delta(k) = 0; (b) budget exhaustion: k = k_max with Delta(k) > 0. Under budget exhaustion, claims carry residual falsification debt proportional to Delta(k_max). The corroboration model C(n) applies to convergent termination; for budget-exhausted runs, R_n (§1 of appendix) with elevated pi_k is the appropriate risk measure."

---

FINDING_ID: MATH-08
COMPONENT: §7.5 (Objective Alignment O_A)
CLAIM: S_sync = (1 - delta_bar) * (1 - O_A) where delta_bar is average adoption delta.
EVIDENCE: The formula uses delta_bar but this quantity is not defined in §7.5. The Adoption Delta in §7.6 defines Delta(A->B) which is directional. For a two-model confer, there are two deltas: Delta(A->B) and Delta(B->A). The text says "delta_bar" without specifying whether it is the average of these two directional deltas, or something else. For n > 2 models, the number of directional deltas is n*(n-1), and delta_bar is even more ambiguous. Additionally, the (1 - delta_bar) factor means S_sync = 0 when delta_bar = 1 (complete capitulation). But complete capitulation with low O_A is the most sycophantic scenario, and it should produce a HIGH S_sync, not zero. The formula has inverted semantics for the independence term.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.91
VERIFIABLE_CLAIM: When delta_bar = 1 (maximum capitulation) and O_A = 0 (unverified convergence), S_sync = 0, but this is the maximally sycophantic case.
SYMPY_EXPRESSION: from sympy import *; delta_bar, O_A = 1, 0; S = (1 - delta_bar) * (1 - O_A); print(f"S_sync = {S}")  # prints 0, should be maximum
CROSS_MODULE_REFS: [§7.5, §7.6, §8.2]
SEVERITY: genuine_fix
PROPOSED_FIX: The sycophancy score should increase with both capitulation AND unverified convergence. Replace with S_sync = delta_bar * (1 - O_A). Now: delta_bar=1, O_A=0 gives S_sync=1 (maximally sycophantic). delta_bar=0, O_A=1 gives S_sync=0 (independent convergence on verified facts). Also explicitly define delta_bar = (Delta(A->B) + Delta(B->A)) / 2 for the two-model case.

---

FINDING_ID: MATH-09
COMPONENT: §7.4 (Online Total Value Estimator)
CLAIM: When lambda(t) > 0, remaining estimate = v_w(t) * (1 - exp(-lambda(t)*(T-t))) / lambda(t).
EVIDENCE: This formula assumes the value generation rate decays exponentially from v_w(t) with rate lambda(t). The integral of v_w(t)*exp(-lambda*(tau-t)) from t to T is v_w(t)/lambda * (1 - exp(-lambda*(T-t))). As t -> T, this goes to 0. Correct. But lambda(t) here is the "empirical decay rate estimated from consecutive round values." In §7.1, lambda(t) is the Duane NHPP intensity function lambda(t) = (beta/eta)*(t/eta)^(beta-1), which is a rate, not a decay rate. These are different quantities sharing the same symbol. The Duane lambda(t) is the instantaneous discovery rate (findings per unit time), while the V-hat formula uses lambda as an exponential decay constant. For a convergent process (gamma > 0, beta < 1), the Duane lambda(t) is decreasing, but it is not itself the decay rate of an exponential. The notation collision obscures that two different lambda functions are in play.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.87
VERIFIABLE_CLAIM: lambda(t) in §7.4 is an exponential decay rate while lambda(t) in §7.1 is a Duane NHPP intensity; these are different functions with the same symbol.
SYMPY_EXPRESSION: # Notation issue, not algebraic. The Duane intensity lambda(t) = (beta/eta)*(t/eta)**(beta-1) is not equal to the exponential decay rate used in the V-hat remaining estimate.
CROSS_MODULE_REFS: [§7.1, §7.4, Notation Summary]
SEVERITY: genuine_fix
PROPOSED_FIX: Use a distinct symbol for the exponential decay rate in §7.4, e.g., mu(t) or lambda_d(t), and define it explicitly: "lambda_d(t) = empirical exponential decay rate, estimated from consecutive v_w values (distinct from the Duane intensity lambda(t) in §7.1)." Update the Notation Summary accordingly.

---

FINDING_ID: MATH-10
COMPONENT: §7.8 (Multi-Verifier Severity, Bayesian log-odds)
CLAIM: L_total = sum_i [L_i * log(TPR_i/FPR_i) + (1-L_i) * log(FNR_i/TNR_i)] yields S_v = 0.5 when all verifiers are indeterminate.
EVIDENCE: The formula as stated uses L_i in {0,1} (binary). There is no provision for an indeterminate outcome (verifier did not run or returned no result). The claim "All indeterminate -> S_v = 0.5 (neutral)" requires L_i to take a third value or be excluded from the sum. If an indeterminate verifier is excluded (sum over empty set), L_total = 0 and S_v = 1/(1+exp(0)) = 0.5. This works but is not stated. If indeterminate is coded as L_i = 0 (falsified), the result would be S_v = 1/(1+exp(-(sum of negative weights))) which is far below 0.5. The ternary case (verified/falsified/indeterminate) is not handled by the binary formulation. The text claims a ternary output (the table in §7.7 has V=True/None/False) but §7.8 uses binary L_i.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.90
VERIFIABLE_CLAIM: L_i in {0,1} cannot represent the indeterminate case V(None)=0.5 from §7.7 without an explicit exclusion rule.
SYMPY_EXPRESSION: from sympy import *; # If indeterminate coded as L=0: L_total = 0*log(Rational(99,100)/Rational(1,1000)) + 1*log(Rational(1,100)/Rational(999,1000)) + 0*log(Rational(8,10)/Rational(1,10)) + 1*log(Rational(2,10)/Rational(9,10)) + 0*log(Rational(7,10)/Rational(15,100)) + 1*log(Rational(3,10)/Rational(85,100)); print(f"L_total if indet=falsified: {float(L_total)}")
CROSS_MODULE_REFS: [§7.7, §7.8]
SEVERITY: genuine_fix
PROPOSED_FIX: Add explicit handling: "When verifier i returns indeterminate, exclude it from the sum (do not contribute to L_total). When all verifiers are indeterminate, L_total = 0 and S_v = 0.5." This reconciles §7.8 (binary) with §7.7 (ternary V).

---

FINDING_ID: MATH-11
COMPONENT: §8.2 (Composite System Emergence)
CLAIM: Emergence condition: Y_composite(t) > max{Y_i(t)} for all individual agents i.
EVIDENCE: This condition is necessary but not sufficient to establish emergence beyond aggregation. The text acknowledges this by also defining Y_union and stating emergence exceeds even Y_union. But the formal emergence condition only states the weaker claim (composite > max individual). There is no formal condition for composite > union. Without formalising the stronger claim, the weaker condition could be satisfied by simple aggregation: if agent A finds {f1,f2} with H=1 each (Y_A=2) and agent B finds {f3,f4} with H=1 each (Y_B=2), then Y_union = 4*1 = 4 > max(2,2) = 2. The emergence condition is satisfied trivially by union without any interaction-generated novelty. The composite > max criterion does not distinguish emergence from aggregation.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.93
VERIFIABLE_CLAIM: Y_composite > max(Y_i) is satisfiable by simple set union without any emergent findings.
SYMPY_EXPRESSION: from sympy import *; # Agent A: 2 findings, H=1 each. Agent B: 2 findings, H=1 each. Y_A=2, Y_B=2. Union: 4 findings, H_bar=1, Y_union=4. 4 > max(2,2). No emergence needed.
CROSS_MODULE_REFS: [§7.3, §8.2, §8.3]
SEVERITY: genuine_fix
PROPOSED_FIX: Replace or supplement with the stronger formal condition: "Emergence condition: Y_composite(t) > Y_union(t) where Y_union(t) = |union(F_i(t))| * H_bar_union(t). The weaker condition Y_composite > max(Y_i) is necessary but not sufficient. The stronger condition establishes that interaction produced cognitive value beyond what the union of independent outputs would yield."

---

FINDING_ID: MATH-12
COMPONENT: §6 (G_n), §7.2 (H(x)), Notation Summary
CLAIM: Symbol D is used for three different quantities.
EVIDENCE: In the Notation Summary: D(n) = distributed compute coverage (white paper Part XIII). D(x) = information density component of H(x) (§7.2). D in the capability fingerprint (D, v_bar, A, C) = decay rate (§7.9). Three distinct quantities sharing the same symbol. The Notation Summary lists all three but does not flag the collision. Within a single section (§7.9 fingerprint definition), D means decay rate, while two sections earlier (§7.2) D(x) means information density. A reader computing the fingerprint for a finding must work with both D values simultaneously.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.94
VERIFIABLE_CLAIM: D is overloaded: D(n) in Part XIII, D(x) in §7.2, and D in the fingerprint (§7.9) are three distinct quantities.
SYMPY_EXPRESSION: # Notation issue, not algebraic
CROSS_MODULE_REFS: [§7.2, §7.9, Notation Summary]
SEVERITY: notation_cleanup
PROPOSED_FIX: Rename the information density component to I(x) or rho_D(x), and/or rename the fingerprint decay rate to lambda_D or D_rate. Update the Notation Summary to eliminate the triple collision.

---

FINDING_ID: MATH-13
COMPONENT: §6 (G_n Reduction Properties)
CLAIM: When rho_MH = 1, G_n reduces to F_n (machine-only).
EVIDENCE: G_n = sum_k w_k * [1 - (1-C_M(k)) * (1 - C_H(k)*(1-rho_MH))]. At rho_MH = 1: G_n = sum_k w_k * [1 - (1-C_M(k)) * (1 - 0)] = sum_k w_k * [1 - (1-C_M(k))] = sum_k w_k * C_M(k) = F_n. Correct. Now at rho_MH = 0: G_n = sum_k w_k * [1 - (1-C_M(k))*(1-C_H(k))]. The table states this equals "1 - (1-C_M)(1-C_H)" (dropping k subscripts). Correct for each class k, weighted by w_k. Now at n_H = 0: C_H(k) = 1 - product over empty set = 1 - 1 = 0. G_n = sum_k w_k * [1 - (1-C_M(k))*(1-0*(1-rho))] = sum_k w_k * [1 - (1-C_M(k))*1] = F_n. Correct. All reduction properties check out algebraically.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.98
VERIFIABLE_CLAIM: G_n reduction properties are algebraically correct.
SYMPY_EXPRESSION: from sympy import *; CM, CH, rho = symbols('CM CH rho'); G = 1 - (1-CM)*(1-CH*(1-rho)); assert simplify(G.subs(rho,1) - CM) == 0; assert simplify(G.subs(rho,0) - (1-(1-CM)*(1-CH))) == 0; assert simplify(G.subs(CH,0) - CM) == 0
CROSS_MODULE_REFS: [§6]
SEVERITY: style_preference
PROPOSED_FIX: None needed. Reductions are correct.

---

FINDING_ID: MATH-14
COMPONENT: §7.5 (Objective Alignment, empty-set convention)
CLAIM: If F_conv = empty, O_A = 1 (convention).
EVIDENCE: F_conv = empty means no new convergence occurred during the confer phase. The convention O_A = 1 labels this as "perfect alignment." This convention interacts with S_sync: S_sync = (1-delta_bar)*(1-O_A) = (1-delta_bar)*0 = 0 regardless of delta_bar. So when models don't converge on anything new, the sycophancy score is zero. This is reasonable only if we accept that non-convergence cannot be sycophantic. But consider: two models that both drop all their original findings (high delta) and converge on nothing (F_conv = empty) would have high capitulation but S_sync = 0. Dropping everything and saying nothing is arguably worse than sycophantic convergence, but the metric gives it a clean bill of health.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.82
VERIFIABLE_CLAIM: When both models drop all blind findings and converge on nothing (F_conv=empty, delta_bar high), S_sync = 0, masking mutual suppression.
SYMPY_EXPRESSION: from sympy import *; delta_bar = Rational(9,10); O_A = 1; S = (1-delta_bar)*(1-O_A); print(f"S_sync = {S}")  # 0 despite high capitulation
CROSS_MODULE_REFS: [§7.5, §7.6]
SEVERITY: genuine_fix
PROPOSED_FIX: Add a "mutual suppression" guard: "If F_conv = empty AND (|B_A \ C_A| + |B_B \ C_B|) > tau_suppress, flag as mutual suppression (distinct from sycophancy). O_A = 1 convention applies only when both blind sets are substantially preserved in the confer output."

---

FINDING_ID: MATH-15
COMPONENT: §8.3 (Second-Order Cognitive System)
CLAIM: The CDSFL composite system meets all four criteria for second-order cognition.
EVIDENCE: Criterion 4 states "the adjustment produces measurable improvement (post-feedback gamma increases or v_bar increases)." This is stated as a factual claim but depends entirely on empirical measurement. As of the document's writing, §8.1 notes "Whether models actually respond to metacognitive feedback is an empirical question." These two statements are in tension: §8.3 asserts the system meets criterion 4, while §8.1 says the answer is unknown. The claim in §8.3 should be conditional ("if criterion 4 is empirically confirmed") rather than categorical. Without this qualification, the formal definition is satisfied by assertion rather than evidence.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.86
VERIFIABLE_CLAIM: §8.3 asserts criterion 4 is met while §8.1 states the relevant evidence is not yet collected.
SYMPY_EXPRESSION: # Logical consistency issue, not algebraic
CROSS_MODULE_REFS: [§8.1, §8.3, §8.5]
SEVERITY: genuine_fix
PROPOSED_FIX: Replace "The CDSFL composite system meets all four criteria" with "The CDSFL composite system meets criteria 1-3 by construction. Criterion 4 (measurable improvement from metacognitive adjustment) is a testable empirical claim. If confirmed, the system qualifies as second-order cognitive under this definition."

---

FINDING_ID: MATH-16
COMPONENT: §1 (Residual Risk R_n), boundary
CLAIM: R_n is well-defined for all valid parameter ranges.
EVIDENCE: R_n = sum_k w_k * (pi_k * m_k) / ((1-pi_k) + pi_k * m_k). When pi_k = 1 (certainty that flaw exists): denominator = 0 + 1*m_k = m_k. If m_k = 0 (perfect detection): R_n has a 0/0 term: (1 * 0) / (0 + 1 * 0) = 0/0. The limit as m_k -> 0 with pi_k = 1 is 0 (via L'Hopital or direct: pi*m/(pi*m) = 1, not 0). Actually: (1 * m_k) / (0 + 1 * m_k) = m_k/m_k = 1. So the limit is 1, meaning "we were certain a flaw existed, perfect detection found nothing, residual risk = 1." This is counterintuitive but actually correct Bayesian reasoning: P(flaw | no detection) when P(flaw)=1 is still 1, because if we are certain the flaw exists, no amount of non-detection changes that (the test must have missed it). The 0/0 form at pi_k=1 and m_k=0 simultaneously is the only degenerate case, and its physical interpretation (certain flaw + perfect detection = contradiction) means it should be excluded from the domain.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.78
VERIFIABLE_CLAIM: R_n is undefined at (pi_k=1, m_k=0); this is a measure-zero boundary that represents a logical contradiction.
SYMPY_EXPRESSION: from sympy import *; pi_k, m_k = symbols('pi_k m_k'); R = (pi_k * m_k) / ((1-pi_k) + pi_k * m_k); print(limit(R, m_k, 0, '+').subs(pi_k, 1))  # should show indeterminate or need special handling
CROSS_MODULE_REFS: [§1]
SEVERITY: notation_cleanup
PROPOSED_FIX: Add domain note: "R_n is defined for pi_k in [0,1) or m_k in (0,1]. The boundary (pi_k=1, m_k=0) is a logical contradiction (certain flaw, perfect detection, no finding) and is excluded."

---

---

## Non-Findings (Examined, No Issue)

1. **Corroboration model C(n)** (core_formal §5): Algebraically sound. C(0)=0, limits correct, derivatives correct for continuous extension. No hidden assumptions beyond i.i.d. pass independence (which is explicitly relaxed in the appendix via d_i).

2. **Constraint classification partition** (core_formal §1): Clean binary partition with explicit default rule for ambiguous cases. No gap.

3. **Extended P-Pass DAG** (core_formal §6): Isolation constraint is well-defined. The pass graph is a valid DAG. Termination criteria are consistent with §3 and §7 of core_formal.

4. **Severity function Sev(f)** (§7.7): Disproved-findings-get-zero property is correct and well-motivated. The multiplicative form means any zero factor zeros the result.

5. **Bayesian calibration E*(t)** (§6): Standard Beta-Binomial conjugate update. Correct. The convergence rate claim (~5 reviews) is plausible for Beta(2,2) prior with true rate 0.55.

6. **Kappa calibration metric** (§6): Asymmetric variant correctly penalises overconfidence more. The negative score for the bluffer case is a feature, not a bug.

---

CONCUR_STOP: false
SUMMARY: I found 8 genuine fixes, 3 notation cleanups, and 3 confirmed-correct components. The most consequential findings are: (1) p_{H,j,k} lacks a clipping constraint and can exceed 1 or go negative (MATH-04), (2) S_sync has inverted semantics for the independence term, scoring maximally sycophantic cases as zero (MATH-08), (3) the emergence condition Y_composite > max(Y_i) is too weak and is satisfiable by simple aggregation without any emergent interaction (MATH-11), and (4) lambda(t) is used for two different functions across §7.1 and §7.4 (MATH-09). These are genuine mathematical issues that affect the model's correctness or interpretability, not style preferences.
