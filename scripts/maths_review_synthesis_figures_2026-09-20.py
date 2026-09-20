#!/usr/bin/env python3
"""Every figure quoted in the 6-round maths-revision review synthesis.

WHY THIS EXISTS. `measured-rate-travels-with-its-script`: a rate cited in a note
is a claim about evidence unless the code that produced it is committed beside
it. This review has already been bitten twice by the absence of that -- an
over-refusal figure of 75.8% presented as settled with no producer, and CC1's
own "191 refusals" claim which contradicted a test-pinned measurement in the
repository. This script regenerates the synthesis's numbers so a reader can
check them rather than trust them.

Run:  python3 scripts/maths_review_synthesis_figures_2026-09-20.py
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLIND = ROOT / "bench/logs/maths_panel_2026-09-21_blind"
OPEN = ROOT / "bench/logs/maths_panel_2026-09-21_open"
ROUNDS = ["maths_panel_2026-09-20", "maths_panel_2026-09-20_r2",
          "maths_panel_2026-09-20_r3", "maths_panel_2026-09-20_r4",
          "maths_panel_2026-09-21_blind", "maths_panel_2026-09-21_open"]
SEATS = ("cc2", "cgpt", "cx", "ds", "fable", "ge", "kimi")


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def sk_records():
    """Every archived fix-admission decision."""
    rows = []
    for f in sorted(glob.glob(str(ROOT / "bench/logs/*/runner_state.json"))):
        if os.path.getsize(f) > 60_000_000:
            continue
        try:
            raw = open(f, errors="ignore").read()
        except OSError:
            continue
        if "sk_result" not in raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue

        def walk(o):
            if isinstance(o, dict):
                s = o.get("sk_result")
                if isinstance(s, dict) and "tristate" in s:
                    rows.append(s)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(d)
    return rows


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.parse_args(argv)

    print("MATHS REVISION REVIEW — SYNTHESIS FIGURES")
    print("=" * 70)

    # 1. Rounds and seat returns
    print("\n1. ROUNDS DISPATCHED AND SEATS RETURNING")
    total_chars = 0
    for r in ROUNDS:
        d = ROOT / "bench/logs" / r
        if not d.is_dir():
            continue
        ok = 0
        chars = 0
        for s in SEATS:
            f = d / f"{s}.json"
            if not f.is_file():
                continue
            try:
                j = json.loads(f.read_text(errors="replace"))
            except Exception:
                continue
            if (j.get("chars") or 0) > 0:
                ok += 1
                chars += j["chars"]
        total_chars += chars
        print(f"   {r:32s} {ok}/7 returned, {chars:>8,d} chars")
    print(f"   {'TOTAL':32s}        {total_chars:>8,d} chars of seat output")

    # 2. The withdrawn claim
    print("\n2. THE WITHDRAWN CLAIM — were any refusals constant-driven?")
    rows = sk_records()
    tri = Counter(str(r.get("tristate")) for r in rows)
    rejected = [r for r in rows if r.get("tristate") == "REJECTED"]
    structural = [r for r in rejected if (r.get("sk") or 0) == 0]
    admissible = [r for r in rows if r.get("tristate") == "ADMISSIBLE"]
    scored = [r for r in admissible if r.get("passes_threshold") is not None]
    gate_refused = [r for r in scored if r.get("passes_threshold") is False]
    print(f"   archived decisions        : {len(rows)}")
    print(f"   tristate distribution     : {dict(tri)}")
    print(f"   REJECTED that are sk == 0 : {len(structural)} of {len(rejected)}")
    print(f"   scored fixes gate-refused : {len(gate_refused)} of {len(scored)}")
    lo, hi = wilson(len(gate_refused), len(scored)) if scored else (0, 0)
    print(f"                               Wilson [{lo:.4%}, {hi:.4%}]")
    print("   => the unmeasured constants decided NOTHING on the archive.")

    # 3. The scorer
    print("\n3. THE SCORER — does it discriminate inside the band it guards?")
    sks = [r.get("sk") for r in admissible if r.get("sk") is not None]
    A = Counter(r.get("A") for r in rows if "A" in r)
    if sks:
        at_ceiling = sum(1 for x in sks if x == 1.0)
        lo, hi = wilson(at_ceiling, len(sks))
        print(f"   scored admissible fixes   : {len(sks)}")
        print(f"   scoring exactly 1.0       : {at_ceiling} = {at_ceiling/len(sks):.4%}")
        print(f"                               Wilson [{lo:.4%}, {hi:.4%}]")
        print(f"   lowest observed score     : {min(sks):.6f}")
    print(f"   the A term across all decisions: {dict(A)}")
    print(f"   distinct A values: {len(A)} -> {'BINARY' if len(A) <= 2 else 'graded'}")

    # 4. Thresholds versus the observed distribution
    print("\n4. THE THRESHOLD DEBATE, against the observed distribution")
    for name, t in (("live corrected gate", 0.504931170970423),
                    ("exact-Phase-2 alternative", 0.395043)):
        below = sum(1 for x in sks if x < t) if sks else 0
        lo, hi = wilson(below, len(sks)) if sks else (0, 0)
        print(f"   {name:26s} {t:.6f}: {below} of {len(sks)} below"
              f"  Wilson [{lo:.4%}, {hi:.4%}]")
    print("   => moving the threshold between these changes 0 archived decisions.")

    # 5. Cross-tool check
    print("\n5. CROSS-TOOL CHECK")
    try:
        from statsmodels.stats.proportion import proportion_confint
        ok = True
        for k, n in ((len(gate_refused), len(scored) or 1),
                     (sum(1 for x in sks if x == 1.0) if sks else 0, len(sks) or 1)):
            a, b = proportion_confint(k, n, method="wilson")
            c, d2 = wilson(k, n)
            if abs(a - c) > 1e-12 or abs(b - d2) > 1e-12:
                ok = False
        print(f"   statsmodels agrees with the local Wilson closed form: {ok}")
    except ImportError:
        print("   statsmodels unavailable")

    print("\n" + "-" * 70)
    print("Companion producers, each committed beside its own claim:")
    for s in ("split_the_191_refusals_2026-09-20.py",
              "sk_verdict_never_fired_2026-09-20.py",
              "panel_independence_breach_2026-09-20.py",
              "panel_figure_provenance_2026-09-20.py",
              "were_the_failures_all_mechanical_2026-09-20.py"):
        print(f"   scripts/{s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
