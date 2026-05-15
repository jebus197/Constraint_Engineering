# Experiment 40 Continuation — What Happened, in Plain English

2026-05-15 05:20 BST

## What this note is

A reader-friendly account of the second leg of Experiment 40 — the
continuation run that picked up where the original 14 May run left off,
ran for two hours and four minutes overnight, completed seven additional
rounds of multi-model review, and stopped when its wall-clock budget
expired. The technical companion at
`experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md` carries the
file paths, log line counts, and commit hashes. This note explains what
the experiment was trying to do, what it produced, what the seven fixes
folded in beforehand actually did once they hit live model output, and
what is still unresolved.

## What the experiment was doing

Experiment 40 puts five large language models — Claude, Gemini, two
gpt-5.5 routes, and DeepSeek — into a structured review of a piece of
Python source code, asks them to surface bugs round after round, and
watches what happens as the panel converges on the same set of real
defects. Each model writes independently, the runner reconciles the
findings into a registry of canonical entries, and the registry tracks
each finding through a Bugzilla-style lifecycle: open, confirmed by
peer review, closed by verified fix, or merged into a duplicate. The
goal is convergence — a state where the panel has nothing new to say,
because every real defect has been surfaced and either fixed or recorded.

The continuation run resumed from Round 10 of the original Exp 40 run,
which had completed rounds zero through nine before being stopped to fold
in fixes from a post-mortem of the earlier run. Seven fixes went into
the runner ahead of the continuation, addressing bugs the original run
had exposed.

## What happened

The continuation ran from 03:15 BST to 05:20 BST on 15 May, producing
seven additional rounds (Round 10 through Round 16). It stopped on a
wall-clock safety boundary rather than on convergence — the runner had
been given a two-hour budget and used 2 hours 4 minutes 38 seconds, then
gracefully saved state and exited.

The panel processed 280 raw findings during the entire 17-round arc,
reconciling them into 179 distinct canonical entries. Twenty-six of
those reached the CLOSED state, twenty-five with verified fixes that
passed four code-quality gates: a linter, a type checker, a security
scanner, and the existing test suite. Forty-two are confirmed but not
yet fixed. Sixty-eight remain open, and twenty-three were unable to
resolve a peer challenge after multiple rounds and were escalated to
human review.

The dominant pattern across the run was deep convergence by one metric
and inconclusive convergence by another. The overall novelty rate — how
much fresh material each round adds compared to existing entries — fell
from around 0.29 in early rounds to 0.03 by the end, roughly a nine-fold
drop. By that measure, the panel is firmly settled. But the boolean
convergence rule — three consecutive rounds with zero novel critical
findings — was not met. Two near-zero moments (Round 10 and Round 14)
were each followed by burst rounds, with Round 15 producing four new
critical findings, the largest single-round critical count anywhere in
the 17-round arc. The panel had largely converged but not in the
specific way the boolean rule looks for.

## Did the fixes work

The seven fixes folded into the continuation can be assessed one by one
against what they did in live operation.

The empty-synthesis fallback for the decomposed dispatch — a salvage
mechanism for when a model's final synthesis call returns nothing —
fired cleanly in Round 11. Gemini's synthesis came back empty, the
fallback reconstructed the model's contribution from its earlier
chunk-by-chunk analysis, and Round 11 closed with Gemini's content
preserved rather than lost. The fix did exactly what it was designed for.

The Bugzilla close-the-loop module is the run's biggest validation. Of
the twenty-six findings that reached the CLOSED state, twenty-five
arrived there through this module — the runner taking a model's proposed
fix, applying it to a sandboxed copy of the target file, running four
code-quality gates against the result, and only closing the finding if
all four pass. The module also rejected fixes in revealing ways: some
because the proposed fix did not include the structured SEARCH/REPLACE
markers the runner needs to extract the change, some because the fix
targeted source code that had already been modified by an earlier fix
landing in the codebase, and one or two because the fix would have
introduced a fresh type-annotation defect that the type checker caught
before close. Every rejection was correct. The module's behaviour
demonstrates that mechanical verification of model-proposed fixes is
viable at scale.

