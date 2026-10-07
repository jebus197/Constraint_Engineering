# Why three attempts to fix the ladder each fixed only half of it

2026-10-07 14:45 BST

## The short version

When the project's falsification ladder cannot settle a finding with the model that raised it, it passes the finding to other models in turn. The question of what order to use has been answered three times, and each answer left an obvious objection standing. On 2026-10-07 the project's founder named the pattern: none of the three proposals had actually dissolved the tension.

He was right. The reason is that the ladder is making two decisions, not one, and they pull in opposite directions. No single ordering rule can be the best answer to both.

## The two decisions

**Which models get asked at all.** There is a hard limit of 2 attempts per finding. The ladder lists 5 models. So 3 of them are never consulted, whatever they might have contributed. Which 2 are chosen determines the chance that the finding goes unanswered altogether.

**In what order the chosen ones are asked.** Because the ladder stops at the first success, asking a cheap model first saves money whenever it succeeds.

The important structural fact is that these two quantities behave completely differently. The chance that nobody solves the problem depends only on *which* models were asked, not the sequence. The expected bill depends only on the *sequence*. Swapping two models around cannot change the first number at all, and cannot fail to change the second.

That was checked rather than asserted. Working through every one of the 120 possible orderings of 5 models, symbolic algebra confirmed the failure probability is identical in all of them. A separate constraint solver was asked to find any case where the cost rule gives the wrong answer and reported that none exists, in both directions. A third check generated 400 random scenarios and compared the rule against an exhaustive search of every ordering: the rule found the cheapest sequence 400 times out of 400.

## A concrete case

Imagine 3 models. Two cost nothing: one succeeds 5 percent of the time, the other 10 percent. The third costs 100 units and succeeds 80 percent of the time.

Choosing the pair that minimises cost means asking the 2 free models, and the finding then goes unanswered 85.5 percent of the time. Choosing the pair most likely to succeed means asking the better free model and the expensive one, and the finding goes unanswered 18 percent of the time. The cheap choice is 4.75 times worse at the job the ladder exists to do.

There is a second case worth noting. If every model under consideration is free, then every possible order costs exactly the same, namely nothing. Measured across all 6 orderings of 3 free models: 1 distinct cost. So among free models, asking which to try first is not a question with a wrong answer. It is a question with no content, and only the choice of models matters.

## What is actually configured today

Reading the live code rather than relying on memory: the 2 attempt limit is the built-in default, and not one of the 47 experiment configuration files changes it. The ladder holds 5 models. Routing is switched on in 23 of those 47 files, and in 22 of the 23 there are enough models on the roster for the order to make a difference. Exactly 1 of the 5 ladder positions is a free model. One of the project's 2 free models does not appear on the ladder at all, which is a fact for the founder to rule on rather than something to quietly change.

## Two mistakes in the measuring instrument

Both mistakes pointed toward a more comfortable conclusion than the truth, which is the pattern worth noticing.

The first version of the measuring script looked for configuration files in a folder that has never existed, and reported finding none. In a summary, "no configuration files found" reads exactly like "no configuration overrides the limit", and only one of those is a finding. The correct count is 47. A figure of 49 had been quoted earlier the same day.

The script also worked out which models are free by scanning every Python file in one area and keeping the last match. The last match was a copy preserved inside a run log, which records what a model was handed during a past review rather than which models the panel dispatcher treats as free today.

A third mistake was caught by a guard that already existed. A paragraph written for the recovery document quoted a test result without naming the command that produces it, and the save was refused on the ground that such a figure can quietly become false without anything noticing.

## What this suggests, and what still blocks it

The natural repair is to stop looking for one rule and use two, one for each decision. Choose the models most likely to succeed, since the order cannot affect that. Then, among those chosen, ask the cheapest-per-unit-of-success first, since that cannot affect the chance of success. Under that split, the founder's instruction to escalate from cheapest upward and his objection to handing a hard problem to a weak model are both correct, about different things, and they stop contradicting each other.

Nothing has been built. One thing blocks it, and it is a measurement rather than a design decision. Both rules need an estimate of how likely a given model is to crack *this particular* finding. What the project's records support is how often each model succeeds across findings in general, which cannot tell a research-grade problem apart from a typographical error. Without that distinction, the selection step would pick the same 2 models for the hardest problem in the archive as for the easiest. That is exactly where the three earlier proposals stopped, and it is where this one stops too.

## Correction: the founder's own earlier ruling already dissolves half of this

Trying to break the argument turned up something better than a confirmation. The weak point was this: if a model that fails with an error does not use up one of the 2 attempts, then a later model gets reached instead, and which models were consulted would depend on who happened to fail. That would wreck the whole separation. Tested by running the real routing code with deliberately failing models: it does not happen. The limit is applied by taking the first 2 off the list, so a failure inside that pair buys nothing.

But the same few lines of code quote a ruling made on the 6th of October: that there should be no limit at all, and a finding should keep going until it is either resolved or the list of models is exhausted. That setting is already built and works. Run with no limit, all 5 models are consulted instead of 2.

That changes the conclusion. If every model is consulted, the choice of which models to ask is no longer a choice, so the chance of nobody succeeding becomes a fixed number that no ordering can affect. Only the cost question remains, and the cost question is solved. **So the tension dissolves under the founder's own ruling, and the 2 attempt limit is what keeps it alive.** The missing measurement is needed only if the limit stays.

What is still outstanding is that the ruling is not in effect: the limit still defaults to 2 and not one of the 47 configuration files turns it off. That is a wiring job, not a question of design.

Written under CDSFL note standard v1.7 (26 August 2026).
