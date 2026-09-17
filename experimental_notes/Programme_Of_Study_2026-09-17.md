# The programme of study for the next simulated run

2026-09-17, 00:26 BST, Europe/London.

## Why This Run Is Being Made

The founder's instruction of 2026-09-16, verbatim: "The purpose of the next simulated run is to enact a study of all recent fixes gathered over the last 10-12 days and to see exactly how well, or otherwise they perform." The run is not a fresh experiment. It is a test of the repairs, to see how they behave together rather than one at a time.

## What Was Repaired, And How Much Of It There Is

Between 2026-09-03 and 2026-09-17 the repository took 323 commits. 84 entries on the master task list are marked DONE, and 151 new test files were added, 1 or more per repair. Grouped by the part of the harness they guard: 27 cover the falsifier and admissibility gates, 17 the panel and its brief, 15 the records and the note linter, 11 the harness guards, 6 the runner and its convergence machinery, and 75 sit outside those groups.

Those 151 tests already prove each repair in isolation. What no test can show is whether the repairs interfere with one another in a live run, which is what this study is for.

## What The Run Must Measure

1. Falsifier supply. The 2026-09-08 run halted because 5 of 14 critical findings arrived with no runnable falsifier. The intake parser was widened afterwards. MEASURE: the share of critical findings arriving with a falsifier the runner can execute, against the 9 of 14 that did last time.

2. The exhausted-round valve. It could never open, because its threshold of 8 equalled the round limit of 8. Set to 6 on the founder's ruling of 2026-09-16. MEASURE: how many findings reach the valve, in which round, and whether any arm still ends in budget exhaustion rather than one of its 2 pre-registered outcomes.

3. The drift detector. Wired on 2026-09-16 after having 0 production callers. For each flaw class it compares the share of findings this run confirmed against the share memory predicted, and accumulates the gap. MEASURE: the largest excursion per flaw class against the threshold of 2.0. Replay of 3 archived runs gave 0.5595, so a live figure near or above 2.0 would mean the threshold is wrong, and a figure far below means it is inert.

4. Seat independence. Every panel seat used to share 1 writable sandbox. Each now gets its own. MEASURE: whether any seat's working files are touched by another, and whether the containment alarm fires with an attributable cause.

5. The admissibility gate on prose. A gap remains: the gate classifies a whole target file rather than each finding inside it. NOTE AND CAUTION: all 3 arms target a Python module, so this gap cannot be exercised by this run. It is listed so that a reader does not mistake silence for a passing result.

6. The panel brief format. Every brief must now require the seat to run the harness, name a mathematical instrument, produce a tested fix rather than a finding, and state what would refute it. MEASURE: whether seats comply, and whether their fixes survive their own falsifiers.

7. Record integrity. The note linter, the DONE-evidence guard and the citation repairs all changed. MEASURE: whether any record written during the run fails its own guard.

## The Three Arms

All 3 target the same file, the registry engine, for 8 rounds, with routing, the falsifier gate and the admissibility gate on, and the hardened gate, merge arbitration and immune memory off.

1. Multi-model panel: 5 seats, CC2, Codex, Gemini, DeepSeek and ChatGPT.
2. Single model with agents: 1 seat, CC2.
3. Seat contrast diversity: 2 seats, Codex and ChatGPT.

The contrast between the first 2 is the question the founder has asked repeatedly: whether several distinct architectures beat 1 architecture wearing several labels.

## What Would Falsify The Claim That The Repairs Work

The claim is that the repairs improve the run rather than merely passing their own tests. It is falsified if any of these occurs. Falsifier supply is no better than the 2026-09-08 run. The valve still never opens, or opens so often that findings bypass review. The drift detector fires on every flaw class, which would mean its threshold is miscalibrated rather than informative. A seat's files are touched by another seat. Any arm ends outside its pre-registered outcomes.

## When To Stop

The run stops on its own terms: convergence, the irreducible-queue alarm, or the round limit. The study stops when every measurement above has a value, or a named reason why it could not be taken. A measurement that could not be taken is reported as such and never as a pass.

## What Is Deliberately Not In This Run

The 4 parked defects in how the CDSFL system prompt is assembled, including the one where the full directive of 27,803 characters is always replaced by a rendering of roughly 2,500. The founder ruled on 2026-09-16 that these fold into the refactor for the revised mathematical model, because both change the text sent to models and doing it twice would pay the replay cost twice. They are listed in the programme so the refactor inherits them.

