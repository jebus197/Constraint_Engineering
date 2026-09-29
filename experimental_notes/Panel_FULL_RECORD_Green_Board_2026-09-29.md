# Clear the board, and settle the model question

Record written 2026-09-29T02:41:07+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

Dispatched 00:20 on 2026-09-29 on the founder's instruction to clear the test board using the free seats rather than the paid panel he had authorised. His words: "If you don't know how to fix the failing tests, why not consult with CC2 and Fable in CDSFL free panel review mode so I can have my pathway fully cleared to resume our outstanding runway items by the morning?" And on cost: "The £10 spend instruction is rescinded unless you, CC2 and Fable can't resolve everything between you." They resolved everything; the £10 was not spent.

The round carried 4 items: 3 failing tests and the open model question. Both seats reported. What follows is their work in full.

THE FINDING NEITHER SEAT WAS ASKED FOR, and the reason this record matters beyond the board. 3 of the 4 items trace to the same cause: the 4 commissioning_arm* runs of 2026-09-21/22 were being counted as REAL archive evidence. They are simulated -- bench/tools/commissioning_arms_2026-09-21.py:17 states that every seat in them is a `-SIM` stand-in. cc2 found the mechanism: scripts/latent_control_audit.py applied its simulation test PER FILE, while the runner writes its 3 provenance keys into the run REPORT only. A simulated run also drops runner_state.json, which carries runner_version (so it was admitted as a report), carries none of the provenance keys, and sits in a directory not named sim*. Those 4 files were the NEWEST admitted reports and therefore set the age baseline, moving it from 2026-08-27 to 2026-09-22 -- 26.3 days -- which silently disabled the TOO_NEW quarantine for every control key committed in that window.

CC1'S BRIEF WAS WRONG ON A LOAD-BEARING POINT and a seat corrected it. The brief stated that none of the 3 failures was a code defect. Item 2 was one.

THE 2 SEATS SOLVED ITEM 1 DIFFERENTLY AND CC1 TOOK THE SIMPLER FORM. cc2 proposed a FIGURE_DRIFT.md sidecar recording the superseding value; fable proposed an --as-of DATE flag on the producer so the historical figure is reproducible at its own date. fable's was taken because it makes the archived figure DECIDABLE BY RE-EXECUTION rather than merely recorded: --as-of 2026-09-11 reproduces the brief's 2/640 = 0.3125% to the character, while today's corpus gives 2/716 = 0.2793%. The brief is unedited and its blob hash is unchanged.

ON THE MODEL QUESTION, the founder's own framing turned out to be the answer. He asked for "whatever gives the best results in both use cases" -- measuring an expended run, and predicting before one. cc2 derived that the 2 quantities are not rivals but the conditional and the joint: A = M / P(not detected) at sigma=1, which is why 1/10 divided by 3/5 is exactly 1/6. Verified here independently on SymPy and Wolfram Language. compute_rk is left byte-identical, verified by sha256, with R_new_expectation recorded beside R_new. The decisive argument against swapping is that M <= A everywhere, so feeding M to thresholds calibrated on A would make every convergence gate easier to pass.

A GUARD CAUGHT CC1 DURING THIS ROUND. While mutation-testing fable's item 1 fix, CC1 edited the archived round-11 brief; its mtime jumped to the present and the validator refused it, because fable had built that anti-dodge deliberately. The mtime was restored and the brief verified byte-identical to HEAD.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — clear the board, and settle the model question

## SECTION 1 — The question

The founder wants a GREEN SUITE by morning so the runway can move. His words:
*"I would prefer to have a fully green board so we can finally move on with our
remaining runway items, some of which have now been outstanding for a long time."*
And on how: *"If you don't know how to fix the failing tests, why not consult with
CC2 and Fable in CDSFL free panel review mode."*

**3 tests fail. None is a code defect. Each is a question about what a guard should
assert, and getting that wrong makes a red suite green by weakening a check — which
is the one outcome worse than leaving it red.**

He also gave his answer to the open model question, and it reframes it. On whether
to adopt Astra's branch-weighted expectation: *"My concern is simply for accuracy in
both measurement of results of any given/already expended run, and in the predictive
accuracy of the explorer in that specific mode also. So my answer is whatever you all
agree gives the best results in both use cases."*

**ALL FIXES MUST BE THE SIMPLEST SUFFICIENT FIX AND MUST BE ADDITIVE.** His
instruction, verbatim: *"Remember all fixes must follow our formal simplest
sufficient fix and additive standards."* A fix that deletes a guard, widens an
exemption, or moves a date cut is NOT additive — it silently licenses the next
failure of the same kind.

## SECTION 2 — Use the harness

`S_k` does not bear on this. **`R_k` and the 2 branch forms bear directly on item 4**,
which is the model question. `gamma` and the two-sided gate bear on none of it; say
so if you find otherwise rather than reaching for them.

## SECTION 3 — Produce a fix, and test it

Deliver every fix by WRITING IT INTO THE SANDBOX TREE AT ITS REAL PATH.

<!-- figure: harvest loss | scripts/panel_harvest_loss_2026-09-22.py | 76.9231 -->

76.9231% of seat-delivered scripts have historically never reached `scripts/`.

A STORED falsifier may not call Wolfram. **Execute, do not grep**: a test asserting
on SOURCE TEXT proves only that a file describes itself consistently. 8 separate
defects on 2026-09-28 were tests that re-derived a value the code owns instead of
extracting it; every one stayed green through a mutation that broke what it guarded.

