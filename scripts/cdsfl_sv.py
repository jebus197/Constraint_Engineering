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
import difflib
import json
import os
import re
import statistics
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

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
        # Do NOT write "tests pass" here: `tests` comes from `pytest --co`, which is a
        # collection count and carries no pass/fail information. Mislabelling it as a
        # pass count is how the retracted "1121 non-network pass" figure propagated.
        f"Experiments 12–{n} ALL COMPLETE. {tests or '?'} tests collected at {ts} "
        f"(collection count, not a pass count — see docs/CURRENT_STATE.md).",
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


# ── CURRENT_STATE.md ────────────────────────────────────

def generate_current_state(
    gs: dict,
    tests: int | None,
    exp: dict | None,
    root: Path,
    will_commit: bool = False,
) -> str:
    """Generate the CURRENT_STATE.md content.

    ``will_commit`` says an sv commit will be created immediately after this
    file is written, i.e. this file is ABOUT TO BE COMMITTED. The git snapshot
    below is therefore taken BEFORE that commit exists and can never describe
    it. Rather than pretend otherwise (a post-commit regenerate + amend just
    moves the lie: amending changes the hash again), the block says plainly
    what it is a snapshot of. See REPAIR S2, 2026-08-05.
    """
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
    ]

    if will_commit:
        lines.extend([
            "> **SNAPSHOT TAKEN IMMEDIATELY BEFORE THE sv COMMIT — NOT CURRENT TRUTH.**",
            "> This file is generated first and committed second, so it cannot describe",
            "> the commit that carries it. Read the block below as follows:",
            "> **\"Last commit\" is the PARENT** of the commit containing this file, and",
            "> **the uncommitted list is the working tree at snapshot time — it is NOT",
            "> that commit's file list.** The two differ in both directions: sv rewrites",
            "> docs/CURRENT_STATE.md, resources/ONBOARDING.md and resources/RECOVERY.md",
            "> *after* this snapshot, and it stages only whitelisted paths. For the",
            "> commit this file actually lives in and its real contents, run",
            "> `git log -1 --stat -- docs/CURRENT_STATE.md`.",
            "",
        ])

    parent_label = (
        "Last commit (the PARENT of the commit containing this file)"
        if will_commit else "Last commit"
    )
    remote_label = "Remote (as of the snapshot, before the sv push)" if will_commit else "Remote"
    tree_label = "Working tree at snapshot time" if will_commit else "Working tree"
    dirty_text = (
        "DIRTY — snapshot-time working tree listed below (NOT the sv commit's file list)"
        if will_commit else "DIRTY — uncommitted changes present"
    )

    lines.extend([
        f"- **Branch:** {gs['branch']}",
        f"- **{parent_label}:** `{gs['last_hash']}` {gs['last_message']}",
        f"- **Committed:** {gs['last_date']}",
        f"- **{remote_label}:** {gs['remote_sync']}",
        f"- **{tree_label}:** {'clean' if gs['clean'] else dirty_text}",
    ])

    if not gs["clean"]:
        lines.append("")
        if will_commit:
            lines.append(
                "Uncommitted files at snapshot time — the working tree as it stood "
                "before the sv commit, NOT that commit's file list:"
            )
        else:
            lines.append("Uncommitted files:")
        shown = gs["uncommitted"][:15]
        for f in shown:
            lines.append(f"- `{f}`")
        # The list is capped. Saying so is the whole point: an undisclosed
        # truncation under a heading that reads as complete is the same defect
        # class this repair set exists to remove.
        hidden = len(gs["uncommitted"]) - len(shown)
        if hidden > 0:
            lines.append(
                f"- … and {hidden} more, not shown (list capped at 15 of "
                f"{len(gs['uncommitted'])} — run `git status --porcelain` for the full set)"
            )

    lines.extend(["", "---", "", "## Tests", ""])
    if tests is not None:
        tree = "" if gs["clean"] else " + uncommitted working tree"
        lines.extend([
            f"**{tests} tests collected** at {ts}, HEAD `{gs['last_hash']}`{tree} "
            f"(`python3 -m pytest bench/tests/ --co -q`)",
            "",
            "This is a COLLECTION count, not a pass count, and it says nothing about "
            "whether the run was offline. Quote it only with the timestamp and commit "
            "above. The total is not stable: `bench/tests/test_immune_memory_consumption.py` "
            "parametrises over the timestamped run directories under `bench/logs/`, so it "
            "grows whenever an experiment archives, and new test files land between saves.",
            "",
            "For a pass count, run the suite offline and record the result with its own date "
            "and command: `python3 -m pytest bench/tests/ -q --netguard-strict`. The suite is "
            "offline by default via `bench/tests/conftest.py`; see docs/REPRODUCING.md. "
            "Figures labelled \"non-network\" before 2026-07-31 were hand-curated exclusions "
            "and included live model dispatch — do not quote them as offline results.",
        ])
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


def update_timestamp(
    filepath: Path, dry_run: bool = False, *, body_regenerated: bool = True,
) -> bool:
    """Update the 'Last updated:' line, saying WHAT was refreshed.

    This line used to be rewritten unconditionally on every sv, while the
    body update returned early whenever hand-written prose sat between the
    markers. The stamp therefore recorded when sv last RAN, not when anything
    was WRITTEN — and because sv stamps and commits in the same run, it always
    matched HEAD's commit time, so the false signal looked independently
    corroborated. A 2026-08-07 cold-start drill scored the resume path 1 of 5
    and named this as its first wrong turn: a reader trusts the date, treats a
    five-day-old body as current, and has no way to detect the difference.

    So the line now distinguishes the two cases. When the auto-generated block
    really was rewritten it reads as before; when the body was preserved it
    says so, and points at the dated entries that ARE the record of recency.
    """
    if not filepath.exists():
        return False

    text = filepath.read_text(encoding="utf-8")
    ts = timestamp_now()
    if not body_regenerated:
        ts += (" — state files only; the narrative below is hand-maintained "
               "and carries its own dates. This stamp is NOT a content date.")
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


def _co_author_trailer() -> Optional[str]:
    """Return the ``Co-Authored-By:`` trailer for an sv commit, or None.

    REPAIR S1 (2026-08-05). This was the literal string "Claude Opus 4.8".
    A hardcoded model version cannot know which model actually ran; it rots at
    the next model change and then stamps a false attribution onto every
    commit — the same provenance failure the project documents elsewhere
    ("a result attributed to a model that never produced it is
    indistinguishable, downstream, from a fabricated result"). It had already
    rotted: the session was Opus 5.

    So nothing is hardcoded. The trailer states only what this process can
    actually verify, in order of preference:

      1. ``CDSFL_SV_CO_AUTHOR`` — explicit operator-supplied identity, wins
         outright (e.g. ``CDSFL_SV_CO_AUTHOR="Claude Opus 5"``).
      2. ``ANTHROPIC_MODEL`` — the model id the running session was told to
         use. Named exactly as given, not paraphrased.
      3. ``CLAUDECODE=1`` and nothing more: the commit was produced through
         Claude Code, but this environment exposes NO model version. Say that
         much and assert no version.
      4. None of the above — sv was run by a human at a shell. No AI
         co-author trailer at all; claiming one would be fabrication.
    """
    override = os.environ.get("CDSFL_SV_CO_AUTHOR", "").strip()
    if override:
        return f"Co-Authored-By: {override} <noreply@anthropic.com>"

    model = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if model:
        return f"Co-Authored-By: Claude Code ({model}) <noreply@anthropic.com>"

    if os.environ.get("CLAUDECODE") == "1":
        return "Co-Authored-By: Claude Code <noreply@anthropic.com>"

    return None


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


# ── Operational-tracker mirror parity (REPAIR S5) ─────────────────────────
#
# Policy says the two tracker copies are kept in step, but nothing enforced
# it, so it was an unenforced habit. The function below is the DETECTOR: it
# reports whether they agree, which is newer, and how they differ, and it
# never writes. It is retained here as the backstop inside _commit_and_push.
#
# WHICH SIDE WINS is a separate question, and it is now answered: the founder
# ruled on 2026-08-05 that the REPO copy is CANONICAL and the Desktop copy is
# the mirror. That direction is applied by _reconcile_tracker() further down,
# not here. The words "canonical" and "mirror" inside this detector's own
# messages predate that ruling and describe the OLD roles — the detector says
# so on screen rather than quietly printing a stale label.

_TRACKER_DESKTOP = Path.home() / "Desktop" / "CDSFL_Agent_Operational_Plan.md"
_TRACKER_MIRROR_REL = "experimental_notes/CDSFL_Agent_Operational_Plan.md"


def _tracker_warn(lines: list[str]) -> None:
    """Print an unmissable tracker-mirror warning to stderr."""
    # stdout is block-buffered when sv is piped or redirected, stderr is not.
    # Without this flush the warning surfaces detached from the output it
    # refers to — an unmissable warning nobody can place is half a warning.
    sys.stdout.flush()
    bar = "!" * 74
    print(bar, file=sys.stderr)
    print("  OPERATIONAL TRACKER OUT OF SYNC", file=sys.stderr)
    for line in lines:
        print(f"  {line}", file=sys.stderr)
    print("  This detector never copies. sv applies the direction separately:", file=sys.stderr)
    print("  the REPO copy is canonical (founder ruling, 2026-08-05), so a save", file=sys.stderr)
    print(f"  refreshes {_TRACKER_DESKTOP} from it —", file=sys.stderr)
    print("  and REFUSES if the Desktop copy is the newer of the two.", file=sys.stderr)
    print(bar, file=sys.stderr)


def _tracker_diff(
    from_lines: list[str], to_lines: list[str], fromfile: str, tofile: str,
) -> list[str]:
    """Return only the added/removed lines of a unified diff, no headers."""
    return [
        line for line in difflib.unified_diff(
            from_lines, to_lines,
            fromfile=fromfile, tofile=tofile,
            lineterm="", n=0,
        )
        if line[:1] in "+-" and not line.startswith(("+++", "---"))
    ]


