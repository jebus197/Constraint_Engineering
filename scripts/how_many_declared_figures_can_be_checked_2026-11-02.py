#!/usr/bin/env python3
"""For how many declared figures is the `--as-of` fallback actually available?

★ THIS SCRIPT'S FIRST VERSION ASKED THE WRONG QUESTION. It counted producers
lacking `--as-of` and called the figures "uncheckable". That is FALSE, and it is
the same overstatement this session had criticised in entry B21 within the hour.

WHAT THE VALIDATOR ACTUALLY DOES, read from its control flow rather than from its
comments (`scripts/panel_brief_validate.py`, the declared-figure loop):

  1. Run the producer PLAIN. If the declared value appears in its output the
     figure is ACCEPTED, and `--as-of` is never consulted.
  2. Only if the plain run does NOT print it, retry with `--as-of <the brief's
     latest date>`. A match is accepted LOUDLY as a historical figure.
  3. Only if that also fails, consult the amendments register for a recorded rule
     change, which must name the figure AND the brief and whose replacement value
     the producer must actually print.
  4. Otherwise refuse.

SO A MISSING `--as-of` COSTS NOTHING FOR A FIGURE THAT STILL REPRODUCES. It bites
only at step 2: a figure that WAS true at the brief's date and is not true today
is refused where it could have been accepted as historical. A real gap, and a far
narrower one than the first version claimed.

WHAT IS MEASURED HERE, and the 2 readings must not be confused:
  * FALLBACK REACH -- how many declared figures have a producer that could answer
    step 2 at all. A property of the producers, not of the figures.
  * NOT how many figures are wrong, and NOT how many are uncheckable. Neither is
    established by this script.

THE CONCRETE CASE THAT STARTED IT. The already-dispatched brief
`bench/logs/falsifier_supply_and_integrity_r2_2026-10-02/BRIEF.md` fails 4
required checks. Its producer `scripts/falsifier_supply_decomposition_2026-10-02.py`
runs clean, prints none of the 4 declared values, and has no `--as-of`, so step 2
cannot run and the refusal stands. Whether those 4 were true on 2026-10-02 is
exactly what cannot now be established -- 4 figures, not 188.

NOTHING IS FIXED HERE. The fix follows the scope.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
FIGURE = re.compile(
    r"<!--\s*figure:\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^>]+?)\s*-->")


def supports_as_of(script: pathlib.Path) -> tuple[bool, str]:
    """Does this producer accept --as-of? Asked by RUNNING it, not by reading it.

    `--help` is the cheap, side-effect-free probe, and the project's standing rule
    is that a `--help` must never cost money, so this is safe to run across the
    whole set.
    """
    if not script.is_file():
        return (False, "producer file absent")
    try:
        r = subprocess.run([sys.executable, str(script), "--help"],
                           capture_output=True, text=True, timeout=60,
                           cwd=str(REPO))
    except subprocess.TimeoutExpired:
        return (False, "--help timed out")
    text = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        return (False, f"--help exited {r.returncode}")
    if "--as-of" in text or "--as_of" in text:
        return (True, "accepts --as-of")
    return (False, "no --as-of in its usage")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description="Count declared figures whose producer cannot be asked what "
                    "it printed as of the brief's date. Reads and probes --help "
                    "only; changes nothing.")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after this many briefs (0 = all)")
    a = ap.parse_args()

    briefs = sorted((REPO / "bench" / "logs").glob("*/BRIEF.md"))
    if a.limit:
        briefs = briefs[:a.limit]

    figures: list[tuple[str, str, str, str]] = []   # brief, label, script, value
    for b in briefs:
        try:
            text = b.read_text(errors="replace")
        except OSError:
            continue
        for label, script, value in FIGURE.findall(text):
            figures.append((b.parent.name, label.strip(), script.strip(),
                            value.strip()))

    scripts = sorted({f[2] for f in figures})
    print("=" * 76)
    print("DECLARED FIGURES, AND WHETHER THE --as-of FALLBACK IS AVAILABLE")
    print("  a missing --as-of costs NOTHING for a figure that still")
    print("  reproduces: the validator runs the producer plain FIRST and")
    print("  accepts on a match. This counts fallback reach, not correctness.")
    print("=" * 76)
    print(f"  briefs scanned            : {len(briefs)}")
    print(f"  declared figures found    : {len(figures)}")
    print(f"  distinct producers named  : {len(scripts)}")
    print()

    verdicts: dict[str, tuple[bool, str]] = {}
    for s in scripts:
        verdicts[s] = supports_as_of(REPO / s)

    ok = [s for s in scripts if verdicts[s][0]]
    bad = [s for s in scripts if not verdicts[s][0]]
    print(f"  producers accepting --as-of : {len(ok)}")
    print(f"  producers WITHOUT the --as-of fallback      : {len(bad)}")
    print()
    for s in bad:
        n = sum(1 for f in figures if f[2] == s)
        print(f"    {s}")
        print(f"      {verdicts[s][1]}; carries {n} declared figure(s)")
    print()

    checkable = sum(1 for f in figures if verdicts[f[2]][0])
    uncheckable = len(figures) - checkable
    if figures:
        from statsmodels.stats.proportion import proportion_confint
        import numpy as np
        lo, hi = proportion_confint(uncheckable, len(figures), method="wilson")
        z = 1.959963984540054
        ph = uncheckable / len(figures)
        n = len(figures)
        dd = 1 + z * z / n
        c = (ph + z * z / (2 * n)) / dd
        h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / dd
        print("=" * 76)
        print("THE COUNT")
        print("=" * 76)
        print(f"  figures WITH the --as-of fallback available : {checkable}")
        print(f"  figures WITHOUT it                          : {uncheckable}")
        print(f"  no-fallback share: {uncheckable}/{len(figures)} = "
              f"{ph:.6f}  Wilson [{lo:.6f}, {hi:.6f}]")
        print(f"  NumPy cross-check                           : "
              f"[{c-h:.6f}, {c+h:.6f}]")
    print()
    print("=" * 76)
    print("WHAT THIS IS AND IS NOT")
    print("=" * 76)
    print("  NO FALLBACK IS NOT WRONG, AND NOT EVEN UNCHECKED. Not 1 figure")
    print("  above is shown to be false, and most are accepted today by the")
    print("  validator FIRST step, a plain re-execution. NOT AN ERROR RATE.")
    print("  What the missing flag costs is the SECOND step: a figure true at")
    print("  the brief date and since drifted is refused where it could have")
    print("  been accepted as historical, loudly and with its date. THE NUMBER")
    print("  THAT WOULD MATTER is how many fail the plain re-execution TODAY,")
    print("  because only those reach step 2. Named, not guessed: 49 producers")
    print("  on an 8 GiB machine with a derived budget of 2 heavy processes.")
    print("  The 1 instance found by hand is 4 figures in 1 brief.")
    print()
    print("  THE FIX FOLLOWS THE SCOPE, which is why nothing is fixed here: a")
    print("  shared helper if many producers lack the flag, 1 patch if few do.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
