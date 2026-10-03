#!/usr/bin/env python3
"""Probe a FINISHED run's falsifiers for the cannot-fail shape.

WHAT IT IS. The discrimination control can only act where a corrected copy was
supplied with the falsifier; measured over the archive, 0 entries carry its
NO_CONTROL stamp, because the applier returns before the control is called on
that population (`scripts/discrimination_reach_2026-10-03.py`). Both seats of
the 2026-10-03 panel refused a second standalone template and named the same
additive move: synthesise the missing side. `invariance_probe` in the runner
does that -- it runs the falsifier against the unchanged target, against the
target emptied, and against the target duplicated, and reports whether the
verdict ever moves. A verdict that never moves is not reading the target to
decide, which is non-discrimination whatever the claim was.

WHY A SWEEP AND NOT A HOOK INSIDE THE RUN. An overlay build at the real
repository root measures 14.034 s, so 2 overlays per probed finding per round
would add roughly 187 minutes to a run, for a statistic nothing in the
convergence path reads. A sweep pays that cost once per DISTINCT falsifier,
after the run, where it cannot perturb what it measures.

ONE-SIDEDNESS, restated because it decides how the output may be read.
`invariant: true` demonstrates the falsifier cannot fail. `invariant: false`
demonstrates NOTHING about whether it tests its claim -- only that its verdict
depends on the target's content somehow. There is no outcome here that clears a
falsifier.

Usage:
  python3 scripts/invariance_sweep_2026-10-03.py --run bench/logs/<run dir>
  python3 scripts/invariance_sweep_2026-10-03.py --run <dir> --limit 10 --out rec.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"k": k, "n": n, "pct": None}
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo, hi = proportion_confint(k, n, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9, (
        f"statsmodels and mpmath disagree on Wilson for {k}/{n}")
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def _registry(run: pathlib.Path) -> dict:
    for name in ("runner_state.json",):
        f = run / name
        if f.is_file():
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            return ((d.get("registry") or {}).get("entries") or {}), d
    for f in sorted(run.glob("*_report.json")):
        d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        return ((d.get("registry") or {}).get("entries") or {}), d
    return {}, {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", default=None,
                    help="a finished run directory under bench/logs")
    ap.add_argument("--target", default="",
                    help="target file the falsifiers review; read from the "
                         "run's own config when omitted")
    ap.add_argument("--limit", type=int, default=0,
                    help="probe at most this many distinct falsifiers "
                         "(0 = all). A limit is REPORTED, never silent.")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--out", help="write the full record here as JSON")
    a = ap.parse_args(argv)

    # CHECKED AFTER PARSING, NOT DECLARED `required=True`, so that an
    # UNRECOGNISED flag is reported as unrecognised. argparse resolves a
    # missing required argument FIRST, so a typo'd flag was answered with
    # "the following arguments are required" and the real mistake -- a flag
    # this script does not have -- went unnamed. Behaviour for a genuinely
    # missing argument is unchanged: argparse still errors with exit 2.
    if not getattr(a, 'run', None):
        ap.error("--run is required")

    from bench.reference_runner_v3 import invariance_probe

    run = pathlib.Path(a.run)
    if not run.is_absolute():
        run = REPO / run
    entries, whole = _registry(run)
    if not entries:
        print(f"no registry found under {run}", file=sys.stderr)
        return 1

    target = a.target or (whole.get("config") or {}).get("test_article") or ""
    if not target:
        print("no target article: pass --target", file=sys.stderr)
        return 1

    # One probe per DISTINCT falsifier body: the shape being tested is a
    # property of the falsifier, so probing the same body twice buys nothing.
    bodies: dict[str, list[str]] = {}
    for cid, e in entries.items():
        if not isinstance(e, dict):
            continue
        code = (e.get("falsifier_code") or "").strip()
        if not code:
            continue
        if (e.get("corrected_copy") or "").strip():
            continue              # the real control can speak here; this cannot
        bodies.setdefault(code, []).append(cid)

    order = sorted(bodies, key=lambda c: sorted(bodies[c])[0])
    skipped = 0
    if a.limit and len(order) > a.limit:
        skipped = len(order) - a.limit
        order = order[:a.limit]

    rows, t0 = [], time.perf_counter()
    for code in order:
        verdict = ""
        for cid in bodies[code]:
            verdict = (entries[cid].get("falsifier_verdict") or "").strip()
            if verdict:
                break
        rec = invariance_probe(code, REPO, target, verdict or "CONFIRMED",
                               kwargs={"timeout": a.timeout})
        rows.append({"cids": sorted(bodies[code]), "verdict": verdict,
                     "probe": rec})
        flag = ("CANNOT FAIL" if rec.get("invariant") is True
                else "reads its target" if rec.get("invariant") is False
                else "indeterminate")
        print(f"  {sorted(bodies[code])[0]:>8s} ({len(bodies[code])} cid) "
              f"verdict={verdict or '?':<16s} -> {flag}")
    elapsed = time.perf_counter() - t0

    ran = [r for r in rows if r["probe"].get("ran")]
    inv = [r for r in ran if r["probe"].get("invariant") is True]
    out = {
        "run": str(run.relative_to(REPO)) if str(run).startswith(str(REPO)) else str(run),
        "target": target,
        "distinct_falsifiers_without_a_corrected_copy": len(bodies),
        "probed": len(rows), "skipped_by_limit": skipped,
        "probe_ran": len(ran),
        "cannot_fail": wilson(len(inv), max(len(ran), 1)),
        "elapsed_seconds": round(elapsed, 1),
        "one_sided": ("invariant=true demonstrates cannot-fail; invariant=false "
                      "demonstrates nothing about discrimination"),
        "rows": rows,
    }
    print(f"\nSWEEP: {len(rows)} probed of "
          f"{out['distinct_falsifiers_without_a_corrected_copy']} distinct "
          f"falsifiers with no corrected copy"
          + (f"; {skipped} SKIPPED BY --limit" if skipped else ""))
    c = out["cannot_fail"]
    if c["pct"] is not None:
        print(f"  cannot-fail: {c['k']} of {c['n']} = {c['pct']}%, "
              f"Wilson [{c['wilson'][0]}%, {c['wilson'][1]}%]")
    print(f"  wall clock: {out['elapsed_seconds']} s")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=2))
        print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
