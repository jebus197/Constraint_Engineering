The following defects and correctness issues were identified in `bench/run_benchmark.py`:

### 1. High Severity: Lack of API Error Handling and Retries
**Location:** `call_anthropic` (Lines 144–165) and `call_openai` (Lines 172–190)
**Defect:** Both functions execute API calls without `try...except` blocks for network errors, timeouts, rate limits (429), or server-side errors (5xx). 
**Why it matters:** Benchmarking is a long-running process. A single transient network failure or rate-limit exception 50 tasks into a 100-task run will crash the entire harness, losing all progress and necessitating a full restart.

### 2. Medium Severity: Pass Numbering and Logic Error in `run_extended`
**Location:** `run_extended` (Lines 277–280)
**Defect:** The `modular_count` is calculated as `max(num_passes - 1, 1)`. If a user requests `--passes 1`, the code performs one modular pass AND one adversarial pass, totaling 2 passes. Furthermore, both records are appended to the results with `pass_number: 1`.
**Why it matters:** This violates the user's configuration and produces inconsistent JSON metadata where multiple distinct steps share the same pass index, making downstream analysis difficult.

### 3. Medium Severity: Brittle Token Limit in Multi-Pass Prompting
**Location:** `call_anthropic` (Line 150) and `call_openai` (Line 183)
**Defect:** `max_tokens` is hardcoded to `4096`. 
**Why it matters:** CDSFL is an iterative methodology. By Pass 3, the user prompt includes the original task, the current draft, and prior issues. If the task itself is large (e.g., a complex engineering spec), the remaining token budget for the model's response (which includes an Initial Answer, Issues, and a Revision) is likely to be exceeded. Truncation will cause `_extract_section` to fail to find the `REVISED_ANSWER` header, which usually appears at the end.

### 4. Low/Medium Severity: Missing Model/Provider Validation
**Location:** `main` (Lines 421–427)
**Defect:** The script allows any string for `--model` and `--provider` independently.
**Why it matters:** The default model is `claude-sonnet-4-20250514`. If a user runs the script with `--provider openai` but forgets to change the model name, the script will proceed to make API calls that will immediately fail with "Model not found" errors, as OpenAI does not host Claude.

### 5. Low Severity: Regex Fragility in Section Extraction
**Location:** `_extract_section` (Line 192)
**Defect:** The regex `rf"(?:^|\n){re.escape(label)}:\s*\n?(.*?){stop_pattern}"` is highly sensitive to the exact presence of the colon and newline.
**Why it matters:** LLMs occasionally deviate from exact formatting (e.g., writing `REVISED ANSWER:` without the underscore, or `REVISED_ANSWER :` with a space). If the model misses the exact header string, the script falls back to using the *entire* response as the draft. In subsequent passes, this causes the prompt to become cluttered with the model's own meta-talk (like "Issues found"), potentially degrading performance.

### 6. Low Severity: Absence of Request Throttling
**Location:** `run_benchmark` loop (Lines 352–386)
**Defect:** The script fires requests sequentially as fast as the API responds.
**Why it matters:** Without basic `time.sleep()` or exponential backoff, users on "Tier 1" or trial API accounts will hit Rate Limits (RPM/TPM) almost immediately, causing the crash described in Defect #1.

### 7. Correctness Observation: Isolated Context vs. System Instructions
**Location:** `run_extended` (Line 318)
**Defect:** The adversarial pass is called with `system_prompt=None`.
**Why it matters:** While the comment notes this is to "avoid anchoring," it means the core CDSFL directives (Part IV, Section 4.1)—specifically the mandate to classify constraints as HARD or SOFT—are not active during the review. If the goal of the benchmark is to evaluate the CDSFL methodology, removing the methodology's core directives from the final "Adversarial" review may undermine the validity of the results.
