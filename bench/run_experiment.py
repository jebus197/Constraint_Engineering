#!/usr/bin/env python3
"""
Unified experiment runner for CDSFL pilot.

Runs the benchmark across all model configurations defined in the
experiment plan, collates results, and produces a single output file.

Usage:
    # Load keys from .env, run full pilot
    source .env && python3 bench/run_experiment.py

    # Dry run (no API calls)
    python3 bench/run_experiment.py --dry-run

    # Run a single config only
    source .env && python3 bench/run_experiment.py --config sonnet-4

    # Custom task subset
    source .env && python3 bench/run_experiment.py --task-ids st-001,ch-003,ma-001
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import from the existing benchmark harness
from run_benchmark import (
    CDSFL_DIRECTIVES,
    PROVIDERS,
    load_tasks,
    validate_task,
    run_control,
    run_experimental,
    run_extended,
    load_directives,
    load_domain_directives,
    compose_directives,
    _err,
)

# ---------------------------------------------------------------------------
# Model configurations for the pilot experiment
# ---------------------------------------------------------------------------

MODEL_CONFIGS: dict[str, dict[str, Any]] = {
    "sonnet-4": {
        "model": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "description": "Claude Sonnet 4 (standard)",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "sonnet-4-thinking": {
        "model": "claude-sonnet-4-20250514",
        "provider": "anthropic-thinking",
        "description": "Claude Sonnet 4 (extended thinking)",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "gpt-4o": {
        "model": "gpt-4o",
        "provider": "openai",
        "description": "GPT-4o (standard)",
        "env_key": "OPENAI_API_KEY",
    },
    "o3-mini": {
        "model": "o3-mini",
        "provider": "openai-reasoning",
        "description": "OpenAI o3-mini (reasoning)",
        "env_key": "OPENAI_API_KEY",
    },
    "gemini-flash": {
        "model": "gemini-2.5-flash",
        "provider": "gemini",
        "description": "Gemini 2.5 Flash (standard)",
        "env_key": "GOOGLE_API_KEY",
    },
    "gemini-pro": {
        "model": "gemini-2.5-pro",
        "provider": "gemini",
        "description": "Gemini 2.5 Pro (thinking)",
        "env_key": "GOOGLE_API_KEY",
    },
    "llama-3.3-70b": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "description": "Llama 3.3 70B (via Groq)",
        "env_key": "GROQ_API_KEY",
    },
}

# Default pilot subset: 2 tasks per domain (first two by ID)
PILOT_TASK_IDS = [
    "bm-001", "bm-002",  # biomedical
    "ch-001", "ch-002",  # chemistry
    "xd-001", "xd-002",  # cross-domain
    "hw-001", "hw-002",  # hardware
    "id-001", "id-002",  # industrial
    "lg-001", "lg-002",  # logistics
    "ma-001", "ma-002",  # mathematics
    "pe-001", "pe-002",  # product-engineering
    "sw-001", "sw-002",  # software
    "st-001", "st-002",  # structural
]


def filter_tasks(
    tasks: list[dict[str, Any]],
    task_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter tasks to the pilot subset."""
    if task_ids is None:
        task_ids = PILOT_TASK_IDS
    id_set = set(task_ids)
    filtered = [t for t in tasks if t.get("id") in id_set]
    # Warn about missing tasks
    found_ids = {t.get("id") for t in filtered}
    missing = id_set - found_ids
    if missing:
        _err(f"WARNING: requested task IDs not found: {sorted(missing)}")
    return filtered


