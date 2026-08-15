#!/usr/bin/env python3
"""Experiment 11 Phase 6: CC2 implements converged design as callable Python module.

CC2 receives the full synthesis document + converged plan + existing orchestrator
and produces a Python module implementing all 6 areas of the dynamic management
and load-balancing layer.

Founder design decisions (locked):
  1. Ascending abstraction guard: CONJUNCTIVE (3/4 majority)
  2. Convergence threshold: τ_κ separate from γ (3/4 majority)

Three additions from Codex timeout analysis:
  1. Pre-dispatch probabilistic feasibility (uncertainty-aware F1)
  2. Correlated failure model (shared vulnerability coefficient v_ij)
  3. Real-time manager monitoring interface (event stream to PM during dispatch)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent for orchestrator imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bench.experiment_11_orchestrator import (
    load_default_config,
    call_openrouter,
    save_output,
    _log,
)


def build_phase6_prompt() -> str:
    """Build the implementation prompt for CC2."""
    repo_root = Path(__file__).resolve().parent.parent
    logs_dir = repo_root / "bench" / "logs" / "experiment_11"

    # Load synthesis document
    synth_path = logs_dir / "phase3_synthesis_cc2_20260328T204745Z.json"
    with open(synth_path) as f:
        synthesis_text = json.load(f)["response"]

    # Load converged plan
    plan_path = logs_dir / "converged_plan.md"
    plan_text = plan_path.read_text(encoding="utf-8")

    # Load existing orchestrator for structural context
    orch_path = repo_root / "bench" / "experiment_11_orchestrator.py"
    orch_text = orch_path.read_text(encoding="utf-8")

    prompt = f"""## PHASE 6: IMPLEMENTATION

You are CC2 (Claude Opus 4.6), the player manager for Experiment 11. In Phase 3,
you synthesised four independent mathematical formalisations into a converged
design for the CDSFL dynamic management and load-balancing layer. That synthesis
declared structural convergence. Now implement it.

### YOUR TASK

Produce a single, complete Python module (`dynamic_management.py`) that implements
all 6 areas of the converged formalisation as callable functions and classes.

### DESIGN DECISIONS (LOCKED BY FOUNDER)

1. **Ascending abstraction guard: CONJUNCTIVE.** Abstraction drop is one factor
   among several in the stop decision, not a unilateral veto. A legitimate shift
   from abstract to concrete findings (drilling into implementation details of an
   architectural flaw) must not trigger premature stopping.

2. **Convergence threshold: τ_κ SEPARATE from γ.** The decision threshold τ_κ is
   a deliberately chosen parameter tuned from operational experience. The Duane γ
   is an empirical estimate used as a diagnostic. Do not couple them.

### THREE ADDITIONS (FROM CODEX TIMEOUT ANALYSIS)

The Codex timeout in Phase 2 (600s, 21,681-char prompt, no output) revealed gaps
between the formalisation and operational reality. Implement these three additions:

