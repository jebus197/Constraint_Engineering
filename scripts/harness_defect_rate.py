#!/usr/bin/env python3
"""The harness-defect rate over time. RECORD ONLY -- nothing reads this to decide.

WHY THIS EXISTS. Fable's Q3 dissent, 2026-08-23: the phrase "demonstrably closer to
iron-clad" requires a convergence curve -- defects found per run over time -- and
nothing in the project tracked one. The founder authorised recording it on the
grounds that the same series could later feed the capability mechanics, since a
falling harness-defect rate is what licenses trusting the instrument's own
competence measurements. How that feed would work is not designed and is not
attempted here.

WHAT IT MEASURES, AND WHY IT IS THE PROJECT'S OWN MEASURE ONE LEVEL UP. gamma is a
Duane NHPP decay parameter fitted to CUMULATIVE novel findings within a run; it rises
as discovery saturates. This fits the same model to harness defects across runs. The
founder's picture (a cumulative curve rising to an asymptote, the asymptote marking
the space explored) and Fable's picture (a rate curve bending down) are ONE curve seen
from two sides -- cumulative flattening IS rate decay. Neither was wrong.

WHAT IT CANNOT DO, STATED PLAINLY. A defect nobody found is not in the ledger, so
every count is a LOWER BOUND and the series measures found-defects, never
present-defects. A run that nobody audited scores zero and looks perfect. The series
is therefore evidence only when paired with comparable audit effort per run, which is
recorded here as `reconstructed` and must be read before the numbers are.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LEDGER = REPO / "experimental_notes/data/harness_defect_ledger.json"


def duane_gamma(cumulative: list) -> float | None:
    """Duane NHPP decay parameter by log-log regression, as the runner computes it.

    Returns None below three points: two points fit any line exactly and the slope
    would be an artefact of having no room to be wrong.
    """
    pts = [(i + 1, c) for i, c in enumerate(cumulative) if c > 0]
    if len(pts) < 3:
        return None
    xs = [math.log(t) for t, _ in pts]
    ys = [math.log(c / t) for t, c in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return -sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def main() -> int:
    if not LEDGER.is_file():
        print(f"  no ledger at {LEDGER.relative_to(REPO)}")
        return 1
    d = json.loads(LEDGER.read_text())
    entries = sorted(d["entries"], key=lambda e: e["date"])

    print("  HARNESS-DEFECT RATE  (record only; nothing reads this to decide)\n")
    print(f"  {'date':<12} {'occasion':<22} {'new':>4} {'cum':>5}  {'blocking':>8}  source")
    cum, series = 0, []
    for e in entries:
        n = len(e["defects"])
        cum += n
        series.append(cum)
        blocking = sum(1 for x in e["defects"] if x.get("severity") == "blocking")
        src = "reconstructed" if e.get("reconstructed") else "measured in flight"
        print(f"  {e['date']:<12} {e['occasion'][:22]:<22} {n:>4} {cum:>5}  {blocking:>8}  {src}")

    g = duane_gamma(series)
    print(f"\n  occasions: {len(entries)}    defects: {cum}")
    if g is None:
        print(f"  gamma: NOT COMPUTED — {len(series)} occasion(s), needs 3.")
        print("  This is the honest state of the series, not a placeholder. Two points")
        print("  fit any line exactly, so a slope here would be arithmetic, not evidence.")
    else:
        verdict = ("SATURATING — the rate is falling" if g > 0.1 else
                   "FLAT — churn, not convergence" if g > -0.1 else
                   "DIVERGING — each fix is opening more than it closes")
        print(f"  gamma (Duane, harness defects across occasions): {g:+.3f}   {verdict}")

    who = {}
    for e in entries:
        for x in e["defects"]:
            who[x.get("author", "?")] = who.get(x.get("author", "?"), 0) + 1
    print("\n  by author: " + ", ".join(f"{k} {v}" for k, v in sorted(who.items(), key=lambda kv: -kv[1])))
    finders = {}
    for e in entries:
        for x in e["defects"]:
            for f in (x.get("finder", "?")).split("+"):
                finders[f] = finders.get(f, 0) + 1
    print("  by finder: " + ", ".join(f"{k} {v}" for k, v in sorted(finders.items(), key=lambda kv: -kv[1])))
    rendered = {}
    for e in entries:
        for x in e["defects"]:
            r = x.get("rendered_as", "?")
            rendered[r] = rendered.get(r, 0) + 1
    print("  rendered as: " + ", ".join(f"{k} {v}" for k, v in sorted(rendered.items(), key=lambda kv: -kv[1])))
    print("\n  READ THIS BEFORE THE NUMBERS: a defect nobody found is not counted, so every")
    print("  figure is a LOWER BOUND. An unaudited run scores zero and looks perfect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
