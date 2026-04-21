# Consolidated Execution Plan — Experiments 40 through 54

**Date:** 2026-04-21 01:35 BST
**Source base:** [Exp40_to_54_Execution_Plan_2026-04-17.md](Exp40_to_54_Execution_Plan_2026-04-17.md) (403-line canonical plan, 17 April 2026)
**Integrates:** [Exp40_Pre_Launch_Panel_Audit_2026-04-20.md](Exp40_Pre_Launch_Panel_Audit_2026-04-20.md) (fold-in-now items F1–F4)
**Integrates (2026-04-21 panel round 1):** [Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md](Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md) (five material fold-ins, two documented-only)
**Standing policy:** shadow-promotion-now (memory: `feedback_shadow_promotion_now.md`, 2026-04-20, bounding condition added 2026-04-21 per panel RQ4)
**Branch:** `exp39-experimental`
**HEAD at plan creation:** `616ad43`

---

## 1. Purpose

This consolidation folds the 20 April pre-launch audit decisions into the 17 April execution plan and shows the 15-experiment arc (40 through 54) as a single forward path, with each experiment's lessons explicitly carried into the next. It does not replace the canonical plan; it supplements it with (a) the four fold-in-now items from the pre-launch audit, (b) per-experiment lessons-forward mapping, and (c) a single dispatch target for the final panel review round.

Every fix, decision, and gate in the canonical 17 April plan carries forward unchanged unless this document explicitly overrides it. Overrides are flagged inline.

---

## 2. Pre-launch fold-in-now items (apply before Exp 40 launches)

Four items were classified fold-in-now under the corrected-framing re-confer on 2026-04-20. The rationale column cites the panel convergence in `Exp40_Pre_Launch_Panel_Audit_Full_Report_2026-04-20.txt`.

### F1 — SymPy sandbox restoration
- **Site:** [bench/immune_agents.py:947-1019](../bench/immune_agents.py)
- **Change:** replace empty `global_dict={}` with allow-list (`Integer, Float, Rational, Symbol, Add, Mul, Pow, pi, E, oo, sqrt, Eq, Gt, Lt, Ge, Le, log, exp`). Keep `builtins={}`.
- **Tests:** (a) regression on `diff(x**2, x) == 2*x`; (b) RCE negative test — `__import__('os').system('id')` rejected.
- **Panel state:** 2-vs-3 split on timing (fold-in-now vs fold-after-Exp40). Shadow-promotion-now policy resolves: **fold-in-now**.
- **Status:** TODO

### F2 — Wrapper activation at compute_rk call site
- **Site:** [bench/reference_runner_v2.py:3510](../bench/reference_runner_v2.py)
- **Change:** swap bare `compute_rk(R_old, q, sk, nu_b, nu_f)` for `compute_rk_with_eta_channel(R_old, sk, eta_int, m_div=1.00, c_ext, nu_k, d, p, nu_b, nu_f)`.
- **Upstream prerequisite:** schema expansion — `entry["model_params"]` must carry `eta_int, c_ext, nu_k, d, p` (currently carries only `nu_b, nu_f, q, R`).
- **Verification gate:** Exp 39 regression through the wrapped path must reproduce prior R_k values within 1e-9 with `m_div=1.00`.
- **Config flip:** on regression pass, set `eta_int_modulator_wired_into_compute_rk=true` in [bench/exp40_configs/40_gate.json](../bench/exp40_configs/40_gate.json).
- **Override on canonical plan:** the 17 April plan deferred wrapper wiring to Exp 54. This consolidation pulls it forward to Exp 40 under shadow-promotion-now; Exp 54 inherits the wired state.
- **Status:** TODO

### F3 — Debug q-composition assertion
- **Site:** [bench/reference_runner_v2.py:3510](../bench/reference_runner_v2.py) (one line, under flag)
- **Change:** under `DEBUG_CHANNEL_CHECK` flag, assert `abs(q - eta_int*(1-c_ext*(1-nu_k))*d*p) < 1e-9`.
- **Purpose:** catch any silent m_div leakage into q during Exp 40 live run.
- **Lifecycle:** enabled for Exp 40; evaluate cost vs signal in post-mortem; keep or disable.
- **Status:** TODO

