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

### 2026-09-11 — A2'S COMPLETION CLAIM WAS FALSE AT HEAD, AND NOTHING IN THE PROJECT COULD HAVE SEEN IT

**What was done.** A2 said a fresh clone runs the suite green. Cloning HEAD and running it there gave **3 failed, 6952 passed, 38 skipped, 1 xfailed** against **6988 passed, 0 failed** in the working tree. Both of A2's declared instruments were sound and neither could see the claim: one guards the individual repairs and clones nothing, the other re-runs its named tests in THIS checkout. `scripts/fresh_clone_suite_2026-09-11.py` performs the clone; `bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py` runs it end to end on 1 fast file.

**The cause.** A pre-commit hook sees the STAGED snapshot. Stage 0's repairs wrote the working tree and never staged what they wrote, so every commit shipped the unrepaired content and the repair lagged 1 commit behind — green here, broken in every clone, for 2 days. `hooks/stage0_restage.sh`.

**Cost.** 0 paid dispatches. 47 commits. 0 files deleted. Roughly 12 MB added to the repository, of which 8 MB is the preserved review record.

**Reversibility.** Every change is a commit and is revertible. The 364 mirrored review files are COPIES; `bench/logs/` is untouched and remains archival. 3 corrupted line references that reached HEAD at `b024c97` were restored by hand, and the corrupting substitution is replaced by a positional splice.

### 2026-09-11 — THE PROBE THAT PROVED THE STAGING FIX DESTROYED 3 CITATIONS

**What was done.** To prove a repair now reaches the commit, 1 citation was deliberately staled and a commit allowed to run. The repair landed. It also rewrote the PREFIX of every longer citation to the same file, because `str.replace` had no digit boundary: 3 correct citations destroyed while repairing 1, and they reached HEAD.

**Cost.** 3 wrong line numbers in the permanent record for roughly 1 hour. **Reversibility.** Restored from the previous revision; `bench/tests/test_citation_repair_does_not_corrupt_2026-09-11.py` holds it, with a mutation control that reproduces the corruption from the old form.

### 2026-09-11 — 30 OF 53 MEASUREMENT SCRIPTS NEVER ANSWERED `--help`

**What was done.** The survey judged the answer by EXIT CODE, and a script with no parser ignores the flag, runs its whole measurement and exits 0. Requiring a `usage:` line: **30 of 53 = 56.6038%**, Wilson [43.2654%, 69.0496%], Clopper-Pearson [42.2826%, 70.1608%]. 2 of those 30 were among the clone's 3 failures. Now **0 of 54**, Wilson [0.0000%, 6.6414%].

**Cost.** 0 paid. 31 scripts edited, each by 2 lines inside its `__main__` block. **Reversibility.** `answer_help` is a no-op on empty argv, so a plain run reaches exactly the code it reached before; an unrecognised argument now exits 2 rather than being ignored.

### 2026-09-11 — PANEL ROUND 14: 5 DEFECTS IN MY OWN FIXES, 3 FOUND BY BOTH SEATS

`bench/logs/panel_round14_2026-09-11/`. **0 paid seats**, `PANEL_ONLY=cc2,fable`. Agreement **3 of 5 = 60.0000%**, Wilson [23.0724%, 88.2379%]; cc2 found nothing fable missed, fable found 2 more.

**cc2 proposed a 3-way `git merge-file` and fable a zero-context `git apply --cached`, and the choice between them was settled by measurement rather than argument.** On an 8-line file against a real index, with the repair at a varying distance from the author's withheld hunk: at gap 1 — the common geometry — `git merge-file` CONFLICTS and zero-context `git apply --cached` succeeds with the hunk excluded. fable's shipped. At gap 0 both refuse, correctly.

**Reversibility.** The index is the only thing written; the working tree is never touched, so a hook that dies mid-repair loses nothing.

### 2026-09-11 — 64 OF 78 REVIEW DIRECTORIES EXISTED ON ONE MACHINE AND IN NO COMMIT

