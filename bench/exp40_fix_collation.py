#!/usr/bin/env python3
"""Exp 40 fix collation (plan item E).

Collates every CLOSED finding's verified fix from the consolidated Exp 40
registry, classifies each as an artefact fix (to bench/dm/_feedback.py), a
runner/methodology fix, or stale/uncategorised, and builds a cumulative
gate-checked cleaned baseline of the artefact.

The cleaned baseline is written to bench/exp40_baseline/_feedback_cleaned.py
(a dedicated artefact dir — the repo bench/dm/_feedback.py is left pristine
for provenance and reproducibility, per the approved remediation plan).

Output: bench/exp40_baseline/collation_report.json + console summary.
Cumulative-gate rule (P-pass risk mitigation): a CLOSED patch is accepted
into the baseline only if (a) its SEARCH block still matches the current
cumulative source and (b) the post-apply source passes AST + py_compile.
Any patch failing either is excluded and logged with a reason — never forced.
"""
from __future__ import annotations

import ast
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.reference_runner_v3 import (  # noqa: E402
    parse_search_replace_blocks,
    apply_fix_blocks,
)

REPORT = REPO / "bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json"
PRISTINE = REPO / "bench/dm/_feedback.py"
OUT_DIR = REPO / "bench/exp40_baseline"
CLEANED = OUT_DIR / "_feedback_cleaned.py"
REPORT_OUT = OUT_DIR / "collation_report.json"

RUNNER_BASENAMES = {
    "reference_runner_v3.py", "runner_core.py", "immune_agents.py",
    "insect_brain.py", "decomposed_dispatch.py", "merge_arbitration.py",
    "evidence.py", "endocrine.py", "experiment_11_orchestrator.py",
    "composer.py", "_sk_format.py",
}


_SB_HOLDER: dict = {}


def _get_sandbox() -> Path:
    """One persistent sandbox repo copy reused for per-patch test gating
    (copytree-per-patch would be far too slow for 40 candidates)."""
    if "sb" not in _SB_HOLDER:
        td = tempfile.mkdtemp(prefix="exp40collate_")
        sb = Path(td) / "sb"
        shutil.copytree(
            REPO, sb, symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs"),
        )
        _SB_HOLDER["sb"] = sb
        _SB_HOLDER["td"] = td
    return _SB_HOLDER["sb"]


def gate_full(source: str) -> tuple[bool, str]:
    """Cumulative gate: AST + py_compile (fast reject) then the canonical
    feedback-channel test suite against the candidate source. A CLOSED
    patch is admitted to the baseline ONLY if the file still passes the
    full invariant suite afterwards — stricter than the run-time S_k
    threshold, which tolerated partial-regression scores (e.g. C0001)."""
    try:
        ast.parse(source)
    except (SyntaxError, ValueError) as e:
        return False, f"ast:{e}"
    sb = _get_sandbox()
    (sb / "bench/dm/_feedback.py").write_text(source, encoding="utf-8")
    try:
        py_compile.compile(str(sb / "bench/dm/_feedback.py"), doraise=True)
    except py_compile.PyCompileError as e:
        return False, f"compile:{e}"
    tr = subprocess.run(
        ["python3", "-m", "pytest",
         "bench/tests/test_feedback_channel.py", "-q", "--tb=no"],
        capture_output=True, text=True, cwd=str(sb),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=120,
    )
    if tr.returncode != 0:
        m = (tr.stdout + tr.stderr).strip().splitlines()
        tail = next((ln for ln in reversed(m) if "failed" in ln), m[-1] if m else "")
        return False, f"feedback_tests_fail:{tail[:120]}"
    return True, "ast+compile+feedback_tests ok"


