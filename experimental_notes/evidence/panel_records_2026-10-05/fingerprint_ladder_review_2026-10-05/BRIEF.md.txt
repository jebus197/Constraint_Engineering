# Review brief — the routing ladder's ordering, and 3 repairs made tonight

You are reviewing work done on 2026-10-05 by CC1. Two things are asked of you, and the
second matters more than the first. Your task is to find what is WRONG, not to confirm
what is right. Disagreement is preserved as information; do not converge for the sake
of converging.

## Part A — 3 repairs. Are they correct, and did any of them weaken a guard?

The full suite finished with 11 failures. 3 were attributable to CC1's own work the
same night and have been repaired:

1. **A name collision.** 8 new scripts under `scripts/*_2026-10-05.py` each defined a
   local function called `answer_help` that built an `argparse` parser.
   `bench/tests/test_fresh_clone_is_actually_run_2026-09-11.py` flags any script
   containing both `answer_help(` and `ArgumentParser`, because the project's shared
   `_cli_help.answer_help` answers `--help` first and would hide argparse's flag list.
   REPAIR: the local function was renamed to `_parse_args` in all 8.
   QUESTION: does the sibling guard
   `bench/tests/test_help_never_acts_2026-09-11.py::test_every_script_that_writes_answers_help`
   still cover these scripts after the rename? Its matcher only flags scripts that
   WRITE something, and its message says "or give the script a parser". CC1 concluded
   the rename is safe because these scripts are read-only and all carry parsers.
   Check that conclusion by execution rather than by reading.

2. **A swallowed exception.** `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`
   had `except Exception: pass` inside the leave-one-out loop that attributes
   convergence blockers. REPAIR: failures are now collected into `probe_errors` and
   reported, and the printed attribution says whether it is complete or a lower bound.

3. **Source-text assertions.** `bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py`
   caps the census of source-text assertions at 80; CC1's new tests took it to 83.
   REPAIR: all 3 were converted to EXECUTING checks rather than deleted. Two now read
   `run_experiment.__code__.co_names` and `co_consts`; one now runs the launcher's
   `--help` as a subprocess and also asserts an unknown `--seat-models` value is
   REFUSED. Each conversion was mutation-checked and 2 tests fail per mutation.
   QUESTION: is reading `co_names`/`co_consts` genuinely stronger than matching source
   text, or has CC1 swapped one proxy for another? Name the cases where it would give
   a FALSE PASS or a FALSE FAIL.

A separate instrument defect was found and repaired during this work: the script that
produced the headline figure "175 of 175 blockers rendered as SETTLED" had been
substring-matching finding ids against the rendered SETTLED block. After the defect it
measured was repaired, it returned 21 of 175 instead. It now tests membership in a
pinned historical status set and reproduces 175 of 175 exactly.
QUESTION: is pinning the historical set the right call, or does it make the script
unable to detect a future regression of the same class?

## Part B — the proposal. Attack it.

Read `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
in full. Summary of the situation it addresses:

`bench/routing.py` says in its docstring that it routes to stronger models "ordered by
capability fingerprint". That is the ONLY occurrence of the word fingerprint in the
file. The code ranks on `DEFAULT_FALSIFIER_STRENGTH`, a frozen tuple of vendor names
derived from Exp 42 in June 2026. Separately, `_update_observed_fingerprint` writes a
live per-model profile every round, consumed by `burst_planner.py`. The glossary
defines that profile as (D, v-bar, A, C) including a verification score; the 15 fields
actually written contain no verification score and no coverage dimension.

The proposal adds a provenance-gated falsification rate to the fingerprint, records it
in shadow, and promotes it to the ladder only on evidence, retaining the frozen order
as prior and cold-start fallback.

Specific questions, and please answer each explicitly:

1. **The selection effect.** The ladder routes findings the weak models could not
   resolve to the strong models, so a strong model is measured against a harder
   population. CC1 states this as the strongest objection and recommends measuring on
   FIRST-PASS falsifiers only. Is that sufficient? Does it measure the wrong construct?
   Propose a better mitigation if you have one.

2. **The provenance gate.** On Exp 55, Gemini scored 2 of 2 CONFIRMED with both
   falsifiers DETACHED (reading nothing, restating the document from memory), while
   DeepSeek scored 0 of 2 with genuine readers that ERRORed on a missing file. A naive
   confirm-rate ranking inverts the correct order. Is gating pool entry on
   `scripts/competence_provenance.py` sufficient to prevent that, or can a detached
   falsifier still pass provenance?

3. **Is the construct right at all?** Confirm rate measures whether a model can
   DEMONSTRATE a defect. The ladder's job is to resolve findings others could not.
   Exp 42 measured the latter directly on a fixed residual set. Is a continuous rate
   actually a worse instrument than the frozen measurement it would replace?

4. **Anything CC1 has missed.** Other schema facilities for exploiting mixed-capability
   panels that are armed in config but inert in fact, or present in the real runners and
   absent from `bench/tools/run_simulated_experiment.py`. CC1 found 3 such gaps:
   `immune_memory_enabled` (13 of 49 real configs), `hardened_gate_enabled` (4 of 49),
   `apply_fixes_back_enabled` (1 of 49). Are there more? Is `burst_mode="off"` in the
   simulated runner defensible, given burst is fingerprint-driven?

## Measured facts you may rely on, with their producers

- Real panel finding rates differ: chi-square 280.0138, df 4, p = 2.213e-59.
  Simulated panel does not: chi-square 3.0084, df 5, p = 0.6987. NumPy and scipy agree;
  Wolfram independently confirms both. Producer:
  `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`.
- A uniform simulated panel presents 1 distinct model across the 5 rungs the ladder
  returns; the shipped seat map presents 2. Producer:
  `scripts/what_the_sim_runner_never_carried_over_2026-10-05.py`.
- 0 of 3473 archived round replies carry an id-addressed falsifier, Wilson
  [0.0000%, 0.1105%]. Producer: `scripts/in_round_falsifiers_are_discarded_2026-10-05.py`.

Verify any of these you doubt. If a figure does not reproduce, say so plainly — that is
the most useful thing you can return.

## Required output

State your position per question. Include a section headed `## Disagreement` with a
real body naming where you disagree with CC1 or with the other seat; "none" is not an
answer unless you genuinely have none, and say so explicitly if that is the case.
Where you make a claim about this repository, run something that demonstrates it and
quote the output.

## Deliver your fix as a FILE, at its real path

Any repair you propose must be WRITTEN INTO THE SANDBOX REPOSITORY TREE at the real
path it belongs at — for example `bench/routing.py`, or a new test under `bench/tests/`.
A fix left in prose, or written to scratch space, is destroyed at teardown and is not
delivered. If you propose a change to the proposal document itself, write the amended
file. Also write any script you used to check a claim, so the check can be re-run.

## State what would REFUTE you

For each position you take, state explicitly what evidence would overturn it. A
position with no refutation condition is an opinion, not a finding. Be concrete: name
the measurement, the file, or the command whose output would change your answer.

## Termination criterion

Stop when further work produces no new above-threshold findings — this project's own
diminishing-returns criterion. A finding is above threshold if missing it could cause a
real-world failure, an unsafe condition, or a wrong experimental conclusion. Do not
generate findings to fill space, do not nitpick style, and do not re-litigate design
choices that are merely not your preference. If you reach that point early, say so and
stop; an early stop with a stated reason is a better answer than padding.
