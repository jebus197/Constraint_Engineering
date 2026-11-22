# THE JOINT PANEL ROUND THAT SETTLED A SPLIT VERDICT

Constraint Engineering, the 22nd of November 2026, between 15:53 and 16:21 GMT.
2 free review seats, each having already reviewed the same 8 repairs in
isolation, were shown each other's answers and asked to resolve where they
disagreed. The round cost no money: both seats run on an existing subscription.

## WHY A SECOND ROUND WAS OWED

A review protocol in this project has 2 halves. In the blind half each seat
works alone and cannot see the others, so agreement between them carries
information. In the joint half each seat is shown the others' answers and asked
to resolve the differences. The second half exists because a disagreement
between 2 careful readers is itself evidence, and smoothing it away loses
the disagreement that was worth knowing.

An attempt to open a new blind round on a later batch of work was refused by the
project's own dispatcher, on the grounds that the earlier blind round still owed
its joint half. The refusal was correct and the debt was real. The 2 seats had
split on 2 of the 8 repairs. 1 returned FAILS on entry B205, the stop gate that
tells the operator it committed when it did not, and on entry B182, the
resource budget gate that stops delegated work launching heavy verification.
The 2nd returned HOLDS on both.
Nobody had resolved it, and the repairs had already been applied to the
repository in the meantime.

## THE RESOLUTION WENT AGAINST BOTH SEATS IN PART

On the stop gate, the second seat confirmed that the first seat's defect was
real, and did so with a stronger instrument than the first seat had: the review
sandbox natively refuses the ps command, which lists running processes, while
permitting pgrep, which searches them by name, so no artificial stubs were needed to reproduce the condition.

It then refuted the first seat's reasoning on 2 counts. The first seat's
demonstration claimed to have started a real shell process and observed it being
misread. It had not started a shell at all. A shell asked to run a single
command replaces itself with that command, so what the demonstration actually
started was a sleep, and what it observed was the correct detection of a
sleep process whose name matched the pattern. This was checked directly rather than
taken on the seat's word: a shell asked to sleep for 7 seconds reports its
process name as sleep, at process 55760.

The repair itself stands and is correct. What failed was the evidence offered
for it, which is a different fault and a more interesting one, because a correct
fix resting on a wrong demonstration looks exactly like a correct fix resting on
a right one.

## A SEAT WITHDREW ITS OWN FIGURE, AND THE WITHDRAWAL IS THE LESSON

On the budget gate, the disagreement was partly about 2 different questions,
with 1 seat judging a claim of completion and the other judging a committed
measurement. Both judgements were individually sound. But the seats had also
made contradictory factual claims about the same body of text: 1 had said a
particular unhyphenated word appears 0 times in the project's prose and used
that to dismiss a change as unnecessary; the 2nd had said 398. Re-measuring in
the joint round, the first seat got 474 and withdrew its own dismissal, with the
sentence that a count over a body of text is not a measurement until the body of
text is named.

Neither figure could be reproduced. Measured in the live repository the answer
is 440. Decomposing it shows why: the choice of what to count over moves the
answer from 157 to 440, a factor of 2.8025. The dominant term is not whether
capital letters are ignored, which moves it by 23. It is whether harvested
review trees are counted, which moves it by 274. Those harvests hold copies of
the project's own files, so counting them counts the same sentence once per
copy. The project has been caught by that shape before, when a symbolic link
walked twice inflated a count of 3,311 severity values that then had to be
withdrawn.

So the seat's method was right and its number was not, and the method survives
the number. For the question actually at issue, which is whether the project
uses a particular turn of phrase, the governing figure excludes the harvests,
because a harvested review tree records what a reviewer wrote rather than what
the project wrote.

The script written to settle this counted itself. Its first run returned 444
where a hand count minutes earlier had returned 440, because its own explanatory
text names the word it is counting. It now excludes itself, and asserts that the
exclusion changes the answer by 5, so that the exclusion cannot quietly stop
working.

## THE MOST VALUABLE THING THE ROUND PRODUCED WAS A SEAT CORRECTING ITSELF

1 seat then amended its answer a fourth time. It had declared that 3 passes
had produced no new finding above threshold. It made that declaration while a
check it had itself started was still running. The check finished, and it found
2 more faults in the same night's batch, neither of which either seat had seen.
In the seat's own account, it stopped looking on the strength of a pass whose
evidence had not come back.

Both faults were then verified against the repository rather than accepted, and
both are fixed.

The first was a genuine defect in a measuring script written the previous night.
It printed 4 examples of what a change had removed, under a heading that had
already printed the full count, and never said that the list was partial. The
project's own rule is that a list cut short under a heading reading as complete
is a silent falsehood and must state its remainder. The project's own truncated-listing guard, which refuses a capped list that
does not state its remainder, was red on that line. The cap is kept at 4, because 4 examples is the useful number for
showing the shape of what was removed, and the remainder is now named.

The second was the opposite: a guard accusing correct code. A check that every
script rejects an unknown command-line option loudly had begun failing on a new
script. The check works by reading which arguments the script says are required
and supplying them, and its method for reading them recognises only options
beginning with dashes. It carried a measured note justifying that: 1 script was
said to carry a required option and none to carry a required bare argument.

Re-measured by inspecting the source of every script rather than by running
them, both halves of that note are now stale. There are 6 required options and 1
required bare argument, and the bare argument belongs to the new script. The
script is correct: supplied with its argument it reports the unknown option and
exits with a failure code. So the check was repaired and the script was left
alone. Changing correct code to satisfy a broken check is repairing the
measurement rather than the fault.

Measuring that the obvious way was itself a hazard, and it is recorded. A first
attempt ran every script with a stray option, which executes the body of any
script that has no argument parser at all. It hung for over 60 seconds on 1
such script and was abandoned in favour of reading the source.

## WHAT THIS SAYS ABOUT THE CHECKING MACHINERY

Neither of those 2 faults could have refused a commit. The file holding both
checks is on no commit-gate list, and appeared in none of the 52 guards derived
as being at risk from the current changeset. They are therefore concrete
instances of a gap the project already tracks: real findings the commit gate
cannot see.

The seat's own summary of the batch is larger than any single repair. Of the 4
accusations it raised against work recorded as finished, exactly 1 pointed at a
genuine fault in the code accused. The other 3 were the measurement machinery
accusing healthy code. That 1-in-4 rate, and not any individual fix, is the result
worth carrying forward.

## WHAT HAPPENS NEXT

The round is recorded as entry B208, the joint panel round that resolved a
disagreement the blind round left open. The joint half is now discharged, which
clears the way for the review of the later batch that was refused at the start.
1 finding was deliberately not acted on and is recorded as entry B207, a reader
that parses a durations table of slowest tests the commit board never emitted. Every proposal the seats made has
been executed against the repository before being adopted, which is the standing
instruction: a review seat's proposal is a hypothesis, not a fix.

Written under CDSFL note standard v1.9 (1 November 2026).
