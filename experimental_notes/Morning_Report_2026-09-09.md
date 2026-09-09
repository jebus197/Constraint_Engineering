# Morning report: 12 outstanding items verified against the repository, and the remote-access fault relocated

2026-09-09 08:15 BST (Europe/London)

## Summary

12 outstanding items were checked against the repository rather than recalled from session memory. 4 of the resulting findings contradict claims made in the preceding session and are corrected here. The most consequential is that the remote-access fault does not lie on the Mac: the host side recovered unaided after both forced restarts on record, in 40 seconds and 75 seconds. A second finding vindicates the founder's ruling of 2026-09-08 that the escalation doctrine must name misconfiguration as well as broken machinery, because the one capability difference between the version 3 runner and its predecessor turns out to be exactly that: routing and the sweep are switched off by configuration, not broken in code.

Nothing in this report has been implemented. It is a discussion document.

## Where the work stands

HEAD is `01906cc` on `main`, working tree clean, **11 commits ahead of `origin/main` at `071f1ed` and not pushed**. The push is refused at the assistant's end and remains the founder's to run. The full suite last ran green: 5454 passed, 4 skipped, 0 failed, pytest exit code 0 captured directly, in 682.03 seconds. No experiment is running and no monitor is left alive.

The Exp 45 simulated run of 2026-09-08 remains the last completed run: 4 rounds, 61 findings, 311.6 minutes, terminal verdict `HALTED_IRREDUCIBLE_QUEUE_ALARM`, did not converge.

## The remote-access fault is not on the Mac

**OBSERVED.** The desktop application restarts itself to apply a pending update, and it waits for the session to fall idle before doing so. The application's own log names the condition it waits for: 48 consecutive deferrals at 20-minute intervals, each reading `Deferring auto-restart ... Claude is working`, then `Auto-restarting app after update pending for 85 hours` at 16:52:11 on 2026-09-08. The restart landed 10 minutes after the last tool call and 78 minutes before the founder's next message. It has fired twice: 2026-09-04 at 23:10:45 after 76 hours, and 2026-09-08 at 16:52:11 after 85 hours.

**The correction.** The working assumption had been that the session only returns after physically returning to the machine. The log does not support this. On both occasions the persisted session `cse_018W1WGDnyD49P2dDARjTpVU` reconnected without intervention, reusing environment `env_01S81CKjRRA4gqpio7of4UNK`, and the device bridge re-authenticated seconds later. Recovery took 75 seconds on 2026-09-04 and 40 seconds on 2026-09-08. No failed reconnection appears anywhere in the log.

Self-recovery: 2 of 2, Wilson 95 percent [34.24%, 100.00%], Clopper-Pearson 95 percent [15.81%, 100.00%]. **The interval is wide because 2 is a small number.** This establishes what happened on both occasions on record; it does not establish that it always will.

Sensitivity to the window, which was a choice rather than a measurement: 1 of 2 recover within 60 seconds, and 2 of 2 within 120, 300, 600 and 1800 seconds.

**What this relocates.** If the host reconnects in under 80 seconds and the founder still cannot reach the session, the failure is on the client side or in the client's retry behaviour, not on the Mac. Driving home is very unlikely to be what restores it; waiting past the 80-second mark, or restarting the client, is the cheaper hypothesis and the one to test next. Script: `scripts/remote_bridge_recovery_2026-09-09.py`, tests `bench/tests/test_remote_bridge_recovery_2026-09-09.py`, status **TESTED**, 12 tests, both mutations caught.

**A caution on that instrument.** The first version of `remote_bridge_recovery_2026-09-09.py` could not have refuted its own hypothesis: it paired each restart with the first reconnection at any later time, so a reconnection 6.3 hours afterwards, which is precisely what a physical return would look like, would have scored as unaided recovery. It also credited any session's reconnection to this one, and divided by zero on a log containing no restart. All 3 are repaired and pinned by tests. The conclusion survived every repair, at every window from 120 seconds upward.

**Options, none taken.** First, apply a pending update deliberately before any long absence, since the restart cannot fire on an update already installed. Second, establish what the client does during the 80-second gap, which is the untested half. Third, keep the secure-shell route over the private network as the independent path in: it does not involve the desktop application, and was verified live at 18:35 on 2026-09-08 with the shell daemon answering, port 22 open on the tailnet address, and the command-line client version 2.1.220 on the login path. Fourth, consider enabling the private network's own shell service, which is currently off and would remove key handling.

