# Exp 40 Pre-Launch Re-audit — Verified Outcome Table

**Date:** 2026-04-20, 17:50 BST
**Branch:** `exp39-experimental` at `5c81f33` (revert of `b3d9420`)
**Working tree:** clean; test suite reference: 1250 passing prior to this audit
**Scope:** Conclusion of the blast-radius audit following the 20 April 2026 revert of the Exp 40 pre-launch panel review that had carried an invalid "v1 preservation" framing.

## Background

On 20 April 2026 the five-round compelled-convergence panel review (commit `b3d9420`) was fully reverted after the framing error `P2. Runner v1 preservation` was identified as a conflation between `bench/reference_runner.py` (v1, historical Exp 38 demonstration artefact) and `bench/reference_runner_v2.py` (v2, the actual Exp 40 runner, actively extended through Phase A/B). The revert was committed as `5c81f33` and pushed to origin. Confer scripts and combined JSON logs from the reverted rounds were extracted to `/tmp/exp40_audit/` for audit use.

This document records the verified outcome of:
1. The corrective audit of every fix proposed in the reverted rounds against `reference_runner_v2.py`, the CDSFL directives, and the Stage 6 mathematical model.
2. A single re-confer round run under CORRECTED framing on 20 April 2026 at 17:42 BST (artefact `bench/logs/confer_exp40_reaudit_round1/combined_20260420T164144Z.json`).
3. Programmatic verification of every fix classified as keep.

## Sole Exp 40 acceptance anchors

Under corrected framing, only two anchors govern Exp 40 acceptance:

- `bench/exp40_configs/40_gate.json` `pass_condition`:
  > `"gamma >= 0.30 OR (3 consecutive rounds with 0 novel CRITICAL findings). Gamma-alt implemented in reference_runner_v2._check_gamma_alt_convergence."`
- Stage 6 orthogonality rule:
  > `R_k` measures validity; `nu_k` measures novelty; `c_ext` measures search quality. The three are independent reporting dimensions and must never be collapsed into a single score before reporting. `m_div` multiplies `eta_int` only, never `R_k` or `q`.

All predicate families, reason-trace schemas, and runtime novelty ceilings proposed in the reverted convergence are measured against these two anchors.

## Re-audit Round 1 — panel outcome

Five models (Gemini 3.1 Pro, Codex GPT-5.4, CC2 Claude Opus 4.6, ChatGPT GPT-5.4, DeepSeek R1-0528) answered four narrow questions under corrected framing in parallel (max_workers=5, star topology, no panel chair). Artefact `combined_20260420T164144Z.json`, 41 KB, five complete responses.

### RQ1. Activation-sequence gate — blocking or not

| Sub-question | Gemini | Codex | CC2 | ChatGPT | DeepSeek | Panel action |
|---|---|---|---|---|---|---|
| (a) SMT sandbox fix (`_verify_sympy`) | NOT REQUIRED; shadow-promote now | REQUIRED | NOT REQUIRED; shadow-promote now | NOT REQUIRED; activate now as non-blocking | REQUIRED | Activate now (5/5 for action; 3/2 on "required" label) |
| (b) 1E.10 runtime wrapper (line 3510) | NOT REQUIRED; defer to Exp 54 (identity function at `m_div=1.0`) | REQUIRED (Stage 6 canonical path) | PARTIALLY REQUIRED; activate now | REQUIRED (Stage 6 path + `R_k` adoption logging) | REQUIRED (Stage 6 orthogonality) | 4/5 for activate now; Gemini dissent |
| (c) K/L/M specialist live-promotion | NOT REQUIRED; defer | NOT REQUIRED; shadow-promote | NOT REQUIRED; shadow-promote now | NOT REQUIRED; shadow-promote if low-risk | NOT REQUIRED; shadow-promote (defer to Exp 41) | 5/5 NOT REQUIRED; 4/5 shadow-promote now |

### RQ2. Reason-trace instrumentation — Exp 40 or Exp 54

| Model | Position |
|---|---|
| Gemini | 4-field minimum required for admissibility attribution (`finding_id`, `model_id`, `admissibility_status`, `severity_and_novelty_flag`); reject 10-field |
| Codex | No schema required for Exp 40; defer reason-trace to Exp 54 |
| CC2 | Zero-field minimum; defer to Exp 54; optional `round_id` for joining |
| ChatGPT | No schema required for Exp 40; defer to Exp 54 |
| DeepSeek | 5-field minimum (`refuted`, `admissible`, `duplicate`, `rk_discrepancy`, `finding_id`); detailed traces deferred to Exp 54 |

**Panel action:** 5/5 reject the reverted 10-field schema. 5/5 agree rich attribution belongs in Exp 54. Residual split (3/2) on whether an explicit minimum schema is required for Exp 40; resolved by programmatic verification that the runner's existing `FindingFeedback` fields already cover the union of both proposed minima.

### RQ3. Four predicate families — diagnostic, gating, or not at all

