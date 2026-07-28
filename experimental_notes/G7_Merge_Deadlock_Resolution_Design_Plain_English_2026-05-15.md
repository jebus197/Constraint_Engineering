# Merge-Deadlock Resolution — Design Note in Plain English

2026-05-15 03:18 BST

## What this note is

A design proposal for one of the three deferred items in the pre-launch plan — the rule the runner should follow when it can't decide whether a newly-reported finding is a duplicate of an existing one. The technical record carries the implementation surface, the regex changes, and the configuration knobs. This note explains what the problem is, why it has been deferred, and what the proposed rule looks like.

## What the problem is

When language models on the panel review the same piece of code, they often surface findings that look similar but aren't identical. Sometimes two findings describe the same underlying bug in different words. Sometimes they describe related-but-distinct bugs. The runner has to decide: are these two reports the same thing (in which case merge them) or different things (in which case keep them separate)?

For most cases the runner's automatic merge logic decides cleanly. But sometimes a new finding matches multiple existing entries plausibly — the description matches one, the proposed fix overlaps another, the target file is the same as a third. The algorithm has no principled way to choose, so it defers the decision. The finding sits unresolved.

In Experiment 40, this deferral happened at least eight times, including once with a finding that could have plausibly merged into twenty-one different existing entries. That's the post-mortem evidence the project was waiting for before designing the resolution rule.

## Why the rule has been deferred

The project's core methodology is Popperian falsification — rules should emerge from observed evidence, not be guessed in advance. The pre-launch plan specified that the merge-deadlock rule would only be designed once real evidence had accumulated. The thinking: if we guess a rule and pre-register it, we'll have built something to fit imaginary data; when real data arrives, the rule will be subtly wrong but already entrenched.

Experiment 40 produced the real data. The rule can now be designed against actual deadlock patterns rather than imagined ones.

## The founder's proposal

The founder noticed something during the 14 May post-mortem review: "Either an issue is a duplicate or it isn't. Either a merge is warranted, or it isn't. Where is the scope for debate?" The runner shouldn't be left helpless in front of a merge it can't decide. The project has a discipline for exactly this case — the compelled-convergence confer round, where models are required to converge on a single answer.

The founder's proposal: apply that same discipline to merge decisions. When the auto-merge can't decide, send the question to the panel. Five models, independent, single-answer-each. Aggregate.

That's the rule.

## How the rule would work

When a new finding arrives and the auto-merge can't uniquely place it among several plausible candidates, the runner does NOT immediately defer. Instead, it dispatches a small focused query to all five panel models. The query is short — it describes the new finding, lists the candidate canonical entries (with their descriptions), and asks one question: which canonical entry — if any — is the same root cause as the new finding?

Each model returns one answer: either "merge into canonical entry C001 (or C002, or C003)" or "keep distinct from all of them." Five answers come back. The runner aggregates.

If three or more of the five models agree on the same target, the runner merges into that target. If three or more say "keep distinct," the new finding becomes its own canonical entry. If the votes split — say, two for one target, two for another, one for keep-distinct — the runner stays with its original deferral. The finding remains unresolved; the panel will encounter it again next round and might converge then.

The first time a finding gets deferred, the runner just logs it and waits. Only when the SAME finding hits a second consecutive deferral does the arbitration dispatch fire. This avoids spending cost on transient deferrals that resolve naturally.

## What it costs

Each arbitration dispatch is roughly fifty cents of OpenRouter credit — five model queries, short prompt, short response. The dispatcher is capped at three arbitrations per round; if more than three findings need arbitration in one round, the rest wait until next round. So the per-round cost is bounded at about one dollar fifty, even in worst-case scenarios.

## What it does not cover

The merge-deadlock rule covers cases where the runner CAN find candidate matches but can't choose among them. It does not cover two related but distinct cases:

The first is when two domain specialists (mathematics, biology, statistics, etc.) return conflicting verdicts on the same finding. That's a different problem (which specialist's verdict wins?) and it doesn't surface until later in the experimental arc when multiple specialists co-rule on shared claims. The pre-launch plan tracks that one separately.

The second is the burst-mode case where the runner needs to override its normal convergence checks. That one is deliberately out of scope for the current fifteen-experiment arc.

## Why this is being written now rather than implemented

The Experiment 40 continuation run is currently underway with the seven other fixes from the post-mortem already folded in. Adding the merge-deadlock arbitration logic mid-run would risk compounding changes — if something looks unexpected in the continuation, it'd be hard to know whether the cause was one of the seven fixes or the new arbitration rule.

The cleaner sequence is: let the continuation run complete, examine how the now-active fixes (especially the Bugzilla loop and the gamma input fix) affect merge-deferral frequency, then implement the arbitration rule against that updated baseline. Some deferrals may resolve naturally once findings start transitioning to CLOSED; others will persist and become evidence for the arbitration logic.

## What to read next

The technical companion at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md` carries the file paths, the data structures, the configuration knobs, and the implementation surface for when this design gets built. The Experiment 40 continuation post-mortem (yet to be written) will record how the deferral pattern actually behaved with the new fixes in place — that's the data the implementation should be tested against.

## Next review trigger

After the Experiment 40 continuation run closes and the founder reviews the continuation's post-mortem. Decision at that point: proceed with implementation, adjust the proposed rule, or defer further pending more evidence.

Written under CDSFL note standard v1.2 (14 May 2026).
