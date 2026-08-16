# What the Similarity Function Actually Does When It Decides

2026-08-16, 23:42 BST. Plain-English companion to the technical note.

## The short version

The similarity function decides whether two findings about the same piece of code
are describing the same defect or two different ones. Its evidence looked
excellent. Measuring what it *does*, rather than what it *says*, found two
problems. One is fixed. Two need a decision.

## The measurement that was never stored

The numbers justifying the similarity function existed only as written comments
inside the source file. Nothing on disk held the underlying data, no script
rebuilt it, and no test would have noticed if the numbers had quietly stopped
being true.

That is now fixed. A script rebuilds the whole dataset from the six archived
experiment runs, and every recorded number comes back identical: 165 findings,
438 pairs, 28 labelled the same defect, 290 labelled different. A test now fails
if that ever stops holding.

This matters beyond tidiness. A claim stored apart from its evidence can outlive
the evidence, and nothing reports a problem when it does.

## The number nobody had computed

The recorded evidence answers "is the separation real?" — and at
p = 1.9 x 10^-25, that was never in doubt.

It does not answer the question the rule is used to decide: **at the setting it
actually runs at, how often does it merge two findings that are genuinely
different?**

The answer is 14.48%. About one in seven.

Two other readings matter, and they pull in opposite directions.

**The alarming one.** Of the 73 pairs the rule merges, 45 are genuinely
different. Its merge precision is 38%.

**The one that puts it in context.** Without this rule, the system merges *every*
one of these pairs — all 290 different-defect pairs, wrongly, every time. The
similarity function cuts that to 45, an 84% reduction, and it has never once
wrongly split a genuine same-defect pair.

Both are true. Quoting only the first would make a large improvement look like a
broken component; quoting only the second would hide a real error rate. The low
precision comes from the skew in the data — only 8.8% of these pairs are the same
defect — not from a weak discriminator.

## Problem one, now fixed: a number with no units matched anything

The third tier asks whether two findings assert the same computed value. To stop
two unrelated numbers agreeing by coincidence, each number is supposed to keep
the word attached to it — 0.6 *penalty*, 64 *comparisons*.

The check for that was skipped whenever one of the two numbers had no word
attached. A bare number matched any number of the same value.

This mattered because the third tier is only allowed to *merge* findings, never
to separate them. So a too-generous match always costs a real second defect: it
gets counted once, the convergence gate stops seeing it, and nothing downstream
can tell.

**How it stayed hidden.** The tier's supporting evidence describes what it
*answers*. It never called two same-defect findings different, and its answers
separate at p = 1.4 x 10^-7. Both true. But the tier only *changes a decision* on
3 of 318 pairs — and all 3 were wrong. A statistic about a mechanism's opinions
is not a statistic about its effects, and thirty-six passing tests never told
those apart.

All three bad merges trace to one finding whose only number is a bare 0.6, which
matched the penalty-tier 0.6 in every neighbouring finding.

**The fix costs nothing.** Pairs that should merge behave identically. Pairs that
should not improve: four wrong merges become correct separations. The supporting
statistic strengthens from p = 1.4 x 10^-7 to p = 3.3 x 10^-9, checked three
independent ways.

The obvious alternative fix does not work, and it is worth saying why. One could
allow a bare number through when the value is distinctive enough to identify
itself. But 0.6 counts as distinctive under that test, and 0.6 in this codebase is
a configuration constant that appears in many findings about the same module.
That is precisely the coincidence the check exists to prevent.

**One real consequence, traced before accepting the fix.** One finding in the
divergence experiment is now counted instead of merged away. Five of the six runs
are completely unchanged, and no convergence conclusion moves — that run's tail
already ended on a non-zero count, so the gate's three-consecutive-quiet-rounds
test failed both before and after.

Whether that recovered finding is a genuine second defect or a re-description of
a known one is **not decided here**, and is marked as pending rather than guessed
at.

## Problem two, needing a decision: most findings are cut off mid-sentence

While tracing the bare 0.6, it turned out the finding it came from had been **cut
off mid-word** at exactly 200 characters. The word that would have identified the
0.6 was removed before the rule ever saw it.

Checking the whole archive: of 2187 stored findings, 714 are exactly 200
characters and 661 exactly 500. **1284 end mid-word.** Around 63% of every
finding this project has recorded is stored truncated, and the similarity
function reads the truncated version.

Two separate causes: a parser that keeps only the first 200 characters when a
finding does not match its expected format, and a 500-character cap when writing
to the registry.

**What is not established.** Pooling all the data, a merged pair involving
truncated text looks about ten times more likely to be a wrong merge. But
splitting by experiment, the pattern reverses on the two exam targets. That is
the classic signature of a confound: the apparent effect is partly explained by
which experiments happen to have both problems at once. The causal claim does not
survive, and it is reported as not surviving.

What does survive is smaller and still worth knowing. Truncation makes findings
shorter, so fewer technical terms are available to compare. With few terms, the
similarity score becomes coarse — one shared term out of three and three gives
exactly 0.200, which is exactly the merge threshold. Fifteen pairs sit precisely
on that line.

**The decision needed.** Keeping the full text is a small code change with a large
reach: it changes how every future run is parsed, and would make experiments from
50 onward not directly comparable with 40 to 49 on any measure derived from
finding text. Fix it now and re-derive, fix it at the integration boundary, or
leave it and record the limitation. That is a question about experimental
continuity, not about code.

## Problem three, waiting on you: the 120 dropped pairs

The original measurement sorted pairs into "same defect" above one similarity
score and "different defect" below another, and **silently discarded the 120 that
fell between**. That is 27% of the data, and it is not a random 27% — it is
precisely the pairs where the question is hard. Nothing in the record said they
had been dropped.

All 120 are now extracted into a file, unanswered, each with both findings' full
text, sorted with the closest calls first.

They are deliberately left unanswered. Labelling them here would repeat exactly
the flaw the exercise exists to remove: a machine grading a machine, where the
grader's own mistakes are invisible because nothing independent ever checks them.
Until those pairs are ruled on, every error rate quoted above is provisional.

## What generalises

One lesson, stated narrowly because it is the useful form.

**A statistic about what a mechanism says is not a statistic about what it does.**
The third tier had a strong, honest, correctly computed p-value describing its
answers. On the handful of occasions its answer actually changed an outcome, it
was wrong every time. The p-value was not incorrect; it was answering a different
question from the one being leaned on.

That is the project's governing failure mode in a new costume: every failure
renders as a confident success. A component that abstains on most cases and is
right about the rest can carry an impressive number while contributing only
errors — and nothing in the number reveals it.

The practical form: whenever a component is justified by a statistic, check
separately how often it changes a decision, and how often those changes are right.
Those are usually far fewer cases than the statistic covers, and they are the only
ones that matter.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
