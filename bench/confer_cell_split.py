#!/usr/bin/env python3
"""
Confer: Macrophage / Ouroboros Cell Type Split & Self-Improving Architecture
============================================================================
Dispatches to Gemini 3.1 Pro AND Codex 5.3 under full CDSFL + FFAFP.

Evaluates:
  Q1 — Is the Macrophage / Ouroboros split architecturally sound?
  Q2 — Macrophage as active cell: external research + anomaly hunting
  Q3 — Ouroboros (O1) as advisory monitor: self-referential, no external access
  Q4 — Self-healing / self-improving cycle design
  Q5 — Exp 39 scope: which cell types, shadow vs active

Date: 12 April 2026
Protocol: CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_gemini

_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        if "=" in _line:
            _k, _, _v = _line.partition("=")
            _k = _k.strip()
            _v = _v.strip().strip("'\"")
            os.environ.setdefault(_k, _v)

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_cell_split"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

CONFER_PROMPT = """## Task

Under CDSFL and FFAFP (Find, Follow, Analyse, Fix, P-pass), evaluate the
following five questions regarding a proposed cell type architecture change.

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance per question.

## Context

CDSFL Exp 39, 12 April 2026. The project has an immune pipeline with
biological cell type analogues (Dendritic Cell, Cytotoxic T, B-Cell, NK,
Helper T, Regulatory T). A recent implementation added an "ouroboros cell"
(O1) with two modes: macrophage (anomaly hunting) and microglia
(self-referential health). Both run in shadow mode.

Three Gemini confer rounds have established:
1. O1 needs sensitivity dial, circuit breaker, and semantic clustering.
2. O1 must NOT have external API access (confirmation bias, latency,
   architectural violation — monitor must not become actor).
3. External research should go to a specialist B-Cell or new cell type.

The founder now proposes a SPLIT:

**Macrophage Cell** (ACTIVE pipeline cell):
- Keeps the "Macrophage" biological analogue name.
- Actively hunts pipeline anomalies (existing macrophage detection logic).
- Gathers external research (arXiv, Semantic Scholar, structured fetches).
- Can gather data from other CDSFL-linked systems/network nodes.
- Its findings enter the pipeline as new claims, subject to PE gates.
- Part of the pipeline proper — participates, not just observes.
- In biology: macrophages engulf, process, and present to other cells.

**Ouroboros Cell (O1)** (ADVISORY-ONLY monitor):
- The self-referential observer (snake eating its own tail).
- Watches the ENTIRE pipeline, including the Macrophage.
- Advisory only — NEVER modifies pipeline state.
- Has sensitivity dial (1-11), circuit breaker, semantic clustering.
- NO external API access (confirmed by prior confer).
- Detects systemic pathologies that individual cells cannot see.
- In biology: closest to the hypothalamus or the vagus nerve — system-
  level monitoring that doesn't participate in the immune response.

The current `ouroboros_cell.py` would be REFACTORED:
- Macrophage mode → new `macrophage_cell.py` (active cell)
- Microglia mode + O1 monitoring → stays in `ouroboros_cell.py` (advisory)

The self-healing/self-improving cycle:
1. Pipeline processes findings.
2. Macrophage hunts anomalies + gathers external research to
   validate/challenge findings.
3. Macrophage's findings enter pipeline as new claims (through PE gates).
4. O1 watches ALL of this and flags systemic issues to HIL.
5. HIL acts on O1's advisories to improve the pipeline itself.

For Exp 39 scope (agreed earlier):
- Load-bearing: Mathematics, CS/Software, Statistics cells
- Secondary: Biology, Information Science cells
- Shadow only: Physics, Chemistry, Engineering cells
- Macrophage: shadow initially, limited to structured academic fetch
- O1: shadow, advisory only

---

## QUESTION 1 — Is the Macrophage / Ouroboros Split Sound?

a) Does splitting the current ouroboros_cell.py (2 modes in 1 cell) into
   two separate cell types (Macrophage + O1) produce a cleaner
   architecture?

