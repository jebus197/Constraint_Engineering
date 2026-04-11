#!/usr/bin/env python3
"""Confer Round 3: review implemented contextual decision logic.

Round 1 reviewed 14 bug fixes — both models confirmed mechanical fixes,
flagged 4 judgment-call fixes as needing contextual logic.
Round 2 asked CX and GE to design the contextual versions.
Round 3 reviews the actual implementations under FFF.

Scoped tightly: 4 contextual implementations only, with the code as written.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runner_core import source_env
from experiment_11_orchestrator import call_openrouter, call_gemini

REPO_ROOT = Path(__file__).resolve().parent.parent
CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core.txt"
LOGS_DIR = REPO_ROOT / "bench" / "logs"

CONTEXTUAL_IMPLEMENTATIONS = r"""
=== IMPLEMENTATION 1: F8 — Contextual Merge Quorum ===

Design origin: Composed from CX Round 2 (target consensus) + GE Round 2 (small-panel).
Founder directive: single-model merge on small panel must be HIL-flagged.

Code (reference_runner.py, _update_finding_statuses):

```python
# ── MERGE: contextual quorum (Round 2 confer design) ──
# Floor: never merge without target consensus. Never merge on 0 votes.
# Contextual: 2+ models on same target = pass. 1 model on small panel
# with high confidence = pass + HIL flag. Target disagreement = defer.
merge_verdicts = [v for v in entry["verdicts"] if v["verdict"] == "MERGE"]
if merge_verdicts:
    # Extract per-vote targets
    by_target: dict[str, list] = {}
    for v in merge_verdicts:
        m = re.search(r'merged_into=(C\d{4,})', v.get("evidence", ""))
        target = m.group(1) if m else "__unknown__"
        by_target.setdefault(target, []).append(v)

    if len(by_target) > 1:
        # Target disagreement — defer, do not merge
        _log(f"  MERGE DEFERRED {canonical_id}: target disagreement "
             f"({', '.join(by_target.keys())})")
    else:
        target_id = next(iter(by_target))
        target_votes = by_target[target_id]
        distinct_models = {v["model"] for v in target_votes}
        available_external = {v["model"] for v in entry["verdicts"]} - {entry["source_model"]}

        if len(distinct_models) >= 2:
            # Clear consensus — merge
            merged_into = target_id if target_id != "__unknown__" else None
            registry.resolve(canonical_id, "MERGED", round_idx, merged_into=merged_into)
            continue
        elif len(available_external) < 2 and len(distinct_models) == 1:
            # Small panel: allow single vote + HIL flag + reversion gate
            merged_into = target_id if target_id != "__unknown__" else None
            registry.resolve(canonical_id, "MERGED", round_idx, merged_into=merged_into)
            entry["hil_escalated"] = True
            entry["hil_reason"] = (
                f"Single-model merge (small panel, {len(available_external)} "
                f"external models). Reversion available."
            )
            _log(f"  MERGED {canonical_id} (small panel, HIL flagged)")
            continue
        # else: insufficient quorum, do not merge this round
```

Decision logic:
- FLOOR: never merge on 0 votes, never merge with target disagreement
- CONTEXTUAL: 2+ distinct models on same target = merge. 1 model on small panel (<2 external) = merge + HIL flag.
- ESCALATION: target disagreement defers. Full panel with only 1 vote waits for more evidence.

=== IMPLEMENTATION 2: F11 — Severity-Based Confirmation Quorum ===

Design origin: CX Round 2 severity gating + GE Round 2 phase-aware concept (phase-aware deferred — not enough evidence of benefit).

Code (reference_runner.py, _update_finding_statuses):

```python
# F11 contextual: severity-based confirmation quorum.
# Floor: at least 1 independent external confirmation (source excluded).
# Critical/High: require 2. Medium/Low: require 1.
independent_count = len(confirm_models - {entry["source_model"]})
sev = entry.get("severity", 0.5)
required = 2 if sev >= 0.7 else 1  # 0.7 = Critical/High threshold
if independent_count >= required and not unresolved_challenges:
    registry.resolve(canonical_id, "CONFIRMED", round_idx)
```

Decision logic:
- FLOOR: 1 independent external confirmation minimum. Source model always excluded.
- CONTEXTUAL: severity >= 0.7 (critical/high) requires 2 independent external confirmations. Below 0.7 requires 1.
- ESCALATION: unresolved challenges block confirmation regardless of count.

=== IMPLEMENTATION 3: F7/F23 — EXHAUSTED Bypass (GE Design) ===

Design origin: GE Round 2 EXHAUSTED mechanism. CX proposed dynamic threshold — rejected as over-engineered for current evidence.

Code (reference_runner.py, FindingRegistry.open_crit_high_count):

