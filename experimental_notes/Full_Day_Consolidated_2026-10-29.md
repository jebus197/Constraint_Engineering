# Consolidated report for the full day, 29 October 2026

2026-10-29, 22:10 GMT (Europe/London). Branch `sim-shakedown-2026-09-29`.

This is the technical companion to the spoken version of the same report. It carries the file paths, commit hashes, producer scripts and test counts that the spoken form omits under Rule 6 of the note standard. The spoken form is the one to listen to; this one is the one to check a figure against.

## 1. Summary of the claim

Every one of the founder's 13 annotations on `Responses/Decisions_Awaiting_You_2026-10-29.txt` was acted on, 7 authorised pieces of work were built and guarded, 3 claims previously made to him were refuted by measurement taken today and are withdrawn here, and 5 defects were found that he did not ask about. 11 defects of this session's own making were caught by a gate or a trace rather than by inspection. 14 decisions remain his.

## 2. What was built, with its guard

Every figure below is produced by a committed script, per `measured-rate-travels-with-its-script`. Every guard was deliberately broken to confirm it goes red; the mutation figure is given as `caught of attempted`, and the day's total is 47 of 47.

| Work | Code | Guard | Tests | Mutants |
|---|---|---|---|---|
| Memory baseline skips an unclean save | `scripts/cdsfl_sv.py` (`record_sv_completion`, `unclean_sv_commits`, `_previous_sv_commit`) | `bench/tests/test_the_memory_baseline_skips_an_unclean_save_2026-10-29.py` | 14 | 7 of 7 |
| An identity can be walked back | `bench/ticket_store.py` (`adopt_identity`, `undefer`, `_index_identity`) | `bench/tests/test_an_identity_can_be_walked_back_2026-10-29.py` | 18 | 4 of 4 |
| Feedback section groups under its headings | `scripts/cdsfl_sv.py` (`group_feedback_index_entries`) | `bench/tests/test_the_feedback_section_groups_under_its_headings_2026-10-29.py` | 15 | 6 of 6 |
| The register is the single source for deferral | `scripts/task_list_markers.py` (`register_deferrals`, `effective_state`, `deferral_disagreements`, `derive_deferred_markers`) | `bench/tests/test_the_register_is_the_single_source_for_deferral_2026-10-29.py` | 17 | 6 of 6 |
| The claim channel enters R_k | `bench/claim_ledger.py` (`claim_channel_coverage`, `claim_channel_factor`, `apply_claim_channel`) | `bench/tests/test_the_claim_channel_enters_r_k_2026-10-29.py` | 16 | 7 of 7 |
| Runner-core lookups announce | `bench/runner_core.py`, `bench/reference_runner_v3.py` via `routing.resolve_or_alarm` | `bench/tests/test_the_runner_core_lookups_announce_2026-10-29.py` | 12 | 4 of 4 |
| The miss ledger is not split | `bench/routing.py` (`_register_under_both_names`, `ledger_is_shared`) | `bench/tests/test_the_miss_ledger_is_not_split_2026-10-29.py` | 7 | 3 of 3 |
| The annotation reader sees CR-only files | `scripts/what_was_he_annotating_2026-10-29.py` | `bench/tests/test_the_annotation_context_reader_sees_cr_only_files_2026-10-29.py` | 8 | 4 of 4 |

Day totals: 17 new guard files, 201 test functions, **47 of 47 mutants caught** (1.0, Wilson 95% [0.924442, 1.0]), 13 new producer scripts, 15 new documents, 25 commits.

Measured effects, each with its producer:

