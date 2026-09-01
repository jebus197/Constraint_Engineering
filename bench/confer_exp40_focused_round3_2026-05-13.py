#!/usr/bin/env python3
"""
Exp 40 Pre-Launch — Focused Confer Round 3 (13 May 2026)
=========================================================

Compelled-convergence follow-up to Round 2 (10 May 2026). Round 2
returned 75-85% convergence; three sub-items had residual divergence
that violated the standing compelled-convergence policy if left
unresolved. Round 3 closes those three items.

Questions:

- Q1. Exp 44 vs Exp 49 as primary trigger for G6 + G7.
      DeepSeek dissent in Round 2: Exp 44 (synthetic composition of
      math + composer + macrophage outputs) is structurally unlikely
      to surface multi-specialist verdict conflict or MERGE deadlock,
      because only one specialist participates. Exp 49 is the first
      experiment that forces multi-specialist co-rule by design. Four
      of five Round 2 models endorsed Exp 44 with migration clause to
      Exp 49 as written; DeepSeek argued Exp 49 should be the primary
      and Exp 44 retained only as early-observation checkpoint.
      Migration logic is already correct; this is a wording question
      about which experiment is named as primary. Force convergence
      on the actual §6b wording.

- Q2. F3 DEBUG_CHANNEL_CHECK closure-state label.
      Round 2 split 3-2: Gemini, ChatGPT-conditional, CC2 argued
      `shadow_integrated` (runs in dev/CI path, executes on real
      inputs, emits side-effects). Codex weakly + DeepSeek explicitly
      argued `library_complete` (production default is no-op; when
      active it can abort the run, which is a behavioural side-effect
      that does not fit shadow-integrated's observation-only
      definition). Round 2 noted F3 fits no existing label cleanly.
      Force convergence on `library_complete`, `shadow_integrated`,
      or — if the panel converges that neither fits — propose a 4th
      lexicon label and its definition.

- Q3. Medium-priority Exp 51 / 52 / 53 brief refinements from Round 2.
      CC2 + ChatGPT flagged in Round 2:
      (a) Exp 51 physics: add z3-routable conservation-violation
          cluster alongside existing kinematics, conservation,
          dimensional, special-function clusters.
      (b) Exp 52 chemistry: rename `collections.Counter` →
          `stoichiometric_balance` (the manifest entry name) for the
          stoichiometry cluster's falsifiability route.
      (c) Exp 53 engineering: drop `astropy.units` (not in engineering
          domain config); add `linear_programming`-routable
          optimisation claim cluster.
      Each refinement had 1-2/5 panel support in Round 2 but was
      surfaced rather than auto-applied. Round 3 forces a single
      yes/no decision per refinement.

Panel composition (unchanged from Round 2; smoke-tested 2026-05-10):
    Gemini 3.1 Pro Preview — google/gemini-3.1-pro-preview via OpenRouter
    Codex GPT-5.5          — openai/gpt-5.5 via OpenRouter
    CC2 Claude Opus 4.7    — opus via Claude CLI piped mode
    ChatGPT GPT-5.5        — openai/gpt-5.5 via OpenRouter
    DeepSeek V4 Pro        — deepseek-v4-pro via DeepSeek direct API

Dispatch: parallel via ThreadPoolExecutor(max_workers=5), star
          topology. Logs to bench/logs/confer_exp40_focused_round3_2026-05-13/.
"""

from __future__ import annotations

import concurrent.futures
import json
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
            import os  # noqa: E402
            os.environ.setdefault(_k, _v)

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_focused_round3_2026-05-13"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("cc2",      "opus",                          "claude_cli"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

# ---------------------------------------------------------------------------
# CDSFL system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Consolidated plan (full content injected as background)
# ---------------------------------------------------------------------------

PLAN_PATH = REPO_ROOT / "experimental_notes" / "Exp40_to_54_Consolidated_Plan_2026-04-21.md"
PLAN_TEXT = PLAN_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Round 3 framing
# ---------------------------------------------------------------------------

