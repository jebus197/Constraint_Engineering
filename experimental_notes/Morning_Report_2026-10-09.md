# Morning report, 9 October 2026


2026-10-09, 05:18 BST

## The short version

The research you asked for is done: 13 agents, 631 tool calls, 126 citations checked by adversarial verifiers, 41 minutes. The answer to your question "are we attempting to reinvent the wheel?" is yes, substantially, and every mechanism you proposed has a published name with results you do not have. But the research that establishes this came back sound only WITH CORRECTIONS on all 6 of its dimensions, including 3 fabricated citations, so the figures below are restricted to what was re-derived independently rather than what the research reported.

And one result vindicates you against a number in yesterday's report that you were right to challenge.

## Your 2 or 3 attempts instinct was right, and the 300 was my error

You said 300 attempts for a single model was clearly far too much and asked whether anyone was checking that these numbers make practical sense. The number was not wrong but it was useless, because it was quoted without the capability gap that determines it.

The attempts needed to rank 2 models depends almost entirely on the GAP between their success proportions. Computed exactly in symbolic algebra and confirmed against an exact binomial search: at a gap of 0.40 it takes 7 attempts each to get the ordering right 95 percent of the time. At 0.30 it takes 14. At 0.20 it takes 32. The 300 figure belongs to a gap of 0.05, where the true requirement is 540.

So your instinct that a very hard problem should be the first thing a model sees is doing real statistical work, and it is not a crude idea. Choosing a hard problem is choosing a problem that MAXIMISES the gap, and maximising the gap is exactly how the established method selects its next question. In the adaptive-testing literature this is Fisher-information item selection, and it is 55 years old. With a well-chosen first problem, 7 attempts is enough, not 300.

What is also true, and is the limit on the idea: 1 attempt orders a model with a 0.70 success proportion above one at 0.50 with probability 3 over 5, which is 0.600, barely better than a coin. Three attempts gives 1371 over 2000, which is 0.6855. Both figures are exact. So 2 or 3 attempts cannot rank a roster on a problem where the models are close. It can rank them on a problem where they are far apart, which is what your "very hard" does.

## The knockout bracket does not work, and this is a theorem rather than a preference

Your second idea was the cup draw: pair models at random from a bag, winners advance, repeat until the strongest meet. The standard way to turn pairwise results into a ranking is the Bradley-Terry model, and Ford proved in 1957 that its estimate exists and is unique only if the win graph is strongly connected, meaning that for every way of splitting the participants into 2 groups, somebody in one group has beaten somebody in the other.

A knockout bracket on n participants produces exactly n minus 1 matches and can never contain a cycle, because nobody ever beats a participant who beat them. I checked this directly at 4, 8 and 16 participants: in every case the graph is acyclic and not strongly connected. So the bracket does not produce a ranking that is hard to estimate. It produces one where the standard estimator is undefined. An 8-participant round robin produces 28 matches and is strongly connected.

A knockout also removes a participant on a single result, which contradicts your own rule that no model is ever permanently set aside.

## What the literature already has, by name

Your calibration task has at least 3 published forms. In volunteer computing it is the BOINC probe job: a task run once on every participant, with the graded result stored in the participant's record and read by the router. In cluster computing it is periodic benchmarking, where each node measures itself and publishes the figure. In testing theory it is computerised adaptive testing, which bins an item bank into difficulty strata and selects the next item by information gain, published in that form in 1973.

Your recursive structure, assess the best and give the rest an easier problem, is Sequential Halving, published 2013. One correction the verifiers caught, and it matters: Sequential Halving holds the question FIXED and varies only how many attempts it spends, precisely so that a proportion of successes measured in round 2 means the same as one measured in round 1. Your version varies the question. That is a real difference and it is not obviously in your favour: 8 successes out of 10 on an easy problem and 8 out of 10 on a hard one are the same arithmetic and not the same evidence.

## Your lock-in worry has an established answer

You asked what happens when the field improves 10 or 20 fold and a model that earned a top place is suddenly outmatched. This is the oldest known problem in rating systems and it has 2 standard answers. The first is to carry an explicit uncertainty alongside every rating, which grows when a participant is idle and shrinks when it competes, so a stale rating is automatically distrusted. The second is to make the weight of history sublinear, so that a long record cannot make a participant unovertakeable.

A continuous rating with an uncertainty attached does everything a league table does and does not lock anyone in. On the evidence, discrete leagues are overhead. That supports your own instinct, stated yesterday, that there should be no distinction between models other than a ranking number.

## The archaeology: what the project already decided, and it contradicts the premise

You asked whether the early discussions of distributed and peer-to-peer operation went anywhere. They exist in 2 waves and almost nothing was built.

The early wave is March and April 2026. A note of 19 March established that "distributed compute" in this project means epistemic diversity rather than network distribution. An architecture note of 3 April set out a shared workspace where all participants read and write directly. The clearest statement of the peer-to-peer trajectory sits in a file on your Desktop dated 10 April that was never copied into the repository, which is itself worth fixing.

The substantive artefact is a specification of 26 August 2026, 141 lines, which names Folding@home, Rosetta@home, SETI@home and Einstein@home in its opening paragraph and addresses your framing directly. Its own closing line reads "Nothing described here has been built."

And it already answered the premise behind your 700-model question, in the opposite direction to the one you were hoping for. Its finding: a distributed version of this project that recruits 50 architectures to review one artefact is a distributed system doing the work of about 4. Its recommendation: panel size fixed at 4 to 6, not scaled. That arithmetic is not an opinion; it is re-derived from the live archive by a guard of 10 tests that passes today. The reason is the project's own coverage model: when the correlation between architectures reaches 1, adding architectures adds nothing.

