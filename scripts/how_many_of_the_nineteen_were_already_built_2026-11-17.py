#!/usr/bin/env python3
"""How many of the 19 decisions put to the founder rest on a premise the live
tree already falsifies?

★ WHY THIS EXISTS. On 2026-11-17 a blind free panel was given all 19 decisions
with my recommendations stripped. Both seats, independently, reported that
several entries describe work as unbuilt which is in fact wired, tested and
live. Every claim below was then VERIFIED by execution in the maintainer's own
tree rather than relayed on a seat's word, because a seat that catches an error
can commit one.

★ AND IT IS NOT A PANEL DISCOVERY. It is my own marker lag. `git log -S` dates
each mechanism's first appearance AFTER the entry that calls it unbuilt was
raised -- in 2 cases by 8 and 10 days. This project already records that shape
as `building the work is not marking the entry`, measured once before at 5 built
and 5 reading OPEN. The panel's contribution was to look, which I had not.

★ WHAT IT COSTS HIM, WHICH IS THE POINT. Each such entry is a decision he was
about to be asked to make about work that is already done.

Reads the tree and git. Writes nothing.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: entry -> (file, symbol, what the entry claims, how the claim is checked)
CLAIMS = [
    ("B77", "bench/reference_runner_v3.py", "required_quiet_run",
     "the roster-aware repair has sat unadopted since 2026-10-07",
     "CALLED in both convergence arms"),
    ("B142", "bench/model_catalogue.py", "known_roles",
     "the role selector cannot offer the 4 roles the UX brief specifies",
     "known_roles() returns more than 3 roles"),
    ("B171", "hooks/work_not_narrate.py", "_is_bare_question",
     "a bare mid-turn question wipes his standing command set",
     "the narrowed reset guard is present at the reset site"),
    ("B125", "bench/confer_maths_panel_2026-09-05.py", "stamp_brief_at_dispatch",
     "3 candidate remedies, none built",
     "the artefact stamper is defined AND called"),
]


def call_sites(path: pathlib.Path, symbol: str) -> list:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:                                          # noqa: BLE001
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and ast.unparse(n.func).endswith(symbol):
            out.append(n.lineno)
    return out


def first_seen(path: str, symbol: str) -> str:
    r = subprocess.run(["git", "log", "-S", symbol, "--format=%ad", "--date=short",
                        "--", path], cwd=REPO, capture_output=True, text=True)
    lines = [x for x in r.stdout.split() if x]
    return lines[-1] if lines else "unknown"


def entry_raised(entry: str) -> str:
    tl = (REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md").read_text(
        encoding="utf-8", errors="replace")
    i = tl.find(f"**{entry}. ")
    if i < 0:
        return "unknown"
    seg = tl[i:i + 600]
    import re
    m = re.search(r"Added (\d{4}-\d{2}-\d{2})", seg)
    return m.group(1) if m else "unknown"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args([] if argv is None else argv)

    TOTAL = 19
    rows = []
    for entry, path, sym, claim, how in CLAIMS:
        p = REPO / path
        sites = call_sites(p, sym)
        defined = f"def {sym}" in p.read_text(encoding="utf-8", errors="replace")
        built = bool(sites) or (sym.startswith("_") and defined)
        rows.append({"entry": entry, "symbol": sym, "file": path,
                     "defined": defined, "call_sites": sites,
                     "built": built, "claim": claim, "checked_by": how,
                     "symbol_first_seen": first_seen(path, sym),
                     "entry_raised": entry_raised(entry)})

    if a.json:
        import json
        print(json.dumps({"total_decisions": TOTAL, "rows": rows}, indent=2))
        return 0

    print(f"  decisions put to him: {TOTAL}")
    print(f"  entries whose premise was checked against the live tree: {len(rows)}")
    print()
    for r in rows:
        lag = ""
        if r["symbol_first_seen"] != "unknown" and r["entry_raised"] != "unknown":
            import datetime as dt
            try:
                d1 = dt.date.fromisoformat(r["entry_raised"])
                d2 = dt.date.fromisoformat(r["symbol_first_seen"])
                lag = f"  ({(d2 - d1).days} day(s) after the entry)"
            except ValueError:
                lag = ""
        print(f"    {r['entry']:<5} {'BUILT' if r['built'] else 'NOT BUILT':<10} "
              f"{r['symbol']}  call site(s) {r['call_sites'] or 'none'}")
        print(f"          the entry says: {r['claim']}")
        print(f"          first seen {r['symbol_first_seen']}, entry raised "
              f"{r['entry_raised']}{lag}")
    built = sum(1 for r in rows if r["built"])
    print()
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    mp.mp.dps = 40
    for lbl, k, n in (("of the entries checked, premise already falsified", built, len(rows)),
                      ("of all 19 decisions, premise already falsified", built, TOTAL)):
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        cl, ch = proportion_confint(k, n, alpha=0.05, method="beta")
        z = mp.sqrt(2) * mp.erfinv(mp.mpf("0.95"))
        p = mp.mpf(k) / n
        d = 1 + z**2 / n
        c = p + z**2 / (2 * n)
        h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        agree = max(abs(float((c - h) / d) - lo), abs(float((c + h) / d) - hi))
        print(f"  {lbl}: {k} of {n} = {k / n:.6f}")
        print(f"      Wilson [{lo:.6f}, {hi:.6f}] (mpmath agrees to {agree:.2e})"
              f"  Clopper-Pearson [{cl:.6f}, {ch:.6f}]")
    print()
    print("  THE SAMPLE IS NOT RANDOM AND THE FIGURE MUST NOT BE READ AS A RATE.")
    print("  These 4 are the entries 2 blind seats NAMED. No sweep of the other")
    print("  15 has been run, so the true count can only be this or higher.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
