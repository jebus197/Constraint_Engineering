# The project's own rulebook never reached a single model

2026-10-15, 02:30 BST. Plain-English companion to `The_Specification_Was_Never_Delivered_2026-10-15.md`. Written for a reader who does not read code.

## The short version

The founder's challenge of 2026-10-14 was that nothing in this project ever justified trimming its own core directives, and that the caps which exist were built for a different purpose entirely: to stop a weaker model being handed more *work* than it could demonstrably handle. He drew a line between work and specification. Drawing that same line in the code turned out to be one line long, and it exposed 6 separate mechanisms that were keeping the specification out of what the models actually receive.

The headline is not that 9 per cent of the rulebook arrived. It is that none of the part which matters arrived. Of the 22 blocks the project's own rule-classifier marks as HARD, **0 reached any model**, on a 95 per cent interval running from 0 to 14.8655 per cent. Among the 22 that were dropped is the entire section headed *Falsifier Integrity, Do Not Reach for the Answer*, and inside it the instructions not to read a scoring key, not to weaken a test to make it pass, and not to stop early to obtain a passing result. Those are the rules every verdict in this project rests on. No model had ever been sent them by any route.

All 22 now arrive, with a 95 per cent interval from 85.1345 to 100 per cent, and each model receives the whole 27,803-character specification rather than a 2,503-character summary of configuration flags.

## The 6 mechanisms, briefly

**The loader asked the wrong question.** It compared the rulebook's length against a per-model work limit, and since all 5 limits are smaller than the rulebook, the shortened version was served every single time. The code's own comment described a full-text branch for larger models, and no model in the panel could reach it. There are now 2 separate limits with separate meanings: one for work, keeping every value it had, and one for the specification, set to deliver it whole.

**The shortened version was not a summary.** It was a dump of configuration flags plus the bullet points of a single section. The cause was 2 different definitions of HARD living inside one file, only one of which was the live code the models saw.

**The conflict resolver was arguing with the rulebook on its own behalf.** It splits text into blocks, labels each by topic from keywords, and deletes any block whose topic clashes with one already kept. Over 10 subject areas it recorded 42 clashes, and **40 of them were the rulebook against itself**, on an interval from 84.2101 to 98.6842 per cent. The rulebook says "be concise" in one section and "give a full formal proof" in another; those are different situations, not a contradiction, and the tie was broken by list order. **41 of the 42 deletions removed something the resolver's own rules class as HARD.** Two guards now apply: a document cannot argue with itself, and a HARD rule is recorded as clashing but never deleted. Afterwards: 2 clashes recorded, 0 HARD deletions, nothing altered.

**The resolver was also damaging text it had decided to keep.** It rebuilt each block list by joining with single line breaks, while the splitter had separated on blank lines and stripped the indentation. So a round trip through it flattened paragraph structure even when it removed nothing. Harmless for a flat checklist, not harmless for a document carrying code listings, formal notation and tables, all of which depend on blank lines. A document that loses nothing now passes through untouched.

**The length cap would have cut the rulebook in half.** The cap ran on the whole assembled text, and the rulebook sits first, so delivering it whole without changing the cap would have truncated inside the rulebook and dropped the subject-area checklist and the review target entirely for all 5 models. The 2 repairs are one repair; neither is safe alone. The cap now measures only the work, so the weakest seat still receives at most 4,000 characters of work, exactly as before.

**The decomposition decision counted something it cannot divide.** Giving models the whole rulebook adds 25,300 characters to their standing instructions, and the rule that decides whether to split a job into chunks was counting those instructions. Work headroom fell from 31,123 characters to 5,823, which is 81.2904 per cent of it, so almost every job would have been split on the size of its own instructions. Worse, splitting re-sends the instructions with every chunk, so counting them triggers a mechanism that multiplies them: 3 separate tools agree that splitting can only ever increase the instruction bytes, never reduce them.

## The confound that would have fired only in the free runs

This one deserves its own heading, because it is exactly the risk the founder named when he asked why a feature would be tested in shadow during a simulation.

Every seat carries a recorded figure for the largest prompt it has been seen to accept. For the 6 simulated seats those figures run from 72,934 to 80,517 characters. The new standing instructions are 74,177 characters. So **all 6 simulated seats, on an interval from 60.9666 to 100 per cent, would have had every single job force-split on the size of the instructions alone** — while the paid seats would not have, because their recorded figures are 418,685 and 99,068. A defect that shows up only in the cheap runs and disappears in the expensive ones is the worst possible shape, and it was found before either run started.

A guard now refuses to split a job when splitting cannot possibly help, which is provable: if the un-splittable part already exceeds the limit, then no number of chunks brings any single request under it, the total bytes rise, and the number of requests rises. An explicit human or escalation instruction to split is still obeyed, because a derived argument must not quietly overrule an instruction.

## Why one shadow was promoted and the other was not

