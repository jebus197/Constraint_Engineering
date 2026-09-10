# A cap that sat inside the distribution, and one defect shape found 15 times in a night

**2026-09-07 23:40 to 2026-09-08 03:05 BST.** All timestamps read from the machine clock rather than estimated. This note consolidates and supersedes `Overnight_The_Defect_Class_And_Two_Release_Blockers_2026-09-08.md`, which covered the first hour; everything in that note is carried forward here, and the sections after "The night's second half" are new.

## The headline: an experiment was losing half its panel to a timeout that was 6 percent too small

A simulated Experiment 45 run was launched at 02:18 BST against `bench/dm/_memory.py`, with 6 seats and a maximum of 16 rounds. It lost **3 of its 6 seats in round 0** — the blind baseline round, the one every later measurement is compared against. Each of the 3 was killed at exactly 900 seconds having returned 0 characters. The 3 that survived took 624, 768 and 845 seconds. The largest success was **94 percent of the cap**.

The runner accepted the half-empty round and carried on. That is what made it serious: a blind baseline built on half a panel propagates into every convergence statistic downstream, and nothing in the run's own output called it a problem.

The cap was set in `bench/tools/run_simulated_experiment.py` with the comment "900 matches the live CC2 timeout in the real panel". That is a per-seat justification for a parameter whose failures compound per run. A 6-seat, 16-round experiment makes **96 dispatches**, and losing any one of them damages a round.

`scripts/seat_timeout_budget.py` was written to answer the question from the archive rather than from a sibling's setting. Over **2,221** archived seat dispatches that record their own duration (median 288 seconds, 95th percentile 932 seconds, 99th percentile 2,068 seconds, maximum 5,194 seconds):

| cap | per-seat loss rate | probability a 6-by-16 run loses no seat at all |
|---|---|---|
| 900 s | 5.45% | **0.5%** |
| 1800 s | 1.44% | 24.8% |
| 2400 s | 0.77% | 47.8% |
| 3600 s | 0.32% | 73.9% |

**At 900 seconds, a full-strength run was a 1-in-200 event.** The cap was raised to 3600 seconds at source, so the correction travels with the code rather than with one person's command line. Raising it is close to free: a round takes as long as its slowest seat either way, so a higher ceiling costs wall-clock time only when a seat genuinely hangs, which at 3600 seconds is expected 0.30 times per run.

### The proof arrived within the hour

The run was restarted at 02:42 with the new cap. Round 0 completed at 03:13 with **all 6 seats returning**: DeepSeek-SIM 662 seconds, Fable-SIM 887, Codex-SIM 958, ChatGPT-SIM 976, Gemini-SIM 1,076 and CC2-SIM 1,870. The slowest seat used 52 percent of the new cap.

**Four of those 6 exceed the old 900-second ceiling.** Three by only 6.4, 8.4 and 19.6 percent, and CC2-SIM — the player-manager seat — by 108 percent. They were never hung. They were marginally slow, and the ceiling sat in the middle of them. Under the previous cap those 3 seats would have been killed at zero characters, exactly as the 3 seats were an hour earlier; instead they returned 42,302, 51,169 and 39,498 characters of analysis. Seats exceeding 900 seconds in the clean run: **4 of 6, 66.7 percent**, Wilson 95 percent confidence interval [30.0%, 90.3%], Clopper-Pearson [22.3%, 95.7%]. Bounds computed with statsmodels and re-derived independently in mpmath.

**The yield difference is the point.** The half-empty round 0 produced **8** findings. The full-strength round 0 produced **27**, with 20 corrected copies derived from proposed fixes. That is a difference of 19 findings between the 2 baseline rounds, and nothing in the run's output said so. The comparison is 1 run against 1 run, so it indicates the size of the loss rather than establishing it.

This also corrects the first diagnosis. The standing instruction is to assume broken machinery when convergence looks out of reach, and the run was stopped on exactly that basis. The measurement says the runner and the 6 seats were **not** broken: the 900-second wall-clock cap in `run_simulated_experiment.py` was the single wrong parameter. Stopping to diagnose was still the right call, because pushing on would have produced a converged-looking result built on a half-empty baseline, and nothing downstream would have flagged it.

