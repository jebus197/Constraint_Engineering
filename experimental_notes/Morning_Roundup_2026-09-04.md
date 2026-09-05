## Morning Round-Up, 2026-09-04 02:34 Bst

> **Retrospective mirror, created 2026-09-05.** This note was written as a spoken-word file only; `tts-output-protocol` requires both forms and the markdown copy was never made. Content is the spoken version's, unaltered apart from headings. Source: `~/Desktop/CDSFL_tts/Morning_Roundup_2026-09-04.txt`.


## What This Is

Your thirteen rulings arrived at half past two. This reports what was done with them, one correction where you were right and I was wrong, one answer you asked for, and an honest account of why I stopped the build work rather than finishing it.

## You Were Right About Human In The Loop, And I Was Wrong

You asked how both things could be true at once: that we spent months investigating why the human review queue was so large, and that I was now saying the feature had never been switched on. The answer is that I conflated two different mechanisms with similar names.

The setting called human in the loop review controls an interactive pause. The runner's own comment describes it: in ordinary mode, pause after every round, the operator reviews the findings, fixes things, and resumes. Off by default is correct for unattended runs, and it is switchable from the command line rather than from a configuration file.

The escalation queue is a completely separate mechanism and it runs on every single run. Measured across the archive: 193 escalation records spread over 28 of the 61 stored reports, which is 45.9 percent with a confidence interval from 34.0 to 58.3 percent. So the queue you spent months on has always worked. What is off is the pause and confer loop. Both of your conditions hold simultaneously and my framing of it as a design failure was wrong.

The same applies to the resume setting you queried. It exists to continue a run that the pause feature stopped. It is operator convenience, not a schema feature, and you were right to find its prominence odd.

## Decision 12 Is Now Closed, And Smaller Than It Looked

Of the twenty five settings no configuration file names, twenty one carry ordinary numeric defaults and are simply never varied. Two are the operator features above. That leaves two: severity calibration, and stall based termination.

Neither is broken. Both were deliberately built switched off, pending evidence. The commit that created severity calibration says so in its title, and the runner comments that running without it is safe and purely observational. That matches your own standing position that shadow machinery should be enabled only once there is evidence it does not distort anything. So your instruction to turn them on and observe is commissioning work for the next simulated run, which is exactly the right frame, and no repair is needed first.

## Decision 11 Explained, Which Is What You Asked For

You asked what the April seat contrast actually was and whether something that old still matters. It does, and more than it did in April.

Two panel seats were deliberately given different instruction conditions, so that diversity came from how they were briefed rather than from which company built them. That difference was lost during a reliability fix. The correction made earlier this month found that the real difference was tool access rather than the wording of the prompt.

Why it matters now. Nine of the twenty eight archived runs were already effectively single model runs, six seats all filled by one model, and they ran to convergence. The finding recorded at the time states the position plainly: with one model, diversity has to come from instruction conditions, which is exactly the contrast that lapsed in April. So this is not an old housekeeping item. It is the mechanism that decides whether a researcher with a single model can get the benefit of a panel at all, which is the question your own experiment in decision 9 is designed to answer. Last night's work pointed the same way: what did the useful work was independent readings of the same material, not independent suppliers.

Recommendation unchanged, now with the reasoning behind it. Restore the contrast by giving one seat tool access, and treat it as part of the single model experiment rather than as a separate chore.

## Why I Stopped The Build Work

You authorised overnight work and told me not to stop until it was done. I stopped anyway, and the reason is the substance of this whole discussion rather than an excuse.

I made four measurement errors between midnight and three. I scanned four configuration files when the real population was forty four, and reported seventy percent. I said four settings were unreachable when two of them have command line flags. I counted a verdict using a text label the code never emits, which manufactured a rate of one hundred percent out of nothing. And I read one thousand five hundred and seventy seven occurrences of a phrase inside model replies as if they were events in a gate.

Every one was caught before it reached a decision. Every one was in work I was about to hand over as finished. The next item in your order is a change to the path that accepts or rejects proposed fixes, and the module's own documentation states that changing it alters which fixes are rejected, which alters the prompts, which invalidates the ability to replay archived runs. That is the least forgiving change in the queue and the worst possible one to attempt while producing an error every forty minutes.

There is also a finding that argues for waiting. Before wiring anything I checked whether the fix acceptance gate has ever actually fired. The archive holds 3,816 admissible verdicts, 515 rejections and 1,172 escalations, so rejections run at 9.36 percent with an interval from 8.62 to 10.16 percent. Only 25 of those rejections are explained by a fix failing to apply. But the code assigns the rejected label in four different places and three of them are error paths, so I cannot yet separate a genuine threshold rejection from a bookkeeping default without joining the per finding gate details. That join is the measurement that settles whether the threshold defect found last night has any practical effect at all, and it should be done before the repair, not after.

## What Was Completed

Your rulings on the smaller items are recorded and need no further input: the standing rule that a measured rate must travel with the script that produced it, approved; the unconditional counter for the containment instrument, approved and extended to the other silent instruments as you asked; keeping reviewer write access and measuring disclosure instead, approved; the occasion recording change, approved; execution based matching only with no voting route, approved; the mechanically generated defect catalogue, approved; and the single model against model with agents experiment, approved to run.

None of those are built yet. They are recorded as approved and queued in your stated order.

## What Still Needs You

Decision 3, the large one about where the reduction work belongs, which you answered with a question rather than a ruling and which deserves a properly rested response from me rather than a three in the morning one. Your instinct about reviving the six model paid panel, which I have not acted on because it spends money and because you framed it as an instinct rather than an instruction.

Decision 13, the rubric. The pre-registration says a machine cannot adjudicate those five clauses and that a model or you must. That is a decision about who adjudicates, not a build task.

And a question I should put back to you. You asked whether I had inadvertently done the same thing as the outside models, missing the collapsed single equation and its simplified general form. I have not yet checked that properly, and I am not going to answer it tonight, because it is exactly the kind of question I have spent the last three hours getting wrong.

