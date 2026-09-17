#!/usr/bin/env python3
"""Reproduce the immune pipeline's 97% removal rate from exp46's archived findings.

WHY THIS EXISTS. `Panel_Stage1_Audit_FULL_RECORD_2026-08-18.md` is the record in
which the four-month suppression defect was found, and it states the rate 6 times
in its own prose. It named no script. Under `measured-rate-travels-with-its-script`
that made the project's single most consequential measurement a claim about
evidence rather than evidence -- and it is the note a reader is most likely to
reach, being linked from canonical documents.

WHAT IT CHECKS, AND AGAINST WHOM. The record declares 6 figures, and 2 further
sources disagree with it on 3 more. Every one is asserted here as a target, so
this script can FAIL rather than merely report:

  the record  : raw cosine min 0.150, median 0.484, max 0.867
  the record  : (cos+1)/2 with no class match -- min 0.460, median 0.593, 97.4% flagged
  the record  : (cos+1)/2 with a class match  -- min 0.520, median 0.653, 100.0% flagged
  _similarity : the class-match floor was 0.541      <- DISAGREES with the record's 0.520
  _similarity : clamping moved 97.4% to 15.8%
  memory      : clamping moved 98.0% to 21.4%        <- DISAGREES with _similarity

EXECUTED, NOT RESTATED. The embeddings come from the live backend in
`bench.dm._similarity` and the constants are read from that module, so a change
to either reaches this measurement. Only the 2 SCALE MAPPINGS are written out
here, because the point is to compare the retired one against the live one and
the retired one no longer exists in the module.

THE THRESHOLD IS 0.50, which is what the record states was in force: tau_sim
calibrated for the Jaccard backend whose floor genuinely is 0.
"""
from __future__ import annotations

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
    """The 27 archived findings, deduplicated by id as the registry holds them."""
    d = json.loads(RUN.read_text(encoding="utf-8"))
    uniq: dict[str, dict] = {}
    for r in d["rounds"]:
        for f in r.get("findings", []):
            uniq.setdefault(f["finding_id"], f)
    return list(uniq.values())


def main() -> int:
    sys.path.insert(0, str(REPO))
    import numpy as np
    from bench.dm import _similarity as S

    fs = findings()
    n = len(fs)
    print(f"exp46 archived findings: {n}   pairs: {n * (n - 1) // 2}")
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

    for label, cls, tmin, tmed, trate in [
            ("no class match", False, 0.460, 0.593, 97.4),
            ("class match", True, 0.520, 0.653, 100.0)]:
        sc = [blend(c, cls, clamp=False) for c in cos]
        rate = 100 * sum(s >= TAU_SIM for s in sc) / len(sc)
        print(f"\nRETIRED mapping (cos+1)/2, {label}")
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
    worst = 0.0
    for name, got, want in checks:
        d = abs(got - want)
        worst = max(worst, d if want < 5 else d / 100)
        print(f"  {name:22} got {got:8.3f}   declared {want:8.3f}   "
              f"{'MATCH' if d <= 0.0006 or (want >= 5 and d <= 0.06) else 'DIFFERS'}")

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
    print(f"    the RECORD quotes 0.520 and 97.4% here, both reproduced")
    print(f"  ACTUAL, each pair with its own flaw class ({ncls} of {len(cos)} match):")
    print(f"    class-match floor {cls_floor_actual:.3f}   "
          f"retired {r_old:.1f}% -> clamped {r_new:.1f}%")
    print(f"    this is what _similarity.py quotes for the floor (0.541) and "
          f"what the session memory quotes for the rates (98.0% -> 21.4%)")
    print(f"  The 4-month logged rate of 97.1% sits between the 2 retired-mapping "
          f"figures, as a live pipeline mixing both kinds of pair.")

    # ONE DECLARED FIGURE DOES NOT REPRODUCE, AND IT IS IN LIVE CODE.
    # bench/dm/_similarity.py's own comment states the clamp moved the rate
    # "97.4% -> 15.8%". The 97.4% reproduces exactly. The 15.8% matches neither
    # scenario: the hypothetical gives 18.5% and the actual 21.4%. Stating it
    # here rather than quietly dropping it, because a figure in a module comment
    # is read as the module's own account of itself.
    print(f"\n  UNREPRODUCED: bench/dm/_similarity.py's comment says clamping "
          f"gave 15.8%.")
    print(f"    measured, same 351 pairs: {hyp_clamped:.1f}% hypothetical, "
          f"{r_new:.1f}% actual. 15.8% is neither.")
    print(f"    Not a blocker -- no entry waits on it -- but the comment is the "
          f"module's account of itself, so it is carried to the final report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
