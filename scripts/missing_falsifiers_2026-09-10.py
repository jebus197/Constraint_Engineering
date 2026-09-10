#!/usr/bin/env python3
"""Task 2.2: how many falsifiers are actually missing, and which?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING: "fix and test all remaining missing falsifiers." Before any of them
can be fixed, "all" has to mean something countable, and the obvious count is
wrong by a factor of 29.

THE NAIVE COUNT IS 817 AND IT IS A CATEGORY ERROR. Sweeping every archived
registry for a critical finding with an empty `falsifier_code` returns 817. But
the falsifier mechanism was BUILT on 2026-06-03 -- components at `ed12c7f`, the
voting replacement at `4fba6cc`. A run from April could not carry a falsifier,
and calling that a missing falsifier is like calling a 1990 car's missing airbag
a manufacturing defect. Split at the build date: 789 pre-mechanism, 28 after.

28 IS THE TASK. Each one is a critical finding, raised after the machinery
existed to test it, that was never tested.

WHY THE CONTROLS ARE COUNTED SEPARATELY. exp53 and exp55 are ZERO-PLANT CONTROLS
-- targets with no defects deliberately planted. A finding raised against a
control is a candidate false positive, so an absent falsifier there is a
different question from one against a live target: writing it does not confirm a
defect, it tests whether the finding was real at all. Both are reported.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The date the falsifier mechanism landed. Before it, absence is not omission.
MECHANISM_BUILT = "20260603"

#: Severity at or above which a finding is "critical" in this project.
CRITICAL = 0.7


def _stamp(dirname: str) -> str:
    for tok in dirname.split("_"):
        if tok.startswith("20") and len(tok) >= 8 and tok[:8].isdigit():
            return tok[:8]
    return "00000000"


def entries(state: dict) -> list[dict]:
    reg = state["registry"]
    ent = reg.get("entries", reg) if isinstance(reg, dict) else reg
    vals = list(ent.values()) if isinstance(ent, dict) else list(ent)
    return [v for v in vals if isinstance(v, dict)]


def survey() -> dict:
    pre, post = [], []
    for r in sorted((REPO / "bench" / "logs").glob("exp*/runner_state.json")):
        name = r.parent.name
        try:
            rows = entries(json.loads(r.read_text()))
        except (ValueError, OSError, KeyError):
            continue
        crit = [v for v in rows
                if isinstance(v.get("severity"), (int, float))
                and v["severity"] >= CRITICAL]
        miss = [v for v in crit if not (v.get("falsifier_code") or "").strip()]
        bucket = pre if _stamp(name) < MECHANISM_BUILT else post
        for v in miss:
            bucket.append({"run": name, "id": v.get("canonical_id"),
                           "status": v.get("status"),
                           "severity": v.get("severity"),
                           "verdict": v.get("falsifier_verdict"),
                           "control": "control" in name,
                           "description": (v.get("description") or "")[:110]})
    return {"pre": pre, "post": post}


def main() -> int:
    s = survey()
    pre, post = s["pre"], s["post"]
    print(f"critical findings with an EMPTY falsifier: {len(pre) + len(post)} in total")
    print(f"  {len(pre)} raised BEFORE the mechanism existed ({MECHANISM_BUILT}) "
          f"-- not omissions")
    print(f"  {len(post)} raised after it -- THIS is the population of task 2.2\n")

    live = [r for r in post if not r["control"]]
    ctrl = [r for r in post if r["control"]]
    print(f"  against LIVE targets  : {len(live)}")
    print(f"  against ZERO-PLANT CONTROLS: {len(ctrl)}  (a finding here is a "
          f"candidate false positive;\n      writing its falsifier tests whether "
          f"the finding was real, not whether a defect is)\n")

    by_run = collections.Counter(r["run"] for r in post)
    for run, n in sorted(by_run.items()):
        ids = sorted(r["id"] for r in post if r["run"] == run)
        print(f"  {run}: {n}  {ids}")

    print("\n  by recorded verdict:",
          dict(collections.Counter(str(r["verdict"]) for r in post)))
    print("  by status           :",
          dict(collections.Counter(str(r["status"]) for r in post)))

    from statsmodels.stats.proportion import proportion_confint
    tot_post_crit = 0
    for r in sorted((REPO / "bench" / "logs").glob("exp*/runner_state.json")):
        if _stamp(r.parent.name) < MECHANISM_BUILT:
            continue
        try:
            rows = entries(json.loads(r.read_text()))
        except (ValueError, OSError, KeyError):
            continue
        tot_post_crit += sum(
            1 for v in rows if isinstance(v.get("severity"), (int, float))
            and v["severity"] >= CRITICAL)
    if tot_post_crit:
        lo, hi = proportion_confint(len(post), tot_post_crit, method="wilson")
        lo_c, hi_c = proportion_confint(len(post), tot_post_crit, method="beta")
        print(f"\n  untested share of post-mechanism criticals: {len(post)} of "
              f"{tot_post_crit} = {100 * len(post) / tot_post_crit:.2f}%")
        print(f"  Wilson 95%          : [{lo * 100:.2f}%, {hi * 100:.2f}%]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c * 100:.2f}%, {hi_c * 100:.2f}%]  (statsmodels/beta)")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, len(post), tot_post_crit - len(post) + 1)
        shi = sbeta.ppf(0.975, len(post) + 1, tot_post_crit - len(post))
        print(f"  Clopper-Pearson 95% : [{slo * 100:.2f}%, {shi * 100:.2f}%]  "
              f"(scipy, cross-check; agrees to {abs(slo - lo_c):.1e})")

    done = {("exp47_divergence_locationkey_live_20260728T230026Z", "C0053")}
    print(f"\n  ALREADY WRITTEN: {len(done)} "
          f"(bench/tests/test_falsifier_C0053_recidivism_2026-09-10.py)")
    print(f"  REMAINING       : {len(post) - len(done)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