The gamma input fix — a metric-correction that changed how the runner
counts "new" findings, excluding already-merged duplicates — produced
the well-behaved declining curve described above. Before the fix, the
metric had been overcounting; after the fix, the values track the
registry state accurately.

The Stage 6 calibrator type-fix prevented a recurrence of the crash
that had hit the original run when a finding's flaw-class field
arrived as an integer rather than a string. No crashes of that class
occurred during the seventeen rounds.

The Intelligent Task Controller fix prevented a misclassification that
had been treating Codex's verdict-heavy rounds as model failure when
in fact Codex was producing exactly the verdict-only output the runner
expected. Codex stopped hitting that specific misclassification from
Round 11 onward.

The parser fix for the FINDING_ID terminator addressed one path through
the admissibility parser where the original run had seen a finding's
content runaway across a section boundary. That specific runaway did not
recur. A different and related parser issue did surface (described
below), which the fix does not cover.

The explicit Bugzilla-paradigm header added to the panel prompt asked
models to submit fixes in a specific block format. Results were mixed:
seventeen findings produced parseable fixes that flowed through the
close-the-loop verifier, but several per round arrived as freeform prose
that the extractor could not parse. The instruction is necessary but
clearly not sufficient on its own.

## What the run surfaced that needs attention next

Five distinct anomalies are worth recording. None blocked the run, but
each is informative for the next experiment.

DeepSeek's per-chunk Phase 1 analyses repeatedly returned zero characters
even when the model's final synthesis call produced substantive output.
The model appears to be treating the chunked instructions as input but
not emitting analytical text per chunk. Whether this is a routing issue
with the OpenRouter wrapper, a prompt-format issue specific to DeepSeek
V4 Pro, or expected behaviour worth simply tolerating, is worth a
short investigation before the next experiment.

A second parser anomaly surfaced multiple times across Rounds 12, 13,
and 14: finding identifiers were being constructed by absorbing code
fragments from the finding's own text rather than from the intended ID
field. Identifiers like `f for f in findings}` appeared, drawn directly
from a Python dictionary-comprehension fragment in the finding's
description. The substantive content of those findings was preserved
and processed normally, but the identifiers themselves were mangled.
The recursive observation here is that the panel was independently
diagnosing the very bug that was mangling its own identifiers — namely,
that the runner's finding-ID handling silently overwrites entries when
two findings from different models happen to share an identifier. The
fix should harden the identifier parser across all construction paths,
and the panel's own analysis on this issue is a candidate design
reference.

The classifier that decides whether each finding is mathematical,
behavioural, or structural logged override decisions at confidence
values below its stated 0.70 threshold a few times. Either the override
logic uses an effective threshold the log doesn't display, or there is a
rounding-tolerance fence post error. A one-line audit will confirm
intended behaviour.

A duplicate-detection layer called the autoimmune detector flagged
Gemini as showing systematic bias in every round where Gemini's findings
reached that layer — because Gemini's verbose output kept recapitulating
already-canonicalised findings, hitting a 100% rejection rate. The
autoimmune override consistently confirmed the rejections were correct.
The flag's signal is informative but, in a converged-state run where
one model is reasonably expected to produce mostly known findings, the
per-round flag generates noise on the human-review queue. Gating the
flag on a multi-round window would reduce the noise without losing the
detection.

