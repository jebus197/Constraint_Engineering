# Specialist-Cell Panel Review — Five-Model Synthesis (pr, no compelled convergence)

**2026-07-28, 20:15 BST.** Panel: CC2 (Opus, CLI — long-retry after three 300s timeouts; instrument, not verdict), Codex, ChatGPT (GPT-5.5, OpenRouter), Gemini 3.1 Pro (OpenRouter), DeepSeek V4 Pro (direct). Full responses: `bench/logs/confer_specialist_cells_pr_2026-07-28/`. CC1 participates as sixth voice. Disagreement preserved as information.

## Q1 Topology — 4:1 FOUR per-domain modules (DeepSeek dissents constructively)

CX, ChatGPT, Gemini, CC2 independently converge on four native per-domain modules, all citing the same decisive constraint: one domain config per run; a consolidated module tests the non-live, tool-incomplete `cross_domain.toml` surface and confounds classification, routing, tool availability, discrimination, and recall in one measurement. **DeepSeek's dissent** — one consolidated artefact run four times (controls artefact variance across specialists) — costs the same four runs and self-falsifies on cluster-difficulty confounding. CC2 adds the budget concession adopted below: **chemistry and engineering first** (their TOMLs changed most in Round 3 and are least validated). CX + ChatGPT jointly park a **cross-domain stress test as a BR2-prep item** once `cross_domain.toml` is made live and tool-complete. **CC1 position: with the majority** — and noting the panel outcome effectively RESTORES the founder's original four-module numbering (my compression proposal stands refuted by the same evidence chain that refuted its premise).

## Q2 Coverage — gaps filled, clusters merged from all five

**Chemistry adds**: (a) *Equilibrium-shift & conservation logic* (z3 + sympy) — planted falses available: inert-gas-at-constant-volume shifts equilibrium (Gemini); "always increases yield regardless of moles" universal (DeepSeek); exothermic-yield-rises-with-heat (CC2); (b) *Analytical-measurement statistics* (statsmodels + scipy + uncertainty_propagation) — planted: naive-addition uncertainty propagation (Gemini: "exactly 8%" vs quadrature 5.83%); p-value-as-P(H0) misread (DeepSeek). **Engineering adds**: *Failure-mode & load-path logic* (z3) — planted: 2-of-3 redundancy asserted to survive two failures (CC2/Gemini convergent). **CC2's practical caution adopted as a build rule: every planted claim's wording must be regex-verified against the domain TOML `claim_patterns` before the run, or mis-routing invalidates the measurement.**

## Q3 Earn-their-keep — synthesized conjunctive gate (per domain)

1. **Attributed planted-false recall = 100%** — caught by the routed specialist, not the baseline (attribution per CC2; CX/ChatGPT/Gemini at 100%, DeepSeek at ≥90% — 100% adopted given deliberately small planted sets).
2. **Non-distortion**: zero false refutations of planted-TRUE claims (Gemini/CC2); ≤5–10% claim-level flag rate on other true content (DeepSeek/ChatGPT band).
3. **Decision-changed tally, conditioned on baseline noise** (Gemini's collapse caveat: an accurate panel yields no noise to filter — the metric must not read that as specialist failure). Measured properly via **CC2's specialist-off paired run** (the counterfactual): ≥1 attributed decision-change per domain *when baseline noise exists*.
4. **Convergence non-distortion** (CC2): identical convergence round + γ trajectory on an all-true control module.
**Prerequisite** (CC2, adopted): per-verdict logging of {classified type, routed tool, verdict, ground truth}. **DeepSeek's standing falsifier** recorded: if false-positive cost exceeds catch value in an explicit BR2 cost model, the layer does not earn its keep even at full recall.

## Q4 The BR2 bridge — UNANIMOUS; effectively settled by convergence

All five, independently: findings pivot from `file:line` to **task-local citation** (task ID + step/equation/table + quoted claim), with stated premises, expected consequence, and a **runnable falsifier that encodes the claim in the domain's tool language** — sympy for a proof step, `stoichiometric_balance` for a reaction, dimensional analysis for a buckling load — raising/`FALSIFIED` iff the defect is present. CC2's sharpening adopted: partition claims into mechanically-falsifiable vs deductive-only (UNTOOLABLE → HIL or 0.5-capped LLM verdict), and **the entire verification core — subprocess re-execution, CONFIRM-only asymmetry, HIL routing — is reused unchanged**: C2 is a claim-extraction + falsifier-authoring layer over the existing machinery. This is the C2 specification.

## Q5 Factorial target — UNANIMOUS: fresh synthesised module, never runner-tests-runner

All five reject runner-tests-runner (circularity; the measurement system becoming the measured object threatens baseline-cell integrity). CC2's ceiling-effect objection adopted with its own mitigation: a **factorial-grade module deliberately overloaded with 10–15 planted defects spanning easy → subtle**, preserving scorability while restoring headroom. Honest residual recorded (Gemini/DeepSeek/CC2 concur): a hand-planted defect set cannot replicate the unknown-unknown structure where feedback/divergence most plausibly help — the cost of choosing scorability over realism, carried into BR2 as an explicit caveat.

## Founder decision points

(1) Ratify topology: four per-domain modules, order chemistry → engineering → physics → biology (restores the original 48–51 numbering; factorial returns to 52). (2) Ratify the Q3 conjunctive gate as each module experiment's pre-registered pass condition. (3) Ratify the Q4 schema as the C2 specification (build scheduled post-factorial, as BR2 prep). (4) Ratify the factorial target: a sixth, factorial-grade module (10–15 layered defects). On ratification the one-shot sequence becomes: **47 divergence → 48 chem → 49 eng → 50 physics → 51 biology → 52 factorial** (~$170–260 total against $452 balance), module drafts panel-reviewed before each run per the locked spec.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
