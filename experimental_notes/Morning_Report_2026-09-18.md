# Morning report, 18 September 2026

2026-09-18, 02:02 BST, Europe/London. Markdown companion to `~/Desktop/CDSFL_tts/Morning_Report_2026-09-18.txt`.

## Summary

The founder's sequence is recorded and nothing in the codebase blocks it: Zenodo key rotation, then the study of the revised mathematical model and the other resources, then a panel review of the model, then a simulated run if it checks out, then back to the runway.

The revised model was read and checked overnight at a first-impressions level. **It does not demote the decay curve and it does not demote gamma.** It states that the original residual-risk recursion is recovered exactly as a special case, and that claim was verified 3 independent ways. It also names an error in `docs/MATHEMATICAL_APPENDIX.md`, and the error is real and still present.

5 open items were classified with `scripts/blocker_triage.py`, the founder's own criterion as code. All 5 returned PARK.

## The revised model, after a first check

`CDSFL_Mathematical_Review_Suite_2026-09-10` verifies its own integrity against a SHA-256 manifest: **PASS on all 41 files**. Its 3 check scripts run clean on exact `Fraction` arithmetic, import only the standard library, contact nothing, and write nothing without a `--report` path. The package states that adoption is undecided, and reports one of its own weaknesses: `free_parameters_can_fit_any_desired_risk: true`.

The core is a Bayesian update on flaw risk followed by a 2-state action with net removal `s` and introduction `b`. Every property below was checked by EXECUTING the package's own `update()`, not by reading it.

| Property | SymPy | z3 | Wolfram | Executed |
|---|---|---|---|---|
| `risk_after = (1-s)z + b(1-z)` | holds | — | holds | 7,776 exact cases, 0 mismatches |
| no action returns the prior exactly | holds | — | holds | 0 violations |
| `risk_after` stays in [0, 1] | — | **unsat** | `Reduce` returns True | 0 violations |
| more removal never raises risk | — | **unsat** | — | — |
| collapses to the original recursion | holds | — | holds | 7-step decay, 0 mismatches |

The 3rd and 4th are proved over the whole valid domain rather than sampled. The 5th is the one that matters most: with `s = b = 0` and a clean review of sensitivity `p`, the revised form becomes `R(1-p)/(1-pR)`, the original CDSFL recursion, and repeated clean reviews multiply the odds by `(1-p)` each time. Wolfram confirms the limit tends to 0 under repeated capable review. **The decay curve survives, derived rather than assumed.**

What the revision replaces is narrow: the repair interpretation of the 3-phase extension, the novelty-validity coupling, and some universal readings of decay. Coverage, weighted class coverage, residual risk, the discovery curves and the tool gates are all retained at their stated scope.

Wolfram results above are computed with Wolfram Language on the local Wolfram Engine via `wolframscript`, through `bench/tools/wolfram_gate/serial`, which is its first real use since the founder enabled it.

## The error it found in our own appendix, confirmed

`docs/MATHEMATICAL_APPENDIX.md` gives the inverse of the coverage-to-risk map **twice, and the 2 disagree**.

- **Line 119**: `C = (π−R)/(π−πR)`. Correct; round-trips.
- **Line 169**: `C_k = (π_k−R_k)/(π_k(R_k−1))`. Exactly the NEGATIVE of the correct form. It does not round-trip, and at `π = 1/2, R = 1/5` it returns `C = −3/4`, which is not a coverage. The same line claims "round-trip residual exactly 0", which is false for the formula it writes.

Confirmed by SymPy and by Wolfram independently. The fix is 1 character class and is NOT applied: the founder asked to discuss before proceeding.

## What needs a word from the founder

