# CDSFL Founder Decision Register — Full State, Point by Point

2026-07-06 01:25 BST · branch `exp39-experimental` · written for founder response, item by item

This register replaces the 2 July assessment's overview register with full specificity. Part A is an incident report requiring founder action. Part B is the recent experimental record. Part C is the present state. Part D enumerates every open item as a numbered decision (D1–D12), each with exactly one recommendation to approve, reject, or amend.

## Part A — The API-key incident (corrected account, founder action required)

**What the founder challenged:** the recurring claim that model API keys were "missing" and had been "shell-exported and lost with the terminal". The challenge was correct and the claim was wrong.

**Tool-verified facts (2026-07-06):**
1. `<repo>/.env` was **created 28 March 2026** — it has been the project's credential store all along, exactly as the founder said. Runs from March through 9 June drew their keys from it.
2. Its **last modification is 9 June 2026, 20:55 BST** — the write that added `SEMANTIC_SCHOLAR_API_KEY`. It has not been touched since, and today it contains only that one key.
3. The Exp 42 landmark run launched 9 June 19:36 BST — **before** that write — with all five model routes working.
4. No model keys exist in any shell profile (`~/.zshrc`, `~/.zprofile`: zero matches) or any other env file.
5. The only APFS snapshot is 2 July (post-loss). No external Time Machine backup is visible from this session (a permission error blocks full enumeration — the founder may know of one).

**Conclusion (high confidence):** the 9 June write **replaced the `.env` file instead of appending to it, destroying the model keys**. The subsequent "keys were shell-exported" explanation was an unverified inference repeated as fact — a fabricated-certainty failure, now retracted. The keys did not go missing; they were destroyed by the assistant's own write.

**Prevention (built 2026-07-06, this session):** `scripts/check_model_keys.py` — a credential preflight that reports PRESENT/ABSENT per required key (values never shown) and exits non-zero if a required key is missing, so launches can gate on it; plus `.env.example` documenting the expected file shape and the **append-only convention**: agents never rewrite `.env` wholesale again.