## SECTION 4 — The 4 items

**1. A HISTORICAL BRIEF DECLARES A FIGURE THAT NO LONGER REPRODUCES.**
`test_brief_figure_coverage_2026-09-11.py` fails because
`bench/logs/panel_round11_2026-09-11/BRIEF.md` declares
`real-rejection rate : 2/640 = 0.3125%` and its named producer now prints
`2/716 = 0.2793%`. **The numerator is unchanged; the ARCHIVE GREW.** The brief was
not wrong when sent on 2026-09-11.

The tension is real and neither horn is obviously right. Editing the brief falsifies
the record of what the seats were actually given. Exempting archived briefs weakens a
guard whose whole purpose is that a number typed into a brief is a claim about
evidence. **What SHOULD this guard assert, and over which briefs?** Consider whether
a declared figure should carry the denominator AS OF its date, and whether the guard's
real subject is briefs about to be DISPATCHED rather than briefs already archived.

**2 and 3. TWO ARCHIVE-CONTENT FAILURES.**
`test_latent_control_audit_2026-09-01.py::TestAgeControl::test_the_quarantine_rule_holds_for_every_row`
reports `critical_boundary_census: verdict SILENT_BUT_RAN but first_committed=1788252544
against newest archive mtime 1787788906` — a script committed 2026-09-01 against an
archive last written 2026-08-27, so the quarantine rule says TOO_NEW and the recorded
verdict says otherwise.
`test_latent_tagger_evaluation.py::TestArchiveExposure::test_prose_source_tags_the_measured_set_and_none_reaches_demotion`
reports a set mismatch over `commissioning_arm1_20260921`, `commissioning_arm4_20260922`
and `exp33_endocrine_20260405`.

**Diagnose both to root cause.** Is the recorded verdict wrong, the rule wrong, or the
archive's own dates wrong? **Do not make either green by excluding a row.**

**4. THE MODEL QUESTION, WITH THE FOUNDER'S OWN FRAMING.**
The shipped recursion (`reference_runner_v3.py` `compute_rk`, and the explorer
verbatim) tracks the NON-DETECTION branch:
`A(R) = sigma*B_minus + (1-sigma)*R`, `B_minus = R(1-q)/(1-qR)`.
Astra's proposal tracks the branch-weighted EXPECTATION: `M(R) = R(1-q*sigma)`.
Verified on SymPy and Wolfram: `A - M = R^2*q*sigma*(1-q)/(1-qR) >= 0`, and at
`R=1/2, q=4/5, sigma=1` the shipped form gives **1/6** where Astra gives **1/10** —
and 1/6 is exactly Astra's negative-branch value.

**Measured blast radius:** over 386 archived (R, q, sigma) triples in 11 log files,
**100% would move**, Wilson 95% [99.0146%, 100.0000%], median shift 0.0438, largest
0.1918, always upward.

**His answer is that BOTH use cases matter** — accuracy when measuring an
already-expended run, and predictive accuracy before one. The explorer already exposes
both as selectable modes. **Does the same answer apply to the RUNNER?** Should
`compute_rk` report both quantities, or keep tracking the branch and report the
expectation alongside, or change? Answer for BOTH use cases and say what it costs.

## SECTION 5 — What would refute you

Per item, state before concluding what evidence would overturn your answer. On item 1
name the brief your rule would wrongly let through. On items 2 and 3 name the row you
would have excluded and why you did not.

## SECTION 6 — Output shape

Per item: `id`, `verdict`, `reasoning` with file and line, `fix_path` or NONE with the
reason, `falsifier_path`, `falsifier_command`, `falsifier_output` verbatim,
`additive_check` naming the caller your change reaches and the test that executes it,
and `refutation_condition`. Then `strongest_disagreement` with this brief, which must
not be empty, and `passes_run`.

## SECTION 7 — Termination

Stop on diminishing returns. If you cannot finish all 4, do fewer properly and say
which you did not reach. **A guard you weakened to make a suite green is a worse
outcome than a test left red**, and the founder will be told which you did.

Disagreement with the other seat is information. Do not smooth it away.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 106 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel green_board_2026-09-29) -->

All four items are done, written into the tree at their real paths, and executed. Summary of what each fix is, and the evidence.

---

## item 1 — archived brief's declared figure no longer reproduces

**verdict: NOT A CODE DEFECT. The guard is right, the brief was right, and the pair drifted. Repaired by adding a re-executed supersession record, not by exempting anything.**

**reasoning.** `scripts/panel_brief_validate.py:331` (`check_declared_figures`) re-executes every declared figure and refuses when the producer does not print it. `bench/logs/panel_round11_2026-09-11/BRIEF.md:4` declares `real-rejection rate : 2/640 = 0.3125%`; the producer now prints `2/716 = 0.2793%`. The numerator is the same 2 findings (`exp48_chemistry_exam_live_20260729T044134Z/C0012` and `/C0015`) — only the corpus of distinct archived falsifier sources grew, 640 → 716. Neither obvious repair is admissible: editing the brief destroys the record of what two paid seats were given; exempting archived briefs deletes the check for every brief ever dispatched.