The founder's objection was that running a feature in shadow during a simulation defeats the purpose of the simulation. On the severity calculation he is right, and the reason is sharper than he put it: that shadow's own promotion criterion asks for evidence from a run, and a shadow never decides anything, so a run can never produce that evidence. It would have stayed a shadow for ever and a paid run would have been its first live test. It is now built as a switch, default off, and turning it on makes the appendix's own severity formula decide rather than merely observe.

Whether it would change anything at all was measured first, over 2,994 archived findings in 59 runs. It changes **7 releases**. The release test has 2 halves joined by "and", so a lower severity only helps if the other half, a proven calculation, ever holds; it holds for 295 of 2,994 findings, about 1 in 10, interval 8.8364 to 10.9726 per cent. So the promotion reaches real decisions rather than being decorative.

The second shadow is different, and promoting it would have been the opposite mistake. It replays the convergence decision against the swept ledger and records whether the answer would have changed. It does not need to decide in order to tell us whether deciding matters, so it is not circular, and its own code calls the reorder the highest-risk edit available in that file. It stays a shadow, and both free runs produce its reading. This corrects an earlier statement that neither shadow could be promoted by a switch: true of both, but only one of them was stuck in a circle.

## 6 figures were produced wrongly before they were produced correctly

This is recorded because the pattern is the same each time and it is the project's own recurring failure: the measuring instrument was the defect, and the rulebook, the resolver and the archive were all fine.

Two counts of what the shortened rulebook carried, 1 of 22 and 13 of 22, are withdrawn. The probe took the first 8 words of a block and joined them with spaces, which cannot match a block that spans several lines, and 9 of the 22 do. The honest figures are 0 of 22 before and 22 of 22 after.

Two counts of what the resolver deleted, 45 HARD and 475 other, are withdrawn. They counted blocks that failed to reappear after a re-split, which measured the flattening described above rather than any loss of content. Nothing was lost.

One count of HARD deletions, 11, is withdrawn: it tested a field truncated to 100 characters which carries no document class. The honest figure is 41 of 42.

And one measurement returned 0 findings across 59 runs because it read the wrong archive key; the correct key gives 2,994. An empty answer from a guessed question is a statement about the question.

Every one of those 6 is recorded beside its correction, in the code and in the producing scripts, because a withdrawn number needs a record of its withdrawal or the same mistake stays available to be made again.

## 3 things found and deliberately not fixed

**The coherence budgets no longer bind, and the pruner comparison cannot be run.** The density measure divides 20 active rules by a prompt-size estimate of 8,096, giving 0.002470. The rulebook made the prompt about 5.7 times longer without adding a single rule to the numerator, so density fell below every budget, the smallest of which is 0.010: **0 of 50 real compositions are now over budget**, against roughly 2 in 3 before. The consequence is named rather than hidden: the lean-versus-full comparison that every proposed cut has been gated on since July cannot be run until the budgets are re-derived from experiment logs, which is what the 2 free runs are for. They were deliberately not re-tuned by hand, because a hand-set limit with no measurement behind it is the exact thing the founder objected to.

**The concise rendering collapses the code under review.** On a test case holding 20 repeated function definitions, the largest seat received all of it and the other 4 received a single copy with the indentation removed. The harm is limited, because the code also reaches the models through the round prompt, so nobody is reviewing an empty page. But 2 genuinely different functions that look alike can be merged into one, and indentation carries meaning in the language these targets are written in. It predates this work, it is not on the path of either run's question, and 3 large changes in one night with nothing measured between them is how a result stops being attributable.

**A floor is being used as a ceiling.** The figure recording the largest prompt a seat has accepted is described in the code as a proof that it can handle *at least* that much, and the code treats it as a limit on how much it may ever be sent. So the recorded figure can never rise. That is a ratchet that cannot climb, which is the same shape as a defect already on the record for the routing ladder. The guard added tonight treats the symptom; changing the rule would alter how work is routed to paid models and is a decision rather than a repair.

## The 2 free runs

Both use the purpose-built prose target carrying computable listings, 10 rounds, the statistics subject area, with the routing ladder active and its rung budget set to exhaust. The first measures the rulebook repair on its own. The second adds the severity switch. Same target, same seats, same round budget, so the difference between them is attributable to the severity switch and nothing else.

The prose target also commissions a task that has been open since 2026-09-10 and that a code target cannot reach: the admissibility switch is inert on a code file, so only a prose document carrying code listings exercises it at all.

Neither run costs money. The simulation substitutes subagents on the founder's own plan at the single point where a paid model would be called, every seat label carries the simulation marker at source, and the spending limit is zero.

## What this costs

No archived run can now be replayed against the current composer and expected to reproduce, because what every model receives has changed. That is the price the finding was parked for, and the founder has paid it in terms: time cannot be rerun, so the confounds found in the last day can only be recorded honestly.

Written under CDSFL note standard v1.7 (26 August 2026).
