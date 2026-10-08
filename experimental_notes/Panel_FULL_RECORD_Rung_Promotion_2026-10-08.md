# Earned rungs and opaque model identifiers: the free panel in full

Record written 2026-10-08T02:59:20+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED. The founder's design for how a model with no track record earns its way up a routing ladder, and his proposal that models be keyed by opaque unique identifiers rather than by name. Neither is built. Three committed artefacts carried the analysis: the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py, the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py, and the live ladder in routing.py.

WHY. A pure sort over measured capability cannot start, because on the first run every model's lower confidence bound is exactly 0.0 and the ordering is a total tie. An earlier panel answered this by keeping the hand-written strength tuple as a cold-start tie-break; that answer is right for 6 models and fails at scale, because a 6-name tuple orders 6 of 70 and 6 of 700. The founder's rung ladder is the first proposal that gives a zero-credit model a route to measurement, and his opaque-identifier proposal removes the naming prior while fixing a live fault: no unique stable identifier for a model exists in the project today.

HOW THE ROUND RAN. 2 free seats, 0 paid, star topology, blind round, dispatched 02:28:39. cc2 answered with 16,743 characters, 2,461 words and 33 tool calls in 1001.0 s on its first attempt; fable with 10,187 characters, 1,447 words and 22 tool calls in 600.9 s on its first attempt. 8 figures were declared in the brief and every one re-executed before dispatch.

THE BRIEF CARRIED A MISATTRIBUTION, AND IT IS RECORDED HERE RATHER THAN HIDDEN. It was dispatched before the founder clarified that he never intended promotion on a single success, so it attributes a one-success rule to him and builds a quantitative case against it. Both seats caught the consequence independently. The round was NOT withdrawn, because by the time the clarification arrived cc2 had already landed, and because the brief had instructed each seat to find where its framing was wrong -- which both did, on this point and on others.

WHAT WAS DONE WITH THE FINDINGS. Nothing is merged into the canonical tree. Both seats delivered fixes as files with executed falsifiers in their own sandbox trees, harvested to experimental_notes/seat_evidence/. CC1 corrected 4 defects in its own committed scripts that the seats found: a Wilson interval on exact arithmetic, a difficulty check that scanned field names instead of executing route, a cold-start price computed at the modal outcome with about 50 percent power, and a claim that rotation costs no extra dispatches.

THE SEATS DISAGREE ON 3 POINTS AND THE DISAGREEMENTS ARE PRESERVED. On the censoring of recorded depth, cc2 finds it right-censored by the cap while fable finds it left-censored by strongest-first ordering; both are correct about different mechanisms, and together they imply difficulty cannot be measured without both removing the cap and varying the order. On the derived promotion parameters, cc2 returns 19 attempts per rung with 14 successes at a floor of 0.50 while fable returns 12 with 8 at an implied floor near 0.39, each claiming minimality under its own stated targets, so the open question is which targets the founder sets rather than which arithmetic is right. On the identifier, both reject random assignment in favour of a digest over the output-affecting configuration, which contradicts the founder's wording while serving his stated intent.

THE SHARPEST SINGLE FINDING came from fable: the founder's phrase "stay on the same simpler problem resolution rung" admits 2 readings, and they fail in opposite directions. Under an absorbing reading a good model is excluded by luck; under a retry reading every model with any nonzero success rate reaches the top eventually, so the rule excludes nothing. The root defect is an uncalibrated criterion rather than the direction of its failure, and one sentence from the founder settles which reading he intended.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# A rung ladder earned by demonstrated capability, keyed by opaque model identifiers: review the design and fix the promotion rule

## What you are reviewing

The founder's design for how a model with no track record earns its way up a routing ladder, and his proposal that models be keyed by opaque unique identifiers rather than by name. Neither is built. Three committed artefacts carry the analysis and all are runnable:

- `bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py`
- `bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py`
- `bench/routing.py`, which holds the live ladder and `RoutingResult`

Run each of them. Several figures in this brief were wrong on a first attempt and were corrected by measurement, so take none of them on trust.

## The design, in the founder's own words

On identifiers: *"We don't need the model's names if we just assign each model in the roster a unique model ID! ... if you have 5 models from the same company, or that are the same model, the only way to tell them apart is through a randomly assigned model ID. Similarly trying to keep a record of 70, or 700 hundred model names would quickly become a nonsensical mess!"* And: *"No new model is inherently trusted, so yes it gets its own unique model ID."*

On promotion: *"new models get tried out on simpler tasks. If they succeed in simpler tasks they are granted an attempt to climb the ladder. If they then succeed in that more complex task, they climb the ladder again, if they fail they either stay on the same simpler problem resolution rung, or if they fail on any more complex task/rung on the ladder, they stay on the last rung where they demonstrated success. Tasks in this sense become increasingly harder, until finally only the most capable (and usually most expensive) models get to deal with the most complex problems."*

