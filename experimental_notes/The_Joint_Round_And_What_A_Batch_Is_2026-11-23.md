# The Joint Round, And What A Significant Batch Actually Is

Constraint Engineering, the 23rd of November 2026, from about 13:20 to 14:30
GMT. A session report covering a free panel round, the 3 findings it produced
that were verified independently, 2 claims of the project's own record that it
refuted, and a measured answer to the question of how large a batch of work
should be before it goes to review.


## The Headline

The panel was right about 3 things and the project's own written record was
wrong about 2 of them. Both corrections were established by running something,
not by rereading. The 2 seats also disagreed with each other about the repair
they were asked to judge, and that disagreement has been kept rather than
resolved, because each seat scored the repair against a different set of
scenarios and the question of which set is right has not been settled.


## What A Significant Batch Is, Measured Rather Than Guessed

The founder's guidance was that each time his verdict has been requested in a
spoken report it has usually come to between 10 and 12 items, and that an
average over the last month should be taken as the guide. That recollection was
checked against the files rather than accepted.

Counting every decision heading in the spoken reports dated on or after the
23rd of October, and treating a morning report and a decisions file written on
the same date as 1 occasion rather than 2, gives 9 distinct occasions carrying
138 verdicts in total. The median is 11.0 verdicts per occasion. The mean is
15.333333, with a 95 per cent interval on the mean from 6.197818 to 24.468849,
and a bootstrap interval over 20,000 resamples from 8.111111 to 22.777778. The
versioned copies in the repository, which are the more complete corpus, give 20
files carrying 268 verdicts, a median of 10.5 and a mean of 13.400000.

So the recollection is confirmed on the figure that matters. The median sits at
10.5 to 11.0 on 2 independent corpora, which is inside the 10 to 12 band. The
mean is higher only because a few occasions carried 29 and 30 items, and those
were backlog overflows rather than intended batch sizes.

A caveat is recorded rather than buried. The number of verdicts put to a
person is not the same quantity as the size of a batch of work, and the 2 are
linked only by the instruction to use the first as a proxy for the second. The
proxy is used as directed, and the distinction is stated so it does not quietly
become a fact.

The measuring script had a defect on its first run, and finding it is the reason
the figures above can be trusted. Its pattern for a decision heading required
the word to start a line, and the versioned copies write their headings with
markdown hash marks in front. It therefore found 3 versioned files where 20
exist, and the spoken copies looked richer than the versioned ones. That was 1
sentence away from being written up as a finding that the founder's verdict
record was not under version control. It was the instrument, not the record.


## Why The Panel Round Happened At All

The standing instruction is that every batch of work goes to a free panel before
it lands. Measured against the commit gate's own test for this, imported rather
than reimplemented so the 2 cannot drift apart, 7 of the last 10 commits landed
with no useful panel round. The **Wilson** 95 per cent interval runs from 0.396778
to 0.892209 and the **Clopper Pearson** interval from 0.347547 to 0.933260, both
computed on 2 agreeing routes. The per commit trail shows something a single
proportion hides: the lapse is consecutive, 6 commits in a row after the only
round that did happen.

The cause is not forgetfulness. The gate printed a line reporting the absence on
every one of those commits, and that line was built to report rather than
refuse, with a shell construction that makes every failure path fall open. It
was walked past 7 times.

The dispatcher then refused the first attempt at a new round, and the refusal was
correct. The previous round had been a blind round, where each seat answers
alone, and it still owed its joint half, where each seat is shown what the other
actually wrote. The refusal was honoured rather than overridden. A joint round
must quote 240 contiguous characters of each parent reply, because pointing a
seat at a directory is not exposure and nothing checks that it read it. The 2
purposes were combined into 1 round deliberately, because a separate round would
have cost another 20 minutes of an 8 core machine for questions the same seats
were already holding in context.


## The First Verified Finding: A Measuring Script That Could Not See Its Own Subject Repaired

The producer written to demonstrate how the cy gate counts its refusals, which
is entry B209, builds its keys by
hand and passes them straight to the function that spends the budget. It
therefore never calls the key construction it exists to measure.

This was confirmed by execution rather than by reading. The key function was
replaced with a tripwire that raises an error if called, and both arms of the
producer ran to completion with 0 calls to it. The consequence is that the
producer could never have reported the repair as working. It would have declared
the defect live forever, no matter what was fixed.

The same pass established something neither seat had named. The live gate
exposes no key function at all; the key is built inline. So extracting it as a
named function is a precondition of the repair rather than a matter of taste,
and that is why both the producer and its guard had been building keys by hand:
there was nothing to call.


## The Second Verified Finding: 2 Of 17 Were Never Defective

The task list records that 17 scripts can edit the project when merely asked
what they do, and that 2 of the 17 fail only under one particular way of
invoking them, with their cause being how that invocation resolves paths.

Driven in a throwaway clone, both of those 2 exit cleanly, change 0 bytes of
Python source and leave 0 modified files. They are false positives of the
measuring instrument, not defects. The figure under that invocation must
therefore not be quoted as a defect total; the figure under the ordinary
invocation, which is 6, is the one that counts.

The instrument used to check this had its own defect first, and it was caught
before it did any harm. The tree hash it computed depended on the order the
operating system happened to list files in, so it reported a change where there
was none. It was validated against an untouched tree before being trusted, and
only then produced the result above.

