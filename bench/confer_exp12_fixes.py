#!/usr/bin/env python3
"""Confer with CC2, CX, and Gemini on Experiment 12 detector fixes.

All three models operate under full CDSFL system prompt via the
existing dispatch infrastructure (experiment_11_orchestrator.dispatch).

This is a single-round confer. Each model P-passes the proposed fixes
and returns structured verdicts.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (
    load_default_config,
    dispatch,
    _log,
)

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "experiment_12" / "confer_fixes"

CONFER_PROMPT = """You are participating in a CDSFL confer round. Your task is to P-pass five proposed fixes to the dynamic management layer (bench/dynamic_management.py, 3161 lines) and experiment script (bench/run_exp12_live_wire.py).

These fixes address three bugs discovered during Experiment 12 (first live orchestration test) plus one allocation improvement. The bugs prevented the mathematical convergence and duplicate detection machinery from functioning correctly. The experiment produced 237 genuine findings across 6 rounds but could not detect its own convergence — it terminated on max_rounds instead of on the mathematical termination conditions.

=== FIX 1: Similarity function — cross-class detection ===

PROBLEM: _finding_similarity() returned 0.0 whenever flaw_class integers differed. Models assign different integers to the same concept across rounds (e.g., "convergence detection" might be class 1 from one model and class 4 from another). This made kappa treat every cross-model or cross-round finding as maximally novel, preventing convergence detection.

PROPOSED FIX: When flaw classes differ, use Jaccard similarity on description words alone, with a 0.8x penalty (vs 0.4 base + 0.6*Jaccard when classes match). This means two findings about the same issue but with different class labels still register as similar if their descriptions overlap substantially.

OLD CODE:
```python
def _finding_similarity(f1, f2):
    if f1.flaw_class != f2.flaw_class:
        return 0.0
    words1 = set(f1.description.lower().split())
    words2 = set(f2.description.lower().split())
    jaccard = len(words1 & words2) / len(words1 | words2)
    return 0.4 + 0.6 * jaccard
```

NEW CODE:
```python
def _finding_similarity(f1, f2):
    class_match = f1.flaw_class == f2.flaw_class
    words1 = set(f1.description.lower().split())
    words2 = set(f2.description.lower().split())
    jaccard = len(words1 & words2) / len(words1 | words2)
    if class_match:
        return 0.4 + 0.6 * jaccard
    else:
        return 0.8 * jaccard
```

With tau_sim = 0.8: same-class duplicate detected at Jaccard >= 0.67. Cross-class duplicate detected at Jaccard >= 1.0 (identical descriptions only). Is the 0.8x penalty appropriate? Should it be lower (more permissive) or is this right?

=== FIX 2: D_decay — similarity-based duplicate detection ===

PROBLEM: update_fingerprints() detected duplicates by matching finding_id strings across rounds. Finding IDs are formatted as "{model_id}_{label}" where labels like F001, F002 are generated fresh each round. If a model uses sequential numbering in both rounds, IDs match by coincidence (false positive). If numbering differs, no match (false negative). Either way, D_decay measures label reuse, not content duplication.

PROPOSED FIX: Replace finding_id matching with the same _finding_similarity function used by the convergence detector. A finding is a duplicate if similarity >= tau_sim with any prior finding.

OLD CODE:
```python
prior_finding_ids: Set[str] = set()
for prev_result in self._round_results:
    for f in prev_result.findings:
        prior_finding_ids.add(f.finding_id)
# ...
duplicates = sum(1 for f in model_findings if f.finding_id in prior_finding_ids)
obs_d = duplicates / len(model_findings)
```

NEW CODE:
```python
prior_findings: List[Finding] = []
for prev_result in self._round_results:
    prior_findings.extend(prev_result.findings)
# ...
duplicates = 0
for f in model_findings:
    for pf in prior_findings:
        if _finding_similarity(f, pf) >= self.config.tau_sim:
            duplicates += 1
            break
obs_d = duplicates / len(model_findings)
```

CONCERN: This is O(n*m) where n = current findings, m = all prior findings. With 237 findings after 6 rounds, this is ~237*237 = ~56K comparisons per round. Each comparison is Jaccard on word sets. Is this a performance concern at the scales we operate at (hundreds of findings, not millions)?

=== FIX 3: Parser — case-insensitive, format-tolerant ===

PROBLEM: parse_findings() uses case-sensitive regex (FINDING_ID, SEVERITY, FLAW_CLASS) and requires FLAW_CLASS to be a bare integer. ChatGPT and DeepSeek produce format variations: markdown bold (**FINDING_ID**:), underscores (Finding_ID), text flaw classes ("convergence_detection" instead of "1"). These variations cause findings to be missed or default to flaw_class=1, collapsing the coverage metric.