His constraint on all of it: *"That does not/should not contradict the premise, that models with demonstrated capability get given tasks in accordance with their demonstrated capability."* And his earlier framing, which forbids excluding a weak model rather than placing it: *"even if a model can do no better than a standard 6 dollar calculator, then we use it for the kind of tasks that kind of capability is best suited for ... even an old 386 computer is still capable of doing work that is beyond many humans."*

## Why the design is needed, and what it fixes

A pure sort over measured capability cannot start. On the first run every model's lower confidence bound is exactly 0.0, so the ordering is a total tie. A previous panel answered this by keeping the hand-written strength tuple as a cold-start tie-break, and its arithmetic was right for 6 models and wrong at scale: the 6-name tuple orders 100.0000% of a 6-model roster, 8.5714% of 70 and 0.8571% of 700, with everything past it ordered by nothing but input order.

Opaque identifiers fix 3 separate defects at once, and the third is a live fault rather than a preference. First, an identifier carries no prior, so it cannot smuggle in a judgement that one vendor beats another. Second, identifiers are generated rather than written, so an arbitrary roster size needs no hand-maintained list. Third, **the project currently has no unique stable identifier for a model at all**: `model_id` in `bench/experiment_11_orchestrator.py` occurs 12 times with only 10 distinct values -- `opus` and `gpt-5.5` each appear twice -- so it collides and cannot key a capability record; and it carries a vendor version in 9 of those 12, so it is not stable across a vendor release.

## What this brief has already measured, and what you must fix

**The promotion criterion is asymmetric in the wrong direction.** Under promote-on-one-success with 5 rungs, a model whose true per-rung success rate is 0.90 reaches the top rung only 59.049% of the time, so it is kept out 40.951% of the time by luck alone. A simulation over 20000 trials returns 0.4101, Wilson [0.403301, 0.416933], agreeing with the closed form. Meanwhile a useless model at 0.10 reaches the top only 0.001% of the time. So the rule does not mainly admit bad models; **it mainly excludes good ones**, and it contradicts the founder's own requirement that *"simply counting when a model is successful"* is not an improvement in capability.

**And the obvious repair over-corrects.** Replacing the single success with a Wilson lower bound over 10 attempts at a floor of 0.50 requires 9 successes per rung, and a genuinely 0.90 model then reaches the top only 21.611302% of the time -- worse than the rule it replaces. State what attempts-per-rung and floor should be, and **derive them from a stated false-negative target** rather than choosing them. If you believe no such calibration exists, say so and say why.

**The absorbing rung contradicts bidirectionality.** If a failure permanently fixes a model at its last successful rung, then the 40.951% of good models capped by luck are capped forever, which contradicts the founder's rule that a model losing capability must be able to regain it. Say what re-test schedule restores bidirectionality without letting a model climb on noise, and what it costs.

**Difficulty appears not to need a classifier, and you should check that.** The founder's ladder needs tasks ordered by difficulty BEFORE a new model is placed, while a previous panel argued difficulty is emergent and retrospective -- a finding is hard because everything better already failed. `RoutingResult` in `bench/routing.py` already records `rungs_tried` and `model_used` per finding, so the depth at which a finding was actually resolved is available today as a measured difficulty label. Verify that this reconciles the two, or show that it does not.

## Open questions you must answer

1. Does a model that fails at a rung lose its place at the rung below, and if not, what stops a model accumulating rungs it can no longer hold?
2. A new vendor release: same identifier inheriting the record, or a new identifier at 0 attempts? The founder's bidirectional rule says a model climbs on demonstrated improvement, which appears to force a new identifier, but say what that costs and whether anything is lost.
3. With the depth cap removed every model is eventually tried on every finding, so a new model gains measurements on hard findings for free, at the back of the order. Does the rung ladder then govern PRIORITY only rather than eligibility, and if so does it still need rungs at all?
4. 5 models from one vendor, or 5 instances of the same model: what must the identifier be derived from so that 2 genuinely identical configurations are not merged and 1 configuration is not split?
5. Rotation was proposed as the tie-break while bounds are tied, because a deterministic identifier order starves everything past the cap: measured over 400 findings with 12 models and a cap of 2, identifier order left **10 of 12** models with 0 attempts, Wilson [0.5520, 0.9530], while rotation gave every model 66 or 67 at identical dispatch cost. Does rotation compose with the rung ladder, or do they conflict?
6. The founder's position on timeouts is that output should be harvested when a model is done rather than at an arbitrary wall clock. An idle timeout was demonstrated against a fixed cap: a slow-but-working process was killed at 5.0 s with 0 lines by a total cap but completed in 8.1 s under an idle cap, and a genuinely hung process was caught in 3.1 s by the idle cap against 20.0 s by the total cap. Is an idle timeout on the stream the right mechanism, and what breaks it?

## Required: fixes, not only findings

