# Experiment 40 Pre-Launch Panel Audit — Full Enumeration and Fold-In Synthesis

**Date:** 20 April 2026
**Context:** Six confer rounds (five reverted "v1 preservation" rounds + one re-confer under corrected framing) were run over approximately 48 hours as a pre-launch panel review for Experiment 40. The reverted rounds used a framing premise that was subsequently refuted: that `reference_runner_v2.py` must "preserve the behavioural signature" of the Exp 39 `reference_runner.py`. The corrected re-confer (Round 1, 20 April 2026) explicitly rejected that premise and anchored only on the `bench/exp40_configs/40_gate.json` pass condition plus the Stage 6 orthogonality rule.
**Test article for Exp 40:** `bench/dm/_feedback.py` (the §17 feedback channel implementation, approximately 22 KB) plus `bench/dm/_types.py` (approximately 30 KB).
**Pass condition:** `gamma >= 0.30 OR (3 consecutive rounds with 0 novel CRITICAL findings)` — star topology, `max_rounds = 8`, `earliest_stop_round = 3`.
**Panel composition:** Codex GPT-5.4 (OpenRouter), Gemini 3.1 Pro (Google GenAI), CC2 (Claude Opus 4.6 via CLI piped mode), ChatGPT GPT-5.4 (OpenRouter), DeepSeek R1-0528 (OpenRouter).

---

## 1. Starting inventory — what the v2 runner already carries over the v1 baseline

Cross-walk against `bench/reference_runner.py` (Exp 39 baseline, 4344 lines) confirms the following identifiers are **genuinely new** in `bench/reference_runner_v2.py` (4922 lines):

| Identifier | v1 count | v2 count | Status |
|------------|---------:|---------:|--------|
| `compute_rk_with_eta_channel` | 0 | 2 | Defined (line 3177). Two references are the definition itself plus the docstring pointer in bare `compute_rk` (line 3145). **Never called.** |
| `ChannelViolationError` | 0 | 3 | Defined and raised from within the wrapper when channel invariants are violated. |
| `_check_gamma_alt_convergence` | 0 | 2 | Defined at line 1064. Implements `gamma >= threshold OR window-consecutive-zero-novel-CRITICAL`. Called in the main round loop. |
| `GAMMA_ALT_CONVERGED` | 0 | 2 | Enum value and string literal for convergence stop condition. |
| `eta_int_modulator` | 0 | 1 | Referenced in one specialist dispatch path (line 4477) where the severe 0.60 tier is surfaced. |
| `m_div` | 0 | 15 | Appears throughout the wrapper body, the `ChannelViolationError` message, Stage 6 docstrings. Never assigned a non-identity value in the current hot path. |

The γ-alt convergence branch is therefore a v2-native capability with no v1 analogue, and the divergence-modulator channel (`compute_rk_with_eta_channel` + `ChannelViolationError`) exists as infrastructure but is not wired into the live R_k update path at `reference_runner_v2.py:3510`. That single call site reads `q = meta.get("q", 0.5)` as a scalar and feeds it directly to bare `compute_rk`; the per-finding `model_params` dict contains only `nu_b`, `nu_f`, `q`, `R` — it does not decompose q into `{eta_int, c_ext, nu_k, d, p}`. Wrapper activation therefore requires an upstream schema expansion, not a drop-in swap at the call site.

The `_verify_sympy` specialist at `bench/immune_agents.py:947-1019` carries a silent regression: the sandbox uses `global_dict={"__builtins__": {}}` without exposing `sympy.Integer`, `sympy.Float`, or other numeric constructors, so `parse_expr` fails on any claim that requires literal Integer construction (`"2 + 2"`, `"x + 1 > x"`, `"x**2 >= 0"` — verified programmatically; see §3). The RCE blocklist at line 962 correctly catches `__import__`, `__class__`, `eval`, `open`, and similar tokens.

The `40_gate.json` configuration (read end-to-end) is consistent with the corrected framing: `eta_int_modulator_wired_into_compute_rk: false`, `_specialist_cells.live = ["mathematics", "statistics", "biology", "information_science"]`, `functional_shadow = ["physics", "chemistry", "engineering"]`, topology star, max_rounds 8, earliest_stop_round 3. The γ-alt branch in the pass_condition is feasible under these parameters (6-round window available for a 3-consecutive requirement).

---

## 2. Full enumeration of fix proposals across all six rounds, with model attribution

### Round 1 (confounded "v1 preservation" framing — reverted on 20 April 2026)

**F1 — Fix SymPy sandbox silent regression.**
- Codex: "Must land before launch. Real blocker in disguise." Fix candidate: "fix sandbox parsing in a minimal way, then add a live regression test proving integer literal handling works while the RCE lockdown remains intact."
- Gemini: "Defer for Exp 40. SymPy's inability to parse integers is operationally irrelevant for this specific run. Becomes a critical blocker for Bench Run 2."
- ChatGPT: "Must land or be explicitly hard-disabled. Either fix parsing safely, or remove SymPy from decisive routing and mark it unavailable until fixed. 'Known broken but still wired' is worse than absent."
- DeepSeek: "Critical blocker. Silent UNCERTAIN verdicts corrupt mathematics-domain verification. Fix sandbox to allow Integer construction without RCE."
- CC2: "Blocker for Bench Run 2, not for Exp 40. Whitelist `{int, float, bool, range, len, type, True, False, None}` and re-run the SymPy specialist test suite."

