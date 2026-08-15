"""Panel review (pr): specialist-cell deployment for the synth-module
experiments and Bench Run 2. Founder-approved brief, 2026-07-28.

Five-model dispatch under the full CDSFL directive; independent verdicts;
NO compelled convergence — disagreement is preserved as information.
Brief framing is neutral per the standing framing-confound rule; models are
instructed that source files outrank this brief (the Round-3 precedent).
"""
from __future__ import annotations
import concurrent.futures
import json
import os
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_specialist_cells_pr_2026-07-28"
LOGS.mkdir(parents=True, exist_ok=True)

SYSTEM = (REPO_ROOT / "bench" / "directives" / "universal"
          / "cdsfl_core_formal.md").read_text(encoding="utf-8")

# Grounding excerpts (source-anchored, per the Round-3 stale-anchor lesson)
_toml_dir = REPO_ROOT / "bench" / "cdsfl_registry" / "domains" / "immune"
CHEM_TOML = (_toml_dir / "chemistry.toml").read_text(encoding="utf-8")
ENG_TOML = (_toml_dir / "engineering.toml").read_text(encoding="utf-8")
CROSS_TOML = (_toml_dir / "cross_domain.toml").read_text(encoding="utf-8")
_task_dir = REPO_ROOT / "bench" / "tasks_frontier"
_task_sample = sorted(_task_dir.glob("FT-0*.json"))[:3]
TASK_SAMPLES = "\n\n".join(
    f"--- {p.name} ---\n" + p.read_text(encoding="utf-8")[:2000]
    for p in _task_sample)

PROMPT = f"""CDSFL PANEL REVIEW: Specialist-Cell Deployment for the Synth-Module
Experiments and Bench Run 2.

Method: independent verdict; your strongest falsification of YOUR OWN position
per question; FFAFP discipline; disagreement is information — do NOT converge
toward an assumed consensus. Where this brief conflicts with repository source
files, THE SOURCE FILES WIN (established precedent: a prior panel majority
anchored to stale brief text was wrong; the source-anchored dissent was right).

SETTLED CONSTRAINTS (context, not for re-litigation):
- The specialist layer is BUILT and LIVE in all eight domains (mathematics,
  statistics, biology, information_science, software, physics, chemistry,
  engineering). A specialist is one manifest-driven dispatch function
  parameterised by a per-domain TOML: claim classified -> routed to the
  domain's tool list -> manifest verifier decides -> CellVerdict. Cells are
  NOT tools; a domain routes claims across MULTIPLE tools.
- Synthesised native modules were chosen over adapted third-party content
  (5/5, in two separate panel rounds; rationale: adapting external content
  conflates search-quality metrics with target validity).
- Module spec (locked): 15-25K chars; 4-6 falsifiable claim clusters; each
  cluster names its falsifiability route and tools; AT LEAST ONE intentionally
  false claim planted (a module producing only confirmations demonstrates
  nothing about discriminative capacity); drafted ahead of the experiment and
  reviewed before use.
- Current runner mechanics load ONE domain config per run (cfg.domain).
- Specialist purpose on record: the per-domain noise filter upstream of the
  convergence measure ("only verifier-surviving findings count as genuine
  discoveries"), and the executable form of "tools decide, not votes".
- Bench Run 2 = 27 frontier STEM tasks (on disk; 3 samples below): the panel
  PRODUCES AND FALSIFIES SOLUTIONS to real STEM problems — not code review.
  Deliberate difficulty band: 10-50% single-pass model accuracy.

THE FIVE QUESTIONS (answer each; number your answers):

Q1 — TOPOLOGY. For the synth-module experiment(s): one consolidated
multi-domain module, four per-domain modules, or another arrangement?
Constraints to weigh: one domain config per run; cross_domain.toml is NOT in
the live specialist set and its routes omit stoichiometric_balance,
linear_programming, and astronomical (see TOML below); measured cost is
roughly 6-20 dollars per small-target run; the purpose is ground-truthed
recall measurement plus specialist validation before Bench Run 2. State
explicitly what your chosen arrangement measures and what it forgoes.

Q2 — COVERAGE GAPS. Chemistry's locked brief has no logical and no
statistical cluster; engineering's has no logical cluster — though their
TOMLs route those claim types (TOMLs below). Propose the missing clusters to
the standard of the existing briefs: each names its falsifiability route and
tools, and the set includes at least one planted false claim.

Q3 — THE EARN-THEIR-KEEP METRIC. "Specialist verdict count > 0" is obsolete
now all domains are live. Define the pass criteria the synth experiments must
meet for the specialist layer to be declared VALIDATED for Bench Run 2.
Candidates present in the project record: planted-false-claim recall; a
decision-changed tally (specialist verdicts that altered a finding's final
status); non-distortion versus the governing pass condition. Propose criteria
AND thresholds, and say what evidence would falsify "the specialists earn
their keep".

Q4 — THE NON-CODE FINDING SCHEMA (the Bench Run 2 bridge). Findings currently
require file-and-line citations plus a RUNNABLE falsifier that the runner
re-executes. Bench Run 2 tasks have no code to cite. Specify the
claim + evidence + falsifier schema for non-code STEM claims: what is a
runnable falsifier for a proof step, a stoichiometric balance, a buckling
calculation? What role does the specialist dispatch play when the artefact
under review is a SOLUTION rather than a module?

Q5 — FACTORIAL TARGET. For the 2x2 feedback/divergence-directive factorial:
the runner-tests-runner self-test candidate, a fresh synthesised module, or
another target — given frozen-threshold requirements and baseline-cell
integrity. State the strongest objection to your own choice.

END WITH exactly this structure:
  Q1-POSITION / Q1-FALSIFICATION
  Q2-CLUSTERS (chemistry) / Q2-CLUSTERS (engineering)
  Q3-CRITERIA (with thresholds) / Q3-FALSIFICATION
  Q4-SCHEMA / Q4-SPECIALIST-ROLE
  Q5-POSITION / Q5-OBJECTION

GROUNDING — chemistry.toml:
{CHEM_TOML}

GROUNDING — engineering.toml:
{ENG_TOML}

GROUNDING — cross_domain.toml:
{CROSS_TOML}

GROUNDING — three sample Bench Run 2 tasks (truncated):
{TASK_SAMPLES}
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
    print(f"=== specialist-cells panel review (pr) — {len(MODELS)} models ===")
    print(f"  prompt: {len(PROMPT):,} chars (system: {len(SYSTEM):,})")
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
