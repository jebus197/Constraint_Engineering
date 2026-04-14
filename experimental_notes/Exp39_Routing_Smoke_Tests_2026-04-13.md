# Experiment 39 Routing Smoke Tests — Fingerprint-Aware Decomposition & DeepSeek Specialist Role

**Date:** 13 April 2026 22:23 BST  
**Context:** Post-confound fixes, pre-relaunch from R2

---

## Changes Tested

### 1. Fingerprint-Aware Decomposition (`run_exp17_immune.py`)

Replaced static hardcoded model rules with data-driven decisions:

| Old Rule | New Rule |
|----------|----------|
| `DeepSeek: always decompose` | Use `max_successful_prompt_chars` from fingerprint (90% margin) |
| `CC2: decompose > 200K` | Use observed prompt limit (418K effective) |
| All others: `> 80K` threshold | Fingerprint-first, static fallback for models without data |

**Decomposition matrix (gate payload ~59K):**

| Model | Fingerprint Limit | Decision |
|-------|------------------|----------|
| CC2 | 465K → 418K eff. | MONOLITHIC |
| ChatGPT | 465K → 418K eff. | MONOLITHIC |
| Codex | 465K → 418K eff. | MONOLITHIC |
| DeepSeek | No data → 80K fallback | MONOLITHIC (59K < 80K) |
| Gemini | 465K → 418K eff. | MONOLITHIC |

### 2. DeepSeek Panel Routing Change

Switched from `deepseek-reasoner` (direct API) to `deepseek/deepseek-r1-0528` (OpenRouter).

| Route | Time | Output | R_k | CoT:Output |
|-------|------|--------|-----|-----------|
| Direct API (`deepseek-reasoner`) | 121.5s | 1,239 chars | YES | 14:1 |
| OpenRouter (`deepseek-r1`) | 105.9s | 2,705 chars | YES | hidden |
| OpenRouter (`deepseek-r1-0528`) | 25.2s | 1,615 chars | YES | hidden |

R1-0528: 5x faster, comparable quality. Selected for panel.

### 3. DeepSeek Reasoner — Deep Verification Specialist

Tested direct API in new specialist role with real finding from R0:

- **Input:** Codex F001 (source_env parsing bug, severity 0.82)
- **Output:** 3,435 chars / 75.7s / 10,002 chars reasoning (3:1 ratio)
- **Key finding:** Caught R_k computation error in original — Codex claimed 0.32, correct value is 0.399 (S_k multiplication order error)
- **Verdict:** CORROBORATED with independent numerical verification

### 4. Ouroboros Real API Queries

Replaced `shadow_mock` in `_fetch_metadata()` with real arXiv and Semantic Scholar calls. Both verified working. Ouroboros remains in shadow mode.

---

## Full Panel Smoke Test

| Model | Route | Time | Chars | R_k | Finding ID | Falsification |
|-------|-------|------|-------|-----|-----------|--------------|
| CC2 | CLI pipe | 46.6s | 4,609 | YES | YES | YES |
| ChatGPT | OpenRouter | 23.8s | 4,733 | YES | YES | YES |
| Codex | OpenRouter | 20.0s | 4,407 | YES | YES | YES |
| Gemini | OpenRouter | 20.7s | 2,525 | YES | YES | YES |
| DeepSeek (direct) | DeepSeek API | 121.5s | 1,239 | YES | YES | YES |
| DeepSeek (OR r1) | OpenRouter | 105.9s | 2,705 | YES | YES | YES |
| DeepSeek (OR 0528) | OpenRouter | 25.2s | 1,615 | YES | YES | YES |

**100% R_k adoption. 100% falsification compliance.**

---

## Killer T-Cell Proposal — P-Pass Analysis

**Proposal:** Repurpose DeepSeek direct API as security scanner using VX-Underground/VirusShare/MalwareBazaar.

**P-pass findings:**

1. **Biological mapping inverted.** CD8+ T-cells detect internal compromise (MHC Class I antigen presentation), not external threats. External database scanning maps to innate immunity (TLR-PAMP matching).
2. **Wrong databases.** VX-Underground/VirusShare/MalwareBazaar are binary malware archives. Cannot hash-match Python source. Tools that would help: GuardDog (YARA source patterns), OSV.dev (known vulnerabilities).
3. **Pipeline already has CT cell.** Cytotoxic T-Cell (Stage 2a) already implemented in `immune_agents.py`. Pipeline has 9 components; shadow cells not yet proven.

**Resolution:** Deep verification specialist role (Option A) + security tools in endocrine layer (Option B, deferred). No new immune cell types.

---

## Pre-Relaunch Checklist

- [x] Fingerprint-aware decomposition verified (all 5 models)
- [x] DeepSeek panel slot → R1-0528 via OpenRouter
- [x] DeepSeek Reasoner specialist role validated
- [x] Ouroboros real API queries verified
- [x] Macrophage + Ouroboros remain shadow (calibration)
- [x] 793 tests pass
- [ ] Resume Exp 39-0 from R2