For every problem you raise, propose a repair, write and EXECUTE a falsifier for it, and deliver each fix as a file at its real path in your sandbox repository tree. A fix you have not run is a hypothesis. Where a fix needs a parameter, derive the parameter and show the derivation; do not choose it.

## Output

Return these fields by name.

- VERDICT on the design as a whole: sound, sound with repairs, or unsound.
- FINDINGS, each with file and line, each marked OBSERVED with the command that shows it or HYPOTHESISED with what would settle it.
- FIXES, one per finding, each delivered as a file with the falsifier you executed and its output.
- YOUR STRONGEST DISAGREEMENT with this brief's own framing. Earlier briefs in this series were wrong about a correlation, about a rate, and about the span of a sensitivity analysis, and each error was found by a seat rather than by the author. Assume this one is wrong somewhere and say where.
- WHAT WOULD REFUTE YOUR OWN POSITION, as a measurement someone else could run.
- CONFIDENCE, with the evidence that sets it.

## Termination

Stop when every question above has either a fix with an executed falsifier or an explicit statement that it cannot be answered and why. Stop early if 2 consecutive passes over your own answer produce no new finding above the threshold of real-world consequence. Diminishing returns is a reason to stop; length is not a virtue.

<!-- figure: good_model_kept_out_by_one_success_rule | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.40951 -->
<!-- figure: bound_gate_overcorrects | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.21611302 -->
<!-- figure: absorbing_rung_caps_good_models | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.4101 -->
<!-- figure: tuple_share_at_70 | bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py | 8.5714 -->
<!-- figure: tuple_share_at_700 | bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py | 0.8571 -->
<!-- figure: good_model_reaches_top_one_success | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.59049 -->
<!-- figure: absorbing_cap_wilson_low | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.403301 -->
<!-- figure: absorbing_cap_wilson_high | bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py | 0.416933 -->


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 33 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel rung_promotion_and_model_ids_2026-10-08) -->

All 35 falsifiers pass. Wolfram (local Wolfram Engine, exit 0, `Out` values present) independently confirmed `0.9^5`, the n=19/k=14 binomial tail, `(0.95)^(1/5)`, and the derived window z.

## VERDICT

**Sound with repairs.** The three load-bearing design decisions survive falsification: opaque content-addressed identifiers, a rung ladder that *places* rather than excludes, and measured difficulty from resolution depth. Four of the brief's own diagnoses are wrong, and two of its figures are unreachable as stated.

## FINDINGS

**F1 — OBSERVED — the brief's central claim "the obvious repair over-corrects" is an invalid comparison.** `bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py:71-73`. The bound gate is compared to the one-success rule on true-positive rate alone, while their false-positive rates differ by 8 orders of magnitude (3.125e-02 vs 1.430e-10 at p=0.50). Two points on different ROC curves cannot be ordered. Scanned over n≤30 and floor∈[0.05,0.95], **138 bound-gate parameterisations beat the one-success rule on *both* rates simultaneously**; cheapest is n=4, floor=0.20, k\*=3 → TPR 0.764459 vs 0.590490, FPR 2.980e-03 vs 3.125e-02. The defect is the parameterisation, not the mechanism.
`python3 -m pytest bench/test_promotion_gate.py -k dominates -s`

**F2 — OBSERVED — why n=10/floor=0.50 fails specifically.** Same file, `:85-88`. It forces k\*=9, an implied point-estimate threshold of **exactly 0.90 = the good model's true rate**, putting the test at its own coin-flip point. That is the entire source of 0.736 per rung and 0.21611302 overall.

**F3 — OBSERVED — power is non-monotone in n, so no closed form may be used.** `successes_required` steps, so n=16 gives Q(0.90)=0.982996 while n=18 gives 0.971806 — *more attempts, worse power*. Any derivation must scan.

**F4 — OBSERVED — re-testing a fixed-z gate is an uncorrected sequential test.** The absorbing rung must go, but naive re-reading replaces it with a worse fault: a p=0.50 model clears a floor of 0.50 somewhere in 190 attempts with probability **0.6468**, Wilson [0.6318, 0.6614], against a single-shot 0.0318. Bidirectionality without a multiplicity correction admits models on noise.

**F5 — OBSERVED — `rungs_tried` is right-censored and is not a difficulty label as claimed.** `bench/routing.py:209` (`_budget = len(list(rungs)) if not max_rungs else max_rungs`) and `:321` (DUPLICATE returns `rungs_tried=0`). Measured against the real `route`: a finding whose true depth is 4 reports `rungs_tried=2` under the default `max_rungs=2`, indistinguishable from one resolved at rung 2. The artefact's claim 4 (`:139-162`) validates this by AST-scanning *field names* — it never executes `route`, so it would report `records_resolution_depth: True` whatever the values are.

