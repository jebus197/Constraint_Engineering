# Macrophage / Ouroboros (O1) Cell Type Split

**Date:** 12 April 2026
**Protocol:** CDSFL (Constraint-Driven Synthesis and Falsification, the Popperian multi-vendor LLM falsification framework) plus FFAFP (Find, Follow, Analyse, Fix, P-pass)
**Models:** Gemini 3.1 Pro (43.6s, 9912 chars) + Codex 5.3 (398.6s, 8467 chars)
**Confer logs:** `bench/logs/confer_cell_split/`

## Context

The CDSFL immune pipeline's `ouroboros_cell.py` has two modes (macrophage + microglia) in a single cell. This confer evaluated splitting them into two separate cell types with distinct responsibilities, trust boundaries, and API permissions.

## Architecture Decision

**Split is architecturally mandatory** (both models agree). A combined cell with mixed API permissions violates the Macrophage's isolation HARD constraint.

### Macrophage Cell (Internal Pipeline Monitor)
- **Role:** Internal observer and patrol cell. Watches, detects, advises.
- **Capabilities:** Pipeline monitoring, PE (Policy Engine) gate meta-monitoring, systemic pathology detection.
- **Pipeline stage:** Continuous observation, advisory only.
- **Output:** Observations filtered by sensitivity dial → HIL (human-in-the-loop) queue.
- **API access:** NONE. Strict isolation.
- **Biology:** Macrophages are patrol cells that operate inside the body, engulfing pathogens and presenting them to other immune cells.

### Ouroboros Cell — O1 (External Research + Self-Improvement)
- **Role:** Hunter, gatherer, self-improver. The snake consuming its own tail — cyclical self-improvement.
- **Capabilities:** External research (arXiv, Semantic Scholar), CDSFL network data gathering, anomaly-targeted evidence acquisition.
- **Pipeline stage:** Between rounds (Codex improvement over Stage 2 insertion).
- **Output:** Candidate claims with full provenance, subject to normal PE gates.
- **API access:** Structured academic fetch only for Exp 39.

## Key Design Decisions

### Between-Round Placement (Codex)
Ouroboros runs *after* each round, not during Stage 2. Stage 2 assumes the batch already exists. Creating claims during verification is architecturally confused. Between-round placement gives deterministic round execution with one-round lag for external research.

### Disjoint Evidence Paths (Both Models)
If Ouroboros proposes based on a paper, B-Cell must verify via computation, execution, or a strictly different source. Prevents epistemic closure / self-confirming loops.

### Provenance Schema (Codex)
External-origin claims must carry: `origin_type`, `source_ref`, `retrieval_query`, `retrieved_at`, `source_hash`, `source_diversity`. Mandatory `falsification_debt: high` flag.

### Macrophage Interface Expansion
Current `observe()` receives only verdicts, triaged findings, timings. Must be extended to include:
- Source provenance metadata (origin tags on claims)
- PE gate pass/fail statistics
- Ouroboros activity metrics

### Anti-Corruption Rules
1. Origin tagging on all external claims
2. Source diversity minimum enforced
3. No same-paper-for-propose-and-verify
4. Shadow replay before promotion
5. No automatic writeback from fetched evidence into live config

## Self-Healing vs Self-Improving

| | Self-Improving | Self-Healing |
|---|---|---|
| **What** | System adds validated knowledge | System corrects structural pathologies |
| **Actor** | Ouroboros (evidence gathering) | Macrophage (detection) → HIL (correction) |
| **Autonomy** | Semi-autonomous, PE-gated | Diagnosis autonomous, correction requires HIL |
| **Example** | Ouroboros fetches convergence lit → B-Cell verifies → pipeline adopts | Macrophage detects 0% gate rejection → flags immune deficiency → HIL investigates |

## P-Pass Results (5 passes)

| Pass | Falsifier | Assessment | Amendment |
|---|---|---|---|
| 1 | One-round lag from between-round placement | Acceptable (Macrophage monitors real-time) | None |
| 2 | Macrophage can't see provenance or PE outcomes | Valid defect | Extend Macrophage `observe()` interface |
| 3 | DC triage designed for model findings, not external research | Valid | Add Ouroboros-origin patterns to DC config |
| 4 | Shadow cells consume load-bearing resources | Valid | Hard-cap budgets, run after main round |
| 5 | Source monoculture in Ouroboros | Valid | `source_diversity` metric in provenance; Macrophage monitors |

All passes produce amendments, none produce rejection. Architecture survives.

## Exp 39 Scope

- Both cells: **shadow mode**, zero pipeline effect
- Ouroboros MVP: target selection + metadata fetch + provenance packet + shadow replay log
- Hard caps: max 3 queries/round, max 2 candidate claims
- Run after main round completes
- Macrophage: current monitoring implementation + expanded interface
- Estimated diff: ~300-400 LOC new/moved

## Implementation

Refactor `bench/ouroboros_cell.py`:
1. Rename/refactor → `bench/macrophage_cell.py` (keeps monitoring + microglia logic, gets expanded `observe()`)
2. Create new `bench/ouroboros_cell.py` for O1 external research cell (between-round, provenance, shadow mode)
3. Add provenance fields to `Finding` schema in `bench/dm/_types.py`
4. Wire Ouroboros into between-round hook in `bench/immune_agents.py`
5. Update `bench/exp39_configs/39_C_macrophage.json` and `39_J_microglia.json`

## Confer Log Summary

### Gemini 3.1 Pro
- Split is "architecturally mandatory"
- Macrophage should write "epistemic stress score" that pipeline router reads
- Anti-corruption: demand disjoint evidence paths
- Ouroboros MVP: anomaly detection + fetch_paper_metadata + log to disk
- Hardcode `shadow_mode = true`, mock/dry-run API for safety

### Codex 5.3
- Split by trust boundary, not by enum names
- Ouroboros should be between-round research step, not Stage 2
- External claims need 6 provenance fields + different verifier evidence path
- Macrophage must monitor PE behaviour and Ouroboros provenance patterns
- Minimal split now is practical; full live Ouroboros is not
