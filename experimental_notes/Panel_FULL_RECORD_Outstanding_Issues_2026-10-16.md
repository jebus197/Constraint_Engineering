# The panel corrected 3 of my repairs, and found a verdict inversion next door to a 4th

Record written 2026-10-16T17:29:31+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED, AND WHY

On 16 October 2026 the founder ruled on a list of outstanding issues and instructed that a free panel check the resulting work under the project's formal `simplest sufficient`, `additive` and `composability` standards, with CC1 suggesting its own fixes first and the seats checking all of it under `a`, `f` and `sy`.

Four repairs were put up for checking: the forward normalisation of finding identifiers on his ruling that vendor names are a recording statistic only; the recording of composer provenance in the dispatch record, which gives the coherence budget recalibration its first real input; the gating of the boundary-band verdict on whether the decay curve is estimable at all; and the measurement answering his question about whether admitting a model to the harness is trivial.

Three open design questions were put with them, each carrying CC1's own position so the seats were not answering a blank page: whether the per-model ceiling on how densely packed with constraints a prompt may be should govern anything now that its only effectful consumer, the mechanical directive pruner, is retired, what the cold-start rule should be for derived-capability routing, and whether model admission should become a single registration point.

The round was blind, both seats free, and no paid seat was dispatched. The brief declared 4 figures for re-execution and passed the brief validator's 8 required sections.

WHAT WAS DONE WITH THE FINDINGS

The panel corrected three of CC1's repairs and found one defect next door to a fourth. Every correction was verified by execution before acceptance, and none was taken on the seat's word.

The repair that refuses a band verdict when the decay curve cannot be estimated had broken an existing test of that verdict, one which drives the real reporter rather than a stub, and which CC1 had not run. Both seats independently found that the `composer_fallback` marker was written at four dispatch sites and read by nothing, and that recording character counts on the fallback branch made a failed composition calibrate to a credible-looking figure instead of an obviously broken one. The admission measurement was understated and is corrected from five of seven to nine of ten steps failing silently. The cc2 seat's fixes for all three were applied as written, from the files it wrote into its sandbox, which were preserved before teardown.

The fable seat found that `_resolve_merge_source` mis-attributes a cross-seat merge source, because the pattern that extracts the source identifier matches inside the seat prefix rather than the finding number. CC1 had written in that very function that no vendor strip was needed there, backed by a measurement showing no pairs changed. The claim was true and the conclusion was wrong: the measurement tested the strip and the hazard was in the resolver's own pattern. That fix is held and is not yet applied, because it touches the same function as the cc2 seat's work and as the blocker-limbo reader added the same day.

One of the fable seat's own figures does not reproduce. Its delivered test states an interval that matches no standard method and is narrower than Wilson at both ends. The finding it supports stands and the interval must be corrected before the fix is adopted. The harvested copy is not edited, because it is the record of what the seat wrote; the interval checker now treats a harvested seat file as verbatim seat output, with the scope measured rather than asserted.

On the three questions the seats upheld CC1's positions and strengthened two of them with harder facts. The recalibration pipeline writes into a key space its consumer never reads, for every seat in the roster, which is a stronger argument for leaving that constraint-density ceiling inert than the one CC1 offered. The prior panel's premise about the routing cold start was arithmetically wrong at the only point that matters, because the lower bound at no observations is not zero but undefined, and an undefined sort key yields a different order for every input order rather than sorting last. On model admission the seats rejected both a raise and refusing to dispatch the seat, the latter because dropping a seat is benching it, and adopted a run-level preflight that reports every miss at once before any spend.

Five items from the day still await the founder's ruling, and they are listed in the end-of-day note of the same date.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Joint round: the outstanding issues from his rulings of 2026-10-16

## 1. Why you are being asked

The founder ruled on a list of outstanding issues on 2026-10-16. Four are now
built and tested. Three are NOT built, deliberately, because each one turns out
to need a design decision rather than code — and his standing instruction is
that a fix is suggested to him, never auto-applied.

Your job has two halves, and the second is the one that matters most.

**Half one: check the built work and APPLY what you find.** Everything below is
CC1's own work from today. Check it under `a` (analyse dispassionately), `f`
(FFAFP — Find, Follow, Analyse with tools, Fix, P-pass) and `sy` (use SymPy,
z3, SciPy, NumPy, statsmodels or mpmath, and cross-verify every computational
claim with at least two of them). Where you find a defect, FIX IT and deliver
the fix as a file.

**Half two: answer the three open design questions in section 4.** CC1 has a
position on each and states it, so you are not guessing at a blank page. The
positions may be wrong. Disagreement is preserved as information here: this
round runs WITHOUT compelled convergence, so if you disagree with CC1 or with
each other, say so and say why rather than converging for its own sake.

## 2. The three formal standards every answer is judged against

These are the founder's own terms. Use them explicitly.

**`simplest sufficient`.** The simplest fix that addresses the root cause and
the downstream consequences. Not the most general, not the most configurable.
If a fix needs a new flag, a new table or a new module, say why the simpler form
fails.

**`additive`.** Work must ADD to reliability, functionality, accuracy and
robustness. A feature may not be removed or narrowed without a COMMITTED
MEASUREMENT showing the replacement dominates on a named property — a judgement
that something is better is not evidence that it is. The standard is SYMMETRIC:
an addition that nothing reaches is not additive either. Every new flag, gate,
subcommand or entry point must be wired to a caller and executed by a test. Over
this project's record since 2026-08-01, 11 confirmed defects were additions that
did nothing and 0 were removals of something needed.

**`composability`.** A fix must compose with what is already there rather than
sitting beside it. Two mechanisms that answer the same question in two places
will diverge; this round contains a worked example of exactly that.

## 3. The built work, to check and correct

Read these files. Run the tests. Run the producers.

### 3.1 Identifier normalisation — `bench/runner_core.py`

HIS RULING, verbatim: *"We normalise going forward, since recording vendor names
is purely a recording statistic and has no impact on capability, or how our
experiments work."*

The runner prefixed the seat label to whatever identifier a model chose for
itself, so a seat dispatched as `Gemini-SIM` writing `GEMINI_F004` produced
`Gemini-SIM_GEMINI_F004`, in which a reader meets a bare vendor name. The seat
label was always correct; the bare name arrived inside the model's own text.

What was done: `_strip_redundant_vendor_prefix` removes the seat's OWN vendor
token, and one shared `_compose_finding_id` replaces the six separate copies of
the composition that previously existed. Five of the six were
model-supplied paths that `_structurally_valid_fid`'s own docstring already
enumerated; the sixth was the verdict-owner path.

Nothing recorded is rewritten. Rewriting run 2's findings to clear a cosmetic
defect would falsify experimental evidence, so the archive's two pre-repair
identifiers are PINNED BY NAME in
`bench/tests/test_sim_naming_and_integrity_directive.py`, which fails on any
other and also refuses a pin naming something the archive does not contain.

<!-- figure: distinct per-seat coherence budgets in force | scripts/what_budget_does_each_seat_actually_get_2026-10-16.py | [0.01, 0.012, 0.015, 0.02] -->

