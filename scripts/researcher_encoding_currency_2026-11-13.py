#!/usr/bin/env python3
"""Is a researcher's encoding current, and has anything been tampered with?

B185. An expert encoding cites standards, and standards are revised. Nothing in
this project recorded WHEN a standard was last checked: 1 of 52 encodings
carried a confirmation date, 0.019231, Wilson [0.0034, 0.1012]. Without that
field an encoding cannot be compared against upstream at all.

★ WHAT THIS DOES AND WHAT IT CANNOT DO. It reports which standards are DUE for
re-confirmation by age, and whether the standards file has changed since it was
last sealed. It does NOT reach the network and does not claim a standard is
unchanged -- a checker that pretended to would assert what it cannot observe.
Confirming is a human or panel act; this records and schedules it.

★ WHY 3 FILES. standards.toml changes about 0.976190 times a year;
confirmations.toml changes on every session start, about 1370 times a year at a
measured 3.75 starts per day. Held together, a content hash over the pair has a
tamper-alert precision of 0.00071220 -- 99.93 per cent of alerts would be
benign, and an alarm nobody can act on is worse than none. Split, the standards
file changes only when a standard does, so the precision is 1.0. A 1404.0952x
improvement on a named property, which is why the split is the design.

★ THE CADENCE IS MEASURED AGAINST HIS OWN WORKING PATTERN, not chosen.
exposure = lambda * T / 730.5, lambda in revisions per year, T in days. The run
rate cancels: this cannot be improved by running more or fewer experiments. On
a boot trigger the expected undetected window is E[G^2]/(2E[G]) = 0.412371 days
-- the inspection paradox, 2.9574x worse than E[G]/2 because a revision is more
likely to land in a long gap -- giving an exposure of 0.00056451 against
0.020534 for a 30-day calendar. 0 of 74 measured session gaps exceeded the
14.61-day ceiling, so the backstop covers absences and nothing else.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import pathlib
import sys
import tomllib

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "bench" / "directives" / "researchers"

#: Revisions per year, from each standard's OWN published history.
LAMBDA = {"FMEA": 0.111111, "CTCAE": 0.142857, "CVSS": 0.222222, "GHS": 0.5}


def exposure(lam_per_year: float, days: float) -> float:
    """Fraction of runs sitting in a stale window, at check interval `days`.

    The closed form is lambda*T/730.5 and the RUN RATE CANCELS, which is why
    this is a property of the cadence alone.
    """
    return lam_per_year * days / 730.5


def backstop_for(ceiling: float, lam_per_year: float) -> float:
    """The longest interval that keeps exposure under `ceiling`."""
    return ceiling * 730.5 / lam_per_year


def _load(path: pathlib.Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def researchers() -> list[str]:
    if not ROOT.is_dir():
        return []
    return sorted(d.name for d in ROOT.iterdir()
                  if d.is_dir() and not d.name.startswith("_")
                  and (d / "standards.toml").is_file())


def check(name: str, today: _dt.date | None = None) -> dict:
    """Report what is due, what is silent, and whether the seal still holds."""
    today = today or _dt.date.today()
    d = ROOT / name
    std_p, conf_p = d / "standards.toml", d / "confirmations.toml"
    out: dict = {"researcher": name, "due": [], "ok": [], "exempt": [],
                 "unconfirmed": [], "standards_digest": digest(std_p)}
    conf = _load(conf_p) if conf_p.is_file() else {}
    policy = conf.get("policy", {})
    ceiling = float(policy.get("exposure_ceiling", 0.01))
    backstop = int(policy.get("backstop_days", 14))
    out["ceiling"], out["backstop_days"] = ceiling, backstop

    std = _load(std_p)
    cited: list[tuple[str, str]] = []
    for dom, block in (std.get("domains") or {}).items():
        if not isinstance(block, dict):
            continue
        scale = block.get("severity_scale")
        if scale and scale != "none":
            cited.append((dom, scale))
        elif scale == "none":
            out["exempt"].append((dom, block.get("severity_scale_reason", "")))

    confirmed = conf.get("confirmed") or {}
    by_scale = {}
    for key, rec in confirmed.items():
        if isinstance(rec, dict):
            by_scale[str(rec.get("standard", key))] = rec

    for dom, scale in cited:
        rec = by_scale.get(scale)
        if not rec or not rec.get("last_confirmed"):
            out["unconfirmed"].append((dom, scale))
            continue
        when = _dt.date.fromisoformat(str(rec["last_confirmed"]))
        age = (today - when).days
        row = (dom, scale, str(when), age)
        (out["due"] if age > backstop else out["ok"]).append(row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--researcher", help="limit to one researcher")
    ap.add_argument("--exposure-table", action="store_true",
                    help="print the cadence table and exit")
    a = ap.parse_args()

    if a.exposure_table:
        print("  exposure = lambda * T / 730.5   (the run rate cancels)\n")
        print(f"  {'T (days)':>10}  " + "  ".join(f"{k:>10}" for k in LAMBDA))
        for T in (1, 7, 14, 30, 90, 180, 365):
            print(f"  {T:>10}  " + "  ".join(
                f"{exposure(v, T):>10.6f}" for v in LAMBDA.values()))
        print("\n  1 per cent ceiling needs a backstop of:")
        for k, v in LAMBDA.items():
            print(f"    {k:<6} {backstop_for(0.01, v):8.4f} days")
        return 0

    names = [a.researcher] if a.researcher else researchers()
    if not names:
        print("  no researcher encodings found; layer 3 is empty")
        return 0
    bad = 0
    for n in names:
        r = check(n)
        print(f"\n  RESEARCHER: {r['researcher']}")
        print(f"    standards.toml sha256 : {r['standards_digest'][:16]}")
        print(f"    exposure ceiling      : {r['ceiling']}  -> backstop "
              f"{r['backstop_days']} days")
        for dom, scale, when, age in r["ok"]:
            print(f"    [  OK  ] {dom}: {scale} confirmed {when} ({age} days ago)")
        for dom, reason in r["exempt"]:
            print(f"    [EXEMPT] {dom}: declares no scale -- {reason[:60]}")
        for dom, scale, when, age in r["due"]:
            bad += 1
            print(f"    [ DUE  ] {dom}: {scale} confirmed {when}, {age} days "
                  f"ago, past the {r['backstop_days']}-day backstop")
        for dom, scale in r["unconfirmed"]:
            bad += 1
            print(f"    [ NONE ] {dom}: {scale} has NO confirmation date at all")
    print(f"\n  {bad} standard(s) need confirming." if bad
          else "\n  every cited standard is within its backstop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
