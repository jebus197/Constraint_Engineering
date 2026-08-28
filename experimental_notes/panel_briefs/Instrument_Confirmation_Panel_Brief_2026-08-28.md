# Panel review: confirm or refute the instrument inventory, with tools

You are one of three reviewers (CC1, CC2, Fable). CC1 curates and does not vote.
Your working directory is a disposable copy of the repository. **Tools decide,
not votes** — run the test, then make the claim.

## What this is

`scripts/instrument_inventory.py` classifies 34 components by whether they are
COMMISSIONED. Its definition of commissioned is strict and worth holding to:

> a test feeds the component known-good AND known-bad input and asserts that it
> answers differently.

A component with tests that only assert it runs, or that only check a happy
path, is **tested but not commissioned**. This project has repeatedly found
components in that state — a full test suite and nothing that would fail if the
component silently stopped discriminating.

## Why a panel, and what the founder ruled

The inventory is a **HEURISTIC, not a verdict**. It marks a row as a
commissioning candidate when a test names the component and carries both a
positive and a negative assertion. That is a proxy, and it has been measured
wrong in the reassuring direction: 2 rows (I14, I26) where the heuristic said
commissioned and measurement said otherwise.

**Founder ruling 2026-08-22: the panel confirms or refutes each row with tools.**

So the 32 rows currently marked "yes" are **UNVERIFIED**, not reassurance. Your
job is to convert heuristic into verdict.

## The current inventory output

```
  id   instrument                                emits            flag             tests  commissioned?   
  I01  Duane/Crow-AMSAA gamma estimator          number           -                    6  yes             test_vacuous_gamma_curve.py
  I02  Two-sided gamma gate                      verdict          -                    9  yes             test_vacuous_gamma_curve.py
  I03  Churn detector (rho)                      number           -                    1  yes             test_per_model_rho_itc.py
  I04  State-convergence check                   verdict          -                    1  yes             test_stopping_components_commissioned_2026-08-25.py
  I05  Gamma-alt convergence                     verdict          -                    9  yes             test_vacuous_gamma_curve.py
  I06  Hardened convergence                      verdict          -                    1  yes             test_hardened_gate.py
  I07  Stall convergence                         verdict          -                    1  yes             test_stopping_components_commissioned_2026-08-25.py
  I08  Budget extension                          verdict          -                    1  yes             test_stopping_components_commissioned_2026-08-25.py
  I09  Attention metrics                         numbers          -                    1  yes             test_fingerprint_attention_metrics.py
  I10  S_k fix efficacy                          number           on in 19/19          3  yes             test_immune_memory_consumption.py
  I11  S_k admissibility threshold               verdict          on in 19/19          3  yes             test_immune_memory_consumption.py
  I12  R_k three-phase model                     number           -                    5  yes             test_channel_boundary.py
  I13  R_k eta channel                           number           -                    3  yes             test_channel_boundary.py
  I14  THE FALSIFIER GATE                        verdict          on in 20/20         11  NO              MEASURED: MEASURED 2026-08-22: reverify_falsifier("print('FALSIFIED')") returns CONFIRMED, and so does "assert False, 'FALSIFIED'". The gate has never required a falsifier to depend on its target. NOT COMMISSIONED, and the heuristic scored it as commissioned.
  I15  Verdict reader                            verdict          -                   16  yes             test_equipment_error_not_terminal.py
  I16  Discrimination control                    verdict          (presence-gated)     4  yes             MEASURED: MEASURED 2026-08-22: run against 372 archived falsifiers with a tripwire, a baseline requirement and a determinism check; it separated 132 discriminating from 131 non-discriminating.
  I17  Routing/escalation ladder                 routing decision on in 18/20          5  yes             test_equipment_error_not_terminal.py
  I18  Status transitions                        status           -                    5  yes             test_confer_verification.py
  I19  Similarity function (3 tiers)             number+verdict   -                    3  yes             test_hierarchical_novelty.py
  I20  Outcome agreement (tier 3)                verdict          -                    2  yes             test_anchorless_outcome_guard.py
  I21  Location keying                           series           -                    2  yes             test_premise_exclusion.py
  I22  Divergence measure                        number           -                   16  yes             test_ouroboros_query_builder.py
  I23  Diversity measure                         number           -                    4  yes             test_diversity_metric.py
  I24  Fix complexity (nu), shadow               number           (shadow)             1  yes             test_fix_complexity.py
  I25  Immune memory prior                       number           -                   19  yes             test_ouroboros_query_builder.py
  I26  Load balancer  [SHELVED 2026-08-22]       allocation       (shelved)            1  NO              MEASURED: SHELVED by founder ruling 2026-08-22. Never ran outside its own tests; reports an impossible allocation as a success.
  I27  Shadow stage-6                            number           (shadow)             2  yes             test_shadow_stage6_calibrator.py
  I28  Near-duplicate feedback into the prompt   prompt text      -                   14  yes             test_feedback_channel.py
  I29  Claim-type classifier                     class            -                    2  yes             test_immune_agents.py
  I30  Immune removal decision                   verdict          -                   39  yes             test_ouroboros_query_builder.py
  I31  Health monitor                            alarm            -                   17  yes             test_discrimination_control.py
  I32  Finding parser / description extractor    structured findings-                    7  yes             test_score_exam.py
  I33  Survived-falsification ledger             positive record  (wired 2026-08-22)     3  yes             MEASURED: MEASURED 2026-08-25: EXERCISED, not merely wired. REFUTED writes a survival row; CONFIRMED, ERROR and UNTOOLABLE write none; the verdict denominator is kept so an empty ledger can state why it is empty; the report carries its own not-proof-of-truth caveat; the gate signature still accepts a ledger. Supersedes the 2026-08-22 reading of NOT COMMISSIONED, which was correct when taken -- nothing called it then.
  I34  Null-perturbation control                 verdict          (offline script)     1  yes             MEASURED: MEASURED 2026-08-21: 397 findings, 360 fired, 0 moved on either an irrelevant comment or an unaccused function rename.

  32 of 34 have a commissioning candidate; 2 do not.

  CALIBRATION OF THE HEURISTIC AGAINST DIRECT MEASUREMENT:
    5 rows have been measured directly; the heuristic
    disagreed with the measurement on 2 of them (I14, I26).
    2 disagreement(s) in the CONFIDENT direction (I14, I26): the heuristic said commissioned
    where measurement says it is not. That is this project's house
    failure mode, so the 32 'yes' rows below are UNVERIFIED, not
    reassurance.

  HEURISTIC, NOT A VERDICT. 'Commissioning candidate' means a test names
  the component and carries both a positive and a negative assertion. The
  panel confirms or refutes each row with tools (founder ruling 2026-08-22).

```

