# Experiment 39 Infrastructure Build Summary

**Date:** 12 April 2026
**Branch:** `exp39-experimental`
**Commit:** `b0f33d7`
**Tests:** 762 passing (3 independent runs)

## Experiment 38 Fixes Folded into the Runner

### 1. D1-B Churn Stall Convergence

**File:** `bench/reference_runner.py`

D1-B adds a convergence detection channel that recognises finding space depletion earlier by using sustained churn as corroborating evidence alongside gamma.

Gamma measures cumulative finding depletion via the Duane NHPP — as novel discoveries dry up over cumulative effort, gamma rises. Rho measures the same phenomenon per-round — the ratio of novel to raw findings. When rho stays below threshold (churn), that is the per-round view of the same depletion gamma is measuring cumulatively. They are two statistical lenses on one underlying process: the finding space is exhausted.

The D1-B conjunction — sustained churn AND gamma above threshold — requires that both lenses agree before declaring convergence. If gamma is high but rho occasionally spikes (a genuine novel finding appears), the churn counter resets and convergence is not declared. If rho is persistently low but gamma hasn't risen (early rounds, insufficient cumulative data), convergence is not declared either.

Two-tier design: advisory (gamma >= 0.30 + sustained churn) means convergence is likely. Terminate (gamma >= 0.45 + sustained churn) means convergence is confirmed through both measures. This is a faster path to the same conclusion the existing static stall detector would eventually reach, not a different conclusion. Previously churn only triggered phase transitions but never contributed to convergence decisions.

### 2. P4 TARGET_FILE

**Files:** `bench/dm/_types.py`, `bench/runner_core.py`

Every finding now carries an explicit `target_file` field identifying which file the finding is about. All four parser paths (JSON array, JSON object, tuple, and marker/block) now extract or infer this field. If the model doesn't state it explicitly, the parser regex-matches file paths from the description and proposed fix text.

Load-bearing for fix verification — you can't verify a fix if you don't know what file it targets.

### 3. LLM-Primary Classifier

**File:** `bench/immune_agents.py`

In the software domain, the LLM classifier now wins over regex for claim type classification. Previously regex was primary and the LLM only overrode at high confidence. Exp 38 showed only 15% agreement between them, with regex consistently wrong on software-specific patterns. Non-software domains still use the confidence-threshold approach.

### 4. Gemini OpenRouter Switch

**File:** `bench/experiment_11_orchestrator.py`

Gemini dispatch moved from the Google GenAI API to OpenRouter. Model ID: `google/gemini-3.1-pro-preview`. Added `extra_body` support to pass `reasoning.effort: "high"` through the OpenRouter API. The deprecated `google-generativeai` package was uninstalled.

### 5. Statistics Domain Configs

**Files:** `bench/cdsfl_registry/domains/statistics.toml`, `bench/cdsfl_registry/domains/immune/statistics.toml`, `bench/cdsfl_registry/schema.toml`

New TOML configs for the statistics specialist cell. Defines verification requirements (hypothesis tests, effect sizes, distribution checks) and immune pipeline parameters (claim patterns, CT prompt template, false positive patterns). Six new parameters added to the PE schema.

## Experiment 39 Infrastructure

### 6. Master Config

**File:** `bench/exp39_config.json`

Defines all 14 sub-experiments with types, dependency graph, execution order, and gate policy (`fail_fast`). The dependency DAG encodes which sub-experiments must complete before others can start.

### 7. Sub-Experiment Configs

**Directory:** `bench/exp39_configs/`

Each config specifies: round limits, wall clock cap, convergence criteria (primary/secondary/fail), artifact schema (required output fields), domain, burst mode, and specialist cell definitions.

| Sub-exp | Name | Rounds | Wall Clock | Domain | Type |
|---------|------|--------|------------|--------|------|
| 39-0 | Infrastructure Gate | 8 | 1h | software | gate |
| 39-A | Mathematics Specialist | 15 | 4h | mathematics | research |
| 39-B | Expert Encodings S_k | 12 | 3h | software | research |
| 39-C | Macrophage Admissibility | 10 | 2h | software | research |
| 39-D | Composition Test | 6 | 1h | software | integration |
| 39-E | Statistics Specialist | 12 | 3h | statistics | research |
| 39-F | CS/Software Specialist | 12 | 3h | software | research |
| 39-G | Biology Specialist | 10 | 2h | biology | research |
| 39-H | Information Science | 10 | 2h | information_science | research |
| 39-I | Cross-domain Synthesis | 10 | 2h | software | integration |
| 39-J | Microglia | 10 | 2h | software | research |
| 39-K | Physics Shadow | 6 | 1h | physics | shadow |
| 39-L | Chemistry Shadow | 6 | 1h | chemistry | shadow |
| 39-M | Engineering Shadow | 6 | 1h | engineering | shadow |

### 8. Sequencer Script

**File:** `bench/launch_exp39.py`

Reads the master config, resolves dependencies via topological sort (Kahn's algorithm), and launches sub-experiments sequentially via `reference_runner.py run --config <path>`.

**Features:**
- `--dry-run`: show execution plan without running
- `--only 39-D`: run 39-D plus all transitive dependencies (auto-pulls 0, A, B, C)
- `--skip 39-K 39-L 39-M`: exclude specified sub-experiments
- `--preflight`: connectivity check only
- Gate fail-fast: failed required gate skips all downstream dependents
- Per-experiment timeout: wall clock cap + 5 min grace
- JSON sequence report: `bench/logs/exp39_artifacts/`

## Remaining Work

1. Build Expert Encodings S_k integration (wire into immune pipeline, ~150-200 LOC)
2. Add HIL phase gate to burst mode transitions (~30-50 LOC)
3. Build Macrophage shadow-mode prototype (~200-300 LOC, log only)
4. Write tests for new sub-experiment infrastructure
5. Run 39-0 (infrastructure gate), then 39-A