The third option, and the one I took: a `FIGURE_DRIFT.md` **sidecar beside the brief**, carrying `<!-- figure-superseded: <date> | <label> | <script> | <exact string NOW> -->`. The superseding value is run through **the same output, the same whole-token predicate and the same 3-significant-character rule**. The only way to turn the refusal into a report is to supply a number the named script really prints today. The brief itself is byte-identical. The brief's hint — "the guard's real subject is briefs about to be DISPATCHED" — is made mechanical rather than an exemption: supersession requires a date **strictly later** than the ISO date in the brief's own directory name, so a brief validated on the day it is stamped has no reconciliation available at all.

- `fix_path`: `scripts/panel_brief_validate.py` (new `FIGURE_SUPERSEDED`, `FIGURE_SUPERSEDED_OPENER`, `superseding_figures()`; `check_declared_figures(..., brief_path=None, notes=None)`; `main()` wiring at the `problems += check_declared_figures(...)` call), plus new `bench/logs/panel_round11_2026-09-11/FIGURE_DRIFT.md`.
- `falsifier_path`: `bench/tests/test_declared_figure_supersession_2026-09-29.py`
- `falsifier_command`: `python3 -m pytest bench/tests/test_declared_figure_supersession_2026-09-29.py -q`
- `falsifier_output`: `13 passed in 7.61s`

Seven of those 13 are refusals — the teeth, executed: no sidecar still refuses; a caller that passes no `brief_path` keeps the old strictness; a supersession the script does **not** print refuses (`prints NEITHER`); a supersession dated on or before the brief refuses; a malformed record refuses; two records for one figure refuse; a `<3`-significant-character supersession refuses. End-to-end on the real brief:

```
panel-brief: FIGURE DRIFT — 1 declared figure(s) no longer reproduce and are reconciled by FIGURE_DRIFT.md:
  - 'archived falsifier rejections that are NOT location artefacts': the brief's 'real-rejection rate : 2/640 = 0.3125%' was superseded on 2026-09-29 by 'real-rejection rate : 2/716 = 0.2793%', which scripts/archived_falsifier_rejections_2026-09-10.py does print. The brief is unedited
panel-brief: BRIEF.md carries all 8 required sections
EXIT=0
```

- `additive_check`: caller is `main()` in `scripts/panel_brief_validate.py`, executed by `test_the_validator_exits_zero_and_names_both_numbers` (subprocess, exit code + both numbers in output) and by the pre-existing `test_brief_figure_coverage_2026-09-11.py::test_it_does_not_refuse`, which is now green for a principled reason. Anti-vacuity is pinned: `test_the_round_eleven_figure_really_has_drifted` asserts the declaration **still** fails without the sidecar, so the mechanism is load-bearing.
- `refutation_condition`: **the brief my rule would wrongly let through, named.** Had round 4's brief *declared* `gamma = 0.451` (it stated it in prose; that is why `undeclared_figures` exists), someone could later add a supersession `gamma = 0.415413` that re-executes, and my rule would report DRIFT and exit 0 — the typo that created this whole guard would pass. I cannot close that without re-running the producer at the brief's own revision, and **this checkout has no `.git`** (`git rev-parse` → `fatal: not a git repository`), so that evidence does not exist here. The residual is bounded by the strictly-later-date rule (pre-dispatch briefs cannot use the path) and is recorded in the module docstring. Show me a case where a same-day supersession reconciles, or where a wrong-at-dispatch figure was papered over, and the rule is refuted.

---

## item 2 — quarantine rule vs `critical_boundary_census`

**verdict: THIS ONE IS A CODE DEFECT, and the brief's claim that none of the three is a code defect is wrong. The rule is right, the archive's dates are real, and the computed verdict is wrong.**

**reasoning.** `scripts/latent_control_audit.py:219` applies `_is_simulated(d, fp)` **per file**, but the three provenance signals it reads (`severity_admissibility.severity_provenance`, `_simulated`, `models[*]` ending `-SIM`) are written only into the run **report**. A simulated run also drops `runner_state.json`, which carries `runner_version` — so line 263 admits it as a report — carries none of the provenance keys, and sits in a directory named `commissioning_arm*`, not `sim*`. Measured by execution:

```
LEAKED files (per-file says real, their run dir is simulated):
    commissioning_arm1_panel_20260921T215405Z/runner_state.json
    commissioning_arm2_single_20260922T020120Z/runner_state.json
    commissioning_arm3_contrast_20260922T025824Z/runner_state.json
    commissioning_arm4_prose_20260922T053349Z/runner_state.json
newest baseline PER FILE   : 1790060648  2026-09-22 07:04:08
newest baseline PER RUN DIR: 1787788906  2026-08-27 00:01:46
inflation: 26.3 days
first_committed critical_boundary_census = 1788252544 2026-09-01
  TOO_NEW under per-file baseline   : False
  TOO_NEW under per-run-dir baseline: True
```

`1787788906` is exactly the number in the failure report, and the per-run-dir baseline matches the test's own mirror to the second. This is the same failure the `_archive` docstring records from 2026-09-01 — the witness set accepting the runner's own rehearsal as field evidence — arriving through a file the earlier fix never covered. The 26.3-day inflation silently disabled the `TOO_NEW` quarantine for every control key committed in that window.

- `fix_path`: `scripts/latent_control_audit.py` — new `_simulated_run_dirs()`; `_archive()` now skips `_is_simulated(d, fp) or fp.parent in sim_dirs`. Simulation is a property of the run, not of the file.
- `falsifier_path`: `bench/tests/test_simulated_runs_are_excluded_per_run_2026-09-29.py`
- `falsifier_command`: `python3 -m pytest bench/tests/test_simulated_runs_are_excluded_per_run_2026-09-29.py -q`
- `falsifier_output`: `6 passed in 42.35s`

