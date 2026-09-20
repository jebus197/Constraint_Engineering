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
