# PANEL BRIEF — VERIFY FOUR CHANGES, THEN TWO OPEN QUESTIONS

Bash, Read, Grep, Glob. Your working directory is a disposable copy carrying the
author's uncommitted work. **Execute. Do not read and agree.**

**Calibration you should apply to everything below.** Of 8 measurements this
author put to the 2026-09-03 panel, 3 could not be reproduced and 1 was wrong on
both halves. Of 8 put to the 2026-09-04 panel, 1 was false and it was the
load-bearing one. Assume the same rate here.

**Anti-overwhelm.** Part 1 is verification with a definite answer per item.
Part 2 is 2 open questions. Do not audit beyond what these need.

---

## PART 1 — CONFIRM OR REFUTE FOUR CHANGES, PROGRAMMATICALLY

For each: **run it**, then return CONFIRMED / REFUTED / REFUTED-WITH-FIX. You are
expected to declare a change SOUND where it is. This panel is not scored on
finding faults.

**C1 — the key collision.** `gamma_threshold_profile` wrote threshold keys with
`f"{thr:.1f}"`, collapsing 0.65 onto 0.7 and 0.75 onto 0.8, so
`boundary_band_sensitivity` returned `None`/`None`/`False` unconditionally.
Changed to `f"{thr:g}"` at 2 sites. New test
`test_boundary_band_executes_2026-09-04.py` calls the function on 2 constructed
registries. Claim: reverting the fix fails 4 of its 5 assertions while the old
source-text file still passes all 8. **Verify the fix is correct AND that the
test discriminates.** Is `:g` right, or does it introduce a float-repr hazard at
some threshold value this project could plausibly adopt?

**C2 — the occasions record.** `register()` seeds
`occasions=[{model, round, alias, via}]`; `resolve()` carries a duplicate's
occasions onto the merge target, deduplicated on `(model, round, alias)`.
`source_model` is untouched and has 12 live consumers. Claim: the change is
purely additive and cannot move a verdict. **Verify that claim specifically** --
grep every consumer, and satisfy yourself nothing reads `occasions` on a decision
path. Also: is dedup on `(model, round, alias)` the right key, or can 2 genuinely
distinct reports collide under it?

**C3 — the netguard markers.** 4 tests that prove the money guard denies a call
now carry `@pytest.mark.allow_outbound`. Claim: the calls are still DENIED and
only the teardown auto-fail is waived. **Verify the guard still denies.** If the
marker weakens enforcement in any path, say so -- this one protects money.

**C4 — grep converted to execution.** `test_the_shim_grants_a_shell` asserted
that `sim_dispatch_shim.py` CONTAINS `--allowedTools` and `Bash`. It now
intercepts `subprocess.run`, calls the shim, and asserts against the built argv.
Claim: removing `Bash` from the argv while leaving the word in the source (syntax
kept valid) passes a grep and fails the executing test. **Reproduce that.**

Suite claim to check: **4870 passed, 0 failed, 0 errors** under
`--netguard-strict`.

---

## PART 2 — TWO OPEN QUESTIONS

### Q1. Is the S_k admissibility gate redundant, or does it need tightening?

**The measurement.** The gate has NEVER rejected anything. Two independent
routes: `"passes_threshold": false` appears 0 times against `true` 3816 times;
the log line only the threshold branch emits appears 0 times against 400
error-path lines. Fire rate 0 of 3816, Wilson 95% CI [0.0000, 0.0010].

**The cause.** `check_sk_threshold` computes
`S* = (nu_b + nu_f - nu_b*nu_f - q*R) / (nu_f*(1-nu_b))`. That is
`nu_eff(s_k) <= nu*` with `nu*` evaluated at **sigma = 1**, while the appendix's
`nu* = sigma*R*q/(1 - q*R*(1-sigma))` is sigma-dependent and sigma IS s_k. At the
only reachable operating point (nu_b 0.05, nu_f 0.20, q 0.5, R 0.5 -- all literal
defaults, `model_params` has no writer) S* is the exact rational **-1/19**,
clamps to 0, and admits everything. True break-even **0.504931170970423**.

**The founder's question, which reframes it.** If fixes arrive at this gate
already confirmed or rejected by the machinery upstream, is the zero fire rate
evidence that the REST of the discrimination machinery is working better than
expected? In that case the question is not "repair the threshold" but **"is this
gate now redundant, and should it be removed?"** The alternative reading is that
it needs tightening to become accurate. Decide between those, or name a third
reading, **with evidence rather than preference**. Note that repairing it is
behavioural: it changes which fixes are accepted, which changes next-round
prompts, which invalidates replay of archived runs.

### Q2. The simplicity/sufficiency formalisation: what maths, what machinery, or neither?

**These are two independent axes and must not be collapsed into a choice.** They
operate at different levels: a gate is a process control over code artefacts; a
mathematical term acts on the model's state equations. Evaluate each on its own
merits and say whether composition is warranted. All 4 outcomes are live.

**The context you need.** The distinction is between *cost simplicity* (a small
artefact) and *compressive simplicity* (a short statement with wide reach, small
because it captured the structure). The proposed criterion: a simplification is
admissible iff the simpler form S and the fuller form F agree across a scope D
**declared before either was proposed** (residual empty), or the residual is
named, bounded and filed as its own claim. Established by proof or exhaustive
enumeration; a confidence interval applies only where D was sampled. Consequence:
**sampling can refute a simplification but can never admit one.**

**The mathematical foundation already verified.** Appendix section 1.1 already
contains sections titled "Reduction Property". Under K=1, d=1, all p_ik=p,
pi=0.5 the unified equation collapses to `R_n = (1-p)^n / (1 + (1-p)^n)`.
Verified: residual exactly 0 for n=1..8, **and the induction step is exactly 0**,
so it holds for all n by proof. mpmath at 30 dp agrees to 1e-32. The project's
own central equation passes the criterion. The appendix carries 28 such
statements; the 2026-09-03 panel found them true by construction, and 5 were spot
checked.

**Prior panel position, which you may disagree with.** Both reviewers on
2026-09-04 said: named definition in the appendix plus one acceptance-policy
sentence; nothing in the equation, because a reduction property is a theorem
ABOUT the equation, not a term IN it, and folding it in would make the equation
piecewise, which is the opposite of collapse. Both also proposed an execution
gate as the operational machinery.

**What the founder is asking that this did not answer.** What NEW MATHEMATICS,
if any, does the distinction warrant -- and what machinery would let it improve
the reliability of model output, which is why the work was begun. "Recording is
sufficient" is a permitted answer if you can say why that is not decoration.

### Q3. The rubric and the human queue -- a boundary condition, not a new mechanism.

The pre-registration says the consequence rubric governs where it and the numeric
proxy disagree, that a machine cannot adjudicate its 5 clauses, and that a model
or the human must. Measured: they agree on 141 of 259 judgeable cases in the
disputed band, 54.4%, Wilson [48.4%, 60.4%].

**The founder's constraint, which narrows this sharply.** The human queue exists
for genuinely irreducible problems: those not computationally accessible, those
affecting safety, those affecting system performance, and legal or ethical
questions. It must NOT be inflated with items that are demonstrably decidable by
tool. So: **what fraction of the disputed-band population is programmatically
decidable, and what test separates the two?** Only the genuine remainder should
reach a human.

The founder adds a selection rule worth testing: **where 2 solutions to an issue
exist, prefer the one that matches the simplicity/sufficiency formalisation most
exactly.** Is that operable as stated, and if so how would it be applied here?

---

State what you would accept as evidence you are wrong, per question. Do not pad.
