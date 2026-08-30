# The Simulation Could Converge Because Subprocesses Timed Out

2026-08-30, 19:46 BST (UTC+1)

Six repairs were executed, then CC2 and Fable reviewed them, then a revised runner was built and reviewed again. The suite finished at 4504 passed, 0 failed, 7 skipped. Skipped tests fell from 34 to 7, which is 79.4 percent of them removed, Wilson 95 percent confidence interval [0.632, 0.897].

The single most important thing found today was found by Fable in the second review, and neither the first review nor this session had seen it: the simulation harness turned a dead subprocess into what the runner read as a successful model response. That meant a simulated run could converge because subprocesses timed out, rather than because the evidence had settled.


## The Six Repairs, And What Two Of Them Turned Out To Be

The first proposal was to derive the number of memory files, 126 of them, inside sv rather than typing it. That proposal was wrong. sv has derived that count since 26 August, unconditionally, in its main routine. The test message that prompted the proposal was a historical note about seven past manual corrections, not a statement of a current defect. It was simply never recounted after a memory file was written. Running the existing derivation moved it from 125 to 126.

The second was to teach the simulated agents to write falsifiers. The agents were never the problem. The harness patched one dispatch function out of eight. The costliest miss was the routing ladder's falsifier writer, whose call hit a real unconfigured model, raised, and was swallowed by a bare handler that returned an empty string. The only symptom anywhere was a log line reading "0 resolved by strong writer", which reads as a weak panel rather than a dead transport. The seam now sits on the primitive that all eight call sites go through, so coverage holds by construction rather than by keeping a list in step. Proved end to end: a routing prompt sent through the repaired seam produced a 1,161-character falsifier that the runner's own extractor accepted.

The third, the fix-efficacy probe, reached 0 of 19 registry entries and left no trace of why, so "wired" and "unreachable" were indistinguishable in the record. It required both a proposed fix and a falsifier; all 19 entries had a fix and none had a falsifier. It is now admitted on the fix alone and records a NOT PROBED NO FALSIFIER outcome, without consuming its per-round budget and without marking the entry tried. Replaying the real 19 entries: 0 explained before, 19 explained after.

The fourth was to find out whether source diversity is computed at all. It is, but it belongs to the Ouroboros cell, where it means the full text of a paper was actually parsed. It is defaulted onto panel findings, which have no such property, so zero is the correct reading there. The investigation found a real defect underneath it, though. The co-discovery recorder added on 23 August, written to close a measured gap of 566 findings each carrying exactly 1.00 source alias, resolved using the duplicate's model paired with the original's finding identifier. For a cross-model duplicate, which is the only case co-discovery exists for, those belong to different models and the lookup can never match. The run held 17 duplicate records, every one a foreign-model identifier, and recorded none. The fix reproduced the defect its own documentation described.

The fifth and sixth were test repairs, and they closed 27 of the 34 skips. One real defect fell out of them: the note lint exited 0 on a path it could not read, so a typo'd filename reported "0 findings" and read as a clean note. Verified against git history rather than asserted: before the fix the exit code was 0, after it is 2.


## The Panel, And The Finding That Invalidated Its Own First Pass

CC2 and Fable were dispatched into disposable sandboxes. Fable's first report opened by stating that four of the five repairs it had been briefed on did not exist in the tree.

Fable was right about the tree it held, and the harness is what made that differ from reality. The sandbox is created with git worktree, which checks out the committed head. Twelve modified and untracked files were sitting in the working tree at dispatch, and nothing anywhere said so. A reviewer given a tree that is not the tree under discussion will produce a review of code nobody is running, and will do so confidently. The harness now carries the uncommitted changes into the sandbox and states in its log exactly what it carried. On the second dispatch it printed that it had carried nothing, because everything was committed, which is how that mechanism should read.

Two errors of this session's own were caught by the reviewers. The specialist knowledge field was reported as absent on all 19 entries; it is present on all 19 and marked admissible. The wrong key was read: the field records its state under "tristate", not "status", and a significance test was then computed on the false premise. And the framing "the falsification core was silent" was corrected by CC2 and the correction was accepted: the core ran, recorded 8 untoolable verdicts and raised its own NO SURVIVALS alarm. What was silent was the supply feeding it.


## The Convergence Defect

CC2 found the most consequential defect in the runner itself. The routing loop sets a flag marking that a round is pending a transport check, and after routing returns it uses that flag to decide whether any model was actually reached. Its own comment says a round where no model was reached must not burn the attempt nor mint a false record of an exhausted ladder.

