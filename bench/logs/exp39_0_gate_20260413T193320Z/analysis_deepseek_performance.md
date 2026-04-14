# DeepSeek R1-0528 Performance Analysis — Exp 39-0

## Executive Summary

DeepSeek was decomposed every round (6/6) due to a missing fingerprint field, making it the only model decomposed in all rounds. The decomposition produced severe 0-char chunk outputs in 4 of 6 rounds (67%), yet the synthesis turn still generated coherent, high-quality analysis every round. Output quality was genuine but suffered from two critical pipeline problems: (1) the parser extracted far fewer findings than DeepSeek actually produced, and (2) DeepSeek re-submitted the same findings across rounds because it never received confirmation that they had been registered. No other model confirmed any DeepSeek finding. The reasoning/thinking tokens from R1-0528 were not captured by the dispatch layer.

## 1. Per-Round Assessment

**Round 0:** 397s, both chunks 0-char, synthesis 20,209 chars. Parsed 1 of 2 actual findings. Content excellent — two well-structured findings (fingerprint type mismatch, JSON bracket-counting fragility) with full FFAFP, concrete traces, proposed fixes, falsification, and quantitative corroboration. Codex did 3 findings in 133s (3x faster).

**Round 1:** 428s, chunk 1 0-char, chunk 2 10,257 chars, synthesis 22,703. Parsed 2 of 3. Strong quality. Notable self-correcting behaviour in D002 (falsification regex): initially claimed markdown bold breaks detection, then traced the code to discover asterisks are already stripped, and retracted that claim while identifying the real issue. Verdicts on registry: CONFIRM C0012, EXTEND C0012, CHALLENGE C0007.

**Round 2:** 748s, chunk 1 0-char, synthesis 10,750. Parsed 3 of 3. Good. Explored DynamicManagementConfig validation gaps (tau_sim_embed, default_vulnerability, per_model_directives length) — territory other models had not systematically covered. Lower-impact than runtime bugs but genuine.

**Round 3:** 836s. Only round where both chunks produced output (10,593 and 7,950 chars). Parsed 2 of 5. Mixed: three of five findings are repeats (fingerprint type mismatch resubmitted from R0, token estimation overlaps C0007). Two novel findings (tau_vocab_growth boundary error, baseline vector validation).

**Round 4:** 409s, both chunks 0-char, synthesis 8,178. Parsed 3. Moderate quality. Watchdog deadlock from full OS pipe buffer is a genuine novel concurrency finding with strong systems-level reasoning. C0032 confirmation shows registry engagement.

**Round 5:** 1,125s (18.8 min, longest round). Both chunks produced output. Parsed 1 of 6 — parser catastrophe. C0041 in registry is an UNSTRUCTURED fallback capturing only the first 500 chars of the response header. The actual response contained 6 well-structured findings, 4 of which were genuinely new (flaw class quoted integers, watchdog resource leak, threshold validation, mutable default risk).

## 2. Timing Analysis

| Round | DeepSeek | Fastest Model | Ratio |
|-------|----------|---------------|-------|
| R0 | 397s | Codex 133s | 3.0x |
| R1 | 428s | Codex 148s | 2.9x |
| R2 | 748s | Codex 61s | 12.3x |
| R3 | 836s | Codex 48s | 17.4x |
| R4 | 409s | ChatGPT 38s | 10.8x |
| R5 | 1125s | Codex 51s | 22.1x |

Total DeepSeek: 3,943s (65.7 min). Total equivalent Codex: ~527s. 7.5x overall, worsening from 3x in early rounds to 22x in R5 due to context accumulation in synthesis prompts (R5 synthesis input was 98,672 chars).

## 3. 0-Char Chunk Analysis

8 of 12 chunks (67%) had 0-char output. Chunk 1 was empty in 4/6 rounds. Both chunks empty in R0 and R4. No reasoning/thinking token fields were captured in any turn across any round (checked `reasoning`, `reasoning_content`, `thinking`, `reasoning_tokens` — all absent). R1-0528's CoT tokens are consumed invisibly, explaining both the high latency and empty chunks.