def _check_tracker_mirror(root: Path, desktop: Path | None = None) -> bool:
    """Compare the canonical Desktop tracker with the repo mirror.

    Returns True if they are byte-identical (or neither exists, meaning this
    is not a CDSFL working tree). Returns False and prints a LOUD warning
    naming which side is newer and how they differ. Never writes.
    """
    desk = _TRACKER_DESKTOP if desktop is None else desktop
    mirror = root / _TRACKER_MIRROR_REL

    if not desk.exists() and not mirror.exists():
        return True

    if not mirror.exists():
        _tracker_warn([
            f"Repo mirror is MISSING: {mirror}",
            f"Canonical Desktop copy exists: {desk}",
            "The mirror is what survives a machine loss. Nothing is backed up.",
        ])
        return False

    if not desk.exists():
        _tracker_warn([
            f"Canonical Desktop copy is MISSING: {desk}",
            f"Repo mirror exists: {mirror}",
            "The canonical tracker is the first read after compaction.",
        ])
        return False

    try:
        desk_bytes = desk.read_bytes()
    except (PermissionError, OSError) as exc:
        # CONTENT IS UNREADABLE BUT METADATA IS NOT. Measured 2026-08-25: on this
        # machine ~/Desktop denied read() on 2026-08-25 (6 of 6 attempts) while
        # stat() and write() both succeed. Content comparison was the ONE operation
        # unavailable, and both this check and _reconcile_tracker were built on it.
        #
        # Falling back to size gives a determinate answer rather than an unknown one,
        # and it would have caught the real drift this check exists for: on
        # 2026-08-24 the RUNWAY mirror was 326 lines against the repo's 453, which is
        # a large size difference, not a subtle one. Equal size is weaker evidence
        # than equal bytes and is reported as such rather than as parity.
        try:
            desk_size = desk.stat().st_size
        except (PermissionError, OSError):
            _tracker_warn([
                f"Tracker parity NOT MEASURED: {type(exc).__name__} on read AND stat.",
                f"{desk} is present but wholly inaccessible to this process.",
                "The REPO copy is canonical and unaffected. Parity is UNKNOWN.",
            ])
            return True
        try:
            mirror_size = mirror.stat().st_size
        except OSError:
            return True
        if desk_size == mirror_size:
            print("  Tracker mirror: sizes match (content unreadable — weaker than "
                  "byte parity, but consistent with it).")
            return True
        _tracker_warn([
            f"Tracker mirror SIZE MISMATCH: repo {mirror_size} bytes, "
            f"Desktop {desk_size} bytes.",
            "Content could not be compared (read denied); size says they differ.",
            "The REPO copy is canonical (founder ruling 2026-08-06) — refresh the "
            "Desktop copy from it, never the reverse.",
        ])
        return True
    mirror_bytes = mirror.read_bytes()
    if desk_bytes == mirror_bytes:
        print("  Tracker mirror: in sync with the Desktop canonical copy.")
        return True

    desk_mtime = datetime.fromtimestamp(desk.stat().st_mtime)
    mirror_mtime = datetime.fromtimestamp(mirror.stat().st_mtime)
    newer = "Desktop canonical" if desk_mtime >= mirror_mtime else "repo mirror"

    desk_lines = desk_bytes.decode("utf-8", "replace").splitlines()
    mirror_lines = mirror_bytes.decode("utf-8", "replace").splitlines()
    diff = _tracker_diff(
        desk_lines, mirror_lines, "Desktop (canonical)", "repo mirror",
    )
    only_desk = sum(1 for line in diff if line.startswith("-"))
    only_mirror = sum(1 for line in diff if line.startswith("+"))

    detail = [
        f"Desktop canonical: {desk}",
        f"  {len(desk_lines)} lines, {len(desk_bytes)} bytes, modified {desk_mtime:%Y-%m-%d %H:%M:%S}",
        f"Repo mirror:       {mirror}",
        f"  {len(mirror_lines)} lines, {len(mirror_bytes)} bytes, modified {mirror_mtime:%Y-%m-%d %H:%M:%S}",
        f"NEWER BY MTIME: {newer}",
        "  ^ the two labels above are this detector's PRE-RULING names for the",
        "    files. Since 2026-08-05 the REPO copy is canonical and the Desktop",
        "    copy is the mirror. Read them as file locations, not as authority.",
        f"Differing lines: {only_desk} only on Desktop, {only_mirror} only in the mirror.",
    ]
    if diff:
        detail.append("First differing lines:")
        detail.extend(f"    {line}" for line in diff[:10])
        if len(diff) > 10:
            detail.append(f"    ... and {len(diff) - 10} more differing line(s)")
    _tracker_warn(detail)
    return False


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

    # 0a. WORKING BRANCH GUARD (2026-08-15). Founder ruling: main is the only
    #     branch that gets updated, unless there is a stated reason to open a
    #     new experimental branch.
    #
    #     This exists because the ruling was made once and then silently
    #     decayed. A milestone merge to main was made on 28 July 2026, and work
    #     continued on exp39-experimental from 19:11 that same evening, for a
    #     further 107 commits over 18 days. Nothing was lost — main was brought
    #     current on 15 August and every path was verified against it — but for
    #     that fortnight the public repository showed a project 16 days stale
    #     while the real work sat on a branch nobody outside would think to read.
    #
    #     The cause was mechanical: this function pushes to whatever branch is
    #     checked out and had no concept of main. An agreement nobody wired into
    #     the tooling is an agreement that lasts until the next distraction.
    #
    #     WARNS, never aborts. A deliberate experimental branch is legitimate;
    #     drifting onto one by accident is not. The distinction is whether
    #     anyone noticed, so this makes it impossible not to.
    try:
        _branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if _branch and _branch != "main":
            print()
            print("=" * 74)
            print(f"  NOT ON main — committing to '{_branch}'")
            print("  Founder ruling: main is the only branch that gets updated,")
            print("  unless there is a stated reason to open an experimental branch.")
            print("  If this branch is deliberate, carry on. If it is drift, stop:")
            print("      git checkout main")
            print("  Drift is what left main 16 days stale in August 2026.")
            print("=" * 74)
            print()
    except (OSError, subprocess.SubprocessError):
        pass  # never let the guard block a save

    # 0. Operational-tracker mirror parity, BEFORE staging (REPAIR S5).
    #    Warn only, never copy. Gated on this being the real CDSFL working
    #    tree — the tracker policy names those two specific files, so the
    #    comparison is meaningless in a synthetic repo. In every real sv run
    #    main() passes root=repo_root(), so this always fires.
    #    It WARNS; it must never abort a commit, so an unreadable file is
    #    itself reported rather than raised.
    if root.resolve() == repo_root().resolve():
        try:
            _check_tracker_mirror(root)
        except OSError as err:
            _tracker_warn([f"Mirror comparison could not run: {err}"])

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
    trailer = _co_author_trailer()
    if trailer is None:
        full_msg = message
        print("  NOTE: no AI co-author trailer — sv was not run from a Claude Code session.")
    else:
        full_msg = f"{message}\n\n{trailer}"
        print(f"  {trailer}")
        if not (os.environ.get("CDSFL_SV_CO_AUTHOR", "").strip()
                or os.environ.get("ANTHROPIC_MODEL", "").strip()):
            print("         (no model version recorded — this environment exposes "
                  "none; set ANTHROPIC_MODEL or CDSFL_SV_CO_AUTHOR)")
    _git("commit", "-m", full_msg, root=root, timeout=60)

    new_hash = _git("log", "--oneline", "-1", root=root)
    print(f"  Committed: {new_hash} ({n_files} files)")

    # 9. Push
    if push:
        branch = _git("branch", "--show-current", root=root)
        _git("push", "origin", branch, root=root, timeout=120)
        print(f"  Pushed to origin/{branch}")
        # Do not take the push command's exit code as the answer. Measure.
        _print_sync_verdict(_verify_remote_sync(root))

    return True



def _print_final_state(root, push: bool) -> None:
    """The ONE block that describes the state sv actually finished in.

    Everything printed before the commit is a pre-commit reading. This runs
    after the commit and, if requested, after the push, and it re-measures
    rather than restating. Never raises: sv has already succeeded by the time
    this runs, and a traceback here would turn a completed save into a failure.
    """
    bar = "=" * 74
    try:
        head = _git("log", "--oneline", "-1", root=root, check=False) or "unknown"
        branch = _git("branch", "--show-current", root=root, check=False) or "unknown"
        dirty = _git("status", "--porcelain", root=root, check=False)
    except (subprocess.SubprocessError, OSError):
        head, branch, dirty = "unknown", "unknown", ""
    print(bar)
    print("  SV COMPLETE — state AFTER the save, re-measured:")
    print(f"    Commit:       {head}")
    print(f"    Branch:       {branch}")
    print(f"    Working tree: {'clean' if not dirty else 'DIRTY (' + str(len(dirty.splitlines())) + ' path(s) still uncommitted)'}")
    if not push:
        print("    Remote:       NOT PUSHED (no --push). Local is ahead of the remote.")
        print(bar)
        return
    try:
        sy = _verify_remote_sync(root)
    except Exception as exc:
        print(f"    Remote:       NOT VERIFIED ({type(exc).__name__}) — this is a "
              "failed measurement, not evidence the push worked.")
        print(bar)
        return
    if sy["error"] and sy["upstream_ahead"] is None:
        print(f"    Remote:       NOT VERIFIED — {sy['error']}")
        print("                  A failed check is NOT evidence the push worked.")
    elif sy["in_sync"]:
        print(f"    Remote:       origin/{sy['branch']} == HEAD. Fully in sync.")
    else:
        print(f"    Remote:       NOT IN SYNC — origin/{sy['branch']} is "
              f"{sy['upstream_ahead']} behind, {sy['upstream_behind']} ahead.")
    if sy.get("main_behind"):
        print(f"    PUBLIC main:  {sy['main_behind']} COMMITS BEHIND this branch. "
              "The public repository does NOT show this work.")
    print(bar)


