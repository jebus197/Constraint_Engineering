#!/usr/bin/env python3
"""Did a CONFIRMED critical land in the closing window and count as zero?

WHY THIS EXISTS
---------------
`_location_keyed_critical_series` (reference_runner_v2.py) counts a critical as
novel iff it names at least one code location not previously flagged. A second,
genuinely distinct defect in an already-flagged function therefore contributes
ZERO — not a duplicate, not a downgrade, zero. The function's own docstring says
so, names that blindness, and states it must never gate. A dedicated test
demonstrates it. The June plan made live gating conditional on first building a
semantic splitter that could tell two defects in one function apart.

The splitter was never built. Gating was enabled in sixteen configs anyway.

It then fired twice, at closing rounds, on CONFIRMED criticals:
    Exp 45  C0031  sev 0.75  opened r3   converged r3
    Exp 47  C0070  sev 0.85  opened r13  converged r13
In both the gate tail read [0,0,0] and the run stopped.

WHY NOT JUST BUILD THE SPLITTER
-------------------------------
Measured 2026-07-31, both existing comparators, replayed over all six completed
runs. Neither works:

  * `finding_similarity` (embedding backend) scores the two target findings at
    0.684 and 0.781 against priors at the same location — both far ABOVE the
    calibrated 0.55 threshold, so it calls them repeats. Embeddings of findings
    about the same function in the same codebase are all close; the backend
    captures "same topic", not "same defect".
  * `jaccard_similarity` scores them 0.081 and 0.152, comfortably below its 0.33
    threshold, so it correctly calls both NEW — but applied across the archive it
    destroys convergence in ALL SIX runs (every tail non-zero). Models reword
    re-finds enough that lexical overlap collapses for genuine repeats too.

One comparator says everything is the same defect; the other says everything is
different. Neither threshold sits anywhere useful. The splitter is real work, and
this module is not it.

WHAT THIS IS INSTEAD
--------------------
The blindness only bites when a CONFIRMED critical opens inside the closing
window — the K rounds the gate read as zero. That is checkable AFTER the fact,
exactly, at no cost, on every run. This module does that check.

It changes no gate and no verdict. It removes the silence: a run that converged
while a demonstrated critical was landing unseen now says so.

A CORRECTION TO THIS MODULE'S ORIGINAL FRAMING (2026-07-31, later the same day)
------------------------------------------------------------------------------
The first version reported C0031 and C0070 as demonstrated criticals left
UNRESOLVED at close, on the strength of their status field reading CONFIRMED
while 158 of their 160 peers read CLOSED. Tracing the state machine showed that
was wrong, and the error is worth recording because it inverts the severity.

`CONFIRMED + verified -> CLOSED` runs in the per-round reconciliation pass, at
the START of a round. A finding demonstrated in the FINAL round never meets it —
there is no next round. Both findings are CONFIRMED, `verified`, and carry zero
unresolved challenges: one bookkeeping step from settled, and the step never ran.
Nothing escaped. `_settle_confirmed_findings` now runs that step once after
convergence, so future runs record them correctly.

So this module reports TWO different things, and they must not be conflated:

  * `findings` — demonstrated criticals still UNRESOLVED at close. After the
    settle pass this should be EMPTY on every future run. A non-empty list is a
    real anomaly, not a bookkeeping lag.
  * `arrived_in_window` — demonstrated criticals that ARRIVED in the closing
    window at all, resolved or not. These are the cases where the counter's
    blind spot COULD have fired: the tail read zero, so by construction none of
    them counted as new. This module cannot tell a correctly-counted re-find
    from a missed new defect — that is the splitter problem, and it is exactly
    what the five refuted routes above failed to solve. The number is a
    screening signal for human judgement, not a defect count.

The distinction that took a wrong turn to find: the counter's blindness is a
question about convergence TIMING — whether the run stopped sooner than ideal.
It was never a question about findings escaping.

USAGE
    python3 bench/audit_closing_window.py                     # every completed run
    python3 bench/audit_closing_window.py bench/logs/exp45_*  # one run
    python3 bench/audit_closing_window.py --json              # machine-readable

Exit status 1 if any audited run has a finding in its closing window, so this can
gate a report step without gating the experiment.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CRITICAL_SEVERITY_THRESHOLD = 0.7
DEFAULT_WINDOW = 3  # gamma_alt_consecutive_zero_crit


# A demonstrated critical that reached one of these was seen and dealt with.
_RESOLVED_STATUSES = {"CLOSED", "MERGED", "DUPLICATE", "REFUTED", "WITHDRAWN"}


def _report_for(run_dir: str) -> Optional[Path]:
    hits = sorted(glob.glob(os.path.join(run_dir, "*_report.json")))
    return Path(hits[0]) if hits else None


def _infer_gate(data: Dict[str, Any]) -> str:
    """Which counting rule produced the zero tail? The report does not say.

    `convergence_config` carries four keys and none of them is the location flag.
    The best available evidence is that `location_crit_shadow_history` — named
    "shadow" even in runs where the config promoted it to gating — agrees with
    the tail quoted in `convergence_reason`. Agreement is consistent with the
    location series having gated; it is not proof, because the two series can
    coincide. Report the strength of the evidence, never a bare assertion.
    """
    # Reports written from 2026-07-31 state this outright.
    if "location_crit_series_is_gating" in data:
        return "location-keyed" if data["location_crit_series_is_gating"] else "id-proxy"
    cc = data.get("convergence_config") or {}
    if "critical_series" in cc:
        return "location-keyed" if cc["critical_series"] == "location_keyed" else "id-proxy"
    for k in ("location_keyed_convergence",):
        if k in cc:
            return "location-keyed" if cc[k] else "id-proxy"
    hist = data.get("location_crit_shadow_history")
    reason = str(data.get("convergence_reason") or "")
    if not isinstance(hist, list) or "tail=[" not in reason:
        return "unrecorded"
    try:
        quoted = [int(x) for x in
                  reason.split("tail=[", 1)[1].split("]", 1)[0].split(",")]
    except (ValueError, IndexError):
        return "unrecorded"
    if hist[-len(quoted):] == quoted:
        return "location-keyed?"  # consistent with, not proof of
    return "id-proxy?"


def audit_run(run_dir: str, window: int = DEFAULT_WINDOW) -> Optional[Dict[str, Any]]:
    """Findings that opened inside the closing window of one run.

    The window is the K rounds the gate must see as zero, i.e. rounds
    ``[converged_at - window + 1, converged_at]``. A CONFIRMED critical opening
    anywhere in there was, by construction, invisible to the counter that closed
    the run — otherwise the tail would not have read zero.
    """
    rep = _report_for(run_dir)
    if rep is None:
        return None
    try:
        data = json.loads(rep.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"run": os.path.basename(run_dir.rstrip("/")), "error": str(exc)}

    conv = data.get("converged_at")
    name = os.path.basename(run_dir.rstrip("/")).split("_2026")[0]
    # The report stores `convergence_config`, not `config`, and it carries only
    # four keys — NOT `location_keyed_convergence` and NOT
    # `gamma_alt_consecutive_zero_crit`. So a completed report does not record
    # WHICH counting rule produced the zero tail that closed the run. That is a
    # reproducibility defect in its own right (reported 2026-07-31, not fixed
    # here — fixing it means changing the runner, which cannot retro-fill a
    # completed record). Infer where possible, and say "unrecorded" otherwise
    # rather than guessing.
    cc = data.get("convergence_config") or {}
    win = int(cc.get("consecutive_required") or window)
    gated = _infer_gate(data)

    out: Dict[str, Any] = {
        "run": name, "report": str(rep), "converged_at": conv,
        "window": win, "gate": gated,
        # Still unresolved at close. Should be empty on every run written after
        # the post-convergence settle pass landed.
        "findings": [],
        # Arrived in the closing window at all, resolved or not — the screening
        # signal for whether the counter's blind spot could have fired.
        "arrived_in_window": [],
    }
    if conv is None:
        out["note"] = "run did not converge — closing window undefined"
        return out

    lo = conv - win + 1
    entries = (data.get("registry") or {}).get("entries") or {}
    for cid, e in sorted(entries.items()):
        r = e.get("open_since_round")
        if r is None or r < lo or r > conv:
            continue
        if float(e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
            continue
        if e.get("falsifier_verdict") != "CONFIRMED":
            continue
        # A finding that was demonstrated AND resolved inside the window is not
        # the failure mode. The gate saw it, the ladder closed it, the run moved
        # on — that is the machinery working. What matters is a demonstrated
        # critical still UNRESOLVED at the moment the run declared itself done.
        # Without this filter the audit flags 7 of 36 runs and means nothing;
        # with it, it flags exactly the two cases the blindness actually cost.
        out["arrived_in_window"].append({
            "id": cid, "severity": float(e.get("severity") or 0.0),
            "opened_round": r, "status": e.get("status")})
        if e.get("status") in _RESOLVED_STATUSES:
            continue
        out["findings"].append({
            "id": cid,
            "severity": float(e.get("severity") or 0.0),
            "opened_round": r,
            "status": e.get("status"),
            "description": (e.get("description") or "")[:400],
        })
    out["findings"].sort(key=lambda f: (-f["severity"], f["id"]))
    return out


def audit_all(pattern: str = "bench/logs/exp*_*/",
              window: int = DEFAULT_WINDOW) -> List[Dict[str, Any]]:
    results = []
    for run in sorted(glob.glob(str(REPO_ROOT / pattern))):
        if not os.path.isdir(run) or run.rstrip("/").endswith(".errata"):
            continue
        r = audit_run(run, window)
        if r is not None:
            results.append(r)
    return results


def _render(results: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    flagged = [r for r in results if r.get("findings")]
    lines.append("CLOSING-WINDOW AUDIT")
    lines.append("=" * 78)
    lines.append("")
    lines.append("A CONFIRMED critical opening inside the closing window was invisible to")
    lines.append("the counter that closed the run. This does not invalidate the run: the")
    lines.append("finding is recorded and demonstrated. It qualifies the convergence claim.")
    lines.append("")
    for r in results:
        if r.get("error"):
            lines.append(f"  {r['run']:36} ERROR {r['error']}")
            continue
        gate = r.get("gate", "unrecorded")
        conv = r.get("converged_at")
        if conv is None:
            lines.append(f"  {r['run']:36} no convergence — not audited")
            continue
        n = len(r["findings"])
        arr = len(r.get("arrived_in_window") or [])
        mark = f"UNRESOLVED x{n}" if n else (f"clean ({arr} arrived)" if arr else "clean")
        lines.append(f"  {r['run']:36} r{conv:<3} window={r['window']} "
                     f"gate={gate:14} {mark}")
        for f in r["findings"]:
            lines.append(f"      -> {f['id']} sev={f['severity']:.2f} "
                         f"opened r{f['opened_round']} ({f['status']})")
            lines.append(f"         {f['description'][:96]}")
    lines.append("")
    lines.append(f"{len(flagged)} of {len(results)} audited run(s) flagged.")
    if flagged:
        lines.append("")
        lines.append("For each flagged run the convergence claim should read: 'no new criticals")
        lines.append("at previously unflagged locations', not 'no new criticals'.")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="*", help="run directories (default: all completed)")
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                    help="closing-window size; per-run config overrides it")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if args.runs:
        results = [r for r in (audit_run(x, args.window) for x in args.runs)
                   if r is not None]
    else:
        results = audit_all(window=args.window)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(_render(results))
    return 1 if any(r.get("findings") for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
