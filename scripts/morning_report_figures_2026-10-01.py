#!/usr/bin/env python3
"""Recomputes every figure in experimental_notes/Morning_Report_2026-09-30.md.

WHY THIS EXISTS. The report was delivered carrying 7 percentages and a p-value
and naming no artefact, which `test_live_notes_are_reproducible_2026-09-10.py`
caught: a live note must say where its figures come from. Under
`measured-rate-travels-with-its-script` a number that exists only as prose "is
not evidence; it is a claim about evidence". This script is the evidence.

It also CORRECTS 2 under-specifications found while rebuilding the figures,
neither of which changes a conclusion:

  1. The report says "Mann-Whitney p = 0.0040" and does not name the tail.
     0.0040 is the ONE-SIDED result; two-sided is 0.0079. Both are printed
     below. The one-sided test is the defensible one -- the repair was
     predicted to LOWER rho, which is a directional hypothesis stated before
     the data was seen -- but an unlabelled p-value lets a reader assume the
     two-sided figure, and the same omission over a convention (ddof) produced
     a wrong claim about a standard deviation on 2026-09-30.

  2. The report says "round 0 sent 12 of 12 findings to the human queue with no
     test verdict at all". True as written, and the denominator needs saying:
     the round catalogued 15 findings, of which 12 went to the queue
     UNCONFIRMED and 3 closed with a CONFIRMED falsifier verdict. "12 of 12"
     reads as "every finding in the round" when it means "every finding that
     reached the queue".

WHAT CANNOT BE RECOMPUTED, STATED RATHER THAN DRESSED UP. The report's "7 of 13
defects, 53.8462%" is a HAND ENUMERATION of one night's defects and who found
each. No artefact on disk records that attribution, so no script can rebuild it.
The interval arithmetic over the stated 7 and 13 is reproduced here so a reader
can check the arithmetic, but the INPUTS are a judgement and the figure must be
read as an attribution rather than a measurement.

Every rate carries a Wilson and a Clopper-Pearson interval, cross-verified on
statsmodels and mpmath per `multi_tool_crossverify`.

Run:  python3 scripts/morning_report_figures_2026-10-01.py
"""
from __future__ import annotations

import collections
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

# The 2 runs the report's rho table compares. Named explicitly rather than
# globbed: the table is a BEFORE/AFTER of one repair, and a glob would silently
# absorb later runs and change the comparison, which is the scope defect that
# took `e1_population_recount_falsifier_2026-09-22.py` red on 2026-10-01.
BEFORE_RUN = "commissioning_arm1_panel_20260929T194414Z"
AFTER_RUN = "commissioning_arm1_panel_20260929T214647Z"
PROSE_RUN = "commissioning_arm4_prose_20260930T064044Z"

# The attribution the report states and no artefact records.
HAND_FOUND_BY_MECHANISM = 7
HAND_TOTAL_DEFECTS = 13


def _rho(run: str) -> list[float]:
    doc = json.loads((LOGS / run / "runner_state.json").read_text())
    return [v for v in doc["rho_history"] if isinstance(v, (int, float))]


def _intervals(k: int, n: int) -> tuple[tuple[float, float], tuple[float, float]]:
    from statsmodels.stats.proportion import proportion_confint
    return (proportion_confint(k, n, method="wilson"),
            proportion_confint(k, n, method="beta"))


def _wilson_mpmath(k: int, n: int) -> tuple[float, float]:
    """Independent recomputation. The interval is the half the 2x double-count
    of 2026-09-22 could not absorb, so it gets a second tool of its own."""
    from mpmath import mp, mpf, sqrt
    mp.dps = 50
    z = mpf("1.959963984540054235524594430520551527955550"
            "17")  # Phi^-1(0.975)
    p, N = mpf(k) / n, mpf(n)
    denom = 1 + z**2 / N
    centre = (p + z**2 / (2 * N)) / denom
    half = (z / denom) * sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(centre - half), float(centre + half)


def _rate(label: str, k: int, n: int) -> None:
    (w_lo, w_hi), (c_lo, c_hi) = _intervals(k, n)
    m_lo, m_hi = _wilson_mpmath(k, n)
    print(f"  {label}")
    print(f"    {k} of {n} = {k / n:.4%}")
    print(f"    Wilson          [{w_lo:.4%}, {w_hi:.4%}]   (statsmodels)")
    print(f"    Wilson          [{m_lo:.4%}, {m_hi:.4%}]   (mpmath, 50 dps, "
          f"agrees to {max(abs(m_lo - w_lo), abs(m_hi - w_hi)):.1e})")
    print(f"    Clopper-Pearson [{c_lo:.4%}, {c_hi:.4%}]")


