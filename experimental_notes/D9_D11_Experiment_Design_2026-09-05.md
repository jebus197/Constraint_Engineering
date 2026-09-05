# Exp 56: One Model With Tools Against A Panel Of Different Ones — Design For Items D9 And D11
2026-09-05, BST (British Summer Time).

**Design and harness only. Nothing here has been dispatched, and nothing here may be dispatched without a founder ruling, because every arm except one bills a paid route.**

Founder verdict, 2026-09-05: *"The single model against single model with agents experiment, approved but not started, together with restoring the seat contrast as its diversity arm. # Verdict: Do it. Do both."* This note is the design that verdict asks for. The three arm configurations live in `bench/exp56_configs/` and every claim below that carries a number is recomputed by `bench/tests/test_d9_d11_configs_valid_2026-09-05.py`, which passes 69 tests.

## The question, stated so that it can be answered wrongly

CDSFL's central claim about panel composition is that a panel of models from different vendors finds defects that any one of them alone would miss. That claim has never been tested head to head. It has been assumed by the instrument's design since the original panel plan and it has never had a control. Item D9 supplies one, and the honest framing puts the burden on the claim rather than on its denial: the multi-model panel is the arm that has to earn its cost.

The rival hypothesis is the one the record already points at. The correction of 2026-09-02 found that the difference between panel seats which had been attributed to prompt wording was in fact tool access. If tool access is what carries the benefit, then a researcher holding one model and a shell gets most of the value without buying a second vendor, and the multi-vendor architecture is an expensive way of buying something cheaper.

Item D11 splits the third possibility out from the second. A panel differs from a single model in two ways at once: the seats hold different weights, and there are more of them under different operating conditions. The seat contrast is the only configuration in this project that separates those, because it puts two seats on identical weights under different conditions.

## The three arms

| arm | file | seats | what it isolates |
|---|---|---|---|
| A | `d9_single_model_with_agents.json` | `CC2` | one model with native shell tools, no other vendor present |
| B | `d9_multi_model_panel.json` | `CC2`, `Codex`, `Gemini`, `DeepSeek`, `ChatGPT` | the standard instrument: 5 seats, 4 vendors |
| C | `d11_seat_contrast_diversity_arm.json` | `Codex`, `ChatGPT` | 2 seats, identical weights, different operating conditions |

Arm A uses `CC2` rather than a paid seat for two reasons, and both are deliberate. It is the only seat in the roster with native shell tools rather than the `execute_python` function-call loop the OpenAI-compatible routes receive, so it is the strongest single-model configuration available. And it bills nothing per dispatch on the Max subscription, so Arm A's paid-dispatch cost is 0. Choosing the strongest and cheapest single-model arm biases the comparison in favour of the rival hypothesis, which is the right direction: the diversity claim should have to beat the best case for its rival, not the worst.

Arm C reads its two seats as a contrast only if the contrast exists. At HEAD it mostly does not, and the next section is the history of how that happened.

## D11: what the seat contrast was, when it went, and what is left of it

**What it was.** Diversity Axis 2 of the original panel design, recorded in `bench/EXECUTION_PLAN_EXPERIMENT_11.md` under "Diversity Axes": *"Configuration: Codex (factory + CDSFL) vs ChatGPT (bare + CDSFL). Same weights, different operating conditions."* The `Codex` seat dispatched through `codex exec`, which carries OpenAI's own hidden agent prompt and its own native tool loop, with CDSFL delivered as elevated directives inside the prompt body because that route has no system-prompt flag. The `ChatGPT` seat dispatched bare through OpenRouter with CDSFL as the system message. Same weights, two instruction conditions.

**When it went.** 2026-04-02, in commit `556e0af`, *"sv: Run 7b complete — 197 findings, file split, context budget, Layer 3"*. The diff changes the `Codex` seat's `ModelConfig` from `api="codex_exec"` to `api="openrouter"`, and the commit's own changelog line records it as *"Codex routed through OpenRouter (was codex_exec CLI)"*.