**What was done.** **64 of 78 = 82.0513%**, Wilson [72.0976%, 88.9961%], Clopper-Pearson [71.7227%, 89.8251%], were wholly untracked; **0 of the 14 that survive a clone is a post-ruling round**. None was partially tracked. All 78 are mirrored now, 364 files, each verified by sha256, and all 14 post-ruling rounds have a readable FULL RECORD note.

**A CORRECTION TO MY OWN PREMISE.** I claimed a clone has no `bench/logs/` at all. **6,462 files under it are TRACKED** and a clone carries 159 subdirectories; what a clone lacks is the recent record.

**Cost.** Roughly 8 MB added. **Reversibility.** Copies only; `bench/logs/` is never edited.

### 2026-09-11 — THE PAID-DISPATCH COUNT WAS 30 AND REPORTED 10

**What was done.** The instrument globbed `panel_*`, which is 46 of 78, and read a MISSING `route` field as free — **20 of 30 paid-named replies record no route at all, 66.6667%**, Wilson [48.7801%, 80.7695%]. The guard asserting the condition was blind the same 2 ways, demonstrated: a paid reply planted in a post-ruling `confer_*` directory passes the old guard both with and without a route field.

**THE CONCLUSION IS UNCHANGED AND IS NOW ARCHIVE-WIDE:** the latest paid dispatch is **2026-09-05** and **0 of the 24 directories dated after it** hold one, Wilson [0.0000%, 11.6970%]. What was broken was the ability to NOTICE one, not the record.

**Cost.** 0. **Reversibility.** Instrument-only; no experiment or archive touched.

### 2026-09-11 — P3 IS STRONGER THAN RECORDED AND P5's INSTRUMENT READ A RENAME AS ABANDONMENT

**P3**, over all 78: under the ruling **28 of 28 = 100.0000%**, Wilson [87.9357%, 100.0000%], against **8 of 134 = 5.9701%** before it. **Fisher exact p = 1.495245e-24**, chi-square with Yates p = 2.051864e-26.

**P5**: the brief renamed the field at round 8, and the scan matched only the old name — reporting **12 of 28 = 42.8571%** and apparently falling where the figure is **26 of 28 = 92.8571%**, Wilson [77.3546%, 98.0188%]. **The rule lived in 2 places and only 1 was repaired:** the guard already carried the wider pattern and its own comment records the rename; the script did not, and the script produces the figure the founder reads.

**Cost.** 0. **Reversibility.** Instrument-only.


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
**The recommended fix was refuted by measurement before it was applied:** widening the regex recovers **4,867 against 5,295 — a net loss of 428**. The diagnosis was right though: of 6,363 labels with a fenced block within 3 lines, **1,081 are missed, 16.99%**, Wilson [16.09%, 17.93%], and 1,066 of those carry a description between label and fence. **CORRECTED 2026-09-10 by 5 independent agents converging on the same numbers:** captured is **5,295**, not 5,282 — a figure this entry already quoted 2 sentences later, so it was internally inconsistent. Missed is **1,068** (6,363 minus 5,295), **16.78%**, Wilson [15.89%, 17.72%]; 16.99% is arithmetically faithful to the wrong numerator. Of those, **1,052** carry a description between label and fence, 97.32%, Wilson [96.17%, 98.13%], not 1,066. **The 6,363 denominator is itself unstable** — not reproduced exactly under any of 15 readings of the 3-line window — so it stands as the entry's own figure rather than as a measurement, and a script that fixes the window is owed (V4). Built as a **union**, which cannot lose an existing capture. The gap is constrained because a looser version captured `assert "FALSIFIER:" not in minimal` — **a false falsifier is worse than a missing one, the harness executes it**. Net **+492 recovered, 0 lost**. 13 tests, 3 mutations.

**Confirmed against the whole archive after the change landed, not only by construction:** recovery moves from **5,295 to 5,787 blocks**, and the count of files where a block was LOST is **0**. Recovery rate rises from 83.22%, Wilson [82.28%, 84.11%], to 90.95%, Wilson [90.21%, 91.63%]. All 492 discordant pairs went the same way; the 0-lost figure is the load-bearing one rather than any p-value, because a union cannot lose by construction and the check was whether the construction held in practice.