Experiment 53, the zero-plant control, is deferred until after this run by the founder's ruling. The discrimination control block is to be armed and tested in this run.

## Addendum, 2026-09-17 17:30 BST: The Programme Checked Against The Rulings It Answers

Status of this addendum: PROPOSED, except where a section names a commit. Drafted at 16:09 BST from a read-only audit; sections 4, 10 and 11 were brought up to date before it was added, after commits `cd3cd83`, `e7b4507` and `34c446c`. Nothing else below is built. Each change named here reaches the task list only through a Section P panel review. The sections above are left as written; where this addendum contradicts them, this addendum governs.

### What Was Checked

The programme was checked against 7 founder instructions in `~/Developer_Projects/Responses/Outstanding_Rulings_2026-09-15.rtf` (I23, I31, Q6, A7, R3, A19 and Q11), against the simulated harness that would run it, and against the 3 arm configurations it names. Every check below was executed at HEAD `989f32f` unless another commit is named.

### 1. The Simulated Harness Cannot Run The 3 Arms As Written

OBSERVED. `bench/tools/run_simulated_experiment.py`, last changed at `f011c1a`, accepts no configuration file. Its `--help` lists `--target`, `--rounds`, `--models`, `--timeout`, `--test-cmd`, `--name`, `--model` and `--no-severity-calibration`. It builds its own run: target `bench/dm/_memory.py`, domain statistics, up to 16 rounds, 6 seats, merge arbitration on. It never sets `exhausted_round_threshold`, `immune_memory_enabled` or `discrimination_control_blocks`, so each takes the runner default of 8, False and False. The run this programme describes, 3 arms on `bench/cdsfl_registry/engine.py` for 8 rounds, has no launcher.

PROPOSED: a simulated entry point that loads each `bench/exp56_configs/*.json` through `RunnerConfig.from_dict`, renames every seat with the `-SIM` suffix, carries the valve setting of section 3, applies the settings of sections 4 and 6 to every arm identically and those of section 7 to the 4th arm only, records each applied setting in the run report, and launches through `bench/tools/run_simulated_experiment_sandboxed.sh`, under the founder's ruling of 2026-09-01 that a simulation runs on a copy and never on the live repository. It needs a caller and a test that loads the 3 configs and asserts the settings the runner actually received.

### 2. Seat Labels: The Arm List Describes The Paid Panel, Not A Simulated One

OBSERVED. The 3 configs carry bare vendor names: `["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]`, `["CC2"]` and `["Codex", "ChatGPT"]`. Loaded through `RunnerConfig.from_dict`, `run_is_simulated(cfg)` returns False for all 3, because it keys on the `-SIM` suffix. The simulated harness names seats `CC2-SIM`, `DeepSeek-SIM` and so on at source, under the founder's ruling of 2026-08-08 that replaced `SIM-A` to `SIM-E`, and every seat is the same stand-in: `claude -p --model opus` with Bash, Read, Grep and Glob, in `bench/tools/sim_dispatch_shim.py`.

For this run the arm list reads:

1. Multi-model panel arm, simulated: 5 seats labelled CC2-SIM, Codex-SIM, Gemini-SIM, DeepSeek-SIM and ChatGPT-SIM, all served by 1 stand-in model.
2. Single model with agents arm, simulated: 1 seat, CC2-SIM.
3. Seat contrast arm, simulated: 2 seats, Codex-SIM and ChatGPT-SIM.

The sentence under The Three Arms, that the first 2 arms test whether several distinct architectures beat 1 architecture wearing several labels, does not hold for this run. In a simulated run every arm is 1 architecture. This run tests whether the repairs work in each arm's shape; the architecture question needs the paid run.

OBSERVED, and it bears on the report this run will write. `study_programme_report` in `bench/reference_runner_v3.py` counts distinct seat labels and never reads `cfg`. Called with 5 `-SIM` labels, it returned `answerable: True` and `why_not: None` for the cross-architecture item while `run_is_simulated` returned True. That is the defect recorded against task 9.4, still present at `989f32f`. Until it is repaired, that field in this run's report is read as unanswerable whatever it says.

NEEDS THE FOUNDER'S RULING. `bench/exp56_configs/d11_seat_contrast_diversity_arm.json` carries `_arm.launch_blocked: true`, and its note permits the weak form only on an explicit ruling. The stated reason is the Codex seat's paid route. In a simulated run both seats are the same stand-in, so the run is the weak form by construction. Recommendation: rule that the simulated run includes this arm, and record the ruling in the config's note. This is item 12(c) of `experimental_notes/Action_List_2026-09-17.md`.

