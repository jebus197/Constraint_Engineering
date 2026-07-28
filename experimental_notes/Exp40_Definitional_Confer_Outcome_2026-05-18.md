# Experiment 40 — Definitional Confer (advisory): Outcome

2026-05-18 12:25 BST

## Summary

An advisory five-model confer (Gemini 3.1 Pro, Codex GPT-5.5, CC2
Opus 4.7, ChatGPT GPT-5.5, DeepSeek V4 Pro; star topology, latest CDSFL
schema; purely factual framing, no embedded position, dissent
explicitly permitted) was run to inform — not bind — the decision on
what "converged / done" should mean for the CDSFL proof-of-concept,
given the fixed goal (a genuinely useful science/STEM calculator, not
theatre) and a hard resource bound (one developer, one M1 Mac Mini,
~1 month runway). All five returned cleanly (cc2 after one timeout
retry). Full unedited responses:
`bench/logs/confer_exp40_definitional_2026-05-18/`.

The result is one robust unanimity and one genuine, informative
dissent. Both are recorded here without collapse.

## Q1 — unanimous (5/5): total exhaustion is not attainable

Every model, independently from the verified facts, judged total
exhaustion (no new findings of any severity) mathematically
ill-matched and practically unreachable: the all-severity surface is
open-ended; the Duane reliability-growth model assumes a closed,
monotonically-depleting pool; empirical γ-all (0.10–0.23) confirms the
low-severity tail never empties; one month on one M1 cannot change
this. Pursuing total exhaustion is the permanent impasse. This is a
genuine, evidence-grounded 5/5, not a forced one, and it confirms the
operator's prior view on independent technical grounds.

## Q2 — NOT unanimous; the dissent is the valuable output

Distribution (recorded as-is, not harmonised): Gemini and CC2 → **X**
(critical/structural exhaustion, hardened). Codex → **X but explicitly
"not as implemented"**, with anti-cooking conditions strong enough to
bridge toward Z. ChatGPT and DeepSeek → **Z** (a pre-registered
*functional* benchmark: the artefact must actually solve held-out STEM
problems with mechanically-checkable answers).

Beneath the X/Z label there is a unanimous core (all five, both camps):

1. Total exhaustion (Y) is out.
2. The bare `severity ≥ 0.7` boundary is the single biggest
   vulnerability — every model flagged it independently — and must be
   replaced by a **pre-registered, consequence-based** definition: a
   finding is critical iff its presence would make the STEM result
   wrong, invalid, or unreliable; not a number, not style.
3. Convergence must be computed on the **settled** post-reconciliation
   registry, never live-at-round (the 0.305→0.231 flip).
4. Pre-registered before the run; scoped; transparently declared (the
   PoC certifies critical/structural convergence on a bounded
   artefact, explicitly does NOT claim total exhaustion, residuals
   catalogued and handed forward); apply-fixes-back ON;
   hostile-reviewer reproducible; the loose OR gate replaced by a
   stricter conjunction.

The genuine dissent, kept intact: **is internal critical-convergence
sufficient, or must the PoC also demonstrate correctness on a frozen
external STEM benchmark?** The Z camp's objection to pure-X is not
refuted by the X camp — internal convergence ("the panel stopped
finding serious problems") is not the same as "the artefact produces
correct answers." On the operator's fixed goal, external task validity
is load-bearing. DeepSeek's mechanical **test-impact** criterion (a
finding is critical iff fixing it would change a ground-truth test
output) is the sharpest single idea in the confer because it dissolves
the unprincipled-0.7 problem that all five named as the top risk.

## Synthesised position (compelled convergence via soundest argument)

The honest resolution is **not X or Z but their conjunction**, because
each camp's necessary condition is the other's blind spot. Defensible
"done" for the CDSFL PoC = a pre-registered consequence-based
critical/structural definition + settled-registry accounting +
critical-exhaustion stability over multiple rounds (the X-hardened
core; 5/5 on every condition) **AND** the artefact passes a frozen,
pre-registered held-out STEM benchmark with mechanical pass/fail, with
the test-impact criterion as the objective anchor (the Z/functional
condition; the surviving dissent). Neither alone proves the goal;
together they do, and the conjunction is harder to satisfy than the
current gate, not easier.

## P-pass of the synthesis (incl. working-model bias-check)

- *A 10-task benchmark is itself a small, gameable surface.* Survives:
  harder to cook than γ (pre-registration timestamp, spanned domains,
  mechanical pass/fail, hostile inspection), but confirms the benchmark
  is necessary-not-sufficient too — which is why the conclusion is the
  conjunction, not a substitution. The attack reinforces it.
- *Is the working model synthesising toward "harder + external" to
  please the operator / enable moving on?* The synthesis makes
  convergence harder, scopes the claim down, and delivers an unwelcome
  message (current internal convergence is insufficient evidence of the
  goal; a frozen external benchmark must be built and passed within the
  month). Opposite of agreement-to-please; survives.
- *Disclosure:* the cc2 panelist mis-framed itself as the working model
  being asked directly ("no need to dispatch external models"). Its
  substantive analysis is independent and consistent, so it
  corroborates; but its independence as a fifth panelist is weakened —
  weight as four-plus-one, not five clean.

## Concrete next steps (5/5-consistent; ~1 month / one M1)

- **Week 1:** freeze `POC_SCOPE.md` (claim, included modules, deferred
  items); write + commit the pre-registered consequence-based
  critical/structural rubric (resolves F6); fix the estimator to
  settled-registry-only (resolves F4; small change); freeze + commit a
  held-out STEM benchmark (~10 problems, analytic ground truth,
  mechanical harness).
- **Weeks 2–3:** run the bounded PoC on decomposed slices,
  apply-fixes-back ON, gated by the conjunction (settled critical-γ
  stable + ≥3 rounds zero novel critical + zero test-impact findings +
  all benchmark tasks pass).
- **Weeks 3–4:** robustness sweep (multi-threshold γ, leave-one-round-
  out, live-vs-settled delta), one isolated adversarial pass, audit
  bundle, scope-declared write-up, hand-forward specification.
- **Defer:** λ_ext (re-injection-extended Duane), full 27-task Bench
  Run 2, any total-exhaustion claim.

## Bottom line for the decision

The internal convergence work to date does not, by itself, demonstrate
the fixed goal. A defensible one-month PoC must show the system
correctly solves pre-registered STEM problems it was not tuned
against, with critical/structural defined by consequence and frozen
before the run. Harder than the prior path; also the first point in
this arc that ends somewhere externally defensible. Advisory: this
informs the operator's decision; it does not replace it.

## Cross-references

- Full responses + combined log:
  `bench/logs/confer_exp40_definitional_2026-05-18/`
- Confer script: `bench/confer_exp40_definitional_2026-05-18.py`
- Prior: Experiment 40 γ-Hardening Confer Outcome (2026-05-17);
  plan-F full-budget resume FALSIFIED outcome (2026-05-18).
- Plain-English companion: Experiment 40 Definitional Confer —
  Plain English (2026-05-18); TTS mirror in the CDSFL TTS folder.

Written under CDSFL note standard v1.2 (14 May 2026).