1. **Pre-dispatch probabilistic feasibility.** Before dispatching a task to a model,
   estimate P(task fits within model capacity). The feasibility constraint F1
   (Σ a_jm · b_j ≤ L_m) assumes L_m is known. In practice, L_m may be uncertain
   (e.g., CLI delivery mechanisms don't expose token limits). Implement an
   uncertainty-aware version: dispatch only if P(feasible) ≥ threshold.

2. **Correlated failure model.** Area 6 treats failures independently. Add a shared
   vulnerability coefficient v_ij ∈ [0,1] between models i and j. High v_ij when
   models share delivery mechanism, API provider, or architectural lineage.
   Correlated failure probability for a model class should be computable.

3. **Real-time manager monitoring interface.** The PM role needs a real-time event
   stream during dispatch, not just batch results after. Define a callback/event
   protocol so the PM can receive TIMEOUT, EMPTY, MALFORMED events as they occur
   and trigger RETRY/REALLOCATE/EXCLUDE dynamically.

### REQUIREMENTS

1. **Module structure:** Single file, `dynamic_management.py`. All 6 areas as
   classes or functions matching the interface contracts from the converged plan.

2. **Type hints:** Full Python type annotations. Use dataclasses for structured data.

3. **No external dependencies** beyond the Python standard library and numpy (for
   numerical operations). No scipy, no torch, no heavy deps.

4. **Testable:** Every public function should be unit-testable. Include docstrings
   with usage examples.

5. **Reduction properties:** Implement the K=1, homogeneous, and no-failures
   reduction checks as validation methods.

6. **Connect to existing schema:** Import paths and symbol names must be compatible
   with the existing Mathematical Appendix notation. Use the notation conventions
   from the converged plan (§3).

7. **Config-driven:** All thresholds, weights, and parameters should be configurable
   via a single config dataclass, with sensible defaults matching the converged plan.

8. **Attribution:** In the module docstring, note which formulations came from which
   model (CC2, ChatGPT, Gemini, DeepSeek) for the minority variations you adopt.

### OUTPUT FORMAT

Produce the complete Python module as a single code block. Do NOT produce
commentary, discussion, or explanations — just the code. The code IS the
deliverable. If you need to explain a design choice, put it in a code comment.

### CONTEXT: CONVERGED PLAN (architecture, interface contracts, notation)

{plan_text}

### CONTEXT: YOUR PHASE 3 SYNTHESIS (merged formalisations, all 6 areas)

{synthesis_text}

### CONTEXT: EXISTING ORCHESTRATOR (for structural compatibility)

```python
{orch_text}
```

### BEGIN IMPLEMENTATION

Produce `dynamic_management.py` now.
"""

    return prompt


def main():
    # Refuse a paid run on `--help` or a typo. Must be the FIRST thing
    # main() does: everything below this line can reach a paid model.
    from bench.runner_argv_guard import guard_argv
    guard_argv([], 'python3 bench/run_exp11_phase6.py (takes no arguments)')
    repo_root = Path(__file__).resolve().parent.parent
    logs_dir = repo_root / "bench" / "logs" / "experiment_11"

    # Source .env
    env_path = repo_root / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()

    config = load_default_config()
    cdsfl_text = config.cdsfl_system_prompt

    prompt = build_phase6_prompt()
    _log(f"Phase 6 prompt: {len(prompt)} chars")

    # Dispatch to CC2 via OpenRouter with extended timeout
    t0 = time.monotonic()
    try:
        response = call_openrouter(
            model_id="anthropic/claude-opus-4-6",
            system_prompt=cdsfl_text,
            user_prompt=prompt,
            max_tokens=32768,
            timeout=600,  # extended for implementation task
            max_retries=2,
            backoff_base=5.0,
        )
        elapsed = time.monotonic() - t0
        _log(f"CC2 Phase 6 response: {len(response)} chars in {elapsed:.1f}s")

        # Save output
        filepath = save_output(
            logs_dir, "phase6_impl",
            "cc2",
            prompt[:500] + "...[truncated]",  # Don't save full 86K prompt
            response,
            metadata={
                "elapsed": round(elapsed, 1),
                "chars": len(response),
                "prompt_chars": len(prompt),
                "phase": "6_implementation",
            },
        )
        _log(f"Saved to {filepath}")

        # Extract Python code if wrapped in code fence
        code = response
        if "```python" in code:
            start = code.index("```python") + len("```python")
            end = code.rindex("```")
            code = code[start:end].strip()
        elif "```" in code:
            start = code.index("```") + 3
            # Skip optional language tag on same line
            newline = code.index("\n", start)
            start = newline + 1
            end = code.rindex("```")
            code = code[start:end].strip()

        # Write the module
        module_path = repo_root / "bench" / "dynamic_management.py"
        module_path.write_text(code + "\n", encoding="utf-8")
        _log(f"Module written to {module_path}")
        _log(f"Module size: {len(code)} chars, {code.count(chr(10))} lines")

    except Exception as e:
        elapsed = time.monotonic() - t0
        _log(f"Phase 6 FAILED after {elapsed:.1f}s: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
