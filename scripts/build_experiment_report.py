#!/usr/bin/env python3
"""The build experiment's results, with the statistics done rather than eyeballed.

The founder's note on 2026-08-22: CC1 had claimed a cy cadence it was not keeping
and had invoked no `sy` analysis at all. Most of tonight's claims were counting
rather than mathematics, where a symbolic tool would be theatre. The acceptance
statistics are the one place it genuinely applies, so they are computed here with
exact tests and confidence intervals instead of a bare percentage.

THE PRE-REGISTERED TELL, fixed before the first dispatch and honoured here:
    acceptance near 100%  -> the checks are not binding; distrust the run
    acceptance near 0%    -> the models cannot do the task
    a mix                 -> the healthy result
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
LOGS = REPO / "bench/logs/build_experiment_2026-08-22"

HARNESS_DEFECTS = {
    # Outcomes now known to have been produced by CC1's own defects rather than by
    # the model. Excluded from any statement about model ability, and NAMED so the
    # exclusion is auditable rather than a quiet filter.
    "REJECTED_SUITE_WENT_RED": "step 3 assumed a green suite (fixed ec95acb)",
    "REJECTED_PATCH_DID_NOT_APPLY": "contaminated parent + read_file prefix "
                                    "(fixed 386c8d4, 36ab4e3)",
    "CONFIG_ERROR_TOOLCALL_BLOCK": "no-tools route sent a use-your-tools prompt "
                                   "(fixed 902bcde)",
}


def from_cy_log() -> list:
    """Rebuild the full record from the APPEND-ONLY cy log.

    results.json is written per invocation and every resume CLOBBERS it, so after
    three pauses it holds only the last slice. The cy log is append-only and
    therefore the authoritative record -- which is the whole reason a run log is
    append-only. Reconstructing from it rather than from the file that was
    overwritten is the same discipline this project applies to its archives.
    """
    import re
    log = (LOGS / "CY_LIVE.log").read_text(encoding="utf-8", errors="replace")
    line = re.compile(r"^\d{4}-\d\d-\d\dT[\d:]{8}\s+\[(T\d+)\]\s+(.*)$", re.M)
    tasks: dict = {}
    for m in line.finditer(log):
        tid, rest = m.group(1), m.group(2)
        t = tasks.setdefault(tid, {"task": tid, "title": "", "attempts": [],
                                   "outcome": "NOT_ATTEMPTED"})
        mm = re.match(r"(\S+) -> ([A-Z_]+)", rest)
        if mm:
            t["attempts"].append({"model": mm.group(1), "outcome": mm.group(2)})
            continue
        if "*** ACCEPTED from" in rest:
            who = re.search(r"ACCEPTED from (\S+)", rest)
            t["outcome"] = "ACCEPTED"
            t["accepted_by"] = who.group(1) if who else "?"
            continue
        if rest.startswith("HIL:"):
            t["outcome"] = "HIL — rejected at every rung"
            continue
        if "TOOL-CALL BLOCK" in rest:
            who = rest.split()[0]
            t["attempts"].append({"model": who, "outcome": "CONFIG_ERROR_TOOLCALL_BLOCK"})
    try:
        from build_experiment_tasks import TASKS as _T
        titles = {t["id"]: t["title"] for t in _T}
    except Exception:                                    # noqa: BLE001
        titles = {}
    for tid, t in tasks.items():
        t["title"] = titles.get(tid, "")
    return [tasks[k] for k in sorted(tasks)]


def main() -> int:
    sys.path.insert(0, str(REPO / "bench"))
    results = from_cy_log()
    if not results:
        print("  nothing in the cy log yet"); return 1
    idx_f = LOGS / "RESPONSE_MODEL_INDEX.json"
    idx = json.loads(idx_f.read_text()) if idx_f.is_file() else {}

    print("=" * 78)
    print("PER TASK")
    print("=" * 78)
    print(f"  {'task':<6}{'outcome':<26}{'by':<8}{'rungs':>6}  title")
    for r in results:
        who = r.get("accepted_by", "")
        print(f"  {r['task']:<6}{r['outcome'][:25]:<26}{who:<8}"
              f"{len(r.get('attempts', [])):>6}  {r['title'][:44]}")

    patch = [r for r in results if r["outcome"] != "REPORT_RECORDED"]
    acc = [r for r in patch if r["outcome"] == "ACCEPTED"]
    n, k = len(patch), len(acc)
    print()
    print("=" * 78)
    print("ACCEPTANCE")
    print("=" * 78)
    print(f"  {k} of {n} patch tasks accepted")
    if n:
        try:
            from scipy import stats
            lo, hi = stats.binomtest(k, n).proportion_ci(confidence_level=0.95,
                                                         method="exact")
            print(f"  point estimate {k/n*100:.1f}%, exact 95% CI "
                  f"[{lo*100:.1f}%, {hi*100:.1f}%]  (Clopper-Pearson, n={n})")
            p_all = stats.binomtest(k, n, 0.99, alternative="less").pvalue
            p_none = stats.binomtest(k, n, 0.01, alternative="greater").pvalue
            print(f"  vs the 'checks are not binding' pole (p=0.99): p = {p_all:.4f}")
            print(f"  vs the 'models cannot do it'   pole (p=0.01): p = {p_none:.4f}")
            print(f"  the interval is WIDE because n = {n}. That is the honest reading;")
            print(f"  a percentage quoted without it would overstate what {n} tasks can show.")
        except ImportError:
            print(f"  {k/n*100:.1f}% (scipy unavailable for an interval)")

    print()
    print("=" * 78)
    print("EVERY ATTEMPT, AND WHICH REJECTIONS WERE CC1's FAULT")
    print("=" * 78)
    out = collections.Counter()
    harness = collections.Counter()
    per_model = collections.defaultdict(lambda: collections.Counter())
    for r in results:
        for a in r.get("attempts", []):
            o = a.get("outcome", "?")
            out[o] += 1
            per_model[a.get("model", "?")][o] += 1
            if o in HARNESS_DEFECTS:
                harness[o] += 1
    for o, c in out.most_common():
        tag = "  <- HARNESS DEFECT: " + HARNESS_DEFECTS[o] if o in HARNESS_DEFECTS else ""
        print(f"  {o:<40}{c:>4}{tag}")
    tot = sum(out.values())
    print(f"\n  {sum(harness.values())} of {tot} attempts were decided by a defect in "
          f"CC1's harness,")
    print(f"  not by the model's work. Any per-model comparison drawn from this run")
    print(f"  would be an artefact of that and IS NOT MADE HERE.")

    print()
    print("  attempts by model (recorded, NOT ranked, for the reason above):")
    for m, c in sorted(per_model.items(), key=lambda kv: -sum(kv[1].values())):
        a = c.get("ACCEPTED", 0)
        h = sum(v for o, v in c.items() if o in HARNESS_DEFECTS)
        print(f"    {m:<8}{sum(c.values()):>3} attempts, {a} accepted, "
              f"{h} decided by a harness defect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
