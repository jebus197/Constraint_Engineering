# Experiment 40 Prelaunch Review, Round 1 of 3

20 April 2026.

## What this review was for

Before Experiment 40 is allowed to launch, a five model panel was asked to review the work closed in the past week. The review had three questions behind it. Is the closure work sound. Are any hidden problems left. And has anything important been missed.

The five models that answered were Codex, Gemini, Claude Opus, ChatGPT, and DeepSeek. Each one received the same briefing document of roughly 21,000 characters, and each one answered independently, without seeing the others' replies. The total review took about 18 minutes of wall time. Their full replies are saved in `bench/logs/confer_exp40_prelaunch_round1/`.

## Where the panel agreed

The panel was aligned on the most important calls.

All five said the mathematics verifier is currently broken and should be fixed before the experiment runs. It silently returns uncertain on every mathematical claim, so any mathematics that appeared in the experiment would go unchecked. Four of the five called this a hard blocker. The fifth called it urgent but pointed out that Experiment 40's target is a software module, so mathematics may not arise. Either way the fix goes first.

All five rejected an extra scoring formula that had been proposed in an earlier conference. The formula would have added a new continuous penalty on top of the project's existing penalty for models paraphrasing one another. The panel found four independent reasons to reject it, any one of which would have been enough on its own. Most tellingly, the model that originally proposed the formula retracted it in this round, on its own initiative. That is the rarest event in a panel review. It almost never happens.

All five agreed that the reference runner, version two, should be promoted to the default now. It has passed 1,250 tests. The version it replaces is frozen by founder directive. Holding a tested replacement back behind a frozen predecessor buys nothing.

All five agreed the panel should keep its current review format, where each model answers in isolation and the founder compares the answers. A small variant was suggested for the next experiment in the sequence, where each answer is challenged once by one other model before the founder sees it. That variant had four out of five support.

## Where the panel split

Three questions produced genuine disagreement.

The first was whether the mathematics verifier is the single thing standing between today and launch. Two models said yes, fix it and launch. Three said other items are equally urgent. The split was about priority, not about whether the verifier was broken.

The second was whether to turn on a runtime safety check inside the scoring equation today or wait. The check watches one specific piece of the equation. Today that piece is not yet connected, so the check has nothing to watch. Four models said wait until the connection is made, which is in a later experiment. One model wanted the check on today, so that when the connection is made the check is already in place. The founder holds the deciding vote.

The third was how to frame the ratio of correct answers to answered questions. This is the simplest of the three questions and it still produced a three way split. One camp said the ratio is already captured by the existing validity score. Another said the ratio should sit alongside, because it gives the founder an immediate ground truth number without having to read into the scoring equation. A third said the ratio is best kept as a diagnostic only.

## The three open questions

The briefing also put three open questions to the panel, the kind that do not have a clean answer yet.

The first asked whether the correctness ratio is redundant with the existing validity score. Opinions were mixed as above. The honest synthesis is that the two measure related but not identical things, and both should be kept, but only one should drive decisions. The validity score drives decisions. The ratio is for the founder's eye.

The second asked where the line sits between a model being genuinely novel and a model hallucinating. Four models said this cannot be derived from first principles. It must be fitted from real experimental data. One model offered a speculative formula and marked it speculative. This is the right answer. The experiment sequence will supply the data.

The third asked whether the framework is, in the end, just doing maths under a fancy label. This was the hardest question and the panel split three ways. One view said yes, at some level, everything is just maths and the framework is a systematic way of using it. A second view said the framework is meaningfully more than maths because of the way it chains tools from different domains together, so that a result from one specialist tool becomes the input to another. A third view said the question cannot be answered without a longer empirical record. All three positions are defensible. The experiment sequence is the arbiter, not the panel.

## What each model admitted it might have wrong

All five models wrote a short section admitting the weakest part of their own review. This is the Popperian discipline the project is built on. It is worth noting that it happened without being explicitly prompted.

Two admitted they might have been too harsh about an inactive part of the verification pipeline. One admitted that an arbitrary discount factor in its topology recommendation had no justification. One admitted that its proposed fix to the rejected formula was unlikely to save it. One admitted that rejecting a novel idea too fast is itself a failure mode. None of the admissions changed the top level recommendations. All of them raised the quality of the review.

## Decisions pending

Four decisions sit with the founder.

1. Promote reference runner version 2 to default. Unanimous recommendation.
2. Fix the mathematics verifier before Experiment 40 launches. Unanimous recommendation.
3. Decide whether to turn on the runtime safety check today or wait for the experiment that actually exercises it. Four to one recommendation to wait.
4. Decide whether to activate the physics, chemistry, and engineering parts of the verification pipeline before Experiment 40 runs. Not required for this experiment, because the target module is software. Can safely wait.

## Summary

The panel review came back clean. The five models converged on the important calls and split only on questions of priority and framing. No model produced a review that would block Experiment 40 on its own. The next two rounds of review, on the per domain configuration files and on the criteria for activating the three currently inactive verifier parts, are scheduled but have not yet been triggered.
