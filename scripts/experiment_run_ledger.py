#!/usr/bin/env python3
"""Derive the experiment run ledger from the run artefacts themselves.

WHY THIS EXISTS. The founder asked, 2026-08-25, for the experiments to be
renumbered by actual run order. Measuring first showed the premise does not
hold: sorted by start time, the experiment NUMBER is already perfectly
monotonic across all 44 non-empty run directories, zero violations. The three
apparent violations are all empty directories written on 2026-08-07 by aborted
re-invocations of exp35 and exp36, which are not runs.

So the order needs no fixing. Two other things do, and this script surfaces
both rather than a renumber that would change nothing:

  1. THE SEQUENCE HAS HOLES THAT LOOK LIKE RUNS. exp50, exp51 and exp52 have
     configs and no run directory. exp54 has neither. A reader counting
     "exp29 through exp55" infers 27 experiments; 23 numbers produced a
     directory and 22 produced a report.

  2. STATUS IS RECORDED IN TWO PLACES THAT DISAGREE. completion_signal.json
     carries status and reason; the run report carries converged_at and
     convergence_reason. Measured 2026-08-26: 20 of 31 signals say INCOMPLETE
     with an EMPTY reason, and in 7 of those the report DOES name one --
     exp36 and exp37 STATE_CONVERGED, exp40 twice, exp35 EXTENSION_STALLED,
     and both exp55 runs HALTED_IRREDUCIBLE_QUEUE_ALARM. Post-mortem tooling
     reading only the signal sees a converged run as INCOMPLETE. The runner's
     own source names this defect at reference_runner_v3.py:11002 and dates a
     partial fix to 2026-05-18; runs after that date still show it.

This script reads BOTH and reports the disagreement instead of picking one.

Usage:
    python3 scripts/experiment_run_ledger.py              # markdown table
    python3 scripts/experiment_run_ledger.py --check      # drift guard, exit 1
    python3 scripts/experiment_run_ledger.py --json       # machine-readable
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
LEDGER = REPO / "experimental_notes" / "EXPERIMENT_RUN_LEDGER.md"

DIR_RE = re.compile(r"^exp(\d+)[_-](.+?)_(\d{8}T\d{6}Z)$")
ROUND_RE = re.compile(r"^round_(\d+)\.json$")


# The anchor text of the comment the ledger cites. Matched against the runner
# source at generation time rather than typed, because it WAS typed: the ledger
# claimed line 11002 while the comment sat at 12070, an error of 1,068 lines
# that survived because the test compared the ledger against this generator's
# own hard-coded string. Two copies of the same wrong number agree with each
# other perfectly. Fixed 2026-09-01.
_GAMMA_ALT_ANCHOR = "gamma-alt gate previously set only the result"


def _gamma_alt_comment_line() -> int:
    """Line number of the cited gamma-alt comment in the runner source.

    Raises rather than guessing: a ledger that silently cites the wrong line is
    worse than one that fails to build, and this document's own header promises
    every figure in it is derived.
    """
    src = (REPO / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
    for i, line in enumerate(src.splitlines(), start=1):
        if _GAMMA_ALT_ANCHOR in line:
            return i
    raise RuntimeError(
        f"anchor comment not found in the runner: {_GAMMA_ALT_ANCHOR!r}. "
        "If the comment was rewritten, update _GAMMA_ALT_ANCHOR to match.")


def _rel(p: pathlib.Path) -> str:
    """Repo-relative when possible, absolute otherwise. NEVER raises.

    `Path.relative_to` throws ValueError for any path outside the repo, which
    turns a report line into a crash. This is the SECOND time that defect was
    written in one session -- scripts/supersession_check.py had it too -- so it
    is a helper here rather than an inline try/except.
    """
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def _pretty(ts: str) -> str:
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}"


def collect() -> dict:
    """Every run directory, plus every configured experiment that never ran."""
    runs = []
    for d in sorted(LOGS.iterdir()) if LOGS.is_dir() else []:
        m = DIR_RE.match(d.name)
        if not (m and d.is_dir()):
            continue
        files = {f.name for f in d.iterdir()}
        num, name, ts = int(m.group(1)), m.group(2), m.group(3)

        sig_status = sig_reason = ""
        sig = d / "completion_signal.json"
        if sig.is_file():
            try:
                c = json.loads(sig.read_text())
                sig_status = str(c.get("status", "") or "")
                sig_reason = str(c.get("reason", "") or "").strip()
            except (OSError, ValueError):
                sig_status = "UNREADABLE"

        rep_at = None
        rep_reason = ""
        reps = [f for f in files if f.endswith("_report.json")]
        if reps:
            try:
                r = json.loads((d / sorted(reps)[0]).read_text())
                rep_at = r.get("converged_at")
                rep_reason = str(r.get("convergence_reason", "") or "").strip()
            except (OSError, ValueError):
                rep_reason = "UNREADABLE"

        rounds = [int(x.group(1)) for f in files for x in [ROUND_RE.match(f)] if x]
        runs.append({
            "exp": num, "name": name, "started": ts, "pretty": _pretty(ts),
            "files": len(files), "rounds": max(rounds) + 1 if rounds else 0,
            "has_report": bool(reps),
            "signal_status": sig_status, "signal_reason": sig_reason,
            "report_converged_at": rep_at, "report_reason": rep_reason,
            "aborted": not files,
        })
    runs.sort(key=lambda r: r["started"])

    configured = set()
    for c in sorted(REPO.glob("bench/exp*_configs")):
        m = re.match(r"^exp(\d+)_configs$", c.name)
        if m and any(c.glob("*.json")):
            configured.add(int(m.group(1)))
    ran = {r["exp"] for r in runs if not r["aborted"]}

    # Every number inside the observed span, so a number with NEITHER a config
    # NOR a run is still surfaced. exp54 is exactly that case and a
    # config-only scan misses it -- which is how "four numbers" came to sit
    # above a list of three while this script was being written.
    span = range(min(ran), max(ran) + 1) if ran else range(0)
    gaps = sorted(set(span) - ran)
    return {
        "runs": runs,
        "configured_never_ran": sorted(configured - ran),
        "gap_numbers": gaps,
        "gap_no_config": sorted(n for n in gaps if n not in configured),
        "span": [min(ran), max(ran)] if ran else [],
        "ran": sorted(ran),
        "reported": sorted({r["exp"] for r in runs if r["has_report"]}),
    }


def monotonicity(data: dict) -> dict:
    """Is the experiment NUMBER monotonic in start time? Answered, not assumed."""
    peak, viol = 0, []
    for r in data["runs"]:
        if r["aborted"]:
            continue
        if r["exp"] < peak:
            viol.append({"exp": r["exp"], "started": r["started"], "after": peak})
        peak = max(peak, r["exp"])
    live = [r for r in data["runs"] if not r["aborted"]]
    return {"checked": len(live), "violations": viol, "monotonic": not viol}


def disagreements(data: dict) -> list:
    """Runs whose signal says INCOMPLETE while the report names an outcome."""
    out = []
    for r in data["runs"]:
        if r["signal_status"] == "INCOMPLETE" and (
                r["report_converged_at"] is not None or r["report_reason"]):
            out.append(r)
    return out


def render(data: dict) -> str:
    mono = monotonicity(data)
    dis = disagreements(data)
    live = [r for r in data["runs"] if not r["aborted"]]
    aborted = [r for r in data["runs"] if r["aborted"]]

    L = []
    A = L.append
    A("# Experiment run ledger — derived from the artefacts, never typed")
    A("")
    A("**DERIVED.** Every figure below is read from `bench/logs/*/` at generation time by")
    A("`scripts/experiment_run_ledger.py`. Nothing here is transcribed by hand, because the")
    A("counts this replaces were transcribed by hand and drifted.")
    A("")
    A("## The order is already correct")
    A("")
    A(f"Sorted by start time, the experiment number is **{'monotonic' if mono['monotonic'] else 'NOT monotonic'}** across")
    A(f"all {mono['checked']} non-empty run directories — **{len(mono['violations'])} violations**. A renumber by run order")
    A("would change nothing. What is actually wrong is stated in the two sections after the table.")
    A("")
    A("## Every run, in the order it started")
    A("")
    A("| # | started | exp | run name | rounds | signal | report says |")
    A("|---:|---|---:|---|---:|---|---|")
    for i, r in enumerate(live, 1):
        reason = r["report_reason"] or r["signal_reason"] or "—"
        if len(reason) > 58:
            reason = reason[:55] + "…"
        at = r["report_converged_at"]
        says = f"`converged_at={at}` — {reason}" if at is not None else reason
        A(f"| {i} | {r['pretty']} | {r['exp']} | `{r['name']}` | {r['rounds']} | "
          f"{r['signal_status'] or '—'} | {says} |")
    A("")
    if aborted:
        A(f"**{len(aborted)} aborted invocations** wrote an empty directory and are excluded above: "
          + ", ".join(f"exp{r['exp']} {r['pretty']}" for r in aborted) + ".")
        A("")
    A("## Hole 1 — numbers that never ran")
    A("")
    A(f"Experiments with a run directory: **{data['ran']}**.")
    A("")
    A(f"Numbers inside that span with **no run directory at all**: **{data['gap_numbers'] or 'none'}** "
      f"({len(data['gap_numbers'])} of {data['span'][1] - data['span'][0] + 1}).")
    A("")
    A(f"Of those, **{data['configured_never_ran']}** have a config and were never launched, and "
      f"**{data['gap_no_config']}** has no config either — planned in prose only.")
    A("")
    lo, hi = data["span"]
    A(f"A reader counting the span `exp{lo}`–`exp{hi}` infers {hi - lo + 1} experiments. "
      f"**{len(data['ran'])} numbers produced a directory** and **{len(data['reported'])} produced a report**. "
      f"The gap is not a numbering error; it is {len(data['gap_numbers'])} numbers that were planned "
      "and never executed.")
    A("")
    A("## Hole 2 — status is recorded twice and the two disagree")
    A("")
    empty = [r for r in live if r["signal_status"] and not r["signal_reason"]]
    A(f"`completion_signal.json` carries a status and a reason. **{len(empty)} of "
      f"{len([r for r in live if r['signal_status']])} signals carry an EMPTY reason.**")
    A("")
    A(f"In **{len(dis)}** of those the run report DOES name an outcome, so the two artefacts")
    A("disagree and a tool reading only the signal draws the wrong conclusion:")
    A("")
    A("| exp | started | signal | but the report says |")
    A("|---:|---|---|---|")
    for r in dis:
        reason = r["report_reason"] or f"converged_at={r['report_converged_at']}"
        A(f"| {r['exp']} | {r['pretty']} | {r['signal_status']} (reason empty) | {reason[:80]} |")
    A("")
    A(f"The runner's own source names this at `bench/reference_runner_v3.py:{_gamma_alt_comment_line()}` and dates a")
    A("partial fix to 2026-05-18: *\"the hardened / gamma-alt gate previously set only the result")
    A("dict, so post-mortem tooling read every hardened convergence as INCOMPLETE.\"* Runs after")
    A("that date still show it, so the fix did not close the class.")
    A("")
    A("Regenerate with `python3 scripts/experiment_run_ledger.py > experimental_notes/EXPERIMENT_RUN_LEDGER.md`.")
    A("`--check` fails if the committed copy no longer matches the artefacts.")
    A("")
    A("Written under CDSFL note standard v1.6 (24 August 2026).")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="compare the committed ledger against the artefacts; exit 1 on drift")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    data = collect()
    if args.json:
        print(json.dumps({**data, "monotonicity": monotonicity(data),
                          "disagreements": len(disagreements(data))}, indent=2))
        return 0
    fresh = render(data)
    if not args.check:
        print(fresh, end="")
        return 0
    if not LEDGER.is_file():
        print(f"  ledger missing: {_rel(LEDGER)}")
        return 1
    if LEDGER.read_text(encoding="utf-8") == fresh:
        print(f"  ledger matches the artefacts ({len(data['runs'])} run directories)")
        return 0
    print(f"  LEDGER DRIFT: {_rel(LEDGER)} no longer matches bench/logs/.")
    print("  Regenerate: python3 scripts/experiment_run_ledger.py > "
          f"{_rel(LEDGER)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
