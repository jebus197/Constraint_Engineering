# Two Things Called Simple: Codifying The Kind Worth Having

**2026-09-02 19:22 BST** — analysis, no code change.

## The distinction that was being missed

There are two unrelated properties both called simplicity, and the project has been optimising the wrong one.

The first is cost simplicity: a small artefact. Few lines changed, few files touched, low blast radius. It is a property of the thing itself and it is cheap to measure. This is the quantity the harness's re-injection rate was built to carry, and the quantity that a directive to make the smallest change would select for.

The second is compressive simplicity: a short statement with wide reach. The mass-energy relation is the standard example. It is four symbols and it governs an enormous range of phenomena. It is not small because something was left out; it is small because it captures the structure exactly. This is a property of the relationship between a statement and the domain it covers, not of the statement alone.

The founder's position is that the second is what the project should aim for, and that in that regime simplicity and sufficiency do not compete: such statements are simple and demonstrably sufficient at the same time. That is correct, and it explains the coin metaphor precisely. For a statement that has captured the real structure, compactness and completeness arrive together. They come apart only for statements that have not captured it, where compactness was bought by dropping coverage.

One qualification, made dispassionately. The mass-energy relation is sufficient within a declared scope and not outside it. Symbolic evaluation of the full relativistic relation confirms the reduction is exact when momentum is zero, and that away from zero the two forms differ by a term equal to the Newtonian kinetic energy. Sufficiency is therefore always relative to a stated domain. This strengthens rather than weakens the principle, because it names what a legitimate simplification must do: declare the domain over which it is exact.

## The codification already exists in this project

The mathematical appendix contains twenty-nine statements of the required form. They are called reduction properties, and each says that a richer formulation collapses exactly onto a simpler one under stated conditions. The most important is the vanishing of the prior flaw rate from the recursive risk update: once the current risk estimate exists, the prior plays no further part, and the update depends only on the present state and the effectiveness of the next pass. Symbolic evaluation confirms this is exact, not approximate. The risk after two passes computed from the prior and the risk after two passes computed from the intermediate state differ by exactly zero, and the prior does not appear in the update rule at all. A forty-digit numerical evaluation agrees to seventeen decimal places.

That is compression, and it is distinguishable from truncation by a mechanical test. The prior was removed by derivation. Nothing that depended on it was lost, because nothing depends on it.

## The state of that codification

Of the twenty-nine reduction properties claimed in the appendix, zero are verified by any test. The unverified fraction is therefore 1.00, with a 95 percent Wilson interval from 0.883 to 1.000. Targeted searches for each specific reduction condition, including the vanishing prior, the delivery-feasibility limit, the decomposition-yield limit, the deferral limit, the severity-weighting collapse and the scope-expansion limit, return no matching test in any test module.

This is not because the checks are hard. Two of them were carried out during this analysis in about ten lines of symbolic algebra each. The caveat is that the two chosen were the two most self-contained; others involve pipeline state and would cost more.

## The operational rule this yields

A simplification is admissible when the simpler form and the fuller form agree exactly across the declared scope, or when the difference between them is named, bounded, and filed as a separate claim carrying its own test.

The second clause is what the relativistic example teaches. The term the compact form omits is not waste. It is the Newtonian kinetic energy, a nameable quantity with its own domain of validity and its own experimental support. A legitimate simplification always leaves behind something that can be named. This is the same rule one panel reviewer proposed on 2026-08-23 in the language of patches: sufficiency gates, the minimal sufficient candidate wins among those that pass, and anything a larger candidate covers beyond the brief is filed as its own finding with its own test. Relativity and the acceptance policy turn out to want the identical discipline.

The compact statement of the rule is that a simplification which cannot name what it dropped is not a simplification. It is a truncation.

## The test applied to a real failure

The finding-absorption fix made earlier in this session is the worked negative case. The simple rule, based on textual signature similarity, was proposed as a sufficient stand-in for the full rule, based on difference between falsifiers. Enumerating the same-function pairs on which the two rules disagree gives 282 of 711, a disagreement rate of 0.397 with a 95 percent Wilson interval from 0.361 to 0.433, computed identically by two libraries. A reduction requires exact agreement within scope, so the admissible value is zero, and zero lies outside that interval. The verdict is unambiguous: not a reduction, and rejected as a simplification.

Running that check would have cost one enumeration over pairs already present in the registry. Not running it cost a shipped fix, a panel round, and a second corrective commit.

## Boundaries of the proposal

The rule tests candidate simplifications; it does not generate them. That limitation is shared with the razor it descends from, and it means the rule belongs at the point of selection, not the point of search.

The rule can be gamed by declaring a narrow scope after the fact, so that a weak simplification appears exact within it. The defence is that the scope must be the requirement set fixed by the brief before any candidate is proposed. This does not remove the possibility of gaming; it relocates it to the brief, where it is visible and reviewable.

The rule applies only to claims that a simpler form suffices. A fix that makes no such claim is not exempted from anything; it passes through the ordinary sufficiency gate as before.
