# Answers to the 5 questions in your annotations, and what they add to the work

2026-10-16 14:45 BST

## Stage 3 is unblocked, and that is the largest single thing to happen to the runway in 69 days

Your ruling that the brief public exposure of the answer keys is not significant releases exp50, exp51 and the 4 exp52 cells. Six of the seven remaining experiments in the arc were built and never run on that one decision, requested on the 8th of August and carried 69 days. The runway documents now say so.

One correction for the record, because you believed it had already been answered. It had not. Searching all 570 of your recorded annotations, 2 touch the question and only today's rules on the exposure; the one from the 2nd of October concerns the answer-key access checks being internalised into the runner, which is a different matter. The founder rulings of the 22nd of August cover 9 items and this is not among them, and the handover document of the 24th of August records it as outstanding with 3 options. So today is the first ruling, not a repeat.

That matters in one practical way. Of the 3 options recorded, you have taken the first: accept the exposure and report it. The reporting half is part of the option, so if those 3 experiments are published as blind exams the exposure window is disclosed alongside the result. That is not a re-opening of your ruling; it is the condition the option carries.

## Are fingerprints recomputed in the first blind round of every experiment?

No. They accumulate, and there is no reset.

The saver takes the larger of the stored value and the new one, so a seat's recorded maximum only ever rises. Nothing in the code mentions resetting or clearing them, and no per-experiment boundary exists. What you described is therefore a requirement to build rather than a fact to confirm, and it is a good requirement: a capacity measured 6 months ago against a model that has since been replaced is not evidence about today's seat.

## Is each model given a unique hash identifier in the first blind round?

No mechanism exists. But you were right that the discussion happened, and my first answer to you understated it badly: I reported that no hash identifier exists and left the impression the idea was never settled. It was settled, by you, repeatedly, and it is a standing ruling that the code does not implement.

Your words on the 7th of October: "the only thing that should impact on capability is measured capability. A models name should have little to do with it, beyond recording this, as you have already proposed." The day before you pressed the same point 3 separate times, including "why should the schema, or capability fingerprints, or the ladder care about model names at all?" and "I don't get why a models name is so important? Yes we should record which models did what for sure." The project's own record of that ruling states what it governs: any ranking, routing, fingerprint or ladder decision. Record the name as provenance; decide on measurement.

So the hashed identifier you remember as the natural form is the natural implementation of your own ruling. It was never built.

**And the ruling is being violated in 6 live places.** Of the 10 declarations in the live runner's reach that key on a model's name, 6 decide capability or routing from that name: the frozen ranking of seats for falsifier work, the initial capability fingerprint, the per-model physical constants, the decomposition threshold, the context ceiling, and the mapping from a seat to the composer profile that carries its coherence budget. That is 60% on a 95 per cent interval from 31.2674% to 83.1820%. The remaining 4 are legitimate: display names, who is taking part, and the check that a reply came from the seat it claims.

The record also names one of the 6 specifically. On the 7th of October both free panel seats, independently and blind, declined to delete the frozen ranking of seats for falsifier work and both said that keeping it was weaker than your ruling. It is still there 9 days later, surviving as the incumbent rather than on its merits.

Your conclusion about the 5 contaminated fingerprints still holds, and now for a clearer reason. It holds because only the experiment name and the timestamp moved while the measured capacity is identical on both sides. What does not yet hold is the premise, because names are not provenance-only today: they are load-bearing in 6 places.

## Is adding, removing or changing a model trivial by design?

Partly. It will not break anything, and the model will be silently un-characterised. That is the honest answer, and the evidence is a model you added yourself.

The live runner's import closure spans 23 modules and contains 10 places that enumerate the roster. Four of those carry hand-tuned numbers for each model: an initial capability fingerprint, a decomposition threshold, a context ceiling, and a set of physical constants. Fable, added on the 20th of September, is present in 1 of those 4 and absent from the other 3.

Nothing crashed, because every read site supplies a generic fallback. So Fable has been running on a default capability fingerprint, a default decomposition threshold of 100,000 and a default context ceiling of 40,000, where the measured values for other seats differ substantially: the decomposition threshold alone ranges from 0 for DeepSeek to 200,000 for Gemini.

So the design objective is half met. The harness tolerates a new model, which is the hard part and is genuinely good. What it does not do is tell you the model is uncharacterised, or give you a procedure for characterising it. A new model today inherits the average of nothing.

And the root cause is the same one as the section above. These tables need a hand-written entry per model only because they are keyed by name. Under your ruling they would be keyed by measurement, and a new model would arrive with no entry because it has no measurements yet, which is the honest state rather than a silent default. Fable's 3 missing entries are a symptom, not a separate defect.

## Do the fixes show repeatability, and should they carry forward to live runs?

Yes to both, with one boundary that must be stated.

**Repeatability is demonstrated.** Across the 3 legs the harness identified the same 9 planted-defect subjects every time: 9 of 9 present in all 3 runs, 100% on a 95 per cent interval from 70.0855% to 100%, with none unique to any single leg. The finding counts varied widely, 22 then 19 then 39, but the defects found did not. That is the right form of repeatability for this question: the same target yields the same identified defects regardless of how many words each run produced getting there.

**The fixes should carry forward,** because the ones that landed are in machinery that does not care which model is in the seat. The convergence gate, the composer, the immune pipeline, the finding lifecycle, the report generator and the marker schema all behave identically whoever produces a finding.

**The boundary, and it is a real one.** Every per-model table is keyed by the real vendor name, and a simulated run dispatches the suffixed label, so none of the 6 seats matched any entry in any of the 4 tables. Every seat in all 3 legs therefore ran on identical generic defaults. The shakedown validated the seat-agnostic machinery thoroughly and validated nothing that depends on a model's individual capability, context budget or decomposition behaviour. Those remain untested until a live run exercises them, which is Stage 2's item 3.

That is not a reason to withhold the fixes. It is the reason the first live run still matters.

## What this adds to the work, and the 3 things that need your word

The approved work stands. These are new, arising from your questions, and I have not built them.

First, the per-experiment fingerprint reset you described. Reset, or recompute in the first blind round, with a switch for researchers who want accumulation across experiments.

Second, your ruling of the 7th of October needs implementing rather than deciding, since you have already given it 4 times. The work is to key capability and routing on measurement rather than on the name, in the 6 places listed above, with the hashed identifier carrying provenance. The honest question is not whether, but what the cold start does: with no measurements every model scores identically and something must break the tie. Any proposal has to say what the fallback is and how it retires itself once data exists, which is the condition the record already attaches to it.

Third, whether to consolidate the roster to a single declaration and add a characterisation procedure, so the next model added is not silently uncharacterised as Fable is now. The immediate repair is smaller: give Fable its 3 missing entries, or make the fallback announce itself.

Written under CDSFL note standard v1.7 (26 August 2026).