**Check in particular:** CC1's first version of this fix took its candidate
tokens from the whole of `MODEL_SPECS`, which meant that under seat `CC2-SIM`
the identifier `GEMINI_F004` — a CC2 reply REFERRING to Gemini's finding —
stripped to `F004` and composed to `CC2-SIM_F004`, resolving to CC2's own F004.
A cross-model mis-attribution. It was narrowed to the seat's own token. Execute
the current form and try to find a remaining case where one seat's reference
can be resolved onto another seat's finding. `_resolve_finding_key` in
`bench/reference_runner_v3.py` is where that would bite, because an unresolved
MERGE source is mandated to be read as a CONFIRM — a silent verdict inversion.

### 3.2 Composer provenance in the dispatch record — `bench/reference_runner_v3.py`

The coherence budget recalibration in `bench/cdsfl_registry/composer.py` could
never work, and the reason is arithmetic. `calibrate_coherence_thresholds`
prefers a recorded `constraint_density` and otherwise estimates
`floor(c/70)/floor(c/4)`. No archived dispatch entry carried any composer
field. What they carried was `prompt_length`, which is the length of the
TRUNCATED prompt copy that `save_output` is passed — `prompt[:200] + "..."`,
i.e. 203 characters. SymPy, NumPy and mpmath agree that
floor(203/70)/floor(203/4) = 2/50 = 1/25 exactly, and z3 and SymPy
independently agree that {200, 201, 202, 203} is the complete integer band on
which that ratio holds. So the truncation length lands at the top of that band
and the value was FORCED for essentially every entry.

<!-- figure: share of dispatch entries at the truncation length | scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py | 96.7646% -->
<!-- figure: the estimator's forced ratio at that length | scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py | 1/25 -->

What was done: `_composer_record_fields` records `constraint_count`,
`token_estimate`, `constraint_density`, `coherence_budget` and `cid`, plus the
untruncated `prompt_chars_full`, at all four dispatch record sites.
`prompt_length` is NOT reinterpreted, because rewriting it would silently change
what every archived entry means. A composer fallback is recorded as
`composer_fallback: true` rather than by omitting the keys, since an absent key
and a failed composition are different facts.

**Check in particular:** whether recording these fields can change any verdict,
and whether a replay of an older run still parses. CC1 claims replay is NOT
invalidated — older runs simply lack the new keys and take the existing fallback
— which is narrower than what the founder was told on 2026-10-15. Try to refute
that.

### 3.3 The boundary-band verdict — `bench/reference_runner_v3.py`

`_estimate_gamma` returns 0.0 for four distinct reasons and only one of them is
a slope of 0.0; its own mirror `_gamma_is_estimable` names the other three. The
boundary-band block compared the two band edges for equality, so two SENTINELS compared equal and the run was reported *robust to the whole rubric
disagreement* on the strength of a gamma that was never measured.

<!-- figure: archived blocks claiming robust on two sentinels | scripts/the_band_verdict_rests_on_a_sentinel_2026-10-16.py | 38.4615% -->

It failed in both directions, which is why the repair is a gate and not a sign
flip: two sentinels read TRUE where the answer is "unreadable", and one real edge
against a sentinel read FALSE, a false alarm. Estimability now travels with the
number, from the SAME predicate the gate uses, and `verdict_robust_to_band` is
null where either edge is not estimable.

**Check in particular:** the composability claim. CC1 asserts that reporting
`gamma_is_estimable` per threshold, from the gate's own predicate, is better than
having the band block re-derive estimability itself. Test whether the two can
still disagree.

### 3.4 Model admission — the measurement, not yet a fix

HIS QUESTION, verbatim: *"adding, removing, or changing models in the harness
should be an entirely trivial affair (by design) and should not require major
code changes to enable researchers to do so. The question is, is it? Have we
adequately addressed this particular design objective?"*

Answered two ways. Structurally, an AST walk finds 156 per-model tables across
67 files, but that total overstates the answer about threefold: 86 sites are
tests, which guard the roster rather than admit to it, 50 are historical one-off
experiment runners whose edit would alter what those runs did, and the LIVE
harness is 12 tables across 6 files plus one per-model registry `.toml`.

The count is modest. The failure mode is not.

<!-- figure: admission steps that fail silently | scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py | 71.4286% -->

A model that does not exist was put through the real resolution chain. Most steps
default SILENTLY and only two fail loudly, so a researcher who misses one table
gets a seat that RUNS while losing whatever that table gated — the class
`base_model_label`'s own docstring calls *"a capability lost with no error"*.

## 4. The three open questions. This is the substance.

### Q1. Should the coherence DENSITY budget govern anything at all now?

CC1's position: probably not, and saying so is more useful than wiring it up.

The reasoning. The budget's only effectful consumer was `_prune_for_coherence`,
which the founder retired by default on 2026-10-13: *"I also agree the
mechanical directive pruner should be retired. We have no way of knowing what it
feeds, or has been feeding our models."* With pruning off, the budget's sole
remaining effect is a warning in `bench/cdsfl_registry/composer.py` stating that
*"Coherence penalty kappa(m,g) < 1 applies to effective detection"* — and
nothing computes or applies that kappa. Every kappa in the tree is the
convergence metric. So the warning asserts a penalty that is not in force.

And the purpose his ruling names is a different quantity. *"It exists so that
models never get fed work that is larger than they have been demonstrably proven
to be able to handle in any experiment"* is a SIZE ceiling, and the per-seat
fingerprint already measures `max_successful_context_chars`,
`max_successful_prompt_chars`, `measured_attention_span`,
`compression_threshold` and `decomposition_recommended` from real runs. The
coherence budget is a directive-DENSITY ceiling.

**What you are asked.** Is CC1 right that these are two mechanisms for two
different quantities, and that the fingerprint ceiling is the one his ruling
describes? If so, what is the `simplest sufficient` disposition of the density
budget — correct the false kappa warning and leave the budget inert, implement
kappa, or wire the budget to the size ceiling? If CC1 is wrong, say what the
density budget should govern and what measurement would show it working.

Note the composability trap before answering: `MODEL_COHERENCE_BUDGETS` resolves
through `COMPOSER_MODEL_MAP`, and four of its five keys name SUPERSEDED model
versions against the current `MODEL_ROSTER` — `opus_4_6` against Opus 4.7,
`chatgpt_5_4` and `codex_5_3` against GPT-5.5, `deepseek_v3` against DeepSeek V4
Pro. So a live seat inherits a dense-instruction allowance written for a model
no longer in the roster, selected by its NAME. His ruling of 2026-10-07 is
*"Names are recorded for provenance only!"* Any answer that makes the table
MORE reachable has to deal with that.

### Q2. Derived-capability routing: what happens on a cold start?

A previous free panel designed the derived-capability fix and both seats rejected
the operator's proposed retirement rule, on different grounds, and both were
right. The design was never merged. The open part is the cold start: if a seat's
routing weight is derived from its measured record, a seat with no record yet has
no weight.

**What you are asked.** The `simplest sufficient` cold-start rule, and the
measurement that would show it is not quietly privileging or starving a new
seat. Be concrete about where it lives in `bench/reference_runner_v3.py`.

### Q3. Should model admission become a single registration point?

CC1's position: yes, but the loudness comes first.

The reasoning. Reducing 12 edits to 1 is worth having, but it is the silent
defaulting that costs capability, and a single registration point that still
defaults silently would hide 12 misses behind 1. So the `simplest sufficient`
first step is to make a missing registration FAIL LOUDLY at dispatch, and the
consolidation second.

**What you are asked.** Whether that ordering is right, and what the loud
failure should be — a raise, a refusal to dispatch that seat, or a run-level
preflight. This changes how every seat is configured, so it is being put to the
founder either way; your job is to give him the strongest version of the options
and the measurement that distinguishes them.

