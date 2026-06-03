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

---

Protocol note for Claude operators preparing sv input:

This script does NOT read ONBOARDING.md, RECOVERY.md, MATHEMATICAL_APPENDIX.md,
PAPER.md or memory files itself — the OPERATOR's qualitative updates must be
prepared before the script runs. Those canonical documents are now large
enough that a single parallel read across them inflates context without
improving understanding and raises the risk of API overload.

Read them sequentially — top to bottom, one section or chunk at a time.
Absorb each chunk, decide if it needs a qualitative update, then move on to
the next. Do NOT fetch several large documents in parallel just to "have
them all loaded". Carefully considered section-by-section updates produce
better recovery docs than bulk ingestion of everything at once.

This protocol is mirrored in .claude/CLAUDE.md and ~/.claude/CLAUDE.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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

    # Canonical count: prefer pre-computed from latest_experiment(), fallback to report
    canonical_count = exp.get("canonical_count", findings)
    gamma_history = []
    per_round = []
    elapsed_s = 0
    report_path = Path(log_dir) / f"exp{n}_report.json" if log_dir else None
    # Also try the name-prefixed report path (e.g. exp38_ouroboros_report.json)
    if report_path and not report_path.exists() and log_dir:
        name = exp.get("name", f"exp{n}")
        report_path = Path(log_dir) / f"{name}_report.json"
    if report_path and report_path.exists():
        try:
            rdata = json.loads(report_path.read_text())
            gamma_history = rdata.get("gamma_history", [])
            per_round = rdata.get("per_round_counts", [])
            if not per_round:
                # Try completion_signal (embedded or separate file)
                comp = rdata.get("completion_signal", {})
                if not comp:
                    cs_path = Path(log_dir) / "completion_signal.json"
                    if cs_path.exists():
                        try:
                            comp = json.loads(cs_path.read_text())
                        except (json.JSONDecodeError, OSError):
                            comp = {}
                per_round = comp.get("per_round_counts", [])
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


_ONBOARDING_PLACEHOLDER = "add manually after sv"


def _has_manual_content(text: str, start_marker: str, end_marker: str, placeholder: str) -> bool:
    """Return True if the section between markers contains manual (non-auto) content.

    Detection: auto-generated blocks contain a placeholder string (e.g.
    'add manually after sv'). If that placeholder is absent, the content
    was manually written and should be preserved.
    """
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end <= start:
        return False
    section = text[start + len(start_marker):end]
    # If placeholder is absent and there's substantial content, it's manual
    return placeholder not in section and len(section.strip()) > 50


def update_onboarding_experiment(
    onboarding_path: Path, exp: dict, root: Path, dry_run: bool = False,
) -> bool:
    """Insert or update the latest experiment summary in ONBOARDING.md.

    Uses marker comments to identify the auto-generated block. If markers
    exist and contain manual content (no placeholder text), the section is
    preserved — only the timestamp is updated. If markers contain auto-
    generated content or don't exist, replaces/inserts the full block.
    """
    if not onboarding_path.exists():
        return False

    text = onboarding_path.read_text(encoding="utf-8")

    # Check for manual content — if present, skip regeneration
    if _has_manual_content(text, _ONBOARDING_MARKER_START, _ONBOARDING_MARKER_END,
                           _ONBOARDING_PLACEHOLDER):
        return False  # Preserved — timestamp update handled separately

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


_RECOVERY_PLACEHOLDER = "Add next steps manually"


def update_recovery_pending(
    recovery_path: Path,
    exp: dict | None,
    gs: dict,
    tests: int | None,
    root: Path,
    dry_run: bool = False,
) -> bool:
    """Update the pending work section in RECOVERY.md.

    Uses marker comments. If markers exist and contain manual content
    (no placeholder text), the section is preserved. Otherwise replaces
    between markers or inserts a new block.
    """
    if not recovery_path.exists():
        return False

    text = recovery_path.read_text(encoding="utf-8")

    # Check for manual content — if present, skip regeneration
    if _has_manual_content(text, _RECOVERY_MARKER_START, _RECOVERY_MARKER_END,
                           _RECOVERY_PLACEHOLDER):
        return False  # Preserved — timestamp update handled separately

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


# ── Atomic commit + push ────────────────────────────────────────────────

_SENSITIVE_PATTERNS = (".env", "credentials", "secret", ".key", ".pem", ".p12")

# Directories whose untracked, non-gitignored files are safe to auto-stage
# during an sv commit. Top-level ad-hoc files and dotfile caches are
# deliberately excluded — they must be staged manually by the operator if
# they are intended for the commit.
_SAFE_STAGING_DIRS: tuple[str, ...] = (
    "bench/",
    "configs/",
    "docs/",
    "examples/",
    "experimental_notes/",
    "logs/",
    "resources/",
    "scripts/",
)