### 3. I23, The Exhausted-Round Valve

OBSERVED. The 3 configs carry `exhausted_round_threshold: 6` from commit `45369e5`, and `bench/tests/test_exhausted_valve_can_fire_2026-09-17.py` passes. The simulated harness does not pass the setting, so a run launched through it today would use 8. Added to item 2 above: the threshold the runner actually used, read from the run's own record, so a default of 8 cannot pass as 6.

### 4. I31, The Drift Detector: As Wired, Item 3 Cannot Be Measured

OBSERVED in 4 ways. The figures in this section are produced by `scripts/i31_drift_detector_premise_2026-09-17.py`, committed at `34c446c` and held by `bench/tests/test_i31_drift_premise_2026-09-17.py`; it works on a copy of the memory file and writes nothing to the repository.

1. Unreached in all 3 arms. The call sits inside `if getattr(cfg, "immune_memory_enabled", False)` in `run_experiment`, and all 3 configs load with `immune_memory_enabled=False`. The simulated harness does not set it either.
2. Unable to fire when reached. The runner calls `update_drift` 1 time per flaw class per run, on a freshly loaded memory. `ImmuneMemory.save` writes `drift_threshold` and no CUSUM state, and `load` restores none, so every run starts from 0. `pi_mem` lies strictly between 0 and 1, so a single residual is smaller than 1 in magnitude. z3 returns unsat for crossing 2.0 within 1 or 2 updates and sat for 3, and `Reduce` on the local Wolfram Engine agrees as a secondary check (`False` for 2, `True` for 3, computed with Wolfram Language). Reproducing the production sequence over 48 extreme cases gave 0 fired and a largest excursion of 0.950032.
3. Absent from the output. The report carries 1 boolean per flaw class and not the excursion, so the largest excursion per flaw class cannot be read from it.
4. The 0.5595 has no producer. It appears only in the docstring of `bench/tests/test_drift_seat_guard_assessment_2026-09-10.py`, and it describes state carried across 3 runs inside 1 object, which production cannot do. The positive control in `bench/tests/test_drift_detector_is_wired_2026-09-17.py` calls `update_drift` 12 times on 1 object, a sequence production never makes, so those tests pass while the production call site cannot fire.

PROPOSED, before the run: save and restore the CUSUM state in `ImmuneMemory`, with a round-trip test; report `cusum_pos` and `cusum_neg` per flaw class; turn recording on in all 3 simulated arms, with `immune_memory_path` pointing at 1 copy inside the run's own directory and never at `bench/state/immune_memory.json`, and with `immune_memory_consume_rk0` left off so no verdict changes; run the 3 arms in sequence on that copy, so each flaw class gets 3 updates, the fewest that can cross 2.0. The measurement becomes the CUSUM per flaw class after each arm. The drift falsifier under What Would Falsify changes from firing on every flaw class to: the CUSUM stays at 0, or does not carry from 1 arm to the next.

OBSERVED, and it takes priority over everything above in this section. The founder's I31 ruling was conditional: "if it depends on some element of how our current mathematical model functions, defer it until we have had an opportunity to fully consider those revisions". Commit `90873cb` wired the detector on the ground that `pi_mem` "appears nowhere in docs/MATHEMATICAL_APPENDIX.md". It does appear. `docs/MATHEMATICAL_APPENDIX.md` section 1.5 defines π_mem(k) at line 1506, and its Drift Detection subsection at lines 1520 to 1527 defines this detector itself: S_pos and S_neg over observed_rate minus π_mem, flagged above a threshold of 2.0. A search for the ASCII spelling `pi_mem` finds nothing because the appendix writes π_mem. So the detector is an element of the current mathematical model, and under the ruling as worded it is deferred to the model review.

NEEDS THE FOUNDER'S RULING, on 1 point only. Recommendation: fold I31 into the review of the revised mathematical model, as the ruling's condition requires; hold every PROPOSED change in this section until that review settles whether section 1.5's drift design stands; and leave the report-only call from `90873cb` in place meanwhile, since it decides nothing and, as shown above, cannot fire. The alternative is to revert that call until the review. Either way, the commit's stated premise is recorded as false: on task A11 and as a dated correction at the call site in `bench/reference_runner_v3.py`, both at `34c446c`. The choice is item 12(b) of the action list.

