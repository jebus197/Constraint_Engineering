# Closing report on the overnight task list

> 2026-10-17 11:29 BST.

## What this covers

The founder's instruction was to go, fix and implement everything, and not to stop until it was complete. This reports what was built, what was corrected, what remains, and the decisions that now rest with him. 19 commits landed since the last saved checkpoint. The set of fast tests that run on every commit went from 793 to 927 and all of them pass. 27 guard files are now gated at commit time. The master task list holds 148 entries, of which 114 are done, 7 withdrawn, 1 blocked and 26 open.

## The ticket store he asked for at the top of the list

His ruling was that every issue and every resolution should carry a unique hashed identifier in a searchable register, and that the register must be searched before any new work is proposed. It was built, and then its own checks found 4 faults in it, each measured before it was repaired.

First, identity drifted with the prose. The identifier digested the entry's text as well as its reference, and an entry is reworded every time an addendum is written, so 5 references already carried 2 tickets each and merely improving the extraction rule re-minted 114 of 141 identities in a single step. A reference is now the whole identity, which is unique across the list and survives every later edit.

Second, 9 of 141 titles, 6.3830 per cent with an interval from 3.3941 to 11.6854, named a different entry. A lookup of B11 returned prose about B10, which either re-proposes settled work or passes over open work.

Third, the label comparison could never converge, because the caller held a 160 character string and the store held it stripped to 159, so 18 of 141 rows rewrote an identical record on every run of a file that is append only by design.

Fourth, 22 of 141 ticket texts were stubs, because stripping the reference left a 15 character status stamp under the floor that triggers the fallback, and a stub matches nothing in the tier that catches the same issue arriving in different words.

The register now holds 27 live entries, 121 closed and 270 unconfirmed items harvested from his own replies that need triage rather than work. It agrees with the task list exactly, and it refused 1 commit during the night because an entry had been written into the list without being harvested. That refusal was the register working on its own author.

## His correction list is discharged, and 2 of the 5 items were faults in the list itself

The first item, which he said was the first thing to fix, was that a published figure of 94 of 212 did not reproduce. The authoritative figure is 73 of 167, 43.7126 per cent, with a Wilson interval from 36.4145 to 51.2934 and a Clopper-Pearson interval from 36.0626 to 51.5897. Both causes of the old number are now quantified and together they reproduce it exactly: 13 of the 74 run states read were nested copies of what a single seat saw, contributing 35 of the 45 excess blockers, and at the same scope a hand copied predicate returns 177 against the counter's 167. His own corrected figure of 94 of 197 is also superseded, because the counter returns 79 at that scope rather than 94. The denominator correction he made was exactly right and the numerator moved with it.

The second and third items concerned the operator facing glossary, which still asserted a penalty both panel seats had retracted and described a retired pruner as active. Both panel seats had repaired the code and neither had touched the glossary. His observation that a comment about the symbol kappa was false by count was correct: there are 355 occurrences across 10 distinct identifiers and only 53 are the one the comment claimed. His second half was right to the line number, and the first census written to check it searched only the Latin spelling and reported the symbol absent, which would have contradicted him. The file uses the Greek letter.

The fourth item, that the runway document existed only on the Desktop, was already discharged. It is versioned, it is a declared mirror with a drift guard, and stage 3 was unblocked by a commit timed at 14 46 18 on the 16th, the same minute as the ruling. Saying so is the honest answer rather than claiming the work.

The fifth item was real and worse than stated. A stage 1 entry marked done rested on an incomplete repair: the merge resolver located a finding identifier with an unanchored search, and the label CC2 is itself a letter C followed by a digit, so the composed identifier CC2 underscore F004 reduced to C2, which no alias key holds. The specification mandates reading an unresolved merge source as a confirmation on the target, so every merge CC2 ever proposed was recorded as CC2 agreeing the target is real. The verdict inverted rather than being lost. CC2 issued 308 of the 800 archived merge verdicts, the largest share of any seat. The archive cannot show this fault, because a failed merge is recorded as an ordinary confirmation: all 800 archived merge verdicts are successes by construction.