PROPOSED FIX: Case-insensitive matching with handling for markdown bold markers, underscores/hyphens in field names, and a text-to-integer mapping for flaw class names. Fallback to single unstructured finding if no structured blocks parse.

FLAW_CLASS_MAP includes: convergence→1, failure→2, role→3, load→4, round→5, diminishing→6, interface→7, mathematical→8 (plus common variants like "failure_handling", "convergence detection", etc.)

Is this mapping complete enough? Are there flaw class names models might use that aren't covered?

=== FIX 4: DeepSeek task decomposition ===

PROBLEM: DeepSeek was blocked from all adaptive rounds because the full artifact (3161 lines) plus cumulative findings context exceeds its 32K input window. The feasibility check correctly identified this. But blocking DeepSeek entirely wastes its demonstrated capability for iterative refinement (Experiment 11 characterisation).

PROPOSED FIX: For DeepSeek only, decompose the artifact into components and dispatch one component per round with relevant prior findings for that component only. The dynamic_management.py module has 6 clear areas:
  - Area 1: Role Assignment (~lines 140-700)
  - Area 2: Load Balancing (~lines 700-1100)
  - Area 3: Round Progression / FSM (~lines 1100-1330)
  - Area 4: Convergence Detection (~lines 1330-1700)
  - Area 5: Diminishing Returns (~lines 1700-2050)
  - Area 6: Failure Handling + Manager (~lines 2050-3161)

DeepSeek rotates through these areas across rounds. Each component + focused findings fits within 32K tokens. DeepSeek's findings are integrated into the same convergence/diminishing returns pipeline as all other models.

CONCERN: Does decomposition bias DeepSeek toward surface-level findings within each component while missing cross-component issues? The other models see the full artifact and can find cross-area interactions that DeepSeek cannot. Is this an acceptable trade-off given the alternative (DeepSeek contributing nothing)?

=== FIX 5: Checkpoint/resume wiring ===

PROBLEM: If the experiment crashes mid-round (API timeout, network error), all prior round data is lost. The experiment must restart from scratch.

PROPOSED FIX: Save a checkpoint JSON after each successful model dispatch within a round. Contains: current_round, completed_models, total_findings, timestamp. Resume logic loads checkpoint and skips already-completed dispatches.

This is a straightforward operational improvement. Is there anything about the checkpoint state that would cause incorrect behaviour on resume? (E.g., fingerprint state not being checkpointed, causing the manager to start with initial fingerprints rather than the evolved ones.)

=== YOUR TASK ===

For each fix (1-5), provide:
  ITEM: Fix N
  VERDICT: APPROVE | REJECT | MODIFY
  CONSTRAINT_CLASS: HARD | SOFT
  EVIDENCE: Mathematical or operational justification
  PROPOSED_CHANGE: If MODIFY, what specifically should change
  CONFIDENCE: 0.00 to 1.00

Apply full CDSFL P-pass to each fix. Falsify the fix — find the strongest argument against it, attempt to satisfy that argument, and revise your verdict accordingly. Do not approve reflexively.
"""


def main():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    exp_config = load_default_config()
    cdsfl_text = exp_config.cdsfl_system_prompt

    # Dispatch to CC2, CX, and Gemini only
    target_models = ["CC2", "Codex", "Gemini"]
    results = {}

    for mc in exp_config.models:
        if mc.label not in target_models:
            continue

        _log(f"Dispatching confer to {mc.label}...")
        t0 = time.monotonic()
        try:
            response = dispatch(mc, CONFER_PROMPT, cdsfl_text)
            elapsed = time.monotonic() - t0
            _log(f"  {mc.label}: {len(response)} chars, {elapsed:.1f}s")
            results[mc.label] = {
                "response": response,
                "elapsed": round(elapsed, 1),
                "chars": len(response),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Save individual response
            out_path = LOGS_DIR / f"confer_{mc.label.lower()}.json"
            out_path.write_text(
                json.dumps(results[mc.label], indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            _log(f"  Saved to {out_path.name}")

        except Exception as e:
            elapsed = time.monotonic() - t0
            _log(f"  {mc.label}: FAILED after {elapsed:.1f}s — {e}")
            results[mc.label] = {
                "response": f"DISPATCH_FAILED: {e}",
                "elapsed": round(elapsed, 1),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    # Save consolidated report
    report_path = LOGS_DIR / "confer_report.json"
    report_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _log(f"\nConfer complete. {len([r for r in results.values() if 'error' not in r])}/3 models responded.")
    _log(f"Report: {report_path}")

    # Print responses for inline review
    for label, data in results.items():
        print(f"\n{'='*60}")
        print(f"=== {label} ===")
        print(f"{'='*60}")
        if "error" not in data:
            print(data["response"])
        else:
            print(f"FAILED: {data['error']}")


if __name__ == "__main__":
    main()
