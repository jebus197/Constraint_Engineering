# Full scope for the commissioning study

21 September 2026 21:33 BST (Europe/London)

## What this document is

The programme of study of 17 September 2026 (`~/Desktop/CDSFL_Programme_of_Study_2026-09-17.txt`, 161 lines) remains the base. This document does not replace it. It records what has changed in the 4 days since, what the completed mathematical-model review has unblocked, and what the founder's rulings of 21 September add. Where the two disagree, this one governs, and the disagreement is named rather than silently resolved.

## The hold is lifted, and that is the single most important change

The 17 September programme holds work in **2 places** on a condition that is now satisfied. Verbatim: *"The run is already held until the revised mathematical model is reviewed"*, and *"Question 9 holds A19's panel review until the revised mathematical model has been reviewed"*.

**That review is complete.** 6 paid rounds and 1 free round across 7 seats, 2026-09-20 to 2026-09-21, synthesised at `experimental_notes/Maths_Revision_Review_Synthesis_2026-09-20.md`, adjudicated against an external assessment on 2026-09-21. Its verdict: the core model is unchanged, 3 corrections landed, **no equation was revised**. The appendix gained 66 lines and lost 2 across the window, and 1 of those 2 is the line-169 inverse sign fix.

**4 items were held on that condition and are now released:** the run itself, A19's panel review, the I31 drift detector (the founder's ruling was conditional on exactly this), and the Q6 composer refactor.

## The arms

The 17 September programme specifies 3, plus a proposed 4th. This scope adds a 5th, and the addition is the one that answers the founder's actual question.

| Arm | Seats | Target | Purpose |
|---|---|---|---|
| 1. Multi-model panel | 5, all `-SIM` | registry engine | the repairs in a panel shape |
| 2. Single model with agents | 1, `CC2-SIM` | registry engine | the repairs in a single-seat shape |
| 3. Seat contrast | 2, `Codex-SIM` + `ChatGPT-SIM` | registry engine | **needs a ruling, see below** |
| 4. **Prose arm** | as arm 1 | a markdown file carrying fenced Python | **commissions A19** |
| 5. **Paired baseline** | as arm 1 | registry engine | **the effectiveness question** |

**Arm 4 is not optional if A19 is to be commissioned.** Measurement 5 of the base programme already records why: all 3 original arms target a Python module, and `_gateable_source` returns Python unchanged, so the flag cannot bite. Verified independently on 21 September: `.py` returns unchanged, `.md` with a fenced block extracts 1 listing. **Setting `sk_score_prose_listings=True` on a Python target reports "enabled" while proving nothing.** That is the difference between a flag being set and a capability being exercised, and it is the whole distinction commissioning exists to draw.

**Arm 5 is new and it is the only arm that can answer "did the 15 days help".** Run at `a2a0197` (2026-09-06, pre-window) against current HEAD, same target, same seed, nothing newly enabled. Feasible: the runner exists there at 13,446 lines against 16,048 now.

**Why no per-fix attribution, and this bounds the whole study.** 345 commits in the window, 194 touching runtime code (56.2319%, Wilson [50.9568%, 61.3697%]) as measured 2026-09-21. **Re-measured 2026-09-29: 421 commits, 239 touching runtime (56.7696%, Wilson [51.9973%, 61.4195%]), statsmodels and mpmath at 40 dps agreeing to 1.27e-18.** The window grew by 76 commits, 45 of them runtime, and a two-proportion z-test finds no detectable change in composition (z = 0.149365, p = 0.881266). The 345 and 194 aged into 421 and 239; the argument they support did not. Ablation would need 195 runs. Even granting them, testing 194 fixes at α = 0.05 gives a family-wise error rate of 0.999952 — a near-certainty of at least one false "this fix helped" — and Bonferroni-corrected the smallest detectable effect at 100 findings per arm is d = 0.6358, which is enormous. **The study attributes the BUNDLE. Claiming per-fix attribution would be the same error as the circular scorer validation.**

## The window boundary, checked against the founder's own marker

Added 2026-09-29. The founder proposed anchoring the study to *"the week I first said I was in a hotel"*, and asked that this be measured before the itinerary is fixed rather than assumed.

**Measured: the choice barely matters, and his marker and this document's existing baseline are indistinguishable.** The record places him at a hotel on 2026-09-07, driving home at 22:03 that evening to seal the archive; the earliest committed mention is 2026-09-09. This document's pre-window baseline `a2a0197` is dated 2026-09-06 17:06.

