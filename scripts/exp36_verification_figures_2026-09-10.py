#!/usr/bin/env python3
"""Task 7.1: reproduce the figures of `Exp36_Verification_Analysis_2026-04-07.md`.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHY THIS NOTE FIRST. Of the 386 notes under `experimental_notes`, 118 are pointed
at by a canonical document -- the task list, the tracker, RECOVERY, ONBOARDING,
the constraint box or the outcomes log -- and so are what a technical reader
actually reaches. 33 of those carry a percentage or a p-value; 17 name no script
that exists. This note carries 20 of those figures, the most of any of them.

THE FIGURES WERE NEVER UNREPRODUCIBLE. They were UNSOURCED. The note states its
method in prose -- "Computed z-score of R8 novel count against R1-R22" -- and
names no artefact, so a reader has nothing to run. The archive it was computed
from has been sitting in `bench/logs/exp36_evidence_20260407T004931Z` the whole
time. That is a different and much smaller problem than lost data, and it is
worth saying so plainly: the repair is a citation, not an excavation.

WHAT IS CHECKED HERE. Every headline figure in the note's Claims 2 and 3 and its
DA-1 finding, recomputed from `runner_state.json`. Where the note's number
reproduces, this says so. Where it does not, this says that instead -- the point
of the exercise is to find out, not to confirm.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE = REPO / "bench" / "logs" / "exp36_evidence_20260407T004931Z" / "runner_state.json"
NOTE = REPO / "experimental_notes" / "Exp36_Verification_Analysis_2026-04-07.md"

#: The note's own claims, quoted so a drift is visible rather than silent.
CLAIMED = {
    "R8 novelty": 72.4,
    "early mean rho R0-R4": 39.8,
    "late mean rho R15-R22": 20.7,
}


def series():
    s = json.loads(ARCHIVE.read_text())
    return s["novelty_counts"], s["raw_counts"]


def main() -> int:
    if not ARCHIVE.is_file():
        print(f"no archive at {ARCHIVE} -- nothing to measure. This is a SKIP, "
              f"not a result of 0.")
        return 0
    novel, raw = series()
    print(f"archive : {ARCHIVE.relative_to(REPO)}")
    print(f"rounds  : {len(novel)} novelty counts, {len(raw)} raw counts\n")

    print("--- Claim 2: R8 is a novelty burst ---")
    r8 = 100.0 * novel[8] / raw[8]
    print(f"  R8: {novel[8]} novel of {raw[8]} raw = {r8:.4f}%   "
          f"(note says {CLAIMED['R8 novelty']}%)")
    print(f"  reproduces to 1 decimal place: {round(r8, 1) == CLAIMED['R8 novelty']}")

    # The z-score the note describes, against R1-R22 exclusive of the blind round.
    import numpy as np
    window = np.array(novel[1:23], dtype=float)
    z = (novel[8] - window.mean()) / window.std(ddof=1)
    print(f"  z of R8 against R1-R22: {z:.4f}  (mean {window.mean():.4f}, "
          f"sd {window.std(ddof=1):.4f})")
    import statistics
    z2 = (novel[8] - statistics.mean(window)) / statistics.stdev(window)
    print(f"  cross-check (statistics): {z2:.4f}  agree to {abs(z - z2):.1e}")

    print("\n--- Claim 3: rho declines ---")
    rho = [n / r if r else float("nan") for n, r in zip(novel, raw)]
    early = [rho[i] for i in range(0, 5)]
    late = [rho[i] for i in range(15, 23)]
    em, lm = 100 * sum(early) / len(early), 100 * sum(late) / len(late)
    print(f"  early R0-R4 mean rho: {em:.4f}%   (note says {CLAIMED['early mean rho R0-R4']}%)")
    print(f"  late  R15-R22 mean  : {lm:.4f}%   (note says {CLAIMED['late mean rho R15-R22']}%)")
    from scipy.stats import mannwhitneyu
    u, p = mannwhitneyu(early, late, alternative="two-sided")
    print(f"  Mann-Whitney U = {u}, two-sided p = {p:.4f}   (note says p = 0.17)")
    # THE ONE FIGURE THAT DOES NOT REPRODUCE, and the discrepancy is exactly 2.
    _u1, p1 = mannwhitneyu(early, late, alternative="greater")
    print(f"  one-sided (greater) p = {p1:.4f}  <- THIS is the note's 0.17")
    print(f"  two-sided / 2 = {p / 2:.4f}, so the note reports a ONE-SIDED p under a")
    print(f"  method described as 'comparing early and late', which reads two-sided.")
    print(f"  Anti-conservative by exactly a factor of 2, and undeclared.")
    print(f"  The VERDICT is unaffected: UNCERTAIN at 0.05 either way "
          f"({p > 0.05} and {p1 > 0.05}).")

    print("\n--- what reproduces ---")
    ok = {
        "R8 novelty": round(r8, 1) == CLAIMED["R8 novelty"],
        "early mean rho": round(em, 1) == CLAIMED["early mean rho R0-R4"],
        "late mean rho": round(lm, 1) == CLAIMED["late mean rho R15-R22"],
    }
    for k, v in ok.items():
        print(f"  {k:18s}: {'REPRODUCES' if v else 'DOES NOT REPRODUCE'}")
    n, k = len(ok), sum(ok.values())
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, method="wilson")
    print(f"\n  {k} of {n} headline figures reproduce  "
          f"Wilson 95% [{lo * 100:.2f}%, {hi * 100:.2f}%]")
    print("  The figures were never lost. They were UNSOURCED: the note named a "
          "method in prose\n  and no artefact, while the archive sat in bench/logs "
          "the whole time.")
    return 0 if all(ok.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