The residual is stated rather than assumed away. Losing 3 of 6 is still inconsistent with even the corrected archive rate of 5.45 percent (binomial test, `scipy.stats.binomtest`, p = 2.9 x 10^-3, cross-checked against an exact mpmath tail agreeing to 1 part in 10^19). Six concurrent seats on a 20,698-character target are genuinely slower than the archive's mixture of configurations. If seats still die at the new ceiling, the answer is retry-on-timeout rather than a larger number — and `ModelConfig.max_retries` already exists as a real dataclass field that `bench/reference_runner_v3.py` reads **nowhere**.

## An aborted run left a tracked source file rewritten, and the cause is not what this note first said

**The observation, measured.** After the first run was killed, `bench/dm/_memory.py` stood at 25,861 bytes against its committed 20,605 — 99 lines inserted, 9 removed, including a new `import os` and a dropped `field` import. Its modification time, 02:29:45, falls inside that run's window. The restart 11 minutes later dispatched against that file.

**The explanation first written here was wrong, and the correction matters.** This note originally said the runner splices corrected passages into the target as normal mid-run behaviour, and that killing a run leaves the mutation behind. Read rather than assumed: `_splice_corrected_copy` and `_derive_corrected_copy_from_fix` in `bench/reference_runner_v3.py` are **pure string transformations with no disk write**. The log line `corrected copy DERIVED C0027 ... spliced into bench/dm/_memory.py (20,829 chars)` names the target path for context and describes an **in-memory** copy. The only write to a target anywhere in the runner is `reference_runner_v3.py:9436`, and it writes into a **sandbox** copy under a comment that says so.

**A seat wrote it, and this was then observed directly rather than inferred.** The panel seats are launched with `working directory: (inherited — repo)` — they execute inside the repository. A later run was watched with a continuous integrity check, and the target was caught being rewritten **twice inside 1 minute** while 5 other seats were reviewing it: 22,682 bytes at 03:39:50 and 23,831 at 03:40:30, against a committed 20,605. The diff is unmistakably a model's proposed repair, carrying prose comments in the project's own house style — "A THRESHOLD IS COMPARED, SO IT MUST BE COMPARABLE" — written 4 minutes into the round, before any seat had returned a reply.

**Three of the six seats reported it themselves, unprompted.** Gemini-SIM: "a review of the target file cannot be trusted while the target mutates during it." CC2-SIM: "The target file mutated under me mid-review." Fable-SIM described a complete apply-then-revert cycle.

**An intermediate explanation was wrong and is withdrawn.** Fable-SIM attributed the cycle to process 2369, an orphaned 27-hour runaway with the repository as its working directory. That process was real and was killed, but the target was rewritten again afterwards, which refutes it. The seat had also misidentified 2369 as "the Exp 45 simulated run" — a misattribution visible at the time, since 2369 started the previous day — and that error was noticed and the conclusion adopted anyway. Model output about the environment is data to check, not evidence to adopt.

## The confinement that should have prevented it has never worked

`RunnerConfig.panel_cwd` exists to keep a shell-bearing panel out of the repository. `run_experiment` applies it at `bench/reference_runner_v3.py:12097` by calling `set_panel_cwd(cfg.panel_cwd or None)` **once, on the main thread**. The seats are then dispatched from a `ThreadPoolExecutor` at `:8244` and `:8337`, and the value is stored in a `threading.local`. A fresh worker thread has no value at all, so the lookup returned nothing and each seat subprocess launched with `cwd=None`, inheriting the repository.

Demonstrated by execution rather than argued: the main thread sees the sandbox, 3 worker threads see `[None, None, None]`.

**So the confinement was inert for every threaded panel dispatch, including the withheld-exam runs it exists to protect.** `bench/build_experiment_run.py` works only because it sets the value inside the same function that dispatches — its own comment records why it was added, after a model edited the runner in the live tree on 2026-08-22.

The runner's target-integrity guard could not catch the writes either: it compares a hash **between** rounds, and these happen **within** one. A check whose granularity is coarser than the event it exists to detect.

Repaired the way this project had already chosen for its confer panel on 2026-09-07: the value is carried to the worker by a module mirror and applied **on the worker's own thread**. A first attempt used a module-level fallback inside the accessor so a main-thread set would reach workers; that made `test_panel_sandbox_2026-09-07.py` fail, which is exactly what that guard exists for — the thread-local is deliberate, so one dispatch's cleanup cannot unsandbox another — and it was withdrawn. `bench/tests/test_panel_cwd_reaches_worker_threads_2026-09-08.py` executes the real seat dispatcher from a real pool worker, 4 tests, mutation-verified.

