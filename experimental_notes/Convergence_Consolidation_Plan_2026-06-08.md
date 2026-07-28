# Convergence Consolidation — Definitive Task List & Findings

2026-06-08 BST · branch `exp39-experimental` · owner CC1 (Opus 4.8)

**Read this FIRST on any compaction touching convergence/gamma/dedup work.** It is the
durable record of the 2026-06-08 convergence investigation and the task list that follows
from it. Every status claim names the tool that verified it — do not take prose on trust.

---

## 0. The thesis (founder, 2026-06-08)

The recurring project pattern: machinery is built, context is lost, a later agent assumes it
is active (because an earlier agent implied so), "new" issues appear that are actually the old
issue resurfacing, and increasingly desperate fixes get devised for a problem already solved.
Convergence — and the common-sense validity of gamma as its measure — has "probably already
been solved many times over." The deeper root cause is **LLM unreliability**, which is the very
thing CDSFL exists to constrain. This document is the antidote: a verified, durable, file/line
-referenced account that survives context loss.

---

## 1. Findings (tool-verified this session)

Source run: `bench/logs/exp42_composer_takeupslack_20260607T154745Z/` (clean take-up-slack
rerun, 16 rounds, 80 registry entries). Critical = severity ≥ 0.7 (`reference_runner_v2.py:1726`).

| # | Finding | Verified by |
|---|---------|-------------|
| F1 | New-critical/round as-run = `15,10,6,3,1,0,1,0,2,1,1,0,4,4,4,0`; never 3 consecutive zeros → no convergence. | report JSON, registry `open_since_round` + severity |
| F2 | `open_crit_high` and `unverified_critical` = 0 every round (routing cleared them). The blocker is the **new-critical counter resetting**, not unresolved findings. | report `rounds[*]` |
| F3 | The 12 late criticals (R12–14) collapse to **4 distinct defects**; tracing function-name signatures, all 4 first appeared by **round 3** (R0,R2,R3,R0). **Zero genuine late critical discovery.** | signature trace across all `rounds[*].findings` |
| F4 | Embedding `finding_similarity` of each late critical to its nearest earlier finding = 0.66–0.82 (i.e. all re-finds). | `bench/dm/_similarity.py` embedding backend |
| F5 | As-run gamma_critical rises to 0.658 (R12) then **declines** to 0.637 (R15) — the late phantoms bend the curve down. Deduplicated, it rises **monotonically** (no decline). The "lag" is a dedup-bug artifact. | `_estimate_gamma` recompute; numpy.polyfit; Wolfram `LinearModelFit` all agree gamma_crit(R15)=0.6372 |
| F6 | gamma_all saturates ~0.57 by R2 and is near-flat after → carries little trigger information. gamma_critical is the informative series but tops ~0.64–0.69 (never crosses a "high" threshold). | report `gamma_history`, `gamma_critical_history` |
| F7 | A single similarity threshold cannot cleanly separate re-finds (0.66–0.82) from unrelated findings (floor ~0.48–0.55) — bands overlap. Dedup'd convergence round is threshold-brittle: tau .60→R5, .65→R6, .70→R11, .75→never. | embedding dedup sweep |
| F8 | **The robust machinery already exists, dormant.** `bench/dm/_diminishing_returns.py::DiminishingReturnsDetector` has `novelty_rate()` (content dedup), `vocab_saturated()` (similarity-INDEPENDENT exhaustion, added after Exp 12 *because* similarity-novelty was brittle), smoothed `mu`, and a multi-signal `stop()`. `bench/dm/_convergence.py::ConvergenceDetector` does union-find content clustering, kappa metrics, a `converged()` predicate with severity veto, and `estimate_gamma()` on the **deduplicated** stream. | source read |
| F9 | **The runner does NOT import either detector.** It imports `dm._feedback,_round_context,_sk_format,_diversity,_divergence,_shadow_stage6` but rebuilds gamma + novelty inline (`_estimate_gamma`, ID-proxy `lookup_alias` at `:574`, registration `:5446-5453`). The dm convergence/diminishing-returns machinery is dormant. | grep imports of `reference_runner_v2.py` |
| F10 | The dormant detectors import cleanly and their self-validators pass (`validate_k1`, `validate_homogeneous`, `validate_no_findings` → True). 84 converg/diminish/similar tests pass. | python import + pytest |

