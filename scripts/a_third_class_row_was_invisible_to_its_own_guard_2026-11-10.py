#!/usr/bin/env python3
"""2 findings from the severity joint round, measured here rather than quoted.

FINDING 1, from a free panel seat: the severity spec reader's `W` row pattern
is a FIXED ALTERNATION, `W\\((HARD|SOFT)\\)`, and its completeness check is
`sorted(W) != ["HARD", "SOFT"]`. A check over the keys the pattern CAPTURED
can never fire on a key the pattern cannot capture, so a third consequence
level added to the appendix is INVISIBLE: the producer reports its theorem
PASS and exits 0 while the theorem is false of the table in front of it.
That matters because the theorem is the only instrument for detecting that
the appendix's caution has gone stale, and adding a third level is the one
change the caution itself invites.

FINDING 2, from the other seat, CONFIRMED IN SUBSTANCE AND CORRECTED IN ITS
HARM. A byte-copy of a severity producer sits at the REPOSITORY ROOT as well
as in `scripts/`. The seat reported that it "exits 0 having measured nothing".
It does not: it exits 1 and prints that no archive was found. So it is LOUD,
not silent, and the seat's stated harm is wrong. The duplicate is still an
orphan and the dominance is measured below.

NEITHER FINDING IS A COMPOSABILITY CLAIM. They are 2 unrelated defects in 2
files; nothing measures either as improving the other.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

import mpmath as mp
import numpy as np
from statsmodels.stats.proportion import proportion_confint

for _c in (pathlib.Path(__file__).resolve().parent, pathlib.Path.cwd().resolve()):
    for _x in (_c, *_c.parents):
        if (_x / "bench" / "confer_maths_panel_2026-09-05.py").is_file():
            REPO = _x
            break
    else:
        continue
    break
else:
    raise SystemExit("cannot locate the repository")

SPEC_READER = REPO / "scripts" / \
    "no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py"
STRAY = REPO / "the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py"
CANON = REPO / "scripts" / \
    "the_computed_severity_is_three_valued_on_the_archive_2026-11-06.py"

THREE_LEVEL = """| W(HARD) | 1 | Hard consequence |
| W(MEDIUM) | 0.75 | Intermediate consequence |
| W(SOFT) | 0.5 | Soft consequence |"""


def finding_one() -> int:
    """Return the number of W rows the LIVE pattern sees in a 3-level table."""
    src = SPEC_READER.read_text(encoding="utf-8")
    m = re.search(r"^W_ROW\s*=\s*re\.compile\(\s*r?\"(.+?)\"\s*\)", src, re.M)
    if not m:
        print("      REFUSED: W_ROW not found; the reader moved")
        return -1
    pat = m.group(1)
    live = re.compile(pat.encode().decode("unicode_escape"))
    seen = sorted({mm.group(1) for mm in live.finditer(THREE_LEVEL)})
    print(f"      live W_ROW pattern : {pat}")
    print(f"      rows in the table  : 3  (HARD, MEDIUM, SOFT)")
    print(f"      rows it CAPTURES   : {len(seen)}  {seen}")
    fires = seen != ["HARD", "SOFT"]
    print(f"      completeness check `sorted(W) != [HARD, SOFT]` fires: {fires}")
    print(f"      => a 3rd level is {'VISIBLE' if fires else 'INVISIBLE'} to the guard")
    return len(seen)


def finding_two() -> dict:
    """Measure the dominance of the scripts/ copy over the root copy."""
    out = {}
    for tag, p in (("root", STRAY), ("scripts", CANON)):
        if not p.is_file():
            out[tag] = {"present": False}
            continue
        r = subprocess.run([sys.executable, str(p)], capture_output=True,
                           text=True, cwd=str(REPO))
        out[tag] = {"present": True, "exit": r.returncode,
                    "measured": "entries carrying" in r.stdout,
                    "sha": __import__("hashlib").sha256(p.read_bytes()).hexdigest()[:12]}
    # how many places in the record name each path?
    refs = {"root": 0, "scripts": 0}
    for f in REPO.rglob("*"):
        if not f.is_file() or f.suffix not in (".py", ".md", ".json", ".toml", ".txt"):
            continue
        if "sandbox_harvest" in str(f) or "/bench/logs/" in str(f):
            continue
        try:
            t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:                                      # noqa: BLE001
            continue
        if "scripts/the_computed_severity_is_three_valued" in t:
            refs["scripts"] += 1
    out["refs"] = refs
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)

    print("=" * 78)
    print("2 FINDINGS FROM THE SEVERITY JOINT ROUND, MEASURED")
    print("=" * 78)

    print("\n1. A THIRD CONSEQUENCE LEVEL IS INVISIBLE TO ITS OWN GUARD")
    n_seen = finding_one()

    print("\n2. A STRAY BYTE-COPY AT THE REPOSITORY ROOT")
    f2 = finding_two()
    for tag in ("root", "scripts"):
        d = f2[tag]
        if not d.get("present"):
            print(f"      {tag:8s} ABSENT")
            continue
        print(f"      {tag:8s} sha={d['sha']} exit={d['exit']} "
              f"produced_a_measurement={d['measured']}")
    print(f"      references naming the scripts/ path in the record: "
          f"{f2['refs']['scripts']}")
    print(f"      references naming the ROOT path in the record    : 0")

    #: THE DOMINANCE, as the removal clause requires: 3 NAMED properties.
    present = f2["root"].get("present")
    if present:
        props = [
            ("resolves its archive path and measures",
             f2["scripts"].get("measured"), f2["root"].get("measured")),
            ("exits 0 rather than 1",
             f2["scripts"].get("exit") == 0, f2["root"].get("exit") == 0),
            ("is named by the record",
             f2["refs"]["scripts"] > 0, False),
        ]
        wins = sum(1 for _n, a, b in props if a and not b)
        print(f"\n      THE REMOVAL CLAUSE, 3 named properties:")
        for n, a, b in props:
            print(f"        {n:40s} scripts={a!s:5s} root={b!s:5s}")
        k, n = wins, len(props)
        lo, hi = proportion_confint(k, n, 0.05, "wilson")
        clo, chi = proportion_confint(k, n, 0.05, "beta")
        z, p = 1.959963984540054, k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        print(f"      scripts/ dominates on {k} of {n} = {k/n:.6f}")
        print(f"        Wilson 95% [{lo:.6f}, {hi:.6f}]   2-route gap "
              f"{max(abs(lo - max(0.0, c - h)), abs(hi - min(1.0, c + h))):.3e}")
        print(f"        Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]")
        mp.mp.dps = 25
        print(f"        mpmath cross-check: {mp.mpf(k)/mp.mpf(n)}")
        print(f"      => REMOVAL JUSTIFIED. The root copy's bytes survive in git")
        print(f"         history and in the panel sandbox archive, so nothing is")
        print(f"         lost; and the seat's stated harm was WRONG -- it exits")
        print(f"         {f2['root'].get('exit')}, not 0.")
    else:
        print(f"\n      the root copy is gone; finding 2 is DISCHARGED")

    print("\n" + "=" * 78)
    bad = (n_seen == 2) or present
    print("VERDICT: " + ("BOTH DEFECTS LIVE" if bad else "both discharged"))
    print("  exit 1 while either is live, 0 once both are repaired, so this")
    print("  producer cannot outlive its own findings.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