**F6 — OBSERVED — Wilson intervals on deterministic quantities, twice.** `bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py:97` puts Wilson [0.039877, 0.174657] on `min(6,N)/N`, which is exactly 6/70 on every evaluation — no estimator, no sampling variability, no referent. The brief repeats the error on its own figure 5: the starved set under a fixed order and a fixed cap is identical across independent seeds, so "Wilson [0.5520, 0.9530]" on 10/12 has no referent either.

**F7 — OBSERVED — "the measured price of cold start" is a modal estimate with ~50% power.** `:55-62` evaluates separation at `round(p*n)`, the modal outcome. Achieved separation probability at the artefact's own n: **0.507** at gap 0.40 (n=21), **0.474** at gap 0.20 (n=88). The true 80%-power n is 37, 67, 155, 650 — **1.63×–1.86× the reported price**.

**F8 — OBSERVED — the brief's `model_id` diagnosis names the wrong mechanism.** `bench/experiment_11_orchestrator.py:131,168,188,192,200`. The brief's "12 occurrences, 10 distinct, so it collides" comes from matching the `model_id` *suffix*, which also captures `secondary_model_id`. Separated: `model_id=` is 6 occurrences, **6 distinct — no collision**; `secondary_model_id=` is 6/5 distinct, and the repeat (`gpt-5.5`, lines 188 and 200) reaches the same api, so it is one model named once, which is correct. The real defect is the opposite — a **split**: 4 models carried under two strings each (`opus`, `gpt-5.5`, `gemini-3.1-pro-preview`, `deepseek-v4-pro`), so a string-keyed record divides one model's evidence in two. The brief's conclusion (`model_id` cannot key a capability record) stands; its stated reason does not.

**F9 — OBSERVED — the brief's figure 5 "66 or 67" is unreachable by the obvious rotation.** 800 slots over 12 models is 12·66+8, so the maximally even allocation is 8 models at 67 and 4 at 66. A contiguous window advanced by **1** gives {66, 67, 68}, spread 2. Only advancing the offset by **`cap`** gives {66, 67}. The figure is right about the target and silent about the step size that reaches it.

**F10 — OBSERVED — "identical dispatch cost" is false under the real routing semantics.** `resolve_via_routing` returns on first CONFIRMED (`bench/routing.py:220`). Attempts *offered* are equal (800 either way); attempts *dispatched* are **579 for 270 resolved under rotation vs 444 for 396 resolved under strength order**. Rotation costs 30% more dispatches and resolves 32% fewer findings at the same cap. It buys coverage, and it is not free.

## FIXES

### `bench/promotion_gate.py` + `bench/test_promotion_gate.py` (F1–F5)

The parameters are **derived from a stated false-negative target**, not chosen.

Rungs are independent gates, so P(top) = Q^R. Requiring Q^R ≥ 1−β gives the per-rung requirement Q ≥ (1−β)^(1/R). At β=0.05, R=5: **Q ≥ 0.9897937816869885** — the per-rung gate must be far tighter than the end-to-end target, which is the compounding the one-success rule ignores. Scanning n for the smallest value where P(Binom(n,0.90) ≥ k\*(n,0.50)) ≥ that:

```
attempts_per_rung: 19       successes_per_rung: 14
per_rung_pass_achieved: 0.9914069792621538
p_reaches_top: 0.9577669784926826        attempts_to_climb: 95
```

So **n=19, k\*=14, floor 0.50** — not 10, and 19 is the smallest such n (the falsifier checks every smaller n). The floor stays 0.50 because "resolves more than it fails" is a semantically grounded rung threshold; `derive_attempts_per_rung` refuses (`ValueError`) rather than returning a number when p_good ≤ floor.

For bidirectionality, `RungRecord` is a sliding window re-read on every attempt: promote on Wilson **lower** bound > floor, demote on Wilson **upper** bound < floor. No absorbing state, **no re-test schedule at all** — the re-test is the ordinary dispatch stream. The window z is derived from the multiplicity of W−1+1 overlapping decisions over a horizon: Bonferroni gives **z = 3.440148** (Wolfram-confirmed), at which measured FP(p=0.50 over 190) = **0.0185 ≤ 0.05** and TP(p=0.90 over 190) = **1.0000** — the correction costs the capable model nothing.

Window versus pooled record was **measured, not judged** (composability rule). On a 0.90 → 0.30 capability drop, attempts to demote: **window median 20.0, never-detected 0.0000; pooled median 298.0, never-detected 0.0007**. The window dominates on the named property at no cost, so it is used alone — the two are *not* composed.

