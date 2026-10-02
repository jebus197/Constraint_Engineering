# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'integrity_advisory_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a7f947c97556059b33b8f0067fa8187874265e115574ca9692a17164183fb914
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""CONFIRMED-hit rate over every archived run, with 3 interval estimators.

Reports the rate BEFORE and AFTER the D3 precision fixes by reading the tiers the
scanner now emits: a hit that D3 set aside still exists on the Report, so
`len(confirmed) + len(set_aside)` reconstructs the pre-fix count exactly, with no
need to check out the old code. SUSPICION demotions are counted separately,
because those hits also used to be CONFIRMED.

Usage: python3 scripts/forensics_archive_census_2026-10-02.py [--json OUT]
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from bench.key_access_forensics import scan_run, CONFIRMED, SUSPECT  # noqa: E402

DEMOTED_MARK = "demoted to suspicion, NOT exempted"


def interval(k: int, n: int) -> dict:
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import beta as sbeta
    import mpmath as mp
    if n == 0:
        return {"k": k, "n": n}
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054"); p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / d
    h = z * mp.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    cp_lo = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n-k+1))
    cp_hi = 1.0 if k == n else float(sbeta.ppf(0.975, k+1, n-k))
    return {"k": k, "n": n, "pct": 100.0*k/n,
            "wilson_statsmodels": [100*lo, 100*hi],
            "wilson_mpmath": [100*float(c-h), 100*float(c+h)],
            "tools_agree": abs(float(c-h)-lo) < 1e-9 and abs(float(c+h)-hi) < 1e-9,
            "clopper_pearson": [100*cp_lo, 100*cp_hi]}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--json", type=pathlib.Path)
    a = ap.parse_args()
    logs = REPO / "bench" / "logs"
    runs = sorted(d for d in logs.iterdir()
                  if d.is_dir() and any(d.rglob("*.json")))
    rows, t0 = {}, time.time()
    for d in runs:
        try:
            rep = scan_run(d)
        except Exception as exc:  # noqa: BLE001
            rows[d.name] = {"ERROR": f"{type(exc).__name__}: {exc}"}
            continue
        aside = rep.set_aside
        demoted = [h for h in rep.hits
                   if h.tier == SUSPECT and DEMOTED_MARK in h.label]
        rows[d.name] = {
            "confirmed_after": len(rep.confirmed),
            "set_aside": len(aside),
            "demoted_to_suspicion": len(demoted),
            "confirmed_before": len(rep.confirmed) + len(aside) + len(demoted),
            "files": rep.files_scanned, "unreadable": len(rep.unreadable)}
    ok = [r for r in rows.values() if "ERROR" not in r]
    out = {
        "runs_scanned": len(runs),
        "errors": len(rows) - len(ok),
        "elapsed_s": round(time.time() - t0, 1),
        "rate_before": interval(sum(1 for r in ok if r["confirmed_before"] > 0), len(ok)),
        "rate_after": interval(sum(1 for r in ok if r["confirmed_after"] > 0), len(ok)),
        "still_confirmed": sorted(k for k, r in rows.items()
                                  if "ERROR" not in r and r["confirmed_after"] > 0),
        "newly_clean": sorted(k for k, r in rows.items()
                              if "ERROR" not in r and r["confirmed_before"] > 0
                              and r["confirmed_after"] == 0),
        "per_run": rows,
    }
    txt = json.dumps(out, indent=1, sort_keys=True)
    if a.json:
        a.json.write_text(txt, encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_run"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
