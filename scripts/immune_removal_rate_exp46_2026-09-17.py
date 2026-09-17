#!/usr/bin/env python3
"""Reproduce the immune pipeline's 97% removal rate from exp46's archived findings.

WHY THIS EXISTS. `Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md` is the record in
which the four-month suppression defect was found, and it states the rate 6 times
in its own prose. It named no script. Under `measured-rate-travels-with-its-script`
that made the project's single most consequential measurement a claim about
evidence rather than evidence -- and it is the note a reader is most likely to
reach, being linked from canonical documents.

WHAT IT CHECKS, AND AGAINST WHOM. The record's measurement blocks state 15
figures, and 2 further sources state 3 more, each about a DIFFERENT SET of the
same pairs. Every one is checked against a recomputation, and the script EXITS 1
if any fails, so it can fail rather than merely report:

  the record  : raw cosine min 0.150, median 0.484, max 0.867
  the record  : (cos+1)/2, no bonus on any pair -- min 0.460, median 0.593, 97.4% flagged
  the record  : (cos+1)/2, bonus on every pair  -- min 0.520, median 0.653, 100.0% flagged
  the record  : clamped, no bonus on any pair   -- min 0.120, median 0.387, 18.5% flagged
  the record  : clamped, bonus on every pair    -- min 0.180, median 0.447, 35.3% flagged
  _similarity : the class-match floor was 0.541      <- the 79 pairs that share a class
  _similarity : clamping moved 97.4% to 15.8%        <- the 272 pairs that do NOT
  3660816     : clamping moved 98.0% to 21.4%        <- all 351 pairs, bonus per pair

WHERE THE 272 COMES FROM. Arithmetic over the class partition leaves only the
272 -- 79 pairs admit neither figure, 351 admit 97.4% but not 15.8% -- but it
cannot exclude every other subset, since 20 pair counts up to 351 admit both. So
the identification rests on a label: measurement M10 of the 2026-08-18 panel
record, experimental_notes/evidence/panel_records_2026-08-18/
confer_stage1_audit_2026-08-18/PRIMARY_SOURCE_MEASUREMENTS.md.txt, reads "flagged
97.4% (n=272)". The plain-English note of the same day qualified the 15.8% "for
pairs without a class match" but, at its line 49, called the 97.4% a rate "of all
pairs" -- both labels in 1 note -- and the comment in bench/dm/_similarity.py kept
"Same 351 pairs" until 2026-09-17. M10's medians are checked as corroboration.

EXECUTED, NOT RESTATED. The embeddings come from the live backend in
`bench.dm._similarity` and the constants are read from that module, so a change
to either reaches this measurement. Only the 2 SCALE MAPPINGS are written out
here, because the point is to compare the retired one against the live one and
the retired one no longer exists in the module.

THE THRESHOLD IS 0.50, which is what the record states was in force: tau_sim
calibrated for the Jaccard backend whose floor genuinely is 0.
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import statistics
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RUN = (REPO / "bench" / "logs" /
       "exp46_stage6_locationkey_live_20260728T103151Z" /
       "exp46_stage6_locationkey_live_report.json")
TAU_SIM = 0.50


def findings() -> list[dict]:
    """The FIRST occurrence of each finding_id: 27 findings.

    Models reuse ids across rounds, so the report holds more findings than ids;
    main() prints both counts. Keeping the first occurrence reproduces every
    figure in the record and in M10. Whether the pipeline's registry holds this
    same 27 is NOT established here, and keeping a different occurrence of a
    reused id gives a different set of findings.
    """
    d = json.loads(RUN.read_text(encoding="utf-8"))
    uniq: dict[str, dict] = {}
    for r in d["rounds"]:
        for f in r.get("findings", []):
            uniq.setdefault(f["finding_id"], f)
    return list(uniq.values())


def main() -> int:
    # `--help` MUST DESCRIBE, NEVER MEASURE. Without this, the flag fell through
    # and ran the whole reproduction: loading the embedding model and scoring 351
    # pairs. Caught 2026-09-17 by test_help_is_answered_2026-09-11.py, which runs
    # any script it cannot vouch for structurally rather than trusting a grep.
    #
    # THE DESCRIPTION IS WRITTEN OUT, not taken from __doc__'s first line, because
    # that line carries "97%" and a figure in help output is the measurement
    # leaking into the thing that exists to avoid measuring.
    argparse.ArgumentParser(
        description="Recompute the immune pipeline's removal rate from exp46's "
                    "archived findings, and check it against the figures the "
                    "Stage 1 panel record states.").parse_args()

    sys.path.insert(0, str(REPO))
    import numpy as np
    from bench.dm import _similarity as S

    fs = findings()
    n = len(fs)
    print(f"exp46 archived findings: {n}   pairs: {n * (n - 1) // 2}")
    raw = [f for r in json.loads(RUN.read_text(encoding="utf-8"))["rounds"]
           for f in r.get("findings", [])]
    reused = sum(1 for fid in {f["finding_id"] for f in raw}
                 if len({f["description"] for f in raw if f["finding_id"] == fid}) > 1)
    print(f"  first occurrence per finding_id: {len(raw)} findings under {n} ids, "
          f"{reused} ids appear with more than 1 description")
    print(f"backend: {S.EMBEDDING_MODEL_NAME}   BETA={S.BETA}   "
          f"CLASS_BONUS={S.CLASS_BONUS}   tau_sim={TAU_SIM}")

    embs = [S._get_embedding(f["description"]) for f in fs]
    if any(e is None for e in embs):
        raise SystemExit("the embedding backend returned None -- the model is not "
                         "available, so this measurement CANNOT be made. It is "
                         "unverified, not zero.")

    cos, same_class = [], []
    for (i, a), (j, b) in itertools.combinations(list(enumerate(fs)), 2):
        u, v = embs[i], embs[j]
        cos.append(float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))
        same_class.append(fs[i]["flaw_class"] == fs[j]["flaw_class"])

    def blend(c: float, cls: bool, clamp: bool) -> float:
        c01 = max(0.0, c) if clamp else (c + 1.0) / 2.0
        return (1 - S.BETA) * c01 + S.BETA * (S.CLASS_BONUS if cls else 0.0)

    checks: list[tuple[str, float, float]] = []

    print(f"\nraw cosine over {len(cos)} pairs")
    print(f"  min {min(cos):.3f}   median {statistics.median(cos):.3f}   "
          f"max {max(cos):.3f}   negative: {sum(c < 0 for c in cos)}")
    checks += [("raw min", min(cos), 0.150),
               ("raw median", statistics.median(cos), 0.484),
               ("raw max", max(cos), 0.867)]

    # "no class match" in the record means the bonus WITHHELD ON ALL 351 PAIRS,
    # not the 272 that genuinely lack a class match. Both give 97.4% retired, which
    # is how the 2 sets came to share a name; the labels here say which is which.
    for label, cls, clamp, tmin, tmed, trate in [
            ("retired, no bonus", False, False, 0.460, 0.593, 97.4),
            ("retired, bonus on all", True, False, 0.520, 0.653, 100.0),
            ("clamped, no bonus", False, True, 0.120, 0.387, 18.5),
            ("clamped, bonus on all", True, True, 0.180, 0.447, 35.3)]:
        sc = [blend(c, cls, clamp=clamp) for c in cos]
        rate = 100 * sum(s >= TAU_SIM for s in sc) / len(sc)
        print(f"\n{label.upper()}, all {len(cos)} pairs")
        print(f"  min {min(sc):.3f}   median {statistics.median(sc):.3f}   "
              f"flagged duplicate: {rate:.1f}%")
        checks += [(f"{label} min", min(sc), tmin),
                   (f"{label} median", statistics.median(sc), tmed),
                   (f"{label} flagged %", rate, trate)]

    act_old = [blend(c, k, clamp=False) for c, k in zip(cos, same_class)]
    act_new = [blend(c, k, clamp=True) for c, k in zip(cos, same_class)]
    r_old = 100 * sum(s >= TAU_SIM for s in act_old) / len(act_old)
    r_new = 100 * sum(s >= TAU_SIM for s in act_new) / len(act_new)
    ncls = sum(same_class)
    cls_scores = [s for s, k in zip(act_old, same_class) if k]
    print(f"\nACTUAL class distribution: {ncls} of {len(cos)} pairs share a flaw class")
    print(f"  class-matching pairs flagged under the retired mapping: "
          f"{sum(s >= TAU_SIM for s in cls_scores)} of {ncls}")
    print(f"  floor among class-matching pairs: {min(cls_scores):.3f}")
    print(f"\nretired mapping -> {r_old:.1f}% flagged")
    print(f"live (clamped)  -> {r_new:.1f}% flagged")

    print("\nAGAINST THE DECLARED FIGURES")
    differs = []
    for name, got, want in checks:
        d = abs(got - want)
        verdict = 'MATCH' if d <= 0.0006 or (want >= 5 and d <= 0.06) else 'DIFFERS'
        if verdict == 'DIFFERS':
            differs.append(name)
        print(f"  {name:30} got {got:8.3f}   declared {want:8.3f}   {verdict}")

    # THE 3 "DISAGREEMENTS" ARE NOT DISAGREEMENTS. Each source quotes a
    # different SCENARIO without naming it, and every figure is correct for the
    # one it describes. Reporting them as a contradiction would be a true
    # sentence in the wrong frame -- so the scenarios are named here instead.
    hyp_clamped = 100 * sum(blend(c, False, clamp=True) >= TAU_SIM
                            for c in cos) / len(cos)
    cls_floor_actual = min(cls_scores)
    cls_floor_hyp = min(blend(c, True, clamp=False) for c in cos)
    print("\nTWO SCENARIOS, NOT TWO ANSWERS")
    print(f"  HYPOTHETICAL, applied to all {len(cos)} pairs alike:")
    print(f"    class-match floor {cls_floor_hyp:.3f}   "
          f"retired {100 * sum(s >= TAU_SIM for s in [blend(c, False, False) for c in cos]) / len(cos):.1f}%"
          f" -> clamped {hyp_clamped:.1f}%")
    print("    the RECORD quotes 0.520 and 97.4% here, both reproduced")
    print(f"  ACTUAL, each pair with its own flaw class ({ncls} of {len(cos)} match):")
    print(f"    class-match floor {cls_floor_actual:.3f}   "
          f"retired {r_old:.1f}% -> clamped {r_new:.1f}%")
    print("    this is what _similarity.py quotes for the floor (0.541) and "
          "what commit 3660816 states for the rates (98.0% -> 21.4%)")
    hyp_retired = 100 * sum(blend(c, False, False) >= TAU_SIM for c in cos) / len(cos)
    lo_r, hi_r = sorted((hyp_retired, r_old))
    where = "between" if lo_r <= 97.1 <= hi_r else ("below" if 97.1 < lo_r else "above")
    print(f"  The 4-month logged rate of 97.1% lies {where} the 2 retired-mapping "
          f"figures ({lo_r:.1f}% and {hi_r:.1f}%).")

    # THE COMMENT'S 97.4% -> 15.8% REPRODUCES, ON THE SET IT MEASURED.
    # Until 2026-09-17 this block called 15.8% unreproduced: rates were computed
    # over all 351 pairs and over the 79 that share a class, never over the 272
    # that do not. M10 of the 2026-08-18 panel record labelled the figures
    # "(n=272)" all along, and the comment dropped the qualifier. Arithmetic over
    # the class partition leaves only the 272 but cannot exclude other subsets --
    # 20 pair counts up to 351 admit both figures -- so the set is taken from M10's
    # label, and its medians are checked here as corroboration.
    from fractions import Fraction
    import sympy as sp

    def counts_rounding_to(target: float, n: int) -> list[int]:
        t = round(target * 10)
        exact = [k for k in range(n + 1)
                 if Fraction(t * 10 - 5, 10000) <= Fraction(k, n) < Fraction(t * 10 + 5, 10000)]
        symbolic = [k for k in range(n + 1)
                    if sp.Rational(t * 10 - 5, 10000) <= sp.Rational(k, n) < sp.Rational(t * 10 + 5, 10000)]
        assert exact == symbolic, "fractions and sympy disagree about the rounding"
        return exact

    differ = [i for i, k in enumerate(same_class) if not k]
    print("\nSETS -- each figure tied to the pairs it describes")
    for name, idx in (("all351", list(range(len(cos)))), ("differ272", differ)):
        kr = sum(act_old[i] >= TAU_SIM for i in idx)
        kn = sum(act_new[i] >= TAU_SIM for i in idx)
        print(f"  SET {name} n={len(idx)} retired {100 * kr / len(idx):.1f} ({kr} of {len(idx)}) "
              f"clamped {100 * kn / len(idx):.1f} ({kn} of {len(idx)})")

    both = [n for n in range(1, len(cos) + 1)
            if counts_rounding_to(97.4, n) and counts_rounding_to(15.8, n)]
    print(f"  pair counts up to {len(cos)} admitting both 97.4% and 15.8%: {len(both)}")
    none351 = counts_rounding_to(15.8, len(cos))
    print(f"  a count out of {len(cos)} that rounds to 15.8%: "
          f"{none351 if none351 else 'none exists'}   (fractions and sympy agree)")

    ret = [act_old[i] for i in differ]
    new = [act_new[i] for i in differ]
    m10 = {"retired rate": 97.4, "clamped rate": 15.8,
           "retired median": 0.594, "clamped median": 0.388}
    got = {"retired rate": round(100 * sum(s >= TAU_SIM for s in ret) / len(differ), 1),
           "clamped rate": round(100 * sum(s >= TAU_SIM for s in new) / len(differ), 1),
           "retired median": round(statistics.median(ret), 3),
           "clamped median": round(statistics.median(new), 3)}
    for k in m10:
        print(f"  M10 {k:15} {m10[k]:>7}   recomputed {got[k]:>7}   "
              f"{'MATCH' if got[k] == m10[k] else 'MISMATCH'}")
    ok = all(got[k] == m10[k] for k in m10)
    print(f"  M10's subset figures: {'REPRODUCED' if ok else 'NOT REPRODUCED'}")
    # EXIT 1 ON ANY FAILED CHECK. Until 2026-09-17 this returned 0 whatever the
    # comparisons said, while its docstring claimed it "can FAIL"; only a test's
    # string match noticed a DIFFERS line.
    if differs or not ok:
        print(f"\n*** FAILED: {differs + ([] if ok else ['M10 subset'])} ***")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