1. **The appendix correction at line 169. DONE** at `8a0952a`, on the founder's instruction. Now `(π_k−R_k)/(π_k(1−R_k))`, with the old form quoted in the retraction. SymPy and Wolfram confirm the round-trip independently; the appendix's 2 statements are now symbolically identical; 81 tests pass across the 3 guards that read it. **Instrument note:** `bench/tests/test_appendix_reduction_properties_2026-09-05.py` exists for exactly this class, was written because the appendix carried 18 reduction claims verified only in prose; its 35 tests never touched this inversion. A guard for the inverse is PROPOSED, not built.
2. **Arm C of the simulated run.** Its designed form needs the `codex_exec` route, now dropped for cost, so it cannot be restored. Run it in weak form, re-register it as a 2-model contrast, or retire it. `launch_blocked` is read by a test, not by a runner, so nothing is mechanically prevented either way. Default: stays flagged, and the simulated run uses arms A and B.
3. **The Codex seat question.** Not urgent: a simulated run uses stand-ins, so it only matters for a paid run. Default: unchanged.

   **CORRECTION to a claim made twice on 2026-09-17/18.** There are 2 separate rosters. The review panel's is `bench/confer_maths_panel_2026-09-05.py:244` and changing the `cx` model id there breaks no test. The experiment runner's is `load_default_config()` in `bench/experiment_11_orchestrator.py:141`, and changing the `Codex` seat there FAILS `test_the_two_seats_share_weights` (`bench/tests/test_d9_d11_configs_valid_2026-09-05.py:557`) by design, because arm C's condition contrast requires identical weights. Proved by construction: `dataclasses.replace(seats['Codex'], model_id='openai/gpt-5.3-codex')` makes the assertion false. The earlier "nothing is mechanically prevented" was true of `launch_blocked` alone. The useful consequence: **the panel can be diversified without touching the experiment.**

   **Also stale:** `.claude/CLAUDE.md` lists the panel as cc2, cx, ge, cgpt, ds. The live maths panel dispatches cx, cgpt, ds, cc2 and fable — no `ge`. Not fixed, per `d`.
4. **The injection plan.** Recommended for retirement, because runway entry `0C.59` retracted its premise on 2026-09-02: the historic difference was AGENCY, a shell in the working directory, not instruction framing. Default: stays recorded as approved and never built.
5. **The founder's own 2 actions:** drop the 2 stashes, and push, now 32 commits.

## What came in after this was first written

**The revision's author: GPT 6 Astra.** Recorded because we record what we do, in the logs and the docs, as always.

**For the morning, at the founder's request:** what to do about the `public-no-model-credit` directive. Facts gathered: `~/.claude/CLAUDE.md:202-206`, present in that repository's first commit `3e50903` (2026-08-25), carrying no date and no ruling marker, unlike the 2 directives in the same file that do.

**An unverified figure, not repeated as fact.** The background sweep reported that changing the Codex seat's `model_id` breaks exactly 2 tests (`test_the_two_seats_share_weights`:557 and `test_the_evaluator_answers_both_ways`:493). I could not reproduce it: an in-memory patch of `launcher_core.load_experiment_config` did not take effect, and the file stayed at 74 passed. **Unmeasured until re-run.** The same sweep's verifiers refuted several of its own counts — 30 tests in a file holding 15, 33 config files where `ls` finds 47 — so its arithmetic needs a second look. CONFIRMED by construction: the 2 seats share an id today, and replacing the Codex seat's id makes the weight-sharing assertion false.

**One sweep claim corrected.** It said no test reads `.claude/CLAUDE.md`'s model table. `bench/tests/test_sim_naming_and_integrity_directive.py` does — `ROSTER_DOC` at line 89, `_TABLE_HEADER` at line 108. The stale `ge` row is therefore guarded, and editing that table is not a free change.

**Self-inflicted, fixed.** A memory file written tonight tripped 2 guards: an index entry at 161 characters against a 150 limit, and the memory ledger stating 142 files against 143 on disk (`resources/MEMORY_EXCLUSIONS.md`, mirrored 85→86). Both corrected, 87 tests green across the 4 guards. The ledger test complains that this manual correction has been needed 7 consecutive times and wants deriving inside `sv` -- and that remedy now EXISTS: `_update_memory_exclusions_ledger` recounts it during `sv`, so the manual bump was redundant.

