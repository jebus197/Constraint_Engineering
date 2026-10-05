<!-- PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: cd52263f1d85375560026fbb0139e147d5955018070306ab1d652ea4d67f9f6d
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited. -->
# Amendment to `Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`

**Status: PANEL SEAT RESPONSE, 2026-10-05. Amendment, not replacement — CC1's
proposal is left intact at its own path.** Two of its four load-bearing claims do
not survive execution. The gap it identifies is real and the shadow-first
discipline is right; the recommended mitigation and the recommended gate are both
wrong, and in the same direction — each substitutes a measurement the measured
model can move for one it cannot.

Producers, all runnable, all written at real paths:
`scripts/ladder_selection_effect_attenuates_not_inverts_2026-10-05.py`,
`scripts/sim_runner_inert_flag_census_2026-10-05.py`.

---

## A1. The "strongest objection" is the WEAKEST of the four, and the recommended mitigation is the one that inverts

The proposal states the selection effect as: "a measured ladder could demote
exactly the models it should promote, and then feed that demotion back into the
next assignment", and recommends **first-pass falsifiers only**, on the ground
that those are "a common population by construction".

Under a one-parameter logistic (Rasch) model — finding *j* has difficulty *d_j*,
model *i* has ability *a_i*, P(resolve) = σ(*a_i* − *d_j*) — both halves fail:

```
A. ladder assignment, correct order   rates [0.8458 0.6307 0.4123 0.2469 0.1143]  tau +1.000
B. true-strongest tried LAST          rates [0.6449 0.5844 0.5316 0.4754 0.3799]  rank of
                                      true-best by measured rate: 1 of 5
C. first-pass-only, by ambition coefficient
     ambition 0.0  [0.846 0.764 0.664 0.542 0.379]  tau +1.000  spread 0.466
     ambition 0.5  [0.696 0.638 0.584 0.520 0.439]  tau +1.000  spread 0.258
     ambition 1.0  [0.502 0.500 0.499 0.501 0.498]  tau +0.600  spread 0.004  SIGNAL GONE
     ambition 1.5  [0.304 0.357 0.417 0.480 0.565]  tau -1.000  spread 0.260  INVERTED
     ambition 2.0  [0.158 0.234 0.342 0.462 0.625]  tau -1.000  spread 0.468  INVERTED
     eps-random    [0.792 0.698 0.583 0.460 0.303]  tau +1.000  spread 0.489
```

**Why A holds.** Each later rung inherits the findings the earlier rungs could not
resolve — a *harder* population. Later rungs are, by the ladder's construction, the
*weaker* models. So the bias pushes weak models further down: it is monotone in the
order-**preserving** direction. It exaggerates the gap; it does not reverse it.

**What the selection effect actually costs** is discrimination, not order. With the
true-best model forced to the last rung the measured spread compresses from 0.731
to 0.265, a factor of 0.36 — the same ranking, reached with ~8× less signal per
observation. That is a power problem, answerable with sample size.

**Why C bites.** First-pass-only is *not* a common population. Each model generates
its own first-pass findings, so the population is **self-selected**. Parameterise
that as an ambition coefficient — how much a stronger model raises the difficulty
of what it bothers to report — and at ambition 1.0 the ability and ambition terms
cancel exactly, every model scores 0.50, and the instrument has zero spread. Above
1.0 the order **inverts**. Ambition is unobserved, and it is **under the measured
model's own control**: a model raises its first-pass confirm rate by reporting only
defects it can already demonstrate. A ranking metric the ranked agent can move by
lowering its own ambition is the property this project's reward-hacking notes treat
as disqualifying, and it would be wired into the mechanics, not the write-up.

So the proposal's recommendation converts a bias that is monotone and safe into one
that is non-monotone, unobserved and gameable.

### The mitigation that survives: randomise the rung on a fraction ε

When a finding becomes routable, with probability ε (ε ≈ 0.2) choose the rung
**uniformly at random** from the eligible pool instead of by the frozen order, and
log `assignment ∈ {ladder, random}`. Estimate the dimension on the random
subsample **only**. Assignment is then independent of difficulty *by construction*
rather than by an assumption about a difficulty covariate — which is what
distinguishes it from the proposal's options 1 and 3, both of which require that
difficulty be fully captured by an observed proxy, and from option 4, which is a
decision not to measure (a prior strong enough to resist the bias is strong enough
to resist true drift, which is the stated purpose).

`ε = 0` reproduces today's behaviour exactly, so this is additive and reversible.
Cost is bounded by ε × `max_rungs` extra dispatches.

**NOT IMPLEMENTED HERE, deliberately.** The proposal's own rule — "Changing the
ladder's behaviour before a shadow comparison exists" is on its NOT-proposing list
— applies to this too. ε-random routing is a change to the mechanics and needs the
founder ruling the proposal asks for. The derivation is delivered as a runnable
script; `bench/routing.py` is untouched.

