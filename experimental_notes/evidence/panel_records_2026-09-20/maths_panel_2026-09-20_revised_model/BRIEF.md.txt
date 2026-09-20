# PANEL BRIEF — does the proposed mathematical revision hold, and where is it wrong?

## Section 1 — The question

A revision to this project's mathematical model, version 1.1, is proposed and **adoption is undecided**. Your task is to decide whether it holds, and to say precisely where it does not.

**This is not an invitation to design new mathematics.** Do not propose alternative formalisms, extra parameters, or decorative generalisations. The founder's instruction, verbatim: *"the purpose of the review is not to tell the models to invent a ton of decorative new maths, but rather simply to address its validity or otherwise, and to subject it to the kind of severe testing/falsification that the model itself promotes, while using the revised model to do so -- and also to offer corrections where it may be patently wrong."*

Corrections to what is there: yes. New apparatus: no.

## Section 2 — What you are reviewing, and what you must use

The review package is **inside the repository** at `docs/maths_revision_review_2026-09-10/`. Its own entry point is `START_HERE.md`. Paths below are relative to that directory unless stated otherwise.

It was copied there from the founder's own assembly of it, unchanged apart from dropping 1 of 2 byte-identical PDFs, **because the seat sandbox refuses any path outside the repository**. Measured before this brief was written: a seat reading the package at its original location gets `[INTEGRITY VIOLATION - NOT EXECUTED] a path outside the declared target`, and would have spent its whole tool budget on refusals. From `docs/` it loads and runs.

**Primary sources, authoritative over any summary:**
- `outputs/CDSFL_revised_model_specification.md` — compact and expanded forms, derivation, assumptions, worked cases, severe testing, circularity checks, self-audit.
- `outputs/CDSFL_revised_core.py` — the exact reference arithmetic. **Execute it.**
- `outputs/CDSFL_lineage_and_decay_clarification.md` — the claimed links to the existing model.
- `outputs/CDSFL_revised_model_validation_plan.md` — the staged empirical programme.
- `outputs/CDSFL_mathematical_review_2026-09-09.md` — the critique that motivated the revision.
- `READING_COPY.html` — the same documents as an offline browsable copy with live mathematical markup. Use it where reading the equations matters.
- `work/` — the frozen original sources, the counterexamples, the challenge records and the validation-design material, including `work/revision-core/derivation.md` and `work/revision-challenge/severe_testing_review.md`.
- In the repository under review: `docs/MATHEMATICAL_APPENDIX.md` for the model being revised, and the project's interactive explorer at `explorer/index.html`.

**Run the checks rather than reading them:** `python3 VERIFY_PACKAGE.py`, then `outputs/CDSFL_math_counterexamples.py`, `outputs/CDSFL_revised_model_checks.py`, `outputs/CDSFL_severe_testing_checks.py`. They are standard-library only and contact nothing.

## Section 3 — The standard you work to

You are operating under the full CDSFL harness and under the revised model itself. That means:

1. **Every claim is falsified before it is presented.** A claim you have not tried to break is a hypothesis, not a finding.
2. **Tools decide, not prose.** SymPy, z3, mpmath, SciPy, statsmodels and NumPy are primary and are used wherever a claim is computable. Wolfram is the SECOND falsifier, used where it can check a result you already hold, and it is reached through the serial gate already on your PATH.
3. **A failed call is NOT EVIDENCE.** An error, a timeout, or a message of the form `Name::tag` verified nothing, and the claim stays UNVERIFIED. Never record a failed measurement as a result.
4. **Cross-verify.** Any computational claim is checked with at least 2 independent tools, and any proportion carries an interval — a Wilson interval where the quantity is a proportion.
5. **A number travels with the code that produced it.** A figure quoted without a runnable producer is a claim about evidence, not evidence.
6. **Use the revised model's own severe-testing standard on the revised model.** That is the point of the exercise: if its discipline cannot survive being applied to itself, that is a finding.

## Section 4 — Scope boundaries, which are HARD

- **Gamma is load-bearing and is not up for demotion.** The decay curve and diminishing returns are the foundation of the model and of the project. Do not propose making gamma reported-only, and do not argue the founder should stop relying on it. You may and should examine whether the revision's treatment of decay is *consistent with* gamma as it stands, and say so if it is not.
- **The convergence gate is two-sided by design**: a gamma criterion and K consecutive zero-new-critical rounds, both required. Criticise its calibration if the evidence supports it; do not propose replacing it with a single-sided rule.
- **`rho`, `nu` and the severity measure are existing instruments.** Where the revision touches them, say what changes and what breaks. Do not invent replacements.

## Section 5 — The questions to answer

1. **Does the collapse claim hold?** The revision states that with removal and introduction set to 0 and a clean review of sensitivity p, its core becomes the original residual-risk recursion `R(1-p)/(1-pR)`. Verify or refute by execution, symbolically and numerically.
2. **Is the derivation sound?** Conditioning, independence assumptions, the base measure when likelihoods are densities rather than masses, and the binary helper's validity.
3. **The free-parameter problem.** The package's own output reports `free_parameters_can_fit_any_desired_risk: true`. Establish what that costs the model's falsifiability, and whether the validation plan actually constrains the parameters or merely describes constraining them.
4. **The replacement of the repair interpretation.** The package describes this as its most invasive change. Is it correct, and what breaks downstream if it is adopted?
5. **The novelty-validity decoupling** and the treatment of decay: correct, overstated, or under-argued? Say explicitly whether it is consistent with gamma as the project uses it.
6. **Circularity.** The package claims to have checked for conclusions hidden in assumptions. Check that claim by executing its circularity checks, not by reading its account of them.
7. **What would refute the revision?** State at least 1 concrete, runnable test whose failure would sink it.

## Section 6 — Fixes, and how to deliver them

A finding without a repair is half a contribution. Where the revision is patently wrong, **fix it**.

- **Deliver each fix as a file in your sandbox repository tree**, at a real path, not as a diff quoted in prose. You are confined to your own writable copy of the repository; write there.
- **Write a falsifier for each fix and execute it.** A fix you have not tried to break is a hypothesis. State the command you ran and its output.
- If a fix touches `docs/MATHEMATICAL_APPENDIX.md`, keep the appendix's existing notation rather than introducing your own.
- A fix that cannot be tested from the standard library alone should say so and say why.

## Section 7 — Output shape

For each finding: the claim, the evidence (executed, with the exact command), the verdict (HOLDS / FAILS / PARTIAL / UNCHECKED), the fix if there is one and the falsifier that tests it, and **what would refute your own verdict**. Quote line references. If a check could not be run, say UNCHECKED and why — never infer a result from a failed measurement.

Disagreement with the other seats is information and is preserved, not smoothed. You are not asked to converge with anyone.

End with a single overall verdict: **ADOPT / ADOPT WITH THE NAMED CORRECTIONS / DO NOT ADOPT / UNRESOLVED**, with the reasoning that decides it.

## Section 8 — Termination

Do not wait on a background task. Whatever you have written when your turn ends IS your answer. A partial answer carrying executed evidence is worth everything; a holding note is worth nothing. Stop when further passes produce no new above-threshold findings — diminishing returns is the criterion, not exhaustion.