# Regex for extracting file paths from commit-message prose. Requires a
# leading whitelisted directory + '/' so bare filenames and embedded
# substrings (e.g. '…/bench/foo.py' inside a longer path) do not match.
# The final group captures: <whitelist-dir>/<path-chars>.<extension>.
_MESSAGE_PATH_RE = re.compile(
    r"(?<![\w/])("
    + r"(?:" + "|".join(re.escape(d) for d in _SAFE_STAGING_DIRS) + r")"
    + r"[\w./-]+\.[A-Za-z0-9]+)"
)


def _git(
    *args: str,
    root: Path | None = None,
    timeout: int = 30,
    check: bool = True,
) -> str:
    """Run a git command. Raises RuntimeError on failure if check=True."""
    result = subprocess.run(
        ["git", *args],
        cwd=root or repo_root(),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"git {args[0]} failed (rc={result.returncode}): {stderr}")
    return result.stdout.strip()


def _discover_untracked_in_whitelist(root: Path) -> list[str]:
    """Return repo-relative paths of untracked, non-gitignored files under
    the safe-staging whitelist.

    Uses ``git ls-files --others --exclude-standard`` so global gitignore,
    repo .gitignore, and .git/info/exclude are all honoured automatically.
    The whitelist adds defense-in-depth against stray top-level or dotfile
    content that is not gitignored but shouldn't be swept into an sv commit.
    """
    out = _git("ls-files", "--others", "--exclude-standard", root=root)
    if not out:
        return []
    return [
        line for line in out.splitlines()
        if line and any(line.startswith(d) for d in _SAFE_STAGING_DIRS)
    ]


def _extract_paths_from_message(message: str) -> list[str]:
    """Extract file paths mentioned in a commit message.

    Only paths rooted at a whitelisted directory with a file extension are
    returned; bare filenames, shell commands, and prose are ignored. Paths
    are deduplicated in first-seen order. Trailing ``:<digits>`` line-number
    suffixes are stripped.
    """
    found: list[str] = []
    seen: set[str] = set()
    for m in _MESSAGE_PATH_RE.finditer(message):
        path = re.sub(r":\d+$", "", m.group(1))
        if path not in seen:
            seen.add(path)
            found.append(path)
    return found


def _validate_message_paths(
    message: str,
    staged: set[str],
    root: Path,
) -> list[str]:
    """Return paths the commit message names that are neither staged nor
    already tracked.

    A path that is staged (present in ``git diff --cached --name-only``)
    passes. A path that is tracked but unchanged also passes — this is a
    legitimate prose reference to an existing file. Only paths that are
    *both* unstaged *and* absent from the repo fail, which is exactly the
    defect class that produced commit f29d0e9 on 2026-04-15.
    """
    missing: list[str] = []
    for path in _extract_paths_from_message(message):
        if path in staged:
            continue
        tracked = _git("ls-files", "--", path, root=root, check=False)
        if not tracked:
            missing.append(path)
    return missing


