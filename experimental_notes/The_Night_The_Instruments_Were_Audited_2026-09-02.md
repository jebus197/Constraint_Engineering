# The night the instruments were audited

**1–2 September 2026.** Three panel rounds, two multi-agent investigations, a
rubric audit that had been outstanding since May, and a simulated run that
finally converged on evidence rather than on absence.

---

## Where it stands

The suite reads **4,839 passing, none failing**. The last simulated run
**converged at round 4** on the two-sided gate with `gamma_critical = 0.953`
against a threshold of 0.3, with **zero occurrences of "VACUOUS"** anywhere in
the report — the decay curve rising cleanly through 0.0, 0.0, 0.9226, 0.9413,
0.9526.

It found **all five seeded defects**, 5 of 5, Wilson [56.6%, 100%] — including
the two that the earlier catalogue could not fairly test for, and the one that
requires reasoning across a round trip rather than comparing code to the comment
above it.

No real experiment has yet run on this runner. That remains the gap.

## The rule that was never ruled

A guard barred a simulated run from being cited as evidence of anything,
including whether the runner works. Its provenance did not survive inspection:
the project's own tracker raised it as "panel-converged, both reviewers, needs a
standing ruling", and forty minutes later a commit restated it as a standing
ruling, with the function's documentation adding "and founder-adopted" on top.
Nothing in the record supported that label. In a framework whose founding
principle is that findings are confirmed by tools or by a human and never by
model agreement, a two-model convergence had become a rule and was then used to
refuse an answer.

The founder could not remember approving it, and had not. He removed the clause.

The withdrawal then had to be done twice, because the first pass edited only the
value the function returns. Three sibling channels went on asserting the
withdrawn bar — the function's own documentation, a log line printed on every
simulated run, and a test file's header — while the test suite stayed green,
because the guard inspected the returned value. One reviewer named the shape
exactly: the same failure as the reachability witness it had caught the previous
round, where the checked artefact was cleaned and the unchecked sibling was not.

## Six statistics, withdrawn

A claim that two panel seats had once been genuinely different rested on six
figures. Neither reviewer could reproduce any of them, and no script computing
them exists anywhere in the repository. The analysis was also wrong in kind:
rounds within a run share target, prompt lineage and accumulated findings, so
they are not independent trials, and with the run as the unit the effect
vanishes. The set labelled "after the lapse" was the entire archive, mislabelled.

The route difference itself is real, documented, and visible in the commit. The conclusion stands on the route difference itself, which is in the diff of commit 556e0af, and needs no significance test. The figures
are struck from the code, the tests and the tracker.

## The audit the pre-registration demanded in May

A document committed on 18 May, before the runs it governs and never edited
since, requires each run to report where the numeric severity proxy and the
five-clause consequence rubric disagree, and how sensitive the verdict is to
that disagreement. Neither half had been built. No archived report carries any
rubric field.

The first half was run for the first time: 286 findings in the disputed band,
drawn from 29 real run directories, scored against the five clauses **blind to
the numeric** — the severity withheld, and redacted from the text of the 80
findings that mentioned it, without which a third of the sample would have
answered itself.

**The rubric and the numeric agree on 54.4% of judgeable findings** — 141 of
259, Wilson [48.4%, 60.4%]. The disagreement is near-symmetric, so no shifted
threshold would fix it.

**And it is not reader noise.** An independent second pass over three shared
slices agrees with the first on 86 of 93 items, 92.5%, with Cohen's kappa 0.837
and a 95% interval of [0.721, 0.953]. Two careful readers track each other
almost perfectly and track the number barely better than chance. Of the findings
sitting exactly on the threshold, the rubric calls 67.0% critical, [57.7%,
75.1%].

This does not license moving the threshold, which is the largest single risk of
self-deception in the project and which the pre-registration makes subordinate to
the rubric anyway. It licenses building the remedy the pre-registration already
specifies: where the two disagree on a finding that matters to the verdict, the
rubric governs and the adjudication is logged. The second half — reporting the
verdict's sensitivity — is now emitted per run.

