# CDSFL Full State Assessment

2026-07-02 15:10 BST · branch `exp39-experimental` · HEAD `6ed0adf` (clean, in sync with origin)

A complete state-of-the-project assessment, written after a roughly three-week pause in active work (11 June to 2 July 2026) and a full state recovery. It consolidates what the project has proven, what is built, what is dormant, what remains, and what gates the next step. It is written to stand alone: a reader with no session context should be able to reconstruct the project's position from this document plus the referenced records.

## 1. What the project is

CDSFL (Constraint-Driven Synthesis and Falsification Loop) is a methodology and working system for making AI-assisted technical work reliable. It formalises Popperian falsification — actively trying to disprove claims before accepting them — as a structured protocol executed by a five-model review panel (Claude Opus via CLI, Codex GPT-5.5, ChatGPT GPT-5.5, Gemini 3.1 Pro, DeepSeek V4 Pro) orchestrated by a reference runner (`bench/reference_runner_v2.py`, ~6,700 lines). The founding rule: **tools decide, not votes.** A critical claim must carry a runnable falsifier that imports the real target module; the runner independently re-runs it and the demonstrated result — never a model's prose assertion — settles the verdict. What tools cannot decide goes to a human (HIL, human-in-the-loop), and the system is engineered to keep that queue minimal and legitimate.

The mathematical core is a diminishing-returns model of defect discovery: cumulative novel findings follow a Duane-type decay curve, whose slope-derived measure **gamma** quantifies depletion of the finding space. Gamma is load-bearing and central — this is a standing, founder-issued directive (`.claude/CLAUDE.md`) after a recurring drift toward demoting it was identified and corrected.

## 2. The central scientific result: honest convergence, proven live twice

The project's core claim — that a multi-vendor falsification panel converges honestly on a bounded target — is now demonstrated on two experiments:

- **Exp 41** (target: the mathematics module `bench/dm/_convergence.py`) converged cleanly at round 6 on 23 May 2026 (22 canonical findings, no empties, no fallback routes).
- **Exp 42** (target: the directive composer `bench/cdsfl_registry/composer.py`, 60,416 chars) converged at round 6 on 9 June 2026 with **zero residual HIL** — 52 findings, 5 confirmed criticals, all resolved mechanically (commit `375236d`).

The road to the Exp 42 landmark peeled four distinct mechanical faults, each fixed and verified:
1. **Falsifier quality** — models produced findings with no runnable checks; fixed by the falsifier gate + per-model dispatch repairs (all five models now produce tool-testable falsifiers).
2. **False-REFUTED masking** — broken falsifiers exiting cleanly refuted real defects; fixed structurally by the CONFIRM-only gate (`0a4d8ce`): a critical is resolved only by a confirmed demonstration; REFUTED on a critical escalates, never drops.
3. **Weak-model dead-ends** — capability-aware routing (`bench/take_up_slack.py`): an unconfirmed critical is re-dispatched up a ladder of stronger falsifier-writers (Codex→CC2) before HIL; live-proven to eliminate a 15-finding HIL pile-up (0 HIL across 16 rounds).
4. **Cross-round dedup failure** — the convergence counter keyed novelty on model-chosen finding-ids, so re-found defects re-counted as new and the quiescence streak never formed; fixed by the **code-location novelty key** (`bench/convergence_location.py`): a critical is new only if it names a target-file AST symbol not previously flagged. The ID-proxy series never converges; the location-keyed series converges at round 6. A free-text-similarity alternative was tested and refuted (over-merges, falsely converges at round 2).

Throughout, every non-convergence proved **mechanical, not mathematical** — the founder's standing position, vindicated at each step. The maths model has never been shown wrong.

## 3. The convergence gate as it stands: the two-sided gate

Convergence is decided by a **two-sided gate** (founder ruling 2026-06-10, commit `71b190b`, `_check_gamma_alt_convergence`): the run converges if and only if **both** (1) `gamma_critical >= 0.30` — the critical-findings decay curve has flattened (gamma as an active condition, never "reported only") — **and** (2) three consecutive rounds produce zero new genuine criticals on the settled, location-keyed series. Both are readings of the same diminishing-returns curve and naturally agree; the count is typically the binding (later) side. Guards: the A4 fail-safe (an unverified critical blocks convergence and is logged for HIL), a small-irreducible-queue alarm (a large ladder-exhausted queue signals mechanical failure, refusing convergence), contested and churn checks.

Verified against both landmark runs via the actual estimator: exp41c critical series `[3,0,0,0,0,0,0]` → gamma_critical = **1.000**; exp42 `[10,1,5,1,0,0,0]` → **0.687**; both clear 0.30. (A recorded "0.240" for exp41c was the all-findings gamma — a different series, not the gate input; the confusion is documented so it cannot recur.) Tests: `bench/tests/test_two_sided_gate.py` + the rewritten `test_gamma_alt_convergence.py` (a stale test class whose name asserted the forbidden gamma demotion was renamed and corrected, `633b4c6`). The full 434-test convergence/runner sweep is green.

## 4. Component inventory — live, shadow, dormant (the honest map)

**Live (drives decisions):** falsifier gate (CONFIRM-only) + `execute_python` tool loop on all dispatch paths; capability-aware routing (`take_up_slack`, gated); location-keyed two-sided convergence gate; §17 feedback + §18 divergence directives; B-Cell specialists (mathematics, statistics, biology, information-science, software); G7 merge arbitration; static-queue closure + alarm.

**Built and tested but INERT pending one companion piece:** severity calibration (`050f17c`, 17 tests) — demotes a falsifier-CONFIRMED-real but explicitly latent critical below the 0.7 threshold (recording original severity + reason, never deleting; never demoting safety/core/security/data-loss categories). Inert by design until a **latent-tagger** writes `entry["latent"]` — nothing currently does; fail-safe when absent.

