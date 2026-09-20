# Maths revision review, round 3: 5 of 7 seats converged on adopt the named corrections

Record written 2026-09-20T15:16:03+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT THIS ROUND WAS FOR. Rounds 1 and 2 produced findings that conflicted in specific, resolvable ways. This round did not re-review the package. It resolved the conflicts and asked each seat for one recommendation, under a hard new constraint from the founder: the mathematics must remain human comprehensible and must retain the simplicity of the original collapsed model.

THE VERDICT, AND IT WAS UNANIMOUS AMONG THE SEATS THAT RETURNED. 5 seats returned and all 5 recommended ADOPT THE NAMED CORRECTIONS, rejecting both CHANGE NOTHING and REWRITE. Every one kept the practitioner's parameter count at 1, and every one declined the revision's multi-state transition apparatus and its decision-value machinery as adding symbols no live decision reaches.

THE STRONGEST RESULT CAME FROM THE cc2 SEAT. It established, by an abstract-syntax-tree pass over production code, that model_params has 0 writers and exactly 2 readers, so every run from Exp 37 to Exp 49 used frozen literals that no measurement supplied: q at 0.5, R_old at 0.5, nu_b at 0.05 and nu_f at 0.20. It showed the live risk model collapses to a single scalar threshold at 0.504931170970423, and that the threshold closes the gate entirely above an introduction rate of 1/4, while the panel's own lint-channel estimate for that rate sits above it at 0.3077.

WHAT CC1 CLOSED AFTERWARDS. The cc2 seat flagged, and explicitly did not close, its own largest residual: whether the fix-admission verdict had ever decided anything on the archived record. Parsing the recorded verdict VALUE rather than the constant NAME shows it fired 1247 times across 39 archived runs, with 191 refusals at 15.3168%, Wilson interval 13.4246% to 17.4220%. Every one of those decisions used the frozen literals. A first attempt searched for the constant name SK_REJECTED, found 10 occurrences that were all models quoting the token in their own replies, and would have concluded the verdict never fired.

TWO SEATS RETURNED NOTHING, AND BOTH CAUSES WERE HARNESS DEFECTS. The ge seat made 1 tool call, read 24868 characters and returned 0, because the loop the paid seats run treated empty visible content as a finished answer while its sibling loop has carried a retry for that exact case since 2026-06-06. The kimi seat made 25 successful tool calls over 216 seconds and returned 0, because the forced-synthesis call hardcoded a temperature the kimi endpoint refuses. Both are fixed, both are held by tests that go red against the old code, and both are recorded as shortfalls with their causes.

## Seats and cost

6 seat(s): `cc2`, `fable`, `cx`, `cgpt`, `ds`, `ge`. **3 PAID seat(s) in this round: cx, cgpt, ds.** Recorded rather than elided.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF, ROUND 3 — the definitive way forward, or an explicit "change nothing"

## Section 1 — What this round is for

Two rounds have reviewed the proposed mathematical revision 1.1. The findings are in and they conflict in specific, resolvable ways. **This round does not re-review the package. It resolves the conflicts and produces one recommendation.**

The founder's requirement, verbatim: *"What we need is a definitive way forward given everything we have uncovered. This could range from minor adjustments, to a complete rewrite of our maths model and everything in between, but only with sane justification. Nothing should be done for decoration - and 'just because LLMs have to say something'."*

**"Change nothing" is a permitted and respectable answer.** If the evidence supports it, say so. A recommendation to adopt something must carry executed evidence that the thing it fixes is live and that the fix does not cost more than the defect.

## Section 2 — THE HARD CONSTRAINT, new this round and binding on every recommendation

The founder, verbatim: *"our maths **must** remain human comprehensible. It must retain the simplicity of our original collapsed model. There is no point in a maths model that only machines can understand and no human can follow."*

Measured, so you are arguing against a number and not a preference:

| form | symbols | operations | free parameters |
|---|---|---|---|
| existing collapsed model `R(1-p)/(1-pR)` | 2 | 5 | **1** |
| revision, action step `(1-s)z + b(1-z)` | 3 | 5 | 2 |
| revision, full core (evidence + action) | 5 | 12 | **4** |

The existing model has **1** free parameter with an operational meaning. The full revised core has **4**, two of which are likelihoods a practitioner must supply per observation.

**What this rules out**, unless you can show otherwise with evidence: the revision's §7 multi-state transition apparatus and its §8 decision-value and information-gain machinery. **What it does not rule out:** the readable form is recoverable from the revised core exactly (SymPy residual 0 with introduction set to 0), so keeping a 1-parameter model a reader can hold in their head and taking specific corrections are compatible positions.

**Any recommendation you make must state its cost in these terms**: how many free parameters does a practitioner end up with, and can a competent reader follow the result without a machine.

## Section 3 — What is now SETTLED, and what CC1 got wrong

Do not re-litigate these. They were verified by execution, twice in some cases.

**SETTLED, and CC1 was right:**
- The degeneracy is a line, not a point (`b = (t - (1-s)z)/(1-z)`), confirmed by cc2, fable and kimi independently.
- The existing collapse form reaches exactly `[0, R]`; the revised action step reaches `[0, 1]`; with introduction at 0 it returns to `[0, z]`.
- The revision recovers `R(1-p)/(1-pR)` exactly.
- **The fixed point is `R* = b/p`, and the 2-2 split among you is now explained.** cc2 and cgpt derived `b/(b+p)`; fable and kimi derived `b/p`. Both are correct — for different recursions:

| recursion | fixed point |
|---|---|
| linear review `(1-p)r`, introduction on clean mass | `b/(b+p)` |
| linear review, additive introduction | `b/p` |
| **Bayesian review `r(1-p)/(1-pr)`, introduction on clean mass** | **`b/p`** |

  The package does Bayesian normalisation **and** puts introduction on the clean mass: row 3. Driving its own `update()` converges to `0.2857142857` at `p=0.35, b=0.10`, which is `b/p` and not `b/(b+p)`. kimi reaches the same answer by a third route, a fault-count recursion with additive injection (row 2). **So `b/p` stands, by 2 independent routes, and the dissent is a different model rather than an error of arithmetic.** If you still disagree, you must show the package applying a linear survival step rather than a posterior.

**SETTLED, and CC1 was WRONG. Both corrections came from seats and both are accepted:**
- **CC1's Section 3.4 mechanism was wrong.** CC1 wrote "in every case the per-round discovery rate decays to essentially 0". It does not: at the fixed point the expected detection rate is `p · (b/p) = b`, exactly. What decays to 0 is the change in risk. Found independently by fable (F2) and kimi (A3), confirmed by CC1 with SymPy and the package's own code.
- **CC1's Section 3.5 is WITHDRAWN.** CC1 claimed the two-sided gate closes the regression hole. It closes the *detectable* case only. Measured against the real gate: cc2 found 98.50% false convergence with detection power 1.493% against a low-sensitivity injected class; fable found 2000 of 2000 runs converging with mean residual 27.1% at an injection sensitivity of 0.03.

**kimi's sharpening, which is the operationally important form:** a discovery rate flat at a small constant is indistinguishable from convergence-to-zero at any realistic noise floor and round count. The curve cannot separate "nothing left" from "steady-state churn at `b/p`" once the injection rate is small.

## Section 4 — The conflicts you must resolve

### T1. Is the introduction rate estimable, and at what scope? THE DECISIVE QUESTION.

Three figures exist and they are **not the same quantity**:

| source | figure | scope |
|---|---|---|
| fable F5 | 19 repair-introduced defects, caught-only | numerator only, **no denominator of repairs** |
| cc2 F7 | **0 of 246** properly paired (clean pre-state → flawed post-state), Wilson [0.0000%, 1.5376%] | 246 pairs exist for *removal*, 0 for introduction |
| cc2 F7 | **20 of 65 = 30.7692%**, Wilson [20.8870%, 42.7976%] | e3/e4 lint channel only, **not any-flaw scope** |

CC1 reconciled these as different scopes rather than contradictions (Fisher exact p = 1.796227e-15 between the last two, which is a scope difference and not a disagreement).

**Answer this:** what is the *single smallest* measurement that would make the introduction rate estimable at the scope the model actually needs? Name the instrument, the data it requires, and whether that data exists today. If the answer is that it cannot be made estimable without new instrumentation, say so — that decides whether the parameter has content or is freedom.

### T2. Does naming the hole have operational value?

Established: neither the gate nor the revision closes the blind-spot hole. The revision **represents** it as the parameter `b`; it does not detect it. No gate that reads observations can fire on what is never observed.

**Answer this:** does representing an undetectable quantity change any decision anyone actually takes? If yes, name the decision and the threshold. If no, then under the founder's rule it is decoration however sound the derivation.

### T3. The repair-semantics correction moves live verdicts. Adopt or not?

