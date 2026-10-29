#!/usr/bin/env python3
"""How the founder actually interacts, measured, for the interaction specification.

HIS INSTRUCTION, 2026-10-19, registered as `fr:3599a74cc1aa`: *"Perhaps therefore,
as well as drawing up a specification for the HIL, you should draw up an
interaction specification or me, and use this in your experiments that involve
the new orchestrator?"* (*or me* is *for me*.)

WHY MEASURED RATHER THAN DESCRIBED. A specification of how he interacts, written
from impression, would be an account of how I remember him interacting. His own
annotations are a committed corpus of 752 items, so the shape of his
instructions can be counted instead.

★ AND THE FIRST ATTEMPT AT THIS MEASUREMENT WAS WRONG, WHICH IS WHY THE
PREDICATE IS WRITTEN OUT HERE. Counting MC commands by word boundary returned
`a` 612 times in 752 annotations and matched `t` inside "don't": a single-letter
command is indistinguishable from English by a boundary regex. Commands are only
identifiable in a COMMAND POSITION -- a line, or a trailing run, whose every
token is an MC command, which is how he writes them ("a, d", "a, f, sy"). With
that predicate the count falls from 612 to 13 of 752.

WHAT THIS CORPUS CANNOT ANSWER, STATED SO THE GAP IS NOT PAPERED OVER. His MC
commands mostly reach a session through CHAT, not through annotations, so the
13 of 752 here measures his use of the TICKET MARKERS and says almost nothing
about how often he issues `a`, `f` or `sy`. Any frequency claim about those
needs the session transcripts, which `scripts/depth_and_breadth_are_measurable_2026-10-25.py`
streams; it is out of scope here and is NOT estimated from this corpus.

READ-ONLY.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"

#: His own command vocabulary, from the committed MC list rather than invented.
MC = {"y", "cy", "d", "p", "a", "e", "f", "sy", "t", "c", "sv", "qc", "rs", "re",
      "rt", "r", "x", "sth", "rg", "ag", "sq", "pr", "cc2", "cx", "ge", "cgpt",
      "ds", "fable", "fr", "pf", "qs", "wr"}
#: The 3 that mark a ticket. These are the ones this corpus can actually measure.
MARKERS = {"fr", "pf", "qs", "wr"}


def commands_in(text: str) -> set[str]:
    """MC commands in a COMMAND POSITION. See the module docstring for why."""
    found: set[str] = set()
    lines = text.replace("\r", "\n").split("\n")
    for line in lines:
        s = line.strip().strip(".").strip()
        if not s:
            continue
        toks = [t for t in re.split(r"[,\s]+", s) if t]
        if toks and len(toks) <= 6 and all(t.lower() in MC for t in toks):
            found |= {t.lower() for t in toks}
    tail = lines[-1].strip() if lines else ""
    m = re.search(r"(?:^|[.?!]\s+)((?:[A-Za-z]{1,5})(?:[,\s]+[A-Za-z]{1,5}){0,5})\s*$", tail)
    if m:
        toks = [t for t in re.split(r"[,\s]+", m.group(1)) if t]
        if toks and all(t.lower() in MC for t in toks):
            found |= {t.lower() for t in toks}
    return found


def annotations() -> list[dict]:
    out = subprocess.run([sys.executable, str(READER), "--json"],
                         capture_output=True, text=True, cwd=str(REPO))
    if out.returncode != 0:
        raise SystemExit(f"the reader failed: {out.stderr[-300:]}")
    return json.loads(out.stdout)["annotations"]


def _interval(k: int, n: int) -> dict:
    from statsmodels.stats.proportion import proportion_confint
    import numpy as np
    from scipy import stats
    lo, hi = proportion_confint(k, n, method="wilson")
    elo, ehi = proportion_confint(k, n, method="beta")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return {"k": k, "n": n, "p": p, "wilson": (lo, hi), "exact": (elo, ehi),
            "closed_form": (c - h, c + h)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    anns = annotations()
    n = len(anns)
    lengths = sorted(len(a["text"]) for a in anns)
    import numpy as np
    arr = np.array(lengths)

    naive = collections.Counter()
    bound = re.compile(r"(?<![A-Za-z0-9_])(" +
                       "|".join(sorted(MC, key=len, reverse=True)) + r")(?![A-Za-z0-9_])")
    for a in anns:
        for t in bound.findall(a["text"]):
            naive[t] += 1

    positioned = collections.Counter()
    carrying = 0
    for a in anns:
        c = commands_in(a["text"])
        if c:
            carrying += 1
            for x in c:
                positioned[x] += 1

    marker_only = {k: v for k, v in positioned.items() if k in MARKERS}
    report = {
        "annotations": n,
        "length": {"median": int(np.median(arr)), "mean": float(arr.mean()),
                   "min": int(arr.min()), "max": int(arr.max()),
                   "under_60": _interval(int((arr < 60).sum()), n),
                   "over_400": _interval(int((arr > 400).sum()), n)},
        "naive_word_boundary_count": dict(naive.most_common(6)),
        "command_position_count": dict(positioned.most_common()),
        "carrying_a_command": _interval(carrying, n),
        "markers_only": marker_only,
    }
    if args.json:
        print(json.dumps(report, indent=2, default=float))
        return 0

    print("== how he actually interacts, from his 752-item annotation corpus ==")
    L = report["length"]
    print(f"   annotations            : {n}")
    print(f"   length median / mean   : {L['median']} / {L['mean']:.1f} characters")
    print(f"   shortest / longest     : {L['min']} / {L['max']}")
    for label, key in (("under 60 characters", "under_60"), ("over 400 characters", "over_400")):
        i = L[key]
        print(f"   {label:<22} {i['k']} of {i['n']} = {i['p']:.6f}  "
              f"Wilson [{i['wilson'][0]:.6f}, {i['wilson'][1]:.6f}]  "
              f"exact [{i['exact'][0]:.6f}, {i['exact'][1]:.6f}]")
    print()
    print("   ★ THE PREDICATE MATTERS, and the first version of this was wrong:")
    print("     by WORD BOUNDARY, the top counts are "
          f"{report['naive_word_boundary_count']}")
    print("     which is the English article and \"don't\", not his commands.")
    print("     by COMMAND POSITION: "
          f"{report['command_position_count']}")
    c = report["carrying_a_command"]
    print(f"     annotations carrying any command: {c['k']} of {c['n']} = "
          f"{c['p']:.6f}  Wilson [{c['wilson'][0]:.6f}, {c['wilson'][1]:.6f}]")
    print()
    print("   WHAT THIS CORPUS CANNOT ANSWER. Every command it finds is a TICKET")
    print(f"   MARKER ({', '.join(sorted(marker_only))}). His steering commands reach a")
    print("   session through CHAT, so this says almost nothing about how often he")
    print("   issues a, f or sy, and no such frequency is estimated from it here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
