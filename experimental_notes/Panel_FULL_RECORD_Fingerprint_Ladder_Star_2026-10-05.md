# The joint round on the routing ladder and the fingerprint proposal

Record written 2026-10-05T23:42:55+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The JOINT round of a star-topology panel review, dispatched 2026-10-05 04:49:13 BST on the cc2 seat alone, 0 paid dispatches. It completed in 3207.1 s across 2 attempts, returning 17,462 characters and 71 tool calls.

WHY IT WAS A JOINT ROUND AND NOT A SECOND BLIND ONE. The founder corrected the protocol mid-session: panel review runs in star topology, with a blind round per seat and a joint round once the blind replies are in, as the runners do. The blind round, `fingerprint_ladder_review_2026-10-05`, had returned a full review from the fable seat and nothing at all from the cc2 seat, which failed both attempts with 0 characters and 0 tool calls.

A BLIND RE-RUN OF THE cc2 SEAT PROVED IMPOSSIBLE, and that is itself the round's first finding. The brief asks the seat to review work done the same night, so its sandbox must contain that work, and that work had by then been annotated with the fable seat's findings in its own code comments. Removing the contamination would have removed the subject matter. A first containment attempt purged every path whose name carried the round identifier, reported zero survivors, and left the first seat's entire verdict readable through two documents named after their subject rather than the round. Blindness is a property of content, not of paths, and it has a shelf life: every blind reply must be collected before any of them is written into the tree.

THE SEAT SAW THE FABLE SEAT'S BLIND REPLY IN FULL, together with what CC1 had already done with it and the one repair CC1 had falsified, and was asked to attack all of it.

WHAT IT FOUND AGAINST CC1, ALL SUBSEQUENTLY VERIFIED BY EXECUTION. First, a repair reported as complete while its own guard was failing: the census of tests that assert on source text was reported at 80 with none belonging to that session, when it was 81 and the single extra entry had been added by that session, in a containment test written after the count was taken. Second, that raising the routing rung budget to 4 was a parity break whose property is never dispatched, since routing stops at the first confirmation, so the third rung runs only when the first two have both failed; the seat's words, and the charge is fair, were that CC1 used exactly that execution argument to refute the other seat and then failed to apply it to its own repair. Third, a provenance defect neither CC1 nor the other seat had raised: the script that decides whether a model's record is safe to rank on credits each confirmation to the model that reported the finding rather than the model that wrote the working test, affecting 1,370 of 16,500 archived entries, 8.3 per cent, in the direction that flatters precisely the models the ladder is designed to demote.

WHAT IT FOUND AGAINST THE OTHER SEAT. The fable seat had claimed that a check reading a compiled function's constants could be satisfied by a docstring containing the same words. The cc2 seat demonstrated this false by execution: membership in that structure is exact equality, not containment. CC1's original note was correct and the first seat had corrected a correct statement into an incorrect one. The first seat's proposed correction for the selection problem was judged the right strategy but unpriced and not deployable at the project's run cadence, and its claim that leaving the burst planner switched off is no longer defensible was judged premature by one dependency.

THE PROTOCOL EARNED ITS KEEP. A single seat produced a strong review containing 2 errors. The joint round caught both, found 3 further faults in CC1's own work, and surfaced a defect in a third script that neither of the other participants had examined. Disagreement was preserved rather than smoothed, which is the stated purpose of running without compelled convergence.

## Seats and cost

1 seat(s): `cc2`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

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

---

# JOINT (STAR) ROUND — the other seat's BLIND reply is below

The blind round is in. The fable seat answered blind and its reply follows IN FULL,
unedited. Your task is NOT to restate it. It is to say where it is WRONG, where it is
right and under-stated, and what it missed.

CC1 has already acted on parts of it and one of its repairs was FALSIFIED in doing so.
That exchange is given below too, so you can attack both.

Answer every question in the brief above in your own right, then add a section headed
`## Where the other seat is wrong` with a real body. Agreement is permitted but must be
reasoned; "I concur" is not an answer.

## The fable seat's blind reply, verbatim

All green. I've reached the diminishing-returns point — further passes produce only sub-threshold observations. Final report.

