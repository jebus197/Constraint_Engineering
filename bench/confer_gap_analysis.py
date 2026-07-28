#!/usr/bin/env python3
"""
Confer: Spec-vs-Implementation Gap Analysis & Domain-Agnostic Redesign
======================================================================
Dispatches to Gemini 3.1 Pro AND Codex 5.3 under full CDSFL + FFAFP.

Evaluates:
  Q1 — Code-correctness bias: how to make FFAFP gates domain-agnostic
  Q2 — Missing domain configs: what Exp 39 sub-experiments need
  Q3 — Spec-vs-implementation priority ordering for Exp 39
  Q4 — O1 external research integration scope
  Q5 — §7 cognitive measurement: what's needed now vs Phase 9

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

# ---------------------------------------------------------------------------
# Repo setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_gemini

# Load .env
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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_gap_analysis"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"

# ---------------------------------------------------------------------------
# Load CDSFL directives as system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Confer prompt (shared between Gemini and Codex)
# ---------------------------------------------------------------------------

CONFER_PROMPT = """## Task

Under CDSFL and FFAFP (Find, Follow, Analyse, Fix, P-pass), evaluate the
following five questions regarding CDSFL Exp 39 readiness.

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance per question.

## Context

CDSFL Exp 39, 12 April 2026. All 9 implementation phases (0-8) are
complete. 784 tests pass. Branch: exp39-experimental.

An audit has revealed a systematic bias: the entire FFAFP enforcement
architecture, O1 ouroboros cell, and recent documentation have been framed
exclusively around CODE CORRECTNESS — test exit codes, AST diff sizes,
tool log presence. But CDSFL is a DOMAIN-AGNOSTIC falsification methodology
intended to work across mathematics, statistics, physics, biology, chemistry,
engineering, and information science.

The specific gaps identified:

1. FFAFP PE gates (proposed 3-gate architecture) assume code artifacts:
   - Gate 1 checks "test exit code == 0" — meaningless for a mathematical proof
   - Gate 2 checks "diff size" — meaningless for a statistical hypothesis
   - Gate 3 evaluates "code modifications" — inapplicable to physics claims

2. O1 ouroboros cell has ZERO external research capability. It monitors
   internal pipeline metrics only. The external research pipeline (arXiv,
   Semantic Scholar, Sci-Hub, web search) exists in run_round_robin.py but
   is isolated from the immune pipeline entirely.

3. Missing domain configurations blocking Exp 39:
   - biology.toml + immune/biology.toml (Exp 39-G blocked)
   - information_science.toml + immune/information_science.toml (Exp 39-H blocked)
   - immune/engineering.toml (Exp 39-M blocked)
   - cs_software.toml + immune/cs_software.toml (Exp 39-F degraded)

4. Mathematical appendix §7 (Cognitive Measurement Framework) is almost
   entirely unimplemented: Abstraction Index, Total Cognitive Yield, Online
   Value Estimator, Sycophancy Detection, Adoption Delta, churn detection.

5. Specialist B-Cell dispatch (Phase B4) is shadow-only and routes to only
   3 tools (SymPy, z3, statsmodels). No domain-specific verification logic
   for non-code domains.

6. Convergence gate reconciliation actions from Exp 36 audit (ascending
   abstraction guard, contested finding formalization, churn as C6) — none
   executed.

7. Corroboration Branch 2 (Ising/Boltzmann), class-specific diversity
   d_ik, seeded defect injection, break-even re-injection — all specified
   in appendix but not implemented.

---

## QUESTION 1 — Domain-Agnostic FFAFP Gate Redesign

The current 3-gate architecture assumes code artifacts. Redesign it to be
domain-agnostic.

For each gate, define what the abstract contract is (domain-independent)
and what the domain-specific implementation looks like for at least 4
domains: software, mathematics, statistics, physics.

Example starting point:
- Gate 1 (Mechanical): "Domain-appropriate mechanical verification succeeded"
  - Software: test exit code == 0
  - Mathematics: SymPy/z3 returns True for claimed identity
  - Statistics: p-value below significance threshold, effect size computed
  - Physics: dimensional analysis consistent, conservation laws satisfied

What should the gate interface look like so domains can plug in their own
verification logic via configuration?

---