### 5.1 / section P — DONE. The panel brief format. Commit `7e26901`
The format did not exist. **Across 49 archived briefs: 0 required a seat to use the mathematical model as an instrument, 8 required a fix, 2 required the fix to be tested.** Template at `bench/directives/universal/panel_brief_template.md`, validator at `scripts/panel_brief_validate.py`, and the dispatcher **refuses** a failing brief before any of the 3 paid seats is reached. All 49 archived briefs would be refused, failing 1 to 7 checks, mean **3.10** (CORRECTED 2026-09-10: 2.4 was wrong and cited no script; `scripts/brief_archive_refusal_rate_2026-09-10.py` reproduces it — 49 refused of 52, 94.23%, Wilson [84.4%, 98.0%], median 3, and the 3 that PASS were written under this format) — the spread is what shows it discriminates. Its own test tightened it twice; the second time because a document-wide search let a brief satisfy the output check by mentioning "verdict" anywhere.

### M1 + M2 — DONE. Task markers and the pulse hook. Commit `127fd36`
Composed rather than chosen, on the founder's correction. **Three regexes counted the same list as 23, 29 and 48; the true figure is 59.** Every entry now carries a machine marker; a 5th `UserPromptSubmit` hook injects the state each turn so it survives compaction. **The cross-check found a real fault on its first run** — entry 1.3 marked DONE with status PROPOSED. It was right: an item closed by founder ruling has no work product, and neither vocabulary could express "closed because it will not be done". A 5th state, `WITHDRAWN`, was added.

### 1.1 — DONE. The commit guard. Commits `33ce5d6`, `3c6f143`
Discussed 5 times since 2026-08-25, never built; `57d5a0e` reached HEAD that morning with the suite red. `hooks/pre-commit` runs 4 guards in 1.26 s against 670 s for the full suite, fails closed, `--no-verify` as the documented escape, wired by onboarding rather than by hand. **Proven live**: staging the previous day's exact breakage gives exit 1 and REFUSED. FOLLOW also found **3 of the 4 live hooks were in no repository at all**.

### Pass 5 — the evidence I said I preserved was never tracked. Commit `3c6f143`
Commit `3c4987d` stated the log and 22 snapshots "are now in the repo". They went into `bench/logs/`, which `.gitignore:41` excludes. **22 on disk, 0 tracked**, and the commit message asserting otherwise was false. Moved to `experimental_notes/evidence/`, stored as `.py.txt` so seat-written code stays out of the source scanners. Repository-wide: **177 of 3,803 cited `bench/logs/` paths are untracked**, 4.65%, Wilson [4.03%, 5.37%].

### Pass 10 — the panel reviewed 3 repairs, and both seats found the correcting sentence repeating the defect
Round 4, 2026-09-10 03:30 to 03:40 BST, seats `cc2` and `fable`, both on the Max subscription, **0 paid dispatches** (`PANEL_ONLY=cc2,fable`). 48 and 35 recorded tool calls; both executed rather than read. Verdict PARTIAL from both. Repairs 1 (restore ordering) and 2 (task 6.7) cleared by both seats under mutation. Repair 3 refused by both, independently, for the same reason: entry 2.1's corrected sentence quoted **97.32%, Wilson [96.17%, 98.13%]**, which is 1,052 of **1,081** — the denominator that same sentence had just retired — matching to 4 decimal places. Corrected to **98.50%, Wilson [97.58%, 99.08%]**.

### Pass 10 — the stop criterion's gamma side does not mean what its own gloss said
`gamma` is fitted to the CUMULATIVE series, so a large opening round produces a sublinear log-log fit whatever the tail does. Reproduced against `_estimate_gamma` and cross-checked against an independent numpy `polyfit` and a scipy `linregress`, all 3 agreeing to 1e-9: the series `[11, 1, 2, 3, 4, 5, 6, 7, 8]`, which rises for 8 consecutive passes, scores **0.324155** and PASSES side (a). **Gamma is not demoted and no threshold moved** — it still correctly returns 0 for constant, linear and doubling discovery. The repair is a printed resurgence diagnostic, wired and tested, which fires on the live series (last 3 passes 21 against 11 in the 3 before).

