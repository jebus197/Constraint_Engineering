"""Exp 40 post-continuation ARCHITECTURAL confer (2026-05-15).

Compelled-convergence review of the three architectural decisions that
gate Experiment 40 R17–R21 resume and G7 enablement. The local P-pass
(Codex CLI was transiently unavailable mid-tranche) already found and
fixed two issues; this live five-model round is the founder's
go/no-go gate before G7 is switched on at Exp 41.

Questions (ONE converged answer each, no menu — compelled convergence):
  Q1. Is the G7 merge-arbitration design (≥3/5 majority; arbitrate on
      2nd consecutive defer; round-level γ<tiebreaker tie-breaker;
      default-disabled, enable at Exp 41) sound to enable as designed?
  Q2. Is the finding-ID structural rule ^[A-Za-z0-9_]{1,128}$ the
      right hardening, or is the UUID-namespace architectural change
      warranted NOW rather than deferred-on-trigger?
  Q3. Is the runner<->panel "common language" (finding-ID grammar +
      SEARCH/REPLACE fix-block + vote grammar) coherent, and is the
      strengthened-reformat-now / in-round-dispatch-deferred staging
      the correct call?

Panel: Gemini 3.1 Pro, Codex GPT-5.5, CC2 Opus 4.7, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, parallel dispatch, latest CDSFL schema
(cdsfl_core_formal.md) as system prompt.
Logs: bench/logs/confer_exp40_architectural_2026-05-15/.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli,
    call_deepseek,
    call_openrouter,
)

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
            os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_architectural_2026-05-15"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("cc2",      "opus",                          "claude_cli"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# Background artefacts the panel cross-references.
G7_DESIGN = (REPO_ROOT / "experimental_notes"
             / "G7_Merge_Deadlock_Resolution_Design_2026-05-15.md").read_text()
TRANCHE_PM = (REPO_ROOT / "experimental_notes"
              / "Exp40_Fix_Tranche_Postmortem_2026-05-15.md").read_text()
G7_MODULE = (REPO_ROOT / "bench" / "merge_arbitration.py").read_text()

FRAMING = r"""
## Architectural confer framing (load-bearing — read first)

This is a compelled-convergence architectural review run AFTER the
Experiment 40 continuation and its post-mortem fix tranche. Context:

- The continuation produced the G7 merge-deadlock evidence cluster:
  six D4 escalations including a 14-round deadlock (C0023) and a
  20-way target ambiguity (C0008).
- A 12-item fix tranche followed (five anomaly fixes, G7
  implementation default-disabled, DeepSeek Phase-1 reasoning fix,
  triple-tool gamma-input cross-verification). 229 regression tests
  pass.
- The architectural confer (this round) was initially run as a LOCAL
  P-pass because the Codex CLI was transiently quarantined by a macOS
  XProtect false-positive (since resolved — codex 0.130.0 reinstalled,
  notarized, authenticated). The local P-pass found and fixed two real
  issues: (a) a pathological-length finding-ID gap (now bounded at 128
  chars), (b) a cross-surface ID-grammar mismatch (G7 used C\d{3,},
  the runner uses C\d{4,}; aligned to C\d{4,}).

This live five-model round is the founder's go/no-go gate before G7 is
enabled (the design stages enablement for Exp 41: single specialist,
low MERGE expected, low blast radius). The local P-pass found NO
falsification of the G7 aggregation rule across eight pathological
vote distributions; your job is to independently confirm or refute.

Compelled-convergence rules (standing project policy):
- ONE converged answer per question. Not a menu of options for the
  founder. If you dissent, defend the dissent explicitly against the
  stated position; if you agree, say so and add only material caveats.
- Ground every claim in the artefacts provided (G7 design note, the
  fix-tranche post-mortem, the merge_arbitration.py source — all
  appended below). Do not speculate beyond the documentary record.
- Word budget: 1200 words total across Q1–Q3.
- Acceptance: 5/5 convergence per question. Anything less re-opens it.
"""

Q1 = r"""
## Q1. G7 merge-arbitration design soundness + enablement

The implemented design (see merge_arbitration.py + the G7 design note
appended): when the auto-merge cannot uniquely place a finding, on the
SECOND consecutive defer the runner dispatches a single-answer query
to all five panel models; aggregation is ≥3/5 same target → MERGE,
≥3/5 KEEP_DISTINCT → register distinct, otherwise stay deferred. A
round-level tie-breaker (γ < tiebreaker_gamma AND γ-alt unmet) sweeps
unresolved deadlocks. Cost-bounded: max 3 arbitrations/round
(~$1.50/round worst case). Ships DEFAULT-DISABLED; design stages
first enablement at Exp 41.

The local P-pass tested the aggregation rule against 8 pathological
vote distributions (5-way scatter, exact 3-2 splits, 2-2-1, all-
unparseable, 1-vote-only, 3-valid-2-dead, 4-keep-1-merge) with NO
falsification.

CONVERGE on ONE answer: Is this design sound to enable AS DESIGNED at
Exp 41, or is a specific change required first? If a change is
required, name the single most important one precisely. If sound,
say so without hedging.
"""

Q2 = r"""
## Q2. Finding-ID hardening: structural rule vs UUID-namespace

