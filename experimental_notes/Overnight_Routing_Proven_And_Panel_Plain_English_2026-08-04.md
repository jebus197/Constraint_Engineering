# What was done while you slept, and what the panel said

2026-08-04 01:16 BST


## The one number that mattered

The routing repair works. Six of eight findings resolved, against a measured baseline of zero out of twenty five.

That baseline is not an estimate. It is what both earlier attempts at the control run actually produced: every escalated finding locked as impossible, twenty five times, zero resolutions. The same findings were put back through the repaired code and six of them resolved. Four of the five panel models did the resolving.

Two independent statistical routes agree that this is not chance. A Fisher exact test gives a probability of two and a half in one hundred thousand. A binomial test against the most generous reading of the baseline gives seven in one hundred thousand, and an exact arbitrary precision calculation confirms that second figure to six significant digits.

This was the question the control restart hung on. It cost eleven model calls, between one pound forty and two pounds thirty.

Two findings remain unresolvable, which is the honest expected residue. Some findings genuinely have nothing runnable to demonstrate.


## On the money, because the wording earlier was bad

Nothing was burned. The eighty two dollar figure was a projection of what a FUTURE run might waste, on a change that was then investigated and NOT made. Total spend for the whole night, including the panel review, is under five pounds.

The investigation is worth repeating because it went the other way to expectation. The proposal was to stop the system re-trying findings whose resolution ladder had already failed, on the grounds that those retries cannot succeed. Before changing anything, every archived run was checked: thirty six findings had been locked that way, and six of them were later rescued on a repeat attempt. Seventeen percent. The retry is the recovery mechanism. The change would have saved money by deleting something that works one time in six, so it was dropped and the claim was corrected in the record.


## The literature cell, answered properly

The question was whether it demonstrably feeds real material back to the panel, confirmable irrefutably. The honest answer had three parts and two are now closed.

The search text was broken in a way that was four times worse than reported, and not what it looked like. It was not that six percent of findings have nothing searchable in them. Measured across two hundred and seventy four real findings from the archive, nineteen of them produced a fixed meaningless phrase, and every single one began with the words verdict, confirm, and a finding number. Those two words sat on a list of machinery labels, so the stripper discarded everything after them, which was the entire description. A perfectly good sentence went in and nothing came out.

The distinction that fixes it is what a label introduces. A falsifier label is followed by program code and must stay on the machinery list. A verdict label is followed by the reasoning, which is exactly what the search wants. Re-measured after the fix: down from six point nine percent to one point five. The queries are now real, things like timeout parameter, partial rollout, race conditions.

The remaining one and a half percent now return nothing and are skipped rather than searching a phrase unrelated to the finding. A search that cannot be about the finding is worse than no search: it wastes a call and risks handing the panel a paper about something else, which the relevance judge may then over-rate. That removed a guarantee, so the skip is tested and, importantly, counted. A silent skip looks identical to a search that found nothing, and this project has already lost a convergence to that exact kind of invisible failure.

The relevance reader has now been run live for the first time. Ten seconds, a genuine five hundred word brief that correctly identifies the paper's bearing on the target, and it passes the guard that refuses briefs judged by the mechanical fallback. A worry that a fallback brief might slip past that guard was checked and is unfounded.

What remains before the cell can influence a run is the configuration switch alone. Every component beneath it is now proven live and separately. Holding the switch is a scheduling decision, not a readiness one: the chemistry and engineering runs happened with the cell observing only, so turning it on mid-arc would confound the capstone's four-way comparison.


## The panel on your first ruling

Five models answered. There is real disagreement, which is the point of running it without forcing agreement, and one measurement that may reframe the question entirely.

Three of the five say no reliable method exists with current signals. Their shared reasoning is that sameness of defect is not a property of the text at all. It is a causal question: if one defect were removed and everything else left alone, would the other still fail? Descriptions, similarity scores and word overlap are all correlates of that counterfactual, and each fails where its correlation is weakest. All three say the honest fallback, keeping the rule and stating the limitation plainly, is defensible for a research release.

Two say a method does exist, and both point at the same thing your question three pointed at: the runnable test, not the prose. One proposes generating a small set of deliberate mutations of the target location, running both tests against each, and comparing the resulting pass and fail signatures. Two findings are the same defect if their tests respond identically across the mutations. The other goes further and says defect identity is only observable under intervention: two findings are the same defect if and only if a repair that removes one removes the other.

So the split is not two camps talking past each other. All five agree the prose is a dead end. The disagreement is whether the counterfactual can be approximated cheaply enough to be practical, and the two who say yes both propose approximating it by running things rather than by comparing words.


## The measurement that may change the question

One model did something none of the others did, and none of us had done: it measured how big the blind spot actually is.

The stopping rule counts new critical findings at previously unmentioned locations. So the size of the gap depends on what fraction of critical findings arrive at a location already flagged. That fraction had never been calculated.

It reports roughly sixty four percent. An independent recalculation here, using a symbol set derived separately, gives fifty nine percent. The two do not match exactly and neither is confirmed, because the runs do not record the symbol set they used, which is itself a gap worth closing. But two independent derivations agree on the direction and the rough magnitude.

If that holds, the blind spot is not an edge case. It covers the majority of critical findings. That does not by itself mean the rule is wrong, because treating a re-find at a known location as not-new is exactly what the rule is for. What it means is that the question the panel was asked, whether those are genuine second defects or merely re-finds, applies to most of the evidence rather than a corner of it.

That is the single highest value thing to settle, and it should be settled with a properly recorded symbol set rather than two reconstructions.


## Also done

Your third ruling is built. A serious finding is still never cleared automatically, and the rule behind that is untouched. What changed is that when the computation runs and returns an answer, that answer is no longer thrown away: the verdict, the model that produced it, and the fix the panel devised are recorded and travel to you together. Eleven tests, several of which pin the things that must not change.

The control document's fingerprint was stale and is corrected. Six glossary entries and a new architecture section were written for a week of undocumented concepts. The full test suite stands at two thousand five hundred and thirty eight passing, none failing, offline.

One item was deliberately left alone. The log that writes into the run archive when it should not needs the default inverted, and inverting it wrongly means a paid run's data silently goes to a temporary folder and is lost. Thirteen harmless lines against that risk, at one in the morning, before a paid run, is the wrong trade.


## Waiting for you

The false confirmation hole, which touches the core verification rule and deserves daylight and your ruling.

Your first ruling, now with five panel answers and a measurement that may reframe it.

And whether to restart the control, which the evidence now supports much more strongly than it did last night.

Written under CDSFL note standard v1.2, 14 May 2026.
