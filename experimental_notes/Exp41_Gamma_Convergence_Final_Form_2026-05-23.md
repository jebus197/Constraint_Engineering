# Experiment 41 — Final Form of the Convergence Rule

2026-05-23 17:13 BST. Constraint Engineering / CDSFL.

> **SUPERSEDED (2026-05-23, later same day).** The control-rule form and the
> 0.85 cut-off recommended below are **withdrawn**. The settled design is
> simpler: the serious-findings decay curve is the criterion; convergence is
> detected by the recent-quiet count (3 zero-new-critical rounds, verifier-
> filtered); the slope value is **reported, not gated**; no 0.85 and no
> control-rule schedule. Reason: the global slope is a laggy instrument (it
> ignores late criticals and is slow to credit a clean recent stop), so it
> should not gate or override the count, which is the accurate recency reading.
> The population fix (gamma on the critical series), report-both-gammas, and the
> classifier-as-single-point-of-failure points below all still stand. See
> `Exp41_Gamma_Convergence_Resolved_Plain_English_2026-05-23.md`.

## Decision

Convergence is decided by a single rule on the genuine (settled,
verifier-filtered) CRITICAL findings: the decay-curve metric γ (gamma, computed
on the critical series, written γ_crit) sets **how many consecutive
zero-new-critical rounds are required** before the run is declared converged.
The continuous decay curve and the discrete quiet-tail count are not two
competing tests — they are one rule in which the decay curve governs the
evidence burden.

Two five-model panels (CC2/Opus 4.7, Codex/GPT-5.5, Gemini 3.1 Pro,
ChatGPT/GPT-5.5, DeepSeek V4 Pro; star topology; compelled convergence;
deliberately neutral framing) reviewed the question. The first established the
structure; the second, reported here, fixed the form and was **unanimous (5/5)**
for the control-rule form and unanimously rejected the flat-conjunction forms.

## Background: the problem being solved

The detector's founding idea is a decay curve: as a finite defect space is
exhausted, genuinely-new discoveries per round fall toward zero. γ = 1 − β,
where β is the log-log slope of cumulative novelty against round; γ near 1 means
the curve has flattened.

Two signals had been in play, combined as an OR: (1) γ ≥ 0.30, and (2) a count
of K consecutive rounds with zero new CRITICAL findings. In run exp41c they
appeared to disagree — the displayed γ was 0.240 while the count fired. The
disagreement was a **population mismatch**: γ was being shown on the
ALL-severity series `[3,2,1,1,1,0,1]` (non-critical footnotes still trickling),
while the count judged the CRITICAL series `[3,0,0,0,0,0,0]`. γ on the critical
series is 1.000. The same run yields 0.240 (all findings) or 1.000 (criticals
only) depending on the population measured.

The risk to avoid was twofold and contradictory: (A) convergence must never
become unreachable (a prior conjunction gate made it impossible); and (B) the
decay curve must remain genuinely load-bearing, not a decorative number — a
credibility requirement, because a model whose central metric never changes a
decision invites the question "does the model say anything at all?"

## What the first panel settled (unanimous)

- Compute γ on the verifier-filtered CRITICAL/material findings, not
  all-severity. The "finite defect space" of the maths model is the material
  space; non-critical footnotes are a near-infinite trickle that never decays
  cleanly. The apparent (A)-vs-(B) tension was an artefact of measuring γ on the
  wrong population: on the critical series γ does flatten, so a conjunction is
  reachable.
- Report both γ_crit and γ_all, always population-labelled; never a bare γ.
- Convergence requires **both** a decay signal (γ) and a recency signal (zero
  new criticals) on the critical population — neither alone. A standalone γ
  trigger is unsafe (a late critical barely moves a whole-history slope:
  `[3,0,0,0,0,0,1]` still gives γ = 0.926); a standalone count with γ merely
  reported is gamma demotion.
- The severity classifier becomes the principal point of failure (mislabelling a
  real critical as minor inflates γ_crit and clears the count). Guarded by
  pre-registration, audit, and publishing the excluded all-severity data.
- This matches the maths model; no revision, only a population index on γ.

## The remaining question and the second panel (unanimous: control rule)

The open question was the exact form of "both required":

