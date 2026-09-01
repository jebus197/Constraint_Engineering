# Panel review, two blinding failures, and a run that can finally be read

**1 September 2026.** A session that began with four fixes and a rename ended by
finding that the simulation's blinding had never worked, that the guard meant to
protect it had never let a run start, and that the panel is measurably alive.

---

## What the panel did to the fixes

Two reviewers were dispatched against committed code in disposable sandboxes:
CC2 (7,714 characters, 223 tool calls) and Fable (4,022 characters, 100 tool
calls). Every claim they made was re-measured before being acted on.

**One of the four fixes rested on a refuted claim, and the claim was mine.** The
mid-run target integrity guard had been recorded as never having fired, on the
evidence that no archived run directory carries the `target_integrity_events`
field. That is the violation-gated key. The unconditional sibling
`target_hashes` is written one line below it, in code that had already been
read. Measured: nine run directories carry it, covering 38 hashed rounds. The
guard has executed 38 times and been correctly silent every time. "Never
reported a violation" is not "never ran".

CC2's triage rule was adopted from that: an unconditional write with zero
occurrences means unreachable; a violation-gated write with a witnessed
unconditional sibling means reachable and correctly silent; only a
violation-gated write with no sibling is genuinely ambiguous. The general
remedy is to give every guard an unconditional "I ran" counter beside its
alarm.

**Seats are not models.** The refutation tally had been changed to count
distinct seat labels. In the live configuration two seats, Codex and ChatGPT,
declare the same underlying model. Of 103 archived findings challenged by three
or more distinct labels, 21 had fewer than three distinct models behind them:
20.4 percent, with a Wilson interval of 13.7 to 29.2 percent. The registry now
resolves seat labels to model identifiers taken from the run's own
configuration.

**A length floor rejects a terse conclusion.** The new panel-reply predicate
rejected anything under 800 characters, which would retry a reviewer who
genuinely had nothing further to say. Acceptance is now structural: a short
reply carrying an explicit verdict marker is accepted, and the 54-character
holding note that prompted the work is still rejected.

## Three documents were stale, and two had no test that ran their generator

Fable was asked to sweep the class rather than re-verify its single instance,
and the class was larger. The systemic enabler is a single line in the quality
checker: line citations have their file checked and their line number
deliberately ignored. Every stale line number in every tracked document is
therefore exempt by construction.

The instrument inventory said 27 of 34 instruments had a commissioning
candidate, and 5 rows had been measured. Its own generator said 30 of 34, and 9
rows. The track record audit said the modern era covered 11 runs and 566
entries; its generator said 13 and 586. Both documents open by promising the
reader that their figures are reproducible.

A parametrised test now runs each generator and compares the figures, and its
discovery half fails if a new document makes that promise without being added.

## The rename manufactured precision

Renaming the runner rewrote the filename in the tracker's citations while
carrying the old line numbers across unchanged, so stale pointers came out
looking freshly checked. All four were wrong when measured: one by 534 lines,
one by 1,897, one naming a comment block rather than the setting it described,
and one pointing at an unrelated function. They are now anchor text, because an
anchor survives an edit above it and a number does not.

## Two blinding failures, one hiding the other

The sandboxed simulation refused to start twice, producing a single line of log
and no process. It looked like the harness killing a background job. It was the
blinding guard: it counted files across two directories with a single command,
one of which the sparse checkout had just excluded, so the command failed, and
the shell's error handling killed the script silently before the run began. The
control that exists to make the sandbox trustworthy had never once let a run
start.

Repairing it exposed the second failure, which was worse. Sparse checkout
removes the archived results from the working tree. It does not touch history,
and a linked worktree points at the main repository's object store. From inside
a sandbox that had just reported itself blinded, the reference experiment's
report was readable in full: 39 entries, 39 severity values, 12 of them at or
above the critical boundary, with exact values of 0.82 and 0.80 downward. The
panel agents carry a shell. That answer key was one command away in every
simulated run to date.

The run now happens in a plain copy with no version-control linkage at all, and
the script refuses to start if history is still reachable.

## The convergence that could not be read, and the one that can

The first complete run converged at round four by critical quiescence, with the
report labelling the curve vacuous: zero critical findings across the entire
run. That is convergence by absence rather than by exhaustion, and on its own it
cannot distinguish a genuinely clean target from a panel that has stopped
working.

It is also structural. The critical arm of the gate requires a severity at or
above 0.70, simulated severity is permanently barred from threshold claims and
clusters near 0.46, so re-running the same harness reproduces the same vacuous
result every time.

The discriminator is seeded defects with known ground truth. That machinery was
built to a founder ruling of 27 August, carries 42 passing tests, and had never
been used, because no catalogue existed for it to read. One now exists outside
the repository holding five real defects in the target, drawn from two distinct
generators because the scoring function refuses to report on a single-generator
set.

Seeding happens after the history is severed, and that ordering is load-bearing:
the seeding function refuses a target inside a version-controlled tree, because
a difference against history returns the planted set perfectly and needs no key.

**The panel is not dead.** On an interim reading of the first round's raw
replies, all six reviewers named the defect that breaks the smoothed
confirmation rate, five named the relaxed count validator, and five named the
dropped blending weight. One defect, the hash that quietly lost its sort and so
became order-dependent, was named by nobody. That is a measured blind spot
rather than an absence of evidence, and it is the first time a simulated run has
been able to say which it was.

## Standing at the close

The suite reads 4,775 passing and none failing. Everything described here is
committed. Three matters need a ruling: whether the current runner should meter
spend at all, since the only tested cost control has never written a byte and
the runner tracks nothing; whether nine configuration gates that no
configuration appears to enable should be removed or wired; and whether the
uncommitted work in a temporary worktree, assessed here as superseded on both
halves, should be discarded and the worktree pruned.
