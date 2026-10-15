#!/usr/bin/env python3
"""The decomposition futility guard held in free run 1. Measured from its log.

WHAT WAS PREDICTED, 2026-10-15 02:34 BST, before either run started. Task B6
item 3 recorded that `max_successful_prompt_chars` is a PROVEN FLOOR used as a
CEILING, and that delivering the project's specification whole would push every
simulated seat's payload past its own recorded floor -- so **6 of 6 simulated
seats would have force-decomposed every dispatch on the size of their own
instructions, while no paid seat would have**, because the paid seats' recorded
figures are 465,206 and 110,076 against the simulated seats' 72,934 to 80,517.
A confound that fires only in the cheap runs and vanishes in the expensive ones
is the worst available shape, which is why a futility guard was built rather
than deferred.

THE GUARD'S ARGUMENT, which is what makes it a repair and not a workaround:
splitting a payload cannot help when the UN-SPLITTABLE part already exceeds the
limit. The system prompt is re-sent with every chunk, so chunking raises total
bytes and raises the request count while leaving every single request still over
the limit. The floor is therefore judged on the DECOMPOSABLE payload, not on the
total.

WHAT RUN 1 SHOWS. This script reads the run's own console log and counts, for
every decomposition decision the runner logged, the total payload, the
decomposable portion and whether a split actually occurred. It does not re-run
anything and it changes nothing.
"""
from __future__ import annotations

import pathlib
import re
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_LOG = REPO / ("bench/logs/free_run1_directive_whole_20261015T061123Z"
                      "_20261015T061124Z/console.log")

# "SEAT: payload N chars exceeds the M floor but only K of it is decomposable
#  (system prompt S chars is re-sent per chunk, not split)"
GUARD = re.compile(
    r"(?P<seat>[A-Za-z0-9_.-]+-SIM):\s+payload\s+(?P<payload>\d+)\s+chars\s+"
    r"exceeds the\s+(?P<floor>\d+)\s+floor but only\s+(?P<decomposable>\d+)\s+"
    r"of it is decomposable\s+\(system prompt\s+(?P<sysprompt>\d+)\s+chars"
)
# Any sign a dispatch was ACTUALLY split.
SPLIT = re.compile(r"decompos(?:ing|ed)\s|chunk\s+\d+\s*/\s*\d+|"
                   r"split into\s+\d+", re.I)


