# Final discussion before authorising the work. 2026-10-16, 21:55 BST.

This supersedes nothing. It answers the questions raised in the 3 annotated files and adds 2 findings made since.


## State After The Restore


The restore ran and returned exit code 0. The working tree is clean, on the simulated shakedown branch, 4 commits ahead of the remote. The last full save was at 17:32 today. The master task list now holds 113 entries, 0 coherence problems, with 13 open.


## A Correction I Owe, And It Is The Good Kind


The fingerprint question was going to get a wrong answer. The question was whether seat fingerprints are recomputed in the first blind round of each experiment, so that they reset after the next live run. The answer is yes, and it was built today on the ruling given today. Executed rather than read: the runner configuration defaults the fingerprint scope to experiment, and under that scope the loader returns 0 seats against 11 under the persisting scope, and it clears its own snapshot so that at save time every seat correctly reads as changed. The expectation is met.

The earlier claim that it was unwired rested on searching for a function name that turned out to be a different function. That different function is where the real fault is, and it is narrower and sharper.


## What Is Actually Wrong With The Fingerprint Reset


There are 2 loaders reading the same directory inside 1 run. The first is the main observation load and it honours the scope. The second sits inside the routine that decides whether a payload is too large for a seat and must be split. That second loader takes no scope parameter at all, reads the same files from disk, and caches the result for the whole process. Under the default scope the main path returned 0 seats while the second returned 11.

This matters because the number it reads is multiplied by 0.9 to set the ceiling that decides splitting. So a run that believes it is measuring its seats afresh is splitting payloads on numbers inherited from an earlier experiment. Of the 11 seats it sees, 5 are paid seats carrying a recorded capacity, and 4 of those 5 share the identical value 465,206. That ties directly to the existing item about a capacity number untouched for 185 days, and it adds something that item did not establish: the shared number is what the splitting decision actually uses, not merely what is written down.

The safety argument for the merge survives, but for a different reason than the one given earlier. Both loaders key on the seat label, so a live run asking for a paid seat reads that seat's own file and never the stand-in file. The stand-in records stay unreachable to a live run. The protection comes from the labelling, not from the scope switch. The distinction is worth stating because the first draft of this finding credited the switch with it.

The repair is small. The routine that clears the cache already exists. What needs a ruling is only which of 2 forms it takes, because changing the splitting ceiling changes what a paid run does.


## The Question About Making The Restore Mechanical


The question was: if compaction can be detected mechanically, why can the restore not also be run mechanically. Two thirds of it already is, and this turn is the evidence.

A hook on message submission does not merely advise. It runs rs, the restore command, as a subprocess, and the full variant at that. It ran on the turn at 21:40 tonight and returned exit code 0. Separately, a hook on the stop event returns a blocking code so that the turn cannot end before the restored context lands, with a guard against looping and a safety exit so that a recovery hook can never kill the session.

So the script half is mechanical and the enforcement half is mechanical. The third that is not mechanical is this: a hook can run a script, inject text, and refuse to let a turn end. It cannot make the reading happen. On that turn the notice supplied a list of 10 documents to read first. Running the script was mechanical. Opening the master task list and the tracker was a choice.

The fix follows directly from naming it that way. Inject the content, not the paths. The restore notice should carry the resume pointer and the open task entries inline on the first turn after compaction, so the state arrives whether or not a file is opened. It is bounded by construction: once per compaction, and only the open entries, 13 of 113, rather than the whole 854 line document. What needs a ruling is how many characters may be spent, because that trades context against reliability and the ceiling belongs to the machine, not to taste.


## Wolfram, Demonstrated Rather Than Promised


The complaint was that Wolfram keeps getting dropped. This turn it was used as the secondary falsifier on a real interval from the repeatability work. The local engine returned the pair 61.48339256287346 and 92.69311541657795. The project's own Wolfram standard classified that result as verified, on the grounds of exit code 0 with output and no failure shape. It agrees with statsmodels and with mpmath to 6 significant figures. The attribution the standard requires is that the value was computed with Wolfram Language on the local Wolfram Engine.