## 5. How to work, and what to deliver

RUN things. Do not describe them. Execute the tests named above, execute the
producers named above, and execute your own checks. The tool output IS the
evidence; reasoning selects and interprets it but never substitutes for it.

Use `sy`: SymPy, z3, SciPy, NumPy, statsmodels, mpmath. Every computational
claim needs at least two independent tools agreeing, and every proportion you
report needs a confidence interval — Wilson and Clopper-Pearson, the exact one
cross-checked between statsmodels and scipy. Name the instrument: say what
gamma, rho, S_k, sigma, nu, the two-sided gate, severity, or a Wilson interval
tells you about the question you are answering, and why that instrument rather
than another.

**Deliver each fix as a file, written INTO the sandbox repository tree at its
real path.** A fix left in prose or in scratch space is destroyed at teardown
and is not delivered. Rounds 5 and 6 of an earlier panel returned 0 source files
for exactly this reason.

**Every fix needs a runnable falsifier that you have EXECUTED, and its output.**
A fix you have not tried to break is a hypothesis, not a fix. Mutate your own
repair and show the test going red; a test that survives the mutation of the
thing it guards is verifying nothing.

**State what would refute you.** For each answer, name the evidence that would
overturn it. An answer with no refutation condition is an opinion.

Do not propose demoting gamma. It is load-bearing and that is settled.

Do not rewrite anything under `bench/logs/`. It is experimental evidence.

### Output fields, per question and per finding

- `QUESTION` or `FINDING_ID`
- `CLAIM` — one sentence
- `EVIDENCE` — the command you ran and its output
- `INSTRUMENT` — which mathematical tool, and what it told you
- `FIX` — the file you wrote and its real path
- `FALSIFIER` — the test you ran against your own fix, and its output before
  and after the mutation
- `STANDARD` — how the fix satisfies `simplest sufficient`, `additive` and
  `composability`
- `REFUTED_BY` — what evidence would overturn your answer
- `DISAGREEMENT` — where you disagree with CC1 or the other seat, and why

### Termination

Stop when further passes produce no new above-threshold findings, or when you
reach diminishing returns. A finding is above threshold if missing it could
cause real-world failure. Do not nitpick, do not generate findings for their own
sake, and do not push back on valid design choices. Two consecutive passes with
nothing new is the stop condition.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 165 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_the_outstanding_issues_2026-10-16) -->

All three files are written into the repository tree. Three findings, two SOUND verdicts, three answers.

---

# HALF ONE — the built work

## F001 — the estimability gate left the end-to-end band guard RED

**CLAIM.** §3.3 broke `test_boundary_band_executes_2026-09-04.py`, and the replacement test reaches the `False` verdict only through a monkeypatched producer — which is precisely the failure mode that file was written to forbid.

**EVIDENCE.**
```
$ python3 -m pytest bench/tests/test_boundary_band_executes_2026-09-04.py -q
FAILED ...::test_it_returns_false_for_a_band_sensitive_registry
   assert None is False
FAILED ...::test_both_outcomes_are_reachable
   verdict_robust_to_band produced only {None, True}
2 failed, 3 passed
```
`_band_sensitive()` puts every critical inside [0.65, 0.75), so the 0.75 edge sees an all-zero series: `gamma_estimable_at_upper_edge: False`. The 2026-09-04 test was asserting `False` **on the sentinel** — it was itself resting on the defect CC1 removed. But nothing replaced it: `test_the_band_verdict_is_gated_on_estimability_2026-10-16.py` reaches all three values by `monkeypatch`ing `_settled_novelty_series`, i.e. with one of the two halves stubbed. That file's own docstring: *"Only running both halves against each other finds that class."*

**INSTRUMENT.** Exhaustive search over the registry fixture space (`severity ∈ {0.70, 0.95} × 4 rounds`, 390 625 combinations) through the real `gamma_threshold_profile`: 149 795 registries give both edges estimable, both non-zero, and differing. `False` is still reachable — the repair did not narrow the diagnostic, it only unmoored the test. Minimal natural witness: `4,3,2,1 @ 0.95` + one `0.70` in round 3 → lower 0.2727, upper 0.3247, both estimable → `False`.

**FIX.** `bench/tests/test_boundary_band_executes_2026-09-04.py`. Added `_band_discriminating()`; moved the `False` assertion onto it with added guards that both edges be estimable *and* non-zero (so it cannot pass on two clamped zeros); kept `_band_sensitive()` with its own assertion that it is now `None`, documented as the "real edge vs sentinel" false-alarm class the producer counts at 4/26; strengthened `test_both_outcomes_are_reachable` → `test_all_three_outcomes_are_reachable`, `{True, False}` → `{True, False, None}`. No assertion deleted.

**FALSIFIER.**
```
--- BASELINE (repaired) --- 6 passed
--- MUTATION 1: gate removed from runner ((_lo == _hi) if _readable else None -> (_lo == _hi)) ---
    2 failed: test_a_sentinel_upper_edge_reports_no_verdict_rather_than_a_false_one
              test_all_three_outcomes_are_reachable
--- MUTATION 2: discriminating fixture neutered (+ [_finding(3, 0.70)] -> + []) ---
    2 failed: test_it_returns_false_for_a_band_discriminating_registry
              test_all_three_outcomes_are_reachable
--- RESTORED --- 6 passed
```

**STANDARD.** `simplest sufficient` — one fixture, no new module. `additive` — the diagnostic's reachable range goes 2 → 3 values, all three now driven through the real series reader. `composability` — it composes with CC1's monkeypatched test rather than replacing it: that one pins the gate's *logic*, this one pins the producer/consumer *contract*. Neither alone catches both; running them together is a demonstrated advantage, not a coexistence claim.

**REFUTED_BY.** A registry shape reaching `False` that my enumeration missed in a way that makes the new fixture degenerate; or evidence that a clamped `0.0` (β ≥ 1) should also be treated as unreadable, which would move `_band_discriminating`'s guards.

---

## F002 — `composer_fallback` is written at 4 sites and read at 0, and it is worse than inert

**CLAIM.** §3.2 records `composer_fallback: true` *and* `directive_chars`/`prompt_chars_full` on the fallback branch; the char keys sit ahead of `prompt_length` in the estimator's `or`-chain while `constraint_count` is absent there — so a failed composition now reaches `floor(c/70)/floor(c/4)` on the **full** prompt.

**EVIDENCE.** Real `calibrate_coherence_thresholds`, 8-entry fixture:
```
OLD (archive shape)        -> {'CC2-SIM': 0.04,   ...}
NEW (composed)             -> {'CC2-SIM': 0.022,  ...}
NEW (composer_fallback)    -> {'CC2-SIM': 0.0567, ...}   <-- estimated, not measured
```
**INSTRUMENT.** The producer's own asymptote. `floor(c/70)/floor(c/4) → 2/35 = 0.0571428…` as c grows; 0.0567 at c = 6000 is that asymptote. So the repair would have traded a *visibly constant* artefact (1/25, forced at 3589/3709 entries, 96.7646%, Wilson [96.1451%, 97.2874%]) for a *varying* one — which reads as measured while containing no constraints at all. That is a strictly worse failure than the one being fixed, because it is no longer self-evidently broken.

**FIX.** `bench/cdsfl_registry/composer.py` — one guard before the density extraction: skip an entry whose `composer_fallback is True`. Wires the flag to its only possible consumer.