```
  138 gates dominate one-success on both rates; cheapest cost=20 n=4 floor=0.2 k*=3 TPR=0.764459 FPR=2.980e-03
  n=10 gate FPR at p=0.50: 1.430e-10 vs one-success 3.125e-02
  derived n=19 k*=14 P(top|0.90)=0.957767 cost=95
  non-monotone: n=16 Q=0.982996 > n=18 Q=0.971806
  P(p=0.50 promoted somewhere in 190) at z=1.96: 0.6468 Wilson [0.6318, 0.6614]
  derived z=3.440148 (k*=17): FP=0.0185 <= 0.05; TP(p=0.90)=1.0000
  demote after 0.90->0.30: window median 20.0 never 0.0000; pooled 298.0 never 0.0007
  promote -> demote -> re-promote on one record, no schedule needed
  capped: rungs_tried=2 -> depth=2 censored=True | exhausted: rungs_tried=4 -> depth=4 censored=False
  share at N=70 is exactly 6/70=0.085714 every evaluation, yet Wilson [0.039877, 0.174657]
  gap=0.40: artefact n=21, achieved separation probability 0.507
```

`observed_difficulty(result, max_rungs)` returns `(depth, censored)`, so a capped depth enters any ordering as a **lower bound** and never as an equality.

### `bench/model_identity.py` + `bench/test_model_identity.py` (F8, Q2, Q4)

`model_uid = "m-" + blake2b(canonical(dispatch_determining_fields))[:16]`. Canonicalisation sorts keys and normalises integral floats, so dict order and `8192` vs `8192.0` cannot split one configuration; only the 8 fields that change the output distribution enter, so an edited comment or display name cannot split it either. All 8 move the uid; 5 instances differing only in temperature stay 5 records; no vendor substring appears in any uid.

```
  12 literal model_id assignments, 10 distinct; colliding: {'opus': 2, 'gpt-5.5': 2}
  primary model_id: 6 occurrences, 6 distinct   secondary_model_id: 6 occurrences, 5 distinct
  SPLIT: one model under 2 strings ['deepseek-v4-pro','gemini-3.1-pro-preview','gpt-5.5','opus']
  one configuration listed twice -> 1 uid(s), indices [[0, 1]]
  m-035a1e68596b3c53 -> m-4585533de252e2ec (both records retained)
  cost of starting over: 95 attempts (19/rung x 5 rungs)
```

### `bench/stream_idle_timeout.py` + `bench/test_stream_idle_timeout.py` (Q6)

Idle timeout on the stream, **plus** a ceiling — and the composition is justified by measurement, not by coexistence. Idle-only never ends a hung process that keeps talking (a 0.2 s retry-print loop under a 1.0 s idle cap runs to the ceiling, 13 lines); ceiling-only kills slow-but-working (1.5 s cap, `DONE` lost). Composed: slow work → `exit`, chatty hang → `ceiling`, silent hang → `idle` at 1.01 s. Block buffering is defeated by forcing `PYTHONUNBUFFERED=1` in the child and treating process exit, not stream silence, as end-of-stream — otherwise the idle timer reads a healthy buffered writer as idle.

The ceiling is derived, and the **sample size needed to derive it is itself derived**: the one-sided allowance on the (1−kill_budget) quantile must be smaller than kill_budget, giving m > z²q(1−q)/kill_budget² → **m ≥ 73 at kill_budget=0.05, m ≥ 16 at 0.20**. Below that the function returns the observed maximum — erring long, which preserves work. (My first version silently saturated; the falsifier caught it.)

```
  silent hang: idle at 1.01s
  chatty hang (prints every 0.2s, idle cap 1.0s): ceiling at 2.51s, 13 lines
  block-buffered writer under idle cap 1.0s: exit at 1.87s, 6 lines
  composed: slow work -> exit; chatty hang -> ceiling
  runs needed before a ceiling sits below the observed max: 73 at 0.05, 16 at 0.20
  m=400: ceiling 37.11s < max 84.0s; would kill 0.0275 of legitimate runs
```

### `bench/test_rotation_composes_with_the_rung_ladder.py` (F6, F9, F10, Q3, Q5)

```
  identifier order, cap 2: 10 of 12 models at 0 attempts; starved set identical across seeds: True
  attempts OFFERED -- rotate by 1: [66,67,68] (spread 2); rotate by CAP=2: [66,67] (spread 1)
  attempts DISPATCHED (first-CONFIRMED stop) -- rotation 579 for 270 resolved;
                                                identifier order 444 for 396 resolved
  rung-2 holders (window 19, k*=14): ['m00','m01','m04']
  rung-2 dispatches: [267, 267, 0, 0, 266, 0, 0, 0, 0, 0, 0, 0]
  ladder 1.103 dispatches/finding | rotation 2.035 | reversed ladder 4.225
```

## OPEN QUESTIONS

