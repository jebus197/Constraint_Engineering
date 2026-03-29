#!/usr/bin/env python3
"""Experiment 12: Live Wire Test — Dynamic Management Layer Validation.

First live test of the DynamicManager under real distributed compute.
CC1 is collator. DynamicManager makes all allocation, convergence, and
stop decisions. CC1 executes them via the API layer.

Usage:
    python3 bench/run_exp12_live_wire.py [preflight|blind|full]

    preflight  — verify all models respond correctly
    blind      — run blind round only (Phase 1)
    full       — run full experiment (blind + adaptive rounds until terminal)
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    load_default_config,
    dispatch,
    save_output,
    _log,
    CircuitBreakerTripped,
    ExperimentConfig,
    ModelConfig,
)
from dynamic_management import (
    DynamicManager,
    DynamicManagementConfig,
    ModelSpec,
    CapabilityFingerprint,
    Task,
    Finding,
    ModelResponse,
    ManagerEvent,
    ManagerEventType,
    FailureType,
    Role,
)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "experiment_12"

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
# Prior config used max_output_tokens (32768) for L — wrong semantics.
# Codex retains L_std because CLI delivery mechanism has uncertain limits.
MODEL_SPECS = {
    "CC2": {"tau": 400.0, "L": 168000.0, "c": 0.015, "L_std": 0.0},      # Opus 4.6: ~200K context - 32K output
    "ChatGPT": {"tau": 200.0, "L": 96000.0, "c": 0.02, "L_std": 0.0},    # GPT-5.4: ~128K context - 32K output
    "Gemini": {"tau": 150.0, "L": 968000.0, "c": 0.01, "L_std": 0.0},    # Gemini 3.1 Pro: ~1M context - 32K output
    "DeepSeek": {"tau": 200.0, "L": 32000.0, "c": 0.01, "L_std": 0.0},   # DeepSeek Reasoner: ~64K context - 32K output
    "Codex": {"tau": 600.0, "L": 96000.0, "c": 0.02, "L_std": 10000.0},  # GPT-5.4 via CLI: ~128K context - 32K, uncertain
}


def source_env() -> None:
    """Load .env file."""
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
        fp = INITIAL_FINGERPRINTS.get(mc.label, CapabilityFingerprint(0.2, 0.7, 0.7, 0.5))
        params = MODEL_SPECS.get(mc.label, {})
        specs.append(ModelSpec(
            model_id=mc.label,
            fingerprint=fp,
            **params,
        ))
    return specs


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


def parse_findings(model_id: str, round_idx: int, response: str) -> List[Finding]:
    """Extract structured findings from model response.

    Parses the FINDING_ID / SEVERITY / FLAW_CLASS / etc. format.
    Falls back to treating the entire response as a single finding if
    structured parsing fails — no model is penalised for format variation.
    """
    findings = []
    import re

    # Split on FINDING_ID markers
    blocks = re.split(r'(?=FINDING_ID\s*:)', response)

    for block in blocks:
        block = block.strip()
        if not block or not block.startswith("FINDING_ID"):
            continue

        # Extract fields
        fid_match = re.search(r'FINDING_ID\s*:\s*(.+?)(?:\n|$)', block)
        sev_match = re.search(r'SEVERITY\s*:\s*([\d.]+)', block)
        fc_match = re.search(r'FLAW_CLASS\s*:\s*(\d+)', block)
        ai_match = re.search(r'ABSTRACTION_INDEX\s*:\s*([\d.]+)', block)
        desc_match = re.search(r'DESCRIPTION\s*:\s*(.+?)(?=\n\s*(?:PROPOSED_FIX|VERIFIED|FINDING_ID|$))', block, re.DOTALL)
        ver_match = re.search(r'VERIFIED\s*:\s*(TRUE|FALSE|true|false)', block)

        finding_id = fid_match.group(1).strip() if fid_match else f"F{len(findings)+1:03d}"
        severity = float(sev_match.group(1)) if sev_match else 0.5
        flaw_class = int(fc_match.group(1)) if fc_match else 1
        abstraction = float(ai_match.group(1)) if ai_match else 0.5
        description = desc_match.group(1).strip() if desc_match else block[:200]
        verified = ver_match.group(1).upper() == "TRUE" if ver_match else False

        # Clamp values
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
            verified=verified,
        ))

    # Fallback: if no structured findings parsed, create one from the response
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


def dispatch_to_model(
    model_config: ModelConfig,
    prompt: str,
    cdsfl_text: str,
) -> tuple[str, float]:
    """Dispatch prompt to model, return (response_text, elapsed_seconds)."""
    t0 = time.monotonic()
    response = dispatch(model_config, prompt, cdsfl_text)
    elapsed = time.monotonic() - t0
    return response, elapsed


def run_blind_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    prompt: str,
    cdsfl_text: str,
) -> tuple[Dict[str, ModelResponse], List[Finding]]:
    """Phase 1: Blind round — same prompt to all feasible models.

    Returns (responses_dict, all_findings).
    """
    _log("=== PHASE 1: BLIND ROUND ===")
    responses: Dict[str, ModelResponse] = {}
    all_findings: List[Finding] = []

    for mc in exp_config.models:
        if mc.role == "collator":
            continue

        # Pre-dispatch feasibility check
        model_spec = next(
            (m for m in mgr.models if m.model_id == mc.label), None
        )
        if model_spec is None:
            _log(f"  {mc.label}: not in manager pool, skipping")
            continue

        prompt_tokens = len(prompt) // 4  # rough estimate
        feasible, p_feasible = mgr.check_dispatch_feasibility(model_spec, prompt_tokens)
        _log(f"  {mc.label}: feasibility P={p_feasible:.3f}, dispatch={'YES' if feasible else 'BLOCKED'}")

        if not feasible:
            # Do NOT create a ModelResponse for blocked dispatches.
            # Feasibility block != model failure. See adaptive round comment.
            continue

        # Dispatch
        try:
            text, elapsed = dispatch_to_model(mc, prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            # Parse findings
            findings = parse_findings(mc.label, 0, text)
            all_findings.extend(findings)
            _log(f"  {mc.label}: {len(findings)} findings parsed")

            responses[mc.label] = ModelResponse(
                model_id=mc.label,
                round_idx=0,
                content=text,
                response_time=elapsed,
                parseable=len(findings) > 0,
                format_compliant=True,
                finding_count=len(findings),
                mean_abstraction=(
                    sum(f.abstraction_index for f in findings) / len(findings)
                    if findings else 0.5
                ),
            )

            # Save output
            save_output(
                LOGS_DIR, "blind", mc.label, prompt[:200] + "...",
                text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(findings),
                    "round": 0,
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            raise
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {e}")
            responses[mc.label] = ModelResponse(
                model_id=mc.label,
                round_idx=0,
                content="",
                response_time=mc.timeout + 1.0 if "timeout" in str(e).lower() else 0.0,
            )

    _log(f"Blind round complete: {len(all_findings)} total findings from "
         f"{sum(1 for r in responses.values() if r.content)} models")

    return responses, all_findings


def run_adaptive_round(
    exp_config: ExperimentConfig,
    mgr: DynamicManager,
    round_idx: int,
    base_artifact: str,
    prior_findings_text: str,
    cdsfl_text: str,
) -> tuple[Dict[str, ModelResponse], List[Finding]]:
    """Phase 2+: Adaptive round — PM synthesises, tasks allocated by capability.

    Each model gets a prompt that includes the artifact PLUS the prior
    round's findings, and is asked to find what was missed.
    """
    _log(f"=== ROUND {round_idx}: ADAPTIVE ===")

    # Build the round prompt with prior context
    prompt = (
        f"You are in ROUND {round_idx} of a distributed compute P-pass.\n\n"
        f"The following findings were produced in prior rounds:\n\n"
        f"{prior_findings_text}\n\n"
        f"Your task: review the artifact below and find what was MISSED. "
        f"Do not repeat findings already listed above. Focus on:\n"
        f"- Flaws the prior findings did not catch\n"
        f"- Deeper analysis of issues that were only superficially noted\n"
        f"- Cross-cutting concerns that span multiple areas\n"
        f"- Edge cases not yet tested\n\n"
        f"Use the same structured format (FINDING_ID, SEVERITY, etc.).\n\n"
        f"=== ARTIFACT UNDER REVIEW ===\n\n"
        f"{base_artifact}\n\n"
        f"=== END ARTIFACT ===\n\n"
        f"Produce your findings now. If you genuinely find nothing new, "
        f"state that explicitly."
    )

    responses: Dict[str, ModelResponse] = {}
    all_findings: List[Finding] = []

    # Get allocation from the manager (uses live fingerprints)
    _log(f"  Live fingerprints:")
    for mid, fp in mgr._live_fingerprints.items():
        role = mgr.role_assignment.role_map.get(mid, Role.PAR)
        _log(f"    {mid} ({role.value}): D={fp.D_decay:.3f} v={fp.v_bar:.3f} "
             f"A={fp.A:.3f} C={fp.C:.3f}")

    for mc in exp_config.models:
        if mc.role == "collator":
            continue
        if mc.label not in mgr.failure_handler.active_models:
            _log(f"  {mc.label}: not active, skipping")
            continue

        model_spec = next(
            (m for m in mgr.get_live_models() if m.model_id == mc.label), None
        )
        if model_spec is None:
            continue

        prompt_tokens = len(prompt) // 4
        feasible, p_feasible = mgr.check_dispatch_feasibility(model_spec, prompt_tokens)
        if not feasible:
            _log(f"  {mc.label}: feasibility BLOCKED (P={p_feasible:.3f})")
            # Do NOT create a ModelResponse for blocked dispatches.
            # Feasibility block is a prompt-sizing issue, not a model failure.
            # Creating an empty response would trigger EMPTY failure detection
            # and degrade the model's fingerprint for something it never attempted.
            continue

        try:
            text, elapsed = dispatch_to_model(mc, prompt, cdsfl_text)
            _log(f"  {mc.label}: {len(text)} chars, {elapsed:.1f}s")

            findings = parse_findings(mc.label, round_idx, text)
            all_findings.extend(findings)
            _log(f"  {mc.label}: {len(findings)} findings parsed")

            responses[mc.label] = ModelResponse(
                model_id=mc.label, round_idx=round_idx, content=text,
                response_time=elapsed, parseable=len(findings) > 0,
                format_compliant=True, finding_count=len(findings),
                mean_abstraction=(
                    sum(f.abstraction_index for f in findings) / len(findings)
                    if findings else 0.5
                ),
            )

            save_output(
                LOGS_DIR, f"round{round_idx}", mc.label, prompt[:200] + "...",
                text,
                metadata={
                    "elapsed": round(elapsed, 1),
                    "chars": len(text),
                    "findings_count": len(findings),
                    "round": round_idx,
                },
            )

        except CircuitBreakerTripped as e:
            _log(f"  {mc.label}: CIRCUIT BREAKER — {e}")
            raise
        except Exception as e:
            _log(f"  {mc.label}: ERROR — {e}")
            responses[mc.label] = ModelResponse(
                model_id=mc.label, round_idx=round_idx, content="",
                response_time=mc.timeout + 1.0 if "timeout" in str(e).lower() else 0.0,
            )

    _log(f"Round {round_idx} complete: {len(all_findings)} findings from "
         f"{sum(1 for r in responses.values() if r.content)} models")

    return responses, all_findings


def format_findings_for_context(findings: List[Finding]) -> str:
    """Format findings as text for inclusion in next round's prompt."""
    if not findings:
        return "(No findings from prior rounds.)"

    lines = []
    for f in findings:
        lines.append(
            f"FINDING_ID: {f.finding_id}\n"
            f"  SEVERITY: {f.severity:.2f}\n"
            f"  FLAW_CLASS: {f.flaw_class}\n"
            f"  ABSTRACTION: {f.abstraction_index:.2f}\n"
            f"  VERIFIED: {'TRUE' if f.verified else 'FALSE'}\n"
            f"  DESCRIPTION: {f.description[:300]}\n"
        )
    return "\n".join(lines)


