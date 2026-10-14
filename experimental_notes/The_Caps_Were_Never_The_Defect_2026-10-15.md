# Your challenge was right on both counts, and the real defect is worse than the caps

2026-10-15, 00:25 BST. Branch sim/shakedown-2026-09-29.

## What You Asked

You asked whether the advice in the last turn pointed backwards, over ground already settled, on the question of lifting the character caps and of carrying a small overhead of possibly superfluous detail. And you said that as far as you recall, the caps only ever existed to avoid feeding a model more work than it could demonstrably handle, especially weaker models such as DeepSeek, with considerable machinery built around that principle, and that there was never an intent to apply the same reasoning to the core directives themselves.

Both points are correct. The second one is correct in a way that reframes the whole question, and it exposes something more serious than anything discussed last night.

## Your Recollection of the Intent is Confirmed By the Code'S Own Comments

The per model transform block in the composer carries this comment, written when it was built: these rules modify how directives are rendered, not what constraints are active, and the layer is a transformation operator rather than an additive constraint set. The per model budgets beside it are annotated exactly as you remember them, model by model: one handles dense instructions well, another needs tighter simpler prompts, and DeepSeek needs the simplest prompts.

So the design intent was an accommodation for what a model can cope with, expressed as a change in presentation. It was never a licence to withhold the specification. Your recollection matches the record, and the record sits in the composer's own documentation rather than in anybody's memory of a conversation.

## The Real Defect, and it is not the Cap

When the source text exceeds a model's cap, the composer calls a function whose own description says it renders the directive in minimal form while preserving all hard constraints. That description is false.

Measured using the project's own 2 predicates rather than any new one: the core formal directive splits into 136 blocks, of which the project's own classifier marks 22 as hard. The minimal rendering emits 5 behavioural lines. The 5 that survive are all conduct rules: push back on impossible requirements, default to the simplest sufficient solution, do not silently comply with tangential requests, end with a definitive stance, and communicate as you would with a serious engineering colleague.

What does not survive is the substance. Eight specific rules were probed, each confirmed present in the source and then looked for in the entire text any seat actually receives, which is 48,878 characters. All 8 are absent. That is 8 of 8, with a 95 percent confidence interval of 67.5592 to 100 percent, computed twice with 2 independent tools in agreement.

The 8 are these. The classification function that defines what makes a constraint hard. The precedence relation that orders hard constraints when they conflict. The corroboration model, which is the mathematical heart of the falsification claim. The requirements a convergence declaration must satisfy. And 4 integrity rules: do not read a scoring key or answer file, do not modify, weaken or skip a test to make it pass, do not terminate early to obtain a passing result, and the section heading those sit under, which is called Falsifier Integrity, Do Not Reach For The Answer.

So the models have never been told not to read the answer key. They have never been told not to weaken a test to make it pass. They have never been told what makes a constraint hard, or how to order hard constraints, or what a convergence declaration has to contain. Every experiment in the archive was run under those conditions.

## Why This Means Last Night'S Advice Pointed Backwards

Last night the recommendation was to decide whether to remove the caps, with a measurement to justify the removal. The panel had refused outright removal on the project's additive standard, which requires a committed measurement showing a replacement is better on a named property before anything is removed, and that refusal was passed on as the recommendation.

That framing was wrong in 2 ways.

First, the additive standard's removal clause protects a justified feature. These caps carry no justifying measurement at all. The budgets beside them say in their own comment that they are conservative defaults to be calibrated from experiment data, and that calibration never happened. The numbers are round. You put this more directly in your own words on the 14th of October: caps that nobody asked for, based purely on model names, are clearly nonsensical.

Second, and more importantly, the cap was never the defect. Removing it would deliver the full text, which would fix the symptom. But what is actually broken is the minimal rendering function itself, which promises to preserve all hard constraints and delivers under a quarter of them. Fixing that honours the intent you remember exactly: a weaker model still gets a simpler presentation, and it also gets every hard constraint. The cap can stay and do the job it was built for.

## What was and was not Already Settled

To be precise about your first question, because the record is mixed rather than one way.

On the overhead, you had already ruled. Your words on the 14th were that a 7 percent overhead of what may ultimately be useful context is not such a huge burden to carry, but that it should be measured. It was measured, and the measurement found the share is predicate dependent, spanning 1.2308 to 11.9579 percent by volume depending on how chatter is defined. So your judgement stands and the figure you were given was one point in a range.

On the caps themselves, you had not settled it, and you said so. Your own words on the 14th include the decision of whether the cap should be removed as something still to come after the panel review. So asking you was not backwards.

What was backwards was the framing: treating the cap as the decision to put to you, when the cap is doing roughly what you intended and the renderer beneath it is not.

## And one Consequence Worth Stating Plainly

With this finding, the question of which sections to cut becomes close to irrelevant, and that was already derivable from last night's arithmetic. Bringing the core file under even the most generous cap would require removing 56.8392 percent of it. The broadest definition of chatter removes 14.7970 percent. An automated theorem prover confirms no cut in the measured range can reach the threshold. So cutting was never going to deliver the specification, and now there is no need for it to: the renderer should carry the hard constraints whether the file is long or short.

## What Needs your Ruling

One item, and it is small.

Repair the minimal rendering so that it carries every block the project's own classifier marks as hard, and leave the caps in place to do what they were built for, which is presentation. This is additive, it needs no removal justification, it preserves the accommodation for weaker models that you designed, and it closes a confound that has sat under every experiment in the archive.

The alternative, which is to lift the caps and deliver the full text to every model, also closes the confound but discards the accommodation, and it is the option your own recollection says was never the intent.

Nothing has been implemented. The recommendation is the first option.

## On the Overnight Run

It remains ready and unchanged: 4 arms of 10 rounds, sandboxed, every seat a simulated stand in, no money. The honest position is that it should not start until the rendering repair is in, because otherwise it measures a harness whose models are not being told the rules they are judged by. That is a 1 function change rather than a redesign, and it can be done and tested before any run begins.

Written under CDSFL note standard v1.7 (26 August 2026).