On making it a switch rather than a preference, the position is better than expected and the gap is exact. The installer already offers the Wolfram Engine, already imports the Wolfram standard module, and already detects whether Wolfram genuinely computes rather than merely whether the command exists. The onboarding document already carries the ruling of the 28th of September that Wolfram is optional and always will be, and that where present it is the secondary falsifier against open source output and never the primary route.

What does not exist, measured: 0 matches anywhere in the repository for a stored researcher preference. Nothing records the statement that this researcher has Wolfram and wants it used as the secondary falsifier. So the installer can install it and the harness can use it, but no durable setting connects those 2 facts. That is the installable switch being asked for, and it is a small addition with 3 parts: a preference written by the installer, read by the falsifier path, and surfaced in the interface design when that is built.

On compulsion, the hook event that can enforce it is now clear. Hooks on message submission can only advise, which is why the existing audit hook reports and nothing more. A hook on the stop event can refuse. Two such gates refused work tonight and a third refused this evening's commit for a genuine reason, catching a note quality regression that would otherwise have shipped. So the mechanical switch asked for is a stop gate, and the precedent for it is 3 refusals in 1 day, all correct.


## Repeatability Across The 3 Simulated Runs


The question was whether the fixes derived over the 3 simulated runs show any tendency towards repeatability, and whether fixes derived from simulated runs on that target should carry forward into live runs.

At the level of run behaviour the answer is yes. The 3 legs converged at rounds 3, 4 and 4, and all 3 reached the decay measure of 1.000. Finding volumes were 22, 19 and 38.

At the level of findings the first answer given was WRONG and is withdrawn here. The figures first delivered, 81.8182 per cent and 89.4737 per cent and 55.2632 per cent, came from comparing 2 fields of the finding catalogue. Those fields turned out to be a true or false value and a fixed status phrase. Leg 3 carries just 3 distinct combined texts across its 38 findings, and 18 of them read, true verified fix, no unresolved challenges. So the word overlap comparison was counting how many findings share a status phrase, and it reported the same figure at every threshold from 10 per cent to 99 per cent, which is the signature of a measure that discriminates nothing. A shuffled control scored 75 per cent against a real figure of 90 per cent, which should have been the warning.

The finding text does exist, in a different file, under the registry entries of the run state. There are 22, 19 and 38 distinct descriptions with median lengths of 825, 720 and 843 characters. Rebuilt on that source, the word overlap comparison now passes 4 attacks: disjoint text scores 0, identical text scores 1, the rate falls as the threshold tightens, and a shuffled control scores 0 per cent against a real figure of 45.4545 per cent.

The corrected answer is roughly half the withdrawn one, and it changes the conclusion. Reading the overlap at a 30 per cent threshold: 50.0000 per cent of leg 1's findings have a partner in leg 2, on an interval from 30.7221 to 69.2779 per cent, and 45.4545 per cent have one in leg 3, from 26.9203 to 65.3402 per cent. Leg 2 is the most contained: 68.4211 per cent of its findings have a partner in leg 1, from 46.0104 to 84.6356 per cent. Leg 3 is the least: 31.5789 per cent of its findings have a partner in leg 1 and 28.9474 per cent in leg 2, from 19.0846 to 47.4558 and from 17.0033 to 44.7571 per cent.

So the earlier claim that legs 1 and 2 are almost entirely contained in leg 3 is false. Fewer than half of leg 1's findings recur in leg 3. The direction of the asymmetry survives, in that the later leg's findings are the least likely to have a partner in an earlier one, but the magnitude does not support calling this containment.

One more thing the sweep shows. At a threshold of 70 per cent the overlap is 0 per cent in every direction. No finding in any leg is a near duplicate of a finding in another leg. Whatever repeats, repeats thematically rather than verbatim.

A number read at a single threshold would have been misleading in either direction, because the rate runs from 100 per cent at a 10 per cent threshold to 0 per cent at 70 per cent. The threshold is a choice, so the whole sweep is now reported rather than 1 figure from it.

