FINDING_ID: MATH-01
COMPONENT: §7.2
CLAIM: The Abstraction Index H(x) contains arbitrary calibration parameters α, β, γ, δ that are not operationally identifiable from typical data.
EVIDENCE: The formula H(x) = c·F(x)·D(x)·G(x) multiplies three subcomponents, each with free parameters (α, β in F; γ, δ in G). Without calibration against human-ranked examples, these parameters are arbitrary. The claimed discrimination ratio of 33.4× depends entirely on the chosen parameter values (initialized at 1.0). Different parameter choices could produce arbitrarily different discrimination ratios, making the measure non-canonical.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.95
VERIFIABLE_CLAIM: For any given finding x, the value of H(x) is not invariant under rescaling of the free parameters, even when holding the Boolean indicators and word counts fixed.
SYMPY_EXPRESSION: 
```python
import sympy as sp
c, alpha, beta, gamma, delta = sp.symbols('c alpha beta gamma delta', positive=True)
F_verifiable, F_hard = sp.symbols('F_verifiable F_hard', integer=True, nonnegative=True)
W_e, W_c = sp.symbols('W_e W_c', positive=True)
N_cm, D_ref = sp.symbols('N_cm D_ref', nonnegative=True)
F = 1 + alpha*F_verifiable + beta*F_hard
D = sp.log(sp.E + W_e/(W_c + 1))
G = 1 + gamma*sp.log(1 + N_cm) + delta*sp.log(1 + D_ref)
H = c * F * D * G
# Show that H is linear in each parameter individually
sp.simplify(sp.diff(H, alpha)/c)  # = D*G*F_verifiable ≠ 0 generally
```
CROSS_MODULE_REFS: §7.9 (Capability Fingerprint depends on H̄(t))
SEVERITY: genuine_fix
PROPOSED_FIX: Replace free parameters with fixed scaling constants determined by a calibration dataset, or define H(x) as a log-linear model with identifiable parameters via maximum likelihood on human-annotated depth rankings.

FINDING_ID: MATH-02
COMPONENT: §7.3
CLAIM: The ascending abstraction condition dH̄/dt > 0 while dN/dt < 0 is insufficient to guarantee that total yield Y(t) = N(t)·H̄(t) increases.
EVIDENCE: The derivative of Y(t) is dY/dt = (dN/dt)·H̄ + N·(dH̄/dt). Even if dH̄/dt > 0 and dN/dt < 0, the product could still decrease if the rate of count decrease outweighs the rate of depth increase. The condition "If the rate of abstraction increase exceeds the rate of count decrease" is qualitative; the model lacks a quantitative inequality to ensure Y increases. This could lead to misclassification of cognitive modes.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.90
VERIFIABLE_CLAIM: There exist functions N(t) and H̄(t) with dN/dt < 0 and dH̄/dt > 0 such that dY/dt < 0.
SYMPY_EXPRESSION:
```python
import sympy as sp
t = sp.symbols('t', positive=True)
N = 10 - t  # linear decrease
Hbar = 1 + 0.05*t  # linear increase
Y = N * Hbar
dY_dt = sp.diff(Y, t)
sp.simplify(dY_dt)  # = -t/20 - 19/20, which is negative for all t>0
```
CROSS_MODULE_REFS: §7.4 (ascending abstraction guard), §8.2 (emergence condition)
SEVERITY: genuine_fix
PROPOSED_FIX: Define ascending abstraction formally as dY/dt > 0, which expands to (dN/dt)·H̄ + N·(dH̄/dt) > 0. Provide a dimensionless condition: (dH̄/dt)/H̄ > |dN/dt|/N (relative depth increase exceeds relative count decrease).

FINDING_ID: MATH-03
COMPONENT: §7.5
CLAIM: The domain guard for O_A (undefined when verifiable subset size < 2) introduces a discontinuity that can arbitrarily affect the composite sycophancy score S_sync.
EVIDENCE: When |{f ∈ F_conv : verifiable(f)}| = 1, O_A = ⊥ and S_sync defaults to S_sync(Δ) = (1 - δ̄). When the set size becomes 2, O_A is computed normally, potentially causing a jump in S_sync. This threshold is arbitrary; a single verifiable finding could still provide evidence about alignment. The discontinuity makes the metric unstable near the threshold.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.85
VERIFIABLE_CLAIM: There exist two scenarios differing only by adding one verifiable finding to F_conv that produce different S_sync values despite similar underlying alignment.
SYMPY_EXPRESSION:
```python
import sympy as sp
delta_bar = sp.symbols('delta_bar', real=True)
# Case 1: 1 verifiable finding, 0 verified → O_A undefined, S_sync = 1 - delta_bar
# Case 2: 2 verifiable findings, 0 verified → O_A = 0, S_sync = (1 - delta_bar)*(1 - 0) = 1 - delta_bar
# Actually same in this edge case, but if O_A > 0 they differ.
# More general: let v = number verified, n = size verifiable subset
n, v = sp.symbols('n v', integer=True, nonnegative=True)
O_A = sp.Piecewise((sp.nan, n < 2), (v/n, True))
S_sync = (1 - delta_bar) * (1 - sp.Piecewise((0, n < 2), (v/n, True)))
# Show discontinuity at n=1 vs n=2 when v=1:
sp.limit(S_sync.subs(v,1), n, 1, dir='-')  # undefined? Actually need to evaluate
```
CROSS_MODULE_REFS: §7.6 (Adoption Delta), §8.2 (genuine emergence discrimination)
SEVERITY: genuine_fix
PROPOSED_FIX: Define O_A using a Bayesian estimate with a prior (e.g., (v+1)/(n+2)) to handle small n smoothly, and remove the domain guard. Alternatively, use a continuity correction.

