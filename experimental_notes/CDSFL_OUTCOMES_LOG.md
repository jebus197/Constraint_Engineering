# CDSFL outcomes log — the companion to the master task list

**Opened 2026-09-09 18:30 BST (Europe/London). Standing file. Append as each outcome lands; never rewrite.**

**Companion to `experimental_notes/CDSFL_MASTER_TASK_LIST.md`.** That file says what is to be done. This one says what was done, what it cost, and whether it can be undone. Desktop mirror: `~/Desktop/CDSFL_OUTCOMES_LOG.md`. The repository copy is canonical.

**Why it exists.** Founder instruction 2026-09-09, verbatim: *"You should of course be marking every outcome from all of your work in a companion file to the task list itself, so that it also does not get lost to compaction. A copy of this should also be placed on my desktop."*

---

## REVERSIBILITY, THE ANSWER TO THE FOUNDER'S QUESTION

He asked, verbatim: *"Would continuing risk anything I can't look at or you can't fix once the full task list is complete?"*

**No.** Census taken 2026-09-09 18:25 rather than asserted:

| Check | Result |
|---|---|
| Files deleted today | **0** |
| `exp39-experimental` branch | still present |
| `backup-pre-rewrite` ref | still present |
| Paid panel dispatch performed | **none** |
| Answer-key store touched | **no** |
| Commits today | 17, all in git |

Every change is a `git revert` away. The 3 categories that would NOT be recoverable are **deleting a git ref, spending money on a paid seat, and touching the sealed key store**. None has been done, and all 3 are on the task list as requiring the founder in person. **They will not be done without him.**

**Is item 3.1 a stopper? No.** The assistant stopped itself before changing anything, recorded why, and the work continues on the corrected item 3.1a. Nothing is broken and nothing is waiting.

---

## OUTCOMES, newest first

### PANEL ROUND 2 — both seats returned, and cc2 found a defect that would have destroyed a paid run

`bench/logs/panel_roster_round2_2026-09-09/`. **0 paid seats**, verified before dispatch by importing the dispatcher with `PANEL_ONLY=cc2,fable` and printing the resolved list. Confinement held: 0 canonical-path references from either seat, all sandbox. The "CANONICAL TREE MODIFIED" alert fired on 14 files, and all 14 are the assistant's own concurrent edits — **the alert cannot tell an assistant edit from a seat escape**, which is I27.

**fable: CONFIRMED**, 4 passes, 55 tool calls, an 8-11 minute run, a 19-check falsifier and 3 of its own mutations. It attacked the C-A refusal and it held. It independently re-derived the gamma answer and went further, naming the genuine series-removal channel: **CC2v REJECT to UNCONFIRMED**, not routing.

**cc2: PARTIAL**, 4 passes, 66 tool calls, 6 mutations. It found **F1**, and F1 is the finding of the day.

**F1 — a valve added so a critical "cannot block for ever" had never executed.** Both `unverified_critical_count` and `open_crit_high_count` skip entries carrying `exhausted`; between them they examine 6 statuses. The setter covered 4, and popped the flag for the rest — so one ordinary round tick stripped it from **UNCONFIRMED**, the only status the A4 counter examines. **Its only test was a source grep** asserting the line exists; it passed against dead code for 2 days, which is `execute-do-not-grep` violated inside the guard for this very valve. cc2 found the UNCONFIRMED half; **the REOPENED half turned up on verification here**, which is why the fix derives the population from the readers instead of adding a status by hand.

**And the empty-ladder repair earlier the same day made that dead valve load-bearing.** `routing_deferred` becomes the terminal state of every escalated critical in a 1-seat arm, and it is deliberately not A4-excluded — the valve was its bound. Measured: an UNCONFIRMED deferred critical gives A4 = 2 against a queue of 2, which is AT the alarm bound rather than over it, so the arm can neither converge nor halt and burns to `max_rounds`. cc2's framing is the right one and is adopted: **not a regression, a 2026-09-07 addition that nothing reached, whose cost became payable the moment the repair started routing traffic into it.**

**The valve is dead a second time, in configuration**, and that half is NOT applied: `exhausted_round_threshold` defaults to 8 while every arm sets `max_rounds: 8`, so `age >= 8` is unsatisfiable. Changing a frozen pre-registration file is the founder's call.

**Both seats independently found the same exposure on Arm B** — its declaration is byte-equal to the stale hardcoded default, so a 6th seat joining the roster would silently widen a frozen 5-seat arm. Closed without touching the frozen file, by a guard recorded as a STRICT expected failure: the day it starts passing, the suite goes red and the marker must be removed deliberately.

