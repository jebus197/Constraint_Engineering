#!/usr/bin/env python3
"""Experiment 11 Phase 2: Blind Round Dispatch.

Sends identical prompt (converged plan + task brief) to all 5 models sequentially.
CC2 gets additional note about upcoming synthesis role.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_11_orchestrator import (
    load_default_config, dispatch, save_output, _log, CircuitBreakerTripped
)


def main():
    # Source .env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()

    config = load_default_config()
    logs_dir = config.logs_dir

    # Load prompts
    converged_plan = (logs_dir / "converged_plan.md").read_text(encoding="utf-8")
    task_brief = (logs_dir / "task_brief.md").read_text(encoding="utf-8")

    # Base prompt (identical for all participants)
    base_prompt = (
        "You are participating in a distributed compute test under CDSFL. "
        "This is a BLIND ROUND — you have not seen any other model's output. "
        "Produce your own independent formalisations for all six areas.\n\n"
        "=== ARCHITECTURE PLAN (binding interface contracts) ===\n\n"
        f"{converged_plan}\n\n"
        "=== TASK BRIEF ===\n\n"
        f"{task_brief}\n\n"
        "=== INSTRUCTIONS ===\n\n"
        "Produce a complete formalisation for ALL SIX AREAS using the output "
        "structure specified in §5 of the architecture plan. Classify every "
        "formalisation as HARD or SOFT. Run internal P-passes. Show reduction "
        "properties. This is your independent contribution — do not hedge or "
        "defer. Produce concrete mathematics.\n"
    )

    # CC2 gets additional note about synthesis role
    cc2_addendum = (
        "\n\nADDITIONAL NOTE (CC2 only): After producing your own independent "
        "solution below, you will be asked in a SUBSEQUENT phase (not this one) "
        "to synthesise all five models' outputs as player manager. For THIS phase, "
        "produce your own work first without anticipating the synthesis role. "
        "Your independent contribution is what matters here.\n"
    )

    # Dispatch order (sequential, M1 8GB constraint)
    dispatch_order = ["CC2", "Codex", "ChatGPT", "Gemini", "DeepSeek"]

    results = {}

    for label in dispatch_order:
        model_config = config.get_by_label(label)
        if model_config is None:
            _log(f"ERROR: No config for {label}")
            sys.exit(1)

        prompt = base_prompt
        if label == "CC2":
            prompt += cc2_addendum

        _log(f"\n{'='*60}")
        _log(f"Phase 2 Blind Round: Dispatching to {label}")
        _log(f"Prompt length: {len(prompt)} chars")
        _log(f"{'='*60}")

        try:
            t0 = time.monotonic()
            response = dispatch(model_config, prompt, config.cdsfl_system_prompt)
            elapsed = time.monotonic() - t0

            _log(f"Response from {label}: {len(response)} chars in {elapsed:.1f}s")

            # Circuit breaker: check for structured output
            response_upper = response.upper()
            structured_fields = ["VERDICT", "EVIDENCE", "CONSTRAINT_CLASS", "CONFIDENCE"]
            found = sum(1 for f in structured_fields if f in response_upper)
            if found < 2:
                _log(f"WARNING: {label} produced only {found}/4 key structured fields")

            # Save output
            filepath = save_output(
                logs_dir, "phase2_blind", label,
                prompt, response,
                metadata={
                    "elapsed_seconds": round(elapsed, 1),
                    "response_chars": len(response),
                    "structured_fields_found": found,
                }
            )

            results[label] = {
                "status": "success",
                "filepath": str(filepath),
                "elapsed": round(elapsed, 1),
                "chars": len(response),
                "structured_fields": found,
            }

            _log(f"✓ {label} complete. Saved to {filepath.name}")

        except CircuitBreakerTripped as e:
            _log(f"\n!!! CIRCUIT BREAKER TRIPPED !!!")
            _log(f"Condition: {e.condition}")
            _log(f"Model: {e.model}")
            _log(f"Detail: {e.detail}")
            results[label] = {"status": "circuit_breaker", "error": str(e)}
            _log(f"\nHalting. {len(results)} models dispatched before halt.")
            break

        except Exception as e:
            _log(f"\n!!! ERROR dispatching to {label}: {str(e)[:300]}")
            results[label] = {"status": "error", "error": str(e)[:500]}
            _log(f"Continuing with remaining models. {label} marked as failed.")

    # Summary
    _log(f"\n{'='*60}")
    _log(f"Phase 2 Blind Round Summary")
    _log(f"{'='*60}")
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    _log(f"Successful: {success_count}/{len(dispatch_order)}")
    for label, result in results.items():
        status = result.get("status", "unknown")
        if status == "success":
            _log(f"  {label}: ✓ {result['chars']} chars, {result['elapsed']}s, {result['structured_fields']}/4 fields")
        else:
            _log(f"  {label}: ✗ {status} — {result.get('error', 'unknown')[:100]}")

    # Save summary
    summary_path = logs_dir / "phase2_summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    _log(f"\nSummary saved to {summary_path}")

    if success_count < len(dispatch_order):
        _log(f"\nWARNING: {len(dispatch_order) - success_count} model(s) failed.")
        _log("Review logs and decide whether to re-dispatch or proceed without.")
        sys.exit(1)
    else:
        _log(f"\nAll {success_count} models completed successfully. Ready for Phase 3.")
        sys.exit(0)


if __name__ == "__main__":
    main()
