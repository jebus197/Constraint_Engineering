#!/usr/bin/env python3
"""CDSFL State Save Script — generates CURRENT_STATE.md and updates timestamps.

Usage: python3 scripts/cdsfl_sv.py [--dry-run]

  --dry-run   Print what would change without writing files

Reads git state, test count, and experiment logs to produce a
machine-generated state snapshot. Updates timestamps in ONBOARDING.md
and RECOVERY.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import (
    git_state,
    latest_experiment,
    repo_root,
    test_count,
    timestamp_iso,
    timestamp_now,
)


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

    # Extract pending work from RECOVERY.md
    recovery = root / "resources" / "RECOVERY.md"
    if recovery.exists():
        text = recovery.read_text(encoding="utf-8")
        next_idx = text.find("NEXT STEPS:")
        if next_idx != -1:
            next_section = text[next_idx:]
            # Find end of next steps
            end_markers = ["ARCHITECTURAL GAPS", "\n\nEXP 32", "\n\nEXP 33",
                           "\n\nRUNNER FITNESS", "\n\nCDSFL TOPOLOGY"]
            end = len(next_section)
            for marker in end_markers:
                idx = next_section.find(marker)
                if idx != -1 and idx < end:
                    end = idx
            next_text = next_section[:end].strip()
            lines.extend(["", "---", "", "## Pending Work", ""])
            for line in next_text.splitlines():
                lines.append(line)

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

    # Generate CURRENT_STATE.md
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

    # Update timestamps
    onboarding = root / "resources" / "ONBOARDING.md"
    recovery = root / "resources" / "RECOVERY.md"

    if update_timestamp(onboarding, dry_run=args.dry_run):
        print(f"Updated timestamp: {onboarding}")
    else:
        print(f"Timestamp unchanged: {onboarding}")

    if update_timestamp(recovery, dry_run=args.dry_run):
        print(f"Updated timestamp: {recovery}")
    else:
        print(f"Timestamp unchanged: {recovery}")

    # Summary
    print()
    print("State save complete.")
    print(f"  Branch: {gs['branch']} @ {gs['last_hash']}")
    print(f"  Tests: {tests if tests else 'unknown'}")
    print(f"  Latest exp: {exp['name'] if exp else 'none'}")
    print(f"  Working tree: {'clean' if gs['clean'] else 'DIRTY'}")
    print(f"  Remote: {gs['remote_sync']}")


if __name__ == "__main__":
    main()
