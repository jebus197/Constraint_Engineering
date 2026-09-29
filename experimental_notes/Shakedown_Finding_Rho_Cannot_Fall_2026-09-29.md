# The Shakedown's First Finding: Convergence By Saturation Is Unreachable, By Construction

**2026-09-29, 19:25 BST.** [NEEDS YOUR RULING]. Audience: a reproducing engineer.

**Run:** `bench/logs/shakedown_2026-09-29/` — arm 1, 5 `-SIM` seats, reached **round 5 of 7** before the session that launched it ended, taking the runner with it. 50 files harvested to `arm1_harvest/`. Every figure below is from that run's own data or from the shipped code, executed.

---

## The finding

**`rho` = novel/raw is pinned at exactly 1.000 in every round, and cannot be otherwise.** Observed: rounds 0–4 all `rho=1.000`. The archived 2026-09-21 run: all 8 rounds `rho=1.000`. Registry grows linearly (22, 30, 37, 45, 53 — +8, +7, +8, +8) with no saturation.

`rho` feeds the convergence machinery. A run can therefore only ever converge by **exhausting its round cap**, never by the discovery curve flattening.

## The chain, each link measured

1. **`FindingRegistry.register()` mints a new canonical id unconditionally** — `canonical_id = f"C{self._next_id:04d}"`. Two models finding one defect produce two unlinked canonicals.

2. **Novelty is counted on an alias miss, not on content.** `reference_runner_v3.py:14418` uses `lookup_alias(f.model_id, f.finding_id)`, and the shipped body is `self._alias_map.get(f"{model_id}:{local_id}")`. Executed: two models with the same defect and the same local id both return `None`, both increment `novel_this_round`, giving `rho = 2/2 = 1.000`. "Novel" means *this model has not used this id before*, not *this defect is not already known*.

3. **`occasions` is the repair, and it is starved.** Added on the founder's 2026-09-04 ruling and described in its own comment as *"read by nothing yet"*. It **is** appended to — at line 2429, `_tgt.setdefault("occasions", []).append(...)` — but only inside a **merge** path.

4. **The merge path never completes.** Merges are withheld pending a tool verdict (`feedback_no_model_voting`, founder ruling 2026-08-19). The run logged the same 4 withheld merges every round from round 2: `C0003→C0008`, `C0004→C0018`, `C0020→C0001`, `C0022→C0016`, each `no tool verdict`.

5. **Measured consequence:** all **53 of 53** canonical entries carry exactly **1** occasion. Multi-occasion entries: **0 of 53 = 0.0000%**, Wilson [0.0000%, 6.7582%].

**The code predicted this itself.** `register()`'s comment records: *"when two models find one defect the runner mints two unlinked canonicals and the second is merged away. The overlap signal is destroyed at exactly the point it is created, so a saturation curve built from `source_model` is linear BY CONSTRUCTION"* — measured 2026-09-02 as **2 of 2,050** archived findings raised by more than one model.

## Why lowering the similarity threshold is not the fix on its own

The routing dedup uses `_routing_similarity` — bare word-overlap Jaccard on the `description` field — at **0.85**.

Measured over this run's **53 canonical findings, 1,378 pairs**: min 0.0000, **max 0.2772**, mean 0.0659 (numpy and statistics agreeing exactly). **0 of 1,378 reach 0.85** — Wilson [0.0000%, 0.2780%]. The threshold is unreachable: at 0.2772, the most similar pair in the whole run reaches under a third of the 0.85 required.

But lowering it is not sufficient, and the numbers say why. The 4 pairs the run itself flagged score **0.1528, 0.1667, 0.1889, 0.1987** — *inside* the general distribution. Three **unflagged** pairs sit above every flagged one: `C0006/C0020` at 0.2772, `C0039/C0043` at 0.2477, `C0046/C0048` at 0.2445.

- Threshold needed to catch all 4 known duplicates: **0.1528**
- False positives it admits: **25 of 1,374 = 1.8195%**, Wilson [1.2354%, 2.6722%]
- Precision at that threshold: **4 of 29 = 13.79%**
- Rank-based separation: **AUC 0.9900** — the instrument *ranks* duplicates well; with only 4 positives the power behind that figure is very low and it is reported as such.

