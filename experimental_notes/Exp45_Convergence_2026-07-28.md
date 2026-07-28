# Exp 45 — Convergence via the Two-Sided Gate (Technical Record)

**2026-07-28, 00:50 BST.**

## Result

`exp45_memory_statistics_live` (target `bench/dm/_memory.py`, 10,726 chars, 14 AST symbols, domain=statistics) reached **CRITICAL_QUIESCENCE_CONVERGED at round 3** — the two-sided γ-alt gate on its own terms: γ_critical = **0.621 ≥ 0.30** AND zero-new-critical tail `[0,0,0]` (all critical discovery in R0; quiet from R1). 4 rounds, **2,720 s (~45 min)**, launcher exit 0. Run dir `bench/logs/exp45_memory_statistics_live_20260727T225640Z`. **Cost: $5.62** (balance $471.09).

**Registry: 39 canonical — 15 CLOSED / 13 CONFIRMED / 2 MERGED / 3 REFUTED / 6 OPEN (sub-critical, non-blocking by design → post-run review).** All 12 criticals `falsifier_verdict=CONFIRMED`. Residual queue EMPTY; open irreducible 0; **NOT-FALSIFIED-as-CONFIRMED audit check = 0** — the first run whose verdict ledger required no post-hoc correction (first full run under the 59ffe77 verdict-reader).

## First flights

- **Statistics specialist LIVE** (first in project history): engaged all 4 rounds ("B-Cell specialist (LIVE, domain=statistics)"), 8 verdicts in R0 alone. Pre-registration prediction met.
- **Ouroboros LIVE** (first execution of the 12-July real-work loop): **4 real OA paper briefs** (r00: 2, r01: 1, r02: 1). Exposed its known query-quality flaw live (raw finding text + backticks into the arXiv API → intermittent HTTP 500), shadow-contained exactly as designed (warnings only, zero convergence effect). Query-construction fix (Item 1E.8) now concrete: sanitise/keyword-extract before query. Scheduled.

## Honesty notes

- Converged via the critical-quiescence side while sub-critical novelty was ongoing (state gate same round: "Gate failed: novel=8") — designed asymmetry (criticals decide; minor items don't hold the gate hostage). The 6 OPEN sub-criticals pass to the standing post-run review, not swept.
- Faster than the pre-registered ~R8–12 band: legitimate under the frozen config (gamma_alt_earliest_round=3); the small, recently-audited module quiesced immediately. No tuning after results.
- Launcher still prints "Experiment 42" (stale label) — cleanup queued.

## Sequence

42: instrument proven (R6) → 43: generalised, 1 artifact → 44: zero-residue convergence, verdict-reader bug caught in audit → **45: ledger born clean, R3, $5.62.** Faults-per-experiment and cost-per-experiment both falling; γ never demoted; the maths model unbroken throughout.

## Next

Standing post-run review (6 OPEN items, specialist verdict quality, ouroboros query fix, **founder decision: enable ImmuneMemory live for the remaining arc**), then Exp 46 = `dm/_shadow_stage6.py`.

---


## Postscript — panel sweep smoke test (28 July, morning)

The founder-approved post-convergence sweep was smoke-tested live against this run's six OPEN residuals, with the real five-model panel doing the clearing and the runner's independent falsifier re-execution as sole judge. **Result: 6/6 cleared in ONE sweep round, zero remaining, zero withdrawals** — Codex supplied runnable falsifiers for all six; each was re-executed and CONFIRMED by the runner. Exp 45 therefore now stands at 39/39 findings terminal — everything over the line, matching Exp 44's bar. The founder's hypothesis (with the ghost-issue machinery fixed, ordinary residuals are panel-clearable) is confirmed; the sweep is enabled as a declared delta from Exp 46 onward. Record: `sweep_smoketest_20260728.json` in the run dir.

*Written under CDSFL note standard v1.2 (14 May 2026).*
