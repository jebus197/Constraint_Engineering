# None of the core directive reaches any model, and the caps forcing that are unjustified

**2026-10-13, 21:34 BST.** Commit `d189488a`, branch `sim/shakedown-2026-09-29`, pushed.

**Audience: a reader who can follow a file path but was not in the session.** The unedited panel replies are in `His_Rulings_FULL_RECORD_2026-10-13.md`. Key paths named here: `bench/directives/universal/cdsfl_core_formal.md` (27,803 chars, 15 sections), `bench/directives/universal/cdsfl_operational.md` (46,374 chars), `bench/cdsfl_registry/composer.py` (`PHENOTYPE_TRANSFORMS`, `max_directive_chars`, `_load_universal_directive`), `experimental_notes/CDSFL_Directive_Pruning_Review_2026-07-18.md`, and the guard `bench/tests/test_falsifier_C0040_universal_directive_2026-09-10.py` (8 passed).

---

None of the core directive reaches any model, and the caps forcing that are unjustified

2026-10-13, 21:34 BST. Commit d189488a.

WHY THIS EXISTS

The founder asked a question before going out: don't we have to actually do the panel review on what the core directive set should contain, in order to fully meet the project specifications, once the irrelevant historical chatter is trimmed out?

The answer is yes. But the measurement taken to answer it found something larger than the question assumed, and it changes what should be done first. That is the whole of this document: the answer to his question, the larger defect found while answering it, and the four decisions now waiting.


THE SHORT VERSION

He is right that a panel review has never been done. The only artefact that exists is a single-reviewer report from 18 July, it covers the wrong file, and its own second line says nothing in it was applied.

He is wrong that historical chatter is the lever, and so was the orchestrator. Measured, the chatter is 3 to 4 percent of those files. They are about 96 percent operative specification.

And the real state is worse than the 9 percent figure that prompted his question. Not 9 percent of the core directive reaches the models. None of its structure does. Zero of its 15 sections survive. What arrives is 2,734 characters of configuration key-value lines out of 27,803.

The caps that force that are round numbers with no measurement behind them, attached to names of models that are no longer the panel. So the first question is not what to cut. It is whether the cap is real at all.


WHAT THE REVIEW HE REMEMBERS ACTUALLY WAS

He recalled raising the idea of stripping out the historical back-and-forth that bore no weight on what the models were being asked to do, and recalled being told it was a good idea, and did not know whether anything had been built.

Nothing was built. There is one artefact: a section-by-section pruning review dated 18 July 2026. Three things about it matter. It was produced by a single reviewer, not by the model panel. It examines the operational directive file and not the core formal one. And its own second caveat reads, word for word, recommendation only, nothing is applied here. It was never applied.

So his instinct was sound and the scope he assumed was not. A panel review of what the core set should contain has genuinely never happened.


WHY CHATTER IS NOT THE LEVER

Every line of both directive files was classified by whether it carries a date or an incident marker, which is what historical narrative looks like in this project's writing.

In the core formal directive, 18 lines of 494 qualify. That is 3.6437 percent, with a 95 percent confidence interval from 2.3171 to 5.6858 percent, and 4.4528 percent of the file by volume. In the operational directive, 20 lines of 762 qualify. That is 2.6247 percent, interval 1.7054 to 4.0192 percent, and 3.0189 percent by volume.

The remainder is specification. The core file is 15 sections covering constraint classification, constraint precedence, the falsification loop, the proportionality gate, the corroboration model, the extended falsification structure, the survival predicate, epistemic marking, proactive verification, and convergence declaration. It carries formal notation. It is not conversation.

The back-and-forth he remembers is real, but it lives in the orchestrator's own instruction files, in the experimental notes and in the task list. It is not in what the models are sent. Trimming it would recover 3 to 4 percent of a file that needs to shrink by a factor of between 2 and 7 to fit the caps. It is worth doing for its own sake. It will not solve this.


WHAT THE MODELS ACTUALLY RECEIVE

This was executed against the live code, not read off a note, and the guard that covers it passes with 8 tests.

The core formal directive is 27,803 characters in 15 sections. Every one of the five models receives 2,734 characters, which is 9.8335 percent of it. Zero of the 15 section headings survive, with a 95 percent interval from 0 to 20.3883 percent by one method and 0 to 21.8019 percent by another. What arrives in their place is a block of configuration key-value lines.

All five models get this reduced form always, not occasionally. The full text is 27,803 characters and the most generous cap is 12,000, so the condition that triggers the reduction is satisfied unconditionally. The code's own comment describes a full-text branch for large-context models, and no model in the panel can reach it.

