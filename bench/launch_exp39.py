#!/usr/bin/env python3
"""Exp 39 sub-experiment sequencer.

Reads bench/exp39_config.json, resolves dependency order, and launches
sub-experiments via reference_runner.py.  Gate failures block downstream
required experiments.  Optional experiments log failures but don't block.

Usage:
    python3 bench/launch_exp39.py                  # run all
    python3 bench/launch_exp39.py --only 39-0      # single sub-experiment
    python3 bench/launch_exp39.py --skip 39-K 39-L 39-M  # skip shadows
    python3 bench/launch_exp39.py --dry-run         # show execution plan
    python3 bench/launch_exp39.py --preflight       # connectivity check only
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "bench" / "exp39_config.json"
RUNNER_PATH = REPO_ROOT / "bench" / "reference_runner.py"
ARTIFACT_DIR = REPO_ROOT / "bench" / "logs" / "exp39_artifacts"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SubExperiment:
    """One sub-experiment from the master config."""
    id: str
    name: str
    type: str  # gate, research, integration, shadow
    config: str
    required: bool
    depends_on: list[str] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "SubExperiment":
        return cls(
            id=d["id"],
            name=d["name"],
            type=d["type"],
            config=d["config"],
            required=d.get("required", True),
            depends_on=d.get("depends_on", []),
            description=d.get("description", ""),
        )


@dataclass
class RunResult:
    """Outcome of a single sub-experiment run."""
    sub_id: str
    exit_code: int
    started: str
    finished: str
    duration_s: float
    skipped: bool = False
    skip_reason: str = ""
    logs_dir: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @property
    def terminated(self) -> bool:
        return self.exit_code == 2

    def summary_line(self) -> str:
        if self.skipped:
            return f"  {self.sub_id}: SKIPPED ({self.skip_reason})"
        status = "PASS" if self.passed else ("TERMINATED" if self.terminated else "FAIL")
        return f"  {self.sub_id}: {status} ({self.duration_s:.0f}s)"


# ---------------------------------------------------------------------------
# Dependency resolution
# ---------------------------------------------------------------------------

def resolve_execution_order(
    experiments: list[SubExperiment],
    skip_ids: set[str] | None = None,
    only_ids: set[str] | None = None,
) -> list[SubExperiment]:
    """Topological sort respecting depends_on.  Filters by skip/only."""
    by_id = {e.id: e for e in experiments}
    skip_ids = skip_ids or set()

    if only_ids:
        # Include requested IDs plus all transitive dependencies
        needed: set[str] = set()
        queue = list(only_ids)
        while queue:
            eid = queue.pop()
            if eid in needed or eid not in by_id:
                continue
            needed.add(eid)
            queue.extend(by_id[eid].depends_on)
        skip_ids = {e.id for e in experiments if e.id not in needed}

    # Kahn's algorithm
    in_degree: dict[str, int] = {}
    adj: dict[str, list[str]] = {}
    for e in experiments:
        if e.id in skip_ids:
            continue
        in_degree.setdefault(e.id, 0)
        adj.setdefault(e.id, [])
        for dep in e.depends_on:
            if dep in skip_ids:
                continue
            adj.setdefault(dep, []).append(e.id)
            in_degree[e.id] = in_degree.get(e.id, 0) + 1

    queue_k = [eid for eid, deg in in_degree.items() if deg == 0]
    queue_k.sort()  # deterministic
    ordered: list[str] = []
    while queue_k:
        eid = queue_k.pop(0)
        ordered.append(eid)
        for child in adj.get(eid, []):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue_k.append(child)
                queue_k.sort()

    if len(ordered) != len(in_degree):
        missing = set(in_degree.keys()) - set(ordered)
        raise ValueError(f"Dependency cycle detected involving: {missing}")

    return [by_id[eid] for eid in ordered]


# ---------------------------------------------------------------------------
# Runner invocation
# ---------------------------------------------------------------------------

def run_sub_experiment(exp: SubExperiment, dry_run: bool = False) -> RunResult:
    """Launch a single sub-experiment via reference_runner.py."""
    config_path = REPO_ROOT / exp.config
    if not config_path.exists():
        return RunResult(
            sub_id=exp.id,
            exit_code=1,
            started=_now(),
            finished=_now(),
            duration_s=0.0,
            skipped=True,
            skip_reason=f"config not found: {exp.config}",
        )

    cmd = [
        sys.executable,
        str(RUNNER_PATH),
        "run",
        "--config", str(config_path),
    ]

    _log(f"\n{'='*72}")
    _log(f"  SUB-EXPERIMENT: {exp.id} — {exp.name}")
    _log(f"  Type: {exp.type} | Required: {exp.required}")
    _log(f"  Config: {exp.config}")
    _log(f"  Command: {' '.join(cmd)}")
    _log(f"{'='*72}")

    if dry_run:
        return RunResult(
            sub_id=exp.id,
            exit_code=0,
            started=_now(),
            finished=_now(),
            duration_s=0.0,
            skipped=True,
            skip_reason="dry run",
        )

    started = _now()
    t0 = time.monotonic()

    # Read wall clock cap from config for subprocess timeout
    try:
        cfg_data = json.loads(config_path.read_text(encoding="utf-8"))
        timeout_s = cfg_data.get("wall_clock_cap_s", 28800) + 300  # 5min grace
    except Exception:
        timeout_s = 28800 + 300

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            capture_output=False,  # stream to terminal
        )
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        _log(f"\n*** {exp.id} TIMED OUT after {timeout_s}s ***")
        exit_code = 3
    except Exception as e:
        _log(f"\n*** {exp.id} LAUNCH FAILED: {e} ***")
        exit_code = 4

    duration = time.monotonic() - t0
    finished = _now()

    return RunResult(
        sub_id=exp.id,
        exit_code=exit_code,
        started=started,
        finished=finished,
        duration_s=duration,
    )


# ---------------------------------------------------------------------------
# Sequencer
# ---------------------------------------------------------------------------

def run_sequence(
    experiments: list[SubExperiment],
    gate_policy: str = "fail_fast",
    dry_run: bool = False,
) -> list[RunResult]:
    """Run sub-experiments in order, respecting gate policy."""
    results: list[RunResult] = []
    results_by_id: dict[str, RunResult] = {}
    failed_required: set[str] = set()

    for exp in experiments:
        # Check if dependencies are met
        unmet = []
        for dep_id in exp.depends_on:
            dep_result = results_by_id.get(dep_id)
            if dep_result is None:
                continue  # dependency was skipped/filtered
            if not dep_result.passed and not dep_result.skipped:
                unmet.append(dep_id)

        if unmet:
            reason = f"dependency failed: {', '.join(unmet)}"
            if exp.required and gate_policy == "fail_fast":
                _log(f"\n  SKIPPING {exp.id} ({exp.name}): {reason}")
                r = RunResult(
                    sub_id=exp.id,
                    exit_code=1,
                    started=_now(),
                    finished=_now(),
                    duration_s=0.0,
                    skipped=True,
                    skip_reason=reason,
                )
                results.append(r)
                results_by_id[exp.id] = r
                failed_required.add(exp.id)
                continue
            elif not exp.required:
                _log(f"\n  SKIPPING optional {exp.id} ({exp.name}): {reason}")
                r = RunResult(
                    sub_id=exp.id,
                    exit_code=1,
                    started=_now(),
                    finished=_now(),
                    duration_s=0.0,
                    skipped=True,
                    skip_reason=reason,
                )
                results.append(r)
                results_by_id[exp.id] = r
                continue

        # Run it
        r = run_sub_experiment(exp, dry_run=dry_run)
        results.append(r)
        results_by_id[exp.id] = r

        if not r.passed and not r.skipped:
            if exp.required:
                failed_required.add(exp.id)
                if gate_policy == "fail_fast" and exp.type == "gate":
                    _log(f"\n*** GATE FAILED: {exp.id} — halting sequence ***")
                    break

    return results


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_sequence_report(results: list[RunResult]) -> Path:
    """Write a JSON summary of the full sequence run."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = ARTIFACT_DIR / f"exp39_sequence_{ts}.json"

    passed = [r for r in results if r.passed and not r.skipped]
    failed = [r for r in results if not r.passed and not r.skipped]
    skipped = [r for r in results if r.skipped]

    report = {
        "timestamp": ts,
        "total": len(results),
        "passed": len(passed),
        "failed": len(failed),
        "skipped": len(skipped),
        "total_duration_s": sum(r.duration_s for r in results),
        "results": [
            {
                "id": r.sub_id,
                "exit_code": r.exit_code,
                "passed": r.passed,
                "skipped": r.skipped,
                "skip_reason": r.skip_reason,
                "started": r.started,
                "finished": r.finished,
                "duration_s": round(r.duration_s, 1),
            }
            for r in results
        ],
    }

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _log(f"\nSequence report: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Exp 39 sub-experiment sequencer",
    )
    parser.add_argument("--config", default=str(CONFIG_PATH),
                        help="Master config JSON (default: bench/exp39_config.json)")
    parser.add_argument("--only", nargs="+", default=[],
                        help="Run only these sub-experiment IDs (+ dependencies)")
    parser.add_argument("--skip", nargs="+", default=[],
                        help="Skip these sub-experiment IDs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show execution plan without running")
    parser.add_argument("--preflight", action="store_true",
                        help="Run preflight connectivity check only")
    args = parser.parse_args()

    # Load master config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    master = json.loads(config_path.read_text(encoding="utf-8"))
    experiments = [SubExperiment.from_dict(d) for d in master["sub_experiments"]]
    gate_policy = master.get("gate_policy", "fail_fast")

    # Preflight
    if args.preflight:
        cmd = [sys.executable, str(RUNNER_PATH), "preflight"]
        _log("Running preflight connectivity check...")
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
        sys.exit(proc.returncode)

    # Resolve execution order
    skip_ids = set(args.skip) if args.skip else None
    only_ids = set(args.only) if args.only else None
    ordered = resolve_execution_order(experiments, skip_ids=skip_ids, only_ids=only_ids)

    _log(f"\nExp 39 Sequencer — {len(ordered)} sub-experiments queued")
    _log(f"Gate policy: {gate_policy}")
    _log(f"\nExecution order:")
    for i, e in enumerate(ordered, 1):
        deps = f" (after {', '.join(e.depends_on)})" if e.depends_on else ""
        req = " [REQUIRED]" if e.required else " [optional]"
        _log(f"  {i:2d}. {e.id} — {e.name}{deps}{req}")

    if args.dry_run:
        _log("\n[DRY RUN] No experiments executed.")
        sys.exit(0)

    # Run
    _log(f"\nStarting sequence at {_now()}")
    results = run_sequence(ordered, gate_policy=gate_policy)

    # Report
    _log(f"\n{'='*72}")
    _log(f"  SEQUENCE COMPLETE")
    _log(f"{'='*72}")
    for r in results:
        _log(r.summary_line())

    report_path = write_sequence_report(results)

    # Exit code: 0 if all required passed, 1 otherwise
    required_failures = [
        r for r in results
        if not r.passed and not r.skipped
        and any(e.required for e in experiments if e.id == r.sub_id)
    ]
    if required_failures:
        _log(f"\n*** {len(required_failures)} required sub-experiment(s) failed ***")
        sys.exit(1)

    _log(f"\nAll required sub-experiments passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
