#!/usr/bin/env python3
"""CDSFL Quality Control Script — staleness, consistency, and reference checks.

Usage: python3 scripts/cdsfl_qc.py [--fix-timestamps]

  --fix-timestamps   Update stale timestamps (otherwise report only)

Checks:
  1. Stale documentation (timestamps older than last commit)
  2. Broken file references in markdown
  3. Test count consistency between docs and actual
  4. Experiment number consistency between docs and logs
  5. Onboarding script wiring (cdsfl_onboard.py --dry-run passes)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cdsfl_utils import (
    check_file_references,
    git_state,
    latest_experiment,
    repo_root,
    test_count,
    timestamp_iso,
)


def check_staleness(root: Path) -> list[dict]:
    """Check for stale documentation timestamps."""
    findings = []

    # Files that carry "Last updated:" timestamps
    timestamped_files = [
        root / "resources" / "ONBOARDING.md",
        root / "resources" / "RECOVERY.md",
    ]

    gs = git_state()
    last_commit = gs["last_date"]

    for f in timestamped_files:
        if not f.exists():
            findings.append({
                "category": "MISSING",
                "file": str(f.relative_to(root)),
                "detail": "File does not exist",
            })
            continue

        text = f.read_text(encoding="utf-8")
        m = re.search(r"Last updated:\s*(.+)", text)
        if m:
            doc_timestamp = m.group(1).strip()
            findings.append({
                "category": "INFO",
                "file": str(f.relative_to(root)),
                "detail": f"Doc timestamp: {doc_timestamp} | Last commit: {last_commit}",
            })

    return findings


def check_test_consistency(root: Path) -> list[dict]:
    """Check test count mentioned in docs against actual."""
    findings = []

    actual = test_count()
    if actual is None:
        findings.append({
            "category": "WARN",
            "file": "bench/tests/",
            "detail": "Could not collect test count (pytest failed)",
        })
        return findings

    # Check RECOVERY.md for test count — only in current state section
    # (first ~100 lines), not in historical entries
    recovery = root / "resources" / "RECOVERY.md"
    if recovery.exists():
        lines = recovery.read_text(encoding="utf-8").splitlines()
        # Scan only the current pending work section (before historical entries)
        current_section = "\n".join(lines[:100])
        matches = list(re.finditer(r"(\d+)\s+tests?\s+pass", current_section))
        if matches:
            for m in matches:
                doc_count = int(m.group(1))
                if doc_count != actual:
                    findings.append({
                        "category": "STALE",
                        "file": "resources/RECOVERY.md",
                        "detail": f"Current section says {doc_count} tests, actual is {actual}",
                    })
                else:
                    findings.append({
                        "category": "OK",
                        "file": "resources/RECOVERY.md",
                        "detail": f"Test count {actual} is current",
                    })

    return findings


def check_experiment_consistency(root: Path) -> list[dict]:
    """Check latest experiment number in docs against logs."""
    findings = []

    exp = latest_experiment()
    if exp is None:
        return findings

    actual_num = exp["number"]

    # Check ONBOARDING.md for experiment mentions
    onboarding = root / "resources" / "ONBOARDING.md"
    if onboarding.exists():
        text = onboarding.read_text(encoding="utf-8")
        # Find highest experiment number mentioned
        exp_nums = [int(m.group(1)) for m in re.finditer(r"EXP\s+(\d+)", text)]
        if exp_nums:
            max_mentioned = max(exp_nums)
            if max_mentioned < actual_num:
                findings.append({
                    "category": "STALE",
                    "file": "resources/ONBOARDING.md",
                    "detail": f"Highest experiment mentioned: {max_mentioned}, actual: {actual_num}",
                })

    return findings


def check_broken_references(root: Path) -> list[dict]:
    """Check all markdown files for broken file references."""
    findings = []

    doc_dirs = [
        root / "resources",
        root / "docs",
        root / "experimental_notes",
    ]

    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue
        for md in doc_dir.glob("*.md"):
            broken = check_file_references(md)
            for ref in broken:
                findings.append({
                    "category": "BROKEN_REF",
                    "file": str(Path(ref["file"]).relative_to(root)),
                    "detail": f"Line {ref['line']}: {ref['reference']}",
                })

    return findings


def check_glossary(root: Path) -> list[dict]:
    """Check if glossary exists and has content."""
    findings = []
    glossary = root / "docs" / "GLOSSARY.md"

    if not glossary.exists():
        findings.append({
            "category": "MISSING",
            "file": "docs/GLOSSARY.md",
            "detail": "Glossary does not exist — term cross-referencing disabled",
        })
    else:
        text = glossary.read_text(encoding="utf-8")
        term_count = len(re.findall(r"^###\s+", text, re.MULTILINE))
        findings.append({
            "category": "INFO",
            "file": "docs/GLOSSARY.md",
            "detail": f"{term_count} terms defined",
        })

    return findings


def check_onboard_script(root: Path) -> list[dict]:
    """Run `cdsfl_onboard.py --dry-run` to verify the onboarding script's
    canonical-document wiring is intact.

    The onboarding script reads project prose from resources/ONBOARDING.md
    and the MC command reference from docs/REPRODUCING.md at runtime. If
    either file is missing a required section or marker, the dry-run
    fails and is surfaced here so staleness is caught before commit.
    """
    findings: list[dict] = []
    script = root / "scripts" / "cdsfl_onboard.py"

    if not script.exists():
        findings.append({
            "category": "MISSING",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "Onboarding script not found",
        })
        return findings

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        findings.append({
            "category": "WARN",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "--dry-run timed out after 30s",
        })
        return findings
    except OSError as err:
        findings.append({
            "category": "WARN",
            "file": "scripts/cdsfl_onboard.py",
            "detail": f"Could not run --dry-run: {err}",
        })
        return findings

    if result.returncode == 0:
        findings.append({
            "category": "OK",
            "file": "scripts/cdsfl_onboard.py",
            "detail": "--dry-run passes (canonical-doc wiring intact)",
        })
    else:
        # Surface the specific failures from stderr as STALE findings.
        stderr_lines = [ln for ln in result.stderr.splitlines() if ln.strip()]
        detail = "; ".join(stderr_lines) if stderr_lines else "--dry-run failed (no stderr)"
        findings.append({
            "category": "STALE",
            "file": "scripts/cdsfl_onboard.py",
            "detail": detail,
        })

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="CDSFL Quality Control")
    parser.parse_args()

    root = repo_root()
    print(f"CDSFL Quality Control — {timestamp_iso()}")
    print(f"Repository: {root}")
    print("=" * 70)

    all_findings: list[dict] = []

    print("\nChecking timestamps...", flush=True)
    all_findings.extend(check_staleness(root))

    print("Checking test consistency...", flush=True)
    all_findings.extend(check_test_consistency(root))

    print("Checking experiment consistency...", flush=True)
    all_findings.extend(check_experiment_consistency(root))

    print("Checking file references...", flush=True)
    all_findings.extend(check_broken_references(root))

    print("Checking glossary...", flush=True)
    all_findings.extend(check_glossary(root))

    print("Checking onboarding script wiring...", flush=True)
    all_findings.extend(check_onboard_script(root))

    # Report
    print("\n" + "=" * 70)
    print("FINDINGS\n")

    categories = ["STALE", "BROKEN_REF", "MISSING", "WARN", "INFO", "OK"]
    for cat in categories:
        items = [f for f in all_findings if f["category"] == cat]
        if items:
            print(f"[{cat}]")
            for item in items:
                print(f"  {item['file']}: {item['detail']}")
            print()

    # Summary
    stale = len([f for f in all_findings if f["category"] == "STALE"])
    broken = len([f for f in all_findings if f["category"] == "BROKEN_REF"])
    missing = len([f for f in all_findings if f["category"] == "MISSING"])
    warns = len([f for f in all_findings if f["category"] == "WARN"])

    issues = stale + broken + missing + warns
    print(f"Total: {len(all_findings)} checks, {issues} issues "
          f"({stale} stale, {broken} broken refs, {missing} missing, {warns} warnings)")


if __name__ == "__main__":
    main()
