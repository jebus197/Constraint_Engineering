#!/usr/bin/env python3
"""How many findings claim tool verification on an instrument already voided?

WHY THIS EXISTS, and what it decides. `shakedown_2026-09-29/arm1_harvest/C0041`
stands at status CONFIRMED with `verified=true` and severity 0.8 while its
`falsifier_verdict` is `NON_DISCRIMINATING` -- the discrimination control voided
the instrument and the record still asserts the finding was verified by a tool.
The star-round seat that found it reported it without changing it, correctly, as
the founder's decision.

THE MECHANISM, traced in `bench/reference_runner_v3.py`. The control sets
`entry["verified"] = False` when it voids an instrument. Two steps later, in the
RECORD-ONLY (non-blocking) branch of the same gate, the gate unconditionally
runs `registry.resolve(cid, "CONFIRMED", round_idx)` and `e["verified"] = True`.
The control's correction is overwritten by the gate that called it.

WHY THE SIZE OF THIS POPULATION IS THE WHOLE QUESTION. `verified` is read by the
halt bound through `unverified_critical_count`, so correcting it moves a
convergence input. The founder refused to arm `discrimination_control_blocks` on
a measured basis -- 126 of 246 fixes do not silence their own falsifier -- and
that refusal would extend to any correction of comparable breadth. If this
population is a handful, the measured objection does not transfer and the
correction is narrow; if it is broad, it is the same decision in disguise and
belongs to him.

Usage:  python3 scripts/verified_on_a_voided_instrument_2026-10-03.py [--json]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


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
    assert abs(float(c - h) - lo) < 1e-9 and abs(float(c + h) - hi) < 1e-9
    return {"k": k, "n": n, "pct": round(100.0 * k / n, 4),
            "wilson": [round(100 * lo, 4), round(100 * hi, 4)]}


def main(argv: list[str] | None = None) -> int:
    # A REAL PARSER, NOT A HAND-ROLLED argv SCAN. The first version read
    # `sys.argv` directly, so an unrecognised flag was SILENTLY IGNORED and the
    # script exited 0 -- the shape `bench/tests/test_operational_scripts.py`
    # calls "the 118-day no-op again", and the reason the project's rule is
    # that a documented command must either work or fail loudly.
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0],
        epilog="Every figure is recomputed from the archive on each run.")
    ap.add_argument("--json", action="store_true",
                    help="emit the full record as JSON instead of a report")
    a = ap.parse_args(argv)
    argv = ["--json"] if a.json else []
    entries = voided = voided_and_verified = voided_and_terminal = 0
    where = []
    for f in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except (ValueError, OSError):
            continue
        for cid, e in ((d.get("registry") or {}).get("entries") or {}).items():
            if not isinstance(e, dict):
                continue
            entries += 1
            if (e.get("falsifier_verdict") or "") != "NON_DISCRIMINATING":
                continue
            voided += 1
            term = e.get("status") in ("CONFIRMED", "CLOSED", "CORROBORATED")
            if term:
                voided_and_terminal += 1
            if e.get("verified") is True:
                voided_and_verified += 1
                where.append({"run": str(f.parent.relative_to(REPO / "bench" / "logs")),
                              "cid": cid, "status": e.get("status"),
                              "severity": e.get("severity"),
                              "escalated": e.get("escalated"),
                              "mechanical_fault": e.get("mechanical_fault")})
    out = {
        "registry_entries_scanned": entries,
        "falsifier_voided_NON_DISCRIMINATING": wilson(voided, entries),
        "voided_AND_terminal_status": wilson(voided_and_terminal, max(voided, 1)),
        "voided_AND_verified_true": wilson(voided_and_verified, max(voided, 1)),
        "instances": where,
    }
    if "--json" in argv:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    print("VERIFIED ON A VOIDED INSTRUMENT")
    print(f"  registry entries scanned        : {entries}")
    for label, key in (("falsifier voided", "falsifier_voided_NON_DISCRIMINATING"),
                       ("of those, terminal status", "voided_AND_terminal_status"),
                       ("of those, verified=true", "voided_AND_verified_true")):
        v = out[key]
        print(f"  {label:32s}: {v['k']} of {v['n']}"
              + (f" = {v['pct']}%, Wilson [{v['wilson'][0]}%, {v['wilson'][1]}%]"
                 if v["pct"] is not None else ""))
    print("  instances:")
    for i in where:
        print(f"    {i['run']}/{i['cid']}  status={i['status']} "
              f"sev={i['severity']} escalated={i['escalated']} "
              f"mech_fault={i['mechanical_fault']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
