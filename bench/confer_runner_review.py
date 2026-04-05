#!/usr/bin/env python3
"""Runner fitness confer — CX (GPT-5.4 high) + Gemini 3.1 Pro.

Three rounds, one runner each. Both models review independently.
CC monitors individual convergence.

Usage:
    python3 bench/confer_runner_review.py
"""

from __future__ import annotations
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import concurrent.futures

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load env
env_path = REPO_ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_runner_review"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

RUNNERS = [
    ("exp34", "Experiment 34 — Endocrine Layer", "run_exp34_endocrine.py"),
    ("exp35", "Experiment 35 — PolicyEngine", "run_exp35_policy_engine.py"),
    ("exp36", "Experiment 36 — Evidence Layer", "run_exp36_evidence.py"),
]


def build_prompt(runner_name: str, runner_label: str, runner_path: str) -> str:
    cdsfl = (REPO_ROOT / "bench" / "directives" / "universal"
             / "cdsfl_core_formal.md").read_text()
    runner_code = (REPO_ROOT / "bench" / runner_path).read_text()

    return f"""=== CDSFL CORE DIRECTIVES (MANDATORY) ===

{cdsfl}

=== END CDSFL DIRECTIVES ===

REVIEW BRIEF:

You are reviewing ONE experiment runner for fitness before live execution.
This runner implements the star/blackboard topology for multi-model code
review under CDSFL.

Runner: {runner_label}
File: bench/{runner_path} ({len(runner_code):,} chars)

YOUR TASK: Assess whether this runner is fit for purpose.

Check:
1. Is the star/blackboard topology correctly implemented?
2. Does the FindingRegistry correctly manage canonical state?
3. Are programmatic status transitions correct? (CONFIRMED at 2+
   independent models, MERGED on merge verdict)
4. Does the verdict parser correctly extract CONFIRM/CHALLENGE/EXTEND/MERGE?
5. Is the convergence gate sound? (5 compound conditions, earliest R12)
6. Is gamma estimation correct for Duane reliability growth?
7. Is the prompt appropriate for the target code?
8. Are all known past mistakes (listed below) avoided?
9. Will the runner produce results consistent with the mathematical model?
10. Are there any bugs, dead code paths, or logic errors?

You are NOT reviewing the test articles (endocrine.py, engine.py,
evidence.py) for bugs. You may look at them to assess whether the runner
prompts and configurations are appropriate.

KNOWN PAST MISTAKES (check ALL):
1. FFF enforcement — must be prompt-only, no enforcement/rejection.
2. Missing verdict parser — verdicts must be parsed from model output.
3. Gemini JSON format — nested dict {{F001: {{...}}}} must be handled.
4. Merkle float rejection — floats must be stringified for hashing.
5. Model voting — no REJECTED status. OPEN -> CONFIRMED/UNCONFIRMED/MERGED.
6. FFF preset ordering — Find -> Follow -> Fix (not Find -> Fix -> Follow).
7. Anchoring framing confound — neutral prompts only.
8. Status transitions — resolve() must be called (not dead code).
9. has_follow dead metadata — must be removed (always False).
10. Undiscussed prompt inventions — any prompt text not discussed with
    the founder is suspect.

For each finding, provide:
  FINDING_ID: unique identifier
  SEVERITY: 0.0 to 1.0
  DESCRIPTION: FIND — what is wrong, where, evidence
  FOLLOW: trace downstream consequences
  PROPOSED_FIX: the simplest sufficient correction
  VERIFIED: TRUE/FALSE

Apply full CDSFL including P-pass falsification on your own findings.
Retract anything you can disprove.

=== RUNNER CODE: {runner_label} ({len(runner_code):,} chars) ===

{runner_code}

=== END RUNNER CODE ===

Produce your findings now under full CDSFL.
"""


def dispatch_gemini(prompt: str, runner_name: str) -> str:
    """Dispatch to Gemini 3.1 Pro."""
    import google.genai as genai

    api_key = (os.environ.get("GOOGLE_API_KEY")
               or os.environ.get("GEMINI_API_KEY"))
    client = genai.Client(api_key=api_key)

    t0 = time.monotonic()
    print(f"  [Gemini/{runner_name}] Dispatching ({len(prompt):,} chars)...")

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=prompt,
        config={"temperature": 0.1, "max_output_tokens": 16384},
    )
    elapsed = time.monotonic() - t0
    text = response.text or ""
    print(f"  [Gemini/{runner_name}] Done: {len(text):,} chars, {elapsed:.1f}s")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = LOGS_DIR / f"{runner_name}_gemini_{ts}.txt"
    out.write_text(text, encoding="utf-8")
    return text


def dispatch_cx(prompt: str, runner_name: str) -> str:
    """Dispatch to CX (GPT-5.4 high reasoning) via codex CLI."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = LOGS_DIR / f"{runner_name}_cx_{ts}.txt"

    t0 = time.monotonic()
    print(f"  [CX/{runner_name}] Dispatching ({len(prompt):,} chars)...")

    proc = subprocess.run(
        [
            "/opt/homebrew/bin/codex", "exec",
            "--ephemeral",
            "-c", 'model_reasoning_effort="high"',
            "-c", "mcp_servers={}",
            "-c", "plugins={}",
            "-o", str(out_path),
            "-",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=600,
    )
    elapsed = time.monotonic() - t0

    text = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    print(f"  [CX/{runner_name}] Done: {len(text):,} chars, {elapsed:.1f}s")
    if proc.returncode != 0:
        print(f"  [CX/{runner_name}] stderr: {proc.stderr[:200]}")
    return text


def main():
    print("=" * 60)
    print("RUNNER FITNESS CONFER — 3 rounds × 2 models")
    print(f"  CX: GPT-5.4 (reasoning: high)")
    print(f"  Gemini: 3.1 Pro Preview")
    print(f"  CDSFL: Full (latest)")
    print(f"  Logs: {LOGS_DIR}")
    print("=" * 60)

    all_results = {}

    for round_idx, (runner_name, runner_label, runner_path) in enumerate(RUNNERS):
        print(f"\n{'─' * 60}")
        print(f"Round {round_idx + 1}/3: {runner_label}")
        print(f"{'─' * 60}")

        prompt = build_prompt(runner_name, runner_label, runner_path)
        print(f"  Prompt: {len(prompt):,} chars")

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            gf = pool.submit(dispatch_gemini, prompt, runner_name)
            cf = pool.submit(dispatch_cx, prompt, runner_name)

            gemini_text = gf.result()
            cx_text = cf.result()

        all_results[runner_name] = {
            "gemini": gemini_text,
            "cx": cx_text,
        }

        print(f"\n  Round {round_idx + 1} complete.")
        print(f"  Gemini: {len(gemini_text):,} chars")
        print(f"  CX: {len(cx_text):,} chars")

    print(f"\n{'=' * 60}")
    print("ALL ROUNDS COMPLETE")
    print(f"  Logs: {LOGS_DIR}")
    for name, results in all_results.items():
        print(f"  {name}: Gemini={len(results['gemini']):,}c, "
              f"CX={len(results['cx']):,}c")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