## Four rulings of his that had never been carried out

The hardened convergence gate is on by default, 12 days after he ruled it. It had been on in the simulated runner alone, which is the exact inverse of what he asked for. The default now has 1 expression rather than 4, because a fallback is the path a configuration object without the field takes, and leaving those at the old value would have let a stub keep the superseded behaviour silently.

The required quiet run is raised from 3 to 7. The measured curve, read off the archive with no model involved, runs 23 of 182 premature closes at 3, falling to 6 of 131 at 5 and 0 of 99 at 7. 5 meets the target on the point estimate only, with an upper bound of 9.6324 per cent against a 5 per cent target. 7 is the first window with no premature close observed and the smallest whose upper bound meets the target, and going further hurts: by 9 the upper bound has risen back above the target because the denominator shrinks as the window lengthens. The cost is about 4 extra rounds on any run that would otherwise have converged, roughly an hour on the measured 71.5 minutes of the third shakedown leg. 8 tests encoded the old value and none was silenced: each now derives its series or its round from the configured value, checked by running the whole convergence suite at 3, 5 and 7.

The arbitrary cap on a model's reply is addressed by recovering what he asked to have recovered. He had been told a better way existed and could not remember it. It was incremental stream json parsing, and it was verified rather than restated. A completion marker separates printed from not printed, and a dead seat never prints one either. The clock separates nothing: a degraded attempt issued 88 tool calls at 20.455 seconds per call and never converged, while a healthy one converged in 49 at 20.816 seconds per call. The seconds per call are stable whether a seat is working or churning and only the number of calls differs, so a longer clock buys churn. Watching the number of calls rise separates all 3 states. The dispatcher now consumes output as it arrives, so the number of calls so far is visible in flight, partial output survives a timeout where before a killed attempt left no trace at all, and every call is stamped with its arrival time. That last point matters because not one of the 135 archived attempt records carries a time per call, so the gap between one call and the next, which a non arbitrary bound must be derived from, is unmeasurable today. This produces it. The derived bound is a second step and is not claimed as done.

The immune memory is reset for the upcoming live experiments, and the priors are archived rather than deleted. The researcher switch he asked for already existed and already defaulted to persist as he directed. The reset itself had been named in a code comment as a script that did not exist. The state it was run against was worse than he had been told: the store held priors from 6 counted experiments and named only 3, and those 3 were exactly the simulated runs. The check against ingesting the same experiment twice refuses an identifier it has seen, so it could not refuse a re-run of an unnamed one, and re-ingesting any of the 3 live experiments would have doubled its totals in silence. The archive is verified against the live file before that file is touched, and the round trip is byte exact.

## The ladder order, where the measurement changes the answer

He has ruled 4 times that nothing but demonstrated capability should rank a model. The code ordered them by vendor name. The question of what may replace that was measured across all 3,020 archived entries, and the answer is more interesting than expected.

No fingerprint field records a falsification outcome at all. The fields are capacity, attention and productivity, and ranking on finding rate was refuted by a free seat on the 6th of October because it measures productivity. The only recorded quantity that measures the capability the ladder exists to exploit is the falsifier verdict. Gemini refuted 10 of 701, DeepSeek 6 of 521, and ChatGPT, CC2 and Codex refuted none at all of 373, 366 and 342. 26 refutations in the entire archive.

The omnibus test rejects equality, chi square 14.5802 on 4 degrees of freedom, probability 0.005656, so the seats genuinely differ. And yet none of the 10 pairwise comparisons survives correction for the number of comparisons: the widest contrast has a raw probability of 0.035825 and a corrected one of 0.286597. A ranking is a set of pairwise orderings, so heterogeneity is established and order is not.

That is why his season design is not a preference but the only sound founding. The order cannot be inherited from an archive that cannot support it, so it must be measured inside the experiment that uses it. The season is built and wired: it measures the experiment's own outcomes, freezes the result, and a later round cannot reshuffle it, which a test drives by supplying second round evidence that reverses the ranking. Where a round does not discriminate the vendor fallback is used and the reason is written to the log, which is the half that was silent before.

