# The instrument inventory: every component that emits a number or a verdict

**22 August 2026. Reproduce: `python3 scripts/instrument_inventory.py`.**

Every defect found in the week to 22 August was found by a measurement nobody had
ever run. Each component had been built, switched on, and used to produce results
without anyone checking it did what it said. **That is not an endless problem. It
is a finite backlog nobody had enumerated.** This is the enumeration.

**COMMISSIONED** means a test exists that exercises the component with a
*known-good* and a *known-bad* input and asserts it answers differently. That is
the falsification principle applied to the instrument rather than to the artefact.

**34 instruments, not the "seventeen-ish" estimated before counting.**

## The inventory caught its own detector lying

The heuristic scored **I14, the falsifier gate**, as commissioned. It is not:
`reverify_falsifier("print('FALSIFIED')")` returns CONFIRMED. It also scored
**I33**, the survived-falsification ledger, as commissioned; it has a full test
suite and nothing calls it.

Direct measurements therefore override the heuristic, and the script reports its
own error rate against them: **9 rows measured, 3 disagreements (I08, I14, I26).** Refreshed from the generator 2026-09-01: the figure read 5 rows for ten days while four further rows were measured, three of them re-measured to COMMISSIONED on 2026-08-30. The remaining "yes" rows are **unverified, not reassurance**. Founder
ruling 2026-08-22: the panel confirms or refutes each row with tools.

| id | instrument | emits | live flag | tests naming it | commissioning candidate | panel |
|---|---|---|---|---|---|---|
| I01 | Duane/Crow-AMSAA gamma estimator | number | - | 6 | YES — test_vacuous_gamma_curve.py | |
| I02 | Two-sided gamma gate | verdict | - | 0 | **NO** | |
| I03 | Churn detector (rho) | number | - | 1 | YES — test_per_model_rho_itc.py | |
| I04 | State-convergence check | verdict | - | 0 | **NO** | |
| I05 | Gamma-alt convergence | verdict | - | 8 | YES — test_vacuous_gamma_curve.py | |
| I06 | Hardened convergence | verdict | - | 1 | YES — test_hardened_gate.py | |
| I07 | Stall convergence | verdict | - | 0 | **NO** | |
| I08 | Budget extension | verdict | - | 0 | **NO** | |
| I09 | Attention metrics | numbers | - | 1 | YES — test_fingerprint_attention_metrics.py | |
| I10 | S_k fix efficacy | number | on in 19/19 | 3 | YES — test_immune_memory_consumption.py | |
| I11 | S_k admissibility threshold | verdict | on in 19/19 | 3 | YES — test_immune_memory_consumption.py | |
| I12 | R_k three-phase model | number | - | 5 | YES — test_channel_boundary.py | |
| I13 | R_k eta channel | number | - | 3 | YES — test_channel_boundary.py | |
| I14 | THE FALSIFIER GATE | verdict | on in 19/19 | 6 | **NO** | |
| I15 | Verdict reader | verdict | - | 13 | YES — test_discrimination_control.py | |
| I16 | Discrimination control | verdict | (presence-gated) | 2 | YES — MEASURED: MEASURED 2026-08-22: run against 372 archived falsifiers with a tripwire, a baseline requirement and a determinism check; it separated 132 discriminating from 131 non-discriminating. | |
| I17 | Routing/escalation ladder | routing decision | on in 17/19 | 3 | YES — test_exp43_fixes.py | |
| I18 | Status transitions | status | - | 4 | YES — test_confer_verification.py | |
| I19 | Similarity function (3 tiers) | number+verdict | - | 3 | YES — test_hierarchical_novelty.py | |
| I20 | Outcome agreement (tier 3) | verdict | - | 2 | YES — test_anchorless_outcome_guard.py | |
| I21 | Location keying | series | - | 2 | YES — test_premise_exclusion.py | |
| I22 | Divergence measure | number | - | 16 | YES — test_ouroboros_query_builder.py | |
| I23 | Diversity measure | number | - | 3 | YES — test_diversity_metric.py | |
| I24 | Fix complexity (nu), shadow | number | (shadow) | 1 | YES — test_fix_complexity.py | |
| I25 | Immune memory prior | number | - | 12 | YES — test_ouroboros_query_builder.py | |
| I26 | Load balancer  [SHELVED 2026-08-22] | allocation | (shelved) | 0 | **NO** | |
| I27 | Shadow stage-6 | number | (shadow) | 3 | YES — test_ouroboros_loop_close.py | |
| I28 | Near-duplicate feedback into the prompt | prompt text | - | 13 | YES — test_feedback_channel.py | |
| I29 | Claim-type classifier | class | - | 2 | YES — test_immune_agents.py | |
| I30 | Immune removal decision | verdict | - | 37 | YES — test_ouroboros_query_builder.py | |
| I31 | Health monitor | alarm | - | 16 | YES — test_discrimination_control.py | |
| I32 | Finding parser / description extractor | structured findings | - | 7 | YES — test_score_exam.py | |
| I33 | Survived-falsification ledger | positive record | (NOT WIRED) | 1 | **NO** | |
| I34 | Null-perturbation control | verdict | (offline script) | 0 | YES — MEASURED: MEASURED 2026-08-21: 397 findings, 360 fired, 0 moved on either an irrelevant comment or an unaccused function rename. | |

**30 of 34 instruments have a commissioning candidate. 4 do not.**

Refreshed from `scripts/instrument_inventory.py` on 2026-09-01. The document had read 27 and 7 since 22 August while the generator it names in its own reproduce line reported 30 and 4 — a header promising reproducibility, with no test that ran the script and compared. That test now exists: `bench/tests/test_derived_docs_match_their_generators_2026-09-01.py`.

Written under CDSFL note standard v1.4.
