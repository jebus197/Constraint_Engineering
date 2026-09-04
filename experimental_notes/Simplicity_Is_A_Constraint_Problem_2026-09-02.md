# Preferring Simplicity Over Sufficiency: What Was Asked, What Was Briefed, And What The Machinery Actually Does

**2026-09-02 19:08 BST** — analysis, no code change.

## The question, and what was actually put to the panel

The founder's question is whether the harness author prefers simplicity over sufficiency, on the grounds that in engineering these are distinct though related quantities. The founder asked for four things: whether the distinction is valid, how it should be quantified, what lessons follow, and how they should be applied.

The record shows the question was put to a panel twice, and narrowed both times.

On 2026-08-18 the Stage 1 audit brief (`bench/logs/confer_stage1_audit_2026-08-18/BRIEF.md`) used the compound phrase "simplest sufficient fix" four times and the word "simplicity" zero times. The two terms were never separated. Question 2(d) asked whether the compound should be formalised as a parsimony term or left in the directives, which is a question about where a phrase belongs, not about whether the two quantities differ.

On 2026-08-23 the convergence panel brief (`bench/logs/convergence_panel_2026-08-23/BRIEF.md`) did separate them, and preserved the founder's framing verbatim: sufficiency and simplicity "are not the same quantities, although they remain two sides to the same coin." That brief asked whether the schema should treat them formally and, if so, by what device. Two of the founder's four questions were carried: how to quantify, partially, and where to apply, partially. Validity was not put to falsification, because the brief instructed that the framing be preserved rather than tested. Lessons were not asked for at all. The brief also noted that every existing anchor governs how the assistant works rather than how the harness adjudicates, and then scoped the question to the harness, dropping the assistant side, which is the side the founder was asking about.

## The panel's direct answer, 2026-08-23

Two reviewers answered, and both gave a substantive quantification.

The first located the trade already present in the mathematical appendix. Sufficiency is the benefit side of a fix cycle, and simplicity is the cost side, expressed as the re-injection rate, the probability that a fix introduces a new defect elsewhere. The comparison between them is the inequality that the appendix already carries. Its verdict: the coin does not need inventing, it needs naming, and no new status, score, gate or admissibility rule should be added.

The second split them by kind. Sufficiency is a truth property and is already mechanised by the two-sided gate. Simplicity is not a truth property, because a simpler patch is not a truer one, and admitting it into adjudication would let a preference influence a truth decision. Its rule was: sufficiency gates; among the candidates that pass the gate, the minimal sufficient patch wins; and anything a larger patch fixes beyond the brief is filed as its own finding with its own test. That final clause is the operative one. It says that the extra work a larger patch does is not complexity to be discarded but a second sufficiency claim that must earn its own gate pass. Discarding it silently is not simplification; it is rejecting an untested claim without recording that a claim was rejected.

## What the machinery actually does

Three checks were run against the current codebase rather than against the panel's description of it.

The break-even re-injection rate given in the appendix was re-derived symbolically from the three-phase update in the runner. The appendix formula is exactly correct: the difference between the derived expression and the published one simplifies to zero, and a numerical root-finder agreed with the closed form to within two parts in ten thousand billion across two thousand random parameter draws.

The re-injection rate as implemented is blind to the complexity of the fix. Its partial derivative with respect to any complexity variable is identically zero, because no such variable appears in it. Its only inputs are two constants and the fix's success indicator. Two fixes with equal success and wildly different blast radius therefore receive identical risk. This is the collapse of the two quantities into one, written into the equation: the model currently assumes that a fix which worked is a fix which was safe, regardless of how much it touched.

The hard exit that the appendix specifies, under which a cycle whose re-injection rate exceeds the break-even value is net harmful and fixing should stop, appears nowhere in the runner. Its only occurrences in the repository are in the appendix and inside briefs sent to models. The module written to supply the missing complexity measurement has tests and no caller in the pipeline; its single non-test reference is an inventory script that catalogues it. Ten days after the panel identified this as the one item whose absence costs bench compute, it remains unwired.

## The formal shape of the error

Stated in engineering terms, sufficiency is a constraint and simplicity is an objective. The correct form is to minimise complexity subject to meeting every requirement. Preferring simplicity over sufficiency is the category error of converting the constraint into a penalty term and then trading it away.

A constraint solver was used to compare the two formulations on a concrete candidate set of four fixes. Under the constrained form the minimal sufficient candidate is selected for every weighting. Under the scalarised form, where uncovered requirements are merely penalised, the insufficient but cheap candidate wins for every penalty weight below a threshold. Under the opposite scalarisation, where total coverage is rewarded against a complexity cost, the over-complex candidate that fixes things nobody asked for wins for every cost weight below a threshold. A brute-force enumeration confirmed the constrained result independently.

This matters because the project's record contains failures in both directions, and they had looked like two different problems. A finding-absorption fix closed the easy case and left forty percent of the real one open. On a separate occasion both panel reviewers proposed populating a scratch directory and overriding the working directory, and the founder's simpler ruling proved strictly better because existing machinery already handled the case. Under-shoot and over-shoot are the same category error at different weights. Neither is cured by resolving to be more careful about size.

## Whether this is specific to one model

The founder's proposal is that the failure is not confined to the harness author. The record supports this, with the caveat that attribution from commit subjects is not independent coding.

Across 309 commits from 2026-08-14 to 2026-09-02, thirteen record an earlier fix proving insufficient, a rate of 4.2 percent with a 95 percent Wilson interval from 2.5 to 7.1 percent, computed identically by two libraries. Three further candidates were rejected on inspection as false positives, being experiments that converged at a third round rather than fixes that failed. Four of the thirteen are self-attributed; the interval on that share runs from 0.13 to 0.58 and spans one half, so the record does not establish that insufficient fixes are disproportionately the author's.

Three model-side instances of the identical failure are documented explicitly. One reviewer's claim that every prose target in the archive was affected was recorded as overstated, a universal asserted after a partial check. Both reviewers proposed the more complex fix that the founder's simpler ruling beat. And one reviewer refuted its own objection by measuring it, having stated it before measuring.

The consequence is structural. A panel asked to adjudicate whether a fix is sufficient is composed of systems exhibiting the same failure. That is the same objection an earlier panel raised about a different failure mode, where five models agreeing on an inherited error produces confidence rather than correction. Sufficiency therefore cannot be established by asking, however many are asked. It has to be established by a gate that executes.

## What follows

The lesson the founder asked for, which neither brief requested and therefore neither panel supplied, is that the operating directive is not an instruction about size. It is an instruction about order. Establish the feasible set first, by checking coverage of every requirement; only then prefer the smallest member of it. The project's own constraint discipline already encodes this, classifying hard constraints as fixed during exploration and permitting free choice only within the soft space, with elegance as a tie-breaker among candidates that satisfy the hard set. Applied to fixes, sufficiency is the hard constraint and simplicity is the tie-breaker. The directive was never ambiguous; it was read as a size rule instead of an ordering rule.