**Why it went.** Reliability, and the reason survives as a comment at the call site in `bench/experiment_11_orchestrator.py`: the change eliminated a decomposed fallback costing 45 to 80 minutes per round, and a brittle CLI authentication dependency. The seat contrast was collateral. Nothing in the commit message records that a designed experimental variable had just been removed, and the loss was not noticed in the record until 2026-09-01.

**What was claimed about the loss, and withdrawn.** A comment in `bench/reference_runner_v3.py` once cited a pre-lapse sign test over 78 paired rounds at p = 0.00515 and a post-lapse one over 205 paired rounds at p = 0.378. All 6 figures were withdrawn on 2026-09-01. Neither panel reviewer could reproduce them, no script computing them exists anywhere in the repository, rounds inside one run share target and prompt lineage and accumulated findings so they are not independent trials, and the 205 post-lapse rounds were the entire archive including pre-lapse runs. Taking the run as the unit, the pre-lapse difference does not survive: run-level sign test p = 0.6875, Wilcoxon p = 0.156. Those numbers are recorded here so that nobody resurrects the withdrawn ones. The design conclusion rests on the documented mechanism and needs no p-value.

**What is left, measured 2026-09-05 by executing `load_experiment_config()` rather than by reading the table.** The two seats' `ModelConfig` objects are identical in 11 of 12 dataclass fields; only `label` differs. `model_id`, `api`, `role`, `system_prompt_path`, `max_tokens`, `timeout`, `max_retries`, `backoff_base`, `extra_body`, `secondary_api` and `secondary_model_id` all match.

**A correction to the standing record.** The memory note `project_model_panel_config.md` lists "context budgets (60K vs 80K)" among the differentiation that survived the lapse. It did not. `CONTEXT_CHAR_BUDGET` in `bench/runner_core.py` reads 60000 for both seats. The correction is executed by `test_the_recorded_context_budget_claim_is_still_true`, so it cannot go stale in silence. A second prose figure should also be treated with care: the docstring of `bench/confer_maths_panel_2026-09-05.py` states that 5 of 8 differentiating dimensions survive and 3 do not. No script producing that count exists in the repository, so under `measured-rate-travels-with-its-script` it is a claim about evidence rather than evidence, and at least one of its 5 survivors, the context budget, does not survive.

**What does still differ, and it is why Arm C is not a null arm today.** The composed directive phenotype: 6035 characters for `Codex` against 7406 for `ChatGPT`, a delta of 1371 characters. The initial capability fingerprints differ, as do the `MODEL_SPECS` priors in `bench/runner_core.py`, where `tau` is 600 for `Codex` against 200 for `ChatGPT`.

**Weak form and strong form.** The weak form is runnable today and is what the shipped config describes: 2 seats differing in composed phenotype and in capability priors. That is a real contrast and a small one. The strong form is what D11 actually asks for: the `Codex` seat restored to `codex exec` so it carries OpenAI's own agent prompt and native tool loop, against `ChatGPT` bare. **Only the strong form tests operating-condition diversity as designed, and it needs a change to `bench/experiment_11_orchestrator.py`, which this design does not own and has not made.** The exact change is in the shared-module section below. Until it lands, `d11_seat_contrast_diversity_arm.json` carries `_arm.launch_blocked = true`, and `test_launch_blocked_matches_the_measured_seat_state` asserts that the flag equals the negation of the measured precondition, so whoever restores the route must clear the flag in the same change and whoever clears the flag without restoring the route is caught.

## What is measured

**Primary, and it needs no answer key.** How many distinct criticals, keyed by code location, had their falsifier independently re-run by the runner and returned CONFIRMED. One integer per arm. This is the project's own truth criterion and it is why Exp 56 does not have to wait on item D10, the mechanically generated seeded catalogue. `location_keyed_convergence` is on and the target is a Python module with real symbols, so the location key separates 2 distinct defects in one function from 2 restatements of 1.

**Reported separately and never added to the primary.** CORROBORATED. It is attestation rather than demonstration, and in Arm A it is worse than that: see confound 5.