The criticism of how the wrong claim got written is worth more than the
correction. The repair half of that entry was caught by execution and fixed, and
then the defect half was left asserted from the same reading that had produced
the error, and marked as holding. A claim that survives reading and dies on
execution is this session's own named failure, and the sentence declaring that
split safe was itself an instance of it.


## The Third Verified Finding: The Right Answer For The Wrong Reasons

The project had declined to claim that the test suite's failure rate improved,
on 2 grounds: that the 2 statistical routes computed straddled the conventional
cut, and that the 2 confidence intervals overlapped.

Both grounds are wrong, and the conclusion is still right.

Reporting 2 routes and calling them the 2 routes turned a statement about which
routes were chosen into a statement about the data. Driven across the family, 4
of 5 two sided routes reject at the conventional cut and only the **Yates**
corrected one does not. The **Barnard** unconditional exact test returns 0.041330
and is genuinely independent of the conditional construction the first route
uses, so it is not a second route to the same number. A fifth route, **Boschloo**,
agrees, and is now behind a flag because it costs 94 seconds against 2 seconds
for **Barnard** and changes no conclusion, which on a machine with 8 cores is not a
cost worth paying on every commit.

The interval argument was the standard fallacy. The overlap of 2 single
proportion intervals is not a test of their difference. All 4 interval methods
on the difference itself exclude 0.

What actually defeats the claim is that the 2 runs did not test the same thing.
The suite grew by 611 tests between them. Comparing like with like on the tests
present in both, the result turns on a single failure's attribution: it gives
0.064721 when every failure is assigned to the shared set, and rejects once even
1 is assigned to the added tests. Which tests failed is not recorded against the
2 populations, so the question is open, and that openness is the reason the claim
is refused.

The direction of that sensitivity is recorded against the seat that raised it.
That seat described the conclusion as flipping if even 1 failure sat among the
added tests. Driven, assigning failures to the added set strengthens rejection
rather than weakening it. The objection it named is right and its direction was
not, and a proposal from a panel is a hypothesis until it is run.


## The Disagreement, Kept Rather Than Resolved

The 2 seats reached opposite conclusions on the repair they were asked to judge.

The first seat conceded the scenario it had previously lost, scored 4 candidate designs,
and concluded that no combination of fixes shows a demonstrated advantage over
the single best one, so under the project's own rule the single fix is preferred.

The other scored a wider set of scenarios, found that the single fix restores the
original defect on a sequence of observations that share nothing between polls,
failing to release a stop in 400 consecutive events, and proposed a combined
design measured at 5 of 6 against 4 of 6 for every single alternative, which is
the strict domination the project's rule requires before combining anything.

The sharper observation belongs to the second seat and it lands on the brief
that was sent to them. A candidate judged against scenarios its own author wrote
will score full marks by construction, so reproducing its table of 6 scores out of 6 confirms
the arithmetic and says nothing about coverage. The brief had reported
reproducing it as though reproducing it had validated the candidate.

The disagreement is testable, because the 2 seats scored different scenario
sets. That test has not been run, and nothing from the round has been adopted.

Both seats also corrected themselves against their own interest, which is the
round's best signal. The first seat found that its first combined candidate never stored
part of its own state, so 1 arm of it was doing nothing and it had failed a
scenario for a reason that was not real. The other found a hole in its own test
on first run.


## 2 Defects Found In Today'S Own Work, Before It Was Committed

A freshness checker built earlier the same day to catch stale evidence was found
to do the opposite. It reported evidence as current after 4 files had been
staged. The cause was that it compared a record against a snapshot written in
the same minute from the same state, so the comparison could never disagree with
itself. The guard shipped with it had passed throughout, because it tested 1 of
the 2 possible orderings of events and the live system hit the other. The fix
ties a snapshot to the commit board that wrote it, so it stops being consulted once
that work is over. 4 of 4 attempts to break the fix turn the guard red, and the
file was verified byte for byte as restored afterwards.

The second was that 3 of the 4 scripts written today declared command line
options that could never be used. A shared helper that answers requests for help
refuses any other argument by default, before the script's own parser is
reached. Its help text also stated that the script took no arguments, over the
top of scripts that had some, and a test believed that sentence. 1 older script
had the same defect. The helper's own behaviour was deliberately left alone
beyond the wording, because changing when it hands control back would, in any of
the hundreds of scripts that act before parsing, make a request for help perform
the work instead.

An action is recorded plainly because it was careless. A flag that writes was
run as a probe to find out whether the flag could be reached. It could, and it
performed a repair on 9 files. The repair was the one that was wanted and each of
the 9 was then verified individually, but asking for help would have answered the same question without writing
anything,
and a flag that writes is not a way to find out whether a flag can be reached.


## What Is Pending

Nothing from the panel round is adopted. 3 proposals are recorded and untested:
a reframing of the review gate question from whether it should refuse to whether
its verdict should be written down, on the grounds that a reported verdict
appended to a ledger would have made all 7 lapses visible on the first commit at
no cost; a rule for catching an empty test, by running it against a tree where
the defect is present and against another where it is absent, requiring the 2 answers to
differ; and a cheaper repair for the 6 scripts still carrying the help defect.

The disagreement between the 2 seats is the first thing to settle, by running
each seat's scenarios against both candidate designs.


---

Written under CDSFL note standard v1.9 (1 November 2026).