b) Is the separation of concerns correct: Macrophage DOES things
   (hunts, gathers, presents), O1 WATCHES things (monitors, advises)?

c) Are there failure modes in the split? E.g., if the Macrophage
   produces bad findings from external sources, does O1 detect this?
   If O1 flags a systemic issue with the Macrophage, who acts on it?

d) Does the split create any redundancy or gaps compared to the current
   single-cell design?

---

## QUESTION 2 — Macrophage as Active Pipeline Cell

The Macrophage would be a new cell type in the immune pipeline,
distinct from existing B-Cells and NK cells.

a) What is the Macrophage's relationship to existing cell types?
   - Does it replace any existing cell, or is it additive?
   - How does it interact with B-Cell (verification), NK (cross-reference),
     and Cytotoxic T (fix)?
   - Does it participate in Stage 2 dispatch, or does it run at a
     different pipeline stage?

b) External research integration: the Macrophage gathers research from
   arXiv, Semantic Scholar, and potentially CDSFL network nodes. Its
   findings become pipeline claims. How should these external-origin
   claims be marked and handled differently from model-generated claims?

c) What does the Macrophage's TOML configuration look like?

d) For Exp 39 shadow mode: what does the Macrophage observe and log
   without affecting verdicts?

---

## QUESTION 3 — Ouroboros (O1) as Advisory Monitor

O1 is the self-referential observer. It watches the pipeline but never
participates. It has the sensitivity dial, circuit breaker, and
clustering architecture designed in prior confers.

a) If O1 watches the Macrophage and detects that the Macrophage is
   introducing bad external research, what is the escalation path?
   O1 is advisory only — it can flag but not block. Is this sufficient?

b) O1's current detection capabilities (verdict clustering, severity
   concentration, timing spikes, tool monoculture, persistent anomalies,
   tool-claim mismatch) were designed for code-centric pipeline
   monitoring. Which of these translate to domain-agnostic monitoring
   and which need redesign?

c) Should O1 monitor the PE gates themselves? (i.e., meta-monitoring:
   are the gates functioning correctly, or are they systematically
   passing/failing in suspicious patterns?)

d) The microglia mode (self-referential health checks) stays in O1.
   Should it also monitor the Macrophage specifically, or just the
   pipeline as a whole?

---

## QUESTION 4 — Self-Healing / Self-Improving Cycle

The founder's vision: the system should develop capacity to be both
self-healing (detecting and correcting its own pathologies) and
self-improving (using external research and network data to enhance
its own capabilities).

a) Define the self-healing cycle precisely. What constitutes a
   "pathology" in CDSFL terms? How is it detected (by O1?), and
   how is it corrected (by Macrophage? by HIL?)?

b) Define the self-improving cycle. How does external research gathered
   by the Macrophage improve the pipeline? Give a concrete example.

c) What prevents the self-improving cycle from becoming self-corrupting?
   (E.g., Macrophage imports a flawed paper, pipeline accepts its
   conclusions, Macrophage gathers more papers confirming the flaw.)

d) Is HIL involvement required at every cycle, or can some self-healing
   happen autonomously? Where is the boundary?

---

## QUESTION 5 — Exp 39 Scope: Cell Types and Practicality

Given the agreed Exp 39 scope:
- Load-bearing: Mathematics, CS/Software, Statistics
- Secondary: Biology, Information Science
- Shadow: Physics, Chemistry, Engineering
- Macrophage: shadow, structured academic fetch only
- O1: shadow, advisory only

a) Is the refactor (split ouroboros_cell.py into macrophage_cell.py +
   ouroboros_cell.py) worth doing BEFORE Exp 39, or should Exp 39
   run with the current combined cell and refactor afterwards?

b) What is the minimum viable Macrophage for Exp 39 shadow mode?
   (Just anomaly detection? Anomaly detection + fetch_paper? Full
   external research pipeline?)