## The confinement is necessary and NOT sufficient, and the reason is a ruling working correctly

With the repair verified live — 1 main-thread call and 6 per-worker calls in the run log — **a seat rewrote the repository target twice more**, at 04:20:52 and 04:22:22, reaching 24,834 and 25,650 bytes against a committed 20,605. The mutation was captured mid-cycle. It is unmistakably a seat's proposed fix, carrying its own experiment in prose: "measured over 400 in-control sequences ... 400/400 alarmed, median 37 observations to the false alarm, earliest 8."

A working directory confines **relative** paths. Seats are handed the **absolute** repository path to their target by `_absolute_target`, under the founder's ruling of 2026-08-23, and that ruling is right for reasons its own docstring records: a repo-relative name cannot be redirected into the discrimination control's overlay, and cannot be found at all from a throwaway working directory — which is what left 6 Experiment 55 falsifiers returning ERROR while the 2 detached ones returned CONFIRMED. Bash is a superset of write, so an absolute path defeats any working directory.

**So `panel_cwd` is not merely unwired for threaded dispatch; for a shell-bearing seat it is the wrong mechanism.** That could not be seen before, because it never functioned well enough to fail visibly.

The remaining repair is to resolve the absolute path against the sandbox when one is set — `_absolute_target` already accepts a `repo_root` — but it changes which paths appear in findings and interacts with `_retarget_falsifier`, which substitutes the absolute repository root. It touches a founder ruling and was not taken unilaterally.

## A causal claim made in this note, and withdrawn

An earlier version of this note presented the target mutation as the cause of the round's high escalation. **That does not survive checking.** `panel_cwd` has been inert for threaded dispatch throughout, so the archived Experiment 45 — the run that converged at round 3 with 2 of 23 escalated — was equally exposed to seats editing the repository. A condition shared by both runs cannot explain the difference between them. The mutation is a real defect; it is not the explanation for the escalation, and what does explain that remains open.

**The current run is clean, and was watched for this.** `git status` reports no tracked file differing from HEAD, and the target is byte-identical to blob `539f6a4`. Three tracked files unrelated to the experiment — `scripts/replay_accounting.py` and 2 panel-record notes — had their modification times touched at 03:09:22 and 03:14:21 during the adjudication phase, with **content identical to HEAD** in all 3 cases. Touched, not changed.

Whatever wrote it, the consequence is the same: the restart would have produced an "Experiment 45 comparison" against a target rewritten during a half-empty blind round, which is precisely the confound Experiment 45 was chosen to avoid.

It was caught 2 minutes in, by noticing that the run banner said 25,861 bytes where the previous banner had said 20,563. The check that catches this cheaply: **compare the byte count in the run banner against `git show HEAD:<target> | wc -c` before accepting any restart.** The target was restored to blob `539f6a4` from commit `ce08914`, verified by hash equality rather than by inspection, and the mutated file preserved as `_memory.py.MUTATED_BY_ABORTED_RUN` beside an `ABORTED.txt` in the dead run's directory. Both abandoned run directories carry that marker so no future archive scan reads them as evidence.

## The run's verdict, and the fault it found

The Experiment 45 run started 04:30 ran **4 rounds in 311.6 minutes** and stopped at `HALTED_IRREDUCIBLE_QUEUE_ALARM` with 61 findings. It did not converge. Under the founder's standing rule that a non-converging run indicates broken machinery, it was diagnosed rather than reported as a result — and the diagnosis found a real fault, though not where the investigation had been looking.

**The halt was correct.** The irreducible-queue alarm fires when criticals locked as unresolvable exceed a bound of 2; it found 5. Its own notification states the governing principle and the trap: "a queue this size is overwhelmingly a MECHANICAL failure ... Do NOT raise max_irreducible_queue to clear this — that is how the same alarm was suppressed twice on 2026-08-01 while it was right."

**The fault is falsifier supply, upstream of every mechanism under examination.** Of the 14 critical-severity findings the run produced, **5 arrived with no runnable falsifier** — a supply rate of 64.3 percent, Wilson 95 percent confidence interval [38.8%, 83.7%] — and those 5 are exactly the queue that halted the run. They came from 4 different seats, so this is not one misbehaving panellist. The project's founding requirement is that every critical finding arrives with a runnable check; it held for 9 of 14.

