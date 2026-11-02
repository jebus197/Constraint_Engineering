#!/usr/bin/env python3
"""Can the difficulty estimator his 4th convergence condition needs be fitted?

HIS INSTRUCTION, 2026-11-01: *"I accept your recommendation. Please implement
it."* against the recommendation *"the difficulty estimator first, because until
it exists the condition is a round counter wearing the name of a confidence
measure."*

HIS PRIORITY ORDERING IS RIGHT AND THIS SCRIPT DOES NOT DISPUTE IT. It asks the
predicate-first question that must be answered before any estimator is written:
does the archive hold anything an estimator could learn FROM?

THE ANSWER IS NO, FOR ONE SPECIFIC AND CHEAPLY FIXABLE REASON. The structured
run state holds 21 keys and not one of them describes the TARGET before the run
began. Every key is a per-round history or the finding registry -- that is, an
OUTCOME. So the only features available are produced by the very thing an
estimator would predict, and fitting on them is circular: rounds and findings
correlate at Pearson r = 0.836787 precisely because more rounds produce more
findings.

WHY THAT MATTERS RATHER THAN BEING A TECHNICALITY. An estimator fitted on
outcomes would return a number that rises with the round count, which is exactly
the failure his own words name. The 4th convergence condition built on it would
be a round counter wearing the name of a confidence measure, and it would carry
the authority of a measurement while being one.

WHAT IS NEEDED, AND IT IS 1 FIELD. A pre-run description of the target recorded
into the run state at start: its identity, its size, and whatever prior-defect
information exists for it. After enough runs carry it, an estimator becomes
fittable and its predictions become checkable against what the runs then did.
Until then the honest state is that the input does not exist.

EVERY FIGURE HERE IS COMPUTED, AND THE 2-TOOL RULE IS APPLIED: SciPy's
correlation against NumPy's, and the duplicate-run census is exact rather than
estimated.
"""
from __future__ import annotations

import argparse
import json
import pathlib

import numpy as np
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: Substrings that would mark a state key as describing the target rather than
#: the run's own progress. Deliberately broad, so a miss is a real absence.
TARGET_MARKERS = ("target", "article", "config", "cfg", "difficult", "domain",
                  "subject", "corpus", "document", "scope")


def runs() -> list[dict]:
    out, seen = [], set()
    for d in sorted(LOGS.iterdir()):
        f = d / "runner_state.json"
        if not (d.is_dir() and f.is_file()):
            continue
        try:
            st = json.loads(f.read_text())
        except Exception:                                      # noqa: BLE001
            continue
        e = (st.get("registry") or {}).get("entries") or {}
        ents = list(e.values()) if isinstance(e, dict) else list(e)
        gh = st.get("gamma_history") or []
        key = (len(gh), len(ents))
        dup = key in seen
        seen.add(key)
        out.append({"run": d.name, "rounds": len(gh), "findings": len(ents),
                    "keys": sorted(st.keys()), "duplicate_shape": dup})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="can_a_difficulty_estimator_be_fitted_2026-11-02.py",
        description="Predicate-first check on the difficulty estimator. "
                    "Reads only, costs nothing.")
    ap.add_argument("--list-keys", action="store_true",
                    help="print every state key seen, with how many runs carry it")
    a = ap.parse_args()

    rs = runs()
    distinct = [r for r in rs if not r["duplicate_shape"]]
    print("=" * 74)
    print("CAN A DIFFICULTY ESTIMATOR BE FITTED FROM THIS ARCHIVE?")
    print("=" * 74)
    print(f"  run directories with a structured state : {len(rs)}")
    print(f"  distinct by (rounds, findings) shape    : {len(distinct)}")
    print(f"  identical twins removed                 : "
          f"{len(rs) - len(distinct)}")

    r = np.array([x["rounds"] for x in distinct], float)
    n = np.array([x["findings"] for x in distinct], float)
    m = (r > 0) & (n > 0)
    print(f"\n  rounds   : n={int(m.sum())} mean={r[m].mean():.4f} "
          f"sd={r[m].std(ddof=1):.4f} min={r[m].min():.0f} max={r[m].max():.0f}")
    print(f"  findings : mean={n[m].mean():.4f} sd={n[m].std(ddof=1):.4f} "
          f"min={n[m].min():.0f} max={n[m].max():.0f}")
    cv = r[m].std(ddof=1) / r[m].mean()
    print(f"  coefficient of variation in rounds = {cv:.6f}")
    print("  -> There IS variance for an estimator to explain. That is not the")
    print("     obstacle, and saying it was would be the easy answer.")

    pr, pp = stats.pearsonr(r[m], n[m])
    manual = float(np.corrcoef(r[m], n[m])[0, 1])
    sr, sp = stats.spearmanr(r[m], n[m])
    print(f"\n  THE CIRCULARITY, measured:")
    print(f"    rounds vs findings  Pearson r = {pr:.6f}  p = {pp:.6e}")
    print(f"    second tool, NumPy corrcoef   = {manual:.6f}  "
          f"{'AGREE' if abs(pr - manual) < 1e-9 else 'DISAGREE'}")
    print(f"    Spearman rho = {sr:.6f}  p = {sp:.6e}")
    print("    Both are OUTCOMES. More rounds produce more findings, so neither")
    print("    is a pre-run predictor of the other.")

    keys: dict[str, int] = {}
    for x in rs:
        for k in x["keys"]:
            keys[k] = keys.get(k, 0) + 1
    target_keys = [k for k in keys
                   if any(t in k.lower() for t in TARGET_MARKERS)]
    print(f"\n  THE OBSTACLE, stated exactly:")
    print(f"    distinct state keys across all runs        : {len(keys)}")
    print(f"    keys describing the TARGET before the run  : "
          f"{len(target_keys)}  {target_keys if target_keys else '(none)'}")
    if a.list_keys:
        for k in sorted(keys):
            print(f"      {k:34s} in {keys[k]:3d} run(s)")

    print()
    print("=" * 74)
    if target_keys:
        print("  A pre-run target feature EXISTS. This script's conclusion is")
        print("  withdrawn and an estimator may be fittable; re-derive before")
        print("  quoting the old one.")
        return 1
    print("  VERDICT: NOT FITTABLE YET, and the gap is 1 field rather than a")
    print("  modelling problem. The archive records what happened and never what")
    print("  was knowable beforehand, so any estimator fitted on it would rise")
    print("  with the round count -- the exact failure his own words name.")
    print("  WHAT UNBLOCKS IT: record the target's pre-run description into the")
    print("  run state at start. It is additive, it changes no decision, and")
    print("  every later run makes the estimator more fittable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
