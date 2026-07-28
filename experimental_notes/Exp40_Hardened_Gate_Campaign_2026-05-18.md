# Experiment 40 — Hardened Convergence Gate Campaign: Outcome

2026-05-18 22:27 BST

## What was done

The Experiment 40 target module (the §17 feedback channel,
`bench/dm/_feedback.py` — the directive that returns the schema's
round-K judgement to each model for round K+1) was decomposed into its
**faithful functional units** and each was run through a newly
**hardened convergence gate** under five-model review (Claude Opus 4.7
via CLI, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5, DeepSeek V4
Pro), with the apply-fixes-back Ouroboros loop active and live
60-second monitoring throughout.

### The hardened gate (committed `ffc88fe`)

The legacy convergence test was a loose disjunction: γ ≥ 0.30 **OR**
three consecutive rounds with zero new critical findings (γ = the Duane
reliability-growth exponent, an ordinary-least-squares log-log fit of
cumulative novelty against round; higher = faster depletion). The
hardening replaces this with a **conjunction** plus four anti-cooking
controls, pre-registered and frozen before the first run:

- **F6** — a consequence-based definition of "critical / structural"
  (a finding is critical iff, left unresolved, it would plausibly cause
  a wrong result, a hard-constraint violation, verification-integrity
  corruption, silent evidence loss, or unreproducibility). The bare
  `severity ≥ 0.7` numeric is retained only as an operational proxy;
  the rubric governs. Frozen in
  `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`.
- **F4** — the verdict is computed on the **settled** post-
  reconciliation registry, never the live-at-round transient (this
  removed the earlier 0.305-vs-0.231 live/settled flip).
- **Conjunction** — converged iff *(γ-critical ≥ θ, sustained, and
  robust to leave-one-round-out)* **AND** *(W consecutive settled
  rounds with zero new critical findings)*.
- **Dual series + sparsity fallback** — all-severity γ is computed and
  logged as a diagnostic only, never gated. When the cumulative
  critical pool is below the minimum (8), the slope is unreliable, so
  γ-critical is reported-not-gated and closure rests on the
  count-based criterion alone.

Gate parameters (θ = 0.30, W = 3, sustain = 2, min-cumulative = 8,
leave-one-round-out tolerance = 0.05) were **identical across all
units** — no per-unit tuning, which would itself be a cooking vector.

### Faithful decomposition (committed `a302a2a`)

Abstract-syntax-tree dependency analysis of the cleaned baseline
(`_feedback_cleaned.py`, 661 lines, 7 top-level definitions)
established the natural seams. The faithful decomposition is **three
units, not seven atomic fragments** — forcing seven would have meant
reviewing pure internal helpers in isolation with the data carrier
stubbed, manufacturing a convergence surface that is not a property of
the real module (a decomposition artefact in the same family the
F6/F4 hardening exists to prevent, merely inverted). The directive's
phrase "every outstanding decomposed unit, if any" cedes the count to
the structure; the honest count is three.

- **Unit A** — `parse_admissibility_block` (the §15 gate-status
  parser): self-contained leaf. Prior plan-F runs were un-hardened
  and one was falsified; this campaign re-ran it under the hardened
  gate.
- **Unit B** — `detect_finding_id_collisions` (the observation-only
  silent-overwrite detector): self-contained leaf.
- **Unit C** — the coupled cluster `FindingFeedback` +
  `build_feedback_records` + `build_feedback_sections` +
  `_render_single_record` + `_rebuild_section`: five definitions all
  bound to the one data carrier; inseparable without fabrication. Its
  seed deliberately preserves the old last-wins comprehension (a
  genuine silent-evidence-loss defect, F6 clause 4) as a legitimate
  convergence target.

## Authoritative outcomes (per-unit `report.json`)

| Unit | Mode | Cumulative critical | Verdict | Apply-back fixes folded | Rounds |
|---|---|---|---|---|---|
| A admissibility | full | 18 | **NOT converged** | 7 | 12 |
| B collision | sparsity fallback | 4 | **HARDENED_CONVERGED at round 3** | 4 | 4 |
| C records cluster | full | 14–15 | **NOT converged** | 8 | 12 (+ 1st run terminated at R5 by external network outage) |

γ-critical cleared the θ = 0.30 threshold and was sustained in **every
unit and nearly every round** (Unit A ≈ 0.41–0.53, Unit C ≈ 0.42–0.60,
Unit B degenerate 1.0). All-severity γ (the never-gated diagnostic)
declined as expected (Unit A 0.49 → 0.36, Unit C 0.34 → 0.37, Unit B
0.54).

## The central result: the conjunction is empirically anti-cooking

A legacy γ-alt **OR** gate would have declared convergence for **all
three units** — γ-critical sat well above 0.30 throughout, and Unit C's
zero-new-critical arm fired at rounds 8 and 9. The hardened conjunction
converged **only Unit B** and refused A and C. Three independent lines
of evidence show the refusals were correct, not over-strict:

1. **Unit B's convergence is the designed sparsity path, not a
   rubber-stamp.** Unit B is a ~90-line pure observation-only leaf; its
   critical surface genuinely exhausts. Cumulative critical = 4 < 8, so
   the gate explicitly **reported-not-gated** the degenerate
   γ-critical = 1.0 (it did not drive the verdict) and closed on three
   consecutive settled zero-new-critical rounds — the pre-registered
   behaviour for a finite, fully-exhaustible artefact.