def final_gate(cleaned_path: Path) -> dict:
    """Full gate on the final cleaned baseline: ruff + py_compile + the
    configured feedback-channel test suite against a sandbox overlay."""
    res: dict = {}
    rf = subprocess.run(
        ["python3", "-m", "ruff", "check", str(cleaned_path)],
        capture_output=True, text=True,
    )
    res["ruff"] = {"rc": rf.returncode,
                   "tail": (rf.stdout + rf.stderr).strip()[-600:]}
    try:
        py_compile.compile(str(cleaned_path), doraise=True)
        res["py_compile"] = {"ok": True}
    except py_compile.PyCompileError as e:
        res["py_compile"] = {"ok": False, "err": str(e)[:400]}
    # sandbox overlay: cleaned -> dm/_feedback.py, run feedback-channel tests
    with tempfile.TemporaryDirectory() as td:
        sb = Path(td) / "sb"
        shutil.copytree(
            REPO, sb, symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs"),
        )
        (sb / "bench/dm/_feedback.py").write_text(
            cleaned_path.read_text(encoding="utf-8"), encoding="utf-8")
        tr = subprocess.run(
            ["python3", "-m", "pytest",
             "bench/tests/test_feedback_channel.py", "-q", "--tb=line"],
            capture_output=True, text=True, cwd=str(sb),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=300,
        )
        res["feedback_tests"] = {
            "rc": tr.returncode,
            "tail": (tr.stdout + tr.stderr).strip()[-800:]}
    return res


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    entries = report["registry"]["entries"]
    vals = list(entries.values()) if isinstance(entries, dict) else entries
    closed = [v for v in vals if v.get("status") == "CLOSED"]

    artefact, runner, stale = [], [], []
    for f in closed:
        pf = f.get("proposed_fix") or ""
        cid = f.get("canonical_id")
        rnd = f.get("last_status_change_round", 0)
        blocks = parse_search_replace_blocks(pf) if pf else []
        if not blocks:
            stale.append({"id": cid, "reason": "no parseable fix block",
                          "round": rnd})
            continue
        bns = {Path(b.file_path).name for b in blocks}
        rec = {"id": cid, "round": rnd, "severity": f.get("severity"),
               "blocks": blocks, "targets": sorted(bns),
               "desc": (f.get("description") or "")[:160]}
        if bns == {"_feedback.py"}:
            artefact.append(rec)
        elif bns & RUNNER_BASENAMES:
            runner.append(rec)
        else:
            stale.append({"id": cid, "round": rnd,
                          "reason": f"non-target basenames {sorted(bns)}"})

    # Build cumulative gate-checked cleaned baseline (artefact fixes only)
    src = PRISTINE.read_text(encoding="utf-8")
    artefact.sort(key=lambda r: (r["round"], r["id"]))
    accepted, skipped = [], []
    for rec in artefact:
        mod, n, err = apply_fix_blocks(src, rec["blocks"], "bench/dm/_feedback.py")
        if mod is None:
            skipped.append({"id": rec["id"], "round": rec["round"],
                            "reason": err or "apply_failed"})
            continue
        ok, detail = gate_full(mod)
        if not ok:
            skipped.append({"id": rec["id"], "round": rec["round"],
                            "reason": f"cumulative_gate_fail:{detail}"})
            continue
        src = mod
        accepted.append({"id": rec["id"], "round": rec["round"],
                         "blocks_applied": n, "severity": rec["severity"]})

    CLEANED.write_text(src, encoding="utf-8")
    fg = final_gate(CLEANED)

    out = {
        "generated": subprocess.run(["date", "-Iseconds"],
                                    capture_output=True, text=True).stdout.strip(),
        "report_source": str(REPORT.relative_to(REPO)),
        "closed_total": len(closed),
        "classification": {
            "artefact_feedback_py": len(artefact),
            "runner_methodology": len(runner),
            "stale_uncategorised": len(stale),
        },
        "baseline": {
            "path": str(CLEANED.relative_to(REPO)),
            "pristine_lines": len(PRISTINE.read_text().splitlines()),
            "cleaned_lines": len(src.splitlines()),
            "patches_accepted": len(accepted),
            "patches_skipped": len(skipped),
            "accepted": accepted,
            "skipped": skipped,
        },
        "runner_fixes": [
            {"id": r["id"], "round": r["round"], "targets": r["targets"],
             "desc": r["desc"]} for r in runner],
        "stale": stale,
        "final_gate": fg,
    }
    REPORT_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"CLOSED findings: {len(closed)}")
    print(f"  artefact (_feedback.py): {len(artefact)}")
    print(f"  runner/methodology     : {len(runner)}")
    print(f"  stale/uncategorised    : {len(stale)}")
    print(f"baseline: {len(accepted)} accepted / {len(skipped)} skipped "
          f"(pristine {len(PRISTINE.read_text().splitlines())} -> "
          f"cleaned {len(src.splitlines())} lines)")
    print(f"final gate: ruff rc={fg['ruff']['rc']} "
          f"py_compile={fg['py_compile'].get('ok')} "
          f"feedback_tests rc={fg['feedback_tests']['rc']}")
    print(f"runner fixes to review for fold-in: {len(runner)}")
    for r in runner:
        print(f"  {r['id']} r{r['round']} -> {r['targets']}: {r['desc'][:90]}")
    print(f"report: {REPORT_OUT.relative_to(REPO)}")
    if "td" in _SB_HOLDER:
        shutil.rmtree(_SB_HOLDER["td"], ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