### 5. Q6, The 4 Parked Composer Defects: Moved Into The Run

The founder's verdict on question 6: "Fold them into the refactor and ensure the fix is effective and add it to the program of study for the next simulated experimental run." What Is Deliberately Not In This Run contradicts the last clause, and this section supersedes its first paragraph. The run is already held until the revised mathematical model is reviewed (ruling 8), and the refactor serves that model, so the order is refactor first, run second.

MEASURE. First, the 4 falsifiers that today assert each defect is present, `bench/tests/test_falsifier_C0040_universal_directive_2026-09-10.py`, `bench/tests/test_falsifier_C0037_containment_dedup_2026-09-10.py`, `bench/tests/test_falsifier_C0036_C0054_conflict_topics_2026-09-10.py` and `bench/tests/test_falsifier_C0001_prune_inversion_2026-09-10.py`, are inverted by the refactor: each fails against the source before it and passes after it. Second, live: the composed system prompt each seat receives in round 0, its length and how many of the universal directive's 16 section headings it carries. OBSERVED: `bench/logs/sim45_memory_20260908T033008Z` holds only its report and `immune_pipeline.log`, with no prompt record, so the live half needs a record the runner does not yet write. If the refactor has not landed when the run starts, this item is reported as not taken, with that reason.

### 6. R3, The Discrimination Control Block: Armed, With Its Own Measurement

The founder ruled on 2026-09-15 that it is "to be armed and tested live in the next experimental run". Loaded through the real loader, all 3 configs have `discrimination_control_blocks=False` and `discrimination_control_ask=False`. Without the ask the control is never given a corrected copy, so arming the block alone would test nothing.

PROPOSED: set both to true in the simulated arms, with a `_note` recording the ruling, because `bench/tests/test_discrimination_control_cannot_arm_silently_2026-09-10.py` refuses an armed config without one, and update its `test_no_config_arms_it_today` in the same change. Panel round 16 recorded that no config has ever carried the key, so this also runs that guard's refusing branch for the first time.

MEASURE: how often the control fires; how many verdicts it reverses; and for each reversal, the finding's status before it and whether the corrected copy silenced the falsifier. Every reversal is listed by finding, never only counted. Arming it can move the primary metric, falsifier-confirmed defects, so that metric is reported both with and without the reversals.

### 7. A19, Per-Fragment Classification: A 4th Simulated Arm

The founder ruled that A19 is tested live in the next run. Item 5 above is right that the 3 arms cannot exercise it: all 3 target a Python module, and `_gateable_source` returns a Python source unchanged. Question 9 holds A19's panel review until the revised mathematical model has been reviewed, and ruling 8 holds the run on the same condition, so the 2 do not conflict.

PROPOSED: a 4th simulated arm, outside Experiment 56's pre-registration, identical to the others except for `target_kind: prose`, `sk_score_prose_listings: true` and a markdown target carrying fenced Python listings. `bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md`, 3,498 bytes with 2 fenced Python listings, is a candidate. UNVERIFIED: that a full run completes on a markdown target. A dry launch settles it.

MEASURE: fixes scored against fixes returning NO_SCORE; ADMISSIBLE, REJECTED and ESCALATE counts on fixes to listings; and any REJECTED on a fix touching only prose, which would be a defect. Declared in advance: the A19 entry records that the archived shell-injection fixture scores 1.0000 ADMISSIBLE with the flag on, so an exploit passing this arm is a known limit and not a new finding.

### 8. A7, Falsifier Supply: The Comparison Is Weaker Than Stated

Item 1 stands. Its comparator, 9 of 14, comes from the 2026-09-08 simulated run on `bench/dm/_memory.py` with 6 seats, a different target and seat count from every arm, so the comparison is indicative only. `git grep` over tracked Python found no committed producer for 5 of 14. The measurement is what `falsifier_intake_telemetry` records during this run, labels seen against blocks recovered per reply, over raw labels and over fenced labels. Panel round 16 recorded that task 9.3's archived intake figures do not add up, 411 minus 271 being 140 and not 138, so they are not used as the baseline.

### 9. Items 4, 6 And 7 Measure Machinery This Run Does Not Use

OBSERVED. The separate sandbox per seat and the brief-format validator both live in `bench/confer_maths_panel_2026-09-05.py`, the panel review dispatcher. `bench/reference_runner_v3.py` never calls `panel_brief_validate`, and `bench/tools/sim_dispatch_shim.py` starts every seat with `cwd=str(REPO)`, so simulated seats share 1 working tree by construction. The note linter and the DONE-evidence guard run at commit time, not inside a run.