### Pass 10 — the brief itself carried a wrong figure, and both seats caught it
The round-4 brief stated `gamma` was **0.451**; it is **0.415413**. `GAMMA_BANDS` puts the boundary at 0.45, so the brief upgraded the convergence evidence by one band, in a brief whose subject was 9 wrong figures. Traced: the 8-pass prefix scores **0.453703**, carried forward one pass too long and garbled in prose. `grep` for `0.451` across the task list, the series JSON, the cycle script and every committed note returns nothing — **the artefacts were clean and only the prose was wrong**. Fixed additively: a brief may now declare `<!-- figure: <label> | <script> | <value> -->` and `scripts/panel_brief_validate.py` re-executes it, refusing the brief on disagreement. Wired into the dispatcher before any seat is reached, and it refuses both `0.451` (invented) and `0.453703` (correct but stale).

### Pass 10 — 4 defects in instruments written the same session, found by my own tests
8 mutation tests were **vacuous**: mutants were written to TMPDIR, so each died at startup, produced empty output, and `assert "<figure>" not in ""` passed. A mutant that crashes reads as caught. Mutants now live in `.mutants/` inside the repo — where `parents[1]` still resolves and no suite scanner looks — and the harness refuses any mutant that did not run. One mutation then SURVIVED and was re-aimed: it had targeted a line the reported figure does not read. A measurement script printed a **typed** closing number that a mutation could not move. And a test asserted `g == 0.0` on a value read from a display rounded to 6 places; the true value is 1.5543122344752192e-15.

### Pass 10 — 1.1's cost figure had been corrected twice, each correction inside the last
The entry read *"56 tests in 1.88 s (CORRECTED: '56 tests in 1.88 s (CORRECTED: '28 tests in 1.26 s' never reproduced)' never reproduced)"* — a sentence quoting itself as the thing it refutes. Measured with `scripts/precommit_gate_cost_2026-09-10.py`, which reads the file list out of `hooks/pre-commit` rather than typing it: the hook names **6** files, not 4, and they collect **169** tests, not 56. The script's own first version token-scanned and reported 5 of 6, caught by running it against a known case before believing it.

### Pass 11 — the commit hook could refuse every remaining commit, and carried its own unreachable cure
The section-R commit was refused. The red guard was the Desktop-mirror drift check; the stage that REPAIRS mirror drift was stage 6 of the same hook, 6 stages below the exit. **The repair sat downstream of the check that needed it**, so from the moment the RUNWAY joined the guarded set, every commit touching a mirrored file was refused permanently — and `CDSFL_MASTER_TASK_LIST.md` is a mirrored file. Fixed by ordering: the refresh is now stage 0. It cannot mask a defect, because the repo copy is canonical and the refresh only ever copies repo to Desktop; the guard still runs afterwards and still refuses.

Underneath sat a second defect. **3 hand-written mirror tables existed and all 3 disagreed** — 3 names in `scripts/sync_desktop_mirrors.py`, 2 pairs in the drift guard, 3 names again in `scripts/cdsfl_recover.py`. The union is 4 and the intersection is 1. All 3 keyed on a bare filename, so none could express `RUNWAY_to_BR2_2026-08-18.md`, which declares its mirror at its own line 229 as `~/Desktop/CDSFL_RUNWAY.md` — a different name. The RUNWAY was guarded by a test and refreshed by nothing; the task list and outcomes log were refreshed and guarded by nothing; the restore could not see the RUNWAY mirror at all and would have called a stale one ordinary. One table of pairs now, imported by all 3. The panel had already named the hand list on 2026-09-01 in `bench/logs/panel_fixes_20260901T123808Z/fable.json`; the finding stood 9 days.

The failure message also reported line counts alone, so the first real drift read *"has 814 lines, has 814"* — 2 equal numbers offered as evidence of difference. It now reports bytes, the first differing line, and the command that fixes it.

