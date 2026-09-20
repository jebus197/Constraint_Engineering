#!/usr/bin/env python3
"""Producer for the panel delivery-channel measurement, 2026-09-20.

THE DEFECT. The round-3 panel brief, Section 8, tells every seat: "Deliver each
fix as a file at a real path". The CLI seats are dispatched with
`--allowedTools Bash Read Grep Glob WebFetch WebSearch`
(bench/experiment_11_orchestrator.py, the call_claude_cli argument list), which
deliberately withholds Write and Edit under the comment "No file modification".

So the brief asks for a deliverable the grant refuses. A seat can comply ONLY by
spontaneously routing around the refusal through Bash. That is not a capability
the brief names, and it is not one the grant advertises: it is a workaround the
seat has to invent for itself.

WHY THIS IS NOT THE sandbox-exec CONFINEMENT ADDED THE SAME DAY. That guard
wraps `run_python`, which is an HTTP-seat tool. The CLI seats never call it.
The refusal here is the CLI's own permission layer and predates today.

WHAT THIS SCRIPT MEASURES, from the archived seat tool records alone:
  - per seat and round: total recorded calls, direct Write/Edit attempts, and
    Bash calls that write a file;
  - how many files each seat actually landed in the harvest.

Run:  python3 scripts/panel_delivery_channel_2026-09-20.py
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = {
    "r1": ROOT / "bench/logs/maths_panel_2026-09-20",
    "r3": ROOT / "bench/logs/maths_panel_2026-09-20_r3",
}
CLI_SEATS = ("cc2", "fable")

# A Bash call that creates or overwrites a file. Deliberately narrow: a
# heredoc, a redirect, tee, or an explicit Python write.
WRITE_MARKERS = ("<<'PY'", '<<"PY"', "<<'EOF'", '<<"EOF"', "cat >", "cat >>",
                 "tee ", "write_text", "open(")
REAL_PATH_RE = re.compile(r"\b((?:scripts|bench|docs)/[A-Za-z0-9_\-/.]+\.(?:py|md))")


def seat_record(round_dir: Path, seat: str) -> dict | None:
    p = round_dir / f"{seat}.tools.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def harvested_files(round_dir: Path, seat: str) -> list[str]:
    base = round_dir / "sandbox_harvest" / seat
    if not base.is_dir():
        return []
    out = []
    for f in sorted(base.rglob("*")):
        if not f.is_file() or f.name == "changes.diff":
            continue
        # dispatch.log is the harness's own file echoed back, not a deliverable.
        if f.name == "dispatch.log":
            continue
        out.append(str(f.relative_to(base)))
    return out


def analyse(round_key: str, seat: str) -> dict:
    round_dir = ROUNDS[round_key]
    rec = seat_record(round_dir, seat)
    if rec is None:
        return {}
    calls = rec.get("calls") or []
    direct = [c for c in calls if (c.get("name") or "") in ("Write", "Edit")]
    bash_writes, targets = 0, set()
    for c in calls:
        if (c.get("name") or "") != "Bash":
            continue
        s = str(c.get("input_preview") or "")
        if any(k in s for k in WRITE_MARKERS):
            bash_writes += 1
            targets.update(REAL_PATH_RE.findall(s))
    return {
        "round": round_key,
        "seat": seat,
        "calls": len(calls),
        "direct_write_edit_attempts": len(direct),
        "bash_write_calls": bash_writes,
        "real_path_targets_seen_in_bash": sorted(targets),
        "files_landed_in_harvest": harvested_files(round_dir, seat),
    }


def main(argv: list | None = None) -> int:
    # `--help` MUST NEVER COST MONEY, and must never run a measurement either.
    # argparse is constructed and parsed BEFORE any archive walk or subprocess,
    # so the flag is answered rather than consumed as a positional argument.
    # This project already carries the rule in its strong form, written after 15
    # of 17 runners billed a live dispatch on an unrecognised argument.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    print("PANEL DELIVERY CHANNEL, 2026-09-20")
    print("The brief asks for files at real paths; the CLI grant withholds Write and Edit.")
    print()
    rows = []
    for round_key in ("r1", "r3"):
        for seat in CLI_SEATS:
            row = analyse(round_key, seat)
            if not row:
                continue
            rows.append(row)
            print(f"{round_key} {seat}:")
            print(f"    recorded calls                 : {row['calls']}")
            print(f"    direct Write/Edit attempts     : {row['direct_write_edit_attempts']}")
            print(f"    Bash calls that write a file   : {row['bash_write_calls']}")
            print(f"    real paths named in those calls: {len(row['real_path_targets_seen_in_bash'])}")
            for t in row["real_path_targets_seen_in_bash"]:
                print(f"        {t}")
            print(f"    files landed in harvest        : {len(row['files_landed_in_harvest'])}")
            for t in row["files_landed_in_harvest"]:
                print(f"        {t}")
            print()

    print("-" * 66)
    print("THE ASYMMETRY, which is the finding:")
    for row in rows:
        route = "Bash workaround" if row["files_landed_in_harvest"] else "none"
        print(f"    {row['round']} {row['seat']:6s}  direct attempts {row['direct_write_edit_attempts']}"
              f"  landed {len(row['files_landed_in_harvest'])}  route: {route}")
    print()
    print("A seat that attempts the documented route (Write/Edit) delivers nothing.")
    print("A seat that invents the undocumented route (Bash) delivers.")
    print("The grant and the brief disagree, and the seat pays for it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
