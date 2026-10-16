# The 6 decisions waiting on the founder, consolidated

Written 2026-10-16 19:14 BST. Paired with `~/Desktop/CDSFL_tts/READ_THIS_ONE_Decisions_2026-10-16.txt`, which is the version written to be read aloud. This file supersedes the decision sections of `End_Of_Day_2026-10-16` and `Panel_Attack_Reassessment_2026-10-16`; both remain as the record of what was found and when, and both now carry a superseded banner.


## Why this file exists


2 reports were delivered today and neither should be read on its own. The end of day report explains the 5 decisions properly, in about 5,300 characters. The later panel reassessment names all 5 in a single sentence of 193 characters and explains none of them, a ratio of 27 to 1, because it was written about the panel attack rather than about the decisions. So reading only the newer one would leave the founder with 5 decisions named and unexplained.

Worse, the older report is now wrong on 1 of them. It says that of 7 steps a new model passes through, 5 fail silently. The panel corrected that measurement 4 hours later to 9 of 10, which is 90 per cent with a 95 per cent interval from 59.5850 to 98.2124 per cent. Reading the older file to decide the model admission question would therefore use a number that has already been superseded.

This file carries all 6 decisions with the current figures. The other 2 remain on disk as the record of what was found and when, and both now carry a line at the top saying this file replaces them.

## First decision. should the instruction density ceiling govern anything at all


There is a per model ceiling on how densely packed with constraints a prompt may be. The recommendation is to leave it inert and not wire it up, and the case has 3 parts.

Its only consumer that did anything was the mechanical directive pruner, which the founder retired by default on 13 October. With pruning off, the ceiling's sole remaining effect was a warning saying that a coherence penalty applies to detection, and nothing in the repository computes or applies such a penalty. That warning sentence has now been corrected in the code.

The panel found a harder fact than that. The routine that would recompute those ceilings writes its results under the model's seat name, while the routine that reads them looks up a different key entirely, the versioned configuration name. They match for 0 of the 5 models in the roster. So the recalibration pipeline writes into a key space its consumer never reads, which is independent of everything else and survives the repair made to its input.

And the purpose the founder named for it is served by a different mechanism. Never being fed work larger than a model has demonstrably handled is a limit on SIZE. This ceiling is a limit on the DENSITY of instructions. What actually does the first job is the per model capability fingerprint, a stored record of the largest prompt each seat has handled, and that is the second decision.

The decision is whether to leave the density ceiling inert, implement the missing penalty, or wire the ceiling to the size limit. The recommendation is the first, and the reason is that the second and third both connect a mechanism to a consumer that does nothing useful.

## Second decision. a capacity number that cannot detect overload


This was item 5 on the founder's own list of smaller defects, described as a capacity number shared identically by 4 paid models and untouched for 185 days.

It is now measured. The field stands at 465,206 characters on 4 of the 5 paid seats, against 110,076 on the fifth. It first entered a committed record on 13 April 2026, which is 186 days before the newest commit, so the founder's figure is confirmed. Against each seat's own stored window of 50 dispatches it sits between 4.89 and 6.64 times above what that seat has actually handled recently. 2 further fields repeat the same number on all 5 seats, so 3 fields carry 1 figure.

It has never been bounded from above. The fields that would record a failure are zero or unset on every paid seat, so the routine that lowers the number when a dispatch fails on length has never once fired, and 1 large dispatch in 1 old run still sets today's routing ceiling.

This matters more than it looks, because the fingerprint ceiling is what actually serves the purpose named in the first decision. A ceiling 6 times above recent experience, with no upper bound, cannot detect a model being overloaded.

It is deliberately not changed, and the code itself says why: altering it changes routing for the paid models, which is a design decision rather than a repair. There are 3 options. Decay the number towards the recent window. Bound it by a measured failure. Or leave it as a proven floor and stop calling it a capacity.

## Third decision. capability is still selected by a model name


The density ceiling is looked up by mapping a seat onto a versioned configuration name, and 4 of those 5 names refer to model versions the current roster has moved past. 1 names Opus version 4.6 against a roster carrying 4.7. 2 name GPT versions 5.4 and 5.3 against a roster carrying 5.5. 1 names DeepSeek version 3 against a roster carrying version 4 Pro. That is 80 per cent, with an interval from 37.5535 to 96.3776 per cent.

So a live seat inherits an allowance for dense instructions that was written for a model no longer in use, selected by its name. The founder's ruling of 7 October is that names are recorded for provenance only and carry no weight on capability. Nothing has been changed here, because making the table reachable would make the problem worse rather than better, and re-keying it onto something measured is the decision.

## Fourth decision. admitting a model. loud failure first, or consolidation first


The founder asked whether adding, removing or changing models is genuinely trivial by design, as it should be, and whether that objective has been met.

The answer has 2 halves. On edit count it is modest: a parse of the code finds 156 per model tables across 67 files, but that overstates it roughly threefold, because 86 of those are tests that guard the roster rather than admit to it, 50 are historical one off experiment scripts whose edit would change what those past runs did, and the rest are measurement tools. The live harness is 12 tables across 6 files plus 1 configuration file.