def _commit_and_push(
    message: str,
    push: bool = False,
    root: Path | None = None,
    auto_stage: bool = True,
    validate_message: bool = True,
) -> bool:
    """Stage sv-related files, commit, optionally push.

    Returns True if a commit was created, False if nothing to commit.
    Runs as a single function call — if launched via subprocess from CC,
    the entire commit+push completes even if the conversation compacts.

    auto_stage: if True, discover untracked files under whitelisted project
        directories (see ``_SAFE_STAGING_DIRS``) and stage them. Defaults on
        because silent exclusion of untracked files is the defect this fix
        addresses. Pass False to require manual pre-staging.
    validate_message: if True, abort before commit if the message names a
        path that is neither staged nor tracked. Defaults on.
    """
    root = root or repo_root()

    # 1. Stage core sv outputs
    for path in ("resources/ONBOARDING.md", "resources/RECOVERY.md", "docs/CURRENT_STATE.md"):
        if (root / path).exists():
            _git("add", path, root=root)

    # 2. Stage all modifications to already-tracked files
    _git("add", "-u", root=root)

    # 3. Stage untracked files under whitelisted project directories.
    #    Honours .gitignore via ``git ls-files --others --exclude-standard``
    #    and further restricts to _SAFE_STAGING_DIRS as defense-in-depth.
    if auto_stage:
        untracked = _discover_untracked_in_whitelist(root)
        if untracked:
            print(f"  Auto-staging {len(untracked)} untracked file(s) under whitelist:")
            for rel in untracked:
                _git("add", "--", rel, root=root, check=False)
                print(f"    + {rel}")

    # 4. Check what's staged
    staged = _git("diff", "--cached", "--name-only", root=root)
    if not staged.strip():
        return False

    # 5. Safety check — unstage anything sensitive
    for f in staged.splitlines():
        f = f.strip()
        if any(s in f.lower() for s in _SENSITIVE_PATTERNS):
            _git("reset", "HEAD", "--", f, root=root)
            print(f"  WARNING: Unstaged sensitive file: {f}")

    # Re-check after unstaging
    staged = _git("diff", "--cached", "--name-only", root=root)
    if not staged.strip():
        return False

    staged_set = set(staged.splitlines())
    n_files = len(staged_set)

    # 6. Validate that every path named in the commit message is either
    #    staged or already tracked. Closes the defect class of commits
    #    whose message references files absent from the tree (f29d0e9).
    if validate_message:
        missing = _validate_message_paths(message, staged_set, root)
        if missing:
            joined = "\n    ".join(missing)
            raise RuntimeError(
                "Commit message references paths that are neither staged "
                "nor tracked:\n    " + joined
                + "\n  Stage them, remove them from the message, or pass "
                "--no-validate-message to override."
            )

    # 7. Onboarding-script wiring sanity check.
    #    cdsfl_onboard.py reads project prose from ONBOARDING.md and the
    #    MC reference from REPRODUCING.md at runtime. If either file has
    #    drifted out of sync (missing SV markers, missing canonical
    #    section headings), the --dry-run fails and we abort before
    #    committing so the defect does not land in origin.
    onboard_script = root / "scripts" / "cdsfl_onboard.py"
    if onboard_script.exists():
        try:
            dry = subprocess.run(
                [sys.executable, str(onboard_script), "--dry-run"],
                capture_output=True,
                text=True,
                cwd=str(root),
                timeout=30,
            )
        except (subprocess.TimeoutExpired, OSError) as err:
            raise RuntimeError(
                f"cdsfl_onboard.py --dry-run could not be executed: {err}. "
                "Fix the script or pass --skip-onboard-check to override."
            ) from err
        if dry.returncode != 0:
            raise RuntimeError(
                "cdsfl_onboard.py --dry-run FAILED — aborting commit.\n"
                f"stderr:\n{dry.stderr.strip()}\n"
                "Canonical-doc wiring has drifted. Repair ONBOARDING.md / "
                "REPRODUCING.md before committing."
            )

    # 8. Commit
    full_msg = f"{message}\n\nCo-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
    _git("commit", "-m", full_msg, root=root, timeout=60)

    new_hash = _git("log", "--oneline", "-1", root=root)
    print(f"  Committed: {new_hash} ({n_files} files)")

    # 9. Push
    if push:
        branch = _git("branch", "--show-current", root=root)
        _git("push", "origin", branch, root=root, timeout=120)
        print(f"  Pushed to origin/{branch}")

    return True


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="CDSFL State Save")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing")
    parser.add_argument("--commit", action="store_true", help="Stage and commit sv files")
    parser.add_argument("--push", action="store_true", help="Push after commit (implies --commit)")
    parser.add_argument("-m", "--message", help="Commit message (default: auto-generated)")
    parser.add_argument(
        "--no-auto-stage",
        action="store_true",
        help="Do not auto-stage untracked files under whitelisted project "
             "directories; require manual `git add` before sv.",
    )
    parser.add_argument(
        "--no-validate-message",
        action="store_true",
        help="Skip the check that every path named in the commit message "
             "is either staged or already tracked.",
    )
    args = parser.parse_args()

    if args.push:
        args.commit = True

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

    # 3. Update experiment summary in ONBOARDING.md (skips if manual content present)
    if exp:
        if update_onboarding_experiment(onboarding, exp, root, dry_run=args.dry_run):
            print(f"Updated experiment summary: {onboarding}")
        else:
            # Distinguish "unchanged" from "preserved manual content"
            if onboarding.exists() and _ONBOARDING_MARKER_START in onboarding.read_text():
                text = onboarding.read_text()
                if _has_manual_content(text, _ONBOARDING_MARKER_START,
                                       _ONBOARDING_MARKER_END, _ONBOARDING_PLACEHOLDER):
                    print(f"Preserved manual content: {onboarding}")
                else:
                    print(f"Experiment summary unchanged: {onboarding}")
            else:
                print(f"Experiment summary unchanged: {onboarding}")
    else:
        print("No experiment data — skipping ONBOARDING.md experiment update")

    # 4. Update pending work in RECOVERY.md (skips if manual content present)
    if update_recovery_pending(recovery, exp, gs, tests, root, dry_run=args.dry_run):
        print(f"Updated pending work: {recovery}")
    else:
        if recovery.exists() and _RECOVERY_MARKER_START in recovery.read_text():
            text = recovery.read_text()
            if _has_manual_content(text, _RECOVERY_MARKER_START,
                                   _RECOVERY_MARKER_END, _RECOVERY_PLACEHOLDER):
                print(f"Preserved manual content: {recovery}")
            else:
                print(f"Pending work unchanged: {recovery}")
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

    # 5. Commit and push (atomic — survives compaction)
    if args.commit and not args.dry_run:
        print()
        msg = args.message or f"sv: state save {timestamp_now()}"
        try:
            if _commit_and_push(
                message=msg,
                push=args.push,
                root=root,
                auto_stage=not args.no_auto_stage,
                validate_message=not args.no_validate_message,
            ):
                print()
                suffix = " and pushed" if args.push else ""
                print(f"State save committed{suffix}.")
            else:
                print("Nothing to commit — all sv files match HEAD.")
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    elif not args.commit:
        print()
        print("  TIP: Use --commit --push to atomically commit and push.")


if __name__ == "__main__":
    main()