**Everything downstream of that worked.** The routing ladder absorbed **10 of the 12 findings it was actually given, 83.3 percent**, Wilson [55.2%, 95.3%]; against the archive's mechanically impaired band of 2.0 percent that is z = 5.13, p = 1.4 x 10^-7, Fisher exact p = 2.6 x 10^-6 with an odds ratio of 54, and against the healthy band of 68.3 percent it is statistically indistinguishable at p = 0.179. The residual human queue across all 4 rounds was **1**.

| round | novel | escalated | absorbed | to human | deferred |
|---|---|---|---|---|---|
| 0 | 27 | 7 | 6 | 1 | 1 |
| 1 | 9 | 2 | 1 | 0 | 1 |
| 2 | 7 | 2 | 1 | 0 | 0 |
| 3 | 18 | 8 | 2 | 0 | 5 |

The round-3 rebound in novel findings, 7 to 18, is not itself anomalous: the archived Experiment 45 that converged cleanly went 11, 11, 6, 11. What differs is the deferral column, which is the falsifier-supply shortfall arriving as a queue.

## One run, two directories — and every archive count is doubled for it

Measured while repairing the drift the run caused: **the runner writes two directories per run.** Tonight's produced `sim45_memory_20260908T033008Z`, holding the immune-pipeline log and the run report, and `...033012Z` four seconds later, holding the 48-file run state. **Both carry the registry**, so any archive scan that walks directories counts each of that run's 61 findings twice.

This is not theoretical and it has now bitten twice in one night. A seat-duration scan double-counted every run written this way; deduplicating moved the 99th percentile from 1,605 to 2,068 seconds and the per-seat loss rate from 3.43 to 5.45 percent — the error ran in the reassuring direction. Then the latent tagger's archive-exposure tripwire grew from 5 entries to 11, of which the 6 new ones are 3 findings listed twice, and its companion safety test from 2 removals to 6, of which 4 are 2 findings listed twice.

Both tripwires were updated rather than suppressed, and in the safe order: the tagger was confirmed unchanged before the exposure list was moved, and the fail-safe property `added == []` was confirmed to still hold before the removal record was extended. A tripwire is only safe to move once the tagger it watches is shown not to have moved.

**Whether the runner should stop emitting 2 directories is a separate decision and is not taken here.** What is recorded is that until it does, every directory-walking measurement over this archive is inflated for runs written since the pattern began, and the correct guard is to deduplicate on the tuple of run, seat, round and value rather than on directory.

## The gate-count pair, re-measured because the archive grew

`sk_threshold_shadow`'s docstring stated that `s_star` is zero in 3,816 of 3,816 archived gate records, Wilson [99.90%, 100.00%]. Tonight's run added 326, and `test_stated_gate_count_matches_measurement_2026-09-07.py` refused the stale pair with its own instruction: "Correct the count AND recompute the Wilson interval beside it — fixing one leaves the pair lying."

Re-measured: **4,142 of 4,142, Wilson [99.91%, 100.00%]**, across 6,727 JSON files. The encoding split is 3,507 strict floats and **635 strings, unchanged**, still confined to the same 4 `sim45_*` families. The lower bound rose exactly as the closed form n/(n+z²) requires at k = n, 99.90 to 99.91 percent, cross-checked in mpmath to 1 part in 10^16. Both halves were corrected together.

## Two defects in the alarm's own evidence path

Both were found by trying to act on the halt, and both defeat the adjudication the halt exists to enable.

**The evidence bundle was empty.** `irreducible_queue_count()` counts entries flagged `irreducible_escalation` **or** `routing_deferred`; the loop that collects the per-finding evidence tested only the first. A repair on 2026-09-07 added `routing_deferred` to the count for well-measured reasons and did not add it to the collector. So a queue made entirely of deferred items — which is what tonight's was — fires the alarm and then describes nothing. The run log reads "5 criticals are locked as irreducible" and, three lines later, "Evidence for all 0 item(s)" and "0 of 0 carry no falsifier at all". The alarm's own instruction is to read the bundle rather than move the line, and the bundle was unreadable. Fixed so the collector matches the counting predicate exactly. Verified against the halted run's saved state, where the headline of 1 and a bundle of 0 became 1 and 1, and mutation-tested by restoring the old predicate, which returned the bundle to 0.