1. **No** — a failure at rung r+1 does not touch rung r's record; the falsifier shows a model at 18/19 still promotes, so one unlucky failure caps nothing. What stops accumulation is that **a rung is held, not granted**: the same window record that promoted demotes when the upper bound falls below the floor.
2. **New identifier at 0 attempts**, and it is forced rather than chosen — the vendor slug is a dispatch-determining field, so the content address changes. Cost: **95 attempts** to re-climb at β=0.05. What is lost is the prior record, which stays attached to the old identifier; that is what makes a regression visible as two records rather than one moving average. Inheriting it would assert the new release is at least as capable as the old — the judgement the founder's rule forbids.
3. **Both, and rungs are still needed.** Eligibility becomes unbounded, but `resolve_via_routing` returns on first CONFIRMED, so order decides cost: **1.103 dispatches per finding under strength order, 2.035 under rotation, 4.225 reversed**. Rung order is worth 3.8× against its inverse. Rungs govern priority, and priority is where the money is.
4. The **canonicalised dispatch-determining configuration** — provider endpoint, model slug, and every sampling/system/tool parameter — hashed. Not the roster entry (splits one config listed twice) and not the vendor name (merges two configs of one model). Five instances differing only in temperature stay five records; the same config in two files is one.
5. **They compose, on different axes**: rungs decide eligibility, rotation decides order among eligible ties. Verified mechanically — rotation never hands rung-2 work to a non-holder, and the ladder reinstates no starvation among holders. But rotation is **not free** (F10), so it belongs at the *tie-break* only, which is where the brief put it.
6. **Idle timeout is right, and insufficient alone.** It breaks on a chatty hang and on block-buffered output; both are fixed above.

## YOUR STRONGEST DISAGREEMENT WITH THIS BRIEF'S FRAMING

**"And the obvious repair over-corrects."** This is the brief's pivot, and it is a single-point comparison across two operating curves. The bound gate's false-positive rate at n=10 is 1.43e-10 against the one-success rule's 3.125e-02 — the gate was not over-correcting, it was *mis-parameterised*, and 138 parameterisations dominate the rule it supposedly loses to on **both** error rates at once. The brief then instructs: "derive them from a stated false-negative target rather than choosing them" — which is correct, and which, once done, yields n=19 at P(top|0.90)=0.9578. The brief had the cure in its own next sentence and filed the diagnosis under the wrong heading.

Secondary: the brief applies Wilson intervals to three deterministic quantities (tuple share, starved-model count, and by extension any fixed-order/fixed-cap allocation). An interval on a quantity with no estimator reads as measured uncertainty to the next reader and is nobody's uncertainty.

## WHAT WOULD REFUTE MY OWN POSITION

1. **p_good=0.90 is inherited from `bench/routing.py`'s Exp-42 note, not re-measured.** Run `scripts/competence_provenance.py` over the Exp-42 report and re-estimate the top-of-roster per-finding resolve rate. If the true p_good is ≤ 0.75, n=19 against floor 0.50 collapses (Q(0.75)=0.57, P(top)=0.06) and the floor, not n, is the parameter to move.
2. **Rung attempts are independent in my model.** If a model's successes at a rung are positively correlated (same finding family, shared prompt), the effective n is smaller than 19 and every figure here is optimistic. Measure the intra-model intra-rung success autocorrelation on logged `RoutingResult` streams; if the lag-1 correlation exceeds ~0.2, n must be inflated by the design effect 1+(n−1)ρ.
3. **The window/pooled comparison used one drop profile (0.90 → 0.30 after 100 attempts).** Sweep the drop magnitude and onset. If a shallow drop (0.90 → 0.60) is detected no faster by the window than by pooling, pooling is simpler and should win.

## CONFIDENCE

**High on the arithmetic, medium on the calibration.**

High: 35 falsifiers executed against the real modules, zero retyped targets; four figures independently confirmed by Wolfram Language (local Wolfram Engine) at exit 0 with `Out` values present; F1, F5, F8, F9, F10 are deterministic and reproduce exactly on re-run; F6's deterministic-interval claim is shown by identical output across independent seeds.

Medium on calibration, for one reason I can name: `p_good=0.90` and `floor=0.50` are inherited rather than re-measured here, and n=19 is sensitive to both (n=16 and n=18 bracket the requirement non-monotonically). The *method* — scan n against (1−β)^(1/R) — is settled; the *number* moves with p_good, and refutation (1) above is the measurement that would move it.

Two honest limits. The rung-2 falsifier shows m02 (true p≈0.77) failing the gate while m04 (p≈0.62) passed: W=19 is calibrated to separate 0.90 from 0.50 and does **not** reliably order models in between — per F7, separating a 0.15 gap needs roughly 155–350 attempts, not 19. And `derive_window_z`'s Bonferroni bound is conservative (measured 0.0185 against a 0.05 target), so it is tighter than necessary; it errs in the direction a bound should, but a measured-crossing calibration would recover power if the climb cost ever matters.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 22 recorded tool call(s).

<!-- verbatim-begin: fable (panel rung_promotion_and_model_ids_2026-10-08) -->

Two passes over my own work produced no new material finding. Final answer.

---

## VERDICT

**Sound with repairs.** The direction is right on all three pillars — earned rungs, opaque identifiers, measured difficulty — but the promotion criterion is uncalibrated under *either* reading of the founder's words, the identifier must be **derived, not random**, and the brief's difficulty-reconciliation claim is materially overstated.

## FINDINGS