**AND THE CLOSURE CLAIM WAS REFUTED THE SAME EVENING — THERE WAS A FIFTH MIRROR.** Panel round 8, fable, severity 0.7. `Exp40_to_54_Consolidated_Plan_2026-04-21.md` → `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` is declared 3 times in the notes, the Desktop copy **exists and is diverged right now by 2,606 bytes**, and `Document_Estate_Audit_2026-08-06.md:421` records it as CORE/KEEP_AND_CONVERT with a live instruction to brief panels from it. It was in no table — and **it escaped both directions of the new test**. The declaration regex required the Desktop path within 20 non-backtick characters of the word "mirror", and that declaration puts a backticked repository path there first, so the reverse sweep written to catch exactly this reported nothing. The failure class this pass claims to close, recurring while the closure was being written. The table now holds 5 pairs and the widened regex was enumerated over every note before shipping: exactly 5 real mirrors, 0 false positives.

**Mutation-verified in both halves.** Moving the refresh back below the guards takes 3 tests red, including one that RUNS the hook against a drifted Desktop; dropping the renamed mirror from the table takes 3 different tests red. Sources restored byte-identical, 15 pass.

### Pass 12 — the record of the orphans declared them non-orphans. Commit `397a2d9`

`scripts/scripts_are_reached_2026-09-11.py` asks whether any tracked file mentions a script. Committing it put its own 8 orphan paths into a tracked file, so the figure rose from 111 of 119 to **120 of 120 within 8 minutes of being published**. A ratchet whose record of the orphans makes them non-orphans measures nothing, and it was caught only because `--check` was re-run against the figure that had just been quoted.

**The first fix over-corrected, and that half is the more instructive one.** It excluded 3 whole FILES, one of them the test — which carries 0 roll-call lines and genuinely runs the script. Throwing the file away threw away a real caller, and the count then read 111 of 120 with the instrument itself as the 9th orphan: it reported itself unreached because the fix for reading everything as reached had deleted its only caller. The same defect class as the one being repaired, one level up. The filter now drops the roll-call LINES and keeps the files. **112 of 120 = 93.3333%**, Wilson [87.3949%, 96.5835%], Clopper-Pearson [87.2863%, 97.0781%], both intervals cross-checked by 2 tools.

Reversible: revert `397a2d9`. Nothing outside those 2 files changed and no script was wired or retired — the 8 remain parked for the founder.

### Pass 12 — a suite run in a clone overwrote the file the founder reads. Commit `a72c1c6`

`scripts/cdsfl_recover.py` reported the Desktop copy of the outcomes log as diverged by 6,413 bytes and NEWER than the repository copy. The flake clone's own copy is 27,669 bytes against the working tree's 34,082 — the same 6,413 — so **the founder's Desktop copy had been replaced by an older one from a temporary clone**. The pre-commit mirror refresh restored it 13 minutes later, which was luck rather than design: had the direction been reversed, or had the repository copy not existed, the loss would have been permanent.

The cause is that `DESKTOP` is absolute and `REPO` is not, so any clone or scratch fixture copies the wrong source over the right destination — task A2's shape exactly. **Attributed by execution, not by reading**: each of 43 candidate test files was run under a fake HOME holding sentinels, and exactly 1 rewrote them, the test that clones this repository and commits inside it. The refusal keys on the **passwd** home rather than `Path.home()`, because the legitimate drills fake `$HOME` on purpose and under a faked `$HOME` a drill and an escape are the same path. End-to-end: the offending test now leaves all 5 Desktop files byte-identical and still passes.

Reversible: revert `a72c1c6`. The only behaviour removed is mirroring from a clone or a test, which was never intended.

### Pass 12 — a guard blocked the suite on a panel seat's own words. Commit `a72c1c6`

The full suite failed on `Panel_Roster_Round2_FULL_RECORD_2026-09-09.md` at line 290 — inside the region opened by that note's `verbatim-begin: fable` marker, which is the exemption task V8 added so a seat's words reach the record unedited. **Writing that marker's full HTML-comment form in this paragraph opened a real region here**, and because nothing closed it, 12 paragraphs from this one to the end of the file were silently exempted from the linter that guards them — measured before the delimiters were removed from this sentence.