**The deferral reason stated a falsehood.** It recorded "no falsifier and no S_k evaluation exist, so nothing has been assessed yet" for entries that carry one: C0055 has an S_k result of REJECTED, and C0057 a complete passing evaluation — ADMISSIBLE, 0.9782, 52 of 55 sandbox tests, ruff and bandit clean. Deferring them remains correct, because a critical is resolved by a runnable falsifier and S_k measures the quality of a fix rather than the truth of a claim, but the record must give the reason that applies instead of denying evidence sitting on the same entry. The message now states the verdict that triggered the deferral and discloses any S_k result.

A first version of that second fix asserted "an equipment failure" as fixed text, on the reasoning that the branch is only reachable on ERROR or UNTOOLABLE. Replaying it against the halted run showed it printing "the falsifier verdict is CONFIRMED, an equipment failure", because the post-halt sweep can rewrite a verdict after the deferral was recorded. The phrase is now checked rather than asserted.

## The escalation queue: the diagnostic is absorption, not escalation

The founder's standing rule is that an unusually high human-escalation queue signals broken machinery rather than a hard document. Round 0 escalated **9 of 11** findings at the falsifier gate, so the rule fired and the run was paused.

**The first attempt to judge that number was the wrong instrument, twice over.** A pooled rate across every archived gate event — 170 of 432, **39.35%** — was computed and called "the archive baseline". The founder rejected it from memory. He was right: split by the record's own account of each run, documented-compromised runs escalate at **65.5%** and the rest at **30.4%** (z = 6.49, p = 4.3 x 10^-11). A pooled mean over a population that is heterogeneous by a property already known is a mixture, not a norm. `docs/GLOSSARY.md` had already recorded the governing doctrine, including the trap: the alarm's premise is that a large irreducible pile "almost always indicates broken machinery rather than an unusually hard document", vindicated on 2026-08-01, and **"raising the bound twice was wrong both times"**. Searching for a number like 39.35% to judge escalation against is the same move as raising the bound from 2 to 3.

**The second error ran the other way.** The report then compared the archived Exp 45 at 2 of 23 against tonight's 9 of 11 and implied a large residual queue. But `_apply_routing` — the only absorber between the falsifier gate and the human queue — runs *after* the gate, and the run had been stopped while it was still working. The gate tally is the load arriving at the absorber, not the queue leaving it.

**The instrument that does separate the record is absorption: how many of the escalated findings the ladder actually cleared, 1 of 50 against 82 of 120.**

| run | gate escalated | absorbed by routing | rate | what the record says |
|---|---|---|---|---|
| Exp 45 | 2 | 2 | 100% | converged at round 3 |
| **Exp 49** | **26** | **25** | **96.2%** | key-exposure run |
| Exp 48 | 18 | 16 | 88.9% | key-exposure run |
| Exp 44 | 34 | 21 | 61.8% | clean convergence, round 12 |
| Exp 47 | 26 | 10 | 38.5% | converged |
| Exp 43 | 9 | 1 | 11.1% | did not converge |
| Exp 43 rerun | 13 | 0 | 0.0% | needed mechanical repairs |
| **Exp 55** | **28** | **0** | **0.0%** | halted at round 0, falsifiers starved |

Runs the record calls mechanically impaired absorbed **1 of 50, 2.0%**; the rest absorbed **82 of 120, 68.3%**. z = 7.88, p = 1.6 x 10^-15; Fisher exact p = 1.6 x 10^-17, odds ratio 105.7.

**Experiment 49 escalated 76.5% at the gate — the highest figure in the archive — and was healthy, because the ladder absorbed 25 of its 26.** A high escalation rate is not the alarm. A ladder that absorbs nothing is. That is exactly the 2026-08-01 case, where routing went 0 for 25 because it was handed findings carrying no target path and no target text while recording "no model produced a runnable test".

### The measurement, taken

The run restarted at 04:30 completed round 0 at 05:51, 80.7 minutes end to end, with all 6 seats returning (825, 997, 1139, 1252, 1274 and 1562 seconds — 4 of the 6 over the old 900-second cap). 27 findings, rho 1.000.

**Gate: 4 CONFIRMED, 0 REFUTED, 7 escalated. Ladder: 6 resolved by strong writer, 0 deduplicated, 1 to the human queue, 1 deferred as never assessed.**

