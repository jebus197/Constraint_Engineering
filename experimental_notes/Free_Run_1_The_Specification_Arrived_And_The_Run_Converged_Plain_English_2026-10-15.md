# Free run 1: the rulebook arrived, and the run converged at round 3

2026-10-15 08:43 BST. Plain-English companion to the technical note of the same name. Audience: a reader who does not read code.

## The headline

Free run 1 is the first run in this project's history in which the models were actually sent the project's own rulebook. It converged at round 3 of a 10-round budget, in 82.4 minutes, on the hardened gate: gamma_critical reached 1.000 and held for 2 rounds with a leave-one-out minimum of 1.000, alongside 3 consecutive settled rounds with no new criticals. 22 findings, 0 unresolved criticals at close, 0 contested. Both planted defects were found in round 0.

That is the cleanest convergence the prose target has produced, and it happened on the run where every seat received 27,803 characters of specification instead of a 2,503-character summary of configuration flags. All 22 of the blocks the project's own classifier marks HARD arrived, against 0 of 22 before the repair. Among the blocks that had never reached any model is the whole of Falsifier Integrity, Do Not Reach for the Answer, which is where the instructions not to read a scoring key and not to weaken a test to make it pass actually live.

## A prediction from the night before came true, and the guard caught it

Before either run started, a confound was recorded: giving the seats the whole rulebook would push every simulated seat's prompt past its own recorded capacity figure, and because that figure is treated as a ceiling rather than the floor it actually is, every single dispatch would have been force-split on the size of its own instructions. The paid seats would not have been affected at all, their figures being 465,206 and 110,076 against the simulated seats' 72,934 to 80,517. A fault that appears only in the free runs and vanishes in the expensive ones is the worst possible shape, so a guard was built rather than deferred.

Run 1 shows it working. Across 24 decomposition decisions covering all 6 seats, the total payload exceeded the 80,000 limit every time, and the part that can actually be split was under the limit every time, and nothing was split. The standing instructions were 78.30% to 89.93% of each payload, so the un-splittable part dominates, which is exactly what makes splitting pointless: the instructions are re-sent with every chunk, so chunking raises the total and leaves every chunk still over the limit.

This is bounded on purpose. It shows the guard fires on the payloads this target and these 6 seats produce. It shows nothing about a paid seat, which the confound was separately measured never to reach.

## The round-budget advisory spoke for the first time, and said there was nothing to say

The advisory, built on 2026-10-11 and never previously emitted into a round log, fired and reported that no projection was available: a run whose novelty does not decay has no optimal round count, and that is a result rather than a gap. The per-round findings were 14, 2, 5 and 1, so the critical series hit zero faster than an intensity decay can be fitted. It declined to answer instead of clamping, which is the designed behaviour.

## 2 defects found during the run, and the credit for 1 of them belongs to a seat

The first is a provenance fault. Every fingerprint file was rewritten at the moment of convergence, including the 5 real paid seats, which were never dispatched in a simulated run at all. CC2's record now says it was observed in free run 1, and its true last real observation, study_run1b of 2026-10-03, was overwritten. The cause is that the loader reads every file in the directory into one table and the saver then writes the whole table back stamped with the current run's name. No measured value moved, because those seats were never asked anything, so nothing was appended. What keeps the real and simulated records apart is one thing only: the mandatory simulation suffix makes them different keys. So a naming rule, recorded as a rule about labels, turns out to be the sole guard on the real seats' accumulated counters, 3 of which feed live routing decisions. Drop the suffix and this stops being a mislabelled record and becomes corrupted data.

The second finding about that first one matters more. The fable seat found it on 2026-10-05, during the fingerprint ladder review, and named that load-everything-then-save-everything asymmetry precisely under a heading reading The Fingerprint Store Erases Run Provenance On Every Save. Its script exists only inside the sandbox it was written in. It is not in the scripts directory and it is named nowhere in the master task list. A seat found a real defect, wrote the producer, and the work never left the sandbox.

The second defect is that the coherence-budget recalibration cannot be driven from these runs, and is inert in 3 separate ways, each sufficient on its own. Nothing calls it. Even if called, it changes a value that lives only in memory, so the recalibration dies with the Python interpreter that performed it. And when handed a real run's logs it returns its own existing defaults unchanged, because 0 of run 1's 61 recorded entries carry the 2 fields it reads. The arithmetic inside it is sound, which is the useful part: given data in the shape it asks for it moves the first seat's budget from 0.02 to 0.0571. So this is a mismatch between what the runner writes down and what the calibrator expects to read, and the repair belongs at the writing end. The consequence is that the lean-versus-full comparison every proposed cut has been gated on since 2026-07-18 stays un-runnable until that mismatch is closed. It was deliberately not fixed between the 2 runs, because changing the composer mid-pair would make neither run attributable.

