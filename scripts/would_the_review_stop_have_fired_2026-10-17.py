#!/usr/bin/env python3
"""Would the B27 review-stop predicate have interrupted a run that CONVERGED?

WHY THIS IS THE DECIDING MEASUREMENT. The expensive error for a human-review stop
is a FALSE PAUSE: interrupting a run that was going to converge destroys the
autonomous-convergence measurement the run exists to produce, whereas a stop that
never fires merely leaves the run to end at `max_rounds` as it does today. So the
predicate in `bench/hil_review_trigger.py` must be shown NOT to fire on the runs
that actually converged, using those runs' own recorded numbers rather than
constructed cases.

It replays each archived report round by round, handing the predicate only what
the runner would have had at that moment -- the convergence history UP TO that
round, never the whole run -- and reports the first round at which it would have
paused, if any.

It decides nothing about whether the predicate is right in general. It answers one
falsifiable question: does it interrupt a success?
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.hil_review_trigger import RunEvidence, Thresholds, assess  # noqa: E402


def _wilson(k: int, n: int) -> tuple[float, float]:
    """95% Wilson interval, cross-checked against statsmodels where available."""
    if n == 0:
        return (0.0, 1.0)
    z, p = 1.959963984540054, k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    manual = (max(0.0, (c - h) / d), min(1.0, (c + h) / d))
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        if abs(lo - manual[0]) > 1e-9 or abs(hi - manual[1]) > 1e-9:
            raise AssertionError(
                f"Wilson disagreement at k={k}, n={n}: statsmodels ({lo}, {hi}) "
                f"against closed form {manual}"
            )
        return (float(lo), float(hi))
    except ImportError:
        return manual


def _num(d: dict, *names, default=None):
    for n in names:
        if n in d and isinstance(d[n], (int, float)):
            return d[n]
    for n in names:
        for holder in ("convergence_config", "_declared_config"):
            sub = d.get(holder)
            if isinstance(sub, dict) and isinstance(sub.get(n), (int, float)):
                return sub[n]
    return default


def _mechanical(rounds: list) -> list[int]:
    """Mechanical faults per round, cumulative. 0 where nothing records them."""
    out, running = [], 0
    for r in rounds:
        for f in (r.get("findings") or []):
            if f.get("mechanical_fault") or f.get("flaw_class") == "mechanical":
                running += 1
        out.append(running)
    return out


def replay(path: Path, th: Thresholds) -> dict:
    d = json.loads(path.read_text(errors="ignore"))
    rounds = d.get("rounds") or []
    if not isinstance(rounds, list):      # older reports store a COUNT here
        rounds = []
    # ★ THE DECIDING SERIES IS `gamma_critical_history`, NOT `gamma_history`.
    # Measured 2026-10-17: reading `gamma_history` produced 2 false pauses out of
    # 28 converged runs, and both were artefacts of reading the wrong series.
    # exp44 converged at round 12 by STATE_CONVERGED while its all-findings gamma
    # sat flat and its CRITICAL gamma climbed monotonically 0.1803 -> 0.4316;
    # exp47 converged by CRITICAL_QUIESCENCE_CONVERGED and leg 3 by
    # HARDENED_CONVERGED, both on gamma_critical. Every recorded convergence
    # reason names the critical series, so that is the layer the gate decides on
    # and the only one a stall may be judged against.
    hist = (d.get("gamma_critical_history")
            or d.get("gamma_history") or d.get("gamma_all_history") or [])
    hist = [h for h in hist if isinstance(h, (int, float))]
    thr = _num(d, "gamma_alt_threshold", "gamma_threshold", default=0.30)
    maxr = _num(d, "max_rounds", default=21)
    earliest = _num(d, "gamma_alt_earliest_round", default=3)
    mech = _mechanical(rounds)
    cumulative_findings, running = [], 0
    for r in rounds:
        running += int(r.get("findings_count") or 0)
        cumulative_findings.append(running)

    # ★ A RUN THAT CONVERGED STOPPED THERE, so a later round never happens and
    # must not be replayed. Measured 2026-10-17: without this bound the replay
    # reported a pause at round 4 on a run that converged at round 3 -- an
    # assessment the runner would never have made. That was a defect in this
    # instrument, not in the predicate, and it inflated the false-pause count
    # from 2 to 3 before it was caught.
    converged_at = d.get("converged_at")
    last_round = len(hist)
    if isinstance(converged_at, int) and converged_at >= 1:
        last_round = min(last_round, converged_at)

    first_pause = None
    for i in range(last_round):
        ev = RunEvidence(
            round_idx=i + 1,
            max_rounds=int(maxr),
            gamma_critical=float(hist[i]),
            gamma_critical_threshold=float(thr),
            earliest_round=int(earliest),
            gamma_critical_history=tuple(float(x) for x in hist[: i + 1]),
            mechanical_faults=mech[i] if i < len(mech) else 0,
            total_findings=cumulative_findings[i] if i < len(cumulative_findings) else 0,
        )
        v = assess(ev, th)
        if v.should_pause:
            first_pause = (i + 1, v.clause, v.reasons)
            break

    return {
        "run": path.parent.name,
        "report": path.name,
        "rounds_recorded": len(hist),
        "rounds_replayed": last_round,
        "converged_at": d.get("converged_at"),
        "convergence_reason": d.get("convergence_reason"),
        "gamma_final": hist[-1] if hist else None,
        "gamma_threshold": thr,
        "first_pause": first_pause,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", default=str(REPO / "bench" / "logs"))
    args = ap.parse_args()

    reports = sorted(
        p for p in Path(args.logs).rglob("*_report.json")
        if "sandbox_harvest" not in str(p)
    )
    if not reports:
        print("no archived reports found -- nothing to replay")
        return 0

    rows, usable = [], 0
    for p in reports:
        try:
            row = replay(p, Thresholds())
        except Exception as exc:                                   # noqa: BLE001
            print(f"  [skip] {p.name}: {type(exc).__name__}: {exc}")
            continue
        if row["rounds_recorded"] < 2:
            continue
        usable += 1
        rows.append(row)

    converged = [r for r in rows if r["converged_at"] is not None]
    paused_a_success = [r for r in converged if r["first_pause"]]

    print(f"archived reports examined:          {len(reports)}")
    print(f"with 2 or more rounds of history:   {usable}")
    print(f"of those, runs that CONVERGED:      {len(converged)}")
    stalled = [r for r in rows if r["converged_at"] is None]
    caught = [r for r in stalled if r["first_pause"]]
    print(f"of those, runs that did NOT converge: {len(stalled)}")
    print()
    fp_lo, fp_hi = _wilson(len(paused_a_success), len(converged))
    tp_lo, tp_hi = _wilson(len(caught), len(stalled))
    print(f"★ FALSE PAUSES -- converged runs it would have INTERRUPTED: "
          f"{len(paused_a_success)} of {len(converged)}, "
          f"{100.0 * len(paused_a_success) / max(1, len(converged)):.4f}%, "
          f"Wilson [{100 * fp_lo:.4f}%, {100 * fp_hi:.4f}%]")
    print(f"  TRUE PAUSES -- non-converged runs it would have caught: "
          f"{len(caught)} of {len(stalled)}, "
          f"{100.0 * len(caught) / max(1, len(stalled)):.4f}%, "
          f"Wilson [{100 * tp_lo:.4f}%, {100 * tp_hi:.4f}%]")
    print()
    print("READ THE ASYMMETRY, NOT THE SECOND NUMBER ALONE. A false pause destroys the")
    print("autonomous-convergence measurement the run exists to produce; a pause that")
    print("never fires merely leaves the run to end at max_rounds as it does today. So a")
    print("predicate that catches a MINORITY of stalled runs while interrupting NO")
    print("successful one is the correct trade, and the low true-pause share is a")
    print("deliberate property rather than a shortfall.")
    print()
    for r in rows:
        mark = "PAUSE" if r["first_pause"] else "  --  "
        conv = f"converged r{r['converged_at']}" if r["converged_at"] is not None else "did not converge"
        print(f"  [{mark}] {r['run'][:46]:46} {r['rounds_recorded']:2}r  "
              f"gamma_final={r['gamma_final']}  {conv}")
        if r["first_pause"]:
            rnd, clause, reasons = r["first_pause"]
            print(f"           would pause at round {rnd}: {clause}")
            for s in reasons:
                print(f"             - {s}")
    print()
    if converged and not paused_a_success:
        print("VERDICT: the predicate interrupts NONE of the runs that converged. The")
        print("false-pause risk is not demonstrated on the archive available.")
    elif not converged:
        print("VERDICT: NO converged run is present in the archive, so the false-pause")
        print("question COULD NOT BE ASKED. That is a gap in the evidence, not a pass.")
    else:
        print("VERDICT: the predicate WOULD have interrupted a converged run. That is a")
        print("false pause and the thresholds are wrong as they stand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
