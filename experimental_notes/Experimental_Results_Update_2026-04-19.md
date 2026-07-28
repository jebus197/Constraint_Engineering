# Experimental Results Update — 19 April 2026

`docs/EXPERIMENTAL_RESULTS.md` previously ended at the HIL Comparison Experiments (C1, C3, C4, C5) dated 4 April 2026. Eleven new entries have been appended, covering the period from 5 April 2026 through 19 April 2026.

## Summary of Appended Entries

| # | Entry | Date(s) |
|---|-------|---------|
| 1 | Experiment 29 — Three-Layer Schema Integration Test | 5–7 Apr 2026 |
| 2 | Mathematical Model Audit | 8 Apr 2026 |
| 3 | Semantic Novelty Fix | 9 Apr 2026 |
| 4 | Immune Cell Type Architecture | 9 Apr 2026 |
| 5 | Tranches A, B, C — B-Cell Tool Integration | 13–14 Apr 2026 |
| 6 | Experiment 36 — CC2 Agent Performance Evaluation | 8–12 Apr 2026 |
| 7 | Stage 6 Literature-Calibrated Extension | 14 Apr 2026 |
| 8 | §17 Feedback Channel Implementation | 15 Apr 2026 |
| 9 | §18 Divergence Directive Implementation | 15–16 Apr 2026 |
| 10 | Experiment 40 Stage 3 Closure | 17–18 Apr 2026 |
| 11 | Documentation Sync and Architecture Refresh | 18–19 Apr 2026 |

## Entry Highlights

### Experiment 29 — Three-Layer Schema Integration Test (5–7 April 2026)

The three-layer schema (Meta structured prompting → CDSFL constraints
→ conversational default with ITC fallback) was validated as the
default operating mode for the five-model panel. Two load-bearing
patterns were observed:

- **Framing confound**: pre-announcing a model's role (adversarial vs.
  supportive) anchors outputs to that framing. Fix: neutral framing
  with role emerging from the constraint set.
- **Long-session degradation**: models operating beyond ~18 hours
  continuous dispatch conflate earlier and later term definitions.
  Fix: ITC restarts with fresh context + fingerprint-informed scope.

### Mathematical Model Audit (8 April 2026)

Results of the audit:

- Internal consistency: 25/25 claims checked.
- All 5 previously noted gaps confirmed.
- 2 claims disputed (R² = 0.985 coverage fit not reproducible;
  z = 3.63 significance not verifiable from raw data).
- ρ threshold flagged as requiring empirical calibration.

The most consequential output was the derivation of the unified
recursive state equation `R_k(i)`:

```
R_k(i) = R_det · (1 − ν_k) + ν_k
R_det  = R_k(i−1) · (1 − q_ik) / (1 − q_ik · R_k(i−1))
ν*     = q · R
```

This replaced the earlier `C(n)` notation as the canonical claim-state
representation.

### Semantic Novelty Fix (9 April 2026)

Before: γ and ρ were computed against finding IDs — a model could
rename a finding and have it counted as novel.

After: `_finding_similarity()` compares finding content (verdict,
evidence, proposed change). Churn rate dropped on identical re-runs
from 84.5% to approximately 65%.

### Immune Cell Type Architecture (9 April 2026)

Seven cell types formalised:

| Cell | Role |
|------|------|
| Dendritic | Intake and dispatch |
| Cytotoxic T | Challenge |
| Natural Killer | Edge stress-testing |
| Regulatory T | Admissibility enforcement |
| B-Cell Complex | Specialist domain dispatch |
| Macrophage | Cleanup and forensic trace |
| Ouroboros (O1) | Self-reference |

Uniform composition law:

```
S_k = A · E
A   = Π g_j              (product of gate values)
E   = Σ w_m · e_m        (weighted evidence aggregate)
```

### Tranches A, B, C (13–14 April 2026)

- **Tranche A**: 16 domains wired (SymPy, z3, NumPy, SciPy, pint,
  uncertainties, astropy, mpmath, AST, pytest, ruff, mypy, bandit,
  PuLP, statsmodels, CrossHair).
- **Tranche B**: +4 domains (RDKit, Biopython, scikit-learn,
  NetworkX).
- **Tranche C**: shadow-only, held for future calibration.
- **Final active at commit `6580737`**: 18 active + 2 delegated.

### Experiment 36 — CC2 Agent Performance (8–12 April 2026)

4-phase plan (A resume, B reference runner, C Bench Run 2, D docs).
Agent performance findings:

| Agent | Status |
|-------|--------|
| Agent 1 | Broken (schema non-conformance) |
| Agents 2–4 | Under-routing (not escalating marginal cases) |
| Agent 5 | Over-relied-upon |

Under-routing was the dominant failure mode. Fix priorities
identified for Experiment 37.

### Stage 6 Literature-Calibrated Extension (14 April 2026)

Two-dimensional novelty introduced:

```
η_combined = η_int · (1 − c_ext · (1 − ν_k))
```

ν_k design iterated over 2 confer rounds producing 12 corrections.
Shadow calibrator hooked into live metric. Mathematical appendix now
1991 lines.

### §17 Feedback Channel (15 April 2026)

`bench/dm/_feedback.py` (533 lines). Action precedence:

```
REFUTED  >  ADMISSIBILITY FAIL  >  NEAR-DUPLICATE  >  R_k INCONSISTENT
```

For any finding, only the first matching action is rendered in the
following round's feedback slot. Feedback is scoped per model and
bounded by `top_k` and `max_chars`.

### §18 Divergence Directive (15–16 April 2026)

`bench/dm/_divergence.py` (443 lines). Five divergence dimensions
(mechanism, assumption, scope, timescale, tradeoff). Jaccard
threshold 0.85. Channel reassignment table:

| Channel             | eta_int_modulator |
|---------------------|-------------------|
| Compliant           | 1.00              |
| Engaged but failed  | 0.85              |
| No engagement       | 0.70              |
| Isomorphic-only     | 0.60              |

The accepted design applies the modulator to η_int (not R_k),
preserving independence between the severe-testing and
bold-conjecture arms.

### Experiment 40 Stage 3 Closure (17–18 April 2026)

- Phase A commit: `8b8682d`
- Phase B commit: `bdfc93a`
- Documentation sync: `6580737`
- **Tests passing: 1250 / 1250**
- Residual: test `1E.3` (gated) and `1E.10` (deferred to Exp 54)

Stage 3 closure establishes that formal documents, mathematics, and
code describe the same object without drift. Empirical validation of
§17 and §18 hypotheses is scheduled for the 2×2 factorial in
Experiments 41–54.

### Documentation Sync and Architecture Refresh (18–19 April 2026)

Full sweep covering seven documents: `FOUNDERS_NOTES.md`,
`SHORTCUTS.md`, `ARCHITECTURE.md`, `cdsfl_topology_formal.md`,
`EXTENDED_RATIONALE.md`, `EXPERIMENTAL_RESULTS.md`, `PAPER.md`. Each
substantive batch produced a TTS `.txt` mirror at
`~/Desktop/CDSFL_tts/` and a markdown mirror at
`experimental_notes/`, per the unification directive.

## Closing Note

The eleven new entries bring `EXPERIMENTAL_RESULTS.md` into alignment with the April 2026 state of the project. Each entry includes dates, models, artefacts, and, where applicable, raw data and analysis references. Prior entries remain unchanged. The Planned Experiments section is unchanged pending the outcome of the 2×2 factorial in Experiments 41–54.
