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
Status log (append-only):
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