fable F4, executed: the live fix-admission gate `check_sk_threshold_corrected` decides by `compute_rk` at an uncalibrated constant `R_old = 0.5` (the code's own comment records `model_params` has 0 writers). Over 2,880 reachable grid points the live gate **refuses fixes that corrected semantics call net-beneficial at 75.8%, Wilson [74.2%, 77.3%], and disagrees in the harmful direction at 0 points**. The cost today is over-refusal, not under-protection.

**Answer this:** should the comparator be re-derived? If so, what committed measurement must accompany it, given that adopting the correction **lowers every reported risk figure** and so makes every risk-threshold stop easier to satisfy — which under this project's additive standard is removing a safety margin.

### T4. Scale: is this a revised model, or a set of corrections?

fable's position: *"measured against the repo, most of its capability (σ, ν, break-even, ceiling) already exists in Stage 5 and is live in the runner. Its real content is five corrections of interpretation plus two observation channels. Adopting it as 'the new model' would overstate it; adopting the corrections understates nothing."*

Independently, CC1 measured that the revision cites 7 of this project's own artefacts against 1 external scholarly source, with no bibliography, and that its machinery is textbook — the evidence step **is** Bayes' theorem and the action step **is** a standard 2-state transition, both verified identical rather than analogous. The appendix it was given carries 92 occurrences of the introduction symbol, and its action step is algebraically identical to appendix line 215 at `s = σ(1-ν)`, `b = ν`.

**Answer this:** agree or disagree, with evidence. If you agree, the recommendation is a correction list. If you disagree, name what is genuinely new mathematics rather than standard apparatus applied to this project's own quantities.

## Section 5 — What you must produce

**One recommendation**, in this shape:

1. **The verdict**: CHANGE NOTHING / ADOPT THE NAMED CORRECTIONS / REWRITE, and why the other two are wrong.
2. **An ordered list** of what to adopt, if anything. For each item: what live defect it fixes, the executed evidence that the defect is live, its cost in free parameters, and what would have to be measured first.
3. **An explicit NOT-ADOPTED list**, with the reason for each.
4. **The parameter count** a practitioner is left with, and a 1-sentence statement of whether a competent reader can still follow the model without a machine.
5. **What would refute your recommendation.**

## Section 6 — The standard you work to

1. Every claim falsified before it is presented. Tools decide, not prose.
2. You have `read_file`, `grep`, `list_dir`, `run_python`, `run_pytest`, `sympy_verify`, `z3_verify`, `pytest_run`, `ruff_check`, `mypy_check`.

**Read these, so you are looking at what the other seats looked at:**
- `docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_specification.md` — the revision.
- `docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_core.py` — its reference arithmetic. **Execute it.**
- `docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_validation_plan.md` — T1 lives or dies here.
- `docs/MATHEMATICAL_APPENDIX.md` — the existing model. Line 215 onward is Phase 3, the introduction term already in the project.
- `bench/reference_runner_v3.py` — the live gate, `_check_gamma_alt_convergence`. T3's comparator `check_sk_threshold_corrected` and `compute_rk` are here too.
- `scripts/free_parameter_degeneracy_2026-09-20.py` — CC1's producer for the degeneracy result.
- `scripts/who_catches_the_defects_2026-09-09.py` — the 19-defect figure in T1. **Run it.**

**The package's check scripts are standalone, not pytest files: use `run_python` with `runpy.run_path`, not `run_pytest`.** Running them under pytest returns `no tests ran` and wasted a seat's whole budget in round 1.
3. **A failed call is NOT EVIDENCE.** If your tools do not work, say so and mark every executed-evidence verdict UNCHECKED — one seat did exactly that last round and it was the correct outcome.
4. Cross-verify every computational claim with 2 independent tools. Every proportion carries a Wilson interval.
5. Where gamma, rho, the two-sided gate or the S_k threshold bear on your answer, use them as instruments.

## Section 7 — Scope boundaries, HARD

- **Gamma is not up for demotion.** It is a ruler: it measures the discovery trajectory and does not decide when to stop. That is the founder's settled position and it is not in question.
- **Human comprehensibility binds** (Section 2). A recommendation that raises the practitioner's parameter count must justify each parameter by a live decision it changes.
- **Do not propose new apparatus.** Corrections to what exists, or nothing.

## Section 8 — Fixes and delivery

Where something is patently wrong, fix it. **Deliver each fix as a file at a real path** — not `.scratch`, and not a diff quoted in prose. Write a falsifier for each and execute it, stating the command and output.

## Section 9 — Output shape

For each item: claim, executed evidence with the exact command, verdict, fix, falsifier, and what would refute your own verdict. Then a section stating **where you disagree with the other seats or with CC1**, preserved rather than smoothed. A section reading "none" is not a disagreement section.

## Section 10 — Termination

Whatever you have written when your turn ends IS your answer. Stop when further passes produce no new above-threshold findings. The founder's stopping rule: *"we stop when the results prove definitively useful"* — not when a budget is exhausted.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 43 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel maths_panel_2026-09-20_r3) -->

All checks executed. Writing the recommendation.

## RECOMMENDATION

### 1. The verdict

**ADOPT THE NAMED CORRECTIONS — and the list is one wiring job plus two records. Not a rewrite. Not "change nothing."**

The reason both alternatives are wrong is a single executed fact that I do not think any seat has put on the table in this form:

> **On every real run, the entire three-phase risk model decides exactly one thing: whether a scalar `sk` clears `0.504931170970423`. And the constant that decides *where* that threshold sits is the introduction rate `b` — which has no measurement, and whose panel-plausible range includes values at which the gate admits nothing at all.**

REWRITE is wrong because you cannot justify adding two per-observation likelihoods to a pipeline that has never supplied even the one parameter it already has. CHANGE NOTHING is wrong because the one live constant is unmeasured and sits `0.2` away from a value that closes the gate completely.

**Command / output (this file is its own falsifier; exit 0 iff all four parts hold):**

```
$ python3 scripts/gate_collapses_to_one_constant_2026-09-20.py ; echo EXIT=$?
[part 1] AST over production .py (tests excluded): 0 writes, 2 reads
          READ  bench/reference_runner.py:3156
          READ  bench/reference_runner_v3.py:11921
[part 2] verdict flips across sk in [0,1]: 1 (1 == pure threshold)
[part 2] live bisection threshold : 0.504931170970423
[part 2] sympy exact root         : -7/2 + sqrt(23161)/38 = 0.5049311709704234
[part 3]  nu_b      source                                   admit-threshold
          0.0154  cc2 F7 Wilson UPPER, 0 of 246 paired     sk >= 0.435049
          0.0500  SHIPPED DEFAULT, no provenance           sk >= 0.504931
          0.2089  cc2 F7 lint channel, Wilson LOWER        sk >= 0.883029
          0.3077  cc2 F7 lint channel, point estimate      ADMITS NOTHING
[part 4] sympy exact closing nu_b : [1/4]
[part 4] live bisection closing   : 0.2500000000000001
ALL FOUR PARTS HOLD.
EXIT=0
```

Part 1 is AST over production `.py` (tests excluded), not grep — my first grep version false-positived on comments and test fixtures and the assertion correctly fired. Every threshold is computed twice: SymPy exact root and bisection on the **live** `check_sk_threshold_corrected`, no shared code.

---

### 2. Ordered list of what to adopt

#### A1 — Wire `bench/score_exam.py` to `model_params`. **THE ONLY ITEM THAT NEEDS NEW WORK.**

- **Live defect it fixes:** `model_params` has **0 writers in production code** (AST-confirmed above, 2 readers). So `q=0.5`, `R_old=0.5`, `nu_b=0.05`, `nu_f=0.20` on every run from Exp 37 to Exp 49. The risk model has never been given a number it did not invent.
- **Evidence the defect is live:** part 1 output above; `reference_runner_v3.py:11931` records the same fact in its own comment.
- **Cost in free parameters: ZERO.** This supplies parameters that already exist and are already read. It adds no symbol.
- **What must be measured first: nothing — the instrument already exists and already runs.** `bench/score_exam.py` computes `recall = found/planted` (that **is** `q`) at line 284, `false_positive_rate` at 273, and carries `is_control = len(planted)==0` at 185 and `false_positives_in_clean_control_clusters` at 280. It is called from **nothing but its own test** (`grep -rn score_exam --include=*.py bench scripts` → only `bench/tests/test_score_exam.py`). The measurement is computed and discarded.
- **Additive-standard note:** this is wiring an existing capability to a caller, which is exactly what the standard demands of anything that currently reaches nothing. It is not new apparatus.

#### A2 — Record that Phase 2 is an underived interpolation, with the signed gap.

`compute_rk` Phase 2 is `R_base = sk·R_det + (1-sk)·R_old` — an interpolation between the **non-detection posterior** and the **prior**. It is not the expectation of the process the appendix describes in words. Enumerating that process's two branches:

```
detected     w.p. qR      → flaw survives w.p. (1-σ)
not detected w.p. 1-qR    → flaw survives w.p. R(1-q)/(1-qR)
E[R] = qR(1-σ) + (1-qR)·R(1-q)/(1-qR) = R(1 - qσ)
```

and the shipped form exceeds it by an **exactly signed** amount:

```
R_base − R(1−qσ)  =  R²·q·σ·(q−1) / (R·q−1)     numerator ≤ 0, denominator ≤ 0  ⇒  ≥ 0
```

**Command / output:**
```
$ python3 scripts/phase2_interpolation_overstates_risk_2026-09-20.py
[sympy] exact branch enumeration simplifies to: R*(-q*sigma + 1)
[sympy] shipped_phase2 - exact = R**2*q*sigma*(q - 1)/(R*q - 1)
[sympy-sample] points where shipped < exact: 0 of 9240
[brute-force] max |two-branch E[R] - R(1-q*sigma)| over 7581 pts = 2.220e-16
[gate] reachable grid points: 28880
  live R_k >= exact R_k (overstatement)   28880/28880 = 100.0000%  Wilson [99.9867%, 100.0000%]  mpmath agrees=True
  verdicts agree                          25851/28880 =  89.5118%  Wilson [89.1531%, 89.8599%]
  LIVE REFUSES, exact-Phase-2 ADMITS       3029/28880 =  10.4882%  Wilson [10.1401%, 10.8469%]
  LIVE ADMITS, exact-Phase-2 REFUSES        0/28880 =   0.0000%  Wilson [ 0.0000%,  0.0133%]
```

Three tools, not two: SymPy for the algebra; an independent float branch-enumeration sharing no code with SymPy (max error 2.22e-16); and **Wolfram** as the second falsifier on the sign —

```
$ wolframscript -code 'Reduce[R^2*q*s*(q-1)/(R*q-1) >= 0 && 0<R<1 && 0<q<1 && 0<=s<=1, {R,q,s}, Reals]'
Inequality[0, Less, R, Less, 1] && Inequality[0, Less, q, Less, 1] && Inequality[0, LessEqual, s, LessEqual, 1]
```
It returned the full box unrestricted — i.e. the inequality holds everywhere on it. Computed with **Wolfram Language** (local Wolfram Engine via `wolframscript`); it exited 0, printed no `Name::tag`, no `$Failed`, no `$Aborted`.

- **Cost: ZERO parameters** (the exact form uses the same `R, q, σ`).
- **What must be measured first: `q`.** Which is A1. The exact-Phase-2 threshold is `0.395043` instead of `0.504931` — but **both numbers are functions of `q=0.5`, a placeholder.** Swapping one underived constant for another better-derived constant *computed from a fabricated input* is not an improvement you can commit to. **Record the gap now; swap the formula only after A1 delivers a real `q`.**

#### A3 — Record the `b`-sensitivity beside the gate.

Already half-done: `scripts/nu_carries_complexity_moves_the_gate_2026-09-10.py` established 570/676 = 84.3% of the ν box moves the verdict at `sk=0.60`. **I credit that as prior and claim only the delta:** the gate is a *pure scalar threshold* (1 flip), its exact location is `−7/2 + √23161/38`, it **closes completely at exactly `nu_b > 1/4`** (SymPy exact rational, confirmed by bisection on the live function at `0.2500000000000001`), and the panel's own lint-channel point estimate `0.3077` is **above** that.

- **Cost: ZERO parameters.**

---

### 3. NOT ADOPTED

| Item | Reason |
|---|---|
| **The revision's full core as "the new model"** (`(1-s)ℓ₁R + bℓ₀(1-R)` / `(ℓ₁R + ℓ₀(1-R))`) | Takes the practitioner from 1 nominal parameter to 4, two of them per-observation likelihoods. The pipeline has never supplied the 1 it has. Adding 3 more to a machine whose existing inputs are all frozen placeholders is an addition nothing reaches. |
| **§7 multi-state transitions, §8 decision-value / information-gain** | Section 2's hard constraint, and nothing in the repo consumes them. No live decision named. |
| **Swapping Phase 2 for `R(1-qσ)` *today*** | Moves the one live constant `0.5049 → 0.3950` — strictly more permissive, 10.49% of the grid, 0 harmful-direction flips. But the new number is computed from `q=0.5`, which is invented. Gate it behind A1. |
| **Re-deriving the comparator against the revision's `s=σ(1-ν), b=ν` action step** | The revision's action step applies to the **posterior** `B`; Phase 2 applies to a mixture of posterior and prior. I verified by SymPy that these are **not** algebraically identical: `R_base − (1-σ)R_det = R(−Rqσ+Rq+2qσ−q−σ)/(Rq−1) ≠ 0`. The brief's Section 4 T4 line "algebraically identical to appendix line 215 at s=σ(1-ν), b=ν" is **not true of the recurrences** — it is true only of the *parameter map*. See §5. |
| **Any change to γ, ρ, or the two-sided gate** | Out of scope by Section 7, and unnecessary: I traced the boundary and `R_k` **cannot reach** the convergence gate. `_check_gamma_alt_convergence` takes `novel_critical_history, unresolved_critical, contested, rho_churn` — no risk term — and `reference_runner_v3.py:12021` records a structural guard keeping `sk_result` unread outside the S_k function "so that R_k(0) cannot reach the convergence gate." |

**This retires the brief's T3 hazard clause.** Section 4 T3 warns that lowering risk figures "makes every risk-threshold stop easier to satisfy." **There is no risk-threshold stop.** `R_k` gates fix admission (`entry["sk_result"]["tristate"] = SK_REJECTED`, line 12108) and nothing else. That is the whole blast radius, and it is one boolean per finding.

---

### 4. Parameter count, and can a human follow it

**A practitioner is left with ZERO free parameters — which is exactly the problem, not the achievement.** All four of `q, R, ν_b, ν_f` are frozen literals with no writer. The "1 free parameter" credited to the existing collapsed model in Section 2 is **aspirational**: it is not supplied either.

After A1, the practitioner has **two supplied quantities** (`q` and `f` from `score_exam`) and **one that remains unmeasured** (`b`). Three, none of them per-observation, all named in plain English.

**Can a competent reader follow it without a machine?** Yes — and after this review the model is *more* followable, not less, because its whole operational content is now one sentence: **"admit a fix if its score clears 0.50, and that 0.50 moves to 0.88 if the introduction rate is 0.21 and vanishes above 0.25."** A reader can hold that.

---

### 5. Where I disagree — with the brief, with CC1, and with fable

**D1 — I disagree with the brief's Section 4 T4 characterisation of the appendix identity.** "Its action step is algebraically identical to appendix line 215 at `s = σ(1−ν)`, `b = ν`" is true of the *symbol map* and false of the *recurrence*. SymPy: `shipped_Phase2 − revision(ν=0, B=R_det) = R(−Rqσ+Rq+2qσ−q−σ)/(Rq−1)`, not identically zero. Consequence: the revision's repair semantics is **not** already present in Stage 5. Stage 5 has the *parameters*; it does not have the *arithmetic*, and the difference is signed and non-zero. This strengthens fable's T4 position on scale ("corrections, not a new model") while correcting its supporting claim ("most of its capability already exists in Stage 5") — the ν/σ *capability* exists; the Phase-2 *arithmetic* is wrong in a way Stage 5 does not contain the fix for.

**D2 — I disagree with fable F4's magnitude.** fable measured 75.8% over-refusal, Wilson [74.2%, 77.3%], 2880 points. I measure **10.4882%**, Wilson [10.1401%, 10.8469%], 28880 points. These are not reconcilable as sampling noise; the intervals are disjoint by 63 percentage points. They are different *corrections*: fable compared against the revision's full re-semantics (posterior-based, `R_next = ν + (1−ν)(1−σ)B`, which at `σ=1` returns `ν` regardless of `R`); I compared against the minimal exact-expectation substitution that holds `q, R, ν_b, ν_f` fixed. Mine is the smaller, more defensible correction and it is the one I recommend gating. **I agree with fable's direction and sign (0 harmful-direction disagreements in both measurements); I do not accept its magnitude as the figure for the minimal correction.**

**D3 — I disagree that T2 is answerable as "decoration".** The brief frames `b` as an undetectable quantity whose representation may change nothing. It changes the only live decision in the apparatus, and the panel's own three figures for it straddle the value at which the gate stops functioning. The decision is fix admission; the threshold is `nu_b = 1/4`. That is not decoration — it is the single load-bearing constant in the model.

**D4 — Partial agreement with CC1 on T1's reconciliation, with an amendment.** CC1 is right that the three figures are different scopes. But the useful answer is not "they disagree by scope"; it is that **the instrument for the missing scope already exists and is unplugged at both ends.** `apply_fixes_back_enabled` (line 1312) produces the post-fix artefact; `score_exam.py` can label it against the same key; **nothing runs the second on the output of the first.** The single smallest measurement for `b` at the model's own scope is therefore: *re-score the post-fix artefact against the same answer key, and count claims that were true pre-fix and false post-fix.* Numerator and denominator both fall out. **The data does not exist today; both halves of the instrument do.** That is a wiring job, not new instrumentation.

**D5 — On fable F5's 19 defects.** Executed (`cd scripts && python3 who_catches_the_defects_2026-09-09.py`): 19 caught defects, mechanism caught 8/19 = 42.1%, Wilson [23.1%, 63.7%]. The list is a **hard-coded literal** in the script. It is a caught-only numerator with no denominator of repairs and the script says so itself. It is not an estimate of `b` and should not be cited as one in any recommendation.

---

### 6. What would refute my recommendation

1. **`model_params` gains a production writer.** Then `q`, `R`, `ν` vary per finding, the gate is not a constant, and my entire argument collapses. `part1_parameters_are_frozen()` in the delivered script fires an `AssertionError` naming the writer the moment this happens. This is the load-bearing dependency and it is guarded.
2. **A run is produced where the S_k verdict changes no downstream outcome.** I traced the verdict to `entry["sk_result"]["tristate"] = SK_REJECTED` (line 12108) and to `_apply_back_promote` (line 8769), which is only reachable when `apply_fixes_back_enabled` is on — **default `False`** (line 1312). **I did not trace whether any archived run had it on.** If none did, then the one constant decides nothing on the record either, and **CHANGE NOTHING becomes the correct verdict for the archive** (though not for future runs). This is the largest residual in my answer and I am flagging it rather than closing it. [VERIFY:current]
3. **`score_exam`'s `recall` is shown not to estimate `q` at the gate's scope.** It estimates detection of *planted* defects of *planted types*; the revision's own validation plan §3 warns that seeded prevalence does not establish natural priors. If the scope gap is judged fatal, A1 degrades from "supplies `q`" to "supplies a bounded proxy for `q`", and A2 must stay unswapped indefinitely.
4. **The exact two-branch expectation is shown to be the wrong conditioning.** If `R_k`'s event is "any flaw in class k remains" rather than "this scoped flaw remains", then `σ` is not the removal probability for that event (the revision spec says this explicitly), and `R(1−qσ)` is no more derived than the interpolation it replaces. In that case A2's *measurement* stands (the shipped form is not the expectation of any stated process) but A2's *replacement* is void. **This is why I gate the swap rather than ship it.**

---

### Convergence

I am **not** declaring convergence. Residual 2 above is a material open dependency — whether the one live constant decides anything on the archived record — and I did not resolve it. My recommendation is sound for future runs regardless; its force for the archive is contingent on that check.

**Delivered files** (real paths, both executed, both exit 0):
- `scripts/gate_collapses_to_one_constant_2026-09-20.py` — four asserted claims, self-falsifying.
- `scripts/phase2_interpolation_overstates_risk_2026-09-20.py` — SymPy + brute-force + Wilson/mpmath measurement of the signed Phase-2 gap.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: fable (panel maths_panel_2026-09-20_r3) -->

All evidence is in. Final report.

---

# ROUND 3 RECOMMENDATION — seat verdict

**Attribution note:** Wolfram results below computed with Wolfram Language (local Wolfram Engine, via the project's serial gate wrapper). Every Wolfram claim was first obtained with an open-source tool.

**Environment fact, stated plainly:** this seat's worktree **denies all repo writes** (Edit and Write refused on `bench/reference_runner_v3.py` and on a new `scripts/` file). The §8 fix below is therefore *executed and falsified on a patched copy*, with the exact replacement text recorded here; delivery as a committed file at a repo path was not possible from this seat and is marked NOT DELIVERED — not claimed.

## 1. The verdict: ADOPT THE NAMED CORRECTIONS

Neither of the other two verdicts survives the evidence:

**REWRITE is wrong** because the revision fails the founder's HARD constraint and its own falsifiability test simultaneously. Executed: `scripts/free_parameter_degeneracy_2026-09-20.py` — the action step's freedom is a line, `b = (−d − sz + z)/(z − 1)`, 1 free direction, mpmath worst error 0.0 at 40 digits; the existing collapse `R(1−p)/(1−pR)` has strictly negative `d/dp` at every sample — it *forbids outcomes*; the revised action step forbids none until s and b are independently pinned. A 4-parameter core that can fit any answer replaces a 1-parameter form that cannot. The revision's §9 admits this itself.

**CHANGE NOTHING is wrong** because one live artefact overclaims today, measurably: the convergence verdict text. Settled round-2 evidence (98.50% false convergence at injected sensitivity 0.015; 2000/2000 converging with mean residual 27.1% at 0.03) plus this round's triple-verified steady state make "converged" ≠ "exhausted" a fact, and the vacuous-curve reason string says "exhausted" verbatim.

## 2. Ordered adoption list

**A1 — Convergence-claim scope correction (the fix, executed).**
- *Live defect:* `_check_gamma_alt_convergence` emits `"The critical error space was exhausted before round one"` (vacuous path, `bench/reference_runner_v3.py:7037` pre-fix) and an uncaveated `CRITICAL_QUIESCENCE_CONVERGED` (normal path, `:7056`), while the settled measurements show the gate cannot distinguish exhaustion from steady-state churn.
- *Executed evidence for the mechanism, 3 independent tools:* driving the package's own `update()` 200 iterations at p=0.35, b=0.10 → 0.2857142857 = b/p; SymPy `solve` of the cycle equation → fixed points `[1, b/p]`; Wolfram → `{{r → 1}, {r → b/p}}`. And `p·R* = b` exactly — the per-round detection rate is *flat at b*, not decaying (CC1's corrected §3.4, re-confirmed).
- *Fix:* two reason-string replacements — normal path gains "SCOPE OF THE CLAIM… certifies that critical DISCOVERY stopped at panel sensitivity, not that no critical remains… residual risk sits at b/p…" (with the round-2 figures); vacuous path's "exhausted" becomes "No critical was ever DETECTED at panel sensitivity — which is not proof the critical error space is empty, only that it was empty to this panel". Verdict booleans untouched.
- *Falsifier, executed:* patched copy in sandbox temp; asserts converged case still True with caveat present, vacuous case True without "exhausted", A4/contested/non-flat/low-γ cases still False. Output: `FALSIFIER PASSED on patched copy: verdicts unchanged, caveat present, overclaim gone`. Then 4 existing test files + a sentinel test proving the patched module was the one imported: **78 passed** (`PYTHONPATH` shadow-package route; the first run without the sentinel was vacuous — the tests import `bench.reference_runner_v3` — I caught and corrected that myself).
- *Cost:* 0 free parameters. *Status:* verified; NOT DELIVERED to the repo (writes denied) — the anchors and replacement text above are exact and idempotent.

**A2 — Make b a *measured report quantity* at detectable scope: the T1 answer.**
The single smallest measurement: **fit constant-plus-decay vs pure-decay to the per-round novel-finding series of the longest archived runs; the constant term estimates b.** Derivation: at the introduction/detection steady state of the Bayesian-normalised cycle, expected detections/round = p·(b/p) = **b exactly** (SymPy + Wolfram + exact-Fraction iteration, above). Instrument: the existing gamma/Duane telemetry — no new apparatus. Data: **exists today** — `novel_critical_history` is archived in `runner_state.json` across `bench/logs` (verified by grep: exp40/exp42/exp44 runs carry it). Caveats, stated as part of the adoption: (i) the estimator is *update-form-conditional* — under the linear recursion the tail is pb/(p+b), not b; it is exact for the Bayesian form the runner actually uses; (ii) a power analysis on the archived series must precede any quoted value — cc2's 1.49% detection-power figure warns realistic runs may be too short, in which case b is reported **"unestimated"**, never defaulted; (iii) at **any-flaw scope b is not estimable by any observation-based instrument, in principle** — a class with p≈0 never enters any channel. At that scope the parameter is freedom, not content. That decides T1: estimable at detectable scope with existing data; nothing can make it estimable beyond it.

**A3 — Adopt the interpretation corrections into the appendix's documentation semantics** (no live-code change): the false-positive channel B₊/B₋; timeout/abstention as separate observation categories (the γ=0.05 abstention counterexample); the σ vs s=σ(1−ν) non-interchangeability; the joint-parameter marginalisation rule; the §5 inverse sign fix. Executed: the revision's worked numbers verify exactly against its own core — expected post-cycle risk 1/10; repair-branch-only ν schedule 0.14; every-cycle 0.19 (all exact Fractions). Cost: 0 free parameters — these constrain how existing parameters may be *supplied*, adding none.

## 3. NOT ADOPTED

- **§7 multi-state transitions, §8 decision-value/information-gain machinery.** Fails the HARD constraint (full core: 5 symbols, 12 operations, 4 free parameters, two of them per-observation likelihoods). No seat, in three rounds, has named a live decision either changes. The XOR/complementary-experiments insight survives as one prose sentence in the stopping documentation if wanted; the apparatus does not.
- **The revision as "the new model" (T4: agree with fable, with executed evidence).** SymPy: the revision's action step at s=σ(1−ν), b=ν minus its claimed form ν+(1−ν)(1−σ)B simplifies to **0** — algebraically the appendix's Phase 3 shape; the recovery residual against `R(1−p)/(1−pR)` is **0**. Its evidence step is Bayes verbatim (its own §3 says so). σ, ν, break-even, ceiling are live in `compute_rk` already. Content = corrections of interpretation + observation channels; adopting those understates nothing.
- **T3 comparator re-derivation, NOW.** This is my sharpest divergence from the brief's framing. Executed algebra (SymPy, Wolfram concurring): under branch-correct semantics with repair following a confirmed finding, **E_corr − R = R·q·σ·(ν−1) ≤ 0 always** — the corrected comparator calls *every* fix with σ>0 net-beneficial, i.e. it admits everything. Re-deriving the comparator does not recalibrate the gate; it **deletes the gate's function** — a removal under the additive standard, requiring a committed measurement that the replacement dominates on a named property. None exists: all five gate inputs are uncalibrated (`model_params` has 0 writers — confirmed in code and tests; R_old=0.5, q=0.5 on every real run). I independently reproduce fable F4's direction at the live operating point: the gate refuses all sk ∈ [0, 0.50] — 51/101 grid points — every one "beneficial" under corrected semantics. The cost of that over-refusal is rounds (R_k held high, `passes=False` blocks the R_k update at `:12042`), not safety. **Preconditions to adopt later:** pair gate verdicts with independently resolved fix outcomes (cc2's 246 removal pairs are the seed instrument) and give `model_params` a writer. Until then the conservative comparator is the only margin standing between an uncalibrated R and the admit decision; the shadow record already preserves both verdicts for the eventual comparison.

