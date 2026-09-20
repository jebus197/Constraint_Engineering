# PANEL BRIEF — is the proposed mathematical revision NEEDED, or is it unbounded model churn?

## Section 1 — The question, and it is not the obvious one

A revision to this project's mathematical model, version 1.1, was produced by an unbounded frontier model asked to improve the existing model. **Adoption is undecided, and the question is not primarily "is the revision correct".**

The founder's question, verbatim: *"Basically do we need it given this new framing and your own formalisations/derivations of this, or is it itself potentially just an example of unbounded LLM churn? And what should we take from it (if anything), again given this new framing?"*

**The selection effect you must reason about.** The revision was produced by a model given a working mathematical model and asked to improve it, with none of this harness: no falsifiers, no directives, no requirement to subject its own output to severe testing, no tool gates. A model asked to improve something will produce improvements whether or not any are needed. That is a property of the request, not evidence about the model. So every proposal in the package is to be graded **individually on its own executed evidence**, and the package is not to be adopted or rejected as a unit.

**This is not an invitation to design new mathematics.** The founder's instruction, verbatim: *"the purpose of the review is not to tell the models to invent a ton of decorative new maths, but rather simply to address its validity or otherwise, and to subject it to the kind of severe testing/falsification that the model itself promotes, while using the revised model to do so -- and also to offer corrections where it may be patently wrong."*

Corrections to what is there: yes. New apparatus: no. **A proposal that adds a term nobody can measure is decorative, however sound its derivation.**

## Section 2 — The framing you must reason inside, which is new and changes the question

This framing is the founder's, set out in his consolidated notes of 2026-09-15, and it is the context in which "do we need it" must be answered.

**Gamma is a ruler, not a verdict.** A declining discovery rate is a strong indication that the currently accessible problem space is becoming depleted. It does not prove every error has been found, nor that a different method would find nothing. The interpretation is a **hypothesis**, informed by the observed trajectory and by what is known about the capability and scope of the examinations performed. In the founder's words: *"A ruler does not decide what length is acceptable for a particular purpose. It provides a measurement that somebody can use to make that decision."*

**Stopping is a researcher's decision, not a mathematical fact.** It depends on the likely value of another finding, its significance, the cost of further work, time, resources and aim. Two researchers can agree entirely about the measured trajectory and reasonably stop at different points.

**Bounded recursion.** Another cycle is worthwhile because something sufficiently useful might be revealed, not because recursion is intrinsically valuable. A question exhausted under one method may become productive again under a better one. **A decision to stop is not a claim that nothing remains.**

**The consequence for this review:** a revision that makes gamma's inferential limits explicit is not demoting gamma. It may be saying, in more precise terms, what the framing above already says. Your job includes deciding whether that is all it is doing.

## Section 3 — What CC1 has already derived, for you to falsify

These are CC1's own results, produced with SymPy, mpmath, NumPy, scipy and statsmodels and cross-verified between at least 2 tools. **Attack them.** If any is wrong, that is a finding worth more than agreeing with it.

**3.1 The degeneracy is a line, not a point.** The package reports `free_parameters_can_fit_any_desired_risk: true` and exhibits 1 setting per target (`s = 1 - d`, `b = d`). Solving the same equation for `b` given ANY `s` gives `b = (z - s*z - d)/(z - 1)`: a 1-parameter family. Worked, from `z = 0.25` to a target of `0.5` — `s = 0.1` needs `b = 0.3667`; `s = 0.7` needs `b = 0.5667`; `s = 0.9` needs `b = 0.6333`. All inside [0,1]. Producer: `scripts/free_parameter_degeneracy_2026-09-20.py`.

**3.2 The reachable sets differ, and that is the whole falsifiability question.** The existing collapse form `R(1-p)/(1-pR)` over `p` in [0,1] reaches exactly `[0, R]` — it can never exceed the risk it started from. The revised action step `(1-s)z + b(1-z)` over both parameters reaches `[0, 1]`. **The existing model forbids outcomes; the revised one, as parameterised, forbids none.** Constrain `b = 0` and the revised step reaches `[0, z]` again — so the entire degeneracy is carried by the introduction term.

**3.3 The revision CONTAINS the existing model.** With a clean review of sensitivity `p` as likelihood `(1-p)` if flawed and `1` if clean, and no action, the package's own `update()` reproduces `R(1-p)/(1-pR)`: 0 mismatches over 20 exact rational steps, mpmath agreeing to 3.4e-41 across 399 pairs. **A generalisation that recovers the original exactly cannot falsify it.**

**3.4 The residual risk behind a flat curve is R\* = b/p.** If repairs inject defects at rate `b` while review catches at sensitivity `p`, the recursion settles at `b/p`. At `p = 0.35`: `b = 0.02` settles at 5.71% residual, `b = 0.10` at 28.57%, `b = 0.20` at 57.14% — and in **every** case the per-round discovery rate decays to essentially 0. **A flat decay curve is consistent with 28.6% residual risk.** SymPy and mpmath agree at every point.

**3.5 But the existing two-sided gate already refuses that case.** Executed against the real `_check_gamma_alt_convergence`: flat gamma with no new criticals converges; flat gamma with 2 new criticals per round **refuses**; even 1 new critical in the last round refuses; unresolved criticals raise an A4 block. Injected defects are new findings, so the second condition catches what gamma alone misses.

