# Instrument confirmation panel — 2026-08-28

Two reviewers, cc2 (opus) and fable, each in a throwaway git worktree, both on the Max plan and
therefore free. The brief asked them to test the instrument inventory's claim that 32 of its 34
rows are commissioned — that is, that a test would actually fail if the component silently stopped
discriminating.

**Both refuted it independently.** CC2 scored 23 confirmed, 9 refuted at the named test, 2 refuted
outright. Fable found 5 to 6 genuinely uncommissioned rows plus 7 whose named test is the wrong file.

The verbatim responses follow. Nothing is summarised away.

---

## fable — 9,692 chars, 921 s

# Fable — Instrument inventory panel review

All 34 rows addressed. Method: run the named test green, apply a one-line break in the component (always toward the *plausible-default* failure, never a crash), rerun, revert, confirm the tree back to green. Every verdict below is a test run, not a reading.

## Table of rows examined

| Row | Component | Break applied (file : what) | Named test under break | Suite under break | VERDICT |
|---|---|---|---|---|---|
| I01 | Gamma estimator | `_estimate_gamma` → constant `0.5` | **FAILED** (4) | — | **COMMISSIONED** |
| I02/I05 | Two-sided gate | (a) streak check `all(n==0…)` → `True`; (b) `if gamma_critical < theta` → `if False` | (a) **FAILED**; (b) *passed* | (b) caught only by `test_two_sided_gate.py` | **COMMISSIONED** — but the named file covers only the streak side |
| I03 | Churn detector | (a) `churn` → `False`; (b) `rho_current` → constant `1.0` | (a) **FAILED** (4); (b) *passed* | (b) caught nowhere (only 1 file names rho) | **PARTIAL** — churn verdict commissioned; the emitted `rho_current` number is unpinned |
| I04 | State convergence | `if all(recent)` → `if True` | **FAILED** (2) | — | **COMMISSIONED** |
| I06 | Hardened gate | `zero_crit_ok` → `True` | **FAILED** (2) | — | **COMMISSIONED** |
| I07 | Stall convergence | static-window check → `if False` | **FAILED** (2) | — | **COMMISSIONED** |
| I08 | Budget extension | `if reasons:` → `if False:` (never extends) | *passed* (17/17) | only file naming it | **NOT COMMISSIONED** — tests pin callability + config-inertness only, by design (founder wants it removed). Consequence low: inert in every exp40+ config, and that inertness IS pinned |
| I09 | Attention metrics | whole function → constants | **FAILED** (11) | — | **COMMISSIONED** |
| I10 | S_k fix efficacy | `compute_sk` → always NO_SCORE | *passed* — named test converted break into **12 silent skips** | caught by `test_target_kind_and_no_score.py`, `test_prose_acceptance_stem.py` | **COMMISSIONED** — wrong attribution; skip-absorption in the named file is itself a defect |
| I11 | S_k admissibility | `return sk >= effective_threshold` → `return True` | *passed* (45) | **all 93 tests across all 3 files naming it passed** | **NOT COMMISSIONED** — flag live in 19/19; the Valley-of-Bad-Fixes gate could admit every fix silently |
| I12 | R_k three-phase | `compute_rk` → constant `0.5` | *passed* (25) | caught by `test_target_kind_and_no_score.py` (2) | **COMMISSIONED** — wrong attribution |
| I13 | R_k eta channel | `m_div * eta_int` → `eta_int` | **FAILED** (1) | — | **COMMISSIONED** |
| I14 | Falsifier gate | none needed — reran the measurement: `reverify_falsifier("print('FALSIFIED')")` → `CONFIRMED`, `"assert False, 'FALSIFIED'"` → `CONFIRMED` | — | — | **NOT COMMISSIONED — inventory's NO confirmed live** |
| I15 | Verdict reader | NOT-FALSIFIED guard regex → never matches (the exact 2026-07-27 bug) | *passed* (11) | **FAILED** in `test_verdict_reader_and_access.py` + `test_exp43_fixes.py` (2) | **COMMISSIONED** — wrong attribution |
| I16 | Discrimination control | corrected-verdict branch → always `DISC_PASSED` | **FAILED** (17) | — | **COMMISSIONED** |
| I17 | Routing ladder | enable-guard → always returns (routing never runs) | **FAILED** (2) | — | **COMMISSIONED** |
| I18 | Status transitions | line 2547 `challenges = []` (CHALLENGE votes silenced) | *passed* (13) | **all 156 tests in all 5 files naming `_update_finding_statuses` passed** | **NOT COMMISSIONED** for the CHALLENGE→CONTESTED path |
| I19 | Similarity | Jaccard → constant `0.0` | **FAILED** (3) | — | **COMMISSIONED** |
| I20 | Outcome agreement | → always `"SAME"` | **FAILED** (2) | — | **COMMISSIONED** |
| I21 | Location keying | dedup-by-location dropped | **FAILED** (4) | — | **COMMISSIONED** |
| I22 | Divergence measure | `eta_int_modulator` → constant `1.0` | *passed* (62) | **FAILED** (6) in recidivism/modulator tests | **COMMISSIONED** — wrong attribution |
| I23 | Diversity | → constant maximally-diverse dict | **FAILED** (7) | — | **COMMISSIONED** |
| I24 | Fix complexity | `blocks = []` (sees no fix) | **FAILED** (5) | — | **COMMISSIONED** |
| I25 | Memory prior | `pi_mem` → uninformative prior always (data ignored) | *passed* (62) | **FAILED** (14) in `test_dynamic_management.py` etc. | **COMMISSIONED** — wrong attribution |
| I26 | Load balancer | none — verified shelving: `get_allocation` has no caller in any runner (grep) | — | — | **NOT COMMISSIONED — inventory's NO confirmed** |
| I27 | Shadow stage-6 | `fail_fraction` → constant `0.5` | *passed* (21) | **all 37 tests in both files naming it passed** | **NOT COMMISSIONED** — shadow-only so low consequence, but heuristic wrong in the confident direction |
| I28 | Feedback channel | `build_feedback_sections` → `{}` | **FAILED** (8) | — | **COMMISSIONED** |
| I29 | Claim classifier | → constant UNCATEGORISED | **FAILED** (8) | — | **COMMISSIONED** |
| I30 | Immune removal | `helper_t_cell_synthesize` → all UNCERTAIN (never removes) | **FAILED** (5, in `test_immune_agents.py`) | — | **COMMISSIONED** — but the row's symbol `immune` is a substring grep; its "39 tests" count is noise |
| I31 | Health monitor | `regulatory_t_cell_check` → never alarms | named `test_discrimination_control.py` *passed* | **FAILED** (2) in `test_immune_agents.py` | **COMMISSIONED** — wrong attribution |
| I32 | Finding parser | drops every parsed finding | **FAILED** (1) | — | **COMMISSIONED** |
| I33 | Survival ledger | REFUTED added to the no-write branch | **FAILED** (25) | — | **COMMISSIONED** |
| I34 | Null-perturbation | `_perturb_unrelated_code` → `None` (never perturbs) | *passed* (2/2) | its only 2 tests pin dry-run/record discipline, not perturbation | **NOT COMMISSIONED by any test** — rests entirely on the one-off 2026-08-21 measurement |