def _sync_sentence(root, gs, pushed: bool) -> str:
    """The summary's one sentence about sync, MEASURED after the push."""
    try:
        sy = _verify_remote_sync(root)
    except Exception as exc:  # never raise: sv has already succeeded by now
        return (f"Branch: {gs['branch']}. Pushed: {'yes' if pushed else 'no'}. "
                f"Post-push sync NOT VERIFIED ({type(exc).__name__}).")
    head = f"Branch: {sy['branch'] or gs['branch']}. Pushed: {'yes' if pushed else 'no'}."
    if sy["error"] and sy["upstream_ahead"] is None:
        body = f" Remote sync NOT VERIFIED: {sy['error']}."
    elif sy["in_sync"]:
        body = f" Remote AFTER this sv: origin/{sy['branch']} == HEAD, fully in sync."
    else:
        body = (f" Remote AFTER this sv: NOT in sync -- origin/{sy['branch']} is "
                f"{sy['upstream_ahead']} behind, {sy['upstream_behind']} ahead.")
    if sy.get("main_behind"):
        body += f" Public main is {sy['main_behind']} commits behind this branch."
    return head + body


def _verify_remote_sync(root) -> dict:
    """Re-MEASURE local vs remote after a push. Never raises.

    FOUNDER INSTRUCTION 2026-08-26, verbatim: "a push/commit should cause both
    local and remote to be *fully* in sync. Surely that is the point of the
    entire exercise? Whatever you are doing that might be preventing this, you
    should fix it." And: sv must complete with "zero errors and zero ambiguity
    about the completed sv state".

    THE DEFECT THIS REPLACES. The session summary said "Remote before this sv:
    <N ahead>" and "Pushed: yes", and stopped. Both statements were true and
    neither answered the only question being asked, because the before-state
    plus a boolean is not an after-state -- a push that silently pushed nothing,
    or pushed a branch nobody reads, produced the same two lines as a push that
    worked. The remedy is not better wording. It is to measure again afterwards.

    Returns keys: branch, upstream_ahead, upstream_behind, in_sync,
    main_behind (how far public main trails this branch), error.
    """
    out = {"branch": "", "upstream_ahead": None, "upstream_behind": None,
           "in_sync": False, "main_behind": None, "error": ""}
    try:
        out["branch"] = _git("branch", "--show-current", root=root, check=False) or ""
        b = out["branch"]
        if not b:
            out["error"] = "detached HEAD: no branch to compare"
            return out
        # Refresh the remote-tracking refs, or the counts describe a stale view.
        _git("fetch", "origin", "--quiet", root=root, check=False, timeout=60)
        ref = f"origin/{b}"
        exists = _git("rev-parse", "--verify", "--quiet", ref, root=root, check=False)
        if not exists:
            out["error"] = f"{ref} does not exist: this branch has never been pushed"
        else:
            a = _git("rev-list", "--count", f"{ref}..HEAD", root=root, check=False)
            d = _git("rev-list", "--count", f"HEAD..{ref}", root=root, check=False)
            out["upstream_ahead"] = int(a) if a.isdigit() else None
            out["upstream_behind"] = int(d) if d.isdigit() else None
            out["in_sync"] = out["upstream_ahead"] == 0 and out["upstream_behind"] == 0
        if b != "main":
            m = _git("rev-list", "--count", "origin/main..HEAD", root=root, check=False)
            out["main_behind"] = int(m) if m.isdigit() else None
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def _print_sync_verdict(sync: dict) -> None:
    """One unambiguous line about where the work now is. Loud when it is not
    where the founder expects it."""
    print()
    print("=" * 74)
    if sync["error"] and sync["upstream_ahead"] is None:
        print(f"  REMOTE SYNC: NOT VERIFIED -- {sync['error']}")
        print("  This is a failed measurement, NOT evidence that the push worked.")
    elif sync["in_sync"]:
        print(f"  REMOTE SYNC: origin/{sync['branch']} == local HEAD. Fully in sync.")
    else:
        print(f"  REMOTE SYNC: NOT IN SYNC -- origin/{sync['branch']} is "
              f"{sync['upstream_ahead']} behind and {sync['upstream_behind']} ahead "
              "of local HEAD.")
    if sync.get("main_behind"):
        print(f"  PUBLIC main IS {sync['main_behind']} COMMITS BEHIND this branch.")
        print(f"  Pushing '{sync['branch']}' does NOT update main. Anyone reading the")
        print("  public repository sees main, not this branch. Merge to update it.")
    elif sync["branch"] and sync["branch"] != "main":
        print(f"  Public main is level with this branch.")
    print("=" * 74)
    print()


# ── Open Brain session capture (REPAIR S3) ────────────────────────────────
#
# The sv spec in ~/.claude/CLAUDE.md and resources/ONBOARDING.md both name
# "Open Brain session summary" FIRST, and this script contained no Open Brain
# code of any kind — which is why the store's last session_summary was
# 2026-08-02 while substantial sessions ran on 08-04 and 08-05.
#
# Canonical install: /Users/georgejackson/Developer_Projects/OpenBrain/ (pip
# editable). Invoked as `<this python> -m open_brain.cli`, which resolves via
# the editable install — deliberately NO PYTHONPATH, so it cannot be captured
# by the stale fork at Project_Genesis/open_brain/.
#
# It must never break sv: capture failure is loud, not fatal.

_OPEN_BRAIN_PROJECT = "CDSFL"
_OPEN_BRAIN_TIMEOUT = 180


def _open_brain_command(summary: str) -> list[str]:
    """Build the Open Brain capture command.

    ``--project`` is set explicitly: rows written without it are invisible to
    the project filter.
    """
    return [
        sys.executable, "-m", "open_brain.cli", "capture",
        "--agent", "cc",
        "--type", "session_summary",
        "--project", _OPEN_BRAIN_PROJECT,
        summary,
    ]


def _open_brain_warn(reason: str, summary: str) -> None:
    """Print an unmissable warning that the Open Brain capture did NOT land."""
    bar = "!" * 74
    print(bar, file=sys.stderr)
    print("  OPEN BRAIN CAPTURE FAILED — THE COMMIT LANDED, THE MEMORY DID NOT.", file=sys.stderr)
    print("  Open Brain is now BEHIND this commit. Recovery from the store alone", file=sys.stderr)
    print("  will not see this session.", file=sys.stderr)
    print(f"  Reason: {reason}", file=sys.stderr)
    print("  Capture it by hand with:", file=sys.stderr)
    print(
        "    python3 -m open_brain.cli capture --agent cc --type session_summary "
        f"--project {_OPEN_BRAIN_PROJECT} \\", file=sys.stderr,
    )
    print(f"      {summary!r}", file=sys.stderr)
    print(bar, file=sys.stderr)


def _open_brain_capture(
    summary: str,
    root: Path,
    timeout: int = _OPEN_BRAIN_TIMEOUT,
    runner=subprocess.run,
) -> bool:
    """Capture one session summary to Open Brain. Returns True on success.

    Never raises: sv has already committed and pushed by the time this runs,
    and a memory-store outage must not turn a good commit into a traceback.
    Every failure path prints the loud warning above — there is no silent skip.
    """
    cmd = _open_brain_command(summary)
    try:
        result = runner(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=str(root),
        )
    except Exception as err:  # noqa: BLE001 — deliberately total; see docstring
        _open_brain_warn(f"{type(err).__name__}: {err}", summary)
        return False

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        _open_brain_warn(
            f"`open_brain.cli capture` exited {result.returncode}: {detail[:400]}",
            summary,
        )
        return False

    stored = (result.stdout or "").strip()
    print(f"  Open Brain: session summary captured (project={_OPEN_BRAIN_PROJECT}). {stored}")
    return True


def _open_brain_summary(
    message: str,
    gs: dict,
    tests: int | None,
    exp: dict | None,
    root: Path,
    pushed: bool,
) -> str:
    """Build the session-summary text from state sv has already measured.

    Runs AFTER the commit and push have landed, so it must not be able to
    raise: a git hiccup here would produce a traceback and a non-zero exit for
    a state save that actually succeeded.
    """
    try:
        head = _git("log", "--oneline", "-1", root=root, check=False)
    except (subprocess.SubprocessError, OSError):
        head = ""
    parts = [
        f"CDSFL sv {timestamp_now()}. {message.splitlines()[0] if message else ''}".strip(),
        f"Commit: {head}." if head else "Commit: unknown.",
        _sync_sentence(root, gs, pushed),
        f"Tests collected: {tests if tests else 'unknown'} "
        "(collection count, NOT a pass count).",
    ]
    if exp:
        parts.append(
            f"Latest experiment: {exp['name']} (#{exp['number']}) {exp['status']}, "
            f"{exp.get('total_rounds', 0)} rounds, gamma {exp.get('gamma', 0.0):.3f}."
        )
    else:
        parts.append("Latest experiment: none found in bench/logs/.")
    return " ".join(parts)


# ── Save-completeness pre-flight (founder rulings 3, 4 and 7, 2026-08-05) ─
#
# RULING 4, verbatim: "Refuse and print an alert if the task is not fully
# completed. Why these things are slipping through the net to begin with is
# genuinely mysterious. If an alert is sounded, presumably this would present
# us with an opportunity to look at why and fix it?"
#
# The second sentence is the important half. An alert that only says
# "something is missing" wastes the opportunity. Every check below therefore
# reports four things — what was checked, what it expected, what it actually
# observed, and where to look — plus the flag that overrides it when the
# omission is deliberate. A check that cannot be performed does NOT pass:
# unverified and verified-complete are different states and are reported as
# different states.
#
# The checks run only on a real committing run (and on --check-save, which is
# the rehearsal). A dry run performs none of them, because a dry run cannot
# produce the incomplete save they exist to prevent.

_MEMORY_DIR = (
    Path.home() / ".claude" / "projects"
    / "-Users-georgejackson-Developer-Projects" / "memory"
)
_MEMORY_INDEX_NAME = "MEMORY.md"

# The loader reads at most this many CHARACTERS of the index. Past it the
# newest entries — the ones a recovering session needs most — are dropped
# with no error anywhere. Characters, not bytes: this file is full of ★, γ
# and em-dashes, and conflating the two units would itself be a silent
# wrong answer.
_MEMORY_INDEX_LIMIT_CHARS = 25_000