```python
def open_crit_high_count(self, exhausted_round_threshold: int = 0,
                          current_round: int = 0) -> int:
    """Count active non-terminal critical/high findings.

    GE EXHAUSTED mechanism: findings stalled for >= exhausted_round_threshold
    rounds are treated as fully processed and excluded from the count.
    The gate threshold stays fixed; finding eligibility changes.
    """
    _NON_TERMINAL = ("OPEN", "CONTESTED")
    count = 0
    for e in self.entries.values():
        if e["status"] not in _NON_TERMINAL or e["severity"] < 0.7:
            continue
        # EXHAUSTED bypass: stalled findings that have been fully reviewed
        if exhausted_round_threshold > 0 and current_round > 0:
            age = current_round - e.get("last_status_change_round", 0)
            if age >= exhausted_round_threshold:
                e["exhausted"] = True
                continue
        count += 1
    return count
```

Config: `exhausted_round_threshold: int = 8` in RunnerConfig.

Gate call (reference_runner.py, _evaluate_gate_conditions):
```python
open_ch = registry.open_crit_high_count(
    exhausted_round_threshold=cfg.exhausted_round_threshold,
    current_round=round_idx,
)
```

Decision logic:
- FLOOR: gate threshold (max_open_crit_high) stays fixed. Never weakened.
- CONTEXTUAL: findings stalled for >= 8 rounds (no status change) are EXHAUSTED and excluded from the count. They don't block convergence, but the gate's bar isn't lowered for active findings.
- ESCALATION: exhausted findings are marked (e["exhausted"] = True) for post-convergence HIL audit.

=== IMPLEMENTATION 4: F14/F17/F22 — UNCONFIRMED Grace Period + Reopen ===

Design origin: Composed CX Round 2 (grace period) + GE Round 2 (reopen on evidence). CX correctly identified UNCONFIRMED as potentially recoverable, unlike MERGED/CLOSED/REFUTED/DUPLICATE.

Code (reference_runner.py, FindingRegistry.contested_count):

```python
def contested_count(self, current_round: int, grace_period: int = 2) -> int:
    """Count actively contested non-terminal findings.

    Composed CX + GE design:
    - MERGED/CLOSED/REFUTED/DUPLICATE: irrecoverable terminal, always excluded.
    - UNCONFIRMED: recoverable. Included during grace period (awaiting review).
      After grace period, excluded. Reopened if new evidence arrives.
    """
    _IRRECOVERABLE = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE"}
    count = 0
    for e in self.entries.values():
        if e["status"] in _IRRECOVERABLE:
            continue
        # UNCONFIRMED: grace period logic
        if e["status"] == "UNCONFIRMED":
            rounds_in_status = current_round - e.get("last_status_change_round", 0)
            if rounds_in_status < grace_period:
                # Still in grace window — count as contested
                count += 1
            else:
                # Grace expired — check for new evidence since UNCONFIRMED
                status_round = e.get("last_status_change_round", 0)
                new_verdicts = [
                    v for v in e["verdicts"]
                    if v["round"] > status_round
                ]
                if new_verdicts:
                    # New evidence arrived — reopen for review
                    e["status"] = "OPEN"
                    e["last_status_change_round"] = current_round
                    count += 1
                    _log(f"  REOPEN {e.get('canonical_id', '?')}: "
                         f"new evidence after UNCONFIRMED")
            # else: grace expired, no new evidence — excluded
            continue
        # Non-terminal, non-UNCONFIRMED: standard contested logic
        challenges = [v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"]
        if not challenges:
            continue
        confirms = [v for v in e["verdicts"] if v["verdict"] == "CONFIRM"]
        latest_confirm_round = max((v["round"] for v in confirms), default=-1)
        unresolved = [v for v in challenges if v["round"] >= latest_confirm_round]
        if unresolved:
            oldest = min(v["round"] for v in unresolved)
            if current_round - oldest > 1:
                count += 1
    return count
```

Decision logic:
- FLOOR: MERGED/CLOSED/REFUTED/DUPLICATE always excluded. Never counted.
- CONTEXTUAL: UNCONFIRMED findings count as contested during a 2-round grace period (awaiting review). After grace, excluded unless new verdicts arrive post-UNCONFIRMED, which triggers reopen to OPEN.
- ESCALATION: reopened findings re-enter the normal contested evaluation pipeline.
"""

CONFER_PROMPT = """You are reviewing 4 contextual decision mechanisms implemented in the
CDSFL experimental runner (reference_runner.py) on the exp38-experimental branch.

Context: This is Round 3 of a confer series. Round 1 reviewed 14 bug fixes and confirmed
the mechanical fixes but flagged 4 judgment-call fixes (F8, F11, F7/F23, F14/F17/F22)
as using static rules where contextual evidence-based decisions would be better.
Round 2 asked you to design the contextual versions. The implementations below compose
the best elements from both CX and GE Round 2 designs.