## 4 corrections to claims made yesterday

**1. The version 3 capabilities are not broken. They are switched off.** The founder observed that fingerprinting, routing, the sweep and decomposed dispatch appear not to work as they did in version 2. All 4 are still reached by live callers in `bench/reference_runner_v3.py`; none is defined-but-never-called. What changed is configuration: routing and the sweep are disabled in all 3 current `bench/exp56_configs/*.json` files, `routing_enabled` false and `post_convergence_sweep_rounds` 0. Whether that is a deliberate experimental control or an omission is **OPEN** and needs a founder ruling, not a patch. This is the misconfiguration case the 2026-09-08 ruling anticipated, arriving within a day of the ruling.

**2. The two-directories account was wrong in its premise.** Only 1 of the 2 directories is created by the runner. The other is created by the simulated launcher at `bench/tools/run_simulated_experiment.py:157-159`, which then correctly tells the runner where to write by setting `ExperimentConfig.logs_dir`. The runner reads that field **0 times**, minting a second timestamp and path of its own at `bench/reference_runner_v3.py:11402-11403`. This is not a duplication bug; it is a field that is written and never read, which is the unwired-addition half of the additive standard. No compensating deduplication exists anywhere. **PROPOSED** fix: read the field the caller already sets.

**3. The falsifier-supply diagnosis was too shallow.** The halt was attributed to 5 of 14 critical findings arriving with no runnable falsifier, which is 35.71 percent, Wilson [16.34%, 61.24%]. That is true but downstream. The dominant loss is in the intake parser, which recovered only 26 of 69 `FALSIFIER:` blocks across the run, 37.68 percent, Wilson [27.18%, 49.48%], and **1 of 9 in the round that halted**, 11.11 percent, Wilson [1.99%, 43.50%]. The seats were supplying falsifiers; the parser was dropping them. **PROPOSED** fix, upstream and additive: widen `_FALSIFIER_BLOCK_RE` and its twin at `bench/runner_core.py:1165-1175` to tolerate text between the literal label and the opening fence, paired with the guard at `:1236`. Whether this would have prevented the halt is **OPEN**: recovering a block is necessary but not sufficient, since it must still bind to the right finding.

**4. Yesterday's sweep was itself a bounded traversal.** A checker was fixed for reading archived run output as production source, and the sweep accompanying that fix was bounded to "the 3 checkers that walk `bench/` for Python files". Sweeping the whole repository finds **6 further traversals** of the same shape, 1 of them wired to a red-or-green suite ratchet exactly as the fixed defect was. The class this project catalogues as "a bounded traversal standing in for a complete one" recurred inside the fix for an instance of itself. **PROPOSED**: one shared path-delimited predicate with a caller at each of the 6 sites.

## What has not been started

**The escalation doctrine still names only broken machinery.** The founder ruled on 2026-09-08 that it must read "broken machinery or misconfiguration or both" and should point at where the fault might lie. The rule appears in 5 live places and the string `misconfigur` appears in **0 of them**: `docs/GLOSSARY.md:168`, `bench/reference_runner_v3.py:6096-6098`, `scripts/hil_escalation_by_run.py:8`, `resources/RECOVERY.md:66` and `experimental_notes/CDSFL_Agent_Operational_Plan.md:132`. The ruling exists in exactly 1 place, `resources/ONBOARDING.md:18`, as an unactioned instruction. No test asserts on this wording, so amending it breaks nothing; a new test would have to call `build_irreducible_queue_alarm` and assert on the returned string rather than read the source.

**No mechanism ties a monitor's lifetime to its run.** Nothing in the repository terminates a monitor when its experiment ends: 0 launchers clean up monitors and 0 monitors read a process identifier file. The 1 such file that is written, at `bench/detached_launch.sh:11`, is consumed only by a read-only diagnostic printer. This is why 5 monitors survived their runs by up to 13 hours and appeared live. A complication: macOS `tail` rejects the `--pid` flag, so the tie must be a shell wrapper rather than a flag.

## What is partly done

**Stop reasons.** A fix of 2026-08-26 does set the stop reason outside the convergence branch, but at only 2 of the 8 ways the run loop can end. A run on 2026-09-08 wrote an empty reason into its completion signal while its own report named `HALTED_IRREDUCIBLE_QUEUE_ALARM`. **PROPOSED**: a 3-line fallback immediately before `signal_complete()`, touching neither existing site.

