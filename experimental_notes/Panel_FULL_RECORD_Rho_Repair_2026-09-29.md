# Panel FULL RECORD: the between-rounds review of the rho repair

**2026-09-29T21:54:53+01:00. Audience: a reproducing engineer. This is the UNFILTERED record.** Both seats' replies are reproduced verbatim and in full below, under the founder's standing rule that external review is presented complete and never summarised in place of the full output.

## The dispatch

**FREE SEATS ONLY. 0 paid dispatches, 0 spend.** `PANEL_ONLY` unset, which selects `FREE_SEATS` and refuses paid seats by construction.

| seat | route | model | elapsed | tool calls | attempts |
|---|---|---|---|---|---|
| cc2 | claude_cli (Max) | opus | 1287.3 s | 65 | 1 |
| fable | claude_cli (Max) | fable | 1301.8 s | 75 | 1 |

Brief: `experimental_notes/evidence/panel_records_2026-09-29/rho_repair_review_2026-09-29/BRIEF.md.txt`. Per-seat sandboxes; seat proposals preserved at `seat_proposals.diff`. Run WITHOUT compelled convergence, so each seat's verdict and its strongest disagreement are preserved as information.

## What the panel changed, and it found a defect in the repair it was reviewing

**BOTH SEATS INDEPENDENTLY FOUND THE SAME CORRECTNESS DEFECT (F1) BY EXECUTION.** That is not a vote: each wrote and ran its own falsifier. `_corroborated_discounts` resolved per PAIR and never checked that the entry it discounted AGAINST was itself still being counted as novel, so a mutual pair or a chain with a discounted root erased a real defect from the novelty total entirely. One seat measured 2 of 42 archive same-defect groups fully annihilated, 4.7619%, Wilson [1.3158%, 15.7899%], with one component spanning 39 canonicals and collapsing novelty from [14,3,4,5,5,5,3] to all zeroes; and demonstrated the state gate flipping False to True on archived data, because `novel_this_round` is one of its unconditional blocking conditions.

**FABLE FOUND A SECOND DEFECT (F2) THAT CC2 DID NOT.** A pre-existing retroactive loop recomputes the WHOLE `novelty_counts` series every round with the settled-only criterion, wiping the corroborated value the settle pass writes into `novelty_counts[-1]` exactly one round after it was written. Confirmed here by reading the code order and by the run's own log: round 0 recorded `rho RECOMPUTED 1.0000 -> 0.9565`, and round 1's provisional `rho_avg=0.978` proves the 22 was still present at round 1's start (0.9783 with 22, 1.0000 with 23) before the wipe takes it back.

**BOTH SEATS REFUTED THE BRIEF'S OWN LOAD-BEARING PREMISE, AND IT WAS CC1'S.** The brief asserted that rho's churn flag is blocking condition (d) of `_check_gamma_alt_convergence`. It is false and has been since the founder's 2026-08-29 contributory ruling. Re-verified here independently: the gate returns the same boolean with `rho_churn` False and True on identical inputs, while a genuinely non-converging input still returns False, so the check is not trivially satisfied. **The direction of the error matters more than the error.** CC1 had presented the repair as conservative — harder to converge. Every route it actually opens (`novel_this_round` on the state gate; `_check_stall_convergence`; the D1 phase transition) points toward convergence being EASIER to reach, and the last two were unreachable while rho was pinned at 1.000 and are live now.

## Disagreement preserved, because it is information

The 2 seats **disagree about which simulation-detection rule is load-bearing**, and both differ from CC1's figure. CC1 measured over 103 KEYED documents: 30 caught by both rules, 0 by either alone. cc2 measured over all 7,250 archive JSON documents and found 170 that only the per-directory rule catches, 2.3448%, Wilson [2.0209%, 2.7192%]. fable re-measured the 103 admissible documents as both 21, per-FILE alone 9, per-directory alone 0. The 3 figures are answers to 3 different populations — admitted documents, all documents, and admissible documents — and the seats ran inside sparse-checkout sandboxes whose `bench/logs` differs from the canonical tree, so none transfers without restating its population. **All 3 reach the same operational conclusion: keep both rules.** Both seats independently proposed the same durable replacement: stamp `_simulated: true` at the producer into every simulated artefact, so detection reads a recorded fact rather than compensating for missing provenance.

