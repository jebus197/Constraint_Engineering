# THE LADDER CONTAINED THE BOARD IT WAS BUILT TO AVOID

Constraint Engineering, the 22nd of November 2026, between 06:30 and 06:45
GMT. A cheap pre-commit check ran a full commit board inside itself, a kill
that reported success killed nothing, and a run recorded as outstanding had
already been completed 20 days earlier.


## WHAT A PRE-BOARD LADDER IS FOR

A commit in this project is gated by a board, meaning a fixed list of 322
guard files that must all pass before the commit is allowed. Re-measured on
the 22nd of November over 91 determinate runs, that board costs a mean of
1866.296703 seconds, which is 31.10 minutes, with a 95 per cent confidence
interval on the mean running from 1736.805540 to 1995.787866 seconds. It
refuses 44 of those 91 runs, a proportion of 0.483516, with a Wilson 95 per
cent interval from 0.383609 to 0.584760. The producer is the script named
what the commit gate actually costs over time, dated the 8th of November.

So about half of all boards refuse, and each costs roughly half an hour of
an 8 core, 8 gibibyte machine. A pre-board ladder is a small subset of those
guards, run first, so that a refusal is caught in minutes rather than in
half an hour.


## THE DEFECT

The ladder stalled. The monitoring discipline in force requires a running
process to be checked about every 60 seconds and paused on anything odd.
The watchdog fired at 06:36:52 reporting no log growth for 904 seconds and
processor time frozen at 55.4 seconds.

The ladder's only live child was a real git commit running inside a
temporary clone, 4 minutes old, with 2 live pre-commit hook processes
beneath it. The guard file named test precommit guard, dated the 9th of
September, makes a genuine commit, which fires the genuine hook, which runs
the genuine board. A check built to cost less than a board was running one
of its own.

The same property had already been recognised in a sibling guard, the one
named test precommit gate cost, which was excluded from the ladder by name
with a comment recording that it contains the board. 1 was named, and there
were at least 2.


3 PREDICATES, AND THE STOP RULE

Selecting the ladder's contents has now defeated 3 separate predicates.

1. Choosing guards by searching for words from the subject gave 13 guards,
ran in 2 minutes 59 seconds, reported 169 passed, and omitted the guard of
the very file being rewritten. The board then refused with 5 failures, 4 of
them inside that omitted guard.

2. Deriving the set from the changed files gave 118 guards and included the
guard that runs a board, which then hung for 18 minutes.

3. Searching for board containment gave 45 of 322 guards and plainly
over-matched, because most of those merely read the hook rather than run it.

A standing rule in this project says that when a surface defeats 3
predicates, stop building predicates. The replacement is a mechanism rather
than a classification. The pytest timeout plugin is installed, so a per test
cap of 300 seconds bounds any guard that hangs, whatever the reason. The 2
guards known to run a full board stay excluded by name, because each costs
31 minutes rather than hanging.


## THE KILL THAT KILLED NOTHING

The stalled processes were terminated with a loop over their identifiers.
The loop passed the entire list as a single argument, the operating system
rejected it, and the resulting error was discarded by a redirection to the
null device. The output said a signal had been sent. No signal had been
sent, and all 6 processes survived.

This was caught only because the survivor check that followed was
unconditional, rather than conditional on the kill reporting a failure. Had
it been conditional, a 31 minute board would have continued running while
the record said it had been stopped. The repeat, with each signal reported
individually and escalation to an uncatchable kill for any survivor, ended
all 6. A fresh orphan was created by the kill itself and cleared separately,
because terminating a parent does not terminate its children.


## A RUN RECORDED AS OUTSTANDING HAD ALREADY HAPPENED

The master task list carries a ticket for a single simulated validation run
on the severity mechanics, to be performed before the orchestrator
experiment, and the body of that entry states that the run has not happened.
That sentence was written on the 3rd of November.

The operational tracker records that the run completed on the 2nd of
November under full monitoring: 6 rounds, converged at 5, 25 findings, 85.5
minutes, scored against 4 predictions committed before it launched.
Prediction 1 held, with severity not constant and a standard deviation of
0.175692. Prediction 3 held, with sensitivity 0.600000 at the 0.7 cut.
Prediction 2 was not testable and prediction 4 was mis-specified. The run
directory exists and carries both a checkpoint and a completion signal.

Reading the tracker before acting avoided repeating an 85.5 minute run. The
ticket row is stale. The work itself is done.


## A LATENT HOLE IN THE GUARD THAT PREVENTS SPENDING

A simulated run is prevented from spending money by replacing the network
name resolution routine with a version that refuses every paid vendor before
a connection can be opened. That installer is idempotent, and when it is
already installed it returns the original routine. The resumable wrapper
restores whatever value it was handed when it finishes.

2 nested wrapper frames would therefore have the inner frame restore the
real routine while the outer frame is still running, leaving the run
unguarded. 2 independent routes agree that the protocol admits this.
Exhaustive enumeration over all call sequences up to length 6 finds 43
witnesses, the shortest being install, install, restore, dispatch. A
satisfiability solver returns satisfiable for the same condition.

The solver model asserts the nesting rather than deriving it from the call
graph, and the call graph does not reach it, because the supervising
actuator drives the wrapper as a separate operating system process, so 2
frames cannot coexist. The hole is therefore latent and not live. It is
recorded, with a repair of roughly 20 lines scheduled for the next batch of
work, and it is explicitly not a reason to alter the batch currently
awaiting commit.


## WHAT STANDS BETWEEN HERE AND THE ORCHESTRATOR RUN

The orchestrator experiment is build complete, with all 4 components
present. The single mechanical blocker recorded against it, that no
invocation of the harness was both simulated and resumable, was closed on
the 8th of November by a wrapper that installs the spending refusal and then
calls the runner inside the same process.

What remains are 2 decisions that belong to the human in the loop by the
project's own definition: the bounds on a run that spends money, and a
re-run that the founder stated he would start when at the keyboard. Neither
is work that can be delegated, and neither is blocked on anything unbuilt.

Written under CDSFL note standard v1.9 (1 November 2026).