Impact on quality: surprisingly low. Synthesis recovers every time, producing the full analysis from scratch. The model effectively reasons 3 times per round, wasting 2/3 of API calls.

## 4. Quality Comparison — Parsed vs Actual Findings

| Round | DS Parsed | DS Actual | Codex | ChatGPT | CC2 | Gemini |
|-------|-----------|-----------|-------|---------|-----|--------|
| R0 | 1 | 2 | 3 | 4 | 4 | 4 |
| R1 | 2 | 3 | 6 | 9 | 5 | 5 |
| R2 | 3 | 3 | 4 | 1 | 5 | 1 |
| R3 | 2 | 5 | 4 | 5 | 5 | 7 |
| R4 | 3 | 3 | 6 | 0 | 5 | 1 |
| R5 | 1 | 6 | 2 | 6 | 4 | 3 |
| Total | 12 | 22 | 25 | 25 | 28 | 21 |

55% capture rate — lowest of all models. The loss is entirely from parser incompatibility with DeepSeek's markdown bold headers.

**9 genuinely novel findings** not covered by other models: tuple parser DOTALL (R1), tau_sim_embed validation (R2), per_model_directives length (R2), tau_vocab_growth boundary (R3), watchdog pipe deadlock novel angle (R4), flaw class quoted integers (R5), watchdog resource leak (R5), threshold validation (R5), mutable default risk (R5).

**Repeated findings:** Fingerprint type mismatch submitted 3 times (R0, R3, R5). Baseline vectors submitted twice (R3, R5). Root cause: no feedback loop telling DeepSeek its findings were registered.

## 5. Registry and Cross-Model Confirmation

All 7 DeepSeek registry entries are UNCONFIRMED. Zero external confirmations. DeepSeek self-confirmed its own findings 6 times (C0025: 3 times, C0028: 2 times, C0038: 1 time) — zero evidential value under CDSFL.

Two entries are parse artefacts (C0016: empty description with fragment "example: [1,2,3]"; C0041: UNSTRUCTURED fallback from R5). Five are legitimate but unconfirmed, likely because other models produced overlapping findings independently (e.g., C0039 overlaps C0032) and registry deduplication did not link them.

DeepSeek did provide useful verdicts on others' findings: CONFIRM C0004, CHALLENGE C0007, CONFIRM+EXTEND C0012.

## 6. Fingerprint Analysis

DeepSeek fingerprint has only 3 entries in `prompt_chars_history` (other models have 5-6). The `max_successful_context_chars` (54,770) is well below the 101K-103K prompts being sent, which triggers decomposition every round. However, `max_successful_prompt_chars` (102,942) proves the model handles the full payload — the fingerprint field that would prevent decomposition is missing from the dispatch logic's check path.

Registry contribution by source model: Gemini 12, ChatGPT 10, Codex 7, DeepSeek 7, CC2 5.

## 7. Recommendations for Specialist Role Switch

1. **Fix the fingerprint** — add the decomposition-prevention field. `max_successful_prompt_chars: 102,942` proves DeepSeek handles full payloads.

2. **Stop decomposing** — 0-char chunks make it counterproductive. Single-call dispatch would produce the same output faster.

3. **Fix parser for markdown format** or add a per-model directive instructing DeepSeek to use JSON array format. The 45% finding loss is entirely from format incompatibility.

4. **Fix the self-confirmation loop** — relay context should include DeepSeek's own registered findings to prevent resubmission.

5. **Capture reasoning tokens** — the dispatch layer should save `reasoning_content` from the API response for diagnostics.

6. **Specialist role design:** Dispatch DeepSeek once per experiment (not per round) with the full finding set. Task: verify top-K findings from other models via CONFIRM/CHALLENGE/EXTEND verdicts. Budget 15-20 minutes for a single deep pass. This matches its natural behaviour and avoids per-round overhead.

7. **Cost-benefit bottom line:** DeepSeek's analysis quality is genuinely high. The problem is not quality but pipeline integration — dispatch, decomposition, parsing, and feedback all worked against it. Fixing fingerprint and parser alone would likely yield 4-6 findings per round in 3-5 minutes instead of 1-3 parsed findings in 7-19 minutes.