**D1 (founder action — the unblocking step):** restore two keys by appending to `<repo>/.env`:
```
OPENROUTER_API_KEY=<value>    # carries Codex + ChatGPT + Gemini (panel routes via OpenRouter since 2026-05-10)
DEEPSEEK_API_KEY=<value>      # DeepSeek direct
```
`GEMINI_API_KEY` is now only a legacy fallback (the panel's Gemini rides OpenRouter) — optional. Recommendation: **rotate** (re-issue) both keys at the provider dashboards rather than re-pasting old values, given the loss event. Verify with `python3 scripts/check_model_keys.py` (prints PRESENT/ABSENT only). This unlocks Exp 43 **and** the full five-model panel.

## Part B — Where we have been (the last four experiments, specifics)

**Exp 40** — target `bench/dm/_feedback.py` (the §17 feedback directive module). Ran a long multi-leg arc (17+ rounds plus slice campaigns, May 2026). Did **not** converge under the early gates: all-findings gamma peaked 0.2967 at round 3 then plateaued ~0.05 for 25 rounds. Its value was the lessons: fixes were being applied only to a sandbox (never written back, so the panel re-reviewed the same defects), the hardened-gate conjunction was shown empirically anti-cooking (it refused convergence an OR-gate would have granted on 2 of 3 slices), and the falsifier-quality problem was exposed.

**Exp 41** — target `bench/dm/_convergence.py` (the bounded mathematics module). **Converged at round 6 on 23 May** via the zero-novel-critical count path: 22 canonical findings, 4 closed, no empty responses, no fallback routes. Its critical-series gamma computes to **1.000** (the series `[3,0,0,0,0,0,0]` is flat). An older record's "gamma 0.240" was the all-findings series — not the gate input; that confusion is now documented everywhere it appeared.

**Exp 42** — target `bench/cdsfl_registry/composer.py` (the four-layer directive assembler, 60,416 chars). The project's hardest and most instructive arc, four faults peeled in sequence, each live-verified:
1. **3 June** — "tools decide, not votes": every critical finding must carry a runnable falsifier importing the real module; the runner re-runs it and decides. Model-vote truth was removed.
2. **7 June** — **CONFIRM-only gate** (`0a4d8ce`): a broken falsifier exiting cleanly had been masking real defects as REFUTED; now only a positive demonstration resolves a critical, and REFUTED on a critical escalates rather than drops.
3. **7 June** — **capability routing** (`bench/take_up_slack.py`): an unconfirmed critical climbs a Codex→CC2 ladder of stronger falsifier-writers before any human sees it. Live-proven: the prior 15-finding human pile-up fell to **zero across 16 rounds**.
4. **8–9 June** — **the convergence root cause**: novelty was keyed on model-invented finding-ids, so re-found defects re-counted as new and the quiescence streak never formed. Fix = the **code-location novelty key** (`bench/convergence_location.py`): a critical is new only if it names a target-file AST symbol not previously flagged. Result: **Exp 42 converged live at round 6, series [10,1,5,1,0,0,0], zero residual HIL** (commit `375236d`). The free-text-similarity alternative was tested and refuted (over-merges; falsely converges at round 2).

**10 June (overnight)** — the **two-sided gate** (`71b190b`, founder ruling): convergence requires BOTH `gamma_critical >= 0.30` (the critical decay curve has flattened — gamma active, never "reported only"; standing directive in `.claude/CLAUDE.md`) AND 3 consecutive zero-new-critical rounds. Verified on both landmarks (exp41c 1.000, exp42 0.687). Also: a 3-test regression the gate commit had left red was caught and fixed (`633b4c6`, 434-test sweep green); **severity calibration built** (`050f17c`, 17 tests — demotes a falsifier-confirmed-real but explicitly latent critical below 0.7, recording original + reason, never deleting, never touching safety/core/security/data-loss; **inert until a latent-tagger sets `entry["latent"]`**); **Exp 43 config built and pre-flight verified** (`1b5d148`).

**2 July** — full recovery + state assessment after the first hiatus: repository confirmed untouched; the operational tracker's resume pointer (stale at 7 June) advanced; MEMORY.md compacted below its load limit (zero content loss — session entries moved verbatim to topic files).

## Part C — Where we are now (state as of 2026-07-06 01:20 BST)

- Branch `exp39-experimental`, tree clean, in sync with origin. 1,596 tests collected; the 434-test runner/convergence sweep green (11 June), the 62-test gate subset re-verified green (2 July).
- **Live and driving decisions:** falsifier gate (CONFIRM-only) + `execute_python` tool loop on all dispatch paths; capability routing; location-keyed two-sided convergence gate; §17/§18 directives; B-Cell specialists (mathematics, statistics, biology, information-science, software); G7 merge arbitration; static-queue closure + small-queue alarm.
- **Built, tested, inert:** severity calibration (needs the latent-tagger, D4).
- **Shadow (runs, no live effect):** macrophage cell (`bench/macrophage_cell.py`); Stage-6 calibrator (`dm/_shadow_stage6.py`); ouroboros literature cell (functional chain: OpenAlex + Semantic Scholar keyed + Unpaywall, optional off-by-default Sci-Hub citing originals — but fetched papers reach no model prompt).
- **Dormant:** dm LoadBalancer (keep for Bench Run 2 — distinct from routing, not subsumed); dm ConvergenceDetector stack (naive swap refuted; consolidation gated).
- **Blocked:** the two required model keys (D1). Codex CLI is restored and logged in.
- Vendor economics: the premium driver tier moves to metered credits **7 July (tomorrow)**; programmatic/CLI usage has had its own meter since 15 June. The project's driver dependency is deliberately minimal (the panel rides the founder's own API keys), but see D12.

## Part D — Decisions (one recommendation each; approve / reject / amend)

