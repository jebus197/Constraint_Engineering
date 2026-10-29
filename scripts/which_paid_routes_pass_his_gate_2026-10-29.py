#!/usr/bin/env python3
"""How many entry points can reach a PAID route without consulting his ledger?

HIS RULING, 2026-10-29, annotation 3 of
`Responses/Decisions_Awaiting_You_2026-10-29.txt`: *"This is declined. No paid
dispatch can happen without my express authorisation."*

THE GOOD NEWS FIRST, because it is the instrument that already exists.
`bench/confer_maths_panel_2026-09-05.py` implements exactly what he describes:
`select_models` refuses any named paid seat unless an authorisation ledger
carries his verbatim words for that round, and EVERY failure path -- missing
file, unreadable file, wrong schema, unnamed round, a quote under the minimum
length -- returns False. So his ruling needs no new mechanism for the panel.

THE QUESTION THIS MEASURES. His words are general and the gate is not: it lives
in 1 module. This counts the modules that can construct a paid request and asks
which of them consult the ledger, separating LIVE entry points from the dated
one-off confer scripts of past rounds, because those must stay reproducible and
gating them would change history rather than protect spending.

READ-ONLY, and it dispatches nothing.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: A module can reach a paid route if it names one of these.
PAID_MARKERS = ("openrouter", "OPENROUTER", "deepseek", "DEEPSEEK")
#: It passes his gate if it names any of these.
GATE_MARKERS = ("_paid_is_authorised", "paid_ledger", "authorisation_for")
#: IT CAN ACTUALLY SPEND if it issues an outbound request. Naming a route is an
#: UPPER BOUND -- a registry table listing `openai/gpt-5.5` as an identifier
#: cannot spend anything -- and this is what separates the bound from the risk.
#: The first version of this script omitted it and reported 34 live entry points
#: as though all 34 could spend.
SPEND_MARKERS = ("requests.post", "requests.request", "httpx", "urlopen",
                 "Request(", "aiohttp", "openai.", "OpenAI(", "curl ")
#: A DATED one-off: a confer or smoke script whose name carries its own date, or
#: which lives under a logs/sandbox path. These are archived runs.
DATED = re.compile(r"_20\d{2}-\d{2}-\d{2}")


def classify(path: pathlib.Path, text: str) -> str:
    rel = path.relative_to(REPO).as_posix()
    if "/logs/" in rel or "/sandbox" in rel or "seat_evidence" in rel:
        return "archived copy"
    name = path.stem
    if name.startswith(("smoketest", "smoke_test", "test_")):
        return "smoke or test"
    if DATED.search(name):
        return "dated one-off"
    if name.startswith("confer_"):
        return "undated confer script"
    return "live entry point"


def scan() -> dict:
    rows = []
    for path in sorted(REPO.glob("bench/**/*.py")) + sorted(REPO.glob("scripts/**/*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not any(m in text for m in PAID_MARKERS):
            continue
        try:
            ast.parse(text)
            parses = True
        except SyntaxError:
            parses = False
        rel = path.relative_to(REPO).as_posix()
        rows.append({
            "path": rel,
            "class": classify(path, text),
            #: SELF-EXCLUDED. This script names the gate markers in order to
            #: SEARCH for them, so without this it counts itself as gated --
            #: which it was doing, and which is an instrument measuring its own
            #: vocabulary rather than the tree.
            "gated": (any(m in text for m in GATE_MARKERS)
                      and path.resolve() != pathlib.Path(__file__).resolve()),
            "can_spend": any(m in text for m in SPEND_MARKERS),
            "parses": parses,
        })
    return {"rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = scan()
    rows = [r for r in data["rows"] if r["class"] != "archived copy"]
    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    print("== which paid-route entry points consult his authorisation ledger? ==")
    buckets: dict[str, list] = {}
    for r in rows:
        buckets.setdefault(r["class"], []).append(r)
    total = len(rows)
    gated = [r for r in rows if r["gated"]]
    print(f"   modules naming a paid route (archived copies excluded): {total}")
    print(f"   of those, consulting the ledger                       : {len(gated)}")
    for r in gated:
        print(f"     GATED  {r['path']}")
    print()
    for name in sorted(buckets):
        rs = buckets[name]
        g = sum(1 for r in rs if r["gated"])
        print(f"   {name:<24} {len(rs):>3}   gated {g}")
    live = [r for r in rows if r["class"] == "live entry point" and not r["gated"]]
    spenders = [r for r in live if r["can_spend"]]
    namers = [r for r in live if not r["can_spend"]]
    print()
    print(f"   LIVE entry points NOT gated: {len(live)}, of which")
    print(f"     {len(spenders)} ISSUE AN OUTBOUND REQUEST and so can spend:")
    for r in spenders:
        print(f"       {r['path']}")
    print(f"     {len(namers)} only NAME a route (a registry table, a config "
          f"default) and cannot spend on their own")
    if total:
        from statsmodels.stats.proportion import proportion_confint
        import numpy as np
        from scipy import stats
        k, n = len(gated), total
        lo, hi = proportion_confint(k, n, method="wilson")
        elo, ehi = proportion_confint(k, n, method="beta")
        z = stats.norm.ppf(0.975); p = k / n; d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        print()
        print(f"   gated share {k} of {n} = {p:.6f}")
        print(f"     statsmodels wilson [{lo:.6f}, {hi:.6f}]")
        print(f"     exact (beta)       [{elo:.6f}, {ehi:.6f}]")
        print(f"     numpy closed form  [{c - h:.6f}, {c + h:.6f}]")
    print()
    print("   WHAT THIS DOES AND DOES NOT ESTABLISH. Naming a paid route is an")
    print("   UPPER BOUND on spending: a registry table listing an identifier")
    print("   cannot spend, and a dated one-off from a past round is an archived")
    print("   experiment rather than a live risk. The figure that bears on his")
    print("   ruling is the LIVE, UNGATED, REQUEST-ISSUING list above. Even that")
    print("   is a bound and not a demonstration: an outbound call named in a")
    print("   module is not proof that any reachable code path makes it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