---

# Verdict — seat Fable, 2026-10-05

Every repository claim below was demonstrated by execution in this turn; outputs quoted are from those runs.

## Part A — the 3 repairs

**A1. The rename (`answer_help` → `_parse_args` in 8 scripts): CORRECT, no guard weakened — but CC1's coverage conclusion is misstated.** Executed, not read: `test_fresh_clone_is_actually_run_2026-09-11.py::TestTheHelperIsNotUsedWhereArgparseAlreadyWorks` and all of `test_help_never_acts_2026-09-11.py` pass (12 passed). However, the sibling guard `test_every_script_that_writes_answers_help` does **not** "still cover these scripts" — it never examines them. Applying its own `WRITES` matcher to all 8: `WRITES=False` for every one, so they are **outside its population by design**, not covered-and-passing. Actual coverage was `test_help_is_answered_2026-09-11.py::TestTheWiringIsReal` — population membership confirmed for all 8 — but that vouches them **structurally** (source mentions `argparse`), and `answers_help` counts an `ArgumentParser` constructed anywhere, including inside a function nothing calls. A defined-but-never-called parser would pass every static guard while `--help` ran the measurement. I executed `--help` on all 8: `rc=0`, `usage:` first line, tree clean. **Delivered:** `bench/tests/test_measurement_scripts_answer_help_2026-10-05.py` — executes `--help` (exit 0 + usage line) and `--no-such-flag` (exit 2) on all 9 scripts (8 + my new one). 18 passed.

**A2. The swallowed exception: repair correct, and the same defect class survives one loop up — now fixed.** The leave-one-out `probe_errors` repair is sound (re-run: `probes that raised: 0`, 175/175 reproduces). But line 240–241 retained `except Exception: continue` around `reg.unverified_critical_count()` at the **run** level: a registry the counter cannot score vanished from the attribution with no trace while staying in `runs_total`, and the script still printed "the attribution is complete, not a lower bound" — a completeness claim computed from `probe_errors` alone. The suite's swallow-guard (`test_no_bare_or_silently_swallowed_exception_handlers`) only flags handlers whose entire body is `pass`, so `continue` escapes it. **Delivered:** fix in `scripts/the_blockers_are_shown_as_settled_2026-10-05.py` — `counter_errors` collected and reported; the completeness line now requires both lists empty. Re-run: 175/175 exact, guard suite passes.

**A3. `co_names`/`co_consts`: genuinely stronger than source text, but still a static reference proxy — one rung down, not a different kind of evidence.** It is immune to comments and commented-out code (a real improvement). Cases, precisely:

- **FALSE PASS (`co_names`):** the name referenced inside `run_experiment` without a reachable call — dead branch (`if False:`), a bare assignment, or a call behind a never-true flag. The compiled code object records the *reference*, not the *execution*.
- **FALSE PASS (`co_consts`):** `run_experiment`'s **docstring is `co_consts[0]`**, and any string literal (a log message) containing `"round_falsifier_reattachments"` satisfies the check after the persist line is deleted. A docstring can satisfy `co_consts` exactly where a comment cannot satisfy source-matching — the same defect class, narrower aperture.
- **FALSE FAIL (both):** a *correct* refactor moving the call or the persist into a helper (module-level or nested — nested code objects have their own `co_names`; the check does not recurse) breaks both tests. That is the "guards break on CORRECT changes" failure the census message warns about, at lower frequency.

I mutation-checked both probes myself: severing the call → `test_the_round_loop_calls_it` FAILED; deleting the persist key → `test_its_record_is_persisted` FAILED; restored, 4 passed. Note: **each mutation failed exactly 1 test, not the "2 tests fail per mutation" stated** — either CC1's mutations were coarser or the claim is overstated; the probes do catch their mutations either way. The call site is real and unconditional (line 16114). Verdict: acceptable conversions, correctly described as proxies; the behavioural form (this file's own `verdict` fixture pattern) remains the stronger standard where feasible.

