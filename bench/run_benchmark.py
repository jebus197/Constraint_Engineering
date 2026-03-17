#!/usr/bin/env python3
"""
Seeded-fault benchmark harness for CDSFL methodology evaluation.

Runs each task under two conditions:
  - Control:      prompt sent with no system prompt.
  - Experimental: prompt sent with CDSFL directives as system prompt,
                  then iteratively revised across n P-Passes.

Outputs raw results as JSON to stdout (or --output file).
Progress and diagnostics go to stderr.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# CDSFL core directives (Part IV, Section 4.1 of the paper)
# ---------------------------------------------------------------------------

CDSFL_DIRECTIVES = """\
Before producing any output, classify every constraint in the problem as \
HARD (physics, mathematics, law, safety - non-negotiable) or SOFT (economic, \
preference, convenience - negotiable). Ambiguous constraints default to HARD.

For every claim you make:
1. Identify the claim.
2. State the strongest falsifying condition - what observation or argument \
would prove this claim wrong?
3. Attempt to satisfy that condition. Actively try to disprove your own \
conclusion.
4. If the claim survives, mark it as provisionally accepted and state the \
residual uncertainty.
5. If the claim fails, revise or retract it before proceeding.

This is iterative: after revising, re-examine downstream claims that depended \
on the revised one. Continue until you reach genuine diminishing returns - \
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

INITIAL_PASS_TEMPLATE = """This is P-Pass {n} of {total}. Perform the full CDSFL loop on the task below.

Original task:
{task_prompt}

Instructions:
- Produce the strongest answer you can to the original task.
- Then attack that answer adversarially for errors, contradictions, physical impossibilities, logical flaws, legal or safety issues, and HARD or SOFT misclassification.
- Revise the answer to fix every issue you can justify fixing.
- Surface uncertainty honestly.
- Do not hide issues merely because you managed to revise them.

Return exactly these sections:
INITIAL_ANSWER:
...

ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

ADVERSARIAL_PASS_TEMPLATE = """You are an independent reviewer. This output was produced by another system \
and has not been independently verified. It may contain:

- Errors at interfaces between subsystems
- Unstated assumptions that conflict across components
- Constraint violations visible only at system level
- Conclusions that are internally consistent but physically or logically wrong

Your task is to find what is wrong, not to confirm what is right.

Original task:
{task_prompt}

Output to review:
{current_draft}

Instructions:
- Examine the complete output as an integrated system.
- Focus on cross-module interactions, shared assumptions, and emergent contradictions.
- Stop when all hard-constraint assumptions are sound and remaining findings represent \
genuinely diminishing returns. The threshold: would this finding, if missed, cause a \
real-world failure, violation, or unsafe condition? If not, it is below threshold.

Return exactly these sections:
ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

FOLLOWUP_PASS_TEMPLATE = """This is P-Pass {n} of {total}. Continue the CDSFL loop by attacking and revising the current draft.

Original task:
{task_prompt}

Current draft from the previous pass:
{current_draft}

Issues identified on the previous pass:
{prior_issues}

Instructions:
- Start from the current draft, not from scratch.
- Try to break the current draft harder than before.
- Look for newly introduced downstream problems caused by earlier fixes.
- Identify every additional issue you find.
- Revise the draft to fix what survives scrutiny.
- Preserve any parts that still survive attack.

Return exactly these sections:
ISSUES_FOUND:
- ...

REVISED_ANSWER:
...
"""

TASKS_DIR = Path(__file__).parent / "tasks"
REQUIRED_TASK_FIELDS = {"id", "domain", "prompt", "seeded_faults", "ground_truth_notes"}
REQUIRED_FAULT_FIELDS = {"id", "type", "description", "location_hint"}


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


def _err(msg: str) -> None:
    """Print to stderr."""
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Task loading
# ---------------------------------------------------------------------------


def load_tasks(tasks_dir: Path) -> list[dict[str, Any]]:
    """Recursively load all .json task files from tasks_dir."""
    tasks: list[dict[str, Any]] = []
    if not tasks_dir.is_dir():
        _err(f"Tasks directory not found: {tasks_dir}")
        return tasks

    for json_path in sorted(tasks_dir.rglob("*.json")):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
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

    client = anthropic.Anthropic()
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

    client = openai.OpenAI()
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content or ""


PROVIDERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
}


# ---------------------------------------------------------------------------
# Experimental prompt construction
# ---------------------------------------------------------------------------