**A correction to an earlier draft of this note.** A first pass reported 23 pairs with identical descriptions never merged. That was an artefact of the extraction, not a finding: the id filter `startswith("C")` matched `Codex-SIM_F003` and `CC2-SIM_F003` as though they were canonical ids, so the same finding was compared against itself under two keys. Re-run with `^C\d{4}$` the count is 0. The figures above are from the corrected pass.

## What this means for the runway

The shakedown did the job it exists for: this was found on arm 1, before any paid run. Nothing here is a regression — the archived 2026-09-21 run shows the identical pattern, and real experiments (`exp40_gate` 53 merges, min rho 0.5; `exp38_ouroboros` 6 merges, rho 0.0) show the machinery *can* work, so the defect is in how the simulated arms exercise it, not in the arms themselves.

## The ruling sought

**What supplies the tool verdict that authorises a merge?** Until something does, the merge path cannot complete, `occasions` cannot grow, and `rho` cannot fall. Three shapes are available and they are not equivalent:

1. **Raise the candidate list, keep the gate.** Lower the routing threshold to ~0.15 so real duplicates become *candidates*. Safe by construction — merges remain withheld pending a tool verdict — but at 13.79% precision the candidate list is mostly noise, and something must still adjudicate it.
2. **Give the falsifier the adjudication.** A candidate pair is merged only if one finding's falsifier also fires on the other's location. That is a tool verdict in the project's own sense and needs no new judgement layer.
3. **Count novelty from `occasions` rather than from alias misses**, and let the overlap record grow on corroboration instead of only on merge. This fixes `rho` without touching the merge gate at all.

Option 3 is the narrowest and the only one that repairs `rho` directly; options 1 and 2 repair merging, which repairs `rho` as a consequence. They compose.

**Not implemented.** All three change the instrument mid-programme, and `feedback_fixes_hil_only` puts that to the founder.

---

## CORRECTION AND EXTENSION, 2026-09-29 20:50 BST — written while implementing the ruling

**The ruling was right and option 3 works. Two claims above need amending, and a second defect was found underneath the first.**

### 1. "rho = novel/raw is pinned at 1.000" is right about rho and wrong about why

The note attributes the pinning entirely to novelty being counted on an alias miss. Measured against the run's own stored state, that is not the whole mechanism. Arm 1 stored `novelty_counts [18, 7, 7, 8, 8]` against `raw_counts [22, 8, 7, 8, 8]`. Those give 0.8182, 0.8750, 1.0000, 1.0000, 1.0000 — **not** 1.000 throughout. Yet `rho_history` records 1.000 in all 5 rounds.

**So the run already knew its own novelty was lower than its rho.** The numerator on disk and the rho on disk disagree.

### 2. The second defect: rho is computed before the settle pass that corrects its own numerator

`_compute_rho` is called at exactly 1 site, at the registration loop, and `rho_history.append` follows it immediately. About 690 lines later the settle pass overwrites `novelty_counts[-1]` — rho's own numerator — from the settled registry. `rho_history` is never recomputed; thereafter it is only cleared on an ITC restart or serialised. The correction reaches the numerator and never reaches rho.

Measured by `scripts/rho_computed_before_the_settle_2026-09-29.py` over 49 archived runs and 406 rounds:

- **25 of 406 rounds** carry a rho disagreeing with their own stored numerator — **6.1576%**, Wilson [4.2053%, 8.9318%].
- The direction is unanimous: **25 of 25 are OVERSTATEMENTS**, Wilson [86.6808%, 100.0000%]. Mean −0.2066, median −0.1667, worst −0.5000.
- **13 of 49 runs affected** — 26.5306%, Wilson [16.2113%, 40.2623%].
- numpy and exact `Fraction` arithmetic agree to 0.000e+00; both Wilson implementations agree to 2.776e-17.

**A measurement error caught before it became a claim.** A first pass compared at a 1e-9 tolerance and reported 220 of 406 rounds mismatching, 94 of them "understatements" whose largest delta was 1e-9. `rho_history` is serialised as `round(r, 6)`, so that pass was measuring the JSON writer. At the stored precision the figure is 25 and the direction is unanimous. Same class as the `startswith("C")` artefact recorded above.

**Honest scope, and it limits the severity.** On that archive the defect flipped **no** churn decision — **0 of 406**, Wilson [0.0000%, 0.9373%] — because every mismatch sits in an early round and churn requires `round_number >= rho_earliest_round`, which is 12. It corrupted a reported metric and the saturation diagnostic, not a recorded verdict. That is a property of this corpus and not a guarantee about future runs.