The decisive one reproduces the red and then resolves it in a single test: with the leaked baseline pinned via `newest_override=1790060648` the verdict is `SILENT_BUT_RAN` (the reported failure, exactly); with the corrected baseline it is `TOO_NEW`, which is what the rule at `test_latent_control_audit_2026-09-01.py:123-130` demands.

- `additive_check`: caller is `audit()` → `_archive()` in the same module, reached by the existing `test_latent_control_audit_2026-09-01.py` suite and by `test_the_reported_verdict_flips_under_the_corrected_baseline`. **`test_the_fix_loses_no_sighting` is the additive check executed**: it runs the audit's own `_report_key_writes` + recursive presence rule over the leaked docs and the kept docs and asserts that **no** control key goes from seen>0 to seen==0. It passes — the four state dumps' only contribution was ever the baseline.
- `refutation_condition`: **the row I would have excluded and did not.** The cheap green was to drop `critical_boundary_census` from the rule's loop, or to add `commissioning_*` to an ignore list. I excluded no row; I corrected the baseline, which makes the control **stricter** (more keys quarantined, not fewer). Refuted if a control key is witnessed only by a simulated run's `runner_state.json` — `test_the_fix_loses_no_sighting` would fail and name it — or if the four commissioning runs are in fact real, which `bench/tools/commissioning_arms_2026-09-21.py:22` ("every seat is a `-SIM` stand-in") denies.
- **caveat, stated rather than implied:** this sandbox has no `.git`, so `_key_first_committed` returns `None` for every key and the reported failure **cannot** reproduce here — the rule holds vacuously. I demonstrated the defect directly instead, and injected the commit date to show the verdict flip.

---

## item 3 — tagger set mismatch

**verdict: NOT A CODE DEFECT. Archive growth. The pin was due for re-measurement by its own documented protocol, and the protocol is now executed instead of recorded in prose.**

**reasoning.** `bench/tests/test_latent_tagger_evaluation.py:237` is a strict list equality over a corpus built by an unbounded glob (`_archived_runs`, `:117-132`, no date filter anywhere). 11 expected → 16 actual: **5 added, 0 lost.** The five are `commissioning_arm1_panel_20260921T215405Z/{C0038,C0054,C0060}` and `commissioning_arm4_prose_20260922T053349Z/{C0003,C0016}`, from runs that landed 2026-09-21/22, fourteen days after the pin was last re-measured. Each has an auditable marker hit (`no_caller`: "no production consumer exists", "no file, no command, and no invocation"; `explicit_latent`: "the worst shape a latent defect can take"). `exp33_endocrine_20260405` was **never a mismatch** — it is on both sides, and appeared in the failure message only because list equality reports the first positional difference. The docstring's own rule is "the tripwire is only safe to move once the thing it watches is shown not to have moved": nothing was lost, which is the mechanical form of "the marker set has not been loosened" — a loosened marker set *adds* tags, a broken one *drops* them.

- `fix_path`: `bench/tests/test_latent_tagger_evaluation.py` — pins lifted to module level as `PINNED_2026_09_08` (unchanged) and `PINNED_PROSE_TAGGED = sorted(PINNED_2026_09_08 + [5 new])`; **equality kept**; new `test_no_previously_tagged_entry_stopped_being_tagged` asserts the no-loss invariant, which is immune to archive growth.
- `falsifier_path`: `bench/tests/test_latent_tagger_evaluation.py`
- `falsifier_command`: `python3 -m pytest bench/tests/test_latent_tagger_evaluation.py -q`
- `falsifier_output`: `43 passed in 2.46s` (was 41 passed + 1 failed; +1 new test)
- `additive_check`: caller is `bench/latent_tagger.py::tag_entry`, driven by the test over the live archive. The equality is deliberately **not** softened to containment — a containment assertion would survive a marker set loosened until it tags half the archive, which is the only thing this pin exists to catch. The new no-loss test is what makes a dropped tag distinguishable from growth at a glance instead of arriving as one positional diff.
- `refutation_condition`: **the row I would have excluded and did not.** The cheap green was to filter `commissioning_*` out of `_archived_runs`, or to relax `==` to `⊆`. I did neither: every row stays in, and the equality stays. Refuted if any of the five new tags is a *false* tag — i.e. if the prose markers fired on text that does not assert unreachability — in which case the correct fix is the marker set, not the pin. I checked each one's matched phrase; all five are `latent_source="prose"`, the source the module already recommends retiring, and all five remain demotion-ineligible (`test_nothing_in_the_archive_is_demotion_eligible` green).
- **EPISTEMIC, not fixed** [SPECULATIVE]: `commissioning_arm1.../C0038` has `status="CLOSED"`, which `RUNNER_SKIP_STATUSES` (`:97`) excludes at the live call site — the assertion calls `tag_entry` directly and applies no status skip, so it counts an entry the runner would never tag. Changing that would change what the pin measures, so I left it and recorded it.

---

## item 4 — the model question

**verdict: NEITHER FORM IS WRONG AND THEY ARE NOT RIVALS. `compute_rk` reports both; the gate keeps tracking the branch. Answer is the same for the runner as for the explorer, but the *reason* is asymmetric, and the brief's own blast-radius figure is the argument.**

**reasoning, derived.** From the probability model alone (one flaw present with prior `R`, detected with probability `q`, repaired with probability `σ`, no false positives):