**FALSIFIER.**
```
--- BASELINE --- 7 passed
--- MUT A: guard removed entirely --- 1 failed: test_a_fallback_entry_yields_no_calibrated_threshold
--- MUT B: `is True` -> `is not None` --- 1 failed: test_a_successful_composition_is_not_skipped
--- MUT C: detection-penalty claim restored --- 1 failed: test_no_detection_penalty_is_asserted
--- RESTORED --- 7 passed
```
`test_the_flag_is_what_does_it_and_not_the_absent_constraint_count` strips the flag from the same entries and requires them to calibrate — without it the guard would pass for the wrong reason. Archive replay pinned at exactly 0.04.

**STANDARD.** `simplest sufficient` — three lines, no flag, no table. `additive` — converts a 4-site/0-consumer write into a consumed one; `is True` (not truthiness) leaves every archived entry on its existing path. `composability` — it composes with CC1's "an absent key and a failed composition are different facts", which was the right call and simply had no reader.

**REFUTED_BY.** A consumer of `composer_fallback` elsewhere that I missed; or a decision that a character estimate on a fallback prompt is *wanted* telemetry, in which case the field should be emitted under a distinct name rather than entering the density series.

---

## F003 — the budget warning asserts a penalty that nothing computes

**CLAIM.** `"Coherence penalty κ(m,g) < 1 applies to effective detection"` told the operator a detection penalty had been applied to that dispatch. None had.

**EVIDENCE.** `grep -rn "κ\|kappa" bench/cdsfl_registry/*.py` → one hit, the warning string itself. Every `kappa` in the live tree is `kappa_set`, the §7.13 convergence metric — a different quantity. With `_prune_for_coherence` retired by default (2026-10-13), the budget has no effectful consumer at all.

**FIX.** `bench/cdsfl_registry/composer.py` — the density comparison is still reported; only the unsupported consequence is withdrawn. Guarded by `test_no_detection_penalty_is_asserted` (behavioural, catches the warning) and a source assertion that the retracted phrase cannot reappear. **STANDARD.** Pure accuracy; no behaviour changes.

---

## SOUND — §3.1 identifier normalisation

**CLAIM.** I can find no remaining case where one seat's reference resolves onto another seat's finding. CC1's narrowing holds.

**EVIDENCE.** Brute force over the real roster × `{_, -, :}` × `{F004, C0007, F12}`, 810 (seat, reference) pairs through the real `_strip_redundant_vendor_prefix` / `_compose_finding_id`:
```
strip CHANGED the string in 90 of 810 pairs
seat tokens that are a separator-bounded PREFIX of another: 5
    ('CC2','CC2-SIM') ('ChatGPT','ChatGPT-SIM') ('Codex','Codex-SIM')
    ('DeepSeek','DeepSeek-SIM') ('Gemini','Gemini-SIM')
```
**INSTRUMENT.** The prefix relation is the structural precondition for the hazard, and it holds **only between a seat and its own `-SIM` form**. No cross-vendor prefix exists, so no reference to seat B can shed B's token under seat A. The 90 changed pairs all land on `X_SIM_<id>` — a key no registry contains — so they resolve to nothing, exactly as before the change. In `_resolve_finding_key` the original candidates still come first and unchanged, so nothing that resolved before resolves differently. 134/134 naming tests pass.

**One accuracy point, below threshold.** The comment claims *"an already-composed identifier is not shortened to `SIM_F004`"* unconditionally. That guarantee holds only when `model_id` ends with `-SIM`; under a bare seat label `CC2`, `STRIP("CC2-SIM_F004","CC2") == "SIM_F004"`. Unreachable in a live run (bare and `-SIM` labels do not co-occur) and it resolves to nothing either way. Noted, not fixed.

## SOUND — §3.2 replay is not invalidated

Archive-shaped entries calibrate to exactly 0.04 before and after. CC1's narrower claim is correct and the 2026-10-15 statement to the founder was the overclaim. With F002's guard applied, that remains true.

---

# HALF TWO — the three questions

## Q1 — should the coherence DENSITY budget govern anything?

**CLAIM. CC1 is right, and I can prove it mechanically rather than argue it. The disposition is: correct the warning (done), leave the budget inert, and do NOT wire it.**

**EVIDENCE — the part CC1 did not find.** `update_coherence_budgets_from_experiments` does `MODEL_COHERENCE_BUDGETS.update(calibrated)`. `calibrated` is keyed by the raw `entry["model"]` string — the **seat label**. The lookup at `composer.py:1763` is `MODEL_COHERENCE_BUDGETS.get(model, …)` where `model` is the **composer key**.
```
seat CC2      -> composer key opus_4_6       | calibrator emits 'CC2'       MATCH=False
seat ChatGPT  -> composer key chatgpt_5_4    | calibrator emits 'ChatGPT'   MATCH=False
seat Codex    -> composer key codex_5_3      | calibrator emits 'Codex'     MATCH=False
seat DeepSeek -> composer key deepseek_v3    | calibrator emits 'DeepSeek'  MATCH=False
seat Gemini   -> composer key gemini_3_1_pro | calibrator emits 'Gemini'    MATCH=False
```
0 of 5. **The recalibration pipeline writes into a key space its consumer never reads, for every seat in the roster.** This is independent of the `prompt_length` artefact and survives §3.2's repair entirely: CC1 fixed the input to a pipeline whose output cannot land. That is the worked example of two mechanisms answering one question in two places, and it is the strongest available evidence that the density budget governs nothing.

**On the two-quantities claim.** Upheld. The fingerprint ceiling measures `max_successful_prompt_chars` etc. — a **size** ceiling, which is what *"never get fed work larger than they have been demonstrably proven to be able to handle"* describes. The coherence budget is constraints-per-token. Different units; neither is a proxy for the other.

**Do not implement κ.** It would be an addition nothing reaches twice over: no consumer exists, the only effectful one is retired, and the detection model that would use it (`R_k(i)`, §3/§16 operational) already carries η, σ, ν and S_k with no κ term. **Do not wire the budget to the size ceiling** — that composes two mechanisms for two quantities on no demonstrated advantage, which is exactly what the founder's 2026-10-02 ruling forbids.

**On the composability trap.** It is sharper than stated. 4 of 5 keys name superseded versions, *and* those stale keys are the only ones that produce a non-default budget — the measurement shows distinct budgets `[0.01, 0.012, 0.015, 0.02]` with the hop and `[0.015]` without it. So the table's entire discriminating power comes from names the 2026-10-07 ruling says decide nothing. **Any repair that makes it reachable first has to re-key it onto something measured.** Leaving it inert is the only option that does not require that decision first — which is itself the argument for inertness.

**REFUTED_BY.** A consumer of `coherence_budget` or `constraint_density` that changes a dispatch, a verdict or a prompt, anywhere outside `_prune_for_coherence`. I found none; one would overturn this.

**DISAGREEMENT with CC1.** None on the conclusion. CC1's reasoning stopped one link short: it argued from "the consumer is retired" and "κ does not exist". Both true, but both reversible by a future ruling. The key-space mismatch is the harder fact — the mechanism was never connected at all.

---

## Q2 — derived-capability routing on a cold start

**CLAIM. Keep `DEFAULT_FALSIFIER_STRENGTH` as the cold-start order, and make the derived key take over per-seat as evidence arrives — but the retirement trigger must be a `routing_weight_is_estimable` predicate, NOT a lower bound of zero, because the bound at n = 0 is `nan`, not `0.0`.**