### F4 — Closure-state stratification (documentation)
- **Site:** [resources/ONBOARDING.md](../resources/ONBOARDING.md) — CDSFL schema index section
- **Change:** introduce three-state lexicon for every schema element:
  - `library_complete` — implementation landed, not yet wired
  - `shadow_integrated` — wired, logs-only, pipeline-neutral
  - `live_operational` — wired into dispatch or R_k, affects output
- **Apply to:** CC2 dispatch, §17 feedback, §18 divergence, specialist cells (math/stats/bio/info live; phys/chem/eng shadow), wrapper function, Stage 6 calibrator, Ouroboros.
- **Status:** TODO

---

## 3. Standing constraints (carried from 17 April plan Part "Standing constraints")

S1–S8 apply unchanged, with two overrides noted:
- **S3 override:** `eta_int_modulator` is wired into `compute_rk` from Exp 40 onward (F2). The original S3 deferred this to preserve baseline measurement; the pre-launch audit ruled the deferral subordinate to shadow-promotion-now.
- **S6 unchanged:** 2×2 factorial remains at Exp 54. §17 and §18 run live from Exp 40, but main-effect attribution needs all four factorial cells to compute, which is an Exp 54 study design, not a live-state change.

All other standing constraints (S1 v1 freeze, S2 Ouroboros runner evolution, S4 specialist cells live-promoted, S5 K/L/M shadow, S7 no preferred outcome, S8 commit at milestones) apply as written.

---

## 4. Per-experiment forward path

Format per experiment: **target, directive/cell state entering, carried-forward from prior, named risks, pass criteria**. Pass criteria follow the `40_gate.json` pattern unless stated: `γ ≥ 0.30 OR 3 consecutive rounds with 0 novel CRITICAL`; topology=star; max_rounds=8; earliest_stop=3.

### Exp 40 — Infrastructure Gate
- **Target:** [bench/dm/_feedback.py](../bench/dm/_feedback.py) (§17 module, ~22K)
- **State entering:** F1–F4 folded in; specialist cells math/stats/bio/info **live**; K/L/M **shadow**; §17 and §18 default-on; `eta_int_modulator` wired via F2
- **Carried-forward:** none (arc head)
- **Named risks:** parse yield under the new wrapper path; specialist cell sanity on first live run; first exercise of §17 admissibility parser on a running experiment (test count: 39 tests pass offline, zero live-run data)
- **Pass:** `γ ≥ 0.30 OR 3 consecutive rounds with 0 novel CRITICAL`; topology=star; max_rounds=8

### Exp 41 — Mathematics Specialist
- **Target:** [bench/dm/_convergence.py](../bench/dm/_convergence.py) or [bench/dm/_suppression.py](../bench/dm/_suppression.py)
- **State entering:** Exp 40 fixes folded; specialist live-mode validated against real findings
- **Carried-forward from Exp 40:** any P0 or P1 bug surfaced in infrastructure gate; §17 parse-yield lessons; R_k wrapper behaviour on live data
- **Named risks:** specialist over-routing (Exp 36 pattern — one agent was over-relied-upon); silence on non-mathematical claims; SymPy sandbox edge cases missed by F1 regression
- **Pass:** mathematics specialist verdict count > 0 on a SymPy-verifiable target claim; no specialist routing errors

### Exp 42 — Expert Encodings S_k
- **Target:** [bench/cdsfl_registry/composer.py](../bench/cdsfl_registry/composer.py)
- **State entering:** mathematics-specialist calibration from Exp 41 applied
- **Carried-forward:** Exp 40–41 bugs; mathematics specialist thresholds
- **Named risks:** S_k format mismatch across vendor encodings; composer-emitted finding IDs triggering parser false-positives
- **Pass:** S_k ADMISSIBLE rate > 0 across all panel vendors on encoded-fix targets