By the end of the run all five panel members were classified as
"degraded" by the runner's ITC mechanism — ITC being the project's
"IT Crowd fix" discipline, the rule that when a model's output quality
declines the runner does not bench or skip the model but restarts it
fresh, handing the fresh instance a scope informed by the prior
instance's fingerprint. The same discipline is also how the project
discovered burst reasoning, the observation that a fresh model instance
will often surface what a long-running instance has stopped seeing.
ITC's classifier uses output-yield decline as its trigger for restart,
which in late-stage convergence is exactly what one would expect — the
panel naturally produces shorter, more verdict-focused output when
there are fewer new defects to surface. The classifier is currently
treating convergence behaviour as if it were model degradation, which
queues up pointless restart triggers and generates a recurring stream
of human-review flags that don't need human action. The fix is to
gate the degradation classification on the overall novelty-decay
metric: when the system is in the active regime (novelty still high)
the classifier behaves as before; when the system is in the converged
regime (novelty decayed) the classifier downgrades low yield to
"healthy converged" rather than "needs restart". This preserves ITC's
burst-reasoning utility in the cases where a fresh instance has new
ground to cover, while preventing the runner from churning the panel
when the panel has already settled.

## The deadlock evidence

The most significant single thing the continuation produced is the
evidence cluster for the merge-deadlock resolution rule that a separate
design note already proposes. When a new finding arrives at the runner
and the auto-merge mechanism cannot uniquely decide which existing
canonical entry to fold it into, the runner records a deferral. If the
deferral persists for five or more rounds the runner escalates to
human review. The continuation produced six such escalations:

The longest-running deadlock involves a finding first deferred in
Round 2 of the original run, which by the end of the continuation had
sat unresolved for fourteen rounds — by far the most persistent
unresolved merge in the project's history. Another deadlock involved a
finding that could plausibly merge into twenty different existing
entries, with no clear winner among them. A third involved a finding
that was both stuck on a merge decision and stuck on an unresolved
peer challenge simultaneously.

These are precisely the patterns the proposed resolution rule —
applying compelled-convergence by dispatching the merge decision to the
panel for a single-answer vote — is designed to address. The rule
itself has been written and is described in plain English at
`experimental_notes/G7_Merge_Deadlock_Resolution_Design_Plain_English_2026-05-15.md`.
Implementation was deferred until the continuation closed; that
condition is now satisfied. The next decision is whether to proceed
with implementation, adjust the design, or defer further pending more
evidence.

## What this run validates

The run demonstrates that mechanical verification of model-proposed
fixes is viable. Seventeen findings moved from confirmed-by-peer-review
to closed-by-verified-fix during the continuation, each one passing
four independent code-quality gates. The verifier rejected fixes when
they were ill-formed, stale, or would have introduced new defects, and
those rejections were correct in every case.

The feedback channel that lets the runner inform models about output
issues between rounds produced measurable behaviour change. Round 14
saw two models produce unusually short output (around 2,000 characters
each, down from the run's typical range of 8,000 to 17,000); after the
feedback channel flagged both, Round 15 saw the same two models
rebound to 17,000 and 12,000 characters respectively. The feedback
channel is effective at countering output shrinkage.

The five-model panel reached deep convergence by the gradual novelty
decay metric, with the final value approximately one ninth of the early
rounds. The 17-round arc was sufficient for convergence by that
measure.

## What this run did not resolve

The boolean convergence rule — three consecutive rounds with no new
critical findings — was not met. The metric oscillated rather than
descending monotonically, with two near-zero moments interrupted by
burst rounds. The merge deadlocks persist on the human-review queue;
without the proposed resolution rule implemented, they await human
judgment or a later mechanism. The DeepSeek and parser anomalies were
recorded but not investigated.

## What comes next

The post-mortem review is the immediate next step. The data needed for
the merge-deadlock resolution rule's implementation decision is now
available; the decision is whether to proceed, adjust, or defer
further. The five anomalies above are worth addressing before the next
experiment in the sequence. The continuation could itself be resumed
for two more rounds if a longer wall-clock budget is approved, though
the next experiment in the planned arc may be the better use of
project time. The next experiment targets a bounded mathematics module
with a smaller panel exposure to the merge-deadlock pattern, which
makes it a low-risk place to introduce the resolution rule for the
first time if implementation is approved.

Written under CDSFL note standard v1.2 (14 May 2026).