---


# SEAT: cc2 — VERBATIM, COMPLETE

Route `claude_cli`, ok `True`, 10836 characters.

---

<!-- verbatim-begin: cc2 panel seat reply, reproduced complete -->

## Verdict

The founder's choice of option 3 is **sound in direction**. The implementation carries one correctness-critical defect and one documentation defect that inverts the reader's understanding of the risk. 4 passes; I stopped when pass 4 produced no new above-threshold finding.

---

### F1 — The discount rule can erase a defect from novelty entirely

**claim** — `_corroborated_discounts` discounts *pairwise* and never checks that the canonical it discounts **against** is itself still counted. Where the discount graph holds a cycle, or a chain whose root a third occasion discounts, every member is discounted and the defect contributes **zero** novelty. This is `cdsfl_a_model_can_delete_a_finding_by_repeating_itself` arriving through **mutual** rather than **self** reference — the function's docstring refuses only the latter, by name.

**site** — `bench/reference_runner_v3.py::_corroborated_discounts` (returns into `_corroborated_novelty_series`)

**evidence** — `python3 scripts/falsify_option3_discount_annihilation_2026-09-29.py`, run against the pre-repair behaviour:

```
[1] mutual codiscovery, 1 defect, 2 canonicals: settled=[2] corroborated=[0]
[2] live entry discounted against a REFUTED target: settled=[0, 1] corroborated=[0, 0]
[3] archive: 42 same-defect groups (from the occasion record), 2 with every countable member discounted
      annihilated component, size 4,  in commissioning_arm4_prose_20260922T053349Z
      annihilated component, size 39, in sim45_memory_20260901T040540Z
AssertionError: 3 of 3 checks demonstrate the defect
```

2/42 groups, **4.7619%**, Wilson **[1.3158%, 15.7899%]** — statsmodels and mpmath agreeing to 5.2e-18. In `sim45_memory_20260901T040540Z` a **single** group spans all 39 canonicals (containing the 2-cycle `C0001↔C0007`), collapsing novelty from `[14,3,4,5,5,5,3]` to `[0,0,0,0,0,0,0]`: 39 CLOSED findings, not one counted as a discovery.

**It moves a real gate.** `novel_this_round` is assigned from this series and blocks `_evaluate_gate_conditions`. Executed on that run's round 6:

```
state gate with novel_this_round= 3 (settled              ) -> passed=False | Gate failed: novel=3
state gate with novel_this_round= 0 (corroborated(option3)) -> passed=True  | All conditions met
```

**verdict** — HOLDS
**fix** — `bench/reference_runner_v3.py` — new `_release_annihilated_components`: union-find over the discount graph; where a group retains no countable survivor, release exactly one (minimal by `(open_since_round, canonical_id)` — the same tie-break the pairwise rule already uses). Strictly additive: identity on the 40 healthy groups; can only *remove* keys from `discounts`, never add.
**falsifier** — same command. Exit **0** with the fix; exit **1** (AssertionError, all 3 checks) with `_release_annihilated_components` replaced by the identity. 121 passed / 2 skipped across 7 targeted test modules with the fix in place.
**what would refute me** — a demonstration that two canonicals joined by a codiscovery occasion are *not* the same defect, which would make the erasure correct; or that `min(open_since_round, canonical_id)` picks the wrong representative in a case the pairwise rule already handles. Note my archive figure depends on `option3_replay`'s reconstruction of occasions from stored `codiscovery` lists — if that reconstruction over-links, 2/42 is an overcount. The two constructed cases do not depend on it.

---

### F2 — "rho's churn flag is blocking condition (d)" is false, and the real route points the other way

**claim** — 5 sites assert rho reaches convergence by blocking the gamma-alt gate. Churn has blocked nothing since the founder's **2026-08-29** ruling removed its early return. The brief repeats the claim.

**site** — `record_codiscovery` docstring; the codiscovery call site (~:15230); `_compute_rho`'s shadow-floor note; `_check_gamma_alt_convergence`'s condition list and its `contested`/`rho_churn` paragraph