So the volunteer-computing shape does not transfer. Those projects solve the problem of many untrusted machines doing identical work, and they resolve disagreement by majority. This project's entire premise is that disagreement is the signal, and the specification says so explicitly: where volunteer computing selects a canonical result by quorum, this project has no equivalent step.

## What was actually built, and the one piece that is genuinely useful

Nothing for peer-to-peer operation. A search of the whole tree for the obvious terms returns networking code in exactly 4 files, and all 4 use network calls to FORBID network access during tests. This project runs as a single process on one machine talking to vendor endpoints.

Three things do exist. A topology switch offering a star or a relay, where the relay is still a central relay and therefore still a coordinator. An allocation module that was shelved in August by your own ruling, having never run outside its own tests. And one genuinely valuable component dated 5 April: a verification chain providing content-addressed digests, detached signatures, and Merkle trees with inclusion proofs. That is real substrate for a system with no central authority, it is live, and it is tested.

The single clearest blocker to a coordinator-free mode is the finding registry's identity scheme. Findings are named by a counter, so 2 peers would both mint the same identifier and there is no rule for merging them. The fix is already in the building: content-addressed identity, which the verification chain already knows how to compute.

Where it sits on the roadmap: deferred past the second bench run, and you have already seen and approved that. It is item 36 on the list of decisions put to you on 6 September, recorded with the recommendation to defer, and it is one of 11 items declared excluded from the master task list. Nothing places peer-to-peer operation on a dated schedule.

## Your season proposal, measured

You suggested that one round of an experiment could serve as a season, with rankings set from the first round and then fixed for the rest of the run. The first half does not survive measurement. A model accumulates a median of 1 decidable observation per round, and 53.40 percent of the 470 model-rounds in the archive yield 0 or 1. No ranking can move on that. Per experiment the mean is 9.7193 observations, 95 percent interval 7.48 to 12.22, confirmed by 2 independent interval methods.

The second half of your proposal is right, and for a stronger reason than you gave. Rankings should indeed be fixed for the duration of a run, not because the first round settles them but because no single round comes close. The ranking has to be carried into the experiment from evidence accumulated across previous ones. That is a persistent rating, which is what the rating literature provides, and it is not a league table recomputed each round.

## Your 2 questions about my own decision list

You asked what an error convention is. It is this. To say a model belongs in a higher band than another, you set a threshold and accept 2 kinds of mistake: calling a good model bad, and calling a bad model good. You can budget 5 percent for each mistake separately, or 5 percent shared between them. The 2 choices give different answers for how many bands the evidence supports, and at 2000 observations the difference is 13 bands against 11. Nothing is measured here; it is a choice about which mistake you mind more, and I should have stated which one the panel was working under rather than asking them to reconcile a difference I had created.

You asked whether an anchor set is better than your own idea of fixing a difficulty measure at the start of an experiment and holding it. They are the same idea, and yours is the better statement of it, with one addition. The reason something like it is needed is that a model getting worse and the work getting harder are mathematically indistinguishable: only the difference between a model's capability and a problem's difficulty affects any outcome, so the 2 explanations predict identical results. The way out is a small set of problems whose difficulty is fixed from outside and re-run in every window, which anchors the scale. Your version fixes it once at the start. That works while the task stream does not drift, and re-running the anchor each window is what detects drift when it happens.

And you asked how something can be repaired that cannot yet be measured. It can, because what needs repairing is the measuring instrument rather than domain-specific strength itself. Findings in the statistics domain reach a verdict 0.2342 of the time against 0.5268 for software. That gap is itself measurable, and closing it is an engineering task: find why the verdict machinery resolves those findings to a terminal state without a confirm or refute. Once that gap closes, domain-specific strength becomes measurable. Repairing the instrument comes first and does not depend on the strengths it will later measure.

## What I got wrong yesterday, for the record

The 300 figure was quoted without the gap that determines it, which made it read as 300 attempts at one problem when it was 300 accumulated observations. You were right to challenge it.

There was never a recommendation of 3000 leagues anywhere in the record. The largest number of bands any seat proposed is 22, and the working range was 2 to 14. Every appearance of 2000 in the record is a number of observations, not a number of bands. The figure you remembered was a sample size.

And the brief I wrote failed to state which error convention applied, which manufactured a disagreement between the 2 seats that did not exist.

## The 5 decisions, unchanged and still yours

1. The 2 gate properties: a verdict must be reproducible from the record, and must depend only on how many attempts succeeded and how many were made. Both seats recommend both and the measured price is 0 additional attempts.

2. Which error convention, as explained above. A choice about which mistake you mind more.

3. One false-alarm proportion for relegation, for example 0.05 on a stable model. Both decision thresholds then follow from it.

4. Whether a set of externally fixed problems is re-run every window, or fixed once at the start as you proposed. Yours works while the task stream is stable.

5. Whether to repair the verdict gap between domains, which is a precondition for measuring anything about domain-specific strength.

## Nothing is wired

None of the ranking, relegation or division work is connected to live code. Not one live module imports any of it. The main branch is untouched. Of the 3 changes made to live code yesterday, 2 default to the previous behaviour exactly and the third is your own ruling of 6 October. There were 0 paid dispatches across all 4 dispatches of the panel.

Written under CDSFL note standard v1.7, 26th of August 2026.