def run_config(
    config_name: str,
    config: dict[str, Any],
    tasks: list[dict[str, Any]],
    directives: str,
    num_passes: int,
    mode: str,
    directives_dir: Path | None,
    condition: str,
    variant: str | None,
) -> dict[str, Any]:
    """Run all tasks for a single model configuration."""
    model = config["model"]
    provider = config["provider"]
    call = PROVIDERS[provider]
    results = []
    total = len(tasks)

    for idx, task in enumerate(tasks, 1):
        task_id = task.get("id", "<no-id>")
        domain = task.get("domain", "<no-domain>")
        _err(f"\n  [{idx}/{total}] Task {task_id} (domain: {domain})")

        # Compose directives
        domain_specific = None
        if directives_dir and condition != "universal-only":
            domain_specific = load_domain_directives(directives_dir, domain, variant)

        task_directives = compose_directives(directives, domain_specific, condition)

        # Run control
        control_result = run_control(task, model, provider)

        # Run experimental
        if mode == "extended":
            exp_result = run_extended(task, model, provider, task_directives, num_passes)
        else:
            exp_result = run_experimental(task, model, provider, task_directives, num_passes)

        results.append({
            "task_id": task_id,
            "domain": domain,
            "prompt": task["prompt"],
            "source_file": task.get("_source_file", ""),
            "seeded_faults": task.get("seeded_faults", []),
            "ground_truth_notes": task.get("ground_truth_notes", ""),
            "control": control_result,
            "experimental": exp_result,
        })

    return {
        "config_name": config_name,
        "config": config,
        "task_count": total,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CDSFL unified experiment runner — runs all model configs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Run a single config only (e.g. 'sonnet-4', 'o3-mini'). "
             f"Available: {', '.join(MODEL_CONFIGS.keys())}",
    )
    parser.add_argument(
        "--task-ids",
        type=str,
        default=None,
        help="Comma-separated task IDs to run (default: pilot subset of 20)",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Number of P-Passes (default: 3)",
    )
    parser.add_argument(
        "--mode",
        choices=["standard", "extended"],
        default="standard",
        help="P-Pass mode (default: standard)",
    )
    parser.add_argument(
        "--condition",
        choices=["universal-only", "universal+domain", "domain-only"],
        default="universal+domain",
        help="Directive condition (default: universal+domain)",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        help="Domain directive variant",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="bench/results",
        help="Output directory for results (default: bench/results/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would run without making API calls",
    )

    args = parser.parse_args()

    # Load and filter tasks
    tasks_dir = Path(__file__).parent / "tasks"
    _err(f"Loading tasks from {tasks_dir} ...")
    all_tasks = load_tasks(tasks_dir)

    errors = []
    for t in all_tasks:
        errors.extend(validate_task(t))
    if errors:
        for e in errors:
            _err(f"  VALIDATION ERROR: {e}")
        sys.exit(1)

    task_ids = args.task_ids.split(",") if args.task_ids else None
    tasks = filter_tasks(all_tasks, task_ids)
    _err(f"Selected {len(tasks)} tasks for experiment.")

    # Determine which configs to run
    if args.config:
        if args.config not in MODEL_CONFIGS:
            _err(f"ERROR: unknown config '{args.config}'. "
                 f"Available: {', '.join(MODEL_CONFIGS.keys())}")
            sys.exit(1)
        configs = {args.config: MODEL_CONFIGS[args.config]}
    else:
        configs = MODEL_CONFIGS

    # Check env keys
    missing_keys = set()
    for name, cfg in configs.items():
        key = cfg["env_key"]
        if not os.environ.get(key):
            missing_keys.add(f"{key} (needed for {name})")
    if missing_keys and not args.dry_run:
        _err("ERROR: missing environment variables:")
        for mk in sorted(missing_keys):
            _err(f"  - {mk}")
        _err("Load them with: source .env")
        sys.exit(1)

    directives = load_directives(None)  # built-in CDSFL directives
    directives_dir = Path(__file__).parent / "directives"

    # Dry run
    if args.dry_run:
        _err("\n=== DRY RUN ===")
        _err(f"Tasks: {len(tasks)}")
        _err(f"Configs: {len(configs)}")
        _err(f"Mode: {args.mode}, Passes: {args.passes}, Condition: {args.condition}")
        _err(f"Total API calls: {len(tasks) * len(configs) * (args.passes + 1)}")
        _err("\nConfigs to run:")
        for name, cfg in configs.items():
            key = cfg["env_key"]
            has_key = "OK" if os.environ.get(key) else "MISSING"
            _err(f"  {name}: {cfg['description']} [{has_key}]")
        _err("\nTasks:")
        for t in tasks:
            faults = len(t.get("seeded_faults", []))
            _err(f"  {t['id']} ({t['domain']}) — {faults} faults")
        sys.exit(0)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    experiment_start = time.monotonic()

    all_config_results = []

    for config_name, config in configs.items():
        _err(f"\n{'='*60}")
        _err(f"CONFIG: {config_name} — {config['description']}")
        _err(f"{'='*60}")

        config_start = time.monotonic()
        config_result = run_config(
            config_name, config, tasks, directives, args.passes, args.mode,
            directives_dir, args.condition, args.variant,
        )
        config_elapsed = time.monotonic() - config_start
        config_result["elapsed_seconds"] = round(config_elapsed, 2)
        all_config_results.append(config_result)

        # Write per-config results
        config_file = output_dir / f"{config_name}_{timestamp}.json"
        config_output = {
            "benchmark_meta": {
                "schema_version": "cdsfl-experiment-v1",
                "config_name": config_name,
                "model": config["model"],
                "provider": config["provider"],
                "description": config["description"],
                "num_passes": args.passes,
                "mode": args.mode,
                "directive_condition": args.condition,
                "task_count": len(tasks),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
            "results": config_result["results"],
        }
        config_file.write_text(
            json.dumps(config_output, indent=2) + "\n", encoding="utf-8"
        )
        _err(f"\nResults for {config_name} written to {config_file}")

    total_elapsed = time.monotonic() - experiment_start

    # Write combined summary
    summary_file = output_dir / f"experiment_summary_{timestamp}.json"
    summary = {
        "experiment_meta": {
            "schema_version": "cdsfl-experiment-v1",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "total_elapsed_seconds": round(total_elapsed, 2),
            "num_configs": len(configs),
            "num_tasks": len(tasks),
            "num_passes": args.passes,
            "mode": args.mode,
            "directive_condition": args.condition,
            "task_ids": [t["id"] for t in tasks],
        },
        "configs_run": [
            {
                "name": r["config_name"],
                "description": r["config"]["description"],
                "elapsed_seconds": r["elapsed_seconds"],
                "task_count": r["task_count"],
            }
            for r in all_config_results
        ],
    }
    summary_file.write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    _err(f"\n{'='*60}")
    _err(f"EXPERIMENT COMPLETE")
    _err(f"  Configs: {len(configs)}")
    _err(f"  Tasks per config: {len(tasks)}")
    _err(f"  Total time: {total_elapsed:.0f}s")
    _err(f"  Summary: {summary_file}")
    _err(f"{'='*60}")


if __name__ == "__main__":
    main()
