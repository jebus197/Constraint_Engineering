"""Exp 41 fix-verification confer (2026-05-22).

An AI reviewer (CC1) folded two fixes into the maths model's convergence
detector (bench/dm/_convergence.py) and proposes returning the runner to
the original "first-principles" convergence design. CC1 had a DOCUMENTED
error tendency this session (misclassified material findings as iteration;
a verification-script bug that false-flagged a finding). So this confer is
an INDEPENDENT falsification check, not a rubber-stamp.

Panel: CC2 Opus 4.7, Codex GPT-5.5, Gemini 3.1 Pro, ChatGPT GPT-5.5,
DeepSeek V4 Pro. Star topology, compelled convergence, latest CDSFL schema.
Logs: bench/logs/confer_exp41_fix_verification_2026-05-22/.
"""
from __future__ import annotations
import concurrent.futures, json, os, sys, time
from datetime import datetime, timezone
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp41_fix_verification_2026-05-22"
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
## Independent fix-verification confer — find what is WRONG

You are auditing fixes an AI reviewer (CC1) made to a convergence-detection
module. CC1 erred repeatedly this session: it first called a set of panel
findings "immaterial refinements", then — only after a fold exposed it —
found one of those was a real material bug; and one of its own
verification scripts false-flagged a finding via a string-match. So DO NOT
assume CC1 is right now. Your job: try to FALSIFY these fixes and this
plan. Compelled convergence: converge on ONE verdict, but each model must
give the single strongest argument AGAINST the consensus and a
book-cooking self-check (is any of this making convergence easier rather
than more correct?).

### Context
bench/dm/_convergence.py = the maths model's ConvergenceDetector. Core
design (founder, §9.2): convergence is decided by kappa = min(kappa_set,
max(0,kappa_rate), kappa_adopt) >= tau_kappa, with a severity veto; gamma
is a DIAGNOSTIC decay curve, NOT a gating threshold. Findings are grouped
into equivalence classes via a similarity function; tau_sim is the merge
threshold. The similarity function has an embedding backend (active here,
sentence-transformers installed) that maps cosine to [0,1] via
cos01=(cos+1)/2. Empirically: similarity(unrelated findings) ~= 0.44-0.58;
similarity(identical) ~= 0.86.

### FIX 1 — kappa_rate (panel findings C0009/C0016/C0024/C0001/C0017/C0025)
BEFORE: rate(r) = |all round-r equivalence classes| / dt; baseline =
rate(round 1); special cases: if baseline<eps -> return 0.0 (no baseline,
no activity) or -1.0 (diverging). Problems: (a) counts ALL classes, so a
round that merely repeats prior findings keeps the rate up and blocks
convergence though novelty is zero; (b) a quiet/empty round 1 destroys the
baseline; (c) a genuinely quiet (converged) state returns 0.0 = "not
converged".
AFTER (verbatim):
    def kappa_rate(self, round_idx):
        if round_idx < 1: return 0.0
        def _novel_rate(r):
            dt = self._round_durations.get(r, 1.0)
            return len(self._novel_classes(r)) / max(dt, 1e-10)
        rate_r = _novel_rate(round_idx)
        peak = max((_novel_rate(r) for r in range(round_idx+1)), default=0.0)
        if peak < self.config.epsilon_conv:
            return 1.0  # no novelty ever -> no decline signal; do not veto
        return max(0.0, min(1.0, 1.0 - rate_r/(peak + self.config.epsilon_conv)))
Claim: this is the Duane-correct quantity (NEW discoveries per round,
decline from peak); a quiet state reads converged; removes brittle
special cases. Returns [0,1] (kappa() already did max(0,kappa_rate)).