There is a second file that does arrive intact. The operational directive, 46,374 characters, is appended in full and is exempt from the caps. But it covers only 6 of the core file's 15 sections. Among the nine it does not cover are the section on runnable falsifiers for critical findings, and the section titled falsifier integrity, do not reach for the answer.

Those are the two sections most directly about the property this whole project exists to establish. Neither reaches any model.


THE CAPS HAVE NO JUSTIFICATION ANYWHERE

The per-model limits are 4,000, 6,000, 8,000 and 12,000 characters, with a default of 8,000. A search of the code and of the documentation finds no measurement, no cited context window, and no stated reason for any of those numbers. They are round.

They are also attached to model labels that are no longer the panel. The labels name an Opus 4.6, a ChatGPT 5.4, a Codex 5.3, a DeepSeek version 3 and a Gemini 3.1 Pro. The panel today is Opus 4.7, Codex 5.3, Gemini 3.1 Pro, GPT 5.5, DeepSeek version 4 Pro, and Fable 5.1. Fable, which did half of today's panel work, has no entry at all.

This is why the sequencing matters. If those caps do not correspond to any real limit, then raising or removing them delivers the entire specification and closes the defect with nothing cut and no rewriting of anything. That is a much smaller and much safer change than deciding what parts of the project's own specification to discard, and the next simulated run can test it directly.


WHAT WAS DONE EARLIER TODAY, BRIEFLY

The mechanical directive pruner is retired, on his ruling. His two grounds were that there is no way of knowing what it feeds the models, and that the models should receive the same core directives every single time an experiment runs. Both were measured and both hold. On the pruner's own objective, deleting text can only make the figure it optimises worse, which an automated theorem prover returns as unsatisfiable and three other tools confirm. On determinism, the five seats carry four distinct density budgets, so the deletion set differs by seat: the same experiment fed different directive text to different models and no record said which text any seat received.

Nothing was deleted. The pruner remains reachable by a flag so the lean-versus-full comparison can still be run. Verified on the real composition path: with the retirement in force, zero of 50 compositions lose a domain directive, against 10 of 50 when the flag is switched back on. Flipping any single one of the five default sites turns two tests red.

The free panel also refuted four of the orchestrator's five proposed fixes, which is the reason for running it. The sharpest was on severity: at the 0.7 critical threshold the formula collapses, so that being critical is exactly equivalent to being a hard-constraint violation that a tool has confirmed with a stated confidence at or above 0.7, and within that single surviving case the computed severity equals the model's stated confidence exactly. The founder's objection that a computed severity would be the opposite of a vote therefore holds for eligibility and fails for magnitude.

And the reader that extracts his written responses was losing his words again. His first annotation of the day ran to 1,053 characters and the reader returned 97 of them, cutting at an embedded hash mark. The lost text carried the instruction to propose fixes before going to the panel. It is repaired, 946 characters recovered, 522 annotations unchanged across 84 files and exactly one lengthened.


WHAT NEEDS HIS RULING

DECISION 1. The sequencing. Establish whether the directive caps are real before commissioning a panel review of what the core set should contain. If the caps are fiction, the content review becomes an improvement rather than a necessity, and the specification does not have to be cut at all. The recommendation is to settle the cap question first, in the next simulated run.

DECISION 2. Whether a finding the routing ladder never reached should enter the halt queue. If it does not, whole classes of fault can go unresolved. If it does, a run can be blocked by something nothing in that run could ever have resolved. The panel measured the churn he feared at an upper bound of 6.58 percent of archived findings, falling to 4.35 percent once a duplicated archive is excluded, with 75 of the remaining 118 cases sitting in a single run from April. His second fear is smaller than it felt, and largely historical.

DECISION 3. Which prose target the next simulated run should carry. The admissibility flag is already switched on in that run's configuration and is inert, because the run's default target is a Python file and the prose path is never taken. Without a prose target the flag tests nothing and the promotion decision has nothing to stand on. Choosing the target is an experiment-design decision.

DECISION 4. Confirmation that the simulated run is next, which he has already ruled, once the panel's fixes and the orchestrator's own are applied. They are applied and tested as of this commit.


STATE

Branch is the simulation shakedown branch, commit d189488a, pushed, working tree clean. State was saved before this document was written, on his instruction, with all four completeness checks passing. The affected test surface is 185 passing across 13 suites, and the pre-commit gate is 510 passing.

Written under CDSFL note standard v1.7 (26 August 2026).