**EVIDENCE.** The prior panel's stated premise — *"a seat with no measurements has a lower bound of 0 and sorts last"* — is arithmetically wrong at the only point that matters:
```
n= 0 k=0  Wilson lo=nan   CP lo=nan
n= 1 k=0  Wilson lo=0.0   CP lo=0.0
```
And a `nan` sort key is not "sorts last":
```
distinct orders from a nan key over 720 input orders: 720
nan < 0.0 : False | nan > 0.0 : False | nan == nan : False
distinct orders from a 0.0 key with a NAME tie-break: 1
distinct orders with DEFAULT_FALSIFIER_STRENGTH:      1
```
**INSTRUMENT.** Wilson vs Clopper-Pearson, cross-checked statsmodels ↔ scipy (upper bound at n=5,k=0: 0.5218237501 both, agree to 1e-12). The comparison `nan < x` is false in both directions, so the ordering relation is **non-transitive** and Python's sort silently returns an input-order-dependent permutation. This reproduces the 2026-10-08 measurement (12 shuffles → 12 orders) and explains *why*: not a tie, an undefined comparison. A tie is detectable; `nan` is not.

The retirement threshold reproduces exactly — SymPy `n = z²/δ²` → 42.682876 → **43**; z3 `N ≤ 42` **unsat**, `N == 43` **sat**; Wolfram Language (local kernel, exit 0) `42.68287578549027`. Three independent tools.

**WHERE IT LIVES.** `bench/reference_runner_v3.py:7988-7989` inside `_apply_routing` — `_roster = _declared_models(...)`, `models = [mc.label for mc in _roster]` — and the reorder itself at `bench/routing.py:125-156` (`rank_falsifier_writers`). Cold start is **not** an edge case: `fingerprint_scope` defaulted to `"experiment"` on 2026-10-16, so `_load_fingerprints` returns `{}` and every seat is cold at round 0 of every run.

**THE RULE.** Mirror `_gamma_is_estimable`, this repo's own settled precedent for exactly this shape (*"A caller that gates on 0.0 without this distinction either gates on a sentinel or demotes gamma; both have happened"*):

- `routing_weight_is_estimable(seat) ≡ n_outcomes(seat) ≥ 43`, from the same function that computes the weight.
- Not estimable → the seat keeps its `DEFAULT_FALSIFIER_STRENGTH` rung. Estimable → Wilson lower bound orders it. Mixed rosters are the normal case and are fine: estimable seats sort among themselves, inestimable ones hold tuple order.
- The tuple is never deleted. It is a committed Exp 42 measurement, and it is the only ordering information that exists at n = 0.

**THE MEASUREMENT that shows it neither privileges nor starves a new seat.** Two-sided, pre-registered, over simulated runs:
1. **Starving** — rung-position of a new seat vs its true capability, over 43+ rounds. A new seat must be *dispatched* at least `43 / (rungs it can reach)` times, or it can never become estimable: a weight that requires evidence the ordering prevents it from acquiring is a trap, and this is the number that detects it.
2. **Privileging** — Fisher exact on confirm-rate, new seat vs incumbents, at the crossover round. The existing baseline is 0/10 model pairs separating (all p ≥ 0.306), so any detected separation at crossover is the rule's doing, not capability.
3. **Determinism** — 720 input permutations must yield 1 order while any seat is inestimable. This is the direct regression guard against the `nan` defect and costs nothing to run.

**REFUTED_BY.** Evidence that `n_outcomes ≥ 43` is unreachable in practice (if seats accumulate < 43 routed outcomes per experiment, the derived key never activates and the whole design is inert — check this before building). Or a Wilson implementation returning `0.0` rather than `nan` at n = 0, which would weaken the `nan` argument but not the "a tie carries no ordering" one.

**DISAGREEMENT.** With the 2026-10-14 seat that withdrew its rejection and proposed **measured dispatch cost ascending** as the tie-break: I do not adopt it. Cost is a measured quantity, which satisfies the 2026-10-07 ruling, but it is uncorrelated with falsification competence — cheapest-first systematically routes unresolved criticals to the weakest seat first and lengthens the ladder. `DEFAULT_FALSIFIER_STRENGTH` is a committed measurement *of the right quantity*; replacing it with a measurement of the wrong one is not an upgrade. Under the symmetric additive standard, that swap needs a committed measurement showing cost-order dominates tuple-order on time-to-first-confirm, and none exists.

---

## Q3 — should model admission become a single registration point?

**CLAIM. CC1's ordering is right — loudness first, consolidation second — but CC1's own measurement understates the problem, and the loud failure should be a run-level preflight, not a raise.**

**EVIDENCE that the measurement understates it.** The producer reports 5 of 7 steps silently defaulting (71.4286%, Wilson [35.8934%, 91.7781%], CP [29.0421%, 96.3307%]) and counts the composer step as a **loud raise**. It is caught:
```python
# bench/reference_runner_v3.py:12244-12254
except Exception as _cmp_exc:                          # noqa: BLE001
    model_cdsfl = cdsfl_text
    _log(f"  COMPOSER FALLBACK for {mc.label}: ...")
```
The run continues on a degraded prompt with a log line. So in the **live** chain it is 6 of 7 degrading without halting, not 5. And the 12-table count misses at least three live per-model tables — `MODEL_COHERENCE_BUDGETS` and `PHENOTYPE_TRANSFORMS` (keyed on composer keys, not roster labels, so the AST filter skipped them) and the `ModelConfig` roster inside `load_default_config()` (a list of constructor calls, not string keys — and a model absent there is **never dispatched at all**).

The worst single instance is not in the producer's 7 steps: `runner_core.py:1876`, `MODEL_SPECS.get(_spec_key(label), {}).get("L", float("inf"))`. A missing entry sets `L = inf`, and the pre-dispatch context gate at the next line **can never fire**. A capability gate that silently becomes a no-op is the exact class `base_model_label`'s docstring names.

**ON THE ORDERING — agree, and for a reason CC1 understates.** A single registration point that still defaults silently hides 12 misses behind 1 *and* removes the only current signal a researcher has (12 separate edits is at least visible work). Loudness first is not merely the cheaper first step; building consolidation first would make the system strictly worse until the second step lands.

**WHAT THE LOUD FAILURE SHOULD BE — a run-level preflight, and I disagree with the raise.**

| Option | Verdict |
|---|---|
| **Raise at each lookup site** | Reject. 15 sites to edit — the surface being complained about. It fails at *first use*, so a table consulted only on the recovery path fails mid-run, after spend. And `reference_runner_v3.py:12244` proves this codebase catches broad exceptions near dispatch: a raise would be swallowed again. |
| **Refuse to dispatch that seat** | **Reject outright.** Dropping a seat is benching it, forbidden by the same rule `_refuse_if_a_route_is_dead` already encodes — *"A DEAD SEAT REFUSES THE RUN AND IS NEVER DROPPED."* Silently losing a capability is the defect; losing the whole seat is a bigger version of it. |
| **Run-level preflight** | **Adopt.** One function, one call site, before any spend. Given a label, assert presence in every table it must be in; report **all** misses at once, not the first; refuse the run. |

