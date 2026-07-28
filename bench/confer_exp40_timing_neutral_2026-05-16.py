"""Exp 40 timing re-confer — NEUTRAL framing (2026-05-16).

The 2026-05-15 architectural confer reached 5/5 but its questions
embedded a deferral baseline ("sound to enable AS DESIGNED at Exp 41?",
"is bounded-fix-now / UUID-on-trigger correct?"). The founder
identified this as a leading-question / agreement-amplification flaw:
a 5/5 yes to a question that contains the answer is weak evidence.

This round re-asks the three timing decisions with NO presupposed
answer. Each question states the technical facts and BOTH competing
lines of reasoning, then asks the panel to independently recommend
timing and to adversarially test (falsify or confirm) the working
model's own reasoning. Deferral is not the default: if the panel
recommends defer, it must give a SPECIFIC technical reason and name
the experiment at which it should land (so it can be marked in the
Exp 40-54 canonical plan).

Panel: Gemini 3.1 Pro, Codex GPT-5.5, CC2 Opus 4.7, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, parallel dispatch, latest CDSFL schema
(cdsfl_core_formal.md) as system prompt.
Logs: bench/logs/confer_exp40_timing_neutral_2026-05-16/.
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

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_timing_neutral_2026-05-16"
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

G7_DESIGN = (REPO_ROOT / "experimental_notes"
             / "G7_Merge_Deadlock_Resolution_Design_2026-05-15.md").read_text()
TRANCHE_PM = (REPO_ROOT / "experimental_notes"
              / "Exp40_Fix_Tranche_Postmortem_2026-05-15.md").read_text()
G7_MODULE = (REPO_ROOT / "bench" / "merge_arbitration.py").read_text()

FRAMING = r"""
## Neutral timing re-confer — framing (read first)

A prior confer (2026-05-15) on these same three items reached 5/5, but
its questions presupposed deferral ("enable AS DESIGNED at Exp 41?",
"bounded-fix-now/UUID-on-trigger correct?"). That is a leading-question
flaw and the 5/5 cannot be trusted for the TIMING decision. This round
removes the bias.

For EACH question below:
- The technical facts are stated without a recommended answer.
- BOTH competing lines of reasoning are given in full, labelled,
  with neither marked as the default.
- One of the lines is the working model's (CC1's) own reasoning,
  marked [CC1-REASONING]. Your task includes adversarially testing
  it: state the single strongest technical argument that CC1's
  reasoning is WRONG, then say whether that argument actually
  overturns it.
- You must answer the timing question directly: implement NOW (before
  the Exp 40 R17-R21 resume), or DEFER. "Defer" is NOT the safe
  default — it must be earned. If you recommend defer, you must give
  a SPECIFIC technical reason (not "caution", not "lower risk" alone)
  AND name the experiment at which it should be implemented, so it can
  be marked in the Exp 40-54 canonical plan at that juncture.

Compelled convergence: ONE converged position per question. If you
dissent from the emerging consensus, defend it on technical grounds.
Word budget: 1400 words total. Acceptance: 5/5 per question.

Background context: the Exp 40 continuation (R10-R16) reached deep
gamma-decay convergence (0.034) but the gamma-alt boolean (3
consecutive zero-novel-CRITICAL rounds) never fired; novelty
oscillated. Six D4 MERGE deadlocks (C0023 14 rounds, C0008 20-way) +
three D2 escalations were observed IN THAT RUN. R17-R21 is the
continuation of exactly that run. The full fix tranche (1a-1e,
DeepSeek Phase-1, gamma-input) is folded in and 229 tests pass. G7 is
implemented but currently disabled by config.
"""

Q1 = r"""
## Q1. G7 merge-arbitration: enable for the R17-R21 resume, or defer?

FACTS (no recommendation embedded):
- G7 resolves merge deadlocks by dispatching a single-answer query to
  the 5-model panel on the 2nd consecutive defer; >=3/5 agreement
  merges or keeps-distinct; otherwise stays deferred. Cost-capped at
  3 arbitrations/round (~$1.50/round). Default-disabled.
- G7's aggregation logic has 18 unit tests incl. 8 adversarial vote
  distributions (stubbed dispatch — no live model calls in tests).