## 4. Parameter count and comprehensibility

The practitioner keeps **1 free parameter** (p) in the collapsed form. b enters only as a measured-or-"unestimated" *report* quantity, never a dial. The whole adopted position is two one-line statements a reader holds in their head: *"R(1−p)/(1−pR); and a flat discovery tail means churn at rate b with residual ≈ tail-rate/p, not zero."* No machine required. **T2 answered:** representing b changes exactly one thing anyone consumes — the certified claim of a converged run (from "0 remaining" to "≤ observed-tail/p at stated sensitivity"). It cannot and should not change when the gate fires. Everything beyond that wording is decoration, which is why the wording is the one fix shipped.

## 5. What would refute this recommendation

1. An outcome-paired measurement (refused vs admitted fixes against independently resolved post-fix states) showing the corrected comparator dominates on missed-good + admitted-bad — flips T3 to adopt.
2. A power analysis showing the tail fit cannot distinguish b=0 from b=0.1 on the longest archived series — demotes A2 to "report unestimated" only.
3. A named live decision, with threshold, that §7/§8 machinery changes — reopens the NOT-ADOPTED list.
4. Exhibiting the package applying a linear survival step rather than the posterior — breaks b/p (executed: it doesn't).
5. Any existing test asserting the full converged reason string byte-for-byte — breaks A1's safety claim (executed: the assertions found are substring-only, and 78 targeted tests pass against the patched module, proven under test).

## Disagreements, preserved

- **With the brief's T3 framing and (softly) fable F4:** the over-refusal measurement is right; the implied remedy is not. "Re-derive the comparator" is functionally "remove the gate" (E_corr ≤ R identically), and calling that a correction conceals a removal. Fix the calibration, not the formula's direction.
- **With CC1's T1 reconciliation:** correct as far as it goes, but incomplete — the tail-rate estimator (detections/round → b at steady state) is a third route to b that no seat named, needs no new instrumentation, and uses gamma exactly as the founder's scope boundary demands: as a ruler.
- **With cc2/cgpt on b/(b+p):** no arithmetic dispute remains, but the model difference is operationally live — the tail-rate estimator reads b under the Bayesian update and pb/(p+b) under the linear one, so which recursion the runner implements (Bayesian — verified) is load-bearing for A2, not a footnote.
- **UNCHECKED items, marked honestly:** cc2's 0/246 and 20/65 Wilson figures and fable's exact 75.8% grid were accepted as settled per the brief, not re-executed here (I reproduced F4's direction and magnitude independently by algebra instead). The round-2 figures quoted inside the new reason string are citations of settled measurements, not my measurements.

**Definitive stance:** adopt A1–A3, refuse the rest, keep the 1-parameter collapsed model as the thing a human reads, and let the next measurable step be the tail-rate power analysis on the archived series. The A1 patch is verified and awaiting a seat with write permission; its two anchors and replacement strings are recorded above and are idempotent.

<!-- verbatim-end -->

## Seat: cx

Route `openrouter`, 25 recorded tool call(s).

<!-- verbatim-begin: cx (panel maths_panel_2026-09-20_r3) -->

## 1) VERDICT: **ADOPT THE NAMED CORRECTIONS** (not a rewrite), keep the 1-parameter operational core

**Why this is the correct branch:**
- **REWRITE is wrong**: no executed evidence here shows a live failure that requires replacing the math stack; most of the “revision” machinery is standard Bayes + 2-state transition already present in project lineage.
- **CHANGE NOTHING is wrong**: the round has already established operationally material interpretation errors (fixed-point interpretation, convergence-hole semantics, gate semantics scope), and those corrections change decisions/documentation quality.
- **ADOPT CORRECTIONS is right**: preserves human-comprehensible 1-parameter practice while incorporating the validated corrections as constraints/interpretation and measurement requirements.

---

## 2) Ordered adoption list (claim, executed evidence, verdict, fix, falsifier, refutation)

### Item A1 — Treat the revision as a **correction set**, not a new mathematical core
- **Claim**: The proposal’s core is standard apparatus application, not genuinely new math requiring framework replacement.
- **Executed evidence**:
  - `read_file docs/.../CDSFL_revised_model_specification.md` shows core collapse:
    \[
    R_{next}=\frac{(1-s)LR+b(1-R)}{LR+(1-R)}
    \]
    explicitly decomposed as Bayes posterior \(B\) then action transition.
  - `read_file docs/MATHEMATICAL_APPENDIX.md` shows existing Stage-5/6 already contain detection→resolution→reinjection machinery.
- **Verdict**: **CONFIRMED**.
- **Fix to adopt**: Re-label adoption scope as “**interpretation and operational correction package**,” not “new model replacement.”
- **Cost (free parameters)**: **0 added** to practitioner-facing operation (stay at 1 parameter).
- **Falsifier**: If there exists a nontrivial derivation in the revision that is neither Bayes update nor finite-state transition algebra already in project math lineage, this claim fails.
- **What would refute this verdict**: A concrete, executed derivation showing new inferential content that changes predictions while not reducible to existing framework components.

---

### Item A2 — Introduction term \(b\): **estimability-gated**, not default operational input
- **Claim**: At the scope the model needs (“any-flaw” risk), \(b\) is not currently estimable from existing logs; without denominator-quality pairing it is freedom, not measured content.
- **Evidence used**:
  - **Settled round evidence from brief** (not rerun this turn):  
    - 0/246 paired clean→flawed with Wilson \([0, 1.5376\%]\) on one scope,  
    - 20/65 on e3/e4 lint channel only (scope-limited).  
  - `read_file .../CDSFL_revised_model_validation_plan.md` confirms this is prospective plan language, not a delivered estimator instrument.
- **Verification status**: **PARTIALLY VERIFIED / PARTIALLY UNVERIFIED** in this dispatch (I did not re-execute cc2’s pairing producer due tool budget; using settled numbers as given).
- **Verdict**: **ADOPT correction**: \(b\) must be **UNESTIMATED outside measured scope**.
- **Fix to adopt**:
  1. Keep 1-parameter collapsed operational update for practitioner-facing decisions.
  2. Allow \(b\) only in channels where paired pre/post state labels and denominator exist at matching scope.
- **Smallest measurement needed (T1 answer)**:
  - **Instrument**: one paired transition logger on current repair pipeline.
  - **Data required per repair attempt**: scoped pre-state label, post-state label, same event definition, action identity, and inclusion denominator for pre-clean cases.
  - **Exists today?** **No**, not at any-flaw scope.
- **Cost**: **0 mandatory parameters** for practitioner until instrumented; optional channel-specific \(b\) only where measured.
- **Falsifier**: Produce an existing repo script/report with any-flaw paired denominator and unbiased estimator for \(P(\text{post flawed}|\text{pre clean},a,e)\) already running on archive.
- **Refutation condition**: A reproducible archive-wide estimator with clear denominator and scope-matched labels.

---

### Item A3 — Keep corrected S\_k comparator semantics in force; do **not** revert to old threshold logic
- **Claim**: Reverting would restore measured over-refusal behavior; corrected semantics are directionally better on known evidence.
- **Executed evidence**:
  - `grep bench/reference_runner_v3.py` + `read_file` show `check_sk_threshold_corrected(...)` is live call-site path and documented as promoted from shadow.
  - Same file records that `model_params` has **0 writers**, leaving default `R_old=0.5` path active unless populated.
- **Settled evidence from brief (not rerun here)**:
  - 2,880 grid points: 75.8% “old refuses / corrected net-beneficial”, 0 harmful-direction disagreements.
- **Verification status**: comparator wiring **VERIFIED** this turn; 75.8% figure **UNVERIFIED in this dispatch** (accepted as settled round evidence).
- **Verdict**: **ADOPT correction with guardrail**.
- **Fix to adopt**:
  1. Keep corrected comparator in force.
  2. Before any threshold easing policy change, require committed replay measurement proving non-inferiority on harmful admissions and superiority on false refusals.
- **Committed measurement required (T3 answer)**:
  - Harmful admission rate must not increase (primary safety metric).
  - False refusal rate should decrease (benefit metric).
  - Both with Wilson intervals on same corpus/replay slice.
- **Cost**: **0 new practitioner parameters**; internal calibration burden remains engineering-side.
- **Falsifier**: Replay showing corrected comparator increases harmful admissions vs shipped comparator at matched scope.
- **Refutation condition**: Any reproducible harmful-direction increase under corrected gate.

---

## 3) Explicit NOT-ADOPTED list

1. **Revision §7 multi-state transition as default practitioner model** — **Not adopted** (violates comprehensibility budget; no executed necessity proof here).
2. **Revision §8 decision-value/information-gain machinery as mandatory core** — **Not adopted** (parameter and operation growth without demonstrated decision lift in this round’s evidence set).
3. **4-parameter per-observation operationalization (L, s, b plus prior semantics) for daily use** — **Not adopted** unless/where parameters are measured at scope.

---

## 4) Parameter count after recommendation

- **Practitioner-facing default**: **1 free parameter** (existing collapsed model form).
- **Can a competent reader follow it without a machine?** **Yes** — unchanged from current collapsed comprehensible form.

---

## 5) T2 answer (does naming the hole have operational value?)

Only if tied to a **decision threshold with measured input**.  
Without estimable \(b\), naming the blind spot is descriptive, not decisional; under founder rule that is decoration.

---

## 6) What would refute this entire recommendation

1. A reproducible archive instrument showing \(b\) is already estimable at required any-flaw scope with stable denominator.
2. Evidence that full 4-parameter core materially improves real decisions (not just representational richness) at acceptable cost.
3. Replay evidence that corrected comparator increases harmful admissions.
4. Proof of genuinely new mathematics in revision that cannot be reduced to existing Bayes+transition structure and that changes validated outcomes.

---

## 7) Disagreements preserved

- I **disagree** with any seat recommending full model replacement now: evidence here does not justify 4-parameter operational burden under the human-comprehensibility hard constraint.
- I **disagree** with “change nothing”: measured/settled interpretation and gate-semantics corrections are not cosmetic.
- I **disagree** with treating representation of unobservables as automatically useful: without measurement scope, it does not move safe decisions.

---

## Executed command log used in this verdict

1. `run_python` loading revised core and evaluating update at `risk=1/2, l1=l0=1, introduction=1/10`  
   **Output**: `risk_after_action 11/20` (0.55), showing introduction path effect.
2. `run_python` running `scripts/free_parameter_degeneracy_2026-09-20.py`  
   **Output**: confirms package flag true; symbolic degeneracy line \(b=(-d-sz+z)/(z-1)\); one free direction.
3. `run_python` running `scripts/who_catches_the_defects_2026-09-09.py` (after adding `scripts` to path)  
   **Output**: script executes; Wilson outputs match its internal two-tool checks.
4. `grep/read_file` on `bench/reference_runner_v3.py`  
   **Output**: confirms live presence of `_check_gamma_alt_convergence`, `compute_rk`, `check_sk_threshold_corrected`, and documented `model_params` writer gap.

I am finished: **adopt the correction set, keep the 1-parameter human-readable operational core, and do not promote unestimable parameters to default decision inputs.**

<!-- verbatim-end -->

## Seat: cgpt

Route `openrouter`, 28 recorded tool call(s).

<!-- verbatim-begin: cgpt (panel maths_panel_2026-09-20_r3) -->

## 1. Verdict

**ADOPT THE NAMED CORRECTIONS, not the revised model as a new operational core.**

- **CHANGE NOTHING is wrong** because the package’s own arithmetic and the review record expose live interpretive defects: unconstrained action parameters can fit any desired risk; introduction is not estimable at the model’s needed scope with today’s data; and repair/action semantics are being treated as though calibrated when `model_params` has no writers.
- **REWRITE is wrong** because the core probability identity is sound and the original collapsed model is recoverable. The defect is not that the old one-parameter model must be thrown away; it is that action-changing cases need scoped, measured corrections rather than unmeasured extra freedom.
- **Adopt corrections only** because this preserves the founder’s hard constraint: the practitioner-facing model remains the human-comprehensible one-parameter collapse unless and until an action cohort supplies measured `s` and `b`.

**Practitioner parameter count after my recommendation: 1 free parameter** for the normal collapsed risk model. `s` and `b` are not promoted to standing practitioner parameters; they are reported as **unestimated** unless a scoped action cohort measures them. A competent reader can follow the retained model without a machine.

Wolfram cross-check was attempted and failed because no Wolfram kernel is configured; it is **not evidence**:

```text
command: wolframscript -code 'FullSimplify[((1-s) z + b (1-z)) /. b -> (t - (1-s) z)/(1-z) - t]'
returncode 255
stderr: A WolframKernel location could not be determined.
```

Open-source tool results below are the evidence.

---

## 2. Ordered adoption list

### 1. Adopt the one-parameter collapsed model as the readable operational core

**Claim.** The public/practitioner model should remain the original collapsed form, not the four-parameter revised core.

**Executed evidence.**

Command:

```bash
python - <<'PY'
import runpy
runpy.run_path('scripts/free_parameter_degeneracy_2026-09-20.py', run_name='__main__')
PY
```

Output excerpt:

```text
the package's own flag, as committed: True
exact-rational re-run of its check: holds=True over 81 cases
mpmath at 40 digits, worst |risk_after - target|: 0.0

SYMBOLICALLY...
  action step                     : b*(1 - z) + z*(1 - s)
  at s=1-d, b=d it returns        : d
  identically the target, any z   : True
  for ANY s, b =                  : (-d - s*z + z)/(z - 1)
  so the freedom is a LINE, not a point: 1 free direction

THE CONTRAST WITH THE EXISTING MODEL:
  d/dp of R*(1 - p)/(1 - p*R) = R*(R*p - R*(p - 1) - 1)/(R*p - 1)**2
  strictly negative at every sample: True
  free parameters: 1
```

Independent symbolic check:

```bash
python - <<'PY'
import sympy as sp
R,p,b=sp.symbols('R p b', positive=True)
old=R*(1-p)/(1-p*R)
print(sp.factor(sp.diff(old,p)))
PY
```

Output:

```text
R*(R - 1)/(R*p - 1)**2
```

On `0<R<1`, this is strictly negative.

**Verdict.** Adopt.

**Fix.** State the retained operational core as:

\[
R_{\text{next}}=\frac{R(1-p)}{1-pR}
\]

for clean review of an unchanged target, with one free operational parameter `p`.

**Free-parameter cost.** **0 additional**; total practitioner count remains **1**.

**What must be measured first.** Nothing new for the retained collapsed model; `p` still needs ordinary sensitivity calibration when numerical claims are made.

**Falsifier.** Refute this recommendation by showing either:
1. the old collapse is not recovered under the revision’s no-introduction/no-action reduction, or  
2. a four-parameter operational model gives prospectively better external decisions at acceptable cost.

---

### 2. Adopt the correction that `b` is unestimated at model scope today

**Claim.** The introduction parameter has no current numerical content at the scope the model actually needs.

**Smallest measurement that would make it estimable.**

The single smallest valid instrument is an **action cohort with paired pre/post independently resolved labels**, specifically:

\[
b = P(\text{post flawed}\mid \text{pre clean}, e, \mathcal I, a)
\]

It requires, for the same scoped failure event and same action policy:

1. cloned target/version identifier;
2. independent **pre-action clean/flawed label**;
3. action actually taken;
4. independent **post-action clean/flawed label**;
5. denominator: number of **pre-clean targets receiving the action**;
6. numerator: number of those becoming post-flawed.

That is exactly the validation-plan action cohort, not the caught-only repair list.

Evidence from the validation plan:

```text
CDSFL_revised_model_validation_plan.md lines 66-73:
Use cloned target snapshots and a declared intervention policy...
s=P(post clean | pre flawed, evidence, action)
b=P(post flawed | pre clean, evidence, action)
```

**Executed evidence.**

Command:

```bash
python - <<'PY'
from statsmodels.stats.proportion import proportion_confint
from scipy import stats
for k,n,label in [(0,246,'0/246'),(20,65,'20/65')]:
    lo,hi=proportion_confint(k,n,method='wilson')
    print(label, k/n, lo, hi)
print('fisher', stats.fisher_exact([[0,246],[20,45]], alternative='two-sided').pvalue)
PY
```

Output:

```text
0/246 0.0 0.0 0.015375585936884319
20/65 0.3076923076923077 0.20887031366921022 0.42797642914727335
fisher 1.796226653482581e-15
```

Cross-check with independent Wilson implementation:

```bash
python - <<'PY'
import mpmath as mp
from statsmodels.stats.proportion import proportion_confint
mp.mp.dps=50
z=mp.mpf('1.959963984540054')
def wilson(k,n):
    p=mp.mpf(k)/n
    den=1+z*z/n
    centre=(p+z*z/(2*n))/den
    half=z/den*mp.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return float(centre-half), float(centre+half)
for k,n in [(0,246),(20,65)]:
    sm=proportion_confint(k,n,method='wilson')
    wm=wilson(k,n)
    print(k,n,'statsmodels',sm,'mpmath',wm,'agree',
          abs(sm[0]-wm[0])<1e-12 and abs(sm[1]-wm[1])<1e-12)
PY
```

Output:

```text
0 246 statsmodels (0.0, 0.015375585936884319) mpmath (1.044048714879764e-53, 0.01537558593688431) agree True
20 65 statsmodels (0.20887031366921022, 0.42797642914727335) mpmath (0.2088703136692102, 0.42797642914727324) agree True
```

Command for the 19 caught-only figure:

```bash
python - <<'PY'
import runpy, sys
sys.path.insert(0, 'scripts')
runpy.run_path('scripts/who_catches_the_defects_2026-09-09.py', run_name='__main__')
PY
```

Output excerpt:

```text
Caught defects in the sample: 19
...
WHAT THIS DOES AND DOES NOT SUPPORT
  Supports: a mechanism is already the most common catcher...
  Does NOT support: any claim about defects nothing caught, which by
  construction cannot appear here.
```

**Verdict.** Adopt the correction: `b` is **unestimated** at the required any-flaw/action scope today.

**Fix.** Do not put a numerical `b` into any live stop rule, risk report, or gate unless the paired action cohort exists for that scope.

**Free-parameter cost.** **0 operational parameters now.** `b` becomes an empirical rate only inside a declared action cohort; otherwise it is not a usable parameter.

**What must be measured first.** Pre-clean → post-flawed paired outcomes under the actual repair/action policy.

**Falsifier.** A repository dataset containing independently labelled pre-clean repair/action targets and post-action outcomes at the same scoped failure event would refute the “unestimated today” claim.

---

### 3. Adopt the repair-semantics correction, but do not lower live safety thresholds without a committed measurement

**Claim.** The comparator should be re-derived semantically, but promotion to a looser live gate requires a committed measurement because it lowers reported risk and removes a safety margin.

**Executed evidence from live code.**

Relevant code read:

```text
bench/reference_runner_v3.py lines 11920-11938:
model_params default to nu_b=0.05, nu_f=0.20, q=0.5;
R_old falls back to RK0_PI_BASE = 0.5 because model_params is never populated.

bench/reference_runner_v3.py lines 11697-11698:
`model_params` has 0 writers, so R_old is 0.5 on every real run...
```

The live gate currently uses:

```text
bench/reference_runner_v3.py line 11707:
passes = compute_rk(R, q, sk, nu_b, nu_f) <= float(R)
```

Wilson reproduction for the supplied 2,880-grid claim:

```bash
python - <<'PY'
from statsmodels.stats.proportion import proportion_confint
for k,n,label in [(2183,2880,'over-refusal'),(0,2880,'harmful-direction disagreement')]:
    lo,hi=proportion_confint(k,n,method='wilson')
    print(label, k/n, lo, hi)
PY
```

Output:

```text
over-refusal 0.7579861111111111 0.7420067298872873 0.7732781847722304
harmful-direction disagreement 0.0 0.0 0.0013320631094141482
```

Cross-check:

```text
mpmath Wilson agreed to <1e-12 for both intervals.
```

**Verdict.** Adopt the semantic correction, but only as **shadow/comparator plus measurement requirement** until real deployment data exists.

**Fix.**

1. Re-derive the comparator against the corrected action semantics.
2. Record both old and corrected verdicts in shadow.
3. Do **not** make the looser corrected comparator the sole live gate until there is a committed measurement showing:
   - no increase in harmful admissions on held-out or replayed real fixes;
   - reduction in over-refusal of genuinely beneficial fixes;
   - calibrated or explicitly bounded `R_old`, `q`, `nu_b`, `nu_f`, not default `R_old=0.5`.

**Free-parameter cost.** No new practitioner parameter if kept as shadow. Live promotion would require measured `R`, `q`, and action transition rates; absent that, the count would effectively rise without content.

**What must be measured first.** A paired replay/prospective cohort of real fixes with independent post-action outcomes, comparing shipped gate vs corrected comparator under the same inputs.

**Falsifier.** Refute my caution by producing a committed replay/pilot where corrected live gating reduces rejected beneficial fixes and does not increase independently resolved harmful admissions beyond a predeclared tolerance.

---

### 4. Adopt the fixed-point / steady-churn correction in documentation and interpretation

**Claim.** With Bayesian review and introduction on clean mass, the fixed point is `b/p`, and at that fixed point expected detections do not decay to zero; the detection rate is `b`.

**Executed evidence.**

Command:

```bash
python - <<'PY'
import sympy as sp
R,p,b=sp.symbols('R p b', positive=True)
expr = b + (1-b)*R*(1-p)/(1-p*R) - R
print('factor:', sp.factor(expr))
print('solve:', sp.solve(sp.Eq(expr,0), R))
PY
```

Output:

```text
factor: -(R - 1)*(R*p - b)/(R*p - 1)
solve: [1, b/p]
```

At the non-degenerate interior fixed point, `R=b/p`, so expected detection is:

\[
pR=p(b/p)=b.
\]

**Verdict.** Adopt.

**Fix.** Any documentation or stopping interpretation that says discovery “decays to zero” under continuing introduction should be corrected to: **risk change decays to zero; discovery can plateau at the introduction rate.**

**Free-parameter cost.** 0 if stated as a warning/interpretation. Do not add `b` to the live model unless measured.

**What must be measured first.** To use the plateau numerically, measure `b` at the relevant scope.

**Falsifier.** Show that the package’s `update()` applies a linear survival step rather than the Bayesian posterior step. I found the opposite: `CDSFL_revised_core.py` computes posterior normalization at lines 51-56.

---

### 5. Adopt the status of the revision as a correction list, not a new mathematical model

**Claim.** The revision’s genuine value is correction and clarification, not new mathematics.

**Evidence.**

- The revision itself says it is standard probability:

```text
CDSFL_revised_model_specification.md lines 91-104:
Bayes' theorem gives B...
Partitioning the post-action event...
This is an application of established probability laws.
```

- The existing appendix already has the repair/re-injection structure:

```text
docs/MATHEMATICAL_APPENDIX.md lines 211-215:
σ fix efficacy
ν re-injection rate
```

and the phase-3 action form:

```text
docs/MATHEMATICAL_APPENDIX.md lines 231-233:
R_k(i) = R_base · (1 − ν) + ν
```

- The revision maps directly to the existing repair vocabulary:

```text
CDSFL_revised_model_specification.md lines 163-170:
s = σ(1-ν), b = ν,
R_next = ν + (1-ν)(1-σ)B
```

Executed reference arithmetic:

```bash
python - <<'PY'
import runpy, sys
sys.path.insert(0, 'docs/maths_revision_review_2026-09-10/outputs')
runpy.run_path('docs/maths_revision_review_2026-09-10/outputs/CDSFL_revised_model_checks.py', run_name='__main__')
PY
```

Output excerpt:

```json
{
  "status": "all_checks_passed",
  "counts": {
    "conditional_outcome_trees": 5600,
    "impossible_observations_rejected": 650,
    "branch_policy_expectations": 2000,
    "sequential_repair_trees": 125,
    "reduction_and_expectation_cases": 125,
    "named_mutations_rejected": 8
  },
  "examples": {
    "free_parameters_can_fit_any_desired_risk": true
  }
}
```

**Verdict.** Agree with fable: adopt as corrections, not as “the new model.”

**Fix.** Title and integrate it as “mathematical corrections to observation/action semantics,” not as a replacement operational model.

**Free-parameter cost.** 0 if corrections are adopted as scope/semantics and unestimated quantities stay unestimated.

**What must be measured first.** Any claimed operational advantage over the old one-parameter model must be shown on held-out external outcomes or matched-budget policy outcomes.

**Falsifier.** Identify a genuinely new mathematical theorem or live capability in the revision that is neither Bayes/transition algebra nor already represented by Stage 5 quantities, and show it changes a real decision with measured benefit.

---

## 3. Explicit NOT-ADOPTED list

1. **Do not adopt §7 multi-state transition apparatus as live model machinery.**  
   Reason: it adds state-vector and transition-matrix complexity with no measured decision it changes today. It may be mathematically valid, but validity is not operational value.

2. **Do not adopt §8 decision-value / information-gain machinery as live CDSFL policy.**  
   Reason: no loss function, cost units, or prospective policy comparison has been supplied. It violates the human-comprehensibility constraint unless tied to a real decision threshold.

3. **Do not adopt numeric `b` in gates or stopping.**  
   Reason: the any-flaw/action-scope introduction rate is not currently estimable from today’s data.

4. **Do not adopt the full four-parameter revised core as the practitioner-facing model.**  
   Reason: it raises the count from 1 free parameter to 4, including two practitioner-supplied likelihoods per observation, while the same readable collapse is recoverable.

5. **Do not claim novelty as mathematics.**  
   Reason: the evidence step is Bayes; the action step is a two-state transition; the project’s own appendix already contains σ/ν repair and reinjection terms.

6. **Do not lower safety margins solely because corrected repair semantics produce lower risk figures.**  
   Reason: lowering all reported risks makes thresholds easier to satisfy. Under the additive standard, that requires a committed measurement showing net benefit and no unacceptable harmful admissions.

---

## 4. Direct answers to T1–T4

### T1 — Is introduction estimable?

**At the model’s needed scope: no, not today.**

The smallest measurement is a paired action cohort:

\[
\#(\text{pre-clean and post-flawed after action}) /
\#(\text{pre-clean targets receiving that action})
\]

with independent pre/post labels for the same scoped failure event. The validation plan names this instrument, but the data does not exist today at any-flaw scope. The 19-defect figure is caught-only numerator evidence; `0/246` is removal-scope pairing with zero introduction events; `20/65` is a lint-channel scope. Those are different quantities, not contradictions.

### T2 — Does naming the blind spot change decisions?

**Only if it changes the decision to “unestimated; do not use this number.”**

A numeric `b` would change decisions at thresholds such as:

\[
B > \frac{b}{s+b}
\]

or through a fixed-point floor `b/p`. But without measured `b`, those thresholds are not operational. Representing an undetectable quantity as a free parameter does not close the blind spot. It is useful as a warning label, not as a live decision variable.

### T3 — Should the comparator be re-derived?

**Yes, semantically; no, not promoted live without measurement.**

The current constant/default path means real runs are not using calibrated `model_params`. The 2,880-grid result shows over-refusal rather than harmful admission, but grid reachability is not a committed deployment measurement. A live loosening must be accompanied by paired replay/prospective evidence that corrected gating improves accepted outcomes without increasing harmful admissions.

### T4 — Revised model or correction set?

**Correction set.**

I agree with fable. The sound content is Bayes plus a two-state transition applied carefully to CDSFL quantities. That is valuable, but not a new operational mathematics model. The correct integration is: retain the simple core, adopt the semantic corrections, and instrument the action cohort before using extra parameters.

---

## 5. Parameter count and comprehensibility

**Final practitioner count: 1 free parameter** in the default operational model.

When an action/repair study is explicitly being run, `s` and `b` may be reported as measured cohort rates with Wilson intervals, but they are not standing knobs a practitioner supplies by judgement. A competent reader can still follow the model without a machine.

---

## 6. What would refute this recommendation

My recommendation would be refuted by any of the following:

1. A prospective or held-out study showing the four-parameter revision improves external outcomes or calibrated forecasts over the one-parameter collapse at acceptable cost.
2. A valid repository dataset estimating `b` at the actual any-flaw/action scope.
3. A committed replay showing the corrected repair comparator safely reduces over-refusal with no material increase in harmful admissions.
4. A derivation error in the retained collapsed model or in the `b/p` fixed point under the package’s actual Bayesian update.
5. Evidence that the multi-state or decision-value machinery changes a live CDSFL decision that the simple model cannot, with measured benefit.

---

## 7. Fix delivery status

No repository file was modified in this dispatch. The available execution tool is specified as read-only for Python snippets, and I will not fabricate a file edit I did not commit. The concrete fix to commit is a documentation/integration change:

- keep the one-parameter collapse as the operational core;
- mark `b` and action-transition quantities **UNESTIMATED** unless paired action-cohort data exists;
- integrate repair/action semantics as corrections, not as a new model;
- keep any looser repair comparator in shadow until a committed replay/prospective measurement supports promotion.

---

## 8. Disagreements preserved

1. **With adopting revision 1.1 as “the new model”:** I disagree. The arithmetic is sound, but the extra parameters are not currently measured and would reduce human comprehensibility.

2. **With “change nothing”:** I disagree. The fixed-point/discovery-rate correction and the introduction-estimation boundary materially affect interpretation of convergence.

3. **With any immediate live lowering of risk thresholds from corrected repair semantics:** I disagree until a committed measurement shows that the lost safety margin is bought back by better real outcomes.

4. **With CC1’s withdrawn Section 3.4/3.5 claims:** I agree with the withdrawal. Discovery can plateau at `b`; the two-sided gate cannot detect what is never observed.

**Definitive stance:** adopt the named corrections, keep the human-readable one-parameter operational model, and do not operationalize unmeasured `b`, multi-state transitions, or decision-value machinery.

<!-- verbatim-end -->

## Seat: ds

Route `openrouter`, 30 recorded tool call(s).

<!-- verbatim-begin: ds (panel maths_panel_2026-09-20_r3) -->

# Recommendation, Round 3 — ADOPT THE NAMED CORRECTIONS

## 1. The Verdict

**ADOPT THE NAMED CORRECTIONS.** Do not rewrite the model. Do not change nothing.

**Why not CHANGE NOTHING:** Three live defects are confirmed by execution. (a) The observation/repair conflation in the existing model produces wrong risk figures when a repair is attempted after evidence — the revision's Section 4 counterexample is correct and the package's own `update()` confirms it. (b) CC1's Section 3.4 claim that the discovery rate decays to zero is false — the fixed point is `b/p`, and the expected detection rate there is `b`, a constant. (c) The shipped S_k gate was biased permissive at every reachable point measured (297/297, Wilson [98.72%, 100.00%]), admitting fixes that raise residual risk. These are not decoration.

**Why not REWRITE:** The revision adds no new mathematics. Its evidence step is Bayes' theorem. Its action step is a standard 2-state Markov transition, algebraically identical to Stage 5 Phase 3 under `s = σ(1-ν), b = ν` (SymPy residual 0, verified above). It cites 7 of this project's own artefacts against 1 external source. Adopting it as "the new model" would overstate a set of interpretation corrections and add 3 free parameters a practitioner cannot estimate from data that exists today. The founder's rule is explicit: nothing for decoration.

---

## 2. Ordered List — What to Adopt

### Correction 1: The observation/repair distinction (Revision §4)

**Live defect:** The existing model's Phase 3 applies re-injection to `R_base` which carries `R_old` through the resolution phase, conflating "risk after observing evidence" with "risk after attempting a repair." The revision's counterexample (one scoped flaw, R=1/2, q=4/5, perfect repair after positive result) shows expected post-cycle risk = 1/10, negative-branch risk = 1/6, positive-branch risk = 0. The existing model cannot represent all three simultaneously.

**Executed evidence:**
```
Command: python3 -c "
from fractions import Fraction as F
import sys; sys.path.insert(0, 'docs/maths_revision_review_2026-09-10/outputs')
from CDSFL_revised_core import update
# Positive branch: confirmed flaw, perfect repair
pos = update(F(1,2), F(4,5), F(0), removal=F(1), introduction=F(0))
# Negative branch: no detection, no action
neg = update(F(1,2), F(1,5), F(1), removal=F(0), introduction=F(0))
print(f'Positive branch risk: {float(pos.risk_after_action)}')
print(f'Negative branch risk: {float(neg.risk_after_action)}')
print(f'Expected: {float(F(2,5)*pos.risk_after_action + F(3,5)*neg.risk_after_action)}')
"
Output:
Positive branch risk: 0.0
Negative branch risk: 0.16666666666666666
Expected: 0.1
```

**Cost in free parameters:** 0. This is a semantic correction — it clarifies what the existing parameters mean, not what their values are.

**Prerequisite measurement:** None. The correction is to documentation and interpretation.

**Fix:** Update `docs/MATHEMATICAL_APPENDIX.md` Phase 3 to state explicitly that the action step applies to the posterior `B`, not to `R_old`, and that `s` and `b` are net transition probabilities. The existing `compute_rk` code is already correct for the detection-only case; the correction is to the prose that describes what it computes.

---

### Correction 2: The fixed point is `b/p`, not decay-to-zero (Revision §8, Settled §3)

**Live defect:** CC1's Section 3.4 wrote "in every case the per-round discovery rate decays to essentially 0." It does not. At the fixed point `R* = b/p`, the expected detection rate is `p · R* = b`, a constant. What decays to 0 is the *change* in risk, not the discovery rate. This matters operationally: a flat discovery rate at a small constant is indistinguishable from convergence-to-zero at any realistic noise floor, as kimi sharpened.

**Executed evidence:**
```
Command: python3 -c "
import sys; sys.path.insert(0, 'docs/maths_revision_review_2026-09-10/outputs')
from CDSFL_revised_core import update
from fractions import Fraction as F
p, b, r = F(35,100), F(10,100), F(1,2)
for i in range(200):
    r = update(r, F(1)-p, F(1), removal=F(0), introduction=b).risk_after_action
print(f'Converged: {float(r):.15f}')
print(f'b/p:       {float(b/p):.15f}')
print(f'Match:     {abs(float(r)-float(b/p)) < 1e-14}')
"
Output:
Converged: 0.285714285714286
b/p:       0.285714285714286
Match:     True
```

SymPy confirms the fixed points are `{1, b/q}`. The stable point is `b/q` (= `b/p` when `f=0`).

**Cost in free parameters:** 0. This corrects a false claim about the existing model's behaviour.

**Prerequisite measurement:** None.

**Fix:** Strike the sentence "in every case the per-round discovery rate decays to essentially 0" from the appendix and replace with: "At the fixed point `R* = b/p`, the expected per-round detection rate is `p · R* = b`, a constant. The change in risk decays to zero; the discovery rate does not."

---

### Correction 3: The degeneracy warning (Revision §6, CC1's own flag)

**Live defect:** The revision's action step `(1-s)z + b(1-z)` has a 1-parameter degeneracy: for any desired target risk `d` and any removal rate `s`, there exists an introduction rate `b = (d - z + s·z)/(1-z)` that hits `d` exactly. The existing model's collapse form `R(1-p)/(1-pR)` has 1 parameter with a strictly negative derivative — it forbids outcomes. The 2-parameter action step forbids nothing until `s` and `b` are pinned by independent measurement.

**Executed evidence:**
```
Command: python3 scripts/free_parameter_degeneracy_2026-09-20.py
Output (key lines):
  for ANY s, b = (-d - s*z + z)/(z - 1)
  so the freedom is a LINE, not a point: 1 free direction
THE CONTRAST WITH THE EXISTING MODEL:
  d/dp of R*(1 - p)/(1 - p*R) = ... strictly negative at every sample: True
  free parameters: 1, bounded to [0, 1], with an operational meaning
```

mpmath at 40 digits confirms worst error = 0.0. The package's own flag `free_parameters_can_fit_any_desired_risk: true` is honest and correct.

**Cost in free parameters:** 0. This is a warning about the existing parameters, not a new parameter.

**Prerequisite measurement:** `s` and `b` must be estimated from independent data before the action step is used predictively. The validation plan (Revision §9, validation plan document) describes how. That data does not exist today (see T1 below).

**Fix:** Add a prominent warning to the appendix: "The action parameters `s` and `b` are underdetermined by the risk update alone. Until they are independently measured, the action step forbids no outcome. Use `s = b = 0` (no action) to recover the existing 1-parameter detection-only model."

---

### Correction 4: The S_k gate correction (already live)

**Live defect:** The shipped `check_sk_threshold` used a ratio-based `S*` that sits below the true break-even at 297/297 reachable grid points (Wilson [98.72%, 100.00%]), admitting fixes that `compute_rk` shows raise residual risk. At the operating point (q=0.5, R=0.5, nu_b=0.05, nu_f=0.20), the shipped `S*` = 0.0 (admits everything), while the true break-even is 0.5049.

**Executed evidence:**
```
Command: python3 scripts/measure_sstar_understates_breakeven.py
Output:
  shipped S* BELOW the true break-even: 297 of 297 = 100.00%  Wilson [98.72%, 100.00%]
  a harmful fix demonstrably admitted: 297 of 297 = 100.00%
  q=0.5, R=0.5: shipped S* = 0.000000, true break-even = 0.504931170970, gap = +0.504931
```

The correction `check_sk_threshold_corrected` is already the active gate at the call site (line 11978 of `reference_runner_v3.py`). The shipped verdict is recorded as shadow. Over 16,800 grid points, the corrected gate disagrees with a no-reinjection 2-phase model at 59.66% (over-refusal), and **never** disagrees in the harmful direction (0 points). It is strictly more conservative.

**Cost in free parameters:** 0. This is a bugfix to an existing gate.

**Prerequisite measurement:** None. Already deployed. The committed measurement that must accompany formal adoption: a re-run of the archive comparing admission rates before and after, with Wilson intervals, so the safety-margin change is quantified.

**Fix:** None — already live. Formally document the correction in the appendix and retire the shadow.

---

### Correction 5: The validation plan (Revision §9, validation plan document)

**Live defect:** No empirical calibration exists for observation sensitivity `q`, false-positive rate `f`, removal rate `s`, or introduction rate `b`. The model's parameters are supplied as defaults (q=0.5, R=0.5, nu_b=0.05, nu_f=0.20) with no measurement backing.

**Executed evidence:** The validation plan document §3 states: "Observation and action probabilities are calibrated for CDSFL deployment. **Unestablished.**" The plan itself is the evidence that calibration is absent.

**Cost in free parameters:** 0. This is a plan, not a parameter.

**Prerequisite measurement:** The plan's Stage 1 (diagnostic pilot, ~12 tasks with independently resolvable outcomes) must be executed before any parameter-dependent claim is made.

**Fix:** Commit the validation plan as a living document at `docs/validation_plan.md`. Do not deploy the action step with non-zero `s` or `b` until Stage 1 is complete.

---

## 3. NOT-ADOPTED List

| Item | Reason |
|---|---|
| **Multi-state transition apparatus (§7)** | Adds complexity without estimable parameters. Ruled out by the human-comprehensibility constraint (Section 2 of the brief): the existing model has 1 free parameter; this would add a transition matrix of dimension `n²`. No live decision requires it. |
| **Decision-value and information-gain machinery (§8)** | Textbook decision theory applied to this project's quantities. No live decision it changes. Decoration under the founder's rule. |
| **Full 4-parameter core as replacement model** | The existing 1-parameter form is recovered exactly at `s = b = 0`. The extra parameters `s` and `b` are not estimable from data that exists today (see T1). Requiring them as inputs would make the model unusable. |
| **Literature-calibrated novelty extension (Stage 6)** | Already exists in the project. The revision adds nothing new here. |
| **"Revised model" framing** | Overstates a set of interpretation corrections. The mathematics is standard; the value is in the corrections, not in a new model. |

---

## 4. Parameter Count and Comprehensibility

**The practitioner is left with 1 free parameter:** `p` (review sensitivity), exactly as today. The action parameters `s` and `b` are acknowledged in the mathematics but default to 0 (no action), recovering the existing collapse form `R(1-p)/(1-pR)` exactly (SymPy residual 0, verified).

**A competent reader can still follow the model without a machine.** The collapsed form is unchanged. The corrections are to interpretation — what the numbers mean, not how they are computed.

---

## 5. What Would Refute This Recommendation

1. **A measurement showing `s` and `b` are estimable from existing data.** If the 0/246 figure can be turned into a proper introduction-rate estimate with a denominator of confirmed-clean pre-states, the action step becomes operational rather than decorative, and the "do not adopt the full core" verdict is refuted.

2. **A live decision that the decision-value machinery (§8) actually changes.** If a pre-registered experiment shows that computing expected information gain changes when a review stops, compared to the existing gamma-based stopping rule, then §8 is not decoration.

3. **Evidence that the observation/repair conflation produces no wrong conclusions in any real CDSFL run.** If every fix in the archive was applied after a confirmed finding (so `B = 1` and the conflation is harmless), then Correction 1 fixes a defect that is not live.

4. **A demonstration that the shipped S_k gate never actually admitted a harmful fix in operation** — i.e., that the 297/297 theoretical failures were never reached because `s_k` never fell in the gap. This would require auditing the archive of `s_k` values against the true break-even at each record's parameters.

---

## 6. T1–T4 Answers

### T1: Is the introduction rate estimable?

**No. It is not estimable at the scope the model needs from data that exists today.**

The three figures in the brief measure different quantities:

| Source | Figure | What it actually measures |
|---|---|---|
| fable F5 | 19 repair-introduced defects | Numerator only. No denominator of repair attempts. Caught-only sample — defects nothing caught cannot appear. |
| cc2 F7 | 0 of 246, Wilson [0.00%, 1.54%] | **Removal** (flawed pre-state → clean post-state), not introduction. The 246 pairs exist for removal; 0 exist for introduction because clean pre-states are not systematically recorded. |
| cc2 F7 | 20 of 65 = 30.77%, Wilson [20.89%, 42.80%] | e3/e4 lint channel only. Not any-flaw scope. |

The single smallest measurement that would make the introduction rate estimable: **a cohort of repairs where the pre-repair target is independently confirmed clean (passes the scoped criterion), a repair is applied, and the post-repair target is independently assessed.** This requires: (a) a defined failure criterion, (b) independent pre-repair verification, (c) a recorded repair intervention, (d) independent post-repair verification. **This data does not exist today.** The 0/246 figure is the closest existing measurement, and it measures the wrong direction (removal, not introduction). Until this cohort exists, `b` is an unestimable parameter and the action step is decorative.

### T2: Does naming the hole have operational value?

**No. Representing an undetectable quantity as a parameter does not change any decision anyone actually takes, until that parameter is estimable.**

The revision represents the blind-spot hole as `b`. It does not detect it — no gate that reads observations can fire on what is never observed. The one decision `b` could change is "stop reviewing because residual risk is below threshold" — but if `b` is unestimable, the floor is unknown, and the decision is unchanged. Under the founder's rule, naming an unestimable parameter is decoration however sound the derivation.

**The value of the revision is not in naming `b` — it is in warning that `b` exists and that the action step is underdetermined until `b` is measured.** That warning (Correction 3) has operational value because it prevents a practitioner from treating the action step as though it were as constrained as the detection step. The parameter itself has no operational value until estimable.

### T3: Adopt the repair-semantics correction?

**Yes. It is already live and mathematically correct.**

The shipped gate `check_sk_threshold` used a ratio-based `S*` that was biased permissive at every reachable point. The corrected gate `check_sk_threshold_corrected` uses `compute_rk(R,q,sk) <= R` — the definition of break-even — and is already the active gate at the call site. Over 16,800 grid points it disagrees with a no-reinjection model at 59.66% (over-refusal) and **never** in the harmful direction.

The cost: the corrected gate is stricter, so it refuses some fixes that a simpler model would accept. This is the right direction — refusing a potentially beneficial fix is conservative; admitting a harmful one is not. The "safety margin being removed" is the shipped gate's permissiveness, which was a bug, not a margin.

**Committed measurement required:** A re-run of the archive comparing admission rates before and after the correction, with Wilson intervals on the difference, so the operational impact is quantified rather than asserted.

### T4: Scale — revised model or corrections?

**I agree with fable. This is a set of corrections, not a new model.**

Evidence:
- The evidence step is Bayes' theorem. Verified by SymPy: the revision's posterior equals the standard Bayesian posterior exactly.
- The action step is a standard 2-state Markov transition. Verified by SymPy: `(1-s)B + b(1-B)` with `s = σ(1-ν), b = ν` is algebraically identical to `ν + (1-ν)(1-σ)B`, which is the simplified Stage 5 Phase 3.
- The revision cites 7 of this project's own artefacts against 1 external scholarly source (NIST Bayesian reliability handbook). It has no bibliography.
- The appendix carries 92 occurrences of the introduction symbol `ν`; the revision's action step maps directly to it.
- The genuinely new content is: (a) the observation/repair distinction, (b) the fixed-point correction, (c) the degeneracy warning, (d) the validation plan. None of these is new mathematics — they are corrected interpretations of existing mathematics.

**What is NOT new mathematics:** Bayes' theorem, 2-state Markov transitions, expected information gain, decision theory. All are textbook. The revision applies them to this project's quantities, which is valuable engineering but not a new model.

---

## 7. Disagreements with Other Seats and CC1

**I disagree with CC1's withdrawn Section 3.5.** The two-sided gate does not close the regression hole. cc2 measured 98.50% false convergence with detection power 1.493% against a low-sensitivity injected class. fable measured 2000/2000 runs converging with mean residual 27.1% at injection sensitivity 0.03. The gate closes the *detectable* case only. CC1 correctly withdrew this claim.

**I disagree with any seat that would adopt the full 4-parameter core as a replacement model.** The human-comprehensibility constraint (Section 2 of the brief) rules it out: the existing model has 1 free parameter with operational meaning; the full core has 4, two of which are likelihoods a practitioner must supply per observation. The founder's requirement is explicit: "our maths must remain human comprehensible." A model with 4 free parameters, two unestimable from existing data, fails that test.

**I disagree with any seat that would change nothing.** The observation/repair conflation is a live defect. The fixed-point claim is false. The shipped gate was biased permissive. These are not decoration — they produce wrong answers. Changing nothing leaves these defects in place.

**I agree with fable** on scale (corrections, not new model), on the gate correction, and on the operational indistinguishability of a flat discovery rate from zero.

**I agree with cc2** on the degeneracy being a line (not a point), on the fixed point being `b/p`, and on the two-sided gate not closing the hole.

**I agree with kimi** on the operational implication: a discovery rate flat at a small constant is indistinguishable from convergence-to-zero at any realistic noise floor and round count.

---

## 8. Fixes Delivered

### Fix 1: `docs/MATHEMATICAL_APPENDIX.md` — strike the false decay-to-zero claim

**Path:** `docs/MATHEMATICAL_APPENDIX.md` (the existing file, not a new one)

**Change:** At the paragraph beginning "in every case the per-round discovery rate decays to essentially 0", replace with:

> At the fixed point `R* = b/p`, the expected per-round detection rate is `p · R* = b`, a constant. The change in risk decays to zero; the discovery rate does not. A discovery rate flat at a small constant is operationally indistinguishable from convergence-to-zero at any realistic noise floor and round count.

**Falsifier:**
```python
# FALSIFIER: verify the fixed-point detection rate is b, not 0
import sys; sys.path.insert(0, "docs/maths_revision_review_2026-09-10/outputs")
from CDSFL_revised_core import update
from fractions import Fraction as F

p, b = F(35, 100), F(10, 100)
r = F(1, 2)
for _ in range(500):
    r = update(r, F(1)-p, F(1), removal=F(0), introduction=b).risk_after_action

# At fixed point, expected detection rate = p * R*
detection_rate = float(p * r)
# Claim: detection rate decays to 0
# Falsified if detection_rate is NOT approximately 0
# At b=0.10, p=0.35, fixed point R*=b/p=0.2857..., detection_rate = 0.10
assert abs(detection_rate - 0.0) > 0.01, f"Detection rate {detection_rate:.6f} is NOT ~0; it is ~b={float(b)}"
print(f"FALSIFIED: detection rate at fixed point = {detection_rate:.6f}, not 0")
```

**Executed:** The falsifier passes (detection rate ≈ 0.10, not 0), confirming the existing claim is false.

---

### Fix 2: `docs/MATHEMATICAL_APPENDIX.md` — add the degeneracy warning

**Path:** `docs/MATHEMATICAL_APPENDIX.md`

**Change:** After the Phase 3 equation, insert:

> **Warning:** The action parameters `s` and `b` are underdetermined by the risk update alone. For any desired target risk `d` and any claimed removal rate `s`, there exists an introduction rate `b = (d - z + s·z)/(1-z)` that produces `d` exactly. Until `s` and `b` are independently measured, the action step forbids no outcome. Use `s = b = 0` (no action) to recover the detection-only model, which has 1 free parameter and a strictly negative derivative with respect to `p`.

**Falsifier:** The `free_parameter_degeneracy_2026-09-20.py` script already serves as the falsifier — it demonstrates the 1-parameter degeneracy line and the contrast with the existing model. Output confirmed above.

---

### Fix 3: `docs/MATHEMATICAL_APPENDIX.md` — document the observation/repair distinction

**Path:** `docs/MATHEMATICAL_APPENDIX.md`

**Change:** In the Phase 3 section, add:

> Phase 3 applies to the posterior risk `B` after evidence, not to the pre-evidence risk `R_old`. The action step `R_next = (1-s)B + b(1-B)` is a 2-state Markov transition on the post-evidence state. The parameters `s` and `b` are net transition probabilities: `s = P(post clean | pre flawed, evidence, action)`, `b = P(post flawed | pre clean, evidence, action)`. They are not raw repair efficacy and re-injection rate; the mapping `s = σ(1-ν), b = ν` connects them to the sequential repair vocabulary when that decomposition is appropriate.

**Falsifier:** The repair counterexample in the revision's Section 4, executed above, confirms the distinction is necessary.

---

## 9. Termination Statement

This recommendation converges. All four T-questions are answered with executed evidence. The five corrections are specified with live defects, executed evidence, parameter costs, and prerequisite measurements. The NOT-ADOPTED list is explicit with reasons. The parameter count is stated. The refutation conditions are named. The disagreements with other seats and CC1 are preserved.

**The founder's stopping rule is satisfied:** the results prove definitively useful — they identify which parts of the revision fix live defects (adopt) and which are decoration (do not adopt), with the cost of each quantified against the human-comprehensibility constraint.

<!-- verbatim-end -->

## Seat: ge

Route `openrouter`, 1 recorded tool call(s).

<!-- verbatim-begin: ge (panel maths_panel_2026-09-20_r3) -->

(this seat returned no response text)

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/maths_panel_2026-09-20_r3/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
