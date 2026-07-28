"""Falsifier test matrix (2026-06-06) — does the I1 fix make the mechanism work,
and do the models handle the composer whole vs decomposed?

For each model x {whole, decomposed} x N runs, dispatch the REAL composer target
with the falsifier gate on (the I1 runnable-falsifier override is active in the
decomposed synthesis prompt), and save each response in the metric-harness
format (r0_<cell>_<ts>.json). Score afterwards with:
    python3 bench/eval/falsifier_metric.py <logs_dir>

  whole      = non-decomposed single-shot tooled dispatch (dispatch_to_model,
               enable_tools=True) -> the ~110K payload in one shot. Tests whether
               capable models handle it whole (the 80K-floor question).
  decomposed = decomposed_dispatch(enable_tools=True) -> chunk + synthesis with
               the I1 fix. Tests whether the prose->runnable fix produces testable
               falsifiers (Phase 1) on the path the live run failed on.

Reliable, proven dispatch pattern (mirrors the panel + smoke scripts). Reads the
real directive + target; writes only logs. No core edits.
"""
from __future__ import annotations
import concurrent.futures
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

from experiment_11_orchestrator import ModelConfig  # noqa: E402
from runner_core import dispatch_to_model  # noqa: E402
from decomposed_dispatch import decomposed_dispatch, DecomposedChunk  # noqa: E402

RUNS = int(os.environ.get("MATRIX_RUNS", "3"))
LOGS = REPO_ROOT / "bench" / "logs" / "falsifier_matrix_2026-06-06"
LOGS.mkdir(parents=True, exist_ok=True)

DIRECTIVE = (
    (REPO_ROOT / "bench/directives/universal/cdsfl_core_formal.md").read_text(encoding="utf-8")
    + "\n\n"
    + (REPO_ROOT / "bench/directives/universal/cdsfl_operational.md").read_text(encoding="utf-8")
)
TARGET = (REPO_ROOT / "bench/cdsfl_registry/composer.py").read_text(encoding="utf-8")

# I1 fix UNDER TEST (gate-aware): redefine the operational §2 FALSIFICATION block
# from prose to a RUNNABLE falsifier. An appended override proved too weak (one
# cell, 2026-06-06: cx still wrote prose); redefining the authoritative §2
# definition worked (cx decomposed produced a runnable falsifier importing the
# real module; runner re-run CONFIRMED). Applied in the harness ONLY -- the
# directive file + runner are untouched until the matrix confirms it across all
# models (policy: test before core).
_RUNNABLE_S2 = (
    "FALSIFICATION: This section is mandatory. For every CRITICAL finding it MUST "
    "contain a RUNNABLE falsifier, NOT prose. Write the literal line \"FALSIFIER:\" "
    "on its own line, then a fenced python code block (```python ... ```) that "
    "imports the REAL target module and raises AssertionError or prints the token "
    "FALSIFIED if and only if the claimed defect is genuinely present (exit cleanly "
    "otherwise). Run it with the execute_python tool first. The runner RE-RUNS this "
    "exact python block and ITS result -- not your prose -- decides CONFIRMED or "
    "REFUTED. A prose-only or missing FALSIFIER cannot be confirmed and is sent to "
    "a human."
)
DIRECTIVE, _n_s2 = re.subn(
    r'FALSIFICATION: This section is mandatory\. It must contain:.*?Did you test it\?',
    _RUNNABLE_S2, DIRECTIVE, flags=re.S)
assert _n_s2 == 1, f"§2 prose block not found for gate-aware redefinition (n={_n_s2})"

FINDINGS_REQUEST = (
    "YOUR TASK: review the target module below under full CDSFL + FFAFP "
    "constraints. For EACH finding output, in this exact order: FINDING_ID "
    "(e.g. F001), SEVERITY (0.0-1.0, 1.0=critical), FLAW_CLASS (integer 1-8), "
    "ABSTRACTION_INDEX (0.0-1.0), FIND (the issue, location, evidence), FOLLOW "
    "(downstream consequences), ANALYSE (HARD/SOFT, premises, CONFIRMED/UNCERTAIN/"
    "REJECTED), FIX (SEARCH/REPLACE), and for CRITICAL findings a FALSIFIER. "
    "Compute a numerical R_k per finding."
)

