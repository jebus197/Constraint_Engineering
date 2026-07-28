"""Panel review ('pr') — what must the CDSFL operational directive contain to
preserve project integrity, and is the proposed ablation method sound? (2026-06-06)

Founder-directed 'pr': cc2, cx, ge, cgpt, ds + sy, sth, f, e, d. Run WITHOUT
compelled convergence — each model gives an INDEPENDENT verdict + its strongest
falsification; disagreement is preserved as information and synthesized by CC1
(who also states its own position). Neutral framing: CC1's own keep/cut opinion
is deliberately NOT in the prompt (framing-confound avoidance).
Logs: bench/logs/confer_operational_pr_2026-06-06/.
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_operational_pr_2026-06-06"
LOGS.mkdir(parents=True, exist_ok=True)

OPERATIONAL = (REPO_ROOT / "bench" / "directives" / "universal"
               / "cdsfl_operational.md").read_text(encoding="utf-8")

# Programmatic section map (titles + sizes) so panelists can do a section-level
# keep/cut/test assessment without hand-counting.
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
    "CDSFL's founding rule: truth is decided by TOOLS and runnable checks, and "
    "when tools cannot decide, by a human — NEVER by model votes. You give an "
    "INDEPENDENT verdict; disagreement is wanted, not smoothed. Be rigorous, "
    "specific, and concrete; do not rubber-stamp."
)

PROMPT = f"""## Panel review: what must this operational directive contain to preserve project integrity — and is the method to decide that sound?

### Background
CDSFL reviews code/STEM with a panel of 5 AI models. Its core objectives ("integrity"):
- Truth decided by TOOLS / runnable checks, never by model consensus (votes).
- Popperian falsification: every critical finding must carry a RUNNABLE falsifier
  (code importing the real target) that the runner independently re-runs; that
  re-run, not the model's prose, decides CONFIRMED/REFUTED. Un-toolable -> human.
- FFAFP admissibility: findings must survive independent falsification (measured
  rate historically 0-13% without enforcement, 60-85% with it).
- R_k self-assessment (a per-finding risk metric) the runner re-derives and checks.
- Bold conjectures: each finding supplies an alternative (not just one solution).
- No model unable to participate and produce parsable, testable output.

The text below — the "operational directive", ~44,000 characters, 23 sections —
is appended IN FULL to every model's system prompt on EVERY turn. It is both a
fixed per-turn token tax and part of the input each model must attend to.

A concrete live failure has already occurred: one section instructs models to
write their falsification as the prose triad "FALSIFICATION (FALSIFIER / ATTEMPT
/ RESULT)". On a real run, this steered all 5 models to write PROSE falsifiers
(or none), so ZERO findings were tool-testable — the system's core was defeated
by the directive's own wording. So at least one element is actively harmful, and
the suspicion is that a large fraction is justification / narration / history
that a model does not act on per turn.

### Section map (size, % of file, title)
{SECTION_MAP}

### The full artifact under review
<<<OPERATIONAL_DIRECTIVE>>>
{OPERATIONAL}
<<<END>>>

### Your two tasks

Q1 — POSITIVE SPECIFICATION. State the MINIMAL set of elements this operational
directive must contain to preserve the integrity objectives above. Go
section-by-section through the 23 sections and classify each as KEEP
(load-bearing — removing it would degrade falsification rigor, tool-decidability,
admissibility, R_k, alternatives, or participation), CUT (justification /
narration / empirical-history a model does not act on per turn), or TEST
(genuinely uncertain — might aid compliance). Flag anything actively HARMFUL
(like the prose-falsifier wording) that must be CHANGED, and anything MISSING
that integrity requires but the directive omits.

Q2 — FALSIFY THE METHOD. The proposed way to decide the above empirically:
  (a) define a 6-dimension per-model metric — format compliance, testable-
      falsifier rate (the core), FFAFP admissibility, R_k present, alternatives,
      participation;
  (b) make free static cuts (provable duplication + pure narration nothing
      references);
  (c) ablate full-directive vs lean-directive across all 5 models, temp 0,
      >=2 runs, scoring the metric per model;
  (d) bisect on any degradation to isolate the load-bearing chunk, restore it;
  (e) take the per-model UNION (no model compromised to shorten the file).
Attack this. What would FALSIFY it? Strongest objections: Is the metric
sufficient to catch real degradation, or could a fix pass it while quietly
harming reasoning the metric doesn't see? Does temp-0 + 2 runs control model
stochasticity? Is ablation at the section level too coarse (interactions between
sections)? Is there a cheaper or more reliable method?

### Constraints
Independent verdict — NO compelled consensus; give YOUR position and your single
strongest disagreement with the likely panel view. Use analytical rigour where it
sharpens a claim. Word budget ~1200.

End with exactly:
  VERDICT on the ablation method = SOUND / SOUND-WITH-CAVEATS / UNSOUND
  KEEP-LIST: the section numbers you would definitely keep
  CUT-LIST: the section numbers you would definitely cut
  ONE-THING: the single most important change to make this directive preserve
  integrity with no waffle.
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
    print(f"=== operational-directive panel review (pr) — {len(MODELS)} models ===")
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
