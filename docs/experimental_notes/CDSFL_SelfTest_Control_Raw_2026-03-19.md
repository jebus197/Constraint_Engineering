The following is a defect report for `bench/run_benchmark.py`, a seeded-fault benchmark harness for CDSFL evaluation.

### **1. Missing API Error Handling and Retries**
*   **Location:** `call_anthropic` (lines 135–158), `call_openai` (lines 161–183), and `run_benchmark` (lines 351–399).
*   **Defect:** The code lacks `try-except` blocks for network errors, rate limits (HTTP 429), or server-side glitches (HTTP 500).
*   **Severity:** **CRITICAL**
*   **Why it matters:** In a large-scale benchmark run involving dozens of tasks and multiple iterative passes, a single transient network failure or rate limit hit will crash the entire script, losing all progress. There is no mechanism to resume or skip a failed task.

### **2. Brittle Section Extraction (Case Sensitivity & Formatting)**
*   **Location:** `_extract_section` (lines 201–214).
*   **Defect:** The regex parser is case-sensitive and strictly expects the labels (e.g., `ISSUES_FOUND:`) to follow the prompt exactly. It also does not account for Markdown headers (e.g., `### ISSUES_FOUND`).
*   **Severity:** **MEDIUM**
*   **Why it matters:** LLMs frequently fluctuate in their output formatting (e.g., using `Issues Found:` or `**REVISED_ANSWER:**`). If the parser fails to match the exact string, it returns `None`, causing the system to lose structured data and potentially polluting the next pass's prompt with raw, unparsed text.

### **3. Fallback to Raw Response Causes "Prompt Pollution"**
*   **Location:** `run_experimental` (line 303) and `run_extended` (line 343).
*   **Defect:** If `_extract_section` fails to find a `REVISED_ANSWER` label, the code falls back to `current_draft = response`.
*   **Severity:** **MEDIUM**
*   **Why it matters:** The `response` contains the model's commentary and previous section headers. If this raw string is passed into the next iterative pass as the "Current Draft," the model is forced to review its own metadata (labels, headers, conversational filler) as if it were part of the technical solution, leading to a degradation in reasoning quality.

### **4. Logic Error in `run_extended` when `num_passes=1`**
*   **Location:** `run_extended` (lines 313–315).
*   **Defect:** `modular_count = max(num_passes - 1, 1)` means that if a user requests 1 pass, the script will run one modular pass *and* one adversarial pass, resulting in 2 total passes.
*   **Severity:** **LOW**
*   **Why it matters:** This violates the principle of least astonishment and the `--passes` CLI argument. Furthermore, both records in the resulting JSON will be labeled `pass_number: 1`, creating duplicate keys/IDs in the metadata.

### **5. Contaminated "Domain-Only" Ablation Condition**
*   **Location:** `compose_directives` (line 454).
*   **Defect:** If `condition == "domain-only"` but no domain-specific file is found, it returns `universal` directives.
*   **Severity:** **LOW**
*   **Why it matters:** For scientific ablation studies, "domain-only" should fail or return an empty string if the domain file is missing. Falling back to the universal prompt makes the results indistinguishable from the `universal-only` condition, potentially skewing the benchmark analysis.

### **6. Potential `TypeError` in `_err` usage within `main` (Dry Run)**
*   **Location:** `main` (lines 538–540).
*   **Defect:** `status = f"loaded ({len(dd)} chars)" if dd else "not found"`.
*   **Severity:** **LOW/MEDIUM** (Safety)
*   **Why it matters:** While `if dd` correctly prevents execution for `None`, if `load_domain_directives` ever returned a non-string object (e.g., an error object or empty list), `len(dd)` could fail. More importantly, if the file exists but is an empty string, it reports "not found," which is misleading during validation.

### **7. Hardcoded `max_tokens` Limit**
*   **Location:** `call_anthropic` (line 150) and `call_openai` (line 177).
*   **Defect:** `max_tokens` is hardcoded to 4096.
*   **Severity:** **LOW**
*   **Why it matters:** CDSFL encourages deep, adversarial revision which can result in very long technical outputs. Modern models (like Sonnet 3.5/4) support much larger output windows (8k+). 4096 may lead to truncated answers in complex structural or biomedical engineering tasks, invalidating the benchmark result for that task.

### **8. No Directory Creation for Output**
*   **Location:** `main` (line 565).
*   **Defect:** `Path(args.output).write_text(...)` fails if the parent directory does not exist.
*   **Severity:** **LOW**
*   **Why it matters:** Users typically specify paths like `--output results/run_01.json`. If `results/` doesn't exist, the script crashes at the very end of the run after all API costs have been incurred.
