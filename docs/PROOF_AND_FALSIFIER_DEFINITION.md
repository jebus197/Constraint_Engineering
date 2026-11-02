# What a proof is, and what a falsifier is

**Status: DRAFTED for the founder's ratification, 2026-11-02.** He accepted the recommendation that this be written from the code and ratified by him, with no panel: *"My reading is that it follows from the code and is mine to write and yours to ratify, so no panel is needed."* Every definition below is derived from live source with a file and line citation, not composed from intent. Where the code leaves something undecided, this document says so rather than filling the gap.

## 1. A falsifier

A falsifier is a self-contained Python snippet, attached by a reviewing model to a critical finding, that **raises `AssertionError` or prints `FALSIFIED` if and only if the claimed defect is real** (`bench/falsifier_verify.py:1-8`).

It carries 2 hard requirements:

1. **It must import the real target.** The module's own words: it *"must IMPORT THE REAL target module ... so it exercises actual repository code, not a model-retyped copy"*. A snippet that reasons about a copy of the code is not a falsifier.
2. **The runner, not the model, decides.** The runner re-runs the snippet independently through `reverify_falsifier`, and *"The runner's result is the verdict — never the model's prose claim."* The reason is measured rather than assumed: the smoke tests of 3 June 2026 proved a model can attach a correct falsifier while making 0 tool calls of its own, so the independent re-run is the only trustworthy decision point.

The sandbox is part of the definition, because a snippet that could not be run safely could not be a falsifier. The guarantees are stated as hard constraints in the same module: a 30 second wall-clock timeout per run; a fresh temporary working directory, never the repository; the repository importable by `PYTHONPATH` so targets can be imported; and read-or-import only, since the snippet file lives in the operating system temporary directory and the working directory is disposable.

## 2. A proof

A proof is the opposite instrument, and the distinction is a matter of **polarity** rather than of form.

A proof is a snippet that **must contain an assertion or a raise** (`bench/proof_verify.py:22-28`). A clean exit from a proof is read as every assertion in it holding, which is what grants admissibility. That is precisely why the assertion requirement exists: a proof containing no assertion at all exits cleanly, so without the requirement *"a model could print 1 harmless line and have its repair admitted"*.

This predicate is deliberately **narrower** than the one used to decide whether a fenced code block is a candidate falsifier. The runner's `_runnable` accepts an import statement as evidence that a block is real code. The module states why that is wrong here: *"a proof that only imports something has asserted nothing, and under proof polarity its clean exit would be read as every assertion holding."* Reusing a predicate written for a different question would have silently widened what counts as proved.

## 3. The 2 polarities, stated plainly

This is the single most confusable point in the vocabulary, so it is written out in both directions.

- **Falsifier polarity.** The snippet is trying to **demonstrate** the defect. A raise or a `FALSIFIED` print means the defect is real and the finding is CONFIRMED. A clean exit means the defect was **not** demonstrated, which is recorded as REFUTED. `FALSIFIER_POLARITY` is the pre-existing default (`bench/proof_verify.py:117-119`).
- **Proof polarity.** The snippet is trying to **demonstrate that a claim holds**. A clean exit means the claim holds. A raise means it does not.

So a clean exit means opposite things under the 2 polarities, and that is why the polarity must travel with the snippet rather than being inferred from the code.

## 4. A severity proof is a third, narrower thing

`severity_is_proven(entry)` is **not** either of the above. It asks a single specific question: whether **the model's stated R_k reproduces from its own stated inputs** (`bench/reference_runner_v3.py:10428-10435`).

Its status has 5 values, read from the entry's own `severity_proof` record: PASS, WARN, FAIL, SKIP, or ABSENT when no proof was recorded at all (`bench/reference_runner_v3.py:10420-10425`). **WARN is accepted alongside PASS**, and the stated reason is specific: WARN is a rounding-scale discrepancy at a tolerance of 0.05, which is *"a model writing 3 significant figures, not a model asserting a number it did not compute"*.

## 5. What neither a proof nor a falsifier is

- **Not a vote.** The whole mechanism exists under the project's rule that tools decide and models do not vote. A model's prose claim that a defect is real carries no weight at any point in the chain.
- **Not the model's own execution.** The model may run its snippet or not; the runner re-runs it regardless, and only the re-run counts.
- **Not a substitute for the other.** A falsifier that passes does not prove a repair correct, and a proof that passes does not demonstrate a defect.

## 6. What the code does not settle, and is therefore the founder's to ratify

3 things are genuinely open, and each is named rather than resolved here.

1. **Whether a non-discriminating falsifier may close a critical finding.** The code records this decision as still open and deliberately avoided settling it by side effect: the corrected-copy ask is gated off by default precisely because arming it *"would have settled"* the question *"by side effect"* (`bench/reference_runner_v3.py:865-871`). This is the decision with the most consequence, because 76 of 91 discrimination-control outcomes in the archive are `INDETERMINATE_NOT_INTERCEPTED`, 0.835165, Wilson 95% [0.745693, 0.897486].
2. **Whether an absent falsifier is a different state from a falsifier that ran and failed.** The status vocabulary distinguishes ABSENT from FAIL for a severity proof, but the falsifier side records UNTOOLABLE and `<none>` as separate values without a stated rule for how a gate should treat each.
3. **Whether a falsifier must read the staged copy or may read the original target.** Both are currently reachable, the forensic scope check flags the staged root at its certainty tier, and that defect is carried at B82.

## 7. How to ratify or amend this

Each numbered definition above is a separate ruling. The useful form of a response is per section: accept, or state the change. A definition altered here should be accompanied by a guard, because the project's standing position is that a definition no mechanism reads is a definition that will drift.

## Citations

- `bench/falsifier_verify.py:1-22` — the falsifier definition and sandbox guarantees.
- `bench/proof_verify.py:16-30` — the assertion requirement and why `_runnable` was not reused.
- `bench/proof_verify.py:117-119` — `FALSIFIER_POLARITY` as the default.
- `bench/reference_runner_v3.py:10420-10435` — `severity_proof_status` and `severity_is_proven`.
- `bench/reference_runner_v3.py:865-871` — the open decision on a non-discriminating falsifier.

Written under CDSFL note standard v1.9.