**Secondary.** Rounds to terminal verdict; `gamma_critical` at the verdict; HIL escalations; irreducible queue size at halt or convergence; wall clock; paid dispatch count actually incurred.

## What would refute the diversity claim

The claim under test is that a multi-vendor panel confirms defects a single model with tools does not.

**Decisive refutation.** Arm B confirms no more distinct located defects than Arm A, **and** Arm B's set of confirmed locations is a subset of Arm A's. The subset condition carries the weight. At n = 1 run per arm a higher count on its own is not separable from run-to-run noise, but "the panel found nothing the single model missed" is a statement about sets rather than about counts, and it does not need a variance estimate.

**Economic refutation, weaker but decision-relevant.** Arm B's confirmed defects per paid dispatch do not exceed Arm A's. Arm A's paid dispatch count is 0, so any positive result for Arm A wins this comparison outright. That is a fact about the subscription rather than about the science, and the note says so rather than hiding behind a defects-per-dispatch figure.

**What Arm C decides.** If Arm C resembles Arm B, the benefit tracks seat count and operating-condition variety rather than vendor diversity, and the multi-vendor architecture is not what is buying the result. If Arm C resembles Arm A, the benefit tracks vendors and the diversity claim survives its first real control.

**What would confirm nothing either way.** A halt on `HALTED_IRREDUCIBLE_QUEUE_ALARM` in some arms and not others, a seat producing no parseable output for 2 consecutive rounds, or a non-convergence. Each of those is a mechanical outcome, is reported as one, and does not demote `gamma`.

## What is held constant

Every key in the 3 configuration files except `models` and `experiment_name` is byte-identical, and `test_every_non_panel_key_is_identical_across_the_three_arms` asserts that by comparison rather than by intention. That covers the target, the round budget, the wall-clock cap, the convergence thresholds, the directive sections, the target-freezing, and every mechanism switch.

Four of those switches are worth naming because they are declared deltas from the arc's house style.

**`immune_memory_enabled` is false in all 3 arms.** Immune memory persists findings across runs. Left on, whichever arm runs second inherits the first arm's findings and the experiment measures run order. This is the one cross-arm contamination path the design closes outright.

**`routing_enabled` is false in all 3 arms.** `_apply_routing` builds its ladder as `models = [mc.label for mc in exp_config.models]` and passes that to `route()` as the available models. That list is the orchestrator's full roster of 5 seats and is never intersected with the declared panel. The ladder then excludes the finding's own source model, so in Arm A the ladder is exactly the 4 vendors the arm exists to do without. Measured by executing the real ladder builder: `rank_falsifier_writers(['CC2'], exclude=['CC2'])` returns 0 rungs, and `rank_falsifier_writers` over the full roster with the same exclusion returns 4.

**`post_convergence_sweep_rounds` is 0 in all 3 arms.** Same defect class. `_post_convergence_sweep` iterates `for mc in exp_config.models` with no filter. Measured by driving the real sweep with a stub in place of `dispatch_to_model`: with 1 declared seat it dispatches to seats the configuration never declared.

**`merge_arbitration_enabled` is false in all 3 arms, and this one is a delta from every configuration from Exp 40 to Exp 55, all of which set it true.** Third instance of the same class: `run_experiment` arms the arbitration context with `"panel": list(exp_config.models)`. It is also inert by design, because the merge path was closed by the no-voting ruling of 2026-08-19 and returns KEEP_DISTINCT whichever way the arbitration votes, so switching it off costs nothing and closes a leak.

The rule those four apply is worth stating so it can be attacked. **A multi-seat mechanism that degenerates gracefully in Arm A stays on, because degeneration is part of the treatment. A multi-seat mechanism that silently re-dispatches the other vendors is off, because it is not a treatment, it is a leak.** Section 18 stays on under that rule even though its text asks a lone seat to diverge from seats that are not there.

## Cost, in paid dispatches

Derived from the configuration files by `paid_review_dispatch_bound` in the test file, so the arithmetic travels with code that reproduces it. The bound is paid seats times `max_rounds` times 2 for the in-round re-ask, plus 1 connectivity probe per paid seat.

