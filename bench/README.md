# CDSFL Testbench

Reproducible benchmark for evaluating the Constraint-Driven Synthesis and Falsification Loop (CDSFL) methodology described in [PAPER.md](../PAPER.md).

## What It Tests

Does methodology-prompted output contain fewer critical errors than unguided output?

30 seeded-fault tasks across three domains (10 each):
- **Hardware engineering** — power budgets, thermal analysis, RF design, impedance matching
- **Software architecture** — concurrency, security, distributed systems, performance
- **Logistics** — shipping, cold chain, customs, fleet management, warehouse operations

Each task contains a realistic design prompt with 2–3 planted errors that have known ground truth.

## How It Works

1. **Control condition**: each prompt sent with no system prompt
2. **Experimental condition**: each prompt sent with CDSFL directive set as system prompt, run through configurable P-Passes (default 3)
3. **Scoring**: automated detection of seeded faults via keyword matching, with per-pass tracking
4. **Curve fitting**: cumulative detection fitted to C(n) = 1 − (1−p)ⁿ to estimate single-pass detection probability

## Quick Start

```bash
pip install -r requirements.txt

# Validate tasks (no API calls)
python3 run_benchmark.py --dry-run

# Full benchmark run (requires ANTHROPIC_API_KEY or OPENAI_API_KEY)
export ANTHROPIC_API_KEY=your-key-here
python3 run_benchmark.py --output results.json

# Score results
python3 evaluate.py results.json --output evaluation.json

# Generate report
python3 report.py evaluation.json
python3 report.py evaluation.json --csv results.csv
```

## Options

```
run_benchmark.py
  --dry-run           Validate tasks, no API calls
  --model MODEL       Model identifier (default: claude-sonnet-4-20250514)
  --provider PROVIDER "anthropic" or "openai" (default: anthropic)
  --passes N          Number of P-Passes for experimental condition (default: 3)
  --output FILE       Output file (default: stdout)

evaluate.py
  RESULTS_FILE        Raw results JSON from run_benchmark.py
  --output FILE       Output file (default: stdout)

report.py
  EVALUATION_FILE     Evaluation JSON from evaluate.py
  --csv FILE          Also write results as CSV
```

## Task Format

Each task is a JSON file in `tasks/{domain}/`:

```json
{
  "id": "hw-001",
  "domain": "hardware",
  "prompt": "Design a battery-powered sensor node that...",
  "seeded_faults": [
    {
      "id": "f1",
      "type": "physical_impossibility",
      "description": "Power budget exceeds coin-cell capacity by 10x",
      "location_hint": "power calculation"
    }
  ],
  "ground_truth_notes": "Correct answer must account for..."
}
```

## Interpreting Results

- **Detection rate**: fraction of seeded faults identified in the response
- **Control vs experimental**: the methodology's effect size
- **Cumulative curve fit**: estimated p (single-pass detection probability) and R² (goodness of fit)
- **Per-domain breakdown**: whether the methodology works equally across domains

A high R² for the C(n) = 1 − (1−p)ⁿ fit suggests the corroboration model from Part II of the paper accurately describes how P-Pass detection accumulates.

## Estimated Cost

At representative frontier model pricing (~$3/MTok input, ~$15/MTok output), a full 30-task run with 3 P-Passes costs approximately $0.50–$1.00.

## Limitations

- Detection scoring uses keyword matching, not semantic understanding. Some faults may be detected but scored as missed (false negative), or non-faults may match keywords (false positive). Manual review of a sample is recommended.
- The benchmark tests the methodology on seeded faults with known ground truth. Real-world errors may be more subtle or domain-specific than the planted faults.
- Results are specific to the model and provider used. Cross-model comparisons require running the benchmark on each model independently.
