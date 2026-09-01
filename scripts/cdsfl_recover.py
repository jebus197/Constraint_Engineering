#!/usr/bin/env python3
"""CDSFL Recovery Script — prints structured project state for CC1 instances.

Usage: python3 scripts/cdsfl_recover.py [--full]

  --full    Include test count (runs pytest, adds ~10s)

Designed to be fast and read-only. Outputs structured state summary
that a new CC1 instance can parse to rebuild working context.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Optional

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

# ── Loud-failure convention ───────────────────────────────────────────────────
# Every section below distinguishes THREE different things, two of which used
# to render identically:
#   "   (...)"  = a real absence. The thing genuinely is not there.
#   "!! ..."    = a LOOKUP FAILED. The answer is UNKNOWN, not empty.
#   ">> ..."    = a LIVE thing was found (a running process). Not a failure —
#                 an alert, and kept distinct from "!!" so the failure marker
#                 keeps meaning exactly one thing.
# A recovering agent reads this output as fact, so a broken probe must never
# render as a confident "nothing to report".

# The pending-work block markers that scripts/cdsfl_sv.py actually writes into
# resources/RECOVERY.md. The previous probe searched for "NEXT STEPS:" /
# "ARCHITECTURAL GAPS", both of which were deleted from RECOVERY.md in April
# 2026 (commit f5e73ab) — so this section printed "(No pending work section
# found)" for 113 days while the block was 1,575 lines long.
PENDING_START = "<!-- SV:PENDING_START -->"
PENDING_END = "<!-- SV:PENDING_END -->"

# The cap on the marked pending-work region. It is stated in the output;
# nothing is truncated silently.
PENDING_MAX_LINES = 80

# scripts/cdsfl_sv.py REGENERATES the marked region and nothing else, so every
# hand-written state block lives ABOVE the start marker and this script never
# read a line of it. Measured 2026-08-05: the newest heading inside the markers
# was dated 2026-06-03 while the file's own line 104 carried a 2026-08-05
# correction and line 129 a "READ THIS FIRST" session state — 63 days and seven
# convergences that a recovering agent was never shown. The markers are NOT
# moved (sv owns that region; relocating the start marker above hand-written
# blocks would put them in sv's overwrite path, which is a founder decision).
# The fix is here, on the reader side: read the head too, label it, and let the
# dates speak.
RECOVERY_HEAD_MAX_LINES = 200

# ── Region provenance: dates that were PARSED, never recency that was assumed ─
# The cap note used to end "Newest block is written first, so the above is the
# most recent." True of the marked region, false about the document, and stated
# as fact either way. Everything below reports only what it actually read.
_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}
_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
_LONG_DATE = re.compile(
    r"\b(\d{1,2})\s+(" + "|".join(_MONTHS) + r")\s+(\d{4})\b", re.IGNORECASE
)


def _clip(text: str, limit: int = 96) -> str:
    """Collapse whitespace and truncate VISIBLY (RECOVERY.md has 300-char headings)."""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _heading_date(text: str) -> Optional[date]:
    """Newest date parsed out of ONE heading line, or None if none parses.

    Two formats: 2026-08-05 and '5 August 2026'. A heading this does not
    recognise is COUNTED as undated and the count is printed, because
    "no heading carries a date" and "the parser missed them all" must not
    render identically — that is this script's whole failure class.
    """
    found: list[date] = []
    for y, m, d in _ISO_DATE.findall(text):
        try:
            found.append(date(int(y), int(m), int(d)))
        except ValueError:
            continue
    for day, name, y in _LONG_DATE.findall(text):
        try:
            found.append(date(int(y), _MONTHS[name.lower()], int(day)))
        except ValueError:
            continue
    return max(found) if found else None


def _scan_headings(
    lines: list[str], first_line_no: int
) -> list[tuple[int, str, Optional[date]]]:
    """(file line number, heading text, parsed date or None) for each '## ' heading."""
    return [
        (first_line_no + i, line.strip(), _heading_date(line))
        for i, line in enumerate(lines)
        if line.startswith("## ")
    ]


def _provenance_lines(
    path: Path,
    region_desc: str,
    first_line: int,
    last_line: int,
    headings: list[tuple[int, str, Optional[date]]],
) -> list[str]:
    """State the line range read, and the newest date actually parsed in it."""
    dated = [h for h in headings if h[2] is not None]
    out = [
        "",
        f"  [READ: {path}",
        f"   lines {first_line}-{last_line} — {region_desc}.",
        f"   {len(headings)} '##' heading(s) scanned; {len(dated)} carried a parseable date",
        "   (formats recognised: 2026-08-05, 5 August 2026).",
    ]
    if dated:
        line_no, text, when = max(dated, key=lambda h: h[2])
        out.append(f"   Newest date parsed in this region: {when.isoformat()}, line {line_no}:")
        out.append(f"     {_clip(text, 92)}")
    else:
        out.append("   No heading in this region carried a parseable date.")
    out.append("   This reports what was read. It asserts nothing about which region of")
    out.append("   the file is newest overall — compare the dates each region prints.]")
    return out


def _mtime_iso(path: Path) -> str:
    """Local-timezone ISO mtime, or a loud marker if it cannot be read."""
    try:
        return (
            datetime.fromtimestamp(path.stat().st_mtime)
            .astimezone()
            .isoformat(timespec="seconds")
        )
    except OSError as exc:
        return f"!! mtime unreadable ({exc})"


def first_read_lines(root: Path) -> list[str]:
    """The FIRST READ section: the operational tracker and the live work queue.

    Named FIRST READ after compaction by ~/.claude/CLAUDE.md
    (operational-tracker-compaction-order) and by RECOVERY.md's own Minimum
    Recovery section. It carries the resume pointer, which nothing this script
    computes can supply.
    """
    # Founder ruling, 2026-08-05: the REPO copy is CANONICAL and the Desktop
    # copy is the mirror. The direction was inverted because the tracker
    # carries the recovery path, and an unversioned file on one machine's
    # Desktop is a single point of failure. This block named the Desktop copy
    # canonical until 2026-08-06 — the label is corrected here rather than
    # left to disagree with .claude/CLAUDE.md, RECOVERY.md, ~/.claude/CLAUDE.md
    # and cdsfl_sv.py, all of which already carry the ruling.
    targets = [
        (
            root / "experimental_notes" / "CDSFL_Agent_Operational_Plan.md",
            "OPERATIONAL TRACKER (canonical) — resume pointer + per-experiment matrix",
        ),
        (
            Path.home() / "Desktop" / "CDSFL_Agent_Operational_Plan.md",
            "Desktop mirror of the above (byte-identical; convenient, not the authority)",
        ),
        (
            root / "experimental_notes" / "OUTSTANDING_QUEUE_to_BR2.md",
            "live work queue to Bench Run 2",
        ),
    ]
    lines = [
        "  Read these BEFORE anything below. This script reports measured state;",
        "  the tracker names the exact resume point, which no section here does.",
        "",
    ]
    for path, desc in targets:
        if path.exists():
            lines.append(f"     {path}")
            lines.append(f"        {desc}")
            lines.append(f"        last modified {_mtime_iso(path)}")
        else:
            lines.append(f"  !! MISSING: {path}")
            lines.append(f"        {desc} — this file is REQUIRED reading and is absent")
    return lines


def recovery_head_lines(
    recovery_path: Path, max_lines: int = RECOVERY_HEAD_MAX_LINES
) -> list[str]:
    """Everything in RECOVERY.md ABOVE the sv pending-work start marker.

    This region is hand-written and is where the current state blocks live;
    sv regenerates only the marked region below it. Nothing here moves a
    marker or writes to the file — it is a read the script was not doing.
    """
    if not recovery_path.exists():
        return [
            f"  !! LOOKUP FAILED: {recovery_path} does not exist.",
            "     The current-state blocks are UNKNOWN, not absent.",
        ]
    try:
        text = recovery_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            f"  !! LOOKUP FAILED: cannot read {recovery_path} ({exc}).",
            "     The current-state blocks are UNKNOWN, not absent.",
        ]

    start = text.find(PENDING_START)
    if start == -1:
        return [
            f"  !! LOOKUP FAILED: marker {PENDING_START} not found in "
            f"{recovery_path},",
            "     so the region above it cannot be delimited. The current-state",
            "     blocks are UNKNOWN, not absent — read the file directly.",
        ]

    marker_line = text.count("\n", 0, start) + 1
    head = text[:start].splitlines()
    while head and not head[-1].strip():
        head.pop()
    if not head:
        return [
            f"     (nothing above {PENDING_START} — the file opens with the marked",
            "      block. This is a real absence, not a failed lookup.)",
        ]

    headings = _scan_headings(head, 1)
    out = [f"  {line}" for line in head[:max_lines]]
    if len(head) > max_lines:
        withheld = len(head) - max_lines
        out.extend([
            "",
            f"  [CAP: showing the first {max_lines} of {len(head)} lines above the",
            f"   start marker (line {marker_line}); {withheld} lines withheld.",
            "   Every withheld '##' heading, so no block is dropped in silence:",
        ])
        for line_no, htext, when in headings:
            if line_no > max_lines:
                stamp = when.isoformat() if when else "no date  "
                out.append(f"     line {line_no:>5}  {stamp}  {_clip(htext, 78)}")
        out.append(f"   Full text: {recovery_path}]")

    out.extend(_provenance_lines(
        recovery_path,
        f"everything above {PENDING_START} (line {marker_line})",
        1,
        len(head),
        headings,
    ))
    return out


def pending_work_lines(
    recovery_path: Path, max_lines: int = PENDING_MAX_LINES
) -> list[str]:
    """The PENDING WORK section, read between the markers the writer emits.

    Returns formatted lines. A failed lookup is prefixed '!!' and says the
    answer is UNKNOWN; a genuinely empty block says so in different words.
    This region is only PART of RECOVERY.md — see recovery_head_lines().
    """
    if not recovery_path.exists():
        return [
            f"  !! LOOKUP FAILED: {recovery_path} does not exist.",
            "     Pending work is UNKNOWN, not absent.",
        ]
    try:
        text = recovery_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            f"  !! LOOKUP FAILED: cannot read {recovery_path} ({exc}).",
            "     Pending work is UNKNOWN, not absent.",
        ]

    start = text.find(PENDING_START)
    end = text.find(PENDING_END)
    if start == -1 or end == -1 or end < start:
        return [
            f"  !! LOOKUP FAILED: markers {PENDING_START} / {PENDING_END} "
            f"not found in {recovery_path}.",
            "     Those markers are written by scripts/cdsfl_sv.py. Pending work is",
            "     UNKNOWN, not absent — read the file directly.",
        ]

    raw = text[start + len(PENDING_START):end]
    body = raw.strip()
    if not body:
        return [
            "     (markers present, block empty — no pending work was recorded",
            "      at the last save. This is a real absence, not a failed lookup.)",
        ]

    # File line number of the first body line, measured, not assumed: the
    # marker line plus whatever whitespace .strip() removed from the front.
    lead = len(raw) - len(raw.lstrip())
    body_first = text.count("\n", 0, start + len(PENDING_START) + lead) + 1

    lines = body.splitlines()
    out = [f"  {line}" for line in lines[:max_lines]]
    if len(lines) > max_lines:
        withheld = len(lines) - max_lines
        out.extend([
            "",
            f"  [CAP: showing the first {max_lines} of {len(lines)} lines between the",
            f"   markers; {withheld} lines withheld. Full text: {recovery_path}]",
        ])

    out.extend(_provenance_lines(
        recovery_path,
        f"between {PENDING_START} (line {text.count(chr(10), 0, start) + 1})\n"
        f"   and {PENDING_END} (line {text.count(chr(10), 0, end) + 1}), the region "
        "scripts/cdsfl_sv.py regenerates",
        body_first,
        body_first + len(lines) - 1,
        _scan_headings(lines, body_first),
    ))
    return out


def experiment_absence_lines(logs_dir: Path) -> list[str]:
    """Explain WHY latest_experiment() returned nothing.

    "(No experiment logs found)" was printed while 109 exp<N>_* directories
    existed — a parser failure rendered as a statement about the project.
    """
    if not logs_dir.exists():
        return [
            f"     (no {logs_dir} directory — no experiment has run in this checkout)",
        ]
    try:
        exp_dirs = [
            d for d in logs_dir.iterdir()
            if d.is_dir() and re.match(r"exp\d+", d.name)
        ]
    except OSError as exc:
        return [
            f"  !! LOOKUP FAILED: cannot list {logs_dir} ({exc}).",
            "     The latest experiment is UNKNOWN, not absent.",
        ]
    if not exp_dirs:
        return [
            f"     (no exp<N>_* directories under {logs_dir} — no experiment logs)",
        ]
    return [
        f"  !! LOOKUP FAILED: {len(exp_dirs)} exp<N>_* directories exist under",
        f"     {logs_dir}, but latest_experiment() (scripts/cdsfl_utils.py) parsed",
        "     none of them. The latest experiment is UNKNOWN, not absent —",
        "     inspect the newest directory by hand.",
    ]


def _last_number(seq: Any) -> Optional[float]:
    """Last element of a numeric series, or None if that is not what it is."""
    if not isinstance(seq, list) or not seq:
        return None
    value = seq[-1]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def gamma_lines(exp: dict[str, Any]) -> list[str]:
    """BOTH gammas, each named by the report key it came from.

    The script printed a bare "Gamma: 0.7738" — gamma_history[-1], the
    ALL-FINDINGS series. The two-sided gate reads gamma_critical_history,
    0.8293 on the same run. Project memory already records this confusion once
    ("0.240 = all-findings gamma, NOT the gate input"), so an unlabelled single
    number invites a third repeat. Gamma is an ACTIVE convergence condition
    (founder directive 2026-06-10, .claude/CLAUDE.md) — the labels must not
    imply either value is mere telemetry.
    """
    gate_note = [
        "     The two-sided gamma-alt gate reads the CRITICAL series, not the",
        "     all-findings one. It converges only when BOTH hold: gamma_critical >=",
        "     gamma_alt_threshold (default 0.30) AND K consecutive zero-new-critical",
        "     rounds (default 3). Gamma is an ACTIVE convergence condition — see",
        "     _check_gamma_alt_convergence in bench/reference_runner_v3.py.",
        "     It is not the only way a run can close: STATE_CONVERGED and",
        "     critical-quiescence are separate rules, and across all completed runs",
        "     they closed more of them than the gamma-alt gate did (measured",
        "     2026-08-04). Read 'Closed by' above to see which rule fired on THIS",
        "     run — do not infer it from the gamma values.",
    ]

    log_dir = Path(str(exp.get("log_dir", "")))
    report: Optional[Path] = None
    try:
        reports = sorted(log_dir.glob("exp*_report.json"))
        report = reports[0] if reports else None
    except OSError:
        report = None

    if report is None:
        carried = exp.get("gamma")
        return [
            f"  !! LOOKUP FAILED: no exp*_report.json under {log_dir or '(no log dir)'},",
            "     so gamma_critical — the convergence gate's input — is UNKNOWN, not zero.",
            f"     cdsfl_utils.latest_experiment() carried one value, {carried}, whose",
            "     series is NOT identified here. Do not read it as the gate input.",
        ] + gate_note

    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [
            f"  !! LOOKUP FAILED: cannot parse {report} ({exc}).",
            "     Both gammas are UNKNOWN, not zero.",
        ] + gate_note

    g_all = _last_number(data.get("gamma_history"))
    g_crit = _last_number(data.get("gamma_critical_history"))
    out: list[str] = []

    if g_all is None:
        out.append("  !! Gamma (all findings): gamma_history absent or non-numeric")
        out.append(f"     in {report.name} — UNKNOWN, not zero.")
    else:
        out.append(f"  Gamma, all findings   (gamma_history[-1]):          {g_all:.4f}")

    if g_crit is None:
        out.append("  !! Gamma (critical, THE GATE INPUT): gamma_critical_history absent or")
        out.append(f"     non-numeric in {report.name} — the gate's input is UNKNOWN, not zero.")
    else:
        out.append(
            f"  Gamma, critical only  (gamma_critical_history[-1]): {g_crit:.4f}"
            "   <-- THE GATE INPUT"
        )
    return out + gate_note


def target_lines(exp: dict[str, Any], root: Path) -> list[str]:
    """The reviewed artefact, existence-checked like the KEY FILES list.

    The script printed the report's target_file verbatim. On the current
    latest experiment that path no longer resolves — the directory holds a
    different file now — and an unchecked path printed as fact is the same
    defect as a KEY FILES entry printed without its '!! MISSING' marker.
    """
    raw = str(exp.get("target") or "").strip()
    if not raw:
        return [
            "  !! Target: the report carries no target_file. The reviewed artefact",
            "     is UNKNOWN, not absent.",
        ]
    resolved = Path(raw).expanduser()
    if not resolved.is_absolute():
        resolved = root / resolved
    if resolved.exists():
        return [f"  Target: {raw}"]
    shown = f"  !! MISSING: Target: {raw}"
    out = [shown]
    if str(resolved) != raw:
        out.append(f"     (checked: {resolved})")
    out.append("     That path does not resolve on disk now. The artefact the run")
    out.append("     reviewed is not there today — do not assume the file named in")
    out.append("     the report is the file you would read.")
    return out


# ── What is running RIGHT NOW ────────────────────────────────────────────────
# Standing detached-launch rule (founder directive 2026-07-29): runners launch
# via bench/detached_launch.sh, which writes a pidfile beside its log. Nothing
# in the documented recovery path checked for one, so a recovering agent could
# not answer "is an experiment running" from any step — and could launch a
# duplicate against a live checkpoint.
RUNNER_PATTERN = re.compile(r"reference_runner_v3|detached_launch|launch_exp")
PIDFILE_GLOBS = ("exp*.pid", "exp*_launch_*.pid")


def _read_ps() -> str:
    """Raw `ps` table. Raises on any failure — a failed scan is not an empty one."""
    proc = subprocess.run(
        ["ps", "-Ao", "pid=,etime=,args="],
        capture_output=True, text=True, timeout=20,
    )
    if proc.returncode != 0:
        raise OSError(f"ps exited {proc.returncode}: {proc.stderr.strip()[:120]}")
    return proc.stdout


def _parse_ps(raw: str) -> dict[int, tuple[str, str]]:
    """pid -> (elapsed, argv). Empty result means the parse failed, and the
    caller treats it as a failure — `ps` always lists at least itself."""
    table: dict[int, tuple[str, str]] = {}
    for line in raw.splitlines():
        parts = line.split(maxsplit=2)
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        table[int(parts[0])] = (parts[1], parts[2])
    return table


def running_experiment_lines(
    pid_dir: Optional[Path] = None,
    ps_reader: Callable[[], str] = _read_ps,
) -> list[str]:
    """Three states, never conflated: running / nothing running / check failed."""
    pid_dir = Path("/tmp") if pid_dir is None else pid_dir
    failures: list[str] = []
    notes: list[str] = []
    running: list[str] = []

    # 1. Live process scan.
    table: Optional[dict[int, tuple[str, str]]] = None
    try:
        raw = ps_reader()
    except Exception as exc:  # subprocess, OS, timeout — all mean UNKNOWN
        failures.append(f"process scan FAILED ({type(exc).__name__}: {exc})")
    else:
        parsed = _parse_ps(raw)
        if not parsed:
            failures.append(
                "process scan returned no parseable rows — `ps` lists at least "
                "itself, so this is a parse failure, not an empty machine"
            )
        else:
            table = parsed

    matched: dict[int, tuple[str, str]] = {}
    if table is not None:
        me = os.getpid()
        matched = {
            pid: v for pid, v in table.items()
            if pid != me and RUNNER_PATTERN.search(v[1])
        }
        notes.append(
            f"{len(table)} process(es) scanned against "
            f"/{RUNNER_PATTERN.pattern}/"
        )
        for pid, (elapsed, argv) in sorted(matched.items()):
            running.append(f"  >> RUNNING: PID {pid}, elapsed {elapsed}")
            running.append(f"     {_clip(argv, 100)}")

    # 2. Pidfiles.
    if not pid_dir.is_dir():
        failures.append(f"{pid_dir} is not a directory — pidfile scan could not run")
    else:
        try:
            pidfiles = sorted({p for g in PIDFILE_GLOBS for p in pid_dir.glob(g)})
        except OSError as exc:
            pidfiles = []
            failures.append(f"cannot list {pid_dir} ({exc}) — pidfile scan incomplete")
        else:
            stale = 0
            for pf in pidfiles:
                try:
                    pid = int(pf.read_text(encoding="utf-8").strip())
                except (OSError, ValueError) as exc:
                    failures.append(
                        f"{pf} holds no readable PID ({exc}) — whether that run is "
                        f"alive is UNKNOWN"
                    )
                    continue
                if table is not None:
                    alive = pid in table
                else:
                    try:
                        os.kill(pid, 0)
                        alive = True
                    except ProcessLookupError:
                        alive = False
                    except PermissionError:
                        alive = True          # exists, owned by another user
                    except OSError as exc:
                        failures.append(
                            f"{pf}: cannot test PID {pid} ({exc}) — UNKNOWN"
                        )
                        continue
                if not alive:
                    stale += 1
                    notes.append(f"stale pidfile {pf} (PID {pid} is not running)")
                elif pid in matched:
                    running.append(f"     pidfile {pf} names this PID {pid}")
                else:
                    elapsed = table[pid][0] if table is not None and pid in table else "unknown"
                    argv = table[pid][1] if table is not None and pid in table else ""
                    running.append(
                        f"  >> RUNNING (from pidfile {pf}): PID {pid}, elapsed {elapsed}"
                    )
                    if argv:
                        running.append(f"     {_clip(argv, 100)}")
            notes.append(
                f"{len(pidfiles)} pidfile(s) under {pid_dir} matching "
                f"{', '.join(PIDFILE_GLOBS)} ({stale} stale)"
            )

    out: list[str] = []
    if running:
        out.extend(running)
        # What was checked is a COMMAND-LINE MATCH, and that is all this may
        # claim: a shell tailing an experiment log or an editor with
        # detached_launch.sh open matches too. The bias is deliberate — a
        # false positive costs one glance at the argv printed above, a false
        # negative costs a duplicate launch against a live checkpoint — but
        # the wording must say which of the two this is.
        out.append("     Each line above MATCHES the runner pattern; the full command")
        out.append("     line is printed so a monitoring shell or editor can be told")
        out.append("     apart from a runner. Read it first, then:")
        out.append("     Do NOT launch another runner against the same checkpoint.")
    if failures:
        out.append("  !! CHECK INCOMPLETE — whether an experiment is running is UNKNOWN.")
        for f in failures:
            out.append(f"     {f}")
        out.append("     Check by hand:")
        out.append(f"       ps -Ao pid,etime,args | grep -E '{RUNNER_PATTERN.pattern}'")
        out.append(f"       ls {'  '.join(str(pid_dir / g) for g in PIDFILE_GLOBS)}")
    elif not running:
        out.append("     (nothing running — no matching process and no live pidfile.")
        out.append("      This is a completed check, not a failed one.)")
    for n in notes:
        out.append(f"     scanned: {n}" if not n.startswith("stale") else f"     {n}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="CDSFL Recovery — rebuild working context")
    parser.add_argument("--full", action="store_true", help="Include live test count")
    args = parser.parse_args()

    root = repo_root()
    print(f"CDSFL Recovery — {timestamp_iso()}")
    print(f"Repository: {root}")
    print("=" * 70)

    # --- FIRST READ ---
    print("\n## FIRST READ\n")
    for line in first_read_lines(root):
        print(line)

    # --- WHAT IS RUNNING (live — printed early because a duplicate launch
    #     against a live checkpoint is the expensive mistake here) ---
    print("\n## RUNNING NOW (live process + pidfile check)\n")
    for line in running_experiment_lines():
        print(line)

    # --- GIT STATE (live — printed BEFORE the saved snapshot below, which is
    #     one commit behind by construction and contradicts it) ---
    print("\n## GIT STATE (live, measured now — authoritative)\n")
    gs = git_state()
    # A git that is not answering returns empty strings, and an empty
    # `git status --porcelain` reads as "clean" — a failure rendered as a
    # confident success. The commit hash is the reliable liveness signal; an
    # empty branch alone is a detached HEAD, which is not a failure.
    git_ok = gs["last_hash"] not in ("", "unknown")
    if not git_ok:
        print("  !! LOOKUP FAILED: git returned no commit.")
        print("     The values below are NOT trustworthy. Check `git status` by hand.")
    print(f"  Branch: {gs['branch'] or '(none — detached HEAD or git failed)'}")
    print(f"  Last commit: {gs['last_hash']} {gs['last_message']}")
    print(f"  Committed: {gs['last_date']}")
    print(f"  Remote: {gs['remote_sync']}")
    if git_ok:
        print(f"  Working tree: {'clean' if gs['clean'] else 'DIRTY'}")
    else:
        print("  Working tree: UNKNOWN — 'clean' here would be a guess, because a")
        print("                git that answers nothing looks exactly like a clean tree.")
    if not gs["clean"]:
        total = len(gs["uncommitted"])
        print(f"  Uncommitted ({total} file(s)):")
        for f in gs["uncommitted"][:20]:
            print(f"    {f}")
        # A count printed above a shorter list reads as the whole list. The
        # remainder must be named, or a reader concludes the tree holds only
        # what is shown -- the same silent-truncation fault this report
        # already guards against in its RECOVERY.md [CAP: ...] blocks.
        if total > 20:
            print(f"    ... and {total - 20} more not shown "
                  f"(run `git status --short` for the full list)")

    # --- RECENT COMMITS ---
    print("\n## RECENT COMMITS\n")
    if gs["recent_log"]:
        for entry in gs["recent_log"]:
            print(f"  {entry}")
    else:
        print("  !! LOOKUP FAILED: git log returned no commits.")
        print("     That is a git failure, not an empty history.")

    # --- SAVED SNAPSHOT ---
    print("\n## SAVED SNAPSHOT — docs/CURRENT_STATE.md (NOT current truth)\n")
    print("  Written by scripts/cdsfl_sv.py BEFORE that save's own commit, so its git")
    print("  block names the PARENT commit and lists the about-to-be-committed files")
    print("  as uncommitted. Where it disagrees with GIT STATE above, GIT STATE wins.")
    print("  THE SAME APPLIES TO EVERY OTHER SECTION IT ECHOES. Its own 'Latest")
    print("  Experiment', 'Tests' and 'Recent Commits' blocks are as of the last save,")
    print("  and the live sections of this report — above and below — supersede them.")
    print("  Kept because it carries prose the live check does not.\n")
    current_state = root / "docs" / "CURRENT_STATE.md"
    if current_state.exists():
        print(current_state.read_text(encoding="utf-8"))
    else:
        # Fallback: extract from ONBOARDING.md
        print("  (docs/CURRENT_STATE.md not present — run scripts/cdsfl_sv.py to")
        print("   generate it. Falling back to resources/ONBOARDING.md.)\n")
        onboarding = root / "resources" / "ONBOARDING.md"
        if not onboarding.exists():
            print("  !! LOOKUP FAILED: resources/ONBOARDING.md does not exist either.")
            print("     Saved state is UNKNOWN, not empty.")
        else:
            section = read_section(onboarding, "## Current State", "\n## ")
            if section:
                # Print first 40 lines to avoid overwhelming output
                lines = section.splitlines()
                for line in lines[:40]:
                    print(line)
                if len(lines) > 40:
                    print(f"  ... ({len(lines) - 40} more lines in ONBOARDING.md)")
            else:
                print("  !! LOOKUP FAILED: resources/ONBOARDING.md exists but has no")
                print("     '## Current State' section. Saved state is UNKNOWN, not empty.")

    # --- LATEST EXPERIMENT ---
    print("\n## LATEST EXPERIMENT\n")
    exp = latest_experiment()
    if exp:
        print(f"  Experiment: {exp['name']}")
        print(f"  Number: {exp['number']}")
        print(f"  Status: {exp['status']}")
        # cdsfl_utils computes convergence_reason and the script never printed
        # it. Without it "Status: CONVERGED" beside a gamma value invites the
        # reader to assume the gamma-alt gate fired, which on exp49 it did not.
        reason = (exp.get("reason") or "").strip()
        if reason:
            print(f"  Closed by: {reason}")
        else:
            print("  !! Closed by: UNKNOWN — neither completion_signal.reason nor")
            print("     convergence_reason is present in the report. Not 'no reason'.")
        print(f"  Topology: {exp['topology']}")
        for line in target_lines(exp, root):
            print(line)
        print(f"  Rounds: {exp['total_rounds']}")
        print(f"  Findings: {exp['total_findings']}")
        for line in gamma_lines(exp):
            print(line)
        print(f"  Models: {', '.join(exp['models'])}")
        if exp["per_model"]:
            print("  Per model:")
            for model, count in sorted(exp["per_model"].items(), key=lambda x: -x[1]):
                print(f"    {model}: {count}")
        print(f"  Logs: {exp['log_dir']}")
        # .get(): tolerates cdsfl_utils versions without this key.
        skipped = exp.get("skipped_higher") or []
        if skipped:
            names = ", ".join(f"exp{n}" for n in skipped)
            print("  !! NOT the highest experiment on disk. Higher-numbered runs with")
            print(f"     no parseable report: {names}. Those runs are UNREPORTED,")
            print("     not absent.")
    else:
        for line in experiment_absence_lines(root / "bench" / "logs"):
            print(line)

    # --- TEST COUNT ---
    if args.full:
        print("\n## TESTS\n")
        count = test_count()
        if count is not None:
            print(f"  {count} tests collected (collection count, NOT a pass count)")
        else:
            print("  !! LOOKUP FAILED: pytest collection returned no parseable count.")
            print("     The test count is UNKNOWN, not zero. Run it by hand:")
            print("     python3 -m pytest bench/tests/ --co -q")

    # --- RECOVERY.md, ABOVE THE MARKERS ---
    # Printed as its own section, immediately before the marked region, so the
    # two can be compared. sv regenerates only the region below; this one is
    # hand-written and was never read.
    print("\n## RECOVERY.md — STATE BLOCKS ABOVE THE sv PENDING-WORK MARKERS\n")
    for line in recovery_head_lines(root / "resources" / "RECOVERY.md"):
        print(line)

    # --- PENDING WORK (the sv-regenerated region only) ---
    print("\n## PENDING WORK (sv-regenerated region of RECOVERY.md only)\n")
    for line in pending_work_lines(root / "resources" / "RECOVERY.md"):
        print(line)

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
        if full.exists():
            print(f"     {path} — {desc}")
        else:
            print(f"  !! MISSING: {path} — {desc}")


if __name__ == "__main__":
    main()