---

## A2. A detached falsifier passes the provenance gate. Measured.

`scripts/competence_provenance.py:43` is the whole gate:

```python
return "reads" if re.search(r"open\s*\(|read_text|\.read\s*\(|linecache|getlines", c) else "detached"
```

That is a **regular expression over the falsifier's source text**. Executed against
six shapes:

```
falsifier shape                                            competence_provenance says
honest reader                                              reads
DETACHED, memorised numbers (the Exp-55 shape)             detached
DETACHED + a COMMENT containing open(                      reads     <-- FALSE PASS
DETACHED + a decorative open() of an unrelated file,
           result discarded                                reads     <-- FALSE PASS
DETACHED + open() in a dead branch                         reads     <-- FALSE PASS
DETACHED + the word read_text inside a string literal      reads     <-- FALSE PASS
```

Four of six detached falsifiers are admitted. One of them is admitted **by a
comment** — the exact anti-pattern CC1 spent the same night removing from three
tests in `bench/tests/`, still live inside the script the proposal nominates as the
gate on pool entry. So the answer to the proposal's question 2 is **no**: gating on
`competence_provenance.py` does not prevent the Exp-55 inversion. It raises the cost
of the inversion to one line of decorative I/O.

**The gate must be a dependence test, not an access test, and this project already
built one.** `scripts/target_independence_probe.py` substitutes the target with
unrelated content and re-runs: a verdict that stays CONFIRMED proves the falsifier
cannot be touching its target, and the probe's own docstring notes it *undercounts*
target-independence, which is the safe direction. `scripts/null_perturbation_control.py`
is the complement. A verdict's **dependence on the target's bytes** is a property no
amount of decorative `open()` satisfies, and it is already measurable offline today.

**Amendment:** replace "gating pool entry on `scripts/competence_provenance.py`"
with "gating pool entry on substitution-response per
`scripts/target_independence_probe.py`, with `competence_provenance.py` retained as
the cheap pre-filter it is adequate to be". Nothing is removed; the sound instrument
is placed in front of the proxy. Note the probe's own stated limit, which must travel
with it: coupling established by `import` does not establish that the assertion is
about the accused defect.

---

## A3. The construct. A continuous rate on production traffic is worse than the frozen measurement. Re-run the frozen measurement instead.

The proposal asks whether confirm rate measures the wrong thing and answers "related
but not identical". The sharper statement is about **identification**, not construct
validity:

- Exp 42 measured on **the 7 hardest residuals — a fixed set**. A fixed set is a
  common population. It is the randomisation-free way to get what ε-random gets:
  hold the population constant instead of randomising who sees it.
- A rate accumulated from production routing traffic has an **endogenous**
  population — the ladder chose it — and is therefore not identified without either
  randomisation or an untestable difficulty model.

So: **yes, a continuous rate is the worse instrument**, and the reason is not that
confirm-rate is the wrong construct but that production traffic is the wrong
population. The frozen order's defect is **staleness**, and the fix for staleness is
to **re-run the identified measurement**, not to replace it with an unidentified one.

**Amendment — what should be proposed instead.** Version the Exp-42 residual set as
a held-out, fixed falsification benchmark (a named suite under `bench/`, pinned by
content hash), re-run it on a schedule or on roster change, and use the result to
*replace the frozen tuple wholesale* with a dated one. The ladder keeps a single
measured order, re-derived rather than drifting; the output is a dated constant, not
a posterior. This is simpler than a per-model Beta-Binomial with a minimum-sample
rule and a shadow ranking, it has no cold-start problem (a new model is benchmarked
before it is trusted, not after), and it carries no selection effect at all. The
Beta-Binomial machinery the proposal wants to reuse is not needed for it.

Keep the proposal's live dimension if desired — but as a **drift alarm** that
triggers a benchmark re-run, never as the thing the ladder reads. That is the
division of labour the proposal's own objection 3 is pointing at.

---

## A4. What is missing, and the denominator is wrong

**The denominator.** There are **47** shipped experiment configs, not 49, and they
are at `bench/exp*_configs/*.json` — `configs/` holds domain-expert prompt
markdown and contains **0** JSON configs. CC1's three numerators reproduce exactly
(13, 4, 1); the figures should read **13 of 47, 4 of 47, 1 of 47**.

**The class is wider than three flags, and the mechanism is not "the flag is
unread".** `bench/tools/run_simulated_experiment.py` has **no `--config`**. It
builds a `RunnerConfig(...)` inline literal (39 keys set, by AST) and hands it to
the *same* `reference_runner_v3.run_experiment` the paid runs use. Every read site
for all three flags sits inside code the simulated run executes. They are inert
because **the literal never sets them, so they take the dataclass default `False`**.
Consequently *any* config key absent from that literal is silently defaulted, with
no test asserting the literal's key set covers the union of keys the real configs
set. The three flags are instances; the missing ratchet is the defect.

