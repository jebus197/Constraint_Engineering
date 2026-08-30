# The Older Backlog: Two Decisions, Both Still Live

2026-08-30, 23:24 BST (UTC+1)

You asked for the older backlog in a separate document, and you asked me to confirm the items are still current first so that neither of us wastes time on questions you have already answered. I checked both against the code and the data before writing a word. Both are still live, and the numbers have not moved.

Neither blocks the next simulated run. Both affect how results from Bench Run 2 can be compared with the experiments already completed.


## Decision A. Finding Descriptions Are Being Cut Off, And Fixing It Breaks Comparability

What happens. When a model reports a defect, the runner stores a description of it. If the model's reply does not match the expected shape, the reply parser falls back to taking the first 200 characters of whatever was written. There is a second cut at 500 characters elsewhere.

The scale, re-measured today. Of 2,286 stored descriptions across the whole archive, 714 are exactly 200 characters long and 661 are exactly 500. Those are not natural lengths. They are the two cut points. Roughly 63 percent end mid-word. These figures are identical to the ones measured on 16 August, so nothing has drifted.

Why it has not simply been fixed. The cut is in the reply parser, at runner_core.py line 896. Changing it changes how every future run is read, in the middle of an experimental arc. Experiments 40 to 49 were recorded under the current behaviour. Experiments 50 and later would be recorded under the new one. Any measurement that depends on the text of a description would then not be comparable across that boundary.

What is honestly known about the harm, and what is not. A pooled statistical association between truncation and outcome looks strong, but it reverses when two of the experiments are examined separately. That is a well-known statistical trap, and it means a causal claim is not established. Do not let anyone tell you truncation has been shown to distort results. What does survive scrutiny is narrower: the identifying signatures derived from descriptions are measurably shorter, and 15 of 318 comparison pairs sit exactly on the decision threshold, where a few missing words could tip them either way.

Your options.

Option 1. Fix it now, before Bench Run 2. Comparability breaks at a known, documented line, and you carry that caveat in the paper. Bench Run 2 gets full descriptions.

Option 2. Leave it until after Bench Run 2. Everything stays comparable, and Bench Run 2 inherits the truncation.

Option 3. Fix it and re-derive the affected measures for the earlier experiments from the stored raw replies, if those replies still hold the full text. I have not verified that they do. If you want this option, say so and I will check before you commit to it.

My recommendation is option 1, with the caveat written down. Bench Run 2 is the run whose findings are meant to be read by people outside this project, and a description that stops mid-word is the first thing an outside reader will notice.


## Decision B. A Quarter Of The Similarity Data Was Never Adjudicated

What happens. When two findings look like they might describe the same defect, the similarity function scores how alike they are. Pairs scoring above a high threshold are treated as the same; pairs below a low one are treated as different. Pairs falling between the two thresholds were silently discarded from the measurement rather than being decided either way.

The scale, re-checked today. The extracted set of undecided pairs is still sitting unanswered on disk at 120,807 bytes. A separate file holds 133 pairs that were adjudicated by a mechanical method. The discarded band represents about 27 percent of the data, and it is the hard 27 percent, because those are precisely the pairs that are genuinely ambiguous.

Why it matters. Every stated operating point for the similarity measure is provisional until those pairs are decided. You cannot know how good the similarity function is from the easy cases alone.

Why it was not pre-answered for you. It was deliberately left unanswered so that the adjudication would not be contaminated by an assistant's guess. That decision stands and I am not proposing to overturn it.

Your options.

Option 1. Adjudicate them mechanically, using the same counterfactual-repair method already applied to the 133 pairs. Zero cost, no model dispatch, and consistent with what was done before.

Option 2. Adjudicate them by human judgement, which is you, and which is a real time cost on 120,807 bytes of pairs.

Option 3. Adjudicate a random sample large enough to bound the answer statistically, and state the bound rather than the exact figure.

My recommendation is option 3, then option 1 for the remainder if the sample shows the mechanical method agreeing with you. That gets a defensible number without spending your evening on it.


## What I Have Already Done, So You Do Not Re-Decide It

Both of tonight's rulings are applied and tested. The review sandbox no longer refuses honest work, using the approach that widens no safety boundary. The check that could silently reverse a correct verdict is now behind the switch whose name always implied it, and everything else it reports still reaches a human.

Tool use is now enabled by default everywhere rather than riding on a separate switch, which it should never have done. One exception remains and it is recorded rather than hidden: of the six panel models, five can run code and Gemini cannot, because that route has no mechanism for it at all. It is booked on the runway, a test holds it so it cannot be forgotten, and a live run will now say so in its own log.

The test suite reports 4581 passed, 0 failed and 0 skipped.


Written under CDSFL note standard v1.7 (26 August 2026).