**evidence** — every input held fixed but `rho_churn`:

```
gamma_alt  rho_churn=False -> converged=True     gamma_alt  rho_churn=True -> converged=True
state gate r14 rho_churn=False -> passed=True    state gate r14 rho_churn=True -> passed=True
```

Only the reason string differs. Where low rho *does* reach a decision it **causes** termination: `_check_stall_convergence` returns `STALL_CONVERGED (churn)` at ≥4 consecutive churn rounds (executed; behind `stall_gamma_termination_enabled`, default `False`).

**This is not pedantry.** The stated mechanism made the repair sound conservative — harder to converge. Every route it actually opens (`novel_this_round`; the stall path) points toward **easier** convergence. The shadow-floor note reasons from the false premise: it says a floor of 6 "would have REFUSED convergence in exp46 and exp48". It would have made them terminate *earlier*.

**verdict** — HOLDS
**fix** — all 6 sites corrected in `bench/reference_runner_v3.py`, stating the executed disproof and naming the live route.
**what would refute me** — a consumer of `rho_churn` I did not trace that vetoes convergence. I grepped every occurrence and read all three gate functions; I did not exhaustively trace the serialised `rho_churn` in the report.

---

### F3 — The half-promotion breaks `crit ≤ all` (Q1)

**claim** — `novel_this_round` reads corroborated while `novel_critical_history` reads settled, so critical novelty can exceed all-severity novelty.

**evidence** — 5 runs show `settled_crit[r] > corroborated_all[r]`. On `sim45_memory_20260901T040540Z` rounds 0 and 3 the gate reads "1 new critical" and "0 new findings of any severity" simultaneously.

**verdict** — HOLDS. **Recommendation: do not promote the critical series yet** — its zero-critical streak *is* a genuine trigger (condition (a)), and promoting before F1's guard lands routes the annihilation defect straight into it (`corrob_crit=[0,0,0,0,0,0,0]` vs `settled_crit=[1,0,0,1,0,0,0]`). Promote after, and re-measure. Holding indefinitely is not neutral: the contradiction is live.
**fix** — `experimental_notes/panel_fixes_rho_repair_2026-09-29/fable.md`

---

### F4 — The test asserting a transient (Q5)

Reproduced: **397 and 397**. The file already contains the honest version of the same question — `test_the_wrapper_is_a_shell_function_not_a_binary` probes `type grep`, gets `grep is /usr/bin/grep`, and skips. The failing test inferred wrapper presence *from the inequality it was asserting*. Same rewrite as `TestAgeControl`.

**fix** — `bench/tests/test_shell_grep_blind_spot_2026-09-28.py`: the invariant is `seen <= real` (the wrapper can only subtract) and now runs **unconditionally**, catching the direction that would invalidate every figure in the header. The strict `seen < real` is gated on the independent `_wrapper_state()` probe.

**falsifier** — `python3 scripts/falsify_grep_gate_not_vacuous_2026-09-29.py` → exit 0:
```
[1] wrapper loaded, 397 == 397 -> test FAILED as required
[2] wrapper absent -> Skipped (skip, correct)
[3] seen=500 > real=397 -> invariant FAILED as required
```
Skipping does **not** destroy the detection. Result: `8 passed, 2 skipped`, 0 failed.

---

### Q2 / Q3 / Q4 — decisions, with evidence, in `experimental_notes/panel_fixes_rho_repair_2026-09-29/fable.md`

