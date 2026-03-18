# CX Phase 2 Handoff Brief — Anthropic Model Testing

**Date:** 2026-03-17
**From:** CC (Claude Code, Opus 4.6)
**To:** CX (Codex)
**Owner:** George Jackson (The Founder)

## Overview

This is Phase 2 of the CDSFL empirical validation — a benchmark comparing how
different prompt methodologies affect AI reasoning quality on genuinely hard
frontier tasks. Phase 1 tested easy tasks (known faults, 90-100% baseline
detection). Phase 2 tests at the frontier where models make real errors.

25 frontier tasks span 5 categories: mathematical proofs, code implementation,
engineering design, multi-domain synthesis, and reasoning-about-reasoning. Each
task is designed so frontier models genuinely struggle on a single pass.

The experiment compares three conditions per task:
- **Condition A**: bare prompt, no system instructions, single pass
- **Condition B**: structured constraint-classification and iterative
  falsification directives (CDSFL methodology), up to 5 P-passes with
  adaptive termination
- **Condition C**: equally-long generic "be thorough, check your work"
  instructions, same number of passes, but without structured falsification

Condition C exists to isolate whether any improvement comes from the specific
methodology (constraint classification, HARD/SOFT distinction, adversarial
self-checking) versus simply giving the model more instructions and more passes.

7 model configs are tested across providers. CC runs 5 non-Anthropic configs.
You run the 2 Anthropic configs. No model assesses its own provider family.

## Your Assignment

Run the benchmark for **Anthropic models only**:
- `sonnet-4` (claude-sonnet-4-20250514, standard)
- `sonnet-4-thinking` (claude-sonnet-4-20250514, extended thinking)

## Task Design Rationale

Each frontier task has:
- A **verification method** (how correctness is checked after the fact):
  proof validity, test suite pass/fail, constraint satisfaction, physical law
  compliance, or self-consistency audit
- A **category** tag and **domain** tag
- Optional **schema_b** flag (task has 3+ independent modules — suitable for
  modular P-pass treatment)
- Optional **schema_c** flag (selected for cross-model adversarial checking)

Tasks are NOT pre-seeded with known faults. The model generates its own solution
and its own errors. The P-passes attempt to find and fix those errors. The
question is whether structured falsification (Condition B) catches more genuine
issues than generic carefulness (Condition C) or a single unguided pass
(Condition A).

The adaptive termination algorithm stops P-passes early if a pass produces zero
findings classified as moderate or severe by a keyword-based severity classifier.
This prevents wasting API calls on passes that produce only trivial restated
observations. Minimum 2 passes always run.

## What To Run

### Prerequisites

```bash
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
source .env   # loads ANTHROPIC_API_KEY and others
```

Verify the key works:
```bash
python3 -c "import anthropic; c=anthropic.Anthropic(); print(c.messages.create(model='claude-sonnet-4-20250514', max_tokens=10, messages=[{'role':'user','content':'ping'}]).content[0].text)"
```

### Run 1: Sonnet 4 (standard)

```bash
python3 bench/run_phase2.py \
  --config sonnet-4 \
  --passes 5 \
  --cost-cap 15.0 \
  --output-dir bench/results/phase2
```

### Run 2: Sonnet 4 thinking (extended thinking)

```bash
python3 bench/run_phase2.py \
  --config sonnet-4-thinking \
  --passes 5 \
  --cost-cap 15.0 \
  --output-dir bench/results/phase2
```

### If a run crashes

Resume from checkpoint (no work is lost):
```bash
python3 bench/run_phase2.py \
  --config sonnet-4 \
  --passes 5 \
  --cost-cap 15.0 \
  --resume \
  --output-dir bench/results/phase2
```

### Dry Run (verify before real run)

```bash
python3 bench/run_phase2.py --config sonnet-4 --dry-run
python3 bench/run_phase2.py --config sonnet-4-thinking --dry-run
```

## Infrastructure

- **Checkpoint/resume**: saves after every task condition. Crash loses at most
  1 API call, not the whole run.
- **Cost ledger**: tracks cumulative spend, aborts safely at cap. File:
  `bench/results/phase2/cost_ledger.json`