ROUND3_FRAMING = r"""
## Round 3 framing (load-bearing — read first)

This is a compelled-convergence follow-up to Round 2 (10 May 2026).
Round 2 closed five questions with 75-85% convergence. Three sub-items
retained divergence that violates the standing compelled-convergence
policy: the panel must converge on a single position per question, not
present a menu of alternatives to the founder.

Round 3 asks three questions only. Each question presents the Round 2
divergence in full, including the dissenting reasoning. The panel is
required to converge on ONE position per question. If a model finds
itself agreeing with a position it previously dissented from, say so
and explain the move. If a model holds its prior position, defend it
explicitly against the counter-arguments now in front of you.

Anchors that remain in force from Rounds 1 and 2:

- bench/exp40_configs/40_gate.json acceptance criterion: "gamma >= 0.30
  OR (3 consecutive rounds with 0 novel CRITICAL findings). Gamma-alt
  implemented in reference_runner_v3._check_gamma_alt_convergence."

- Stage 6 orthogonality: R_k = VALIDITY, nu_k = NOVELTY, c_ext = SEARCH
  QUALITY. Three independent reporting dimensions; MUST NEVER be
  collapsed before reporting.

- The four residuals from the 22 April 2026 founder oversight Q&A are
  closed on the merits per Round 2 5/5 consensus (one labelling
  sub-item under Q2 below).

- The two high-confidence fold-ins from Round 2 are applied: Exp 47
  biology brief now has a z3 logical cluster + corrected codon-error
  attribution; §6b carries a clarifying note on Exp 44 vs Exp 49
  trigger expectations.

Compelled-convergence rules:
- ONE answer per question, not a menu.
- If you previously dissented, address the counter-arguments now in
  front of you explicitly. Either move, or defend the prior position.
- Word budget: 1500 words total across Q1-Q3.

Acceptance criterion for the round: 5/5 panel converges on each
question. Anything less re-opens that question.
"""

# ---------------------------------------------------------------------------
# Q1 — Exp 44 vs Exp 49 trigger
# ---------------------------------------------------------------------------

Q1 = r"""
## Q1. Exp 44 vs Exp 49 as primary trigger for G6 + G7

**Round 2 divergence summary.**

Four of five models (Gemini, Codex, ChatGPT, CC2) endorsed the §6b
text as written: primary trigger is Exp 44 post-mortem; migration to
Exp 49 if Exp 44 produces no qualifying evidence. Gemini's stated
reason: "Exp 44 is a synthetic composition test explicitly designed to
force multi-specialist interaction, making it the correct observation
ground."

DeepSeek V4 Pro dissented with the following reasoning (verbatim from
Round 2):

> Exp 44 lacks the multi-specialist merge path. It composes outputs
> from the mathematics specialist [Exp 41], the encodings composer
> [Exp 42], and the macrophage admissibility cell [Exp 43] — only one
> specialist cell participates; no cross-specialist conflict can
> arise. The first experiment guaranteed to have multiple specialists
> is Exp 49 (cross-domain synthesis). The migration clause to Exp 49
> is present, but the primary trigger will never fire, delaying
> activation unnecessarily.

Inspection of the per-experiment matrix in §2 of the consolidated plan
(see background) supports DeepSeek's structural reading: Exp 44 is the
"composition test (no new target)" combining Exp 41 + 42 + 43 outputs.
Exp 41 produces the mathematics specialist's outputs; Exp 42 produces
encoded targets via the composer; Exp 43 produces macrophage verdicts.
None of those involve two B-Cell specialists co-ruling on a shared
Finding.

**Stage 6 anchor.** Specialist-to-specialist verdict conflict (G6) and
MERGE deadlock between specialists (G7) require AT MINIMUM two
distinct B-Cell specialists from `LIVE_SPECIALIST_DOMAINS` (currently
{mathematics, statistics, biology, information_science}) returning
verdicts on the same `Finding`. Exp 44 routes through a single
specialist plus the composer plus the macrophage; cross-specialist
co-rule is not in its dispatch.

**Required output.** ONE of the following, defended:

A. **Keep §6b as written.** Exp 44 primary trigger, Exp 49 migration.
   If you choose this, name a specific dispatch path in Exp 44 that
   produces multi-specialist co-rule, citing the consolidated plan or
   `bench/reference_runner_v3.py`. If you cannot, this option is
   refuted by structural analysis.

B. **Reword §6b to Exp 49 primary, Exp 44 retained as early-observation
   checkpoint.** Migration logic unchanged. Trigger fires on first
   observed multi-specialist conflict from Exp 49 onwards; Exp 44 logs
   are still parsed in case anything anomalous surfaces.

C. **Other.** Specify exactly.

State your choice as `**Final position: A/B/C — <one sentence
justification>**`.
"""

# ---------------------------------------------------------------------------
# Q2 — F3 DEBUG_CHANNEL_CHECK label
# ---------------------------------------------------------------------------