**Shadow (runs, logged, reaches no live decision):** macrophage cell (`bench/macrophage_cell.py` — anomaly patrol; its output flows only to shadow telemetry; a prior index error mis-tiered it live and mis-located it in `immune_agents.py`, both corrected 2026-06-10); Stage-6 calibrator (`dm/_shadow_stage6.py` — computes novelty/external-coverage estimates that are logged, never fed to the live equation); ouroboros research cell (functional — hard timeouts, OpenAlex/Semantic Scholar/Unpaywall chain, optional off-by-default Sci-Hub fallback citing originals only — but fetched literature reaches no model prompt: the loop-close is unbuilt).

**Dormant (never executed in the live arc):** the dm `LoadBalancer` (planning-time capability-aware task allocation — distinct from routing, not subsumed by it; keep for Bench Run 2 differential allocation); the dm `ConvergenceDetector`/`DiminishingReturnsDetector` stack (unreachable from the gate; a naive swap is empirically refuted — consolidation direction is runner→core extraction, Steps 2–6 gated on founder approval).

## 5. The experiment programme (Exp 40–54)

Each experiment targets one real artefact. Status: **Exp 40** (feedback directive `dm/_feedback.py`) — completed across a long arc; did not converge under early gates; produced the falsifier-quality lessons and the anti-cooking hardened-gate evidence. **Exp 41** (maths module) — converged. **Exp 42** (composer) — converged, the landmark. **Exp 43** (macrophage cell, `bench/macrophage_cell.py`, 22K chars, 15 AST symbols) — the **generalisation test**: does the location-keyed two-sided gate converge a second, different module, or was the composer special? Config `bench/exp43_configs/43_macrophage_locationkey_live.json` is written to the two-sided-gate semantics and pre-flight verified end-to-end (all gate flags survive into RunnerConfig; symbol extraction confirmed on raw source). **Exp 44–54**: composition test, statistics/divergence/information-science targets, four synthesised native STEM modules (biology/physics/chemistry/engineering, scope briefs locked), Stage-6 self-referential calibration, and the Exp 54 2×2 factorial integration. Bench Run 2 (27 frontier STEM problems) remains explicitly gated behind the arc.

## 6. What blocks the next step

- **Model API keys.** `.env` holds only `SEMANTIC_SCHOLAR_API_KEY`. The `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY` entries (per `docs/REPRODUCING.md:39-41`) are required for four of the five panel routes. This gates both the Exp 43 launch and the full five-model panel review. The June runs used keys exported in an interactive shell, invisible to non-interactive sessions — putting them in `.env` makes runs session-independent.
- **Vendor-side economics.** As of 1 July the premium Anthropic model tier is included only until 7 July, after which it moves to metered credits; separately, programmatic/CLI usage moved to its own credit meter on 15 June. Neither threatens the project's design — the panel's heavy lifting rides the founder's own API keys, and the driver-model dependency is deliberately minimal — but run costs should be checked against the current plan meter before long runs.
- **Founder decisions pending:** macrophage minimal-promote (wire a human-review flag on a high-severity anomaly) versus formally retire; load-balancer keep-dormant confirmation; dm consolidation go-ahead (Steps 2–6); rename of `take_up_slack` to `routing`.

## 7. The immediate path, in order

1. Keys into `.env` → launch Exp 43 under live monitoring (single command, recorded in the tracker resume pointer).
2. Fold the Exp 42 findings forward into the runner/project (staleness-checked individually — the target moved repeatedly during Exp 42's arc).
3. Builds, each closing only on an integration test: the latent-tagger (activates severity calibration), the ouroboros loop-close (fetched papers must reach model prompts and ground the external-coverage estimate), Stage-6 estimates into the live equation, dm consolidation Steps 2–6, the routing rename.
4. The directive-pruning panel: measurement shows the dispatched system directive is ~50K chars of which 43,667 (the operational directive) is appended unpruned outside the composer's prune path — today's pruner reaches only ~6%. A trim-to-~27K draft distinguishing load-bearing falsification machinery from prunable exposition awaits panel critique. (A long-standing "~60K directive" figure conflated the directive with the 60,416-char composer target article; corrected in the records.)

## 8. Where the records live

Master remediation plan: `experimental_notes/CDSFL_Remediation_Program_2026-06-09.md` (post-compaction block at top). Operational tracker: `~/Desktop/CDSFL_Agent_Operational_Plan.md` (canonical) + repo mirror, resume pointer current as of 2026-07-02. Latest session record: `experimental_notes/Overnight_Run_Report_2026-06-10.md`. Canonical state docs: `resources/ONBOARDING.md`, `resources/RECOVERY.md` (both current to 11 June, accurate as of this assessment). Landmark commits: `375236d` (Exp 42 convergence), `71b190b` (two-sided gate), `050f17c` (severity calibration), `1b5d148` (Exp 43 config), `6ed0adf` (state save). Test base: 1,596 collected; the 434-test runner/convergence sweep and the 62-test gate subset are green.

## 9. Bottom line

The project's central claim is demonstrated: a multi-vendor falsification panel, governed by a tools-decide gate and a two-sided diminishing-returns convergence criterion, converges honestly on real code targets with zero residual human escalations — twice, on different modules. The convergence instrument (location key + two-sided gate) now awaits its generalisation test on a third module, fully prepared and gated only on three API keys. The remaining work is enumerated, each item test-gated, none blocked on design unknowns. Every historical non-convergence traced to a mechanical fault, never to the mathematical model — which stands unrefuted.

Written under CDSFL note standard v1.2 (14 May 2026).