**F1 — The promotion criterion fails in opposite directions depending on an unstated assumption.** `bench/the_promotion_ladder_needs_a_bound_not_a_success_2026-10-08.py:46-68`. OBSERVED: `python3` run reproduces 0.59049/0.40951; my check shows that under the retry reading ("stay on the rung" = keep receiving its tasks), P(ever top) = 1 for any p > 0 (geometric waits, E[attempts] = R/p: 5.6 for p=0.9, 50 for p=0.1) — the rule then excludes *nothing* and the ladder is a monotone ratchet. Either reading breaks it; the root defect is an uncalibrated criterion, not the asymmetry's direction.

**F2 — The absorbing rung contradicts bidirectionality.** Same file:109-136. OBSERVED: simulation 0.4101, Wilson [0.4033, 0.4169], closed form 0.40951 — agrees.

**F3 — The brief's claim that `rungs_tried` reconciles the ladder with emergent difficulty is wrong for the majority of findings.** `bench/routing.py:210` (strongest-first loop); claim at `bench/the_promotion_ladder…py:139-162`. OBSERVED: `python3 bench/test_rungs_tried_is_left_censored_2026-10-08.py` drives the **real** `resolve_via_routing` and gets `rungs_tried = 1` for *every* difficulty the top model can handle — the label is left-censored at depth 1 and measures difficulty only above the strongest rung's ceiling (1 of 7 findings in Exp 42). Weakest-first recovers the full ranking at +10 dispatches per 5 findings.

**F4 — `model_id` collides and is version-unstable.** `bench/experiment_11_orchestrator.py:131/168` (`opus` ×2), `:188/200` (`gpt-5.5` ×2). OBSERVED: `grep -n 'model_id' bench/experiment_11_orchestrator.py` — 12 occurrences, 10 distinct, 9 carrying a vendor version. Brief figure confirmed exactly.

