"""Exp 41 gamma convergence — FINAL FORM confer (2026-05-23).

The prior neutral panel converged on: gamma on the critical population; report
both gammas; require BOTH decay (gamma) and recency (zero-critical count);
classifier is the new single point of failure; matches the maths model. ONE
question remained: the exact FORM of "both required" — a flat AND, or Codex's
control rule where gamma sets the required quiet-tail length. This bounded round
adjudicates that, with the decisive criterion being that gamma must be GENUINELY
(not cosmetically) load-bearing — the founder's explicit credibility concern.

Panel: CC2 Opus 4.7, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, compelled convergence, latest CDSFL schema.
Logs: bench/logs/confer_exp41_gamma_form_2026-05-23/.
"""
from __future__ import annotations
import concurrent.futures, json, os, sys, time
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp41_gamma_form_2026-05-23"
LOGS.mkdir(parents=True, exist_ok=True)
CDSFL = (REPO_ROOT / "bench" / "directives" / "universal"
         / "cdsfl_core_formal.md").read_text(encoding="utf-8")

MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

PROMPT = r"""
## Confer (narrow): the final FORM of the convergence rule

A prior neutral panel already converged on the points below. Treat them as
SETTLED, not for re-litigation:
  - gamma is computed on the verifier-filtered CRITICAL / material findings
    (not the all-severity series);
  - both gammas (critical + all-severity) are reported, always population-labelled;
  - convergence requires BOTH a decay signal (gamma) AND a recency signal (zero
    new criticals for K rounds) on that critical population — neither alone;
  - the severity classifier becomes the main point of failure (guarded by
    pre-registration + audit + showing the excluded all-severity data);
  - this MATCHES the maths model (a finite defect space whose discovery decays as
    it exhausts); no model revision, only a population index on gamma.

ONE question remains: the exact FORM of "both required". Adjudicate between these
candidates, or propose a clearly-better hybrid:

  Design A — flat AND.
    Converge when  gamma_crit >= T  AND  z >= K     (e.g. T = 0.30, K = 3),
    where z = consecutive most-recent rounds with zero new criticals.
  Design A' — flat AND with a higher bar (e.g. T = 0.85) so gamma bites more often.
  Design B — gamma controls the evidence burden (Codex's control rule).
    Converge when state gate clean AND z >= K_required(gamma_crit), with a finite,
    pre-declared schedule, e.g.:
       gamma_crit >= 0.30      -> K_required = 3
       gamma_crit <  0.30      -> K_required = 5
       gamma_crit unestimable  -> K_required = 5  (+ explicit "gamma undefined")

Decision criteria (ALL must hold):
  (1) Convergence stays REACHABLE — a finite quiet-tail always terminates a
      genuinely-exhausted critical space (no impossibility).
  (2) Gamma is GENUINELY load-bearing — it must demonstrably CHANGE the outcome
      in plausible cases, not merely rubber-stamp the count. This is the decisive
      concern: the project's credibility rests on the decay curve actually meaning
      something. A rule where gamma is formally present but never changes a
      decision FAILS this criterion.
  (3) Defensible to a sceptical reviewer; auditable; as simple as possible but no
      simpler.

The specific tension to resolve: in Design A at T = 0.30, whenever z >= 3 holds on
the critical series, gamma_crit is almost always ALREADY high (a flat 3-round tail
forces a low slope), so gamma may be REDUNDANT — cosmetically load-bearing. Does
A' (higher T) fix that without risking reachability? Does B fix it better by making
gamma change K? Is there a cleaner hybrid?

Grounding data — real gamma estimator + K=3 count on per-round CRITICAL series:
  clean stop    [3,0,0,0,0,0,0]   gamma 1.000   z>=3 yes
  late crit     [3,0,0,0,0,0,1]   gamma 0.926   z>=3 no
  slow trickle  [1,0,0,1,0,0,1]   gamma 0.436   z>=3 no
  still finding [3,2,2,2,2,2,2]   gamma 0.169   z>=3 no

Questions:
  Q1. Which design (A, A', B, or a hybrid) best satisfies criteria (1)-(3), and
      specifically makes gamma genuinely (not cosmetically) load-bearing?
  Q2. Give concrete parameters (T and/or the K schedule).
  Q3. Under your choice, name a plausible run where gamma CHANGES the outcome
      (demonstrate gamma is not redundant). If you cannot, your choice fails (2).
  Q4. Falsify your own choice (strongest argument against) + a book-cooking check
      (could gamma still be cosmetic; could this be threshold-shopping?).

Compelled convergence: ONE recommendation. Word budget ~800.
"""

def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, CDSFL, PROMPT)
        elif route == "deepseek":
            resp = call_deepseek(model_id, CDSFL, PROMPT)
        else:
            resp = call_openrouter(model_id, CDSFL, PROMPT)
        ok = bool(resp and resp.strip())
        out = {"model": name, "ok": ok, "chars": len(resp or ""),
               "elapsed_s": round(time.time()-t0, 1), "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time()-t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars',0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out['ok'] else ""))
    return out

def main():
    print(f"=== gamma FINAL-FORM confer — {len(MODELS)} models ===")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result(); results[res["model"]] = res
    (LOGS / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok = [n for n, r in results.items() if r["ok"]]
    print(f"\n=== {len(ok)}/{len(MODELS)} responded: {ok} ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
