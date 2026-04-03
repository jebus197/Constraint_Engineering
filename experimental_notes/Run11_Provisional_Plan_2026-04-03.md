# Run 11 Provisional Plan

**Date:** 3 April 2026
**Status:** Provisional — contingent on Run 10 results
**Premise:** Run 10 is the first run where all immune cells are operational.
Run 11 responds to what Run 10 reveals.

## What Run 10 Tests

Run 10 is a diagnostic run. It answers:

1. Does the B-Cell produce meaningful verdicts now that it actually fires?
2. Does the calibrated NK Cell (tau_sim=0.33) catch restatements?
3. Does convergence detection terminate the run at a reasonable point?
4. Do the models find new bugs in the revised immune code, or restate old ones?
5. Does the Dynamic Management health monitor's self-tuning matter in practice?

## Run 11 Decision Tree

### Branch A: Run 10 converges cleanly (findings stabilise, run terminates early)

The infrastructure fixes worked. Run 11 focus shifts to the 5 valid Dynamic
Management findings from Run 9, applied and verified:

1. Per-model pathology routing — add per-model key resolution in apply_diagnosis
2. Legacy chain bypass blocks — remove special-case branches for mu_novelty_disagree,
   dispatch_false_positive, verification_miscalibration so they use their chains
3. sensitivity_decay self-adjustment direction — fix self_diagnose so increasing
   decay widens the window (reduces sensitivity) as intended
4. Remediation state collision — scope _remediation_state by (chain_key, model_id)
5. Deferred remediation round — use approval round, not queue round

Run 11 then tests whether the Dynamic Management layer with correct self-tuning
produces different convergence behaviour than Run 10 without it.

### Branch B: Run 10 converges but B-Cell verdicts are all UNCERTAIN

The f-string fix kept the B-Cell alive but it still cannot parse natural language
claims into SymPy expressions. Run 11 focus: improve claim extraction.

Options (evaluate before committing):
- Structured claim extraction in the Dendritic Cell: pull mathematical sub-claims
  from code-focused descriptions and express them as testable assertions
- Dual routing: send code findings with mathematical properties to both the
  Cytotoxic T cell and the B-Cell, with different extracted claims for each
- Accept that B-Cell adds value only for genuinely mathematical findings and
  focus effort elsewhere

Still apply the 5 Dynamic Management fixes regardless.

### Branch C: Run 10 does not converge (churn persists despite fixes)

The dedup threshold and convergence detection work but the models keep producing
cosmetically varied restatements that pass the similarity check. This means the
problem is upstream of the immune layer — it is in the prompt structure.

Run 11 focus: add conferring structure to the parallel round instruction.
Currently models see a dump of prior findings and produce more findings. There
is no agree, disagree, or extend structure. They cannot say "I looked at this
and it is already fixed" or "I agree with this finding but the proposed fix is
wrong." Without that structure, restating an existing finding in different words
is the only way a model can express agreement.

Concrete change: add to the adaptive round prompt a section requiring each model
to classify each prior finding as AGREE, DISAGREE, EXTEND, or SUPERSEDED, with
a one-sentence justification. Novel findings remain as they are. This preserves
parallelism (all models still run simultaneously) but adds the missing discussion
layer.

Still apply the 5 Dynamic Management fixes.

### Branch D: Run 10 reveals new infrastructure bugs

The ouroboros finds something we missed. Treat these as priority fixes, apply
them, and re-run as Run 11 before proceeding to Dynamic Management work.

## Invariants Across All Branches

- Switch runtime to Python 3.13 before Run 11 (eliminates 3.9 compatibility
  hacks, google-auth warnings, and tomli fallback)
- All fixes verified with SymPy where mathematically falsifiable
- Full test suite must pass before launch
- Convergence detection has three independent signals (gamma on clusters,
  Dynamic Management convergence, finding-ID exhaustion)
- B-Cell, Cytotoxic T cell, and NK Cell all operational
- No silent exception swallowing anywhere in the pipeline

## Success Criteria for Run 11

- Churn rate below 50% (Run 9: 84.5%)
- Convergence detected and run terminates before max rounds
- B-Cell produces at least one non-UNCERTAIN verdict
- If Branch A: Dynamic Management self-tuning produces measurably different
  convergence trajectory than Run 10
- If Branch C: agree/disagree structure reduces restatement rate measurably

## What We Learn

Run 10 tells us whether the immune pipeline works when its components are
actually alive. Run 11 tells us whether the system as a whole can converge
on a stable set of findings through genuine multi-model discussion, or whether
the architecture needs a more fundamental change to the interaction protocol.