- G7's registry mutation is `registry.resolve(canonical_id,
  "MERGED", round_idx, merged_into=...)` — the SAME call the existing
  D4 quorum path already makes. It is NOT a new registry-mutation
  code path; only the trigger (panel vote vs verdict quorum) differs.
- G7's runner-integration path (_try_merge_arbitration -> live
  dispatch -> resolve) has never executed against a live registry or
  real model calls.
- R17-R21 is the continuation of the exact run that produced the six
  observed D4 deadlocks (C0023 14 rounds, C0008 20-way).
- The G7 design note staged first enablement for Exp 41 ("single
  specialist, low MERGE expected, low blast radius if the arbitration
  logic has issues").

[CC1-REASONING] (adversarially test this): Resuming R17-R21 with G7
off deterministically reproduces a problem we already have full
evidence for — wasted compute/time/money to rediscover a known
result. The registry-mutation path is not novel (reused resolve call),
the aggregation is adversarially tested, and R17-R21 is the ideal
context to exercise G7 BECAUSE it is deadlock-dense. The Exp-41
staging was written for a hypothetical, before the deadlock evidence
existed. Therefore enable G7 for R17-R21.

[COUNTER-REASONING]: G7 has never run live; a long convergence run is
a poor place to first exercise unproven integration code, because a
latent bug (dispatch wrapper, candidate-set construction, the
round-level tie-breaker sweep) could corrupt registry state or burn
the round budget mid-run, and you cannot cleanly attribute R17-R21
convergence to the fix tranche vs G7. Exp 41 is single-specialist,
low-MERGE, cheap-failure — the correct first-exercise context.

ANSWER: Is G7 technically sound? Implement (enable) NOW for R17-R21,
or DEFER to Exp 41? If defer, the specific technical reason that
outweighs the rediscovery cost, and confirm Exp 41 as the marked
juncture. Adversarially test [CC1-REASONING]: strongest argument it
is wrong, and does that argument actually overturn it?
"""

Q2 = r"""
## Q2. Finding-ID: structural rule alone, or structural + UUID-namespace,
and when?

FACTS:
- Fix 1a added `^[A-Za-z0-9_]{1,128}$` structural validation at all
  parser paths. It rejects MALFORMED ids (code fragments, backticks,
  multi-token text) at parse time. Implemented + tested.
- UUID-namespace (proposed, not built): the runner generates a hidden
  UUID per finding at intake; the model-supplied id becomes a display
  label only; all system-level reconciliation/dedup/registry indexing
  keys on the UUID.
- The continuation post-mortem records that the panel itself
  diagnosed a collision-overwrite bug: `{f.finding_id: f for f in
  findings}` silently overwrites when two findings from different
  models share a finding_id.

[CC1-REASONING] (adversarially test this): 1a and UUID-namespace fix
DIFFERENT bugs at different layers. 1a rejects malformed ids; it does
NOT close the collision-overwrite. Two models both emitting a clean
`F001` both pass 1a and still silently overwrite — a finding vanishes
with no error (silent data loss, the worst failure class in a
convergence run because lost findings are indistinguishable from
converged ones). Therefore 1a is necessary but NOT sufficient; the
collision-overwrite is a still-open, panel-diagnosed defect that 1a
does not touch; both measures should be implemented, and the timing
question for UUID-namespace is open on its own merits, not "deferred
deeper alternative".

[COUNTER-REASONING]: If, empirically, finding-id collisions across
models are rare or zero in practice (model ids are usually
model-prefixed: CC2_F001 vs Gemini_F001 do not collide), then 1a may
be sufficient in practice and UUID-namespace is an architectural
change whose cost (touching every canonical-id keying site) is not
justified pre-resume; it can wait until evidence of an actual
collision.

ANSWER: Is CC1-REASONING correct that 1a does not close the
collision-overwrite and they are different bugs? Is UUID-namespace
technically sound? Implement NOW (before R17-R21), or DEFER (specific
technical reason + named experiment)? Does implementing BOTH together
materially harden convergence, or is that a false "defense in depth"?
One converged position.
"""

Q3 = r"""
## Q3. In-round reformat re-dispatch: implement before R17-R21, or defer?

FACTS:
- Fix 1e strengthened the NEXT-round reformat request (mandatory
  STRUCTURE_VIOLATION template, "unparseable fix = no fix").
  Implemented + tested. A malformed fix is re-requested next round.
- In-round re-dispatch (proposed, not built): on parse failure,
  immediately re-send the model its own output with the strict
  template, parse the retry before reconciliation closes — same
  round, not next.
- Stale findings (proposed_fix targeting already-modified source) are
  correctly rejected and are out of scope for BOTH mechanisms (the
  fix text itself is obsolete; re-asking cannot help).
- Continuation showed ~4-5 extract failures/round, a mix of stale and
  genuinely-malformed.

[CC1-REASONING] (adversarially test this): For the genuinely-malformed
fraction, 1e (done) already recovers them with a one-round-close
delay. In-round dispatch removes that delay but adds a new dispatch
path INSIDE the reconciliation loop with real loop-risk and per-round
cost. The honest framing is a concrete tradeoff: a one-round-close
delay across ~4-5 findings/round for 5 rounds, versus a new
mid-reconciliation dispatch loop in a run we want stable. 1e is
plausibly sufficient for R17-R21; in-round dispatch is an
optimisation, not a correctness fix.

[COUNTER-REASONING]: We KNOW malformed output recurs. A one-round
delay compounded over a 5-round resume on every malformed finding is
non-trivial wasted convergence headroom; if convergence is
marginal (gamma-alt never fired in R10-R16), the delay tax could be
the difference between converging and not. Implement in-round now and
stop paying the tax.

ANSWER: Is in-round dispatch technically sound? Implement NOW (before
R17-R21), or DEFER (specific technical reason + named experiment)? Is
1e alone sufficient for R17-R21? One converged position; adversarially
test CC1-REASONING.
"""

RESPONSE_FORMAT = r"""
## Response format

For EACH of Q1, Q2, Q3:
  RECOMMENDATION: <NOW or DEFER — one word, then one sentence>
  TECHNICAL RATIONALE: <grounded in the stated facts + appended
    artefacts; if DEFER, the specific technical reason AND the named
    experiment for canonical-plan marking>
  CC1-REASONING TEST: <single strongest argument CC1's reasoning is
    wrong; then: does it overturn CC1's reasoning? yes/no + why>

End with:
  OVERALL: <one paragraph: with your three recommendations applied,
  is the runner sound to restart Exp 40 R17-R21? Name any item that
  must be implemented before restart vs marked-and-deferred.>

Total <= 1400 words. ONE converged position per question. Defer is
not the default and must be technically earned.
"""


def build_user_prompt() -> str:
    return (
        FRAMING + "\n\n" + Q1 + "\n\n" + Q2 + "\n\n" + Q3 + "\n\n"
        + "## Background A — G7 design note (full)\n\n" + G7_DESIGN
        + "\n\n## Background B — merge_arbitration.py (full source)\n\n"
        + "```python\n" + G7_MODULE + "\n```\n\n"
        + "## Background C — fix-tranche post-mortem (full)\n\n"
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
    print(f"Dispatching Exp 40 NEUTRAL timing re-confer to {len(MODELS)} models")
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