# THE SECOND TRUNCATION TRIGGER, added 2026-09-01. The loader truncates on
# EITHER of two conditions and this file guarded only one of them, so a save
# could pass every check while the index was being cut on line count. Both
# constants are read out of the installed binary rather than assumed:
#
#   $ python3 -c "...re.finditer(rb'PRe=\\d+', data)..."   -> PRe=25000
#   $ python3 -c "...re.finditer(rb'fie=\\d+', data)..."   -> fie=200
#   /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe
#   v2.1.220, re-confirmed 2026-09-01 (first extracted in the 2026-08-05
#   recovery-resource audit, same values).
#
# The enforcing function is:
#   function Rtr(e,t="index"){let{trimmed:r,lineCount:n,byteCount:o}=EDt(e),
#                             i=n>fie, s=o>PRe; ...}
#   function EDt(e){let t=e.trim();
#                   return{trimmed:t,lineCount:au(t,'\\n')+1,byteCount:t.length}}
#
# Two details of EDt are load-bearing and were both measured wrongly here
# before: it TRIMS first, and `t.length` is the JavaScript UTF-16 length, not
# UTF-8 bytes and not Python code points. Those three units differ on this
# file — 24,451 UTF-8 bytes against 24,040 code points — so a guard written in
# bytes fires roughly 400 characters early, and one written in code points
# agrees with the loader only while the index stays free of astral characters
# (an emoji in a memory title would silently break the equivalence).
_MEMORY_INDEX_LIMIT_LINES = 200
_MEMORY_INDEX_REFUSE_FRACTION = 0.95
_MEMORY_ENTRY_ONE_LINE_CHARS = 150

# Canonical Open Brain install. Named explicitly because a stale fork of the
# same package exists elsewhere on this machine, and an import that resolves
# to it writes session summaries into the wrong store while reporting success.
_OPEN_BRAIN_ROOT = Path.home() / "Developer_Projects" / "OpenBrain"

_PREFLIGHT_TIMEOUT = 30

_FLAG_ALLOW_INCOMPLETE = "--allow-incomplete-save"
_FLAG_OVERWRITE_DESKTOP = "--overwrite-newer-desktop-tracker"

# THE BLIND SPOT, 2026-09-01. This pattern required the "[" to follow the
# bullet directly, so every entry written as `- **[Title](file.md)**` was not an
# entry at all as far as this audit was concerned. Measured on the live index:
# 15 of 132 entries invisible (11.4%, Wilson [7.0%, 17.9%]) -- and ALL 15 were
# over the 150-character one-line rule, carrying 4,050 characters of excess
# against 1,135 in the 117 entries the audit could see. The check built to
# catch over-long entries was blind to the longest ones in the file, which were
# also the newest, because bold is what a session note reaches for to mark
# itself important. Entry counts, the median, headroom-in-entries and the
# over-long report were all computed off the smaller set.
_MEMORY_ENTRY_RE = re.compile(r"^\s*[-*]\s+\*{0,2}\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class _Check:
    """One completeness check and the evidence behind its verdict."""

    name: str
    passed: bool
    why: str
    expected: str
    observed: str
    look_at: str = ""
    override: str = _FLAG_ALLOW_INCOMPLETE
    # Any file this check WROTE while running, or "" if it wrote nothing. The
    # alert reports what actually happened rather than asserting that nothing
    # did: the tracker reconciliation (ruling 3) can legitimately refresh the
    # Desktop mirror in the same pre-flight that a later check then refuses.
    wrote: str = ""


@dataclass
class _MemoryIndexAudit:
    """Read-only audit of the persistent-memory index (RULING 7)."""

    path: Path
    error: str = ""
    chars: int = 0
    lines: int = 0
    byte_len: int = 0
    entries: list[tuple[str, str, int]] = field(default_factory=list)
    broken: list[str] = field(default_factory=list)
    orphans_unmentioned: list[str] = field(default_factory=list)
    orphans_mentioned: list[str] = field(default_factory=list)
    over_long: list[tuple[int, str]] = field(default_factory=list)
    median_entry: int = 0

    @property
    def headroom(self) -> int:
        return _MEMORY_INDEX_LIMIT_CHARS - self.chars

    @property
    def lines_headroom(self) -> int:
        return _MEMORY_INDEX_LIMIT_LINES - self.lines

    @property
    def entries_left(self) -> int:
        """How many more entries fit, at the current median entry size.

        Each entry costs its own line plus the newline that terminates it.
        """
        if self.median_entry <= 0:
            return -1  # unknown: nothing parsed to take a median of
        return max(0, self.headroom) // (self.median_entry + 1)


def _audit_memory_index(mem_dir: Path) -> _MemoryIndexAudit:
    """Audit the memory index. READS ONLY — never writes under mem_dir."""
    index = mem_dir / _MEMORY_INDEX_NAME
    audit = _MemoryIndexAudit(path=index)

    if not mem_dir.is_dir():
        audit.error = f"persistent-memory folder does not exist: {mem_dir}"
        return audit
    if not index.is_file():
        audit.error = f"index file does not exist: {index}"
        return audit
    try:
        raw = index.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as err:
        audit.error = f"index unreadable — {type(err).__name__}: {err}"
        return audit

    audit.byte_len = len(raw)
    # EDt trims before measuring, and counts UTF-16 code units. Mirrored
    # exactly so this audit and the loader cannot disagree about the same file.
    trimmed = text.strip()
    audit.chars = sum(2 if ord(ch) > 0xFFFF else 1 for ch in trimmed)
    audit.lines = trimmed.count("\n") + 1 if trimmed else 0

    # Parse per line. A multiline regex would let ``\s`` swallow newlines and
    # silently mis-measure entry lengths.
    for line in text.splitlines():
        m = _MEMORY_ENTRY_RE.match(line)
        if m:
            audit.entries.append((m.group(1), m.group(2), len(line)))

    targets = {t for _title, t, _n in audit.entries if t.endswith(".md")}
    audit.broken = sorted(t for t in targets if not (mem_dir / t).is_file())

    # glob() returns [] on a permission denial instead of raising, which
    # would report every indexed file as missing. Enumerate explicitly.
    try:
        on_disk = {p.name for p in _memory_files(mem_dir)
                   if p.name.endswith(".md")} - {_MEMORY_INDEX_NAME}
    except MemoryUnreadable as exc:
        audit.error = str(exc)
        return audit
    for name in sorted(on_disk - targets):
        # A name that appears in the prose but not as an index entry is a
        # weaker fault than one that appears nowhere, so they are separated
        # rather than lumped together under a single scary heading.
        if name in text:
            audit.orphans_mentioned.append(name)
        else:
            audit.orphans_unmentioned.append(name)

    audit.over_long = sorted(
        ((n, title) for title, _t, n in audit.entries
         if n > _MEMORY_ENTRY_ONE_LINE_CHARS),
        reverse=True,
    )
    lengths = sorted(n for _title, _t, n in audit.entries)
    audit.median_entry = int(statistics.median(lengths)) if lengths else 0
    return audit


def _memory_ledger_section(text: str, heading: str) -> str:
    """Return a top-level markdown section from ``heading`` to the next ``##``."""
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    return text[start:] if end == -1 else text[start:end]


def _memory_ledger_bucket_names(section: str) -> set[str]:
    """Names counted by the public exclusion ledger.

    This intentionally mirrors ``bench/tests/test_recovery_memory_doc_repairs.py``:
    uppercase ``MEMORY.md`` prose mentions are not bucket entries, while the
    lower-case private memory filenames are.
    """
    return set(re.findall(r"`([a-z0-9_.-]+\.md)`", section))


def _replace_memory_ledger_count_row(text: str, label: str, count: int) -> str:
    pattern = re.compile(
        rf"(\|[^|\n]*{re.escape(label)}[^|\n]*\|\s*)(\**)\d+(\**)(\s*\|)"
    )

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{count}{match.group(3)}{match.group(4)}"

    return pattern.sub(repl, text, count=1)


class MemoryUnreadable(Exception):
    """The private memory directory could not be READ, as distinct from absent.

    MEASURED mid-session on 2026-08-26, between 00:53 and 01:27 BST: this process
    lost read access to the memory directory while running. Under that state
    `exists()` and `is_dir()` both return True, `iterdir()` and `read_text()`
    raise PermissionError, and `glob()` returns an EMPTY LIST without raising.

    sv guarded every one of those sites with `is_dir()`, so the guard did not
    fire, and `_update_memory_exclusions_ledger` crashed sv outright with a
    traceback and exit 1. Earlier in the same window the same command exited 0,
    stamping the ledger 00:53.

    THE EXACT MINUTE IS NOT RECORDED, AND THAT IS ITSELF A DEFECT. Earlier drafts
    of this docstring said "01:45", and the test file said the crash was at
    "01:52". Both were typed rather than captured, and both were LATER than the
    clock actually read at the moment of writing. This project's rule is that a
    time is read from the clock and never typed; the hook that supplies it fires
    on user turns, and a long autonomous stretch has none, so `date` has to be
    run deliberately. It was not. The bracket above is what the evidence supports.

    Absent and unreadable must not share a code path: absent means there is
    nothing to count, unreadable means the count DID NOT HAPPEN. The second must
    never produce a fresh "counted <date>" stamp, because a stamp is a claim
    about when the number was last verified.
    """


def _memory_files(mem: Path) -> list:
    """Every file in the memory directory, or raise MemoryUnreadable.

    Never returns an empty list to mean "denied" -- that is the glob() defect
    this exists to remove.
    """
    try:
        return [p for p in mem.iterdir() if p.is_file()]
    except (PermissionError, OSError) as exc:
        raise MemoryUnreadable(
            f"{mem} cannot be enumerated: {type(exc).__name__}. The count did "
            "not happen; this is not evidence that the directory is empty."
        ) from exc


def _update_memory_exclusions_ledger(
    root: Path,
    *,
    mem_dir: Optional[Path] = None,
    dry_run: bool = False,
    counted_at: Optional[str] = None,
) -> bool:
    """Recount ``resources/MEMORY_EXCLUSIONS.md`` from the private memory dir.

    The ledger's recurring failure mode was not the check; it was relying on an
    author to bump the accounting table by hand after writing a memory file.
    ``sv`` already knows the private memory directory for its completeness
    checks, so the save path owns the recount.
    """
    ledger = root / "resources" / "MEMORY_EXCLUSIONS.md"
    mem = _MEMORY_DIR if mem_dir is None else mem_dir
    if not ledger.is_file() or not mem.is_dir():
        return False

    try:
        text = ledger.read_text(encoding="utf-8")
        excluded = _memory_ledger_bucket_names(
            _memory_ledger_section(text, "## Excluded Entries")
        )
        unclassified = _memory_ledger_bucket_names(
            _memory_ledger_section(text, "## Unclassified — awaiting review")
        )
    except (OSError, UnicodeDecodeError, ValueError):
        return False

    # Raises MemoryUnreadable rather than crashing sv or, worse, counting a
    # denial as an empty directory and writing 0 into the ledger.
    on_disk = sorted(p.name for p in _memory_files(mem))
    if _MEMORY_INDEX_NAME not in on_disk:
        return False

    individual = [name for name in on_disk if name != _MEMORY_INDEX_NAME]
    handoffs = {name for name in individual if name.startswith("handoff_")}
    mirrored = set(individual) - excluded - unclassified - handoffs

    counts = {
        "Mirrored (in summarised form) in `MEMORY.md`": len(mirrored),
        "Named as excluded, with a reason, below": len(excluded),
        "Session handoffs, declared in `MEMORY.md` as retained privately and deliberately not mirrored": len(handoffs),
        "Unclassified — neither mirrored nor previously declared": len(unclassified),
        "total": len(individual),
    }

    stamp = counted_at or datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    updated = re.sub(
        r"## Accounting \(counted [^)]+\)",
        f"## Accounting (counted {stamp})",
        text,
        count=1,
    )
    updated = re.sub(
        r"The directory holds \*\*\d+ files\*\*, of which one is `MEMORY\.md` itself\s*\n"
        r"\(the index\), leaving \*\*\d+ individual memory files\*\*\.",
        (
            f"The directory holds **{len(on_disk)} files**, of which one is `MEMORY.md` itself\n"
            f"(the index), leaving **{len(individual)} individual memory files**."
        ),
        updated,
        count=1,
    )
    for label, count in counts.items():
        updated = _replace_memory_ledger_count_row(updated, label, count)

    if updated == text:
        return False
    if not dry_run:
        ledger.write_text(updated, encoding="utf-8")
    return True


def _print_memory_index_report(audit: _MemoryIndexAudit) -> None:
    """Print the RULING 7 reports. These inform; only size can refuse."""
    print(f"  Persistent-memory index: {audit.path}")
    if audit.error:
        print(f"    NOT AUDITED — {audit.error}")
        return

    pct = 100.0 * audit.chars / _MEMORY_INDEX_LIMIT_CHARS
    left = audit.entries_left
    left_str = (
        "unknown (no index entries parsed)" if left < 0
        else f"~{left} more entr{'y' if left == 1 else 'ies'} at the current "
             f"median entry size of {audit.median_entry} chars"
    )
    print(
        f"    Size: {audit.chars} of {_MEMORY_INDEX_LIMIT_CHARS} characters "
        f"({pct:.1f}% of the loader limit; the file is {audit.byte_len} bytes)"
    )
    print(f"    Headroom: {audit.headroom} characters — {left_str}.")
    print(f"    Entries: {len(audit.entries)} linked, {len(audit.broken)} broken.")
    for target in audit.broken:
        print(f"      BROKEN LINK: {target} — linked from the index, absent from disk")

    orphans = audit.orphans_unmentioned + audit.orphans_mentioned
    if not orphans:
        print("    Orphans: none — every .md file in the folder is linked.")
    else:
        print(
            f"    Orphans: {len(orphans)} .md file(s) exist but are not linked "
            "from the index, so they will never be recalled:"
        )
        for name in audit.orphans_unmentioned:
            print(f"      {name} — name appears nowhere in the index")
        for name in audit.orphans_mentioned:
            print(f"      {name} — name appears in the index text, but not as an entry")

    if not audit.over_long:
        print(f"    One-line rule: all entries are within {_MEMORY_ENTRY_ONE_LINE_CHARS} chars.")
    else:
        shown = audit.over_long[:5]
        print(
            f"    One-line rule: {len(audit.over_long)} of {len(audit.entries)} "
            f"entries exceed {_MEMORY_ENTRY_ONE_LINE_CHARS} chars "
            f"(longest {audit.over_long[0][0]}):"
        )
        for n, title in shown:
            print(f"      {n:5d}  {title[:64]}")
        if len(audit.over_long) > len(shown):
            print(
                f"      … and {len(audit.over_long) - len(shown)} more, not shown "
                f"(capped at {len(shown)})"
            )


def _check_memory_index_size(audit: _MemoryIndexAudit) -> _Check:
    """The one RULING 7 check that can refuse a save."""
    threshold = int(_MEMORY_INDEX_LIMIT_CHARS * _MEMORY_INDEX_REFUSE_FRACTION)
    # THE ORIGINAL RATIONALE HERE WAS FALSIFIED, 2026-09-01. It read: "the
    # index is truncated silently, and what is dropped is the END of the file
    # — the NEWEST entries ... Nothing reports that it happened." Three claims,
    # all wrong, and wrong in the alarming direction. The loader cuts at
    # `lastIndexOf('\\n', PRe)`, so the loss is the END of the file, but the end
    # of THIS file is the March 2026 handoffs the index itself labels
    # "historical, read only if relevant" — new entries are written near the
    # top. Measured 2026-09-01: the last six lines are dated 2026-03-19 to
    # 2026-03-23, the first fifteen are dated 2026-08-30 to 2026-08-31, and the
    # entry written that night landed at line 125 of 183. Nor is it silent:
    # Rtr appends a visible "MEMORY.md is N bytes (limit: 25000)" warning into
    # the context. The condition is real and worth refusing on, but it is
    # housekeeping with announced failure, not silent loss of the newest work,
    # and saying otherwise sends a reader hunting for the wrong remedy.
    why = (
        "the loader truncates the index on EITHER limit — over "
        f"{_MEMORY_INDEX_LIMIT_CHARS} characters or over {_MEMORY_INDEX_LIMIT_LINES} "
        "lines — and what it drops is the tail, which on this file is the "
        "oldest archival material. Truncation is announced by the loader, so "
        "this is housekeeping rather than silent loss; it still refuses, "
        "because a save should not be the thing that pushes the index over."
    )
    expected = (
        f"the index under {threshold} characters AND under "
        f"{int(_MEMORY_INDEX_LIMIT_LINES * _MEMORY_INDEX_REFUSE_FRACTION)} lines, i.e. below "
        f"{_MEMORY_INDEX_REFUSE_FRACTION:.0%} of both loader limits "
        f"({_MEMORY_INDEX_LIMIT_CHARS} characters, {_MEMORY_INDEX_LIMIT_LINES} lines)"
    )
    if audit.error:
        return _Check(
            name="memory-index-headroom", passed=False, why=why, expected=expected,
            observed=f"the index could not be measured — {audit.error}",
            look_at=str(audit.path),
        )
    line_threshold = int(_MEMORY_INDEX_LIMIT_LINES * _MEMORY_INDEX_REFUSE_FRACTION)
    if audit.lines >= line_threshold:
        return _Check(
            name="memory-index-headroom", passed=False, why=why, expected=expected,
            observed=(
                f"{audit.lines} lines — {audit.lines_headroom} below the "
                f"{_MEMORY_INDEX_LIMIT_LINES}-line loader limit. The LINE limit is "
                f"the binding one here; the file is {audit.chars} characters "
                f"({audit.headroom} left). Consolidate entries before saving."
            ),
            look_at=str(audit.path),
        )
    if audit.chars >= threshold:
        return _Check(
            name="memory-index-headroom", passed=False, why=why, expected=expected,
            observed=(
                f"{audit.chars} characters — {audit.headroom} left, room for about "
                f"{max(audit.entries_left, 0)} more entries. Consolidate or prune "
                "entries before saving."
            ),
            look_at=str(audit.path),
        )
    return _Check(
        name="memory-index-headroom", passed=True, why=why, expected=expected,
        observed=(f"{audit.chars} characters ({audit.headroom} left), "
                  f"{audit.lines} lines ({audit.lines_headroom} left)"),
        look_at=str(audit.path),
    )


def _previous_sv_commit(root: Path) -> Optional[tuple[str, str, datetime]]:
    """Return (short sha, subject, commit time) of the most recent sv commit.

    ``--grep`` matches anywhere in the message, so the subject is re-checked
    here: a body line beginning "sv:" must not be mistaken for an sv commit.
    """
    out = _git(
        "log", "--grep=^sv:", "--format=%H%x1f%cI%x1f%s", "-n", "50",
        root=root, check=False,
    )
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        sha, iso, subject = parts
        if not subject.startswith("sv:"):
            continue
        try:
            when = datetime.fromisoformat(iso)
        except ValueError:
            continue
        return sha[:7], subject, when
    return None


def _mtime(path: Path) -> datetime:
    """Timezone-aware local modification time."""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).astimezone()


