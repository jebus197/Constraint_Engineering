# Experiment 38 Confer Synthesis — 9 April 2026

Two confers (cross-model adversarial review sessions) were dispatched to **Codex GPT-5.4** (OpenAI via OpenRouter) and **Gemini 3.1 Pro** (Google) under the full CDSFL (Constraint-Driven Synthesis and Falsification) 4-layer schema.

## Overall Verdict

Both models confirm the Exp 38 plan is **conceptually sound**. The runner implementation contains **critical bugs** that must be fixed before the experiment can produce trustworthy results.

## Converged Findings (Both Models)

S* is the break-even threshold for fix quality below which a fix does net harm; nu_b is baseline re-injection rate; nu_f is fix-induced re-injection rate; q is effective detection rate; R is residual risk.

| # | Finding | Classification | Status |
|---|---------|---------------|--------|
| 1 | **Regression gate doesn't test modified artifact** — pytest runs against REPO_ROOT, not the temp-modified source | HARD | Fix: copytree isolation |
| 2 | **Tristate ESCALATE broken** — tool unavailability returns score=1.0 ("skipped") instead of ESCALATE | HARD | Fix: structured gate returns |
| 3 | **Hardcoded S\* inputs** — nu_b=0.05, nu_f=0.20, q=0.5, R=0.5 regardless of actual finding | HARD | Fix: wire from per-finding metadata |

## Gemini-Specific Findings

| # | Finding | Classification | Status |
|---|---------|---------------|--------|
| 4 | **E geometric mean gives graded gates veto power** — any e_i=0 collapses all of E | HARD | Fix: weighted arithmetic mean |
| 5 | **Ruff scoring penalises identical states** — ratio formula counts pre-existing violations | HARD | Fix: delta-based penalty |

## Codex-Specific Findings

| # | Finding | Classification | Status |
|---|---------|---------------|--------|
| 6 | **SEARCH/REPLACE parser regex-fragile** — delimiter content in payloads breaks parsing | HARD | Fix: line-state machine |
| 7 | **S\* edge cases** — nu_f=0 and nu_b=1 treated identically; S\* may exceed [0,1] | HARD | Fix: explicit branching |
| 8 | **Python encoding misaligned** — g2 still says import, g3/e1/e5 not in runner | MEDIUM | Fix: update encoding |
| 9 | **Directive sigma/nu residue** — CORROBORATION section says sigma/nu | MEDIUM | Fix: update wording |

## Composability Check

All findings compose. No mutual exclusivity detected:
- Gemini arithmetic mean + Codex structured gate returns = complementary
- Both copytree sandbox proposals = convergence (same fix)
- Codex line-state parser = independent addition (Gemini had no parser finding)

## Priority Fix Order

1. Regression gate sandbox (copytree isolation)
2. SEARCH/REPLACE parser (line-state machine)
3. E aggregation formula (arithmetic mean)
4. Ruff delta scoring
5. nu clamp + R_k loop closure
6. ESCALATE for zero/unavailable gates
7. S\* edge cases + hardcoded values
8. Directive sigma/nu residue
9. Python encoding alignment

## Cell Type Architecture

- **Gemini:** Sound, no finding
- **Codex:** Sound as design target; claims like "no runner changes needed for new domain" are aspirational, not current implementation truth

## Implementation Gaps (Codex, 9 items)

1. Dynamic expert encoding loader
2. Gate registry / dispatcher
3. Baseline capture integration point
4. Per-finding model parameters (R_old, eta, d, p, nu_b, nu_f)
5. R_k persistence to registry
6. ESCALATE/UNVERIFIED in registry + telemetry
7. Isolated repo execution for all side-effectful gates
8. Config additions (encoding_path, gate timeouts, tool availability policy)
9. Immune/brain/endocrine integration with S_k results

## Source Files

- Gemini: `bench/logs/confer_exp38_plan/exp38_plan_gemini_20260409T223546Z.txt` (14,455 chars)
- Codex: `bench/logs/confer_exp38_plan/exp38_plan_cx_20260409T223724Z.txt` (31,501 chars)
