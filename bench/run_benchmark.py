#!/usr/bin/env python3
"""
Seeded-fault benchmark harness for CDSFL methodology evaluation.

Runs each task under two conditions:
  - Control:      prompt sent with no system prompt.
  - Experimental: prompt sent with CDSFL directives as system prompt,
                  repeated over n P-Passes.

Outputs raw results as JSON to stdout (or --output file).
Progress and diagnostics go to stderr.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# CDSFL core directives (Part IV, §4.1 of the paper)
# ---------------------------------------------------------------------------

CDSFL_DIRECTIVES = """\
Before producing any output, classify every constraint in the problem as \
HARD (physics, mathematics, law, safety — non-negotiable) or SOFT (economic, \
preference, convenience — negotiable). Ambiguous constraints default to HARD.

For every claim you make:
1. Identify the claim.
2. State the strongest falsifying condition — what observation or argument \
would prove this claim wrong?
3. Attempt to satisfy that condition. Actively try to disprove your own \
conclusion.
4. If the claim survives, mark it as provisionally accepted and state the \
residual uncertainty.
5. If the claim fails, revise or retract it before proceeding.

This is iterative: after revising, re-examine downstream claims that depended \
on the revised one. Continue until you reach genuine diminishing returns — \
not until you feel comfortable, but until further passes produce no new \
failures or revisions.

Mark any claim that depends on present-day market conditions, technology \
availability, or regulatory state as [VERIFY:current]. Mark any untested \
inference as [SPECULATIVE]. Both inline, at point of claim.

Push back on impossible, contradictory, or ill-advised requirements. Say \
"no" or "I don't know" when either is the honest answer. Never fabricate \
certainty.

Default to the simplest sufficient solution. Justified complexity is \
complexity the user cannot do without.\
"""

PASS_INSTRUCTION = (
    "This is P-Pass {n} of {total}. Review the task for errors, "
    "contradictions, physical impossibilities, logical flaws, and constraint "
    "violations. Identify every issue you find. Be adversarial — actively "
    "try to find problems."
)

TASKS_DIR = Path(__file__).parent / "tasks"
REQUIRED_TASK_FIELDS = {"id", "domain", "prompt", "seeded_faults", "ground_truth_notes"}
REQUIRED_FAULT_FIELDS = {"id", "type", "description", "location_hint"}


# ---------------------------------------------------------------------------
# Task loading
# ---------------------------------------------------------------------------

def load_tasks(tasks_dir: Path) -> list[dict[str, Any]]:
    """Recursively load all .json task files from tasks_dir."""
    tasks = []
    if not tasks_dir.is_dir():
        _err(f"Tasks directory not found: {tasks_dir}")
        return tasks

    for json_path in sorted(tasks_dir.rglob("*.json")):
        try:
            with open(json_path) as f:
                task = json.load(f)
            task["_source_file"] = str(json_path.relative_to(tasks_dir))
            tasks.append(task)
        except (json.JSONDecodeError, OSError) as exc:
            _err(f"WARNING: skipping {json_path}: {exc}")
    return tasks


def validate_task(task: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors = []
    source = task.get("_source_file", "<unknown>")

    missing = REQUIRED_TASK_FIELDS - task.keys()
    if missing:
        errors.append(f"{source}: missing top-level fields: {missing}")

    faults = task.get("seeded_faults", [])
    if not isinstance(faults, list):
        errors.append(f"{source}: seeded_faults must be an array")
    else:
        for i, fault in enumerate(faults):
            if not isinstance(fault, dict):
                errors.append(f"{source}: seeded_faults[{i}] is not an object")
                continue
            fault_missing = REQUIRED_FAULT_FIELDS - fault.keys()
            if fault_missing:
                errors.append(
                    f"{source}: seeded_faults[{i}] missing fields: {fault_missing}"
                )
    return errors


# ---------------------------------------------------------------------------
# API callers
# ---------------------------------------------------------------------------

def call_anthropic(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a single request via the Anthropic SDK."""
    try:
        import anthropic
    except ImportError:
        _err("ERROR: `anthropic` package not installed. pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)
    return response.content[0].text


def call_openai(
    model: str,
    system_prompt: str | None,
    user_prompt: str,
) -> str:
    """Send a single request via the OpenAI SDK."""
    try:
        import openai
    except ImportError:
        _err("ERROR: `openai` package not installed. pip install openai")
        sys.exit(1)

    client = openai.OpenAI()  # reads OPENAI_API_KEY from env
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content


PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
}


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_control(
    task: dict[str, Any],
    model: str,
    provider: str,
) -> dict[str, Any]:
    """Run the control condition: bare prompt, no system instructions."""
    call = PROVIDERS[provider]
    _err(f"  [control] calling {provider}/{model} ...")
    t0 = time.monotonic()
    response = call(model, None, task["prompt"])
    elapsed = time.monotonic() - t0
    _err(f"  [control] done ({elapsed:.1f}s)")
    return {
        "condition": "control",
        "model": model,
        "provider": provider,
        "response": response,
        "elapsed_seconds": round(elapsed, 2),
    }