def _check_memory_updated(root: Path, mem_dir: Optional[Path] = None) -> _Check:
    """(a) At least one memory file changed since the previous sv commit."""
    mem = _MEMORY_DIR if mem_dir is None else mem_dir
    name = "memory-updated"
    why = (
        "an sv that commits code and documents but leaves the persistent-memory "
        "folder untouched saves the work and loses the session: the next "
        "recovery reads an index that has never heard of it."
    )

    if not mem.is_dir():
        return _Check(
            name, False, why=why,
            expected=f"a persistent-memory folder at {mem}",
            observed="no such folder — the check could not be performed",
            look_at=str(mem),
        )

    try:
        prev = _previous_sv_commit(root)
    except (RuntimeError, OSError, subprocess.SubprocessError) as err:
        return _Check(
            name, False, why=why,
            expected="git to report the previous sv commit's timestamp",
            observed=f"git failed — {type(err).__name__}: {err}",
            look_at="git log --grep='^sv:'",
        )

    if prev is None:
        return _Check(
            name, False, why=why,
            expected="a commit on this branch whose subject starts with 'sv:', "
                     "to measure 'modified since' against",
            observed="none found in the last 50 matching commits, so there is no "
                     "reference time — the check could not be performed, which is "
                     "not the same as passing",
            look_at="git log --grep='^sv:' --format='%h %cI %s'",
        )

    sha, subject, when = prev
    newest: Optional[tuple[Path, datetime]] = None
    for path in mem.rglob("*.md"):
        if not path.is_file():
            continue
        stamp = _mtime(path)
        if newest is None or stamp > newest[1]:
            newest = (path, stamp)

    ref = f"{sha} \"{subject[:60]}\" at {when:%Y-%m-%d %H:%M:%S %z}"
    expected = f"at least one *.md under {mem} modified after {ref}"

    if newest is None:
        return _Check(
            name, False, why=why, expected=expected,
            observed="the folder contains no .md files at all",
            look_at=str(mem),
        )

    path, stamp = newest
    if stamp > when:
        return _Check(
            name, True, why=why, expected=expected,
            observed=f"{path.name} modified {stamp:%Y-%m-%d %H:%M:%S %z}",
            look_at=str(mem),
        )

    behind = when - stamp
    hours = behind.total_seconds() / 3600.0
    return _Check(
        name, False, why=why, expected=expected,
        observed=(
            f"nothing has changed. The newest file is {path.name}, modified "
            f"{stamp:%Y-%m-%d %H:%M:%S %z} — {hours:.1f} hours BEFORE the previous "
            "sv commit. Write this session's memory, then re-run."
        ),
        look_at=str(mem),
    )


