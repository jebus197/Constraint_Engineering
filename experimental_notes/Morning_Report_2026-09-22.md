# Morning report, 2026-09-22

Written overnight on 21 September 2026, 22:14 to 23:00 BST. Audience: a reproducing engineer. Every figure below names the script that produced it, and every exit code quoted was captured rather than assumed.

---

## The short version

A state restore ran clean, and it immediately found that the first document the restore protocol reads was stating false facts about the repository. That is now repaired, mechanised and guarded. Folding the day's fixes into the simulated runner then turned up a second gap: one of the commissioning study's 5 arms could not be launched at all, because there was no way to ask for it. Both are fixed. A committed producer was found to overstate its own finding in a way that would have foreclosed a real option, and is corrected. The full test suite ran red at 8 tests, all 8 reproduced serially, and all 8 are accounted for.

---

## 1. The restore, and what it found

`python3 scripts/cdsfl_recover.py --full` returned **exit code 0**. Run again with `--record-restore`, it returned **exit code 0**. Git, Open Brain session context, the operational tracker, the newest `RECOVERY.md` session-state block and the metacognitive command table were all read.

The tracker — `experimental_notes/CDSFL_Agent_Operational_Plan.md`, which its own header calls the "First resource to read after any compaction or long break" — carried this as its live resume pointer:

> HEAD `d17ab01`, main, working tree CLEAN, **11 ahead of `origin/main` — NOT PUSHED**

At the moment it was read, HEAD was `2b56916`, **23 commits later**, and `origin/main` was identical to HEAD. Nothing was unpushed. Every git fact in the pointer was false.

### Why the existing guard could not see it

A staleness guard built earlier the same day, `bench/tests/test_a_stale_source_says_so_2026-09-21.py`, asks whether a canonical document is **old and silent**: it takes the file's git-commit age and requires a supersession banner past 14 days. The tracker had been committed 2 days earlier. No banner was owed and none was missing. The guard was not at fault; age is simply not the variable that goes wrong in a resume pointer. A pointer goes wrong by being **false**, and a false one can be hours old.

This is the `execute-do-not-grep` principle applied to a document rather than a module. The tracker is internally consistent whichever commit it names, so only resolving its claim against the repository can show that the document and the repository disagree.

### The repair

`scripts/resume_pointer_truth_2026-09-21.py` resolves every git claim the recovery documents make. Measured at 22:14 BST: **1 of 1** sources asserting a current git claim stated it falsely, Wilson [20.6549%, 100.0000%]. The interval is wide because the denominator is 1, and it is reported that way rather than dressed up. After the repair the same producer returns **0 of 1** and exits 0.

**The producer's first version over-reported, and was corrected before it was believed.** It charged `resources/RECOVERY.md` with naming a HEAD 399 commits behind, and `docs/CURRENT_STATE.md` with naming one 5 behind. Both were doing exactly the right thing: the RECOVERY block opens `[HISTORICAL — this block describes commit b6a2032 and is NOT current state]`, and `CURRENT_STATE.md`'s header states that its git block is by construction the **parent** of the commit carrying it and is "NOT CURRENT TRUTH". Recording history has to stay cost-free, or a future session comes under pressure to delete accurate history to get the suite green. A disclaimer test was added, and 2 of the new tests hold it shut from both sides — a `HISTORICAL` label 40 lines below a live pointer must **not** excuse it, and a correctly labelled historical block must **not** be charged.

9 new tests, exit code 0. The revert check reconstructs the stale pointer verbatim and requires the 2 claims it made about the *present* — `NOT PUSHED` and `11 ahead` — to be found, plus the ancestor note. It originally required 3, and section 5 records why that was wrong and how the test was passing for the wrong reason. The stale pointer was demoted in place rather than deleted, because the tracker is a record and now carries the account of its own defect.

Commit `f372f0b`.

---

## 2. Folding the day's fixes into the simulated runner

### Arm 3 could not be asked for

`bench/tools/run_simulated_experiment.py` took its panel as `VENDORS[:args.models]` — a **count**, resolved as a **prefix** of a list ordered CC2, DeepSeek, ChatGPT, Gemini, Codex, Fable.