CHECKPOINT_PATH = LOGS_DIR / "checkpoint.json"


def save_checkpoint(data: Dict[str, Any]) -> None:
    """Save experiment state to disk after each dispatch."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    _log(f"  [CHECKPOINT] Saved ({len(data.get('completed_models', []))} models, "
         f"round {data.get('current_round', 0)})")


def load_checkpoint() -> Optional[Dict[str, Any]]:
    """Load checkpoint if it exists."""
    if CHECKPOINT_PATH.exists():
        data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
        _log(f"  [CHECKPOINT] Resumed from round {data.get('current_round', 0)}, "
             f"{len(data.get('completed_models', []))} models completed")
        return data
    return None


def run_full_experiment():
    """Run the full Live Wire experiment."""
    source_env()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    exp_config = load_default_config()
    exp_config.logs_dir = LOGS_DIR
    cdsfl_text = exp_config.cdsfl_system_prompt

    # Build model specs for the DynamicManager
    model_specs = build_model_specs(exp_config)
    _log(f"Model pool: {[m.model_id for m in model_specs]}")

    # Initialise DynamicManager
    events: List[ManagerEvent] = []
    def on_event(event: ManagerEvent) -> None:
        events.append(event)
        _log(f"  [EVENT] {event.event_type.value}: {event.detail}")

    dm_config = DynamicManagementConfig(
        max_rounds=20,  # Let convergence and diminishing returns detectors decide
        feasibility_threshold=0.90,
    )
    mgr = DynamicManager(model_specs, config=dm_config, event_callback=on_event)

    _log(f"Roles assigned: {mgr.role_assignment.role_map}")
    _log(f"PM: {mgr.role_assignment.pm_model_id}")

    # Load the artifact to review
    artifact_path = REPO_ROOT / "bench" / "dynamic_management.py"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    _log(f"Artifact: {artifact_path.name} ({len(artifact_text)} chars, "
         f"{artifact_text.count(chr(10))} lines)")

    # Build blind round prompt
    blind_prompt = build_task_prompt(artifact_text)
    _log(f"Blind prompt: {len(blind_prompt)} chars")

    # ── Phase 1: Blind Round ──
    responses, findings = run_blind_round(exp_config, mgr, blind_prompt, cdsfl_text)

    # Process through DynamicManager
    round_cost = sum(
        len(r.content) * 0.00001 for r in responses.values()  # rough cost estimate
    )
    result = mgr.process_round(
        responses, findings, [], round_cost=round_cost,
        duration=sum(r.response_time for r in responses.values()),
    )
    _log(f"Round 0 result: state={result.state}, "
         f"kappa={result.convergence_metric:.4f}, "
         f"mu={result.marginal_value:.4f}, "
         f"converged={result.converged}, stop={result.stop}")

    # Track all findings across rounds
    all_findings = list(findings)

    # ── Phase 2+: Adaptive Rounds ──
    round_idx = 1
    while not mgr.fsm.is_terminal:
        _log(f"\n{'='*60}")
        findings_context = format_findings_for_context(all_findings)

        responses, new_findings = run_adaptive_round(
            exp_config, mgr, round_idx, artifact_text,
            findings_context, cdsfl_text,
        )
        all_findings.extend(new_findings)

        round_cost = sum(
            len(r.content) * 0.00001 for r in responses.values()
        )
        result = mgr.process_round(
            responses, new_findings, [], round_cost=round_cost,
            duration=sum(r.response_time for r in responses.values()),
        )
        _log(f"Round {round_idx} result: state={result.state}, "
             f"kappa={result.convergence_metric:.4f}, "
             f"mu={result.marginal_value:.4f}, "
             f"converged={result.converged}, stop={result.stop}")

        round_idx += 1

    # ── Final Report ──
    _log(f"\n{'='*60}")
    _log(f"EXPERIMENT COMPLETE")
    _log(f"  Termination: {mgr.fsm.termination_reason}")
    _log(f"  Rounds: {round_idx}")
    _log(f"  Total findings: {len(all_findings)}")
    _log(f"  Active models at end: {mgr.failure_handler.active_models}")
    _log(f"  Total events: {len(events)}")

    # Fingerprint evolution
    _log(f"\nFingerprint evolution:")
    for mid in sorted(mgr._live_fingerprints):
        initial = INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0, 0, 0, 0))
        final = mgr._live_fingerprints[mid]
        _log(f"  {mid}:")
        _log(f"    Initial: D={initial.D_decay:.3f} v={initial.v_bar:.3f} "
             f"A={initial.A:.3f} C={initial.C:.3f}")
        _log(f"    Final:   D={final.D_decay:.3f} v={final.v_bar:.3f} "
             f"A={final.A:.3f} C={final.C:.3f}")

    # Save final report
    report = {
        "experiment": "12_live_wire",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "termination_reason": mgr.fsm.termination_reason.value if mgr.fsm.termination_reason else None,
        "rounds": round_idx,
        "total_findings": len(all_findings),
        "active_models_at_end": sorted(mgr.failure_handler.active_models),
        "total_events": len(events),
        "fingerprint_evolution": {
            mid: {
                "initial": {
                    "D_decay": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).D_decay,
                    "v_bar": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).v_bar,
                    "A": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).A,
                    "C": INITIAL_FINGERPRINTS.get(mid, CapabilityFingerprint(0,0,0,0)).C,
                },
                "final": {
                    "D_decay": round(fp.D_decay, 4),
                    "v_bar": round(fp.v_bar, 4),
                    "A": round(fp.A, 4),
                    "C": round(fp.C, 4),
                },
            }
            for mid, fp in mgr._live_fingerprints.items()
        },
        "round_results": [
            {
                "round": rr.round_idx,
                "state": rr.state,
                "kappa": round(rr.convergence_metric, 4),
                "mu": round(rr.marginal_value, 4),
                "converged": rr.converged,
                "stop": rr.stop,
                "findings_count": len(rr.findings),
                "active_models": sorted(rr.active_models),
            }
            for rr in mgr.round_results
        ],
        "event_log": [
            {
                "type": e.event_type.value,
                "model": e.model_id,
                "round": e.round_idx,
                "detail": e.detail,
                "timestamp": e.timestamp,
            }
            for e in events
        ],
    }

    report_path = LOGS_DIR / "experiment_12_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    _log(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "preflight":
        source_env()
        from experiment_11_orchestrator import run_preflight
        config = load_default_config()
        config.logs_dir = LOGS_DIR
        config.logs_dir.mkdir(parents=True, exist_ok=True)
        results = run_preflight(config)
        all_pass = all(
            r["identity_pass"] and r["compliance_pass"]
            for r in results.values()
        )
        sys.exit(0 if all_pass else 1)

    elif mode in ("blind", "full"):
        run_full_experiment()

    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python3 run_exp12_live_wire.py [preflight|blind|full]")
        sys.exit(1)