**That hazard was then closed rather than merely avoided, because it is not specific to this file.** Any note that shows the marker in prose opens a region, and an unclosed region exempts to the end of the file while reporting nothing — an exemption says nothing when it swallows a whole file. 2 independent repairs: an inline code span is now treated as quoted, exactly as a fenced block already was, and an unbalanced pair is reported as a COUNTED finding that the region it describes cannot itself exempt. **Measured across 402 notes: 0 carry an unbalanced region**, so the new check blocks nothing that exists today and its positive control matters more than that figure. The project had pinned the swallow as a known property in `test_verbatim_regions_are_not_linted_2026-09-10.py`, whose own docstring asked for it to be "a known property rather than a surprise" while asserting only that nothing was counted; both halves are pinned now. The lint CLI subtracted the verbatim paragraphs; `test_note_standard_v17_enforced_2026-08-26.py` called the reporter raw and subtracted nothing. Each was internally consistent, so neither could detect the disagreement. `partition()` now owns the split and the CLI CALLS it: 1 implementation with 2 callers, never 2 asserted to agree.

A second, independent defect sat underneath. The Rule 28 check was a bare substring test, so `"the decay curve measure"` fired on "measure**s**" — a verb, using the founder's own term as a subject, which the rule does not ban. **Measured over 402 notes: 28 substring matches against 27 bounded ones.** The boundary drops exactly 1 and it is that verb. The 2 defects are independent, proved by putting the NOUN form inside a verbatim region: still reported, still not counted.

A third followed from the repair. `test_future_timestamp_guard` grepped for the literal `future_stamp(p)` and false-alarmed when the call moved into `partition()` and its variable was renamed — a source-text assertion cannot tell a moved call from a deleted one. It now RUNS the reporter, with the dominance measured rather than asserted: with the call present but renamed the grep form fails and the executing form passes; with the call deleted both fail.

Reversible: revert `a72c1c6`. No note was edited — the seat's sentence stands exactly as `fable` wrote it, which was the point.

### Pass 13 — panel round 15 broke 2 of 5 fixes, and the sharpest finding was a guard that turned itself off. Commit `9348514`

`cc2` and `fable`, free seats only, **0 paid dispatches**. Both returned SPLIT, both reproduced their findings, both delivered fixes rather than problems. Every finding was re-verified here by execution before being acted on, because a fix proposed by a panel seat is a hypothesis until it has been run, exactly as one written locally is.

**THE DESKTOP GUARD FAILED OPEN.** Its first line treated "this is not the passwd user's Desktop" as proof that a drill was running, and returned *allowed* before any other rule was consulted. Under `sudo` this platform keeps `HOME` while the numeric user becomes root, so the passwd Desktop becomes root's, the paths differ, and **the guard classified the highest-privilege run there is as a drill and switched both its remaining rules off**. It failed in the permissive direction, which is the one that lets a clone through. Both seats found it independently and both rated it the sharpest finding of the round. 2 further bypasses followed from the same design: a clone outside the scratch tree satisfied neither rule and replayed the original incident exactly, and with the temporary-directory variable unset a clone in the usual place escaped the temp rule entirely. The decision is now a function of explicit inputs — which is what made all 3 cases reachable by a test — the drill exemption requires displacement INTO scratch rather than mere difference, unreliable identification fails closed, and a marker on the Desktop names the single checkout allowed to write it. Verified end-to-end in all 4 directions after committing. **The remaining limit is written into a test rather than hidden**: with no marker, a clone outside scratch is still admitted.

**A TALLY IS ORDER-BLIND AND AN UNCLOSED REGION IS A FACT ABOUT ORDER.** The balance check written that morning compared the number of opening markers with the number of closing ones, so a stray close before an unclosed open gave 1 and 1 and reported BALANCED while a region was genuinely open and genuinely exempting to end of file — the silent amnesty it was written to end, unchanged, inside the guard meant to end it. A close and an open inside a single paragraph ended the exemption instead of restarting it, because the old walk kept 1 flag per paragraph and applied the close last wherever it sat; **a seat's quoted words were then counted as the note's own, which is precisely the task V8 defeat**. 2 opens in 1 paragraph counted as 1. One ordered walk now, read by both consumers. Corpus differential: **402 notes, 0 whose counted total moved**.

