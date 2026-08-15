# Experiment 44 Preparation, Contested-Convergence Fix Design and Forward Plan

**Preserved into the repository 2026-08-06 02:15 .** The FIX 1–5 design. IMPLEMENTED — commit `1cec60d`, 2026-07-27. This is the design record, not a to-do list. Any citation describing it as pending is stale.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/Exp44_Fix_Design_and_Forward_Plan_2026-07-19.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `RECOVERY.md`, `CDSFL_Agent_Operational_Plan.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

Experiment 44 Preparation, Contested-Convergence Fix Design and Forward Plan

2026-07-19, 10:30 BST.

Register note. Technical register at the founder's standing request. This supersedes and corrects one point in the earlier overnight analysis file, which characterised the contested blocker as model disagreement. The data shows it is not disagreement. It is a sub-critical falsifier gap. The corrected diagnosis follows.


Part One. The corrected root cause, synthesised.

The residuals that blocked Experiment 43 from converging were two sub-critical findings, both severity zero point three zero, well below the critical-severity threshold of zero point seven. The first, C0013, carried a runnable falsifier whose execution errored, giving a falsifier verdict of ERROR. The second, C0040, was a round-eight review summary that leaked into the registry as if it were a finding, carrying no falsifier at all. Neither is a model disagreement. There were zero unresolved CHALLENGE verdicts in the final registry. The panel was not arguing.

The mechanism is a category error in the runner. The falsifier gate and the capability-aware routing that resolve findings by runnable demonstration only engage for findings at or above the critical-severity threshold of zero point seven. Sub-critical findings never receive that treatment. So a sub-critical finding whose model-supplied falsifier errors, or which has no falsifier, cannot be resolved by the tool path. It sits in UNCONFIRMED status. And the contested_count function, via its grace-period path, counts UNCONFIRMED findings for two rounds regardless of severity. The convergence gate then fails on any contested count above zero. So an un-demonstrated sub-critical claim is given veto power over convergence, which directly contradicts the framework's own rule that an unfalsified claim earns zero corroboration.


Part Two. The core fix, and its verification.

Fix one. Exclude un-demonstrated sub-critical findings from the gate's contested count. A finding below the critical-severity threshold that is UNCONFIRMED with an errored or absent falsifier has not been demonstrated, is therefore not a confirmed defect, and must not gate convergence. It is instead logged to a residual queue and flagged for review.

This fix was verified two ways before any code was touched. First, a simulation replayed the actual Experiment 43 round data through the gate. Without the fix the gate never reaches three consecutive passing rounds, which matches the real run that ran the full fourteen rounds without converging. With the fix applied, the gate reaches three consecutive passes and converges at round six, because rounds four, five, six and seven failed on nothing but the contested count. Second, a z3 satisfiability check proved a safety invariant. Whenever a critical finding, at or above severity zero point seven, is contested, the fixed gate still fails. There is no counterexample. The fix relaxes the gate only for sub-critical un-demonstrated findings and never for criticals, so critical handling, and the existing irreducible-critical human escalation queue, are untouched.


Part Three. The supporting fixes.

Fix two. When a finding's falsifier returns ERROR, route it once to a stronger writer for a re-attempt, exactly as routing already does for un-confirmed criticals, then confirm or dismiss. No indefinite limbo.

Fix three. Harden the finding intake so a review summary or prose block without the required finding schema, a FINDING_ID with FIND and FALSIFIER fields, cannot register as a finding. C0040 should never have existed.

Fix four. Relax or make adaptive the max-contested-rounds threshold of five. Five rounds of real-cash compute to age out a trivial item is both wasteful and, against churning residuals, ineffective. With fix one in place this threshold matters far less, since sub-criticals no longer block.

Fix five. The founder's proposal, expressed on the directive side. Make clearing the outstanding residual queue an explicit part of the panel's role at round or run end, produce a working falsifier for an un-demonstrated finding, or explicitly dismiss the unfalsifiable. This is additive falsification discipline, more faithful to tools decide not votes, not a trim of the directive.

Fix one alone would have converged Experiment 43. Fixes two through five are robustness and cleanliness, and reduce the chance of sibling edge-cases in future runs.


Part Four. The Experiment 44 question, and the shake-out vehicle.

Experiment 44, per the operational plan, is a composition test with no new target, a synthetic combination of the Experiment 41, 42 and 43 outputs, a mechanical interface check. It has no single target file with a character count. Critically, a composition test does not exercise the convergence machinery these fixes touch. So Experiment 44 is not the right vehicle to shake out the convergence fixes. The right shake-out is a convergence run on a real target. The most direct is a re-run of the Experiment 43 target, the macrophage cell module, with the fixes in place, which should now converge cleanly at around round six, confirming the counterfactual for roughly thirty five dollars. The recommendation is therefore to build the fixes, re-run the Experiment 43 target as the shake-out and the clean convergence result, and only then proceed to the Experiment 44 composition test.


Part Five. Extrapolation. On approaching autonomy.

Across Experiment 42 and Experiment 43 the pattern is consistent. Each experiment surfaces one specific mechanical edge-case, over-production first, then the sub-critical falsifier gap, and each fix is bounded and precedented, mirroring machinery that already exists. The surface of mechanical faults is itself following a diminishing-returns curve, the same principle the project measures for findings, now applied one level up, to the project's own mechanics. This supports a real trajectory toward progressively less human intervention per experiment.

A falsifiable prediction follows. If this meta-level diminishing-returns holds, Experiment 44 and beyond should surface fewer mechanical faults per experiment than 42 and 43 did, and the interventions should get smaller and more precedented. That is testable. Track faults-per-experiment. If it declines, the approaching-autonomy thesis holds. If it stays flat, there is a deeper issue.

The boundary condition. A literal one-shot of the remaining arc is not guaranteed, because new experiment types, the composition test, the factorial, the final integration, exercise different code paths and may surface new edge-cases. The honest position is progressively more autonomous with diminishing interventions, not certain single-shot completion. On self-improvement, the founder's observation that every run is already a form of it is correct. The system already reviews and repairs code, including, through these meta-fixes, its own convergence machinery. Turning the schema more fully toward self-improvement is the ouroboros and apply-fixes-back path, currently in shadow, plus the expanded model brief of fix five, and is correctly staged for after the foundation is solid.


Part Six. Status.

No code has been changed. Under the discuss-before-proceeding discipline, this design is presented for the founder's decision. On approval, the fixes are implemented as a Find-Follow-Analyse-Fix-P-pass cycle with regression tests, each traced through the code independently rather than trusted from the model panel, followed by the shake-out re-run.


Written under CDSFL note standard v1.2 (14 May 2026), technical register at founder request.
