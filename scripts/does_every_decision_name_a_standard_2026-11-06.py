#!/usr/bin/env python3
"""RULE 33 COMPLIANCE over the live decisions -- producer, 2026-11-06.

RULE 33 of note standard v1.9 requires a numbered decision to carry a
recommendation that NAMES one of the project's 3 formal standards: additive,
simplest sufficient, or composability. The rule exists because the file he
rejected on 2026-10-29 carried 0 recommendations across 6 open decisions and
used all 3 words 0 times.

WHY THIS IS MEASURED AND NOT ASSERTED. On 2026-11-06 his morning report named
3 things awaiting him when the record tracked 29, and the gap was invisible
because nothing counted. This script counts, so the claim that his queue is
rulable is a measurement rather than an impression.

BOTH HALVES ARE COUNTED SEPARATELY, because they fail independently: a
decision can carry a recommendation that argues nothing against any standard,
which is the weak form Rule 33 was written to stop.

Every proportion carries 2 interval families, each by 2 routes.
"""
from __future__ import annotations

import pathlib as _pl, sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _cli_help import answer_help as _answer_help  # noqa: E402
import importlib.util, json, pathlib, re, sys

from statsmodels.stats.proportion import proportion_confint
from scipy.stats import beta as _beta
import mpmath as mp

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
DETAIL = REPO / "experimental_notes" / "data" / "morning_report_decisions.json"
SURFACES = REPO / "scripts" / "do_the_two_decision_surfaces_agree_2026-11-01.py"

STANDARD = re.compile(r"additive|simplest sufficient|composab", re.I)
RECOMMENDS = re.compile(r"this is the recommendation|\brecommend", re.I)


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    wl2, wh2 = float(cen - half), float(cen + half)
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - wl2), abs(hi - wh2), abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label, k, n):
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"routes disagree by {dis}"
    return k, n


def main() -> int:
    spec = importlib.util.spec_from_file_location("sf_r33", SURFACES)
    sf = importlib.util.module_from_spec(spec)
    sys.modules["sf_r33"] = sf
    spec.loader.exec_module(sf)

    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    live = [i for i, _h in sf.derived()]
    print(f"live decisions awaiting him: {len(live)}")

    def blob(ident):
        for k in (ident, f"task:{ident}", f"study:{ident}"):
            v = detail.get(k)
            if isinstance(v, dict):
                return json.dumps(v)
        return ""

    rec = [i for i in live if RECOMMENDS.search(blob(i))]
    std = [i for i in live if STANDARD.search(blob(i))]
    print()
    _show("carry a recommendation", len(rec), len(live))
    _show("name one of the 3 standards", len(std), len(live))

    gaps_rec = sorted(set(live) - set(rec))
    gaps_std = sorted(set(live) - set(std))
    print(f"\n  no recommendation ({len(gaps_rec)}): {', '.join(gaps_rec) or 'none'}")
    print(f"  no standard named ({len(gaps_std)}): {', '.join(gaps_std) or 'none'}")
    print("\nANTI-VACUITY: the counts above are meaningless on an empty queue.")
    assert len(live) >= 5, f"only {len(live)} live decisions; the rates say little"
    return 0


if __name__ == "__main__":
    #: ★ THE CALL BELONGS HERE AND NOT AT MODULE LEVEL. Placed at
    #: module level it runs on IMPORT, and `answer_help` exits 2 on an
    #: unrecognised argument -- so importing this file under pytest, whose
    #: argv is its own, raised SystemExit: 2 and took 12 tests in
    #: test_an_interval_rests_on_two_routes_2026-11-03 down with it. One
    #: guard was satisfied by breaking another.
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
