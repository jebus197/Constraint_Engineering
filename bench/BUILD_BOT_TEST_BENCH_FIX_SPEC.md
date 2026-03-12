# Test Bench Fix Specification

## Scope
Patch only:
- `bench/run_benchmark.py`
- `bench/evaluate.py`
- `bench/report.py`

Do not change task JSON files.

## Critical Invariant (Must Keep)
`run_benchmark.py` must **not** stop `REVISED_ANSWER` parsing at arbitrary uppercase headings like `NOTE:`.  
It must stop only at known benchmark section labels or end-of-text.

## Required Patches

### 1) `bench/run_benchmark.py`

#### A. Preserve iterative pass chaining
Experimental passes should carry forward the prior revised draft and prior issues into the next pass prompt.

#### B. Add explicit section labels and safe extraction
Add this constant near prompt-construction helpers:

```python
SECTION_LABELS = ("INITIAL_ANSWER", "ISSUES_FOUND", "REVISED_ANSWER")
```

Replace `_extract_section(...)` with logic equivalent to:

```python
def _extract_section(text: str, label: str) -> str | None:
    stop_labels = [re.escape(item) for item in SECTION_LABELS if item != label]
    if stop_labels:
        stop_pattern = rf"(?=\n(?:{'|'.join(stop_labels)}):\s*(?:\n|$)|\Z)"
    else:
        stop_pattern = r"\Z"

    pattern = rf"(?:^|\n){re.escape(label)}:\s*\n?(.*?){stop_pattern}"
    match = re.search(pattern, text, flags=re.DOTALL)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None
```

Behavioral requirement:
- `REVISED_ANSWER` may contain lines like `NOTE:` and they must remain in the extracted section unless a known section label starts.

#### C. Include run metadata envelope
Output should be object form:
- top-level `benchmark_meta`
- top-level `results`

`benchmark_meta` should include at least:
- `schema_version` (e.g., `cdsfl-bench-v2`)
- `model`
- `provider`
- `num_passes`
- `task_count`
- `directives_source`
- `timestamp_utc`
- `domains`

---

### 2) `bench/evaluate.py`

#### A. Accept both input shapes
Input JSON must support:
1. legacy raw list of task results
2. object containing `benchmark_meta` + `results`

#### B. Emit report-oriented schema
Output should contain:
- `metadata`
- `summary`
- `per_domain`
- `per_pass`
- `corroboration_fit`
- `control_vs_experimental`
- `false_positive_detail`
- `fault_details`

#### C. Curve-fit field normalization
Use `estimated_p` as the canonical key (not `p`) in output.  
If fitting is unavailable/fails, keep graceful fallback with note fields (no crash).

---

### 3) `bench/report.py`

#### A. Accept normalized evaluation schema
Require and consume the `summary`-based structure from `evaluate.py`.

#### B. Support legacy fit naming
If `corroboration_fit` uses legacy key `p`, map it to `estimated_p` before reporting.

#### C. Tolerate partial fit data
If `estimated_p` or `r_squared` is missing, print `unavailable` rather than failing.

## Verification Steps

Run:

```bash
cd bench
python3 run_benchmark.py --dry-run
python3 evaluate.py --help
python3 report.py --help
```

Expected:
- dry run validates all tasks and prints counts
- help commands exit successfully

### Parser Regression Test (Required)
Use a response block where `REVISED_ANSWER` contains `NOTE:`.  
Pass condition: extracted `REVISED_ANSWER` still includes `NOTE:` content and is only cut at the next known section label (or EOF).

## Non-Negotiable Acceptance Criteria
1. No syntax errors in patched files.
2. Dry-run benchmark still works.
3. `REVISED_ANSWER` extraction is not truncated by unknown uppercase headings.
4. `evaluate.py` output is consumable by `report.py` without schema errors.

