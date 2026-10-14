# Joint round on the directive set and measured capability — FULL RECORD, unfiltered

2026-10-14T23:52:28+01:00. Branch `sim/shakedown-2026-09-29`. Round `joint_the_directive_set_2026-10-14`, JOINT, 2 free seats, `paid_seats: []`.

**Audience: a reader who can follow a file path but was not in the session.** Both replies are reproduced below between verbatim markers, complete and unedited.

## SEATS

| seat | chars | tool calls | elapsed |
|---|---|---|---|
| cc2 (Claude Opus 4.7) | 37,768 | 56 | 946.5 s |
| fable (Fable 5.1) | 26,432 | 44 | 947.8 s |

## WHERE THE 6 ITEMS LANDED

| Item | cc2 | fable |
|---|---|---|
| J1 the caps, made decidable | PARTIAL — specifiable, but 1 run is underpowered by 6.7x | CONFIRMED — specified, and the power arithmetic given |
| J2 one chatter predicate | CONFIRMED — adopt P2 | CONFIRMED on the premise — adopt P1 |
| J3 the prose target | PARTIAL | PARTIAL |
| J4 capability_identity not adopted | CONFIRMED | CONFIRMED |
| J5 the irreducible exception | CONFIRMED | PARTIAL against BOTH blind positions |
| J6 fable's section 11 | REFUTED as proposed | ATTACK SUCCEEDS against its own version |

## THE FINDING THAT REFRAMES THE FOUNDER'S DECISION 1

**cc2 established that the cap VALUE changes nothing.** `bench/cdsfl_registry/composer.py:591-598` reads `use_minimal = format_style == "minimal" or len(full_text) > cap`, and 27,803 characters exceeds every configured cap, so the minimal render fires for all 5 phenotypes and returns the same 2,503 characters whatever the cap says. Measured across the whole configured range of 4,000, 6,000, 8,000 and 12,000: **distinct delivered lengths = [2503]**. The cap is a BINARY SWITCH, not a graded knob, so a cap-value sweep is not an experiment design.

**And what the 2,503 characters contain is worse than a truncation.** cc2 printed the render: 43 `policy.*` configuration keys plus 5 behavioural lines. **No R_k, no corroboration model, no runnable-falsifier requirement, no falsifier-integrity section, no section 10.**

**CC1 then derived, and verified 3 ways, that trimming chatter CANNOT fix this.** To bring the core file under even the LARGEST cap requires removing **15,803 of 27,803 characters = 56.8392%**. The broadest of the 4 measured chatter predicates removes 4,114 characters = 14.7970%, leaving **11,689 characters still over the cap**. SymPy and mpmath agree on the share to 4 decimal places and z3 returns **unsat** for the question "can a cut of at most 11.96% reach the cap". **So the founder's question of which sections to cut has an answer: cutting chatter is worth doing on its own merits and cannot change what any model receives. Only removing or raising the cap can.**

## THE ONE GENUINE DISAGREEMENT, PRESERVED

**The seats split on which chatter predicate to adopt, and both arguments are sound.** cc2 chooses **P2**, paragraph-expanded with an imperative veto, because a cut operates on a removable unit and a per-line predicate cannot answer "what should we cut"; it measures 44 of 49 P2 hits inside a section the 2026-07-18 review already marks compressible, 89.7959%, Wilson [78.2436%, 95.5620%]. fable chooses **P1**, narrow, because the predicate's job is a CUT LIST and must be precision-first; it refutes P3 for that job on its own audit (7 of 21 hits operative, a false-positive share of Wilson [17.1948%, 54.6265%]) and rejects P2 because paragraph expansion "cannot distinguish a provenance stamp from the rule it stamps". Both reject P3 and P4 for the cut-list job. **This is not resolved by vote and is left as information.**


## ONE INTERVAL IN THE REPLIES BELOW IS WRONG, AND IT IS RECORDED HERE RATHER THAN CORRECTED THERE

A seat quotes **[0.0000%, 8.4495%]** as the Wilson 95% interval for 0 of 41. The correct upper bound is **8.5668%**, statsmodels and mpmath agreeing. The reply is NOT edited: the founder's standing instruction is that panel replies are presented in full and unfiltered, and silently correcting a seat's arithmetic turns the record into a paraphrase. The conclusion it supports is unaffected, since both bounds place the figure far below any threshold in play.

**`scripts/wilson_interval_consistency.py` refused the commit over this**, which is the checker working: it had no notion of the verbatim markers that `scripts/note_vagueness_lint.py` already honours. It now skips marked spans and nothing else, proven by execution — an identical wrong interval placed before and after a verbatim block is still caught, at the correct line numbers, while the one inside it is not.

## Seat: cc2 — Claude Opus 4.7

`ok=True`, 37,768 characters, 56 tool calls, 946.5 s.

<!-- verbatim-begin: cc2 (panel joint_the_directive_set_2026-10-14) -->

All work is executed and committed to files. Targeted regression: **88 passed** across 7 test files.

---

## J1 — The caps, made decidable

1. **item** — J1
2. **verdict** — **PARTIAL.** The measurement is specifiable; the next *single* simulated run is **SHOWN UNDERPOWERED** for it, by a factor of 6.7. Two sub-parts: (a) the arm design is settled and deterministic — CONFIRMED; (b) the outcome comparison at n=1 run — REFUTED as a settling instrument.
3. **evidence** — `python3 scripts/the_caps_measurement_is_underpowered_2026-10-14.py`:

```
=== 1. THE CAP IS A BINARY SWITCH, NOT A GRADED KNOB ===
  cdsfl_core_formal.md source: 27,803 chars
  opus_4_6       cap=12,000 -> delivered 2,503 chars, 0 of 16 headings
  chatgpt_5_4    cap= 8,000 -> delivered 2,503 chars, 0 of 16 headings
  codex_5_3      cap= 6,000 -> delivered 2,503 chars, 0 of 16 headings
  gemini_3_1_pro cap= 8,000 -> delivered 2,503 chars, 0 of 16 headings
  deepseek_v3    cap= 4,000 -> delivered 2,503 chars, 0 of 16 headings
  distinct delivered lengths over cap range [4000,6000,8000,12000]: [2503]
```
The cap **value** changes nothing. `bench/cdsfl_registry/composer.py:591-598` takes `use_minimal = format_style=="minimal" or len(full_text) > cap`; 27,803 exceeds every configured cap, so `_render_universal_minimal` fires for all five phenotypes and returns 2,503 chars regardless of its `max_chars` argument. I printed that render: it is a dump of 43 `policy.*` TOML keys plus 5 behavioural lines. **No R_k, no corroboration model, no runnable-falsifier requirement, no falsifier-integrity section, no §10.** A cap-value sweep is therefore not a design; the only contrast that exists is minimal-vs-full.

