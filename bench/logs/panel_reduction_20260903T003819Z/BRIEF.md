# PANEL BRIEF — THE REDUCTION CRITERION

You have Bash, Read, Grep, Glob. Your working directory is a disposable copy of the
repository. **Run the commands. Do not take a single number in this brief on trust** —
five of eleven claims the author made while producing it were overturned by a tool that
was then run. Assume the same rate applies to what follows.

Answer **Q1 from the three cases and the repository alone, before reading Section 3.**
Section 3 states where the author landed; Q1 exists to see whether you land elsewhere.

---

## SECTION 1 — THE THREE CASES

Three "simplifications" from this project's own record. Two are held to be legitimate,
one is held to be a defect. Determine what separates them.

**CASE A — the prior flaw rate vanishing from the recursive risk update.**
`docs/MATHEMATICAL_APPENDIX.md` §1.1 and line 184. The update is
`R_k(i) = R_k(i-1)(1-q) / (1 - q·R_k(i-1))`, initialised at `R_k(0) = π_k`. The claim is
that π plays no further part once the first update has run.

**CASE B — E = mc².** The restricted form of `E² = (pc)² + (mc²)²`. Included because the
founder raised it as the archetype of "simple but demonstrably sufficient". Treat it as an
illustration to be tested, not as physics being imported into this project.

**CASE C — the finding-absorption fix, `bench/reference_runner_v3.py` around line 11209.**
A textual-signature-similarity rule was proposed as a sufficient stand-in for a rule based
on difference between falsifiers. The author reports it "closed the easy case and left 40%
of the real one open" (commit `976b6b5`).

## SECTION 2 — MEASUREMENTS TO RE-RUN, NOT TO BELIEVE

Each of these is the author's; each is checkable in your copy. Report any you cannot
reproduce, and say what you got instead.

1. `docs/MATHEMATICAL_APPENDIX.md` states **29** reduction properties ("reduces to",
   "special case", "vanishes"). **Zero** are asserted by any test in `bench/tests/`.
2. `compute_rk` in `bench/reference_runner_v3.py` computes
   `nu_eff = 1 - (1-nu_b)(1-(1-sk)·nu_f)`. The claim is that this is **blind to the fix**:
   no complexity, size or blast-radius term appears, so two fixes with equal `sk` and
   wildly different reach receive identical re-injection risk.
3. The appendix's hard exit — `ν > ν*` means the cycle is net harmful, stop fixing — is
   claimed to exist **in no live code path**, only in the appendix and in briefs.
4. `bench/dm/_fix_complexity.py` is claimed to have **no pipeline caller** (its one
   non-test reference is an inventory script).
5. The runner carries **27** decision-shaping tunable numerics; **7** are documented as
   pre-registered or founder-ruled — 0.26, Wilson 95% CI [0.132, 0.447]. Stated as a
   lower bound: one module, and a name matcher cannot see an unnamed literal.
6. Case C: the simple rule and the full rule disagree on **282 of 711** same-function
   pairs — 0.397, Wilson 95% CI [0.361, 0.433].
7. Across 309 commits since 2026-08-14, **13** record an earlier *fix* proving
   insufficient — 0.042, CI [0.025, 0.071]. Only 4 are self-attributed, CI [0.13, 0.58],
   which spans one half.
8. Searching the record for a model **dishonestly optimising a measured quantity** returns
   **0**. Searching for **containment** events — a model acting outside its boundary —
   returns **5**: a reviewing model mutating the Exp 47 target and restoring it
   (`9bb0047`), a model writing to the repo (`98ddede`), a sandbox escape (`eeaa0b3`),
   panel agents editing the repo twice on 2026-09-01, and repeated integrity-log
   mutations.

## SECTION 3 — WHERE THE AUTHOR LANDED (read only after answering Q1)

Two unrelated properties share the word *simple*. **Cost simplicity** is a small artefact —
few lines, low blast radius. **Compressive simplicity** is a short statement with wide
reach, which is small because it captured the structure, not because something was
dropped. The project has been optimising the first and the founder has been asking for the
second.

Proposed name and definition — **The Reduction Criterion**. Let S be the proposed simpler
form, F the fuller form it claims to replace, and D the scope declared *before* either was
proposed. The residual is Δ = { x ∈ D : S(x) ≠ F(x) }, and the **truncation rate** is
τ = |Δ| / |D|.

> A simplification is admissible iff **τ = 0 across D**, or **Δ is characterised, bounded,
> and filed as its own claim carrying its own test.**

τ = 0 may be established by **proof** (symbolic equivalence over D) or by **enumeration**
of D. A confidence interval applies **only** where D was sampled. Case A: τ = 0 by proof.
Case B: τ = 0 by proof within its declared scope, and the residual outside it is the
Newtonian kinetic energy — a *nameable* claim with its own domain. Case C: τ = 0.397, not
a reduction, inadmissible as a simplification.

Provenance: this is **theory reduction** (Nagel, *The Structure of Science*, 1961) and the
**correspondence principle** (Bohr, 1920s) — a general theory reducing exactly to a
restricted one under stated limits. Nothing here is novel as a concept. What would be new
is instrumenting it as an executable acceptance gate and measuring truncation rates.

Constraint-solver results, reproducible with z3: a complexity *score* is gameable (witness
found: coverage falls 1/5 → 0/5 while the score improves) and its verdict flips with the
weight; the *predicate* is unsat for gaming and carries no weight. **The founder has ruled
that the gaming argument is over-weighted in this project** — see measurement 8 — so the
parameter-free property, not the anti-gaming property, is what should carry the case.

## SECTION 4 — THE QUESTIONS

**Q1. From Section 1 and the repository only: what distinguishes the admissible
simplifications from the defective one?** State your discriminator before comparing it to
Section 3. If you arrive somewhere else, that is the most useful thing you can return.

**Q2. Is the distinction between simplicity and sufficiency valid as an engineering
distinction, and is the reasoning above sound?** You are explicitly permitted — and
expected, where true — to declare it **sound**. This panel is not scored on finding
problems. If it holds, say so and say what it rests on.

**Q3. How should these two principles be quantified and expressed?** Is τ the right
quantity, or is there a better one already present in this project under another name?
Note that the appendix already carries `ν ≤ ν*` as a benefit/cost trade. **The founder's
constraint is explicit: we are not adding complexity, only defining the essence of these
principles.** A recommendation of "define it, add no machinery" is a legitimate answer.

**Q4. How should it be applied, and what should be learned going forward?** Concretely:
does it belong in `docs/MATHEMATICAL_APPENDIX.md` as a definition, in the acceptance
policy as a rule, in the directives, or nowhere? If findings 1–4 above reproduce, is the
right first move to make the 29 existing reduction properties checkable, or something else?

**Q5. Containment — practically, not as a crisis.** Given measurement 8, and given that
this very dispatch confines you to a disposable worktree: what is the *proportionate*
next step? What should the next simulated run measure about containment, and what would
distinguish a model exceeding its boundary while trying to help from one doing something
worse?

**Q6. Anything the author has missed.** Including: is any part of this a solution in search
of a problem, given that the project's own stopping criterion asks whether the absence of
a piece of machinery would waste bench compute?

Where a question has a decision consequence, state the consequence you would accept if you
turn out to be wrong. Do not pad.