def run_experimental(
    task: dict[str, Any],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
) -> dict[str, Any]:
    """Run the experimental condition: CDSFL directives + n P-Passes."""
    call = PROVIDERS[provider]
    passes = []

    for i in range(1, num_passes + 1):
        pass_instruction = PASS_INSTRUCTION.format(n=i, total=num_passes)
        user_prompt = f"{pass_instruction}\n\n{task['prompt']}"

        _err(f"  [experimental] P-Pass {i}/{num_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = call(model, directives, user_prompt)
        elapsed = time.monotonic() - t0
        _err(f"  [experimental] P-Pass {i}/{num_passes} done ({elapsed:.1f}s)")

        passes.append({
            "pass_number": i,
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
        })

    return {
        "condition": "experimental",
        "model": model,
        "provider": provider,
        "num_passes": num_passes,
        "passes": passes,
    }


def run_benchmark(
    tasks: list[dict[str, Any]],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
) -> list[dict[str, Any]]:
    """Run all tasks under both conditions."""
    results = []
    total = len(tasks)

    for idx, task in enumerate(tasks, 1):
        task_id = task.get("id", "<no-id>")
        domain = task.get("domain", "<no-domain>")
        _err(f"\n[{idx}/{total}] Task {task_id} (domain: {domain})")

        task_result: dict[str, Any] = {
            "task_id": task_id,
            "domain": domain,
            "source_file": task.get("_source_file", ""),
            "seeded_faults": task.get("seeded_faults", []),
            "ground_truth_notes": task.get("ground_truth_notes", ""),
            "control": run_control(task, model, provider),
            "experimental": run_experimental(
                task, model, provider, directives, num_passes
            ),
        }
        results.append(task_result)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


def load_directives(path: str | None) -> str:
    """Load directives from a file, or return the built-in constant."""
    if path is None:
        return CDSFL_DIRECTIVES
    p = Path(path)
    if not p.is_file():
        _err(f"ERROR: directives file not found: {path}")
        sys.exit(1)
    return p.read_text().strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CDSFL seeded-fault benchmark harness.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="Model identifier (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="API provider (default: anthropic)",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Number of P-Passes for experimental condition (default: 3)",
    )
    parser.add_argument(
        "--directives",
        type=str,
        default=None,
        help="Path to a text file containing CDSFL directives "
             "(default: built-in constant)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write JSON results to this file instead of stdout",
    )
    parser.add_argument(
        "--tasks-dir",
        type=str,
        default=None,
        help="Path to tasks directory (default: bench/tasks/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and validate tasks only — no API calls",
    )

    args = parser.parse_args()

    # Resolve tasks directory
    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else TASKS_DIR

    # Load tasks
    _err(f"Loading tasks from {tasks_dir} ...")
    tasks = load_tasks(tasks_dir)

    if not tasks:
        _err("No task files found. Nothing to do.")
        sys.exit(0)

    _err(f"Loaded {len(tasks)} task(s).")

    # Validate
    all_errors = []
    for task in tasks:
        all_errors.extend(validate_task(task))

    if all_errors:
        _err("Validation errors:")
        for err in all_errors:
            _err(f"  - {err}")
        sys.exit(1)

    _err("All tasks valid.")

    # Dry run: report and exit
    if args.dry_run:
        domains = {}
        for task in tasks:
            d = task.get("domain", "<unknown>")
            domains[d] = domains.get(d, 0) + 1
        fault_count = sum(len(t.get("seeded_faults", [])) for t in tasks)

        _err(f"\nDry run summary:")
        _err(f"  Tasks:  {len(tasks)}")
        _err(f"  Faults: {fault_count}")
        for domain, count in sorted(domains.items()):
            _err(f"  {domain}: {count} task(s)")
        sys.exit(0)

    # Load directives
    directives = load_directives(args.directives)

    # Check API key availability
    if args.provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        _err("ERROR: ANTHROPIC_API_KEY not set in environment.")
        sys.exit(1)
    if args.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        _err("ERROR: OPENAI_API_KEY not set in environment.")
        sys.exit(1)

    # Run
    _err(
        f"\nRunning benchmark: model={args.model}, provider={args.provider}, "
        f"passes={args.passes}"
    )
    results = run_benchmark(
        tasks, args.model, args.provider, directives, args.passes
    )

    # Output
    output_json = json.dumps(
        {
            "benchmark_meta": {
                "model": args.model,
                "provider": args.provider,
                "num_passes": args.passes,
                "task_count": len(tasks),
                "directives_source": args.directives or "built-in",
            },
            "results": results,
        },
        indent=2,
    )

    if args.output:
        Path(args.output).write_text(output_json + "\n")
        _err(f"\nResults written to {args.output}")
    else:
        print(output_json)

    _err("\nDone.")


if __name__ == "__main__":
    main()
