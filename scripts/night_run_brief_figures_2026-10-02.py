#!/usr/bin/env python3
"""Figures for the free panel round of 2026-10-02: why runs do not converge.

RE-EXECUTED RATHER THAN TYPED. `measured-rate-travels-with-its-script`: every
figure the brief declares is produced here, so a seat can contradict it by
running this rather than by trusting CC1's prose. Written after an evening in
which a Wilson interval typed from recall into a code comment was wrong by
0.02 percentage points at one bound and 0.04 at the other.

WHAT IT MEASURES. Every commissioning-arm run in `bench/logs` that produced a
report: its recorded convergence reason, its target, its round count, and
whether the report and the completion signal AGREE about why it stopped. The
disagreement is the point: 4 runs carry `convergence_reason: None` in the
report while `completion_signal.json` says `UNRECORDED_STOP`, so the archive
holds 2 records of one fact that do not match.

Run:  python3 scripts/night_run_brief_figures_2026-10-02.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"


def survey(pattern: str = "commissioning_arm*"):
    out = []
    for d in sorted(LOGS.glob(pattern + "/")):
        rep = next(iter(d.glob("*_report.json")), None)
        sig = d / "completion_signal.json"
        if not (rep and rep.is_file()):
            out.append({"run": d.name, "reported": False})
            continue
        try:
            r = json.loads(rep.read_text(encoding="utf-8"))
        except ValueError:
            out.append({"run": d.name, "reported": False})
            continue
        s = {}
        if sig.is_file():
            try:
                s = json.loads(sig.read_text(encoding="utf-8"))
            except ValueError:
                s = {}
        out.append({
            "run": d.name, "reported": True,
            "report_reason": r.get("convergence_reason"),
            "signal_reason": s.get("reason"),
            "status": s.get("status"),
            "target": r.get("target_file"),
            "rounds": r.get("total_rounds"),
            "max_rounds": r.get("max_rounds"),
            "findings": r.get("total_findings"),
            "halted": r.get("halted"),
            "wall_s": r.get("_wall_seconds"),
            "simulated": r.get("_simulated"),
        })
    return out


def wilson(k: int, n: int):
    """Two tools, because one library agreeing with itself is not a check."""
    a = b = None
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        a = (lo * 100, hi * 100)
    except ImportError:
        pass
    try:
        import mpmath as mp
        mp.mp.dps = 30
        z = mp.mpf('1.959963984540054235524594430520551527955550')
        N, K = mp.mpf(n), mp.mpf(k)
        p = K / N
        c = p + z ** 2 / (2 * N)
        d = 1 + z ** 2 / N
        h = z * mp.sqrt(p * (1 - p) / N + z ** 2 / (4 * N ** 2))
        b = (float((c - h) / d * 100), float((c + h) / d * 100))
    except ImportError:
        pass
    return a, b


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n")[0])
    ap.add_argument("--pattern", default="commissioning_arm*")
    args = ap.parse_args()

    rows = survey(args.pattern)
    reported = [r for r in rows if r["reported"]]
    print("EVERY COMMISSIONING-ARM RUN THAT PRODUCED A REPORT")
    print("=" * 108)
    print(f"{'run':<46}{'report reason':<32}{'signal':<16}{'rds':>4}{'find':>5}{'wall_s':>8}")
    for r in reported:
        print(f"{r['run']:<46}{str(r['report_reason'])[:31]:<32}"
              f"{str(r['signal_reason'])[:15]:<16}{str(r['rounds']):>4}"
              f"{str(r['findings']):>5}{round(r['wall_s'] or 0):>8}")

    n = len(reported)
    conv = [r for r in reported if "CONVERGED" in str(r["report_reason"]).upper()]
    halt = [r for r in reported if "HALTED" in str(r["report_reason"]).upper()]
    silent = [r for r in reported if r["report_reason"] is None]
    disagree = [r for r in reported
                if (r["report_reason"] or "") != (r["signal_reason"] or "")]

    print()
    print(f"  runs with a report                 {n}")
    print(f"  CONVERGED                          {len(conv)}")
    print(f"  HALTED on an alarm                 {len(halt)}")
    print(f"  report records NO stop reason      {len(silent)}")
    print(f"  report and signal DISAGREE         {len(disagree)}")
    if n:
        sm, mpm = wilson(len(conv), n)
        print(f"\n  CONVERGENCE RATE {len(conv)} of {n} = {len(conv)/n*100:.4f}%")
        if sm:
            print(f"    statsmodels Wilson 95% [{sm[0]:.4f}%, {sm[1]:.4f}%]")
        if mpm:
            print(f"    mpmath      Wilson 95% [{mpm[0]:.4f}%, {mpm[1]:.4f}%]")
        if sm and mpm:
            print(f"    tools agree to {max(abs(sm[0]-mpm[0]), abs(sm[1]-mpm[1])):.2e} pp")
        if not sm or not mpm:
            print("    ONLY 1 TOOL AVAILABLE — the cross-verification rule is NOT "
                  "satisfied and this interval is reported as unconfirmed.")

    print("\n  BY TARGET")
    for t, c in Counter(str(r["target"]) for r in reported).items():
        tc = [r for r in reported if str(r["target"]) == t]
        cc = sum(1 for r in tc if "CONVERGED" in str(r["report_reason"]).upper())
        hh = sum(1 for r in tc if "HALTED" in str(r["report_reason"]).upper())
        print(f"    {t:<46} {cc} converged, {hh} halted, of {c}")

    print("\n  ROUNDS AT WHICH A CONVERGED RUN CONVERGED")
    print(f"    {sorted(r['rounds'] for r in conv)}")
    print("  ROUNDS AT WHICH A HALTED RUN HALTED")
    print(f"    {sorted(r['rounds'] for r in halt)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
