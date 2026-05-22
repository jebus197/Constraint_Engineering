# Experiment 41 — Convergence-Detector Fixes + Five-Model Confer Verification (technical)

2026-05-22 (BST). Constraint Engineering / CDSFL.

## Summary

Two material defects in the maths model's convergence detector
(`bench/dm/_convergence.py`) were found, fixed, and independently
verified by a five-model confer. A return-to-first-principles
convergence scope was endorsed (with conditions) for a controlled
Exp 41 re-run. This note also **corrects the materiality record**: an
earlier pass (same day) misclassified the novelty/similarity findings as
iteration; they are material, and the panel that raised them was right.

## The two material fixes (folded into the maths model)

1. **kappa_rate (panel C0009/C0016/C0024/C0001/C0017/C0025).** Previously
   measured the rate of *all* per-round equivalence classes with a brittle
   "round-1 baseline" special case (returning 0.0/-1.0 for quiet states).
   Now: `kappa_rate(r) = clamp(1 - lambda_novel(r)/lambda_peak, 0, 1)`,
   where `lambda_novel` counts **novel** classes per unit time and
   `lambda_peak` is the peak novel rate over rounds 0..r. A genuinely
   quiet state reads converged; no-novelty-ever returns 1.0 (non-vetoing).
   Duane-correct (new discoveries, not raw volume); removes special cases.

2. **Novelty/similarity threshold (panel C0014/C0044/C0019/C0023).** The
   embedding similarity backend maps cosine via `(cos+1)/2`, flooring
   *unrelated* findings at ~0.48; the detector merged at `tau_sim=0.33`
   (below the floor), so **everything merged → genuinely-novel findings
   (incl. critical) were treated as "already seen" → the severity veto
   never fired → false convergence.** The config already defined
   `tau_sim_embed=0.55` but it was never wired in. Fix: a backend-aware
   `effective_tau_sim()` selector (in `_similarity.py`), bound at the
   detector to its **actual** `similarity_fn` via `_tau_sim()` (confer
   condition — a custom lexical fn under an installed embedding backend
   must not inherit 0.55). Same fix applied to `_manager.py:692` (rho
   metric). The shared similarity math is untouched (the runner's immune
   pipeline already independently hardcodes `tau_sim=0.50`, so live
   experiments were unaffected; the bug was isolated to this module).

Plus: removed a pre-existing unused `numpy` import from `_convergence.py`
(the "numpy imported but unused" pattern the panel kept flagging).

## Five-model confer verdict (2026-05-22)

Panel: CC2 Opus 4.7, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, falsification-framed, compelled
convergence. Logs: `bench/logs/confer_exp41_fix_verification_2026-05-22/`.

- **FIXES:** 4× SOUND-WITH-CONDITIONS, 1× SOUND (DeepSeek).
- **SCOPE:** 4× REASONABLE-WITH-CONDITIONS, 1× REASONABLE (DeepSeek).
- Book-cooking self-checks: cleared by all five.

Conditions (all mapped):
1. Bind threshold to the active similarity backend, not package state
   (Gemini called the global form "UNSOUND under injection"). → **DONE**
   (`_tau_sim()` instance-binding; default→0.55, custom→0.33, verified).
2. `kappa_rate`'s peak baseline is outlier-vulnerable; the convergence
   *guarantee* must not rest on `kappa_rate` alone. → **Step 3** (explicit
   K-round zero-genuine-novel rule; peak is diagnostic only).
3. Add explicit "no new genuine discoveries for K rounds" condition
   (codex/chatgpt). → **Step 3** (runner gate).
4. Outstanding/known criticals must still block via the veto even if the
   generator goes quiet (Gemini/cc2). → **Step 3** (outstanding-criticals
   veto, registry-resolution-aware).
5. `_manager.py` must NOT be deferred — silent evidence loss is a hard
   blocker (Gemini). → **DONE** this session.
6. Verifier must show near-zero false-negative rate on criticals before
   live gating (DeepSeek/Gemini conservatism). → **Step 3** (uncertain→keep,
   never silent-discard) + **Step 4** A/B non-distortion check.
7. The frozen-target A/B is mandatory and must show BOTH
   false-convergence-prevented AND true-convergence-preserved (cc2). →
   **Step 4**.

## Corrected materiality record

The first materiality pass (same day) made three errors, all caught by
the fold-and-falsify process and by the panel:
- A verification-script string-match false-flagged the estimate_gamma
  cluster as material (it is iteration — diagnostic, never gates).
- A hardcoded verdict + a misread of test output filed C0014/C0044
  (novelty flaw) as iteration; it is **material** (false convergence).
- By extension the clustering-threshold findings (C0019/C0023) were
  under-rated; they share the same material root.
Final: material = {kappa_rate cluster, novelty/similarity cluster}; the
other ~7 clusters are genuine but non-material footnotes (iteration
backlog — kept, not discarded). The maths model's *core idea* is sound;
two *implementation* defects were real and are now fixed.

## Verification

- 283 convergence/manager tests + 141 immune/feedback tests pass.
- Convergence still reachable: a clean exhausted target → converged=True.
- False convergence blocked: a novel critical → veto fires → converged=False.
- `_convergence.py` ruff-clean; all modules import (runner + immune).
- 4 pre-existing unused-import lints remain in `_manager.py` (not
  introduced here; deferred to a lint sweep).

## Plan (Steps 3–4)

- **Step 3 — runner gate ("return to first principles"):** gamma →
  diagnostic (never gates); convergence = K consecutive rounds of zero
  verifier-surviving genuine novelty; outstanding-criticals veto; verifier
  promoted with conservatism; pre-declared materiality rubric (incl.
  verification-integrity).
- **Step 4 — pre-registered Exp 41 A/B:** same frozen target
  (`bench/dm/_convergence.py`), thresholds frozen, no post-hoc tuning,
  report both directions. Goal: replicate the clean convergence of Exp 37
  (the last naturally-converged run, state-based, on `main` before the
  Exp 40 gamma-gate complications).

## Cross-references

- *Experiment 41 Convergence Investigation* (2026-05-22) — the diagnosis.
- Confer logs: `bench/logs/confer_exp41_fix_verification_2026-05-22/`.

Written under CDSFL note standard v1.2 (14 May 2026).