**cc2's sharpest criticism is of this assistant's own brief, and it lands.** The brief asserted the gamma question was one "the assistant has NOT asked" — true when written at 20:37, false by the 21:12 dispatch, because a 177-line executing test answering it landed in between. Its format was validated before dispatch; its currency was not. In cc2's words, *"a brief that asserts what has not been looked at is doing the same thing the source grep does."* Logged as I26.

**Its second criticism is also correct and narrows a claim made here.** `_declared_models` is described as "the seats a run is ALLOWED to dispatch to", and after the C-A refusal that is not quite true: Arm C reaches a CC2 verifier it never declared. **The refusal is right and the confinement claim was overstated; both hold at once.** cc2 declined to file its own proposed repair — an explicit verifier key in each arm config — because a new key with no caller would be the additive violation the brief warns about. That is the standard being applied to itself.

### 3.1a — the roster repair took the suite RED, and the panel found a hole the repair opened

**The suite went to 6 failed, 5560 passed at 20:17.** Three distinct causes, all reproduced against the working tree before anything was touched.

**Cause 1, the material one, self-inflicted.** `_declared_models` treated a NON-EMPTY `cfg.models` as an arm's declaration. `RunnerConfig.models` defaults to a hardcoded `['CC2', 'Codex', 'Gemini', 'DeepSeek', 'ChatGPT']`, and the runner's own comment above `run_experiment` records that this is the pre-Fable panel and that a run leaving it untouched is the launcher config-drop class the project has hit 7 times. Reading that stale default as a declaration made it 8. Executed against the wiring fixture: roster `['SIM-A']`, `cfg.models` at its default, intersection EMPTY, so routing and the post-convergence sweep dispatched to nobody and stamped nothing, in silence. The first version's docstring argued at length that falling back to the full roster was "the one unacceptable outcome". That ruling was wrong and is reversed: a declaration sharing no vocabulary with the roster is not a restriction on it, and erasing a roster disables a feature, which the additive standard forbids. The fallback cannot leak, because the leak case is not disjoint. **Archive reach measured, not asserted: 0 of 60 archived runs carry a panel disjoint from the default, Wilson [0.0%, 6.0%], Clopper-Pearson [0.0%, 6.0%], statsmodels and scipy agreeing to 1e-9, from 89 panel records across 2 independent sources with 0 disagreements.** Script: `scripts/roster_disjointness_2026-09-09.py`. Real and reachable, never suffered — and an earlier draft of the fix's own docstring said it "would have disabled routing in every simulated run", which the measurement refutes and which has been corrected in all 3 places it appeared.

**Cause 2, a source-text test broken by a behaviour-preserving rename.** `test_the_sweep_does_not_reclear_2026-09-02.py` anchored on the literal string `for mc in exp_config.models:` and raised ValueError the moment the iterable changed. Re-anchored on the loop rather than on what it iterates. A test that breaks on an edit that changes nothing it asserts reports a defect that does not exist.

**Cause 3, ledger drift, and `test_experiment_run_ledger_2026-08-26.py` doing its job.** The ledger cites a runner line number that is DERIVED from where the gamma-alt comment sits, and today's edits shifted it from 13753 to 13848. Regenerated; 1 line changed.

### C-A — REFUSED on measurement. The panel's observation was right and its prescription was wrong

Fable and CC2 found that `_verification_step` receives `exp_config.models` unfiltered while the 2 sibling call sites had just been repaired, and proposed filtering it for consistency. **The observation is correct and the fix is not.** `_verification_step` does not dispatch to the roster: it selects the single seat whose base label is CC2 as a verifier and returns `{"skipped": True}` if that seat is absent. **Measured against the 3 real arm configs: filtering keeps CC2v reachable in the 1-seat arm and the 5-seat arm and removes it from the contrast arm alone**, which declares `['Codex', 'ChatGPT']`. That converts a control held constant across arms into a confound in exactly 1 of 3, and disables a capability in that arm. No exp56 arm config sets any `verification_*` key, so all 3 inherit the same default — which is what held-constant means. Refused, with the reasoning pinned at the call site and by `test_cc2v_is_held_constant_across_arms_2026-09-09.py`, 8 tests, written to go RED if the refusal ever stops being correct rather than to pass forever.

### C-B — DONE. Enabling routing opened a hole in the arm that most depends on the alarm

Found by fable, confirmed by execution before it was applied. `_apply_routing` reached one branch for 2 different situations: no rung reached a model because the transport failed, and no rung reached a model because there were no rungs. Both took "retry a later round". That is right for a transport fault, which may clear, and wrong for an empty ladder, which cannot: `route` excludes the finding's own source model, so `rank_falsifier_writers(['CC2'], exclude=('CC2',))` returns 0 rungs while `rank_falsifier_writers(['Codex', 'ChatGPT'], exclude=('Codex',))` returns 1.

