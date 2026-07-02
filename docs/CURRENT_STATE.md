# CDSFL Current State

Generated: 3 July 2026 00:24 BST (2026-07-03T00:24:23+01:00)

---

## Git

- **Branch:** exp39-experimental
- **Last commit:** `ab62cc9` Correct record timestamps to actual write time (23:35 BST, not mid-afternoon) — session ran 14:42 to 23:37
- **Committed:** 2026-07-02 23:38:20 +0100
- **Remote:** ahead by 172
- **Working tree:** DIRTY — uncommitted changes present

Uncommitted files:
- `M resources/ONBOARDING.md`
- `M resources/RECOVERY.md`

---

## Tests

**1596 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

---

## Latest Experiment

- **Experiment:** exp42_composer_locationkey_live (#42)
- **Status:** CONVERGED
- **Topology:** star
- **Target:** `bench/cdsfl_registry/composer.py`
- **Rounds:** 7
- **Total findings:** 80
- **Gamma:** 0.5327
- **Models:** CC2, ChatGPT, Codex, DeepSeek, Gemini
- **Per model:**
  - Gemini: 34
  - Codex: 15
  - DeepSeek: 12
  - ChatGPT: 11
  - CC2: 8
- **Logs:** `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/logs/exp42_composer_locationkey_live_20260609T183659Z`

---

## Recent Commits

- `ab62cc9 Correct record timestamps to actual write time (23:35 BST, not mid-afternoon) — session ran 14:42 to 23:37`
- `39af565 Full rs (2 July) + full state assessment + tracker resume-pointer advance`
- `6ed0adf sv: gamma two-sided gate live + overnight build banked (severity calibration built; Exp 43 macrophage config pre-flight-verified, gated on model API keys; gamma-test regression fixed; matrix + closure-index macrophage corrections; 434 tests green)`
- `053e873 Overnight run record: durable plan update + matrix correction + report`
- `1b5d148 Exp 43 macrophage config — generalisation test, wiring VERIFIED, gated on keys`
- `050f17c Build severity calibration — over-production bounding (T6, gated default-off)`
- `633b4c6 Fix stale gamma-alt tests left red by the two-sided gate (71b190b)`
- `71b190b Restore gamma as ACTIVE convergence condition — TWO-SIDED GATE (founder ruling)`
- `c865bd9 Add pytest.ini (global 300s test timeout + network marker) — closes the hanging-test bug`
- `6817227 sv: convergence LANDMARK — code-location novelty key proven live (Exp 42 converges R6, 0 residual HIL); gamma clarified as central/non-demoted (decay-curve diagnostic; count = its threshold-free endpoint); gamma 'reported only' log wording corrected; ouroboros functional (timeout+OpenAlex+Unpaywall/Sci-Hub full-text+SS key); static-queue closure + small-queue alarm; shadow-mode survey; remediation program plan`
