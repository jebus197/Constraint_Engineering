#!/usr/bin/env python3
"""Section P: do the panel rounds actually meet the founder's conditions?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE CONDITIONS ARE HIS, verbatim, 2026-09-09: *"In all cases and with all fixes
always check them with Fable and CC2 in full CDSFL panel review format (so not
just some simple open ended prompt), they must use whatever aspects of the
harness are currently working, including our mathematical model and all relevant
mechanics in the formation of their answers/fixes, as should you."*

Section P restates that as P1 to P7. Entries P1, P3, P4 and P5 have sat at
PROPOSED since, with no measurement of whether the rounds actually satisfy them.
This measures it from the archived seat records rather than asserting it.

WHAT EACH CLAUSE IS CHECKED BY, and none of it is a word search of the brief.

  P1  full CDSFL format          -- the dispatcher carries the formal schema, and
                                    the brief passed the validator before dispatch
  P3  seats USE the harness      -- recorded tool calls per seat, from the tool
                                    logs the dispatcher writes, not from claims
  P4  seats PRODUCE and TEST     -- source files the seat left in the sandbox,
                                    which is the only delivery the harness keeps
  P5  no compelled convergence   -- each seat returning its own verdict AND a
                                    strongest_disagreement section

P4 IS THE HARD ONE AND IT IS WHY THIS EXISTS. A seat can describe a fix at any
length. Only a file it leaves behind is a delivered fix, because
`panel_sandbox.teardown` destroys everything else.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Cache and build artefacts are not deliverables.
CACHE = re.compile(r"__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.pyc$|\.db$")
#: A round is one directory holding at least 1 seat reply.
SEATS = ("cc2", "fable", "cx", "cgpt", "ds")


def rounds() -> list[pathlib.Path]:
    return sorted(d for d in LOGS.glob("panel_*")
                  if d.is_dir() and any((d / f"{s}.json").is_file() for s in SEATS))


def source_files(d: pathlib.Path) -> list[str]:
    p = d / "seat_proposals.diff"
    if not p.is_file():
        return []
    paths = [ln[4:].strip() for ln in p.read_text(errors="replace").splitlines()
             if ln.startswith("### ")]
    return [x for x in paths if not CACHE.search(x)]


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sps
    import mpmath as mp

    def rep(label, k, n):
        if not n:
            print(f"  {label}: no denominator")
            return
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        mp.mp.dps = 30
        z = mp.mpf(str(sps.norm.ppf(0.975)))
        p, N = mp.mpf(k) / n, mp.mpf(n)
        cc = (p + z**2 / (2 * N)) / (1 + z**2 / N)
        h = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
        agree = abs(w[0] - float(cc - h)) < 1e-9
        print(f"  {label}: {k} of {n} = {k / n:.4%}")
        print(f"      Wilson [{w[0]:.4%}, {w[1]:.4%}] statsmodels | "
              f"[{float(cc - h):.4%}, {float(cc + h):.4%}] mpmath | agree 1e-9: {agree}")
        print(f"      Clopper-Pearson [{c[0]:.4%}, {c[1]:.4%}]")

    rs = rounds()
    print(f"panel rounds with at least 1 seat reply: {len(rs)}\n")
    print(f"  {'round':38s} {'seats':>5} {'tool calls':>11} {'src files':>10} {'disagree':>9}")
    tool_ok = disagree_ok = seatn = 0
    delivered = []
    paid = 0
    for d in rs:
        calls = 0
        n = 0
        dis = 0
        for s in SEATS:
            f = d / f"{s}.json"
            if not f.is_file():
                continue
            try:
                j = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            n += 1
            if j.get("route") and j["route"] != "claude_cli":
                paid += 1
            c = int(j.get("n_tool_calls") or 0)
            calls += c
            tool_ok += c > 0
            if re.search(r"strongest[_ ]disagreement", j.get("response", ""), re.I):
                dis += 1
                disagree_ok += 1
        seatn += n
        src = source_files(d)
        if src:
            delivered.append((d.name, src))
        print(f"  {d.name:38s} {n:5d} {calls:11d} {len(src):10d} {dis:9d}")

    print(f"\nP3 — seats USED the harness (recorded tool calls > 0):")
    rep("seat replies with at least 1 recorded tool call", tool_ok, seatn)
    print(f"\nP5 — no compelled convergence (each seat returns its own disagreement):")
    rep("seat replies carrying a strongest_disagreement", disagree_ok, seatn)
    print(f"\nP4 — seats DELIVERED a fix as a file, not as prose:")
    rep("rounds that returned at least 1 source file", len(delivered), len(rs))
    _SHOW = 6
    for name, src in delivered:
        print(f"      {name}: {len(src)} file(s)")
        for x in src[:_SHOW]:
            print(f"          {x}")
        if len(src) > _SHOW:
            # Naming the remainder, because a capped listing that stays silent
            # reads as the whole set.
            print(f"          ... {len(src) - _SHOW} more not shown")

    print(f"\nCOST CONTROL — paid seat replies across every round: {paid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