| window opens | commits | touching runtime | share | Wilson 95% |
|---|---:|---:|---:|---|
| 2026-09-06 (`a2a0197`) | 421 | 239 | 56.7696% | [51.9973%, 61.4195%] |
| 2026-09-07 | 384 | 220 | 57.2917% | [52.2960%, 62.1429%] |
| 2026-09-08 | 368 | 211 | 57.3370% | [52.2335%, 62.2888%] |

The 3 intervals overlap across almost their whole range, so no boundary in that span changes what the study is measuring. **`a2a0197` is retained**, because arm 5 already depends on a runnable pre-window commit and that one is known runnable at 13,446 runner lines. Adopting a boundary 1 or 2 days later would require finding and re-verifying another, for a difference of 0.57 percentage points that the intervals cannot separate.

## The commissioning set: 8 flags, 5 on, 3 studied

Settled by the founder on 21 September and verified by execution at commit `7f7a443`.

**ENABLED in `bench/tools/run_simulated_experiment.py`:** `discrimination_control_ask`, `severity_calibration_enabled`, `latent_tagger_enabled` (all 3 were **already on** — the sweep's "armed by nothing" counted JSON configs only, and this is a Python config), plus `hierarchical_novelty_convergence` and `sk_score_prose_listings`.

**NOT ENABLED, each a study item with its condition:**

1. **`discrimination_control_blocks`** — refuted by the 2026-08-12 panel: satisfied by *access* rather than *dependence*, defeated by `open(TARGET).read()` with the contents discarded, and it **fails green**. **The study item is whether a dependence-based test repairs it**, not whether the refuted design works. Note this **contradicts** the base programme's section 6, which proposes arming it on the founder's 2026-09-15 ruling. The ruling predates the refutation being carried into the flag's own documentation. **Needs his ruling.**
2. **`immune_memory_consume_rk0`** — the memory is a single persistent file, `bench/state/immune_memory.json`. 19 configs have recording on, including `52_factorial_cell_B` and `_C`, so a global enable destroys the 2×2 factorial's independence and the zero-plant control, and the run completes and produces numbers regardless. **Study it with the memory file reset first**, which scopes consumption to that run. This is what the base programme's section 4 already proposes.
3. **`hil_review`** — not a dormant capability. An operator stepping mode that pauses and resumes; it does **not** change the stopping condition, which remains convergence or round exhaustion. **Nothing to commission.**

## Measurements

The base programme's 7 stand. These are added.

**8. The scorer's non-circular validation.** The post-repair separation of cure from non-cure is **circular** — the gate reads the cure verdict, so separating groups defined by it is near-tautological. The valid held-out signal is whether an admitted fix later attracts an **extension** filed by a different model, which `e1_efficacy` never reads. On the archive this is underpowered: 14 of 192 admitted entries, mean sk 0.964300 extended against 0.951370 not — the wrong direction — p = 0.161004, smallest detectable effect d = 0.7776 against an observed d = 0.3616. **MEASURE: the same comparison on this run's own findings, where the sample is not fixed in advance.**

**9. Routing reach.** `max_rungs` defaults to 2 in `bench/routing.py:183` with **no config surface** — not a flag left off, but a hardcoded default with nothing to switch. Archive: every routing record declares 6 seats available and only 3 distinct models were ever reached. **MEASURE: `rungs_available` against distinct `model_used` per arm, and whether any seat beyond position 2 is ever entered.**

**10. Declared state against observed state.** `bench/launch_exp40.py:324` prints `functional_shadow: ['physics','chemistry','engineering']` to the operator — 56 days after those were promoted live. Behaviour is correct; the report to the human is false. **MEASURE: for every mechanism the run exercises, whether what the launcher declares matches what fires. A commissioning run that certifies from declared state certifies a fiction.**

**11. The maths-model corrections in flight.** The floor is `ν/q`, not `ν`. `ΔR` is unimodal and the decision-relevant quantity is the expected improvement — **`R·q·σ·(1−ν) − ν·(1−R)` in general, and `R·q` only at σ = 1, ν = 0.** The panel corrected this: unscoped, `R·q` overstates by up to 0.164350 at σ = 0.5, ν = 0.1, and z3 shows it never understates, so it is always an upper bound. **The study must quote the general form**, because it will be quoting it against runs where σ < 1. **MEASURE: the observed `R_k` trajectory against both, and whether any arm's stopping decision differs under the two quantities.**

## The panel ruled, 2026-09-21: 6 of 7 seats, and 4 of my items dissolved

`bench/logs/final_review_2026-09-21`. 6 of 7 responded; `kimi` returned empty after 1,116.8s and is a quarantined seat. **Total new apparatus recommended across all 6: none.** cc2's own summary: *"Total new practitioner parameters: zero."* The founder's constraint held.

**1. The `discrimination_control_blocks` "conflict" was mine, not the record's.** The 2026-08-12 refutation does not describe the shipped code. The dependence-based test it demanded **already exists inside the control it refuted**: driven with an access-only falsifier the interception probe returns `intercepted=False` → `DISC_NOT_INTERCEPTED`, a member of `DISC_INDETERMINATE`, so it fails **indeterminate and not green**. Verified by execution. So the founder's 2026-09-15 *"armed and tested live"* ruling is **already satisfied** — with `ask` on and `blocks` off the control runs and records; only the reversal is gated. Both readings hold at once.

**The real reason `blocks` stays off is different and measured**, in the runner's own comment at `:5207-5231`: `DISC_FAILED` cannot distinguish a non-discriminating instrument from an ineffective fix, and **51.2% of fixes, Wilson [45.0%, 57.4%], do not silence their own falsifier**. Blocking would reverse sound verdicts about half the time it fires. The stale comment is corrected in place.

**2. The routing ladder: study, do not raise.** Converged across ge, ds, cx and cc2. ge's reason is the sharpest: 100% of archived refusals were structural (`sk = 0`), so further rungs meet the same wall. ds adds: measure reach first; the 2-rung default is empirically sufficient. **Measurement 9 stands; the change does not.**

**3. `hil_review`: nothing to commission.** Unanimous across cc2, cx, ds and fable — an operator stepping mode that does not change the stopping condition.

**4. Wolfram in panel reviews: denial stands.** Unanimous. **[CORRECTED 2026-09-29 — THE PANEL'S POSITION WAS WRONG AND CC1 CARRIED IT AS A FOUNDER RULING.** The founder: *"There is no 'denial rule' for Wolfram. That is clearly an invention by you."* Measured the same day: `DEFAULT_POLICY` is `serial`, the live seat arguments are `('--strict-mcp-config',)` with **no** `--disallowedTools`, the serial gate sits first on every seat's `PATH`, and nothing in the repository sets `CDSFL_WOLFRAM_POLICY=deny`. **Wolfram has been enabled for command-line seats since his 2026-09-17 ruling.** A panel opinion is not a rule (`feedback_no_model_voting`); this line records what the seats said, not what is in force.]**

**5. I31 save/restore: do not land it mid-commissioning.** cc2's reason: *"enabling persistence mid-commissioning changes the instrument being commissioned."* ge: not until a committed measurement shows drift actually occurs.

**6. ν is measurable from the archive and φ is not.** ds: ν is *"fully automatable... run before the commissioning study so the run uses an empirical ν rather than the default"*. φ needs human classification and is not automatable in time. **cc2 sharpens it: φ's SIGN is already decided; only its magnitude is unknown.**

**7. Added to Measurement 8, from fable, using outputs that already exist.** Condition the `DISC_FAILED` population on the fix-efficacy probe's `FIX_CURES` result. A fix that cures while its falsifier still fires on the corrected copy is a **genuine instrument fault**; one that does not cure is not. That separates the 51.2% confound with no new apparatus, and it is what `blocks` actually waits on.

**8. And the panel corrected 2 things of mine.** Measurement 11's `R·q` is the σ = 1, ν = 0 corner and overstates everywhere else — the general form is `R·q·σ·(1−ν) − ν·(1−R)`, verified identical on SymPy and unsat on ever understating in z3. And the appendix carried a **gamma demotion** at line 1087, dated 23–29 May 2026, which the founder's two-sided-gate ruling reversed 12 days later and which survived 66 lines of revision unnoticed. The shipped predicate blocks convergence when `gamma_critical < threshold`, so the appendix contradicted both the directive and the code. Corrected, with a reproducer that drives the real predicate.

## What still needs the founder's ruling

1. ~~`discrimination_control_blocks`~~ — **RESOLVED by the panel, no ruling needed.** The conflict was a stale premise; both readings already hold. See above.
2. **The seat contrast arm** (base programme item 12c) — its file marks launch as blocked on the Codex paid route; in a simulated run both seats are the same stand-in, so it is the weak form by construction.
3. **I31 drift detector** (item 12b) — released by the maths review completing; the choice is whether the PROPOSED save/restore changes land before the run.
4. **Wolfram in panel reviews** (item 12d) — **NEEDS NOTHING, AND NOT FOR THE REASON THIS LINE USED TO GIVE. Wolfram is ENABLED for command-line seats and has been since 2026-09-17; the "denial" was CC1's invention, retracted 2026-09-29.** The API seats cannot reach a shell, so his own fallback clause governs them: *"where they cannot, then they should default to equivalent Open Source tools"* — they have SymPy and z3 and use them.

## A caution that bears on the whole exercise

`scripts/done_audit_overclaim_rate_2026-09-17.py`, re-executed 2026-09-21: **31 of 84 DONE entries claim more than their evidence shows, 36.9048%**, Wilson [27.3701%, 47.5848%], with statsmodels, scipy's closed form and mpmath at 30 digits agreeing to 8.33e-17. **`R3`, `9.1`, `9.2`, `9.3` and `9.4` are among the 31, and this run leans on each.** `P1`, `P3`, `P4`, `P5` and `P7` — the Section P panel conditions — are also among them.

A commissioning study that reads DONE markers as evidence would inherit that error at better than 1 entry in 3. **The study reads what fires, never what a marker claims.**

## What would falsify the claim that the repairs work

The base programme's list stands, with 2 additions. The bundle comparison shows no difference between the pre-window and current arms on any primary metric. Or: a mechanism the launcher declares enabled does not fire, and nothing in the run's own record would have revealed it.

## When to stop

Unchanged, and it is the project's rule from the outset: **convergence, the irreducible-queue alarm, or the round limit.** The study stops when every measurement has a value or a named reason it could not be taken. A measurement that could not be taken is reported as such and never as a pass.

Written under CDSFL note standard v1.7 (26 August 2026).

## REVISION, 2026-10-14T21:50:11+01:00: the window re-measured and 10 mechanisms added

Added on his instruction: *"the next simulated run and (revised) program of study, that should include all fixes since I first told you I was staying in a hotel. (I think that was about 4 or 5 weeks ago?)"*

**His recollection is accurate and the boundary does not move.** The record places him at a hotel on 2026-09-07, driving home at 22:03 that evening to seal the answer-key archive; the earliest committed mention is 2026-09-09. From 2026-10-14 that is 37 days, so "4 or 5 weeks" is right. The window boundary measured on 2026-09-29 stands: `a2a0197`, 2026-09-06 17:06, whose 3 candidate openings gave intervals overlapping across almost their whole range. Nothing in the intervening 15 days bears on that choice, and arm 5 still depends on that commit being runnable.

**The window has grown by 176 commits and its composition has not moved at all.** Measured now: **597 commits since `a2a0197`, 339 of them touching runtime code, 56.7839%**, Wilson [52.7793%, 60.7018%]. Against the 2026-09-29 figure of 239 of 421 (56.7696%, Wilson [51.9973%, 61.4195%]) a two-proportion test finds **z = -0.004543, p = 0.996375**, with Fisher exact at p = 1.000000 and a Yates-corrected chi-square agreeing; a hand computation in NumPy and mpmath reproduces the z to 4.0e-16. The share across the 3 measurements reads 56.2319%, 56.7696%, 56.7839%.

**So the argument that bounds this study is unchanged and now rests on a larger sample.** Per-fix attribution would need 339 ablation arms, and the family-wise error rate argument already recorded applies with greater force. **The study attributes the BUNDLE.** What the revision adds is not a new method but 10 mechanisms whose first data point is the next run, each of which was built inside the window and has never been exercised by a live run.

### The 10 mechanisms the next run measures for the first time

1. **The directive length cap's own record.** `manifest["length_cap"]` carries fired, cap, chars_cut and packets_cut as of 2026-10-14. Before it, deepseek_v3 at cap 4000 received **1 of 196 characters** of its situation packet while the manifest claimed full delivery. **MEASURE: whether the cap fires in the run at all, and for which seats, against what the manifest records.**
2. **The retired mechanical pruner.** Retired on his ruling of 2026-10-13, reachable only behind a flag. Verified on the real compose path: 0 of 50 compositions lose a domain directive with the retirement in force, against 10 of 50 with the flag on. **MEASURE: that 0 holds in a live run, and the lean-versus-full comparison if he wants it run.**
3. **Directive delivery, now known to be uniform.** Every one of 8 seat labels receives the same 2,503 characters, 9.0026% of the core formal directive, with 0 of its 16 headings surviving. The per-model caps therefore differentiate nothing. **MEASURE: what each seat actually receives in the run, recorded per seat rather than derived.**
4. **The worked-proof gate, which no directive states.** "worked proof" occurs 0 times in either directive file while the requirement is enforced at `bench/dm/_rk_proof.py` and `bench/reference_runner_v3.py:9499-9511`. **MEASURE: how many findings are refused by a gate the seats were never told about. This is the sharpest open confound in the study.**
5. **The severity specification shadow.** Appendix section 7.7 computed as a shadow, gating nothing, since 2026-10-12. **It has never recorded**: 0 archived reports carry the field. **MEASURE: its first live values, and whether promoting it would distort.**
6. **The evidence deny tier.** A falsifier can no longer read the project's own evidence; 0 of 1,360 archived falsifier sources ever did. Not yet exercised by a live verification, which is his own stated instruction. **MEASURE: that the tier fires and refuses nothing honest.**
7. **The routing ladder's EXHAUST default.** His ruling of 2026-10-06 made `max_rungs=0` mean "use every rung". **0 of 39 archived UNTOOLABLE rows postdate that ruling**, Wilson [0.0000%, 8.9667%], so cc2's finding that 11 of 11 attempted-and-failed cases stopped with rungs in hand is entirely pre-ruling. **MEASURE: whether any finding still stops with rungs untried. This is the test of whether the never-attempted class is already closed.**
8. **The never-attempted class itself.** 1,938 of 3,298 archived findings carry no falsifier, of which 1,639 of 1,938 were never attempted. **But 1,568 of 1,886 deduplicated, 83.1389%, Wilson [81.3822%, 84.7609%], predate the falsifier machinery entirely** — April and May 2026 are 100% falsifier-less because nothing existed to carry one. **MEASURE: the rate within this run alone, where no pre-machinery era can inflate it.**
9. **A19 on a prose target with verified defects.** `sk_score_prose_listings` has been set and inert because the launcher's target defaults to a Python file. `targets/prose_with_computable_listings.md` is now named as `PROSE_TARGET` and carries 2 defects verified by 2 independent tools each, plus one claim carrying no listing at all. **MEASURE: that the reducible hunks are scored and the unscoreable claim returns NO_SCORE rather than a fabricated grade.**
10. **The pre-verdict sweep shadow**, added 2026-10-06, which 0 archived reports carry because the newest report predates it. **MEASURE: its first data point.**

### What the revision does NOT change

The 5 arms stand. The 8 flags stand, 5 on and 3 studied. Measurements 1 to 11 stand. Arm 5 remains the only arm that can answer whether the bundle helped, and it still runs `a2a0197` against current HEAD on the same target with the same seed.

### 4 items still need his ruling and no measurement substitutes for them

1. **The caps.** Both panel seats of 2026-10-14 refused outright removal on the additive standard, since no committed measurement shows removal dominates in either direction. Their recommendation, which supersedes CC1's own proposal, is to measure it in this run.
2. **The prose target.** His own suggestion of PAPER.md is refuted: its 11 fenced blocks contain 0 Python.
3. **fable's proposed section 11 Worked Proofs** in the core formal directive, marked by fable as awaiting his ratification.
4. **cc2's single irreducible exception**, `sim45_memory_20260908T033012Z` C0050, where cc2 records 1 genuinely irreducible finding in 41 and fable records 0.

Producers: `scripts/were_the_missing_falsifiers_pre_machinery_2026-10-14.py`, `scripts/directive_chatter_predicate_2026-10-14.py`, `scripts/never_attempted_findings_2026-10-14.py`, `scripts/what_the_full_directive_set_costs_2026-10-14.py`. Repository state at the time of writing: branch `sim/shakedown-2026-09-29`, HEAD `da23d286`.
