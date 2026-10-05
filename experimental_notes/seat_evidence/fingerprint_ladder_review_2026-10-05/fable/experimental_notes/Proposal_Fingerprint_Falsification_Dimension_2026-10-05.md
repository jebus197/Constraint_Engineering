# Proposal — give the capability fingerprint a falsification dimension, and key the routing ladder on it

**Status: PROPOSAL. Nothing implemented. Founder ruling required.** Written 2026-10-05 02:35 BST.

---

## The gap, measured

`bench/routing.py` routes an unresolved critical "to progressively STRONGER models (ordered by capability fingerprint)". That phrase is from the module's own docstring, and it is the **only** occurrence of the word "fingerprint" in the file. The code reads no fingerprint. It ranks on `DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek")`, a frozen 5-tuple of bare vendor names derived from Exp 42 in June 2026 and never re-derived.

Meanwhile `_update_observed_fingerprint` writes a live profile for every model every round, `_save_fingerprints` persists it to `bench/fingerprints/`, and `burst_planner.py` and `_should_decompose` consume it. So the schema already measures per-model capability continuously, and the ladder is the one consumer that ignores it.

**The ladder's ordering is therefore a measured statistic that stopped measuring in June 2026.**

### Why it cannot simply be swapped today

The glossary defines the fingerprint as a 4-dimensional profile `(D, v̄, A, C)` — decay rate, verification score, verified findings, coverage — citing appendix §7.9. The 15 fields actually written are:

`D_decay`, `attention_ratio`, `avg_findings_per_round`, `compression_threshold`, `decomposition_recommended`, `failure_modes`, `max_failed_context_chars`, `max_failed_prompt_chars`, `max_successful_context_chars`, `max_successful_prompt_chars`, `measured_attention_span`, `prompt_chars_history`, `quality_at_capacity`, `rounds_participated`, `total_findings`.

There is **no verification score and no coverage dimension**. `total_findings` counts raw findings, not verified ones. The implemented fingerprint measures context capacity and productivity; it does not measure falsification quality. The documented profile and the implemented one disagree, and the missing dimension is precisely the one the ladder needs.

---

## The proposal

Add one measured dimension, record it in shadow, and promote it to the ladder only on evidence.

### 1. The quantity

For each model, per run:

```
v_falsif  =  confirmations whose falsifier is PROVENANCE-CLEAN
             ────────────────────────────────────────────────
             falsifiers it supplied that reached a verdict
```

Denominator excludes `ERROR` and no-falsifier cases, which are a *supply* problem and are already measured separately. Numerator counts a CONFIRMED verdict **only** where the falsifier demonstrably read its target.

### 2. Why the provenance gate is load-bearing, not decoration

This is the hazard `bench/routing.py` already names in a ★-marked founder observation, and it is measured. On Exp 55, a prose target, while the empty-working-directory defect was live:

- **Gemini: 2 of 2 CONFIRMED, both falsifiers DETACHED** — they open nothing and restate the document's numbers from memory.
- **DeepSeek: 0 of 2**, both falsifiers genuine readers that ERRORed on the missing file.

A naive confirm-rate ranking re-derived from that run **promotes Gemini to first and demotes DeepSeek to last — ranking models by their willingness to ignore the evidence**, which is the exact inversion the discrimination control exists to detect. `scripts/competence_provenance.py` already exits 2 and prints UNSAFE TO RANK ON for this condition. It becomes a gate on pool entry rather than an advisory script.

### 3. Estimator

Per-model Beta-Binomial with a pooled prior, which is **machinery this project already has**: `ImmuneMemory` uses Beta-Binomial per-flaw-class priors with CUSUM drift (appendix S1.5). That is one of the 3 capabilities currently unarmed in the simulated runner, so arming it and adding this dimension are naturally the same piece of work.

A minimum sample size per model before its posterior is allowed to reorder the ladder. Below it, the frozen order stands.

### 4. Promotion path — shadow first

Nothing changes in the ladder on day one. The dimension is recorded, and a shadow ranking is computed and logged beside the frozen one every run. Promotion requires showing the shadow ranking does not distort — the project's standing pattern for shadow elements, and the same discipline applied to `hierarchical_novelty_convergence`.

**This is additive in both directions.** `DEFAULT_FALSIFIER_STRENGTH` is retained as prior and as cold-start fallback; nothing is removed. And the new dimension is wired to a caller and executed by a test, so it is not an addition nothing reaches.

---

## The strongest objection, stated first

**The ranking would be computed on a non-random assignment, and the assignment is made by the ranking.**

The ladder routes findings *the weak models could not resolve* to the strong models. So a strong model's falsifiers are attempted against a systematically harder population than a weak model's. Its confirm rate is therefore depressed by the very fact that it is trusted. Left uncorrected, a measured ladder could demote exactly the models it should promote, and then feed that demotion back into the next assignment.

This is a selection effect, not noise, and it does not average out with more data.

**Candidate mitigations, none yet tested:**