The 3 items stay, each at a named juncture. Item 4: inside the run, target rewrites with the seats recorded in flight (task 6.6); seat sandboxes, in the panel review of the run's results. Item 6: in that panel review. Item 7: at the commit of the run's notes, through `hooks/pre-commit`.

### 10. Q11, Wolfram In This Run

UPDATED at commits `cd3cd83` and `e7b4507`. The Wolfram standard is now code, `bench/wolfram_standard.py`, and automated runs are denied the kernel. Every `claude -p` seat launcher, the simulated-run shim included, carries `--disallowedTools "Bash(wolframscript *)" "Bash(WolframKernel *)" --strict-mcp-config`, and every seat launcher puts a refusing `wolframscript` first on the seat's PATH. `scripts/wolfram_seat_deny_probe_2026-09-17.py --live` started 2 seats with a fake `wolframscript` on PATH: without the layer the seat ran it, with it the CLI denied the command, and neither session listed a Wolfram tool or MCP server. The falsifier sandbox and the runner's 2 fix gates refuse the kernel or run behind the same gate.

What remains true for this run: the shim collects each seat's final text and not its tool calls, so an attempted call is not visible in the run's output, only its refusal in the seat's reply if the seat reports it. A seat that types the real binary's absolute path is not stopped by the CLI rule or the PATH gate; the module says so.

No ruling is needed for simulated seats: the licence constraint already bars automated use and is now enforced. Whether panel reviews may use Wolfram through a single-kernel queue is item 12(d) of the action list; denial is the default in force.

### 11. Every Fix In The Window, Derived Rather Than Typed

OBSERVED. The figures under What Was Repaired have no committed producer. The group counts 27, 17, 15, 11, 6 and 75 exist only in an uncommitted scratch file with no code beside it, and reproduce from nothing. The other 3 do not reproduce together at any 1 commit: `git rev-list --count --since=2026-09-03` gives 323 at `90873cb`, 2 commits before this programme, and 325 at `6c3bedc`, the programme's own commit; `bench/tests/test_*.py` files added in the window number 150 at `90873cb` and 151 at `6c3bedc`; DONE entries number 84 at both. `scripts/fix_study_programme_2026-09-10.py`, task 9.2's inventory, derives DONE entries and evidence files only, and the programme does not cite it.

"Those 151 tests already prove each repair in isolation" does not hold as written. `scripts/done_audit_overclaim_rate_2026-09-17.py` reports 31 of 84 DONE entries claiming more than their evidence shows, 36.9048%, Wilson [27.3701%, 47.5848%]. R3, 9.1, 9.2, 9.3 and 9.4 are among the 31, and this run leans on each.

COMMITTED with this addendum: `scripts/programme_of_study_inventory_2026-09-17.py`, deriving commits, DONE entries with their evidence, and added test files at a named commit, grouped by section prefix rather than by an unrecorded classifier. With `--at 90873cb` it prints 323 commits, 84 DONE entries of 95 and 150 added test files; with `--at 6c3bedc`, 325, 84 and 151. PROPOSED: the programme quotes its output together with the commit, and a test requires every DONE identifier to appear in a table stating where this run observes it or why it cannot, so a fix added later cannot drop out unnoticed.

### 12. The Study Items This Programme Left Out

Task 9 of the master task list and the operational tracker scheduled 6 study items for this run: the critical-severity ceiling (item 14), why the sweep cannot clear a critical (item 28), falsifier ERROR causes (item 29), the cross-architecture rho of 0.564 (item 46), the corrected S* values, and reach in both homes. The founder asked 3 times for that full programme to be run. `study_programme_report` already emits all 6, so including them costs nothing. 2 caveats travel with them. Item 46 is unanswerable in a simulated run, as section 2 records. For item 28 the report's answer is a fixed string: `_post_convergence_sweep`'s terminal set is `{MERGED, CLOSED, REFUTED, DUPLICATE}`, while the report hard-codes a set that adds CONFIRMED and states that the sweep can never clear one. Panel round 16 recorded an executed falsifier showing the sweep clearing a CONFIRMED critical; it was not re-run for this addendum, so the field is reported as disputed and not as a result.

Written under CDSFL note standard v1.7 (26 August 2026).