**Retry on timeout.** The founder judged a plain retry instruction close to superfluous given fingerprinting, routing and the sweep. Partly right: `ModelConfig.max_retries` exists and is genuinely wired, read at 5 sites in `dispatch()`, and timeouts at the interface layer do retry. But the string `max_retries` appears **0 times** in `bench/reference_runner_v3.py`, and the runner's own wall-clock watchdog raises a timeout with no retry of that route. Its budget of `timeout * 3` truncates the configured retry budget for 4 of 5 seats. **PROPOSED**: derive the watchdog budget from the retry budget instead of a fixed multiplier, which makes an already-wired capability spendable rather than adding a new one.

**Vagueness in the notes.** The founder asked whether the vagueness he identified in the overnight report had carried into the experimental notes, which exist for reproducibility. It has, and the scale is larger than expected: **1158 findings across 217 of the 373 notes**, 58.18 percent of files, Wilson [53.11%, 63.07%]. Of those findings **535 are the unnamed-subject class**, 46.20 percent, Wilson [43.35%, 49.08%] — the exact class complained of. 1 offending phrase alone, the bare noun phrase beginning `the sys` and ending `tem`, accounts for 235 findings, 20.29 percent of the corpus. Naming each subject is editorial work, not a mechanical substitution. Separately **OPEN**: whether any hook, test or continuous-integration step invokes the linter, or whether it is only ever run by hand.

**The residual human-queue item.** C0050 is confirmed as the single item left in the queue at severity 0.9, raised by the ChatGPT-SIM seat. It carries no falsifier of its own claim, none was ever executed, and 0 verdicts were recorded. It does not meet any reasonable reading of computationally irreducible. The exit is a recorded human ruling rather than new measurement.

## What is already in place

**The panel machinery exists and works.** Exactly 1 dispatcher carries the formal schema in its system prompt while also seating Fable and CC2 and recording their tool calls: `bench/confer_maths_panel_2026-09-05.py`. Both seats are genuinely tool-enabled, with 237 and 41 recorded tool calls on the run of 2026-09-07. The dispatch the founder asked for therefore needs no new machinery. 1 adjacent gap, not on this path: `bench/experiment_11_orchestrator.py:1442` sets tools to none unconditionally for the DeepSeek route.

**The exp39 branch is intact and its deletion is cheaply reversible.** `exp39-experimental` exists locally at `e49a021` with 107 commits unreachable from `origin/main`, is not an ancestor of it, and exists on no remote and under no tag or backup reference. Its tip tree is byte-identical to main commit `043a0a8`, so deletion would orphan 865 objects and 12 file paths that exist nowhere else, but **0 files from its tip**. The smallest safeguard is 1 command creating a durable tag before any deletion, which pins all 865 objects without pushing anything.

**A caution on the argument for keeping it.** The standing ruling rests on the claim that 20 of 21 falsifiers failing against today's file reproduce against some earlier stored version. That figure exists in exactly 2 places: prose in `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md:253`, and a code comment at `scripts/adjudicate_by_repair.py:270`. No committed output or test reproduces it. This is the shape `measured-rate-travels-with-its-script` names, code comments included. The ruling may well be right; it is currently unevidenced, and the script that could rebuild the number is the one carrying the comment.

## Decisions that sit with the founder

1. **Push.** 11 commits are unpushed and the push is refused at the assistant's end.
2. **Routing and the sweep in the exp56 configuration.** Deliberate control, or omission?
3. **Order of work.** The recommended order is falsifier supply first, since it is the halt cause and everything else is downstream of a run that can finish; then the doctrine wording, which is cheap; then the two-directory field; then the 6 remaining traversals.
4. **The panel brief.** Before it is written, the assistant owes a statement of what "simplest sufficient additive" is taken to mean in this project, for correction. Getting that wrong wastes the panel.
5. **The notes remediation.** 1158 findings is a programme, not a task. It needs a scope ruling: all notes, or only those a reader would reach.

## What this report does not establish

The intake-parser fix is not shown to have prevented the halt. Whether the exp56 configuration is deliberate is unknown. The client-side half of the remote-access fault is untested, because only the host side leaves a log on this machine. The recovery figure rests on 2 incidents.

Written under CDSFL note standard v1.7 (26 August 2026).