| arm | paid seats | bound on billed review dispatches |
|---|---|---|
| A | 0 | **0** |
| B | 4 | **68** |
| C | 2 | **34** |
| total | | **102** |

`CC2` bills nothing per dispatch on the Max subscription; `Codex`, `ChatGPT` and `Gemini` bill through OpenRouter and `DeepSeek` bills direct.

**This is a bound on the review path, not a total.** It counts review dispatches and the preflight probe. It does not count tool-loop completions inside a single dispatch, falsifier-gate re-asks, or any decomposed-dispatch fallback, all of which add tokens and some of which add calls. The one that could move the figure materially is the decomposed fallback on a restored `codex exec` seat in Arm C, which is the same 45-to-80-minute-per-round behaviour that caused the route to be abandoned in the first place. **A currency figure is not offered.** `bench/FINANCIAL_LEDGER.md` was last updated in the Phase 2 era and its totals do not describe present-day per-token pricing. [VERIFY:current] Converting 102 dispatches to a pound figure needs current OpenRouter and DeepSeek rates and a token estimate per dispatch, and neither exists in the repository today.

## Confounds, including the ones that cannot be removed

**1. Seat count is confounded with vendor diversity, and 3 arms cannot separate them.** Arm A has 1 seat, Arm C has 2, Arm B has 5. A difference between Arm A and Arm B could be vendors or could be arithmetic. Arm C narrows it because its 2 seats share weights, but the clean separation needs a fourth arm that this design does not build: 2 seats on identical weights **and** identical operating conditions, a duplicate-seat control. Without it, an Arm C result between Arm A and Arm B is consistent with both explanations. Building it needs a second `ModelConfig` for the same seat, which is a change to `bench/experiment_11_orchestrator.py`, and it costs a further 34 paid dispatches on the same bound. **This is the sharpest open question in the design and it is a founder decision.**

**2. Arm A holds richer tools than any individual seat in Arm B or Arm C.** `CC2` dispatches through the claude CLI with native shell access; the OpenRouter and DeepSeek routes receive the `execute_python` function-call loop only. So "one model with agents" is genuinely the strongest single-model configuration and not a like-for-like seat. This is deliberate and it biases toward the rival hypothesis. It cannot be removed without either handicapping Arm A or giving every seat a shell, and the second of those is a change to the dispatch layer.

**3. The cost comparison is degenerate.** Arm A's paid dispatch count is 0, so defects per paid dispatch is a division by zero rather than a ratio. Cost is therefore reported in dispatches and wall clock. Any statement of the form "Arm A is cheaper per finding" is true by subscription accounting and says nothing about the instrument.

**4. Section 18 is vacuous in Arm A.** It asks a seat to diverge from the other seats and there are none. Held on rather than off, because what Exp 56 varies is panel composition, and a lone seat having nobody to diverge from is part of that variation. Unremovable.

**5. The confirmation quorum degenerates at panel size 1, and this one is a live defect rather than a design choice.** `_update_finding_statuses` computes the external panel size as `len(set(cfg.models) - {source_model})` and then `required = min(2, external_panel_size)` for severity at or above 0.7. With 1 declared seat that is `min(2, 0) = 0`, and `independent_count >= 0` holds with no independent confirmation whatever. Measured by running the real status updater on a real registry: a lone critical raised by the only seat is promoted to CORROBORATED in the 1-seat arm and stays OPEN in the 5-seat panel. The comment 2 lines above the arithmetic states the intended rule as *"Floor: at least 1 independent external confirmation (source excluded)"*, so the code disagrees with its own docstring. It has never fired because every configuration from Exp 40 to Exp 55 declared 5 seats. **It is why the primary metric admits falsifier-gate CONFIRMED only.** The repair is in the shared-module section and is not applied here.