SECTION_LABELS = ("INITIAL_ANSWER", "ISSUES_FOUND", "REVISED_ANSWER")


def _extract_section(text: str, label: str) -> str | None:
    """Extract a labelled section from a model response."""
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



def _build_pass_prompt(
    task_prompt: str,
    pass_number: int,
    total_passes: int,
    current_draft: str | None,
    prior_issues: str | None,
) -> str:
    """Build the user prompt for the current experimental pass."""
    if current_draft is None:
        return INITIAL_PASS_TEMPLATE.format(
            n=pass_number,
            total=total_passes,
            task_prompt=task_prompt,
        )

    return FOLLOWUP_PASS_TEMPLATE.format(
        n=pass_number,
        total=total_passes,
        task_prompt=task_prompt,
        current_draft=current_draft.strip(),
        prior_issues=(prior_issues or "- No explicit issues listed on the prior pass."),
    )


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
    """Run the experimental condition: CDSFL directives + iterative P-Passes."""
    call = PROVIDERS[provider]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None

    for i in range(1, num_passes + 1):
        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=num_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        _err(f"  [experimental] P-Pass {i}/{num_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = call(model, directives, user_prompt)
        elapsed = time.monotonic() - t0
        _err(f"  [experimental] P-Pass {i}/{num_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)

        current_draft = extracted_revision or response
        prior_issues = extracted_issues

    return {
        "condition": "experimental",
        "model": model,
        "provider": provider,
        "num_passes": num_passes,
        "passes": passes,
        "final_response": current_draft or "",
    }



def run_extended(
    task: dict[str, Any],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
) -> dict[str, Any]:
    """Run the final-pass-isolation condition.

    Passes 1 to (num_passes - 1) run as standard iterative P-Passes in one
    context chain.  The final pass runs in an isolated context containing only
    the original task and the current draft — no prior P-Pass conclusions.

    NOTE: This is NOT the full Extended P-Pass protocol from CLAUDE.md, which
    specifies 4 module-scoped passes + 1 isolated adversarial pass. This mode
    tests final-pass context isolation only — module-aware decomposition would
    require per-task module maps that the current task schema does not provide.
    """
    call = PROVIDERS[provider]
    passes: list[dict[str, Any]] = []
    current_draft: str | None = None
    prior_issues: str | None = None

    # Modular passes (1 through n-1)
    modular_count = max(num_passes - 1, 1)
    for i in range(1, modular_count + 1):
        user_prompt = _build_pass_prompt(
            task_prompt=task["prompt"],
            pass_number=i,
            total_passes=num_passes,
            current_draft=current_draft,
            prior_issues=prior_issues,
        )

        _err(f"  [extended] iterative P-Pass {i}/{num_passes}, calling {provider}/{model} ...")
        t0 = time.monotonic()
        response = call(model, directives, user_prompt)
        elapsed = time.monotonic() - t0
        _err(f"  [extended] iterative P-Pass {i}/{num_passes} done ({elapsed:.1f}s)")

        extracted_issues = _extract_section(response, "ISSUES_FOUND")
        extracted_revision = _extract_section(response, "REVISED_ANSWER")
        extracted_initial = _extract_section(response, "INITIAL_ANSWER")

        pass_record: dict[str, Any] = {
            "pass_number": i,
            "pass_type": "iterative",
            "response": response,
            "elapsed_seconds": round(elapsed, 2),
        }
        if extracted_initial is not None:
            pass_record["initial_answer"] = extracted_initial
        if extracted_issues is not None:
            pass_record["issues_found"] = extracted_issues
        if extracted_revision is not None:
            pass_record["revised_answer"] = extracted_revision

        passes.append(pass_record)
        current_draft = extracted_revision or response
        prior_issues = extracted_issues

    # Isolated adversarial pass (final pass — fresh context, no prior P-Pass data)
    adversarial_prompt = ADVERSARIAL_PASS_TEMPLATE.format(
        task_prompt=task["prompt"],
        current_draft=(current_draft or "").strip(),
    )

    _err(f"  [extended] adversarial P-Pass {num_passes}/{num_passes}, calling {provider}/{model} (isolated context) ...")
    t0 = time.monotonic()
    # No system prompt for the adversarial pass — it operates without CDSFL
    # directives to avoid anchoring on the methodology that produced the draft.
    response = call(model, None, adversarial_prompt)
    elapsed = time.monotonic() - t0
    _err(f"  [extended] adversarial P-Pass {num_passes}/{num_passes} done ({elapsed:.1f}s)")

    extracted_issues = _extract_section(response, "ISSUES_FOUND")
    extracted_revision = _extract_section(response, "REVISED_ANSWER")

    pass_record = {
        "pass_number": num_passes,
        "pass_type": "adversarial_isolated",
        "response": response,
        "elapsed_seconds": round(elapsed, 2),
    }
    if extracted_issues is not None:
        pass_record["issues_found"] = extracted_issues
    if extracted_revision is not None:
        pass_record["revised_answer"] = extracted_revision

    passes.append(pass_record)
    final_draft = extracted_revision or current_draft or ""

    return {
        "condition": "extended",
        "model": model,
        "provider": provider,
        "num_passes": num_passes,
        "iterative_passes": modular_count,
        "adversarial_passes": 1,
        "passes": passes,
        "final_response": final_draft,
    }


def run_benchmark(
    tasks: list[dict[str, Any]],
    model: str,
    provider: str,
    directives: str,
    num_passes: int,
    mode: str = "standard",
    domain_directives_dir: Path | None = None,
    condition: str = "universal-only",
    variant: str | None = None,
) -> list[dict[str, Any]]:
    """Run all tasks under both conditions."""
    results = []
    total = len(tasks)

    for idx, task in enumerate(tasks, 1):
        task_id = task.get("id", "<no-id>")
        domain = task.get("domain", "<no-domain>")
        _err(f"\n[{idx}/{total}] Task {task_id} (domain: {domain})")

        # Compose directives for this task's domain
        domain_specific = None
        if domain_directives_dir and condition != "universal-only":
            domain_specific = load_domain_directives(
                domain_directives_dir, domain, variant
            )
            if domain_specific:
                _err(f"  [directives] loaded domain-specific directives for {domain}")
            else:
                _err(f"  [directives] no domain-specific directives found for {domain}")

        task_directives = compose_directives(directives, domain_specific, condition)

        if mode == "extended":
            experimental_result = run_extended(
                task, model, provider, task_directives, num_passes
            )
        else:
            experimental_result = run_experimental(
                task, model, provider, task_directives, num_passes
            )

        task_result: dict[str, Any] = {
            "task_id": task_id,
            "domain": domain,
            "prompt": task["prompt"],
            "source_file": task.get("_source_file", ""),
            "seeded_faults": task.get("seeded_faults", []),
            "ground_truth_notes": task.get("ground_truth_notes", ""),
            "control": run_control(task, model, provider),
            "experimental": experimental_result,
        }
        results.append(task_result)

    return results



def load_directives(path: str | None) -> str:
    """Load directives from a file, or return the built-in constant."""
    if path is None:
        return CDSFL_DIRECTIVES
    p = Path(path)
    if not p.is_file():
        _err(f"ERROR: directives file not found: {path}")
        sys.exit(1)
    return p.read_text(encoding="utf-8").strip()


def load_domain_directives(
    directives_dir: Path, domain: str, variant: str | None = None
) -> str | None:
    """Load domain-specific directives for a given domain.

    If *variant* is given, load that specific file (e.g. 'building' loads
    structural_building.txt from the domain folder).  Otherwise, load the
    first available .txt file alphabetically.

    Returns None if no matching file exists.
    """
    domain_dir = directives_dir / domain
    if not domain_dir.is_dir():
        return None

    if variant:
        # Try exact match first, then prefix match
        for txt_file in sorted(domain_dir.glob("*.txt")):
            stem = txt_file.stem  # e.g. "structural_building"
            if variant == stem or stem.endswith(f"_{variant}"):
                return txt_file.read_text(encoding="utf-8").strip()
        return None

    # Default: first available .txt file
    txt_files = sorted(domain_dir.glob("*.txt"))
    if txt_files:
        return txt_files[0].read_text(encoding="utf-8").strip()
    return None


def compose_directives(
    universal: str,
    domain_specific: str | None,
    condition: str,
) -> str:
    """Compose the system prompt from universal and domain-specific directives.

    Conditions:
      - universal-only:  universal directives only (default)
      - universal+domain: universal + domain-specific layered
      - domain-only:     domain-specific only (for ablation studies)
    """
    if condition == "domain-only":
        return domain_specific or universal  # fall back if no domain file
    if condition == "universal+domain" and domain_specific:
        return universal + "\n\n" + domain_specific
    return universal  # universal-only or no domain file available



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
        help="Path to a text file containing CDSFL directives (default: built-in constant)",
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
        "--mode",
        choices=["standard", "extended"],
        default="standard",
        help="P-Pass mode: 'standard' (all passes in same context) or "
             "'extended' (iterative passes + final-pass context isolation). "
             "Note: 'extended' tests context isolation only, not the full "
             "module-scoped Extended P-Pass from CLAUDE.md. Default: standard",
    )
    parser.add_argument(
        "--domain-directives",
        type=str,
        default=None,
        help="Path to domain directives directory (e.g. bench/directives/). "
             "Each subdirectory contains domain-specific directive files.",
    )
    parser.add_argument(
        "--condition",
        choices=["universal-only", "universal+domain", "domain-only"],
        default="universal-only",
        help="Directive condition: 'universal-only' (default), "
             "'universal+domain' (layers domain-specific on top of universal), "
             "or 'domain-only' (domain-specific only, for ablation studies).",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        help="Select a specific variant within each domain (e.g. 'building' "
             "selects structural_building.txt). If omitted, uses the first "
             "available variant alphabetically.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and validate tasks only - no API calls",
    )

    args = parser.parse_args()

    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else TASKS_DIR

    _err(f"Loading tasks from {tasks_dir} ...")
    tasks = load_tasks(tasks_dir)

    if not tasks:
        _err("No task files found. Nothing to do.")
        sys.exit(0)

    _err(f"Loaded {len(tasks)} task(s).")

    all_errors = []
    for task in tasks:
        all_errors.extend(validate_task(task))

    if all_errors:
        _err("Validation errors:")
        for err in all_errors:
            _err(f"  - {err}")
        sys.exit(1)

    _err("All tasks valid.")

    domain_directives_dir = Path(args.domain_directives) if args.domain_directives else None

    if args.dry_run:
        domains: dict[str, int] = {}
        for task in tasks:
            domain = task.get("domain", "<unknown>")
            domains[domain] = domains.get(domain, 0) + 1
        fault_count = sum(len(t.get("seeded_faults", [])) for t in tasks)

        _err("\nDry run summary:")
        _err(f"  Tasks:     {len(tasks)}")
        _err(f"  Faults:    {fault_count}")
        _err(f"  Mode:      {args.mode}")
        _err(f"  Condition: {args.condition}")
        if domain_directives_dir:
            _err(f"  Domain directives: {domain_directives_dir}")
            for domain_name in sorted(domains.keys()):
                dd = load_domain_directives(
                    domain_directives_dir, domain_name, args.variant
                )
                status = f"loaded ({len(dd)} chars)" if dd else "not found"
                _err(f"    {domain_name}: {status}")
        if args.variant:
            _err(f"  Variant:   {args.variant}")
        for domain_name, count in sorted(domains.items()):
            _err(f"  {domain_name}: {count} task(s)")
        sys.exit(0)

    directives = load_directives(args.directives)

    if args.provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        _err("ERROR: ANTHROPIC_API_KEY not set in environment.")
        sys.exit(1)
    if args.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        _err("ERROR: OPENAI_API_KEY not set in environment.")
        sys.exit(1)

    _err(
        f"\nRunning benchmark: model={args.model}, provider={args.provider}, "
        f"passes={args.passes}, mode={args.mode}, condition={args.condition}"
    )
    results = run_benchmark(
        tasks, args.model, args.provider, directives, args.passes, args.mode,
        domain_directives_dir=domain_directives_dir,
        condition=args.condition,
        variant=args.variant,
    )

    meta: dict[str, Any] = {
        "schema_version": "cdsfl-bench-v2",
        "model": args.model,
        "provider": args.provider,
        "num_passes": args.passes,
        "mode": args.mode,
        "directive_condition": args.condition,
        "task_count": len(tasks),
        "directives_source": args.directives or "built-in",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "domains": sorted({task.get("domain", "<unknown>") for task in tasks}),
    }
    if args.domain_directives:
        meta["domain_directives_source"] = args.domain_directives
    if args.variant:
        meta["variant"] = args.variant

    benchmark_output = {
        "benchmark_meta": meta,
        "results": results,
    }
    output_json = json.dumps(benchmark_output, indent=2)

    if args.output:
        Path(args.output).write_text(output_json + "\n", encoding="utf-8")
        _err(f"\nResults written to {args.output}")
    else:
        print(output_json)

    _err("\nDone.")


if __name__ == "__main__":
    main()
