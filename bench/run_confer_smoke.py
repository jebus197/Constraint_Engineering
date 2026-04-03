#!/usr/bin/env python3
"""Conversational confer smoke test: CC2 + Gemini on immune_agents.py.

Instead of building a 300K monolithic prompt, this test gives two models
a task brief and the target file, then lets them converse about findings.
Each model sees the other's response and can agree, disagree, or add new
findings. The immune pipeline runs on each exchange. Convergence when
both models produce zero novel findings in the same round.

This tests whether conversational dispatch produces better results than
the broadcast-and-collect architecture used in Runs 8-10.

Usage:
    python3 bench/run_confer_smoke.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    dispatch,
    save_output,
    _log,
    ModelConfig,
)
from run_exp17_immune import parse_findings
from dynamic_management import Finding

# Try to import immune pipeline — non-fatal if unavailable
try:
    from immune_agents import run_immune_pipeline
    IMMUNE_AVAILABLE = True
except ImportError:
    IMMUNE_AVAILABLE = False
    _log("WARNING: immune_agents not importable, running without pipeline")

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

TARGET_FILE = REPO_ROOT / "bench" / "immune_agents.py"
CDSFL_PATH = (REPO_ROOT / "bench" / "directives" / "universal"
              / "cdsfl_core_formal.md")
LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_smoke_20260403"
MAX_ROUNDS = 8
# Convergence: 2 consecutive rounds where both models produce 0 novel IDs
CONVERGENCE_ZERO_ROUNDS = 2

MODELS = {
    "CC2": ModelConfig(
        label="CC2",
        model_id="opus",
        api="claude_cli",
        role="participant",
        system_prompt_path=str(CDSFL_PATH),
        max_tokens=32768,
        timeout=300,
        max_retries=3,
    ),
    "Gemini": ModelConfig(
        label="Gemini",
        model_id="gemini-3.1-pro-preview",
        api="google",
        role="participant",
        system_prompt_path=str(CDSFL_PATH),
        max_tokens=32768,
        timeout=300,
        max_retries=5,
        backoff_base=3.0,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Prompt construction
# ─────────────────────────────────────────────────────────────────────────────

FINDING_FORMAT = (
    "For each finding use this format:\n"
    "  FINDING_ID: IM_F001 (increment per finding)\n"
    "  SEVERITY: 0.0-1.0\n"
    "  FLAW_CLASS: 1=logic, 2=interface, 3=notation, 4=completeness, "
    "5=correctness, 6=edge-case, 7=performance, 8=documentation\n"
    "  DESCRIPTION: what is wrong and why\n"
    "  PROPOSED_FIX: specific fix with code\n"
    "  VERIFIED: TRUE/FALSE\n\n"
)

def build_initial_prompt(file_text: str) -> str:
    """Build the first-round task brief.

    Key design: the file is included but with an explicit sequential
    read instruction. The model is told to read from top to bottom
    before starting analysis.
    """
    return (
        "You are a code reviewer working with a colleague on a Python "
        "module called immune_agents.py. This file implements a 6-cell "
        "immune agent pipeline for automated code review verification.\n\n"
        "Read the file below carefully from start to finish, top to "
        "bottom. Do not try to absorb everything at once. Build your "
        "understanding of each cell before moving to the next.\n\n"
        "After you've read it, share what you notice — bugs, design "
        "issues, edge cases, anything that looks wrong or fragile. "
        "Think of this as talking to a colleague: 'Hey, look at line X "
        "— this looks like it would crash because...' Your colleague "
        "will respond with their own observations, and you'll discuss "
        "back and forth until you both agree on what's real and what "
        "isn't.\n\n"
        "Be specific. Cite lines, quote code, trace consequences. "
        "Don't pad with minor style issues — focus on things that would "
        "actually break or produce wrong results.\n\n"
        "When you identify something concrete, format it as:\n"
        + FINDING_FORMAT
        + "=== FILE: bench/immune_agents.py ===\n\n"
        + file_text
        + "\n\n=== END FILE ===\n\n"
        "What do you see?"
    )


def build_response_prompt(
    own_label: str,
    other_label: str,
    other_response: str,
    round_idx: int,
    prior_findings_summary: str,
) -> str:
    """Build a conversational follow-up prompt.

    The model sees what the other model found and responds naturally.
    """
    return (
        f"Your colleague {other_label} has been looking at the same "
        f"file. Here's what they said:\n\n"
        f"---\n\n"
        f"{other_response}\n\n"
        f"---\n\n"
        f"Respond naturally. If they found something you missed, say "
        f"so. If you think they're wrong about something, explain why "
        f"— cite the code. If their observation reminds you of "
        f"something else you noticed, follow that thread.\n\n"
        f"If you have new findings, use the standard format:\n"
        + FINDING_FORMAT
        + f"Your own previous observations for reference:\n"
        f"{prior_findings_summary}\n\n"
        f"What's your response?"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Finding tracking
# ─────────────────────────────────────────────────────────────────────────────

def summarise_findings(findings: List[Finding]) -> str:
    """Build a compact summary of findings for context."""
    if not findings:
        return "(no findings yet)"
    lines = []
    for f in findings:
        lines.append(
            f"  {f.finding_id} (sev={f.severity:.2f}): "
            f"{f.description[:100]}..."
        )
    return "\n".join(lines)


def count_novel_ids(
    new_findings: List[Finding],
    seen_ids: set,
) -> int:
    """Count findings with IDs not seen before."""
    novel = 0
    for f in new_findings:
        if f.finding_id and f.finding_id not in seen_ids:
            seen_ids.add(f.finding_id)
            novel += 1
    return novel


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

def run_smoke_test():
    """Run the conversational confer smoke test."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load file and CDSFL
    file_text = TARGET_FILE.read_text(encoding="utf-8")
    cdsfl_text = CDSFL_PATH.read_text(encoding="utf-8")

    _log("=" * 60)
    _log("CONVERSATIONAL CONFER SMOKE TEST")
    _log(f"  Models: CC2, Gemini")
    _log(f"  Target: immune_agents.py ({len(file_text):,} chars)")
    _log(f"  Max rounds: {MAX_ROUNDS}")
    _log(f"  Convergence: {CONVERGENCE_ZERO_ROUNDS} consecutive "
         f"zero-novel rounds from both models")
    _log(f"  Logs: {LOGS_DIR}")
    _log("=" * 60)

    all_findings: Dict[str, List[Finding]] = {"CC2": [], "Gemini": []}
    seen_ids: set = set()
    responses: Dict[str, str] = {"CC2": "", "Gemini": ""}
    novel_per_round: List[Dict[str, int]] = []
    zero_novel_streak = 0
    experiment_start = time.monotonic()

    for round_idx in range(MAX_ROUNDS):
        round_start = time.monotonic()
        _log(f"\n{'─' * 60}")
        _log(f"Round {round_idx}")
        _log(f"{'─' * 60}")

        round_novel = {}

        if round_idx == 0:
            # Round 0: both models get the file independently
            prompt = build_initial_prompt(file_text)
            _log(f"  Initial prompt: {len(prompt):,} chars")

            for label in ["CC2", "Gemini"]:
                mc = MODELS[label]
                try:
                    start = time.monotonic()
                    text = dispatch(mc, prompt, cdsfl_text)
                    elapsed = time.monotonic() - start
                    _log(f"  {label}: {len(text):,} chars, {elapsed:.1f}s")

                    _log(f"\n{'─' * 30} {label} {'─' * 30}")
                    _log(text[:2000] + ("..." if len(text) > 2000 else ""))
                    _log(f"{'─' * 30} /{label} {'─' * 30}\n")

                    findings = parse_findings(label, round_idx, text)
                    all_findings[label].extend(findings)
                    responses[label] = text
                    novel = count_novel_ids(findings, seen_ids)
                    round_novel[label] = novel
                    _log(f"  {label}: {len(findings)} findings, "
                         f"{novel} novel")

                    save_output(
                        LOGS_DIR, f"r{round_idx}", label,
                        prompt[:200] + "...", text,
                        metadata={
                            "round": round_idx,
                            "elapsed": round(elapsed, 1),
                            "findings": len(findings),
                            "novel": novel,
                        })

                except Exception as e:
                    _log(f"  {label}: ERROR — {type(e).__name__}: {e}")
                    round_novel[label] = 0

        else:
            # Rounds 1+: each model sees the other's last response
            for label, other_label in [("CC2", "Gemini"),
                                        ("Gemini", "CC2")]:
                mc = MODELS[label]
                prior_summary = summarise_findings(all_findings[label])

                prompt = build_response_prompt(
                    own_label=label,
                    other_label=other_label,
                    other_response=responses[other_label],
                    round_idx=round_idx,
                    prior_findings_summary=prior_summary,
                )
                _log(f"  {label} prompt: {len(prompt):,} chars "
                     f"(includes {other_label}'s response)")

                try:
                    start = time.monotonic()
                    text = dispatch(mc, prompt, cdsfl_text)
                    elapsed = time.monotonic() - start
                    _log(f"  {label}: {len(text):,} chars, {elapsed:.1f}s")

                    _log(f"\n{'─' * 30} {label} {'─' * 30}")
                    _log(text[:2000] + ("..." if len(text) > 2000 else ""))
                    _log(f"{'─' * 30} /{label} {'─' * 30}\n")

                    findings = parse_findings(label, round_idx, text)
                    all_findings[label].extend(findings)
                    responses[label] = text
                    novel = count_novel_ids(findings, seen_ids)
                    round_novel[label] = novel
                    _log(f"  {label}: {len(findings)} findings, "
                         f"{novel} novel")

                    save_output(
                        LOGS_DIR, f"r{round_idx}", label,
                        prompt[:200] + "...", text,
                        metadata={
                            "round": round_idx,
                            "elapsed": round(elapsed, 1),
                            "findings": len(findings),
                            "novel": novel,
                        })

                except Exception as e:
                    _log(f"  {label}: ERROR — {type(e).__name__}: {e}")
                    round_novel[label] = 0

        novel_per_round.append(round_novel)
        total_novel = sum(round_novel.values())
        round_elapsed = time.monotonic() - round_start

        # Run immune pipeline on this round's findings
        round_findings = []
        for label in ["CC2", "Gemini"]:
            n = round_novel.get(label, 0)
            # Get the last N findings from this model (the new ones)
            recent = all_findings[label][-max(1, len(
                parse_findings(label, round_idx, responses[label]))):]
            round_findings.extend(recent)

        immune_summary = ""
        if IMMUNE_AVAILABLE and round_findings:
            try:
                # Collect prior findings (everything before this round)
                prior = []
                for label in ["CC2", "Gemini"]:
                    prior.extend(all_findings[label][:-len(
                        parse_findings(label, round_idx,
                                       responses.get(label, ""))
                    ) or len(all_findings[label])])

                result = run_immune_pipeline(
                    new_findings=round_findings,
                    prior_findings=prior,
                    source_paths=[str(TARGET_FILE)],
                )
                rejection_rate = sum(
                    1 for v in result.final_verdicts.values()
                    if v in ("REJECTED", "DUPLICATE")
                ) / max(len(result.final_verdicts), 1)
                immune_summary = (
                    f"Immune: {rejection_rate:.0%} rejection, "
                    f"autoimmune={result.autoimmune_flag}"
                )
                _log(f"  {immune_summary}")
            except Exception as e:
                _log(f"  Immune pipeline error: {e}")

        _log(f"\n  Round {round_idx} summary: "
             f"{total_novel} novel findings, {round_elapsed:.1f}s")
        for label in ["CC2", "Gemini"]:
            _log(f"    {label}: {round_novel.get(label, 0)} novel")

        # Convergence check
        if total_novel == 0:
            zero_novel_streak += 1
            _log(f"  Zero-novel streak: {zero_novel_streak}/"
                 f"{CONVERGENCE_ZERO_ROUNDS}")
        else:
            zero_novel_streak = 0

        if zero_novel_streak >= CONVERGENCE_ZERO_ROUNDS:
            _log(f"\n  CONVERGED at round {round_idx} "
                 f"({CONVERGENCE_ZERO_ROUNDS} consecutive zero-novel)")
            break

    # ─────────────────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────────────────
    total_elapsed = time.monotonic() - experiment_start
    total_findings = sum(len(v) for v in all_findings.values())

    _log(f"\n{'=' * 60}")
    _log(f"CONVERSATIONAL CONFER SMOKE TEST — COMPLETE")
    _log(f"  Rounds: {len(novel_per_round)}")
    _log(f"  Total findings: {total_findings}")
    _log(f"  Unique IDs: {len(seen_ids)}")
    _log(f"  CC2: {len(all_findings['CC2'])} findings")
    _log(f"  Gemini: {len(all_findings['Gemini'])} findings")
    _log(f"  Novel per round: {[sum(r.values()) for r in novel_per_round]}")
    _log(f"  Elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    if total_findings > 0:
        churn = 1 - len(seen_ids) / total_findings
        _log(f"  Churn: {churn:.1%}")
    _log(f"{'=' * 60}")

    # Save report
    report = {
        "experiment": "conversational_confer_smoke",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_file": str(TARGET_FILE),
        "target_chars": len(file_text),
        "models": ["CC2", "Gemini"],
        "rounds": len(novel_per_round),
        "total_findings": total_findings,
        "unique_ids": len(seen_ids),
        "churn_rate": 1 - len(seen_ids) / max(total_findings, 1),
        "novel_per_round": [sum(r.values()) for r in novel_per_round],
        "novel_detail": novel_per_round,
        "per_model": {
            k: len(v) for k, v in all_findings.items()
        },
        "elapsed_s": round(total_elapsed, 1),
        "converged": zero_novel_streak >= CONVERGENCE_ZERO_ROUNDS,
    }
    report_path = LOGS_DIR / "smoke_test_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _log(f"  Report: {report_path}")


if __name__ == "__main__":
    run_smoke_test()
