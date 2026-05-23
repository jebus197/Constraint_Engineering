"""Exp 41 gamma-unification confer (2026-05-22, late).

After exp41c converged cleanly at round 6 via the zero-novel-critical COUNT
path while the runner's reported gamma (on the ALL-severity series) sat at
0.240, the founder asked: shouldn't the decay-slope gamma and the
zero-novel-critical count be ONE quantity, not two that can disagree /
race? They appear to measure the same thing (the decay curve going flat).

Data finding (CC1, on the exp41c run): the apparent disagreement was a
POPULATION mismatch, not a lag and not two different measures. Gamma on
the genuine CRITICAL series [3,0,0,0,0,0,0] = 1.000 (flat cumulative after
round 0) — it AGREES with the count. The 0.240 was gamma on the broader
all-severity series (footnotes still trickling). A "recent-window gamma"
idea was tried and REJECTED: an all-zero window makes the estimator return
0.0 (its no-data branch), the opposite of high.

PROPOSAL to review (falsify it): unify to ONE measure — gamma computed on
the GENUINE (settled, verifier-filtered) CRITICAL series; the
K-consecutive-zero-novel-critical count is the DISCRETE form of the same
statement (flat critical tail <=> gamma_crit high). Convergence = gamma_crit
>= threshold, with the count as its by-construction confirmation.

Panel: CC2 Opus 4.7, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, compelled convergence, latest CDSFL schema.
Logs: bench/logs/confer_exp41_gamma_unify_2026-05-22/.
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp41_gamma_unify_2026-05-22"
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
## Confer: should the two convergence measures be unified into one gamma?

Falsify this proposal; do not rubber-stamp. Compelled convergence: one
verdict, but each model gives the single strongest argument AGAINST the
consensus and a book-cooking self-check. CRITICAL founder constraint: do
NOT endorse anything that risks making convergence UNREACHABLE again (a
prior "hardened" gamma gate did exactly that).

### Background (verified on the live exp41c run)
The convergence detector exhausts a finite defect space; gamma = 1 - beta,
where beta is the log-log slope of cumulative novelty vs round (gamma high
=> discovery has flattened => converged). There are two signals in play:
(1) gamma (continuous slope), and (2) a COUNT: K consecutive rounds with
zero novel CRITICAL findings.

exp41c (the corrected runner on the now-fixed module) converged at round 6
via the COUNT path. The runner's REPORTED gamma was 0.240 ("weak depletion,
maybe premature"). That looked like the count terminating early while gamma
disagreed — i.e. like a hack / gamma demotion.

DATA FINDING: the 0.240 was gamma on the ALL-SEVERITY novelty series
[3,2,1,1,1,0,1] (non-critical footnotes still trickling). Gamma on the
GENUINE CRITICAL series [3,0,0,0,0,0,0] (3 criticals in round 0, then zero)
= 1.000 — it AGREES with the count. So the apparent disagreement was a
POPULATION MISMATCH (gamma shown on all-severity vs count judged on
criticals), NOT a real divergence and NOT a lag. (A "recent-window gamma"
was also tried and REJECTED: an all-zero window makes the estimator return
0.0 — its no-data branch — i.e. low exactly when discovery has stopped.)

### PROPOSAL to review
Unify to ONE measure: gamma computed on the GENUINE (settled,
verifier-filtered) CRITICAL series. The "K consecutive zero-novel-critical
rounds" count is the DISCRETE form of the SAME statement — a flat critical
tail <=> gamma_crit near 1.0. Convergence = gamma_crit >= threshold (e.g.
0.30), and the count is its by-construction confirmation; they cannot
disagree because they read the same series. gamma stays fully load-bearing
(it reads ~1.0 at a genuine convergence), reported as the headline number.

### The founder's challenge (address it directly)
"I struggle to see how this is anything NEW — both just measure when the
decay curve is steep/depleted enough that no meaningful new discoveries are
being made. They are not fundamentally different quantities. Shouldn't they
simply be one combined gamma that triggers convergence?"

### Questions (converge on ONE position)
Q1. Is the founder correct that these are the SAME quantity (the genuine-
    critical decay), so 'unification' is really just (a) computing gamma on
    the same population the count judges, and (b) treating the count as its
    discrete confirmation? Or is there a genuine, load-bearing difference
    between the continuous slope and the discrete count that must be kept?
Q2. Does gating on gamma_crit >= threshold (over the GENUINE critical
    series) risk recreating the "convergence impossible" failure? The prior
    hardened gate stuck at gamma_crit=0.0 because it was fed RAW,
    over-produced criticals (never flat); fed GENUINE criticals it reads
    1.0 when they stop. Is "clean input, not changed measure" a sound
    resolution, or does a real impossibility risk remain (e.g. a target
    with many genuine criticals, a slope that rises too slowly, threshold
    miscalibration)? Recommend a threshold and whether to keep the count as
    a guard.
Q3. Does the unified version read as principled (the maths model's gamma
    reaching its threshold) rather than a hack / early termination / gamma
    demotion? Any remaining way it could be gamed or look like cooking?

Word budget: 1000. Verdict: UNIFY = SOUND / SOUND-WITH-CONDITIONS / UNSOUND;
IMPOSSIBILITY-RISK = LOW / MEDIUM / HIGH.
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
    print(f"=== gamma-unification confer — {len(MODELS)} models ===")
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