Stated plainly because the figure invites over-reading: this is the boundary band
by construction, the hardest 14% of findings, chosen because that is where the
gate is decided. It is not a claim that severity scoring is 54% accurate overall.

## A catalogue that measured the wrong thing

Five defects had been seeded into a target to test whether the panel detects
anything. Three were killed by every seat; two were missed by all of them. Four
independent investigations agreed on why, and the fault was the catalogue's.

Every plant that was killed contradicted a formula written verbatim in the
docstring directly above it; 17 of 22 findings justified themselves by quoting
that docstring. The two that required reasoning about an invariant were the only
real tests of detection, and both had been assigned to the group the scoring
function does not report on — so the headline returned a perfect score while two
in five plants went unfound.

The decisive measurement is simpler. Seed each plant alone and run the project's
own memory suite: the three killed plants fail 4, 3 and 12 tests. The two missed
plants pass all 135. The project's own instruments cannot distinguish them from
clean code, so a blind reviewer cannot fairly be expected to.

One plant sat in a function the target's own header declares dead, and three
seats cited exactly that to exclude the site. The seeding deleted the file's only
evidence for the property it broke, because the sorting call *was* that evidence.
And three of four seats cited the other seeded function as an example of the
module's good design: the target's prose was arguing the panel out of suspecting
the function it had been seeded into.

The rebuilt catalogue is written to five stated criteria, and against it the
panel found everything.

## Findings that were being deleted

A finding could be deleted by reusing an identifier. The alias map keys on model
and local id alone, so when a model re-used its own identifier for a different
defect, the second was converted into a confirming vote on the first and its
description, its falsifier and its proposed fix were discarded without ever being
registered. One reviewer traced a correct catch to exactly that path.

The first fix compared descriptions and was refuted on real data: of 711 archived
pairs naming the same function and carrying different falsifiers — different
defects by the project's own criterion — 282 scored above the threshold, 39.7%,
Wilson [36.1%, 43.3%]. The signature is built from location tokens, so two
findings about one function collide by construction, and the threshold had been
calibrated on the opposite population. The shipped test used a cross-file pair
sharing no tokens: the easy case, shipped as the whole set.

The rule is now the project's own: a different falsifier is a different defect.
In the next run the guard fired **ten times**, each one preserving a finding that
would previously have vanished — two of them about the very function whose single
catch had been lost.

## What the instruments were doing to themselves

A tool built to find controls nobody has seen fire was accepting the runner's own
rehearsal as the evidence they had fired, twice over, through a dead conditional.
Its replacement excluded nine real panel transcripts for discussing simulation,
one of them 76 characters from a window boundary, while the authoritative
provenance keys sat at character 494,477 — outside the window it chose to look
in. It now parses the document and reads the key.

A test meant to prove the age control works failed because the age control
worked. Its replacement asserted an invariant that holds vacuously whenever
nothing is new, and a mutation survived the whole suite. The control is now
driven rather than observed, and four mutants die where two survived.

A settle pass carried a comment saying it runs unconditionally and was gated one
line later, so on halted runs already-confirmed findings were re-offered to the
panel — and a carefully written test had pinned that gate in place, asserting the
code against its own comment.

And the tool's own actionable verdict was unpinned: inverting one condition
flipped 16 of 51 classifications with the suite still green.

## What remains

The binding fault behind the one halted run is cross-model duplicate handling:
six seats reporting the same defects with nothing merging them, a duplicate guard
whose threshold is unreachable for rewordings, and a snapshot taken before the
loop that makes same-round confirmations invisible. Routing asks two of five
seats and calls it exhaustion. A lowercased label would silently un-rank the
whole ladder. Sweep replies are persisted nowhere, which is why an attribution
overwrite was unrecoverable.

Four matters need a human ruling: whether spend should be metered at all, since
nothing meters it today on either path; whether nine configuration gates no
configuration enables should be removed or wired; whether to restore the seat
contrast that lapsed in April or accept four architectures and say so; and
whether the superseded work in a temporary worktree should be discarded.
