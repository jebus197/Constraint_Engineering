"""Falsifier-mechanism metric harness (Exp 42 fix campaign, Phase 0, 2026-06-06).

Given a directory of saved round outputs from a runner experiment, compute a
per-model, multi-dimensional quality metric that encodes the project's core
objectives. Every fix and ablation in the campaign is scored against this; a fix
is admissible only if it holds the metric for EVERY model (no compromises).

Dimensions, per model (all in [0,1] or None when undefined):
  M1 format_compliance  — parsed findings / FINDING_ID markers (did the output
                          parse into the structured schema?).
  M2 testable_falsifier — of CRITICAL findings (severity >= 0.7), the fraction
                          carrying a runnable falsifier the runner can ADJUDICATE
                          (reverify -> CONFIRMED/REFUTED), not prose/broken/missing.
                          THE PROJECT CORE — prose falsifiers score 0 here.
  M3 ffafp_structure    — findings exposing the FIND/FOLLOW/ANALYSE/FIX structure
                          (admissibility proxy).
  M4 rk_present         — findings carrying a numerical R_k self-assessment.
  M5 alternatives       — findings supplying an alternative (Structure A/B or a
                          documented null-alternative) — the §18 requirement.
  M6 participation      — produced usable, parsable, non-empty output (bool).
Plus pipeline_loss: the model produced output but the runner-VISIBLE text was
empty (e.g. the CC2 claude_cli text-extraction bug) — a delivery defect, not a
model failure. The harness scores the model's ACTUAL output so a delivery bug is
visible as pipeline_loss rather than silently zeroing the model.

Pure measurement: no model dispatch. reverify_falsifier runs each falsifier in
its local sandbox (no network). Reads only; never edits the runner.

Usage:  python3 bench/eval/falsifier_metric.py <logs_dir> [--json out.json]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from bench.runner_core import parse_findings  # noqa: E402
from bench.falsifier_verify import reverify_falsifier  # noqa: E402

CRITICAL_SEVERITY = 0.7


def _read_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _best_text(logs_dir, model, round_tag="r0", round_word="round0"):
    """Return (model_actual_text, runner_visible_text).

    runner_visible = what the runner saved as the model's response (may be empty
    if a delivery bug dropped it). model_actual = the model's real output,
    recovered from the decomposed result's response field or its longest
    assistant turn — so a delivery bug shows as pipeline_loss, not model failure.
    """
    runner_visible = ""
    for f in sorted(glob.glob(str(Path(logs_dir) / f"{round_tag}_{model}_*.json"))):
        # save_output stores the runner-visible response under "response".
        d = _read_json(f)
        runner_visible = d.get("response", "") or d.get("text", "") or ""
        break
    model_actual = runner_visible
    for f in sorted(glob.glob(str(Path(logs_dir) / f"{round_word}_{model}_*.json"))):
        d = _read_json(f)
        resp = d.get("response", "") or d.get("text", "") or ""
        turns = d.get("turns", []) or []
        assistant = [t.get("content", "") or "" for t in turns
                     if t.get("role") == "assistant"]
        longest = max(assistant, key=len) if assistant else ""
        model_actual = max([resp, longest, runner_visible], key=len)
        break
    return model_actual, runner_visible


def _split_findings(text):
    """Per-finding chunks, split on FINDING_ID markers (bold-stripped)."""
    clean = text.replace("**", "")
    parts = re.split(r'(?=FINDING_ID\s*[:\-])', clean)
    return [p for p in parts if re.search(r'FINDING_ID\s*[:\-]', p)]


def score_model(logs_dir, model):
    model_text, runner_text = _best_text(logs_dir, model)
    produced = bool(model_text and model_text.strip())
    pipeline_loss = produced and not (runner_text and runner_text.strip())

    findings = parse_findings(model, 0, model_text) if produced else []
    chunks = _split_findings(model_text)
    criticals = [f for f in findings if (getattr(f, "severity", 0) or 0) >= CRITICAL_SEVERITY]

    # M2 — testable falsifier rate over CRITICAL findings (the core metric).
    testable = 0
    for f in criticals:
        code = (getattr(f, "falsifier_code", "") or "").strip()
        if code and reverify_falsifier(code) in ("CONFIRMED", "REFUTED"):
            testable += 1
    m2 = (testable / len(criticals)) if criticals else None

    # M1 — did the structured output parse?
    if chunks:
        m1 = min(1.0, len(findings) / len(chunks))
    else:
        m1 = 1.0 if findings else (0.0 if produced else None)

    def frac(pred):
        return (sum(1 for c in chunks if pred(c)) / len(chunks)) if chunks else None

    m3 = frac(lambda c: all(k in c.upper() for k in ("FIND", "FOLLOW", "ANALYSE", "FIX")))
    m4 = frac(lambda c: bool(re.search(r'R[_ ]?K\b', c, re.I) and re.search(r'\d', c)))
    m5 = frac(lambda c: bool(re.search(r'alternativ|structure a|structure b|null[- ]?alt', c, re.I)))

    return {
        "model": model, "produced": produced, "pipeline_loss": pipeline_loss,
        "findings": len(findings), "finding_markers": len(chunks),
        "criticals": len(criticals), "testable_criticals": testable,
        "M1_format": m1, "M2_testable_falsifier": m2, "M3_ffafp": m3,
        "M4_rk": m4, "M5_alternatives": m5, "M6_participation": produced,
        "model_chars": len(model_text), "runner_chars": len(runner_text),
    }


def score_dir(logs_dir):
    models = []
    for f in glob.glob(str(Path(logs_dir) / "r0_*_*.json")):
        m = re.match(r'r0_(.+?)_\d', os.path.basename(f))
        if m and m.group(1) not in models:
            models.append(m.group(1))
    return [score_model(logs_dir, m) for m in sorted(models)]


def _fmt(v):
    if isinstance(v, bool):
        return "Y" if v else "."
    if isinstance(v, float):
        return f"{v:.2f}"
    return "—" if v is None else str(v)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: falsifier_metric.py <logs_dir> [--json out.json]")
        return 2
    logs_dir = args[0]
    rows = score_dir(logs_dir)
    print(f"=== falsifier metric: {logs_dir} ===")
    cols = [("model", "model"), ("prod", "produced"), ("ploss", "pipeline_loss"),
            ("find", "findings"), ("crit", "criticals"), ("M1", "M1_format"),
            ("M2*", "M2_testable_falsifier"), ("M3", "M3_ffafp"), ("M4", "M4_rk"),
            ("M5", "M5_alternatives"), ("M6", "M6_participation"),
            ("mchar", "model_chars"), ("rchar", "runner_chars")]
    print("  ".join(f"{h:>7}" for h, _ in cols))
    for r in rows:
        print("  ".join(f"{_fmt(r[k])[:7]:>7}" for _, k in cols))
    m2s = [r["M2_testable_falsifier"] for r in rows if r["M2_testable_falsifier"] is not None]
    print()
    print(f"models={len(rows)}  produced={sum(r['produced'] for r in rows)}  "
          f"pipeline_loss={sum(r['pipeline_loss'] for r in rows)}  "
          + (f"mean M2 testable-falsifier={sum(m2s)/len(m2s):.2f}  (THE CORE)"
             if m2s else "mean M2=— (no criticals parsed)"))
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(rows, open(out, "w"), indent=2)
        print(f"saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