## Where I differ from the brief

The brief's binary "32 yes rows" hides that the inventory has **two separable failure modes**, and the second is the bigger one:

1. **Genuinely uncommissioned verdict components: I11, I18, I08 (accepted-inert), I27, I34, plus I03's number output.** I11 and I18 are the two that matter. I11's admissibility gate is live in 19/19 configs and can be hardwired to always-admit with zero test failures. I18's CHALLENGE-silencing survives all 156 tests naming the function — a model's disagreement with a CONFIRMED finding would vanish, `contested` would undercount, and gate condition (c) would open early. That is convergence-corrupting and invisible.

2. **The named-test column is wrong in at least 7 rows where the verdict is right** (I02-gamma-side, I10, I12, I15, I22, I25, I31). The component is protected, but by a *different* file than the inventory names. That matters operationally: anyone triaging a regression from the inventory would run the wrong test and conclude safety. I10 is worst — its named test converts the break into 12 silent *skips*, which reads as green.

3. The heuristic's test-count column is substring noise for I30 ("immune", 39 alleged tests) and I31 ("health"). `_grep_tests` matches substrings; `_symbol_resolves` passes because the word trivially occurs. The calibration section's "5 rows measured, 2 disagreements" now becomes, on my measurement: **34 rows measured, 5–6 disagreements in the confident direction** (I08, I11, I18, I27, I34, arguably I03).

