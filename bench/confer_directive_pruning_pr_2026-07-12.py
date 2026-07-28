"""Panel review ('pr') — directive PRUNING, GUARDED (2026-07-12).

Founder-directed 'pr': cc2, cx, ge, cgpt, ds. Run WITHOUT compelled convergence —
each model gives an INDEPENDENT verdict + its strongest falsification; disagreement
is preserved and synthesized by CC1. Neutral framing (CC1's own keep/cut opinion is
NOT in the prompt — framing-confound avoidance).

GUARDS (added 2026-07-12, per founder — vs the 2026-05 gamma-demotion-panel disaster):
  1. HARD-CONSTRAINT EXCLUSION — the falsification CORE is OFF the pruning surface.
     The panel may NOT recommend cutting/altering it; it is retained verbatim by
     founder ruling. Core = the falsification protocol, the finding + runnable-
     falsifier output format, the R_k self-assessment equation + its variables, the
     worked R_k procedure, the SEARCH/REPLACE fix format, the FFAFP admissibility
     gates, the HARD/SOFT constraint rule, the epistemic-marking tags.
  2. GAMMA / THE MATHS ARE NOT UNDER REVIEW. Gamma, the diminishing-returns / decay
     curve, and the convergence machinery live in the RUNNER, not this directive.
     They are the project's load-bearing foundation and are OUT OF SCOPE. Do not
     discuss, question, or recommend any change to them.
  3. HYPOTHESIS, NOT AUTHORITY. The panel's output is a RECOMMENDATION only. Every
     proposed cut is validated by a lean-vs-full ABLATION before it is adopted;
     nothing is cut on the panel's say-so. Propose freely; the experiment decides.

Logs: bench/logs/confer_directive_pruning_pr_2026-07-12/.
"""
from __future__ import annotations
import concurrent.futures
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_openrouter,
)

_env = REPO_ROOT / ".env"
if _env.exists():
    for ln in _env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        ln = ln[7:] if ln.startswith("export ") else ln
        if "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

LOGS = REPO_ROOT / "bench" / "logs" / "confer_directive_pruning_pr_2026-07-12"
LOGS.mkdir(parents=True, exist_ok=True)

OPERATIONAL = (REPO_ROOT / "bench" / "directives" / "universal"
               / "cdsfl_operational.md").read_text(encoding="utf-8")


def _section_map(text):
    lines, secs, title, buf = text.split("\n"), [], "(preamble)", []
    for ln in lines:
        m = re.match(r'^(#{1,3})\s+(.*)', ln)
        if m:
            secs.append((title, len("\n".join(buf))))
            title, buf = m.group(2), [ln]
        else:
            buf.append(ln)
    secs.append((title, len("\n".join(buf))))
    total = len(text)
    return "\n".join(f"  {sz:>6} ({100*sz/total:4.1f}%)  {t[:64]}" for t, sz in secs if sz)


SECTION_MAP = _section_map(OPERATIONAL)

SYSTEM = (
    "You are an expert reviewer on a panel auditing the OPERATIONAL DIRECTIVE of "
    "CDSFL, a multi-model Popperian-falsification system for STEM and code review. "
    "CDSFL's founding rule: truth is decided by TOOLS and runnable checks, and when "
    "tools cannot decide, by a human — NEVER by model votes. Your job here is narrow: "
    "identify what EXPOSITION (history, motivation, narration, provenance) can be cut "
    "or compressed to shrink a bloated per-turn token tax WITHOUT degrading "
    "falsification rigour. You give an INDEPENDENT verdict; disagreement is wanted, "
    "not smoothed. Be rigorous, specific, concrete; do not rubber-stamp. Respect the "
    "HARD CONSTRAINTS stated in the prompt: some elements are off-limits and the "
    "project's mathematics is out of scope."
)

