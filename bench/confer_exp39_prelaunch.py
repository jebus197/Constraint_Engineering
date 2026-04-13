#!/usr/bin/env python3
"""
Confer: Exp 39 Pre-Launch 5-Panel Review
=========================================
Dispatches to ALL 5 models: CC2, Codex, Gemini, ChatGPT, DeepSeek.
Full CDSFL + Meta SRP + FFAFP protocol.

GO/NO-GO verdict required from each reviewer.

Date: 13 April 2026
Protocol: CDSFL + Meta Structured Reasoning Protocol + FFAFP
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    call_gemini,
    call_openrouter,
    call_deepseek,
    call_codex,
)

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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp39_prelaunch"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Model identifiers
GEMINI_MODEL = "gemini-3.1-pro-preview"
CODEX_MODEL = "codex-5.6"
CHATGPT_MODEL = "openai/gpt-5.4"
DEEPSEEK_MODEL = "deepseek-reasoner"
CC2_MODEL = "cc2-opus-4.6"


def _log(msg: str) -> None:
    print(msg, flush=True)


def get_diff_context() -> str:
    """Get the git diff for recent changes."""
    result = subprocess.run(
        ["git", "diff", "0f7c553..HEAD", "--", "bench/", "docs/GLOSSARY.md"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    return result.stdout[:40000]  # cap at 40K chars


def get_key_excerpts() -> str:
    """Extract key code sections for review context."""
    excerpts = []

    # launch_exp39.py (small, include fully)
    launch = (REPO_ROOT / "bench" / "launch_exp39.py").read_text()
    excerpts.append(f"=== bench/launch_exp39.py (full, {len(launch.splitlines())} lines) ===\n{launch}")

    # 39_0_gate.json config
    config = (REPO_ROOT / "bench" / "exp39_configs" / "39_0_gate.json").read_text()
    excerpts.append(f"=== bench/exp39_configs/39_0_gate.json ===\n{config}")

    # schema.toml (HARD constraints section)
    schema = (REPO_ROOT / "bench" / "cdsfl_registry" / "schema.toml").read_text()
    excerpts.append(f"=== bench/cdsfl_registry/schema.toml (full) ===\n{schema}")

    # universal.toml
    universal = (REPO_ROOT / "bench" / "cdsfl_registry" / "universal.toml").read_text()
    excerpts.append(f"=== bench/cdsfl_registry/universal.toml ===\n{universal}")

    # registry.py HARD_CONSTRAINTS
    registry = (REPO_ROOT / "bench" / "cdsfl_registry" / "registry.py").read_text()
    excerpts.append(f"=== bench/cdsfl_registry/registry.py (full) ===\n{registry}")

    # New domain TOMLs
    for name in ["biology.toml", "information_science.toml", "cs_software.toml"]:
        p = REPO_ROOT / "bench" / "cdsfl_registry" / "domains" / name
        if p.exists():
            excerpts.append(f"=== bench/cdsfl_registry/domains/{name} ===\n{p.read_text()}")

    for name in ["biology.toml", "information_science.toml", "cs_software.toml"]:
        p = REPO_ROOT / "bench" / "cdsfl_registry" / "domains" / "immune" / name
        if p.exists():
            excerpts.append(f"=== bench/cdsfl_registry/domains/immune/{name} ===\n{p.read_text()}")

    return "\n\n".join(excerpts)


REVIEW_PROMPT = """## Exp 39 Pre-Launch Review — GO/NO-GO Assessment

You are one of 5 independent reviewers. Your verdict must be GO or NO-GO.
If NO-GO, specify exact blockers with file:line references.

### Context

Experiment 39 is a 13-sub-experiment sequence testing the CDSFL methodology
across 8 domains (software, physics, mathematics, chemistry, biology,
engineering, statistics, information science). The first sub-experiment
(39-0) is an infrastructure gate test: 8 rounds, 1h wall clock, star
topology, burst_mode OFF, targeting the bench code itself.

Recent changes (this session, 13 April 2026):
1. HIL review gate: --hil-review flag pauses after each round/phase for
   operator review (exit code 42, resume with --resume)
2. Domain plumbing: `domain` field added to DynamicManagementConfig,
   propagated cfg.domain → dm_config.domain → InsectBrain → immune pipeline