**F2 — Activate 1E.10 `compute_rk_with_eta_channel` wrapper at `reference_runner_v2.py:3510`.**
- Codex: "Keep deferred full activation, but add a launch-time static assertion at the current call site that `w(f)` and `m_div` are absent from `compute_rk` inputs by construction, plus a TODO-guarded failing test that flips once Exp 54 wiring lands." (Defer activation.)
- Gemini: "Blocker in disguise. Do not defer this to Exp 54. Fix immediately by activating the wrapper at `reference_runner_v2.py:3510` and passing a hardcoded `m_div = 1.00`. This secures the channel invariant natively." (Activate now.)
- ChatGPT: "Can defer if and only if documented as intentionally inactive. Do not activate dead assertions for theatre. But annotate the production call site with an explicit invariant debt comment." (Defer with annotation.)
- DeepSeek: "Defer. Activation without `m_div` would crash. Fix during Exp 54 wiring."
- CC2: "Not a blocker. Add a debug-mode assertion at line 3510 that checks `q == η_combined * d * p` with the canonical decomposition, even without wiring `m_div`." (Defer with upstream-q diagnostic.)

**F3 — Runner v2 promotion decision.**
- All five panel members: governance blocker, not technical. Founder decision. If Exp 40 depends on v2-only mechanisms (star topology enforcement, per-model ρ, structured tool-use, γ-alt convergence), running on v1 invalidates the experiment.

**F4 — K/L/M live-promotion (physics, chemistry, engineering specialists).**
- All five: defer for Exp 40. Software-target experiment; shadow-wired specialists do not contribute to `_feedback.py` validation.

**F5 — Adversarial-panel P-pass on Phase A+B code.**
- All five: the panel review itself is this pass. Required, in progress.

**F6 — Diversity (1E.7) and recidivism (1E.9) scoring integration.**
- All five: defer. Log-only is correct pre-Exp 54.

**F7 — M1 cross-domain composability architecture order (B = cells→configs, C = configs→configs, D = cells→cells).**
- Codex: D → B → selective C.
- Gemini: C → D, with B deferred.
- ChatGPT: D → B → selective C.
- DeepSeek: C > D > B ("C first to fix single-domain myopia; D second to reduce false UNCERTAINs; B last").
- CC2: B → D → C ("B is highest-value because it makes configs empirical").

**F8 — M1 rule for combining N domain verdicts on one claim.**
- Codex: "Definitive contradiction veto, otherwise weighted corroborative aggregation. If any high-confidence domain returns a definitive refutation, overall verdict is not definitive-support."
- Gemini: "`p_eff = 1 − Π_j (1 − p_j)`. Multi-domain verification legitimately accelerates `R_k(i)` toward 1.0 via `p`, not via `eta_int`."
- ChatGPT: "Confidence-weighted admissibility with contradiction veto. DEFINITIVE-SUPPORT requires either one high-confidence primary-domain support with no refutation, or two or more independent supports with no refutation."
- DeepSeek: "First-definitive-tool-wins policy."
- CC2: "First-definitive, not majority. If both domains return DEFINITIVE and agree, both verdicts stand. If they conflict, both verdicts carry a CONFLICT flag and the finding is escalated."

**F9 — M2 topology for Exp 40 (infrastructure gate).**
- Unanimous: star.

**F10 — M2 third topology.**
- Codex: "Star-with-paired-challenge. Shared registry remains canonical, but each finding can trigger one bounded adversarial exchange between two assigned models."
- Gemini: "Star-with-Challenge. Models submit structured findings to the blackboard, but the coordinator can open a temporary pairwise challenge thread on one finding only."
- ChatGPT: "Star with scoped challenge channels. Preserves schema discipline while allowing direct adversarial extension."
- DeepSeek: "Sequential pipeline (model N sees 1..N−1) is not useful — it delays feedback and amplifies early errors." (Rejects third topology.)
- CC2: "Star-with-paired-challenge. One model pair assigned adversarial challenge duty on each other's findings while the remaining three models file independent discoveries. Pair rotates each round. 5 choose 2 = 10 distinct pairings across 10 rounds."

**F11 — M3.i Correctness ratio M/N.**
- Unanimous: not a Stage 6 channel. Track separately as orthogonal benchmark / calibration diagnostic.

**F12 — M3.ii Novelty boundary (constraint density → novelty vs hallucination).**
- Unanimous: not derivable from Stage 6 math alone. Empirical, to be measured in Bench Run 2.