Fix 1a added `^[A-Za-z0-9_]{1,128}$` structural validation at all
parser paths (the continuation showed code fragments like
`f for f in findings}` leaking into the FINDING_ID field). The
unconstrained-Gemini second opinion proposed a deeper architectural
change instead: generate a hidden UUID per finding; the model's
identifier becomes a display label only; system-level processing uses
the UUID — eliminating the collision class entirely.

The tranche took the bounded structural fix NOW and documented the
UUID change as a deferred escalation IF R17–R21 still shows mangled
IDs after the structural rule.

CONVERGE on ONE answer: Is "bounded structural fix now, UUID-namespace
only on trigger" the correct call, or should the UUID-namespace change
be done before the R17–R21 resume? One position, defended.
"""

Q3 = r"""
## Q3. Common-language schema coherence + reformat staging

The runner<->panel contract has three schemas: finding-ID grammar
(`^[A-Za-z0-9_]{1,128}$`); fix-block (`<<<< SEARCH <file> … ====
… >>>> REPLACE`); vote grammar (CONFIRM/CHALLENGE/MERGE + G7
MERGE_INTO_<C\d{4,}>/KEEP_DISTINCT). Fix 1e strengthened the
next-round reformat request (mandatory STRUCTURE_VIOLATION template,
"unparseable fix = no fix") but DEFERRED the in-round re-dispatch
loop, on the reasoning that the continuation's persistent extract
failures were mostly STALE findings (targeting already-modified
source) that an in-round retry cannot fix anyway.

CONVERGE on ONE answer: Are the three schemas coherent as a single
common language, AND is "strengthen the next-round reformat now,
defer in-round dispatch on a documented trigger" correct — or is the
in-round dispatch warranted before the resume? One position.
"""

RESPONSE_FORMAT = r"""
## Response format (compelled-convergence)

For EACH of Q1, Q2, Q3:
  CONVERGED POSITION: <one clear sentence — the single answer>
  REASONING: <grounded in the appended artefacts; cite by name>
  FALSIFICATION: <the strongest argument against your position, and
    why it does not overturn it — or, if it does, change your position>

End with:
  OVERALL: <one paragraph — is the architecture sound to (a) resume
  Exp 40 R17–R21 with G7 still disabled, and (b) enable G7 at Exp 41?
  YES/NO + the single blocking item if NO.>

Total ≤ 1200 words. No menu. One position per question.
"""


def build_user_prompt() -> str:
    return (
        FRAMING + "\n\n" + Q1 + "\n\n" + Q2 + "\n\n" + Q3 + "\n\n"
        + "## Background A — G7 design note (full text)\n\n" + G7_DESIGN
        + "\n\n## Background B — merge_arbitration.py (full source)\n\n"
        + "```python\n" + G7_MODULE + "\n```\n\n"
        + "## Background C — fix-tranche post-mortem (full text)\n\n"
        + TRANCHE_PM + "\n\n" + RESPONSE_FORMAT
    )


def _dispatch(model_label: str, model_id: str, api: str,
              system_prompt: str, user_prompt: str) -> dict:
    start = time.time()
    try:
        if api == "claude_cli":
            response = call_claude_cli(model_id, system_prompt, user_prompt)
        elif api == "openrouter":
            response = call_openrouter(model_id, system_prompt, user_prompt)
        elif api == "deepseek":
            response = call_deepseek(model_id, system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown api: {api}")
        elapsed = time.time() - start
        return {
            "model": model_id, "label": model_label, "api": api,
            "response": response, "time_s": round(elapsed, 1),
            "chars": len(response) if response else 0,
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model_id, "label": model_label, "api": api,
            "error": f"{type(e).__name__}: {e}",
            "time_s": round(elapsed, 1),
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }


def main() -> int:
    system_prompt = CDSFL_TEXT
    user_prompt = build_user_prompt()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching Exp 40 architectural confer to {len(MODELS)} models")
    print(f"Prompt size: {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
    print(f"Timestamp: {timestamp}")
    print(f"Logs: {LOGS_DIR}")
    print()

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {
            ex.submit(_dispatch, label, mid, api, system_prompt, user_prompt): label
            for (label, mid, api) in MODELS
        }
        for fut in concurrent.futures.as_completed(futures):
            label = futures[fut]
            result = fut.result()
            results[label] = result
            if "error" in result:
                print(f"  {label}: ERROR in {result['time_s']}s — "
                      f"{result['error'][:200]}")
            else:
                print(f"  {label}: {result['chars']} chars in "
                      f"{result['time_s']}s")
            (LOGS_DIR / f"{label}_{timestamp}.json").write_text(
                json.dumps(result, indent=2))

    combined_path = LOGS_DIR / f"combined_{timestamp}.json"
    combined_path.write_text(json.dumps(results, indent=2))
    print()
    print(f"Combined log: {combined_path}")

    errors = [label for label, r in results.items() if "error" in r]
    if errors:
        print(f"\n{len(errors)}/{len(MODELS)} models errored: "
              f"{', '.join(errors)}")
        return 1
    print(f"\nAll {len(MODELS)} models returned cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