- `B₋ = R(1−q)/(1−qR)` **is** `P(flaw | NOT detected)` by Bayes — `P(flaw ∧ no detect)=R(1−q)`, `P(no detect)=1−qR`. So the shipped `A = σB₋ + (1−σ)R` is a **conditional on the negative branch**; at `σ=1` it *is* `B₋`. It answers "the pass reported nothing — what is left?"
- Astra's `M = R(1−qσ)` is `R[(1−q) + q(1−σ)]`, the **unconditional** survival probability — the pre-pass expectation averaged over both branches. It answers "before I run, how much risk do I expect to remain?"
- They are **quotient and numerator of one fraction**: at `σ=1`, `A = M / P(not detected)`. At `R=1/2, q=4/5, σ=1`: `A = 1/6`, `M = 1/10`, `P(no detect) = 3/5`. That is why "1/6 is exactly Astra's negative-branch value" — it is `M` divided by the branch probability.
- `A − M = σqR²(1−q)/(1−qR) ≥ 0` on the whole unit cube. z3: the negation is **unsat** — a proof over the reals, not a sample. Confirmed independently with **Wolfram Language (local Wolfram Engine, via `wolframscript`)**, which returned `((-1 + q)*q*R^2*sigma)/(-1 + q*R)`, exit 0, no `Name::tag`, no `$Failed`.

**So: do not change what the gate consumes.** `M ≤ A` everywhere, and the brief's own measurement says 100% of 386 archived triples move, median 0.0438, largest 0.1918, **always** in the direction that makes `A` the larger. Feeding `M` to thresholds calibrated on `A` lowers reported residual risk on every triple and makes **every convergence gate in the project easier to pass**. A measurement change that can only loosen gates is not a measurement improvement; it is a silent threshold move, and by the additive standard it needs a committed measurement showing it dominates, which no one has.

**Both use cases, answered.** *Prediction before a run:* `M` is the correct quantity and the explorer is right to expose it. *Measurement of an expended run:* neither form is unconditionally correct, because for an expended run the branch is **known** — `A` is the right posterior on a round that confirmed nothing, and is merely conservative (never flattering) on a round that did confirm. So the runner keeps `A` as the gated number and records `M` beside it as `R_new_expectation`, at the same `q_eff` as the channel composition, read by nothing.

- `fix_path`: `bench/reference_runner_v3.py` — new `_rk_finite()` and `compute_rk_expectation()`; the live call site in `_evaluate_sk_for_findings` now writes `entry["sk_result"]["R_new_expectation"]` beside `R_new`. **`compute_rk` is left byte-identical** — it is the gate-bearing path, and this was a one-shot dispatch.
- `falsifier_path`: `scripts/branch_form_semantics_2026-09-29.py` and `bench/tests/test_rk_expectation_companion_2026-09-29.py`
- `falsifier_command`: `python3 scripts/branch_form_semantics_2026-09-29.py` then `python3 -m pytest bench/tests/test_rk_expectation_companion_2026-09-29.py -q`
- `falsifier_output`:

```
1. M(R) = R[(1-q) + q(1-sigma)] = R(1-q*sigma)      -- marginal, VERIFIED
2. P(flaw | not detected) = R(1-q)/(1-qR) = B_minus -- Bayes,    VERIFIED
3. A(sigma=1) = B_minus and A(sigma=0) = R          -- mixture,  VERIFIED
4. A - M = R**2*q*sigma*(1 - q)/(-R*q + 1)
   z3: (A - M) < 0 on (0,1)^3 is unsat -- A >= M proved, VERIFIED
   sweep 19^3 = 6859 points, min(A - M) = 0.000006 >= 0, VERIFIED
5. A = M / P(not detected) at sigma=1               -- cond/joint, VERIFIED
   at R=1/2, q=4/5, sigma=1:  A = 1/6   M = 1/10   B_minus = 1/6   -- brief's figures, VERIFIED
   compute_rk (nu off) == A(R) on 18/18 triples -- the SHIPPED code is the conditional form, VERIFIED

FALSIFIER-CLEAN: all 5 derivations hold; A is a negative-branch conditional,
  M is the pre-pass expectation, and A >= M always.
EXIT=0
```
```
15 passed in 2.32s
```

The derivation script imports and executes the repository's own `compute_rk` rather than retyping it, and confirms the shipped code is the conditional form at 18/18 triples.

- `additive_check`: caller is `_evaluate_sk_for_findings` in `bench/reference_runner_v3.py`, driven for real by `test_the_evaluator_records_the_expectation_beside_the_gated_number` (builds a registry entry, calls the evaluator, asserts the field arrives — a keyword typo would grep green and this would not). `test_both_fields_come_from_the_2_forms_at_the_SAME_q` recovers `q` by bisection from `R_new` and requires the recovered value to reproduce `R_new_expectation` through the *other* function, so neither field can drift from its formula. The derivation script is itself reached by the suite (`test_the_stored_derivation_runs_clean`), so it is not an artefact archived beside the tests. `_rk_finite` duplicates `compute_rk`'s inline clamp; the duplication is a **checked** invariant — five parametrised tests execute both functions on non-finite inputs in all five slots.
- `cost, stated`: one extra float per admissible finding in every report (no schema consumer reads it, so archived reports stay comparable); one duplicated 6-line clamp, guarded by tests; and the open question is **not** closed — whether a gate should ever consume `M` is a threshold recalibration needing its own committed measurement, and it is recorded as such in the docstring rather than decided here.
- `refutation_condition`: refuted if `A − M < 0` anywhere on `[0,1]³` (z3 says unsat; a counterexample kills the whole argument), or if a gate is shown to read `R_new_expectation` (then I did change behaviour and must say so), or if someone produces the committed measurement that `M` dominates `A` on a named property under recalibrated thresholds — in which case the gate should move, with the thresholds, together.

