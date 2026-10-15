# The last measurement closed, and a guard was switched off everywhere except one kind of experiment

2026-10-15 23:52 BST

## The short version

The 12th and last of the programme's measurements now has an answer, so every one of them carries a result. The study has not been closed, because that is the founder's call and because the separate success criterion of 3 consecutive clean convergences is still in progress.

The third and final leg of the shakedown ran through the session. It declined to converge once, at round 3, and that refusal was checked and is correct.

Two faults were found in the part of the harness that decides which checking tool a finding should go to. One is fixed. The other is measured, is happening in the final leg as it runs, and needs a ruling, because fixing it would relax a guard rather than add one.

## Arm 5: the rulebook reached none of the model at the old commit, and all of it now

A copy of the project as it stood on the 6th of September was created, and the same experiment was launched inside it. While it was running, the actual instruction text that one model received was captured out of the running system and decoded.

Against the 22 blocks of the rulebook that are marked as mandatory, that text carried 0 of them. Today's version carries all 22. That is the clearest single result of the whole programme: before the repair, the project's own rules were not reaching the models at all.

**The second half of the comparison needed no second run**, which saved about 85 minutes of the founder's machine. The method used this morning to reconstruct what the old version would have sent was checked against what the old version actually did send, and the two agree. A measuring instrument that agrees with reality where reality is available can be trusted where it is not.

**The other half of arm 5 cannot be answered between these 2 versions, and the reason is itself useful.** The old copy predates a repair made on the 3rd of October. Without that repair, a model that writes a filename in the ordinary way, wrapped in backticks, has the backtick swallowed into the filename, and the harness then reports the file as missing and throws the finding away. This was watched happening: 6 of the first 7 findings were discarded, every one of them naming a file that exists in both versions. A run was already stopped for exactly this on the 3rd of October. A run whose findings are being thrown away cannot be compared on how many findings it produced.

The old copy also answers every seat with a weaker stand-in model than today's version does, so model strength and the rulebook repair moved together. The baseline run was stopped once the useful measurement was in hand, and everything it produced is preserved.

**One fault in arm 5's own design was found.** It says the two halves use the same target and the same random seed. There is no seed anywhere in either version. So they could never have been matched that way, and with a single run each, ordinary run-to-run variation cannot be told apart from a real difference. This does not affect the result above, which does not depend on chance.

## The classifier: 3 jobs, 1 of them restricted, and restricted the wrong way round

The founder asked whether restricting the classifier to code questions risks making it useless in experiments that have nothing to do with code, and asked for a fix.

The first thing the measurement shows is that the premise needs correcting, and the wording that produced it was mine. That model has 3 jobs in the harness and only 1 of them is restricted by subject at all. The other 2, removing duplicate findings and reading literature, run in every kind of experiment. Even the restricted job is not switched off outside software; it is demoted, so it can still act when it is confident. It made 22 judgements in a mathematics experiment.

**The first fault, now fixed.** There is a protection that stops a finding about code being moved onto a checking tool that cannot read code. Its written reasoning is entirely about the kind of claim, and nothing in it is about the subject of the experiment. But it had been wired to fire only in software experiments. So in every other kind, a real code finding could be moved off the only path that can check it. Measured across 220 archived logs: 10 findings, 8 of them from the very experiment the protection's own notes cite as the reason it exists. It now works in every subject, and deliberately breaking it again turns the new tests red.

**The second fault, measured and deliberately not fixed.** Trying to break the first fix uncovered it. A separate protection stops a finding labelled mathematical from being relabelled outside software, at any confidence, including when the proposed new label is a code label. But a code label is exactly the one destination that CAN check a claim about code. So the single most valuable move this model can make, spotting that something filed as mathematics is really a code defect, is only available in software experiments. Across the archive, more than 3 in 4 of everything that protection refused was an attempt to make precisely that move: 327 occasions across 32 runs.

**And it is happening in the final leg right now.** 5 of its 12 refusals so far were that move, at confidences up to 0.92, on a target that is written prose with real code embedded in it. This is the exact situation the founder described.

The repair is a single condition. Because it loosens a guard rather than adding one, the project's own standard requires his ruling and a named measured reason rather than a judgement. A test now records today's behaviour and will invert when he rules.

## The terminology problem has had its cause fixed, not its symptom recorded