FINDING_ID: MATH-04
COMPONENT: §7.8
CLAIM: The Bayesian log-odds formula for multi-verifier severity S_v uses log-likelihood ratios incorrectly when L_i = 0.
EVIDENCE: The formula given is L_total = Σ_i [L_i·log(TPR_i/FPR_i) + (1−L_i)·log(FNR_i/TNR_i)]. However, FNR_i = 1−TPR_i and TNR_i = 1−FPR_i. The term for L_i=0 should be log((1−TPR_i)/(1−FPR_i)) = log(FNR_i/TNR_i) only if FNR_i and TNR_i are defined as complements. The notation is consistent but potentially confusing. More critically, the veto property relies on SymPy's negative weight magnitude exceeding the sum of others' positive weights, which is a numerical coincidence dependent on the chosen TPR/FPR values.
CONSTRAINT_CLASS: SOFT
CONFIDENCE: 0.80
VERIFIABLE_CLAIM: The veto property is not inherent to the Bayesian log-odds formulation but depends on specific TPR/FPR assignments.
SYMPY_EXPRESSION:
```python
import sympy as sp
TPR_s, FPR_s = 0.99, 0.001
TPR_d, FPR_d = 0.80, 0.10
TPR_n, FPR_n = 0.70, 0.15
w_pos_s = sp.log(TPR_s/FPR_s)
w_neg_s = sp.log((1-TPR_s)/(1-FPR_s))
w_pos_d = sp.log(TPR_d/FPR_d)
w_pos_n = sp.log(TPR_n/FPR_n)
# Check veto condition: |w_neg_s| > w_pos_d + w_pos_n?
print(float(abs(w_neg_s)), float(w_pos_d + w_pos_n))
```
CROSS_MODULE_REFS: §7.7 (Sev(f)), §7.9 (fingerprint uses v̄)
SEVERITY: notation_cleanup
PROPOSED_FIX: Clarify the log-odds formula using standard notation: L_total = Σ_i [L_i·log(TPR_i/FPR_i) + (1−L_i)·log((1−TPR_i)/(1−FPR_i))]. Note that the veto property is a design choice ensured by appropriate TPR/FPR settings.

FINDING_ID: MATH-05
COMPONENT: §8.2
CLAIM: The emergence condition Y_composite(t) > max{Y_i(t)} is not sufficient to distinguish emergence from simple aggregation due to possible measurement noise.
EVIDENCE: The condition is a strict inequality. In practice, Y_composite(t) and Y_i(t) are estimated from finite data. Without a statistical significance test, random fluctuations could cause the inequality to be satisfied spuriously. The model does not specify a confidence interval or threshold for "materially greater than," leaving the emergence claim vulnerable to noise.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.85
VERIFIABLE_CLAIM: Given random variations in Y measurements, the probability that Y_composite > max{Y_i} by chance alone is non-zero even when no true emergence exists.
SYMPY_EXPRESSION:
```python
import sympy as sp
# Simplified: assume Y_i ~ Normal(μ, σ), Y_composite = max{Y_i} + ε where ε ~ Normal(0, σ)
# Probability that Y_composite > max{Y_i} is P(ε > 0) = 0.5 if symmetric noise.
# More realistic simulation would require joint distributions.
```
CROSS_MODULE_REFS: §7.3 (Y(t) definition), §7.4 (online estimator), §8.5 (falsifiable claims)
SEVERITY: genuine_fix
PROPOSED_FIX: Augment the emergence condition with a statistical test: Y_composite(t) > max{Y_i(t)} + k·σ, where σ is an estimate of measurement uncertainty (e.g., bootstrap standard error) and k is a confidence multiplier (e.g., 1.96 for 95% confidence).

CONCUR_STOP: false
SUMMARY: The model exhibits several mathematical weaknesses, primarily in the cognitive measurement framework (§7). The Abstraction Index has unidentifiable parameters, the ascending abstraction condition is insufficient, and the emergence condition lacks statistical rigor. However, the core detection models (§1-6) appear more robust, with clear reduction properties. The model is not fundamentally broken but requires refinement in the novel components.