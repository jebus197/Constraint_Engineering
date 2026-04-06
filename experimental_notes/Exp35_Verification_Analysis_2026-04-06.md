# Experiment 35 — Verification Analysis

**Date:** 6 April 2026, 20:32 BST
**Target:** `bench/cdsfl_registry/engine.py` (PolicyEngine)
**Method:** Programmatic verification (AST analysis, text search, schema cross-reference) + FFF

## Summary

| Metric | Value |
|--------|-------|
| Raw findings | 533 |
| Canonical entries | 79 |
| Unique verified issues | 18 |
| Refuted | 2 (C0029, C0039) |
| Empty/malformed | 17 (parser artifacts) |
| Verdict-only entries | 2 (C0066, C0075) |
| Dedup ratio | 4.4:1 |
| Confirmation rate (in-experiment) | 11.4% (9/79) |
| Merge rate | 0% (0 merges in 23 rounds) |

## Verified Issues by Severity

### HIGH (3 issues — correctness bugs with silent failure modes)

#### 1. VALIDATE_UNIDIRECTIONAL
**Findings:** C0002, C0007, C0011, C0023, C0038, C0056, C0057, C0073 (8 duplicates)
**Evidence:** `validate()` computes `registry_hard_X - schema_hard_X` but never `schema_hard_X - registry_hard_X`. HARD constraints in schema but not in registry will be silently unenforced.
**Verification:** Regex search of validate function body confirms no `schema_hard` - `registry_hard` set difference.

#### 2. NO_TYPE_VALIDATION
**Findings:** C0003, C0019, C0021, C0044, C0045, C0063, C0067, C0074 (8 duplicates)
**Evidence:** No `isinstance`, no type comparison, no `allowed_values` check exists in `validate()`, `query()`, or `get_parameter()`. A TOML value of wrong type passes silently.
**Verification:** Text search for isinstance/type check in validate function body returns zero matches outside import-related lines.

#### 3. MIN_LAYER_NOT_ENFORCED
**Findings:** C0018, C0026, C0062 (3 duplicates)
**Evidence:** `min_layer` loaded into `ParameterDef` but never compared against actual layer source in any validation path.
**Verification:** `min_layer` appears only in schema loading (L161-163) and dataclass definition (L86). No enforcement logic exists.

### MEDIUM (6 issues)

#### 4. LAYER4_MERGE
**Findings:** C0001, C0006, C0013, C0076 (4 duplicates)
**Evidence:** `_compute_provenance()` L239-246: Layer 4 iterates `model_config` but never calls `_deep_merge(current, model_config)`. Layers 2+3 both merge.
**Impact:** No wrong results today (Layer 4 is last). Maintenance hazard.

#### 5. PROVENANCE_OVERWRITE
**Findings:** C0012, C0022, C0036 (3 duplicates)
**Evidence:** No value comparison in `_compute_provenance`. Provenance reports source layer for all keys regardless of whether value changed.
**Impact:** Misleading provenance; effective values correct.

#### 6. LOAD_SCHEMA_NO_DEFAULT_CHECK
**Findings:** C0004, C0009, C0025, C0046, C0060 (5 duplicates)
**Evidence:** `load_schema()` checks `type`/`constraint_class`/`min_layer` strings only. Never inspects `default` field type.
**Impact:** Current schema.toml is consistent. Latent defect.

#### 7. DIFF_MISSING_TASK
**Findings:** C0015, C0030, C0037, C0068, C0078 (5 duplicates)
**Evidence:** `diff_policies(self, domain_a, domain_b, model_a, model_b)` — no `task_id` parameter.
**Impact:** Cannot diff task-level policies. Interface gap.

#### 8. ERROR_HANDLING_ASYMMETRY
**Findings:** C0010 (1 finding)
**Evidence:** `registry.py` L271 raises `FileNotFoundError` for missing model. `engine.py` L242 silently skips.
**Impact:** Inconsistent behavior depending on code path.

#### 9. UNKNOWN_PARAMS_NOT_CAUGHT
**Findings:** C0027 (1 finding)
**Evidence:** No validation that TOML keys exist in schema. Typos silently ignored.
**Impact:** Silent misconfiguration.

### LOW-MEDIUM (1 issue)

#### 10. DIFF_NO_DEFAULTS
**Findings:** C0024, C0055, C0061, C0077 (4 duplicates)
**Evidence:** `diff_policies()` uses `load_effective_policy()` which doesn't inject schema defaults. Misleading diffs.

### LOW (8 issues)

| # | Issue | Findings | Notes |
|---|-------|----------|-------|
| 11 | VIOLATIONS_DEAD | C0020, C0052 | `PolicyResult.violations` never populated |
| 12 | UNUSED_IMPORTS | C0005 | Path, Sequence, tomllib + 2 possibly re-exported |
| 13 | QUERY_DOUBLE_LOAD | C0014, C0041, C0059 | Performance only |
| 14 | FLATTEN_SCHEMA_HEURISTIC | C0017, C0040, C0072, C0079 | Theoretical fragility |
| 15 | ENUM_TYPE_UNUSED | C0004, C0058 | Dead type category |
| 16 | SCHEMA_SEMANTIC_OVERLAP | C0064 | Design choice |
| 17 | SCHEMA_INCOMPLETE | C0008 | Partially confirmed |
| 18 | LIST_PARAMS_FILTER | C0042 | Minor edge case |

## Refuted Claims

| ID | Claim | Reason |
|----|-------|--------|
| C0029 | `validate()` threshold check excludes `int` | `int` IS in the `("int", "float")` tuple. Claim is factually wrong. |
| C0039 | `sympy_verification` default not in `allowed_values` | `"auto"` is in `["auto", "mandatory", "disabled"]`. Self-corrected mid-description. |

## Process Metrics

- **Convergence:** Gate never triggered. `open_ch=31` permanent blocker. γ=0.650 (depletion passed).
- **Extension stall detector** terminated the experiment at R22.
- **Churn:** 533→79 canonical (6.7:1). Models re-describing, not resolving.
- **Confirmation:** 9/79 (11.4%). Zero merges.
- **Per-model:** DeepSeek 25, CC2 15, ChatGPT 14, Codex 13, Gemini 12 canonical findings.

## Convergence Gate Analysis

4/5 gate conditions passed consistently from R17+:
1. `round >= 12` — PASS from R12
2. `open_ch == 0` — **PERMANENT FAIL** (open_ch=31)
3. `novel <= 2` — PASS from ~R17
4. `contested == 0` — PASS from ~R17
5. Gamma gate — PASS (γ=0.650 > hard threshold)

Root cause: 11.4% confirmation rate + 0% merge rate + no CLOSED status = findings accumulate faster than they resolve.