1. **Stratify by finding difficulty.** Compare confirm rates only within a difficulty band. Requires a difficulty measure; `difficulty_ladder` / `difficulty_tier` tokens already appear in `bench/falsifier_verify.py`'s guard patterns, so something of the kind may exist.
2. **Measure on first-pass falsifiers only** — every model's own findings, before any routing — which is a common population by construction.
3. **Record the rung at which each attempt was made** and model rung as a covariate.
4. **Accept the bias and use the frozen order as a prior strong enough to resist it**, treating the measurement as drift detection rather than as ranking.

Option 2 is the cheapest and most defensible, and it is what the Exp 42 derivation effectively used. It is my recommendation, but it measures a different thing from what the ladder does, and that gap should be stated rather than papered over.

## Three further objections

**Cold start.** A new model has no history. Mitigated by the minimum-sample fallback, but it means a genuinely strong new entrant is tried last until it has earned a posterior.

**Simulation flatness.** Measured today, the simulated panel is statistically homogeneous: χ² = 3.0084, df = 5, **p = 0.6987** (NumPy and scipy agreeing; Wolfram independently 0.6986902611048746). The real panel is not: χ² = 280.0138, df = 4, **p = 2.213e-59** (Wolfram independently 2.2132215525140779e-59). A measured ladder computed from a uniform simulated panel would be ordering noise. **So this proposal depends on the seat-model map being meaningful, and cannot be validated in simulation until it is.**

**It may measure the wrong construct.** Confirm rate measures whether a model can *demonstrate* a defect. The ladder's purpose is to resolve findings other models could not. Those are related but not identical, and Exp 42 measured the latter directly on a fixed residual set — arguably a better instrument than a continuous rate.

---

## What I am NOT proposing

- Re-deriving `DEFAULT_FALSIFIER_STRENGTH` from any archived run. The ★ warning stands and the Exp 55 measurement above shows why.
- Removing the frozen order.
- Changing the ladder's behaviour before a shadow comparison exists.

---

## Open questions for the founder

1. Is the construct right — should the ladder rank on *falsification quality*, or on something else entirely?
2. Which selection-effect mitigation, if any? My recommendation is first-pass-only, with the limitation stated.
3. Should this be bundled with arming `immune_memory_enabled`, given both rest on the same Beta-Binomial machinery?
4. Does the glossary's `(D, v̄, A, C)` definition get corrected to match what is implemented, or does the implementation get completed to match the glossary? They have disagreed for an unknown period.

---

Producers for every figure cited: `scripts/the_sim_panel_is_not_heterogeneous_2026-10-05.py`, `scripts/what_the_sim_runner_never_carried_over_2026-10-05.py`.

---

# Panel review — seat Fable, 2026-10-05

Every claim below that could be executed was executed. Producer for the new
demonstrations: `scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py`
(4 sections, all reproduced at review time). Verdicts per question put to the panel:

## Q1 — the selection effect: first-pass-only is NOT a common population

The objection is correctly identified as the strongest, but mitigation 2's premise
is wrong as stated. "Every model's own findings, before any routing — a common
population by construction" is false: each model writes first-pass falsifiers for
**its own findings**, and the finding populations differ by model — that is what
χ² = 280.0138 (df 4, p = 2.213e-59) measures. First-pass-only removes the routing
confound and keeps the self-selection confound: a model that files shallow findings
confirms them easily. It also measures demonstration-of-own-findings, which is not
the ladder's construct (resolution of *others'* residuals).

**Better mitigation: randomise a small audit fraction of the assignment.** For a
fixed fraction of ladder attempts (recorded as such), pick the rung uniformly at
random instead of by rank, and compute the shadow statistic on randomised attempts
only. That measures the ladder's own construct — resolution of routed residuals —
on an assignment independent of the ranking, which is the one property mitigations
1–4 all lack. Mitigation 3 (rung as covariate) cannot identify the model effect
without the overlap randomisation provides; with a deterministic ladder, rung and
model are confounded by construction. The audit fraction's cost is bounded and
known in advance: occasionally a weaker model is tried first and one extra rung is
consumed.

## Q2 — the provenance gate: NOT sufficient as it stands. Two holes, one repaired

Demonstrated by execution on 2026-10-05:

1. **The style classifier is a source-text regex.** `open("/dev/null")` as a decoy
   — or the word `open(` inside a comment — classifies as `reads`. A detached
   falsifier passes the gate by containing the vocabulary of reading. This is the
   comment-satisfiable-guard defect class, inside the instrument built to catch a
   neighbouring defect class.
2. **The UNSAFE rule aggregated per model, not per confirmation** (repaired same
   day in `scripts/competence_provenance.py`): 2 detached CONFIRMED + 1 reading
   REFUTED scored `unsafe=False`, because one reading falsifier anywhere in the
   model's set vouched for every detached confirmation.