Q2 = r"""
## Q2. F3 DEBUG_CHANNEL_CHECK closure-state label

**F3 in context.** F3 is a debug-time assertion at
`bench/reference_runner_v3.py:3510`, gated by environment variable
`DEBUG_CHANNEL_CHECK=1`. When the env var is set, the assertion
compares the wrapped `compute_rk_with_eta_channel(...)` output against
an independently computed bare `compute_rk(...)` output to within
1e-9. On mismatch, it raises AssertionError (which would halt the
runner). Production default is no-op (env var unset).

**F4 closure-state lexicon (from `resources/ONBOARDING.md`):**

- `library_complete.` Code exists and is correct on its own terms. It
  is NOT yet hooked into any live pipeline, runner, or dispatch path.
- `shadow_integrated.` Code is hooked into the live pipeline in an
  observation-only capacity. Runs on every relevant input, emits logs
  or metrics, participates in audits, but its outputs do NOT drive
  verdicts, promotions, or gate decisions.
- `live_operational.` Code drives live decisions. Reversion requires
  an explicit policy change, not just a config flip.

**Round 2 split.**

- *Shadow_integrated camp (3/5):* Gemini, ChatGPT (conditional), CC2.
  Reasoning: F3 runs in the dev/CI path (where the env var is set
  during pytest runs and pre-Exp-40 verification), executes on real
  inputs, and emits side-effects (the assertion log + halt).
  Conditional from ChatGPT: only `library_complete` if it remains
  dev/CI-only and is NOT active during Exp 40 production dispatch.

- *Library_complete camp (2/5):* Codex (weakly), DeepSeek (explicitly).
  Reasoning from DeepSeek: "F3 is implemented, library-complete, and
  only active under a debug flag (dev/CI). It is not shadow (it can
  abort the run on failure), nor live-operational without flag, so
  library_complete is the correct label."

**The edge case.** The F4 lexicon was designed for components that
are either off (library_complete), observing (shadow_integrated), or
driving live decisions (live_operational). F3 is off by default but
becomes assertive (can halt the run) when toggled. It fits no label
cleanly.

**Required output.** ONE of the following, defended:

A. **`library_complete`.** F3 is hooked-on-flag, default off; the dev/CI
   activation is a developer affordance, not a pipeline observation.

B. **`shadow_integrated`.** F3 runs in the pipeline whenever the flag
   is set and emits side-effects on every relevant input. The
   assertion-halt is a measurement-driven outcome; that DOES drive
   decisions in dev/CI but not in production.

C. **`tripwire` (new 4th label).** Define it here: "Code present in
   the live or dev/CI pipeline that is observation-only by default
   (off; or on-emit-only) but becomes assertive (halts the run, blocks
   the gate, or otherwise drives an outcome) when an explicit flag is
   set." Promote F4 lexicon to four labels: library_complete → tripwire
   → shadow_integrated → live_operational. F3 takes the new `tripwire`
   label.

D. **Other.** Specify exactly.

State your choice as `**Final position: A/B/C/D — <one sentence
justification>**`.

**Note for the panel.** Option C (new 4th label) is offered explicitly
to relieve the edge-case pressure. If the panel converges that the
lexicon as it stands forces a poor fit for F3, adopting `tripwire`
solves the labelling problem permanently. Choose only if the panel
agrees this is the correct architectural move.
"""

# ---------------------------------------------------------------------------
# Q3 — Exp 51 / 52 / 53 brief refinements
# ---------------------------------------------------------------------------