Which forces an honest qualification. The 3 legs were not run under identical conditions. Leg 1 ran with the directive set arriving whole, leg 2 with the severity specification deciding rather than merely recorded, and leg 3 after the confinement repair. Repeatability in the strict sense requires identical conditions, and there are no 3 identical runs in this record. What exists is consistency across deliberately changing conditions, which is weaker and should not be reported as replication.

One boundary still has to be stated plainly. There is no field that identifies a defect ACROSS runs. Identifiers are unique per run, and the field named mechanism is a pipeline label rather than a defect class. So word overlap between descriptions is the only available proxy, and it remains a proxy: shared wording may indicate 1 defect or merely 1 vocabulary. If repeatability is to become a reportable property of this programme, a stable defect identifier has to exist.

On whether the fixes should carry forward, the recommendation is to carry them, with 1 limit. Each fix's warrant is a test that executes against the code, and the identity of the seat that raised the finding never enters that test. So the evidence for a fix does not depend on whether a stand-in or a paid seat surfaced it. The limit is that the selection of what got fixed was simulation dependent even though the warrant is not, so the simulated runs must not be cited as establishing how often such defects occur in live runs. Carry the repairs. Do not carry any claim about how often the defects they fix would arise in a paid run.


## Whether Adding Or Removing A Model Is Trivial


This was asked as a design objective and the answer is no, with a correction to an earlier figure. The live harness holds 12 per model tables across 6 files, plus 1 per model registry file. A raw structural count of 156 tables across 67 files overstates it about threefold, because 86 of those are tests that guard the roster rather than admit to it and 50 are historical one off experiment runners whose edits would alter what those runs did.

The count is modest. The failure mode is not. A model that does not exist was put through the real resolution chain, and of 10 steps, 9 fail silently and only 1 fails loudly. That is 90.0000 per cent, on an interval from 59.5850 to 98.2124 per cent by one method and 55.4984 to 99.7471 per cent by another. A researcher who misses 1 table gets a seat that runs while silently losing whatever that table gated. The worst single instance sets a context limit to infinity when an entry is missing, so the check that refuses an over-long prompt can never fire.

The free panel's answer on how the loud failure should work goes further than the ordering question, and it rejects 2 of the 3 candidate designs. A raised error needs 15 edit sites, fails at first use so that a recovery path table fails mid run after money has been spent, and this codebase demonstrably swallows broad exceptions near the dispatch point. Refusing to dispatch the affected seat is benching it, which is forbidden by the existing rule that a dead seat refuses the run and is never dropped. What it adopts instead is a run level preflight: 1 function, 1 call site, before any spend, checking a label's presence in every table it must appear in, reporting all misses at once rather than the first, and refusing the run. It names the precedent, a policy validation routine that already exists in the registry and is not wired into the live runner, so the repair extends something rather than adding a parallel mechanism. What is needed is a ruling on the form.


## A Point Where An Assumption Has Been Stated Twice And Is Not True Yet


Two of the annotations describe participating models as being assigned a unique hash identifier in the first blind round of an experiment, and 1 of them uses that as the reason a provenance problem is harmless. That facility does not exist. It was never built, and it was never put to the panel: the word hash appears 0 times in the panel brief and 0 times in either reply.

The conclusion it was used to support still holds, but by a different route. The 5 paid seat records that drifted had exactly 2 fields move, the experiment name and the timestamp, and no measured value moved at all, so the capacity recorded on both sides is identical. That is a provenance smear and not a corruption of capability. But it is not harmless because of hashing, and the design should be put to the panel rather than treated as settled.


## What Is Recommended


One thing, in keeping with the rule against presenting a list where a recommendation belongs. Rule on the form of the fingerprint repair, because it is the only finding from tonight that changes what a paid run does, and the merge is already approved and waiting behind it. Everything else on the list is additive and can proceed on the authorisation already given.

Written under CDSFL note standard v1.7, 26 August 2026.