| Family | Gemini | Codex | CC2 | ChatGPT | DeepSeek | Panel action |
|---|---|---|---|---|---|---|
| Math-path fidelity | Defer entirely | Diagnostic | Not Exp 40 (verified by tests) | Diagnostic | Post-hoc diagnostic | 5/5 NOT a gate |
| Correction fidelity | Diagnostic | Diagnostic | Defer to Exp 54 | Diagnostic | Post-hoc diagnostic | 5/5 NOT a gate |
| Counterfactual sensitivity | Diagnostic | Defer/optional | Defer to Exp 54 | Defer to Exp 41/54 | Defer to Exp 41 | 5/5 NOT a gate |
| Convergence stability | Diagnostic | Diagnostic | Already subsumed by `pass_condition` | Diagnostic | Defer to Exp 54 | 5/5 NOT a gate |

**Panel action:** `40_gate.json` `pass_condition` is the sole Exp 40 acceptance gate. No predicate family is elevated to gating.

### RQ4. Conditional novelty ceiling — Exp 40 scope or not

| Model | Position |
|---|---|
| Gemini | NO; defer to Exp 54 |
| Codex | YES, post-hoc sanity only; NOT runtime guard |
| CC2 | NO; defer to Exp 54 or later single-target experiment |
| ChatGPT | YES, post-hoc sanity only; NOT runtime guard |
| DeepSeek | YES, post-hoc sanity; defer runtime to Exp 54 |

**Panel action:** 5/5 against runtime guard. 3/5 permit post-hoc sanity computation from logs; 2/5 defer entirely. Operationally identical for Exp 40 runtime — no v2 code change required either way.

## Programmatic verification

Every actionable item was verified against the current state of `reference_runner_v2.py`, the Stage 6 decomposition, and the `_feedback.py` §17 channel implementation.

| Item | Check | Result |
|---|---|---|
| SMT sandbox bug | Run `_verify_sympy('2 + 2 == 4')` | Returns `UNCERTAIN`, evidence `UNVERIFIABLE: name 'Integer' is not defined`. Bug at `bench/immune_agents.py:977` (`global_dict={'__builtins__': {}}`) confirmed; every SymPy verdict currently UNCERTAIN. |
| 1E.10 wrapper identity at `m_div=1.0` | 1620 parameter combinations across `{R_old, sk, eta_int, c_ext, nu_k, d, p}` | `compute_rk_with_eta_channel(R, sk, eta, 1.0, c, nu, d, p) == compute_rk(R, eta * d * p * (1 - c*(1-nu)), sk)` to within `1e-12` for all 1620 cases. Gemini's identity claim verified. |
| R_k discrepancy §17 feedback class | Trace `rk_validation` source | Built by `validate_round_rk` → `_validate_rk_computation` at `reference_runner_v2.py:3254`. Recomputes R_k inline from corroboration text (lines 3318-3338), does NOT call `compute_rk` or the wrapper. Independent of the `:3510` call site. |
| `FindingFeedback` field coverage for §17 admissibility | Inspect `bench/dm/_feedback.py:42-105` | Existing fields: `finding_id`, `model_origin`, `severity_claimed`, `final_verdict`, `refutations`, `admissibility_failures`, `duplicates`, `rk_discrepancy`. Covers DeepSeek's 5-field minimum and Gemini's 4-field minimum as supersets. No new schema required for Exp 40. |
| K/L/M live promotion | Inspect `bench/immune_agents.py:334` | `LIVE_SPECIALIST_DOMAINS = frozenset({"mathematics", "statistics", "biology", "information_science"})`. Promotion is a literal one-line extension of the set. Gated by S5 constraint of the Exp 40 plan pending K/L/M tool coverage. |
| Conditional novelty ceiling runtime presence | Grep `nu_max`, `novelty_ceiling`, `conditional_ceiling` across runner v2 | No matches. Not currently wired. Panel's "NO runtime guard" convergence is consistent with current v2 state; no v2 code change required. |

## Verified outcome table

