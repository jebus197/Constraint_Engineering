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

**So something else wrote to a tracked source file during a run.** The panel seats are launched with `working directory: (inherited — repo)` — they execute inside the repository. This project has already measured panel agents editing the repository mid-run, twice, on 2026-09-01. A seat applying a fix it had just proposed is the explanation most consistent with the diff, which reads exactly like a proposed repair: a `MAX_DECAY_RATE` constant and a bound check raising `MemoryIntegrityError`. **That is the leading explanation, not an established one** — the write was not observed directly, and no record attributes it.

**The current run is clean, and was watched for this.** `git status` reports no tracked file differing from HEAD, and the target is byte-identical to blob `539f6a4`. Three tracked files unrelated to the experiment — `scripts/replay_accounting.py` and 2 panel-record notes — had their modification times touched at 03:09:22 and 03:14:21 during the adjudication phase, with **content identical to HEAD** in all 3 cases. Touched, not changed.

Whatever wrote it, the consequence is the same: the restart would have produced an "Experiment 45 comparison" against a target rewritten during a half-empty blind round, which is precisely the confound Experiment 45 was chosen to avoid.

It was caught 2 minutes in, by noticing that the run banner said 25,861 bytes where the previous banner had said 20,563. The check that catches this cheaply: **compare the byte count in the run banner against `git show HEAD:<target> | wc -c` before accepting any restart.** The target was restored to blob `539f6a4` from commit `ce08914`, verified by hash equality rather than by inspection, and the mutated file preserved as `_memory.py.MUTATED_BY_ABORTED_RUN` beside an `ABORTED.txt` in the dead run's directory. Both abandoned run directories carry that marker so no future archive scan reads them as evidence.

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