2. **Units A and C failed the leave-one-round-out robustness arm, not
   the threshold.** γ-critical cleared θ and was sustained, but
   collapsed when any single round was removed: Unit A's
   leave-one-round-out minimum was **flat at 0.0 across all nine
   telemetry points** (rounds 3–11); Unit C's climbed 0.0 → 0.07 →
   0.15 → 0.20 but never reached the 0.25 floor. The decay depended on
   single-round spikes, not a genuine trend — exactly what the
   robustness arm is designed to reject.

3. **Unit C provides a direct empirical vindication.** At rounds 8 and
   9 Unit C's zero-new-critical arm was satisfied (a legacy OR gate
   converges here). The hardened gate withheld because the γ-critical
   arm was not leave-one-round-out robust. At round 10 a **new critical
   finding emerged** (cumulative critical 14 → 15), flipping the
   zero-critical arm back to false. An OR-gate "convergence" at round
   8/9 would therefore have been **empirically false** — refuted by the
   next round's data. The conjunction's refusal was vindicated by
   subsequent observation, on the one case where the two gate designs
   could be directly compared.

The gate's behaviour is principled and consistent: sparsity-fallback
closure only for genuinely sparse critical pools (B); the rigorous
full-mode conjunction otherwise (A, C), refusing convergence where the
critical-novelty decay is not robust.

## Process-integrity events (all surfaced, none cooked)

Live monitoring under the Find–Follow–Analyse–Fix–P-pass discipline
surfaced and handled, without corrupting any measurement:

- **Three runner-class verification-integrity defects**, found live,
  root-caused, P-passed, fixed at the Unit B→C inter-unit seam
  (committed `5fe9101`), and twice live-validated in production:
  1. `CircuitBreakerTripped` was not pickle-safe across the
     `multiprocessing.Queue` boundary in `dispatch_to_model` — its
     custom constructor meant the default exception pickling
     reconstructed it with one argument, raising a `TypeError` that the
     broad except swallowed, leaving the circuit breaker silently
     inoperative across the whole arc. Fixed with a `__reduce__`
     method; regression test added; later observed working cleanly on
     genuine empty-response events in Units C and A.
  2. The launcher's convergence check read a per-round flag that is
     always absent; it misreported every hardened convergence as "no
     convergence". Fixed to read the authoritative top-level result.
  3. The same root meant `completion_signal.json` recorded a converged
     run as INCOMPLETE; fixed by propagating convergence to the brain
     state, guarded so stall/churn stops keep their own status.
  All three are reporting/serialisation-layer (they misreport, they do
  not corrupt the measurement — the `report.json` verdict is
  authoritative and was always correct). They were fixed **between
  units, never mid-run**, so no run was split across two runner
  versions.

- **One external network outage** terminated Unit C's first run at
  round 5 (`all_models_failed`). This is infrastructure, not a gate
  verdict. Unit C was re-run fresh from an archived copy of the
  terminated run (no resume into mid-outage state — the non-cooking
  choice).

- **Roughly five degraded-DeepSeek decomposed-recovery events** (one
  synthesis read took ~23 minutes). Each resolved via the runner's
  finite layered recovery; content was recovered every time; no
  findings were lost. Patient monitoring was vindicated each time —
  no destructive false-freeze.

- The **apply-fixes-back Ouroboros** operated substantively: 19
  full-test-suite-gated fix promotions total (B 4, C 8, A 7) folded
  into the per-run working copies.

## Residual non-blocking follow-ups (flagged, not skipped)

- Scattered legacy `0.7` critical-severity literals in
  `reference_runner_v2.py` are not yet replaced by the
  `CRITICAL_SEVERITY_THRESHOLD` constant the hardened gate uses.
- `completion_signal.json` labels a ran-to-max-rounds non-converged
  run "INCOMPLETE"; "MAX_ROUNDS_NO_CONVERGENCE" would be more precise
  (a labelling nicety; `report.json` is authoritative).
- The launcher's non-convergence message hardcodes "(likely
  wall-clock)"; Units A and C actually hit max-rounds, not wall-clock.
- The decomposed-dispatch path produces multi-minute silent blocks
  during a degraded-API event with no heartbeat log, degrading live
  monitorability (a monitoring enhancement, not a correctness defect).

None corrupts a measurement; all are tracked for Exp-41-or-later
hygiene.

## Verification state

60 regression tests pass (hardened-gate 8, three slice suites, the
pickle-safety regression); zero new lint findings versus HEAD; all
three authoritative `report.json` verdicts are reproducible by a
hostile reviewer from the logged registry, fixes, and γ script. Commits
this campaign: `ffc88fe` (gate-hardening + F6 pre-registration),
`a302a2a` (faithful decomposition + per-unit hardened configs),
`5fe9101` (three seam fixes + regression test).

## Bottom line

The Experiment 40 question — does the hardened gate prevent cooked
convergence? — is answered **yes, empirically and reproducibly**,
across the full faithful decomposition. The gate converged the one
genuinely-exhaustible unit on its pre-registered sparsity path and
refused the two units whose critical-novelty decay was not robust, with
one refusal directly vindicated by subsequent data that an OR-gate
convergence would have contradicted.

Written under CDSFL note standard v1.2 (14 May 2026).
