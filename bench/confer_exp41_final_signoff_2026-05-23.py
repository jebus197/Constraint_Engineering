"""Exp 41 convergence + reframe — FINAL SIGN-OFF sprint review (2026-05-23).

Six-model neutral sign-off before implementation. Adds CX2 = Codex via the CLI
(`codex exec`, ChatGPT login, read-only sandbox, run from /tmp) alongside the
five API/CLI routes. Framing: robust WORKING PLATFORM, not exhaustive flaw
enumeration; diminishing returns applied to the review itself (material blockers
only). Recommendations were SymPy-verified before dispatch.

Panel: CC2 Opus 4.7, CX1 Codex GPT-5.5 (OpenRouter), CX2 Codex (CLI),
Gemini 3.1 Pro, ChatGPT GPT-5.5, DeepSeek V4 Pro. Star topology, compelled
convergence. Logs: bench/logs/confer_exp41_final_signoff_2026-05-23/.
"""
from __future__ import annotations
import concurrent.futures, json, os, subprocess, sys, tempfile, time
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_exp41_final_signoff_2026-05-23"
LOGS.mkdir(parents=True, exist_ok=True)
CDSFL = (REPO_ROOT / "bench" / "directives" / "universal"
         / "cdsfl_core_formal.md").read_text(encoding="utf-8")

MODELS = [
    ("cc2",      "opus",                          "claude_cli"),
    ("cx",       "openai/gpt-5.5",                "openrouter"),
    ("cx2",      "codex-cli",                     "codex_cli"),
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]


def call_codex_cli(system_prompt: str, user_prompt: str, timeout: int = 600) -> str:
    """Dispatch to Codex via the CLI (ChatGPT login, read-only sandbox, /tmp cwd).

    Captures the agent's final message via --output-last-message. Prompt is fed
    on stdin (large directive). read-only sandbox + /tmp cwd ensure the confer
    cannot modify the repo.
    """
    full = f"SYSTEM DIRECTIVE:\n{system_prompt}\n\n---\n\n{user_prompt}"
    outf = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name
    cmd = [
        "codex", "exec",
        "-s", "read-only",
        "-C", "/tmp",
        "--skip-git-repo-check",
        "--color", "never",
        "-o", outf,
        "-",
    ]
    try:
        r = subprocess.run(cmd, input=full, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            return Path(outf).read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    ans = ""
    try:
        ans = Path(outf).read_text(encoding="utf-8").strip()
    except OSError:
        ans = ""
    if not ans:
        ans = (r.stdout or "").strip()
    return ans


PROMPT = r"""
## Final sign-off review: is this plan sound enough to BUILD? (sprint)

This is a final, independent sign-off before implementation. The objective is a
ROBUST WORKING PLATFORM that demonstrates multi-model falsification converging
honestly on real targets — NOT a system that enumerates every possible flaw
class. **Apply diminishing returns to THIS review**: flag only MATERIAL problems
(things that would make the platform not work, or that are mathematically
unsound / indefensible). Do NOT generate marginal nitpicks or speculative
"could be better" items — that over-production is the failure mode the project
is escaping. Hard deadline; this is a sprint.

Compelled convergence: return ONE verdict — APPROVE / APPROVE-WITH-CONDITIONS /
REJECT — conditions being genuine blockers only. Each model also gives its single
strongest argument against the verdict, and a book-cooking self-check.

### Already settled (verified by two prior neutral panels + SymPy; do NOT re-litigate)
- Convergence = the genuine critical/material decay curve flattening.
- gamma = 1 - beta, computed on the verifier-filtered CRITICAL series; HIGH gamma
  = converged (SymPy + live code confirmed: a flat tail gives gamma = 1.0).
- The discovery RATE decays to zero while DIFFICULTY (1/rate) rises to infinity —
  the same exhaustion. "Diminishing returns" is the unifying frame (SymPy
  confirmed: rate decays for beta<1; 1/rate -> infinity; marginal risk-reduction
  dR -> 0 as residual risk R -> 0).
- The whole-history slope LAGS (a late critical leaves gamma high at 0.926); the
  recent-quiet COUNT is the accurate recency detector (it resets on the late
  critical).

### The plan to sign off (consolidated)
**Convergence (code).** Converge when the state gate is clean (no open criticals)
AND there are 3 consecutive rounds with zero NEW genuine criticals (verifier-
filtered). gamma is computed and REPORTED on BOTH the critical and all-severity
series (labelled), reading ~1.0 at a genuine convergence; it is the founding
decay-curve criterion, not a separate numeric gate. No 0.30 trigger, no 0.85, no
control-rule schedule. Keep the prior fixes (novel-rate metric correction;
embedding-similarity threshold fix that prevented false convergence; genuine /
verifier-filtered novelty feed; live software verifier). The old "hardened
conjunction gate" stays OFF (it had made convergence unreachable).

**Verification flow.** Intelligent models judge materiality/value; a MECHANICAL
verifier (tools) then confirms each included finding is real; only confirmed
genuine criticals count toward the series.

**Model instruction (directive reframe).** The job is the best efficient solution
and the material defects that decide whether it works — framed as DIMINISHING
RETURNS: weigh marginal value against effort; prioritise high-value findings;
converge when further effort yields only marginal value. VALUE-weighted, NOT
count-weighted, with an explicit guard that a plausibly-reachable HIGH-value late
finding still justifies continuing (so a late deep finding is not skipped).

**Doc fixes.** Correct an inverted convergence condition in the maths appendix
(an old gate documented "gamma < 0.35 = converged", backwards vs the live code
where high gamma = converged); add a note stating the rate-decay / difficulty-
rise / diminishing-returns duality.

**Then.** Run the planned experiment arc (42 -> 54) under this reframe and the
frozen rule; verify; write up; hand to the community.

### Questions
Q1. Is the convergence design sound, mathematically defensible, and SUFFICIENT
    for a robust working platform? Name any element that is actually UNSOUND (not
    merely improvable).
Q2. Is the diminishing-returns / value-weighted reframe sound, and does it
    correctly avoid premature stopping on a high-value late finding? Any real
    failure mode?
Q3. Are the two doc fixes correct?
Q4. Is there any GENUINE BLOCKER to shipping a robust working platform on this
    plan? (Diminishing returns applies to your answer: material only.)
Q5. Extrapolate: implications for robustness, the verifier/classifier as the
    remaining dependency, and the next phase (distributed compute / scaling).

Verdict: APPROVE / APPROVE-WITH-CONDITIONS / REJECT. Word budget ~800.
"""


def dispatch(name, model_id, route):
    t0 = time.time()
    try:
        if route == "claude_cli":
            resp = call_claude_cli(model_id, CDSFL, PROMPT)
        elif route == "codex_cli":
            resp = call_codex_cli(CDSFL, PROMPT)
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
    print(f"=== FINAL SIGN-OFF sprint review — {len(MODELS)} models ===")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(dispatch, n, m, r): n for n, m, r in MODELS}
        for f in concurrent.futures.as_completed(futs):
            res = f.result(); results[res["model"]] = res
    (LOGS / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok = [n for n, r in results.items() if r["ok"]]
    print(f"\n=== {len(ok)}/{len(MODELS)} responded: {ok} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
