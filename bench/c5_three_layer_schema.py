#!/usr/bin/env python3
"""C5 Experiment: Three-Layer Schema Validation.

Tests the hypothesis that full continued conversation + CDSFL constraints
+ Meta structured prompting produces >= 30 verified findings, combining
C1's cross-component breadth with C4's formal depth.

Three-layer schema:
  Layer 1 — Meta structured prompting (reasoning format)
  Layer 2 — CDSFL constraints (FFF, falsification, classification)
  Layer 3 — Full conversational mode (ITC is fallback only)

Usage:
    python3 bench/c5_three_layer_schema.py [--dry-run]

Outputs:
    bench/logs/c5_<timestamp>/   — round-by-round transcripts + results JSON
    experimental_notes/          — results markdown (manual post-processing)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Path setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from c5_prompts import (
    SYSTEM_INSTRUCTION,
    round_1_prompt,
    round_2_prompt,
    round_3_prompt,
    round_4_prompt,
    round_5_prompt,
    round_6_prompt,
    round_7_prompt,
    round_8_prompt,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_ID = "gemini-3.1-pro-preview"
MAX_OUTPUT_TOKENS = 32768
TIMEOUT_S = 300
MAX_RETRIES = 5
BACKOFF_BASE = 3.0

# Code artifact — pre-v2, same as C1/C3/C4
CODE_COMMIT = "927bfbc"

# Master Finding Registry for R3/R4 injection
REGISTRY_PATH = (
    REPO_ROOT / "experimental_notes" / "Master_Finding_Registry_2026-04-04.md"
)

# ITC trigger thresholds
ITC_REPETITION_THRESHOLD = 0.40  # >40% repeated content triggers ITC
ITC_MIN_RESPONSE_CHARS = 500     # <500 chars on substantive round triggers ITC
ITC_MAX_ZERO_NOVEL_ROUNDS = 3    # 3 consecutive zero-novel rounds triggers ITC


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def source_env() -> None:
    """Load .env from repo root into os.environ."""
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()


# ---------------------------------------------------------------------------
# Code artifact loading
# ---------------------------------------------------------------------------

def load_code_artifact() -> str:
    """Load immune_agents.py at the target commit via git show."""
    result = subprocess.run(
        ["git", "show", f"{CODE_COMMIT}:bench/immune_agents.py"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to load code artifact at commit {CODE_COMMIT}: "
            f"{result.stderr.strip()}"
        )
    code = result.stdout
    _log(f"Loaded code artifact: {len(code)} chars from commit {CODE_COMMIT}")
    return code


# ---------------------------------------------------------------------------
# Master Finding Registry parsing
# ---------------------------------------------------------------------------

def parse_registry() -> Tuple[str, str]:
    """Parse the Master Finding Registry into two batches for R3/R4.

    Returns (batch_1_text, batch_2_text) where batch 1 = MF-01..MF-20
    and batch 2 = MF-21..MF-40.
    """
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Registry not found: {REGISTRY_PATH}")

    text = REGISTRY_PATH.read_text()
    lines = text.splitlines()

    # Find all ### MF-XX headers and split
    finding_starts: List[int] = []
    for i, line in enumerate(lines):
        if re.match(r"^###\s+MF-\d+:", line):
            finding_starts.append(i)

    if len(finding_starts) < 40:
        _log(
            f"WARNING: Expected 40 findings, found {len(finding_starts)} "
            f"headers in registry"
        )

    # Split at MF-21 boundary
    split_idx = None
    for i, start in enumerate(finding_starts):
        if "MF-21:" in lines[start]:
            split_idx = start
            break

    if split_idx is None:
        # Fallback: split at midpoint
        mid = len(finding_starts) // 2
        split_idx = finding_starts[mid]
        _log(f"WARNING: Could not find MF-21 header, splitting at finding {mid}")

    # Build batch texts — strip markdown formatting for cleaner injection
    batch_1_lines = lines[finding_starts[0]:split_idx]
    batch_2_lines = lines[split_idx:]

    # Strip trailing summary section from batch 2
    summary_idx = None
    for i, line in enumerate(batch_2_lines):
        if line.startswith("## SUMMARY") or line.startswith("## Summary"):
            summary_idx = i
            break
    if summary_idx is not None:
        batch_2_lines = batch_2_lines[:summary_idx]

    batch_1 = "\n".join(batch_1_lines).strip()
    batch_2 = "\n".join(batch_2_lines).strip()

    _log(f"Registry parsed: batch 1 = {len(batch_1)} chars, "
         f"batch 2 = {len(batch_2)} chars")
    return batch_1, batch_2


# ---------------------------------------------------------------------------
# ITC degradation monitoring
# ---------------------------------------------------------------------------

def check_itc_triggers(
    round_num: int,
    response_text: str,
    prior_responses: List[str],
    zero_novel_streak: int,
) -> Tuple[bool, str]:
    """Check whether ITC fallback should be triggered.

    Returns (triggered: bool, reason: str).
    """
    # Check 1: Response too short for substantive round
    if round_num <= 7 and len(response_text) < ITC_MIN_RESPONSE_CHARS:
        return True, (
            f"Thin response: {len(response_text)} chars "
            f"(threshold: {ITC_MIN_RESPONSE_CHARS})"
        )

    # Check 2: Repetition rate against prior responses
    if prior_responses:
        # Simple n-gram overlap as repetition proxy
        response_sentences = set(
            s.strip().lower()
            for s in re.split(r'[.!?]\s+', response_text)
            if len(s.strip()) > 20
        )
        if response_sentences:
            prior_sentences = set()
            for pr in prior_responses:
                for s in re.split(r'[.!?]\s+', pr):
                    if len(s.strip()) > 20:
                        prior_sentences.add(s.strip().lower())

            if prior_sentences:
                overlap = len(response_sentences & prior_sentences)
                rate = overlap / len(response_sentences)
                if rate > ITC_REPETITION_THRESHOLD:
                    return True, (
                        f"Repetition rate: {rate:.1%} "
                        f"(threshold: {ITC_REPETITION_THRESHOLD:.0%})"
                    )

    # Check 3: Hallucination signals — references to non-existent functions
    hallucination_patterns = [
        r'\bdef\s+\w+_v3\b',           # v3 functions don't exist
        r'\bclass\s+\w+V3\b',          # v3 classes don't exist
        r'line\s+\d{5,}',              # line numbers > 9999 (code is 1309 lines)
    ]
    for pat in hallucination_patterns:
        if re.search(pat, response_text):
            return True, f"Possible hallucination: matched pattern {pat!r}"

    # Check 4: Zero-novel streak
    if zero_novel_streak >= ITC_MAX_ZERO_NOVEL_ROUNDS:
        return True, (
            f"Zero novel findings for {zero_novel_streak} consecutive rounds"
        )

    return False, ""


# ---------------------------------------------------------------------------
# Gemini multi-turn conversation
# ---------------------------------------------------------------------------

def create_gemini_chat():
    """Create a Gemini chat session with CDSFL system instruction.

    Returns (client, chat) — caller must keep a reference to client,
    otherwise GC closes its internal httpx connection pool and the
    chat's send_message() fails with 'client has been closed'.
    """
    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        raise RuntimeError(
            "google-genai package not installed: pip install google-genai"
        )

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)

    config = genai_types.GenerateContentConfig(
        max_output_tokens=MAX_OUTPUT_TOKENS,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    chat = client.chats.create(model=MODEL_ID, config=config)
    _log(f"Chat session created: model={MODEL_ID}")
    return client, chat


def send_round(
    chat,
    round_num: int,
    prompt: str,
    logs_dir: Path,
) -> Tuple[str, float, int]:
    """Send a round prompt and return (response_text, elapsed_s, chars).

    Includes retry logic matching the existing call_gemini pattern.
    """
    _log(f"R{round_num}: Sending prompt ({len(prompt)} chars)...")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            _log(f"  R{round_num}: retry {attempt}/{MAX_RETRIES}")
        t0 = time.monotonic()
        try:
            response = chat.send_message(prompt)
            elapsed = time.monotonic() - t0

            if response.text is not None:
                text = response.text.strip()
                _log(
                    f"  R{round_num}: done ({elapsed:.1f}s, {len(text)} chars)"
                )

                # Save round transcript
                round_file = logs_dir / f"r{round_num}_transcript.txt"
                round_file.write_text(
                    f"=== ROUND {round_num} ===\n"
                    f"Prompt ({len(prompt)} chars):\n{prompt}\n\n"
                    f"=== RESPONSE ({len(text)} chars, {elapsed:.1f}s) ===\n"
                    f"{text}\n"
                )
                return text, elapsed, len(text)

            reason = "unknown"
            if response.candidates:
                reason = str(response.candidates[0].finish_reason)
            raise RuntimeError(
                f"Response text is None, finish_reason={reason}"
            )

        except Exception as e:
            elapsed = time.monotonic() - t0
            last_error = e
            _log(
                f"  R{round_num}: attempt {attempt} failed "
                f"({elapsed:.1f}s): {str(e)[:120]}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_BASE)

    raise RuntimeError(
        f"R{round_num} failed after {MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
    )


# ---------------------------------------------------------------------------
# Finding extraction (lightweight — full verification is in c5_verify.py)
# ---------------------------------------------------------------------------

def count_finding_ids(text: str) -> int:
    """Count C5-XX style finding IDs in a response."""
    return len(set(re.findall(r'C5-\d+', text)))


def estimate_novel_findings(text: str, prior_responses: List[str]) -> int:
    """Rough estimate of novel content in a response.

    Counts sentences that don't appear in any prior response.
    """
    current = set(
        s.strip().lower()
        for s in re.split(r'[.!?]\s+', text)
        if len(s.strip()) > 30
    )
    if not current:
        return 0

    prior = set()
    for pr in prior_responses:
        for s in re.split(r'[.!?]\s+', pr):
            if len(s.strip()) > 30:
                prior.add(s.strip().lower())

    novel = current - prior
    return len(novel)


# ---------------------------------------------------------------------------
# Main experiment loop
# ---------------------------------------------------------------------------

def run_c5(dry_run: bool = False) -> Dict[str, Any]:
    """Execute the C5 three-layer schema experiment."""

    # Setup
    source_env()
    code_artifact = load_code_artifact()
    batch_1, batch_2 = parse_registry()

    # Create output directory
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logs_dir = REPO_ROOT / "bench" / "logs" / f"c5_{ts}"
    logs_dir.mkdir(parents=True, exist_ok=True)
    _log(f"Logs directory: {logs_dir}")

    # Save experiment metadata
    metadata = {
        "experiment": "C5",
        "description": "Three-Layer Schema Validation",
        "model": MODEL_ID,
        "code_commit": CODE_COMMIT,
        "code_chars": len(code_artifact),
        "registry_findings": 40,
        "batch_1_chars": len(batch_1),
        "batch_2_chars": len(batch_2),
        "start_time": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
    }
    (logs_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )

    if dry_run:
        _log("DRY RUN — prompts will be generated but not sent")
        prompts = {
            "R1": round_1_prompt(code_artifact),
            "R2": round_2_prompt(0),
            "R3": round_3_prompt(batch_1),
            "R4": round_4_prompt(batch_2),
            "R5": round_5_prompt(),
            "R6": round_6_prompt(),
            "R7": round_7_prompt(),
            "R8": round_8_prompt(),
        }
        for name, prompt in prompts.items():
            _log(f"  {name}: {len(prompt)} chars")
            (logs_dir / f"{name.lower()}_prompt.txt").write_text(prompt)
        _log("Dry run complete. Prompts saved to logs directory.")
        return {"status": "dry_run", "logs_dir": str(logs_dir)}

    # Create chat session — keep client ref alive to prevent GC
    _gemini_client, chat = create_gemini_chat()

    # Tracking state
    responses: List[str] = []
    timings: Dict[str, float] = {}
    char_counts: Dict[str, int] = {}
    itc_triggered = False
    itc_reason = ""
    zero_novel_streak = 0
    experiment_start = time.monotonic()

    # ── Round 1: Structured Certificate Review ──────────────────────────
    _log("=" * 60)
    _log("PHASE 1: INDEPENDENT DISCOVERY")
    _log("=" * 60)

    r1_prompt = round_1_prompt(code_artifact)
    r1_text, r1_time, r1_chars = send_round(chat, 1, r1_prompt, logs_dir)
    responses.append(r1_text)
    timings["R1"] = r1_time
    char_counts["R1"] = r1_chars

    # Check ITC
    triggered, reason = check_itc_triggers(1, r1_text, [], zero_novel_streak)
    if triggered:
        itc_triggered = True
        itc_reason = f"R1: {reason}"
        _log(f"ITC TRIGGERED at R1: {reason}")

    # Count findings for R2 prompt
    r1_finding_count = count_finding_ids(r1_text)
    if r1_finding_count == 0:
        # Fallback: count numbered items
        r1_finding_count = len(re.findall(r'^\s*\d+\.', r1_text, re.MULTILINE))
    _log(f"R1 finding count estimate: {r1_finding_count}")

    # ── Round 2: FFF Press Harder ───────────────────────────────────────
    if not itc_triggered:
        r2_prompt = round_2_prompt(r1_finding_count)
        r2_text, r2_time, r2_chars = send_round(chat, 2, r2_prompt, logs_dir)
        responses.append(r2_text)
        timings["R2"] = r2_time
        char_counts["R2"] = r2_chars

        novel = estimate_novel_findings(r2_text, responses[:-1])
        zero_novel_streak = 0 if novel > 0 else zero_novel_streak + 1

        triggered, reason = check_itc_triggers(
            2, r2_text, responses[:-1], zero_novel_streak
        )
        if triggered:
            itc_triggered = True
            itc_reason = f"R2: {reason}"
            _log(f"ITC TRIGGERED at R2: {reason}")

    # ── Round 3: Prior Findings Batch 1 ─────────────────────────────────
    _log("=" * 60)
    _log("PHASE 2: PRIOR FINDINGS INJECTION")
    _log("=" * 60)

    if not itc_triggered:
        r3_prompt = round_3_prompt(batch_1)
        r3_text, r3_time, r3_chars = send_round(chat, 3, r3_prompt, logs_dir)
        responses.append(r3_text)
        timings["R3"] = r3_time
        char_counts["R3"] = r3_chars

        novel = estimate_novel_findings(r3_text, responses[:-1])
        zero_novel_streak = 0 if novel > 0 else zero_novel_streak + 1

        triggered, reason = check_itc_triggers(
            3, r3_text, responses[:-1], zero_novel_streak
        )
        if triggered:
            itc_triggered = True
            itc_reason = f"R3: {reason}"
            _log(f"ITC TRIGGERED at R3: {reason}")

    # ── Round 4: Prior Findings Batch 2 ─────────────────────────────────
    if not itc_triggered:
        r4_prompt = round_4_prompt(batch_2)
        r4_text, r4_time, r4_chars = send_round(chat, 4, r4_prompt, logs_dir)
        responses.append(r4_text)
        timings["R4"] = r4_time
        char_counts["R4"] = r4_chars

        novel = estimate_novel_findings(r4_text, responses[:-1])
        zero_novel_streak = 0 if novel > 0 else zero_novel_streak + 1

        triggered, reason = check_itc_triggers(
            4, r4_text, responses[:-1], zero_novel_streak
        )
        if triggered:
            itc_triggered = True
            itc_reason = f"R4: {reason}"
            _log(f"ITC TRIGGERED at R4: {reason}")

    # ── Round 5: Cross-Component Probe ──────────────────────────────────
    _log("=" * 60)
    _log("PHASE 3: SYNTHESIS AND FALSIFICATION")
    _log("=" * 60)

    if not itc_triggered:
        r5_prompt = round_5_prompt()
        r5_text, r5_time, r5_chars = send_round(chat, 5, r5_prompt, logs_dir)
        responses.append(r5_text)
        timings["R5"] = r5_time
        char_counts["R5"] = r5_chars

        novel = estimate_novel_findings(r5_text, responses[:-1])
        zero_novel_streak = 0 if novel > 0 else zero_novel_streak + 1

        triggered, reason = check_itc_triggers(
            5, r5_text, responses[:-1], zero_novel_streak
        )
        if triggered:
            itc_triggered = True
            itc_reason = f"R5: {reason}"
            _log(f"ITC TRIGGERED at R5: {reason}")

    # ── Round 6: Self-Falsification ─────────────────────────────────────
    if not itc_triggered:
        r6_prompt = round_6_prompt()
        r6_text, r6_time, r6_chars = send_round(chat, 6, r6_prompt, logs_dir)
        responses.append(r6_text)
        timings["R6"] = r6_time
        char_counts["R6"] = r6_chars

        triggered, reason = check_itc_triggers(
            6, r6_text, responses[:-1], zero_novel_streak
        )
        if triggered:
            itc_triggered = True
            itc_reason = f"R6: {reason}"
            _log(f"ITC TRIGGERED at R6: {reason}")

    # ── Round 7: Novel Discovery Sweep ──────────────────────────────────
    if not itc_triggered:
        r7_prompt = round_7_prompt()
        r7_text, r7_time, r7_chars = send_round(chat, 7, r7_prompt, logs_dir)
        responses.append(r7_text)
        timings["R7"] = r7_time
        char_counts["R7"] = r7_chars

        novel = estimate_novel_findings(r7_text, responses[:-1])
        zero_novel_streak = 0 if novel > 0 else zero_novel_streak + 1

    # ── Round 8: Final Summary Certificate ──────────────────────────────
    if not itc_triggered:
        r8_prompt = round_8_prompt()
        r8_text, r8_time, r8_chars = send_round(chat, 8, r8_prompt, logs_dir)
        responses.append(r8_text)
        timings["R8"] = r8_time
        char_counts["R8"] = r8_chars

    # ── Results ─────────────────────────────────────────────────────────
    experiment_elapsed = time.monotonic() - experiment_start
    total_output_chars = sum(char_counts.values())
    rounds_completed = len(responses)

    results = {
        "experiment": "C5",
        "model": MODEL_ID,
        "code_commit": CODE_COMMIT,
        "start_time": metadata["start_time"],
        "end_time": datetime.now(timezone.utc).isoformat(),
        "total_elapsed_s": round(experiment_elapsed, 1),
        "rounds_completed": rounds_completed,
        "total_output_chars": total_output_chars,
        "per_round_timing": timings,
        "per_round_chars": char_counts,
        "itc_triggered": itc_triggered,
        "itc_reason": itc_reason,
        "itc_before_r5": itc_triggered and rounds_completed < 5,
    }

    # Save results
    (logs_dir / "results.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )

    # Save full transcript
    transcript_lines = []
    for i, resp in enumerate(responses, 1):
        transcript_lines.append(f"{'=' * 60}")
        transcript_lines.append(f"ROUND {i}")
        transcript_lines.append(f"Time: {timings.get(f'R{i}', 0):.1f}s")
        transcript_lines.append(f"Chars: {char_counts.get(f'R{i}', 0)}")
        transcript_lines.append(f"{'=' * 60}")
        transcript_lines.append(resp)
        transcript_lines.append("")

    (logs_dir / "full_transcript.txt").write_text(
        "\n".join(transcript_lines)
    )

    # Print summary
    _log("=" * 60)
    _log("C5 EXPERIMENT COMPLETE")
    _log("=" * 60)
    _log(f"Rounds completed: {rounds_completed}/8")
    _log(f"Total time: {experiment_elapsed:.1f}s ({experiment_elapsed/60:.1f} min)")
    _log(f"Total output: {total_output_chars} chars")
    for rnd in sorted(timings.keys()):
        _log(f"  {rnd}: {timings[rnd]:.1f}s, {char_counts[rnd]} chars")
    if itc_triggered:
        _log(f"ITC TRIGGERED: {itc_reason}")
        if rounds_completed < 5:
            _log("FALSIFICATION: ITC before R5 — three-layer schema rejected")
    _log(f"Logs: {logs_dir}")

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    try:
        results = run_c5(dry_run=dry_run)
        if not dry_run:
            _log("\nNext step: run c5_verify.py against the transcript")
            _log(f"  python3 bench/c5_verify.py {results.get('start_time', '')}")
    except KeyboardInterrupt:
        _log("\nExperiment interrupted by user")
        sys.exit(1)
    except Exception as e:
        _log(f"\nExperiment failed: {e}")
        raise