## What to do

Work through the rows. For each one you examine:

1. **Name the component and the test file** that supposedly commissions it.
2. **Run that test.** Then break the component deliberately — a one-line edit in
   your disposable copy — and run the test again.
3. **The verdict is whether the test FAILED when the component was broken.**
   If it still passed, the component is NOT commissioned regardless of what the
   heuristic says, and regardless of how many tests name it.
4. Record the exact break you made, so CC1 can reproduce it.

Prioritise by consequence. A component whose silent failure would corrupt a
convergence verdict matters more than one whose failure is visible. Say which
you prioritised and why.

## Specific things worth your scepticism

- **I14 and I26** are the two the heuristic already got wrong in the confident
  direction. Start there and establish what the heuristic mistook.
- Any row whose "commissioning" test is a **source-text assertion** (checking a
  string appears in a file) rather than a behavioural one. Those pin wiring, not
  behaviour, and this project has confused the two before.
- Any component whose failure mode is **returning a plausible default** rather
  than raising. Those are the ones that pass happy-path tests forever.

## Also report: clean-run readiness

Second question, separate verdict. Given what you find, is the harness ready for
a clean experimental run? Name specifically what would have to be true, and what
currently is not. A list of preconditions, not a yes or no.

## Output format

A table of rows examined: component, test file, break applied, test result under
break, VERDICT (COMMISSIONED / NOT COMMISSIONED / COULD NOT TEST). Then the
clean-run readiness verdict. Then **WHAT I COULD NOT CHECK AND WHY**.

Coverage matters less than honesty about coverage. Ten rows genuinely tested
beats thirty asserted.

Do not pad. The founder is dyslexic and reads every word.
