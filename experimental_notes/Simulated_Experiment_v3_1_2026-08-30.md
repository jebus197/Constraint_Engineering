# THE SIMULATED RUN CONVERGED AT ROUND 3, AND IT HAD TO BE RUN TWICE

2026-08-30, 17:57 BST (UTC+1)

The simulated experiment converged at round 3 on target bench/dm/_memory.py, which is the same round, the same gate and the same reason as the real experiment 45 on the same target. It was run twice. The first attempt was discarded because the project's own naming guard caught it writing 123 bare vendor names into the record, which is a provenance failure and not a cosmetic one.


## What Was Run

The full run_experiment function, all 2,363 lines of it, on runner v3.1. Real rounds, real routing, real immune pipeline, real fix scoring, all 4 convergence gates. The single substitution is at _dispatch_single_model, where 6 agents stand in for the 6 paid models. Their raw text is parsed by the runner's own parse_findings, so the parse path is the real one.

Target: bench/dm/_memory.py, 20,563 characters, 18 location keys extracted. It is the smallest target in the Exp 40 to Exp 54 series, and its real run, experiment 45, is the shortest on record at 4 rounds.


## THE FIRST ATTEMPT PUT 123 BARE VENDOR NAMES INTO THE RECORD

bench/tools/sim_dispatch_shim.py computed the simulated label for each agent, printed it to the console, and then passed mc.label, the vendor name, to parse_findings. That call is the one place where model_id and finding_id are stamped into every persisted finding. So the simulated label was correct in the terminal and absent from the artefact. The record held findings attributed to ChatGPT, Gemini, CC2, Codex and DeepSeek, none of which ran, and no paid dispatch occurred at all.

This is the exact failure of 2026-08-04 that feedback_no_fake_model_labels exists to prevent, reproduced by the harness written to avoid it. It was caught by bench/tests/test_sim_naming_and_integrity_directive.py, not by inspection.

The fix is at source rather than in a mapping. VENDORS in the run script is now defined as CC2-SIM, DeepSeek-SIM, ChatGPT-SIM, Gemini-SIM, Codex-SIM, Fable-SIM, so the ModelConfig labels, cfg.models, parse_findings, every finding ID, the log directory name and the report all carry the suffix by construction. A relabelling map has somewhere to be dropped. A correct name at source does not.

The offending artefacts are quarantined at bench/logs_quarantine/ with a README recording why, rather than deleted.


## The Naming Rule And The Runner Were In Direct Conflict

Honouring the -SIM suffix would have silently switched machinery off. Two sites in reference_runner_v2.py compared mc.label to the exact string CC2:

Line 7563, in the verification stage: if no config is labelled exactly CC2, it returns skipped with the reason "CC2 config not found". Not an error, not a warning. A capability lost in silence. That is the config-drop class, and this is its 8th occurrence in the project.

Line 6669: the dispatch wall-clock multiplier drops from 5x to 3x.

So obeying the naming ruling would have broken the runner, and obeying the runner would have broken the naming ruling. base_model_label resolves CC2-SIM back to CC2 for vendor-keyed logic while the label stays correct everywhere else. describe_model now reports a simulated panellist as "SIMULATED stand-in for Claude Opus 4.7 (Anthropic), no paid dispatch occurred", so the report says so in the roster line rather than in a footnote.

The first version of that helper was refuted during its own P-pass: it crashed on a missing label. 8 tests now hold both halves, including that the fix does not make every label look like CC2.

Out of scope and stated rather than hidden: 14 other files carry the same exact-match comparison, including reference_runner.py, which is the frozen v1 baseline, and the per-experiment scripts for experiments 11, 17, and 29 through 37. The simulated run drives reference_runner_v2 only.


## The Second Failure Was The Guard, Not The Run