**The pinned historical set: the right call.** The substring match was unsound in both directions (an id inside a `merged_into` pointer or another finding's description matched spuriously; the claim was always about status membership). Regression detection is **not** lost: the live status→section map is derived each run by calling `build_summary`, and — decisive — the repaired partition is pinned by an executing test, `test_status_partition_covers_everything_2026-08-30.py` (5 passed). The script's live print alone would be insufficient (it always exits 0); the test is what guards the regression.

## Part B — the proposal

**B1. First-pass-only is NOT sufficient, and its stated premise is false.** "A common population by construction" is wrong: each model writes first-pass falsifiers for *its own findings*, and the finding populations differ per model — χ² = 280.0138, p = 2.213e-59 (reproduced) is direct evidence. First-pass-only trades the routing confound for a self-selection confound, and it measures *demonstration of own findings*, not the ladder's construct (*resolution of others' residuals*). **Better mitigation: randomise a small audit fraction of rung assignments** and compute the shadow statistic on randomised attempts only — the only option that measures the ladder's own construct on an assignment independent of the ranking. Covariate modelling (option 3) cannot identify without the overlap randomisation provides.

**B2. The provenance gate is NOT sufficient. Demonstrated, twice.** `falsifier_style` is a source-text regex: `open("/dev/null")` as a decoy → classified `reads`; the word `open(` **in a comment** → classified `reads` (both executed). And the UNSAFE rule aggregated per *model*: 2 detached CONFIRMED + 1 reading REFUTED → `unsafe=False` (executed). A detached falsifier passes the gate by containing the vocabulary of reading. **Delivered:** per-confirmation accounting in `scripts/competence_provenance.py` (Exp 55 still exits 2 with `UNSAFE TO RANK ON`; all 13 pinned tests pass), plus the demonstration script. The regex hole cannot be fixed by text: gating requires **execution-derived provenance** (audit-hook recording of files opened during `reverify_falsifier`, or perturbed-target invariance — a verdict that doesn't change when the target does is detached by measurement). Also: `test_nothing_imports_either_script_into_the_runner` pins this script as RECORD ONLY; promoting it to a gate overturns a pinned design decision and must say so.

**B3. Yes — as a replacement, the continuous rate is the worse instrument.** Exp 42 measured the ladder's actual construct (residual resolution: 0/7 weak, 6/7 rung 1, 7/7 rung 2); a provenance-clean confirm rate measures a related but different one. Under the additive standard, a measurement of the wrong construct cannot displace a committed measurement of the right one. The supported composition: frozen order stays the decider; the shadow rate runs as **CUSUM drift detection**; an alarm triggers **re-running an Exp-42-style fixed-residual probe**; only that reorders. Rate = tripwire, probe = decider — "tools decide" applied to the ranking itself.

**B4. Yes, there is more, and one item I repaired:**
1. **The exercised ladder prefix was uniform even with the mixed bench armed.** `routing_max_rungs=2`; the top rungs are always drawn from {Codex-SIM, CC2-SIM, ChatGPT-SIM}; `DEFAULT_LADDER` mapped all three to `opus` → **0 of 6 source seats got a climb between two different models** (executed). "2 distinct models across the 5 rungs" was true and materially incomplete. **Delivered:** `Codex-SIM → fable` in `sim_dispatch_shim.py` (5 of 6 mixed — the maximum with CC2-SIM pinned to `opus`; derivation in the test docstring), pinned by `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py` with an anti-vacuity probe asserting the old map reads 0/6. All 18 pre-existing ladder tests still pass.
2. **The fingerprint store erases run provenance on every save.** All 11 files in `bench/fingerprints/` — real and `-SIM` alike — carry `experiment=study_run1b_2026-10-03`, one timestamp (executed), because `_save_fingerprints` writes back every loaded profile. The proposal's dimension would be persisted in a store where "which run measured this" is already unanswerable. Also no key contract: routing normalises `-SIM`, fingerprint consumers don't; the proposal must name the lookup key.
3. **`burst_mode="off"`: defensible as the parity default, no longer defensible as the only state.** Burst is fingerprint-driven; with a mixed bench now available, permanently-off burst leaves the burst planner in exactly the never-rehearsed state the routing ladder occupied before 2026-08-30.

All of this is written into the proposal file as an attributed review section.

**Measured facts:** all three reproduce exactly (χ² 280.013760 / 3.008403; p 2.213221e-59 / 0.6987; 0 of 3473, Wilson [0.0000%, 0.1105%]). Wolfram second check (local Wolfram Engine via `wolframscript`, attribution: Wolfram Language): Wilson upper bound 0.11048702870671313% — agrees.

## Disagreement

- **With CC1 on A1:** "the sibling guard still covers these scripts" is the wrong description. It skips them (`WRITES=False`); the rename is safe because the harm class doesn't apply, not because coverage persists. Coverage was structural-only until tonight's executing test.
- **With CC1 on B1:** mitigation 2's "common population by construction" is false, per the project's own χ² measurement. I reject first-pass-only as the recommendation and propose the randomised audit fraction.
- **With the proposal's promotion path (B3):** "shadow ranking does not distort" is the wrong promotion criterion; promotion should go alarm → fixed-residual probe → reorder. I also reject bundling with `immune_memory_enabled` absent a measured advantage of the composed work — shared machinery is a convenience, not a demonstration.
- **With the brief's framing of A3:** "2 tests fail per mutation" did not reproduce; my two mutations each failed exactly 1 test.

## What would refute me

- **A1:** output of `python3 -m pytest bench/tests/test_help_never_acts_2026-09-11.py` showing the 8 scripts in `test_every_script_that_writes_answers_help`'s offender-candidate set (i.e. `WRITES` matching them).
- **A2:** a demonstration that `unverified_critical_count` cannot raise on any archived registry shape — then the run-level handler is dead code and my fix guards nothing (it still costs nothing).
- **A3:** a mutation of `reference_runner_v3.py` that removes the *reachable* call yet keeps both wiring tests green without touching the test file — that would upgrade my "proxy" verdict to "broken proxy".
- **B2:** section 1 of `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py` failing to reproduce (it self-reports staleness via exit 1).
- **B3:** a committed measurement where the provenance-clean rate predicts residual-set resolution better than the Exp-42 probe predicts itself on re-run.
- **B4.1:** `rank_falsifier_writers` yielding a mixed 2-prefix under the old map — re-run section 4 with `Codex-SIM: opus` (the anti-vacuity test does exactly this and asserts 0/6).

## Delivered files

Modified: `scripts/competence_provenance.py`, `scripts/the_blockers_are_shown_as_settled_2026-10-05.py`, `bench/tools/sim_dispatch_shim.py`, `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md` (appended review). New: `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py`, `bench/tests/test_measurement_scripts_answer_help_2026-10-05.py`, `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`. Final guard sweep over the amended tree: 50 passed (help guards, swallow guard, source-text census, help-is-answered), plus 18 + 4 + 18 + 36 + 13 on the targeted files.

**Termination:** stopping here under the diminishing-returns criterion. The last pass (status-partition pinning check) produced confirmation, not a new finding; remaining observations (e.g. `n_attrib = [0]` as a 1-element list, the producer's "any of them in executable code: True" line) are below threshold. One caveat on my own evidence: this sandbox had no `.git`, so git-population guards ran against a scratch index I built from the working tree — in the real checkout the populations are the committed set, which CC1 should confirm includes tonight's files.

## What CC1 did with it, and the one repair that was falsified

Accepted and applied: the run-level swallowed-failure fix, and the finding that the
seat map left 0 of 6 source seats a same-model climb.

FALSIFIED: the seat proposed mapping Codex-SIM to the weaker model. That yields 5 of 6
mixed prefixes but 0 of 6 in the ladder's own direction, because rung 1 is the
STRONGEST writer and resolve_via_routing stops at the first CONFIRMED. It would
rehearse weak-then-strong, which the real runs do not execute.

What was done instead: DeepSeek-SIM (ranked LAST in DEFAULT_FALSIFIER_STRENGTH, 28%
confirm rate) moved to the weaker model — a correction toward faithfulness — and
routing_max_rungs raised to 4 for simulated runs only. Result: 6 of 6 mixed, 6 of 6
correctly directed.

Attack this. Is raising the rung budget defensible, or does it change what the
simulation rehearses in some way CC1 has not noticed?


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 71 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel fpl_star_2026-10-05) -->

Both χ² figures reproduce exactly. Writing up.

---

# Verdict — seat Sonnet, 2026-10-05 (joint round)

Every repository claim below was demonstrated by execution in this turn. Quoted outputs are from those runs. Wolfram Language (local Wolfram Engine, via `wolframscript`) ran as second falsifier on the probability derivation and agreed.

## Part A

**A1 — the rename is safe; CC1's stated reason is false, and the fable seat is right.** Executed the guard's own `WRITES` matcher and `answers_help` against all 9 of tonight's scripts (the brief says 8; all 9 carry `_parse_args`):

```
script                                            _parse_args  answers_help  WRITES   in guard population?
in_round_clearance_is_monotone_2026-10-05.py      True         True          False    NO - outside population
...  (all 9 identical)
```

`test_every_script_that_writes_answers_help` does not "still cover these scripts" — `WRITES=False` for every one, so they are outside its population by construction. The rename is safe because the harm class does not apply, not because coverage persisted. Behaviourally confirmed: `--help` on all 9 → `rc=0`, `usage:` as first line. This repo has no `.git`, so `tracked_scripts()`' `git ls-files` cannot run here; I applied the matcher directly instead.

**A2 — repair correct, and the fable seat's run-level finding is already in CC1's tree.** `scripts/the_blockers_are_shown_as_settled_2026-10-05.py` now carries both `probe_errors` and `counter_errors`, and line 325 requires **both** empty before printing the completeness claim. Correct.

**A3 — `co_names`/`co_consts` is genuinely stronger, and the other seat named the wrong false-pass.** Executed:

```
co_consts = ('A docstring mentioning round_falsifier_reattachments in prose.', ...)
exact-membership "round_falsifier_reattachments" in co_consts -> False
```

Tuple membership is **element equality, not substring containment**. A docstring or log message *containing* the token does not satisfy the check. CC1's comment ("a comment, a docstring or a commented-out call cannot satisfy either") is correct; the fable seat contradicted it and is wrong. The real cases:

- **FALSE PASS (`co_names`)**: the name referenced without a reachable call — `if False:`, a bare assignment, a call behind a never-true flag. The code object records the reference, not the execution.
- **FALSE PASS (`co_consts`)**: the *exact* literal in a non-persisting use — a membership test, a `del`, a key read. Narrower than source-matching, not zero.
- **FALSE FAIL (both)**: a correct refactor into a helper. Executed: moving the call into a nested function leaves the outer `co_names` as `()`.

So: one rung up, not a different kind of evidence. Correctly described as a proxy.

**A3, and this is my first above-threshold finding: the repair is INCOMPLETE and its own guard is RED.** CC1 reports "all 3 were converted" and the census back at 80. Measured:

```
census with ALL 2026-10-05 test files removed: 80
census with them restored: 81    cap in the guard: 80
the 2026-10-05 contributors:
    ('test_a_blind_round_is_actually_blind_2026-10-05.py', 'test_the_env_var_reaches_build', 203, ['PANEL_BLIND_OF'])
```

Baseline is exactly 80. Tonight's files add exactly 1 — a fourth source-text assertion that was never converted. `test_source_text_and_neighbour_audit_2026-09-11.py::test_the_class_has_not_grown_silently` **failed in the delivered tree**, and its failure also trips the DONE-marker check ("task A6 is marked DONE and names … a completion claim with no support"). Neither my files nor the fable seat's contribute. **Repaired**: converted to two executing checks (import with the env var set and read `_BLIND_OF` back; AST-count `panel_sandbox.build` call sites passing `blind_of` against the total, so a *new* unwired call site fails — a literal count of 2 could not detect that). Mutation-checked: removing `blind_of` from one call site → `1 failed, 14 passed`. Census now `10 passed`.

**The pinned historical set: right call, and regression detection is not lost.** Substring-matching ids against a rendered block was unsound in both directions. The live status→section map is still derived each run by calling `build_summary`, and the repaired partition is pinned by the executing `test_status_partition_covers_everything_2026-08-30.py`. The script's print alone would be insufficient (it always exits 0); the test is the guard.

## Part B

**B1 — first-pass-only is insufficient, and so is the randomised audit fraction.** "A common population by construction" is false: each model writes first-pass falsifiers for *its own* findings, and the populations differ — χ² = 280.013760, df 4, p = 2.213221e-59, reproduced exactly this turn. It trades a routing confound for a self-selection confound and measures "demonstrates its own findings", not "resolves what others could not".

The fable seat's randomised audit fraction is the right *identification* strategy and is **not deployable at this scale** — the seat did not price it. Routing fires only on un-confirmed criticals, the budget is 2, and rung 1 resolved 6 of 7 on the Exp-42 residual set. A randomised fraction of an already-rare event will not reach any usable minimum-sample threshold within the project's run cadence. Randomisation identifies; it does not estimate.

**My proposal**: the Exp-42 *fixed residual set* already is a common population by construction, not by assumption. Rate as drift detector only → alarm → re-run the fixed-residual probe → only the probe reorders.

**B2 — not sufficient, and it has a defect in the attribution that nobody raised.** The fable seat's two holes reproduce (I executed both):

```
decoy open of /dev/null            -> reads
the word open( in a COMMENT        -> reads
docstring mentioning read_text     -> reads
Gemini: n=3 confirmed=2 reads=1 detached=2   unsafe -> False
```

**New, and larger:** `analyse` keyed per-model on `source_model` — the model that *reported* the finding. When routing resolves a critical the falsifier was written by a **rung**, recorded as `resolved_by_routing`. Measured over the archive:

```
archived registry entries scanned: 16500
entries carrying resolved_by_routing: 1370
   source_model='ChatGPT-SIM'  resolved_by_routing='Codex-SIM'  n=165  <- gate credits 'ChatGPT-SIM'
   source_model='DeepSeek'     resolved_by_routing='Codex'      n=84   <- gate credits 'DeepSeek'
```

8.3% of all entries credited the falsifier to the model that **failed** to write a working one — and in the direction that matters: a strong rung's successful resolutions credited to the weak source model, flattering exactly the models the ladder demotes. The runner already carried the correct precedence in `_corrected_copy_owner`. The proposal's own §1 says "falsifiers **it** supplied", which is the rung. **Both repaired** in `scripts/competence_provenance.py`; 13 pinned tests still pass; new guard `test_the_provenance_gate_attributes_the_writer_2026-10-05.py` → 10 passed, including a test asserting agreement with `_corrected_copy_owner` by calling both.

Answer: **no**. A detached falsifier still passes, because `falsifier_style` is a regex. Only execution-derived provenance closes it.

**B3 — yes, as a replacement the continuous rate is the worse instrument.** Exp 42 measured the construct directly on a fixed set (0/7 weak, 6/7 rung 1, 7/7 by rung 2). Under the additive standard a measurement of the wrong construct cannot displace a committed measurement of the right one. And "the shadow ranking does not distort" is the wrong promotion criterion — distortion-freedom in shadow is not predictive validity.

**B4 — yes, there are more, and raising the rung budget is NOT defensible.**

*The budget.* Measured:

```
config-shaped JSON files scanned: 288
of those pinning routing_max_rungs: 0 []
RunnerConfig.routing_max_rungs default: 2
```

Rungs 3–4 are reachable **only** in simulation, and the literal sat immediately above a block headed *"PARITY WITH THE REAL exp45 CONFIG … Every value below differed, and each difference let the simulation behave in a way the run it is compared against structurally could not."* It is a new instance of the class that block exists to remove.

And the 6-of-6 figure is measured on a list that is never dispatched. Executed `resolve_via_routing`:

```
confirms at rung   budget 2                  budget 4
1                  ['opus']                  ['opus']
2                  ['opus', 'opus']          ['opus', 'opus']
3                  ['opus', 'opus']          ['opus', 'opus', 'fable']

candidate                                    mixed prefix  P(exec) 1st-pass  P(exec) residual
shipped map, budget 4 (CC1's repair tonight) 6 of 6        2.7542%           0.7857%
```

Rung 3 is dispatched only when rungs 1 **and** 2 both failed. Wolfram Language confirms `0.027541666666666662`. Under the residual rates Exp 42 actually validated (rung 1 → 6/7, rung 2 → 1/1) it buys **0.79%**. CC1 used exactly this execution semantics to falsify the fable seat and did not apply it to its own repair.

CC1 *is* right on one point, and I derived it exhaustively rather than conceding it: over all 64 two-model seat maps, **0** reach 6-of-6 mixed at budget 2, and the monotone ceiling is 5 of 6. So 6-of-6 genuinely needs a deeper budget. That is not the question the repair turns on.

**Repaired additively.** `--routing-max-rungs`, default `None` = the dataclass default. Parity is the default; a run that wants rungs 3+ asks, and the ask is recorded. Nothing removed. Wiring mutation-checked: deleting the pass-through → `1 failed, 25 passed`. I deliberately did **not** repartition `DEFAULT_LADDER` to the Codex-only map, even though it measures 8.3333% / 11.9048% (3.03× and 15.15× better, Wolfram-confirmed) — it moves 2 of 6 seats off the strong model, so it wins on ladder rehearsal and **loses** on per-seat capability fidelity. It does not dominate, so under the founder's removal standard it does not displace the shipped map. The honest residue: a 2-model bench cannot dispatch the ladder's cross-model handoff at parity.

*More inert facilities.* CC1's three reproduce at identical ratios (`immune_memory_enabled` 78/288 ≈ 13/49; `hardened_gate_enabled` 24/288 ≈ 4/49; `apply_fixes_back_enabled` 6/288 ≈ 1/49). Additional: **`panel_cwd` (72 of 288 ≈ 12 of 49)** — the confinement control the falsifier-integrity directive names as one of its four mechanical defences; `context_files` (78), `wall_clock_cap_s` (270), `target_kind` (36), `exhausted_round_threshold` (18), `gamma_alt_threshold` / `gamma_alt_consecutive_zero_crit` (6). `panel_cwd` is the one above threshold: simulated stand-ins carry Bash and are not confined the way real panel routes are.

*`burst_mode="off"`.* Defensible **today** and for a reason neither CC1 nor the fable seat gave: burst is fingerprint-driven, and the fingerprint store carries no verification or coverage dimension at all, so a simulated burst would plan from context-capacity fields only. Arming it before the fingerprint has the dimension this proposal adds would rehearse a planner reading the wrong inputs. The fable seat's "no longer defensible as the only state" is premature by one dependency.

## Disagreement

- **With CC1 on A3 completeness.** "All 3 were converted" and "the census is back at 80" is wrong. It is 81, a fourth assertion was left unconverted, and the guard being repaired was failing in the delivered tree. Measured with tonight's files removed: exactly 80. This is the finding I weight highest in Part A, because the repair's *own instrument* reported the failure and the report said otherwise.
- **With CC1 on the rung budget.** Raising it to 4 is a parity break of the class the adjacent block exists to remove, and the property it was raised to achieve is not dispatched: 2.75% / 0.79%. CC1 applied execution semantics to refute one seat and not to itself.
- **With CC1 on A1's framing.** The sibling guard skips these scripts; it does not cover them.
- **With the proposal's §2.** Gating on `competence_provenance.py` is necessary and not sufficient, and until tonight the script also credited 1370 archived entries to the wrong model.
- **With the proposal's §4 promotion criterion.** "Shadow ranking does not distort" is not evidence of predictive validity.
- **With the proposal's open question 3.** Do not bundle with `immune_memory_enabled`. Shared Beta-Binomial machinery is a convenience; the composability standard requires a measurement, and none exists.

## Where the other seat is wrong

- **A3, `co_consts` — wrong on the mechanism.** "A docstring can satisfy `co_consts` exactly where a comment cannot satisfy source-matching" and "any string literal containing the token satisfies the check" are both false. Executed: `"round_falsifier_reattachments" in co_consts` → `False` for a docstring and a log message both containing it. Tuple membership is equality. CC1's comment is right and the seat corrected a correct statement into an incorrect one. The real false pass is the *exact* literal in a non-persisting use — narrower, and still worth naming.
- **B1 — right strategy, unpriced.** The randomised audit fraction is the correct identification move and the seat did not ask how many randomised attempts the ladder produces. At `max_rungs=2` with rung 1 resolving 6 of 7, a random subset of an already rare event will not reach a usable sample. Right in principle, not deployable; the fixed-residual probe is.
- **B4.1 — correct diagnosis, falsified repair, and CC1's counter is also falsified.** The seat found the real defect (0 of 6 source seats got a cross-model climb) and its fix inverted the direction. CC1 was right to falsify it and then committed the mirror error. Both repairs optimised a prefix neither of them dispatched.
- **B4.2 — right and under-stated.** The fingerprint store erasing run provenance is worse than "which run measured this is unanswerable": it means a shadow-recorded dimension cannot be *attributed* to a run, so the shadow comparison the proposal's §4 rests on has no unit of analysis. The seat reported the symptom and not that it blocks §4.
- **B4.3 — premature.** See `burst_mode` above: the dependency runs the other way.
- **Right and under-stated on B2.** The seat found the aggregation hole and stopped at the classifier. The attribution defect is 8.3% of the archive and runs in the direction that corrupts the ladder's own ordering.
- **Its self-reported caveat is correct and applies to me too**: no `.git` in this sandbox, so git-population guards cannot run here. I did not substitute a scratch index; I applied the matchers directly and said so.

## What would refute me

- **A3 incompleteness**: `python3 -m pytest bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py -q` passing on CC1's *pre-my-edit* tree. It did not — `assert 81 <= 80`.
- **The rung budget**: a real config pinning `routing_max_rungs > 2`. `test_no_real_config_pins_the_budget` re-measures this every run and fails if one appears. Or: a committed measurement that rungs 1–2 fail more often than Exp-42's rates imply, which would raise 2.75% toward usefulness.
- **The execution argument**: a demonstration that `resolve_via_routing` dispatches a rung after a CONFIRMED. `test_defect_3_the_deep_climb_needs_two_failures_first` asserts it does not.
- **B2 attribution**: `test_the_archive_population_this_was_measured_on_is_real` failing — i.e. 0 archived entries carrying `resolved_by_routing`, which would make the defect affect nothing. It finds 1370 of 16500.
- **B2 classifier limitation**: `TestTheKnownRemainingHole` starting to pass — then the regex has become behavioural and my "necessary not sufficient" verdict is wrong.
- **`co_consts` correction**: any Python build where `"x" in ("…x…",)` is `True`. There is none.
- **My refusal to repartition `DEFAULT_LADDER`**: a measurement showing a 1-strong-seat bench does not degrade panel-capability fidelity — then the Codex-only map dominates outright and should be adopted.

## Delivered files

New: `scripts/the_ladder_climb_is_measured_on_an_unexecuted_prefix_2026-10-05.py` (producer; exits 1 if any figure goes stale), `bench/tests/test_the_provenance_gate_attributes_the_writer_2026-10-05.py`.
Modified: `bench/tools/run_simulated_experiment.py` (opt-in `--routing-max-rungs`), `scripts/competence_provenance.py` (`falsifier_owner` + per-confirmation UNSAFE rule), `bench/tests/test_the_exercised_ladder_prefix_is_mixed_2026-10-05.py` (assertions now execute `resolve_via_routing`), `bench/tests/test_a_blind_round_is_actually_blind_2026-10-05.py` (the unconverted assertion), `experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md` (attributed review section).

Final sweep over the amended tree: **99 passed** across the ladder, provenance, blind-round, source-text-census, sim-seat-ladder and `routing_max_rungs` guards; plus **27 passed** on the swallow and help guards. Two mutation checks performed and restored.

**Termination.** Stopping here. The last pass produced only sub-threshold observations (`falsifier_style`'s regex could also be defeated by `builtins.__dict__["open"]`, which changes nothing about the verdict; `wall_clock_cap_s` parity is a cost difference, not a capability one). The three measured facts I relied on reproduced exactly; I did not independently re-run the Wilson interval, which the other seat did and which my argument does not depend on.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/fpl_star_2026-10-05/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
