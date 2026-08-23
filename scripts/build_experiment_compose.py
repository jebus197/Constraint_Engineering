#!/usr/bin/env python3
"""Apply every ACCEPTED patch in sequence and prove they hold together.

WHY THIS IS A SEPARATE STEP, AND WHY IT IS NOT OPTIONAL
------------------------------------------------------
The build experiment's gate validates each candidate INDEPENDENTLY against the
same parent commit. That is the right unit for judging one model's work, and it
says NOTHING about the set. Two patches can each pass fail-before/pass-after and
still, together, conflict, mask one another, or leave the suite red.

"Each part was verified, therefore the whole is verified" is a composition
fallacy, and it is the shape of several defects this project has already shipped.
So the set is proved separately, here, and a patch that composes badly is reported
rather than quietly dropped.

WHAT IT DOES
------------
    1. Build a worktree at the parent.
    2. Apply the accepted patches in task order, recording any that no longer
       apply once an earlier one has landed.
    3. Run every accepted test TOGETHER.
    4. Run the full suite and compare against the PARENT's own failing set, not
       against an assumption of green -- the same two-sided rule the gate uses,
       for the same reason.

Nothing is written to the repository. The branch is updated only by a human
reading this report and choosing to.

    python3 scripts/build_experiment_compose.py [--apply-to-branch <name>]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import uuid

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from bench import build_acceptance as BA   # noqa: E402

LOGS = REPO / "bench/logs/build_experiment_2026-08-22"


def _run(cmd, cwd, timeout=1800):
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", default="", help="commit to compose onto")
    ap.add_argument("--apply-to-branch", default="",
                    help="if given AND composition is clean, write the result here")
    args = ap.parse_args()

    # results.json is clobbered by every resume; the cy log is append-only and is
    # therefore the authoritative record. Same reasoning the report script uses.
    sys.path.insert(0, str(REPO / "scripts"))
    from build_experiment_report import from_cy_log
    results = from_cy_log()
    idx_f = LOGS / "RESPONSE_MODEL_INDEX.json"
    idx = json.loads(idx_f.read_text()) if idx_f.is_file() else {}
    accepted = [r for r in results if r.get("outcome") == "ACCEPTED"]
    if not accepted:
        print("  no accepted patches to compose"); return 1

    parent = args.parent or subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
        text=True).stdout.strip()
    suite = ["python3", "-m", "pytest", "bench/tests/", "-q", "--netguard-strict",
             "-p", "no:randomly"]
    baseline = BA.suite_baseline(parent, suite, 1800)
    if baseline is None:                      # unmeasured != clean (2026-08-23)
        raise RuntimeError(
            "parent baseline could not be measured; refusing to compose against an "
            "unmeasured baseline, which would render every pre-existing failure as new.")
    print(f"  parent {parent[:8]}; it already fails {len(baseline)} test(s) in a worktree")
    print(f"  composing {len(accepted)} accepted patch(es)\n")

    wt = pathlib.Path(tempfile.mkdtemp(prefix="cdsfl_compose_")) / f"wt_{uuid.uuid4().hex[:8]}"
    report = {"parent": parent, "baseline_failures": sorted(baseline), "applied": [],
              "conflicts": [], "tests": [], "suite": "", "new_failures": []}
    try:
        rc, out = _run(["git", "worktree", "add", "--detach", str(wt), parent], REPO)
        if rc != 0:
            print(f"  worktree add failed: {out[-300:]}"); return 1

        for r in accepted:
            tid = r["task"]
            # The ACCEPTED attempt is the rung named in the record, not merely the
            # last file on disk -- a later rung may exist from an earlier, aborted
            # pass. Resolve it through the model index.
            who = r.get("accepted_by", "")
            src = None
            for cand in sorted(LOGS.glob(f"{tid}_rung*_response.md")):
                if idx.get(cand.name) == who:
                    src = cand
            if src is None:
                for cand in sorted(LOGS.glob(f"{tid}_rung*_response.md")):
                    src = cand
            if src is None:
                report["conflicts"].append({"task": tid, "why": "no response file"})
                continue
            resp = src.read_text(encoding="utf-8")
            patches = BA.parse_patch(resp)
            tpath, tsrc = BA.parse_test(resp)
            # ROLLBACK ON PARTIAL APPLICATION. The first version broke on a failed
            # hunk WITHOUT reverting the hunks already written, so a half-applied
            # patch stayed in the tree and the NEXT patch was matched against it.
            # That manufactured a conflict: the T05 conflict reported on 2026-08-22
            # was against a half-applied T04, not against T02/T03 as the report said.
            # On a clean tree Fable measured T05 matching 14/14. Found by Fable,
            # 2026-08-23. Without this, every conflict downstream of the first is
            # untrustworthy.
            ok, why, snapshot = True, "", {}
            for rel, search, replace in patches:
                f = wt / rel
                if not f.is_file():
                    ok, why = False, f"target absent: {rel}"; break
                text = f.read_text(encoding="utf-8", errors="replace")
                if search not in text:
                    ok, why = False, (f"SEARCH no longer matches {rel} once earlier "
                                      f"patches are applied")
                    break
                snapshot.setdefault(rel, text)          # first state of this file
                f.write_text(text.replace(search, replace, 1), encoding="utf-8")
            if not ok:
                for rel, original in snapshot.items():  # revert THIS patch entirely
                    (wt / rel).write_text(original, encoding="utf-8")
            if not ok:
                report["conflicts"].append({"task": tid, "model": idx.get(src.name, "?"),
                                            "why": why})
                print(f"  {tid}  CONFLICT — {why}")
                continue
            if tpath:
                tf = wt / tpath
                tf.parent.mkdir(parents=True, exist_ok=True)
                tf.write_text(tsrc, encoding="utf-8")
                report["tests"].append(tpath)
            report["applied"].append({"task": tid, "model": idx.get(src.name, "?"),
                                      "files": [p[0] for p in patches], "test": tpath})
            print(f"  {tid}  applied ({idx.get(src.name,'?')})  {[p[0] for p in patches]}")

        if report["tests"]:
            rc_t, out_t = _run(["python3", "-m", "pytest", *report["tests"], "-q",
                                "--netguard-strict"], wt, 900)
            report["accepted_tests_together"] = BA._summarise_pytest(out_t)
            print(f"\n  all accepted tests together: {report['accepted_tests_together']}")

        rc_s, out_s = _run(suite, wt, 1800)
        report["suite"] = BA._summarise_pytest(out_s)
        report["new_failures"] = sorted(BA.failing_nodeids(out_s) - baseline)
        print(f"  full suite with everything applied: {report['suite']}")
        print(f"  failures the parent does NOT have : {len(report['new_failures'])}")
        for f in report["new_failures"]:
            print(f"     {f}")

        clean = not report["new_failures"] and not report["conflicts"]
        report["composes_cleanly"] = clean
        print(f"\n  COMPOSES CLEANLY: {clean}")

        if clean and args.apply_to_branch:
            for a in report["applied"]:
                for rel in a["files"]:
                    shutil.copy2(wt / rel, REPO / rel)
                if a["test"]:
                    dst = REPO / a["test"]
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(wt / a["test"], dst)
            print(f"  written into the working tree for branch {args.apply_to_branch}; "
                  f"NOT committed -- a human commits it")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=str(REPO), capture_output=True)
        shutil.rmtree(wt.parent, ignore_errors=True)
        (LOGS / "composition_report.json").write_text(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
