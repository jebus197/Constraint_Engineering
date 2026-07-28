# Exp 46 — Convergence with the Full Machinery End-to-End (Technical Record)

**2026-07-28, 13:45 BST.**

## Result

`exp46_stage6_locationkey_live` (target `bench/dm/_shadow_stage6.py`, 29,523 chars, 19 AST symbols, domain=software) reached **CRITICAL_QUIESCENCE_CONVERGED at round 5** via the two-sided γ-alt gate: γ_critical = **0.336 ≥ 0.30** AND zero-new-critical tail `[0,0,0]`. 6 rounds, ~1h40m, launcher exit 0, **cost ≈ $19** (balance $452.05). Run dir `bench/logs/exp46_stage6_locationkey_live_20260728T103151Z`.

**The founder's "everything over the line" standard was delivered mechanically for the first time:** at the verdict, the **post-convergence sweep fired automatically** — 6 residuals → panel → **6/6 terminal in one epilogue round (~2.5 min)**. Registry final: 27 canonical, all terminal. All 12 criticals falsifier-CONFIRMED. NOT-FALSIFIED audit: the single flag (C0003) re-run live → genuine AssertionError demonstration; ledger clean.

## Declared deltas, both performed

- **Sweep (first in-run use):** in-run 2 cleared / 4 withdrawn / 0 remaining; independent offline replay of the same residual set: 3 cleared / 3 withdrawn / 0 remaining — same endpoint, honest dispatch variance. Withdrawal reasons audited: two residuals were truncated/malformed texts with no testable claim; one reasoned technical dismissal. Per-item audit: `sweep_replay_audit_20260728.json`.
- **Ouroboros 1E.8 query fix:** **zero query failures** across the run (Exp 45: HTTP 500s from round 0).

## Instrument sightings

FIX-1 residual queue logged explicitly from R3 (C0014, non-gating). One ladder-exhausted critical entered the guarded irreducible queue at R3 within bound and was resolved by the endgame. R_k validator corrected a ChatGPT self-assessment (0.402 vs recomputed 1.000). One REOPEN attempt (C0005) HIL-logged; verified fix stood. Software specialist live throughout.

## One defect found and fixed (the run reviewing its own tooling, again)

The round checkpoint predates the sweep, so Exp 46's per-item sweep dispositions were lost at process exit (counts survived in the report). Fixed same hour: per-item dispositions now recorded in sweep stats AND the post-sweep registry is persisted to `runner_state.json` (commit on `exp39-experimental`); the lost audit trail for this run was reconstructed by offline replay. Faults-per-experiment series: 42 root-cause hunt → 43 gate fix → 44 none in-run (reader bug in audit) → 45 none → **46 one bookkeeping gap, found by post-run verification, fixed in one hour.**

## Sequence

**Five consecutive convergences: 42 (R6) → 43 (gate-passed, formal block since fixed) → 44 (R12, zero residue) → 45 (R3, ledger born clean) → 46 (R5, everything-over-the-line delivered by the machine itself).** Next: Exp 47 = `dm/_divergence.py` (39K, the largest remaining real module) with ImmuneMemory recording live as its declared delta.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
