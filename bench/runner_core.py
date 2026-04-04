"""Canonical shared runner infrastructure for CDSFL experiments.

This module is the SINGLE SOURCE OF TRUTH for:
  - Finding parser (JSON, tuple, marker, bare, fallback formats)
  - Model dispatch with multiprocessing watchdog
  - Model specifications and initial fingerprints
  - Finding context formatting with windowing
  - Environment loading
  - Experiment numbering

ALL experiment runners import from here. Fixes applied once propagate
to every experiment. Created 1 April 2026 after Run 5 lost 29 ChatGPT
findings to a parser bug that had been fixed in one script but not
carried forward to new ones.

Usage:
    from runner_core import (
        parse_findings,
        dispatch_to_model,
        format_findings_for_context,
        source_env,
        build_model_specs,
        build_task_prompt,
        next_experiment_number,
        INITIAL_FINGERPRINTS,
        MODEL_SPECS,
        CONVERGENCE_EXCLUDED_MODELS,
    )
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    dispatch,
    _log,
    ExperimentConfig,
    ModelConfig,
)
from dynamic_management import (
    ModelSpec,
    CapabilityFingerprint,
    Finding,
)


# ─────────────────────────────────────────────────────────────────────────────
# Model configuration
# ─────────────────────────────────────────────────────────────────────────────

# Initial fingerprints from Experiment 11 Phase 2 observations.
# These are estimates based on output characteristics — the management
# layer will update them from actual performance in each round.
INITIAL_FINGERPRINTS = {
    "CC2": CapabilityFingerprint(D_decay=0.10, v_bar=0.90, A=0.85, C=0.80),
    "ChatGPT": CapabilityFingerprint(D_decay=0.15, v_bar=0.85, A=0.80, C=0.75),
    "Gemini": CapabilityFingerprint(D_decay=0.20, v_bar=0.80, A=0.75, C=0.70),
    "DeepSeek": CapabilityFingerprint(D_decay=0.25, v_bar=0.75, A=0.80, C=0.65),
    "Codex": CapabilityFingerprint(D_decay=0.20, v_bar=0.80, A=0.85, C=0.70),
}

# L = input context window minus 32K reserved for output generation.
# This is the token budget available for the PROMPT (system + user).
MODEL_SPECS = {
    "CC2": {"tau": 400.0, "L": 168000.0, "c": 0.015, "L_std": 0.0},
    "ChatGPT": {"tau": 200.0, "L": 96000.0, "c": 0.02, "L_std": 0.0},
    "Gemini": {"tau": 350.0, "L": 968000.0, "c": 0.01, "L_std": 0.0},
    "DeepSeek": {"tau": 200.0, "L": 32000.0, "c": 0.01, "L_std": 0.0},
    "Codex": {"tau": 600.0, "L": 96000.0, "c": 0.02, "L_std": 10000.0},
}

# Models excluded from convergence calculations (e.g. always decomposed,
# so their vocabulary growth follows a different trajectory).
CONVERGENCE_EXCLUDED_MODELS = {"DeepSeek"}

# Context pressure threshold (characters) at which a model is switched to
# decomposed dispatch.
DECOMPOSITION_CONTEXT_THRESHOLD = {
    "DeepSeek": 0,
    "Codex": 60000,
    "ChatGPT": 80000,
    "Gemini": 200000,
    "CC2": 120000,
}

# WP4b: Per-model context character budgets for findings relay.
# When accumulated findings exceed this, the insect brain switches to
# summary-only mode (finding IDs + one-line descriptions). This prevents
# prompt bloat while preserving cross-pollination awareness.
# Mirrors DynamicManagementConfig.context_budget_overrides but available
# at the runner level for non-DM dispatch paths.
CONTEXT_CHAR_BUDGET = {
    "CC2": 30_000,        # WP4c: matches DeepSeek's proven limit
    "ChatGPT": 80_000,
    "Gemini": 200_000,    # 1M context window — generous budget
    "DeepSeek": 30_000,   # Reasoner CoT scales with input
    "Codex": 60_000,
}


# ─────────────────────────────────────────────────────────────────────────────
# Environment and setup
# ─────────────────────────────────────────────────────────────────────────────

def source_env() -> None:
    """Load .env file from repo root into os.environ."""
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()


def build_model_specs(exp_config: ExperimentConfig) -> List[ModelSpec]:
    """Build ModelSpec list for DynamicManager from experiment config."""
    specs = []
    for mc in exp_config.models:
        if mc.role == "collator":
            continue
        fp = INITIAL_FINGERPRINTS.get(
            mc.label, CapabilityFingerprint(0.2, 0.7, 0.7, 0.5)
        )
        params = MODEL_SPECS.get(mc.label, {})
        specs.append(ModelSpec(
            model_id=mc.label,
            fingerprint=fp,
            **params,
        ))
    return specs


def next_experiment_number() -> str:
    """Auto-increment: scan bench/logs/experiment_* and return max+1."""
    logs_root = REPO_ROOT / "bench" / "logs"
    max_num = 0
    if logs_root.exists():
        for d in logs_root.iterdir():
            m = re.match(r'experiment_(\d+)$', d.name)
            if m:
                max_num = max(max_num, int(m.group(1)))
    return str(max_num + 1)


def build_task_prompt(task_description: str) -> str:
    """Build the P-pass prompt for distributed review."""
    return (
        "You are participating in a distributed compute P-pass under CDSFL.\n\n"
        "Your task: review the following artifact and produce structured findings.\n"
        "For each finding, provide:\n"
        "  FINDING_ID: unique identifier (e.g., F001)\n"
        "  SEVERITY: 0.0 to 1.0 (1.0 = critical)\n"
        "  FLAW_CLASS: integer category (1=logic, 2=interface, 3=notation, "
        "4=completeness, 5=correctness, 6=edge-case, 7=performance, 8=documentation)\n"
        "  ABSTRACTION_INDEX: 0.0 to 1.0 (0=surface, 1=architectural)\n"
        "  DESCRIPTION: what is wrong and why it matters\n"
        "  PROPOSED_FIX: how to fix it\n"
        "  VERIFIED: TRUE if you have a proof/test, FALSE if this is an assertion\n\n"
        "Produce ALL findings you can identify. Do not hold back for subsequent "
        "rounds — give everything in this round.\n\n"
        "=== ARTIFACT UNDER REVIEW ===\n\n"
        f"{task_description}\n\n"
        "=== END ARTIFACT ===\n\n"
        "Produce your findings now."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Finding parser
# ─────────────────────────────────────────────────────────────────────────────

# Flaw class mapping: both the prompt taxonomy (1=logic, 2=interface, etc.)
# and area-based names that models may use. Sorted by key length descending
# for longest-match-first semantics (CC2 recommendation).
_FLAW_CLASS_MAP = {
    # Prompt taxonomy terms (CX catch: models use these, not area names)
    "documentation": 8, "performance": 7, "edge-case": 6, "edge_case": 6,
    "correctness": 5, "completeness": 4, "notation": 3, "interface": 2,
    "logic": 1,
    # Area-based names models may use
    "convergence_detection": 1, "convergence detection": 1, "convergence": 1,
    "failure_handling": 2, "failure handling": 2, "failure": 2, "error": 2,
    "role_assignment": 3, "role assignment": 3, "role": 3, "allocation": 3,
    "load_balancing": 4, "load balancing": 4, "load": 4, "balance": 4,
    "round_progression": 5, "round progression": 5, "round": 5, "fsm": 5,
    "state_machine": 5, "state machine": 5,
    "diminishing_returns": 6, "diminishing returns": 6, "diminishing": 6, "stop": 6,
    "api": 7, "integration": 7,
    "mathematical": 8, "invariant": 8, "formal": 8,
    "resource_leak": 7, "resource leak": 7,
}


def _parse_flaw_class(text: str) -> int:
    """Parse flaw class from text or integer.

    Handles three formats (CX catch):
    1. Bare integer: "5"
    2. Integer with label: "5 (correctness)"
    3. Text label: "convergence_detection"

    For unknown text, uses deterministic hash (Gemini recommendation)
    to ensure consistent mapping without corrupting metrics.
    """
    text = text.strip().strip("*").strip()
    # Try bare integer first
    try:
        return max(1, min(8, int(text)))
    except ValueError:
        pass
    # Try "5 (correctness)" format — extract leading integer
    leading_int = re.match(r'(\d+)\s*[\(\[]', text)
    if leading_int:
        return max(1, min(8, int(leading_int.group(1))))
    # Text matching — longest match first (CC2 recommendation)
    key = text.lower().strip()
    for map_key in sorted(_FLAW_CLASS_MAP.keys(), key=len, reverse=True):
        if map_key in key:
            return _FLAW_CLASS_MAP[map_key]
    # Deterministic hash for unknown classes (Gemini recommendation)
    return (abs(hash(key)) % 8) + 1


def parse_findings(model_id: str, round_idx: int, response: str) -> List[Finding]:
    """Extract structured findings from model response.

    Parser priority (first match wins):
      1. JSON array    — ChatGPT GPT-5.4 format: [{"FINDING_ID": ...}, ...]
      2. Tuple format  — Gemini/ChatGPT: (F001, 0.9, 5, 0.8, "desc", "fix", TRUE)
      3. Marker format — CC2/Codex: FINDING_ID: F001\\nSEVERITY: 0.9\\n...
      4. Bare ID       — ChatGPT: F001\\nSEVERITY: 0.9\\n...
      5. Fallback      — Single unstructured finding from raw text

    Handles:
    - Markdown bold markers (**FINDING_ID**: ...)
    - Underscores/hyphens (Finding_ID, Finding-ID, finding_id)
    - Text flaw classes mapped to integers
    - Various separator styles (: vs = vs -)
    - Triple-backtick code fences (Gemini)
    - _FOLLOW companion entries (ChatGPT FFF) — filtered from JSON

    No model is penalised for format variation.
    """
    findings: List[Finding] = []

    # Strip markdown bold markers — CC2 uses **SEVERITY:** format
    response = re.sub(r'\*{2,}', '', response)

    # Strip triple-backtick code fences — Gemini wraps in ```text...```
    response = re.sub(r'^\s*```\w*\s*\n?', '', response, flags=re.MULTILINE)
    response = re.sub(r'^\s*```\s*$', '', response, flags=re.MULTILINE)

    # ── 1. JSON array parser ─────────────────────────────────────────
    # ChatGPT (GPT-5.4) outputs findings as JSON arrays:
    #   [{"FINDING_ID": "IM_F001", "SEVERITY": 0.9, ...}, ...]
    # Must run FIRST — JSON quotes around keys break all regex patterns.
    # Run 5 lost 29 ChatGPT findings to this bug.
    json_match = re.search(r'\[[\s\n]*\{', response)
    if json_match:
        start = json_match.start()
        bracket_depth = 0
        end = start
        for i, ch in enumerate(response[start:], start):
            if ch == '[':
                bracket_depth += 1
            elif ch == ']':
                bracket_depth -= 1
                if bracket_depth == 0:
                    end = i + 1
                    break
        json_text = response[start:end]
        try:
            arr = json.loads(json_text)
            if isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], dict):
                # Validate this is actually a findings array, not embedded JSON
                # (e.g. remediation actions in PROPOSED_FIX). Require at least
                # one object to have FINDING_ID or SEVERITY — the two fields
                # that distinguish findings from arbitrary JSON.
                _FINDINGS_KEYS = {"FINDING_ID", "SEVERITY"}
                has_findings_key = any(
                    _FINDINGS_KEYS & {k.upper().replace(" ", "_") for k in obj}
                    for obj in arr if isinstance(obj, dict)
                )
                if not has_findings_key:
                    raise ValueError("JSON array lacks findings keys — not a findings array")
                for obj in arr:
                    if not isinstance(obj, dict):
                        continue
                    norm = {k.upper().replace(" ", "_"): v for k, v in obj.items()}
                    fid = str(norm.get("FINDING_ID", f"F{len(findings)+1:03d}"))
                    # Skip _FOLLOW companion entries — supplementary
                    if "_FOLLOW" in fid.upper():
                        continue
                    severity = float(norm.get("SEVERITY", 0.5))
                    severity = max(0.0, min(1.0, severity))
                    flaw_raw = norm.get("FLAW_CLASS", 1)
                    if isinstance(flaw_raw, str):
                        try:
                            flaw_class = max(1, min(8, int(flaw_raw)))
                        except ValueError:
                            flaw_class = 1
                    else:
                        flaw_class = max(1, min(8, int(flaw_raw)))
                    abstraction = float(norm.get("ABSTRACTION_INDEX", 0.5))
                    abstraction = max(0.0, min(1.0, abstraction))
                    description = str(norm.get("DESCRIPTION", ""))
                    proposed_fix = str(norm.get("PROPOSED_FIX", ""))
                    verified_raw = norm.get("VERIFIED", False)
                    if isinstance(verified_raw, str):
                        verified = verified_raw.upper() == "TRUE"
                    else:
                        verified = bool(verified_raw)
                    findings.append(Finding(
                        finding_id=f"{model_id}_{fid}",
                        model_id=model_id,
                        round_idx=round_idx,
                        flaw_class=flaw_class,
                        severity=severity,
                        abstraction_index=abstraction,
                        description=description,
                        proposed_fix=proposed_fix,
                        verified=verified,
                    ))
                if findings:
                    return findings
        except (json.JSONDecodeError, ValueError, TypeError):
            pass  # Not valid JSON — fall through to tuple parser

    # ── 2. Tuple-format parser ───────────────────────────────────────
    # (F001, 0.9, 5, 0.8, "description", "fix", TRUE)
    # or with prefixed IDs: (LB_R2_F001, 0.88, 5, 0.42, "desc", "fix", "TRUE")
    # CX P-pass: DOTALL removed — tuples are single-line.
    tuple_pattern_quoted = re.compile(
        r'\(([A-Z0-9_]*F\d{2,4}),\s*'
        r'([\d.]+),\s*'
        r'(\d+),\s*'
        r'([\d.]+),\s*'
        r'"([^"]*(?:\\"[^"]*)*)"\s*,\s*'
        r'"([^"]*(?:\\"[^"]*)*)"\s*,\s*'
        r'"(TRUE|FALSE|True|False|true|false)"\s*\)',
    )
    tuple_pattern_bare = re.compile(
        r'\(([A-Z0-9_]*F\d{2,4}),\s*'
        r'([\d.]+),\s*'
        r'(\d+),\s*'
        r'([\d.]+),\s*'
        r'"([^"]*(?:\\"[^"]*)*)"\s*,\s*'
        r'"([^"]*(?:\\"[^"]*)*)"\s*,\s*'
        r'(TRUE|FALSE|True|False|true|false)\s*\)',
    )
    tuple_matches = list(tuple_pattern_quoted.finditer(response))
    if not tuple_matches:
        tuple_matches = list(tuple_pattern_bare.finditer(response))
    if tuple_matches:
        for m in tuple_matches:
            fid = m.group(1).strip()
            severity = max(0.0, min(1.0, float(m.group(2))))
            flaw_class = max(1, min(8, int(m.group(3))))
            abstraction = max(0.0, min(1.0, float(m.group(4))))
            description = m.group(5).replace('\\"', '"')
            proposed_fix = m.group(6).replace('\\"', '"')
            verified = m.group(7).upper() == "TRUE"
            findings.append(Finding(
                finding_id=f"{model_id}_{fid}",
                model_id=model_id,
                round_idx=round_idx,
                flaw_class=flaw_class,
                severity=severity,
                abstraction_index=abstraction,
                description=description,
                proposed_fix=proposed_fix,
                verified=verified,
            ))
        return findings

    # ── 3/4. Marker and bare ID parsers ──────────────────────────────
    finding_id_pattern = (
        r'\*{0,2}[Ff][Ii][Nn][Dd][Ii][Nn][Gg][\s_-]*'
        r'[Ii][Dd]\*{0,2}\s*[:=\-]\s*'
    )

    blocks = re.split(rf'(?={finding_id_pattern})', response)

    # If no FINDING_ID markers, try bare F### format
    matched_primary = [
        b for b in blocks
        if b.strip() and re.match(finding_id_pattern, b.strip())
    ]
    use_bare = False
    if len(matched_primary) == 0:
        bare_blocks = re.split(
            r'(?m)(?=^\*{0,2}F\d{2,4}\*{0,2}\s*:?\s*$)', response
        )
        matched_bare = [
            b for b in bare_blocks if b.strip()
            and re.match(
                r'\*{0,2}F\d{2,4}\*{0,2}\s*:?\s*',
                b.strip().split('\n')[0],
            )
        ]
        if len(matched_bare) > 0:
            blocks = bare_blocks
            use_bare = True

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        first_line = block.split('\n')[0].strip()
        if use_bare:
            bare_match = re.match(
                r'\*{0,2}(F\d{2,4})\*{0,2}\s*:?\s*$', first_line
            )
            if not bare_match:
                continue
        else:
            if not re.match(finding_id_pattern, block):
                continue
            bare_match = None

        fid_match = re.search(rf'{finding_id_pattern}(.+?)(?:\n|$)', block)
        if not fid_match and bare_match:
            fid_match = bare_match
        sev_match = re.search(
            r'\*{0,2}[Ss][Ee][Vv][Ee][Rr][Ii][Tt][Yy]\*{0,2}'
            r'\s*[:=\-]\s*([\d.]+)', block
        )
        fc_match = re.search(
            r'\*{0,2}[Ff][Ll][Aa][Ww][\s_-]*[Cc][Ll][Aa][Ss][Ss]\*{0,2}'
            r'\s*[:=\-]\s*(.+?)(?:\n|$)', block
        )
        ai_match = re.search(
            r'\*{0,2}[Aa][Bb][Ss][Tt][Rr][Aa][Cc][Tt][Ii][Oo][Nn][\s_-]*'
            r'[Ii][Nn][Dd][Ee][Xx]\*{0,2}\s*[:=\-]\s*([\d.]+)', block
        )
        desc_match = re.search(
            r'\*{0,2}[Dd][Ee][Ss][Cc][Rr][Ii][Pp][Tt][Ii][Oo][Nn]\*{0,2}'
            r'\s*[:=\-]\s*(.+?)'
            r'(?=\n\s*(?:\*{0,2}(?:[Pp][Rr][Oo][Pp]|[Vv][Ee][Rr][Ii]|'
            r'[Ff][Ii][Nn][Dd])|$))',
            block, re.DOTALL
        )
        ver_match = re.search(
            r'\*{0,2}[Vv][Ee][Rr][Ii][Ff][Ii][Ee][Dd]\*{0,2}'
            r'\s*[:=\-]\s*(TRUE|FALSE|true|false|True|False)', block
        )
        fix_match = re.search(
            r'\*{0,2}[Pp][Rr][Oo][Pp][Oo][Ss][Ee][Dd][\s_-]*'
            r'[Ff][Ii][Xx]\*{0,2}\s*[:=\-]\s*(.+?)'
            r'(?=\n\s*(?:\*{0,2}(?:[Vv][Ee][Rr][Ii]|[Ff][Ii][Nn][Dd])|$))',
            block, re.DOTALL
        )

        if fid_match:
            finding_id = fid_match.group(1).strip().strip("*")
        else:
            finding_id = f"F{len(findings)+1:03d}"
        severity = float(sev_match.group(1)) if sev_match else 0.5
        flaw_class = _parse_flaw_class(fc_match.group(1)) if fc_match else 1
        abstraction = float(ai_match.group(1)) if ai_match else 0.5
        description = desc_match.group(1).strip() if desc_match else block[:200]
        proposed_fix = fix_match.group(1).strip() if fix_match else ""
        verified = (
            ver_match.group(1).upper() == "TRUE" if ver_match else False
        )

        severity = max(0.0, min(1.0, severity))
        abstraction = max(0.0, min(1.0, abstraction))
        flaw_class = max(1, min(8, flaw_class))

        findings.append(Finding(
            finding_id=f"{model_id}_{finding_id}",
            model_id=model_id,
            round_idx=round_idx,
            flaw_class=flaw_class,
            severity=severity,
            abstraction_index=abstraction,
            description=description,
            proposed_fix=proposed_fix,
            verified=verified,
        ))

    # ── 5. Fallback ──────────────────────────────────────────────────
    if not findings and len(response.strip()) > 50:
        findings.append(Finding(
            finding_id=f"{model_id}_UNSTRUCTURED",
            model_id=model_id,
            round_idx=round_idx,
            flaw_class=1,
            severity=0.3,
            abstraction_index=0.3,
            description=response[:500],
            verified=False,
        ))

    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────

def _dispatch_worker(model_config, prompt, cdsfl_text, result_queue):
    """Worker function for multiprocessing watchdog."""
    try:
        response = dispatch(model_config, prompt, cdsfl_text)
        result_queue.put(("ok", response))
    except Exception as e:
        result_queue.put(("error", e))


def dispatch_to_model(
    model_config: ModelConfig,
    prompt: str,
    cdsfl_text: str,
    wall_clock_limit: float = 0,
) -> tuple[str, float]:
    """Dispatch prompt to model, return (response_text, elapsed_seconds).

    Two-layer resilience (CX finding 5):
    Layer 1: httpx timeouts on each API client (already applied).
    Layer 2: multiprocessing watchdog — if the process exceeds wall_clock_limit
    seconds, it is forcibly terminated. Catches stuck sockets, GIL-holding
    C-extension blocks, and any other failure that httpx timeouts miss.
    Default wall_clock_limit = model timeout * 2.
    """
    import multiprocessing as mp

    if wall_clock_limit <= 0:
        wall_clock_limit = model_config.timeout * 2

    t0 = time.monotonic()
    result_queue = mp.Queue()
    proc = mp.Process(
        target=_dispatch_worker,
        args=(model_config, prompt, cdsfl_text, result_queue),
        daemon=True,
    )
    proc.start()
    proc.join(timeout=wall_clock_limit)
    elapsed = time.monotonic() - t0

    if proc.is_alive():
        _log(
            f"  {model_config.label}: WATCHDOG — process exceeded "
            f"{wall_clock_limit:.0f}s wall clock, terminating"
        )
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
            proc.join(timeout=2)
        raise TimeoutError(
            f"{model_config.label} dispatch exceeded wall-clock limit "
            f"({wall_clock_limit:.0f}s). Process forcibly terminated."
        )

    if result_queue.empty():
        raise RuntimeError(
            f"{model_config.label} dispatch process exited without result "
            f"(exit code {proc.exitcode})"
        )

    status, payload = result_queue.get_nowait()
    if status == "error":
        raise payload
    return payload, elapsed


# ─────────────────────────────────────────────────────────────────────────────
# Context formatting
# ─────────────────────────────────────────────────────────────────────────────

def format_findings_for_context(
    findings: List[Finding],
    max_findings: int = 150,
    recency_rounds: int = 3,
) -> str:
    """Format findings as text for inclusion in next round's prompt.

    Context windowing: instead of dumping ALL findings (which grows linearly
    and exceeds context windows), include:
    1. All findings from the most recent `recency_rounds` rounds
    2. Top-severity findings from earlier rounds, up to `max_findings` total

    This prevents context bloat while preserving the most valuable signal:
    recent findings (for duplication avoidance) and high-severity findings
    (for quality benchmarking).
    """
    if not findings:
        return "(No findings from prior rounds.)"

    if len(findings) <= max_findings:
        selected = findings
    else:
        max_round = max(f.round_idx for f in findings)
        recent_cutoff = max(0, max_round - recency_rounds + 1)

        recent = [f for f in findings if f.round_idx >= recent_cutoff]
        older = [f for f in findings if f.round_idx < recent_cutoff]

        remaining_slots = max(0, max_findings - len(recent))
        older_sorted = sorted(older, key=lambda f: f.severity, reverse=True)
        selected = recent + older_sorted[:remaining_slots]

    lines = [
        f"(Showing {len(selected)} of {len(findings)} total findings: "
        f"most recent rounds + highest severity from earlier rounds)\n"
    ]
    for f in selected:
        lines.append(
            f"FINDING_ID: {f.finding_id}  [source: {f.model_id}]\n"
            f"  SEVERITY: {f.severity:.2f}\n"
            f"  FLAW_CLASS: {f.flaw_class}\n"
            f"  ABSTRACTION: {f.abstraction_index:.2f}\n"
            f"  VERIFIED: {'TRUE' if f.verified else 'FALSE'}\n"
            f"  DESCRIPTION: {f.description[:300]}\n"
        )
    return "\n".join(lines)