## A third defect, and this one was caught by watching run 2 go past

The confinement guard refuses a falsifier permission to read the very document it was asked to review. Run 1 carries 18 such refusals, and every one of them is the run's own working copy of the target. Each one sends its finding to a human marked neither confirmed nor refuted.

Both halves of this are individually right, which is exactly why neither file could reveal it on its own. The guard refuses any path inside the run-evidence tree, even where the surrounding directory is allowed, because a falsifier that can read run evidence can read earlier verdicts instead of demonstrating anything. Both free seats found that hole independently on 2026-10-12 and it was closed the same day. Separately, since 2026-09-01, the runner has placed its working copy of the target inside that same evidence tree. And there is already a designated, permitted place for a staged review target, described in the guard's own words as where an exam falsifier opens the one document it is given, which the runner has never used.

The date is settled by the refused paths rather than by commit history. The run of 2026-10-03, before the rule, has 81 refusals and not one of them is a target: they are Python interpreter paths and import probes. Both runs today have 18 refusals and all 18 are the target. The separation is about as sharp as a measurement gets.

It needs its bound stated, because this would be easy to overstate. It did not stop run 1 converging and it left no critical unresolved, because the gate reads unconfirmed criticals and a refusal is not a disconfirmation. What it costs is verification depth: how many findings carry a demonstration that actually ran, rather than a referral to a person. It was deliberately not fixed, because run 2 is carrying the identical fault at the same count, which keeps the pair comparable.

## The severity question was already answered, and not by these runs

Run 1's severity shadow reports nothing crossing downward across its 22 findings. That is the expected outcome rather than a surprise: at the rate measured over the archive, 7 in 2,994, the chance of seeing 0 crossings in 22 findings is 0.9498. 688 findings are needed before a zero carries any information, so the 2-run contrast is under-powered by a factor of 31.27. The effect question is already settled at proper power by the archive replay, which gives 7 changed releases, small because the other half of the release test holds for only 295 of 2,994 findings. What run 2 therefore measures is whether turning the switch on breaks anything, not what it changes. Presenting its 22 findings as the effect measurement would be swapping an under-powered instrument for an adequate one that has already run.

## A tension in the programme's own design

The in-round clearance arm asks whether the unresolved section elicits the identifier-addressed falsifier form at all, against a baseline of 0 in 3473 archived round replies. Run 1 gives 0 in 29 seat replies, and that zero means nothing, because the form can only be supplied if there was an unconfirmed critical rendered for a seat to address, and run 1 ended with none. The parser had nothing to fire on.

This is worth stating plainly: the programme's success criterion is 3 consecutive clean convergences, a clean convergence leaves no unresolved criticals, and that is precisely the state in which this arm cannot be read. The better the runs go, the less measurable it becomes. 3 options are on the record: accept it as unreadable on clean runs and read it only from runs that stall; seed a run with a known unconfirmable critical; or replay the 175 attributed blockers from the archive through the repaired summary and measure elicitation against the corrected prompt instead of a live run. That is a decision rather than a repair.

## 1 hypothesis formed and withdrawn inside the hour

Three findings failed to close, and the explanation offered at 08:14 was that the verification step could not reach the code listings inside a prose document. That was wrong, and it was wrong in the way 6 earlier figures this week were wrong: a universal asserted after reading one part. Calling the function rather than reading it shows the narrow prose path is deliberate, with 3 rejected alternatives recorded beside it, one of which had been measured closing a finding on a fix that injected a shell command. Run 1 then closed 2 of those 3 findings in its own post-convergence settle, refuting the hypothesis a second time without being asked. What survives is narrower and already known: on a prose target nothing closes by static verification, so closure rate is not a measurable quantity there.

## Where things stand

Run 2 launched at 08:34 with the identical configuration plus the severity switch, under the same watchdog and the same tail terminal. The invariance sweep that answers the guard-reach arm runs over both runs once run 2 exits; it was held back rather than run alongside, because each probe clones about 683 MB three times per finding and the machine had about 57.8 MB of free pages with a run live.

Neither run costs money. The simulation substitutes subagents at the single point a paid model would be called, every seat label carries the simulation marker at source, and the spending limit is 0.00.

Written under CDSFL note standard v1.7 (26 August 2026).
