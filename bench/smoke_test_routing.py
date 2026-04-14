#!/usr/bin/env python3
"""Smoke test: DeepSeek direct API vs OpenRouter + all-model spot check.

Tests the fingerprint-aware decomposition fix by sending a gate-sized
prompt to all 5 models, with DeepSeek tested via both direct API and
OpenRouter for comparison.

Usage:
    python3 bench/smoke_test_routing.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from runner_core import source_env
source_env()

from experiment_11_orchestrator import (
    call_openrouter,
    call_deepseek,
    call_gemini,
    _log,
)

# ── Smoke prompt ─────────────────────────────────────────────────────────
# Simulates a real Exp 39 gate payload: CDSFL instructions + code snippet
# + R_k computation requirement. ~8K chars — well under any threshold.

SMOKE_SYSTEM = (
    "You are a technical reviewer under the CDSFL protocol. "
    "For each finding, you MUST compute residual risk R_k using:\n"
    "  R_k = R_old * (1 - eta*d*p) * S_k + nu_eff\n"
    "Show your numerical estimates for R_old, eta, d, p, S_k, nu_eff "
    "and the resulting R_k value. Qualitative-only assessment will be rejected.\n\n"
    "Output format per finding:\n"
    "  FINDING_ID: F001\n"
    "  SEVERITY: 0.0-1.0\n"
    "  FIND: what is wrong\n"
    "  FIX: simplest sufficient correction\n"
    "  FALSIFICATION: (MANDATORY) state falsifier, attempt, result\n"
    "  CORROBORATION: (MANDATORY) compute R_k numerically\n"
)

SMOKE_CODE = '''
def _should_decompose(model_label: str, mgr, payload_chars: int = 0) -> bool:
    """Check if a model should receive decomposed (smaller) prompts."""
    LENGTH_THRESHOLD = 80_000

    if model_label == "DeepSeek":
        return True  # BUG: always decomposes, ignoring observed capability
    if model_label == "CC2":
        return payload_chars > 200_000
    if payload_chars > LENGTH_THRESHOLD:
        return True
    return model_label in mgr.config.pre_decompose_models


def compute_rho(novel_counts, raw_counts):
    """Compute semantic novelty rate."""
    if not raw_counts or raw_counts[-1] == 0:
        return 0.0
    return novel_counts[-1] / raw_counts[-1]
'''

SMOKE_PROMPT = (
    f"Review this code for bugs. Follow the output format exactly.\n\n"
    f"```python\n{SMOKE_CODE}\n```\n"
)


def run_smoke(label: str, route: str, model_id: str, **kwargs):
    """Run a single smoke test and return results."""
    print(f"\n{'='*60}")
    print(f"  {label} via {route} ({model_id})")
    print(f"{'='*60}")

    t0 = time.monotonic()
    try:
        if route == "deepseek":
            text = call_deepseek(
                model_id=model_id,
                system_prompt=SMOKE_SYSTEM,
                user_prompt=SMOKE_PROMPT,
                max_tokens=kwargs.get("max_tokens", 8192),
                timeout=kwargs.get("timeout", 300),
                max_retries=1,
                backoff_base=0,
            )
        elif route == "openrouter":
            text = call_openrouter(
                model_id=model_id,
                system_prompt=SMOKE_SYSTEM,
                user_prompt=SMOKE_PROMPT,
                max_tokens=kwargs.get("max_tokens", 8192),
                timeout=kwargs.get("timeout", 300),
                max_retries=1,
                backoff_base=0,
                extra_body=kwargs.get("extra_body"),
            )
        elif route == "gemini":
            text = call_gemini(
                model_id=model_id,
                system_prompt=SMOKE_SYSTEM,
                user_prompt=SMOKE_PROMPT,
                max_tokens=kwargs.get("max_tokens", 8192),
                timeout=kwargs.get("timeout", 300),
                max_retries=1,
                backoff_base=0,
            )
        elif route == "claude_cli":
            import subprocess
            combined = f"{SMOKE_SYSTEM}\n\n{SMOKE_PROMPT}"
            result = subprocess.run(
                ["claude", "-p"],
                input=combined,
                capture_output=True,
                text=True,
                timeout=kwargs.get("timeout", 300),
            )
            text = result.stdout.strip()
        else:
            text = f"Unknown route: {route}"
    except Exception as e:
        text = f"__SMOKE_FAILED__: {type(e).__name__}: {e}"

    elapsed = time.monotonic() - t0
    chars = len(text)

    # Check for R_k computation
    has_rk = any(marker in text for marker in [
        "R_k", "R_old", "eta", "nu_eff", "residual risk",
        "η", "ν_eff",
    ])
    has_finding_id = "FINDING_ID" in text or "F001" in text or "F00" in text
    has_falsification = "FALSIF" in text.upper() or "FALSIFIER" in text.upper()

    result = {
        "label": label,
        "route": route,
        "model_id": model_id,
        "elapsed_s": round(elapsed, 1),
        "response_chars": chars,
        "has_rk_computation": has_rk,
        "has_finding_id": has_finding_id,
        "has_falsification": has_falsification,
        "failed": text.startswith("__SMOKE_FAILED__"),
        "preview": text[:500] if not text.startswith("__SMOKE_FAILED__") else text[:200],
    }

    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Response: {chars:,} chars")
    print(f"  R_k computation: {'YES' if has_rk else 'NO'}")
    print(f"  Finding ID: {'YES' if has_finding_id else 'NO'}")
    print(f"  Falsification: {'YES' if has_falsification else 'NO'}")
    if text.startswith("__SMOKE_FAILED__"):
        print(f"  ERROR: {text[:200]}")
    else:
        print(f"  Preview: {text[:300]}...")

    return result


def main():
    print("CDSFL Routing Smoke Test")
    print(f"Prompt size: system={len(SMOKE_SYSTEM)} + user={len(SMOKE_PROMPT)} "
          f"= {len(SMOKE_SYSTEM) + len(SMOKE_PROMPT):,} chars")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    results = []

    # 1. DeepSeek via direct API (current route)
    results.append(run_smoke(
        "DeepSeek-Direct", "deepseek", "deepseek-reasoner",
        max_tokens=8192, timeout=300,
    ))

    # 2. DeepSeek via OpenRouter (user's gut-instinct suggestion)
    results.append(run_smoke(
        "DeepSeek-OpenRouter", "openrouter", "deepseek/deepseek-reasoner",
        max_tokens=8192, timeout=300,
    ))

    # 3-6. Other models via their actual experiment routes
    results.append(run_smoke(
        "ChatGPT", "openrouter", "openai/gpt-5.4",
        max_tokens=8192, timeout=120,
    ))

    results.append(run_smoke(
        "Codex", "openrouter", "openai/gpt-5.4",
        max_tokens=8192, timeout=120,
    ))

    results.append(run_smoke(
        "Gemini", "openrouter", "google/gemini-3.1-pro-preview",
        max_tokens=8192, timeout=120,
        extra_body={"reasoning": {"effort": "high"}},
    ))

    # CC2 via CLI pipe (short prompt, should work)
    results.append(run_smoke(
        "CC2", "claude_cli", "claude",
        timeout=120,
    ))

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<22s} {'Route':<14s} {'Time':>6s} {'Chars':>7s} {'R_k':>4s} {'FID':>4s} {'Fals':>5s}")
    print("-" * 65)
    for r in results:
        rk = "YES" if r["has_rk_computation"] else "NO"
        fid = "YES" if r["has_finding_id"] else "NO"
        fals = "YES" if r["has_falsification"] else "NO"
        t = f"{r['elapsed_s']:.1f}s"
        c = f"{r['response_chars']:,}"
        if r["failed"]:
            c = "FAILED"
        print(f"{r['label']:<22s} {r['route']:<14s} {t:>6s} {c:>7s} {rk:>4s} {fid:>4s} {fals:>5s}")

    # Save results
    out_path = REPO_ROOT / "bench" / "logs" / "smoke_test_routing.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nResults saved: {out_path}")


if __name__ == "__main__":
    main()