## Already in hand

V9 open and scheduled after the model review; the drift detector on the runway at Stage 4 row 4.5 and on the post-revision list; the skip-versus-repair fix delivered at `48487c4`; Wolfram enabled as the second falsifier for every seat and agent, queued against 1 kernel; a fresh working tree per panel attempt with nothing deleted at the end; the full suite green at 8,011 passed under `--netguard-strict`.

**Ordering note.** Zenodo was previously ruled last. The founder has now placed it first, and the record follows the new order.

Written under CDSFL note standard v1.7 (26 August 2026).

## Response sheet, added 2026-09-19 22:10 BST

Answerable in 1 file, 1 line each. Quote the label. Every default in force is non-destructive.

| # | Item | The question | Default |
|---|---|---|---|
| 1 | **Arm C of the next simulated run** | Weak form, re-register as a 2-model contrast, or retire? Its designed form held the model constant and varied conditions (same weights, 1 seat carrying OpenAI's agent scaffolding via `codex_exec`, 1 bare). `codex_exec` is dropped for cost, so the designed form is unbuildable. | Stays flagged; the run uses arms A and B |
| 2 | **The review panel's Codex seat** | Point `cx` at `openai/gpt-5.3-codex`? The panel's `cx` and `cgpt` share 1 model id, so it has 4 architectures and reports 5. This is the PANEL roster (`confer_maths_panel_2026-09-05.py:244`), not the experiment's, and changing it breaks no test. | Unchanged |
| 3 | **The Codex prompt-injection plan** | Retire it? Runway `0C.59` retracted its premise on 2026-09-02: the measured difference was AGENCY (a shell in the cwd), not instruction framing. | Stays "approved, never built" |
| 4 | **1 paid probe call** | Everything about the Codex models is catalogue-read; no route is dispatch-proven. 1 short call to `gpt-5.1-codex-mini` settles it for a fraction of 1 penny. | No call |
| 5 | **The stale panel table in `.claude/CLAUDE.md`** | Fix it? It lists Gemini, which the live panel does not dispatch, and omits Fable, which it does. `test_sim_naming_and_integrity_directive.py` parses that table, so it is not a free edit. | Left as is |
| 6 | **`public-no-model-credit`** | Your call. `~/.claude/CLAUDE.md:202-206`, present in that repo's first commit `3e50903` (2026-08-25), carrying no date and no ruling marker unlike the 2 that do. Authorship not establishable from history. | Unchanged |
| 7 | **Your own 2 actions** | Drop the 2 stashes (deleting a git ref is yours in person); push, now **40** commits. | Neither done |

### For reference only — no response needed

**V9, the one you asked about.** Every closed entry names a test as its evidence. V9 asks the harder question of that test: **undo the fix the entry claims to have made — does the same test go red?** One that stays green against its own reverted fix is decorative: it shows the evidence file runs, not that it would fail if the fix were removed. Approved by you 2026-09-18, state OPEN / status PROPOSED, scheduled after the model revision because the entries it audits are the ones the revision may reopen.

**A19** — `S_k` classifies the whole target rather than each element, so a computable fragment inside prose is never scored. Held for the revision, on your ruling (a).

**A8** — the cited `bench/logs/` paths not under version control. You have ruled on it **twice**; it needs nothing further from you. Its entry names its one remaining condition: *"the Section P panel review of `b8dc6fd`, `f22e95e` and the classifier repair"*. That is step 3 of your sequence, so it closes as a by-product.

### The one red test, and why it needs nothing from you

`test_closure_outpaced_discovery_on_the_latest_full_day` fires because on the most recent day with movement the list gained 1 (V9) and closed 0. It is telling the truth and should not be adjusted. In aggregate the picture is strong: **82 closed against 37 added**, exact binomial p = 4.5e-05 against "adding is as common as closing", cross-checked with scipy and statsmodels. The guard reads a single day, which is why a quiet one fails it. It goes green when A8 closes.

Written under CDSFL note standard v1.7 (26 August 2026).
