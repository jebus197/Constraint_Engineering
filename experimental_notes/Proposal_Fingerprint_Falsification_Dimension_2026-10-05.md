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

The ladder routes findings *the weak models could not resolve* to the strong models. So a strong model's falsifiers are attempted against a systematically harder population than a weak model's. Its provenance-clean confirm proportion, the numerator over the denominator defined in section 1, is therefore depressed by the very fact that it is trusted. Left uncorrected, a measured ladder could demote exactly the models it should promote, and then feed that demotion back into the next assignment.

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