test_corrected_copy_wiring reported 14 archived findings carrying a corrected copy, which would mean the wiring had reached backwards into the historical record. It had not. The guard identified pre-v3 runs by directory name, matching exp followed by a number and excluding 55 and above. A directory not named exp anything falls into the guarded set by default, so a v3.1 run in sim45_memory_20260830T161215Z was filed as old archive and its 14 legitimate corrected copies read as contamination.

The guard now classifies by the run's own recorded runner_version and falls back to the directory-number rule only for runs predating the version stamp. That required stamping runner_version into runner_state.json as well as the report, because the state file is what the archive guards walk.


THE RESULT

runner_version v3.1. 4 rounds. converged_at 3. Reason: CRITICAL_QUIESCENCE_CONVERGED, gamma_critical = 1.000, with 3 consecutive zero-new-critical rounds. 29 findings raised, 19 canonical registry entries, gamma final 0.842. Elapsed 2,219 seconds, 37.0 minutes. Verification chain sealed at 9 records.

Discovery decayed 15, 8, 3, 3 across rounds 0 to 3. All 6 panellists dispatched in every round.

Real experiment 45 converged at round 3, on the same gate, for the same reason, in 4 rounds. Its gamma_critical was 0.621 against 1.000 here, and it produced 39 findings against 19. A weaker panel producing fewer findings is the expected direction. None of this is an experiment and none of it belongs in the paper.


## THE 35% TIMEOUT LOSS HAS A CONFIRMED CAUSE

The earlier attempt lost 7 of 20 dispatches to timeout at the 300-second limit, 35%. The diagnosis was that 300 seconds is simply too short for a 20 KB target, and that is now confirmed rather than assumed.

Across the 24 dispatches of this run at a 900-second limit: 0 timeouts. 7 of those 24, 29.2%, exceeded 300 seconds and would have been killed under the old limit. Wilson 95% confidence interval [0.149, 0.492], which contains the 35% first observed. Fisher exact against the earlier run gives p = 0.002023. The slowest dispatch took 523 seconds, leaving 377 seconds of headroom.

Four of the 6 round-0 dispatches ran between 327 and 352 seconds. Every one of them died in the earlier attempt for no reason other than the ceiling.


## The Version Question, Answered From The Existing Ruling

The instruction was to call the new runner v3. The ruling of 2026-08-23 already settled the form: v3 is a derivation of v2, not a rebuild, and the file keeps its name because renaming it changes the blast radius from 10 patches to every import in the project for no gain.

So there is no new file. What there is now is an accurate version number that reaches the artefacts. v3.0 was v2 plus 10 patches, 1 commit, 880 lines added. 17 further commits and 493 lines followed carrying no version at all, which is about 4% of the current runner postdating the version it claimed. The only prior v3 run has no version field anywhere, so its results cannot be attributed to the code that produced them without reading git history. This one can, from both the report and the state file.


## What The Earlier Staged Run Found

Folded in before this run: 3 finding states were invisible to the panel entirely; rejection reasons rendered only for findings in one section, so a confirmed finding with a failed fix received no feedback at all; _absolute_target crashed on a path object, which is the first thing every run does and had never been exercised since it was added on 2026-08-23; and the panel list used for every count and denominator defaulted to the old 5-model roster while 6 were dispatched, so the earlier attempt logged 5 and ran 6. This run logged 6 and ran 6.


## State Of The Suite

4,436 passed, 0 failed, 34 skipped, in 264 seconds. The netguard recorded 41 outbound attempts across 15 tests, all denied.


## Still Open, And Needing A Ruling

The push is still not made. The remote is 160 commits behind. The pre-push scan found 21 occurrences of personal information in files staged for the public repository, most of them a line written into review briefs by this session, and all have been removed. That scan is worth running before every push rather than once.

31 key files remain in plaintext and encrypting them needs a passphrase.

The discrimination-control misattribution remains latent. Bench Run 2 is its first exposure.


Written under CDSFL note standard v1.7 (26 August 2026).