3. Enum serialization: _enum_safe_default() replaces default=str
4. Round report detail: per-finding summaries with provenance in round_data
5. Macrophage shadow parity: per-round JSON logs (matches Ouroboros)
6. RegulatoryResult: structured dataclass for regulatory_t_v2 output
7. CT specialist prompt wiring: loads template from domain TOML config
8. 6 new domain TOMLs (3 Layer 2 PE-validated, 3 immune specialist)
9. PE schema: constraints.ffafp_required + constraints.structured_reasoning_required (HARD)
10. PE schema: protocol.reasoning_protocol enum (UX selector for prompting style)
11. Composer Layer 2 renamed to FFAFP (5-step), Layer 3 to Extended Falsification
12. GLOSSARY updated: FFAFP supersedes FFF/FFAF

793/793 tests pass. Branch: exp39-experimental. Commit: 83dd7ab.

### Review Protocol (MANDATORY)

Apply ALL of the following:

**Meta Structured Reasoning Protocol:**
State premises explicitly. Trace execution through concrete examples.
Derive formal conclusions. Do not assert without derivation.

**FFAFP (Find-Follow-Analyse-Fix-P-pass):**
For EVERY finding:
1. FIND: State the issue, exact location, evidence
2. FOLLOW: Trace consequences — dependencies, interfaces, downstream effects
3. ANALYSE: CONFIRMED, UNCERTAIN, or REJECTED
4. FIX: For CONFIRMED only, simplest sufficient correction
5. P-PASS: Try to disprove your own finding

**Extended Falsification:**
After all findings, global P-pass for cross-finding contradictions.

### Review Focus Areas

A. **HIL gate correctness** — Does exit code 42 propagate correctly through
   launch_exp39.py? Is checkpoint state intact after pause? Can --resume
   restore cleanly?

B. **Domain plumbing chain** — Does cfg.domain reach immune pipeline cells?
   What happens with unknown domains? Fallback behaviour?

C. **PE HARD constraint enforcement** — Are ffafp_required and
   structured_reasoning_required enforced at runtime? Can a lower layer
   override them to False? Is the monotonicity property maintained?

D. **Sequencer dependency resolution** — Topological sort correctness?
   Cycle detection? Gate failure propagation?

E. **Burst mode + convergence** — Phase transitions, convergence gate,
   strong depletion advisory override

F. **Crash paths** — Timeout handling, model API failures, disk errors,
   checkpoint corruption, empty model responses

G. **Data integrity** — Finding provenance fields, enum serialization,
   JSON round-trip fidelity, checkpoint save/load

### Verdict

End with exactly one of:
- **VERDICT: GO** — no blockers found, 39-0 is safe to launch
- **VERDICT: NO-GO** — list specific blockers that must be fixed first

{diff_context}

{key_excerpts}
"""


def dispatch_cc2(system_prompt: str, user_prompt: str) -> str:
    """CC2 via claude CLI piped mode."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "claude-sonnet-4-20250514"],
            input=full_prompt,
            capture_output=True, text=True, timeout=600,
            cwd=str(REPO_ROOT),
        )
        return result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "(CC2 timed out after 600s)"
    except FileNotFoundError:
        return "(claude CLI not found)"


def dispatch_codex(system_prompt: str, user_prompt: str) -> str:
    """Codex via codex exec."""
    return call_codex(user_prompt, system_prompt, timeout=600)


def dispatch_gemini(system_prompt: str, user_prompt: str) -> str:
    """Gemini 3.1 Pro via Google API."""
    return call_gemini(GEMINI_MODEL, system_prompt, user_prompt, timeout=300)


def dispatch_chatgpt(system_prompt: str, user_prompt: str) -> str:
    """ChatGPT 5.4 via OpenRouter."""
    return call_openrouter(CHATGPT_MODEL, system_prompt, user_prompt, timeout=300)


def dispatch_deepseek(system_prompt: str, user_prompt: str) -> str:
    """DeepSeek Reasoner via DeepSeek API."""
    return call_deepseek(DEEPSEEK_MODEL, system_prompt, user_prompt, timeout=600)


MODEL_DISPATCHERS = {
    "cc2": ("CC2 (Opus 4.6)", dispatch_cc2),
    "codex": ("Codex 5.6", dispatch_codex),
    "gemini": ("Gemini 3.1 Pro", dispatch_gemini),
    "chatgpt": ("ChatGPT 5.4", dispatch_chatgpt),
    "deepseek": ("DeepSeek Reasoner", dispatch_deepseek),
}


