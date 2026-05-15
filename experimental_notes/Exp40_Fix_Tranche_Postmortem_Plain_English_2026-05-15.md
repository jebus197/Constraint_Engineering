# Experiment 40 Fix Work — What Was Done, in Plain English

2026-05-15 22:30 BST

## What this note is

A reader-friendly account of a block of engineering work that followed
the second leg of Experiment 40. The technical companion carries the
file paths, test counts, and commit hashes. This note explains what was
broken, what was fixed, what was deliberately not done and why, and what
now waits on a human decision.

## The setting

Experiment 40 puts five large language models into a structured,
round-after-round review of a piece of source code and watches them
converge on the real defects. Its second leg (the continuation run)
finished and produced a post-mortem listing five anomalies plus a
backlog item — a rule for resolving "merge deadlocks", where the system
cannot decide whether a newly reported defect is the same as one it
already knows about. The project founder reviewed that post-mortem,
also ran the text past an unconstrained instance of one model for a
second opinion, and asked for the whole list to be worked through under
the project's full rigour discipline: cross-checking every change with
multiple independent tools, actively trying to disprove each fix before
trusting it, and keeping a paired written record.

## What was fixed

Five smaller fixes addressed the continuation's anomalies.

The first hardened the part of the system that reads a model's output
and extracts each finding's identifier. Models had occasionally written
fragments of code into the identifier field — a stray piece of a Python
expression, a lone backtick — and the old guards, which only caught
things shaped like variable names, let these through as malformed
phantom entries. The new rule is strict: an identifier must be a single
run of letters, digits, and underscores, and no longer than is sensible.
Every legitimate identifier the project has ever used passes; every
malformed one observed in the run is rejected. Adversarial fuzzing —
deliberately feeding it injection strings, look-alike Unicode
characters, and a pathologically long token — found one gap (the long
token), which was closed on the spot.

The second turned out not to be a logic error at all. A classifier that
decides what kind of claim each finding makes had been logging
"overridden below threshold" in a way that looked like a bug. The
investigation showed the override is intentional in software reviews
(the simple pattern-matcher agrees with the model only about fifteen
percent of the time there, so the model's judgement wins regardless of
its confidence number). The defect was the log message describing a
correct decision dishonestly. Each decision branch now states its real
reason, and a dedicated test proves the decision itself is unchanged.

The third stopped a piece of bias-detection from crying wolf. In a run
that has converged, one model reasonably keeps reporting things the
system already knows, which tripped a "possible systematic bias" alarm
every single round. The alarm now only fires if the pattern persists
for several consecutive rounds. Crucially, the change is opt-in: unless
the round-aware caller supplies the tracking state, behaviour is exactly
as before, so nothing else is disturbed.

The fourth fixed the genuine continuation bug behind the "every model
flagged for human review, every round" noise. The system already knew
not to *restart* a model that was merely quiet because the work had
converged — but it was still *recording* that quiet round as a failure,
which still triggered the human-review flag. Now a suppressed quiet
round is recorded as a non-event, so it feeds neither the failure
streak nor the flag. A second gate was added so that deep convergence
(measured by the project's novelty-decay metric) suppresses the
false alarm independently. A genuinely failing model still escalates
exactly as before — that path was tested explicitly.

The fifth strengthened the message the system sends a model when its
proposed fix could not be parsed. The old wording politely asked for a
reformat; the new wording states plainly that an unparseable fix counts
as no fix and gives a strict mandatory template. The more invasive
option — re-asking the model mid-round instead of next round — was
deliberately not built. It is the riskiest change for the smallest
gain, and most of the continuation's unparseable fixes were stale
anyway (they targeted code that had already changed), which an
immediate retry cannot help. A precise condition is recorded for when
that bigger change would become warranted.

## The merge-deadlock rule

The backlog item was the merge-deadlock resolution rule, designed
before the continuation run on the project's evidence-first principle.
It is now built: when the system cannot decide which existing entry a
new finding belongs to, it asks all five models a short, single-answer
question and goes with a clear majority — merge if three or more agree
on a target, keep separate if three or more say so, otherwise leave it
for next round. A round-level tie-breaker (suggested by the
second-opinion model and folded in) sweeps the unresolved deadlocks
when the run is deeply converged but the strict convergence rule has
not formally fired. The whole mechanism ships switched off by default —
the design always intended it to be switched on first in a smaller,
lower-risk experiment after review. Because it is off, it changes
nothing yet, and the full test suite confirms that.

## The empty-output mystery, solved

The continuation had shown one model repeatedly producing nothing for
the per-section part of its review while still producing a final
synthesis. The cause was found by reading the code path (which is
deterministic, so reading it is the diagnosis): the per-section calls
were capped at a small output budget, and the two affected models are
reasoning models that "think out loud" before answering. On a large
section the thinking alone exhausted the budget, leaving the answer
field empty — and the code only ever read the answer field, silently
discarding the thinking, which for a code review *is* the analysis. The
fix raises the per-section budget and, when the answer field is empty,
falls back to the reasoning trace. This is a more direct version of the
second-opinion model's "recursive synthesis" idea — the analysis was
already there; it just needed to be read.

## Checking the earlier fixes

The eight fixes folded in before the continuation were re-verified. All
are intact. The one with real mathematical content — a correction to
how the system counts novelty — was cross-checked with three
independent tools: a constraint solver proved its core inequality
always holds, a symbolic-algebra system proved its curve-fitting
formula is identical to the textbook one, and a numerical run over two
thousand random cases confirmed it behaves correctly and, in the
specific convergence scenario, surfaces the depletion signal the old
version had masked.

## What was not done, and why

Two items were surfaced for a human decision rather than done
autonomously. The first is a live five-model conference on the
architecture: the command-line tool for one of the models was unstable
in the environment, and a live five-model multi-round conference is a
real expense whose actual purpose is the founder's go/no-go on
switching the merge-deadlock rule on. A rigorous local falsification
pass was run instead — it found and fixed two genuine issues, so the
substance was covered. The second is restarting Experiment 40 for more
rounds: that is a multi-hour run with significant cost, and the
founder's established practice is to monitor these closely. Launching
it unattended would contradict that practice and the project's
cost-awareness discipline. Both are ready to go the moment the founder
chooses; nothing is blocked by waiting.

## Where things stand

Two hundred and twenty-nine tests pass across the whole body of work.
Every behavioural change is either off by default, opt-in, or covered
by its own new tests. The working tree is clean of regressions and
ready to be committed as one coherent set whenever the founder directs.
The two open items are decisions, not unfinished work.

Written under CDSFL note standard v1.2 (14 May 2026).