Your task: Review these 4 implementations under FFF (Find-Follow-Fix).
For each implementation:
  FIND: Is the implementation correct? Does it match the design intent?
  FOLLOW: Trace consequences. What could break? What interactions exist with
          the other 10 mechanical fixes? Does it affect convergence?
  FIX: If you find a problem, state the minimal correction.

Focus on:
1. FLOOR SAFETY: Is each hard minimum actually enforced? Can it be bypassed?
2. CONTEXTUAL SOUNDNESS: Does the evidence-based rule produce correct decisions?
3. ESCALATION COMPLETENESS: Are ambiguous cases properly handled?
4. INTERACTIONS: Do the 4 contextual mechanisms interact badly with each other
   or with the 10 mechanical fixes from Round 1?
5. CONVERGENCE IMPACT: Could any implementation prevent legitimate convergence
   or allow premature convergence?

Here are the implementations:

""" + CONTEXTUAL_IMPLEMENTATIONS + """

Present your findings as a numbered list. For each finding:
- State what you found (FIND)
- Trace the consequence (FOLLOW)
- State the fix if needed (FIX)
- Mark severity: CRITICAL / HIGH / MEDIUM / LOW

If an implementation is correct and you find no issues, say so briefly and move on.
Do not pad with filler. Be direct.
"""


def main():
    source_env()
    cdsfl = CDSFL_PATH.read_text(encoding="utf-8")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    results = {}

    # --- Codex (CX) via OpenRouter ---
    print(f"[{ts}] Dispatching to Codex (GPT-5.4) via OpenRouter...")
    t0 = time.monotonic()
    try:
        cx_response = call_openrouter(
            model_id="openai/gpt-5.4",
            system_prompt=cdsfl,
            user_prompt=CONFER_PROMPT,
            max_tokens=16384,
            timeout=300,
            max_retries=2,
        )
        cx_elapsed = time.monotonic() - t0
        results["cx"] = {"response": cx_response, "elapsed": cx_elapsed, "error": None}
        print(f"  CX done ({cx_elapsed:.1f}s, {len(cx_response)} chars)")
    except Exception as e:
        cx_elapsed = time.monotonic() - t0
        results["cx"] = {"response": None, "elapsed": cx_elapsed, "error": str(e)}
        print(f"  CX failed ({cx_elapsed:.1f}s): {e}")

    # --- Gemini (GE) via Google GenAI ---
    print(f"  Dispatching to Gemini 3.1 Pro via Google GenAI...")
    t0 = time.monotonic()
    try:
        ge_response = call_gemini(
            model_id="gemini-3.1-pro-preview",
            system_prompt=cdsfl,
            user_prompt=CONFER_PROMPT,
            max_tokens=16384,
            timeout=300,
            max_retries=3,
        )
        ge_elapsed = time.monotonic() - t0
        results["ge"] = {"response": ge_response, "elapsed": ge_elapsed, "error": None}
        print(f"  GE done ({ge_elapsed:.1f}s, {len(ge_response)} chars)")
    except Exception as e:
        ge_elapsed = time.monotonic() - t0
        results["ge"] = {"response": None, "elapsed": ge_elapsed, "error": str(e)}
        print(f"  GE failed ({ge_elapsed:.1f}s): {e}")

    # --- Save results ---
    log_path = LOGS_DIR / f"confer_exp38_contextual_r3_{ts}.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"CDSFL Confer Round 3: Contextual Implementation Review\n")
        f.write(f"Timestamp: {ts}\n")
        f.write(f"Branch: exp38-experimental\n")
        f.write(f"Subject: 4 contextual implementations (F8, F11, F7/F23, F14/F17/F22)\n")
        f.write(f"Models: CX (GPT-5.4), GE (Gemini 3.1 Pro)\n")
        f.write(f"{'='*72}\n\n")

        for label, data in results.items():
            model_name = "Codex GPT-5.4" if label == "cx" else "Gemini 3.1 Pro"
            f.write(f"## {model_name} ({label.upper()})\n")
            f.write(f"Elapsed: {data['elapsed']:.1f}s\n")
            if data["error"]:
                f.write(f"ERROR: {data['error']}\n")
            else:
                f.write(f"Response length: {len(data['response'])} chars\n\n")
                f.write(data["response"])
            f.write(f"\n\n{'='*72}\n\n")

    print(f"\nConfer log saved: {log_path}")

    for label, data in results.items():
        if data["response"]:
            model_name = "Codex GPT-5.4" if label == "cx" else "Gemini 3.1 Pro"
            print(f"\n{'='*72}")
            print(f"  {model_name} ({label.upper()}) — {data['elapsed']:.1f}s")
            print(f"{'='*72}\n")
            print(data["response"])


if __name__ == "__main__":
    main()