### Exp 43 — Macrophage Admissibility
- **Target:** [bench/immune_agents.py](../bench/immune_agents.py) macrophage subsection (bounded unit, ~20K)
- **State entering:** Macrophage verdict wiring fix (Item 1B.1 from canonical plan) confirmed on synthetic data
- **Carried-forward:** 40–42 lessons; AUTOIMMUNE_REJECTION vs DEPLETION_EXPECTED split (Item 1C.1)
- **Named risks:** false autoimmune flags in late rounds; verdict wiring regression under live load
- **Pass:** non-zero Macrophage observations across ≥ 3 rounds; AUTOIMMUNE_REJECTION fires only on content-rejection, not duplicate-rejection

### Exp 44 — Composition Test
- **Target:** synthetic composition of 41+42+43 outputs (mechanical interface check, no new target article)
- **State entering:** three specialist-or-cell modules live-validated
- **Carried-forward:** all prior fixes; all specialist calibrations
- **Named risks:** interface mismatch between math specialist, composer, and Macrophage; shared state pollution
- **Pass:** composed outputs pass type checks; convergence signal on synthetic data

### Exp 45 — Statistics Specialist
- **Target:** [bench/dm/_memory.py](../bench/dm/_memory.py) (beta-binomial memory, CUSUM drift)
- **State entering:** composition lessons from 44
- **Carried-forward:** prior; statistics specialist scipy.stats routing
- **Named risks:** CUSUM threshold miscalibration; statistics specialist confusing point-estimate claims with distributional claims
- **Pass:** statistics specialist verdict count > 0 on distributional target claim

### Exp 46 — CS/Software Specialist
- **Target:** [bench/dm/_divergence.py](../bench/dm/_divergence.py) (§18 module, ~20K)
- **State entering:** §18 live since Exp 40; first time §18 module is also the test article
- **Carried-forward:** prior; any §18 divergence-directive issues surfaced in 40–45
- **Named risks:** self-referential confound (the module being tested IS the directive mechanism); recidivism detection self-loop
- **Pass:** convergence; recidivism detection (Item 1E.9) confirmed; no circular attribution

### Exp 47 — Biology Specialist
- **Target:** synthesised minimal native biology module (15–25K chars, purpose-built) — committed 2026-04-21 from panel RQ6 consensus (5 of 5 panel members judged no suitable native biology module exists in the codebase; synthesis preferred over adapter layer to preserve Stage 6 orthogonality between `c_ext` search-quality and target-module validity). Target construction is an Exp 40 post-mortem action item, pre-Exp-47 completion; it is not an Exp 40 launch blocker.
- **State entering:** prior lessons applied
- **Carried-forward:** prior; biology specialist biopython routing
- **Named risks:** target domain fit (synthesised module must contain falsifiable biological claims amenable to biopython verification); specialist silence if synthesised content leans on metaphor rather than mechanism
- **Pass:** biology specialist verdict count > 0 on a native biology claim embedded in the synthesised target; synthesis justified against Part 3 selection criteria

### Exp 48 — Information Science
- **Target:** [bench/evidence.py](../bench/evidence.py) (641 LOC, ~23K, confirmed right-sized)
- **State entering:** prior lessons applied
- **Carried-forward:** prior
- **Named risks:** information science specialist overlap with mathematics specialist on probabilistic claims; evidence module self-test artefacts
- **Pass:** information science specialist verdict count > 0; no specialist-to-specialist routing conflict