**6. The arm configurations and this note sit where a shell-bearing seat can read them.** `panel_cwd` is unset, which matches the runner's own convention for code targets, because a falsifier needs the repository. So a seat can in principle read `bench/exp56_configs/` and learn which arm it is in and what the hypothesis is, which is the anchoring confound this project has documented. The exposure is identical in all 3 arms so it cannot bias the contrast in a known direction, but the direction of any effect is unknown rather than absent. Closing it needs `panel_cwd` set to a staged directory, which in turn trips the runner's vault gate and needs the founder's passphrase to seal the plaintext keys in `../CDSFL_experiment_keys/`, and it would also cost the panel the repository browsing that Exp 42 had. Recorded as open rather than closed.

**7. n = 1 run per arm.** There is no within-arm variance estimate, so a difference of a few findings is not separable from run-to-run noise. This is the reason the decisive refutation is stated as a subset condition rather than as a comparison of totals. Three runs per arm would fix it at 3 times the cost and is a founder decision.

**8. The absorber between the falsifier gate and the HIL queue is absent in every arm, and it is absent for different reasons.** In Arm A the routing ladder genuinely has nowhere to climb, which is the treatment. In Arms B and C it is switched off to stop the Arm A leak, which is an instrument compromise. So escalations accumulate in all 3 arms and `max_irreducible_queue` sits at the code default of 2. A halt on the queue alarm is therefore a likely and reportable outcome. **The alarm is left at its default deliberately**, because the record contains a founder ruling that raising it to 8 and then 30 on 2026-08-01 was wrong and was reverted. One fallback is pre-registered here and applies to all 3 arms identically or not at all: if every arm halts on the queue alarm before `earliest_stop_round`, all 3 may be re-run once with `max_irreducible_queue` raised to 8, and both attempts reported. Raising it for one arm after seeing results is tuning and is not permitted.

## The target

`bench/cdsfl_registry/engine.py`, 591 lines, the PolicyEngine facade. It has never been a target in any configuration in the repository, so no prior findings against it exist anywhere for a seat to read. It sits in the same package as Exp 42's target, `bench/cdsfl_registry/composer.py`, which is the best-characterised code run in the archive and gives a prior for defect density and falsifier confirm behaviour. It is not on the runner's own decision path at run time, so a seat reviewing it is not reviewing the runner code that adjudicates its own findings. It is a Python module, which matters: the falsifier gate reaches a code target by import, and imports resolve through PYTHONPATH regardless of working directory, so the truth criterion is at its strongest here and at its weakest on prose. The target is frozen: `apply_fixes_back_enabled` is false and the runner hashes the target every round.

## How to launch, once the founder rules

One command per arm, using the standing detached-launch directive so the run survives a host restart. Each configuration carries its own launch line in its `_launch` key, and `test_the_launch_line_names_this_config` asserts the line names the file it sits in.

```
bash bench/detached_launch.sh bench/exp56_configs/d9_single_model_with_agents.json bench/logs/exp56_d9_single_model_with_agents.log
bash bench/detached_launch.sh bench/exp56_configs/d9_multi_model_panel.json bench/logs/exp56_d9_multi_model_panel.log
bash bench/detached_launch.sh bench/exp56_configs/d11_seat_contrast_diversity_arm.json bench/logs/exp56_d11_seat_contrast.log
```

`bench/detached_launch.sh` already routes through `bench/launch_exp42.py`, which resolves any path containing a separator, so no new launcher is needed and none was written. Recompute every figure in this note with `python3 -m pytest bench/tests/test_d9_d11_configs_valid_2026-09-05.py -q --netguard-strict`.

## Shared-module changes this design needs and did not make

These are in files this work does not own. Each is described precisely enough to apply and each has been checked by execution rather than by reading.

**S1. Restore the seat contrast, and it is required before Arm C tests what D11 asks.** In `bench/experiment_11_orchestrator.py`, `load_default_config()`, the `ModelConfig` labelled `Codex`: set `api="codex_exec"` and `model_id="gpt-5.5"`, and set `secondary_api="openrouter"` with `secondary_model_id="openai/gpt-5.5"` so the seat keeps a fallback and no seat misses a round. That is the 2026-04-02 change of `556e0af` inverted, with the reliability escape kept as the secondary route rather than dropped. The cost is the cost that caused the original change: `codex exec` has no system-prompt flag, so CDSFL travels in the prompt body, and the route previously drove a 45-to-80-minute-per-round decomposed fallback. `wall_clock_cap_s` is set to 21600 in all 3 arms to give it room. Whoever applies this must also set `_arm.launch_blocked` to false in `d11_seat_contrast_diversity_arm.json`, and the test file fails if the two disagree.

