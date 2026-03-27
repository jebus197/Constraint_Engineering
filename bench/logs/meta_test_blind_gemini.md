```
FINDING_ID: MATH-01
COMPONENT: §7.3 Total Cognitive Yield Y(t)
CLAIM: The ascending abstraction condition $dN/dt < 0$ is mathematically impossible because $N(t)$ is defined as a cumulative finding count.
EVIDENCE: $N(t)$ is defined as the "finding count at time t" and is used to calculate total yield $Y(t) = N(t) \cdot \bar{H}(t)$. In all standard reliability models (including the Duane NHPP in §7.1), a cumulative finding count $N(t)$ is monotonically increasing, meaning $dN/dt \ge 0$ always. For $dN/dt < 0$ to occur, the system would have to lose or delete previously established findings faster than it generates new ones, which contradicts the definition of an accumulating analytical process. The author likely meant a decreasing *rate* of findings.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: For a cumulative counting process $N(t) = \int_0^t \lambda(\tau) d\tau$ where intensity $\lambda(\tau) > 0$, the derivative $dN/dt$ cannot be negative.
SYMPY_EXPRESSION:
```python
import sympy as sp
t, beta, eta = sp.symbols('t beta eta', positive=True)
lam = (beta/eta) * (t/eta)**(beta-1) # Duane NHPP intensity
N = sp.integrate(lam, t)
dN_dt = sp.diff(N, t)
is_possible = sp.ask(sp.Q.negative(dN_dt))
print(is_possible) # False
```
CROSS_MODULE_REFS: §7.1, §7.4
SEVERITY: genuine_fix
PROPOSED_FIX: Change the ascending abstraction condition to $d\bar{H}/dt > 0 \land d\lambda/dt < 0$ (or $d^2N/dt^2 < 0$), and update the guard in §7.4 to use $d\lambda/dt \le 0$.

FINDING_ID: MATH-02
COMPONENT: §7.2 Abstraction Index H(x)
CLAIM: The stated reduction property that $H(x)$ reduces to $c$ when word counts are equal is mathematically false for any non-zero word count.
EVIDENCE: The text claims that when Boolean indicators are 0 and word counts are equal ($W_e = W_c$), $H(x)$ reduces to $c$. However, the density function is $D(x) = \ln(e + W_e / (W_c + 1))$. If $W_e = W_c = w > 0$, then $D(x) = \ln(e + w / (w + 1))$. Since $w / (w + 1) > 0$, $D(x) > \ln(e) = 1$. Therefore, $H(x) = c \cdot 1 \cdot D(x) \cdot 1 > c$. The reduction only holds if $W_e = 0$, not for all equal word counts.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: The expression $\ln(e + w / (w + 1))$ is strictly greater than 1 for all $w > 0$.
SYMPY_EXPRESSION:
```python
import sympy as sp
w = sp.Symbol('w', positive=True)
D = sp.log(sp.E + w / (w + 1))
is_greater = sp.simplify(D > 1)
print(is_greater) # True
```
CROSS_MODULE_REFS: None
SEVERITY: genuine_fix
PROPOSED_FIX: Change the density function to $D(x) = \ln(e - 1 + (W_e + 1) / (W_c + 1))$ so that when $W_e = W_c$, the ratio is 1 and $D(x) = \ln(e) = 1$.

FINDING_ID: MATH-03
COMPONENT: §7.8 Multi-Verifier Severity
CLAIM: The negative weight values in the numerical example are calculated using an incorrect likelihood ratio $\log(FNR / TPR)$, contradicting both the stated formula and standard Bayesian logic.
EVIDENCE: The formula correctly states the negative update as $\log(FNR_i / TNR_i)$, which represents the likelihood ratio $P(L_i=0 | \text{True}) / P(L_i=0 | \text{False})$. However, the table's negative weights are calculated as $\log(FNR_i / TPR_i)$. For example, Dimensional's negative weight is given as $-1.39$, which is exactly $\ln(0.20 / 0.80)$, whereas the correct Naive Bayes weight $\ln(FNR / TNR)$ would be $\ln(0.20 / 0.90) \approx -1.50$. This invalidates the numerical proof of the "veto property".
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: The value -1.39 for the Dimensional negative weight corresponds to $\ln(FNR/TPR)$ and not the stated formula $\ln(FNR/TNR)$.
SYMPY_EXPRESSION:
```python
import sympy as sp
tpr, fpr = 0.80, 0.10
fnr, tnr = 1 - tpr, 1 - fpr
correct_weight = sp.log(fnr / tnr).evalf(4)
table_weight = sp.log(fnr / tpr).evalf(4)
print(f"Correct: {correct_weight}, Table used: {table_weight}")
```
CROSS_MODULE_REFS: None
SEVERITY: genuine_fix
PROPOSED_FIX: Recalculate the negative weights in the table using the correct $\log(FNR_i / TNR_i)$ formula. Dimensional should be -1.50, Numerical should be -1.04, and SymPy should be -4.60.

FINDING_ID: MATH-04
COMPONENT: §7.5 Objective Alignment O_A
CLAIM: The sycophancy score formula $S_{sync} = (1 - \bar{\delta}) \cdot (1 - O_A)$ uses an undefined variable and produces inverted logic if $\bar{\delta}$ is intended to be the Adoption Delta $\Delta$.
EVIDENCE: The variable $\bar{\delta}$ is never defined. If it is a typo for the Adoption Delta $\Delta$ (which measures deference/capitulation), the formula fails its own stated interpretation. The text states "S_sync high: sycophantic convergence". Sycophancy implies high capitulation ($\Delta \to 1$) and low verification ($O_A \to 0$). Under these conditions, $(1 - \Delta) \cdot (1 - O_A) = (1 - 1) \cdot (1 - 0) = 0$, yielding a *low* sycophancy score instead of a high one.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: If $\bar{\delta}$ is $\Delta$, the function $S_{sync}(\Delta, O_A) = (1 - \Delta)(1 - O_A)$ is strictly decreasing with respect to $\Delta$, meaning higher capitulation produces lower sycophancy scores.
SYMPY_EXPRESSION:
```python
import sympy as sp
Delta, O_A = sp.symbols('Delta O_A')
S_sync = (1 - Delta) * (1 - O_A)
dS_dDelta = sp.diff(S_sync, Delta)
is_negative = sp.simplify(dS_dDelta < 0)
print(dS_dDelta) # O_A - 1, which is negative for O_A < 1
```
CROSS_MODULE_REFS: §7.6, §8.2
SEVERITY: genuine_fix
PROPOSED_FIX: Replace $\bar{\delta}$ with $\Delta$ and correct the formula to $S_{sync} = \Delta \cdot (1 - O_A)$ so that high capitulation and low verification correctly maximize the sycophancy score.

FINDING_ID: MATH-05
COMPONENT: §7.4 Online Total Value Estimator
CLAIM: The variable $\lambda(t)$ is used simultaneously as a strictly positive power-law intensity function and as an exponential decay constant that can be negative, creating a mathematical contradiction.
EVIDENCE: In §7.1, $\lambda(t)$ is defined as the Duane NHPP intensity function $\lambda(t) = (\beta/\eta)(t/\eta)^{\beta-1}$. Since $t, \beta, \eta > 0$, this $\lambda(t)$ is strictly positive. However, in §7.4, the estimator branches on "If $\lambda(t) \le 0$", which is impossible for the Duane model. Furthermore, the integral evaluates to $(1 - \exp(-\lambda(t)(T-t)))/\lambda(t)$, which is the solution for an *exponential* decay process $e^{-\lambda \tau}$, not a power-law process.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: The Duane intensity function $\lambda(t) = (\beta/\eta)(t/\eta)^{\beta-1}$ cannot be less than or equal to zero for any $t > 0, \beta > 0, \eta > 0$.
SYMPY_EXPRESSION:
```python
import sympy as sp
t, beta, eta = sp.symbols('t beta eta', positive=True)
lam = (beta/eta) * (t/eta)**(beta-1)
is_positive = sp.ask(sp.Q.positive(lam))
print(is_positive) # True
```
CROSS_MODULE_REFS: §7.1
SEVERITY: notation_cleanup
PROPOSED_FIX: Rename the decay constant in §7.4 to a different symbol (e.g., $k(t)$) and clarify that it represents the local exponential decay rate of the sliding window $v_w(t)$, distinct from the global NHPP intensity $\lambda(t)$.

FINDING_ID: MATH-06
COMPONENT: §6 Combined Machine-HIL Detection Model (G_n)
CLAIM: The HIL detection probability $p_{H,j,k}$ can easily exceed 1.0 due to unconstrained multiplicative domain modifiers, violating the axioms of probability.
EVIDENCE: The formula is $p_{H,j,k} = f_k(E, M) \cdot \prod_s (1 + \lambda_s \cdot V_s)$. While the base function $f_k(E, M)$ is bounded in $[0,1]$, the product term has no upper bound. If a domain operator plugs in multiple positive variables (e.g., two variables with $\lambda_s = 0.5$ and $V_s = 1$), the product becomes $1.5 \times 1.5 = 2.25$. If $f_k(E, M) = 0.8$, the resulting probability is $1.8$, which breaks the subsequent $G_n$ calculation by producing negative miss probabilities.
CONSTRAINT_CLASS: HARD
CONFIDENCE: 0.99
VERIFIABLE_CLAIM: For $f_k(E,M) = 0.8$, $\lambda_1 = 0.5, V_1 = 1$, and $\lambda_2 = 0.5, V_2 = 1$, the resulting probability $p_{H,j,k}$ evaluates to 1.8.
SYMPY_EXPRESSION:
```python
import sympy as sp
f_k, l1, v1, l2, v2 = 0.8, 0.5, 1.0, 0.5, 1.0
p_H = f_k * (1 + l1*v1) * (1 + l2*v2)
print(p_H > 1.0) # True
```
CROSS_MODULE_RE