### 3. This is why option 3 and the recomputation are one fix, not two

Option 3 counts novelty from `occasions`. The overlap record for round K is not complete until the triage pipeline has run and `record_codiscovery` has fired, which happens **after** the novelty counter. A counter keyed on `occasions` at the registration site would see only earlier rounds — which the alias map already covered. **The recomputation after the settle is therefore a precondition of option 3, not extra scope.**

### 4. What option 3 actually yields, replayed on real corroboration

`scripts/option3_replay_2026-09-29.py` reconstructs the occasion the new code would write, using only the `codiscovery` records each run already produced, then calls the shipped series function.

Arm 1's rho becomes **[0.5909, 0.7500, 0.5714, 0.8750, 0.8750]** against a recorded [1.000] × 5. The archived 2026-09-21 panel arm becomes **[0.9130, 0.8571, 0.7500, 0.2857, 0.4000, 0.8750, 0.5000, 0.3333]** against a recorded [1.000] × 8 — a genuinely varying discovery-efficiency curve.

All **10** of arm 1's corroboration events sat on entries whose status was **not** terminal, so every option-3 exclusion is additional to what the settled series already removes. The two mechanisms are complementary, not overlapping.

**The limit of that replay, stated because it matters.** Those series are recomputed from each run's **final** registry, so they include statuses that settled after the round and corroboration recorded later. The live runner recomputes rho once per round from the registry as it stood then. The replay is an **upper bound**, not a prediction: 242 of 406 rounds move under it, against 25 of 406 for the pure timing defect. The live effect lies between. Only a live run settles it, which is why the shakedown is being re-run rather than this being treated as the verification.

### 5. A third defect, found in passing and NOT fixed — [NEEDS YOUR RULING]

Only `novelty_counts[-1]` is overwritten by the settle, so earlier rounds stay frozen at the vintage they were written with. Arm 1's round 1 holds 7; recomputed from the final registry it is 6. The runner's own comment at the location-keyed block records this exact class of defect for `novel_critical_history` and says the whole-series correction was applied there on 2026-08-19 — and left this copy. Whether rho's history should be retroactively resettled is a change to a reported series across a whole run, so it goes to the panel rather than being taken here.

### 6. A resume defect found by the new guard test itself

`record_codiscovery` returned early whenever the alias was already recorded. Any run resumed from a checkpoint written before the occasion write existed would therefore carry corroboration in `source_aliases` and `codiscovery` while `occasions` stayed empty — reinstating the whole defect through the resume path alone, silently, with every test green. Repaired by backfilling the missing occasion without re-appending the alias; the `False` return is preserved because 3 existing tests assert on it.

### 7. The lost run had a cause, and it was not the runner

Arm 1 died at 18:53:47 because the launching session ended. The detached-launch directive has stood since 2026-07-29, and `bench/detached_launch.sh` implements it — for `bench/launch_exp42.py` only, whose config argument it hardcodes. The simulated path runs through `run_simulated_experiment_sandboxed.sh`, which nothing detached: `--run` used `subprocess.call`, which blocks and dies with its parent. A standing rule with no executing caller on the route actually in use — the same shape as `boundary_band_sensitivity` and `EXTEND`. Repaired by a `--detach` flag that re-enters `--run` in a new session, so the arms stay sequential and the ordering has exactly 1 definition.

### What is now implemented, against what is still the founder's to rule on

| | Status |
|---|---|
| `occasions` grows on corroboration | IMPLEMENTED |
| Novelty counts distinct defects (`_corroborated_novelty_series`) | IMPLEMENTED |
| rho recomputed after the settle | IMPLEMENTED (precondition of the above) |
| Corroborated **critical** novelty reaching the gate | SHADOW ONLY — logged, does not gate |
| Retroactive resettling of the whole rho history | NOT DONE — [NEEDS YOUR RULING] |
| Options 1 and 2 (candidate threshold; falsifier as tool verdict) | NOT DONE — for the panel |

Guards: `bench/tests/test_rho_counts_distinct_defects_2026-09-29.py`, 35 tests; `bench/tests/test_a_simulated_run_survives_its_session_2026-09-29.py`, 17 tests.