Arm 3 of the commissioning study is a seat contrast between **Codex-SIM and ChatGPT-SIM**, positions 4 and 2. No value of `--models` selects that pair. This was not a flag left switched off; it was an arm with no way to ask for it, and it is the kind of gap a commissioning study exists to find before money is spent rather than after.

`--seats` names them instead. Order is preserved, because seat 0 takes the `player_manager` role and sorting would hand that role elsewhere silently. Duplicates are refused rather than de-duplicated, because the runner builds 2 lists from the selection and its own comment records that they must agree "or the runner counts a different panel than it dispatches" — so the selection is now resolved **once** and both lists read it, where previously they were 2 separate expressions that happened to match. Omitting the flag reproduces the prefix behaviour exactly, so no existing caller changes meaning.

### The rest of the arm configuration

`CDSFL_Programme_of_Study_2026-09-17.txt` specifies the arms run "with routing, the falsifier gate and the admissibility gate on, and the hardened gate, merge arbitration and immune memory off", and the same document records that the run it describes "has no launcher". Checked against the shipped config rather than taken from the note: every item in that sentence was already reachable **except merge arbitration**, which was a bare `True` in the config literal with no flag anywhere.

`--no-merge-arbitration` exposes it, **default unchanged**. Turning it off by default would disable a shipped capability with no measurement showing the run is better without it, which the additive standard forbids in that direction. The flag makes the pre-registered configuration reachable; which arms use it is a ruling, not a default.

`--domain` likewise: it was the literal `statistics` for every target, and it selects the composer's per-domain directives, so a registry-engine or markdown target was being briefed as a statistics problem. **It is deliberately not used by the arms.** `software` is the better description of a Python target, but arm 5 compares this bundle against a pre-window run that used `statistics`, and changing the briefing would confound the one arm whose entire purpose is that comparison.

The argument parser was extracted into `build_parser()`, so the tests parse real argument lists and assert on the resulting namespace instead of reading source. 16 tests.

Commits `522509b` and `8473803`.

---

## 3. The scorer: what the efficacy gate does and does not do

The `e1_efficacy` gate added on 20 September is **wired end to end**, verified by tracing the chain rather than assuming it: the probe is invoked at `reference_runner_v3.py:3805` and `:15618`, writes `entry["fix_efficacy"]` at `:3793`, `:3814` and `:15626`, and `compute_sk` reads it at `:12082`.