### FIX 2 — novelty/similarity threshold (panel C0014/C0044/C0019/C0023)
BUG: ConvergenceDetector used config.tau_sim = 0.33 as the merge
threshold, but in embedding mode unrelated findings score ~0.48 (>0.33),
so EVERYTHING merges -> genuinely-novel findings (incl. a critical-severity
one) are treated as "already seen" -> never counted novel -> the severity
veto NEVER fires -> the module can declare convergence with an unaddressed
critical finding (false convergence). The config ALREADY defined
tau_sim_embed = 0.55 (calibrated for the embedding floor) but it was never
wired in.
FIX: a backend-aware selector effective_tau_sim(config) returns
tau_sim_embed (0.55) when the embedding backend is active, else tau_sim
(0.33); ConvergenceDetector's clustering + novelty checks now use it. At
0.55: identical(0.86)->merge; unrelated(0.44-0.49)->novel. The shared
similarity math is NOT changed (the runner's immune pipeline already
independently hardcodes tau_sim=0.50, so live experiments were unaffected;
the bug was isolated to this module).

### VERIFICATION CC1 RAN (verify the LOGIC; do not trust the numbers blindly)
- After both fixes: a novel critical finding is now detected novel -> veto
  fires -> converged()=False (the project's own veto test, previously
  passing for the WRONG reason, now passes correctly).
- 283 convergence/manager tests + 141 immune/feedback tests pass.
- A materiality sweep of all ~10 distinct panel finding-clusters: only the
  kappa_rate cluster and the novelty/similarity cluster flip a convergence
  verdict for a reachable input (= MATERIAL, fixed); the other ~7 (e.g.
  estimate_gamma edge case = diagnostic, never gates; kappa_set "can go
  negative" = never reached in 2000 random trials) are genuine but
  non-material footnotes -> iteration backlog (kept, not discarded).

### PROPOSED EXPERIMENTAL SCOPE ("return to first principles")
1. gamma stays a DIAGNOSTIC decay curve, never a gate (reverses an Exp-40
   "hardening" that had made gamma a strict >=0.30 conjunction gate, which
   made convergence unreachable for any target with >=8 findings).
2. Convergence = no new GENUINE (verifier-surviving) discoveries for K
   consecutive rounds (the top of the decay curve). K ~ 3.
3. The specialist verifier (z3/mypy vs source AST) filters/classifies
   findings; it is promoted from shadow to live.
4. Materiality (fundamental defect that must block vs iteration refinement
   to defer) is a HIL-in-post decision, INFORMED by an objective tool-test:
   does a finding flip a real convergence verdict for a reachable input?
   Genuine-but-immaterial findings are backlogged, never discarded.
5. Re-run Exp 41 on the same frozen target as a controlled A/B.

### YOUR TASKS (converge on ONE position)
Q1. Do FIX 1 and FIX 2 check out — correct, no new defects, faithful to
    the convergence math? Name any case where kappa_rate (new) or
    effective_tau_sim gives a wrong/contract-violating result. Specifically
    stress: kappa_rate when novelty re-accelerates late; the peak-baseline
    choice; effective_tau_sim when a caller passes a custom (non-embedding)
    similarity_fn while embedding is installed (threshold/backend mismatch).
Q2. Is the experimental scope reasonable and integrity-preserving, or does
    any element risk book-cooking (making convergence easier rather than
    more correct)? Is "gamma diagnostic, kappa gates" sound, given gamma
    was the founding decay concept?
Q3. Anything CC1 STILL has wrong or missing (e.g. _manager.py has the same
    tau_sim bug on an operational path but with an adaptive-threshold
    complication — flagged, not fixed; is deferring it acceptable?).

Word budget: 1200. State your verdict as: FIXES = SOUND / SOUND-WITH-CONDITIONS / UNSOUND,
and SCOPE = REASONABLE / REASONABLE-WITH-CONDITIONS / UNREASONABLE.
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
        out = {"model": name, "route": route, "ok": ok,
               "chars": len(resp or ""), "elapsed_s": round(time.time()-t0, 1),
               "response": resp or ""}
    except Exception as e:  # noqa: BLE001
        out = {"model": name, "route": route, "ok": False, "error": f"{type(e).__name__}: {e}",
               "elapsed_s": round(time.time()-t0, 1), "response": ""}
    (LOGS / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars',0)} {out['elapsed_s']}s"
          + (f" ERR={out.get('error')}" if not out['ok'] else ""))
    return out

def main():
    print(f"=== Exp 41 fix-verification confer — {len(MODELS)} models ===")
    print(f"prompt {len(PROMPT)} chars; logs -> {LOGS}")
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