def _check_open_brain(
    root: Path,
    runner: Callable[..., Any] = subprocess.run,
    expected_root: Optional[Path] = None,
    timeout: int = _PREFLIGHT_TIMEOUT,
) -> _Check:
    """(b) Pre-flight the Open Brain capture path. WRITES NOTHING.

    The capture itself happens after the commit, where a failure is already
    too late to act on — by then the commit has landed and the store is behind
    it. So the path is proved beforehand, with two read-only probes: that
    ``import open_brain`` resolves inside the canonical checkout rather than a
    stale fork, and that the store answers. ``open_brain.cli status`` opens a
    read connection and runs ``SELECT 1``; it stores nothing.
    """
    expected = _OPEN_BRAIN_ROOT if expected_root is None else expected_root
    name = "open-brain-reachable"
    why = (
        "the sv contract names the Open Brain session summary first, and the "
        "capture runs AFTER the commit — so if the path is broken, the commit "
        "lands and the memory does not. Proving it first is the only point at "
        "which the operator can still do something about it."
    )

    probe = [
        sys.executable, "-c",
        "import open_brain, os; "
        "print(os.path.dirname(os.path.abspath(open_brain.__file__)))",
    ]
    try:
        res = runner(probe, capture_output=True, text=True, timeout=timeout, cwd=str(root))
    except Exception as err:  # noqa: BLE001 — any launch failure is a failed check
        return _Check(
            name, False, why=why,
            expected=f"`import open_brain` to resolve inside {expected}",
            observed=f"the probe could not run — {type(err).__name__}: {err}",
            look_at=str(expected),
        )
    if res.returncode != 0:
        detail = (res.stderr or res.stdout or "").strip().splitlines()
        return _Check(
            name, False, why=why,
            expected=f"`import open_brain` to resolve inside {expected}",
            observed=f"import failed (exit {res.returncode}): "
                     f"{detail[-1] if detail else 'no output'}",
            look_at=str(expected),
        )

    resolved_text = (res.stdout or "").strip()
    if not resolved_text:
        return _Check(
            name, False, why=why,
            expected=f"`import open_brain` to resolve inside {expected}",
            observed="the probe printed nothing, so the install location is unknown",
            look_at=str(expected),
        )
    resolved = Path(resolved_text)
    # Compare literally AND with symlinks resolved. An install reached through
    # a symlink is still the canonical install, and refusing a good save is
    # worse than the defect this check exists to catch. Both forms are strict
    # against a genuinely different checkout, so accepting either is safe.
    inside = resolved.is_relative_to(expected)
    if not inside:
        try:
            inside = resolved.resolve().is_relative_to(expected.resolve())
        except OSError:
            inside = False
    if not inside:
        return _Check(
            name, False, why=why,
            expected=f"`import open_brain` to resolve inside {expected}",
            observed=f"it resolves to {resolved} — a different checkout. A capture "
                     "would be written to that install's store, not this one.",
            look_at=str(resolved),
        )

    status_cmd = [sys.executable, "-m", "open_brain.cli", "status"]
    try:
        st = runner(status_cmd, capture_output=True, text=True, timeout=timeout, cwd=str(root))
    except Exception as err:  # noqa: BLE001
        return _Check(
            name, False, why=why,
            expected="`open_brain.cli status` to report a live database",
            observed=f"the status probe could not run — {type(err).__name__}: {err}",
            look_at=str(resolved),
        )
    if st.returncode != 0:
        detail = (st.stderr or st.stdout or "").strip().splitlines()
        return _Check(
            name, False, why=why,
            expected="`open_brain.cli status` to report a live database",
            observed=f"the store did not answer (exit {st.returncode}): "
                     f"{detail[-1] if detail else 'no output'}",
            look_at=str(resolved),
        )

    first = (st.stdout or "").strip().splitlines()
    return _Check(
        name, True, why=why,
        expected=f"`import open_brain` inside {expected}, and a live store",
        observed=f"resolved to {resolved}; {first[0] if first else 'store answered'}",
        look_at=str(resolved),
    )


def _atomic_write_bytes(target: Path, payload: bytes) -> None:
    """Replace ``target`` atomically, so an interrupted sync cannot truncate it."""
    tmp = target.with_name(target.name + ".sv-tmp")
    tmp.write_bytes(payload)
    os.replace(tmp, target)