On failure mode it is not modest at all. A model that does not exist was put through the real resolution chain. Of 10 steps, 9 fail SILENTLY and only 1 fails loudly. That is 90 per cent, with a 95 per cent interval from 59.5850 to 98.2124 per cent and an exact interval from 55.4984 to 99.7471 per cent. This is the corrected figure; an earlier report said 5 of 7, which counted the directive composition step as a loud failure when the dispatcher actually catches it and carries on with a degraded prompt.

The worst single instance was missed by the first measurement entirely. The context budget is read with a default of infinity, and the next line compares the work against that budget, so a missing entry sets the limit to infinity and the check can never fire. The code's own documentation names that hazard in exactly those terms.

The recommendation is that making the failures loud comes first and consolidating to a single registration point comes second, because a single point that still defaults silently would hide 12 misses behind 1 and would also remove the only signal a researcher currently has, which is that 12 separate edits are at least visible work.

On the form of the loud failure, the panel rejected 2 of the 3 options. A plain error at each lookup needs 15 edit sites, fails at first use so a recovery path fails mid run after money has been spent, and this codebase demonstrably swallows broad errors near dispatch. Refusing to dispatch that seat is benching it, which the code already forbids in the rule that a dead seat refuses the whole run and is never dropped. It adopted a check before the run starts: 1 function, 1 call site, before any spend, asserting a model's presence in every table it must be in and reporting all the misses at once rather than the first. There is an existing routine built for exactly this that is not yet wired into the live runner, so the repair extends it rather than adding a parallel mechanism.

## Fifth decision. when to reset the immune memory


The founder ruled that the immune memory should be reset for the upcoming live experiments, since simulation can only say so much about how the facility behaves in real paid runs. He also ruled that researchers should be able to choose, and that the default should be left on so the memory persists between experiments. The switch and the default are built and tested.

The one off reset itself is deliberately not done yet, because the right moment is immediately before the first live experiment rather than while the work is still on the simulation branch. The decision is simply confirmation of that timing.

## Sixth decision, and this one is new from the panel. an ownership guard on merge verdicts


A model can say that 2 findings are the same defect. The panel found that when a model names ANOTHER model's finding as the duplicate, the current code resolves it wrongly: the pattern that extracts the identifier matches the characters C2 inside 1 model's own label, so the lookup fails, and the specification then converts an unresolved duplicate into a confirmation of the target. That is a silent inversion of a verdict. 442 identifiers in the archive are misread this way, confirmed by 2 independent implementations.

The panel's repair makes that resolve correctly. The consequence is that the verdict is then recorded against the other model's finding, at a call site that has no ownership check at all.

The record says this is intended. The lookup the repair uses documents its own purpose as resolving a duplicate raised by a DIFFERENT model, and calls that the only case the duplicate recorder exists for. The routine that records verdicts has never carried an ownership check for ANY verdict type, because a shared blackboard is the design.

But the consequence was demonstrated both ways. With 3 models proposing, the current code manufactures a corroboration out of a mis-resolved duplicate. The repair instead puts the verdict on the correct finding, and over 6 rounds can escalate to a human decision on a finding whose owner never voted.

The decision is whether that is acceptable as designed, or whether an ownership guard belongs at that call site.

## What is owed as a correction rather than a decision


These need no ruling. They are listed so the founder knows they are known and queued.

A figure published earlier today, 94 of 212, does not reproduce. The producer carries a hand written copy of the counter's release conditions instead of calling the counter, and the copy is wider by 15 entries. The numerator of 94 and the run total of 18 are right; the denominator of 212 is wrong. The corrected figure is 94 of 197, 47.7157 per cent with an interval from 40.8515 to 54.6673. It is live in 5 places and is the first thing to fix.

The glossary still states the penalty claim both panel seats retracted, and still describes the retired pruner as active. It is the definition an operator looks up.

A code comment about the symbol kappa is false by count, and the coherence penalty itself does appear in the tree inside a prompt used for a mathematics audit, which both seats' comments drop.

The runway document exists only on the Desktop, unversioned, which is the single point of failure already fixed for the operational tracker. 6 of its stage 3 rows also still say they are blocked on a ruling that was given at 14:46 today.

Stage 1 item 1.2 is marked done on an incomplete repair. Its own text is the panel's finding word for word, and within its own stated scope it still fails for 2 of 8 model labels, 25 per cent, interval 7.1479 to 59.0725.

## Where the project stands, in 3 numbers


Across stages 1 to 3 there are 19 items with 6 done, 31.5789 per cent, interval 15.3644 to 53.9896. Stage 1 has 2 outstanding, 1 of which is a replay that costs nothing and is that stage's own exit test. Stage 2 has 3 outstanding and needs 1 live run. Stage 3 has 6 built but never run plus 1 not built. The task list holds 111 entries with 11 open and 1 blocked.

The backlog of 869 undefined compound terms is untouched, and 4 of the 6 smaller items on the founder's list remain. A full board run is owed; it was started and stopped deliberately at 12 per cent because the machine had 1.60 gibibytes free with swap already at 2.56 of 4, and the panel was the instruction that mattered more at that moment.

Written under CDSFL note standard v1.7, 26 August 2026.