**F13 — M3.iii External DCY formulation.**
- All five: reject as presented. Four of five propose a salvageable correction:
  - Codex: "`DCY = (1 − sim) * (1 − Jaccard(Deps(f), Deps(A_k)) * I_FFF)`" with sim-boundary fix.
  - ChatGPT: "`DCY' = max_k [(1 − sim_norm(f, A_k)) * (1 − Jaccard*(f, A_k))]`" with I_FFF as gate on Jaccard term only.
  - CC2: "`DCY = max_k [(1 − s(f, A_k) / 0.86) * (1 − J(Deps(f), Deps(A_k))) + (1 − I_FFF) * s_floor]`".
  - DeepSeek: reject outright, no salvage ("discrete `m_div` is sufficient and auditable; continuous DCY duplicates effort").
  - Gemini: reject outright ("continuous semantic similarity is already rigorously handled by the suppression channel `w(f)`; modulating `eta_int` using an unbounded similarity metric risks violating orthogonality").

**F14 — M3.iv "Just doing maths" objection.**
- All five: operationally indistinguishable from the framework's current capabilities. Invention-engine goal does not require the distinction to be resolvable.
- Codex: proposes "out-of-distribution prospective success under verification on tasks with low retrieval plausibility".
- Gemini: proposes "explicit resolution of a multi-domain claim using a verification path that crosses specialist boundaries not present in the training data".
- ChatGPT: proposes "counterfactual novelty under constrained search: hold `c_ext` high, require solutions that are independently valid, then test whether outputs remain non-derivable from retrieved neighbors by expert post-hoc reconstruction".
- CC2: proposes "a solution that is independently verifiable as correct, novel against the literature (`nu_k > 0.6`, `c_ext > 0.5`), and not reconstructible from any single training-data source — the third condition is not measurable within the current framework".
- DeepSeek: "empirically indistinguishable; the invention engine succeeds if outputs are correct and novel".

**Codex-specific from §A:** add static assertion that `w(f)` and `m_div` are absent from `compute_rk` inputs by construction — forward-protection for the deferred activation.

**CC2-specific from §A:** add a debug-mode assertion at line 3510 checking `q == eta_combined * d * p` with canonical decomposition, independent of m_div wiring.

**ChatGPT-specific from §A:** stratify closures into library-complete / shadow-integrated / live-operational, instead of the binary "landed / not landed" label. Warn that 1D.5 re-prompt loops can cause retry-induced format overfitting (mechanical parse recovery is not semantic recovery). Warn that 1E.11 "first definitive verdict wins" is a latent priority-inversion source.

### Rounds 2a, 2b, 3, 3b (still confounded by "v1 preservation" framing)

The multi-round structure produced lockable positions on the Q3/Q4/Q5/Q6 sequence. These are retained here for completeness, with the strong caveat that the re-confer under corrected framing supersedes them:

- **Q3-lock (conditional novelty ceiling placement).** Round 3 split: Codex, ChatGPT, DeepSeek for (w2) post-hoc analysis; CC2, Gemini for (w1) runtime guard-rail. Round 3b arbitration locked **(w2) post-hoc only**. Codex's derivation: `nu_max = 1 − (1 − (R − R_min) / (R × (1 − R_min) × eta_int × d × p)) / c_ext`.
- **Q4-lock (unified reason-trace schema).** Round 3b locked the CC2 **10-field schema**: `point_id`, `stance (yield|refute|unchanged)`, `target_model`, `pivot_quote`, `pivot_quote_verified`, `reason_type (math_error|logical_gap|scope_error|corrected_misread|unsupported_assumption|tool_output)`, `reason_text`, `prior_position_hash`, `revised_position`, `state_delta`. Gemini's 3-field scheme and DeepSeek's cosine-similarity auto-tag both refuted.
- **Q5-lock (v1 preservation predicates).** Round 3b locked the CC2 **4-family scheme**: math-path fidelity (`forbidden_pattern_hits == 0`); correction fidelity (`downstream_revisits >= upstream_revisions`); counterfactual sensitivity (deterministic-stride perturbation of `eta_int` or `nu_k` by ±0.15 on at least 10% of dispatches); convergence stability (unresolved-points non-increasing, reasoned yields ≥ compliance yields). DeepSeek's `residual_risk < 0.05 and fail_rate = 0` refuted.
- **Q6-lock (topology label).** Unanimous `star`. Codex's "(c) star-now, paired-challenge-at-41" composite refuted as a cross-experiment plan, not a per-experiment label.

### Re-confer Round 1 (CORRECTED framing — 20 April 2026)

The re-confer abandoned "v1 preservation" and anchored on `40_gate.json` pass_condition plus the Stage 6 orthogonality rule. Four research questions RQ1–RQ4 were posed.