**S2. Floor the confirmation quorum at 1, which is what its own comment says it does.** In `bench/reference_runner_v3.py`, `_update_finding_statuses`, change `required = min(2, external_panel_size) if sev >= 0.7 else 1` to `required = max(1, min(2, external_panel_size)) if sev >= 0.7 else 1`. Verified by executing both forms against the real registry at panel sizes 1, 2 and 5: the 1-seat case changes from CORROBORATED to OPEN, and the 2-seat and 5-seat cases are unchanged. Every completed run in the archive declared 5 seats, so no archived result moves. This is a defect independent of Exp 56 and would be worth fixing whether or not these arms ever run.

**S3. Intersect the panel list at the 3 sites that read the full roster.** In `bench/reference_runner_v3.py`: `_apply_routing` builds `models = [mc.label for mc in exp_config.models]`; `_post_convergence_sweep` iterates `for mc in exp_config.models`; and `run_experiment` populates the merge-arbitration context with `"panel": list(exp_config.models)`. Each should be filtered by `set(cfg.models)` the way `_dispatch_round_star` already filters its `eligible` list. This is the eighth occurrence of the panel-list drop class and the first that is not in a launcher. Applying it would let Exp 56 run with the routing ladder and the post-convergence sweep enabled in all 3 arms, which is the more interesting comparison, because the ladder is a genuine multi-model capability and Arm A would correctly have none. **It changes behaviour for no archived run**, since every archived configuration declared all 5 seats and the intersection is then the identity. It is nonetheless a change to the runner and belongs to whoever owns that file.

**S4. Correct the memory note.** `project_model_panel_config.md` records "context budgets (60K vs 80K)" as surviving differentiation between the two seats. Measured: both read 60000 in `CONTEXT_CHAR_BUDGET`. The surviving differentiation is the composed phenotype, the capability fingerprints and the `MODEL_SPECS` priors.

## Open questions for the founder

1. **The duplicate-seat control.** Confound 1 cannot be removed by 3 arms. Building it costs a fourth `ModelConfig` and about 34 more paid dispatches. Without it, an intermediate Arm C result is ambiguous between seat count and vendor identity.
2. **Weak form or strong form for Arm C.** Running the weak form today tests a 1371-character phenotype delta. Running the strong form needs S1 and reinstates a known reliability risk. The recommendation is the strong form, because the weak form does not test what D11 names.
3. **Whether S3 lands before the run.** With it, all 3 arms can run with the ladder and the sweep on and the comparison covers the full instrument. Without it, they run with 3 mechanisms off and the comparison covers the review path only. The recommendation is to land S3 first; it is behaviour-preserving for every archived configuration.
4. **The queue alarm.** Confound 8. The pre-registered fallback is written into all 3 configurations and needs sign-off before it is used, not after.
5. **n = 1 or n = 3 per arm.** At n = 1 only the subset condition is decisive.

## How to read the claims in this note

An unlabelled claim is a plain one, not an unchecked one. Figures marked **MEASURED** were obtained by executing code, and the extent is named beside them. Figures marked **DERIVED** follow from the configuration files by arithmetic. The paid dispatch bounds of 0, 68, 34 and 102 are DERIVED. The seat-comparison figures — 11 of 12 identical `ModelConfig` fields, 60000 characters of context budget on both seats, 6035 against 7406 characters of composed phenotype, and the CORROBORATED promotion at panel size 1 — are MEASURED, each by one execution against the live configuration at HEAD on 2026-09-05, and each re-measured by the test file rather than transcribed.

---

Written under CDSFL note standard v1.7 (26 August 2026).