**The cost was not a slow retry loop.** The finding got neither `irreducible_escalation` nor `routing_deferred`, and `irreducible_queue_count` counts exactly those 2, so the critical blocked convergence to the round cap while never entering the queue count, and `HALTED_IRREDUCIBLE_QUEUE_ALARM` could not fire. **The exp56 1-seat arm pre-registers that halt as its reportable outcome, in its own words "a reportable outcome of this design, not a mechanical fault to be tuned away".** The path was unreachable while all 3 arms held `routing_enabled: false` and became reachable the moment routing was enabled earlier the same day. Fixed by stamping `routing_deferred` with a reason on `rungs_tried == 0`, which is a clean discriminator rather than a heuristic. 7 tests including an end-to-end assertion that `build_irreducible_queue_alarm` actually returns an alarm at 3 deferred criticals against a bound of 2.

### Mutation testing — 6 of 6 caught, and the root-cause mutant survived the first round

Every mutation asserts it APPLIED before any conclusion is drawn from the run, per the standing rule that a mutation which fails to apply is indistinguishable from one not caught. **The first round caught 5 of 6.** The survivor was the root cause itself: reverting the default check left all 64 tests green, because the 2 fixes mask each other — the fail-open rescues the default-as-declaration case. The test was vacuous because its roster equalled the 5 default labels, so the intersection was the whole roster either way. Only a roster carrying a seat the stale default omits can separate the behaviours, which is exactly the 2026-08-30 episode: 6 ModelConfigs supplied, `cfg.models` left at its 5-item default, the run reporting a 5-model panel while dispatching a sixth. Re-aimed on a post-Fable roster; 6 of 6 caught.

### CC2's criticism of my own test — CONFIRMED by mutation, and fixed

CC2 found that the re-aimed routing test in `test_d9_d11_configs_valid_2026-09-05.py` calls `_declared_models` directly, "exactly the weakness its own docstring criticises in its predecessor". **Confirmed precisely: reverting the routing wiring site left that test green, and the file went red only through a sibling test that already drove the sweep.** A test carried by its neighbour while claiming to catch the wiring itself is worse than no test, because the claim is what gets believed. Rewritten to drive `_apply_routing` per arm with a stubbed dispatcher; it now fails with "d9_single_model_with_agents.json declares ['CC2'] but routing DISPATCHED to ['ChatGPT', 'Codex']". The duplicated `_base` helper CC2 flagged is also gone, replaced by `base_model_label` at rr:449 after cross-verifying the 2 forms agree on 9 inputs including edge cases.

### The stale config notes — corrected in all 3 arms

`_routing_note` and `_sweep_note` still read "OFF IN ALL THREE ARMS" beside `routing_enabled: true` and `post_convergence_sweep_rounds: 2`, stale from the moment the flags were flipped. Rewritten to state the repair, the measured per-arm outcome, and the pre-registered consequence that survives it. A third note records the C-A refusal so the next reader does not re-propose it.

### 3.1 — SUPERSEDED. The "misconfiguration" was a deliberate mitigation. Commit `560c93a`
**Nothing changed in the configs.** The founder ruled that `routing_enabled: false` and `post_convergence_sweep_rounds: 0` in the 3 exp56 arms should be fixed, on an assistant report that said it was OPEN whether they were deliberate. **The record says deliberate.** They mitigate 2 live runner defects, each proven by an executing test: `_apply_routing` builds its ladder from the full orchestrator roster rather than `cfg.models`, so the 1-seat arm would dispatch to the vendors it exists to exclude, 3 of the 5 seats being paid; and the post-convergence sweep reaches undeclared seats. Both tests **passed rather than skipped** on 2026-09-09, so both defects are live. Flipping the flags would have destroyed the experiment and spent money. Superseded by **3.1a**, repair the runner to respect `cfg.models`, after which the guard lifts itself.

### 6.1 — DONE. All stop reasons now recorded. Commits `39b1042`, `e78fed4`
**23 of 41 archived runs never recorded why they stopped** — 56.1%, Wilson [41.0%, 70.1%]. All 23 INCOMPLETE; all 16 CONVERGED carry a reason. The round loop has **8 `break` statements and only 2 set `stop_reason`**. Root cause: the irreducible-queue halt set `result["convergence_reason"]` and never `brain.state`, so `_save_checkpoint()` on the next line wrote nothing — **the identical fault the gamma-alt comment records being repaired on 2026-05-18 for a different branch**. Fixed at the halt site before the checkpoint (ordering pinned by a test) and by a fallback before `signal_complete()` covering every exit including future ones, writing `UNRECORDED_STOP` rather than an empty string. 6 tests, 3 mutations, all caught.