def _reconcile_tracker(
    root: Path,
    desktop: Optional[Path] = None,
    *,
    apply: bool = True,
    allow_overwrite: bool = False,
) -> _Check:
    """(c) Make the two operational-tracker copies agree — RULING 3.

    The founder inverted the direction on 2026-08-05: the REPO copy is
    canonical, the Desktop copy is the mirror. So sv refreshes the Desktop
    copy from the repo.

    The Desktop copy has been the hand-edited one for months, which makes a
    blind repo -> Desktop copy a data-loss mechanism — the exact class of
    failure this programme exists to remove. So the sync is one-directional
    AND conditional: it runs only when the repo copy is the newer of the two
    (or they already agree). If the DESKTOP copy is newer it is left alone and
    the save is refused, because the only safe reading of "newer on the mirror"
    is "somebody edited the mirror and the edit is not in the repo yet".

    Which case fired is printed every time. ``apply=False`` reports the case
    without writing anything.
    """
    desk = _TRACKER_DESKTOP if desktop is None else desktop
    repo = root / _TRACKER_MIRROR_REL
    name = "tracker-copies-agree"
    why = (
        "the tracker is the first thing read after a compaction. If the two "
        "copies disagree, the next session's resume pointer depends on which "
        "file it happens to open."
    )
    expected = f"{repo} (canonical) and {desk} (mirror) byte-identical"
    mode = "" if apply else " [check only — nothing written]"

    def say(case: str, detail: str) -> None:
        print(f"  Tracker: {case}{mode} — {detail}")

    if not repo.exists() and not desk.exists():
        say("NEITHER-PRESENT", "no tracker on either side; not a CDSFL working tree")
        return _Check(
            name, True, why=why, expected=expected,
            observed="neither copy exists", look_at=str(repo),
        )

    if not repo.exists():
        say("CANONICAL-MISSING", f"the canonical copy is absent: {repo}")
        return _Check(
            name, False, why=why, expected=expected,
            observed=(
                f"the canonical repo copy is missing while the Desktop mirror "
                f"exists ({desk}). sv will NOT promote the mirror into the repo "
                "for you — that would commit unreviewed content. Copy it in and "
                "stage it yourself."
            ),
            look_at=str(repo),
        )

    repo_bytes = repo.read_bytes()

    if not desk.exists():
        if apply:
            desk.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_bytes(desk, repo_bytes)
            say("MIRROR-CREATED", f"wrote {len(repo_bytes)} bytes to {desk} from the canonical copy")
        else:
            say("MIRROR-MISSING", f"would create {desk} from the canonical copy")
        return _Check(
            name, True, why=why, expected=expected,
            observed=f"Desktop mirror was absent; {'created' if apply else 'would be created'} from {repo}",
            look_at=str(desk),
            wrote=str(desk) if apply else "",
        )

    try:
        desk_bytes = desk.read_bytes()
    except (PermissionError, OSError) as exc:
        # Content unreadable, metadata available — see _check_tracker_mirror. This
        # reconciler exists to REFRESH the Desktop copy FROM the repo, and the repo
        # copy is canonical by founder ruling 2026-08-06, so the read was only ever
        # a safety check against clobbering a newer Desktop edit. mtime answers that
        # question without reading a byte, and write() is permitted, so the save can
        # complete DETERMINISTICALLY instead of reporting an unknown.
        try:
            desk_mtime = desk.stat().st_mtime
            repo_mtime = repo.stat().st_mtime
        except (PermissionError, OSError):
            say("UNMEASURABLE", "cannot read or stat the Desktop tracker")
            return _Check(
                name, True, why=why, expected=expected,
                observed=(f"NOT COMPARED - {desk} is wholly inaccessible to this "
                          "process. The REPO copy is canonical and unaffected."),
                look_at=str(desk),
            )
        if desk_mtime > repo_mtime + 1:
            say("DESKTOP-NEWER", "refusing to overwrite a newer Desktop copy")
            return _Check(
                name, False, why=why, expected=expected,
                observed=(f"The Desktop copy is NEWER than the repo copy and its "
                          f"content cannot be read to merge. Resolve by hand: the "
                          f"repo copy is canonical, so confirm nothing is only on "
                          f"the Desktop before it is overwritten."),
                look_at=str(desk),
            )
        if apply:
            try:
                desk.write_bytes(repo_bytes)
            except (PermissionError, OSError) as werr:
                # RE-MEASURED 2026-08-26: stat(), read() AND overwrite all SUCCEED.
                # The 2026-08-25 observation -- create-new and stat permitted,
                # read and overwrite denied, 6 of 6 -- no longer holds. Access was
                # evidently granted in between.
                #
                # THE CLAIM WAS RECORDED IN FIVE PLACES and each lent authority to
                # the others, so it was repeated to the founder three times in one
                # day without being retested. A measurement of a permission is a
                # measurement of a MOMENT, not a property.
                #
                # This branch is retained deliberately. The write is ATTEMPTED every
                # save and this path runs only if it actually fails, so the code was
                # always right; only the comment asserted a permanent state.
                #
                # That is a definite, explainable state, not an unknown one, and the
                # save must report it as such and COMPLETE. The repo copy is canonical
                # by founder ruling 2026-08-06; a convenience mirror that cannot be
                # written is not a reason to fail a save of canonical state.
                say("MIRROR-NOT-WRITABLE",
                    f"cannot refresh the Desktop copy: {type(werr).__name__}")
                return _Check(
                    name, True, why=why, expected=expected,
                    observed=(f"NOT REFRESHED - {desk} cannot be overwritten by this "
                              f"process ({type(werr).__name__}). The Desktop copy is "
                              f"therefore STALE from this save onward. The repo copy "
                              f"is canonical and is fully saved. Re-sync by hand, or "
                              f"grant this process write access to ~/Desktop."),
                    look_at=str(desk),
                )
            say("REFRESHED", "Desktop copy rewritten from the canonical repo copy")
            return _Check(
                name, True, why=why, expected=expected,
                observed=(f"refreshed from the repo copy ({len(repo_bytes)} bytes); "
                          "content comparison unavailable, mtime confirmed the repo "
                          "copy was not older"),
                look_at=str(desk), wrote=str(desk),
            )
        return _Check(
            name, True, why=why, expected=expected,
            observed="would refresh the Desktop copy from the canonical repo copy",
            look_at=str(desk),
        )
    if desk_bytes == repo_bytes:
        say("IN-SYNC", "both copies are byte-identical")
        return _Check(
            name, True, why=why, expected=expected,
            observed=f"identical, {len(repo_bytes)} bytes", look_at=str(repo),
        )

    repo_mtime = _mtime(repo)
    desk_mtime = _mtime(desk)
    repo_lines = repo_bytes.decode("utf-8", "replace").splitlines()
    desk_lines = desk_bytes.decode("utf-8", "replace").splitlines()
    diff = _tracker_diff(repo_lines, desk_lines, "repo (canonical)", "Desktop (mirror)")
    only_repo = sum(1 for line in diff if line.startswith("-"))
    only_desk = sum(1 for line in diff if line.startswith("+"))
    stat = (
        f"{len(repo_lines)} lines / {len(repo_bytes)} bytes in the repo copy "
        f"(modified {repo_mtime:%Y-%m-%d %H:%M:%S}) vs "
        f"{len(desk_lines)} lines / {len(desk_bytes)} bytes on the Desktop "
        f"(modified {desk_mtime:%Y-%m-%d %H:%M:%S}); "
        f"{only_repo} line(s) only in the repo, {only_desk} only on the Desktop"
    )

    # The ruling authorises a sync only when the repo copy is NEWER, or when the
    # two already agree. A tie — different content, identical mtime — is neither.
    # Nothing there shows which side carries the later edit, so overwriting on a
    # tie would be a guess with data loss as its downside. Ties refuse.
    repo_is_newer = repo_mtime > desk_mtime
    tie = repo_mtime == desk_mtime

    if not repo_is_newer and not allow_overwrite:
        case = "REFUSED-SAME-MTIME" if tie else "REFUSED-DESKTOP-NEWER"
        headline = (
            "THE TWO COPIES DIFFER BUT CARRY THE SAME MODIFICATION TIME."
            if tie else
            "THE DESKTOP COPY IS NEWER THAN THE CANONICAL REPO COPY."
        )
        reason = (
            [
                "Neither side can be shown to hold the later edit, so sv will not",
                "guess. Compare them and copy the winning content into the repo.",
            ] if tie else [
                "Refusing to overwrite it: the likeliest explanation is a hand edit",
                "that has not been carried into the repo, and copying over it would",
                "destroy that edit.",
            ]
        )
        say(case, "the Desktop copy was NOT touched")
        _tracker_warn([
            headline,
            *reason,
            f"Canonical (repo): {repo}",
            f"  {len(repo_lines)} lines, {len(repo_bytes)} bytes, modified {repo_mtime:%Y-%m-%d %H:%M:%S}",
            f"Mirror (Desktop): {desk}",
            f"  {len(desk_lines)} lines, {len(desk_bytes)} bytes, modified {desk_mtime:%Y-%m-%d %H:%M:%S}",
            f"Differing lines: {only_repo} only in the repo, {only_desk} only on the Desktop.",
            *([f"  {line}" for line in diff[:10]]),
            *([f"  … and {len(diff) - 10} more differing line(s)"] if len(diff) > 10 else []),
            "TO FIX: carry the Desktop content into the repo copy and stage it, or —",
            f"if the Desktop content is genuinely to be discarded — re-run with "
            f"{_FLAG_OVERWRITE_DESKTOP}.",
        ])
        return _Check(
            name, False, why=why, expected=expected,
            observed=(
                "they differ and the repo copy is NOT the newer one "
                + ("(both carry the same modification time)" if tie
                   else "(the DESKTOP copy is newer)")
                + ", so sv refused to overwrite the Desktop copy. " + stat
            ),
            look_at=f"diff '{repo}' '{desk}'",
            override=_FLAG_OVERWRITE_DESKTOP,
        )

    if not repo_is_newer:
        # Explicitly overridden. Keep the discarded content recoverable — an
        # override is a decision to proceed, not a decision to be unable to
        # change your mind.
        which = "same-mtime" if tie else "newer"
        written = ""
        if apply:
            backup = desk.with_name(
                f"{desk.name}.superseded-{datetime.now():%Y%m%dT%H%M%S}"
            )
            _atomic_write_bytes(backup, desk_bytes)
            _atomic_write_bytes(desk, repo_bytes)
            written = f"{desk} (previous contents kept at {backup})"
            say(
                "OVERWROTE-DESKTOP",
                f"{_FLAG_OVERWRITE_DESKTOP} was passed; the {which} Desktop copy was "
                f"replaced from the repo. Previous contents saved to {backup}",
            )
        else:
            say(
                "WOULD-OVERWRITE-DESKTOP",
                f"{_FLAG_OVERWRITE_DESKTOP} was passed; a real run would replace the "
                f"{which} Desktop copy (keeping a .superseded- backup)",
            )
        return _Check(
            name, True, why=why, expected=expected,
            observed=f"the {which} Desktop copy was overwritten under "
                     f"{_FLAG_OVERWRITE_DESKTOP}. " + stat,
            look_at=str(desk),
            wrote=written,
        )

    # The repo copy is newer, so refreshing the mirror is the ruling-3 direction
    # and needs no override. It is still an OVERWRITE of a file a human edits by
    # hand, and mtime ordering is a weak guard: `git checkout`, `git pull`,
    # `git stash`, or any agent editing the repo tracker makes the repo copy
    # newer without the Desktop copy having been carried across. This branch
    # shipped without the `.superseded-` backup its sibling three lines above
    # takes, so a hand edit could be destroyed while the run reported success —
    # a data-loss path introduced by the very change meant to stop the two
    # copies drifting. Back it up here too. Same pattern, same naming, so a
    # recovering operator finds the backup in the same place either way.
    if apply:
        backup = desk.with_name(
            f"{desk.name}.superseded-{datetime.now():%Y%m%dT%H%M%S}"
        )
        _atomic_write_bytes(backup, desk_bytes)
        _atomic_write_bytes(desk, repo_bytes)
        say(
            "MIRROR-REFRESHED",
            f"the repo copy is newer; {desk} was refreshed from it. "
            f"Previous contents saved to {backup}",
        )
    else:
        say("MIRROR-STALE", f"the repo copy is newer; a real run would refresh {desk} "
                            f"(keeping a .superseded- backup)")
    return _Check(
        name, True, why=why, expected=expected,
        observed=f"the repo copy was the newer one; the Desktop mirror was "
                 f"{'refreshed, with a .superseded- backup of the previous contents'
                    if apply else 'left alone (check only)'}. " + stat,
        look_at=str(desk),
        wrote=str(desk) if apply else "",
    )


def _alert_field(label: str, text: str) -> list[str]:
    """Wrap one labelled field of the alert so it stays readable in a terminal."""
    lead = f"     {label:<14}"
    body = textwrap.wrap(text, width=72) or [""]
    return [lead + body[0]] + [" " * len(lead) + line for line in body[1:]]


def _print_save_alert(
    failed: list[_Check], total: int, refusing: bool, checking: bool = False,
    wrote: Optional[list[str]] = None,
) -> None:
    """The RULING 4 alert. Loud, on stderr, and actionable.

    It names the check, what it expected, what it observed, where to look and
    which flag overrides it — because "something is missing" gives nobody
    anything to fix.
    """
    # See _tracker_warn: order the alert against the evidence it cites, or a
    # redirected run prints the verdict before the measurements.
    sys.stdout.flush()
    bar = "#" * 74
    err = sys.stderr
    print(bar, file=err)
    if checking:
        # A rehearsal neither refuses nor allows anything: it measures. Saying
        # "REFUSED" here would report an event that did not happen.
        print(f"  --check-save: THE SAVE IS INCOMPLETE — {len(failed)} of {total} "
              "checks FAILED", file=err)
        print("  This is a report. Nothing was written and nothing was committed.",
              file=err)
    elif refusing:
        print(f"  sv REFUSED TO SAVE — {len(failed)} of {total} completeness checks FAILED",
              file=err)
        # Report what the pre-flight actually did. The tracker reconciliation
        # (ruling 3) runs inside the pre-flight and can rewrite the Desktop
        # mirror before a later check refuses, so a blanket "nothing was
        # rewritten" would be a claim this function never checked.
        if wrote:
            print("  NOTHING WAS COMMITTED and no file in the repository was rewritten,",
                  file=err)
            print(f"  but the pre-flight DID write {len(wrote)} file(s) before refusing:",
                  file=err)
            for path in wrote:
                print(f"    {path}", file=err)
        else:
            print("  NOTHING WAS COMMITTED AND NO DOCUMENT WAS REWRITTEN.", file=err)
    else:
        print(f"  INCOMPLETE SAVE ALLOWED — {len(failed)} of {total} completeness checks FAILED",
              file=err)
        print(f"  {_FLAG_ALLOW_INCOMPLETE} was passed, so these are warnings, not refusals.",
              file=err)
    print(bar, file=err)
    for check in failed:
        print("", file=err)
        print(f"  [FAIL] {check.name}", file=err)
        for line in _alert_field("WHY IT FIRED:", check.why):
            print(line, file=err)
        for line in _alert_field("EXPECTED:", check.expected):
            print(line, file=err)
        for line in _alert_field("OBSERVED:", check.observed):
            print(line, file=err)
        if check.look_at:
            for line in _alert_field("LOOK AT:", check.look_at):
                print(line, file=err)
        for line in _alert_field("OVERRIDE:", check.override):
            print(line, file=err)
    print("", file=err)
    print("  An alert is an opportunity, not an obstacle: it says a step of the save", file=err)
    print("  did not happen. Fix the step and re-run. If a check fired on a save you", file=err)
    print("  know IS complete, the CHECK is the defect — repair it in", file=err)
    print("  scripts/cdsfl_sv.py rather than reaching for the override again.", file=err)
    print(bar, file=err)
    err.flush()