**Absorption 6 of 7, 85.7%**, Wilson 95 percent confidence interval [48.7%, 97.4%], Clopper-Pearson [42.1%, 99.6%]. Against the archive's mechanically impaired band of 2.0 percent: z = 6.32, p = 1.3 x 10^-10 by `proportions_ztest`, Fisher exact p = 1.3 x 10^-6 with an odds ratio of 294, cross-checked against an exact mpmath tail at 4.4 x 10^-10. Against the healthy band of 68.3 percent: z = 0.97, **p = 0.333, indistinguishable**.

**The falsifier gate and the routing ladder are sound.** All 7 escalations were engaged with substantive dispatches of 7,400 to 11,500 characters each, across a ladder bounded at 2 rungs — the failure mode in exp55 and the Experiment 43 rerun was a ladder that engaged and resolved nothing, 0 of 28 and 0 of 13.

The single deferred finding is a recent repair working rather than a fault. `bench/reference_runner_v3.py:5417` records why: findings with no falsifier and no S_k were previously "never assessed, then labelled as findings no machine could assess", and **every irreducible-queue alarm in the archive, 4 of 4, fired at round 0** on that mislabelling. Such a finding now stays open and blocking, which is the fail-safe direction. So the founder's heuristic — that a high escalation queue signals broken machinery — has been correct in every archived instance, and the instrument it was detecting has since been repaired.

The script is `scripts/hil_escalation_by_run.py`, which prints the absorption table and refuses the pooled figure in its own output.

## The shape of the night: a bounded traversal standing in for a complete one

The evening began with a sealing procedure that failed 3 times in the founder's hands and cost a 60-mile round trip. The cause was 1 line: `chmod 600 "$STORE"/*` in `unvault()`. That glob matches **directories**, and mode 600 strips a directory's execute bit, so `targets/` and `clearances/` became untraversable and the next `tar` died with `Cannot stat: Permission denied`. It would have recurred on every unseal-reseal cycle.

That was the 5th instance of one shape in a single file. The others, all corrected on 2026-09-07: a manifest built with `shasum -a 256 *` that omitted 27 of 31 keys while `verify` passed against the truncated result; a store count of `ls -1 | wc -l` reporting 4 keys for 29; the same construct in `verify` printing "opened: 18 file(s)" seconds after "sealed: 53 keys"; and a register that enumerated only `$STORE` while every file lived in legacy stores folded in later.

Five instances of one bug in one file is a pattern rather than an accident, so a sweep was run against the whole repository for that class. **8 findings raised, 7 confirmed by adversarial verification that reproduced each by execution, 1 refuted.** The refutation matters: it shows the verifiers were testing rather than agreeing.

### The severe one: a safety gate that could not see the repository

`bench/vault_keys.sh` scanned for stray plaintext keys with `find "$HOME" -maxdepth 5`. The repository sits 2 levels below `$HOME`, so a file inside `bench/cdsfl_registry/targets/` is at depth 6 — exactly where the Experiment 48 leak came from, and where the answer keys for experiments 48 to 52 were tracked.

Measured on the live machine: that predicate returns **0** matches; an unbounded pruned walk returns **6**. `bench/arc_sequencer.sh:50` gates an entire experiment arc on that verdict. Removing the ceiling exposed 2 further defects it had been masking: `*canary*.json` matched 6 run-output files with **0** answer-bearing content, which would have blocked every arc, now narrowed to `canary_catalogue_*.json`; and, found only by writing a fixture with an **empty** `CDSFL_LEGACY_STORES`, a trailing pipe character in the exclusion alternation that matches the empty string and suppresses every stray file. One empty configuration value produced a total false all-clear. **Write fixtures with empty values; the live configuration hides these.**

### Three more instances closed in the night's second half

`bench/arc_sequencer.sh` carries 2 containment gates that decide whether an experiment leg may launch, and both had the same shape. Line 74 counted the panel working directory with `find -maxdepth 1 -type f` and then required exactly 1 file, so a second exam document one directory down was not counted and the gate passed while a panel could reach a sibling paper. Line 173 counted the staging directory with `-type d`, so a sibling document staged as a **file** was not counted at all. These gate the withheld-exam arc, experiments 48 to 53, where a leg reading another paper destroys the blindness the whole arc depends on. Both were widened to complete traversals. The staged layout is flat — one directory named `current` holding one Markdown file — so counting the whole subtree cannot change a legitimate case and only closes an evasion; verified by running both traversals against the live staged tree, which still counts 1.

