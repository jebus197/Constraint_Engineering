# CDSFL Remediation Program — master todo from the 2026-06-08/09 session

2026-06-09 BST · branch `exp39-experimental` · owner CC1 (Opus 4.8)

**Read this FIRST on any compaction.** It is the complete, verification-anchored program to
"test and fix everything discussed this session + the neglected (shadow/dormant) elements," so
that every CDSFL subsystem works **as intended and as originally envisaged**. Every item names
its **verification** (how we KNOW it works — integration test, not just unit), because the
session's defining lesson is *unit-green / integration-dead* (the location-key bug below).

---

## A. DONE + verified this session

| # | Item | Verification |
|---|------|-------------|
| A1 | Convergence root cause = cross-round dedup keyed on model-chosen id | signature trace + adversarial panel wf_88bbdd46 |
| A2 | Fix = code-LOCATION novelty key | real gate `_check_gamma_alt_convergence`: ID-proxy never converges, location-key → R6 |
| A3 | `bench/convergence_location.py` + 12 tests (incl. Exp-42 pin, calibration, real-gate characterisation) | pytest green |
| A4 | Location-key wired to the live gate (`location_keyed_convergence` flag) | live log `[location-key] 30 symbols … =True` |
| A5 | **Silent-failure bug** in the wiring (symbols read from wrapped `full_code` → 0 → swallowed) | FOUND via cy, FIXED (raw `target_text` + loud warn), live-verified |
| A6 | Static-queue closure + small-queue ALARM | `test_static_queue_closure.py` 2 tests; small queue converges, large alarms |
| A7 | Ouroboros made functional: hard timeout + OpenAlex fallback | probe 95.7s→21s, OpenAlex 1.5s; 12 ouroboros tests pass |
| A8 | Unpaywall reality-checked | 4/6 OA, 4/4 PDFs HTTP-200 (Sci-Hub justified for the ~⅓ gap) |
| A9 | Stale structural test fixed (was NOT a regression); pytest.ini global timeout + `network` marker | suite no longer hangs for hours |
| A10 | gamma reconciliation (no demotion; count = threshold-free reading of the same decay curve's critical endpoint; dedup fix cleans gamma too) | numbers + founder agreement |

## B. Shadow / dormant inventory (survey wf_25fab8a8, adversarially verified) + required action

| Subsystem | Status | Action to make it real | Verification gate |
|---|---|---|---|
| **Ouroboros** | SHADOW — papers reach no model | Close the loop: inject fetched literature into `_build_prompt` next-round; full-text chain Unpaywall→Sci-Hub (cite original), feed real (ν_k,c_ext) | integration test: a model prompt contains a fetched abstract AND c_ext derives from it, not self-report |
| **Stage 6 calibrator** | SHADOW — (ν_k,c_ext) only logged | Feed its estimates into the live `q=η·d·p` (replace hardcoded c_ext=0) | a live run where c_ext≠0 changes a verdict/score |
| **Macrophage** | SHADOW — `pipeline_modified=False` hard-set | DECIDE: promote (anomaly→re-exam/HIL flag) or formally retire. Founder call | if promoted: an anomaly pauses/redirects a round |
| **dm load-balancer** | DORMANT — never imported | DECIDE: wire (capability-aware allocation) or delete. The "load balancing at scale" claim depends on it | a run where allocation differs by model capability |
| **severity calibration** | DORMANT — NEVER BUILT | Build: lower an over-rated-but-real finding's severity without discarding (over-production bound) | unit + replay exercising the demotion path |
| **directive pruning** | PARTIAL — prunes only ~10% of payload; 44K operational directive appended UNPRUNED | **PANEL REVIEW (pr): what must the pruned operational directive retain to stay fully effective without compromising CDSFL integrity?** then prune + lean-vs-full ablation | ablation: lean directive ≥ full on a fixed task |
| **specialist science-tools** | PARTIAL — rdkit/biopython/sympy never fire (all live exps domain=software) | Verify routing fires for a non-software domain (the macrophage/bio experiment) | a bio finding routes to biopython and uses output |
| **dm convergence/diminishing detectors** | PARTIAL — runner uses inline; detectors unused | DECIDE: consolidate onto dm (Strangler-Fig) or delete the dormant copies | one source of truth; replay-diff identical |
| **insect_brain check_convergence/signal_complete** | PARTIAL — cosmetic | confirm relay is the only live role; mark the cosmetic methods | no behaviour depends on the cosmetic methods |
| execute_python loop, G7 merge-arbitration | **LIVE** ✓ | none | already consumer-reaching |

## C. Convergence completion

- C1 — **live Exp 42 confirmation run** (location-key + static-queue + routing + gate ON) — RUNNING (`exp42_composer_locationkey_live_20260609T165146Z` relaunch `b4i21mlyn`). Landmark = converges ~R5-7, 0 residual HIL. Then **commit** (the next commit is the landmark, per founder).
- C2 — promote routing + location-key to the default path + other experiment configs once C1 confirms.

## D. Cross-cutting

- D1 — Semantic Scholar key: pending since 26 Mar, never wired; NOT a blocker (OpenAlex covers). Founder may add `SEMANTIC_SCHOLAR_API_KEY` to `.env`.
- D2 — A real contact email for OpenAlex/Unpaywall/Crossref polite pool (replace placeholder).
- D3 — Standing "reaches-consumer" discipline: no component is "done" until an integration test proves its output changes a real decision (the anti-shadow-drift rule).

## E. Verification policy (the lesson)

Unit-green is not done. Each B/C item closes only when an **integration test** shows its output
reaches and changes a live decision. Panel review (pr: cc2,cx,ge,cgpt,ds) for design-uncertain
items (directive pruning; macrophage/load-balancer promote-vs-retire). cy monitoring on every run.

---
## ★★ POST-COMPACTION: READ THIS FIRST ★★ (2026-06-10)

**GAMMA IS RESTORED AND LOAD-BEARING. Do NOT demote it.** Standing directive now in
`.claude/CLAUDE.md` (§ "GAMMA IS LOAD-BEARING"). Convergence is a **TWO-SIDED GATE**:
`gamma_critical >= gamma_alt_threshold` (0.30, decay curve flattened) **AND** 3 consecutive
zero-new-critical rounds (the strict insurance endpoint). BOTH must agree. Implemented in
`_check_gamma_alt_convergence` (`reference_runner_v2.py`), tests `bench/tests/test_two_sided_gate.py`.
Verified on the 9 June live run: both held first at round 6 (gamma_critical 0.607 >= 0.30, count
[0,0,0]) — identical to the count-only result; gamma worked, depletion was reachable. The founder's
"two sides of the same coin" was correct. Faults are MECHANICAL, never the model.

**OVERNIGHT 2026-06-10 PROGRESS (detail in the status log). DONE + pushed:** gamma-test regression
fixed (`633b4c6` — the two-sided gate had left 3 tests red; both landmarks tool-verified clearing the
0.30 gate: exp41c gamma_critical=1.0, exp42=0.69); **severity calibration BUILT + 17 tests** (`050f17c`,
gated default-off, byte-identical-off, INERT without a latent-tagger — fail-safe); **Exp 43 macrophage
config built + ALL pre-flight checks verified** (`1b5d148`). **BLOCKED tonight:** the live Exp 43 run AND
the full `pr` panel — no model API keys in `.env` (only SEMANTIC_SCHOLAR) + codex CLI rate-limited to
11 June. Investigations complete (severity spec, directive measurement+correction, macrophage/
load-balancer/dm decisions). The 7-June "demoting gamma was CORRECT" line is SUPERSEDED.

**Immediate next tasks (in order), each integration-test-gated:**
1. **ADD MODEL KEYS** to `.env` (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`; see
   `docs/REPRODUCING.md:39-41`) → **launch the Exp 43 generalisation run**:
   `python3 bench/launch_exp42.py --config "$(pwd)/bench/exp43_configs/43_macrophage_locationkey_live.json"`
   → cy-monitor → does the location-keyed two-sided gate GENERALISE to a 2nd module? (config + wiring
   already verified: 15 symbols extracted from source, all gate flags survive into RunnerConfig.)
2. **`sy` + `f` the Exp 42 findings** (this run + earlier — CAREFUL: moving target). Fold forward.
3. Remaining shadow/dormant builds: the latent-tagger that makes severity calibration LIVE; ouroboros
   loop-close; Stage-6→live equation; dm consolidation (Step 0 DONE = gamma-test pin; Steps 2-6 behind
   `go`); directive-pruning EXECUTION (run the full `pr` panel first — deferred on keys/quota).
4. **DECISIONS for founder (investigated tonight):** macrophage = retire-as-cosmetic OR minimal-promote
   (HIL-flag on a high-severity anomaly — it runs but reaches no live decision); load-balancer = KEEP
   dormant (DISTINCT from take_up_slack, NOT subsumed; wire only for Bench-Run-2 differential
   allocation); routing rename (take_up_slack→routing). **Matrix CORRECTED:** Exp 43 target is
   `bench/macrophage_cell.py` (the "immune_agents.py macrophage section" pointer was WRONG — 0
   macrophage code there).

## Experiment programme — what each experiment STUDIES (documentation gap, flagged by founder 2026-06-10)

CDSFL is being validated by breaking the schema into per-experiment chunks, each targeting a real
software/STEM artefact. **The notes have NOT been recording what each studies — fix this in every
future note so the work is reproducible.** Known so far: **Exp 41 = the maths model** (`dm/_convergence.py`);
**Exp 42 = the composer** (`bench/cdsfl_registry/composer.py` — the four-layer directive assembler,
domain=software); **Exp 43 = the macrophage cell** (slated). Full per-experiment target matrix lives
in `experimental_notes/CDSFL_Agent_Operational_Plan.md` (Exp 40–54). **OPEN DECISION (founder):** if
the Exp 43 macrophage target is large, pick a SMALLER outstanding-experiment target and rebadge it
Exp 43 (and vice-versa) so we surface problems faster — review the target sizes before launching.
NOTE: the operational plan's "demoting gamma was CORRECT" line (7 June) is **SUPERSEDED** by the
two-sided-gate ruling above.

Status log (append-only):
- 2026-06-10 ~01:00–04:00 BST — **OVERNIGHT AUTONOMOUS RUN (founder asleep, reviews in AM; rs done).**
  Goal: build/test the outstanding items + the Exp 43 generalisation test. Architecture: 4 parallel
  read-only investigation sub-agents (protect main context), I verify + apply + commit each. **WORK
  BANKED (all pushed to exp39-experimental):**
  - **`633b4c6` — fixed my own regression.** The two-sided-gate commit (`71b190b`) changed
    `_check_gamma_alt_convergence` reason strings but left 3 tests red in `test_gamma_alt_convergence.py`
    (committed with a red suite — surfaced independently by 2 investigations). Rewrote them to the TRUE
    two-sided semantics: `TestGammaIsReportedNeverTriggers` (a name asserting the very demotion the
    directive forbids) → `TestLegacyGammaParamIsInert` + NEW `TestGammaCriticalIsActiveCondition`
    (gamma_critical<θ BLOCKS even with a zero tail). **HARD-constraint check (gate must break NEITHER
    landmark), tool-verified via `_estimate_gamma`: exp41c [3,0,0,0,0,0,0]→gamma_critical=1.000;
    exp42 [10,1,5,1,0,0,0]→0.687; both ≥0.30.** The "0.240" in the record was the ALL-FINDINGS gamma,
    NOT the gate input. The count is the binding side; gamma is the early-flattening curve — they agree.
  - **`050f17c` — severity calibration BUILT (T6, NEVER-BUILT gap closed).** Gated
    `severity_calibration_enabled` (default off, byte-identical). Demotes a falsifier-CONFIRMED-real BUT
    explicitly-latent critical below 0.7 (recording original+reason, never deleting), so it stops
    re-blocking convergence; NEVER demotes safety/core/security/data_loss. 17 tests + 72 convergence/gate
    tests green. **HONEST: inert until a latent-tagger sets `entry["latent"]` — the verified building
    block, not yet live.**
  - **`1b5d148` — Exp 43 macrophage config, pre-flight VERIFIED.** Target `bench/macrophage_cell.py`
    (22K, 15 symbols, self-contained). All gate flags survive launcher→RunnerConfig; `target_symbols(raw
    source)=15` (the silent-0-symbol bug pre-empted). Pre-registration written to the two-sided semantics.
  - **BLOCKED:** the live Exp 43 run + the full `pr` panel — `.env` has only SEMANTIC_SCHOLAR_API_KEY;
    Codex/ChatGPT/Gemini/DeepSeek need keys (exp42 used shell-exported ones, not visible to non-interactive
    tools); codex CLI hit its usage limit (resets 11 June). Not launched (a keyless run fails at round 0).
  - **INVESTIGATIONS (4 sub-agents, file:line-referenced):** (a) **severity** — spec applied above;
    (b) **directive measurement — CORRECTION:** the "~60K directive" is a CONFLATION — 60,416 chars is the
    TARGET ARTICLE (composer.py in the USER prompt), NOT the directive. The real dispatched system directive
    is ~50K, of which 43,667 (`cdsfl_operational.md`, 18 §) is appended UNPRUNED at `reference_runner_v2.py:2932`
    OUTSIDE the prune path; the composer pruner reaches only ~6% (the domain packet). Full §-by-§ breakdown +
    a draft pruning recommendation (trim to ~27K) produced — the `pr` panel on it is DEFERRED (keys/quota);
    a local P-pass stands in. (c) **macrophage** — only in `bench/macrophage_cell.py` (immune_agents.py has
    0 macrophage code → matrix pointer WRONG); wired into the runner (L3438/3544) but reaches NO live decision
    (shadow→shadow via ouroboros). DECISION: retire-as-cosmetic OR minimal-promote (HIL-flag on a ≥0.9 anomaly).
    (d) **load-balancer** — `dm/_load_balancer.py`, dormant-in-practice (DynamicManager.process_round never
    called by the runner). DISTINCT from take_up_slack (planning-time allocator vs reactive falsifier
    re-router), NOT subsumed → KEEP, wire only for BR2 differential allocation. (e) **dm consolidation** —
    Strangler-Fig dm→runner; Step 0 (the gamma-test pin) DONE; Steps 2-6 deferred behind `go` (the landmark
    is fragile; a blind ConvergenceDetector swap is refuted). All four notes' specs preserved in the agents.
- 2026-06-10 ~00:30 BST — **GAMMA TWO-SIDED GATE implemented + tested.** Founder ruling: gamma was
  never to be demoted; restore it as the active first side of a 2-part gate. Verified the live run
  would converge at round 6 under it (gamma_critical 0.607 >= 0.30 AND 3 zeros — both first at R6).
  Code: `_check_gamma_alt_convergence` now requires gamma_critical >= threshold AND the count; the
  call site passes `gamma_critical`; the misleading "reported only" wording is gone. Tests
  `test_two_sided_gate.py` (2) + existing convergence tests pass. **Standing directive added to
  `.claude/CLAUDE.md`** so this stops recurring. gamma depletion was REACHABLE; gamma worked; the
  count was the binding (later) condition; the two naturally agree. Mechanical, not theoretical.
- 2026-06-09 ~22:12 BST — **★ LANDMARK ACHIEVED ★ Live Exp 42 CONVERGED at round 6, ZERO residual
  HIL.** location_keyed_convergence + routing + CONFIRM-only gate, all genuinely active (the silent
  symbol-extraction bug was caught + fixed first). Location-keyed critical series `[10,1,5,1,0,0,0]`
  → 3 consecutive zeros → γ-alt CRITICAL_QUIESCENCE_CONVERGED at R6 (matches the offline prediction
  R6–7). Report: hil_flags=0, irreducible queue=0, unconfirmed criticals=0; 52 findings, 5 confirmed
  criticals all resolved by routing/gate. gamma_critical reported (~0.61), never gated. The ID-proxy
  path never converges; this one does. **C1 DONE. Committed + pushed `375236d` on exp39-experimental
  — the landmark commit.** Convergence is now a reliable, mechanical consequence of the work, proven
  live end-to-end. The chronic non-convergence was mechanical (the dedup key), exactly as the founder
  always maintained — not theoretical.
- 2026-06-09 ~20:05 BST — Program plan created. Live run b4i21mlyn in progress. SS key recovered
  as "never wired". Survey wf_25fab8a8 complete. Next: directive-pruning panel; ouroboros loop-close.
- 2026-06-09 ~20:10 BST — Live run VERIFIED active: `[GATE] location-keyed novel-crit=10 (ID-proxy
  crit=20) FEEDS γ-alt` at R0 — the fix halves the inflated count in real time. SS key: founder
  re-applied; OpenAlex covers it meanwhile (not a blocker).
- 2026-06-09 ~20:35 BST — **Semantic Scholar API key wired + verified.** Founder provided the key;
  stored in gitignored `.env` as `SEMANTIC_SCHOLAR_API_KEY` (not committed, not echoed);
  `_query_semantic_scholar` now reads it from env and passes `api_key=`. Measured: **1.8s with key
  vs 95.7s unauthenticated** (throttling removed). 17 ouroboros tests pass. Rate limit 1 req/s
  (cell does ≤3 sequential queries/round — within bound). D1 CLOSED.
- 2026-06-09 ~20:20 BST — **Ouroboros full-text chain BUILT + verified** (`ouroboros_cell.py`):
  `full_text_for_doi` = Unpaywall (legal OA) → Sci-Hub (configurable `enable_scihub_fallback`,
  OFF by default, `scihub_mirror`), cited source ALWAYS the original DOI. OpenAlex added to default
  sources. 5 tests (`test_ouroboros_fulltext.py`) + 12 ouroboros tests pass. This is the building
  block the loop-close consumes. Restores the 14-Apr-planned source list (arXiv+SS+Unpaywall+CORE+
  OpenAlex) + the founder's silent-Sci-Hub fallback. **B-Ouroboros remaining:** the loop-close
  (inject literature into `_build_prompt`) — its own unit, gated on an ouroboros-enabled test run
  (Exp 42 has no `_ouroboros`, so it gets exercised on the macrophage/bio experiment).
