# Where the Project Stands After a Sixteen-Day Break

2026-05-09 20:55 BST

## What this note is

This is the plain-English companion to the technical record of the project's state when the founder resumed work after a sixteen-day pause. The pause covered 23 April through 9 May 2026, and it was driven by health and personal matters rather than by anything in the project itself. The note exists so that a returning reader (the founder, or anyone else who picks the project up cold) can re-anchor quickly on what was done before the break and what was waiting on the other side.

## What the project is, in case the reader is cold

The project is an experimental study of how language models, working under explicit constraints and a structured discipline of trying to disprove their own conclusions, can be steered to do genuinely rigorous technical work rather than merely sounding rigorous. The discipline is called CDSFL, which stands for Constraint-Directed Self-Falsification Loop. The current experimental arc runs from Experiment 40 through Experiment 54 — fifteen experiments in sequence — followed by a longer benchmark run against a set of frontier science and technology problems. Experiment 40 is the first in the arc and serves as the gate that opens everything that follows. The runtime code for Experiment 40 was finished and tested in late April; only founder-judgement decisions remained outstanding when the pause started.

## What the break did not change

The repository sits on the same development branch and the same commit as it did when the founder last engaged on 23 April 2026. No new commits landed during the sixteen-day gap. The test suite still runs at 1,311 collected tests, of which the fast subset (excluding five long-running or command-line-blocking files) passes 907 out of 907. The single test that has been hanging since well before the break still hangs on the same cause (it calls out to a small command-line model that takes about fourteen seconds per call across three rounds with many findings per round, which is a known operational characteristic, not a project regression).

All the pre-launch work that landed in April is still in place. Three named code fixes (corrections to the mathematics sandbox, the activation of a more general mathematical wrapper running in a parameter regime that reduces to a simpler form, and a debug-time safety check on the same site) all remain present. The audit-logging enrichment that captures per-judgement detail from three shadow-mode specialists (physics, chemistry, engineering — currently observation-only, will graduate to live status experiment-by-experiment later in the arc) is still in place, with the small key-name bug that was caught and fixed during the overnight gap-closure shift on 22 April still corrected.

## What was waiting on the founder when work resumed

Four items had been left open at the end of the 22 April founder oversight session. None of them is code. All four are judgement calls that the agent cannot make alone.

The first is the scope of a focused follow-up review round, where the panel of five large language models examines specific items not yet under their review. The agent had a proposed scope; the founder needed to approve, amend, or substitute it.

The second is what to do about three specific gaps in the runner code that the project deliberately leaves un-implemented at design time. These three concern arbitration rules for cases where specialist subsystems disagree, where a merge between their outputs deadlocks, and where a burst-dispatch mode would need a convergence override. The Popperian discipline of the project says: wait for actual evidence from later experiments and write the rule from observed cases. The question on the table was whether to follow that discipline, implement the rules now in a fresh pass, or accept deferral with explicit flagging in the launch checklist.

The third is the disposition of four residual concerns from the same April oversight session. Each is small in isolation but each was nagging: a cross-check that an earlier gate experiment was correctly recorded as complete; an assessment of whether tracking one particular mathematical measurement over time would block any planned experiment; a documentation amendment to formalise a scientific-notation rule that had caused a misreading; and a sweep through the project documentation to apply the maturity-state vocabulary consistently. Block the launch on these, or defer to post-launch housekeeping?

The fourth is the launch approval for Experiment 40 itself. The runtime is ready. The question is whether the first three items above gate the launch, or whether the launch can proceed while the focused review round runs in parallel.

## Two integrity notes worth re-stating

The discipline of waiting for evidence before pre-registering arbitration rules (for the three gaps mentioned above) is genuine design integrity — rules built from observed cases beat rules guessed in advance. It is also in part cover for some overnight judgement calls during the 22 April shift that would have benefited from founder oversight or a second model's review at the time. Both characterisations are true; it is worth not letting the first conceal the second.

Panel-review status across the pre-launch surface is uneven. Several items had been reviewed by the full panel (the three code fixes, the launch-gate preflight, the calibrator design, the arc scope and ordering, the native-synthesis commitment for the four later test articles, the shadow-mode non-distortion principle, the policy of promoting shadow elements to live as soon as evidence permits). Several items had not been reviewed by the panel (the code-correctness fix to the audit logger, the design briefs for the four synthesised native modules, the trigger specifications for the three deferred gaps, the test-coverage adequacy of three of the gap-closure items, and the lexicon wording in the maturity-state documentation). The focused review round in item one above was intended to close that review gap.

## The recommended path forward, as it stood at the break's end

If the goal is the shortest path to Experiment 40 launch with integrity intact, the natural sequence was: approve, amend, or substitute the focused review round scope; let the round return and use its outcome to inform the gap-path decision and the residuals disposition; then approve the launch on a clean documentary state. An alternative was to launch now and run the review round in parallel, since the runtime code is closed and tested.

The decision was the founder's, not the agent's.

## What this note exists for

This note is the re-orientation artefact for a returning reader. It does not advance the project; it states where the project stood when work resumed. The actual decisions and work that followed the break are captured in subsequent notes (a second review round on 10 May, a third on 13 May, and a comprehensive documentation sweep before the experiment dispatches).

Written under CDSFL note standard v1.2 (14 May 2026).