### Exp 49 — Cross-domain Synthesis
- **Target:** synthetic integration of 41+45+46 outputs (mathematics + statistics + CS)
- **State entering:** three live specialists calibrated
- **Carried-forward:** all prior; cross-specialist routing thresholds
- **Named risks:** integration emits contradictions under competing specialist verdicts; Macrophage unable to arbitrate multi-specialist disagreement
- **Pass:** integration without unresolvable contradiction; convergence signal
- **Post-Exp-49 reorder review (added 2026-04-21 from panel RQ5 carried alternatives):** if cross-domain synthesis at Exp 49 surfaces specialist tier inconsistencies, revisit three reordering proposals raised in the 21 April panel before committing to the original Exp 50–53 sequence: (a) Gemini — move §18 target (Exp 46) earlier in the arc; (b) ChatGPT — swap Exp 46 and Exp 48 (information-science-before-CS); (c) DeepSeek — promote Exp 45 (statistics) adjacent to Exp 41. Two of five panel members (Codex, CC2) defended the current ordering as dependency-optimal; the three YES votes diverged on specific reordering, producing no consensus alternative. Default on no tier-inconsistency signal: retain current ordering. Decision (retain or reorder) is recorded in the Exp 49 post-mortem.

### Exp 50 — Microglia
- **Target:** [bench/dm/_shadow_stage6.py](../bench/dm/_shadow_stage6.py) (self-referential calibration module)
- **State entering:** prior lessons; Stage 6 calibrator shadow-log audit fix (Item 2.3) applied
- **Carried-forward:** prior; Ouroboros query-quality fix (Item 1E.8) as prerequisite
- **Named risks:** calibrator inputs garbage-in-garbage-out if Ouroboros query quality regressed; self-referential feedback loop
- **Pass:** calibrator produces `(ν_k_proxy, c_ext, H_ratio)` triples with ≥ 2 distinct values across rounds

### Exp 51 — Physics Shadow (still shadow mode; live-promotion gated on data plus non-distortion check per §6)
- **Target:** [bench/cdsfl_registry/composer.py](../bench/cdsfl_registry/composer.py) **conditional** — DeepSeek's RQ6 candidate (minority-of-one in panel, citing existing unit/dimensional content). Gate: verify that composer.py contains physics-relevant dimensional material of sufficient density to exercise the K shadow cell. If insufficient, fall back to synthesised minimal native physics module (15–25K chars, purpose-built), matching the default path used for Exp 47/52/53 per panel RQ6 majority.
- **State entering:** prior; K shadow built functional per Item 1E.4
- **Carried-forward:** prior; pint + astropy.units dimensional-analysis routing
- **Named risks:** shadow verdict noise; false dimensional-analysis alarms on code-only claims; composer.py content density below threshold for meaningful K-shadow exercise (triggers synthesis fallback)
- **Pass:** physics shadow logs verdicts without affecting pipeline; verdict rate within expected range (tentatively 0.1 to 0.5 per finding for physics-tagged claims)

### Exp 52 — Chemistry Shadow
- **Target:** synthesised minimal native chemistry module (15–25K chars, purpose-built) — committed 2026-04-21 from panel RQ6 consensus (5 of 5 panel members judged no suitable native chemistry module exists; synthesis preferred over adapter layer under Stage 6 orthogonality)
- **State entering:** prior; L shadow built functional per Item 1E.4
- **Carried-forward:** prior; rdkit stoichiometry routing
- **Named risks:** synthesised SMILES content must exercise the rdkit parse + stoichiometry path without triggering noise on valid molecules; chemistry shadow silent on non-molecular claims (baseline)
- **Pass:** chemistry shadow logs verdicts; SMILES validity gate fires appropriately

### Exp 53 — Engineering Shadow
- **Target:** synthesised minimal native engineering module (15–25K chars, purpose-built) — committed 2026-04-21 from panel RQ6 consensus (5 of 5 panel members judged no suitable native engineering module exists; synthesis preferred over adapter layer under Stage 6 orthogonality)
- **State entering:** prior; M shadow built functional per Item 1E.4
- **Carried-forward:** prior; safety-factor calculation routing
- **Named risks:** synthesised content must embed falsifiable engineering claims (load factors, material tolerances) that exercise the safety-factor routing path; false positives without structural context remain a baseline concern
- **Pass:** engineering shadow logs verdicts

### Exp 54 — Integration run with 2×2 factorial
- **Target:** TBC — candidate: `bench/reference_runner_v2.py` itself (runner tests runner; meta-test)
- **Configuration:** four factorial cells:
  - Cell A: Exp 36–38 baseline archive (§17 off, §18 off), subject to the three-layer integrity strategy below
  - Cell B: §17 on, §18 off
  - Cell C: §17 off, §18 on
  - Cell D: both on (current state from Exp 40 onward)