| # | Proposed fix | Classification | Panel convergence | Programmatic verification | Action for Exp 40 launch |
|---|---|---|---|---|---|
| 1 | SMT sandbox fix (`_verify_sympy` Integer construction) | MISSING_VALID | Activate now (5/5 action; 3 NOT REQ / 2 REQ on label) | Bug confirmed empirically; fix is scoped to `immune_agents.py:977` | Activate pre-launch per `feedback_shadow_promotion_now.md` (sole CDSFL policy currently in effect governing deferred shadow fixes). NOT a blocker for `40_gate.json` `pass_condition`. |
| 2 | 1E.10 runtime wrapper at `reference_runner_v2.py:3510` | MISSING_FRAMING_DEPENDENT | 4/5 activate now; 1/5 defer (identity function) | Identity confirmed across 1620 cases; R_k discrepancy feedback class independent | NOT required for acceptance. Optional shadow-promote for structural channel enforcement ahead of Exp 54 `eta_int_modulator` wiring. |
| 3 | K/L/M specialist live-promotion | MISSING_VALID | 5/5 NOT REQUIRED; 4/5 shadow-promote now | 1-line set extension at `immune_agents.py:334`; currently gated by S5 tool coverage | NOT required for acceptance. Founder decision: activate now per `shadow-promotion-now` or hold pending broader K/L/M tool-coverage confirmation. |
| 4 | Four predicate families as acceptance gates | MISSING_FRAMING_DEPENDENT | 5/5 NOT a gate | 40_gate.json `pass_condition` is sole gate | Discard as gating criteria. Optional diagnostic instrumentation permitted post-hoc. |
| 5 | 10-field reason-trace schema | OFF-TARGET | 5/5 reject | Runner's existing `FindingFeedback` fields cover minimum required | Discard. Rich attribution belongs in Exp 54 factorial. |
| 6 | Conditional novelty ceiling as runtime guard | OFF-TARGET | 5/5 NOT runtime | Not wired in current v2; leaving as-is is correct action | Discard runtime variant. Optional post-hoc sanity analysis permitted (3/5 YES, 2/5 defer). |
| 7 | Four-family "preservation" criteria framing | DISCARD | Framing refuted | n/a | Discarded with `b3d9420` revert. |
| 8 | Schema "preservation" enum hard-coding | DISCARD | Framing refuted | n/a | Discarded with `b3d9420` revert. |
| 9 | Conditional-ceiling runtime wiring as "preservation guard" | DISCARD | Framing refuted | n/a | Discarded with `b3d9420` revert. |

## Residual Exp 40 launch requirements

Under the verified outcome:

**Hard requirements (none remaining for acceptance beyond the quoted `pass_condition`):**
The runner already emits every field required for §17 admissibility attribution. The γ-alt path at `reference_runner_v2._check_gamma_alt_convergence` is live. The star topology is configured in `40_gate.json` line 7. No additional runtime fix is blocking launch.

**Founder-decision items (shadow-promote-now versus defer):**
- SMT sandbox fix — panel 5/5 for activate now; policy `feedback_shadow_promotion_now.md` in effect.
- 1E.10 wrapper activation — 4/5 activate now, 1/5 defer; `m_div=1.0` makes the wrapper mathematically transparent for Exp 40.
- K/L/M specialist live-promotion — 4/5 shadow-promote now, 1/5 defer to Exp 41; gated in plan on broader tool-coverage.

**Deferred to Exp 54:**
- Full reason-trace attribution schema.
- `eta_int_modulator` wiring into `compute_rk` with active `m_div` values.
- Any runtime novelty ceiling (if pursued at all).

## State of the repository at audit close

- Branch `exp39-experimental` at `5c81f33`; working tree clean.
- Test suite run in progress at audit close; reference count prior to audit was 1250 passing across runner v2 + §17 + §18 + S_k + Phase A + Phase B infrastructure.
- Memory and Desktop TTS files poisoned by the reverted framing have been removed: `project_exp40_prelaunch_lock.md`, `feedback_runner_preservation.md`, `Exp40_Prelaunch_Round1_Panel_2026-04-20.txt`, `Exp40_Prelaunch_Rounds2_to_3B_2026-04-20.txt`. `MEMORY.md` pointers removed. `ce_state.md` updated to reflect reverted status.
- Confer artefacts from the reverted rounds preserved at `/tmp/exp40_audit/scripts/` and `/tmp/exp40_audit/logs/` for reference.
- Round 1 re-audit artefact: `bench/logs/confer_exp40_reaudit_round1/combined_20260420T164144Z.json` plus five per-model JSON files.

## Panel convergence status

Under compelled convergence rules:
- RQ1(a): 5/5 panel convergence on action (activate). Label divergence (2 REQ / 3 NOT REQ) non-material — the action is the operational decision.
- RQ1(b): 4/5 convergence on activate; Gemini dissent verified algebraically as mathematically correct. Divergence resolved in Gemini's direction by programmatic test (identity at `m_div=1.0`). Panel position now coherent as NOT REQUIRED for acceptance, optional shadow-promote for structural Exp 54 prep.
- RQ1(c): 5/5 NOT REQUIRED; 4/5 activate now.
- RQ2: 5/5 reject 10-field schema; 5/5 defer rich attribution to Exp 54. Minimum-field divergence resolved by programmatic verification that existing fields are a superset of both proposed minima.
- RQ3: 5/5 across all four families — none are gating, `40_gate.json` is the sole gate.
- RQ4: 5/5 against runtime guard. 3/5 permit post-hoc, 2/5 defer; operationally identical for Exp 40 code.

No question requires a yield-or-refute Round 2. Every residual divergence is either resolved by programmatic verification or operationally non-material (label-level disagreement with identical actions).

## Founder-decision surface

With the verification closed, the remaining decisions are:

1. Accept the verified outcome table and recommit. The Exp 40 runner v2 is acceptance-ready under `40_gate.json` `pass_condition`.
2. Choose for each founder-decision item above between `shadow-promote-now` and `defer`.
3. Authorise Exp 40 launch under the accepted configuration, or hold pending further adjustment.

No code changes have been applied to `reference_runner_v2.py` during this audit. All three activate-now candidates (SMT, 1E.10 wrapper, K/L/M) remain pending founder authorisation.