| RQ | Codex | Gemini | CC2 | ChatGPT | DeepSeek |
|---|-------|--------|-----|---------|----------|
| **RQ1a SymPy sandbox** | REQUIRED | NOT-REQ (shadow-promote) | NOT-REQ (shadow-promote) | NOT-REQ (activate non-blocking) | REQUIRED |
| **RQ1b 1E.10 wrapper** | REQUIRED | NOT-REQ (defer to Exp 54) | PARTIALLY REQUIRED | REQUIRED | REQUIRED |
| **RQ1c K/L/M promotion** | NOT-REQ | NOT-REQ | NOT-REQ | NOT-REQ | NOT-REQ |
| **RQ2 reason-trace schema** | No | 4-field (`finding_id`, `model_id`, `admissibility_status`, `severity_and_novelty_flag`) | 0 fields (optional `round_id` for forward-compat) | No | 5-field (`refuted`, `admissible`, `duplicate`, `rk_discrepancy`, `finding_id`) |
| **RQ3 math-path fidelity** | Diagnostic | Not applicable to `_feedback.py` (no continuous maths) | Not applicable (already verified by 200+ unit tests) | Diagnostic | Post-hoc diagnostic |
| **RQ3 correction fidelity** | Diagnostic | Diagnostic | Not Exp 40 (defer to Exp 54 causal question) | Diagnostic | Diagnostic |
| **RQ3 counterfactual sensitivity** | Not Exp 40 acceptance | Diagnostic | Not Exp 40 (literally Exp 54's factorial design) | Not Exp 40 (defer to Exp 41 or Exp 54) | Not Exp 40 (defer to Exp 41) |
| **RQ3 convergence stability** | Diagnostic | Diagnostic | Already subsumed by `40_gate.json` pass_condition | Diagnostic | Not Exp 40 (defer to Exp 54 stability analysis) |
| **RQ4 `nu_max` ceiling** | Post-hoc only | NOT Exp 40 scope (defer to Exp 54) | NOT Exp 40 scope (orthogonality violation if runtime) | Post-hoc only | Post-hoc only |

**CC2 re-confer key insight on RQ1b:** "Bare `compute_rk` without the eta channel means R_k discrepancy feedback (one of §17's four feedback types per `_feedback.py`) cannot fire correctly — there's no `eta_combined` to detect discrepancies against. Without it, §17 admissibility rates are measured over 3/4 feedback classes — the logged signal is incomplete." This is the strongest argument for wrapper activation and it is behavioural, not cosmetic.

**Corrected-framing convergence:**
- **Unanimous:** RQ1c (K/L/M not required). RQ3 (all four families post-hoc or not Exp 40). RQ4 (ceiling post-hoc only).
- **4-of-5:** RQ1b 1E.10 wrapper activation required or partially required (only Gemini dissents, arguing m_div=1.0 is behaviourally an identity function and therefore pointless). RQ2 no rich schema required for Exp 40 (Gemini's 4-field and DeepSeek's 5-field minima are lighter than the reverted 10-field lock).
- **Split 2-3:** RQ1a SymPy sandbox — two REQUIRED (Codex, DeepSeek), three NOT-REQ-but-activate (Gemini, CC2, ChatGPT). All five agree the fix should be applied; they disagree only on whether its absence blocks launch.

---

## 3. Programmatic verification (`sy`) of the critical claims

Performed inline with SymPy 1.14.0 on Python 3.13 (results captured in the run log):

**(1) SymPy sandbox regression — reproduced and fixed.**
Current sandbox fails `"2 + 2"`, `"x + 1 > x"`, `"x**2 >= 0"` with `name 'Integer' is not defined`. It accepts `"Eq(x + y, y + x)"` because `Eq` is in the local_dict. Fix candidate — add an allow-list to `global_dict` that exposes `{Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, exp}` while keeping `__builtins__: {}` — parses all four claims correctly. The MF-40 RCE blocklist still catches `__import__`, `__class__.__bases__`, `eval(...)`, `open(...)`. No RCE regression from the fix.

**(2) Codex's `nu_max` ceiling formula — derivation correct.**
From `R_new = R * (1 − q) / (1 − q * R)` with the constraint `R_new ≥ R_min`, SymPy solves for `q_max = (R − R_min) / (R × (1 − R_min))`. Substituting `q = eta_int × (1 − c_ext × (1 − nu_k)) × d × p` (the Stage 6 composition at `m_div = 1.0`) and solving for `nu_k` yields exactly Codex's published formula (symbolic difference = 0 against his version).

At a representative working point — `R = 0.9`, `R_min = 0.8`, `eta_int = 0.5`, `d = 0.7`, `p = 0.6`, `c_ext = 0.4` — `nu_max` evaluates to **5.11**, which exceeds the natural domain `[0, 1]` of novelty and is therefore **non-binding**. The ceiling only becomes binding when `q_max < eta_int × d × p`; at the reference point `q_max = 0.556` but `eta_int × d × p = 0.210`, so the ceiling is inactive. This substantially weakens the argument for runtime enforcement: the operational value of the ceiling is lower than its algebraic validity suggests, because the typical parameter regime keeps it non-binding.

**(3) `m_div = 1.0` as "identity function" — partially false at the current call site.**
The wrapper `compute_rk_with_eta_channel(m_div = 1.0, ...)` computes `eta_combined = eta_int × (1 − c_ext × (1 − nu_k))` and then `q = eta_combined × d × p`. Bare `compute_rk` reads `q` as a scalar from `entry["model_params"]` at `reference_runner_v2.py:3497`. The wrapper-equals-bare claim holds **only if** the upstream `q` that the caller stores in `model_params` was composed from the full `eta_int × (1 − c_ext × (1 − nu_k)) × d × p` product. If the upstream callers produced `q` as a plain scalar or from a partial composition (for example `eta_int × d × p` without the `c_ext` term), wrapper activation is a behavioural change, not an identity operation. This means Gemini's "identity function, therefore mathematically meaningless" argument is only valid conditional on an upstream invariant that has not been independently established, and CC2's "enables R_k discrepancy feedback" argument gains force.

The per-finding schema in the current v2 runner carries `model_params = {nu_b, nu_f, q, R}` only. Activating the wrapper requires the schema to expand to `{nu_b, nu_f, eta_int, c_ext, nu_k, d, p, R}` (or similar decomposition) plus changes to whichever upstream code emits `model_params`. This is a real architectural increment, not a one-line swap at line 3510.

**(4) γ-alt feasibility under current gate config.**
`max_rounds = 8`, `earliest_stop_round = 3`, consecutive-zero-CRITICAL requirement = 3 → available window = 6 rounds. 3-consecutive is reachable inside the window. Feasible.

---

## 4. Classification of every fix against the current `reference_runner_v2.py` state

Using the classification buckets: **already-in-v2** (done, no action), **fold-in-now** (required for Exp 40 launch under corrected framing), **fold-in-later** (required before Bench Run 2 but not Exp 40), **defer-with-annotation** (carry a `TODO`/`NOTE` but do not implement), **off-target** (framing-dependent proposal now rejected).

| # | Fix proposal | Round | Source | Classification | Action |
|---|--------------|-------|--------|----------------|--------|
| 1 | γ-alt convergence (`_check_gamma_alt_convergence`) | Pre-existing | v2 scaffolding | **already-in-v2** | No action — lines 1064ff, invoked in round loop. |
| 2 | `compute_rk_with_eta_channel` wrapper + `ChannelViolationError` | Pre-existing | v2 scaffolding | **already-in-v2 as library** | Library defined at lines 3177ff. Not yet called. |
| 3 | `eta_int_modulator` config field | Pre-existing | `40_gate.json` | **already-in-v2 as flag** | `eta_int_modulator_wired_into_compute_rk: false` — flag present. |
| 4 | Runner v2 promotion (F3) | R1 all 5 | Governance | **fold-in-now** (founder decision) | Exp 40 runs on v2 regardless — confirmed. Administrative only. |
| 5 | Adversarial panel P-pass (F5) | R1 all 5 | Panel | **fold-in-now — completed by this audit** | This document is the pass. |
| 6 | SymPy sandbox fix (F1, RQ1a) | R1 Codex/ChatGPT/DeepSeek majority + re-confer 2/5 REQUIRED, 3/5 NOT-REQ-but-activate | All 5 models | **fold-in-now under shadow-promotion-now policy** | Unanimous agreement that the fix should be applied. The question of whether its absence blocks Exp 40 launch is moot once the fix lands. Low-cost repair; high signal-quality dividend. |
| 7 | 1E.10 wrapper activation at `reference_runner_v2.py:3510` with `m_div = 1.0` (F2, RQ1b) | R1 Gemini only ("now"); re-confer 4/5 REQUIRED (Codex, CC2, ChatGPT, DeepSeek), 1/5 NOT-REQ (Gemini) | All 5 models | **fold-in-now with caveats** | Required by majority under corrected framing. Requires upstream schema expansion so that `model_params` carries `{eta_int, c_ext, nu_k, d, p}` and wherever `model_params` is produced, the emit path sets these fields. At `m_div = 1.0` the wrapper is mathematically equivalent to bare `compute_rk` only if upstream `q` composition included the `c_ext` term; if not, activation is a real behavioural change. The CC2 R_k-discrepancy feedback argument (one of §17's four feedback classes is structurally disabled without wrapper) is the strongest behavioural reason to activate. Include a dry-run of Exp 39 data through the wrapped path before Exp 40 launch, per Gemini's R1 P-pass revision. |
| 8 | Debug-mode assertion at line 3510 checking `q == eta_combined × d × p` | R1 CC2 (§A) | CC2 | **fold-in-now** | Cheap diagnostic; catches upstream composition drift independent of whether the wrapper is activated. One-line assertion gated on a `DEBUG_CHANNEL_CHECK` flag. |
| 9 | K/L/M live-promotion flip (F4, RQ1c) | R1 unanimous defer; re-confer unanimous NOT-REQ | All 5 | **defer-with-annotation** | Exp 40 is software-scoped. `functional_shadow` posture remains correct. Schedule for Bench Run 2 calibration after the empirical exercise on real physics/chemistry/engineering claims. |
| 10 | Diversity (1E.7) and recidivism (1E.9) scoring integration (F6) | R1 unanimous defer | All 5 | **defer** | Log-only is correct pre-Exp 54. No Exp 40 work needed. |
| 11 | Cross-domain composability architecture (F7, meta-question M1) | R1 all 5, ordering varies | All 5 | **defer** (out of Exp 40 scope) | Exp 40 single-domain (software) target. No architectural change required. Record positions for Exp 54 design input. |
| 12 | Rule for combining N domain verdicts (F8) | R1 all 5, mechanism varies | All 5 | **defer** (out of Exp 40 scope) | Only matters once K/L/M are promoted; see row 9. |
| 13 | Star topology for Exp 40 (F9, Q6-lock) | R1 + R3b unanimous; re-confer anchor | All 5 | **already-in-v2** | `40_gate.json` `topology: "star"` confirmed. |
| 14 | Third topology — star-with-paired-challenge (F10) | R1 Codex/Gemini/ChatGPT/CC2; DeepSeek rejects | 4 of 5 | **defer** to Exp 41 | Out of Exp 40 scope. Record for the paired-challenge follow-up. |
| 15 | M/N correctness ratio as separate channel (F11) | R1 unanimous | All 5 | **defer** (Bench Run 2 reporting) | Not a Stage 6 channel; orthogonal throughput metric. No Exp 40 action. |
| 16 | Novelty boundary is empirical, not derivable (F12) | R1 unanimous | All 5 | **defer** (Bench Run 2 data) | Acknowledgement; no action. |
| 17 | Reject continuous DCY formulation (F13) | R1 unanimous reject; 3/5 propose salvage | All 5 | **off-target for Exp 40** | Discrete `m_div` tiers are sufficient. Continuous DCY is speculative engineering; revisit post-Bench Run 2 if motivated by data. |
| 18 | Synthesis-vs-retrieval operational signal (F14) | R1 unanimous "operationally indistinguishable" | All 5 | **defer** | Philosophical; invention-engine goal does not require resolution. |
| 19 | Static assertion that `w(f)` and `m_div` are absent from bare `compute_rk` inputs | R1 Codex (§A) | Codex | **superseded by row 7** | If wrapper is activated, this assertion becomes redundant. If deferred, reconsider. |
| 20 | Stratify closures into library-complete / shadow-integrated / live-operational | R1 ChatGPT (§A) | ChatGPT | **fold-in-now (documentation only)** | Apply to the Phase A/B closure ledger in ONBOARDING.md when documenting Exp 40 launch readiness. |
| 21 | 1D.5 re-prompt retry-induced format overfitting warning | R1 ChatGPT (§A) | ChatGPT | **defer with note** | Low risk; add to Exp 40 post-run analysis checklist. |
| 22 | 1E.11 "first definitive verdict wins" priority-inversion risk | R1 ChatGPT (§A) | ChatGPT | **defer with note** | Not triggered in single-domain Exp 40; revisit when K/L/M promote. |
| 23 | Q3-lock — `nu_max` ceiling runtime/post-hoc placement | R3b locked (w2) post-hoc; re-confer unanimous post-hoc-or-out-of-scope | All 5 | **defer** (post-hoc analysis only) | Do not wire at runtime. Post-hoc computation is trivial — one SymPy formula over session parameters. Execute after Exp 40 completes. The ceiling is non-binding at typical parameter values (numerically verified — `nu_max = 5.11` at the reference point), which reduces its operational value. |
| 24 | Q4-lock — unified 10-field reason-trace schema | R3b locked 10-field; re-confer 4/5 no-schema (Gemini 4-field, DeepSeek 5-field, three zero-field) | Confounded by "v1 preservation" framing | **off-target** | The 10-field schema was anchored on preservation reasoning that has been refuted. For Exp 40, no per-finding reason-trace is required beyond what the existing finding schema already carries for §17 admissibility. Defer the full attribution schema to Exp 54, where the 2×2 factorial requires it. If forward-compatibility is desired, a single `round_id` or a 4-field minimum (Gemini's `finding_id`, `model_id`, `admissibility_status`, `severity_and_novelty_flag`) is cheaper and achieves the same post-hoc joining capability. |
| 25 | Q5-lock — v1 preservation 4-family predicate gates | R3b locked 4 families as gates; re-confer unanimous diagnostic-or-not-applicable | Confounded framing | **off-target as gates; defer as diagnostics** | Under corrected framing, these do not gate Exp 40 acceptance. `40_gate.json` pass_condition is the sole gate. Counterfactual sensitivity specifically is Exp 54's factorial design. Log the equivalent data passively if cheap; do not add acceptance predicates to `40_gate.json`. |

---

## 5. P-pass — active falsification of this synthesis

**(a) Falsifier against row 7 (wrapper activation required).** If every caller that produces `model_params["q"]` already composes `q = eta_int × (1 − c_ext × (1 − nu_k)) × d × p` upstream, then the wrapper at `m_div = 1.0` is behaviourally identity and Gemini is right. Not every producer of `model_params` has been inspected in this audit; there are approximately 15 `eta_int` references in v2, most in the wrapper body and Stage 6 docstrings, not in call-path producers. **Mitigation:** the fold-in implementation must locate every producer (`grep "model_params" -r bench/`) and either confirm full composition or patch them. The CC2 R_k-discrepancy-feedback argument is strong on its own even if the upstream composition is complete, because the wrapper's structural `ChannelViolationError` path is not reachable from bare `compute_rk`.

**(b) Falsifier against row 6 (SymPy sandbox fix required).** If `_verify_sympy` is never invoked for any Exp 40 finding (because the software target `_feedback.py` never emits a claim that routes to the math specialist), then the fix is immaterial for Exp 40. This is consistent with Gemini's and ChatGPT's positions. **Mitigation:** even under this falsifier, all five models agree the fix should be applied; the only disagreement is whether its absence blocks launch. Shadow-promotion-now policy applies regardless. The fix is also cheap — one allow-list in one function.

**(c) Falsifier against row 23 (`nu_max` ceiling non-binding at typical values).** If Exp 40 produces findings with high `eta_int × d × p` (say 0.8), then `nu_max` drops into `[0, 1]` and becomes binding. The numeric check used `eta_int = 0.5`, `d = 0.7`, `p = 0.6` — these are reasonable priors but not empirically calibrated against Exp 40's actual `_feedback.py` findings. **Mitigation:** the post-hoc analysis should compute `nu_max` over the actual per-finding parameter distribution, not a single representative point. If the empirical distribution shows binding frequency above a threshold (say 10 percent of findings), revisit the runtime-guard question for Exp 54.

**(d) Falsifier against the overall "defer the 10-field schema" verdict (row 24).** If Exp 54's factorial analysis later discovers that critical attribution signals — whether a yield was reasoned or compliance-driven — are impossible to reconstruct from Exp 40 logs post-hoc, then omitting the reason-trace now is a cost that has to be paid later with re-runs. **Mitigation:** record the 10-field schema in a design document as the Exp 54 attribution schema. Defer the runtime implementation to Exp 54 rather than dropping the schema entirely.

**(e) Falsifier against row 8 (debug-mode q-composition assertion).** If the assertion catches a genuine bug, we gain signal. If it never fires, it adds dead code. **Mitigation:** gate on a `DEBUG_CHANNEL_CHECK` flag that is on by default for Exp 40's first run and off for later runs. Document the flag's half-life.

**(f) Falsifier against the corrected-framing re-confer itself.** The re-confer ran a single round per model. It did not run Rounds 2a/2b/3/3b under the corrected framing. Compelled-convergence P4 requires the full round structure when multi-round arbitration is needed; a single round may have missed positions that would have emerged under challenge. **Mitigation:** for a single-domain software target with unanimous agreement on the five subsidiary questions (RQ1c, RQ3 all four families, RQ4), the single round is sufficient. The one split (RQ1a SymPy) is resolved by the shadow-promotion-now policy, which is an independent standing rule from 20 April 2026. The one 4-of-5 question (RQ1b 1E.10) has Gemini as the dissenting voice; Gemini's argument (identity function) is partially refuted by the `sy` check above (§3 item 3). Further rounds would be value-adding if the founder judges the current evidence insufficient, but none of the positions are evidence-underdetermined.

---

## 6. Synthesis — what to fold into the runner before Exp 40 launches

**Must land pre-launch (fold-in-now):**

1. **Fix `_verify_sympy` sandbox (row 6).** Replace the empty `global_dict` with an allow-list exposing `{sympy.Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, exp}` while retaining `__builtins__: {}`. Add a regression test with the four claims from §3 item 1 and one negative RCE test (`"__import__('os')"` must still be blocked). Approximately 20 lines of code.

2. **Activate the 1E.10 wrapper at `reference_runner_v2.py:3510` with hardcoded `m_div = 1.0` (row 7).** Requires:
   - Locate every producer of `model_params` and confirm or patch the upstream `q` composition to `eta_int × (1 − c_ext × (1 − nu_k)) × d × p`, or equivalently emit `{eta_int, c_ext, nu_k, d, p}` as separate fields.
   - Update the `model_params` schema documentation to reflect the expanded field set.
   - Swap the call at line 3510 from `compute_rk(R_old, q, sk, nu_b, nu_f)` to `compute_rk_with_eta_channel(R_old, sk, eta_int, 1.0, c_ext, nu_k, d, p, nu_b, nu_f)`.
   - Run Exp 39 regression data through the wrapped path before Exp 40 launch (Gemini's R1 P-pass revision).
   - Flip `eta_int_modulator_wired_into_compute_rk: true` in `40_gate.json` only after the dry-run passes.

3. **Add a debug-mode `q`-composition assertion at line 3510 (row 8).** Under a `DEBUG_CHANNEL_CHECK` flag, assert `abs(q − eta_int * (1 − c_ext * (1 − nu_k)) * d * p) < 1e-9`. One line. Catches upstream composition drift regardless of wrapper state.

4. **Apply the closure-state stratification to ONBOARDING.md (row 20).** Document every Phase A/B closure as one of {library-complete, shadow-integrated, live-operational}. This is the ChatGPT-originated documentation rigour; no code change.

**Defer until Bench Run 2 or Exp 54 (fold-in-later, with annotation where relevant):**

- K/L/M live-promotion flip (row 9). Schedule for Bench Run 2 empirical calibration run.
- Cross-domain composability architecture (row 11). Record panel positions for Exp 54 design.
- Star-with-paired-challenge third topology (row 14). Exp 41 design input.
- 10-field reason-trace schema (row 24). Exp 54 attribution design.
- `nu_max` ceiling runtime enforcement (row 23). Post-hoc analysis for Exp 40; re-evaluate for runtime at Exp 54 once empirical `nu_max` distribution is known.

**Off-target — do not implement:**

- The four "v1 preservation" predicate families as acceptance gates (row 25). `40_gate.json` pass_condition is the sole gate.
- Continuous DCY formulation (row 17). Discrete `m_div` tiers are sufficient.
- The "v1 behavioural signature preservation" premise itself. Refuted.

**Expected post-fold-in state:**

- `40_gate.json`: `eta_int_modulator_wired_into_compute_rk: true`, otherwise unchanged.
- `reference_runner_v2.py`: line 3510 calls `compute_rk_with_eta_channel`; new debug assertion at adjacent line; upstream `model_params` producers emit decomposed Stage 6 parameters.
- `bench/immune_agents.py`: `_verify_sympy` sandbox uses allow-list `global_dict`; regression test passes.
- `resources/ONBOARDING.md`: closure states stratified.
- `docs/CURRENT_STATE.md`: regenerated by `cdsfl_sv.py` after the above.

**Not expected to change:**

- Topology label, pass_condition, max_rounds, earliest_stop_round — all retained as in `40_gate.json`.
- `LIVE_SPECIALIST_DOMAINS` — retained as `[mathematics, statistics, biology, information_science]`.
- The test article — retained as `bench/dm/_feedback.py`.

---

## 7. Outstanding discussion points for HIL

- **Schema decomposition scope.** Activating the wrapper requires upstream changes to every producer of `model_params`. The audit did not enumerate those producers (it confirmed only that line 3510 reads `q` as a scalar). Before applying row 2, the implementer should `grep -r "model_params" bench/` and confirm the upstream set. Decision: does the founder want the audit to extend that inventory before any code edit, or is that pre-edit checklist something the implementer owns?
- **Gemini RQ1b dissent.** Gemini's identity-function argument against wrapper activation is partially refuted in §3 item 3, but the refutation assumes the upstream `q` composition currently omits the `c_ext` term. If the empirical upstream check shows Gemini is right (composition already complete), the wrapper becomes a behaviourally cosmetic change — useful for surfacing `ChannelViolationError` on future `m_div` drift, but not load-bearing for Exp 40. Decision: is the founder satisfied with the CC2 R_k-discrepancy-feedback rationale as the primary justification, independent of the identity-function question?
- **Shadow-promotion-now scope for SymPy.** The shadow-promotion-now directive (20 April 2026) says "enable shadow elements and fix broken tools now; deferral costs more than activation given context-loss risk." Under that directive, row 6 is unambiguous. Decision: confirm the directive applies here, or carve out an exception?
- **Post-hoc `nu_max` computation triggering Exp 54 runtime guard.** If the post-hoc ceiling analysis on Exp 40 data shows the ceiling binding on more than some threshold fraction of findings, that is empirical evidence for reconsidering runtime enforcement. Decision: what threshold triggers the reconsideration — 5 percent, 10 percent, 25 percent?

---

## Appendix A. Raw confer artefacts

- `/tmp/exp40_audit/split/round1__{codex, gemini, chatgpt, cc2, deepseek}.txt` — Round 1 per-model outputs.
- `/tmp/exp40_audit/split/round2a__*.txt`, `round2b__*.txt`, `round3__*.txt`, `round3b__*.txt` — Rounds 2–3 outputs. Superseded for Exp 40 gating purposes by the re-confer.
- `bench/logs/confer_exp40_reaudit_round1/{codex, gemini, cc2, chatgpt, deepseek}_20260420T164144Z.json` — re-confer Round 1 under corrected framing.
- `bench/logs/confer_exp40_reaudit_round1/combined_20260420T164144Z.json` — combined re-confer log.

## Appendix B. Configuration and code anchors

- `bench/exp40_configs/40_gate.json` — Exp 40 pass_condition, topology, specialist cells, max_rounds, earliest_stop_round.
- `bench/reference_runner_v2.py:1064` — `_check_gamma_alt_convergence`.
- `bench/reference_runner_v2.py:3116` — `ChannelViolationError`.
- `bench/reference_runner_v2.py:3133` — bare `compute_rk`.
- `bench/reference_runner_v2.py:3177` — `compute_rk_with_eta_channel` wrapper (defined, not yet called).
- `bench/reference_runner_v2.py:3494-3497` — per-finding `model_params` access.
- `bench/reference_runner_v2.py:3510` — live `compute_rk` call site.
- `bench/immune_agents.py:947-1019` — `_verify_sympy` (sandbox regression).
- `bench/dm/_feedback.py` — Exp 40 test article, §17 feedback channel.
- `bench/reference_runner.py` — Exp 39 baseline (confirmed to contain none of the Stage 6 channel wrapper, `ChannelViolationError`, or γ-alt convergence identifiers).

