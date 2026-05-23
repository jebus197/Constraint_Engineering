"""Advisory definitional confer — convergence definition (2026-05-18).

Advisory (not binding). No presupposed answer. Dissent permitted and valued.
Panel: Gemini 3.1 Pro, Codex GPT-5.5, CC2 Opus 4.7, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, latest CDSFL schema.
Logs: bench/logs/confer_definitional_advisory_2026-05-18/.
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_definitional_advisory_2026-05-18"
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

USER_PROMPT = r"""
## Advisory definitional confer — framing (read first)

This confer is ADVISORY. Its output informs a decision; it does not
bind one. Dissent is explicitly permitted and valued. Do NOT
manufacture unanimity: if the verified evidence genuinely supports one
position, converge on it on the technically soundest argument; if it
does not, report the genuine distribution and the strongest case for
each position. A reasoned split is information, not failure.

NO position is presupposed. Neither the operator nor the working model
holds a preferred answer, and none is embedded below or presented for
falsification. The brief is verified facts plus open questions only.
Reason from the facts and the project's mathematical model, not from
preference, optimism, or accommodation.

Each model must, in addition to its answer: state the single strongest
argument AGAINST its own recommendation and whether it overturns it;
give an explicit book-cooking self-check (why its recommendation
measures a real phenomenon rather than fitting a measure to a desired
result); and flag any unsupported assertion or parroting in its own or
others' reasoning. Word budget ~1500.


## Fixed goal and hard constraint (operator-stated facts, not in question)

GOAL (fixed, recorded in README / founders' notes / mathematical
appendix; non-negotiable): CDSFL is to be a genuinely useful
science/STEM "calculator" that produces real, dependable results — not
demonstration theatre. Whether this goal is correct is NOT the
question; it is settled.

RESOURCE BOUND (factual): one developer, one Apple M1 Mac Mini,
approximately one month of financial runway remaining. Continuation
beyond that requires generating external interest. This is a hard
practical bound on compute and wall-clock.


## Verified technical facts (code- and data-grounded; reason from these)

F1. gamma is the Duane reliability-growth parameter, gamma = 1 - beta,
   computed by an OLS log-log fit of CUMULATIVE novel findings vs round
   index (a global-cumulative statistic; runner _estimate_gamma). Its
   input is post-reconciliation (gross duplicate churn already
   stripped).

F2. The ratified Exp 40 acceptance gate (Consolidated Plan S10, status
   "Enforced"): converged iff gamma >= 0.30 OR 3 consecutive rounds with
   zero novel CRITICAL (severity >= 0.7) findings. It is an OR — the
   two arms can disagree and the run still passes.

F3. Production-faithful audit (runner's own post-reconciliation rule +
   the real estimator): on a small (~110-line) decomposed slice with
   apply-fixes-back ON, gamma all-novelty = 0.231 while gamma critical-only =
   0.553. On the full 621-line file with no apply-back over a long
   arc, gamma all = 0.102, gamma critical = 0.329. Findings are ~41-57%
   substantive (verified or fix-bearing). Residual near-duplicate among
   gamma-relevant canonicals is ~0% (slice) to ~10% (long arc) by an
   offline proxy; the reconciliation strip itself is production-true.

F4. The estimator is run-length-fragile. In a full-budget resume gamma
   crossed 0.30 (0.3047) on a single round, by a 0.0047 margin; a
   faithful recompute from the SETTLED registry gave 0.231 (below the
   gate). The convergence verdict flips on live-at-round vs
   after-settling novelty accounting.

F5. The all-severity finding surface is effectively unbounded —
   continuous minor refinements are always possible on code/language.
   The mathematical appendix S7.1 states the standard Duane model
   assumes a CLOSED, monotonically-depleting defect pool; an
   error-re-injection-extended intensity lambda_ext is specified but
   UNIMPLEMENTED; the appendix's divergence condition holds that when
   re-injection exceeds the decay rate the system produces more noise
   than signal.

F6. The critical/structural severity boundary is the constant 0.7 in
   the runner. The mathematical appendix's documented severity
   thresholds are 0.0 / 0.3 / 0.5; 0.7 is a code convention, not a
   documented schema boundary. A principled definition of
   "critical/structural" is unresolved.


## The questions (no preferred answer; advisory; dissent permitted)

Q1. Given the fixed goal and the hard resource bound, is TOTAL
   exhaustion — convergence defined as no new findings of ANY severity
   — realistically attainable? Answer from F1-F6 and the mathematical
   model, not from preference.

Q2. What is the soundest, falsifiable, NON-cooking definition of
   "converged / done" for the CDSFL proof-of-concept under that goal
   and that bound:
     (X) exhaustion of the critical/structural problem space;
     (Y) total exhaustion across all severities;
     (Z) some other precisely-specified criterion.
   If X: state exactly the conditions that make it non-cooking and
   externally defensible to a hostile reviewer. If Y: state how it is
   attainable under the bound. If Z: specify it precisely. "Cooking" =
   choosing or redefining a measure to obtain a desired result;
   distinguishing it from a principled, pre-registered, transparently
   scoped definition is part of the task.

Q3. Given your Q2 answer, what are the concrete, prioritised next steps
   within ~1 month of solo compute on one M1 — what to build, what to
   run, what to defer, what to hand forward — to best demonstrate the
   stated goal? Be specific.

Per-model, also: strongest counter to your own position + whether it
overturns it; book-cooking self-check; parroting/unsupported-assertion
flags.


## Response format

Q1 VERDICT: <attainable / not attainable — one line, then rationale
  grounded in F1-F6 + the model>
Q2 POSITION: <X / Y / Z + the precise criterion; if X, the explicit
  non-cooking + external-defensibility conditions>
Q3 NEXT STEPS: <prioritised, concrete, scoped to ~1 month / 1 M1>
STRONGEST COUNTER TO MY POSITION: <one paragraph; then does it
  overturn? yes/no + why>
BOOK-COOKING SELF-CHECK: <why this measures a real phenomenon, not a
  fitted measure>
FLAGS: <unsupported assertions / parroting spotted, own or others'>

<= ~1500 words. Advisory: a reasoned dissent is a valid output; do not
converge for the sake of converging.
"""


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
    user_prompt = USER_PROMPT
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching advisory definitional confer to {len(MODELS)} models")
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
