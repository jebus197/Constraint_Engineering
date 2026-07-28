# Experiment 40 — γ-Hardening Neutral Confer: Outcome

2026-05-17 20:13 BST

## Summary

A five-model neutral confer (Gemini 3.1 Pro, Codex GPT-5.5, CC2 Opus
4.7, ChatGPT GPT-5.5, DeepSeek V4 Pro; star topology, compelled
convergence, latest CDSFL schema) was run to resolve how to harden the
γ (gamma) convergence metric, given the founder ruling that γ demotion
is a HARD constraint and out of scope. All five returned cleanly
(prompt 28,924 chars; responses 3,980–8,638 chars). The full
unedited responses are in
`bench/logs/confer_exp40_gamma_hardening_2026-05-17/`.

**Unanimous (5/5) core result:** harden γ, do not demote it — and every
model independently argued demotion is technically unnecessary, not
merely founder-excluded. The dominant finding, raised unprompted by
four of five, is that the hardening *is* book-cooking unless explicit
controls are enforced. The confer therefore converged not just on a
fix but on the integrity guardrails that make the fix legitimate.

## The 5/5 converged core

- γ's input must be the post-reconciliation **critical/structural,
  severity-gated** novelty series, which carries the convergence gate.
  The all-novelty series is retained and logged as an entropic-noise
  **diagnostic** (dual-series). This subsumes the bare "feed γ the
  critical series" option.
- **Regime-aware threshold recalibration**, principled and
  pre-registered, explicitly NOT fitted to plan-F.
- **Apply-back is kept.** All five reject reverting to the
  collect-fixes-at-end methodology as the general method — it is the
  documented cause of non-convergence (flat γ on an unrepaired
  artefact); at most it survives as a frozen calibration role.
- γ remains the load-bearing gate. No demotion. Framed by all five as
  correcting a measurement-population specification error, not
  deprecating the metric.
- The offline ≈0.60 critical-only γ and the `[8,4,0,3,1,1,1]` series
  are NOT production truth and must be recomputed through the full
  reconciliation+severity pipeline before any gate claim. Codex,
  ChatGPT and CC2 independently flagged that this offline series
  visibly mismatches the post-mortem's "three consecutive zero-critical
  rounds" tail — a real inconsistency that must be reconciled in
  production, not asserted away.

## The book-cooking centre of gravity (the important result)

Four of five models, unprompted, identified that relocating the gate to
the critical-only series *after* observing plan-F fail on the
all-novelty series is the exact shape of book-cooking. Their collective
answer defines the legitimacy conditions: the hardening is a valid
specification correction **iff** (a) the structural/critical class is
pre-registered semantically (not the bare numeric 0.7 cut); (b)
thresholds are recalibrated on a held-out corpus or null-distribution
simulation, never tuned to make plan-F pass; (c) the production γ is
recomputed through the real pipeline before being cited; (d) the
recalibrated γ is allowed to FAIL future runs (the gate must be able to
reject). Without these it is cooking; with them it is correcting a
documented specification error (F2/F3: the input is already
churn-stripped; the residual mismatch is severity granularity).

## Genuine divergences and their compelled-convergence resolution

The core was unanimous; three real splits were resolved on the
founder's HARD anti-book-cooking constraint as the stated tiebreaker
(this resolution is the working model's synthesis, not a raw vote):

- **Phase isolation / frozen calibration leg.** 3 for (Codex, ChatGPT,
  CC2), 2 against (Gemini, DeepSeek, who argue the extended Duane model
  makes it unnecessary). Resolution: **kept.** Gemini and DeepSeek both
  conceded in their own counter-arguments that the extended model's
  ν/Δ are themselves a book-cooking vector; relying on it to remove the
  need for a clean measurement regime trades a regime problem for a
  free-parameter problem — worse for integrity. A frozen calibration
  leg is the cheapest unimpeachable integrity anchor.
- **Re-injection-extended Duane (λ_ext) timing.** All five want it
  eventually; split on urgency. Resolution: **deferred to
  instrumented-but-not-gate-grade** until ν/Δ are empirically
  identified from accumulated data (aligns Codex/ChatGPT/CC2; against
  Gemini/DeepSeek front-loading it), because its free parameters are a
  cooking vector until data-fixed.
- **Severity ≥ 0.7 cut.** 4/5 hold the bare number is not principled
  and needs a pre-registered semantic class (HARD-vs-SOFT-constraint
  violation / closure-blocking-consequence ontology). DeepSeek alone
  calls 0.7 "already sound" by asserting it equals the CDSFL schema's
  High/Critical boundary — recorded as an **unverified assertion** (the
  one parrot-risk in the panel; it asserts the mapping without
  evidence). Resolution: adopt the 4/5 position — use the project's
  existing HARD/SOFT-constraint classification, validated, not a round
  number.
- **CC2's unique adversarial finding (raised by no other model):** the
  critical-only series on short runs is sparse; log-log OLS on ~7 small
  integers with a non-monotonic spike is high-variance. Non-optional
  guard: below a minimum cumulative-critical count, γ is
  reported-not-gated and closure falls back to the robust count-based
  zero-novel-critical consecutive-round criterion; OLS-slope confidence
  intervals logged.

## Synthesised single position

Harden γ to a post-reconciliation, structural-constraint-gated,
dual-series, regime-recalibrated metric with a frozen calibration
anchor and a sparsity fallback — γ stays the gate, never demoted, under
enforced anti-cooking controls. Implementation order: (1) dual-series,
structural series gates, all-novelty logged; (2) pre-register the
structural class as HARD-constraint/closure-blocking, retire the bare
0.7; (3) recompute plan-F + the run corpus through the production
reconciliation+severity pipeline; (4) recalibrate thresholds on
held-out data, pre-registered, allowed to fail; (5) sparsity guard with
count-based fallback; (6) frozen-target calibration leg as the
integrity anchor; (7) λ_ext instrumented, deferred from gating until
ν/Δ are empirically fixed.

## Working model's independent position (separate from the panel)

Concurs with the synthesised core — it independently reproduces the
working model's own falsification-grounded finding and is the
integrity-preserving answer. One substantive divergence from a panel
member: DeepSeek's "0.7 is already sound" is rejected as unverified.
Strongest residual caution, recorded so it cannot be engineered around:
the production recompute (step 3) may show critical-only γ does not
cleanly clear a properly recalibrated bar; the offline figure is not
trustworthy and the post-mortem mismatch is real. If so, the honest
outcome is that the bar holds and the run did not fully structurally
converge — to be reported, not engineered around. The plan is sound
only because it can still fail.

## Status / path forward (not executed — analysis + confer only)

No code was changed. This is a decision-grade recommendation requiring
founder approval before implementation; the seven-step composition is
real engineering work, not a config flip. Recommended next step:
founder ruling on the synthesised position; then implement steps 1–2+5
(low-risk, high-leverage) under FFAFP with the anti-cooking controls
pre-registered before any new run.

## Cross-references

- Confer logs (full, unedited):
  `bench/logs/confer_exp40_gamma_hardening_2026-05-17/`
- Confer script:
  `bench/confer_exp40_gamma_hardening_2026-05-17.py`
- Why Gamma Convergence Stays Elusive — Plain-English Analysis
  (2026-05-17) — the cause analysis this confer arbitrated.
- Experiment 40 plan-F Convergence Result (2026-05-17) — the run whose
  γ behaviour prompted this.
- Plain-English companion: Experiment 40 γ-Hardening Confer Outcome —
  Plain English (2026-05-17); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