`bench/tests/test_arc_containment_gates_2026-09-08.py` is new, and it **extracts each `find` invocation from the live script and executes it** against fixtures built to defeat the bounded form, rather than asserting on the script's source text. Reverting either gate turns all 4 tests red; that was verified by actually restoring the old file and running them, then restoring the fix and confirming green. This matters because 3 guards written the previous night passed their own suites while protecting nothing.

Two documentation checkers had the same defect at lower consequence. `scripts/cdsfl_qc.py` and `scripts/supersession_check.py` both walked their document roots with `glob("*.md")`, which sees only the top level. Measured: `docs/` holds 13 Markdown files at the top level and **152** in the whole tree, so 139 nested documents could not fail either checker. Both now use `rglob`. The supersession scan went from 382 files to **534** and still reports no stale holds.

## The same fix read as correct 3 times and was wrong 3 times

`_record_recovery_ran()` in `scripts/cdsfl_recover.py` writes the marker that lets the compaction alarm clear on the **restore event** instead of on a text pattern in a message. It failed 3 ways, and each failure concealed the next.

1. It was defined and never called. The patch that added the call targeted a `return 0` that `main()` does not contain, so it matched nothing. The fix read as done.
2. Once called, it raised `AttributeError: type object 'datetime.datetime' has no attribute 'datetime'`, because line 22 of that file is `from datetime import date, datetime` and binds the name `datetime` to the class rather than the module.
3. The repair for that used `timezone.utc` **without importing `timezone`**, because the conditional edit targeted the string `from datetime import datetime`, which does not occur in the file. A blanket `except Exception: pass` swallowed the resulting `NameError`, and the run reported success. The same edit also left behind a comment asserting an import that was not there.

The narrow `except OSError` now prints to standard error rather than swallowing, so an unwritable home directory is reported instead of looking like success. `bench/tests/test_recovery_marker_2026-09-08.py` executes the whole path end to end: a full restore writes the marker, a partial report does not, a write failure is reported, and the real hook is run over a synthetic transcript for 5 acknowledgement cases. It includes a **mutation test** that deletes the marker and requires the alarm to return, proving the marker is load-bearing rather than decorative. 9 tests, all passing.

## Two measurement errors caught in this session, both running in the reassuring direction

**Archive scans double-count, because one dispatch is stored under two names.** Seat records exist as both `r5_gemini_<timestamp>.json` and `round5_gemini_<timestamp>.json`, same timestamp, same dispatch: 2,969 of the first form repository-wide and 1,580 of the second. A scan that globs either shape counts every such run twice, and the faster runs dominate. The first duration scan did exactly that and produced a 99th percentile of 1,605 seconds and a 3.43 percent loss rate. The deduplicated figures are **2,068 seconds and 5.45 percent** — the error made the situation look better than it was, and the wrong numbers had already been written into a permanent source comment before it was caught. Deduplicate on the tuple of run, seat, round and duration; never on filename.

The same flawed scan also produced a claim that 14 of 55 multi-round runs had short-handed rounds. That was an artefact of a regular expression matching only one of the two naming conventions, and it is **not reported as a finding**. Checked afterwards: seat shortfall is **not** silent in the record. `round_NN.json` carries a `failures` field and `checkpoint.json` carries `active_models`, `failed` and `failure_reason`.

**The exit code of a pipeline is the exit code of its last command, and this cost a false all-clear twice more in one night.** A background suite run was scripted as pytest redirected to a file, then an echo, then a `tail`. The task's exit status is its last command, so the harness reported "exit code 0" while pytest had reported **1 failed**. This is the same defect as the missing `set -o pipefail` in `vault_keys.sh` repaired hours earlier, and the third instance in one night. Any script whose verdict matters must end with an explicit `exit $code`, and the tool's own summary line is what should be read, not the runner's status. The same run also used `-x`, which stopped it at 1,858 of roughly 5,400 tests, so "1,858 passed" was never the suite.

The failure itself was a drift guard doing its job: `experimental_notes/EXPERIMENT_RUN_LEDGER.md` cited `bench/reference_runner_v3.py:13622`, and a 15-line insertion had moved that line to 13637.

## The runner had never executed the feature it shipped

`bench/reference_runner_v3.py` was missing a pre-loop initialisation for `rk_proof_requests_for_next_round`. That variable is read at the top of every round when the context prefix is built, at 2 sites, and assigned only near the end of a round. On round 0 nothing has assigned it, so `run_experiment` died with an `UnboundLocalError` at the **first round of every run**.