The census (`scripts/sim_runner_inert_flag_census_2026-10-05.py`) reports **5** keys
in the gap class. Two are not real:

- `panel_cwd` (12 truthy) **is** set, post-construction, at
  `run_simulated_experiment.py:724` — an AST scan of the constructor literal alone
  misses it.
- `target_kind` (6 truthy) is documented in `RunnerConfig` as "a DECLARATION OF
  INTENT ONLY"; `resolve_target_kind` detects from path and bytes and a declaration
  can only veto, "never redirect". Not declaring it leaves the authoritative
  detection unopposed.

Four further keys — `prior_fix_summary_enabled` (33), `windowed_context_enabled`
(33), `inround_reask_enabled` (32), `location_shadow_enabled` (21) — default
**True**, so the sim gets the armed value. A scan that only asks "is it in the
literal?" ranks these four *above* `immune_memory_enabled`. Worth recording, because
that is the scan a reader would write.

**`burst_mode="off"`: defensible as parity, damning for this proposal.** It is
hardcoded at `run_simulated_experiment.py:480` under a comment reading `# PARITY
WITH THE REAL exp45 CONFIG`. The dataclass default is `'auto'`; **43 of 47** shipped
configs say `'off'` and the 4 that say `'auto'` are all exp39, the oldest
generation. So it is a deliberate override *toward* the real-world majority, not a
gap of the same class — the honest answer to the proposal's question is that
`burst_mode="off"` is defensible on its own terms.

It is nonetheless fatal to rehearsing **this** proposal. `cfg.burst_mode != "off"`
gates the burst path at `reference_runner_v3.py:15231`, and `burst_planner.py` is
the fingerprint's principal consumer. So the one path that would exercise a
fingerprint-keyed decision is **off in every simulated run**, on top of the
proposal's own "simulation flatness" objection and on top of the uniform seat map
(1 distinct model across the 5 rungs the ladder returns). Rehearsing a
fingerprint-keyed ladder needs **all three**: a non-uniform seat map,
`burst_mode != "off"`, and `immune_memory_enabled=True`. Today none holds in the
simulated runner. That is a stronger version of the proposal's objection 2 and
should replace it.

---

## Standing figures: reproduced, with two corrections

- Real panel χ² = 280.013760, df 4, p = 2.213221e-59; simulated χ² = 3.008403,
  df 5, p = 6.986902e-01. Both reproduce exactly (NumPy and scipy). Wolfram Language
  (local Wolfram Engine, via `wolframscript`) independently returns
  0.6986902611048746 for the simulated p; the real-panel tail underflowed and then
  raised `N::meprec` at 25 digits, so **Wolfram verified nothing on that one figure**
  and it stands on scipy/NumPy alone in this run.
- The test is a one-way χ² goodness-of-fit against `pooled_rate × rounds`, not a
  test of independence; `rounds_participated` is constant within each panel so the
  exposure weighting is inert and df = k−1 is correct. Expected counts 668.60 and
  39.67, both ≫ 5.
  **Correction to how the comparison may be read:** real N = 3343 over 1370
  model-rounds vs simulated N = 238 over 138 — ~14× less data and a different df.
  Transplanting the real panel's rate profile into the sim's sample size gives
  λ ≈ 19.9, power ≈ 0.95, so the sim test *would* have caught the real effect size.
  But the sim's own observed spread (max/min 1.406) sits at power ≈ 0.48. The
  defensible claim is "no heterogeneity detectable at the real panel's effect size",
  not "one rate explains every member". Also: real χ²/df = 70.0 indicates
  overdispersion, so `2.213e-59` is directionally safe but not a calibrated number.
- 0 of 3473 round replies carry an id-addressed falsifier; Wilson upper 0.110487%.
  Reproduces; Wilson confirmed by statsmodels, by hand, and by Wolfram Language
  (0.11048702870671313).
  **Correction:** the population filter drops 2267 `round*_*.json` replies in the
  same run directories, which are round replies too. Scanned, including under a
  much looser predicate: still 0. So the zero holds on a 5866-file superset and the
  interval should have been **0.0654%** (Wolfram Language: 0.06544399619041685), not
  0.1105%. The quoted interval is conservative, so no conclusion moves.
  Separately, that script's docstring is now **stale**: the form has two parse sites,
  not one, and the second — `record_in_round_falsifier_reattachments` at
  `reference_runner_v3.py:13552` — **is** called from the round loop at `:16114`.
  Its cited line 7454 is off by 108. The figure is what justified building that
  parser; the prose was not updated and now reads as a live claim that is false.
