# Immune Agent Architecture for Run 9

**Date:** 2 April 2026, 21:44 BST
**Status:** Built, tested, wired (observation-only for Run 8, load-bearing for Run 9)
**Tests:** 23 new tests, 450 total passing
**Commit:** Part of Run 9 infrastructure build session

## Biological Mapping

| Cell Type | CDSFL Role | Tools | Stage |
|-----------|-----------|-------|-------|
| **Dendritic Cell** | Triage: classify findings by claim type | regex patterns | Stage 1 (sequential) |
| **Cytotoxic T-Cell** | Code FFF: read source, verify bugs exist | claude CLI + Bash/Grep/Read | Stage 2 (parallel) |
| **B-Cell** | Math/Logic/Stats: adaptive multi-tool verification | SymPy + z3 + statsmodels | Stage 2 (parallel) |
| **NK Cell** | Pattern memory: dedup + known FP matching | _finding_similarity + FP DB | Stage 2 (parallel) |
| **Helper T-Cell** | Synthesis: confidence-weighted voting | aggregation logic | Stage 3 (sequential) |
| **Regulatory T-Cell** | Meta-verification: prevent autoimmune | pipeline health checks | Stage 3 (sequential) |

## Pipeline Architecture

```
findings from round N
        |
        v
+-------------------+
| DENDRITIC CELL    |  Stage 1: classify claims (~1s)
| 5 claim types     |  MATH, LOGIC, STATS, STRUCTURAL, BEHAVIORAL
+--------+----------+
         |
         v (parallel)
+--------+--------+---------+
| CYTOTOXIC T     | B-CELL  | NK CELL   |  Stage 2: verify (~30-60s)
| claude CLI FFF  | SymPy   | dedup     |
| reads source    | z3      | FP DB     |
| kills false     | stats   | anomaly   |
| positives       | switch  | detect    |
+---------+-------+----+----+-----+-----+
          |            |          |
          v            v          v
+-------------------+
| HELPER T-CELL     |  Stage 3a: synthesize verdicts (~1s)
| weighted voting   |  asymmetric: reject needs 0.6+, confirm needs 0.4+
+--------+----------+
         |
         v
+-------------------+
| REGULATORY T-CELL |  Stage 3b: meta-check (~1s)
| autoimmune check  |  if rejection rate > 50%: override, pass everything
| per-model bias    |  prevents pipeline from destroying its own input
+--------+----------+
         |
         v
   verified findings -> next round context
```

## P-Pass (4 falsification attempts)

1. **Distinctness of roles:** DC classifies forward (routing), NK checks backward (memory). B-Cell works symbolically (SymPy/z3), CT works empirically (file reading). Genuinely orthogonal tools and functions.

2. **6 agents for ~10 findings:** Each agent processes ALL findings through its lens, not one each. Correct parallelism on same data, different analysis angles.

3. **M1 8GB feasibility:** Only CT is expensive (1 API call, network-bound). B-Cell = Python subprocess (1-10s). Others = pure Python (<1s). Observed 6 agents stable on this hardware.

4. **Granularity justified:** 500M years of evolutionary selection converged on specialised immune cells. Persistence of specialisation implies it outperforms generalisation against diverse threats.

## New Tools Integrated

| Tool | Version | Cell | Run 9 Use | Bench Run 2 Use |
|------|---------|------|-----------|-----------------|
| z3-solver | 4.16.0 | B-Cell | Logical invariants | Formal verification tasks |
| statsmodels | 0.14.6 | B-Cell | Statistical claims | Hypothesis testing tasks |
| uncertainties | 3.2.3 | B-Cell | Error propagation on gamma/omega | Measurement tasks |
| SymPy | 1.14.0 | B-Cell | Mathematical claims (existing) | Mathematical tasks |

All tools verified in Python 3.13 at `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`.

## B-Cell Class Switching

When SymPy returns UNCERTAIN on a mathematical claim, the B-Cell class-switches to z3 as a fallback. This mirrors biological B-cell class switching (IgM -> IgG based on infection type):

```python
if tf.claim_type == ClaimType.MATHEMATICAL:
    v = _verify_sympy(tf.extracted_claim)
    if v.verdict == "UNCERTAIN":
        v2 = _verify_z3(tf.extracted_claim)
        if v2.verdict != "UNCERTAIN":
            v = v2  # class-switched
```

## NK Cell Memory (seeded from Run 7b)

Known false-positive patterns:
- Codex `@dataclass` decorator hallucination (8 occurrences in Run 7b, 7% of Codex output)
- Severity inflation detection: findings with severity > 0.95 after round 5

This memory persists across runs and grows with each session.

## Asymmetric Verdict Thresholds

False negatives (suppressing a real bug) are worse than false positives (letting a questionable finding through). The Helper T-Cell enforces this asymmetry:
- **Rejection threshold:** 0.6+ net confidence required
- **Confirmation threshold:** 0.4+ net confidence required
- **Default (no verdicts):** UNCERTAIN — finding passes through

## Regulatory T-Cell Checks

1. Overall rejection rate > 50% -> autoimmune flag
2. All findings from one model rejected -> systematic bias flag
3. Autoimmune override: when flagged, ALL findings pass through regardless

## Run 9 Activation

Two flags in `run_baseline_confer.py`:
```python
immune_result = run_immune_pipeline(
    findings, prior_findings, source_paths,
    observation_only=False,   # was True (Run 8)
    ct_enabled=True,          # was False (Run 8)
)
```

## Expected Run 9 Impact

- **Churn reduction:** 76% of findings were churn in Run 7b. Quality gate + immune pipeline should eliminate most before context injection.
- **Time savings:** Fewer findings in context -> shorter model responses -> faster rounds.
- **Quality improvement:** Verified findings only enter context, so models see higher-signal input.
- **Overhead:** 35-65 seconds per round (12-31% of Run 7b's 52 minutes).

## Files

- `bench/immune_agents.py` — 630 lines, full pipeline
- `bench/verification_utils.py` — updated with z3/statsmodels + Python 3.13 discovery
- `bench/run_baseline_confer.py` — immune pipeline wired in
- `bench/tests/test_immune_agents.py` — 23 tests
