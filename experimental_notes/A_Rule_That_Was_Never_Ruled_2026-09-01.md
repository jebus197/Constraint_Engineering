# A rule that was never ruled, and a canary catalogue that measured the wrong thing

**1 September 2026, evening.** Two panel reviewers took apart a batch of fixes, a
four-angle investigation took apart the catalogue behind them, and both arrived
at the same conclusion: the instruments were flattering their operator.

---

## The rule that was never a rule

A guard in the runner declared that a simulated run is barred from being cited
as evidence — among other things, barred from "convergence verdicts as
evidence". That clause blocked the only question the simulation exists to
answer, which is whether the runner is fit to take into a real experiment.

Its provenance does not survive inspection. The runway raised it as
*"Panel-converged, both reviewers | HIGH — needs a standing ruling"*. Forty
minutes later a commit restated it as *"STANDING RULING, panel-converged"*, and
the function's docstring went further and added *"and founder-adopted"*. Nothing
in the record supports that label. Both reviewers found the chain independently;
one observed that the runway's own wording, asking for a ruling, is an admission
it did not have one. In a framework whose founding principle is that findings
are confirmed programmatically or by a human and never by model agreement, a
two-model convergence had been promoted to a rule and then used to refuse an
answer.

The founder, asked about it, could not remember approving it, and the record
says he did not. He then ruled: remove the clause.

**The withdrawal stopped at the payload.** Removing the bar from the dictionary
the function returns left three sibling channels still asserting it — the
function's own docstring, a runtime log line emitted on every simulated run, and
the test module's docstring. The console barred what the report permitted, and
the suite stayed green throughout, because the guard test inspected the
dictionary. One reviewer named the shape precisely: it is the same failure as
the reachability-witness sibling it had caught the previous round, where the
checked artefact was cleaned and the unchecked sibling was not.

What survives is a caveat on magnitudes, not a bar on conclusions.

## Six statistics, withdrawn

The same batch claimed that two panel seats had once been genuinely different —
one routed through a vendor CLI carrying its own hidden agent prompt, the other
bare — and that the difference lapsed on a particular day. The route difference is real, documented in the experiment plan under Diversity Axes, and visible in the diff of commit 556e0af.

The statistics offered in support are withdrawn. Neither reviewer could
reproduce any of the six numbers, and no script computing them exists anywhere
in the repository; they appear only as prose in a docstring, a test comment and
a commit message. The analysis was also wrong in kind. Rounds within a run share
target, prompt lineage and accumulated findings, so they are not independent
trials; with the run as the unit the claimed effect does not survive. The
"post-lapse" set turned out to be the entire archive, pre-lapse runs included —
the whole dataset mislabelled. And a confound makes the contrast unattributable
regardless: before the lapse one seat was dispatched against a chunked target
far more often than the other, so the route change altered dispatch mechanics
and output length, not only the instruction condition.

The design conclusion stands on the route difference itself and needs no p-values.

## A tool that accepted its own rehearsal as evidence

The audit built to find controls nobody has seen fire carried a dead
conditional where its simulated-run filter should have been, so it excluded
nothing. The consequence was circular: the three controls it reported as having
fired had fired only in the rehearsal, whose report sits in the archive — twice,
via a duplicated run directory. With the filter working, the witness set drops
from 82 reports to 73 and those three controls correctly revert to quarantined.

A second reviewer found that commissioning the comparison is not commissioning
its input. Corrupting the function that dates a control's first appearance left
the entire suite green while flipping three verdicts, including the very witness
key from the earlier refutation. Every test had been reading that date out of
the tool's own output and re-applying the comparison to it. It is now pinned
against version control, independently.

## The catalogue measured docstring-diffing

Five defects had been seeded into a target to test whether the panel detects
anything. Three were killed by every seat; two were missed by all of them. Four
independent investigations agree on why, and the verdict falls on the catalogue
author.

Every plant that was killed contradicted a formula written verbatim in the
docstring directly above it. 17 of 22 findings justified themselves by quoting that docstring (77.3%, Wilson [56.6%, 89.9%]). The two plants that required reasoning
about an invariant were the only real tests of detection — and both were
assigned to the split the scoring function does not report, so the headline
returned a perfect score while two in five plants went unfound.

The decisive measurement is simpler than any of that. Seed each plant alone and
run the project's own memory test suite: the 3 killed plants fail 4, 3 and 12 tests respectively. The two missed plants pass all 135. The
project's own instruments cannot distinguish them from clean code, so a blind
reviewer cannot fairly be expected to.

It compounds. One plant sat in a function the target's own header declares dead
— *"HASH GROUNDING is UNUSED. Nothing calls compute_source_hash"* — and three
seats cited exactly that to exclude the site. The seeding deleted the file's
only evidence for the invariant it broke, because the sorting call was that
evidence. And three of four seats cited the other seeded function as an example
of the module's good design: the target's own prose was arguing the panel out of
suspecting the function it had been seeded into.

The residual model-side component is real but small. The word "sorted" appears nowhere in any of the 24 replies; two seats rewrote the seeded line verbatim while
fixing a different bug in the same function; one seat named the other plant's
operator and cleared it in prose without writing the two-line falsifier that
would have killed it.

## The rebuilt catalogue, and what it found

A second catalogue was written to five stated criteria: no plant beside its own
answer except where retained as a labelled control, none in code the module
declares unused, difficulty not correlated with split, generators naming a real
mechanism rather than satisfying a guard, and every plant demonstrable through
the public interface. Each new plant was verified to discriminate before use.

Against it the panel named four of five plants, including a hard one with no
adjacent formula, where the negative arm of a drift detector is clamped so that
downward drift becomes permanently undetectable. That is detection rather than
string matching. Only the incomplete-state-reset plant, which requires
round-trip reasoning, went unnamed.

## The halt, and what it was

The run stopped at its first round on an alarm: three critical findings locked as
irreducible against a bound of two, none of them carrying a falsifier. The alarm
exists to catch mechanical failure and its own text forbids raising the bound to
clear it, because that is how it was suppressed twice while it was right.

All three were correct catches of seeded defects. Two quote the inverted
duplicate guard; the third is the smoothed-rate plant. All three carried an
untoolable verdict at the moment the alarm evaluated, and all three finish the
run closed and confirmed with falsifier code present, because the
residual-clearing sweep tooled them.

So the findings were sound, and the falsifier path was not broken either. The alarm evaluates
before the falsifier path has finished tooling, and a bound of two is reached by
findings minutes away from being toolable. The correction is to evaluate after
tooling, or to exclude transiently-untoolable items — and since it touches a
gate, it goes to the panel before it goes into the runner.

## Standing at the close

The suite reads 4,785 passing and none failing. The runner's machinery is
exercised and its guards are commissioned rather than assumed. What remains open
is named: the alarm's timing, a failover path that still counts a seat by its
primary architecture, an aliasing path that absorbed 23 of 45 raw findings (51.1%, Wilson [37.0%, 65.0%]) and through which one correct catch was lost, and the boundary case in the age
comparison. No real experiment has yet run on this runner.
