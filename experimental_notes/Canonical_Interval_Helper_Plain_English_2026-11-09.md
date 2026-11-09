# Two intervals, one of them missing

9 November 2026, 14:55 GMT

## The short version

A small piece of measurement code written on 9 November 2026 was supposed to report 2 different kinds of error bar around every proportion it published. It reported 1 of them twice instead. A test that runs every copy of that code and compares their answers caught it and refused the commit. The code has been replaced with the project's shared version. None of the numbers already published changed. And a report made to the founder the night before, describing the mistake as worse than it was, is withdrawn here.

## Why two error bars

When this project says something happened in 1 case out of 5, it also says how uncertain that is, and it does so twice over, using 2 different pieces of mathematics. The 1st is called a Wilson interval, the 2nd a Clopper-Pearson interval. They are not alternatives to choose between. They answer the same question by different routes, and the point of reporting both is that a mistake in 1 is unlikely to be repeated identically in the other.

The broken code computed the Wilson interval, and then computed the Wilson interval again. Where every other copy in the project puts the Clopper-Pearson figure, it put a second Wilson figure. The Clopper-Pearson interval was never calculated at all.

The test that caught this loads every copy of the helper in the project, calls each one with the same inputs, and compares all four numbers that come back. A second Wilson figure sitting where a Clopper-Pearson figure belongs will disagree with the other 46 copies no matter what its value is. 6 of the test's cases failed, and the commit was refused. That is the test doing precisely its job.

## The part that was overstated

The first account of this given to the founder said that every agreement figure the code had produced was effectively meaningless, because 2 correct implementations of the same formula have no choice but to agree.

That goes further than the evidence allows, and the project's own tools say so. There is a script whose job is to decide whether a published figure rests on 1 route or 2. Run against the broken code, it reports the Wilson interval as resting on 2 routes: a well-known statistics library, and the formula written out by hand. The test that protects that script contains an assertion that this exact pairing does count as a genuine cross-check.

So the pairing was the weaker sort of check, the same formula computed 2 ways rather than the same quantity reached by 2 different mathematics. The project already classifies that as the weaker sort. But it is not worthless, and calling it near-meaningless was wrong.

A symbolic algebra check confirms the 2 were computing the same thing: subtract either form of the Wilson lower bound from the other and the difference reduces exactly to 0.

What was genuinely missing is the Clopper-Pearson interval. That, and nothing wider, is the defect.

## Why the published numbers held

The shared version reports a single number for how far apart its 2 routes came out, taking whichever of the 2 intervals disagreed more. In the case the project had already published, the Wilson side is the one that dominates, so that reported number is identical before and after the repair. The Wilson figures themselves were right all along.

What the repair adds is the interval that was absent. Where the Wilson interval for 1 case in 5 runs from 0.036224 to 0.624465, the Clopper-Pearson interval runs from 0.005051 to 0.716418, which is considerably wider. Those new figures were checked on 3 independent routes and agreed to about 1.11 times 10 to the power of minus 16, which is the limit of ordinary computer arithmetic.

## Asking for a proportion of nothing

The broken code, asked about a proportion with no observations behind it at all, returned an interval from 0 to 0. The test guarding it had that value written in as correct.

It is not correct, and the reason is worth stating plainly. With no observations, every possible proportion is equally consistent with what was seen, because nothing was seen. So the honest answer is the whole range from 0 to 1. An interval from 0 to 0 claims certainty that the true proportion is 0, on the strength of no evidence whatsoever. The shared version returns 0 to 1, and the test now records that value together with the reasoning behind it.

## The test that could not have caught this, and the one that can

The obvious check is that the wider interval should contain the narrower one. That check cannot catch this fault, for a simple reason, that an interval contains itself. Run against the broken code it passes at every single one of 741 test points.

The property that does discriminate is strictness. The Clopper-Pearson interval is not merely as wide as the Wilson interval, it is strictly wider, everywhere except at the 2 extremes where a count is 0 or equals its total. Measured across a grid of denominators from 2 to 39, that holds at 741 of 741 interior points, and the broken form is rejected at all 741 of them.