- **Design A (flat conjunction)**: converge when γ_crit ≥ T AND z ≥ K (e.g.
  T = 0.30, K = 3), z = consecutive most-recent zero-critical rounds.
- **Design A′**: flat conjunction with a higher T (e.g. 0.85).
- **Design B (control rule)**: γ_crit sets the required quiet-tail length K.

All five models rejected A and A′ and chose **Design B**, for one shared,
verifiable reason: γ and z are **correlated when computed on the same series** —
any tail of K zeros mechanically forces a low slope and therefore a high γ. So
in a flat conjunction γ is satisfied whenever z is, and γ never independently
changes the outcome. That is cosmetic load-bearing, and it fails requirement
(B). A higher flat threshold (A′) makes γ bite but only as a brittle veto that
can reject genuinely-exhausted runs with messy early histories (an estimator
"cliff"). Design B makes γ change the **amount of evidence required**, so it
demonstrably changes outcomes while never blocking convergence outright.

## The agreed rule

Compute and report every round: γ_crit (critical population), γ_all
(all-severity, diagnostic), and z (consecutive most-recent zero-critical
rounds), all population-labelled. Then:

> Converge iff the state gate is clean AND z ≥ K_required(γ_crit).

Recommended pre-registration starting schedule (a two-tier form; the panels'
cutoffs spanned 0.30–0.85 and K ∈ {3,4,5}, with the heavier reasoning favouring
a high cutoff so γ genuinely bites):

| γ_crit | interpretation | K_required |
|---|---|---|
| ≥ 0.85 | strong, clean decay | 3 |
| < 0.85 | weak / messy / not-yet-corroborated decay | 5 |
| unestimable (no criticals ever, or < 4 points) | no reliable decay estimate | 5, with explicit "γ undefined" note |

An optional middle band (0.30 ≤ γ_crit < 0.85 → K = 4) gives a smoother burden
if wanted. The exact cutpoints are conventional and **must be calibrated on
historical runs and locked before live use** — not tuned after seeing a result.

Properties:
- **Reachable**: even with weak or undefined γ, a finite quiet tail (K = 5)
  terminates a genuinely-exhausted critical space. No impossibility.
- **γ genuinely load-bearing**: γ changes K (3 vs 5), so it changes the verdict
  in plausible cases — e.g. a messy-but-quieted critical series such as
  `[3,2,2,1,0,0,0]` has γ_crit ≈ 0.62 (< 0.85), so three quiet rounds do **not**
  converge it; it is held to five. A clean `[3,0,0,0,0,0,0]` (γ = 1.0) converges
  at three. Same recency, opposite verdict, decided by γ.
- **Defensible / auditable**: a small, finite, monotone, pre-declared schedule;
  no hidden gate.

## Why this answers the credibility concern

γ is not demoted and the decay curve is not decorative: it sets the evidentiary
bar and there exist concrete runs where it flips the decision. The honest
description — "we stop when serious discovery has decayed and stayed quiet long
enough, where the decay curve decides how long 'long enough' is" — is the
project's founding logic, stated directly. The all-severity γ is retained as a
published diagnostic, so nothing is hidden and no number is silently swapped.

## Residual risks and guards

- **Severity classifier is the single point of failure.** Mislabelling inflates
  γ_crit and clears the count. Guard: pre-register the classifier; audit a
  sample of non-critical exclusions; always publish γ_all and both per-round
  series alongside γ_crit.
- **Cutpoint conventionality / threshold-shopping.** Pre-register the schedule
  and the γ estimator before runs; version any change with a full replay showing
  whether prior conclusions flip.
- **Empirical cosmetic check (ongoing).** Track, across runs, how often γ
  actually changes the convergence decision relative to a count-only rule. If
  that fraction is ~0, γ is empirically cosmetic and the schedule must be
  revised prospectively. This converts "is γ load-bearing?" from an assertion
  into a measurable, auditable property.

## Status and next step

Design approved by the founder ("go fully with the panel's recommendations").
Implementation pending: wire the control-rule gate (γ_crit on the settled
critical series sets K_required; report both γ values) into the runner, lock the
pre-registered schedule, and re-verify that exp41c still converges (it will:
γ_crit = 1.0 → K = 3, and its zero-critical tail is [0,0,0]).

Written under CDSFL note standard v1.2 (14 May 2026).
