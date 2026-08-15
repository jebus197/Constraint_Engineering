#!/usr/bin/env python3
"""Experiment 16: Plan Review Under CDSFL.

Models review the Experiment 17 plan (immune + load balancing layer validation)
operating UNDER CDSFL directives. This is a single blind round — each model
independently reviews the plan and proposes improvements.

The test article is the PLAN, not code. Models are asked to:
1. P-pass the plan under CDSFL (falsify claims, check completeness)
2. Answer the 4 open questions in §7
3. Propose specific improvements with justification

CC1 (this script's caller) is collator — merges improvements into the plan.

Usage:
    python3 bench/run_exp16_plan_review.py [preflight|run]

    preflight  — verify all models respond and keys are valid
    run        — execute the blind review round
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    load_default_config,
    dispatch,
    save_output,
    _log,
    CircuitBreakerTripped,
    ExperimentConfig,
    ModelConfig,
)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

EXPERIMENT = "16"
LOGS_DIR = REPO_ROOT / "bench" / "logs" / f"experiment_{EXPERIMENT}"
EXP17_PLAN_PATH = REPO_ROOT / "bench" / "logs" / "experiment_17_plan.md"
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"


def source_env() -> None:
    """Load .env file."""
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()


def build_review_prompt(plan_text: str) -> str:
    """Build the CDSFL plan review prompt."""
    return (
        "You are participating in Experiment 16: a CDSFL-governed review of "
        "an experiment plan.\n\n"
        "Your system prompt contains the CDSFL core directives. You must "
        "operate UNDER these directives while reviewing the plan below.\n\n"
        "## Your Task\n\n"
        "1. **P-pass the plan** — identify the strongest falsifying conditions "
        "for each claim or assumption in the plan. For each:\n"
        "   - State the assumption\n"
        "   - State the falsifier\n"
        "   - Assess whether it holds\n"
        "   - If it doesn't hold: propose a specific revision\n\n"
        "2. **Answer the 4 open questions** in §7 of the plan. For each, "
        "provide a specific recommendation with justification.\n\n"
        "3. **Propose improvements** — anything the plan is missing, any "
        "scope that should be added or removed, any risks not covered, any "
        "protocol gaps.\n\n"
        "## Output Format\n\n"
        "Structure your response as:\n\n"
        "### P-PASS FINDINGS\n"
        "For each finding:\n"
        "  FINDING_ID: PF001 (etc.)\n"
        "  ASSUMPTION: what the plan assumes\n"
        "  FALSIFIER: the condition that would prove it wrong\n"
        "  ASSESSMENT: HOLDS | FAILS | UNCERTAIN\n"
        "  SEVERITY: 0.0–1.0\n"
        "  REVISION: specific change to the plan (if needed)\n\n"
        "### OPEN QUESTION RESPONSES\n"
        "  Q1: [your answer + justification]\n"
        "  Q2: [your answer + justification]\n"
        "  Q3: [your answer + justification]\n"
        "  Q4: [your answer + justification]\n\n"
        "### PROPOSED IMPROVEMENTS\n"
        "  IMP001: [description + justification]\n"
        "  IMP002: ...\n\n"
        "Be thorough. This plan will be executed as Experiment 17 — your "
        "review is the last check before live execution.\n\n"
        "=== EXPERIMENT 17 PLAN (TEST ARTICLE) ===\n\n"
        f"{plan_text}\n\n"
        "=== END PLAN ===\n\n"
        "Produce your review now."
    )


def _dispatch_worker(mc, p, c, q):
    """Worker function for multiprocessing watchdog (must be module-level)."""
    try:
        response = dispatch(mc, p, c)
        q.put(("ok", response))
    except Exception as e:
        q.put(("error", e))


def _dispatch_with_watchdog(
    model_config: ModelConfig,
    prompt: str,
    cdsfl_text: str,
) -> tuple[str, float]:
    """Dispatch with multiprocessing watchdog (from run_exp12_live_wire.py)."""
    import multiprocessing as mp

    wall_clock_limit = model_config.timeout * 2

    t0 = time.monotonic()
    result_queue = mp.Queue()
    proc = mp.Process(
        target=_dispatch_worker,
        args=(model_config, prompt, cdsfl_text, result_queue),
        daemon=True,
    )
    proc.start()
    proc.join(timeout=wall_clock_limit)
    elapsed = time.monotonic() - t0

    if proc.is_alive():
        _log(f"  {model_config.label}: WATCHDOG — exceeded {wall_clock_limit:.0f}s, terminating")
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=2)
        raise TimeoutError(
            f"{model_config.label} exceeded wall-clock limit ({wall_clock_limit:.0f}s)"
        )

    if result_queue.empty():
        # Gemini's genai client can fail to pickle results through mp.Queue.
        # Fall back to direct (in-process) dispatch.
        _log(f"  {model_config.label}: watchdog queue empty (exit {proc.exitcode}), falling back to direct dispatch")
        t0 = time.monotonic()
        response = dispatch(model_config, prompt, cdsfl_text)
        elapsed = time.monotonic() - t0
        return response, elapsed

    status, payload = result_queue.get_nowait()
    if status == "error":
        raise payload
    return payload, elapsed


# ─────────────────────────────────────────────────────────────────────────────
# Preflight
# ─────────────────────────────────────────────────────────────────────────────

PREFLIGHT_PROMPT = (
    "Respond with exactly one sentence confirming you can read this message "
    "and are ready to review an experiment plan under CDSFL."
)


def run_preflight(exp_config: ExperimentConfig) -> bool:
    """Verify all models respond correctly."""
    _log("=== PREFLIGHT CHECK ===")
    all_ok = True

    for mc in exp_config.models:
        if mc.role == "collator":
            continue
        try:
            _log(f"  Testing {mc.label}...")
            response, elapsed = _dispatch_with_watchdog(
                mc, PREFLIGHT_PROMPT, exp_config.cdsfl_system_prompt,
            )
            _log(f"  {mc.label}: OK ({elapsed:.1f}s, {len(response)} chars)")
            save_output(LOGS_DIR, "preflight", mc.label, PREFLIGHT_PROMPT, response,
                        {"elapsed_s": elapsed})
        except Exception as e:
            _log(f"  {mc.label}: FAIL — {type(e).__name__}: {e}")
            all_ok = False

    if all_ok:
        _log("Preflight PASSED — all models responding.")
    else:
        _log("Preflight FAILED — some models unreachable.")
    return all_ok


# ─────────────────────────────────────────────────────────────────────────────
# Main experiment: blind review round
# ─────────────────────────────────────────────────────────────────────────────

def run_review(exp_config: ExperimentConfig) -> Dict[str, Any]:
    """Run the blind review round. Returns collated results."""
    _log("=== EXPERIMENT 16: BLIND PLAN REVIEW ===")
    _log(f"Logs: {LOGS_DIR}")

    # Load plan
    if not EXP17_PLAN_PATH.exists():
        raise FileNotFoundError(f"Exp 17 plan not found: {EXP17_PLAN_PATH}")
    plan_text = EXP17_PLAN_PATH.read_text(encoding="utf-8")
    _log(f"Plan loaded: {len(plan_text)} chars, {len(plan_text.splitlines())} lines")

    # Build prompt
    prompt = build_review_prompt(plan_text)
    _log(f"Prompt: {len(prompt)} chars")

    cdsfl_text = exp_config.cdsfl_system_prompt
    _log(f"CDSFL system prompt: {len(cdsfl_text)} chars")

    # Sequential dispatch (M1 8GB constraint — one model at a time)
    results: Dict[str, Any] = {}
    models_dispatched = 0
    models_succeeded = 0

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        models_dispatched += 1
        _log(f"\n--- {mc.label} ({mc.model_id} via {mc.api}) ---")

        try:
            response, elapsed = _dispatch_with_watchdog(mc, prompt, cdsfl_text)
            _log(f"  Response: {len(response)} chars in {elapsed:.1f}s")

            # Save raw response
            filepath = save_output(
                LOGS_DIR, "review", mc.label, prompt, response,
                {
                    "elapsed_s": round(elapsed, 2),
                    "model_id": mc.model_id,
                    "api": mc.api,
                    "experiment": EXPERIMENT,
                    "phase": "blind_review",
                },
            )

            results[mc.label] = {
                "status": "ok",
                "response": response,
                "elapsed_s": round(elapsed, 2),
                "chars": len(response),
                "filepath": str(filepath),
            }
            models_succeeded += 1

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            results[mc.label] = {"status": "circuit_breaker", "error": str(e)}

        except TimeoutError as e:
            _log(f"  {mc.label}: TIMEOUT — {e}")
            results[mc.label] = {"status": "timeout", "error": str(e)}

        except Exception as e:
            _log(f"  {mc.label}: ERROR — {type(e).__name__}: {e}")
            results[mc.label] = {"status": "error", "error": str(e)}

    # Summary
    _log(f"\n=== SUMMARY ===")
    _log(f"Models dispatched: {models_dispatched}")
    _log(f"Models succeeded: {models_succeeded}")
    _log(f"Models failed: {models_dispatched - models_succeeded}")

    for label, r in results.items():
        if r["status"] == "ok":
            _log(f"  {label}: {r['chars']} chars, {r['elapsed_s']}s")
        else:
            _log(f"  {label}: {r['status']} — {r.get('error', 'unknown')}")

    # Save summary report
    summary = {
        "experiment": EXPERIMENT,
        "description": "Experiment 16: Blind plan review of Exp 17 under CDSFL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plan_source": str(EXP17_PLAN_PATH),
        "models_dispatched": models_dispatched,
        "models_succeeded": models_succeeded,
        "results": {
            label: {k: v for k, v in r.items() if k != "response"}
            for label, r in results.items()
        },
    }
    summary_path = LOGS_DIR / "experiment_16_summary.json"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _log(f"\nSummary saved: {summary_path}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Refuse a paid run on `--help` or a typo. Must be the FIRST thing
    # main() does: everything below this line can reach a paid model.
    from bench.runner_argv_guard import guard_argv
    guard_argv([], 'python3 bench/run_exp16_plan_review.py [preflight|run]')
    source_env()
    config = load_default_config()

    mode = sys.argv[1] if len(sys.argv) > 1 else "run"

    if mode == "preflight":
        ok = run_preflight(config)
        sys.exit(0 if ok else 1)

    elif mode == "run":
        # Preflight first
        if not run_preflight(config):
            _log("Aborting — preflight failed.")
            sys.exit(1)

        results = run_review(config)

        succeeded = sum(1 for r in results.values() if r["status"] == "ok")
        _log(f"\nExperiment 16 complete. {succeeded}/{len(results)} models produced reviews.")
        _log(f"Review logs at: {LOGS_DIR}")

    else:
        print(f"Usage: {sys.argv[0]} [preflight|run]")
        sys.exit(1)


if __name__ == "__main__":
    main()