# (label, model_id, api)
MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("cx",       "openai/gpt-5.5",                "openrouter"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]


def _mc(label, model_id, api):
    # Gemini 3.1 Pro is a reasoning model: its chain-of-thought can consume the
    # entire output budget, returning empty visible content. Production
    # ModelConfig gives it 32768 max_tokens + reasoning.effort=high; the matrix
    # must match (8192 with no extra_body starved it -> empty_response). Other
    # models keep the lighter 8192 budget.
    is_gemini = label == "gemini"
    return ModelConfig(
        label=label, model_id=model_id, api=api, role="participant",
        system_prompt_path="bench/directives/universal/cdsfl_core_formal.md",
        max_tokens=32768, timeout=600, max_retries=2,  # match production config (all models)
        extra_body={"reasoning": {"effort": "high"}} if is_gemini else None,
    )


def whole_cell(label, model_id, api):
    """Non-decomposed single-shot tooled dispatch — the full payload in one shot."""
    prompt = f"{FINDINGS_REQUEST}\n\n=== TARGET: composer.py ===\n```python\n{TARGET}\n```"
    text, _elapsed = dispatch_to_model(
        _mc(label, model_id, api), prompt, DIRECTIVE,
        wall_clock_limit=900, enable_tools=True)
    return text or ""


def decomposed_cell(label, model_id, api):
    """Decomposed dispatch with the I1 fix active in the synthesis turn."""
    chunks = [DecomposedChunk(content=TARGET, label="target_0")]
    # Gemini reasoning-budget alignment (see _mc): forward reasoning.effort and a
    # larger synthesis budget so the tooled synthesis turn has visible-content
    # room. Other routes keep the lighter 8192 default and no extra_body.
    is_gemini = label == "gemini"
    res = decomposed_dispatch(
        api=api, model_id=(None if api == "claude_cli" else model_id),
        system_prompt=DIRECTIVE, chunks=chunks,
        final_instruction=FINDINGS_REQUEST,
        max_tokens=32768 if is_gemini else 8192, timeout=600,
        cdsfl_directives=DIRECTIVE, enable_tools=True,
        extra_body=({"reasoning": {"effort": "high"}} if is_gemini else None))
    return (getattr(res, "text", "") or getattr(res, "response", "") or "")


def run_cell(label, model_id, api, path, run):
    cell = f"{label}{path}r{run}"
    t0 = time.time()
    try:
        text = (whole_cell if path == "whole" else decomposed_cell)(label, model_id, api)
        ok = bool(text and text.strip())
    except Exception as e:  # noqa: BLE001
        text, ok = f"[ERROR {type(e).__name__}: {e}]", False
    rec = {"model_label": cell, "path": path, "run": run, "ok": ok,
           "response": text, "response_length": len(text),
           "elapsed_s": round(time.time() - t0, 1)}
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    (LOGS / f"r0_{cell}_{ts}.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"  [{cell}] ok={ok} chars={len(text)} {rec['elapsed_s']}s"
          + ("" if ok else f" :: {text[:90]}"))
    return rec


def main():
    cells = [(lbl, mid, api, path, run)
             for (lbl, mid, api) in MODELS
             for path in ("whole", "decomposed")
             for run in range(1, RUNS + 1)]
    print(f"=== falsifier matrix: {len(MODELS)} models x 2 paths x {RUNS} runs "
          f"= {len(cells)} cells ===")
    print(f"  directive {len(DIRECTIVE):,} chars + target {len(TARGET):,} chars")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(run_cell, *c) for c in cells]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())
    (LOGS / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok = sum(r["ok"] for r in results)
    print(f"\n=== {ok}/{len(results)} cells ok. logs: {LOGS} ===")
    print(f"score with: python3 bench/eval/falsifier_metric.py {LOGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