## Clean-run readiness — preconditions, not a yes/no

Not ready until:

1. **I14 is fixed or the falsifier gate is run with the discrimination control mandatory.** A falsifier that touches nothing still CONFIRMs (reproduced live this session). I16 works (17 failures under break) and is the existing countermeasure — it must be presence-*required* for critical CONFIRMs, not presence-gated.
2. **I18's CHALLENGE→CONTESTED path gets a commissioning test.** One test: CONFIRMED finding + later CHALLENGE → status CONTESTED. Currently nothing fails if that transition is deleted.
3. **I11 gets a discriminating test**: a (sk, s_star) pair below threshold must return `False`. One assertion; currently absent across 93 tests.
4. **I08 is either removed (founder's stated preference) or left as is** — its inertness is pinned; it does not block a run.
5. The inventory's named-test column is corrected for the 7 misattributed rows, and `_grep_tests` switched from substring to word-boundary matching — otherwise the instrument that measures instruments keeps issuing wrong pointers.
6. I34 and I27 are accepted as measurement-only/shadow respectively, or given one behavioural test each. Neither blocks a run.

## WHAT I COULD NOT CHECK AND WHY

- **I03's `rho_current`**: I showed no test pins it, but did not trace whether any *live report field* consumes it versus only `rho_avg` — so consequence is unquantified.
- **I30's full removal path in a live pipeline**: my break was at `helper_t_cell_synthesize`; downstream reconciliation (`v2_final`, line ~5946) could mask other synthesizer faults — not exercised.
- **End-to-end runner behaviour**: every verdict here is unit/component level in a disposable copy. No live experiment was run; nothing here says the runner *wires* these components correctly at run time (I33's wiring is tested; others I did not trace).
- **I16 against the 372-falsifier archive**: the 2026-08-22 measurement was not re-run (archive-scale, and the break-test already discriminated).

Exact breaks are one-liners recorded in the table; each applies with a single string replacement and reverts with `git checkout`. Working copy left green (only the auto-regenerated `instrument_inventory.json` modified).

One line for the record: it's 04:20 BST. If you're reading this live rather than at breakfast — this will keep.

---

## cc2 — 14,984 chars, 1008 s

All mutations reverted; the tree is clean. Here is what the tools said.

## Method

Mutation testing. For each row: run the test file the inventory names, insert one line at the top of the component that makes it return a plausible constant (the "silently stopped discriminating" failure this project keeps shipping), re-run, restore with `git checkout`. Harness and specs are in `_mut/` in the disposable copy. Verdict = did the **named** test file go red.

I prioritised the falsifier gate, the verdict reader and the six stopping/convergence components (I01–I08, I14–I17), because their silent failure writes a wrong convergence verdict into a run report and nothing downstream would contradict it. Everything else came after.

## Rows examined — 33 of 34 (I05 is the same function as I02)

| id | component | named test | break applied | result under break | VERDICT (named test) |
|---|---|---|---|---|---|
| I01 | `_estimate_gamma` | test_vacuous_gamma_curve | `return 0.5` | 7 failed | COMMISSIONED |
| I02/I05 | `_check_gamma_alt_convergence` | test_vacuous_gamma_curve | `return True, 'converged'` | 11 failed | COMMISSIONED |
| I03 | `_compute_rho` | test_per_model_rho_itc | `return 0.5, 0.5, False` | 4 failed | COMMISSIONED |
| I04 | `_check_state_convergence` | test_stopping_components_… | `return True, '…'` | 4 failed | COMMISSIONED |
| I06 | `_check_hardened_convergence` | test_hardened_gate | `return True, '…', {}` | 7 failed | COMMISSIONED |
| I07 | `_check_stall_convergence` | test_stopping_components_… | constant never-stalled dict | 2 failed | COMMISSIONED |
| **I08** | `_check_budget_extension` | test_stopping_components_… | `return False` **and** `return True` | **17 passed both ways** | **NOT COMMISSIONED** |
| I09 | `_compute_attention_metrics` | test_fingerprint_attention_metrics | `return fp` uncomputed | 22 failed | COMMISSIONED |
| **I10** | `compute_sk` | test_immune_memory_consumption | `fix_text = ''` | **33 passed, 12 skipped, rc=0** | **NOT COMMISSIONED** (see below) |
| **I11** | `check_sk_threshold` | test_immune_memory_consumption | `return True, 0.0` | 45 passed | **NOT COMMISSIONED** by named file; caught by test_immune_memory_evaluation (4 failed) |
| **I12** | `compute_rk` | test_channel_boundary | `return 0.5` | 25 passed | **NOT COMMISSIONED** by named file; caught by test_ouroboros_loop_close (1 failed) |
| I13 | `compute_rk_with_eta_channel` | test_channel_boundary | `return 0.5` | 20 failed | COMMISSIONED |
| I14 | `apply_falsifier_verdicts` | test_equipment_error_not_terminal | `return` (gate is a no-op) | 7 failed | COMMISSIONED **as wiring only** — see below |
| I15 | `reverify_falsifier` | test_equipment_error_not_terminal | `return 'CONFIRMED'` | 5 failed | COMMISSIONED |
| I16 | `run_discrimination_control` | test_discrimination_control | constant `DISCRIMINATES` record | 28 failed | COMMISSIONED |
| I17 | `_apply_routing` | test_equipment_error_not_terminal | `return` | 2 failed | COMMISSIONED |
| **I18** | `_update_finding_statuses` | test_confer_verification | `return` | 13 passed | **NOT COMMISSIONED** by named file; caught by test_status_vocabulary_catalogue (4 failed) and test_discrimination_control (1 failed) |
| I19 | `signature_similarity` | test_hierarchical_novelty | `return 1.0` | 4 failed | COMMISSIONED |
| I20 | `outcome_agreement` | test_anchorless_outcome_guard | `return 'SAME'` | 2 failed | COMMISSIONED |
| I21 | `location_only_series` | test_premise_exclusion | `return [0]*max_round` | 4 failed | COMMISSIONED |
| **I22** | `eta_int_modulator` | test_ouroboros_query_builder | `return 1.0` | 62 passed | **NOT COMMISSIONED** by named file; caught by test_divergence_directive group (6 failed) |
| I23 | `_jaccard` (diversity) | test_diversity_metric | `return 0.5` | 5 failed | COMMISSIONED |
| I24 | `fix_complexity_features` | test_fix_complexity | `fix_text = ''` | 5 failed | COMMISSIONED |
| **I25** | `blended_prior` | test_ouroboros_query_builder | `return pi_base` | 62 passed | **NOT COMMISSIONED** by named file; caught by test_immune_memory_evaluation (3 failed) |
| I26 | load balancer (shelved) | test_load_balancer_shelved | added a real `LoadBalancer(cfg)` call to `reference_runner_v2.py` | 1 failed | shelving claim COMMISSIONED; component itself still NOT |
| I27 | `_estimate_h_ratio` | test_shadow_stage6_calibrator | `return 0.5` | 1 failed | COMMISSIONED |
| I28 | `_render_single_record` | test_feedback_channel | `return ''` | 5 failed | COMMISSIONED |
| I29 | `_classify_claim_v2` | test_immune_agents | constant class | 5 failed | COMMISSIONED |
| **I30** | `dendritic_cell_triage` | test_ouroboros_query_builder | `findings = []` | 62 passed | **NOT COMMISSIONED** by named file; caught by test_immune_agents (5 failed) |
| **I31** | `regulatory_t_v2` | test_discrimination_control | `max_rejection_rate = 1.01` (alarm can never fire) | 47 passed | **NOT COMMISSIONED** by named file; caught by test_rt_v2_bias_windowing group (6 failed) |
| I32 | `parse_findings` | test_score_exam | `return []` | 1 failed | COMMISSIONED |
| I33 | `SurvivedFalsificationLedger.record` | test_survival_ledger_commissioned_… | `return` | 3 failed | COMMISSIONED |
| **I34** | `_perturb_unrelated_code` | test_null_perturbation_control | `return None` (never perturbs) | 2 passed | **NOT COMMISSIONED — anywhere** |

**Score: 23 confirmed, 9 refuted at the named test, 2 refuted outright.** The heuristic's 32/34 does not survive contact.

## The four things that matter

**1. I10's test file switches itself off when I10 breaks.** `test_immune_memory_consumption.py:83` computes its own skip guard by *calling the component under test*:

```python
_PIPELINE_LIVE = compute_sk(GOOD_FIX, TARGET_SRC, "toy_target.py",
                            baseline=_BASELINE).tristate == "ADMISSIBLE"
_needs_pipeline = pytest.mark.skipif(not _PIPELINE_LIVE, ...)
```

Baseline: 45 passed, 0 skipped. With `compute_sk` blinded: **33 passed, 12 skipped, exit code 0.** Break the component and its tests stop running rather than failing. This is the house failure mode moved into the test layer, and it is the named evidence for both I10 and I11. I scanned the rest of the suite: this is the only `skipif` whose condition calls project logic under test — the other 18 are file-presence or platform guards.

**2. I08 is inert in both directions.** `return False` and `return True` both leave its only test at 17 passed. That test asserts it is callable, returns a 2-tuple whose first element is a bool, and that no modern config permits an extension. Those are real claims, honestly labelled in the file — but the file is named `test_stopping_components_commissioned_2026-08-25.py`, and for I08 it does not commission. The founder's own note in it says the mechanism should probably be removed. Nothing here would notice if it were.

**3. I14's measured defect reproduces, and my mutation was too coarse to see it.** A no-op gate is caught. Target-independence is not. Direct run:

```
reverify_falsifier("print('FALSIFIED')")   → CONFIRMED
reverify_falsifier("assert False, 'FALSIFIED'") → CONFIRMED
```

End-to-end through the gate, with a critical finding whose falsifier never touches its target:

```
status: CONFIRMED   falsifier_verdict: CONFIRMED   verified: True
escalated: False    discrimination: None   (tally: no_control=1)
```

What the heuristic mistook: the gate *is* well tested as a **token reader**, and `test_falsifier_gate.py` explicitly pins `("print('FALSIFIED')", "CONFIRMED")` as correct. So the property "the falsifier must depend on its target" is not merely untested — the suite currently encodes its absence as intended behaviour. The mechanism that does check dependence, the discrimination control (I16), is **presence-gated**: `reference_runner_v2.py:3666` returns `DISC_ABSENT` when `entry["corrected_copy"]` is empty, and a corrected copy is something the model has to supply. No corrected copy, no check, and the gate confirms.

Scale, from the committed archive `discrimination_control_archive.json` (372 rows): route B replays each falsifier against every historical version of its target. **346 of 372 fired on every version and were never quiet.** A falsifier that genuinely tests a defect should be quiet on at least one version. It is possible for a long-lived defect to be present in all versions, so this is not proof — but 93% is not a rate a healthy population produces.

**4. I34 gives a clean bill of health to a falsifier that never reads its target.** I ran the control on one real archived item with the code swapped for `print('FALSIFIED')`:

```
run_one → ('CONFIRMED', 'CONFIRMED', 'CONFIRMED', 'build_interaction_pattern')
```

Zero flips — a pass. So the measured "0 of 360 moved" is exactly the result a corpus of target-independent falsifiers would produce. The measurement itself reproduces off the committed record (397 rows, 360 fired, 0 comment flips, 0 code flips ✓), with one detail the row omits: **56 of the 360 had no unrelated definition to rename**, so only 304 actually received the meaningful perturbation. And the machinery has no commissioning test at all — `test_null_perturbation_control.py` monkeypatches `run_one` wholesale and tests the CLI's file-overwrite safety instead. Under my mutation the counter `(no unrelated def available to rename)` moves 0 → 6, so the failure is visible in the printed output. Visible, but unguarded.

## Where I disagree with the brief

The brief says I26's row is a heuristic error. I think it is the strongest row in the file. The component is genuinely not commissioned — `LoadBalancer.allocate` warns on infeasibility and returns the allocation anyway (`_load_balancer.py:425–439`), so the "impossible allocation as success" claim holds. But the *shelving* claim is properly commissioned: I added a live `LoadBalancer(cfg)` call to `reference_runner_v2.py` and `test_the_runner_does_not_call_the_load_balancer` went red. It is an AST-based source assertion, which is the category the brief tells me to distrust — correctly here, because the claim being pinned ("the runner does not call it") *is* structural, and the file ships its own negative control. That is how a source-text assertion should be built.

## A defect in the inventory itself

I ran an AST check over all 34 rows, asking whether the row's symbol is a defined name (function, class or module-level assignment) in the file the row names.

**8 of 34 are not:** I22 `_divergence`, I23 `_diversity`, I25 `_memory`, I26 `_load_balancer`, I28 `_feedback`, I30 `immune`, I31 `health`, I34 `null_perturbation`.

These are module names and bare substrings. `_symbol_resolves` — added 2026-08-25 for exactly this class — passes them because it does `symbol not in file_text`, and a module's name usually appears somewhere in its own source (in a docstring, a log string, a relative import). The guard against reporting a lookup failure as evidence is itself reporting a lookup failure as evidence. `immune` and `health` are worse: as substrings they match any test file containing the word, which is where I30's "39 tests" and I31's "17 tests" come from.

The consequence is measurable rather than theoretical. Of the 8 mis-symbolled rows, 5 (I22, I25, I30, I31, I34) had their named evidence file fail to catch the break. Six of my nine "named file does not commission" results fall in this set. The evidence column points a reader at the wrong file, in the reassuring direction.

Separately: **I02 and I05 are the same function** (`_check_gamma_alt_convergence`) counted as two instruments. The denominator 34 contains 33 distinct components.

## Clean-run readiness — preconditions, not a yes

Not ready. What would have to be true:

1. **The falsifier gate requires target-dependence before CONFIRMED.** Today a model that emits `print('FALSIFIED')` gets a verified critical. Every "tools decide, not votes" number a clean run produces is uninterpretable until this closes. Minimum bar: no CONFIRMED without a discrimination result, i.e. the control stops being presence-gated on a model-supplied corrected copy. `test_falsifier_gate.py:26` needs to change with it — it currently pins the defect as intended.
2. **Route B's 346/372 is explained.** Either those falsifiers are target-independent, in which case the archive's confirmations are worth less than their labels, or there is an innocent explanation. Until that is settled, prior-run numbers cannot be used as baselines.
3. **`test_immune_memory_consumption.py`'s skip guard stops calling the component under test.** A green suite that quietly dropped 12 tests is worse than a red one. Any run that reports "suite green" should also report the skip count against a pinned expected value.
4. **I08 is either commissioned or deleted.** Founder's own note leans delete. Either is fine; leaving it inert and labelled "commissioned" is not.
5. **The inventory's 8 mis-symbolled rows get real symbols, and `_symbol_resolves` becomes an AST name lookup rather than a substring test.** Otherwise the next panel re-derives this from scratch.
6. **I34 gets a commissioning test** that fails when the perturbation stops perturbing — assert `NO_UNRELATED_DEF` count against a pinned value, since the counter already moves.
7. **The evidence column is regenerated** after 5 and 6, because 9 of the rows I checked currently name a file that does not do the job.

None of 1–7 requires new architecture. 3, 4, 6 are hours. 1 and 2 are the real work.

## What I could not check, and why

- **The 12 skipped tests in `test_immune_memory_consumption.py` under an unbroken `compute_sk`.** They pass at baseline, so their content is untested by me; I only established that breaking the component removes them from the run.
- **Whether route B's 346/372 means what I think.** I read the classifier (`discrimination_control_archive.py:309–322`) and the tally, but I did not re-run the archive sweep or hand-audit a sample of the 346. The alternative explanation — defects present across the whole file history — is not excluded by anything I ran.
- **I16 end-to-end in a live run.** I commissioned `run_discrimination_control` by mutation and read its call site, but I never observed it fire on a real round, because that needs a model-supplied corrected copy and this session made no dispatches.
- **I05 as a distinct instrument.** It shares a symbol with I02, so there is nothing separate to break.
- **Whether my mutations are the *worst* break for each row.** A component can be commissioned against "returns a constant" and still be uncommissioned against a subtler wrong answer. Every COMMISSIONED verdict above means "survives one specific coarse break", not "fully commissioned". I13 and I19 in particular have numeric ranges I did not probe near their boundaries.
- **Anything requiring the model panel.** No dispatch, no network, offline suite throughout.

One more thing, and it is not about the code: it is 04:00. Nothing above changes if it is read at nine.

---

## Brief

```
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

Do not pad. Every word is read, so make every word carry weight.

```