## QUESTION 2 — Missing Domain Configurations

For each missing domain (biology, information science, engineering,
cs_software), define:
a) What claim types exist in that domain?
b) What mechanical verification is possible?
c) What tools can ground findings?
d) What should the TOML config contain?
e) What are the domain-specific FFAFP constraints?

---

## QUESTION 3 — Priority Ordering for Exp 39

Given the 7 gap categories above, which are:
a) BLOCKING (Exp 39 cannot run without them)?
b) LOAD-BEARING (Exp 39 can run but results will be unreliable)?
c) ENHANCEMENT (improves quality but not required for valid results)?
d) PHASE 9 (research write-up, not needed for experiment execution)?

Propose a concrete execution order with dependencies.

---

## QUESTION 4 — O1 External Research Integration

The external research pipeline in run_round_robin.py includes:
- SymPy computation
- arXiv search
- Semantic Scholar search
- Sci-Hub full-text fetch
- Web search + page reading
- External model delegation

a) Should this be integrated with O1, with B-Cell specialist dispatch,
   or with a new cell type entirely?
b) What are the risks of giving a pipeline observer (O1) the ability to
   query external sources? (Confirmation bias, latency, API costs, etc.)
c) For Exp 39 specifically, which sub-experiments benefit most from
   external research integration?
d) What would a MINIMAL viable integration look like?

---

## QUESTION 5 — §7 Cognitive Measurement: Now vs Phase 9

The mathematical appendix §7 specifies:
- §7.1a: Churn detection (rho-bar-3 rolling window)
- §7.2: Abstraction Index H(x)
- §7.3: Total Cognitive Yield Y(t)
- §7.4: Online Total Value Estimator V-hat(t,T)
- §7.5: Sycophancy Detection (O_A, S_sync)
- §7.6: Adoption Delta
- §7.7-7.8: Multi-verifier severity fusion

Which of these are needed for Exp 39 to produce valid results, and which
are research analysis tools that can wait for Phase 9?

Specifically: can Exp 39 run with the current convergence gate (gamma +
rho thresholds) or does the gate need the §7 enhancements first?

---

Respond with rigorous FFAFP analysis for ALL FIVE questions. Be concrete
and specific. Propose data structures and interfaces where appropriate.
End with a definitive stance per question.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def dispatch_gemini(ts):
    """Dispatch to Gemini 3.1 Pro."""
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
        return {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "error": str(e),
            "time_s": round(elapsed, 1),
        }


def dispatch_codex(ts):
    """Dispatch to Codex 5.3 via CLI."""
    print("Dispatching to Codex 5.3...")
    prompt = f"{CDSFL_TEXT}\n\n---\n\n{CONFER_PROMPT}"
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["codex", "exec", prompt],
            capture_output=True, text=True, timeout=300,
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
        return {
            "model": "codex-5.3",
            "timestamp": ts,
            "error": "Timeout after 300s",
            "time_s": round(elapsed, 1),
        }
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"  Codex FAILED after {elapsed:.1f}s: {e}")
        return {
            "model": "codex-5.3",
            "timestamp": ts,
            "error": str(e),
            "time_s": round(elapsed, 1),
        }


def save_result(result, prefix, ts):
    """Save JSON and plaintext for a single model result."""
    model_tag = result["model"].replace(".", "").replace("-", "")

    out_json = LOGS_DIR / f"{prefix}_{model_tag}_{ts}.json"
    out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  JSON saved: {out_json.name}")

    if "response" in result:
        out_txt = LOGS_DIR / f"{prefix}_{model_tag}_{ts}.txt"
        header = (
            f"CONFER: Gap Analysis & Domain-Agnostic Redesign\n"
            f"Timestamp: {ts}\n"
            f"Model: {result['model']}\n"
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
    print(f"  CONFER: Gap Analysis & Domain-Agnostic Redesign")
    print(f"  Timestamp: {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Models: Gemini 3.1 Pro + Codex 5.3")
    print(f"{'='*72}\n")

    # Dispatch sequentially (Gemini first, Codex second)
    ge_result = dispatch_gemini(ts)
    save_result(ge_result, "gap", ts)

    cx_result = dispatch_codex(ts)
    save_result(cx_result, "gap", ts)

    # Print results
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