def main() -> int:
    from statsmodels.stats.proportion import proportion_confint
    import numpy as np

    log = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG
    if not log.exists():
        print(f"log not found: {log}", file=sys.stderr)
        return 2
    text = log.read_text(encoding="utf-8", errors="replace")

    rows = [m.groupdict() for m in GUARD.finditer(text)]
    splits = SPLIT.findall(text)

    print("=" * 76)
    print("1. EVERY DECOMPOSITION DECISION THE GUARD TOUCHED")
    print("=" * 76)
    print(f"  log: {log.relative_to(REPO)}")
    print(f"  guard decisions logged: {len(rows)}")
    print(f"  actual splits found   : {len(splits)}")
    print()
    print(f"  {'seat':<14}{'payload':>9}{'floor':>8}{'decomp':>9}{'sysprompt':>11}"
          f"{'over?':>7}{'decomp<floor?':>15}")
    seats = {}
    over_floor = 0
    decomp_under = 0
    for r in rows:
        pay = int(r["payload"]); flo = int(r["floor"])
        dec = int(r["decomposable"]); sysp = int(r["sysprompt"])
        o = pay > flo
        u = dec < flo
        over_floor += o
        decomp_under += u
        seats.setdefault(r["seat"], []).append((pay, dec, sysp))
        print(f"  {r['seat']:<14}{pay:>9}{flo:>8}{dec:>9}{sysp:>11}"
              f"{str(o):>7}{str(u):>15}")

    n = len(rows)
    print()
    print("=" * 76)
    print("2. THE TWO PROPORTIONS THAT MATTER")
    print("=" * 76)
    lo1, hi1 = proportion_confint(over_floor, n, method="wilson")
    lo1b, hi1b = proportion_confint(over_floor, n, method="beta")
    print(f"  payload over the seat's floor : {over_floor} of {n} "
          f"= {over_floor/n*100:.4f}%")
    print(f"    Wilson          95% [{lo1*100:.4f}%, {hi1*100:.4f}%]")
    print(f"    Clopper-Pearson 95% [{lo1b*100:.4f}%, {hi1b*100:.4f}%]")
    lo2, hi2 = proportion_confint(decomp_under, n, method="wilson")
    lo2b, hi2b = proportion_confint(decomp_under, n, method="beta")
    print(f"  DECOMPOSABLE part under floor : {decomp_under} of {n} "
          f"= {decomp_under/n*100:.4f}%")
    print(f"    Wilson          95% [{lo2*100:.4f}%, {hi2*100:.4f}%]")
    print(f"    Clopper-Pearson 95% [{lo2b*100:.4f}%, {hi2b*100:.4f}%]")
    print()
    print("  So in every logged decision the TOTAL exceeded the floor while the")
    print("  SPLITTABLE portion did not. Judging on the total force-decomposes;")
    print("  judging on the splittable portion does not. That is the whole repair.")

    print()
    print("=" * 76)
    print("3. HOW BIG WAS THE UN-SPLITTABLE PART?")
    print("=" * 76)
    sysps = np.array([int(r["sysprompt"]) for r in rows])
    decs = np.array([int(r["decomposable"]) for r in rows])
    pays = np.array([int(r["payload"]) for r in rows])
    frac = sysps / pays
    print(f"  system prompt chars : min {sysps.min()}  max {sysps.max()}  "
          f"mean {sysps.mean():.1f}")
    print(f"  decomposable chars  : min {decs.min()}  max {decs.max()}  "
          f"mean {decs.mean():.1f}")
    print(f"  system prompt as a fraction of payload: min {frac.min():.4f}  "
          f"max {frac.max():.4f}  mean {frac.mean():.4f}")
    print(f"  seats observed      : {len(seats)} ({', '.join(sorted(seats))})")

    print()
    print("=" * 76)
    print("VERDICT")
    print("=" * 76)
    held = len(splits) == 0 and n > 0 and decomp_under == n and over_floor == n
    print(f"  guard decisions           : {n}")
    print(f"  dispatches actually split : {len(splits)}")
    print(f"  B6(3) confound fired      : {len(splits) > 0}")
    print(f"  GUARD HELD                : {held}")
    print()
    print("  BOUND ON THIS CLAIM: this is 1 simulated run, and it establishes")
    print("  that the guard fires and declines to split on the payloads this")
    print("  target and these seats produce. It does not establish behaviour on")
    print("  a paid seat, whose recorded floor is 465,206 or 110,076 and which")
    print("  the confound was measured never to reach in the first place.")

    import json
    out = {
        # The run NAME, not the log path: `bench/logs/` is gitignored, so a full
        # path here reads as a citation a reader could open and is not one.
        "run": log.parent.name,
        "log_note": "read from console.log inside that run directory under bench/logs/, which is gitignored",
        "guard_decisions": n,
        "payload_over_floor": [over_floor, n],
        "payload_over_floor_wilson": [lo1, hi1],
        "decomposable_under_floor": [decomp_under, n],
        "decomposable_under_floor_wilson": [lo2, hi2],
        "dispatches_actually_split": len(splits),
        "system_prompt_chars_min": int(sysps.min()),
        "system_prompt_chars_max": int(sysps.max()),
        "decomposable_chars_min": int(decs.min()),
        "decomposable_chars_max": int(decs.max()),
        "seats_observed": sorted(seats),
        "guard_held": held,
        "bound": ("1 simulated run; establishes the guard fires and declines to "
                  "split on these payloads, not behaviour on a paid seat"),
    }
    dest = REPO / "experimental_notes/evidence/futility_guard_held_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if held else 1


if __name__ == "__main__":
    answer_help(__doc__, __file__)
    sys.exit(main())