Gating pool entry therefore requires **execution-derived provenance**, not text
classification: record the set of files the falsifier actually opens while
`reverify_falsifier` runs it (an audit hook on file opens — machinery of the same
kind as `bench/key_access_forensics.py`), or re-run the falsifier against a
perturbed copy of the target and treat a verdict invariant to the target's content
as detached. Either is a tool deciding; the regex is a description.

Also: `bench/tests/test_defect_rate_and_competence_provenance_2026-08-23.py::
test_nothing_imports_either_script_into_the_runner` **pins this script as RECORD
ONLY** — "nothing reads either to make a decision". Promoting it to a pool-entry
gate overturns a pinned design decision and needs the founder ruling to say so
explicitly, plus that test changed in the same commit, or the gate ships as a
contradiction with its own suite.

## Q3 — the construct: a continuous rate should TRIGGER re-measurement, never reorder

Agreed with the proposal's own doubt, and sharpened: confirm rate (even
provenance-clean, even first-pass) measures *can demonstrate*; the ladder needs
*can resolve what others could not*. Exp 42 measured the latter directly on a fixed
residual set, and the frozen order's validation (6/7 resolved, 7/7 with rung 2) is
of exactly that construct. A continuous rate of a different construct does not
dominate a frozen measurement of the right construct, so under the additive
standard it cannot replace it on promotion day.

The composition that is actually supported: **frozen order stays the decision
policy; the shadow statistic runs as drift detection (the proposal's own mitigation
4, CUSUM per the ImmuneMemory machinery); a drift alarm triggers re-running an
Exp-42-style fixed-residual probe with provenance-clean falsifiers; only that
committed measurement reorders the ladder.** The rate is the tripwire, the residual
probe is the decider — "tools decide" applied to the ranking itself. The shadow
recording in §4 of the proposal is right; the promotion criterion "shadow ranking
does not distort" should be replaced by the alarm→probe→reorder path above.

On bundling with `immune_memory_enabled` (open question 3): composability requires
a demonstrated advantage of the composed work over each piece alone. Shared
machinery is an implementation convenience, not that demonstration. Decide each on
its own measurement.

## Q4 — what the proposal missed

1. **The fingerprint store erases run provenance on every save.** Measured: all 11
   files in `bench/fingerprints/` — real and `-SIM` alike — carry
   `experiment=study_run1b_2026-10-03` with one timestamp, because
   `_load_fingerprints` loads every file and `_save_fingerprints` writes back every
   model in the loaded dict. A per-model falsification rate persisted there
   inherits a store in which "which run measured this" is already unanswerable.
   The proposal's dimension needs per-run provenance (append, don't overwrite; or
   stamp per-field), or its own provenance gate is built on an attribution the
   store destroys.
2. **Real and simulated profiles share one directory with no key contract.**
   `routing.py` normalises `-SIM` to the vendor name for ranking; the fingerprint
   consumers look up by exact label. The proposal must state which key the ladder
   reads, or a simulated run's flat profile can stand in for a real model's the
   day someone normalises the lookup the way routing already normalises ranks.
3. **The exercised ladder prefix was uniform even with the mixed bench armed.**
   `routing_max_rungs` defaults to 2, the top rungs are always drawn from
   {Codex-SIM, CC2-SIM, ChatGPT-SIM}, and `DEFAULT_LADDER` mapped all three to
   `opus`: 0 of 6 source seats got a capability climb between two different
   models. Repaired 2026-10-05 (Codex-SIM → `fable`; 5 of 6 mixed, the maximum
   with CC2-SIM pinned to `opus`), pinned by
   `bench/tests/test_routing_ladder_prefix_is_mixed_2026-10-05.py`. The
   "2 distinct models across the 5 rungs" figure was true and materially
   incomplete: the rungs routing *tries* are the first 2.
4. **`burst_mode="off"` in the simulated runner: defensible as the parity default,
   no longer defensible as the only state.** Burst is fingerprint-driven; with the
   seat ladder now able to produce non-flat fingerprints, keeping burst
   permanently off in simulation leaves the burst planner in the same
   never-rehearsed state the routing ladder was in before 2026-08-30. One
   simulated configuration with `--seat-models ladder` and burst armed should
   exist before any real run depends on burst behaviour.

## What would refute this review

* Q1: a measurement showing per-model first-pass confirm rates computed on a
  shared, fixed finding set (not each model's own findings) — that would restore
  mitigation 2's "common population" premise.
* Q2: an execution trace showing `falsifier_style` consulting runtime behaviour,
  or the two demonstrations in section 1 of the producer script failing to
  reproduce.
* Q3: a committed measurement in which a provenance-clean continuous confirm rate
  predicts residual-set resolution better than the Exp-42 probe predicts itself on
  re-run — that would make the rate the better instrument for the ladder's
  construct.
* Q4.1: fingerprint files on disk carrying distinct experiment stamps after
  multiple runs — re-run section 3 of the producer script.
* Q4.3: `rank_falsifier_writers` output showing a mixed model prefix under the
  pre-2026-10-05 map — re-run section 4 with `Codex-SIM: opus`.