c) Does introducing two new cell types (even in shadow) risk
   overcomplicating Exp 39's already complex 13-sub-experiment design?

d) What would convince you (as reviewer) that the split is practical
   and can work within the Exp 39 timeline?

---

Respond with rigorous FFAFP analysis for ALL FIVE questions. Be concrete
and specific. End with a definitive stance per question.
"""


def dispatch_gemini(ts):
    print("Dispatching to Gemini 3.1 Pro...")
    t0 = time.monotonic()
    try:
        response = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=CDSFL_TEXT,
            user_prompt=CONFER_PROMPT,
            max_tokens=32768,
            timeout=300,
            max_retries=5,
            backoff_base=3.0,
        )
        elapsed = time.monotonic() - t0
        print(f"  Gemini responded in {elapsed:.1f}s ({len(response)} chars)")
        return {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response),
        }
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  Gemini FAILED after {elapsed:.1f}s: {e}")
        return {"model": GEMINI_MODEL, "timestamp": ts, "error": str(e),
                "time_s": round(elapsed, 1)}


def dispatch_codex(ts):
    print("Dispatching to Codex 5.3 (600s timeout)...")
    prompt = f"{CDSFL_TEXT}\n\n---\n\n{CONFER_PROMPT}"
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", prompt],
            capture_output=True, text=True, timeout=600,
            cwd=str(REPO_ROOT),
        )
        elapsed = time.monotonic() - t0
        response = result.stdout.strip()
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if not response and stderr:
                raise RuntimeError(f"Codex exit {result.returncode}: {stderr[:500]}")
        print(f"  Codex responded in {elapsed:.1f}s ({len(response)} chars)")
        return {
            "model": "codex-5.3",
            "timestamp": ts,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response),
        }
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - t0
        print(f"  Codex TIMED OUT after {elapsed:.1f}s")
        return {"model": "codex-5.3", "timestamp": ts,
                "error": "Timeout after 600s", "time_s": round(elapsed, 1)}
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  Codex FAILED after {elapsed:.1f}s: {e}")
        return {"model": "codex-5.3", "timestamp": ts, "error": str(e),
                "time_s": round(elapsed, 1)}


def save_result(result, prefix, ts):
    model_tag = result["model"].replace(".", "").replace("-", "")
    out_json = LOGS_DIR / f"{prefix}_{model_tag}_{ts}.json"
    out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  JSON saved: {out_json.name}")
    if "response" in result:
        out_txt = LOGS_DIR / f"{prefix}_{model_tag}_{ts}.txt"
        header = (
            f"CONFER: Macrophage / Ouroboros Cell Split\n"
            f"Timestamp: {ts}\nModel: {result['model']}\n"
            f"Protocol: CDSFL + FFAFP\n"
            f"Response time: {result['time_s']}s\n"
            f"Response length: {result.get('chars', 0)} chars\n"
            f"{'='*72}\n\n"
        )
        out_txt.write_text(header + result["response"] + "\n", encoding="utf-8")
        print(f"  Text saved: {out_txt.name}")


def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"\n{'='*72}")
    print(f"  CONFER: Macrophage / Ouroboros Cell Split")
    print(f"  Timestamp: {ts}")
    print(f"  Models: Gemini 3.1 Pro + Codex 5.3 (600s)")
    print(f"{'='*72}\n")

    ge_result = dispatch_gemini(ts)
    save_result(ge_result, "split", ts)
    cx_result = dispatch_codex(ts)
    save_result(cx_result, "split", ts)

    for label, result in [("GEMINI", ge_result), ("CODEX", cx_result)]:
        print(f"\n{'='*72}")
        if "error" in result:
            print(f"  {label}: ERROR -- {result['error']}")
        else:
            print(f"  {label} ({result['model']}) -- {result['time_s']}s")
            print(f"{'='*72}\n")
            print(result["response"])
        print(f"{'='*72}")

    return ge_result, cx_result


if __name__ == "__main__":
    run_confer()