- **D1 — Restore the two keys** (founder action; Part A above). Recommendation: rotate at the providers, append to `.env`, verify with `scripts/check_model_keys.py`.
- **D2 — Launch Exp 43 the moment D1 lands.** Target `bench/macrophage_cell.py` (547 lines / ~22K chars / 15 AST symbols, self-contained). The generalisation test: does the location-keyed two-sided gate converge a second module? Command: `python3 bench/launch_exp42.py --config "$(pwd)/bench/exp43_configs/43_macrophage_locationkey_live.json"` under full cy monitoring (60-second cadence, terminal tailing the log, pause-FFAFP-resume on anomaly). Config pre-flighted end-to-end. Recommendation: **yes, same day as D1**.
- **D3 — Exp 42 findings fold-forward.** The Exp 42 review was static (`apply_fixes_back=false`), so `composer.py` still carries the panel's confirmed defects; 69 findings stand CONFIRMED across the runs (the target moved during the arc, so each needs a staleness check). Recommendation: I run the `sy`+`f` sweep and deliver a per-finding fix package **for your sign-off** (fixes are suggested to HIL, never auto-applied), while Exp 43 executes.
- **D4 — Build the latent-tagger** (activates severity calibration). A conservative reconciliation step that marks a falsifier-confirmed critical as `latent` only when its trigger is demonstrably absent from the real usage (the Exp 42 evidence base: 9 of 15 residuals were real-but-latent). Gated, integration-test-gated. Recommendation: **build now**.
- **D5 — Ouroboros loop-close** (fetched papers into model prompts; external-coverage estimate grounded in them). Gets genuinely exercised on the bio/STEM experiments (Exp 47+), and Exp 43's domain is software. Recommendation: **build after Exp 43 is in flight**, integration-test-gated.
- **D6 — Macrophage promote-vs-retire.** It runs every round, reaches no live decision. Options: minimal-promote (a high-severity anomaly raises a HIL flag / pauses a round) or formally retire-as-cosmetic. Recommendation: **defer the decision until Exp 43's results** — the panel is about to review this exact file; its findings will inform the call better than we can now.
- **D7 — LoadBalancer disposition.** Recommendation: **confirm keep-dormant** (planning-time task→model allocator, distinct from the reactive routing ladder; wire only when Bench Run 2 needs differential allocation).
- **D8 — dm consolidation Steps 2–6** (extract the gamma estimator + novelty series into one `convergence_core.py`, collapse the dm duplication, guard-test the refuted detector out of the decision path; Steps 0–1, the green-baseline pin, are already done). Recommendation: **authorise now, execute after Exp 43 completes** — behaviour-preserving, replay-diff-gated, but the landmark deserves the extra insurance of a second converged run first.
- **D9 — Rename `take_up_slack` → `routing`** (module, flag, logs, tests; backward-compatible launcher alias). Recommendation: **yes** — folded into the same post-Exp-43 window as D8.
- **D10 — Directive-pruning panel (`pr`).** Measured: each model receives a ~50K-char system directive of which 43,667 chars (`cdsfl_operational.md`, 18 sections) is appended unpruned outside the composer's prune path — today's pruner reaches ~6%. A trim-to-~27K draft exists (S18 divergence exposition −4.5K, S16 Stage-6 narrative −3.5K, S17 mechanism prose −2.5K, S8/S4 economics prose −2.5K, provenance strings −1.5K; the falsification core — S1, S2, S3/S6 R_k, S7 fix format, S15 admissibility gates, S11/S12 — retained verbatim). Recommendation: **run the panel once D1 lands** (it needs the same keys), then implement what survives critique behind a lean-vs-full ablation.
- **D11 — MEMORY.md restructure review.** Executed under a harness mandate (the index exceeded its load limit and was silently truncating every session): four session entries moved verbatim to `cdsfl_session_*.md` topic files with one-line pointers; nine long entries tightened; 26.3KB → 17.6KB; zero content deleted. Recommendation: **approve as-is** (or direct changes — everything is recoverable).
- **D12 — Billing check before long runs** (founder action, ~2 minutes). The 15 June change moved programmatic/CLI usage to its own credit meter, which may include the CC2 (`claude -p`) dispatches inside runs. Recommendation: glance at the plan's usage page before the first long run. [VERIFY:current — vendor-side, unverifiable from here.]

## The sequence, if the recommendations stand

D1 (keys, ~10 minutes) → D2 (Exp 43 launches, runs 4–6 hours under cy) → D3 + D4 build in parallel while it runs → D10 panel on pruning → Exp 43 results → D6 decided on evidence → D8 + D9 consolidation window → Exp 44 planning. That is a genuinely substantial arc for the cleared days, and every step is verification-gated.

Written under CDSFL note standard v1.2 (14 May 2026).