### 2.1 — DONE. Falsifier intake. Commit `03ea98a`
**The recommended fix was refuted by measurement before it was applied:** widening the regex recovers **4,867 against 5,295 — a net loss of 428**. The diagnosis was right though: of 6,363 labels with a fenced block within 3 lines, **1,081 are missed, 16.99%**, Wilson [16.09%, 17.93%], and 1,066 of those carry a description between label and fence. Built as a **union**, which cannot lose an existing capture. The gap is constrained because a looser version captured `assert "FALSIFIER:" not in minimal` — **a false falsifier is worse than a missing one, the harness executes it**. Net **+492 recovered, 0 lost**. 13 tests, 3 mutations.

**Confirmed against the whole archive after the change landed, not only by construction:** recovery moves from **5,295 to 5,787 blocks**, and the count of files where a block was LOST is **0**. Recovery rate rises from 83.22%, Wilson [82.28%, 84.11%], to 90.95%, Wilson [90.21%, 91.63%]. All 492 discordant pairs went the same way; the 0-lost figure is the load-bearing one rather than any p-value, because a union cannot lose by construction and the check was whether the construction held in practice.

### 5.1 / section P — DONE. The panel brief format. Commit `7e26901`
The format did not exist. **Across 49 archived briefs: 0 required a seat to use the mathematical model as an instrument, 8 required a fix, 2 required the fix to be tested.** Template at `bench/directives/universal/panel_brief_template.md`, validator at `scripts/panel_brief_validate.py`, and the dispatcher **refuses** a failing brief before any of the 3 paid seats is reached. All 49 archived briefs would be refused, failing 1 to 7 checks, mean **3.10** (CORRECTED 2026-09-10: 2.4 was wrong and cited no script; `scripts/brief_archive_refusal_rate_2026-09-10.py` reproduces it — 49 refused of 52, 94.23%, Wilson [84.4%, 98.0%], median 3, and the 3 that PASS were written under this format) — the spread is what shows it discriminates. Its own test tightened it twice; the second time because a document-wide search let a brief satisfy the output check by mentioning "verdict" anywhere.

### M1 + M2 — DONE. Task markers and the pulse hook. Commit `127fd36`
Composed rather than chosen, on the founder's correction. **Three regexes counted the same list as 23, 29 and 48; the true figure is 59.** Every entry now carries a machine marker; a 5th `UserPromptSubmit` hook injects the state each turn so it survives compaction. **The cross-check found a real fault on its first run** — entry 1.3 marked DONE with status PROPOSED. It was right: an item closed by founder ruling has no work product, and neither vocabulary could express "closed because it will not be done". A 5th state, `WITHDRAWN`, was added.

### 1.1 — DONE. The commit guard. Commits `33ce5d6`, `3c6f143`
Discussed 5 times since 2026-08-25, never built; `57d5a0e` reached HEAD that morning with the suite red. `hooks/pre-commit` runs 4 guards in 1.26 s against 670 s for the full suite, fails closed, `--no-verify` as the documented escape, wired by onboarding rather than by hand. **Proven live**: staging the previous day's exact breakage gives exit 1 and REFUSED. FOLLOW also found **3 of the 4 live hooks were in no repository at all**.

### Pass 5 — the evidence I said I preserved was never tracked. Commit `3c6f143`
Commit `3c4987d` stated the log and 22 snapshots "are now in the repo". They went into `bench/logs/`, which `.gitignore:41` excludes. **22 on disk, 0 tracked**, and the commit message asserting otherwise was false. Moved to `experimental_notes/evidence/`, stored as `.py.txt` so seat-written code stays out of the source scanners. Repository-wide: **177 of 3,803 cited `bench/logs/` paths are untracked**, 4.65%, Wilson [4.03%, 5.37%].

---

## STANDING NUMBERS

| Measure | Value |
|---|---|
| Full suite | see the closing report; last green 5555, went red at 6 failed 20:17, repaired |
| Task list | 60 entries, 6 done, 1 withdrawn, 1 blocked |
| Commits today | 17 |
| Files deleted today | 0 |
| Mutations run today | 27, all caught once verified applied; 1 survived a first round and was re-aimed |

---

## WHAT IS NOT ESTABLISHED

Stated so it is not mistaken for a finding. Whether the falsifier gate ran in the 2026-09-08 run and recorded nothing, or never ran at all, is **OPEN** — the first search term used to test it was wrong and the stronger claim is not asserted without evidence. Whether the intake-parser repair would have prevented the halt is **OPEN**: recovering a block is necessary but not sufficient, since it must still bind to the right finding.

Written under CDSFL note standard v1.7 (26 August 2026).