That flag was being set inside the branch for sub-critical findings. For a critical finding it was never set at all, so the guard never covered a critical. A critical whose every routing attempt died on transport was recorded as genuinely irreducible, and unverified_critical_count, the reading that blocks convergence, skips exactly those entries. The chain runs: the network fails, a critical looks exhausted, the gate stops counting it, and the run can converge on an infrastructure failure rather than on evidence. It is hoisted above the severity branch now, pinned structurally, and the consequence is pinned by measurement: marking a critical irreducible drops the blocking count from 1 to 0.

CC2 then tried three separate ways to break that repair and failed on all three.


## THE SECOND PASS, AND FABLE'S N1

The revised runner, version 3.2, went back to both reviewers. Fable found the defect that matters most for the next run.

The real dispatch function raises an exception when a transport dies. The function that dispatches a round catches that exception and converts it into a failure sentinel itself, so that sentinel belongs to the findings path alone. The simulation shim returned the sentinel instead of raising. Every other path, including routing, verification, the sweep and preflight, detects transport death by exception, so a normal return was read as a model that had genuinely been reached.

The consequence is that a timed-out subprocess burned the one routing attempt a finding gets, and if every rung timed out the finding was marked irreducible, which removes it from that same reading. So the simulated run could converge because subprocesses timed out. Worse, the transport guard repaired earlier the same day could never fire in simulation at all, because the attempt counter always grew. The seam and the guard were separately correct and jointly broken. This was not hypothetical: the earlier run lost 7 of 20 dispatches to timeout.

The shim now raises, matching the real contract exactly, and its telemetry is recorded before each raise or it would leave with the exception.

Both reviewers also found, independently, that the core directive reaches no simulated model. The field the harness was setting is read zero times by this runner; the directive text is loaded inside a command-line entry point the harness bypasses. CC2 checked 6 distinctive lines of the directive against every composition and found 0 of 6 present. The harness now passes the directive text directly.

The reviewers disagreed on one point and CC2 settled it by measurement. Fable said the decomposed dispatch path cannot trigger at a 20 kilobyte target. CC2 measured the actual payload at 76,569 characters against a limit of 31,511, for every model in every round, because the 50,946-character system prompt dominates rather than the target. That path fires, raises an unknown API error, is caught, and falls through to the simulated dispatcher. It fails safe and costs nothing, but it is entered and never exercised.

Nine configuration values were also brought into line with the real experiment 45 they are compared against. One of them mattered a great deal: the earliest permitted stopping round defaulted to 12 while the run allowed 7, so one of the two convergence gates reported "too early" in every round and was never exercised at all.


## The Seven Tests That Still Do Not Run

Three are the Ouroboros network tests. They are correctly gated, because the suite is offline by default and that is right. They were run today with the opt-in set and all 20 tests in those files passed in 137 seconds. They are not broken; they had simply never been run in 49 days, and nothing in the repository ever sets the variable that enables them. Recommendation: run them on a schedule as a separate network job, and keep them out of the default suite.

Four are in the prose acceptance tests. They cover falsifiers whose own source contains a markdown fence, and the test wraps the falsifier in a fence, so the case is genuinely inapplicable and is covered by a dedicated class that tests something stronger. That class documents an open, unrepaired defect: a falsifier carrying its own fence cannot cross the reply channel intact, and the loss is silent. The damage is bounded, since the truncated fragment reaches an error rather than a false confirmation, but confirmations are lost and the re-route uses the same channel so it cannot heal. Recommendation: repair the transport before Bench Run 2 only if any of the 27 target tasks is a prose or markdown artefact carrying fenced listings. Otherwise defer. That is a decision about the target list, not about the code.


## What Will Still Be Silent On The Next Run

Stated in advance rather than discovered afterwards. The verification stage will not fire, because it requires round 6 and the run is expected to converge at round 3. That is faithful rather than defective: the real experiment 45 never fired it either and still reached 24 verified fixes of 39 through the falsifier path. Fable-SIM will run without a per-model directive, because no model configuration file exists for it and its tuning values were not invented. The post-convergence sweep is configured off. The decomposed dispatch path will be entered and will fail safe on every model in every round.

One measurement is worth stating on its own. The discrimination control needs a falsifier and a corrected copy on the same finding. The real experiment 45 has 23 falsifiers of 39 and 0 corrected copies; the simulated run has 0 falsifiers of 19 and 19 corrected copies. Entries carrying both, across both runs pooled: 0 of 58, Wilson 95 percent confidence interval [0.0000, 0.0621]. That control has never once had both its inputs.


Written under CDSFL note standard v1.7 (26 August 2026).