- **Adaptive throttle**: starts at 2s (standard) / 4s (thinking), backs off
  exponentially on rate limits, converges to fastest safe rate.
- **Retry with backoff**: 10 retries, exponential from 8s to 300s, catches
  429/503/504/529/timeout/overloaded.

## Data Collation

After both configs complete, produce a unified summary CSV:

```bash
python3 -c "
import json, csv
from pathlib import Path

cp = json.loads(Path('bench/results/phase2/checkpoint.json').read_text())
rows = []
for key, result in sorted(cp['completed'].items()):
    parts = key.split(':')
    config, task_id, condition = parts[0], parts[1], parts[2]
    if config not in ('sonnet-4', 'sonnet-4-thinking'):
        continue
    row = {
        'config': config,
        'task_id': task_id,
        'condition': condition,
    }
    if 'passes' in result:
        passes = result['passes']
        row['num_passes'] = len(passes)
        row['terminated_early'] = result.get('terminated_early', False)
        total_severe = sum(p.get('severity_counts',{}).get('severe',0) for p in passes)
        total_moderate = sum(p.get('severity_counts',{}).get('moderate',0) for p in passes)
        total_trivial = sum(p.get('severity_counts',{}).get('trivial',0) for p in passes)
        row['total_severe'] = total_severe
        row['total_moderate'] = total_moderate
        row['total_trivial'] = total_trivial
        row['final_response_length'] = len(result.get('final_response',''))
    else:
        row['num_passes'] = 1
        row['terminated_early'] = False
        row['total_severe'] = 0
        row['total_moderate'] = 0
        row['total_trivial'] = 0
        row['final_response_length'] = len(result.get('response',''))
    rows.append(row)

out = Path('bench/results/phase2/cx_anthropic_summary.csv')
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f'Wrote {len(rows)} rows to {out}')
"
```

This produces `bench/results/phase2/cx_anthropic_summary.csv`. CC will merge
this with non-Anthropic results in Phase 4.

## Reporting

When each run completes, post to IM service:
```bash
python3 cw_handoff/im_service.py post \
  "CX: Phase 2 [config-name] complete. Tasks: N/25. Cost: \$X.XX. Checkpoint: bench/results/phase2/checkpoint.json"
```

If a run fails and cannot resume, post:
```bash
python3 cw_handoff/im_service.py post \
  "CX: Phase 2 [config-name] FAILED at task [task-id]. Error: [brief description]. Checkpoint preserved."
```

## Rate Limit Guidance

- Sonnet 4 thinking requests are heavy (~26K tokens each with thinking budget)
- 25 tasks x 3 conditions x up to 5 passes = up to 375 API calls per config
- Expected runtime: 2-4 hours per config
- If you see sustained 429s with delays >60s, the daily limit may be hit.
  In that case, stop and resume the next day with --resume.

## Scope Boundaries

1. Do NOT modify any task files, directives, evaluation code, or run_benchmark.py
2. Do NOT run non-Anthropic models (GPT-4o, Gemini, etc.) — CC handles those
3. Do NOT run Schema C unless CC coordinates it
4. Do NOT exceed $15 per config ($30 total for both configs)
5. If you encounter a bug in the infrastructure, document it and post to IM.
   Do not attempt to fix it — CC owns the codebase.

## After Main Runs: Grandslam (Schema C Cross-Model)

After all 7 configs complete their main runs, a cross-model adversarial round
("Grandslam") will pit frontier models against each other on the 10 Schema C
tagged tasks. CW (Cowork) will orchestrate the pingpong sequencing. CC will
coordinate timing. Do not begin this phase until CC explicitly signals go.

The Grandslam pairs (4 pairs, maximising training-bias diversity):
- Sonnet-thinking vs GPT-4o
- GPT-4o vs Gemini Pro
- Gemini Pro vs Sonnet-thinking
- o3-mini vs Sonnet-thinking

For pairs involving Anthropic models, you (CX) make the Anthropic API calls.
CC makes the non-Anthropic calls. CW sequences the exchanges.
