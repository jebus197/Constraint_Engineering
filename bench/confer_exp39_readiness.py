#!/usr/bin/env python3
"""
Confer: Exp 39 Readiness Assessment
====================================
Dispatches to Gemini 3.1 Pro AND Codex 5.3 under full CDSFL + FFAFP.

Evaluates:
  Q1 — Which pre-39-0 items are truly BLOCKING vs deferrable?
  Q2 — Parsing/serialization: are cell I/O formats sound for system + HIL?
  Q3 — Domain TOML strategy: minimal viable for 39-0 or full set needed?
  Q4 — ImmuneResponse checkpointing: priority and approach?
  Q5 — What is the minimum viable path to running 39-0?

Date: 13 April 2026
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp39_readiness"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

CONFER_PROMPT = """## Task

Under CDSFL and FFAFP (Find, Follow, Analyse, Fix, P-pass), evaluate the
following five questions regarding Exp 39 readiness. This is a pre-run
assessment — we want to know the minimum viable path to running the first
sub-experiment (39-0, the infrastructure gate test).

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance per question.

## Current State

Branch: exp39-experimental. 793 tests passing. Last commit: f57d6ce.

Completed:
- All 9 implementation phases (0-8) for Exp 39
- Macrophage/Ouroboros cell type split (implemented, tested)
- Provenance schema (6 fields on Finding, captured in FindingRegistry)
- origin_type="model" set on all 5 Finding() instantiation sites
- 4 Gemini + Codex confer rounds (O1+FFAFP, PE 3-gate, gap analysis, cell split)
- Shadow cell wiring into reference_runner.py main loop
- Mathematical appendix expanded (7 new sections)

The agreed execution order (pre-39-0) has 10 items:
1. Domain-agnostic gate interface (IFalsificationGate protocol + GateResult)
2. Convergence gate: add churn detection (§7.1a) as C6
3. Missing domain configs (biology, info science, engineering immune, cs_software)
4. B-Cell dispatch: route to domain-specific tools from new TOML configs
5. Severity fusion (§7.7) for gate output synthesis
6. Sycophancy detection (§7.5) — can shadow alongside 39-0
7. O1 calibration: sensitivity dial, circuit breaker, semantic clustering
8. Run 39-0 (infrastructure gate), then 39-A
9. MC command sync across all reference locations
10. Phase 9 (research write-up) — deferred post-Exp 39

Exp 39-0 is the INFRASTRUCTURE GATE test — it tests the pipeline
infrastructure itself (reference_runner.py, immune_agents.py, runner_core.py)
using CS/Software domain experts. Target: the bench code.

## Known Issues

A. ImmuneResponse from immune_agents.py is not checkpointed — if the runner
   crashes mid-experiment, all immune reasoning is lost. The runner does
   checkpoint findings and round data to JSON, but the ImmuneResponse object
   (containing T-cell triage, B-cell verdicts, NK severity, CT inspection,
   Dendritic routing, Regulatory gate decisions) is transient.

B. Shadow cell logs go into round_data["shadow_cells"] but are not in the
   checkpoint. If the runner resumes from checkpoint, shadow cells restart
   from scratch (no history of prior observations).

C. FindingRegistry entries now include provenance fields, but the
   round report summary is counts-only — it doesn't expose individual
   finding details or provenance to the HIL.

D. The falsification gate in runner_core.py checks for FALSIFICATION
   sections in model responses but does not produce structured gate
   results (pass/fail with evidence). It just marks findings as
   unverified if the section is missing.

E. Convergence detection uses gamma + rho but has only a basic rho_churn
   flag — no proper churn metric (C6) to distinguish refinement from
   oscillation.

---

## QUESTION 1 — What is truly BLOCKING for 39-0?

Of the 10-item execution order, which items MUST be complete before 39-0
can produce meaningful results? Which can run in parallel or be deferred?

Consider: 39-0 is an infrastructure test using CS/Software domain experts.
It targets the bench code itself. The gate interface redesign was motivated
by domain-agnosticism — but 39-0 IS a software domain test.

## QUESTION 2 — Are cell I/O formats sound for system + HIL?

The immune pipeline has 8 cell types. Each produces output that must be:
(a) machine-parsable for downstream cells, (b) serializable to JSON for
round reports, and (c) human-readable for the HIL reviewer.

Known cell types:
- T-Cell (triage): assigns priority tiers
- B-Cell (verification): produces verdicts (CONFIRM/CHALLENGE/EXTEND)
- NK-Cell (severity): numeric severity scores
- CT-Cell (code inspection): structural analysis results
- Dendritic-Cell (routing): determines which cells review which findings
- Regulatory-Cell (convergence gate): pass/fail with convergence metrics
- Macrophage (shadow, internal monitor): observations with categories
- Ouroboros (shadow, external research): candidate claims with provenance