Q3 = r"""
## Q3. Exp 51 / 52 / 53 brief refinements

**Round 2 surfaced three specific corrections to the §2a target-article
scope briefs, with 1-2/5 panel support each. Round 3 asks for a single
yes/no per refinement.**

For each (a), (b), (c) below, answer **YES (apply now)** or **NO (do
not apply)** with a one-sentence justification anchored to either the
consolidated plan §2a, the relevant `bench/cdsfl_registry/domains/immune/<domain>.toml`,
or the `bench/cdsfl_registry/tool_manifest.toml`.

### (a) Exp 51 physics brief: add z3-routable conservation-violation cluster

Current §2a Exp 51 has four claim clusters: kinematics, conservation
laws, dimensional consistency, special-function. The physics specialist
routes per `domains/immune/physics.toml`: mathematical →
`sympy + dimensional_analysis + astronomical`. The brief lists no
explicit z3 logical-claim cluster, but the consolidated plan §2a
opening paragraph commits each module to "exercise the routed
specialist tools at the experiment's intended depth".

Question: does `domains/immune/physics.toml` route any claim type to
z3? If yes, the brief MUST contain a z3-routable cluster; add a
conservation-violation cluster phrased as a propositional structure
the specialist can test for unsatisfiability (e.g., "energy in =
energy out + dissipation; if dissipation is asserted negative, derive
contradiction"). If no, the brief is complete as-is and no z3 cluster
is needed.

**YES / NO — anchored to physics.toml.**

### (b) Exp 52 chemistry brief: rename `collections.Counter` → `stoichiometric_balance`

Current §2a Exp 52 cluster 2 says: "**Stoichiometry.** Balanced-equation
claims with coefficient-sum assertions. Falsifiability route: `rdkit`
+ `collections.Counter` atom-balance cross-check."

CC2's Round 2 observation: `bench/cdsfl_registry/tool_manifest.toml`
lists a tool entry named `stoichiometric_balance` that wraps the
atom-balance check. `collections.Counter` is the underlying stdlib
used inside the routed tool, not the manifest's named entry.

Question: is `stoichiometric_balance` the manifest entry name for the
routed atom-balance check? If yes, the brief should name the manifest
entry, not the underlying primitive. If no, leave as written.

**YES / NO — anchored to tool_manifest.toml.**

### (c) Exp 53 engineering brief: drop `astropy.units`, add linear_programming cluster

Current §2a Exp 53 cluster 4 says: "**Dimensional consistency.** Units
across mechanical, thermal, electrical domains. Falsifiability route:
`pint` + `astropy.units` cross-check."

CC2's Round 2 observation: `astropy.units` is not declared in
`domains/immune/engineering.toml`. Including it in the brief risks
the synthesised target prompting verification against a tool the
specialist does not route to. Separately: the engineering domain
typically benefits from explicit optimisation modelling, and the
manifest declares `linear_programming` as a routed tool.

Question (two parts):
- Should `astropy.units` be dropped from the Exp 53 brief? Answer
  anchored to `domains/immune/engineering.toml` declared routings.
- Should a linear_programming-routable optimisation cluster be added
  to Exp 53? Answer anchored to the manifest's `linear_programming`
  entry and the engineering domain's tool routings.

**YES-drop / NO-keep** for `astropy.units`. **YES-add / NO-skip** for
linear_programming cluster.

---

State the three answers as:
- **Final position (a): YES / NO — <one sentence>**
- **Final position (b): YES / NO — <one sentence>**
- **Final position (c-units): YES-drop / NO-keep — <one sentence>**
- **Final position (c-LP): YES-add / NO-skip — <one sentence>**
"""

# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

RESPONSE_FORMAT = r"""
## Response format (compelled-convergence)

For each question:

1. FFAFP workings (Find, Follow, Analyse, Fix, P-pass). Keep terse;
   word budget across Q1-Q3 is 1500 words total.
2. ONE final position per the option set named in the question,
   bolded as specified.
3. Anchor every claim to the consolidated plan section number, the
   file:line citation in the relevant code module, or the
   `bench/cdsfl_registry/domains/immune/*.toml` or
   `bench/cdsfl_registry/tool_manifest.toml` entry, as appropriate.

Compelled-convergence reminder:
- ONE answer per question; no menus.
- If you held a different position in Round 2, address the
  counter-arguments now in front of you explicitly. Either move with
  reason, or defend the prior position with reason.

Acceptance criterion: 5/5 convergence on Q1, Q2, and each of Q3's
sub-parts. Anything less re-opens that item.
"""


# ---------------------------------------------------------------------------
# Compose full user prompt
# ---------------------------------------------------------------------------

def build_user_prompt() -> str:
    return (
        ROUND3_FRAMING
        + "\n\n"
        + Q1
        + "\n\n"
        + Q2
        + "\n\n"
        + Q3
        + "\n\n"
        + "## Background — Exp 40-54 consolidated plan (full text, for cross-reference)\n\n"
        + PLAN_TEXT
        + "\n\n"
        + RESPONSE_FORMAT
    )


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

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
            "model": model_id,
            "label": model_label,
            "api": api,
            "response": response,
            "time_s": round(elapsed, 1),
            "chars": len(response) if response else 0,
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model_id,
            "label": model_label,
            "api": api,
            "error": f"{type(e).__name__}: {e}",
            "time_s": round(elapsed, 1),
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }


def main() -> int:
    system_prompt = CDSFL_TEXT
    user_prompt = build_user_prompt()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching Exp 40 focused Round 3 to {len(MODELS)} models")
    print(f"Prompt size: {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
    print(f"Plan under reference: {PLAN_PATH.name} ({len(PLAN_TEXT)} chars)")
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
                print(f"  {label}: ERROR in {result['time_s']}s — {result['error'][:200]}")
            else:
                print(f"  {label}: {result['chars']} chars in {result['time_s']}s")

            per_model_path = LOGS_DIR / f"{label}_{timestamp}.json"
            per_model_path.write_text(json.dumps(result, indent=2))

    combined_path = LOGS_DIR / f"combined_{timestamp}.json"
    combined_path.write_text(json.dumps(results, indent=2))
    print()
    print(f"Combined log: {combined_path}")

    errors = [label for label, r in results.items() if "error" in r]
    if errors:
        print(f"\n{len(errors)}/{len(MODELS)} models errored: {', '.join(errors)}")
        return 1
    print(f"\nAll {len(MODELS)} models returned cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