That grid is walked by the test itself rather than by a separate script. There are 2 reasons. Any figure quoted to the founder has to be reproducible by code that is committed alongside it, and and the same loop, pointed at a deliberately broken copy, doubles as proof that the test is capable of failing. It costs about 5 seconds against a check suite that runs for over an hour.

4 deliberate reversions were applied to the repaired code and all 4 turned the test red.

## 3 mistakes made during the repair

None of these 3 were noticed by reading. Each was caught by running something.

The script that applies those deliberate reversions named a test that does not exist, because the name had been typed from memory rather than read from the test runner. The runner reported that no tests had run, which looks like a broken script rather than a wrong name. It now reads the list of real test names and complains by name about any that do not match.

The list of tests that guard every commit was sorted alphabetically while adding 2 entries to it. The list was never alphabetical. It is grouped by the batch of work that added each block, and sorting it turned a 2-line addition into a change of 260 lines, burying the actual edit. It was put back, and the 2 entries appended, which is a change of 4 lines.

That same list was edited twice while a commit check was already running and reading it. A check whose own definition is being rewritten underneath it does not produce a measurement, it produces an accident of timing. The run was stopped, and it turned out to have written a timing record of 705 seconds into the project's own log of how long these checks take. That record has been kept rather than deleted, partly because the project's standing rule is to point at a doubtful record rather than remove it, and partly because removing it moves the headline figure only from 12 of 13 to 11 of 12, which settles nothing either way.

## A number that was right when it was written

The project's master list of work stated that the commit check exceeds its own time limit on 7 of 8 recorded runs, and stated it in the present tense. The log it draws on has since grown from 8 entries to 14, because the checks run by this session's own commits write into the very file being measured. The figure is now 12 of 13, and the earlier reading has been kept beside it in the past tense.

The lesson is narrower than the figure being wrong, because it was not wrong. A number stated in the present tense about a record that keeps growing goes stale by having been correct at the time.

## What is actually left to do

A separate reading of the work list was made while the commit check ran, since reading touches nothing.

20 items are recorded as open. 12 of them appear in the file of decisions put to the founder, and none of those 12 carries the marker the list reserves for a decision awaiting him. Because they are marked as ordinary open work instead, the tool that suggests what to do next points at them, which means it points at items only he can move. The first of them is the item it has been suggesting all along.

Of the remaining 8, 4 are marked as finished work that is still recorded as open, and every 1 of those 4 either asks him something directly or is waiting on 1 of the 12 decisions. Another is a question he put to the model panel. A 3rd records a fault in code that has been switched off, and says in its own text that deciding whether to close it is his call. A 4th is marked as a report rather than a fault, and is deliberately left failing, because the failure is the alarm he asked for.

The single remaining fault record turned out to be his as well. It concerns a rule of his own design, that agreement between 2 classifiers should raise the confidence of the result. A check written on 8 November walks every place that confidence value is set and finds all 4 of them take it either from the model's own answer or from a fixed number, with 0 taking it from any other signal. Since that value decides whether a classifier is allowed to overrule another, a rule that raised it would change which results get flagged. So the rule was never built, and building it is a change to a decision point, which is his.

## 1 live number he asked to be told about

1 item on the list exists solely because the founder asked to be told if the work list ever stopped being guaranteed to finish. It records a ratio of 0.914692, with an uncertainty range running up to 1.111534, measured on 4 November. Re-measured on 9 November the ratio is 0.9072, with the range running up to 1.0908.

The range still reaches above 1, so the item is still flagged and it still cannot be said that the list is guaranteed to finish. But the top of that range has come down from 1.1115 to 1.0908, so the movement is toward the alarm clearing rather than away from it. The central estimate has stayed below 1 throughout, and no statistical test rejects the idea that the list finishes.

1 suspicion was checked and proved wrong. It looked as though this alarm might be hidden from him, because a script that rebuilds his morning report carries an old ratio of 0.7791 written in as a fixed value. The generated report he actually reads computes the ratio fresh, states the 2 counts it used, names the script that produced it, and carries both relevant items. The old fixed value appears only in a report correctly dated 30 October. The alarm reaches him exactly as intended.

Written under CDSFL note standard v1.9 (1 November 2026).