Are there format mismatches, type pollution, or HIL-unreadable outputs?

## QUESTION 3 — Domain TOML strategy for 39-0

39-0 targets CS/Software domain. Existing domain TOMLs:
- bench/cdsfl_registry/domains/statistics.toml
- bench/cdsfl_registry/domains/immune/statistics.toml
- bench/cdsfl_registry/universal.toml (HARD constraints)

Missing (identified in gap analysis): biology, information_science,
immune/engineering, cs_software.

Does 39-0 need a cs_software.toml to run, or can it use the existing
universal.toml + the default domain config in the runner?

## QUESTION 4 — ImmuneResponse checkpointing

The ImmuneResponse object is transient. For 39-0 (which may run 15-24
rounds over several hours), is this acceptable? Options:
a) Accept the risk — 39-0 is short enough
b) Serialize ImmuneResponse to checkpoint JSON
c) Defer to after 39-0 (learn from the run what needs checkpointing)

## QUESTION 5 — Minimum viable path to 39-0

Given everything above, what is the shortest path to running 39-0 that
doesn't compromise the experiment's scientific validity? List the
mandatory items in order, estimate effort for each, and identify what
can be safely deferred to post-39-0.

---

For each question, provide:
1. Your classification (HARD/SOFT constraint)
2. P-pass analysis (at least one falsification attempt per claim)
3. Definitive recommendation
"""


def call_codex(prompt: str, timeout: int = 600) -> str:
    """Call Codex 5.3 via CLI exec mode."""
    try:
        result = subprocess.run(
            ["codex", "exec", prompt],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        return result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"(Codex timed out after {timeout}s)"
    except FileNotFoundError:
        return "(codex CLI not found)"


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    system_prompt = (
        f"You are reviewing under the CDSFL methodology.\n\n"
        f"--- CDSFL DIRECTIVES ---\n{CDSFL_TEXT}\n--- END DIRECTIVES ---\n\n"
        f"Apply the full protocol. Be precise. Be adversarial where needed."
    )

    full_prompt = f"{system_prompt}\n\n{CONFER_PROMPT}"

    # ── Gemini ───────────────────────────────────────────────────────
    print(f"[{ts}] Dispatching to Gemini 3.1 Pro...", flush=True)
    t0 = time.monotonic()
    try:
        gemini_resp = call_gemini(GEMINI_MODEL, system_prompt, CONFER_PROMPT)
    except Exception as e:
        gemini_resp = f"(Gemini error: {e})"
    gemini_time = time.monotonic() - t0
    print(f"  Gemini responded in {gemini_time:.1f}s ({len(gemini_resp)} chars)")

    gemini_log = {
        "model": GEMINI_MODEL,
        "timestamp": ts,
        "elapsed_s": round(gemini_time, 1),
        "prompt_chars": len(CONFER_PROMPT),
        "response_chars": len(gemini_resp),
        "response": gemini_resp,
    }
    (LOGS_DIR / f"readiness_gemini31propreview_{ts}.json").write_text(
        json.dumps(gemini_log, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (LOGS_DIR / f"readiness_gemini31propreview_{ts}.txt").write_text(
        gemini_resp, encoding="utf-8"
    )

    # ── Codex ────────────────────────────────────────────────────────
    print(f"[{ts}] Dispatching to Codex 5.3...", flush=True)
    t0 = time.monotonic()
    codex_resp = call_codex(f"{CDSFL_TEXT}\n\n---\n\n{CONFER_PROMPT}", timeout=600)
    codex_time = time.monotonic() - t0
    print(f"  Codex responded in {codex_time:.1f}s ({len(codex_resp)} chars)")

    codex_log = {
        "model": "codex-5.3",
        "timestamp": ts,
        "elapsed_s": round(codex_time, 1),
        "prompt_chars": len(CONFER_PROMPT),
        "response_chars": len(codex_resp),
        "response": codex_resp,
    }
    (LOGS_DIR / f"readiness_codex53_{ts}.json").write_text(
        json.dumps(codex_log, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (LOGS_DIR / f"readiness_codex53_{ts}.txt").write_text(
        codex_resp, encoding="utf-8"
    )

    print(f"\nConfer complete. Logs in {LOGS_DIR}/")
    print(f"  Gemini: {gemini_time:.1f}s")
    print(f"  Codex:  {codex_time:.1f}s")


if __name__ == "__main__":
    main()