def _preflight_completeness(
    root: Path,
    *,
    apply: bool = True,
    allow_incomplete: bool = False,
    allow_overwrite_desktop: bool = False,
    checking: bool = False,
    mem_dir: Optional[Path] = None,
    desktop: Optional[Path] = None,
    runner: Callable[..., Any] = subprocess.run,
) -> bool:
    """Run every completeness check and report. Returns True if all passed.

    ``apply=False`` makes the whole pass read-only: the tracker case is
    reported but no file is written anywhere. ``checking=True`` additionally
    says the run is a rehearsal, so the alert reports the measurement instead
    of announcing a refusal that did not happen.
    """
    print()
    print("Save-completeness pre-flight (founder rulings 3, 4 and 7, 2026-08-05):")

    audit = _audit_memory_index(_MEMORY_DIR if mem_dir is None else mem_dir)

    checks = [
        _check_memory_updated(root, mem_dir=mem_dir),
        _check_open_brain(root, runner=runner),
        _reconcile_tracker(
            root, desktop=desktop, apply=apply,
            allow_overwrite=allow_overwrite_desktop,
        ),
        _check_memory_index_size(audit),
    ]

    _print_memory_index_report(audit)
    print()
    for check in checks:
        print(f"  [{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.observed}")

    failed = [c for c in checks if not c.passed]
    if failed:
        _print_save_alert(
            failed, len(checks),
            refusing=not allow_incomplete, checking=checking,
            wrote=[c.wrote for c in checks if c.wrote],
        )
    else:
        print(f"  All {len(checks)} completeness checks passed.")
    return not failed


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
    parser.add_argument(
        "--check-save",
        action="store_true",
        help="Run the save-completeness checks, print the report, and exit. "
             "Writes nothing and commits nothing. Exit 0 if the save is "
             "complete, 1 if any check failed. Reports the measurement, so "
             "--allow-incomplete-save does not change the exit code.",
    )
    parser.add_argument(
        _FLAG_ALLOW_INCOMPLETE,
        action="store_true",
        help="Commit even though the save is incomplete. The alert is still "
             "printed; the failures become warnings. For deliberate omissions.",
    )
    parser.add_argument(
        _FLAG_OVERWRITE_DESKTOP,
        action="store_true",
        help="Refresh the Desktop operational-tracker copy from the repo even "
             "when the Desktop copy is NEWER. Discards the newer Desktop "
             "content (a .superseded- backup is kept beside it).",
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

    # 0. Save-completeness pre-flight (RULINGS 3, 4, 7 — founder, 2026-08-05).
    #    Runs BEFORE anything is written, so a refusal leaves the tree exactly
    #    as it found it. --check-save is the read-only rehearsal; --dry-run
    #    skips it entirely, because a dry run cannot produce the incomplete
    #    commit the checks exist to prevent.
    if args.check_save or (args.commit and not args.dry_run):
        complete = _preflight_completeness(
            root,
            apply=not args.check_save,
            checking=args.check_save,
            allow_incomplete=args.allow_incomplete_save,
            allow_overwrite_desktop=args.overwrite_newer_desktop_tracker,
        )
        if args.check_save:
            print()
            print("--check-save: nothing was written and nothing was committed.")
            sys.exit(0 if complete else 1)
        if not complete and not args.allow_incomplete_save:
            sys.exit(1)

    print()

    # 1. Generate CURRENT_STATE.md
    #    will_commit tells the generator this file is about to be swept into an
    #    sv commit, so its git block must label itself as a pre-commit snapshot.
    will_commit = args.commit and not args.dry_run
    state_content = generate_current_state(gs, tests, exp, root, will_commit=will_commit)
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

    # Timestamps are written AFTER the body updates below, so they can
    # report whether the body actually changed. Stamping first is what
    # made the date a claim the file could not support.

    # 3. Update experiment summary in ONBOARDING.md (skips if manual content present)
    #    REPAIR S4: record what the update function ACTUALLY returned so the
    #    closing summary can report it, instead of re-asserting success from
    #    the loop condition.
    preserved_note = "manual content preserved, auto-block NOT regenerated"
    if exp:
        if update_onboarding_experiment(onboarding, exp, root, dry_run=args.dry_run):
            print(f"Updated experiment summary: {onboarding}")
            onboarding_status = "regenerated"
        else:
            # Distinguish "unchanged" from "preserved manual content"
            onboarding_status = "unchanged"
            if onboarding.exists() and _ONBOARDING_MARKER_START in onboarding.read_text():
                text = onboarding.read_text()
                if _has_manual_content(text, _ONBOARDING_MARKER_START,
                                       _ONBOARDING_MARKER_END, _ONBOARDING_PLACEHOLDER):
                    print(f"Preserved manual content: {onboarding}")
                    onboarding_status = preserved_note
                else:
                    print(f"Experiment summary unchanged: {onboarding}")
            else:
                print(f"Experiment summary unchanged: {onboarding}")
    else:
        print("No experiment data — skipping ONBOARDING.md experiment update")
        onboarding_status = "not attempted (no experiment data found)"

    # 4. Update pending work in RECOVERY.md (skips if manual content present)
    if update_recovery_pending(recovery, exp, gs, tests, root, dry_run=args.dry_run):
        print(f"Updated pending work: {recovery}")
        recovery_status = "regenerated"
    else:
        recovery_status = "unchanged"
        if recovery.exists() and _RECOVERY_MARKER_START in recovery.read_text():
            text = recovery.read_text()
            if _has_manual_content(text, _RECOVERY_MARKER_START,
                                   _RECOVERY_MARKER_END, _RECOVERY_PLACEHOLDER):
                print(f"Preserved manual content: {recovery}")
                recovery_status = preserved_note
            else:
                print(f"Pending work unchanged: {recovery}")
        else:
            print(f"Pending work unchanged: {recovery}")

    # 5. Recount the public memory-exclusion ledger from the private memory
    #    directory. This is mechanical accounting, not qualitative editing, and
    #    belongs in sv so a new memory file cannot repeatedly leave the counts
    #    stale until a test catches the author's missed manual bump.
    try:
        if _update_memory_exclusions_ledger(root, dry_run=args.dry_run):
            verb = "Would update" if args.dry_run else "Updated"
            print(f"{verb} memory-exclusions ledger: {root / 'resources' / 'MEMORY_EXCLUSIONS.md'}")
    except MemoryUnreadable as exc:
        # LOUD, and explicitly not a pass. The ledger keeps its previous counts
        # AND its previous "counted <date>" stamp, because restamping would
        # assert a freshness this run cannot support.
        print()
        print("  MEMORY LEDGER NOT RECOUNTED — the directory is unreadable:")
        print(f"    {exc}")
        print("    Counts and the 'counted' date are LEFT AS THEY WERE. This is a")
        print("    failed measurement, not a clean bill of health.")
        print()

    # 6. NOW stamp the two documents, knowing whether their bodies changed.
    #    A stamp written before this point could only ever record when sv ran.
    for doc, status in ((onboarding, onboarding_status), (recovery, recovery_status)):
        regenerated = status == "regenerated"
        if update_timestamp(doc, dry_run=args.dry_run, body_regenerated=regenerated):
            print(f"Updated timestamp: {doc}"
                  + ("" if regenerated else "  [flagged: body preserved, so the "
                                            "stamp says so rather than implying freshness]"))

    # Summary
    print()
    if args.dry_run:
        bar = "=" * 74
        print(bar)
        print("DRY RUN — NOTHING WAS WRITTEN TO DISK.")
        print("Every line below describes what WOULD change on a real run.")
        print(bar)
        print("State save dry run complete — no files written.")
    elif args.commit:
        # NOT "complete": the commit and push have not run yet, and every line
        # below is a PRE-COMMIT reading. Printing "State save complete." here
        # and then doing more work is the same defect as reporting the remote
        # state from before a push -- a before-state under a final-sounding
        # heading. Founder, 2026-08-26: sv must finish with "zero errors and
        # zero ambiguity about the completed sv state".
        print("State files written. Commit and push STILL TO RUN — "
              "the lines below are the state BEFORE that.")
    else:
        print("State save complete.")
    print(f"  Branch: {gs['branch']} @ {gs['last_hash']}")
    # A COLLECTION count, never a pass count, and the label must say so. This
    # line has printed a bare number since the script was written: a red suite
    # and a green one produce the same figure, and that figure is then carried
    # into docs/CURRENT_STATE.md where a reader takes it for health. Found by
    # the 2026-08-08 gate, which noted it is "the house failure mode" — a
    # failure rendering as a confident success, in the state file.
    print(f"  Tests: {tests if tests else 'unknown'} COLLECTED "
          f"(collection count only — says NOTHING about pass/fail. "
          f"For health run: python3 -m pytest bench/tests/ -q --netguard-strict)")
    print(f"  Latest exp: {exp['name'] if exp else 'none'}")
    print(f"  Working tree: {'clean' if gs['clean'] else 'DIRTY'}")
    print(f"  Remote{' BEFORE this sv' if args.commit and not args.dry_run else ''}: "
          f"{gs['remote_sync']}")
    print(f"  ONBOARDING.md: {onboarding_status}")
    print(f"  RECOVERY.md: {recovery_status}")

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
                _print_final_state(root, push=args.push)
                # REPAIR S3: the sv spec names the Open Brain session summary
                # FIRST. Only on a successful commit, never under --dry-run
                # (this whole branch is gated on `not args.dry_run`), and it
                # can only warn — never break a commit that already landed.
                _open_brain_capture(
                    _open_brain_summary(
                        msg, gs, tests, exp, root, pushed=args.push,
                    ),
                    root=root,
                )
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
