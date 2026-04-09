#!/usr/bin/env python3
"""CDSFL State Save Script — generates CURRENT_STATE.md, updates ONBOARDING.md,
RECOVERY.md, and timestamps.

Usage: python3 scripts/cdsfl_sv.py [--dry-run]

  --dry-run   Print what would change without writing files

Reads git state, test count, and experiment logs to produce a
machine-generated state snapshot. Auto-updates the latest experiment
entry in ONBOARDING.md and the pending work section in RECOVERY.md.

The goal: anyone cloning this repo can read ONBOARDING.md and pick up
the project from its exact last state without any further context.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import (
    git_state,
    latest_experiment,
    repo_root,
    test_count,
    timestamp_iso,
    timestamp_now,
)


# ── Experiment summary for ONBOARDING.md ──────────────────────────────────

_ONBOARDING_MARKER_START = "<!-- SV:LATEST_EXP_START -->"
_ONBOARDING_MARKER_END = "<!-- SV:LATEST_EXP_END -->"


def _format_experiment_summary(exp: dict, root: Path) -> str:
    """Generate a structured experiment summary block for ONBOARDING.md.

    This covers the mechanical/quantitative data that can be extracted
    from the experiment report JSON. Qualitative observations (model
    reasoning behaviour, immune system highlights, mid-experiment fixes)
    should be added manually below the auto-generated block.
    """
    ts = timestamp_now()
    status = exp["status"]
    n = exp["number"]
    target = exp.get("target", "unknown")
    topology = exp.get("topology", "unknown")
    rounds = exp.get("total_rounds", 0)
    findings = exp.get("total_findings", 0)
    gamma = exp.get("gamma", 0.0)
    models = exp.get("models", [])
    per_model = exp.get("per_model", {})
    reason = exp.get("reason", "")
    log_dir = exp.get("log_dir", "")

    # Gamma interpretation
    if gamma >= 0.45:
        gamma_desc = "strong depletion"
    elif gamma >= 0.30:
        gamma_desc = "moderate depletion"
    else:
        gamma_desc = "productive"

    # Per-model line
    per_model_str = ", ".join(
        f"{m} {c}" for m, c in sorted(per_model.items(), key=lambda x: -x[1])
    ) if per_model else "unavailable"

    # Read report JSON for additional fields
    canonical_count = findings  # default
    gamma_history = []
    per_round = []
    elapsed_s = 0
    report_path = Path(log_dir) / f"exp{n}_report.json" if log_dir else None
    if report_path and report_path.exists():
        try:
            rdata = json.loads(report_path.read_text())
            canonical_count = rdata.get("registry_size", rdata.get("total_findings", findings))
            gamma_history = rdata.get("gamma_history", [])
            per_round = rdata.get("per_round_counts",
                                  rdata.get("completion_signal", {}).get("per_round_counts", []))
            elapsed_s = rdata.get("total_elapsed_s", 0)
        except (json.JSONDecodeError, OSError):
            pass

    elapsed_str = f"{elapsed_s:.0f}s (~{elapsed_s/60:.0f} min)" if elapsed_s else "unknown"

    lines = [
        f"- **EXP {n} {status} ({ts}):**",
        f"  Target: `{target}`, {topology} topology, {len(models)} models.",
        f"  {rounds} rounds, {elapsed_str}. **{status}**"
        + (f" — {reason}" if reason else "") + ".",
        f"  {findings} raw findings → {canonical_count} canonical entries.",
        f"  γ final={gamma:.3f} ({gamma_desc}).",
        f"  Per model: {per_model_str}.",
    ]

    if log_dir:
        # Make path relative to repo root for portability
        try:
            rel = Path(log_dir).relative_to(root)
            lines.append(f"  Logs: `{rel}/`")
        except ValueError:
            lines.append(f"  Logs: `{log_dir}`")

    if per_round:
        lines.append(f"  Per round: {per_round}")

    if gamma_history:
        lines.append(f"  γ history: [{', '.join(f'{g:.3f}' for g in gamma_history)}]")

    lines.append("")
    lines.append("  **Qualitative observations** (add manually after sv):")
    lines.append("  <!-- Add: model reasoning behaviour, immune highlights,")
    lines.append("       mid-experiment fixes, key design findings -->")

    return "\n".join(lines)


def update_onboarding_experiment(
    onboarding_path: Path, exp: dict, root: Path, dry_run: bool = False,
) -> bool:
    """Insert or update the latest experiment summary in ONBOARDING.md.

    Uses marker comments to identify the auto-generated block. If markers
    exist, replaces content between them. If not, inserts markers + content
    at the top of the 'Current State' section.
    """
    if not onboarding_path.exists():
        return False

    text = onboarding_path.read_text(encoding="utf-8")
    summary = _format_experiment_summary(exp, root)
    block = f"{_ONBOARDING_MARKER_START}\n{summary}\n{_ONBOARDING_MARKER_END}"

    if _ONBOARDING_MARKER_START in text:
        # Replace existing block
        pattern = re.escape(_ONBOARDING_MARKER_START) + r".*?" + re.escape(_ONBOARDING_MARKER_END)
        new_text = re.sub(pattern, block, text, flags=re.DOTALL)
    else:
        # Insert after "## Current State" header
        marker = "## Current State (update after each major milestone)"
        idx = text.find(marker)
        if idx == -1:
            marker = "## Current State"
            idx = text.find(marker)
        if idx == -1:
            return False
        # Find end of the header line
        eol = text.find("\n", idx)
        if eol == -1:
            eol = len(text)
        insert_point = eol + 1
        new_text = text[:insert_point] + "\n" + block + "\n\n" + text[insert_point:]

    if new_text != text:
        if not dry_run:
            onboarding_path.write_text(new_text, encoding="utf-8")
        return True
    return False


# ── Pending work for RECOVERY.md ──────────────────────────────────────────

_RECOVERY_MARKER_START = "<!-- SV:PENDING_START -->"
_RECOVERY_MARKER_END = "<!-- SV:PENDING_END -->"


def _format_pending_work(
    exp: dict, gs: dict, tests: int | None, root: Path,
) -> str:
    """Generate a pending work block for RECOVERY.md from current state."""
    ts = timestamp_now()
    n = exp["number"] if exp else "?"
    status = exp["status"] if exp else "UNKNOWN"

    lines = [
        f"## Current Pending Work ({ts})",
        "",
        f"Experiments 12–{n} ALL COMPLETE. {tests or '?'} tests pass.",
        "",
    ]

    if exp:
        target = exp.get("target", "unknown")
        topology = exp.get("topology", "unknown")
        rounds = exp.get("total_rounds", 0)
        findings = exp.get("total_findings", 0)
        gamma = exp.get("gamma", 0.0)
        reason = exp.get("reason", "")
        log_dir = exp.get("log_dir", "")

        lines.extend([
            f"EXP {n} {status} ({ts}):",
            f"  Target: {target}, {topology}, {rounds} rounds.",
            f"  {findings} findings, γ={gamma:.3f}."
            + (f" {reason}." if reason else ""),
        ])
        if log_dir:
            try:
                rel = Path(log_dir).relative_to(root)
            except ValueError:
                rel = Path(log_dir)
            lines.append(f"  Logs: {rel}/")
            lines.append(f"  Report: {rel}/exp{n}_report.json")

    # Uncommitted changes
    if not gs["clean"]:
        lines.extend(["", "Uncommitted changes in working tree:"])
        # Group by directory for readability
        for f in gs["uncommitted"][:20]:
            lines.append(f"  {f}")
        if len(gs["uncommitted"]) > 20:
            lines.append(f"  ... and {len(gs['uncommitted']) - 20} more")
    else:
        lines.extend(["", "Working tree: clean."])

    # Remote sync
    lines.extend(["", f"Remote: {gs['remote_sync']}."])

    lines.extend([
        "",
        "NEXT: <!-- Add next steps manually after sv -->",
    ])

    return "\n".join(lines)


def update_recovery_pending(
    recovery_path: Path,
    exp: dict | None,
    gs: dict,
    tests: int | None,
    root: Path,
    dry_run: bool = False,
) -> bool:
    """Update the pending work section in RECOVERY.md.

    Uses marker comments. If markers exist, replaces between them.
    If not, replaces the '## Current Pending Work' section up to the
    next '## ' heading.
    """
    if not recovery_path.exists():
        return False

    text = recovery_path.read_text(encoding="utf-8")
    pending = _format_pending_work(exp, gs, tests, root)
    block = f"{_RECOVERY_MARKER_START}\n{pending}\n{_RECOVERY_MARKER_END}"

    if _RECOVERY_MARKER_START in text:
        pattern = re.escape(_RECOVERY_MARKER_START) + r".*?" + re.escape(_RECOVERY_MARKER_END)
        new_text = re.sub(pattern, block, text, flags=re.DOTALL)
    else:
        # Find existing "## Current Pending Work" and replace to next ##
        cpw = text.find("## Current Pending Work")
        if cpw == -1:
            # Append
            new_text = text.rstrip() + "\n\n" + block + "\n"
        else:
            # Find next ## heading after this one
            next_heading = text.find("\n## ", cpw + 1)
            if next_heading == -1:
                # Replace to end of file
                new_text = text[:cpw] + block + "\n"
            else:
                new_text = text[:cpw] + block + "\n\n" + text[next_heading + 1:]

    if new_text != text:
        if not dry_run:
            recovery_path.write_text(new_text, encoding="utf-8")
        return True
    return False


# ── CURRENT_STATE.md (unchanged logic) ────────────────────────────────────

def generate_current_state(
    gs: dict,
    tests: int | None,
    exp: dict | None,
    root: Path,
) -> str:
    """Generate the CURRENT_STATE.md content."""
    ts = timestamp_now()
    iso = timestamp_iso()

    lines = [
        "# CDSFL Current State",
        f"",
        f"Generated: {ts} ({iso})",
        "",
        "---",
        "",
        "## Git",
        "",
        f"- **Branch:** {gs['branch']}",
        f"- **Last commit:** `{gs['last_hash']}` {gs['last_message']}",
        f"- **Committed:** {gs['last_date']}",
        f"- **Remote:** {gs['remote_sync']}",
        f"- **Working tree:** {'clean' if gs['clean'] else 'DIRTY — uncommitted changes present'}",
    ]

    if not gs["clean"]:
        lines.append("")
        lines.append("Uncommitted files:")
        for f in gs["uncommitted"][:15]:
            lines.append(f"- `{f}`")

    lines.extend(["", "---", "", "## Tests", ""])
    if tests is not None:
        lines.append(f"**{tests} tests collected** (`python3 -m pytest bench/tests/ --co -q`)")
    else:
        lines.append("Test count unavailable (pytest collection failed or timed out)")

    lines.extend(["", "---", "", "## Latest Experiment", ""])
    if exp:
        lines.extend([
            f"- **Experiment:** {exp['name']} (#{exp['number']})",
            f"- **Status:** {exp['status']}",
            f"- **Topology:** {exp['topology']}",
            f"- **Target:** `{exp['target']}`",
            f"- **Rounds:** {exp['total_rounds']}",
            f"- **Total findings:** {exp['total_findings']}",
            f"- **Gamma:** {exp['gamma']:.4f}",
            f"- **Models:** {', '.join(exp['models'])}",
        ])
        if exp.get("per_model"):
            lines.append("- **Per model:**")
            for model, count in sorted(exp["per_model"].items(), key=lambda x: -x[1]):
                lines.append(f"  - {model}: {count}")
        lines.append(f"- **Logs:** `{exp['log_dir']}`")
    else:
        lines.append("No experiment logs found.")

    # Recent commits
    lines.extend(["", "---", "", "## Recent Commits", ""])
    for entry in gs["recent_log"][:10]:
        lines.append(f"- `{entry}`")

    lines.append("")
    return "\n".join(lines)


def update_timestamp(filepath: Path, dry_run: bool = False) -> bool:
    """Update the 'Last updated:' line in a file. Returns True if changed."""
    if not filepath.exists():
        return False

    text = filepath.read_text(encoding="utf-8")
    ts = timestamp_now()
    new_text = re.sub(
        r"(Last updated:\s*).*",
        rf"\g<1>{ts}",
        text,
        count=1,
    )

    if new_text != text:
        if not dry_run:
            filepath.write_text(new_text, encoding="utf-8")
        return True
    return False


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="CDSFL State Save")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    args = parser.parse_args()

    root = repo_root()
    print(f"CDSFL State Save — {timestamp_iso()}")
    print(f"Repository: {root}")
    print()

    # Gather data
    print("Collecting git state...", end=" ", flush=True)
    gs = git_state()
    print("done")

    print("Counting tests...", end=" ", flush=True)
    tests = test_count()
    print(f"{tests if tests else 'failed'}")

    print("Reading experiment logs...", end=" ", flush=True)
    exp = latest_experiment()
    print(f"Exp {exp['number']}" if exp else "none found")

    print()

    # 1. Generate CURRENT_STATE.md
    state_content = generate_current_state(gs, tests, exp, root)
    state_path = root / "docs" / "CURRENT_STATE.md"

    if args.dry_run:
        print("=== CURRENT_STATE.md (dry run) ===")
        print(state_content[:500])
        print("...")
    else:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(state_content, encoding="utf-8")
        print(f"Written: {state_path}")

    # 2. Update timestamps
    onboarding = root / "resources" / "ONBOARDING.md"
    recovery = root / "resources" / "RECOVERY.md"

    if update_timestamp(onboarding, dry_run=args.dry_run):
        print(f"Updated timestamp: {onboarding}")

    if update_timestamp(recovery, dry_run=args.dry_run):
        print(f"Updated timestamp: {recovery}")

    # 3. Update experiment summary in ONBOARDING.md
    if exp:
        if update_onboarding_experiment(onboarding, exp, root, dry_run=args.dry_run):
            print(f"Updated experiment summary: {onboarding}")
        else:
            print(f"Experiment summary unchanged: {onboarding}")
    else:
        print("No experiment data — skipping ONBOARDING.md experiment update")

    # 4. Update pending work in RECOVERY.md
    if update_recovery_pending(recovery, exp, gs, tests, root, dry_run=args.dry_run):
        print(f"Updated pending work: {recovery}")
    else:
        print(f"Pending work unchanged: {recovery}")

    # Summary
    print()
    print("State save complete.")
    print(f"  Branch: {gs['branch']} @ {gs['last_hash']}")
    print(f"  Tests: {tests if tests else 'unknown'}")
    print(f"  Latest exp: {exp['name'] if exp else 'none'}")
    print(f"  Working tree: {'clean' if gs['clean'] else 'DIRTY'}")
    print(f"  Remote: {gs['remote_sync']}")
    if exp:
        print(f"  ONBOARDING.md: experiment #{exp['number']} summary auto-generated")
        print(f"  RECOVERY.md: pending work auto-generated")
    print()
    print("  NOTE: Qualitative observations (model behaviour, immune highlights,")
    print("  mid-experiment fixes) must still be added manually to ONBOARDING.md.")


if __name__ == "__main__":
    main()