## Section 4 — The questions to answer

1. **Is the revision NEEDED?** Given Section 2's framing and Section 3's results, does the revision give this project anything it does not already have? Answer in terms of what becomes decidable that was not decidable before.
2. **Is the introduction rate measurable in this project's archive?** This is the decisive empirical question. The extra parameter buys the ability to represent repairs that make things worse — real, and measured in this project's own history. If `b` cannot be estimated from what is recorded, the term adds freedom and no content. Look at `bench/logs/`, the archived run records and the finding registries and say whether paired pre-repair and post-repair states exist.
3. **Does the two-sided gate actually close the R\* = b/p hole, or only appear to?** The gate catches regression when injected defects surface as criticals. If a repair introduces something the same review is LESS sensitive to than the original defects, does the gate still fire? Construct the case and test it.
4. **Grade each proposal separately.** The replaced repair interpretation; the novelty-validity decoupling; the abstention channel; the conditioning made explicit; the separation of derivation from calibration. For each: NEEDED / ALREADY HAVE IT / DECORATIVE / WRONG, with executed evidence.
5. **Falsify Section 3.** Any of CC1's 5 results that does not hold is a finding.
6. **What should be taken from it, if anything?** A concrete list, in adoption order, or an explicit "nothing".

## Section 5 — The standard you work to

You run under the full CDSFL harness and are expected to use the mathematical model as an instrument, not discuss it.

1. **Every claim is falsified before it is presented.** A claim you have not tried to break is a hypothesis.
2. **Tools decide, not prose.** SymPy, z3, mpmath, SciPy, statsmodels and NumPy are primary, and you have `run_python`, `run_pytest`, `read_file`, `grep` and `list_dir`. Wolfram is the SECOND falsifier where it can check a result you already hold.
3. **A failed call is NOT EVIDENCE.** An error, a timeout or a `Name::tag` message verified nothing, and the claim stays UNVERIFIED.
4. **Cross-verify.** Every computational claim is checked with at least 2 independent tools, and every proportion carries a Wilson interval.
5. **A number travels with the code that produced it.** A figure with no runnable producer is a claim about evidence.
6. **Where gamma, rho, the two-sided gate, severity or the S_k threshold bear on your answer, use them.** Say plainly if they do not; a forced application is worse than none.

## Section 6 — What you are reviewing

The package is at `docs/maths_revision_review_2026-09-10/`, entry point `START_HERE.md`. Paths below are relative to it.

- `outputs/CDSFL_revised_model_specification.md` — the revision itself.
- `outputs/CDSFL_revised_core.py` — the reference arithmetic. **Execute it.**
- `outputs/CDSFL_revised_model_validation_plan.md` — the staged empirical programme. Question 2 lives or dies here.
- `outputs/CDSFL_lineage_and_decay_clarification.md`, `outputs/CDSFL_mathematical_review_2026-09-09.md`, `READING_COPY.html`, `work/`.
- In the repository: `docs/MATHEMATICAL_APPENDIX.md`, `explorer/index.html`, `bench/reference_runner_v3.py` for the live gate, and `scripts/free_parameter_degeneracy_2026-09-20.py`.

**Run the checks rather than reading them:** `VERIFY_PACKAGE.py`, then `outputs/CDSFL_math_counterexamples.py`, `outputs/CDSFL_revised_model_checks.py`, `outputs/CDSFL_severe_testing_checks.py`.

## Section 7 — Scope boundaries, which are HARD

- **Gamma is load-bearing and is not up for demotion.** You may and should examine whether the revision's treatment of decay is consistent with gamma as the project uses it. You may not propose making it reported-only.
- **The convergence gate is two-sided by design.** Criticise its calibration on evidence; do not propose replacing it with a single-sided rule.
- **Do not add a parameter without saying how it would be measured.**

## Section 8 — Fixes, and how to deliver them

Where the revision or the existing appendix is patently wrong, **fix it**.

- **Deliver each fix as a file in your sandbox repository tree, at a real path.** Not a diff quoted in prose. Do not write into `.scratch`: work there if you like, but deliverables go at real paths.
- **Write a falsifier for each fix and execute it.** State the command and its output.
- Keep the existing notation.

## Section 9 — Output shape

For each finding: the claim, the executed evidence with the exact command, the verdict (HOLDS / FAILS / PARTIAL / UNCHECKED), the fix and its falsifier, and **what would refute your own verdict**.

Then, in its own section, **where you disagree with the other seats or with CC1**. Disagreement is preserved as information, never smoothed. A section reading "none" is not a disagreement section; if you genuinely disagree with nothing, say what evidence would have changed that.

End with a single verdict: **ADOPT / ADOPT WITH THE NAMED CORRECTIONS / DO NOT ADOPT / UNRESOLVED**, and separately answer question 1 in one sentence: is it needed, or is it churn?

## Section 10 — Termination

Do not wait on a background task. Whatever you have written when your turn ends IS your answer. A partial answer carrying executed evidence is worth everything; a holding note is worth nothing. **Stop when further passes produce no new above-threshold findings** — the founder's stopping rule for this round is that it ends when the results are definitively useful, not when a budget is exhausted.
