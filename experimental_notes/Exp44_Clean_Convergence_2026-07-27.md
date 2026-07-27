# Exp 44 — Clean Convergence (Technical Record)

**2026-07-27, 05:15 BST.**

## Result

`exp44_evidence_locationkey_live` (target `bench/evidence.py`, 23,207 chars, 30 AST symbols, domain=software) reached **STATE_CONVERGED at round 12** — 3 consecutive full gate passes (R10/R11/R12): `open_ch=0 (stable), novel=2, contested=0`. γ_critical (the gate input, location-keyed critical series) = **0.453 ≥ 0.30**; location-keyed novel-critical series tail `[0,0,0,0,0]` from R8. The all-findings gamma printed in the state line (0.253) is telemetry, NOT the gate input. Launcher exit 0; run dir `bench/logs/exp44_evidence_locationkey_live_20260727T002705Z`; wall clock 01:27→05:08 BST (~3.7 h); 13 rounds (R0–R12).

**Registry at convergence: 82 canonical — 63 CLOSED, 13 CONFIRMED, 1 MERGED, 5 REFUTED. Zero OPEN / UNCONFIRMED / CONTESTED. Residual queue (FIX 1 un-demonstrated sub-criticals): EMPTY. HIL: 6 irreducible items in the guarded queue (`irreducible_escalation`, severity-filtered) awaiting founder materiality review.** First run in project history to reach the formal endpoint with zero non-terminal residue.

## Fix tranche performance (pre-registered prediction: clean convergence, no sub-critical blocking — MET)

- **FIX 1**: the Exp-43 blocker class never manifested; residual queue empty throughout; the one `contested=1` episode (R7–R8) was `C0047` — sev 0.70 **critical**, UNTOOLABLE — correctly counted at full protection, routed, ladder-exhausted → guarded irreducible queue; gate closed around it (contested clear from R9). Exactly the designed critical/sub-critical asymmetry.
- **FIX 2/routing**: 11 findings resolved by stronger writers across the run (5+3+3 tallies).
- **FIX 3**: no review-summary leak registered.
- **FIX 4** (`max_contested_rounds=3`): no stale-contested aging was needed.
- **Location key live demonstration (R10)**: ID-proxy crit=1 re-raise recognised as re-find (location count 0) — the Exp-42 cure working on target #3.
- REOPEN attempts on C0001 (R5, R10) and C0002 (R10) HIL-logged; verified fixes stood (final status CLOSED).

## Sequence established

Exp 42 (composer.py): instrument proven, converged R6. Exp 43 (macrophage_cell.py): generalised, formal convergence blocked by one mechanical artifact. **Exp 44 (evidence.py): artifact fixed → formal convergence, zero residue, first attempt, zero in-run HIL intervention.** Faults-per-experiment: one root-cause hunt (42) → one bounded gate fix (43) → none (44). The meta-level diminishing-returns prediction (19 July note) is holding.

## Queued next steps

(1) Founder materiality review of the 6 irreducible HIL items + the 2 REOPEN attempts. (2) The committed post-44 **shadow audit** (ouroboros, macrophage, stage-6 calibrator, severity calibration, load balancer). (3) Founder funding decision on the remaining arc (≈5 experiments; this run's cost ≈ $20–30 [estimate — dashboard is authoritative]). (4) On go: Exp 45 = `dm/_memory.py` with `domain=statistics` (the declared specialist variable), then the enable-ImmuneMemory decision at its post-mortem.

Cosmetic defect noted for cleanup: the launcher prints "Experiment 42 reached a terminal verdict" (stale label string in `launch_exp42.py`) — harmless, flagged.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