**On the harness sections:** `S_k` does not bear on any item, as the brief says. `gamma` and the two-sided gate bear on none of them — I checked and found nothing, and did not reach for them.

---

## strongest_disagreement with this brief

**"3 tests fail. None is a code defect." Item 2 is a code defect, at `scripts/latent_control_audit.py:219`, and treating it as a question about what a guard should assert would have left it in place.** `_is_simulated` is evaluated per file while its evidence exists only per run report, so four simulated commissioning runs' `runner_state.json` were admitted as field sightings and, being the newest admitted files, set the age baseline — 2026-08-27 became 2026-09-22. For 26.3 days of baseline the `TOO_NEW` quarantine could not fire for any control key committed in that window. The red test was the age control working exactly as designed and reporting a real disabling of itself. Had I accepted the brief's framing, the honest-looking move would have been to reconcile the rule with the recorded verdict — which is the one outcome the brief rightly says is worse than red.

Two smaller ones. The brief describes a "recorded verdict" for `critical_boundary_census`; there is no recorded verdict anywhere on disk — every verdict is computed at runtime (`scripts/latent_control_audit.py:323-326`), and the only on-disk occurrence is the brief's own prose. And on item 1, the brief's hint ("the guard's real subject is briefs about to be DISPATCHED rather than briefs already archived") is, taken literally, the exemption the same paragraph forbids; scoping the guard to pre-dispatch briefs would have deleted it for all 49 archived ones. I used the date ordering to get the hint's benefit without the exemption.

## passes_run

Four targeted passes, no full-suite run. Green: the 3 named tests plus the 3 new files, `48 passed in 49.83s`. Regression sweep over everything my edits touch: brief-validator family (8 files) `102 passed, 6 skipped`; `test_operational_scripts.py` `470 passed`; runner `R_k`/`S_k` family (7 files) `343 passed`; tagger file `43 passed`.

**Pre-existing failures in this sandbox that I did not cause and did not fix: 9, all git-absence artifacts** — this checkout has no `.git`, so `git status`/`git ls-files`/`git log` exit 128 and the dating function returns `None`. Four in `test_latent_control_audit_2026-09-01.py` (same four the diagnosis found before my change), three in `test_parked_measurements_still_run_2026-09-11.py`, two in `test_task_list_figures_have_producers_2026-09-10.py`. They should be green in your git-bearing checkout; if any is not, it is not one of these four items.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 62 recorded tool call(s).

<!-- verbatim-begin: fable (panel green_board_2026-09-29) -->

All verification complete. The 4 remaining failures are proven pre-existing sandbox artefacts (no `.git` in the sandbox; identical on unpatched HEAD). Final report.

---

# Panel reply — seat: Claude (Fable) — 2026-09-29

**Board state delivered: the 3 failing tests are green in the sandbox tree, none by weakening a check.** 87 passed across every affected file; the only remaining reds are 4 git-dependent tests that fail identically on unpatched HEAD because this sandbox has no `.git` (`_key_first_committed` shells to `git log` → `first_committed=None`) — verified by temporary revert, not assumed. They will pass on the founder's machine.

---

## Item 1 — archived brief's declared figure

**id:** 1 · **verdict:** Guard scope was wrong, not the brief and not the check's strength. The guard's refusal subject is a brief about to be **dispatched**; over an archived brief a declared figure is a claim about evidence **as of its date** — and it should stay *decidable by re-execution*, not exempted.

**reasoning:** `scripts/panel_brief_validate.py:check_declared_figures` (was lines 222–336) re-executed against today's corpus only. Producer `scripts/archived_falsifier_rejections_2026-09-10.py` counts distinct falsifier sources over `bench/logs/**/*_report.json`; the growth 640→716 is **exactly** the 4 `commissioning_arm*` rehearsals of 2026-09-21/22, verified by execution: restricting to runs dated ≤ 2026-09-11 reproduces `2/640 = 0.3125%` to the character, numerator unchanged. Editing the brief falsifies the dispatch record (rejected); a path exemption is dead on arrival because the dispatcher (`bench/confer_maths_panel_2026-09-05.py`) validates briefs *in* `bench/logs/`, so the exemption would cover dispatch too.