- **Q2 — resettle the whole series. YES.** `_backfill_occasion` stamps the round corroboration *arrived*; the series buckets by `open_since_round`. Executed (`scripts/measure_rho_retroactive_drift_2026-09-29.py`): a round-3 corroboration rewrites round 1, which `[-1]` cannot reach, and the error lands **inside** the rolling window — `rho_avg` 0.1667 stored vs 0.0000 resettled, against a 0.25 threshold. **The archive cannot answer this** and my script says so in its own output: archived `codiscovery` records carry no round, so a replay returns 0/318 *by construction*. Recorded as UNMEASURABLE-FROM-ARCHIVE, not measured-clean.
- **Q3 — (b) first, then (a); neither is redundant.** (a)'s *accounting* motive is now redundant; its *routing* purpose is not. At 13.79% precision — 4/29, Wilson **[5.4974%, 30.5590%]** — (a) alone manufactures ~6.25 false candidates per true one into a human queue: the founder's broken-machinery signature, deliberately. (b) is the on-principle answer but the predicate is too weak — *both locations* proves a shared **location**, not a shared **defect**; require the **same** falsifier to demonstrate **both claims**.
- **Q4 — retain the per-directory rule.** Over all 7,250 archive JSON documents it catches **170 the per-file rule misses** (2.3448%, Wilson [2.0209%, 2.7192%]) — not redundant at the level that matters; the brief's figure is over 103 keyed docs only. `-SIM`-in-keys is a sound **sufficient** condition, not a necessary one. The better invariant is a *produced fact*: write `"_simulated"` unconditionally into every artefact. Measured: only **4** documents archive-wide are caught by `_simulated` first — that is the gap.

---

**Wolfram:** used as second falsifier on the first Wilson interval; local kernel, exit 0, `{0.04260807310761862, 0.20978234681080865}` — agreeing with statsmodels and mpmath to 2.8e-17. *Computed with Wolfram Language.* Not used on the later intervals (statsmodels/mpmath agreed to <1e-17).

**What I did NOT check:** the 4 other full-suite failures said to be addressed at `80f0a0c`; the merge-arbitration path (`_try_merge_arbitration`); `gamma_threshold_profile` under the corroborated series; per-model rho (`raw_counts_per_model`); whether `record_codiscovery`'s call site can actually emit a same-round symmetric pair in production (F1 check [1] is constructed — checks [2] and [3] are not); the full suite (excluded by brief).

**Where I could not decide:** `test_latent_control_audit_2026-09-01.py::TestAgeControl` fails 4/4 here because the sandbox has no `.git`, so `first_committed` is `None`. Unrelated to my changes. But the audit then prints `Quarantined set: []` — a reassuring empty set — rather than refusing, which is the "lie in the reassuring direction" the grep script's own header warns against. I could not separate "no git here" from "fails open in general" without git history, so I report it unresolved rather than ruling.

**Strongest disagreement with the brief's framing:** it states as given that "`rho`'s churn flag is blocking condition (d) in `_check_gamma_alt_convergence`" and asks whether "the new numerator can move the gate". Both halves are wrong in the same direction. Churn blocks nothing (executed, both gates, identical verdicts). And the numerator does not need to move *gamma* to move a gate — it already feeds `novel_this_round`, an unconditional blocking condition of the state gate, where I demonstrated a `False → True` flip on archived data. The brief invited a question about a gate the repair cannot reach, while the gate it does reach went unnamed.


<!-- verbatim-end -->

---


# SEAT: fable — VERBATIM, COMPLETE

Route `claude_cli`, ok `True`, 9607 characters.

---

<!-- verbatim-begin: fable panel seat reply, reproduced complete -->

All verification is complete: 115 targeted tests pass (2 correct skips), both committed producing scripts exit 0, and the probe's edge cases resolve. Final report.

---

# Findings

## F1 — `_corroborated_discounts` resolved per pair, not per defect: a defect can be zeroed out of the count — **HOLDS** (fixed)