**F5 — Random identifier assignment splits identical configurations.** Design-level (founder's "randomly assigned model ID"). OBSERVED by measurement in my falsifier: 2 instances of one configuration under split records need 21 rounds to separate 0.8 from 0.4; pooled under one key, 11 rounds. Random keys double the cold-start price for zero benefit.

**F6 — False rigour: Wilson intervals on deterministic quantities.** `bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py:96` (pre-patch): a confidence interval on the exact ratio 6/N, which has zero sampling variance. OBSERVED and patched; the same defect appears **in this brief's own text** — "10 of 12 models with 0 attempts, Wilson [0.5520, 0.9530]" is deterministic under identifier order with a cap of 2 (exactly 10 of 12, always); the interval asserts uncertainty that does not exist.

**F7 — Idle timeout alone is unbounded and kills buffered workers.** Design Q6. OBSERVED: heartbeat child (1 line/0.5 s) is never idle — stopped only by the total cap at 6.0 s; a *working* child writing unflushed to a pipe showed **0 bytes** at a 2.0 s idle cap (wrongly killed) while the identical child under `python3 -u` completed at 3.1 s.

## FIXES (all executed; outputs shown above)

| Finding | File | Falsifier result |
|---|---|---|
| F1+F2 | `bench/promotion_gate.py` | `bench/test_promotion_gate_2026-10-08.py` — **ALL CHECKS PASS** |
| F3 | per-rung record stratification inside `promotion_gate.py`; censoring demonstrated by `bench/test_rungs_tried_is_left_censored_2026-10-08.py` | **CONFIRMED censored** |
| F4+F5 | `bench/model_identity.py` | `bench/test_model_identity_2026-10-08.py` — **ALL CHECKS PASS** incl. live-collision check |
| F6 | patch to `bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py` | re-run shown, `share_is_exact: True` |
| F7 | `bench/idle_timeout_needs_a_backstop_2026-10-08.py` | **BOTH ADVERSARIES CONFIRMED** |

**The derived parameters the brief demanded** (inputs are stated targets, outputs are searched minima, every tail double-checked by SciPy, NumPy summation, and Wolfram Language local kernel):

- Targets: β_total = 0.05 (p=0.90 model reaches top of 5 rungs ≥ 95% per campaign), α_top = 0.001 (p=0.50 model ≤ 0.1%), hold-safety 10⁻³, drop-detect 0.95 at p 0.90→0.40. Anchor rates 0.90/0.50 are consistent with the archive rates already in `routing.py:35-37` (Codex 90%, DeepSeek 28%).
- **Promotion gate: n = 12 attempts per rung, promote at ≥ 8 successes** (Wilson-floor equivalent ≈ 0.39, not 0.50 — the brief's 0.50 floor is why its repair over-corrected). Per-rung pass: good 0.99567, bad 0.19385; per-campaign: good **0.97854**, bad 2.74×10⁻⁴. Minimality verified by exhaustive search below n=12. Calibration **exists**; the brief's doubt is answered constructively.
- **Demotion window: W = 17 held-rung attempts, demote at ≤ 10 successes.** P(demote|healthy) = 7.84×10⁻⁴, P(demote|degraded) = 0.9652.
- **Re-test schedule (F2):** gate blocks repeat indefinitely — every 12 candidate-rung attempts is a fresh gate, riding on real routed work at that rung so marginal dispatch cost ≈ 0 when work exists; worst case 12 dispatches per retry block. Measured: 300/300 unlucky good models reached the top; climb-on-noise bounded ergodically — a p=0.5 model's long-run occupancy of the top two rungs measured **0.0000** (rung distribution [0.946, 0.050, 0.004, 0, 0, 0]); a degraded model descended 5→0.

## OPEN QUESTIONS

1. **No** — failing the gate at rung k+1 never touches the rung-k record (records are per-rung). What stops accumulating unholdable rungs is the demotion window on held-rung work: W=17/j=10, derived, falsified above.
2. **New identifier at 0 attempts, by construction**: `capability_key` includes `model_version`, so a release re-keys automatically. Cost: the measured cold-start price (21–350 attempts by gap; 1465 at gap 0.05). Lost: nothing — the old record stays valid *for the old configuration*; it is retired, not destroyed. Inheriting instead risks routing hard findings on a stale 0.9 bound — bounded cost versus unbounded consequence.
3. **Yes, priority not eligibility — and rungs are still needed**, for a reason the brief missed: a new model at the back of the order sees only findings every stronger model already failed — a maximally hard, biased sample. Its "free" measurements are near-pure failures and cannot demonstrate capability (F3's censoring, mirrored). Rungs exist to hand it *easy* attempts; per-rung stratification keeps back-of-order failures from poisoning its easy-rung record.
4. Derived from the **output-distribution-affecting configuration**: digest over (provider, model_version, temperature, top_p, max_tokens, system_prompt, tool_set, quantisation). Identical configs merge (correct — pooling measured 11 vs 21 rounds); any distribution change splits. Random tokens survive only as `instance_id` for dispatch bookkeeping. This *contradicts the founder's "randomly assigned"* wording while serving his intent better.
5. **They compose.** Rotation breaks ties *within* an equivalence class of overlapping bounds at the same rung; the ladder orders *between* rungs. At cold start all models sit in one rung-0 tie class where rotation governs — exactly the measured starvation case. Conflict arises only if rotation is applied across rungs, which nothing requires.
6. **Idle timeout is the right primary and insufficient alone** (F7): it needs an unbuffered stream (pty or `-u`, else the idle clock measures the stdio buffer, not the model) and a generous total-cap backstop (else a heartbeat runs forever). The composition clears the founder's composability bar by measurement: each component alone fails a demonstrated adversary.

## YOUR STRONGEST DISAGREEMENT

The brief's headline — the one-success rule "mainly excludes good ones," 40.951% "kept out by luck alone" — **holds only under an absorbing one-attempt-per-rung reading the founder never stated.** His words "stay on the same simpler problem resolution rung" naturally mean the model keeps receiving that rung's tasks; under that reading every model with p > 0 reaches the top with probability 1 (derived above, E[attempts] = R/p), and the rule's true defect is the opposite: it excludes *nothing*. The brief built its quantitative case on the less natural reading without flagging the choice. Secondary: the brief's own Wilson interval on the deterministic 10-of-12 starvation count is the same false-rigour defect its companion script committed (F6).

## WHAT WOULD REFUTE MY OWN POSITION

1. **The binomial design assumes i.i.d. Bernoulli attempts.** Compute lag-1 autocorrelation (Ljung–Box) on per-model confirm/fail sequences in the CDSFL archive; significant serial correlation (p < 0.01) would miscalibrate (12, 8) and (17, 10) and refute the derivation method, not just the numbers.
2. **The anchor rates 0.90/0.50/0.40 are stated targets, not re-measured here.** Re-run `scripts/competence_provenance.py`-gated confirm rates; if the good/bad separation in the archive is materially narrower than 0.9 vs 0.5 (e.g. 0.75 vs 0.6), the minimal n grows sharply (gap 0.05 needs ~1465 attempts) and the gate as parameterised is impractical.
3. **The retry-reading disagreement** is refuted by one sentence from the founder confirming the absorbing reading was intended.
4. **The new-identifier-per-release rule** is refuted if paired before/after confirm rates across real vendor releases show behavioural change in a negligible share of tasks — then inheritance with a demotion window would dominate on cold-start cost.

## CONFIDENCE

**High on every number** — each figure was computed by at least two open-source tools and the six load-bearing tails were independently confirmed by Wolfram Language (local Wolfram Engine) to 7+ digits. **Medium on the design parameters** — the derivation is exact given the targets, but the anchors (0.90/0.50/0.40) are assumptions supported only indirectly by the Exp-42 rates recorded in `routing.py`; refutation path 2 above is the measurement that would settle it.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/rung_promotion_and_model_ids_2026-10-08/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