**fix_path:** `scripts/archived_falsifier_rejections_2026-09-10.py` (gains `--as-of YYYY-MM-DD`, run-dir UTC stamp with mtime fallback) and `scripts/panel_brief_validate.py` (`_historical_reproduction`: on token-not-found, retry `--as-of` the **latest date the brief carries**, gated on the brief's **mtime being consistent with that date** (≤ EOD+48h), accepted only if the figure re-executes there, and **loudly** — never silenced by `--quiet`; producer without `--as-of` exits non-zero → refusal stands, fail-closed).

**falsifier_path:** `bench/tests/test_declared_figure_as_of_2026-09-29.py`
**falsifier_command:** `python3 -m pytest bench/tests/test_declared_figure_as_of_2026-09-29.py -q`
**falsifier_output:** `7 passed in 15.80s` — including the executed dodge (fresh copy of the same brief, mtime today → **refused**), the never-true figure `3/640` (**refused** even archived), and the no-`--as-of` producer (**refused**, fail-closed). Validator on the archived brief: `panel-brief: BRIEF.md carries all 8 required sections` / `EXIT: 0` with `panel-brief: HISTORICAL FIGURE — … DOES re-execute with --as-of 2026-09-10 …`.
**additive_check:** `--as-of` is wired to a real caller (the validator's retry) and executed by the new tests; `brief_path` is wired from `main()` which the dispatcher invokes; nothing removed — every previously refused input is still refused (pinned by `test_a_fresh_brief_claiming_a_past_date_is_still_refused` and the unchanged 107-test brief suite).
**refutation_condition:** The brief my rule would wrongly let through: one authored within the 48h mtime slack *after* its latest carried date, declaring a figure true at that date but overtaken inside the slack window — dispatched, it carries a stale number past the gate. Evidence overturning me: any archived dispatch that reached seats via the historical path with a then-stale figure. (Round-11's own latest textual date is 2026-09-10, not 2026-09-11 as the brief implies — the mechanism works because 640 was the corpus at both dates.)

## Items 2 and 3 — one root cause, two different correct fixes

**id:** 2 · **verdict:** **The recorded verdict was wrong; the rule and the archive's dates are right — and contra the brief, this one IS a code defect**: a hole in `_is_simulated`.

**reasoning:** `scripts/latent_control_audit.py:_is_simulated` (line 159) reads three authoritative signals (`severity_provenance`, `_simulated`, top-level `models`) plus a dir-name heuristic. A `runner_state.json` is report-shaped (`runner_version`+`registry`) so it enters `_archive()`, **carries none of the three keys**, and "commissioning" defeats the dir heuristic. The 4 rehearsals are simulated (sibling reports: `severity_provenance: "simulated"`, every model `*-SIM`), yet their state files were admitted, moving the age baseline from 1787788906 (2026-08-27, `exp55`, the last **real** run) to 1790060648 (2026-09-22, a rehearsal). Hence `critical_boundary_census` (committed 2026-09-01) read SILENT_BUT_RAN where the rule says TOO_NEW — which is the *true* state: no real run has witnessed anything since 2026-08-27. The audit's own doctrine: a rehearsal cannot witness.

**fix_path:** `scripts/latent_control_audit.py` — `_is_simulated` additionally reads the model labels the state file *does* carry, runner-written, in `itc_model_state` / `novelty_counts_per_model` / `raw_counts_per_model` (parsed dict keys, no text window; the 2026-09-02 prose-quoting repair is untouched and re-pinned).
**falsifier_path:** `bench/tests/test_simulated_runner_state_is_excluded_2026-09-29.py`
**falsifier_command:** `python3 -m pytest bench/tests/test_simulated_runner_state_is_excluded_2026-09-29.py bench/tests/test_latent_control_audit_2026-09-01.py -q`
**falsifier_output:** `7 passed in 2.71s`; audit file `4 failed, 17 passed` where the 4 are the no-git sandbox artefacts (identical on reverted HEAD: `4 failed, 2 passed` on the same selection). Post-fix audit: `baseline_mtime: 1787788906 (2026-08-27)`, `reports: 73`, all pinned verdicts (`target_integrity_events` SILENT_BUT_RAN/`target_hashes`, `hil_status`, `burst_phases` AMBIGUOUS, `stalled` SEEN) intact.
**additive_check:** reached by `_archive()` → `audit()` → CLI and every existing audit test; the widening is exclusion-only for `-SIM`-keyed state files, and `test_a_real_runs_state_file_is_still_admitted` executes the opposite direction over real `exp*` state files on disk.
**refutation_condition:** Row I would have excluded and did not: **none** — `critical_boundary_census` stays in; its verdict now follows the rule at whatever baseline holds. Overturned if: (a) git shows any live-pinned key (`hil_status`, `burst_phases`, `target_integrity_events`, `stalled`) first-committed after 2026-08-27 — the corrected baseline then flips it TOO_NEW on the founder's machine and that pin goes red (the rule working, but my green-board claim refuted); (b) any genuine live run writes `-SIM` model labels.

**id:** 3 · **verdict:** Pure archive growth; the pin moves, per the file's own 2026-09-08 precedent, in the required order.

**reasoning:** `bench/tests/test_latent_tagger_evaluation.py:237` pins the tagged set. Executed: 5 ADDED (`commissioning_arm1_panel/C0038,C0054,C0060`, `commissioning_arm4_prose/C0003,C0016`), **0 removed, all 11 prior pins reproduce exactly** — a loosened marker set would have tagged old prose; it tagged none. `exp33_endocrine/C0010` never moved; its appearance in the brief's mismatch list is pytest index-shift noise. Watch-target shown unmoved first: `bench/latent_tagger.py` mtime 2026-09-07 02:00:57, the a4cc407 stamp the docstring records. Simulated runs are in scope here by the file's own precedent (sim45 pins); this corpus measures tagger behaviour over every archived registry, not the witness set — so items 2 and 3 correctly get **opposite** treatments of the same 4 directories. None of the 5 reaches demotion (`test_nothing_in_the_archive_is_demotion_eligible`, executed).
**fix_path:** `bench/tests/test_latent_tagger_evaluation.py` (pin 11→16 + dated docstring recording the verification order and evidence).
**falsifier_path:** same file (the pin is the falsifier). **falsifier_command:** `python3 -m pytest bench/tests/test_latent_tagger_evaluation.py -q` · **falsifier_output:** `42 passed in 2.15s` (includes the untouched `added == []` fail-safe and `removed` pins).
**additive_check:** no code changed; the tripwire is retightened around the grown corpus, and the corpus-floor test (≥28 runs/≥2247 findings; now 47/2769) still executes it.
**refutation_condition:** Row I would have excluded: the 5 commissioning entries — not excluded, for the precedent above. Overturned if git shows `bench/latent_tagger.py` touched after a4cc407 (mtime is my only no-git evidence), or if any of the 5 reaches demotion eligibility on the founder's machine.

## Item 4 — the model question

**id:** 4 · **verdict:** **The founder's both-use-cases answer does NOT transfer to the runner as a code change. The runner keeps the branch; the expectation stays in the explorer, where both modes already ship.** `compute_rk` is unchanged; the decision is now *pinned by an executed test*, which is the additive form of a ruling.

**reasoning (derived, tools first):** SymPy: `A − M = R²qσ(1−q)/(1−qR) ≥ 0`; law of total probability closes exactly — `(1−qR)·B₋ + qR(1−σ) = M`, residual 0 — so **M is the coherent average of the branch posteriors** and A at σ=1 **is** the quiet-round posterior B₋ (1/6 vs 1/10 at the brief's point, reproduced). Wolfram Language (local Wolfram Engine) concurs: `{0, True, 1/6, 1/10}` on the identity, the ordering over the open cube, and both values. Wilson for the blast radius re-derived: 386/386 → `[99.0146%, 100.0000%]`, matching the brief. The two forms answer two questions. *Measurement of an expended run* (`reference_runner_v3.py:11417`): the runner updates on realised rounds, and the rounds that decide convergence are observed quiet rounds — conditioning on the observed branch is measurement; averaging over a branch already observed **understates risk by exactly the SymPy gap, everywhere, always downward** — the direction that licenses earlier convergence and would silently move 100% of 386 archived triples (median 0.0438). A measurement channel must not move in the flattering direction by modelling preference. *Prediction*: the expectation is the honest pre-outcome quantity — and the explorer's prospective mode already computes it with its own floor `ν/(qσ+ν(1−qσ))` (fixed-point verified). One honesty note the brief's framing invites but does not state: A is not the exact coherent posterior for *detection* rounds either — it is a σ-interpolation that is everywhere ≥ the coherent average, i.e. conservative, which is the fail-safe side for a gate.

**What it costs:** nothing in code and one asymmetry in prose — a reader of a report must go to the explorer for the predictive number. I deliberately did **not** add an `rk_expected` report field: no channel reads it, and an addition nothing reaches is this project's most-confirmed defect class (11 since 2026-08-01). The moment a caller needs it, the pinned test file is where the one owned Python implementation should graduate from.

**fix_path:** NONE for production code (reason above). **falsifier_path:** `bench/tests/test_rk_branch_vs_expectation_2026-09-29.py` — imports the **real** `compute_rk`; a silent switch to the expectation fails 4 independent ways (point value 1/6, gap identity on an 11³ grid, ordering with re-injection on, and equilibrium: 4000 iterations settle at the trajectory floor 0.4545…, > 0.09 from the expectation floor). **falsifier_command:** `python3 -m pytest bench/tests/test_rk_branch_vs_expectation_2026-09-29.py -q` · **falsifier_output:** `5 passed in 0.32s`. **additive_check:** the test reaches `compute_rk` itself — the function every R_k channel calls.
**refutation_condition:** A committed measurement showing a downstream consumer reads R_k as a *prediction* (then the alongside-field becomes reached and my ruling flips); or a derivation that the runner's per-round observation model makes M the observed-branch conditional (it is not: the quiet-round conditional is B₋, shown above). Confirmed as the brief states: `S_k`, `gamma` and the two-sided gate bear on none of the four items.

---

**strongest_disagreement:** The brief asserts *"None is a code defect."* False for items 2/3's shared root: `_is_simulated` failing to classify a simulated run's state file is a hole in a guard — code, not philosophy — and calling it a guard-assertion question invited exactly the wrong fix (excluding a row or moving the rule). Second: the brief's item-3 framing names `exp33_endocrine_20260405` as part of the mismatch; it never moved — a seat "fixing" exp33 would have chased pytest diff-alignment noise. Third, smaller: the round-11 brief's latest carried date is 2026-09-10, not the 09-11 the brief's framing suggests; my mechanism survives this only because the corpus was 640 at both dates — the founder should know the record's own dating is one day looser than assumed.

**passes_run:** P1 reproduce all three failures + root-cause each (execution, incl. mirror-vs-audit baseline decomposition and the vacuous-pass discovery that the sandbox lacks `.git`); P2 fix design falsification (path-exemption killed by dispatcher evidence; as-of reproduction executed before adoption; dodge scenario constructed and closed); P3 implementation + per-fix falsifiers (7+7+42+5 tests, all executed); P4 collateral sweep (146 brief/tagger/operational tests green; 4 reds proven pre-existing by revert); P5 independent math derivation (SymPy) + Wolfram second falsifier + Wilson re-derivation. Converged: last two passes produced no new failures; remaining residuals are the named refutation conditions, all below the material threshold in this checkout and stated for the machine that has git.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/green_board_2026-09-29/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