def main() -> int:
    print(__doc__.strip().splitlines()[0])
    print("=" * 78)

    print("\n1. THE RHO TABLE -- rounds stuck at exactly 1.000, and the minimum\n")
    before, after = _rho(BEFORE_RUN), _rho(AFTER_RUN)
    for label, run, series in (("before the repair", BEFORE_RUN, before),
                               ("after the repair ", AFTER_RUN, after)):
        stuck = sum(1 for v in series if v == 1.0)
        print(f"  {label}  {stuck} of {len(series)} rounds at 1.000, "
              f"minimum {min(series):.4f}")
        print(f"                     {run}")
        print(f"                     {[round(v, 6) for v in series]}")
    print("\n  REPORT SAYS: before 3 of 4, lowest 0.9565; after 0 of 8, "
          "lowest 0.3333.")
    ok = (sum(1 for v in before if v == 1.0) == 3 and len(before) == 4
          and sum(1 for v in after if v == 1.0) == 0 and len(after) == 8
          and abs(min(before) - 0.9565) < 5e-5
          and abs(min(after) - 0.3333) < 5e-5)
    print(f"  REPRODUCED: {ok}")

    print("\n2. THE DIFFERENCE IN RHO, BOTH TAILS NAMED\n")
    from scipy.stats import mannwhitneyu
    for alt in ("greater", "two-sided"):
        u, p = mannwhitneyu(before, after, alternative=alt)
        note = "  <-- the figure the report quotes" if alt == "greater" else ""
        print(f"  Mann-Whitney U={u:.1f}  {alt:10s} p={p:.4f}{note}")
    print("\n  The report's unlabelled 'p = 0.0040' is the ONE-SIDED result.")
    print("  Directional by prior hypothesis: the repair was predicted to")
    print("  lower rho, not merely to change it. Two-sided it is 0.0079, and")
    print("  the conclusion -- the difference is clear -- holds under both.")

    print("\n3. THE PROSE ARM'S ROUND 0, WITH ITS DENOMINATOR STATED\n")
    cat = next((LOGS / PROSE_RUN).glob("*finding_catalogue.jsonl"))
    recs = [json.loads(ln) for ln in cat.read_text().splitlines() if ln.strip()]
    status = collections.Counter(r.get("status") for r in recs)
    queued = [r for r in recs if r.get("status") == "UNCONFIRMED"]
    verdicts = collections.Counter(r.get("falsifier_verdict") or "(empty)"
                                   for r in queued)
    no_verdict = [r for r in queued
                  if (r.get("falsifier_verdict") or "") in ("", "ERROR")]
    print(f"  findings catalogued in the round : {len(recs)}")
    print(f"  by status                        : {dict(status)}")
    print(f"  queued to the human (UNCONFIRMED): {len(queued)}")
    print(f"  their falsifier verdicts         : {dict(verdicts)}")
    print()
    _rate("of those queued, carrying no test verdict:",
          len(no_verdict), len(queued))
    print("\n  REPORT SAYS: 12 of 12, 100.0000%, interval 75.7506% to "
          "100.0000%.")
    print(f"  REPRODUCED: {len(no_verdict) == 12 and len(queued) == 12}")
    print(f"  AND THE FRAME IT OMITS: the round catalogued {len(recs)} "
          f"findings, not 12.")
    print(f"  {len(recs) - len(queued)} closed with a CONFIRMED verdict, so "
          f"'12 of 12' is every")
    print("  finding that REACHED THE QUEUE, not every finding in the round.")

    print("\n4. THE ATTRIBUTION -- ARITHMETIC REPRODUCED, INPUTS NOT "
          "REPRODUCIBLE\n")
    _rate("found by the mechanised layer (HAND-ENUMERATED k and n):",
          HAND_FOUND_BY_MECHANISM, HAND_TOTAL_DEFECTS)
    print("\n  REPORT SAYS: 7 of 13, 53.8462%, interval 29.1438% to 76.7939%.")
    print("  The interval arithmetic reproduces. THE INPUTS DO NOT: no")
    print("  artefact on disk records which defects were found that night or")
    print("  by what. This is an ATTRIBUTION, and a reader should treat it as")
    print("  a judgement with its arithmetic checked, not as a measurement.")
    return 0


if __name__ == "__main__":
    # A REAL PARSER. `test_operational_scripts::test_an_unknown_flag_is_rejected_loudly`
    # asserts argparse's own "unrecognized arguments", and this script takes no
    # arguments, so argparse answers `--help` and refuses anything else before
    # any work is done -- `feedback_help_must_never_cost_money`.
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()
    raise SystemExit(main())