PROMPT = f"""## Panel review (guarded): what EXPOSITION can this operational directive shed without harming falsification integrity?

### Background
CDSFL reviews code/STEM with a panel of 5 AI models under Popperian falsification.
The text below — the "operational directive", ~44,000 characters — is appended IN
FULL to every model's system prompt on EVERY turn: a fixed per-turn token tax that
also competes for each model's attention. The founder's hypothesis is that a large
fraction is justification / narration / project-history / motivational prose that a
model does not act on per turn, and could be cut or compressed to make the directive
leaner and sharper WITHOUT losing anything load-bearing.

### HARD CONSTRAINTS — read before you answer (violating these makes your review unusable)

1. **The falsification CORE is OFF-LIMITS. Do NOT recommend cutting or rewording it.**
   It is retained verbatim by founder ruling. The core comprises: the falsification
   protocol; the finding output format INCLUDING the runnable-falsifier block; the
   R_k self-assessment equation and every one of its variable definitions; the worked
   R_k procedure; the SEARCH/REPLACE fix format; the FFAFP admissibility gate set; the
   HARD/SOFT constraint-classification rule; and the epistemic-marking tags. For these
   sections, your only valid classification is KEEP. If you think one is redundant,
   say so in one line but still mark KEEP — the founder decides the core, not the panel.

2. **The mathematics is OUT OF SCOPE.** Gamma, the diminishing-returns / decay curve,
   and the convergence machinery live in the RUNNER, not in this directive, and are the
   project's load-bearing foundation. Do NOT discuss, question, or propose any change to
   them. (A prior panel's recommendation to demote gamma was a serious, costly error;
   do not repeat it. This review is ONLY about pruning directive exposition.)

3. **Your output is a RECOMMENDATION, not a decision.** Every cut you propose will be
   validated by a lean-vs-full ABLATION (the lean directive must score >= the full one
   on a fixed task before any cut is adopted). So propose freely — but nothing is cut on
   authority; the experiment decides. Do not smooth toward a group consensus.

### Section map (size, % of file, title)
{SECTION_MAP}

### The full artifact under review
<<<OPERATIONAL_DIRECTIVE>>>
{OPERATIONAL}
<<<END>>>

### Your tasks

Q1 — PRUNE THE EXPOSITION. Go section by section. For each NON-CORE section classify it
CUT (justification / narration / project-history / motivational prose a model does not
act on per turn — safe to remove), COMPRESS (operative instruction buried in exposition
— keep the instruction, cut the surrounding prose; estimate the char saving), or KEEP
(operative and lean). For CORE sections (constraint 1) mark KEEP. Give a rough total
char saving. Flag anything MISSING that falsification integrity needs but the directive
omits. Flag any element that is actively HARMFUL to tool-decidability.

Q2 — FALSIFY THE PRUNING METHOD. The plan: make the free cuts you identify, then run a
lean-vs-full ABLATION across all 5 models (temp 0, >=2 runs) scoring a per-model metric
(format compliance, testable-falsifier rate [the core signal], FFAFP admissibility, R_k
present, alternatives supplied, participation); bisect on any degradation to isolate the
load-bearing chunk and restore it; take the per-model UNION so no model is compromised to
shorten the file. Attack this. Could a cut pass the metric while quietly harming reasoning
the metric does not see? Is section-level ablation too coarse (cross-section interactions)?
Is there a cheaper or more reliable method?

### Constraints
Independent verdict — NO compelled consensus; give YOUR position and your single strongest
disagreement with the likely panel view. ~1200 words.

End with exactly:
  VERDICT on the pruning method = SOUND / SOUND-WITH-CAVEATS / UNSOUND
  CUT-LIST: section titles/numbers you would definitely cut (non-core only)
  COMPRESS-LIST: sections to compress, with rough char saving each
  KEEP-VERBATIM: confirm the core (constraint 1) stays untouched
  ONE-THING: the single highest-value prune, in one sentence.
"""

MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("cx",       "openai/gpt-5.5",                "openrouter"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]


def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, SYSTEM, PROMPT)
        elif route == "deepseek":
            resp = call_deepseek(model_id, SYSTEM, PROMPT)
        else:
            resp = call_openrouter(model_id, SYSTEM, PROMPT)
        ok = bool(resp and resp.strip())
        out = {"model": name, "ok": ok, "chars": len(resp or ""),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time() - t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""))
    return out


def main():
    print(f"=== directive-pruning panel review (pr, GUARDED) — {len(MODELS)} models ===")
    print(f"  artifact: {len(OPERATIONAL):,} chars, prompt: {len(PROMPT):,} chars")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            results[res["model"]] = res
    (LOGS / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok = [n for n, r in results.items() if r["ok"]]
    print(f"\n=== {len(ok)}/{len(MODELS)} responded: {ok} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
