"""Exp 41 gamma convergence — NEUTRAL panel review (2026-05-23).

The founder asked for a fully neutral confer: present the situation and the
facts, state both hard constraints with equal weight, supply the raw data, and
ask the open question "what should we do?" — WITHOUT pre-selecting an answer or
leading the panel toward keeping or dropping either measure. CC1's own
conclusion is deliberately excluded from the prompt so the panel reasons
independently; we then compare.

Panel: CC2 Opus 4.7, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, compelled convergence, latest CDSFL schema.
Logs: bench/logs/confer_exp41_gamma_neutral_2026-05-23/.
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp41_gamma_neutral_2026-05-23"
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
## Confer: how should convergence be measured and triggered? (open question)

This is a genuinely OPEN design question. No answer is preferred; do not assume
one. Reason from first principles, recommend what you think is best, then try
hard to falsify your own recommendation. Compelled convergence: the panel
returns ONE recommendation, but each model must also give the single strongest
argument AGAINST that recommendation plus a book-cooking self-check.

### The maths model (context, not under review)
The convergence detector models a review that exhausts a finite defect space.
As the space is exhausted, the number of genuinely-new discoveries per round
declines toward zero — a decay curve. gamma = 1 - beta, where beta is the
log-log slope of cumulative novelty vs round; gamma near 1 means the cumulative
curve has flattened (discovery has stopped). The decay curve is the founding
concept of the project.

### Two signals currently in play
Convergence is currently declared if EITHER of these fires (an OR), plus a
separate state-based gate:
  (1) gamma (the continuous slope above) >= 0.30, recomputed each round; and
  (2) a COUNT: K = 3 consecutive rounds with zero new CRITICAL findings, on the
      settled, verifier-filtered series.

### Project history (factual)
The decay curve (gamma) was the original convergence metric, and for a long
stretch the ONLY one. The specific 0.30 value and the consecutive-zero-critical
count were later additions. It is not certain gamma's threshold was always 0.30.

### Two hard constraints — any answer must satisfy BOTH, equally
  (A) Convergence must never become UNREACHABLE. A prior "hardened" design that
      REQUIRED gamma to clear a bar (an AND condition) made convergence
      effectively impossible and had to be removed.
  (B) The decay-curve / gamma must remain LOAD-BEARING — it must not be reduced
      to a decorative diagnostic that plays no role in declaring convergence.
      (Founder standing ruling; the decay curve is the project's core claim.)
These two pull in different directions. Resolving that tension is the task.

### A live result to ground the discussion (run exp41c, on a sound module)
The run converged at round 6 via signal (2): the per-round CRITICAL series was
[3,0,0,0,0,0,0] (3 criticals in round 0, then zero), giving a zero tail
[0,0,0]. The gamma DISPLAYED was 0.240 — but that was gamma on the ALL-severity
series [3,2,1,1,1,0,1] (non-critical footnotes still trickling). gamma on the
CRITICAL series [3,0,0,0,0,0,0] is 1.000. So the SAME run yields gamma = 0.240
(all findings) or gamma = 1.000 (criticals only), depending on the population
gamma is measured on.

### Estimator behaviour (raw data — interpret it yourselves)
The real gamma estimator and the K=3 zero-critical count, on five per-round
CRITICAL patterns:
  series                          gamma(slope)   slope>=0.30?   count(3-zero)?
  clean stop   [3,0,0,0,0,0,0]       1.000          yes             yes
  late crit    [3,0,0,0,0,0,1]       0.926          yes             no
  late crit x2 [3,0,0,0,0,0,2]       0.868          yes             no
  slow trickle [1,0,0,1,0,0,1]       0.436          yes             no
  still finding[3,2,2,2,2,2,2]       0.169          no              no
(A "recent-window gamma" — slope over only the last few rounds — was tried and
found degenerate: an all-zero window makes the estimator return 0.0, its no-data
branch, i.e. low exactly when discovery has stopped.)

### The question — what should we DO?
How should convergence be measured and triggered, given all of the above?
Consider the FULL option space, including but not limited to:
  - keep gamma's slope as an independent trigger (with a threshold);
  - make the count the trigger and report gamma as continuous evidence;
  - require both (AND); allow either (OR); combine them another way;
  - on which population(s) gamma should be computed and reported.

Address directly:
  Q1. Which design best satisfies BOTH hard constraints (A) and (B) at once,
      and why?
  Q2. What is the real relationship between the continuous slope and the
      discrete count — the same quantity, two different quantities, or two
      readings of one thing? Does the estimator-behaviour data change your view?
  Q3. How should gamma be reported so the result is honest and not misleading,
      given the population issue (0.240 vs 1.000 for the same run)?
  Q4. Does your recommendation risk EITHER false convergence (stopping with a
      genuine critical still open) OR impossibility (never converging)? Where
      does the residual risk live, and how is it controlled?
  Q5. Is your recommendation defensible to a sceptical outside reviewer, and
      does it MATCH the maths model's predictions or require revising the model?
  Q6. Extrapolate: what does your answer imply for other targets, domains, or
      scales beyond this single run?

Word budget: ~1100. Give ONE recommendation. Then: the single strongest
argument against it, and a book-cooking self-check (could this be dressed-up
early termination, or gamma demotion in disguise?).
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
    print(f"=== gamma NEUTRAL panel review — {len(MODELS)} models ===")
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
