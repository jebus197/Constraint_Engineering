# The Truncation Rate: A Parameter-Free Admissibility Test For Simplifications

**2026-09-03 00:56 BST** — analysis and proposed formalisation. No code change, no schema change, pending a ruling.

## Framing, and a correction

An earlier note in this series contained the sentence "relativity and the acceptance policy turn out to want the identical discipline." That framing is withdrawn. It invites the reading that a physical theory is being imported into a research harness, which is not what was meant and is not supportable.

What is actually being used is a standard and long-established idea with its own name. In philosophy of science it is theory reduction, set out systematically by Ernest Nagel in 1961: a more general theory reduces to a more restricted one under stated limiting conditions, and the restricted theory is exactly recovered, not merely approximated, within its domain. In physics the same idea is the correspondence principle, associated with Bohr in the 1920s. Newtonian mechanics is the low-velocity limit of special relativity; classical mechanics is the small-action limit of quantum mechanics. The mass-energy relation was used in this project's discussion only as a familiar illustration of that relation, chosen because the founder raised it, and it was run through a symbolic algebra system purely to confirm that the illustration behaved as described.

For any public-facing document the recommendation is to drop the physics example entirely and use the project's own worked case instead. The vanishing of the prior flaw rate from the recursive risk update is exact, is native to this work, and demonstrates the identical structure without inviting any suspicion of over-reach.

## The quantity

Let S be a proposed simpler form, F the fuller form it claims to replace, and D the scope declared before either was proposed. Define the residual as the set of cases in D on which the two disagree, and the truncation rate as the size of that residual divided by the size of the scope.

A simplification is admissible when the truncation rate is zero across the declared scope, or when the residual is characterised, bounded, and filed as a separate claim carrying its own test.

Three cases from the project's own record illustrate the range. The vanishing of the prior has a truncation rate of exactly zero, established by symbolic proof: the risk after two passes computed from the prior and the same quantity computed from the intermediate state differ by exactly zero, and the prior does not appear in the update rule at all. The mass-energy restriction likewise has a truncation rate of exactly zero within its declared scope, and the quantity it omits outside that scope is the Newtonian kinetic energy, which is separately named and separately tested. The finding-absorption fix made during this session has a truncation rate of 0.397, established by enumerating 711 same-function pairs, with a 95 percent Wilson interval from 0.361 to 0.433 computed identically by two libraries. Zero lies outside that interval, so the fix is a truncation and was inadmissible as a simplification.

An important distinction emerged while tabulating those three, and belongs in the formalisation. A truncation rate of zero may be established in two quite different ways: by proof, meaning symbolic equivalence over the whole scope, or by enumeration of the scope. A confidence interval is appropriate only where the scope has been sampled rather than proved or enumerated. Attaching an interval to a symbolic identity is a category error, and the first version of the table in this analysis committed it.

## What this adds beyond the existing model

Three properties were established by constraint solving, with brute-force enumeration agreeing on every result. They are given here in order of how well each is grounded in this project's own record, which is the reverse of the order in which they were first presented.

The property that matters most is that the predicate carries no parameter. A scored formulation gives different verdicts under different weights: two weightings were found that rank the same pair of candidates in opposite orders. The predicate contains no weight, so no such disagreement is possible. This matters because the runner already carries 27 decision-shaping tunable quantities, including the convergence thresholds, the two re-injection rates, the score floor, the similarity threshold and the severity floors, of which only 7 are documented as pre-registered or explicitly ruled, a rate of 0.26 with a 95 percent Wilson interval from 0.132 to 0.447. That count is a lower bound, since it covers one module and cannot detect an unnamed literal inside a comparison. Every one of those numbers is a value somebody had to choose and defend, and several have already cost an explicit ruling. A parameter-free admissibility test adds nothing to that burden.

The second property is that the predicate cannot be hill-climbed. Searching the candidate space for a move that reduces requirement coverage while remaining admissible is unsatisfiable, because the only way to improve the predicate is to achieve the thing it measures. The equivalent search against a complexity score returns a witness immediately, with coverage falling from one requirement of five to zero of five while the score improves.

That second property should be weighted carefully rather than led with. The concern it answers was raised by two panel reviewers as a hypothesis about what a system told it is scored on brevity would do. Searching this project's record for an instance of a model dishonestly optimising a measured quantity returns none. What the record does contain is five containment events, in which a model acted outside its permitted boundary: a reviewing model mutating the target under review and restoring it, a model writing to the repository, a sandbox escape, panel agents editing the repository during a run, and several mutations logged by the integrity watcher. Those are a different class, some of them arising from a model attempting a helpful repair in a place it should not have been able to write. Treating containment events as evidence of gaming overstates how often gaming has occurred here, which is not at all.

## Where it belongs

It is not a new term in the recursive risk update, and it should not be one. It is an admissibility predicate applied at fix acceptance, together with a definition in the mathematical appendix. The appendix already contains twenty-nine statements of exactly this form, described there as reduction properties, none of which is verified by any test. The proposal is therefore not to invent machinery but to name a quantity the appendix already relies on, state how it may be established, and make it checkable.

The scope of the claim should be stated plainly. The test discriminates among candidate simplifications; it does not generate them, which is a limitation it inherits from the razor it descends from. It applies only to claims that a simpler form suffices; an ordinary fix making no such claim passes through the existing gate unchanged. And it can be gamed by declaring a narrow scope after the candidate is known, which is why the scope must be fixed by the brief beforehand. That defence relocates the vulnerability to the brief, where it is visible and reviewable, rather than removing it.

## On the broader speculation

The founder raised the possibility that work of this kind might say something about reasoning, logic or mathematics themselves. Assessed dispassionately, the concept is not novel: inter-theory reduction has been studied for over sixty years. What would be new is not the idea but its instrumentation, namely operating it as an executable acceptance gate inside a falsification harness and measuring truncation rates empirically across the outputs of several independent systems. No claim that this reveals something about the nature of mathematics is supported by anything established here, and none is made.

What is supported, and is worth having on its own terms, is that two words previously used as informal virtues now have an operational definition, a measurable quantity, and a decision rule with no free parameter.

## Evidence on the tooling question

The founder also proposed that a system lacking formal-logic tooling is impoverished, and enriched by having it. A direct measurement is available from this session. Eleven claims made in the course of this analysis were subsequently checked with a tool. Five were overturned or materially corrected by the check, giving a rate of 0.45 with a 95 percent Wilson interval from 0.213 to 0.720, identical across two libraries. The overturned claims include an entire proposed thesis about the nature of the failure pattern, a hypothesis about a dormant exit condition, a count inflated by three false positives, and a claim about the briefing history that a search of the archive refuted.

The denominator is biased and this must be stated: claims are tool-checked selectively, and several of the confirmed rows were verifications of other parties' claims rather than the author's. The figure is not a population error rate. What it does establish is that the checking step is not ceremonial, and that in this session every one of those five errors was caught before reaching the founder because something was executed rather than asserted.
