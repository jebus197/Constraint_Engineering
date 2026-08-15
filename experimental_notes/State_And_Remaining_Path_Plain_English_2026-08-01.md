# Where the project stands, and what is left before Bench Run 2

2026-08-01 21:45 BST

## Summary

The remaining path is: a control run, two remaining subject exams, the capstone,
then Bench Run 2. There is also one small paid check worth doing before any of
that.

What that sequence leaves out is the unpaid work sitting in front of the control
run. Five agreed engineering items remain, plus three smaller defects. None costs
money. All of them have to land before a paid run is worth launching, because a
run launched without them burns money producing a result that cannot be trusted.
That is not a projection — it is what happened on 1 August, twice.

## The state tonight

2461 tests pass, none fail, and the whole suite runs with no network access, so
no test can quietly spend money. Four commits landed this evening; the working
tree is clean. Nothing is pushed and nothing is merged, per the founder's
instruction to wait until the move to `main` can be confirmed by hand.

Five of the ten agreed must-do items are closed.

## What happened today, briefly

One decision point in the review system was rebuilt four times: the point that
decides whether a proposed repair may close an issue. Nothing else closes an
issue, so that single decision carries the whole weight of a run.

The third attempt looked correct and was not. It approved any repair whose code
was still grammatical. Every harmful change is grammatical, so a repair that
inserted a command injection into the document under review was approved and
closed its issue. The fourth attempt makes that check able to refuse a repair but
never to approve one.

Full account: *The check that could only ever say no* (same date).

## The road to Bench Run 2

### Stage one — unpaid, engineering only

Five items remain from the panel-agreed list. Three concern how the document
reaches the review panel and how its replies are read back:

- **Presentation.** The document is handed to the panel wrapped as though it were
  a program, and only 45 of its 307 lines arrive. The panel has been reviewing a
  fragment, and nothing told it so.
- **Reading the panel's tests.** The system only recognises a proposed test if it
  contains an `import` line. A test written for an English document opens the
  document by name instead, so it is discarded and the system wrongly concludes
  nobody could produce a test at all.
- **Routing.** Prose targets are still sent to the code-inspection tools, which
  is the root of most of today's trouble.

The remaining two are guards rather than repairs:

- A preflight that **refuses to start** a run whose settings contradict the kind
  of document it is pointed at. All eight queued prose configurations currently
  fail it, which is exactly why it is worth having.
- **Telling the panel why its repairs were rejected.** Across four rounds, fifty
  repairs were rejected and no model was ever told. This is the founder's own
  design point from earlier in the week: a claim the machinery cannot handle
  should go back to the panel, not be quietly filed.

Three smaller defects sit alongside: a check that reads a linter's success
message as an error and so confirms code-quality issues that do not exist; a log
that writes into the run archive when it should not; and a documentation sweep.

Roughly a day of work. Costs nothing.

### Stage two — the small paid check

One dispatch to one model, costing pennies, confirming a model actually reads and
respects the new document markers introduced in stage one. Cheapest available
insurance against discovering at round four of a paid run that the panel never
saw what it was meant to see.

### Stage three — the control

The run with nothing planted in it. Its purpose is to measure what a panel
produces when there is genuinely nothing wrong, which is the only way to know how
much of a normal run's output is real. Started 1 August, spent four rounds,
paused when the machinery broke underneath it.

**Recommendation: restart, not resume.** Those four rounds were produced while
the fix-scoring machinery was rejecting every repair, so thirteen issues were
locked into an unresolvable state by a fault rather than by anything real.
Resuming carries that artefact into the one experiment whose entire purpose is to
measure what a panel leaves behind. Sunk cost of restarting: roughly $20.

### Stage four — the two remaining exams

Physics and biology. Chemistry and engineering are done and both converged.

Those two results answer the founder's question about documents where argument
and mathematics live side by side: both converged, with 31 of 32 and 31 of 31
findings demonstrated by a runnable test, **while the fix-scoring machinery was
rejecting every repair**. The system reached a correct stopping point against a
headwind, not with a tailwind.

### Stage five — the capstone

A four-cell comparison varying two factors at once, on a frozen system with no
fixes applied partway through. The integration result.

### Stage six — Bench Run 2

Twenty-seven frontier problem sets. Substantially larger than everything above,
with its own design discussion still unheld.

## Money

Two recent full runs measured at roughly $6 and roughly $19. On that basis the
control, the two exams and the four capstone cells come to somewhere near $140,
with the caveat that a run which fails to converge costs more than one that does.
Bench Run 2 is larger than all of it together and should be budgeted separately.

The operational tracker records a balance of about $452 as of 29 July.
Unverified since. [VERIFY:current]

## Decisions required from the founder

1. **Restart or resume the control.** Recommendation: restart.
2. **The queue alarm now halts the run outright** rather than merely refusing to
   declare convergence. That change was made today and is stronger than what was
   originally specified — the difference between a run that stops and waits and
   one that keeps going while flagging a problem. Confirm halting is intended.
3. **Whether to spend the pennies on the stage-two dispatch check.**
   Recommendation: yes.
4. **Whether this evening's four commits should be pushed.** They are local only.
   Nothing in them is sensitive, but pushing is outward-facing and the founder
   asked for caution around the shared branch until the merge is confirmed.

Unchanged and still open: deleting the experimental branch once the merge is
verified; regenerating the three exams whose answer keys are in public history.
On the second the founder judged the exposure overstated and elected to move on,
recorded as a deliberate decision rather than an oversight.

## What proceeds without a decision

The five engineering items, the three smaller defects, and the documentation
sweep. None spends money; none changes a measurement already taken.

Written under CDSFL note standard v1.2 (14 May 2026).
