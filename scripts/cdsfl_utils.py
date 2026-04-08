"""Shared utilities for CDSFL automation scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def repo_root() -> Path:
    """Return the repository root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def timestamp_now() -> str:
    """Return formatted timestamp in project convention."""
    now = datetime.now()
    day = now.day
    month = now.strftime("%B")
    year = now.year
    time_str = now.strftime("%H:%M")
    tz = now.astimezone().strftime("%Z")
    return f"{day} {month} {year} {time_str} {tz}"


def timestamp_iso() -> str:
    """Return ISO 8601 timestamp."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _run_git(*args: str, cwd: Optional[Path] = None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd or repo_root(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def git_state() -> dict[str, Any]:
    """Collect current git state."""
    root = repo_root()

    branch = _run_git("branch", "--show-current", cwd=root)
    status_raw = _run_git("status", "--porcelain", cwd=root)
    uncommitted = [line.strip() for line in status_raw.splitlines() if line.strip()]
    is_clean = len(uncommitted) == 0

    last_log = _run_git("log", "--oneline", "-1", cwd=root)
    last_hash = last_log.split()[0] if last_log else "unknown"
    last_msg = " ".join(last_log.split()[1:]) if last_log else "unknown"
    last_date = _run_git("log", "-1", "--format=%ci", cwd=root)

    recent_log = _run_git("log", "--oneline", "-10", cwd=root).splitlines()

    # Remote sync
    _run_git("fetch", "--quiet", cwd=root)
    ahead = _run_git("rev-list", "--count", "origin/main..HEAD", cwd=root)
    behind = _run_git("rev-list", "--count", "HEAD..origin/main", cwd=root)
    ahead_n = int(ahead) if ahead.isdigit() else 0
    behind_n = int(behind) if behind.isdigit() else 0
    if ahead_n == 0 and behind_n == 0:
        remote_sync = "up to date"
    elif ahead_n > 0 and behind_n > 0:
        remote_sync = f"diverged (ahead {ahead_n}, behind {behind_n})"
    elif ahead_n > 0:
        remote_sync = f"ahead by {ahead_n}"
    else:
        remote_sync = f"behind by {behind_n}"

    return {
        "branch": branch,
        "clean": is_clean,
        "uncommitted": uncommitted,
        "last_hash": last_hash,
        "last_message": last_msg,
        "last_date": last_date,
        "recent_log": recent_log,
        "remote_sync": remote_sync,
    }


def test_count() -> Optional[int]:
    """Count tests via pytest collection. Returns None on failure."""
    root = repo_root()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "bench/tests/", "--co", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Last meaningful line is "N tests collected"
        for line in reversed(result.stdout.splitlines()):
            m = re.search(r"(\d+)\s+tests?\s+collected", line)
            if m:
                return int(m.group(1))
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def latest_experiment() -> Optional[dict[str, Any]]:
    """Find and parse the latest experiment from bench/logs/."""
    logs_dir = repo_root() / "bench" / "logs"
    if not logs_dir.exists():
        return None

    # Find exp{N}_* directories
    exp_dirs: list[tuple[int, Path]] = []
    for d in logs_dir.iterdir():
        if d.is_dir():
            m = re.match(r"exp(\d+)_", d.name)
            if m:
                exp_dirs.append((int(m.group(1)), d))

    if not exp_dirs:
        return None

    # Get highest experiment number, then latest timestamp for that number
    max_n = max(n for n, _ in exp_dirs)
    candidates = sorted(
        [d for n, d in exp_dirs if n == max_n],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for exp_dir in candidates:
        # Look for report JSON
        report_files = list(exp_dir.glob("exp*_report.json"))
        if not report_files:
            continue
        try:
            data = json.loads(report_files[0].read_text())
            comp = data.get("completion_signal", {})
            return {
                "number": max_n,
                "name": data.get("experiment", f"exp{max_n}"),
                "status": comp.get("status", "UNKNOWN"),
                "reason": comp.get("reason", ""),
                "total_rounds": data.get("total_rounds", 0),
                "total_findings": data.get("total_findings", 0),
                "gamma": data.get("gamma", 0.0),
                "models": data.get("models", []),
                "target": data.get("target_file", ""),
                "topology": data.get("topology", ""),
                "timestamp": comp.get("timestamp", ""),
                "per_model": comp.get("per_model_findings", {}),
                "log_dir": str(exp_dir),
            }
        except (json.JSONDecodeError, OSError):
            continue

    return None


def read_section(filepath: Path, start_marker: str, end_marker: str = "") -> str:
    """Extract text between markdown section markers.

    start_marker: text to search for (e.g. '## Current State')
    end_marker: text marking end of section (e.g. next '## ').
                If empty, reads to end of file.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        return ""

    start_idx = text.find(start_marker)
    if start_idx == -1:
        return ""

    content = text[start_idx + len(start_marker):]

    if end_marker:
        end_idx = content.find(end_marker)
        if end_idx != -1:
            content = content[:end_idx]

    return content.strip()


def check_file_references(md_path: Path) -> list[dict[str, Any]]:
    """Check a markdown file for broken file path references."""
    broken = []
    try:
        lines = md_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return broken

    root = repo_root()

    for i, line in enumerate(lines, 1):
        # Match backtick-enclosed paths and markdown link targets
        for pattern in [r"`([^`]+/[^`]+)`", r"\]\(([^)]+/[^)]+)\)"]:
            for m in re.finditer(pattern, line):
                ref = m.group(1)
                # Skip URLs
                if ref.startswith(("http://", "https://", "mailto:")):
                    continue
                # Expand ~ paths
                check_path = Path(ref.replace("~", str(Path.home())))
                if not check_path.is_absolute():
                    check_path = root / check_path
                if not check_path.exists():
                    broken.append({
                        "file": str(md_path),
                        "line": i,
                        "reference": ref,
                    })

    return broken


def source_env() -> None:
    """Load .env file into environment (mirrors runner_core.py)."""
    env_file = repo_root() / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            os.environ.setdefault(key, value)