- **State entering:** all 40–53 fixes folded; `eta_int_modulator` already wired live since Exp 40 via F2; all admissibility, severity, and tier thresholds **frozen** per Gate C threshold-freeze (added 2026-04-21 from panel RQ2); frozen thresholds applied identically across Cells A/B/C/D
- **Carried-forward:** all lessons from the 14-experiment arc
- **Named risks:** factorial attribution confounded if §17 and §18 have been co-live for 14 prior experiments (tier calibration already settled — mitigated by threshold-freeze above); Cell A data quality — not merely archive integrity but also confound-by-runner-evolution (Gemini's RQ3 minority position, 21 April panel)
- **Cell A integrity strategy (three layers, added 2026-04-21 from panel RQ3):**
  1. **Primary:** archive integrity check at Gate C — γ trajectory from the Exp 36–38 archive must reproduce within tolerance when replayed through the Exp 54 runner configuration with §17/§18 both off.
  2. **Fallback 1 (Gemini's RQ3 proposal):** if integrity fails, execute a fresh Cell A run at the Exp 54 codebase with §17 and §18 both off. This replaces the archived Cell A and sacrifices the Exp 36–38 archive value in exchange for runner-version comparability across all four cells.
  3. **Fallback 2 (DeepSeek's RQ3 proposal):** if both above fail, perform a sensitivity analysis bounding §17 and §18 main effects via Cell B and Cell C early-round data as an ad-hoc baseline. Report interaction term only and flag main effects as confounded rather than estimated.
- **Pass:** all four cells complete under frozen thresholds; attribution statistics computed via two-way ANOVA or equivalent GLM; standard contrasts — §17 main = (B + D)/2 − (A + C)/2; §18 main = (C + D)/2 − (A + B)/2; interaction = (D − C) − (B − A) — within declared confidence interval; schema coherence verified across cells

---

## 5. Gate criteria between experiments (carried from 17 April plan Part 5, unchanged)

- **Gate A — runner clean:** unit tests pass; `ruff` and `mypy` clean; post-mortem written and in `experimental_notes/`; all new bugs classified 1A/1B/1C
- **Gate B — lessons folded:** every P0 and P1 from Exp N folded into `reference_runner_v2.py` before Exp N+1 launches; P2 may defer one experiment
- **Gate C — target ready:** target article under 80,000 characters (`LENGTH_THRESHOLD`); config lint-clean against `cdsfl_registry/schema.toml`; launch script `--dry-run` and `--preflight` pass
  - **Gate C preflight (Exp 40 launch, added 2026-04-21 from panel RQ1):** live-path preflight for the §17 admissibility parser on `bench/dm/_feedback.py` — verify live parsing behaviour matches the offline-tested behaviour before first live dispatch. Downgraded from a new fix-item (F5) to a pre-launch verification step after the panel converged on "F1–F4 sufficient" for the 40_gate.json pass_condition.
  - **Gate C threshold-freeze (Exp 54 launch, added 2026-04-21 from panel RQ2):** freeze admissibility, severity, and tier thresholds before Exp 54 launches; apply identical frozen thresholds across all four factorial cells A/B/C/D. Purpose: prevent calibration drift learned under co-live §17+§18 (during Exp 40–53) from contaminating single-channel main-effect attribution at cells B and C.
- **Gate D — founder sign-off:** post-mortem reviewed; any scope change approved; fail-fast DAG verified

---

## 6. Shadow-promotion-now policy applied across the arc

Per `feedback_shadow_promotion_now.md` (2026-04-20): activate shadow elements now unless demonstrably harmful; deferral risk (context loss) outweighs activation risk (measurable as noise).

**Bounding condition (added 2026-04-21 from panel RQ4 consensus; 3 of 5 panel members proposed it, the other 2 affirmed unconditional safety — the stricter reading is adopted):** the policy is *conditionally* safe. Each promoted component must pass a non-distortion check against the `40_gate.json` pass_condition before live activation. Specifically, the promoted component must not silently alter the "γ ≥ 0.30 OR 3 consecutive rounds with 0 novel CRITICAL findings" clause through unintended channel coupling, tier drift, or suppressed signal. F2 satisfies the bounding condition via its 1e-9 regression gate on the wrapped `compute_rk` path (measured against Exp 39 baseline with `m_div=1.00`). K/L/M shadow specialists require equivalent non-distortion evidence before their post-Exp-53 live promotion — specifically, their shadow-round logs must show no case where their verdict would have changed the `40_gate.json` pass_condition outcome if applied live.

Applied to 40–54 arc:
- F1–F4 fold in pre-launch (Exp 40)
- Specialist cells math/stats/bio/info: **live from Exp 40** (confirmed per canonical S4)
- Specialist cells K/L/M (physics/chemistry/engineering): **shadow through Exp 50**; promotion to live evaluated at Exp 51–53 based on shadow-log evidence *plus* the non-distortion check above
- `eta_int_modulator` wiring into `compute_rk`: **flipped live at Exp 40 via F2** (overrides canonical S3 Exp-54 deferral; F2's 1e-9 regression gate satisfies the bounding condition)
- 2×2 factorial: **stays at Exp 54** — this is a study-design decision, not a deferral (needs post-hoc cell A reconstruction from Exp 36–38 archives under the three-layer integrity strategy in §4 Exp 54)

---

## 7. Risk carry forward

Risks identified across the arc that need explicit monitoring:
- **Specialist routing imbalance** (Exp 36 pattern: 3 of 4 specialist agents under-routed, 1 over-relied-upon). Track per-specialist verdict counts across 40–54; re-calibrate thresholds at Exp 49 (cross-domain synthesis) if imbalance persists.
- **Long-session degradation** (18h+ sessions cause term conflation). Commit at every Gate A checkpoint; fresh starts safer than contaminated continuations.
- **Framing confound** (v1 preservation framing rejected 2026-04-20). Every dispatch to the panel under 40_gate.json + Stage 6 orthogonality framing; reject v1 preservation as a design axis.
- **Narrow focus** (system-level signals first, then drill down). Aggregate metrics computed before per-specialist analysis in every post-mortem.
- **Factorial attribution contamination at Exp 54** (§17 and §18 co-live for 14 experiments). Cell A archive integrity is load-bearing; if archive is corrupted, factorial collapses to §17×§18 interaction-only without main effects.

---

## 8. Open questions for the final panel review round

**Round 1 status (2026-04-21):** DISPATCHED and CLOSED. Outcome captured in [Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md](Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md). Five material fold-ins applied to this document (RQ1 Gate C preflight, RQ2 threshold-freeze, RQ3 three-layer Cell A integrity strategy, RQ4 shadow-promotion bounding condition, RQ6 synthesis commitment for Exp 47/52/53 with conditional on Exp 51). Two items documented-only (RQ1 speculative DeepSeek additions; RQ5 three incompatible reordering proposals retained as post-Exp-49 watch items). No second round required.

Dispatch constraints (for reference, in case a second round is triggered by Exp 40 or Exp 49 post-mortem): five-model panel (CC2 Opus 4.6, Codex GPT-5.4, Gemini 3.1 Pro, ChatGPT GPT-5.4, DeepSeek R1); star topology with CC1 as hub; full CDSFL + FFAFP system prompt; framing anchored in `40_gate.json` + Stage 6 orthogonality (not v1 preservation); one round unless genuine split.

**Scope guardrail:** the panel is asked to find what breaks within the 40 → 54 arc. Proposals for Exp 55 and beyond are out of scope for this round.

### Questions

1. With F1–F4 folded in pre-launch, does the `40_gate.json` configuration leave any fix unaddressed that would invalidate Exp 40 data?
2. Does the lessons-forward sequence (40 → 41 → ... → 53) miss any cross-experiment interaction that would undercut the Exp 54 integration run?
3. Does the Exp 54 2×2 factorial produce attribution statistics sufficient to separate §17 main effect, §18 main effect, and interaction, given that §17 and §18 have been co-live since Exp 40?
4. Does shadow-promotion-now create any risk in the arc (premature calibration; uncontrolled variable interaction; information leakage from shadow to live specialists) that outweighs the context-loss risk the policy was adopted to prevent?
5. Is there any ordering of Exp 41–53 that would reduce risk without changing the target set?
6. For Exp 47, 51, 52, 53 (targets TBC), does the panel see a native codebase candidate that meets the Part 3 selection criteria without requiring a synthetic target construction?

### Panel output format requested

Per-question, per-model: DIRECT ANSWER (1–3 sentences), RATIONALE (concrete file/constraint references), NOVEL FINDING (if any — flagged as such, with falsifier if speculative), TIER (P0/P1/P2/noop if a change is proposed).

---

## 9. Plan maintenance

This consolidated plan supersedes none of the canonical artefacts. It is a dispatch surface for the final review round and a readable arc summary. Status updates land in the canonical `Exp40_to_54_Execution_Plan_2026-04-17.md`; this document is refreshed only if the panel review produces material new findings, which would be folded into both documents.

If the panel identifies a fix unaddressed by F1–F4, it enters Part 1 of the canonical plan (classified 1A/1B/1C per the canonical classification rules) and this document's §2 is updated to cite it.

---

## Appendix A — canonical file layout

| Artefact | Path |
|---|---|
| Experiment 39 runner (frozen) | `bench/reference_runner.py` |
| Experiment 40+ runner (evolves) | `bench/reference_runner_v2.py` |
| Experiment 40 launcher | `bench/launch_exp40.py` |
| Experiment N launcher (N ≥ 40) | `bench/launch_exp{N}.py` |
| Experiment N config | `bench/exp{N}_configs/*.json` |
| Experiment N logs | `bench/logs/exp{N}_*/` |
| Experiment N post-mortem (repo) | `experimental_notes/Exp{N}_PostMortem_{DATE}.md` |
| Experiment N post-mortem (TTS) | `~/Desktop/CDSFL_tts/Exp{N}_PostMortem_{DATE}.txt` |
| Canonical execution plan | `experimental_notes/Exp40_to_54_Execution_Plan_2026-04-17.md` |
| This consolidated plan | `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` |
| Plain-English companion | `~/Desktop/CDSFL_tts/Exp40_to_54_Consolidated_Plan_2026-04-21.txt` |
| Pre-launch panel audit (short) | `experimental_notes/Exp40_Pre_Launch_Panel_Audit_2026-04-20.md` |
| Pre-launch panel audit (full) | `~/Desktop/CDSFL_tts/Exp40_Pre_Launch_Panel_Audit_Full_Report_2026-04-20.txt` |
| Plan review round 1 outcome (technical) | `experimental_notes/Exp40_to_54_Plan_Review_Panel_Round1_Outcome_2026-04-21.md` |
| Plan review round 1 companion (TTS) | `~/Desktop/CDSFL_tts/Exp40_to_54_Plan_Review_Panel_Round1_Plain_English_2026-04-21.txt` |
| Plan review round 1 dispatch script | `bench/confer_exp40to54_consolidated_plan_review_2026-04-21.py` |
| Plan review round 1 raw responses | `bench/logs/confer_exp40to54_consolidated_plan_review_2026-04-21/` |

## Appendix B — 40_gate.json pass condition reference

From [bench/exp40_configs/40_gate.json](../bench/exp40_configs/40_gate.json) (current state on branch `exp39-experimental`):

```
gamma_threshold: 0.30
consecutive_zero_novel_critical_rounds_for_pass: 3
topology: star
max_rounds: 8
earliest_stop_round: 3
eta_int_modulator_wired_into_compute_rk: false  # flipped true by F2
```

F2 flips the last field to `true` after Exp 39 regression through the wrapped path succeeds.