Precedent and composability: `validate_all_policies()` (`cdsfl_registry/registry.py:286`) is the architectural model and is **not wired into the live runner** — this composes by extending it to the in-code tables and calling it from the existing `run_preflight` (`reference_runner_v3.py:16931`), which today checks connectivity only and consults no per-model table. One new call, no new entry point. Note `run_preflight` currently does `if mc.label not in baseline: continue` — a silent skip that the new check must not inherit.

**THE MEASUREMENT THAT DISTINGUISHES THE OPTIONS.** Run the fictitious-model harness (`how_many_places_must_change_to_add_a_model_2026-10-16.py`, method B) against all 15 live tables under each option, and report **(a) misses surfaced before any spend, (b) misses surfaced at all, (c) seats lost**. Preflight should give 15/15/0. Per-site raise gives roughly 1/*k*/0 with *k* < 15 — it stops at the first miss, and the composer one is caught. Refuse-the-seat gives 15/15/1, failing on (c). Pre-registering (a) as the discriminator is what makes this a measurement rather than a preference; and widening the denominator from 7 to 15 is itself the first deliverable, since the current 71.4286% is computed on a hand-picked sample.

**REFUTED_BY.** A table whose correct behaviour genuinely *is* to default — i.e. where a researcher should be able to omit an entry — which would make a blanket preflight over-strict and argue for a declared per-table "optional" marking. `CONTEXT_CHAR_BUDGET_CEILING` is the plausible candidate and should be checked before the preflight's table list is fixed.

**DISAGREEMENT with CC1.** Two. (1) The headline figure: 5 of 7 should be 6 of 7 in the live chain, and the denominator should be 15 tables, not 7 steps — the understatement matters because the founder is being asked to rule on "is this trivial?" and the honest answer is less trivial than reported. (2) CC1 leaves the loud-failure mechanism open between three options; I rule one of them out on existing policy rather than on measurement — refusing to dispatch a seat is already forbidden, so it should not be put to him as a live option.

---

**Termination.** Two consecutive passes produced nothing new above threshold: the cross-model hazard enumeration (0 reachable cases over 810 pairs) and the `_gamma_is_estimable` / `_estimate_gamma` mirror check (0 disagreements over 21 845 vectors; the one unmirrored branch, `|denom| < 1e-12`, requires a round index > 10⁶ — SymPy and mpmath both `1e+06`, z3 `unsat` below it).

**Not mine:** `test_note_naming_check_2026-09-28.py::test_compare_backends_executes_both_and_reports_a_ci` fails in this sandbox because there is no `.git` (*"can only run from a populated git checkout"*). Pre-existing and environmental.

**Tool note.** Wolfram ran locally (exit 0, no `Name::tag`, no `$Failed`) and confirmed one value only: `z²/δ² = 42.68287578549027`, attributed to Wolfram Language. Every other claim rests on the open-source set, two tools minimum.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 91 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_the_outstanding_issues_2026-10-16) -->

All checks converged: two consecutive passes produced nothing new above threshold. Final report.

---

# HALF ONE — the built work, checked and corrected

## 3.1 Identifier normalisation — SOUND, with one adjacent defect found and fixed

**FINDING_ID: F1 — `_resolve_merge_source` resolves a cross-seat merge source onto the WRITER's own finding**

