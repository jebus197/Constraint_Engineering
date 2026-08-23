#!/usr/bin/env python3
"""Compose T01 (the panel's converged answer) plus T02-T10, in BOTH disputed orders.

CC2 says T02 -> T03 -> T04 -> T05. Fable says T02 -> T03 -> T05 -> T04, on the
grounds that rebasing T04's 5 hunks onto T05's 14 is the smaller job. The panel was
required to converge on Q1 only, so this disagreement stands -- and it is settled by
running both, not by preferring a reviewer.

T01 uses Fable's patch: the converged answer is its site (the FIX-2 sub-critical arm
at :3362) and its one-hunk widening, and the gate ACCEPTED it on 2026-08-23 after the
fence defect was repaired.
"""
from __future__ import annotations
import json, pathlib, shutil, subprocess, sys, tempfile, uuid

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from bench import build_acceptance as BA  # noqa: E402

L = REPO / "bench/logs/build_experiment_2026-08-22"
IDX = json.loads((L / "RESPONSE_MODEL_INDEX.json").read_text())
# task -> the response file whose patch the gate ACCEPTED
ACCEPTED = {
    "T01": "T01_rung3_response.md",   # fable, the panel's converged site
    "T02": "T02_rung2_response.md", "T03": "T03_rung2_response.md",
    # rebased over T03's inserted ledger line, 2026-08-23
    "T04": "T04_REBASED_response.md",
    "T05": "T05_rung2_response.md",
    "T06": "T06_rung2_response.md", "T07": "T07_rung1_response.md",
    "T08": "T08_rung1_response.md", "T09": "T09_rung2_response.md",
    "T10": "T10_rung1_response.md",
}
# BOTH ORDERS WERE RUN 2026-08-23 AND GAVE THE IDENTICAL RESULT: 9 of 10 applied,
# T04 conflicting either way, zero new suite failures. So the CC2/Fable disagreement
# about ordering was moot -- T04's conflict is with T03's inserted ledger line, not
# with T05. Fable was right that T05's earlier conflict was manufactured by the old
# composer; CC2 was right that T04's is real. With T04 rebased, one order suffices.
ORDERS = {
    "T02->T03->T04(rebased)->T05": ["T01","T02","T03","T04","T05","T06","T07","T08","T09","T10"],
}


def _run(cmd, cwd, timeout=1800):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def try_order(name, order, parent):
    wt = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_compose_")) / f"wt_{uuid.uuid4().hex[:8]}"
    res = {"order": name, "applied": [], "conflicts": [], "tests": []}
    try:
        rc, out = _run(["git", "worktree", "add", "--detach", str(wt), parent], REPO)
        if rc != 0:
            res["error"] = out[-200:]; return res
        for tid in order:
            f = L / ACCEPTED[tid]
            if not f.is_file():
                res["conflicts"].append({"task": tid, "why": "response file missing"}); continue
            resp = f.read_text(errors="replace")
            patches = BA.parse_patch(resp)
            tpath, tsrc = BA.parse_test(resp)
            snap, ok, why = {}, True, ""
            for rel, search, replace in patches:
                tgt = wt / rel
                if not tgt.is_file():
                    ok, why = False, f"target absent: {rel}"; break
                text = tgt.read_text(encoding="utf-8", errors="replace")
                n = text.count(search)
                if n != 1:
                    ok, why = False, (f"{rel}: SEARCH matches {n}x "
                                      f"{'(gone once earlier patches land)' if n==0 else '(ambiguous)'}")
                    break
                snap.setdefault(rel, text)
                tgt.write_text(text.replace(search, replace, 1), encoding="utf-8")
            if not ok:
                for rel, orig in snap.items():           # ROLLBACK, defect 5
                    (wt / rel).write_text(orig, encoding="utf-8")
                res["conflicts"].append({"task": tid, "model": IDX.get(f.name,"?"), "why": why})
                print(f"    {tid}  CONFLICT — {why}")
                continue
            if tpath:
                tf = wt / tpath; tf.parent.mkdir(parents=True, exist_ok=True)
                tf.write_text(tsrc, encoding="utf-8"); res["tests"].append(tpath)
            res["applied"].append(tid)
            print(f"    {tid}  applied ({IDX.get(f.name,'?')})")
        if res["tests"]:
            _, o = _run(["python3","-m","pytest",*res["tests"],"-q","--netguard-strict"], wt, 900)
            res["accepted_tests"] = BA._summarise_pytest(o)
            print(f"    all accepted tests together: {res['accepted_tests']}")
        _, o = _run(["python3","-m","pytest","bench/tests/","-q","--netguard-strict",
                     "-p","no:randomly"], wt, 2400)
        res["suite"] = BA._summarise_pytest(o)
        base = BA.suite_baseline(parent, ["python3","-m","pytest","bench/tests/","-q",
                                          "--netguard-strict","-p","no:randomly"], 2400)
        res["new_failures"] = sorted(BA.failing_nodeids(o) - base)
        print(f"    full suite: {res['suite']}")
        print(f"    failures the parent does NOT have: {len(res['new_failures'])}")
        for nf in res["new_failures"]: print(f"      {nf}")
    finally:
        subprocess.run(["git","worktree","remove","--force",str(wt)], cwd=str(REPO),
                       capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
    return res


def main():
    parent = subprocess.run(["git","rev-parse","HEAD"], cwd=str(REPO),
                            capture_output=True, text=True).stdout.strip()
    print(f"  parent {parent[:8]}\n")
    out = []
    for name, order in ORDERS.items():
        print(f"  === {name} ===")
        out.append(try_order(name, order, parent))
        print()
    (L / "composition_both_orders.json").write_text(json.dumps(out, indent=1))
    print("  written: bench/logs/build_experiment_2026-08-22/composition_both_orders.json")
    for r in out:
        clean = not r.get("new_failures") and not r.get("conflicts")
        print(f"  {r['order']:<28}applied {len(r['applied'])}/10  "
              f"conflicts {len(r.get('conflicts',[]))}  CLEAN={clean}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