- **claim**: The landed discount rule can delete a real defect from the corroborated count entirely: (i) mutual occasions (A names B, B names A, same round) discount **both** registrations, counting one defect 0 times; (ii) a discount whose kept entry is itself status-excluded (e.g. REFUTED) removes the OPEN re-sighting too, so an **OPEN critical** contributes zero novelty for the whole run.
- **site**: `bench/reference_runner_v3.py::_corroborated_discounts`.
- **evidence**: `python3 scripts/panel_probe_rho_novelty_2026-09-29.py` (pre-fix): `EDGE-1: discounts={'C0002': 'C0001', 'C0001': 'C0002'} settled=[2] corroborated=[0]` and `EDGE-3: discounts={'C0002': 'C0001'} … corroborated=[0, 0]/[0, 0] … C2 status=OPEN — OPEN critical, corroborated series contributes 0 criticals total`.
- **verdict**: HOLDS. Caveat on reachability: I constructed the registry states directly through the public `record_codiscovery` API; the kept-terminal case needs only a later REFUTED verdict on the earlier entry (a live path), while the 2-cycle requires triage to emit mutual `duplicate_of`, which I could not confirm or exclude.
- **fix**: `bench/reference_runner_v3.py` — occasions are edges, a defect is a connected component, one representative survives: earliest-opened member whose status still counts, ties by canonical id (preserving the same-round-keeps-target rule exactly).
- **falsifier**: 4 new tests appended to `bench/tests/test_rho_counts_distinct_defects_2026-09-29.py` (mutual-pair, refuted-keeper, OPEN-critical-visibility, chain) — `39 passed`. All 43 pre-existing guard tests pass unmodified, and `option3_replay` output over the archive is **byte-identical** under the fix (the degenerate shapes don't occur in recorded corroboration — the shakedown note's "complementary" claim re-measured TRUE).
- **what would refute me**: a demonstration that neither degenerate registry state is reachable from any runner path; then this is hardening, not repair.

## F2 — the option-3 numerator repair is undone one round later by the retroactive γ-input loop — **HOLDS** (fixed)

- **claim**: Line ~14967's pre-existing loop (2026-08-18) recomputes the **whole** `novelty_counts` series every round with the settled-only criterion, wiping the corroborated value the settle pass wrote into `novelty_counts[-1]` exactly one round after it was written. `rho_avg`'s window and gamma's input therefore keep re-sightings the registry already knows are re-sightings.
- **site**: `bench/reference_runner_v3.py:~14967` (retroactive correction loop) vs `:15567` (corroborated overwrite).
- **evidence**: code order within one round iteration (append → retroactive settled resettle → codiscovery → `novelty_counts[-1] = _corr_all[round_idx]`), plus probe EDGE-6: `recorded=[6, 6, 3] -> rho_avg=0.8333; resettled=[6, 3, 3] -> rho_avg=0.6667; delta=+0.1667`.
- **verdict**: HOLDS — the repair was sound but incomplete.
- **fix**: the loop now reads `_corroborated_novelty_series(registry, len(novelty_counts)-1)`; the settle-pass `[-1]` overwrite stays as the fresher within-round update. This also removes a second inline copy of the settled criterion (`execute-do-not-grep` class).
- **falsifier**: module imports clean; 115 targeted tests across 9 files pass post-patch.
- **what would refute me**: a live-run trace showing round r's element retaining its corroborated value at round r+2 under the unpatched code.

## F3 — the brief's own gate framing is stale: churn cannot block `_check_gamma_alt_convergence` — **HOLDS** (docstring fixed)

- **claim**: "Blocking condition (d)" has been unable to block since the founder's 2026-08-29 contributory ruling; the docstring (and this brief) said otherwise for 31 days.
- **site**: `bench/reference_runner_v3.py::_check_gamma_alt_convergence` docstring vs body.
- **evidence**: probe GATE: `converged (no churn) = True / converged (CHURN) = True` on identical inputs.
- **verdict**: HOLDS. The new numerator's real behavioural surface is `_check_stall_convergence` (STALL_CONVERGED needs ≥ max(stall_window, 4) consecutive churn rounds AND gamma ≥ threshold) and the D1 phase transition — both **unreachable while rho was pinned at 1.000** and now live. That is where this change can move a run outcome.
- **fix**: docstring corrected in place, with the executed falsifier cited.
- **what would refute me**: any call path where `rho_churn` flips that function's boolean.

## F4 — both repairs otherwise SOUND, declared so with derivation

Sweep: `rho_corr` falls 1.000 → 0.500 as overlap k goes 0 → 6 while `rho_settled` stays 1.000. Chain collapses to 1; self-reference refused; backfill idempotent (`occasions=1`, returns False, `from_canonical` correct). Both producing scripts re-run and **reproduce every recorded figure**: 25/406 = 6.1576% Wilson [4.2053%, 8.9318%], 25/25 overstatements, arm1 option-3 rho `[0.5909, 0.75, 0.5714, 0.875, 0.875]`, stored-7-vs-settled-6 at round 1. Archive-ageing repair verified live: 22 sim dirs including `shakedown_2026-09-29/arm1_harvest`, baseline restored to **2026-08-23**, `_provenance_time` correct on all 4 dating shapes and None on undated paths.