Executed against the shipped scorer on the prose target `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, with a captured baseline:

| efficacy outcome | sk | verdict |
|---|---|---|
| cures its own falsifier | 1.000000 | ADMISSIBLE |
| **does NOT cure its own falsifier** | **0.600000** | **ADMISSIBLE** |
| no probe result | 1.000000 | ADMISSIBLE |

A fix measured as **not curing the defect it was written to fix is still admitted.** The ruff baseline of 4 over the extracted listings reproduces the figure recorded under task A19, so the substrate repair is working correctly; it is the threshold that does not bite.

### A committed producer overstated this, and its own table refuted it

`scripts/scorer_gate_limits_2026-09-21.py` was headed "THE DILUTION NO WEIGHT CAN CLOSE" while printing `w=8 -> sk = 0.384615`, which is **below** the corrected break-even S\* = 0.50493. Two different claims had been run together:

- no finite weight drives `sk` to **0** — **true**, and it is the limit the script itself computes;
- no finite weight changes the **verdict** — **false**.

A fix is rejected at `sk < S*`, not at `sk = 0`, and S\* is approximately one half, so the first does not support the second. Solved symbolically rather than read off a table: rejection requires

> **w > W_rest · (1 − S\*) / S\***

which is finite for every S\* > 0 and exactly `W_rest` at S\* = 1/2. On a Python target that threshold is **4.9024** against other gates totalling 5; on prose it is **2.9414** against 3. Cross-verified on 2 tools: SymPy for the closed form, z3 for tightness — the search for any `w` at or below the bound that still rejects returns **unsat**.

So the dilution **is** closable by weight, at a weight that makes efficacy worth about as much as every other available gate combined. That is a demanding design statement and a decidable one. Recording it as impossible would have foreclosed an option that is the founder's to rule on. S\* is computed per entry from `nu_b`, `nu_f`, `q` and `R`, so the required weight moves with the operating point, and the formula is reported in place of a single number.

**A false alarm, recorded so it is not raised again.** The prose scoring probe first appeared to show `e1` discarding a definite verdict, reporting `score: None` against an outcome of `FIX_CURES`. The gate was correct and the probe was wrong: the shipped constant is `FIX_CURES_ITS_OWN_FALSIFIER`, and the harness had passed a string the gate has never heard of.

---

## 4. The test suite

`python3 -m pytest bench/tests/ -q --netguard-strict`, run at `2b56916`: **8 failed, 8286 passed, 5 skipped, 1641.45 s**, captured exit code **1**.

**The completion notification reported exit code 0 and was wrong.** The command ended with a trailing `tail`, so the shell returned that command's status rather than the test runner's. The captured `$?` written into the output file is the reliable value. This is the same exit-code-masking defect corrected earlier the same day in its pipe form, reintroduced in its sequence form.

All 8 were reproduced **serially** before anything was touched, which is what separates a real defect from a parallelism artefact. All 8 reproduced. They fall into 3 groups.

**Group 1 — 4 tests, unmirrored panel records.** The `final_review_2026-09-21` round existed in the ignored log directory and had never been copied out. The test named its own remedy. `scripts/mirror_panel_records_2026-09-11.py` copied 11 files; the check now reports **90 of 90 rounds preserved, 100.0000%**, Wilson [95.9064%, 100.0000%], Clopper-Pearson [95.9841%, 100.0000%], exit code 0.

**Group 2 — 2 tests, the unreached-script ratchet.** `scripts/estimate_nu_from_archive_2026-09-21.py` and `scripts/gamma_is_still_a_gate_2026-09-21.py` were reached by nothing. Both are evidence for live questions and are cited here, which is the honest discharge rather than a suppression. The first estimates the re-injection rate `nu` from the archive; **its conclusion was withdrawn on 21 September**, because `e2` is `passed/total` with no baseline and so conflates "the fix broke the suite" with "the suite was already red". The second decides, by driving the real convergence predicate, which of 2 contradictory sources is true of the shipped code where the appendix says gamma no longer gates.

**Group 3 — 1 test, a guard that read source instead of running it.** `test_the_simulated_launcher_sets_both_lists` asserted that the literal string `models=VENDORS[:args.models]` appeared in the launcher's text. The launcher was changed so that both lists read one resolved variable, which is a **stronger** guarantee than 2 expressions that happen to agree, and the text matcher went red on the improvement. Its real failure is that it cannot distinguish a correct refactor from a regression.

It now runs the launcher with both config constructors intercepted and compares the lists actually built. Mutation-verified: diverging `RunnerConfig.models` from the dispatched panel produces `['Codex-SIM', 'ChatGPT-SIM'] vs ['CC2-SIM', 'DeepSeek-SIM']` and a red test; reverting restores exit code 0.

---

## 5. Two safety mechanisms that deadlocked, and a guard of mine that would have gone red on every commit

### The deadlock

Arm 1 of the study failed to start, exit code 2 at 22:51:57 BST, and the reason is worth keeping.

A simulated run happens inside a **disposable copy** of the repository whose git history is **deliberately severed**, so a seat cannot ask `git diff` which lines were recently changed and read the answers off. Separately, the runner **confines the panel to a disposable git worktree** so a seat's relative writes cannot reach the live target, and **refuses to run** if it cannot build one. That worktree is built with git.

So the copy removes the history, the confinement requires it, and the runner correctly refuses rather than running unprotected. Both mechanisms are right on their own. Together they made **every sandboxed simulated run unlaunchable.**

**It had been unlaunchable for 13 days, and nothing noticed because nothing tried.** The refusal was introduced at commit `f011c1a`, 2026-09-08 04:29:45 BST. The last simulated run before tonight started at 2026-09-08 03:30 — *before* that commit. So no sandboxed simulated run was attempted in the intervening 13 days, and arm 1 is the first thing to exercise the path since. It failed on the first attempt. Confirmed against `a2a0197` (2026-09-06, the arm 5 baseline commit), where the refusal is absent: arm 5 does **not** hit this deadlock and remains launchable, though it predates `--seats` and so must select its panel with `--models 5`.

The repair recognises that what the confinement protects against — a write reaching the *live* target — is already impossible inside a throwaway tree, and builds the same isolated directory by copying instead. The wrapper exports the directory it created; the runner **resolves and compares it against its own root** rather than trusting it, so a stale or hostile value naming another directory unlocks nothing. 12 tests, most of them on the lock rather than the key. One records where the protection actually rests: inside a real checkout `git worktree add` succeeds, the fallback is never reached, and that test asserts the live repo is still a git checkout — because the day it is not, the declaration becomes load-bearing alone.

### The guard I wrote at 22:14 was wrong by 22:59, and executing it is what showed that

Two faults, both in the resume-pointer check from section 1, found by running it again after 6 further commits rather than by re-reading it.

**It required the pointer to name the current HEAD.** A resume pointer is written once; HEAD moves with every commit. So it failed on the next commit and would have failed on every commit after, including ones with nothing to do with project state. **A check that is red by default is one that gets disabled, and a disabled check is worse than none.** What a resume pointer legitimately does is record where a session stopped, so the named commit must now be real and an **ancestor** of HEAD — still catching a fabricated hash, a rewritten history or another branch — with its distance reported as information. The original defect is still caught by the part that always should have carried it: `11 ahead of origin/main — NOT PUSHED` are claims about the state **right now**, and both were false.

**`git merge-base --is-ancestor` conflates "no" with "git failed".** It exits 0 for ancestor, 1 for not, and other codes for errors. Reading any non-zero as "not an ancestor" produced a confident false statement — *"it is on another branch or from a rewritten history"* — about a repository git had merely failed to read.

**And the revert test was green for exactly that reason.** It monkeypatches the repo root to a temporary directory and redirected only the `git` helper, not the raw subprocess call, so `merge-base` ran against a non-repository, errored, and was counted as a refutation. It asserted 3 failures and got 3 — **the wrong 3.** The two helpers now redirect together, and the test asserts the 2 present-tense claims plus the ancestor note *by name* rather than counting. 9 tests.

---

## 6. THE RUN'S FIRST REAL FINDING: seats understate their own R_k, 17 times out of 17

Round 0 of arm 1 closed at 23:09, and the falsifier gate, the corrected-copy splicer, the discrimination control and the scorer all ran end to end: **8 CONFIRMED, 0 REFUTED, 3 to HIL** from the falsifier gate, tools deciding rather than models voting; 17 corrected copies accepted with 0 refused, 0 unmatched and 0 dropped; the discrimination control returning DISCRIMINATES=5, INDETERMINATE_ERROR=2, NO_DISCRIMINATION=1; and one mechanical fault escalated to a human rather than silently closed. **`e1_efficacy` fired in a live run** — `FIX_CURES_ITS_OWN_FALSIFIER` on C0007 — so tonight's scorer repair is commissioned in practice and not only in tests.

Then the R_k validation rejected 17 self-reported proofs:

| seat | result |
|---|---|
| CC2-SIM | FAIL=4, SKIP=1 |
| Gemini-SIM | FAIL=4 |
| DeepSeek-SIM | FAIL=5 |
| ChatGPT-SIM | FAIL=4 |
| **Codex-SIM** | **PASS=5** |

**Every one of the 17 deltas is positive.** The recomputed value exceeds the seat's stated value in 17 of 17 cases and never once the other way: 100.0000%, Wilson [81.5682%, 100.0000%], Clopper-Pearson [80.4936%, 100.0000%]. Against the hypothesis that a slip is equally likely in either direction, the exact sign test gives **p = 1.525878906e-05**, computed twice and agreeing to 1e-12 (scipy's `binomtest` against the closed-form tail in mpmath at 50 digits). Mean delta **0.204294**, median 0.260000, range 0.059000 to 0.348000. A one-sample t-test gives p = 1.421603e-06 and Wilcoxon p = 1.525879e-05.

A seat making arithmetic slips errs in both directions. **A perfectly one-sided result is a systematic difference between what the seats compute and what the runner computes** — a formula or input discrepancy, not sloppiness. The direction is the informative part: the seats report *lower* residual risk than the runner derives, which in the model's own terms means overstating how much a fix accomplished.

**Why this matters beyond tidiness.** `severity_is_proven`, the 2026-09-06 interlock, requires a stamped R_k proof that recomputes before a severity demotion is permitted. If self-reported proofs routinely fail to recompute, that interlock is never satisfied and the severity-calibration machinery this run exists to exercise cannot reach its demotion path — for a reason that has nothing to do with severity. That is exactly the class of thing a commissioning run is for.

**Not explained here, and deliberately so.** Codex-SIM passed 5 of 5 while the other 4 seats failed, and every seat is the same underlying stand-in model, so this is not a capability difference between models. It depends on the findings or their inputs. The producer establishes that a cause exists and that it is one-directional; identifying it is the next question and is not answered tonight.

Producer: `scripts/rk_self_report_bias_2026-09-21.py`.

---

## 7. What the commissioning run cannot conclude, stated in advance

**No canary catalogue is available, so no ground-truth defects are seeded.** A `CRITICAL_QUIESCENCE` convergence therefore cannot distinguish "the target is genuinely clean" from "the panel is dead". The sandboxed launcher's own note records exactly that happening on 2026-09-01, with a vacuous curve and zero critical findings across a whole run.

The catalogue is answer-key material and is the founder's in person. Generating one unilaterally is refused by design: `Canary.generator` is load-bearing and `detection_rate` will not report on a single-generator held-out set, because such a set measures whether reviewers have learned one generator rather than whether they can still detect. The route that works is **cc2 and fable as independent generators**, which costs nothing and follows.

---

## 8. Outstanding, with the decisions taken in the founder's absence

Of the 4 items the study scope listed as needing a ruling, 1 was resolved by the panel. The other 3 were given safe defaults rather than left to block, and each is reversible:

1. **Seat contrast arm** — run in its weak form and **reported as weak**. In simulation both seats are the same stand-in model under different labels, so the contrast is weak by construction, not by accident.
2. **I31 drift detector** — the proposed save and restore changes do **not** land before the run. Introducing unreviewed changes immediately before a commissioning run would confound what the run measures.
3. **Wolfram in panel reviews** — denial remains the default in force. No change.

**For a ruling when convenient:** whether `e1_efficacy` should carry a weight that lets it reject alone (4.9024 on a Python target, 2.9414 on prose), or whether efficacy belongs in the hard-gate product `A` rather than the effect mean `E`. The second would make any non-curing fix score 0 outright. Both change what is admitted on every target ever run, which is why neither was done unilaterally. The commissioning run measures how often the case actually arises, so the ruling can be made against data rather than in the abstract.

---

## Producers and evidence

| Claim | Producer |
|---|---|
| Resume pointers resolve against git | `scripts/resume_pointer_truth_2026-09-21.py` |
| Efficacy-gate limits and the corrected weight threshold | `scripts/scorer_gate_limits_2026-09-21.py` |
| Panel records preserved, 90 of 90 | `scripts/mirror_panel_records_2026-09-11.py --check` |
| Scripts reached by something | `scripts/scripts_are_reached_2026-09-11.py --check` |
| Gamma still gates in the shipped runner | `scripts/gamma_is_still_a_gate_2026-09-21.py` |
| Re-injection rate from the archive (**conclusion withdrawn**) | `scripts/estimate_nu_from_archive_2026-09-21.py` |

Commits: `f372f0b`, `522509b`, `8473803`.

Written under CDSFL note standard v1.7.
