#!/usr/bin/env python3
"""Reproduce, or refute, the 3 competing causes of falsifier supply failure.

Each was reported by an adversarial pass with no committed producer. A number
that exists only as prose is a claim about evidence, not evidence. This script
is the attempt to turn them into evidence, and it reports failure to reproduce
as loudly as success.

Every odds ratio and p-value is computed by scipy AND by an independent mpmath
hypergeometric sum; disagreement is printed rather than hidden.
"""
from __future__ import annotations
import json, pathlib, re, sys
from collections import Counter

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CRIT = 0.7

def fisher(a, b, c, d):
    from scipy.stats import fisher_exact
    import mpmath as mp
    odds, p = fisher_exact([[a, b], [c, d]])
    mp.mp.dps = 50
    n = a+b+c+d; r1, c1 = a+b, a+c
    def pr(x):
        return (mp.binomial(c1, x)*mp.binomial(n-c1, r1-x))/mp.binomial(n, r1)
    obs = pr(a); tot = mp.mpf(0)
    for x in range(max(0, r1-(n-c1)), min(r1, c1)+1):
        q = pr(x)
        if q <= obs*(1+mp.mpf("1e-30")): tot += q
    return odds, p, float(tot)

def entries():
    rows = {}
    for name in ("runner_state.json", "*_report.json"):
        for f in sorted((ROOT/"bench"/"logs").glob(f"*/{name}")):
            try: data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception: continue
            cfg = data.get("config") or {}
            tgt = str(cfg.get("target_file") or data.get("target_file") or "")
            for cid, e in ((data.get("registry") or {}).get("entries") or {}).items():
                if not isinstance(e, dict) or (e.get("severity") or 0) < CRIT: continue
                key = (f.parent.name, cid)
                body = ((e.get("falsifier_code") or "").strip()
                        or (e.get("last_falsifier_code") or "").strip())
                prev = rows.get(key)
                if prev is None or (not prev[2] and body):
                    rows[key] = (f.parent.name, tgt, body, e)
    return rows

def expno(r):
    m = re.match(r"exp(\d+)", r); return int(m.group(1)) if m else None

FILE_RE = re.compile(r"[\w./-]+\.(?:py|md|json|toml|txt|csv|yaml|yml)\b")

def main():
    rows = entries()
    post = {k: v for k, v in rows.items()
            if expno(k[0]) is None or expno(k[0]) >= 42}
    print(f"post-feature criticals: {len(post)}\n")

    def verdict(e):
        h = e.get("routing_history") or []
        return ((e.get("falsifier_verdict") or "").strip().upper()
                or (e.get("routing_verdict_unreconciled") or "").strip().upper()
                or ((h[-1].get("verdict") or "").strip().upper() if h else ""))

    # ── CAUSE 1: does naming a concrete file predict ERROR? ────────────────
    a=b=c=d=0
    for (run, cid), (r, tgt, body, e) in post.items():
        v = verdict(e)
        if v not in ("ERROR", "CONFIRMED") or not body: continue
        named = bool(FILE_RE.search(body))
        if v == "ERROR": a, b = a + named, b + (not named)
        else:            c, d = c + named, d + (not named)
    print("CAUSE 1  over-specificity: naming a concrete file vs ERROR")
    print(f"  ERROR     named {a:4d}  unnamed {b:4d}")
    print(f"  CONFIRMED named {c:4d}  unnamed {d:4d}")
    if a+b and c+d:
        o, p, pm = fisher(a, b, c, d)
        print(f"  Fisher OR = {o:.4f}  scipy p = {p:.6e}  mpmath p = {pm:.6e}  "
              f"agree={abs(p-pm) < 1e-9}")
        print(f"  claimed: OR 4.3049, p = 0.000251448 -> "
              f"{'REPRODUCED' if abs(o-4.3049) < 0.05 else 'NOT REPRODUCED'}")

    # ── CAUSE 2: zero-plant controls ───────────────────────────────────────
    a=b=c=d=0
    for (run, cid), (r, tgt, body, e) in post.items():
        ctrl = ("control" in run.lower() or "zero" in run.lower())
        nobody = not body and not verdict(e)
        if ctrl: a, b = a + nobody, b + (not nobody)
        else:    c, d = c + nobody, d + (not nobody)
    print("\nCAUSE 2  zero-plant controls: no falsifier at all")
    print(f"  control runs  no-body {a:4d}  other {b:4d}")
    print(f"  live runs     no-body {c:4d}  other {d:4d}")
    if a+b and c+d:
        o, p, pm = fisher(a, b, c, d)
        print(f"  Fisher OR = {o}  scipy p = {p:.6e}  mpmath p = {pm:.6e}  "
              f"agree={abs(p-pm) < 1e-9}")
        print(f"  claimed: 19 of 46, OR 14.9614, p = 6.39737e-12 -> "
              f"{'REPRODUCED' if (a, b) == (19, 46-19) else 'NOT REPRODUCED (counts differ)'}")

    # ── CAUSE 3: prose vs code targets ─────────────────────────────────────
    a=b=c=d=0
    for (run, cid), (r, tgt, body, e) in post.items():
        t = tgt.lower()
        nobody = not body and not verdict(e)
        if t.endswith(".md"):   a, b = a + nobody, b + (not nobody)
        elif t.endswith(".py"): c, d = c + nobody, d + (not nobody)
    print("\nCAUSE 3  prose vs code targets: no falsifier at all")
    print(f"  prose (.md)  no-body {a:4d}  other {b:4d}")
    print(f"  code  (.py)  no-body {c:4d}  other {d:4d}")
    if a+b and c+d:
        o, p, pm = fisher(a, b, c, d)
        print(f"  Fisher OR = {o}  scipy p = {p:.6e}  mpmath p = {pm:.6e}  "
              f"agree={abs(p-pm) < 1e-9}")
        print(f"  claimed: 18 of 123 vs 11 of 357, OR 5.3922 -> "
              f"{'REPRODUCED' if (a, a+b, c, c+d) == (18, 123, 11, 357) else 'NOT REPRODUCED (counts differ)'}")
    return 0

if __name__ == "__main__":
    # A `--help` must never cost anything (founder ruling).
    answer_help(__doc__, __file__)
    raise SystemExit(main())