**`_similarity.py` self-documents the exact recurring bug class:** its `effective_tau_sim`
docstring records a prior fix (2026-05-22) where "`tau_sim_embed` was defined in the config but
never wired in… the runner's immune pipeline had already independently worked around this by
hardcoding tau_sim=0.50." Same shape of bug: a correct value/component, defined, never wired in.

**Correction owed (mine, now on record):** my earlier claim that "old gamma would have FALSELY
converged at round 3 while real criticals poured in" does NOT survive the numbers — those
"criticals" were dedup phantoms and gamma_critical(R3)=0.398 is no convergence signal. Gamma is
not the villain; the ID-proxy novelty input is. (Refuted by F3, F5.)

---

## 2. Config defaults (dm, `bench/dm/_types.py`)

`tau_novelty=0.40` · `tau_novelty_stop=0.15` · `tau_vocab_growth=0.040` · `vocab_sustained_window=5`
· `smoothing_window=2` · `r_min=2` · `tau_sim=0.33` (Jaccard) · `tau_sim_embed=0.55` (embedding).

---

## 3. The plan — incremental, evidence-gated (Strangler-Fig)

Each task lists its **verification** (how we'll KNOW it works, not assert it). No task is "done"
until its verification passes and is recorded here with the tool that produced it.

### T0 — Durable record (THIS FILE) + tracker entry — *in progress*
Verification: file exists in repo + mirrored to operational tracker; committed.

### T1 — Independent active-vs-dormant audit (whole dm library + runner)
Independent agents (workflow) verify, per component, with tools (import graph, AST call-graph,
pytest): does it exist? imported by runner? called on the live path? tested? Adversarially checked.
Verification: structured audit table, each row tool-grounded, cross-checked by a skeptic agent.
**Purpose: kill the "assumed active" failure mode at the root.**

### T2 — DECISIVE TEST: replay Exp 42's 80 findings through the dormant detectors (offline)
Build a replay harness that feeds the recorded findings, round by round, into
`ConvergenceDetector` + `DiminishingReturnsDetector` and asks: do they recognise convergence at
the right round (~5–7) where the inline path failed? This tests the convergence LOGIC without a
4.5-hour live rerun.
Verification: harness output shows converged-round + which signal fired (novelty_rate / vocab /
mu / kappa / dedup'd gamma); adversarial agent tries to refute the result.
**If they converge correctly → the solution existed in our code all along (thesis confirmed).
If they DON'T → the dm library needs calibration, not just wiring (report honestly).**

### T3 — Wire the verified detector into the runner (gated, characterisation-tested)
Only if T2 confirms. Characterisation-test current inline behaviour first; add the detector behind
a config flag; replay-diff old-vs-new on recorded runs; default OFF so non-flag runs stay
byte-identical.
Verification: characterisation tests + replay-diff + full pytest green.

### T4 — Confirmation live rerun of Exp 42 (the final falsification)
One live run with the wired detector ON. Predicts convergence ~R5–7. Then **retire Exp 42 as a
test vehicle regardless of outcome.**
Verification: live run report shows convergence at predicted round with named signal.

### T5 — Promote routing to default + propagate to other experiment configs
Routing (`take_up_slack`) is wired but gated-off in one config only. Verification: configs updated;
gated default flipped; pytest + one smoke run.

### T6 — Severity calibration (NEVER BUILT) — over-production bounding
Build the ability to lower an over-rated-but-real finding's severity without discarding it.
Verification: unit tests + replay showing severity-demotion path exercised.

### T7 — Directive pruning (NEVER DONE) — dedicated panel (pr) + lean-vs-full ablation
~63K-char directive. NOT covered by this session's panel (that was convergence). Verification:
ablation run comparing lean vs full directive on a fixed task; panel review recorded.

### T8 — Stop-criterion hardening
Vocab saturation as similarity-independent backstop + multi-instrument agreement + seeded-defect
benchmark + clean-module null test. Verification: null test (clean module → no false convergence
delay) + seeded benchmark (known defects all found before convergence).

### T9 — Rename `take_up_slack` → `routing` (load-balancing/fingerprinting family)
Verification: grep shows consistent naming in code+docs; pytest green.

### T10 — Find→Fix→re-verify loop (full reliability claim)
### T11 — Separate-runner load-balancing evidence test
### T12 — Advance to Exp 43 (macrophage)

**Deferred by founder until the above are addressed:** LaunchPad seamless wiring (the `.zshrc`
line) and the voice/TTS rendering. Wolfram MCP is already live this session regardless.

---

## 4. Status log (append-only; each entry names its verification tool)

- 2026-06-08 ~15:13 BST — T0 file created. Findings F1–F10 tool-verified (report JSON, registry,
  numpy, Wolfram, pytest, source read). Branch `exp39-experimental`.
- 2026-06-08 ~15:35 BST — **T2 DECISIVE TEST run** (`bench/replay_exp42_convergence.py`). Result
  is a TWO-PART refutation+discovery, recorded honestly:
  - **The naive thesis "just wire in the dormant dm ConvergenceDetector" is REFUTED.** Run as-is
    at its default `tau_sim_embed=0.55` on Exp 42's raw per-round findings, the detector
    **over-merges** nearly all composer.py findings into ~1 equivalence class per round (because
    findings all about one ~400-line file score 0.55–0.82 to each other regardless of being the
    same defect — the exact failure its own `effective_tau_sim` docstring warns of) and **falsely
    declares convergence at round 2** — before the compose()-ignores-extras critical even appears
    (round 3). The dm machinery has the SAME threshold-calibration disease as inline gamma.
    Verified: `#cls`≈1 every round, `converged()`=True from R2. DiminishingReturnsDetector.stop()
    also fires R2 (over-merged novelty_rate at tau_novelty=0.40).
  - **The disease is general: NO single free-text similarity signal is clean.** Embedding
    over-merges (tau .55→false-converge R2); my earlier sweep under-merged (tau .75→never). The
    reason convergence has been "endlessly out of reach": every prior metric (Jaccard kappa,
    embedding kappa, gamma-on-novelty-count, ID-proxy count) keys on free-text, which can't tell
    two defects in one file apart.
  - **DISCOVERY (candidate solution, pending adversarial verification):** key critical findings by
    **code LOCATION** — the composer.py function(s) each finding names (AST-extracted). New-critical
    -location/round = `[8,1,0,1,2,0,0,0,0,0,0,0,0,0,0,0]` → 3 consecutive zeros at **round 7** with
    a STABLE zero tail (R5–15), matching the independent signature-trace ground truth (all distinct
    defects found by ~R4). No threshold to tune. Code findings are addressable by code location;
    free-text similarity is the wrong tool. Verified by direct computation; **under adversarial
    re-verification in workflow wf_88bbdd46-194** (skeptics try to find a genuinely-new critical
    after R4 that location-keying wrongly merges).
  - **Revised fix direction (supersedes naive T3):** the runner's existing "zero novel critical for
    K rounds" gate (`_check_gamma_alt_convergence`, `gamma_alt_consecutive_zero_crit=3`) is sound;
    the defect is its NOVELTY KEY. The gate consumes `novel_critical_history`, built by
    `_settled_novelty_series` (`reference_runner_v2.py:1736`), which counts registry entries by
    `open_since_round` — and re-finds get fresh entries (ID-proxy at `lookup_alias`/registration
    `:5446-5453`), inflating the count. **Injection point = `_settled_novelty_series` critical
    counting.** Replace with code-location novelty (AST symbols of the target file). Gated config
    flag, default OFF (byte-identical when off). Deeper consolidation (registration-level dedup so
    re-finds never mint entries, which also cleans gamma + registry bloat) = follow-on T3b.
- 2026-06-08 ~15:20 BST — Built + tested `bench/convergence_location.py` (`LocationNoveltyTracker`,
  `target_symbols`, `finding_locations`). 6 unit tests pass incl. Exp-42 regression pin
  (`bench/tests/test_convergence_location.py`). Conservative S3 semantics (new iff names any
  never-flagged location). **Four independent computations now agree** the location key converges
  Exp 42 at R6–7 with a stable zero tail where the ID-proxy never converges:
  signature-trace (all distinct defects by R4); raw-findings S1 → R7; raw-findings S3 → R7;
  **entry-level (what `_settled_novelty_series` sees) `[10,2,2,1,0,0,…]` → R6**.
  Calibration of severity threshold + window belongs to NULL test (clean module → fast converge,
  no false late "new") + SEEDED test (N known defects → all found before converge), NEVER Exp 42.
- 2026-06-08 ~15:29 BST — Adversarial verification workflow `wf_88bbdd46-194` running (6 audit +
  4 skeptic agents). **Runner wiring HELD until its verdict returns** — do not wire a design the
  skeptics might refute. Next on CONFIRM: gate-flag `_settled_novelty_series` to location key +
  characterisation test + full pytest, then offline replay as the convergence regression test.
- 2026-06-08 ~15:35 BST — **Workflow `wf_88bbdd46-194` COMPLETE (10 agents, ~753K tokens).**
  AUDIT confirmed the dormancy map exactly: runner uses its OWN inline `_estimate_gamma`
  (`:904`), inline gate (`_check_state_convergence`/`_check_gamma_alt_convergence`/
  `_check_hardened_convergence`), and ID-proxy novelty (`lookup_alias`, exact-string,
  `register` `:518`/`:5450`); `dm._convergence` + `dm._diminishing_returns` are NEVER imported
  by the runner (reachable only via the unused `brain.check_convergence`). One nuance found:
  inline gamma is NOT pure telemetry under DEFAULT config (`gamma_telemetry_only_until=14`,
  soft-gate `<0.30` rounds 14–19, hard-gate `<0.35` after) — experiment configs override it to
  telemetry-only, but the dataclass default can gate. Severity calibration: CONFIRMED absent.
  **ADVERSARIAL VERDICTS (the discipline catching me):**
  - **A (dm detector over-merges → false-converge R2): CONFIRMED.** Distinct bugs score
    0.576–0.671 > 0.55, single-linkage chains them to ~1 class; `converged()` True at R2.
  - **C (R12–14 burst = re-finds, zero genuine late discovery): CONFIRMED in substance**, with a
    correction: one defect (M4) first appears at round **4**, not "by round 3." My "all by R3"
    was off by one. The load-bearing thesis (no genuine NEW critical in the R12–14 burst) holds.
  - **B (my EXACT vector `[8,1,0,1,2,…]`, stable zero from R5): REFUTED as stated.** I quoted a
    STALE number (first quick-script S1) in the claim; my MODULE actually emits `[10,2,2,1,2,…]`,
    which the skeptic independently reproduced and CONFIRMED as a clean-converging variant. But
    the skeptics surfaced a real point: the exact convergence round is **keying-dependent** — a
    naive frozenset-of-functions keying does NOT give a stable tail; per-individual-location
    keying (my module's S3) does. **Qualitative thesis survives robustly** ("location-keying
    converges with a stable tail where model-id keying never does"); the EXACT round must not be
    asserted threshold-free. → Wiring as the LIVE trigger is therefore NOT yet earned; it needs
    null/seeded calibration to validate the keying + window. This is why the fix is gated.
- 2026-06-08 ~15:45 BST — Building null + seeded CALIBRATION tests (T8) as the gate to trusting
  the location key: must NOT false-converge when a genuine new location appears late, must count
  N seeded defects exactly once, and the known limitation (2nd distinct defect in an already-
  flagged function) is surfaced honestly, not hidden. Runner wiring is evidence-gated on these.
- 2026-06-08 ~15:55 BST — Calibration tests PASS (`test_convergence_location_calibration.py`,
  5 tests): re-finds collapse + converge; ongoing genuine discovery blocks convergence; known
  2nd-defect-same-function limitation pinned. **11/11 location tests green.**
- 2026-06-08 ~16:05 BST — **SHADOW wired into the runner** (telemetry-only, `location_shadow_enabled`
  default True, never gates). Sites: `RunnerConfig` flag (`:411`); helper
  `_location_keyed_critical_series` (after `_settled_novelty_series`); symbol extraction from
  `full_code` + `location_crit_history` init (~`:4970`); per-round shadow compute+log (after the
  settled-novelty block, wrapped in try/except so it can never break a run); round-record field
  `location_crit_shadow` (`:5982`-area); report field `location_crit_shadow_history`. Verified:
  runner `py_compile` OK; wired helper reproduces the offline series `[10,2,2,1,0,…]` → round 6
  on the Exp 42 registry; **199 runner/convergence/config tests pass; full non-network suite
  running.** The next live run will log the location series beside the ID-proxy count for
  side-by-side proof. **Live-GATING remains future work** (semantic splitter for 2nd-defect-same
  -function + a live confirmation run), per the adversarial verdict.

---
Operational tracker, not a standard-v1.2 technical note. The session's analytical synthesis is
mirrored to TTS separately per the `t` command.