The founder asked whether recording a lesson is the same as fixing what caused it. It is not. There is now a mechanical check that refuses a note using an invented multi-word technical term, meaning one that appears nowhere he could look it up.

Of the 4 terms he challenged, 3 appeared nowhere in the project at all and 1 was genuine but undefined, so both halves are treated: invented terms are refused, and genuine undefined terms get written into the glossary. 4 terms were added there.

**The check had to be defended 4 times against itself.** Its own explaining comment used all 4 invented terms, which made it accept them. So did the scripts written in the same hour. So did its own test examples. And the fourth only appeared once it was working: writing in the glossary that something had been called `confinement guard`, which is not its name, made that phrase acceptable. A line can now mark itself as quoting an invented term, which is the only way a glossary can say "this is not what it is called" without making it what it is called.

**It caught its author within the hour.** Writing this note, it refused a term and sent me to the code, where the real name turned out to be different. It also accepts the project's own spelling of another term while refusing my shorthand for it, which is the naming rule enforced by machine instead of remembered.

Run against the 2 files he annotated today, it flags both of the invented terms he challenged, and 3 more he did not. There is a backlog of 869 instances across 263 of 524 notes, mostly real mechanisms that were simply never written down. How to clear that is a decision for him; the check is a ratchet, so new notes are clean and the recorded figure can only fall.

## The 7 test failures awaiting his ruling are fixed, and one test is now stronger than before

On his instruction to make each test work out its baseline from the archive rather than pin a number. All 259 tests in those files pass.

The clearest case is the immune memory, which had learned from the 2 runs and so no longer matched a hard-coded count of 3 experiments. The set of experiments is now worked out from the memory's own records, and replaying all of them reproduces the stored result exactly. A pinned threshold figure was replaced by the 2 claims the test's own description actually makes, and one of those is a stronger check than the number it replaced: it would notice the threshold climbing high enough to start rejecting good fixes, which the fixed number could not.

He was warned that deriving baselines weakens these as early-warning tests. On this one it strengthens it. On the other 2 the only thing lost is the ability to notice that something was added, which every successful run does by design.

## Two more faults: one fixed, one partly wrong

**The shortened version of the instructions was deleting the code it was asking models to review.** On a sample holding 20 similar functions, the full version passes all 20 through; the shortened version passed 1, with all indentation removed. That is 19 of 20 functions deleted from a code review, and the shortened version is what 4 of the 5 models receive. The function's own description promises that only presentation changes, and for code that promise is false, because indentation is part of the meaning. Content whose layout is part of its meaning now passes through untouched. A plausible version of this fix would have changed nothing, because the code is not wrapped in the usual markers; that was proved by breaking it deliberately.

**A claim recorded last night turns out to be partly wrong.** It held that a model's demonstrated capacity is used as a limit, so the recorded figure can never grow. Measured across the full history of those records, it has grown 3 times for the simulated seats and never fallen. A second guess of mine, that the live harness never writes that figure, was also wrong. What remains is sharper: 4 of the 5 paid models carry exactly the same capacity number, to the character, unchanged for 185 days, and a separate size limit means no ordinary run can ever test or correct it. That number is already blamed in the project's own notes for one measured collapse in quality.

## Where this leaves the runway, and the thing that has waited longest

Tonight's work was groundwork and checking. It did not advance the numbered runway stages, and should not be counted as if it had.

The nearest thing that can actually be done costs no money and no model time: replaying the earlier experiments through the repaired accounting, which is the exit test for the first stage, and the tool for it already exists.

**The real delay is not engineering.** 6 of the 7 remaining experiments in the arc are built and have never been run, and all 6 wait on a single decision: whether 3 of them can still be reported as blind exams, given that their articles and answer keys were briefly on a public branch. That decision was asked for on the 8th of August and is 68 days outstanding. Of the 555 comments he has recorded since then, none addresses it. Nothing else can be substituted, because this is the remaining experimental arc, and the final capstone has not been built.

## What needs a decision from him

The mathematical guard and the move it blocks, with 327 recorded occasions before leg 3 and 337 after it, 5 of them in leg 3 itself. The blind-exam question, 68 days old, blocking 6 experiments. The shared capacity number on the 4 paid models, and whether the size limit should move. The 869-instance terminology backlog. Whether to close the programme of study now that every measurement has an answer. And one change to how finding names are recorded, which is the only honest route to a fully green test board.

Written under CDSFL note standard v1.7 (26 August 2026).
