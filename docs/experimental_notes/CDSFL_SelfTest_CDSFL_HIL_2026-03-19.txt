### Constraint Classification

*   **HARD:** Scientific validity (isolation of variables), Data integrity (extraction robustness), Reproducibility (deterministic outputs), Operational reliability (error handling).
*   **SOFT:** CLI argument structure, internal logging verbosity, file path naming conventions.

---

### Engineering Review: CDSFL Benchmark Harness

The following review applies the CDSFL methodology to the provided benchmark code.

#### 1. Reproducibility & Scientific Validity [HARD]

**Claim:** The harness provides a fair comparison between control and experimental conditions.
**Falsifier:** If stochastic model noise exceeds the delta produced by the methodology, the results are invalid.
**Test:** Check API call parameters for `temperature` and `seed` settings.
**Finding:** Both `call_anthropic` and `call_openai` omit `temperature` parameters. By default, most models use `temperature > 0` (typically 0.7 or 1.0). In a benchmark designed to measure the effect of a specific prompt methodology, non-deterministic output is a primary confound.
**Revision:** **[REQUIRED]** Explicitly set `temperature=0` and, where supported (OpenAI), a fixed `seed` in both `call_anthropic` and `call_openai`. Without this, "survival" of a fault may be a roll of the dice rather than a result of the P-Pass.

**Claim:** The `extended` mode correctly isolates the adversarial pass.
**Falsifier:** If the adversarial pass is influenced by the same system instructions or conversation history as the modular passes, isolation is violated.
**Test:** Examine `run_extended` and its API call.
**Finding:** `run_extended` calls `call(model, None, adversarial_prompt)`. Passing `None` for the system prompt successfully removes the CDSFL directives. Since the API callers create fresh requests (no `thread_id` or message history), the isolation is technically sound at the API level. However, the `ADVERSARIAL_PASS_TEMPLATE` instructs the model to act as an "independent reviewer," which is a behavioral shift but not a formal isolation of the data if the model has a strong internal bias toward the methodology.

#### 2. Data Integrity & Section Extraction [HARD]

**Claim:** `_extract_section` robustly captures model output without silent loss.
**Falsifier:** If a model produces the string "ISSUES_FOUND:" within its response body (e.g., in a sentence explaining the process), the regex will truncate the section.
**Test:** Inspect regex `stop_pattern = rf"(?=\n(?:{'|'.join(stop_labels)}):\s*(?:\n|$)|\Z)"`.
**Finding:** The use of `(?=\n(?:...))` (lookahead for a newline followed by a label) is reasonably safe but vulnerable to models that use markdown headers (e.g., `## ISSUES_FOUND:`) or those that omit the trailing colon.
**Revision:** **[VERIFY:current]** The current implementation assumes the model follows the "Return exactly these sections" instruction perfectly. In practice, models often add conversational filler.
**Speculative:** If the model repeats the "Original task" in its response and that task contains the string "ISSUES_FOUND:", the extractor will likely fail or return incorrect spans.

#### 3. Operational Reliability [HARD]

**Claim:** The harness handles API-level failures gracefully.
**Falsifier:** A single rate-limit error or timeout during a 3-pass experimental run crashes the entire benchmark.
**Test:** Check for `try/except` blocks or retry logic in `call_` functions.
**Finding:** There is **no retry logic**. A transient network failure or 429 (Too Many Requests) during Pass 2 of Task 50 will terminate the script. For a benchmark of this scale (100+ tasks * 4+ calls per task), this is a high-probability failure mode.
**Revision:** **[REQUIRED]** Implement exponential backoff for rate limits and basic retries for 5xx errors.

#### 4. Constraint Classification & Precedence (Methodology Check)

The `CDSFL_DIRECTIVES` string correctly implements the "Ambiguous defaults to HARD" rule. However, the `INITIAL_PASS_TEMPLATE` and `FOLLOWUP_PASS_TEMPLATE` do not explicitly remind the model of the classification tiers (Physics > Legal > User). 
**Revision:** **[SUGGESTED]** Update templates to explicitly prompt for the *tier-based* precedence defined in the Formal Methodology.

---

### Epistemic Marking & Status

*   **[VERIFY:current]** The robustness of `_extract_section` against Markdown formatting (e.g., `### REVISED_ANSWER`) should be tested against the latest Sonnet/GPT-4o output styles before running full-scale.
*   **[SPECULATIVE]** The lack of `max_tokens` adjustment for complex tasks may result in truncated `REVISED_ANSWER` sections, which the current extractor would capture as a partial (valid-looking) string.

### Definitive Stance

The code is architecturally sound but scientifically fragile. The omission of `temperature=0` is a critical defect for a benchmark harness. Implementation of API retries is necessary for operational success given the volume of requests required by the iterative P-Pass protocol.

**Next Steps:**
1.  Inject `temperature: 0` into all provider kwargs.
2.  Wrap provider calls in a retry decorator (e.g., `tenacity`).
3.  Add `strip().rstrip(':')` logic to section labels to handle model variability.