## The decision that was not taken, and why

Emptying the vendor tuple was tried and reverted within the hour, because it sets 2 of his own rulings against each other. His ruling of the 7th of October, that a free seat should be added to the ladder, is implemented as membership of that very tuple and is verified by a guard asserting the ladder has 6 rungs. 8 guards went red, and they were red for that reason rather than from staleness. Membership and order are separable, and separating them is the proposal, but it changes recorded behaviour and so it is his to rule on rather than taken on his behalf.

## Explanations owed, and they are all of the same kind

9 faults of the assistant's own were found and are recorded in the places they occurred, because the measuring instrument has been the weak point more often than the code it was measuring.

Three measuring instruments were wrong rather than the code they examined. The kappa census searched one spelling of the symbol and reported it absent from a file that uses the other. A first comparison of the blocker predicate guessed conditions the test does not use and reported 532 blockers against 167; that figure is withdrawn. A producer for the adjudication figure treated any entry carrying a tool's output as decided by a tool and returned 79 of 79 instead of 77 of 79; carrying a tool's output is not the same as having been decided by one.

Two figures of the assistant's are withdrawn outright. The 532 above, and a branching ratio of 1.3243 which counted the 59 entries of the list's founding population as offspring of closures when they are the generation zero ancestors.

Two defects were introduced by the assistant's own earlier repairs. A counter refactor left an unreachable return statement naming a variable no longer in scope, which would have raised an error had anything reached it. And a test that guarded the exhausted valve asserted on source text, so it went red on a rename while the behaviour was unchanged.

One test written to protect the immune memory destroyed it. The archive listing matched the sidecar file, which sorts after the real copy, so restoring the latest wrote the sidecar over the live priors. It was recovered byte exactly from the verified archive, which is the entire reason the archive is written and checked first.

And the invented timestamp fault recurred after being recorded. An entry carried a time typed from memory rather than read from the clock, hours after the same fault had been written up. The clock had been captured in the same step and the value was still typed. The working practice has changed so that the captured value is interpolated and cannot be typed.

## The register's own totals were wrong twice and both are fixed

Settled work was overstated by more than double, 257 against 111, because a retired identifier is a terminal status and was being added to the settled total. And 73 closed duplicates sat at superseded identities until the sweep was widened. Every record away from the canonical identity is now a redirect, so the closed total of 121 equals the list's own done and withdrawn figures exactly.

## What remains

26 entries are open. 16 of them await the founder, either because they are questions he has asked that need his decision or because the work is built and tested and the last step changes recorded behaviour. 10 can proceed without him.

The 4 decisions that matter most are these. Whether ladder membership and ladder order should be separated, which is the collision described above. Whether the required quiet run should be 7 as built or 5, which halves the added cost of about 4 rounds and still meets the 5 per cent target on the point estimate. Whether the list should keep filing every discovered gap as its own entry, which is what has kept new entries arriving faster than they close and what makes the record complete, or raise the bar, which slows that arrival by changing policy rather than work. And the branching result below.

## The one finding that is not a repair

A test written on the 11th of September carries this in its own words: it exists to fail if the list stops terminating, and that is a conversation to have rather than a number to quietly restate. It has gone red and has been left red deliberately.

Treating each closed entry as producing new entries, the ratio was 0.4444 with an interval from 0.3009 to 0.6565 and a probability of 0.0000193 against the critical threshold. It is now 0.8148 with an interval from 0.6155 to 1.0787 and a probability of 0.0873. The interval now admits a process that need never terminate, so termination is no longer established. It does not say the list is growing without bound: the point estimate is still below the threshold. The honest statement is that termination is no longer demonstrated.

What drove it is worth saying plainly. The list gained 34 entries and closed 17 on the 17th, and the audit of his own instructions added 22 of those 34, each recording a ruling or a question that nothing tracked. The rise is substantially the cost of having looked, which is the opposite of a quality problem. The bar for what becomes an entry has not been changed on the assistant's own initiative, because the figure of 0.8148 new entries per entry closed is a number he is entitled to see move for real reasons only.

Written under CDSFL note standard v1.7.