**2 findings were against work done hours earlier and are worth naming plainly.** A control shipped that morning was red in every clone made under the platform's temporary-file root — exactly where the reproducibility harness clones — confirmed by cloning there and running it: 1 failed, 20 passed. It had also been contaminating the intermittent-failure record sitting beside it, since 6 of the 8 censused runs are clones. And a test written to pin an asymmetry left a mutant alive: it covered 3 of the 4 cases in the table, and the uncovered direction was the one the mutant flipped. **3 of 4 quadrants is not a decision table.**

**The panel harness itself crashed after both seats had replied**, `diff -u` under text mode raising on a byte that is not valid UTF-8, so the artefact carrying the seats' FIXES was never written. The replies survived on disk. Reproduced with that exact byte before fixing.

**AND THE CLONE HARNESS DISCARDED THE EVIDENCE IT WAS EXTENDED TO CAPTURE.** The I38 flake reproduced at `37cc328` — the first reproduction since diagnostics were added to its assertion for exactly that moment — and the run reported the test's NAME and nothing else. That is why the entry has read OBSERVED rather than diagnosed across 8 runs: not because the state was unavailable, but because the instrument dropped it. Re-counted with the new run: **3 of 8 full-size runs = 37.5000%**, Wilson [13.6844%, 69.4258%], Clopper-Pearson [8.5233%, 75.5137%]. Both seats made the same point unprompted: 8 observations spanning a factor of 5 is a description of 8 runs, not a rate.

Reversible: revert `9348514`, `3b1cb37`, `68bf559`, `4917b5e`. The only behaviour removed is mirroring the founder's Desktop from a clone, a test, or a second checkout, none of which was ever intended. **A marker file `.cdsfl_canonical_checkout` was written to the Desktop**, naming this checkout; deleting it restores the previous behaviour exactly.

---

## STANDING NUMBERS

| Measure | Value |
|---|---|
| Full suite | measured at each commit with `python3 -m pytest bench/tests/ -q --netguard-strict`; see the closing report for the current figure |
| Task list | **2026-09-11: 94 entries, 83 done, 2 open, 4 blocked, 1 deferred, 4 withdrawn** (was 88 entries, 40 done, 42 open, 3 blocked, 3 withdrawn) |
| Commits since 2026-09-10 00:00 | 127 |
| Commits on 2026-09-11 | 61 |
| Files deleted today | 0 |
| Paid model dispatches today | **0** — panel rounds 3, 4, 14 and 15 all ran `PANEL_ONLY=cc2,fable`, Max subscription only |
| Paid dispatches, WHOLE ARCHIVE | **30 across 79 review directories**, latest 2026-09-05; **0 of the 25 directories since**, Wilson [0.0000%, 13.3192%]. The figure read 10 until 2026-09-11, because the instrument globbed `panel_*` and read a missing `route` field as free |
| Scripts reached by a caller, a citation or a document | **115 of 121 = 95.0413%**, Wilson [89.6029%, 97.7078%]. Producer: `scripts/scripts_are_reached_2026-09-11.py`. The denominator grows; re-run rather than quote |
| I38 artefact-classifier flake | **3 of 8 full-size runs = 37.5000%**, Wilson [13.6844%, 69.4258%]. Producer: `scripts/flake_rate_2026-09-11.py`. 8 observations is a description of 8 runs, not a rate |
| Panel records mirrored | **79 of 79** round directories have a tracked copy |
| FFAFP cycle | 10 passes, series `[11, 4, 2, 3, 6, 2, 3, 2, 9, 10]`, gamma 0.365597, gate KEEP GOING, resurgence flagged |

Counts in this table are produced by `scripts/task_list_markers.py` and `git log`, not typed.

---

## WHAT IS NOT ESTABLISHED

Stated so it is not mistaken for a finding. Whether the falsifier gate ran in the 2026-09-08 run and recorded nothing, or never ran at all, is **OPEN** — the first search term used to test it was wrong and the stronger claim is not asserted without evidence. Whether the intake-parser repair would have prevented the halt is **OPEN**: recovering a block is necessary but not sufficient, since it must still bind to the right finding.

Written under CDSFL note standard v1.7 (26 August 2026).