4. **tools** — Wilson intervals: hand/`math` implementation vs `statsmodels.proportion_confint(method="wilson")`, agreeing to <1e-12 on all five proportions (`[AGREE]` printed per row). Sample size: `statsmodels.NormalIndPower` (arcsine) **191.9**, closed-form normal approximation **196.0**, **SymPy** symbolic substitution **196.0**, and **Wolfram Language** (local Wolfram Engine via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`) **195.98361501642495** — *Computed with Wolfram Language*. Four tools agree at p1=0.90. **One honest disagreement reported, not suppressed:** at p1=0.95 the arcsine solver gives 68.6 against the closed form's 74.5, a 7.9% gap — the arcsine transform and the raw normal approximation diverge near the boundary. The operative row (p1=0.90) is unaffected.
5. **interval** — Capped-arm baseline, determinate falsifier verdict: **183/229 = 79.9127%**, Wilson **[74.2493%, 84.5890%]**. The two statistics the seats proposed, both refuted as instruments: fable's runner-reverified confirm rate **12/229 = 5.2402%**, Wilson [3.0227%, 8.9346%] — floor-bound and clustered, per-run counts `[0,0,0,11,0,0,1,0]`, 11 of 12 events in one run; critical-carrying-a-falsifier **55/58 = 94.8276%**, Wilson [85.8606%, 98.2254%] — ceiling-bound, maximum attainable gain 5.17 points, which needs n≈873/arm.
6. **falsifier** — `scripts/the_caps_measurement_is_underpowered_2026-10-14.py`, section 1, carries `assert len(distinct) == 1`. It is **GREEN** on the tree as it stands (the cap is inert across its range) and goes **RED** the moment any cap is set below 2,503 or `_render_universal_minimal` becomes cap-sensitive — i.e. it fails exactly when the premise of this item stops holding. Output pasted above.
7. **refutation** — I tried to find a cap value in the configured range that produces a different delivery and could not: the four distinct caps yield one distinct length. I then tried to rescue fable's confirm-rate statistic by pooling all 8 archived runs; pooling does not help, because 11 of the 12 events come from one run, so the effective cluster count is 2, not 229. I also tried the critical-carrying-a-falsifier rate as a fallback and it is ceiling-bound. Both attempts failed to overturn "underpowered".
8. **fix** — `scripts/the_caps_measurement_is_underpowered_2026-10-14.py` (new producer, `--help` free, exit 0). **The design, stated so tomorrow's configuration is decidable:**

   - **Property:** per-finding **determinate falsifier verdict rate** — `falsifier_verdict ∈ {CONFIRMED, REFUTED}` as recorded by the runner's own re-execution. Chosen over both seats' proposals because it is harness-computed with no model judgement, its base rate is away from 0 and 1, and the requirement it measures ("Runnable Falsifiers for Critical Findings", "Falsifier Integrity") is stated **only** in the core sections the cap deletes.
   - **Arms:** exactly 2. **A (capped, status quo)** = 2,503-char minimal render. **B (uncapped)** = 27,803-char full core, *with the compose-level final cap at composer.py:1478 also lifted* — this is forced, not optional: leaving it on would re-truncate arm B at 4,000–12,000 chars. **Consequence, stated rather than hidden: a 2-arm design cannot attribute the effect between the two cap sites.** A third arm (full core, final cap retained) is required for attribution and is not worth running until arm B shows an effect.
   - **Statistic:** difference in proportions, each arm reported with a Wilson score interval, the difference with a Newcombe hybrid-score interval.
   - **Stopping rule: fixed n, pre-registered, no interim looks.** n = **196 findings per arm** for 80% power at α=0.05 against a 10-point effect (0.799 → 0.900). At the archive's observed yield (8, 16, 19, 22, 25, 39, 39, 61; mean 28.6) that is **≈7 runs per arm, 14 total**. Findings cluster within (run, seat), so 196 is a **floor**: estimate the ICC from the first arm's data and re-inflate by DEFF = 1 + (m̄−1)·ICC, and report a cluster-bootstrap interval over runs rather than the naive binomial.
   - **Decision rule:** remove the caps iff the Newcombe lower bound on (B − A) exceeds 0. Otherwise record the measured transport limit per identity, with its date and producer, which is what the proposal itself says a limit must have.
   - **What tomorrow's single run CAN settle, with no sampling error at all:** the manipulation check. Assert by execution that arm B delivers 16 of 16 headings and arm A delivers 0 of 16, and that no other delivered byte changes. **Recommendation for tomorrow: run arm B, and do not remove the caps on the strength of it.**
9. **disagreement** — Against **fable**: its named property, per-seat runner-reverified confirm rate, is **unusable** — 5.2402% with 11 of 12 events in one run. Its arm is also incomplete: lifting only the universal cap leaves composer.py:1478 to re-truncate, so "the arm returns source byte-for-byte" holds for the packet and not for the delivery. Against **cc2**: I confirm its "inert over its whole configured range" and sharpen it — the inertness is not a quirk, it makes a cap-value sweep logically impossible, which neither seat stated. I changed position on nothing; I had no prior blind position on the statistic.
10. **termination** — Stopped when four tools agreed on n≈196 and the observed per-run yield made the factor of 6.7 arithmetic rather than arguable. Further precision on the ICC requires arm-B data that does not exist.

---

## J2 — One chatter predicate, chosen

1. **item** — J2
2. **verdict** — **CONFIRMED.** Adopt **P2 (paragraph-expanded, imperative-vetoed)**.
3. **evidence** — `python3 scripts/directive_chatter_predicate_2026-10-14.py` and `python3 scripts/the_caps_measurement_is_underpowered_2026-10-14.py` section 4, which imports `p2_medium` from the committed producer rather than reimplementing it:

```
  [compress     ]  23 lines  16. Stage 6 Literature-Calibrated Extension
  [compress     ]   9 lines  §18 Divergence Directive
  [compress     ]   6 lines  7.1. Finding Lifecycle (Bugzilla Paradigm)
  [compress     ]   6 lines  17. Feedback Channel — Corrective Loop
  [KEEP-VERBATIM]   5 lines  15. FFAFP Admissibility Constraint Set
  P2 hits inside a 'compress' section  44/49 = 89.7959%  Wilson [78.2436%, 95.5620%]
```
**Why P2 and not the other three.** A cut operates on a *removable unit*. P1 and P3 are **per-line** predicates; cutting a line out of the middle of a paragraph is not a cut anyone would make, so neither can answer "what should we cut" whatever its share. P3 additionally fails its own stated intent: **7 of its 21 hits carry no calendar date at all**, including `**σ_measured — fix efficacy measured, not assumed.**` and the Stanford POPPER citation. P4 is paragraph-level and therefore the right shape, but it has **no imperative veto**, so it sweeps in paragraphs containing MUST / NEVER / DO NOT — HARD-constraint text under §1. Cutting those is a hard-constraint removal and is excluded before any measurement. P2 is the only predicate that is both paragraph-shaped and imperative-vetoed.

The decisive positive argument is not the share, it is **concurrence between two independently-derived instruments**: a human pruning review in July 2026 and a mechanical predicate in October 2026 agree on 44 of 49 marked lines. And the founder's "7%" sits inside P2's combined line-share interval (98/1256 = 7.8025%, Wilson [6.4446%, 9.4178%]) — the predicate that is correct on structural grounds is also the one that reproduces his figure.

4. **tools** — hand Wilson vs `statsmodels` on every proportion, `[AGREE]` to <1e-12. Section attribution computed by executing the producer's own `p2_medium` against a heading map built from the live file, not by a second copy of the predicate.
5. **interval** — P2 combined lines **98/1256 = 7.8025%** [6.4446%, 9.4178%]; P2 combined chars 6,740/74,177 = 9.0864%. Concurrence with the July review **44/49 = 89.7959%** [78.2436%, 95.5620%]. P3 false positives **7/21 = 33.3333%** [17.1948%, 54.6265%].
6. **falsifier** — `scripts/the_caps_measurement_is_underpowered_2026-10-14.py` section 4. It is GREEN as written and goes RED if `p2_medium`'s hits migrate out of the compress sections or §15's residual grows — i.e. it fails if the concurrence that justifies the choice stops holding. Output pasted.
7. **refutation** — I tried to defend P4 on the ground that the imperative veto might be over-broad and discard genuine chatter. It does discard: P4 marks 130 lines against P2's 98. I inspected the delta and it is imperative-bearing paragraphs, which §1 classifies HARD. The attempt failed and P2 stands.
8. **fix** — No directive text cut. **NO CUT PROPOSED, and the reason is a measurement, not a preference:** the capped delivery means 0 of `cdsfl_core_formal.md` reaches any seat, so cutting P2's 3,582 core chars saves **exactly 0 delivered characters**. The entire actionable saving is the 3,158 operational chars ≈ 790 tokens per seat per round, and 44 of 49 of those lines are inside sections the July review already marked compressible. **Implication for the 6 compressible sections:** P2 lands in only 4 of them (§7.1, §16, §17, §18); the preamble and §14 carry no P2 hits, so there is nothing mechanical to cut there and the July review's judgement is unsupported for those two. The 14 KEEP-VERBATIM sections keep their text, and the 5 residual §15 hits go to the founder rather than being cut — under the additive standard KEEP-VERBATIM wins because no measurement shows removal dominates.
9. **disagreement** — Against **fable**: it ruled "cut: nothing" having enumerated only P3's 21 lines, which is the wrong predicate for a cut question; its answer happens to coincide with mine on the core file for a reason it did not identify (the core reaches no seat at all), and understates the operational case. Against **cc2**: it reported the range 1.0–11.3% and declined to choose. A range is the honest answer to "how much" and no answer to "what to cut"; choosing is what the item asked for.
10. **termination** — Stopped at the structural elimination of P1/P3/P4. The concurrence figure corroborates; it was not needed to decide.

---

## J3 — The prose target

1. **item** — J3
2. **verdict** — **PARTIAL.** Fit to commission the *extraction* half of A19; **not** fit for the *inadmissibility* half, and as it stood it could not measure discrimination at all. Part (a) fit — CONFIRMED; part (b) design point coverage — REFUTED and now repaired. On the cc2-vs-fable split: **cc2's attack on PAPER.md succeeds; fable's Item 5 SOUND is REFUTED on its operative claim.**
3. **evidence** — The live classifier, executed, not grepped:

```
prose_with_computable_listings.md  hunks= 2 src=589  gating 2 fenced listing(s)...
control_two_distinct_defects.md    hunks= 0 src=None target carries no code; syntax gates not applicable
PAPER.md                           hunks= 0 src=None target carries no code; syntax gates not applicable
bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md hunks= 2 src=569 gating 2 fenced listing(s)...
```
`reference_runner_v3._gateable_source` at line 13057 returns `None` for PAPER.md. **fable's Item 5 asserted "11 fenced blocks plus 49–69 computable lines exercises both paths."** It exercises the inadmissible path only, because 0 of the 11 fences carry Python. fable's own producer counted fences without checking their language tag; `_gateable_source` checks the tag, and it decides. That resolves the split by execution.

**Two defects in the target verified independently, by two tools each, before I attacked it.** PL-01: SymPy gives `E[listing] = 4σ²/5`, bias `−σ²/5`; a 200,000-draw NumPy simulation returns 0.801737 against the exact (n−1)/n = 0.8. PL-02 at k=10, n=50: listing upper bound 0.3660448588889335; `statsmodels` 0.33037105932225413 and `mpmath` at 40 dps 0.33037105932225413 agree to <1e-12 against each other and both differ from the listing by 0.0357.

**The attack that succeeds.** Both listings were defective, so a seat that reports every listing it is handed scores 2 of 2 and is indistinguishable from one that discriminated. **Precision had no denominator.** And `control_two_distinct_defects.md` already serves the code-free half (0 hunks) — commissioning needs both targets run, not one.

4. **tools** — SymPy + NumPy (PL-01); statsmodels + mpmath@40dps (PL-02); SymPy + mpmath@40dps (new PL-03). Each pair independent of the listing and of each other.
5. **interval** — PAPER.md fences containing Python **0/11 = 0.0000%**, Wilson **[0.0000%, 25.8833%]** — the upper bound is 25.88%, so "0 of 11" does not license "PAPER.md never contains Python", only that the measured target does not. Target composition after the fix: defective listings **2/3 = 66.6667%**, Wilson [20.7660%, 93.8508%].
6. **falsifier** — `bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py`.
   **RED (before the fix):**
```
FAILED ...::test_the_live_extractor_sees_exactly_two_listings
FAILED ...::test_the_target_also_carries_a_claim_with_no_listing
2 failed, 7 passed in 2.12s
```
   **GREEN (after):** `10 passed in 2.04s`.
7. **refutation** — I tried to show the target was already sufficient by arguing the mutation-grade test at line 143 supplies the precision denominator. It does not: it repairs a *defective* listing in memory and checks the repair; it never asks whether a seat can tell a correct listing from a defective one, because no correct listing was present to be mis-reported. I also tried to make PAPER.md serviceable by re-reading its fences for Python-shaped content — `_gateable_source` returns `None`, and tagging those fences `python` would be false.
8. **fix** — Two files.
   - `bench/cdsfl_registry/targets/prose_with_computable_listings.md` — added **Claim PL-03** with a **correct** listing (`cumulative_detection`, the Stage-1 corroboration model C(n) = 1 − (1−p)ⁿ), renumbered the listing-free prose claim to **PL-04**, and amended §3 to say in the target's own words that being reducible is not the same as being wrong. The target now carries 3 listings: 2 defective, 1 correct, plus 1 unscoreable claim.
   - `bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py` — count assertion sharpened `== 2` → `== 3`; the listing-free claim pinned to PL-04 with `claims == ["PL-01","PL-02","PL-03","PL-04"]` replacing `len(claims) >= 3`; new `test_PL03_listing_is_CORRECT_under_two_independent_tools` (SymPy decides C(0)=0, dC/dn>0, d²C/dn²<0; mpmath@40dps decides the arithmetic at four points; the ValueError guards are exercised). **Neither assertion was weakened — both were replaced by strictly stronger ones, and the reason is written in place in each docstring.** The docstring also records that the code-free half belongs to `control_two_distinct_defects.md` and that commissioning A19 requires both targets.
9. **disagreement** — Against **fable**: its Item 5 held PAPER.md SOUND as a prose target on a fence count that did not check the language tag. I hold it REFUTED, by the live classifier. Against **cc2**: its attack succeeds and I extend it — cc2 stopped at "PAPER.md → NO_SCORE", which is correct and leaves the real gap unnamed. The gap is that a target with no correct listing cannot measure discrimination however good its defects are, and that gap was in the *replacement*, not in PAPER.md.
10. **termination** — Stopped when the guard went green with the precision denominator present and both A19 paths had a named target. Running the arm is the next dispatch's work.

---

## J4 — `bench/capability_identity.py` not adopted

1. **item** — J4
2. **verdict** — **CONFIRMED.** The orchestrator's call is right, and I am not building a wiring, because there is not one that is both additive and dispatch-neutral.
3. **evidence** — Both harvested modules exist and neither has a consumer: `wc -l` gives 352 (cc2) and 123 (fable); `grep -rn "capability_identity" bench/ --include=*.py` outside the harvested evidence tree returns nothing. The reason the brief gives — wiring measured capability into seat selection is a design change — is correct, and the ranking is the module's only exported purpose. The substantive point is different and it is measured: **the module is not merely unread, the measurement it exists to enable is already derivable from the committed archive without it.** Eight lines against `runner_state.json`'s `source_model` and `falsifier_verdict`:

```
runs 8 determinate 183
  DeepSeek-SIM  40  per-run 5.00  runs to reach 43: 9
  CC2-SIM       32  per-run 4.00  runs to reach 43: 11
  Gemini-SIM    29  per-run 3.62  runs to reach 43: 12
  Codex-SIM     28  per-run 3.50  runs to reach 43: 13
  ChatGPT-SIM   27  per-run 3.38  runs to reach 43: 13
  Fable-SIM     27  per-run 3.38  runs to reach 43: 13
```
So fable's `RETIREMENT_MIN_OUTCOMES = 43` is reachable in **9 to 13 simulated runs per seat**, from records the runner already writes. A module in `bench/` is not required to get there; a producer script is. That is the simplest-sufficient answer.

4. **tools** — `statsmodels.proportion_confint` and the hand Wilson implementation on the determinate rate (agreeing to <1e-12); `json`/`glob` enumeration of the 8 archived simulated runs cross-checked against the entry total 229 that the J1 producer independently reaches.
5. **interval** — Determinate outcomes **183/229 = 79.9127%**, Wilson **[74.2493%, 84.5890%]**. Per-seat shares range 27/229 to 40/229; at the observed per-run rates the 43-outcome threshold is 9–13 runs away per identity.
6. **falsifier** — No new file. The falsifying observation is the `grep` above returning zero consumers, which is a negative result and not a defect demonstration; I am not dressing it as one. The J1 producer is the file that carries this item's live numbers.
7. **refutation** — I looked hard for a dispatch-neutral wiring that would make adoption additive, and found the tempting one: record the capability ranking in shadow, reusing the project's own committed idiom (`fix_efficacy_mode="record"`, `macrophage_shadow_r*.json`, `hierarchical_novelty_convergence` recorded in shadow since 2026-08-04). I rejected it on the measurement above: the shadow record would have **no reader**, and the outcomes it would accumulate are **already in the archive**, so it is an addition that does nothing — the exact shape of 11 confirmed defects since 2026-08-01. The one thing `stable_identity()` genuinely buys that the archive does not is that `source_model` is a seat *label* (`CC2-SIM`), not an identity; if the model behind a label changes, the archive silently pools two capabilities. Recording the provider/model_id/version triple fixes that **going forward only**, and it is additive only once something reads it — and the only reader that needs it is a ranking that changes dispatch. The circle does not open, so I say so rather than building half of it.
8. **fix** — **NO FIX PROPOSED.** Neither harvested module should be adopted into `bench/`. The founder's decision reduces to one line: if he wants the capability record, the simplest sufficient form is a producer script over the existing `runner_state.json` corpus, and it is 9–13 runs from a usable n per seat. If he wants the stale-label problem closed, that is a runner edit recording the identity triple, and it must land *with* its reader or not at all.
9. **disagreement** — Against **fable**: it withdrew its defence of the frozen tuple and derived n=43 (which I reproduce: z²/δ² = 42.683 → 43 at δ=0.3), but then wrote a module whose only consumer changes 23 routed configs, and said the cutover is the founder's. That is an addition parked against a decision, which is how the 11 unwired defects happened. Against **cc2**: it flagged its own Item 2 audit and Item 3 ledger as unwired and said passing test counts do not make them additive. **I agree with cc2 and go further**: for the capability ledger specifically, the wiring will never be additive, because the measurement it would enable already exists in the archive. cc2 treated its non-adoption as a debt to be discharged next dispatch; I treat it as the correct permanent outcome for this module.
10. **termination** — Stopped when the per-seat outcome counts showed the archive already supplies the measurement. Nothing further is decidable without a founder ruling on the dispatch change.

---

## J5 — The one real disagreement

1. **item** — J5
2. **verdict** — **CONFIRMED, and it settles on the record. The genuinely-irreducible count is 0 of 41. cc2's exception falls — and fable's reason for reaching 0 is also wrong.** C0050 is not equipment failure; it is a **toolable claim whose dispositive sub-claim is false**, decided by two subtractions.
3. **evidence** — `python3 scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py --claim cc2`:

```
  target_chars                               20563
  target_bytes                               20605
  multibyte_delta                            42
  numbers_are_chars_and_bytes_of_one_file    True
  falsifier_verdict                          'UNTOOLABLE'
  rungs_tried                                2
  rungs_available                            6
  routing_verdict                            'ERROR'
  attempt_subject_is_experiment_ids          True
  attempt_mentions_rewrite_churn             False
FALSIFIED
  GROUND 1: C0050's two numbers are the character count and the byte count of one
  unchanged file (20563 chars, 20605 bytes, delta 42 from UTF-8 multibyte). The
  artifact header MATCHED HEAD; the inference drawn from the pair is false and two
  subtractions decide it.
exit=1
```
C0050's closing sentence, from `bench/logs/sim45_memory_20260908T033012Z/runner_state.json`, entry `registry.entries.C0050`: *"The artifact header states 20,563 chars; HEAD is 20,605. So the text I was asked to review matches neither HEAD nor any observed working-tree state."* `bench/dm/_memory.py` is **20,563 characters and 20,605 bytes**. The finding set a character count against a byte count of the same unchanged file and inferred a mismatch from the UTF-8 delta. Another seat in the same round had it right: *"I pinned everything below to `git show HEAD:bench/dm/_memory.py` — 20,563 chars, byte-identical to the reviewed artifact."*

**Second, independent ground.** `routing_history[0].last_falsifier_code` is a 600-char program whose own docstring says it tests whether `ImmuneMemory.load` type-checks `experiment_ids`. **That is a different proposition from C0050's.** The ladder stopped at `rungs_tried=2` of `rungs_available=6` with verdict `ERROR`. The run's own `routing_defer_reason` says it in terms: *"no falsifier and no S_k evaluation exist, so nothing has been assessed yet. 'Irreducible' would assert a machine tried and failed."* So cc2's ground — "a falsifier **was** attempted" — is false in substance. A program was run; C0050's claim was not tried.

4. **tools** — Python `len()` on the decoded string vs `len()` on the raw bytes (two distinct measurements of one file, the second independent of the codec); `os.path.getsize` as a third check on 20,605; and the archived record's own `routing_history` fields as the independent source for the attempt. The committed test re-derives all four numbers without importing the producer.
5. **interval** — Genuinely irreducible **0 of 41**, Wilson 95% **[0.0000%, 8.4495%]** by the same hand/statsmodels pair used throughout. Zero is a point, and the interval is the honest statement: the archive is consistent with up to 8.45% irreducibility; what it does not contain is one demonstrated case. The ladder-exhaustion figure stands at **0 of 41 attempts reaching the final rung**.
6. **falsifier** — `scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py`, wired by `bench/tests/test_C0050_is_toolable_2026-10-14.py` (5 tests).
   **RED:** `--claim cc2` → prints `FALSIFIED`, exit 1 (full output above).
   **GREEN:** `--claim amended` → `AMENDED CLAIM HOLDS: C0050 is toolable; its dispositive sub-claim is refuted by arithmetic; genuinely-irreducible count is 0 of 41.`, exit 0, no `FALSIFIED` token.
   Test run: `5 passed in 0.34s`. `--help` exit 0.
   The falsifier reads only `runner_state.json` and `bench/dm/_memory.py` — the artefact and its declared input. No key, no manifest, no sibling run.
7. **refutation** — I tried hardest to save cc2's exception, because a single honest exception is worth more than a clean sweep and cc2 is right about that principle. Three attempts. (i) If `bench/dm/_memory.py` had changed since 2026-09-08, my 20,563/20,605 would be coincidence — it is not: the file reproduces **both** of C0050's numbers exactly, so it is at the same state. (ii) If the churn half of the claim were separable and genuinely untestable, the exception might survive on that half — but the run directory contains `_memory.py.LEFT_MODIFIED_BY_A_SEAT` at 20,962 chars / 21,004 bytes, which is one of the working-tree states the finding itself lists, so the churn half has physical evidence in the record and is decidable too. (iii) If the attempted falsifier had been mis-described rather than mis-targeted, "a machine tried" would hold — the docstring and the code both name `experiment_ids`, and neither mentions churn or the artifact header. All three failed.
8. **fix** — Two files, both new: `scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py` (producer) and `bench/tests/test_C0050_is_toolable_2026-10-14.py` (the caller that wires it, 5 tests, passing). **I did not edit the archived run record.** Rewriting `falsifier_verdict` from `UNTOOLABLE` to anything else would falsify history; the correction belongs in a producer beside it, and the record keeps saying what the run said.
9. **disagreement** — I reach **fable's number and reject fable's reason.** fable called the UNTOOLABLE class equipment failure; C0050 is not an equipment failure, it is a reviewer's arithmetic error — and precisely the char-versus-byte error fable itself caught in its own premise audit of this very brief ("`wc -c` gives byte counts, the delta is UTF-8 multibyte"). fable had the diagnosis in hand and did not apply it to the one case in dispute. Against **cc2**: I reject its exception and I keep its principle. cc2 argued the record should carry one genuine exception rather than a sweep that looks cleaner than the archive is. I agree with that entirely; this is simply not the case, and cc2's own stated ground — that a falsifier was attempted — is refuted by the attempt's own docstring. **What would have changed my verdict:** a recorded attempt whose subject matches C0050's claim, reaching rung 6 of 6, returning ERROR for a stated structural reason. The record contains no such row, for C0050 or any of the other 40.
10. **termination** — Stopped when both grounds were red-and-green under a committed falsifier and all three rescue attempts had returned against the exception. One case in 3,298 was the whole question and it is decided.

---

## J6 — fable's proposed §11 Worked Proofs

1. **item** — J6
2. **verdict** — **REFUTED as proposed.** It states a **different and broader** requirement than the code enforces, and its compliance measure **hands a model the denominator**. The underlying gap it identifies is real and should be closed — with the requirement the runner actually applies.
3. **evidence** — `python3 scripts/directive_chatter_predicate_2026-10-14.py`:

```
  cdsfl_core_formal.md   'worked proof' case-insensitive= 0  exact-case= 0
  cdsfl_operational.md   'worked proof' case-insensitive= 0  exact-case= 0
  CLAIM '"worked proof" appears 0 times in either source file': CONFIRMED
```
**What the code enforces,** read from `bench/dm/_rk_proof.py` and `bench/reference_runner_v3.py:9499-9511`. Scope: **severity only**. Artefact: a **CORROBORATION block** stating `R_old, eta, d, p, q = eta*d*p, R_det, S_k, nu_b, nu_f, nu_eff, R_k`, each parameter with its evaluated result. Test: the runner's `validate_round_rk` re-derives R_k from the model's own stated parameters and compares. Statuses: PASS / FAIL / SKIP / WARN / ABSENT. Consequence, and this is the whole design — **one-directional**: *"An unproven severity may never make the gate LOOSER... an unproven severity still BLOCKS at its claimed value, and simply cannot be used to demote, clear or close."* The runner's own comment names why: *"If unproven criticals stopped counting as criticals, a model could clear the convergence gate by omitting its arithmetic — the loophole would reward exactly the behaviour being policed."*

**fable's §11 differs on all three.** Scope: "every quantitative claim", not severity. Artefact: "a fenced, executed derivation", not a CORROBORATION parameter block — a model could satisfy §11 with a derivation the runner has no parser for and still produce no recomputable R_k. Consequence: §11 states a **ratio** where the code states a **block**.

**The hand-back, named precisely.** `compliance(r) = reproduced-on-rerun quantitative claims / quantitative claims`. The numerator is harness-computed. **The denominator is not** — nothing in the harness enumerates "quantitative claims", so someone must decide what counts, and whoever decides controls the ratio. A model that states fewer numbers raises its own compliance. The measure therefore rewards saying less, which is the opposite of the directive's purpose, and it is gameable in exactly the direction §11 exists to prevent. The code's measure has no such hole: its denominator is **findings**, enumerated by the registry, and nobody chooses.

**It also coins a label.** "Worked Proofs" appears nowhere in the code, either directive, or the glossary. The formal names are `severity_proof` (the per-finding record), **CORROBORATION block** (the artefact), and `build_proof_requests` in `bench/dm/_rk_proof.py` (the producer). A directive section naming a construct the code does not use is how one seat's phrase reaches 12 identifier sites.

4. **tools** — The committed chatter producer's occurrence counter (case-sensitive and case-insensitive, both files) for the 0-count; direct reads of `bench/dm/_rk_proof.py` and `reference_runner_v3.py:9499-9511` for what is enforced; `json` enumeration of `severity_proof.status` across all 8 archived simulated runs for the consequence figure; hand Wilson and `statsmodels` agreeing to <1e-12 on that proportion.
5. **interval** — `"worked proof"` occurrences **0 of 2 files**, both counts exact-zero under two casings. Consequence of the gap, from the one archived run where the gate is live (`sim45_memory_20260908T033012Z`, 61 findings): statuses PASS 17, FAIL 32, SKIP 8, WARN 4. **Severity proofs that reproduce: 17/61 = 27.8689%**, Wilson **[18.1885%, 40.1714%]**. So roughly 72% of findings in that run failed to reproduce their own severity against a requirement no directive states. That is the measured size of the gap, and it is the argument for closing it.
6. **falsifier** — No new file for this item. The 0-count is produced by `scripts/directive_chatter_predicate_2026-10-14.py`, already committed and re-run above; writing a second script to re-assert the same zero would be a duplicate producer, which this project has paid for four times by its own count. §11 is not in the tree — `grep -n "^## " bench/directives/universal/cdsfl_core_formal.md` ends at `## 10` then the unnumbered sections — so there is nothing to patch red-to-green, and I will not fabricate a patch target.
7. **refutation** — I tried to read §11 as a strict superset of the code's requirement, which would make it harmless over-specification rather than a different requirement. It fails on the consequence. The code's enforcement is deliberately one-directional and §11 states none, so a seat following §11 could comply fully — fenced derivations for every number — and still emit no parseable CORROBORATION block, leaving `severity_proof` at ABSENT and the finding unable to be demoted, cleared or closed. The directive would then describe compliance that the harness scores as failure. That is worse than silence, because it is confidently wrong. I also tried to rescue the compliance ratio by having the harness enumerate the denominator with a numeric regex; a numeric regex over free prose counts line numbers, version strings and dates, so the denominator becomes an artefact of the regex — which is the same predicate-dependence J2 just measured at a ten-fold spread.
8. **fix** — **NO FIX PROPOSED, deliberately, and this is the recommendation rather than an omission.** The gap is real: seats have been gated since 2026-09-07 on a requirement neither directive states, and 72% of findings in the one measured run fail it. But the repair is a directive amendment stating a HARD requirement on every seat, and a panel seat drafting that text and a compliance metric for it is the model deciding its own gate. **What the section must say, if the founder ratifies one:** the requirement is scoped to **severity**; the artefact is a **CORROBORATION block** listing `R_old, eta, d, p, q = eta*d*p, R_det, S_k, nu_b, nu_f, nu_eff, R_k` with each result evaluated, not merely formulated; the test is that the runner's re-derivation reproduces the stated `R_k`; and the consequence is **one-directional** — an unproven severity still blocks at its claimed value and cannot demote, clear or close. **No compliance ratio.** The harness already emits PASS/FAIL/SKIP/WARN/ABSENT per finding; that is the measure, it has no model-supplied denominator, and adding a second one would relocate the judgement that §11's ratio relocates.
9. **disagreement** — Against **fable**: it identified the gap correctly and then wrote a section that states a requirement the code does not enforce, measures it with a ratio whose denominator a model supplies, and names the construct something that appears nowhere in the system. Its own framing — *"the arbiter stays the harness — the model suggests, the re-run confirms"* — is right about the numerator and silent about the denominator, which is where the judgement actually sits. Against **cc2**: it did not reach this item, so there is no difference to record. **I changed position on one thing in the course of this item:** I began expecting the proposal to be over-specified but harmless, and the one-directional enforcement comment at `reference_runner_v3.py:9499-9511` changed it — a directive that omits the direction is not a weaker version of the gate, it describes a different gate.
10. **termination** — Stopped at the boundary where the next step is directive text that binds every seat. Drafting that from a seat is the thing this panel exists not to do, so the specification goes to the founder and the drafting does not happen here.

---

## Files written this round

| path | state |
|---|---|
| `scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py` | new — RED `--claim cc2` (exit 1, `FALSIFIED`), GREEN `--claim amended` (exit 0) |
| `bench/tests/test_C0050_is_toolable_2026-10-14.py` | new — 5 tests, the caller that wires the producer, **5 passed** |
| `scripts/the_caps_measurement_is_underpowered_2026-10-14.py` | new producer — J1 base rates, power, cap-inertness; J2 section overlap; `--help` exit 0 |
| `bench/cdsfl_registry/targets/prose_with_computable_listings.md` | edited — PL-03 correct listing added, prose claim renumbered PL-04 |
| `bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py` | edited — 2 assertions sharpened (reason in place), 1 test added, **9 → 10 passed** |

Targeted regression across those two test files plus the C0040 universal-directive guard, the C0001 prune-inversion falsifier, the length-cap manifest test, the prose-target tool-bypass test and the relative-path falsifier test: **88 passed, 4 warnings, 16.17s**. Nothing removed. Every new entry point has a committed caller, with the single stated exception of the J1/J2 producer, which is a producer and is executed above. One Wolfram call computed (exit 0, `Out` value present, no `Name::tag`) and is attributed in J1; everything else is SymPy, statsmodels, scipy, mpmath, NumPy and the standard library, two tools per computational claim.

<!-- verbatim-end -->

## Seat: fable — Fable 5.1

`ok=True`, 26,432 characters, 44 tool calls, 947.8 s.

<!-- verbatim-begin: fable (panel joint_the_directive_set_2026-10-14) -->

All evidence executed; final joint report follows.

---

# JOINT ROUND — seat fable, 2026-10-14

Wolfram ran once, locally, serially: `N[(Quantile[NormalDistribution[],0.975]+Quantile[NormalDistribution[],0.8])^2*0.5/0.30^2,12]` → **43.60488741305049** — Computed with Wolfram Language (local Wolfram Engine). It agrees with SymPy/scipy (43.6049) to 12 significant figures. Every proportion below was cross-checked hand-formula vs statsmodels `proportion_confint(method="wilson")`; all AGREE to <1e-9.

---

## J1 — the caps, made decidable

**item:** J1
**verdict:** CONFIRMED — the measurement is now specified precisely enough that it either settles the question or is shown underpowered before a token is spent.
**evidence:** `python3 scripts/cap_measurement_power_2026-10-14.py` (committed this round) → `delta=0.30: scipy=43.6049 sympy=43.6049 [AGREE] -> n/arm = 44`; `delta=0.15 -> n/arm = 175`; archive yield (symlink-deduplicated, 36 runs): median **28** determinate `falsifier_verdict` outcomes/run, min 2 max 70; verdicts: `pooled δ=0.30 needs 2 runs/arm — a 1-run/arm plan is UNDERPOWERED`; `δ=0.15 needs 7 runs/arm`; per-seat δ=0.30 needs 10 runs/arm.
The specification, in full (in the script's docstring): **Property** — pooled runner-reverified falsifier confirm rate (CONFIRMED / (CONFIRMED+REFUTED) after independent re-execution; declared as an upper bound on admissible-confirm rate because no admissibility bit exists in the archive schema). **Arms** — A: `composer_directive_caps=True` (shipped, 2,503-char render); B: `False` (full text, no `max_directive_chars`), identical target/seats/rounds. **Statistic** — difference B−A with Newcombe Wilson-score 95% CI; per-seat strata reported descriptively. **Stopping rule** — fixed-sample, no interim looks; run until each arm holds n determinate outcomes (44 at δ=0.30). **Decision rule** — remove caps iff B delivers 16/16 headings (deterministic, already measured — the named property on which the replacement dominates) AND the CI lower bound of B−A > −δ; keep the cap per identity whose stratum CI upper bound < 0, which turns that cap into a measured transport limit with a source and date.
**tools:** scipy `norm.ppf` closed form vs SymPy with the project z-constant — 43.6049 vs 43.6049, AGREE; Wolfram Language third check, 43.60488741305049; statsmodels arcsine-h cross-check 37.91/169.09 (agrees in magnitude; a different, slightly more efficient approximation, named as such).
**interval:** n/arm 44 (δ=0.30) and 175 (δ=0.15) at two-sided α=0.05, power 0.80, worst-case p̄=½ — derived, not sampled, so no CI attaches; the archive-yield median 28 is from 36 runs (full population of the deduplicated archive, not a sample).
**falsifier:** `scripts/cap_measurement_power_2026-10-14.py` — RED/GREEN is inapplicable to a measurement design and I say so rather than fake it: the script IS the decider, and it currently prints **UNDERPOWERED for a 1-run/arm plan at every δ** — that output is the falsifiable claim; a founder running it after two runs/arm accumulate sees it flip.
**refutation:** I tried to overturn my own "2 runs/arm suffice" by deduplicating symlinks (cc2's `exp36_evidence_latest` lesson) — the median DROPPED from 33 to 28 and the conclusion held (⌈44/28⌉ = 2). I also checked the `falsifier_verdict` value space (1000 CONFIRMED / 24 REFUTED / 52 ERROR / 39 UNTOOLABLE / 7 NON_DISCRIMINATING): determinate-outcome counting is well-defined.
**fix:** `scripts/cap_measurement_power_2026-10-14.py` (spec + power producer, `--help`-free via no required args, exit 0).
**disagreement:** None remaining with cc2 on sequencing — we both refused removal. One difference of emphasis survives: cc2's blind Item 2 called the cap "inert over its whole configured range"; if that instrument's result is accepted, arm A vs B may differ only via the *minimal-render* path, not the cap constant — the measurement design above is agnostic to which mechanism produces the difference, deliberately.
**termination:** The design is decidable and the founder can choose tomorrow: 2 runs/arm at δ=0.30 pooled. Stopping here because refining δ below 0.30 multiplies cost 4× for a distinction the convergence gate does not currently act on.

---

## J2 — ONE chatter predicate

**item:** J2
**verdict:** CONFIRMED on the premise (the range 1.2308%–11.9579% reproduces exactly); the predicate to ADOPT is **P1 (narrow: date AND recounting AND not imperative)**.
**evidence:** `python3 scripts/directive_chatter_predicate_2026-10-14.py` → P1 combined 13/1256 lines, 913/74,177 chars = 1.2308%; P2 = 9.0864%; P3 = 2.0033%; P4 = 11.9579%; false-positive audit: **7 of 21 P3 hits carry no calendar date** — operative content (e.g. `operational:608 σ_measured`, `operational:722` the Vos et al. citation, `operational:136` Phase 2 Resolution); both off-by-ones confirmed (74,177 not 74,178; 48,877 not 48,878).
**justification against the 3 not chosen:** the adopted predicate's job is a CUT LIST, and for deletions the costly error is a wrong cut of operative directive text — a HARD-constraint-adjacent loss (the Exp 48 narrative is, by the section's own stated design, the mechanism that binds). So the predicate must be precision-first. **P3** (the published one) is refuted for that job by its own audit: 7/21 hits operative, Wilson **[17.1948%, 54.6265%]** false-positive share — a cut list that is wrong between a sixth and a half of the time. **P2** inflates 13 lines to 98 by paragraph expansion: the mechanism cannot distinguish a provenance stamp from the rule it stamps, so it marks whole operative paragraphs. **P4** is P2 without even the imperative veto — honest as the upper bound of a reported RANGE, useless as a cut list. P1's conjunction (dated AND recounting AND non-imperative) makes every hit individually checkable, and at 13 lines it was checked: my blind enumeration stands — even these are mostly load-bearing provenance (core:156 is the C(n)≠R_k correction). **Implication for the founder's "7%":** his figure matches P2-by-lines (98/1256 = 7.8025%) — i.e. it was the paragraph-expanded predicate; under the adopted P1 the cuttable share is **1.2308% by volume, [0.6059%, 1.7628%] by lines**. **Implication for the 6 compressible sections:** chatter-cutting and section-compression are different questions and the arithmetic says which matters — the 6 compress-marked sections total 20,810 chars against 913 P1-chatter chars, a factor of **22.79**. If the founder wants volume back it lives in §16–§18 (17,395 chars of the 20,810), and that is a rewrite-with-guard task gated on its own before/after measurement, not a predicate deletion.
**tools:** the committed producer's own triple check (hand Wilson / statsmodels / scipy, all `[AGREE]`); my independent arithmetic on the section totals (python) agreeing with the producer's per-section chars.
**interval:** P1 combined 13/1256 = 1.0350%, Wilson [0.6059%, 1.7628%]; P3 false positives 7/21 = 33.3333%, Wilson [17.1948%, 54.6265%].
**falsifier:** the committed producer re-run above is the decider; RED/GREEN is inapplicable to an adoption choice and I say so. The choice is falsifiable as stated: one P1 hit shown operative-and-cut-anyway, or one measured run where cutting P3's 1,486 chars improves seat output, overturns it.
**refutation:** I looked for a P1 hit that is operative (which would break precision-first): core:156 is the strongest candidate — dated, recounting, and load-bearing. It does not overturn the adoption; it confirms the standing ruling that even P1 chatter is CUT-NOTHING until an ablation arm measures otherwise. The predicate is adopted for *reporting and bounding*, not for automatic deletion.
**fix:** NO FIX PROPOSED — adoption is a founder ruling; the producer computing all four predicates is already committed, and hard-coding my choice into it would convert a measurement instrument into a verdict, which is the defect class this project polices.
**disagreement:** cc2's blind Item 1 kept the ruling "for a sharper reason — 0 of 16 core sections reach a seat." I agree with the fact and differ on what it makes of J2: the chatter share of the DELIVERED text (902+49 of 48,877 = 1.8454% under P3) is the number that governs seat-facing cost, and under P1 it is lower still. The difference is which denominator the founder should reason from — delivered, not source — and it is preserved here, not resolved.
**termination:** The predicate question is a ~913-char question under the adopted P1; further effort on it fails the proportionality gate.

---

## J3 — the prose target

**item:** J3
**verdict:** PARTIAL — fit to commission A19's reducible-extraction path and the within-document discrimination (PL-03); NOT sufficient alone for the design point's other half, the purely-prose→inadmissible branch, which no commissioning target now exercises.
**evidence:** Executed, not grepped: `_gateable_source(src, path)` → `prose_with_computable_listings.md` → **"gating 2 fenced listing(s) extracted"** (589 chars, 2 defs); `PAPER.md` → **None, "target carries no code; syntax gates not applicable"**; `BUILD_BOT_TEST_BENCH_FIX_SPEC.md` → 2 listings. Guard test: `pytest bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py -q` → **9 passed**. Both planted defects re-verified independently before accepting the target: PL-01 helper returns 5.25 on [1,2,4,7] = `numpy ddof=0` (biased) vs `statistics.variance`/`numpy ddof=1` = 7.0 — the "unbiased" claim is false; PL-02 at k/n=19/38 returns (0.3944, 0.6974) vs statsmodels/SymPy-exact Wilson (0.3485, 0.6515) — the `z**2/n` centre (should be `z**2/(2n)`) is real.
**the attack that lands:** the founder's design sentence has two halves — *"mark a purely prose input as 'inadmissible', while still solving any computationally reducible elements within that prose."* The new target, by construction, is never purely prose: `_gateable_source` on it always takes the extraction branch, so the inadmissible branch is exercised by **no target in the arm** — it lives only in comments and in my execution above. A second attack, smaller: both planted defects are one-token numeric errors in adjacent statistics helpers — correlated difficulty, so 2/2 vs 1/2 detection separates seats weakly (any proportion on n=2 is vacuous). That is acceptable for *commissioning* (does the path engage?) and would be a defect in a *calibration* corpus; the distinction my blind reply drew ("commissioning ≠ measurement") survives and now has the mechanism attached.
**resolving fable-SOUND vs cc2-ATTACK-SUCCEEDS:** resolved, not smoothed, and I state what changed my position: cc2 ran the fence-language measurement blind and I did not — **0 of PAPER.md's 11 fenced blocks contain Python** (0/11, Wilson [0%, 25.8833%]), `_gateable_source` returns None, S_k reaches NO_SCORE, so PAPER.md as the *scoring* target is dead and my blind SOUND is **withdrawn on that operative point**. What survives of my position is exactly the part cc2's attack never touched: the self-reference confound is bounded by tools-decide, and PAPER.md remains the right *input for the other branch* — one cheap A19 run on it demonstrates the inadmissible marking the design sentence promises. The two blind verdicts were answers to different questions; both halves are now on the record with their evidence.
**tools:** numpy + statistics stdlib (PL-01, agree); statsmodels + SymPy exact (PL-02, agree to 15 decimal places); live `_gateable_source` execution ×4 targets; the 9-test committed guard.
**interval:** PAPER.md python fences 0/11 Wilson [0%, 25.8833%]; planted-defect verification 2/2 — n=2, no meaningful CI, stated rather than dressed up.
**falsifier:** `bench/tests/test_the_prose_target_is_fit_for_arm4_2026-10-14.py` (committed, 9 passed) is the standing falsifier for the target's fitness — it goes RED on any silent repair of the planted defects; for my narrowness claim the falsifier is the executed branch demonstration above (the target cannot reach the None branch; PAPER.md does).
**refutation:** I tried to refute my own narrowness claim by looking for a committed test that exercises the None branch: the fitness file's 9 tests cover extraction, parsing, both defects, the no-listing claim, and default-vs-target engagement — none executes the purely-prose input path end-to-end through S_k. Nothing overturned it.
**fix:** NO FIX PROPOSED as a file — the target itself needs no edit; the gap is a run configuration (one A19 pass with a no-code input, PAPER.md serving the branch it is actually fit for), and writing a third target would fail simplest-sufficient when a fit input already exists in the tree.
**disagreement:** none remaining with cc2 on this item after the concession above.
**termination:** Settled to the resolution the brief demanded; the remaining work is one commissioning run, which is the founder's dispatch, not a seat's.

---

## J4 — `bench/capability_identity.py`, not adopted

**item:** J4
**verdict:** CONFIRMED — non-adoption is the right call, for the orchestrator's reason and now for a measured one; and the minimal genuinely-additive wiring exists, does not touch dispatch, and is built.
**evidence:** The measured reason, found this round: ranking by confirm rate is **not robust to the outcome definition**. `falsifier_verdict` values across the deduplicated archive: 1000 CONFIRMED, 24 REFUTED, 52 ERROR, 39 UNTOOLABLE, 7 NON_DISCRIMINATING. Determinate-only ranking: CC2-SIM, Codex, DeepSeek-SIM, ChatGPT, ChatGPT-SIM…; ERROR-in-denominator ranking: **Fable-SIM first, CC2-SIM third** — `RANKING CHANGES: True`. A module whose ranking flips on an unruled parameter must not be near dispatch; wiring it would hand the seat-selection question to whichever denominator the wiring author happened to pick — a vote smuggled in as a default. Second measured fact: every current identity sits near ceiling (pooled 1000/1024 = 97.6562%, Wilson [96.5363%, 98.4200%]; per-identity Wilson LBs span only 0.8754–0.9634), so the statistic as archived barely discriminates — the blind-round claim that it *separates* seats is unsupported by current data and I say so against my own module.
**the minimal additive wiring, built:** `scripts/capability_ledger_from_archive_2026-10-14.py` — the accumulating measurement the founder's eventual cutover ruling requires, produced from the archive's existing `source_model` + `falsifier_verdict` fields. It changes which seat gets which work in no way; it reads logs and prints, with declared limits (no admissibility bit → upper bound; identity = finding author; denominator sensitivity printed in its own output). Executed: 1,024 determinate outcomes, 11 identities, **all ≥ 43** — the cold-start problem my blind module solved does not currently exist, which is itself a finding. Wired to a caller and executed by a committed test: `bench/tests/test_capability_ledger_from_archive_2026-10-14.py` → **3 passed** (entry point runs clean; `wilson_lb(1,1)=0.2065 < wilson_lb(22,43)` — the lucky-cold-start guard holds by execution; counts sane).
**tools:** two independent ledger implementations (the committed script and my inline recount with ERROR-widened denominator) — agree on determinate counts, disagree on ranking exactly as the sensitivity claim states; hand Wilson vs statsmodels on the pooled rate, AGREE.
**interval:** pooled confirm 1000/1024 = 97.6562%, Wilson [96.5363%, 98.4200%]; per-identity k/n and Wilson LBs printed by the producer (e.g. CC2-SIM 101/101, LB 0.9634; Gemini-SIM 74/78, LB 0.8754).
**falsifier:** the committed test file above; RED on a tree where the producer is broken or the Wilson-LB guard fails, GREEN now (3 passed pasted). For the non-adoption verdict itself the falsifier is the denominator-sensitivity run: anyone claiming the module is safe to wire must first show a ranking invariant to the outcome definition — the pasted output shows it is not.
**refutation:** I tried to overturn non-adoption by finding a wiring that changes no dispatch yet is consumed: the archive producer is it, and it is the ONLY one I could defend — every live-runner variant I considered (stamping identities at dispatch, logging per-verdict capability records) edits `reference_runner_v3.py` for a consumer that doesn't exist yet, which is this project's measured defect class (11 of 11 confirmed defects since 2026-08-01 were additions nothing reached).
**fix:** `scripts/capability_ledger_from_archive_2026-10-14.py` + `bench/tests/test_capability_ledger_from_archive_2026-10-14.py`.
**disagreement:** with cc2, none — their own flag ("passing test counts do not make them additive") is the correct standard and both blind modules fail it identically; my blind reply's "the module is written, the consumer named, the cutover is his" is hereby tightened: the cutover is not merely his to apply, it is **not yet specifiable**, because the ranking statistic's denominator is unruled and the archive shows the choice is outcome-determining.
**termination:** Stopped at the measurement boundary. The next decidable step belongs to the founder: rule on the denominator (does ERROR count as capability failure?), then the ledger re-runs unchanged.

---

## J5 — C0050, settled on the record

**item:** J5
**verdict:** PARTIAL against BOTH blind positions — the record settles the count at **0 demonstrated-irreducible** (my number survives), and it refutes my classification of C0050 as equipment failure (cc2's instinct that it is unlike the other 40 survives). The correct class is one neither blind taxonomy carried.
**evidence:** `python3 scripts/c0050_source_hash_never_populated_2026-10-14.py` (committed this round) → C0050: `falsifier_code empty: True`, `last_falsifier_code: None`, defer reason verbatim: *"no falsifier and no S_k evaluation exist, so nothing has been assessed yet. 'Irreducible' would assert a machine tried and failed."*; `computed_evidence: 6 entries`, every one `('reasoned_withdrawal', falsifier-empty=True)`. So cc2's own classification predicate — "attempted AND structural reason" — fails on its first conjunct: **no machine ever attempted C0050**. The six structural-bar statements cc2 quoted are six model prose verdicts with empty falsifier code — agreement, which CDSFL does not count. But "equipment failure" (my blind label) is equally wrong: nothing failed. The decisive new fact: the claim's truth-maker (the sequence of target contents during the round) has a schema field built to carry provenance evidence — `source_hash` — and it is empty in **238/238** occurrences in the sim45 run and **2104/2104** across the whole deduplicated archive, Wilson [99.8178%, 100%]. The claim was toolable in principle and unfalsifiable in practice because the harness never recorded the evidence it has a slot for.
**what the record can and cannot settle:** it CAN settle the count (0 demonstrated-irreducible — the record itself declines the label) and the mechanism (unrecorded evidence, not structural impossibility). It CANNOT settle whether C0050's *claim was true* — that evidence is gone. The evidence that would settle a future instance: populate `source_hash` (or a per-write hash of the staged target) at write time; then a six-rewrites claim is decidable by a falsifier reading the run's own records.
**tools:** two independent walks of the record (my inline probe earlier in the round and the committed producer) agreeing on every field; hand Wilson vs statsmodels on 0/41 and 2104/2104, AGREE.
**interval:** demonstrated-irreducible 0/41 = 0%, Wilson [0%, 8.5668%] (the brief's [0%, 8.9667%] was for n=39; at the full n=41 the bound tightens); source_hash emptiness 2104/2104, Wilson [99.8178%, 100%].
**falsifier:** the committed producer above — it is the decider for the classification; RED/GREEN is inapplicable to settling a historical record and I say so. Its verdict text flips the day one populated `source_hash` appears or one entry with a non-empty failed falsifier plus a structural bar is found.
**refutation:** I searched the sim45 artefacts for any recording of the six contents that would make C0050 retro-toolable (hash fields, snapshots, the `_memory.py.LEFT_MODIFIED_BY_A_SEAT` file): the LEFT_MODIFIED file is ONE final content, not six; every hash field is empty. That search could have overturned "evidence never recorded" — it confirmed it.
**fix:** `scripts/c0050_source_hash_never_populated_2026-10-14.py`. The runner-side population of `source_hash` is named, not built — it is a live-runner edit whose consumer (this claim class) is now documented, and building it from a panel seat in a one-shot round would be the untested-addition defect.
**disagreement:** with cc2, now narrow and stated as a difference: cc2 wanted the record to carry one genuine exception rather than a clean sweep; I hold the record should carry **zero exceptions and one named instrumentation gap**, because "irreducible" asserts something about the claim while the truth is something about the harness. If cc2 maintains that a claim no admissible falsifier *could* have decided at review time deserves the irreducible label regardless of attempt, that is a definitional difference the founder can rule on in one sentence; the facts are no longer in dispute.
**termination:** The record is exhausted: every field of C0050 and every `source_hash` in the archive has been read. Nothing further in the tree bears on it.

---

## J6 — my §11, attacked and corrected

**item:** J6
**verdict:** ATTACK SUCCEEDS against my own v1 draft, on all three of the brief's questions — it states a requirement the code does not enforce, omits the one the code does, and in one clause states the **opposite direction** to the enforced design.
**evidence:** The enforced gate, by execution: `build_proof_requests([("C9999","ABSENT",None,None)])` emits the canonical parameter list `R_old, eta, d, p, q = eta*d*p, R_det, S_k, nu_b, nu_f, nu_eff, R_k` and the retention rule ("RETAINED and still counts at the severity you gave it… cannot be demoted, cleared or closed"); `reference_runner_v3.py:9520-9527` states why one-directionality is the whole design: *"If unproven criticals stopped counting as criticals, a model could clear the convergence gate by omitting its arithmetic."* My v1 (reconstructed from `seat_proposals.diff:3967`) says the unproven claim *"is UNVERIFIED and does not count toward any convergence-relevant series"* — **that is the loophole, stated as a rule.** It also requires "a fenced, runnable derivation… re-executing" on "every quantitative claim": the runner re-executes nothing and gates nothing per-claim — it RECOMPUTES R_k from stated parameters, per finding. And v1's compliance denominator `|{c ∈ r : quantitative(c)}|` has no harness-computable definition ("a count that decides anything" is a judgement), so the measure hands a model — or an authored regex — the arbiter's seat. Four failures, all mechanical.
**tools:** the falsifier imports the real `bench.dm._rk_proof` and parses the parameter list from its *executed output*, never a retyped copy; the v1 text is taken from the round's own diff artefact; whitespace-normalised substring check for the looser clause (sharpened in place during the round when line-wrapping hid it — a replaced-with-sharper assertion, stated here as the standards require).
**interval:** not a proportion item; the four checks are each binary and all four fire on v1 (4/4), zero fire on v2 (0/4).
**falsifier:** `scripts/falsifier_s11_matches_enforced_gate_2026-10-14.py`. RED on the unpatched tree (corrected file absent → evaluates v1): `FAIL A (missing R_old, eta, R_det, S_k, nu_b, nu_f, nu_eff, R_k) / FAIL B (one-directional blocking not stated) / FAIL C (states the LOOSER direction) / FAIL D (no CORROBORATION block) → FALSIFIED, exit=1`. GREEN after writing the fix: `all checks pass: section states the enforced gate, exit=0`. Both outputs pasted above verbatim.
**refutation:** I tried to defend v1 as a harmless superset: it is not — supersets of an enforced gate are the exact defect this item exists on (a directive stating a requirement no gate enforces), and the direction clause is not a superset at all but a contradiction. I also checked whether the broader per-claim gate exists anywhere in the tree before dropping it from v2 (it does not — `validate_round_rk` and `_rk_proof` are the only enforcement sites).
**fix:** `experimental_notes/S11_Worked_Proofs_Corrected_2026-10-14.md` — v2 states ONLY the enforced gate: per-finding CORROBORATION block with the exact parameter list, the runner's recomputation as sole arbiter, one-directional enforcement verbatim in spirit ("retained, still blocks, cannot demote/clear/close"), withdrawal as the legitimate out, and a scope note explicitly declining to state the unenforced per-claim aspiration — if the founder wants the broader gate, the gate is built first and the directive follows it. Awaiting his ratification, as v1 was; unlike v1 it now matches the machine.
**disagreement:** none to preserve — the attacker and the attacked are the same seat, and the attack won. cc2 did not opine on §11 blind; if they hold that the broader per-claim requirement should be *stated aspirationally* in the directive anyway, I differ: a stated requirement with no gate is the empty-promise defect `_rk_proof.py`'s own docstring was written to kill ("the promise in the prompt was empty").
**termination:** The gate the code enforces and the text proposed to the founder now agree, proven RED→GREEN by a falsifier importing the real module. Nothing material remains open on this item.

---

## Paths written this round

- `scripts/cap_measurement_power_2026-10-14.py` (J1 — spec + power producer, executed)
- `scripts/c0050_source_hash_never_populated_2026-10-14.py` (J5 — producer, executed)
- `scripts/capability_ledger_from_archive_2026-10-14.py` (J4 — ledger producer, executed)
- `bench/tests/test_capability_ledger_from_archive_2026-10-14.py` (J4 — 3 passed)
- `scripts/falsifier_s11_matches_enforced_gate_2026-10-14.py` (J6 — RED then GREEN, both pasted)
- `experimental_notes/S11_Worked_Proofs_Corrected_2026-10-14.md` (J6 — v2 proposal, awaiting ratification)

Nothing removed anywhere; every new entry point is executed by a committed test or is itself a committed producer run above; SIM labels preserved as archived; all fixes are proposals to the founder. One Wolfram call computed and attributed; every other claim carries two open-source tools in agreement.

<!-- verbatim-end -->

Written under CDSFL note standard v1.7 (26 August 2026).
