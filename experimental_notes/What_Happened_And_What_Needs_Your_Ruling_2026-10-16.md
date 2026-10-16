# What happened in the last run, why it produced so many rulings, and what is outstanding

2026-10-16 10:55 BST

## The run itself went well, and it closed the study's success criterion

Leg 3, the third and final leg of the shakedown, converged at round 4. The reason string is the hardened one: the decay-curve measure reached 1.000 against a threshold of 0.30, sustained over 2 rounds with a leave-one-out minimum also of 1.000, and 3 consecutive settled rounds with no new critical finding. 5 rounds ran in total, 38 findings, 71.5 minutes.

That is 3 consecutive clean convergences, so the success criterion the programme set is met. Legs 1, 2 and 3 converged at rounds 3, 4 and 4, and all 3 reached 1.000 on the decay curve.

Two things that had never been exercised were exercised. The closing sweep was handed 15 residual findings and acted on them, withdrawing 4 and leaving 9; legs 1 and 2 had given it nothing to do, which you correctly ruled is not a fault, and this leg shows it is not inert either. And 2 in-round falsifiers executed, which is the first data that arm has had from a clean run rather than a stalled one.

The gate also refused once, at round 3, while both of its conditions already held. That refusal was checked rather than assumed: round 0 produced 13 findings of which 12 carry severity at or above 0.7, while rounds 1, 2 and 3 produced a maximum severity of 0.5 and no criticals at all. So the blocker was one of round 0's genuine criticals and the refusal was correct. Leg 2 took the identical path.

## Why it produced so many rulings, measured rather than asserted

The honest answer has 3 parts, and the first one corrects what I implied to you last night.

**Most of them are genuinely new.** Of the 13 dated decision items, 11 were recorded on the 15th or 16th of October and only 2 predate the run: 15.3846% predating, with a 95 per cent interval from 4.3258% to 42.2346%. So this is not mostly a stale queue. The night found a great deal, and I was wrong to imply otherwise.

**A large share of what it found is the kind of thing your own standard routes to you by design.** The additive standard says a feature may not be removed or narrowed without a committed measurement and your ruling. Several of the night's findings are exactly that shape: a guard that should be loosened, a recorded output that would change, a schema that would invalidate replay. So a productive night mechanically produces rulings for you. That is the standard working, not failing.

**And 2 were a real mechanical fault, which you diagnosed from the symptom alone and which is now fixed.** Two items had already been ruled on by you and were being put to you again. The zero-plant control is the clearest: you ruled "restart it" on the 7th of August and again on the 6th of September, and 70 days later it was still appearing under decisions that need you.

The cause was that neither the task list nor the report generator recorded that you had ruled. Every task entry carries a lifecycle label and a build label, and both describe the WORK. Neither could express "he has already decided this". So a ruling you gave that was not immediately carried out left its entry indistinguishable from one you had never seen. Separately, your rulings live in 29 dated documents created at a rate of 1.1469 per week over 177 days, and the one actually named the founder decision register has 3 commits and was last touched on the 15th of August, so there was no canonical place to check either.

## What was fixed this morning

A ruled field now exists on every task entry, and the report generator routes an item you have ruled on out of the decision list and into outstanding work, carrying the date you ruled it. It moves rather than vanishing, because a queue that quietly under-reports is worse than one that over-asks. The queue fell from 13 to 11 on the first regeneration. 15 tests hold it and 4 deliberate breakages each turn them red.

A second fault was found while doing that, and it had already reached you. The routine that prepares the spoken version of the morning report promises in its own description that file paths are dropped, because reading a path aloud is unusable. It never dropped one. The file delivered to you last night contained 12 path-like tokens that a reader pronounces character by character. The test meant to catch it checked for a single literal prefix, and 11 of the 12 did not begin with that prefix, so the test passed while the fault shipped. Both the routine and the test are repaired, and the spoken file now contains none while the written one keeps all 35 of its locators, because a listener needs to decide and a reader needs to act.

## Outstanding work that needs no decision from you

There are 5 items. Two of them are the ones you already ruled on: the zero-plant control restart, ruled on the 7th of August, and the admissibility scorer, ruled on the 10th of September and already built and tested. The other 3 are a check on whether a completed entry's evidence actually fails when its fix is reverted, a blind spot in the note checker, and the shortened-instruction fault that was deleting code from reviews, which is now fixed and awaiting its next run.

## The 11 rulings, and which ones actually matter

Four of these are consequential and 7 are quick. Taking the consequential ones first.

The largest is a guard that stops a finding labelled mathematical from being moved onto the code-checking path, outside software experiments, at any confidence. That move is the single most valuable move Haiku makes, and the guard refuses it. More than 3 in 4 of everything that guard has ever refused was an attempt to make precisely that move, and 5 of them happened inside leg 3 itself, on a target that is prose with real code embedded. The repair is one condition, and because it loosens a guard it needs your word.

Second, a commit from the 6th of September quotes you approving the removal of a severity gate, and the record of decisions awaiting you appears to say something different. That needs a straight confirm or deny from you, because if you did not approve it the gate goes back and this is a reversal rather than a new design.

Third, the coherence budget recalibration, which you asked me to explain before you would rule. It is a per-model ceiling on how densely packed with constraints a prompt may be; when a model exceeds its ceiling the composer prunes optional content to get under it. The recalibration is the routine that recomputes those ceilings from past experiments instead of using hard-coded defaults, and it is inert in 3 separate ways. Fixing it means every future run records 2 extra fields, which invalidates replay against older runs, and that is why it is yours.

Fourth, the honest answer on the fully green board. Of the 9 failures that remained after the runs, 7 are now fixed on your ruling to derive each baseline from the archive rather than pin a number. Of the 2 left, one goes green simply by closing work. The other cannot go green honestly without your ruling, because run 2's own recorded findings carry identifiers containing a bare vendor name, and the only ways to clear it are to rewrite recorded experimental evidence, which is falsification, or to normalise future identifiers going forward, which changes what gets recorded. I recommend the forward normalisation.

The remaining 7 are smaller: 3 defects found during the specification repair and deliberately left unfixed, a counter whose release condition disagrees with it about severity, an integrity check that refuses a correct falsifier by construction, a band label printed for a quantity that is not yet measurable, a capacity number shared identically by 4 paid models and untouched for 185 days, and the backlog of 869 undefined compound terms across the notes.

## The one thing I recommend

Rule on the mathematical guard. It is the only item on the list that is actively costing finding quality in every non-software experiment, it was observed doing so 5 times inside the final leg, and the repair is a single condition with the measurement already committed. Everything else can wait for a quieter morning.

Written under CDSFL note standard v1.7 (26 August 2026).