def run_single_review(model_key: str, system_prompt: str, user_prompt: str, ts: str) -> dict:
    """Run a single model review and save logs."""
    name, dispatcher = MODEL_DISPATCHERS[model_key]
    _log(f"  [{ts}] Dispatching to {name}...")
    t0 = time.monotonic()
    try:
        response = dispatcher(system_prompt, user_prompt)
    except Exception as e:
        response = f"(Error: {e})"
    elapsed = time.monotonic() - t0
    _log(f"  [{model_key}] responded in {elapsed:.1f}s ({len(response)} chars)")

    log_entry = {
        "model": name,
        "model_key": model_key,
        "timestamp": ts,
        "elapsed_s": round(elapsed, 1),
        "response_chars": len(response),
        "response": response,
    }

    # Save individual logs
    (LOGS_DIR / f"prelaunch_{model_key}_{ts}.json").write_text(
        json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (LOGS_DIR / f"prelaunch_{model_key}_{ts}.txt").write_text(
        response, encoding="utf-8"
    )

    return log_entry


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    _log(f"Exp 39 Pre-Launch 5-Panel Review — {ts}")
    _log(f"Protocol: CDSFL + Meta SRP + FFAFP")
    _log(f"Models: CC2, Codex, Gemini, ChatGPT, DeepSeek\n")

    # Prepare context
    _log("Preparing review context...")
    diff_context = get_diff_context()
    key_excerpts = get_key_excerpts()

    prompt = REVIEW_PROMPT.format(
        diff_context=f"### Git Diff (recent changes)\n```\n{diff_context}\n```",
        key_excerpts=f"### Key Source Files\n\n{key_excerpts}",
    )

    system_prompt = (
        f"You are an independent code reviewer under the CDSFL methodology.\n\n"
        f"--- CDSFL DIRECTIVES ---\n{CDSFL_TEXT}\n--- END DIRECTIVES ---\n\n"
        f"Apply the full CDSFL + Meta Structured Reasoning Protocol + FFAFP. "
        f"Be precise. Be adversarial. Your verdict determines whether a large "
        f"multi-day experiment proceeds."
    )

    _log(f"Prompt: {len(prompt)} chars | System: {len(system_prompt)} chars\n")

    # Dispatch to all 5 models in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(run_single_review, key, system_prompt, prompt, ts): key
            for key in MODEL_DISPATCHERS
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                _log(f"  [{key}] FAILED: {e}")
                results[key] = {"model_key": key, "error": str(e)}

    # Summary
    _log(f"\n{'='*72}")
    _log(f"  5-PANEL REVIEW COMPLETE")
    _log(f"{'='*72}\n")

    verdicts = {}
    for key in ["cc2", "codex", "gemini", "chatgpt", "deepseek"]:
        r = results.get(key, {})
        resp = r.get("response", "")
        elapsed = r.get("elapsed_s", 0)
        chars = r.get("response_chars", 0)

        # Extract verdict
        if "VERDICT: GO" in resp.upper():
            verdict = "GO"
        elif "VERDICT: NO-GO" in resp.upper() or "NO_GO" in resp.upper():
            verdict = "NO-GO"
        else:
            verdict = "UNCLEAR"
        verdicts[key] = verdict

        name = MODEL_DISPATCHERS[key][0] if key in MODEL_DISPATCHERS else key
        _log(f"  {name}: {verdict} ({elapsed:.0f}s, {chars} chars)")

    # Save consolidated report
    report = {
        "timestamp": ts,
        "protocol": "CDSFL + Meta SRP + FFAFP",
        "models": list(MODEL_DISPATCHERS.keys()),
        "verdicts": verdicts,
        "all_go": all(v == "GO" for v in verdicts.values()),
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "response"}
                    for k, v in results.items()},
    }
    (LOGS_DIR / f"prelaunch_summary_{ts}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _log(f"\nLogs: {LOGS_DIR}/")

    if report["all_go"]:
        _log(f"\n*** ALL 5 MODELS: GO — Exp 39 cleared for launch ***")
        sys.exit(0)
    else:
        no_go = [k for k, v in verdicts.items() if v != "GO"]
        _log(f"\n*** {len(no_go)} model(s) did NOT give GO: {no_go} ***")
        _log(f"Review individual responses before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