- **CLAIM.** The vendor-strip itself is sound (the narrowing to the seat's own token holds under execution), but the resolver the brief pointed me at mis-attributes: in a registry where every seat holds its own F004, `MERGE … <- Gemini-SIM_F004` written by `CC2-SIM` resolved to **CC2-SIM's own F004** — the writer's distinct finding merged away (silent evidence loss) and the named finding got no verdict. 30 of 48 cross-seat forms mis-attributed (62.50%, Wilson [48.40%, 74.76%]). A second, worse sub-case: on `CC2-SIM_F004` the regex `(?:F|C)(\d+)` matches **`C2` inside the prefix**, so that form resolved to `None` — which `cdsfl_topology_formal.md:126-127` mandates reading as a **CONFIRM on the target**: a verdict inversion. The form is real, not hypothetical — the v3.1 run's duplicate records cite foreign composed ids (`Fable-SIM_F003`, `DeepSeek-SIM_F002`) verbatim.
- **EVIDENCE.** Executed sweep (`/tmp/panelchk/resolve_sweep.py`) over a 4-seat registry, pre-fix: `_resolve_merge_source: correct 12, unmatched 6, MIS-RESOLVED 30`. Post-fix: all 12 composed foreign forms correct, 0 regressions in `test_merge_integrity.py` (13 passed).
- **INSTRUMENT.** Exhaustive enumeration over the 48-form product space (deterministic, so the sweep IS the proof); Wilson interval via statsmodels, Clopper–Pearson cross-checked against `scipy.stats.beta.ppf` (agree to 6 d.p.).
- **FIX.** `bench/reference_runner_v3.py`: the source id is resolved **as written** before the digits-strip guesses — the prefixed token whose span *contains* the regex match is looked up via the writer's own alias key, then `lookup_alias_any` (which refuses ambiguity); a miss falls through to the prior candidates unchanged, so nothing that resolved before resolves differently. Companion: `_resolve_finding_key` gains `lookup_alias_any(k)` as its **last** candidate, so a corrected copy offered against a foreign composed id resolves instead of dropping UNMATCHED (the non-owner refusal downstream still governs who may act).
- **FALSIFIER.** `bench/tests/test_merge_source_resolves_as_written_2026-10-16.py` (10 tests, executed). Mutation (`if _tok and False`) → **4 failed**; restored → **10 passed**. The undemonstrated residual (bare-vendor foreign form `GEMINI_F004` cross-seat) is **pinned** by `test_known_limit_…`, not built for: it appears 0 times in the archive as a foreign reference.
- **STANDARD.** Simplest sufficient: one containment-anchored lookup before the existing chain; no vendor table, no roster key (consistent with the 2026-10-16 "no vendor table is consulted" narrowing). Additive: nothing removed; new path wired and executed. Composable: it reuses `lookup_alias_any`, the registry's existing ambiguity-refusing resolver, rather than a second alias notion.
- **REFUTED_BY.** A run artefact showing a previously-resolving merge source now resolving to a different canonical than before the fix (the sweep and `test_an_own_model_prefixed_source_resolves_exactly_as_before` say none exists).

On the brief's specific question: **CC1's narrowing is verified** — under the current strip, no seat's reference resolves onto another seat's finding *through the strip*; foreign composed ids went loudly UNMATCHED in `_resolve_finding_key`. The mis-attribution lived next door, in the resolver whose comment claimed "no vendor strip is needed here" — true, but the regex's prefix-blindness was the live hazard the comment's 48-pair measurement did not cover, because it measured the strip, not the resolver.

## 3.2 Composer provenance — SOUND, with the written-but-unread marker now wired

- **Verdict checks, executed.** Recording cannot change any verdict: `calibrate_coherence_thresholds` has **no live caller** in the runner (only measurement scripts and `update_coherence_budgets_from_experiments`, itself uncalled by the harness), and the runner reads `metadata` from 0 sites. Replay NOT invalidated: older entries lack the keys and take the estimator exactly as before — CC1's narrower claim **CONFIRMED**. Arithmetic re-derived independently: SymPy `Rational(203//70, 203//4) = 1/25`; Wolfram Language (local Wolfram Engine) `Floor[203/70]/Floor[203/4] = 0.04`.

**FINDING_ID: F2 — `composer_fallback` was written but read by nothing; a marked fallback still calibrated to an estimator constant**

- **CLAIM.** The marker whose own docstring says "the calibrator must not read the second as the first" had no reader outside tests — the written-but-never-read half of the additive standard (the project's 11-defect class) — and a marked fallback fell into the estimator, whose large-chars value tends to the constant 2/35 = 0.0571… (SymPy limit, confirmed by the producer's mpmath/NumPy path): a property of the estimator, not of any model. CC1's own test pinned this gap explicitly ("not yet gated on the marker"); I closed it.
- **FIX.** `bench/cdsfl_registry/composer.py`: the calibrator `continue`s on an entry marked `composer_fallback: true` with no recorded density. Pre-2026-10-16 archive entries (marker absent) are untouched.
- **FALSIFIER.** `test_a_recorded_fallback_does_not_silently_become_an_estimate` upgraded from pin-the-gap to assert-the-gate (fallback-only records → the declared `MODEL_COHERENCE_BUDGETS` value, never an estimate), plus a new mixed-archive pollution test with densities disjoint from both estimator constants. Mutation (`elif False and …`) → **red**; restored → **11 passed**.
- **STANDARD.** Simplest sufficient: one guard clause. Additive: completes an existing flag's wiring; removes nothing. Composable: the gate reads the marker the dispatch record already writes — one mechanism, both ends.
- **REFUTED_BY.** A measurement showing marked-fallback entries carry information about density→quality (they cannot: a fallback has no composed directive set, hence no density).

**FINDING_ID: F3 — the producer's "complete integer band" claim was false for the predicate it named**

- **CLAIM.** `scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py` enumerated a **window [150, 260]** and called the result "the COMPLETE integer band on which the ratio equals this value". False: the reduced ratio 1/25 also holds on **[100, 103]** (`floor(100/70)/floor(100/4) = 1/25`). Two tools agreeing over the same truncated domain is not completeness. The claim is true only for the unreduced **pair** floor(c/70)=2 ∧ floor(c/4)=50, whose complete solution over all integers is [140, 209] ∩ [200, 203] = [200, 203].
- **EVIDENCE/INSTRUMENT.** SymPy + z3 enumeration found {100–103, 200–203} for the ratio predicate; Wolfram Language confirmed both the 0.04 value at c=100 and, via `Reduce[Floor[c/70]==2 && Floor[c/4]==50, c, Integers]`, the unbounded pair-band {200, 201, 202, 203}. z3 in the repaired script now proves completeness unboundedly (pair constraints ∧ outside-[200,203] → **unsat**).
- **FIX.** Script rewritten: windowed enumeration replaced by the SymPy interval derivation + z3 unbounded completeness proof; the ratio predicate's other band is enumerated and printed so the wording cannot rot; the VERDICT names the pair. Its own pass gate now requires the completeness proof. Executed: exit 0, headline conclusion unchanged — 203 is the top edge of a 4-integer band forced by the truncation.
- **STANDARD/REFUTED_BY.** Headline figures untouched (additive); refuted by any integer outside [200,203] satisfying the pair, which z3's unsat excludes. This is a §10 category-3 class defect (a defect in the measurement machinery itself); the brief's sentence repeating the claim should be read as corrected.

## 3.3 Boundary-band verdict — SOUND, composability claim CONFIRMED; one red-at-HEAD test repaired

- **The composability question, answered by execution and derivation.** Can the band block and the gate's predicate disagree? **No, on any practical input.** Exhaustive check over 5,461 series plus 3,000 random fuzz: `_gamma_is_estimable` and an independent SymPy reimplementation of the estimator's early returns agree on every one, and `estimable=False ⇒ gamma == 0.0` held without exception. The one condition the mirror omits (degenerate denominator) is unreachable: by the Lagrange identity, denom = Σ_{i<j}(log(i+1) − log(j+1))², and the guard 1e-12 cannot fire before ~10⁶ rounds (1/(e^{10⁻⁶}−1) ≈ 999 999.5). Reporting the flag from the gate's own predicate is therefore strictly better than the band block re-deriving it — there is exactly one mirror and it is executed against its producer. Archive proportions re-derived: 10/26 (38.46%, Wilson [22.43%, 57.47%], CP [20.23%, 59.43%] — statsmodels and scipy agree) and 14/26 uninformative verdicts confirmed.

**FINDING_ID: F4 — the tree was red at HEAD: `test_boundary_band_executes_2026-09-04.py` was not updated for the gate**

- **CLAIM.** CC1 shipped the estimability gate without repairing the pre-existing executor test: its "band-sensitive" fixture holds only severity-0.70 criticals, so at the 0.75 edge the series is empty, the gate now (correctly) returns `None`, and 2 of its 5 tests failed on the delivered tree.
- **EVIDENCE.** `pytest bench/tests/test_boundary_band_executes_2026-09-04.py` → 2 failed before my edits touched anything near the band.
- **FIX.** `bench/tests/test_boundary_band_executes_2026-09-04.py`: new `_band_sensitive` fixture with **both edges estimable and slopes unequal** (executed: lower 0.0682, upper 0.3247, verdict False); the old fixture retained as `_band_vanishes_at_the_upper_edge` pinning the new null-with-named-reason semantics; the reachability test now demands all **three** outcomes {True, False, None}. I side with CC1's tri-state on the substance: a gamma that was never measured grounds neither boolean, and the information is not lost — `band_is_readable`, `not_readable_because` and the per-threshold series carry it.
- **FALSIFIER.** Mutated the gate back to ungated `_lo == _hi` → 2 failed (including the tri-state reachability test); restored → all green.
- **REFUTED_BY.** An argument that an empty critical series at one edge should read as "not robust": I considered and rejected it — the verdict is defined over gamma equality, and the live gate handles a vacuous critical curve through a separate branch (`gate_would_fire`'s removal note documents the executed counterexample), so asserting False there would fabricate a comparison. **DISAGREEMENT candidate preserved** if the other seat reads it the other way.

## 3.4 Model admission — measurement VERIFIED

Producer executed and reproduced: 12 live tables across 6 files + 1 `.toml`; 'Kimi' through the real chain: 5 of 7 steps default silently (71.43%, Wilson [35.89%, 91.78%], CP [29.04%, 96.33%] — both re-derived, statsmodels = scipy). The structural threefold-overstatement decomposition (86 test sites, 50 historical runners) is a fair reading; no correction needed.

---

# HALF TWO — the three open questions

## Q1. Should the density budget govern anything?

**CC1 is right on the central distinction, verified by trace.** His ruling describes a **work-size** ceiling, and that quantity is already measured and enforced: `max_successful_prompt_chars` is a proven floor feeding `get_effective_context_budget`, capped by `CONTEXT_CHAR_BUDGET_CEILING`; `DECOMPOSITION_CONTEXT_THRESHOLD` routes oversize work to decomposed dispatch. The coherence budget is constraints-per-token of the **directive text** — a different quantity. Verified, not assumed: with `_prune_for_coherence` retired by default (`composer_coherence_pruning: bool = False`), the budget's sole remaining effect was the composer warning, and the penalty that warning asserted — "κ(m,g) < 1 applies to effective detection" — **exists nowhere**: every κ in the tree is the convergence metric (`kappa_set/rate/adopt`, `bench/dm/_convergence.py`) or the HIL calibration metric (appendix §7); κ(m,g) appears only inside a prompt payload in `bench/gemini_math_audit.py` — a proposal delivered for audit, never implemented.

**Disposition (simplest sufficient): correct the false warning; leave the budget as recorded provenance; do not implement κ; do not wire it to the size ceiling.** Implementing κ fails simplest-sufficient — its only designed consumer was the retired pruner, and no committed measurement shows a density penalty predicts anything (the one calibration attempt measured a truncation constant, per 3.2). Wiring density to the size ceiling repeats the exact conflation his 2026-10-14 ruling just separated into `max_directive_chars` vs `spec_chars`. The budget is not dead weight once inert: since today it is **recorded per dispatch** (`constraint_density` vs `coherence_budget`), which is precisely the data a future ruling would need.

**Delivered (defect half only):** `bench/cdsfl_registry/composer.py` — the warning now states what is true: over-budget, recorded in the dispatch record, no penalty in force. The *disposition* beyond that, including the stale-key trap, is his to rule on. On that trap: 4 of 5 `MODEL_COHERENCE_BUDGETS` keys name superseded versions and a live seat inherits an allowance selected by NAME through `COMPOSER_MODEL_MAP` — any answer making the table more reachable must first re-key it the way the rest of the harness keys capability (per-model registry `.toml` / `base_model_label`), with values marked inherited-not-measured, exactly as `MODEL_SPECS` does for Fable. I did not change it: it is behavioural and gated on his Q1 ruling.

**Measurement that would show the budget working, if he wants it live:** a pre-registered two-arm run (density above vs below budget at matched work size) showing a drop in findings-per-1000-response-tokens at the threshold — the calibrator's own curve, now computable for the first time since the provenance fields exist. **REFUTED_BY:** such a run showing a real quality cliff at the budget — that would justify implementing the penalty, and my "leave inert" answer falls.

## Q2. Derived-capability routing cold start

**The simplest sufficient cold-start rule: lower-confidence-bound ranking with the committed tuple as tie-break — which is the structure `bench/routing.py` already carries in embryo.** A seat with no record has Wilson lower bound exactly 0 and sorts **last among the ranked**, as Fable's entry documents ("needs 12 consecutive successes before its lower bound can pass a seat at 60 of 70"); ties among no-record seats break by `DEFAULT_FALSIFIER_STRENGTH` (itself a committed Exp-42 measurement — the previous panel's finding that without it 12 shuffled inputs gave 12 distinct orders stands), then `extras` input order. No new exploration machinery: with `DEFAULT_MAX_RUNGS = 0` meaning EXHAUST, a cold seat is reached whenever every stronger rung fails, so its record accumulates without a new flag — an exploration bonus would be an addition nothing requires.

**Where it lives:** the ordering in `rank_falsifier_writers` (`bench/routing.py` — sort key becomes `(-wilson_lcb(resolved, attempts), tuple_rank)`, `-SIM` normalised as now); the attempts/successes counters in the per-seat fingerprint the runner already persists; the cap interaction at `route`'s `rungs[:_budget]` slice, called from `_apply_routing` in `bench/reference_runner_v3.py`.

**The measurement that shows it is neither starving nor privileging — and the trap it must catch:** two numbers per seat in `_routing_telemetry`: (1) **attempts within the cap** — if a configured cap (not EXHAUST) leaves a cold seat at 0 attempts after N runs, last place is self-perpetuating and the rule starves it: the falsifying test is a simulated roster with cap=2 and one cold seat, asserting the seat's attempt count is reachable; (2) **rung-depth-stratified resolve rate** — a cold seat reached only under exhaustion is measured only on the residuals every stronger seat failed, so its raw rate is biased DOWN by selection; compare Wilson intervals at matched rung depth, never raw. And the standing guard from `routing.py`'s own header applies unchanged: run `scripts/competence_provenance.py` before any re-ranking — a contaminated confirm rate contaminates the mechanics. **REFUTED_BY:** telemetry showing a cold seat with nonzero attempts whose depth-stratified interval still cannot converge — that would show LCB-ranking needs an explicit exploration provision after all.

## Q3. Single registration point — is loudness-first the right order?

**Yes, and the project's own record is the proof:** since 2026-08-01, 11 confirmed defects were additions that did nothing and the silent-default class ("a capability lost with no error") is recorded 8 times; a single registration point that still defaulted silently would hide 12 misses behind 1, and the consolidation itself cannot be *verified* without the loud check existing first — loudness is the measurement instrument for the consolidation.

**The loud failure should be a run-level preflight that refuses to start, not a raise at first lookup and not a per-seat refusal.** Grounds, by the project's own precedents: the vault-keys precondition ("NO PLAINTEXT SCORING KEY MAY EXIST WHILE AN EXAM RUNS") refuses start; `set_panel_cwd` refuses a missing directory. Comparison of the three options on the measurement that distinguishes them — *(a) paid/dispatched calls before the miss surfaces, (b) misses reported per failure, (c) whether a run can silently narrow*:

| option | paid calls wasted | misses per failure | silent narrowing |
|---|---|---|---|
| raise at first lookup | ≥1 round, mid-run | 1 | no, but partial run |
| refuse that seat only | 0 for that seat | 1 per seat | **yes** — a 6-seat run silently proceeds as 5, which is itself the lost-capability class |
| **run-level preflight** | **0** | **all seats × all 7 steps, named** | **no** |

Concretely: extend the existing `run_preflight` in `bench/reference_runner_v3.py` to walk each configured seat through the same 7 resolution steps the producer script already exercises (roster description, composer map, coherence budget, `MODEL_SPECS`, `INITIAL_FINGERPRINTS`, `compose()`, per-model `.toml`) and refuse the run with the complete per-seat miss list. The acceptance measurement is the producer's own figure: steps-that-fail-silently drops from 5/7 (71.43%, Wilson [35.89%, 91.78%]) to 0/7, tested by putting a nonexistent label through the chain with preflight on. Consolidation to one registration point (the per-model `.toml` is the natural home — it is the only admission step that is already one-file-per-model) comes second, landing table by table **behind** the preflight that proves each migration lost nothing. **REFUTED_BY:** a founder requirement that a run must degrade gracefully when one seat of six is misconfigured — that would argue for per-seat refusal plus a run-level WARNING; I think it wrong here because a panel's statistics (ladder order, convergence, co-discovery) are roster-conditioned, so a silently smaller panel is a different experiment wearing the same name.

**DISAGREEMENT with CC1:** none of substance on Q1/Q3; on Q3 I sharpen his "a raise, a refusal, or a preflight" to: preflight is not merely the best option, it is the only one of the three that cannot produce a silently narrowed run. On 3.3 I *confirm* rather than merely accept his composability claim, with the Lagrange-identity bound showing the one unmirrored estimator condition is unreachable below ~10⁶ rounds.

**Files delivered** (all tested, all falsified by executed mutation): `bench/reference_runner_v3.py` (F1), `bench/tests/test_merge_source_resolves_as_written_2026-10-16.py` (F1, new), `bench/cdsfl_registry/composer.py` (F2 + Q1 warning), `bench/tests/test_the_dispatch_record_carries_composer_provenance_2026-10-16.py` (F2), `scripts/the_recorded_prompt_length_forces_the_estimator_2026-10-16.py` (F3), `bench/tests/test_boundary_band_executes_2026-09-04.py` (F4). Final state: **203 tests green** across every touched file; nothing under `bench/logs/` modified. Wolfram results above are attributed to Wolfram Language (local Wolfram Engine); it served as second falsifier only — every claim stands on the open-source tools alone.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_the_outstanding_issues_2026-10-16/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
