#!/usr/bin/env python3
"""CDSFL Recovery Script — prints structured project state for CC1 instances.

Usage: python3 scripts/cdsfl_recover.py [--full]

  --full    Include test count (runs pytest, adds ~10s)

Designed to be fast and read-only. Outputs structured state summary
that a new CC1 instance can parse to rebuild working context.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import (
    git_state,
    latest_experiment,
    read_section,
    repo_root,
    test_count,
    timestamp_iso,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="CDSFL Recovery — rebuild working context")
    parser.add_argument("--full", action="store_true", help="Include live test count")
    args = parser.parse_args()

    root = repo_root()
    print(f"CDSFL Recovery — {timestamp_iso()}")
    print(f"Repository: {root}")
    print("=" * 70)

    # --- CURRENT STATE ---
    print("\n## CURRENT STATE\n")
    current_state = root / "docs" / "CURRENT_STATE.md"
    if current_state.exists():
        print(current_state.read_text(encoding="utf-8"))
    else:
        # Fallback: extract from ONBOARDING.md
        onboarding = root / "resources" / "ONBOARDING.md"
        section = read_section(onboarding, "## Current State", "\n## ")
        if section:
            # Print first 40 lines to avoid overwhelming output
            lines = section.splitlines()
            for line in lines[:40]:
                print(line)
            if len(lines) > 40:
                print(f"  ... ({len(lines) - 40} more lines in ONBOARDING.md)")
        else:
            print("  (No current state found — run cdsfl_sv.py to generate)")

    # --- GIT STATE ---
    print("\n## GIT STATE\n")
    gs = git_state()
    print(f"  Branch: {gs['branch']}")
    print(f"  Last commit: {gs['last_hash']} {gs['last_message']}")
    print(f"  Committed: {gs['last_date']}")
    print(f"  Remote: {gs['remote_sync']}")
    print(f"  Working tree: {'clean' if gs['clean'] else 'DIRTY'}")
    if not gs["clean"]:
        print("  Uncommitted:")
        for f in gs["uncommitted"][:20]:
            print(f"    {f}")

    # --- RECENT COMMITS ---
    print("\n## RECENT COMMITS\n")
    for entry in gs["recent_log"]:
        print(f"  {entry}")

    # --- LATEST EXPERIMENT ---
    print("\n## LATEST EXPERIMENT\n")
    exp = latest_experiment()
    if exp:
        print(f"  Experiment: {exp['name']}")
        print(f"  Number: {exp['number']}")
        print(f"  Status: {exp['status']}")
        print(f"  Topology: {exp['topology']}")
        print(f"  Target: {exp['target']}")
        print(f"  Rounds: {exp['total_rounds']}")
        print(f"  Findings: {exp['total_findings']}")
        print(f"  Gamma: {exp['gamma']:.4f}")
        print(f"  Models: {', '.join(exp['models'])}")
        if exp["per_model"]:
            print("  Per model:")
            for model, count in sorted(exp["per_model"].items(), key=lambda x: -x[1]):
                print(f"    {model}: {count}")
        print(f"  Logs: {exp['log_dir']}")
    else:
        print("  (No experiment logs found)")

    # --- TEST COUNT ---
    if args.full:
        print("\n## TESTS\n")
        count = test_count()
        if count is not None:
            print(f"  {count} tests collected")
        else:
            print("  (pytest collection failed)")

    # --- PENDING WORK ---
    print("\n## PENDING WORK\n")
    recovery = root / "resources" / "RECOVERY.md"
    pending = read_section(recovery, "NEXT STEPS:", "\nARCHITECTURAL GAPS")
    if pending:
        for line in pending.splitlines()[:30]:
            print(f"  {line}")
    else:
        print("  (No pending work section found)")

    # --- KEY FILES ---
    print("\n## KEY FILES\n")
    key_files = [
        ("resources/ONBOARDING.md", "Full project context and experiment history"),
        ("resources/RECOVERY.md", "Pending work and recovery protocol"),
        ("docs/GLOSSARY.md", "Term definitions and acronyms"),
        ("docs/ARCHITECTURE.md", "System components and data flow"),
        ("docs/REPRODUCING.md", "How to replicate experiments"),
        ("docs/CURRENT_STATE.md", "Machine-generated state snapshot"),
        ("bench/experiment_11_orchestrator.py", "Model dispatch and configuration"),
        ("bench/runner_core.py", "Shared runner infrastructure"),
        ("bench/insect_brain.py", "Central relay and checkpoint management"),
        ("bench/immune_agents.py", "Immune pipeline (6 cell types)"),
        ("bench/evidence.py", "Evidence layer"),
        ("bench/endocrine.py", "Endocrine layer"),
        ("bench/cdsfl_registry/composer.py", "Per-model directive composition"),
        ("docs/MATHEMATICAL_APPENDIX.md", "Mathematical framework"),
    ]
    for path, desc in key_files:
        full = root / path
        exists = "  " if full.exists() else "! "
        print(f"  {exists}{path} — {desc}")


if __name__ == "__main__":
    main()