# The 5 decisions (full evidence in `experimental_notes/panel_fixes_rho_repair_2026-09-29/fable.md`)

1. **Don't promote the corroborated critical series yet.** It was UNSAFE before this evening (F1's EDGE-3 could hide an OPEN critical from the count-side gate; A4 covers UNCONFIRMED only). That hole is now closed and pinned by a test, but the shadow line has never fired on real data — promote only when it fires on the resumed shakedown and every divergent round is explained.
2. **rho history: then vs now dissolves under measurement.** The input series is *already* whole-series resettled every round (2026-08-18); it should be as-known-**now** (F2 fix makes it so, corroboration-aware). `rho_history` stays as-known-**then**: it is the log of what the instrument read when the run decided; rewriting it falsifies the archive. Correction scripts are the lens for old runs.
3. **Both unchosen repairs stay live and compose.** Option 3 fixed the counter, not the supply: only 13/49 runs carry any corroboration (26.53%, Wilson [16.21%, 40.26%]). Do (b) first — a falsifier firing on both locations is a tool verdict in this project's own sense and converts arm 1's 4 perpetually-withheld merges into decidable cases — then (a) as a top-K candidate list (13.79% precision is fine for a tool-gated candidate stage; top-K bounds the cost; AUC 0.99 is relied on from the note, not re-measured).
4. **The brief's figures are wrong in the direction that matters.** Re-measured on the 103 admissible docs: both 21, **per-file alone 9** (8.74%, Wilson [4.67%, 15.78%] — statsmodels, closed form, and Wolfram Language local kernel agreeing), per-dir alone 0 [0%, 3.60%], neither 73. The 9 are exactly the leaking commissioning/arm1 runner_states: the per-file rule is **load-bearing**, the directory rule is the corpus-redundant one — keep both. These are census proportions of this corpus; the distribution of future leaking files is unknown. Durable invariant: stamp `_simulated: true` at the producer into every simulated document including `runner_state.json` — the label-key rule is compensating for missing provenance (founder's call, mid-shakedown).
5. **The TestAgeControl rewrite applies, and I applied it.** Measured here: newest snapshot resolves `grep` to `/usr/bin/grep`, ugrep absent, counts (398, 398) — the test failed for wrapper-absence, i.e. a skip written as a failure. Rewritten as a conditional invariant: assert `seen < real` **only when** grep resolves to a shell function, skip otherwise with a message distinguishing no-snapshot from no-wrapper. Detection is preserved: the honesty guard (script exits 3 on vacuous) is tested unconditionally. `7 passed, 2 skipped`.

# Closing declarations

- **What I did NOT check**: the full suite (targeted 115 tests instead); `run_exp17_immune` triage internals (whether mutual `duplicate_of` is producible); the exp40/exp38 "machinery can work" figures (relied on from the note); races with the concurrent shakedown's writes (both scripts exited 0 with cross-tool agreement to ≤2.8e-17, so none surfaced). TestAgeControl's 4 failures here are sandbox artefacts (no `.git` → `_key_first_committed` returns None).
- **Where I could not decide**: reachability of the occasion 2-cycle from a live triage path; the right top-K for Q3(a) without the resumed shakedown's candidate volumes.
- **Strongest disagreement with the brief**: its load-bearing premise — "rho's churn flag is blocking condition (d)" — is false and has been since 2026-08-29 (F3, executed). The repair's convergence relevance runs through the stall machinery and D1 transitions, not gamma-alt, and future review of this change should be scoped there.
- **Wolfram**: one call via the serial gate, local kernel, computed (`Out` values, exit 0): Wilson bounds for 9/103 and 13/22 = 0.5909… — attribution: computed with Wolfram Language.
- **Passes**: 3; the third produced nothing above the material threshold. Convergence declared on §6 criteria: hard assumptions (repair mechanism, archive figures, gate behaviour, detection rules) each tested by an executed program; residual findings are below the real-world-consequence threshold.


<!-- verbatim-end -->

---


Written under CDSFL note standard v1.7 (26 August 2026).