The severity-proof round trip shipped on 2026-09-07 and had therefore never executed end to end: the last archived run predates it, and its unit tests exercise the builder and the stamp in isolation rather than through `run_experiment`. A feature whose tests pass and whose only real caller cannot reach round 0 is this project's most repeated shape. Both runs tonight reached round 0 and dispatched, which is the first end-to-end execution of that path.

## Corrections to the record

**Experiment 55 ran; it did not fail to start.** Both archived runs, `exp55_v3_control_20260823T144624Z` and `...T153955Z`, completed 1 round of 6 and stopped on the terminal verdict `HALTED_IRREDUCIBLE_QUEUE_ALARM`. Each produced 10 findings and sealed an 8-record verification chain, with Merkle roots `sha256:0ef98ba7...` and `sha256:5138d4c1...`. The halt is the irreducible-queue alarm firing at round 0, with 6 criticals locked as irreducible in the first run and 7 in the second. `docs/REPRODUCING.md` listed Experiment 55 as reproducible and said **nothing** about that halt, in a document whose purpose is telling a newcomer where to start; the verdict is named in 8 other files but was absent from the one a reader would consult. A disclosure has been added there. A related recording defect is worth knowing: `checkpoint.json` shows no reason for either run, because the runner copies its stop cause into `convergence_reason` only inside the branch taken when a run converges. The cause is in the run report, not the checkpoint. See `bench/insect_brain.py:132`.

**The branch `exp39-experimental` still exists locally.** It was stated to be fully retired, on the repository, locally and remotely. That is **correct about the remote and not about local**. `git ls-remote --heads origin` returns only `main`, and no remote carries the branch. Locally, `refs/heads/exp39-experimental` exists at `e49a021` with **107** commits not on `origin/main`, and it is not an ancestor of `origin/main`. Also still present: `refs/heads/backup-pre-rewrite-2026-08-27`, `refs/tags/pre-rewrite-2026-08-27` and `refs/original/refs/heads/build-experiment-2026-08-22`.

Retrievable from that branch: **5** answer keys, not the 7 previously recorded. Experiment 48 chemistry at 42,457 bytes, 49 engineering at 43,645, 50 physics at 82,863, 51 biology at 57,620 and 52 factorial at 46,101 — **272,686 bytes in total**. They were deleted on that branch on 2026-07-29 and remain in its objects. Publicly, all 5 reach `origin/main` in **0** commits. The file `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` is in the current public tree, published deliberately, and is not an exposure. The one genuine public residual is unchanged: `control_two_distinct_defects_GROUND_TRUTH.json`, 635 bytes, reachable from public history only, documented on 2026-08-26 and still awaiting a ruling.

**Nothing has been deleted.** A standing instruction from 2026-08-23 says to keep `exp39-experimental`, which conflicts with the retirement statement. That conflict is the founder's to resolve, and branch deletion is irreversible.

## What needs a decision

1. **The branch conflict above.** Keep `exp39-experimental` as the 2026-08-23 instruction says, or delete it and its 2 sibling refs. It carries 5 answer keys totalling 272,686 bytes and 107 commits absent from the remote. Nothing public depends on the answer.
2. **The 635-byte public residual**, unchanged from the earlier note. Experiment 55's target is spent either way, because both its runs began 3 days after the ground-truth file was published. A history rewrite would re-hash **353** of the 955 commits on `origin/main` and break **174** hash citations across 57 files. Disclosure as a stated limitation remains the cheaper option and is what this project's own methodology advocates.
3. **Whether to add retry-on-timeout** to seat dispatch, wiring the `max_retries` field that already exists and is read by nothing. At the new cap the expected loss is 0.30 seats per run; a single retry would take that to roughly 1 in 10,000, at the cost of one extra dispatch when a timeout actually occurs.

## Measured state

Suite under `--netguard-strict`, exit code captured directly rather than through a pipe. The Experiment 45 clean run started 02:42 BST against blob `539f6a4`, 6 seats, maximum 16 rounds, 3600-second cap, writing to `bench/logs/sim45_memory_20260908T014200Z`. Its full output can be followed with `tail -f` on the task output file named in the session record. Round 0 closed at 03:13 with all 6 seats, 27 findings, a registry of 27 canonical entries at rho 1.000, and 20 corrected copies derived from 22 findings carrying a fix. One fix-efficacy result is already recorded: `C0016 FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER`. The run continues under the standing rule; its verdict is reported separately.