- Feedback index grouping: `MEMORY.md` 174 lines to 105, refusal headroom 26 to 95 lines, characters unchanged, 187 pointers intact. Producer: `group_feedback_index_entries` in `scripts/cdsfl_sv.py`, reached from the save flow at line 3375 with `dry_run=not apply`, so `cdsfl_sv.py --dry-run` exercises it read-only. There is no `--group-feedback` flag; an earlier draft of this line named such a flag and it never existed. Run read-only at HEAD 5180b471 it now reports no merge, which is the correct result of the grouping having already been applied.
- Claim channel form: `R_k * (1 - w * coverage)`. **NOT WIRED INTO THE LIVE PATH, corrected 2026-10-29 after this report was first delivered.** `apply_claim_channel`'s only caller outside its own module is its own producer script; the live computation at `bench/reference_runner_v3.py:15774` and `:15848` is `R_k = R_base * (1 - nu_eff) + nu_eff` and does not call it. `ClaimLedger.informative_only` is still `True` and its docstring says so honestly. So the pathway is BUILT and UNREACHED, which is the addition-that-does-nothing class the additive standard names 11 prior instances of; this is the 12th and it is mine. Earlier wording here said the channel "enters the residual risk term", which is true of the function and false of the harness, `CLAIM_CHANNEL_WEIGHT = 0.0`, `CLAIM_CHANNEL_MAX_WEIGHT = 0.5`. 6 properties verified in SymPy and cross-checked in Wolfram Language, which agreed on all 6 (attribution: Wolfram Language; SymPy remains primary). Producer: `scripts/the_claim_channel_enters_r_k_2026-10-29.py`.
- Admission silence: 5 of 10 steps silent before, 1 of 10 after, the survivor being a `SILENT DEGRADE` which is not a table lookup. Producer: `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py`.
- Paid run reordered from entry 16 of 184 to last of 186 in `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, on his ruling R1.

## 3. The 3 claims withdrawn

**The workspace trust claim.** He had accepted it; `~/.claude/settings.json` records `/Users/georgejackson/Developer_Projects` as trusted, which is where this session roots. The second half of the claim, that seats run degraded, is refuted: a headless seat used Bash successfully in a scratch directory with no settings file and with all 31 `CLAUDE*`/`ANTHROPIC*` environment variables stripped. Decision 2 is **withdrawn, not ruled**. Producer: `scripts/does_the_project_allow_list_reach_a_seat_2026-10-29.py`.

**The identity floor is 319, not 320.** His ruling approving 320 rested on the claim that the count could not fall. `adopt_identity` succeeded on 1 of the 3 offending tickets and was correctly refused on the other 2, each of which has a correctly-identified twin. Producer: `scripts/an_identity_can_now_be_walked_back_2026-10-29.py`. Ratchet: `bench/tests/test_an_identity_is_derived_not_remembered_2026-10-28.py`.

**The explanations owed are 11 live questions, not 9 and not 16.** B51's own predicate is a word match and covers 1 of the 11, missing 10 (0.909091, Wilson [0.622642, 0.983768]). 7 of the 10 are unanswered questions of his from the 2026-10-17 files that nothing tracked as debt. The basis is now the register. Producer: `scripts/register.py --kind qs --state live`.

## 4. The answers

**The 63 adjudications.** The standing correction reads "Findings confirmed programmatically or by HIL — no model voting", so programmatic confirmation is 1 of 2 permitted routes. 63 is a power figure (simulated 0.916500; 48 reaches 0.80; the closed form says 35 and simulates 0.6472, so it must not be quoted). The 2026-09-02 blind audit already holds 286 first-pass and 108 second-pass verdicts against the 5 clauses of `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`. 0 items shown to require him; 30 optional spot checks give 0.9537 detection against 0.9902 at 63. Producer: `scripts/how_many_adjudications_actually_need_him_2026-10-29.py`. The false sentence was removed from `.claude/CLAUDE.md` and `~/.claude/CLAUDE.md`.

**B50, the immune-memory assertions.** He reset the store on 2026-10-17. 6 assertions in `bench/tests/test_immune_memory_persistence.py` describe 3 to 5 experiments against a live store holding 1, the first post-reset records having been written at 00:57 on 2026-10-29 by a free run. 2 of the 6 are a stale constant naming 3 late-July runs. The other 4 assert facts measured on destroyed data. Recommendation: widen the skip predicate from "0 records plus an archive" to "the live store no longer holds the runs the claim was measured on".

**The severity wobble.** Median inter-assessment spread 0.1200 over 147 archive entries. The 0.7 cut is a separate thing: an undocumented code convention later pre-registered as a proxy for the 5-clause rubric. The merge path keeps whichever entry was the target, with 0 calls to `max`, `min`, `median`, `mean` or `sum`, so the kept value lies outside the range of its own inputs in 35 of 147 cases (0.238095, Wilson [0.176469, 0.313061]). What severity should mean remains his.

**The 16 closed findings.** 1 archived run, 69 entries all carrying `fix_efficacy`, splitting 25 cured / 16 not cured / 28 not measurable, summing to 69. The 16 are closed with the defect demonstrated and the fix measured as not curing its own falsifier: 0.231884, Wilson [0.148079, 0.343968].

**The demotion false-alarm proportion.** Recommended 0.05: conventional, so not taken on trust, and it makes every other threshold recomputable from 1 number.

**Would the fix raise failures.** Reported failures rise; actual faults do not change. Review-queue impact 0, established by running the pre-run health check and observing 0 writes to the registry, the ticket store and any data file. Live figure: that run reported 8 of 8 checks passed while listing all 6 simulated seats absent from 4 tables each, so 24 absences inside a pass.

**The paired comparison.** Its baseline arm, the side held fixed so the other can be compared against it, names a 2026-10-03 run; the branch has moved 341 commits since, 51 touching the runner and 10 the composer. The annotated file said 141, 24 and 3, correct on 2026-10-15. The decision is timing: both arms after the third convergence.

**The hazard figure.** A brief built on an unmeasured 0.3 where the seats measured 0.2337 and 0.1994, so 22.1% and 33.5% too high; a claimed collapse factor of 7.7915 against a correct 6.053 over the range actually priced ([0.1, 0.5]). All 3 errors ran reassuring. Briefs now declare figures the validator re-executes before dispatch.

**The long-running process.** Turn-elapsed 4h33m32s against a 4-minute-old command. Pre-commit board mean 343.85 s, sd 13.72 s, n = 8. Full board mean 91.4 min. Nothing stuck; 3.81 hours of his machine was nonetheless spent on boards invalidated by later commits.

## 5. Found without being asked

**His own specification had sat unread for 8 days.** `Responses/CDSFL_UX_AUTHORITATIVE_DESIGN_BRIEF_2026-10-21.txt`, 257 lines, dated 2026-10-21, marked single source of truth for product shell behaviour, with 4 companions. None was in version control. It answers the bounded-orchestrator question at section 2 rule 2 (the orchestrator seat is bound by the same experimental rules; the tab is named Orchestrator), declares the product identity as a local-first general-purpose STEM calculator and experiment instrument, and carries a 9-step implementation order with 12 acceptance checks. All 6 are now at `docs/ux/`, byte-identical, with `docs/ux/PROVENANCE_AND_WHAT_IT_SETTLES.md` separate so his document stays his. Derived companions: `docs/ux/ORCHESTRATOR_ROLE_SPECIFICATION_DERIVED_2026-10-29.md`, `docs/ux/HIL_INTERACTION_SPECIFICATION_DRAFT_2026-10-29.md`. Producers: `scripts/what_is_the_orchestrators_role_derived_2026-10-29.py`, `scripts/how_does_he_actually_interact_2026-10-29.py`.

**A live seat is routed as the weakest of all.** Fable has a `MODEL_SPECS` entry and no `INITIAL_FINGERPRINTS` entry, so `CapabilityFingerprint(0.2, 0.7, 0.7, 0.5)` is substituted silently, worse than every measured seat on all 3 capability axes by 0.05, 0.05 and 0.15. `MODEL_SPECS` records `_provenance: 'inherited from CC2 2026-08-30; not measured'`; `INITIAL_FINGERPRINTS` records nothing. Raised as `pf:5c099c217f11`. No claim is made that this caused any past result.

**The announcements were written where nobody could read them.** `routing` and `bench.routing` were 2 module objects with 2 `_LOOKUP_MISSES` lists. Run as a script, the runner bound the top-level module and the producer bound the package, so a miss was recorded in the first ledger and read from the second, which makes the instrument report working code as defective. Fixed by self-aliasing in `bench/routing.py`.

**The termination measure crossed 1.** R = 0.803797, 95% [0.636696, **1.014754**]; one-sided exact test rejects R = 1 at p = 0.0377. The guard reads the upper bound, which is now above 1. Cause: 2 entries added on his instruction with 0 list entries closed. 3 further closures return it to 0.994885. Raised as `pf:d809d60e08a8`.

## 6. The gates caught 11 defects of this session's own making

1. `scripts/cdsfl_sv.py` memory ledger counted `MEMORY.backup-*` as memory entries; the first repair fixed 2 of the 3 sites counting the same population and the pre-commit board caught the third. Single population rule extracted to `bench/tests/_private_memory.py` (`INDEX_NAME`, `BACKUP_PREFIX`, `individual()`).
2. `scripts/task_list_markers.py` `check()` read the live register for any path, so 20 tests on a temporary `LIST.md` saw phantom disagreements. Scoped to the canonical list.
3. The panel brief lived only in gitignored `bench/logs/`; mirrored, 148 of 148 rounds preserved.
4. B51 and B52 were added with no tickets; harvested.
5. The closed-count predicate counted tickets against entries; corrected to entries, then to "every non-`qs` ticket settled", which his `qs` ruling had broken by design.
6. `bench/blocker_triage.py` `park()` accepted an empty detail; now refuses, CLI seeds from the classifier's reason.
7. A B20 addendum was inserted before its marker, breaking marker adjacency; the checker caught it.
8. The context extractor split CR-only files on `\n`, reproducing the exact blindness `scripts/read_founder_responses_2026-10-11.py` exists to prevent. Fixed and guarded.
9. The namespace script printed "THE SAME" on a 1-of-6 intersection; corrected before reporting.
10. A producer lambda passed `ExperimentConfig` where `ModelConfig` was wanted; the RAISE was read rather than the summary. `model_context_ceiling(model_config)` extracted from `bench/runner_core.py` so the producer calls the live function.
11. `bench/tests/test_admission_counts_announced_apart_from_silent_2026-10-18.py` asserted `"SILENT DEFAULT" in outcomes`, which can only hold while a silent lookup still exists. When the last silent lookup was repaired the guard refused the commit, celebrating its own obsolescence, against its own docstring: *"Not the number -- the number may move again, and should"*. Replaced by `test_the_discriminator_still_tells_a_recorded_miss_from_an_unrecorded_one`, which tests `record()`'s actual predicate (`announced = bool(_rt.lookup_misses())`) on a synthetic table no repair can remove. Commits `22528777` and `5180b471`.

Also corrected today, in the same class: `bench/tests/test_a_typed_timestamp_is_refused_2026-10-17.py` pinned a **count** in a sliding window and accused correct code once HEAD advanced past the newest of 10 historical violations. Replaced by a pinned **set** of 10 shas with the survey window derived from the oldest, per `feedback_pin_a_set_not_a_count`.

## 7. Decisions outstanding

1. **B50** — widen the immune-memory skip predicate. The only test failures of the day that remain by design.
2. **The identity collapse** — 2 faults against 1 entry take the same identity and the second overwrites the first. Already corrupted the register once: the only ticket carrying B50's `task_ref` wears a different fault's title. Changes the identity scheme, so it waits. His ruling of this morning is ambiguous between the identity-setting method (built) and the collapse fix (not built); flagged rather than resolved.
3. **The authorisation check on paid dispatch, which refuses an outbound billed request unless his approval is on record** — sound in 1 module. Of 155 modules naming a paid route, 1 consults the authorisation ledger; of 34 live entry points 10 can issue an outbound request, 0 gated. Producer: `scripts/which_paid_routes_pass_his_gate_2026-10-29.py`.
4. **The 2026-09-02 audit names no scorer** and its `ground_truth` field holds withheld severity numbers rather than human labels. Whether to record provenance as an addendum.
5. **Whether to commission the claim-channel calibration run.** The channel would move R_k in 42 of 65 archived runs (0.646154, Wilson [0.524751, 0.751245]), so it is ruled out that it would change nothing.
6. **The demotion false-alarm proportion**, recommended at 0.05.
7. **Whether to reopen the 16 non-curing-fix findings.**
8. **Whether both baseline arms run after the third convergence.**
9. **B21's single registration point** — designed at `experimental_notes/B21_Single_Registration_Point_Design_2026-10-29.md`, so a yes or no. Sub-question: whether a `SIM-` label registers in its own right or inherits its base model's registration.
10. **B39's semantic question** — whether severity is inherently a confidence within a range. He has already said no archive can settle it.
11. **Fable's fingerprint** — measure (needs a run) or record as borrowed (cheap, honest).
12. **The paid run itself**, which he placed at the end of the list.
13. **7 unanswered questions of his from 2026-10-17**: `qs:c156469d2f14`, `qs:4691ab3af39c`, `qs:ff7b6d97b33d`, `qs:514829474aa6`, `qs:6a8c53b0c1bd`, `qs:7f90c6872fa7`, `qs:41b9aab3df0e`.
14. **`qs:cea0bd553f52`** was closed by this session. `TicketStore.reopen` refuses anyone but the founder by design, so only he can reverse it.

## 8. Recommendations

1. **Rule on B50 and the identity collapse first.** Both are small and unblock mechanical work; the identity collapse is actively corrupting the register while it waits.
2. **Do not spend time on the 63 adjudications**, nor on the 30 spot checks unless the assurance is wanted. 0 items have been shown to require him and the labour proposed came from a rule widened past its own words.
3. **Record Fable's fingerprint as borrowed rather than measuring it now.** Measurement needs a run; the cheap option removes the dishonesty immediately and matches what `MODEL_SPECS` already does for the same model.
4. **Let the termination measure recover by closing entries, not by changing the criterion.** Switching the guard to the point estimate would be loosening a guard to pass.
5. **Run the board when the tree stops changing.** 2 boards of about 90 minutes each were invalidated today by commits made while they ran. The final board of the day was run on a frozen HEAD.

Written under CDSFL note standard v1.8 (17 October 2026).
