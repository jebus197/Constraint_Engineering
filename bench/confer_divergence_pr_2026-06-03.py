"""Panel review ('pr') — falsify the completed divergence study + design the
scaling/decomposition architecture (2026-06-03).

Founder-directed 'pr' (new MC command): cc2, cx, ge, cgpt, ds + sy, sth, f, e,
d, t. CX2 (Codex CLI) added as 6th panelist per founder endorsement. Run
WITHOUT compelled convergence — the study finds consensus-forcing is the disease;
each model gives an INDEPENDENT verdict + its strongest falsification + design
vision; disagreement is preserved as information and synthesized by CC1 (who
also participates). Logs: bench/logs/confer_divergence_pr_2026-06-03/.
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

LOGS = REPO_ROOT / "bench" / "logs" / "confer_divergence_pr_2026-06-03"
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
    full = f"SYSTEM DIRECTIVE:\n{system_prompt}\n\n---\n\n{user_prompt}"
    outf = tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name
    cmd = ["codex", "exec", "-s", "read-only", "-C", "/tmp",
           "--skip-git-repo-check", "--color", "never", "-o", outf, "-"]
    try:
        subprocess.run(cmd, input=full, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    try:
        return Path(outf).read_text(encoding="utf-8").strip()
    except OSError:
        return ""


PROMPT = r"""
## Panel review: falsify this diagnosis of a multi-AI system, and design its scaling layer

You are reviewing a completed forensic study of a system called CDSFL: a
multi-model scientific-falsification architecture whose goal is to use many AI
models, Popperian-falsification-style, to solve STEM problems — ultimately at
distributed scale (a "Global Mind"), the way SETI@home / Folding@home / ZetaGrid
used distributed raw compute, but with intelligence injected.

Do NOT rubber-stamp. Your two jobs: (1) try hard to FALSIFY the diagnosis below;
(2) inject concrete design vision on the scaling question. There is NO compelled
consensus — give YOUR independent position; disagreement is wanted as
information, not smoothed away.

### The completed study's claims (verified where noted)

CLAIM A — single root cause. The system drifted from its own founding rule
("the system does not rely on model consensus to decide what is true; it relies
on tools, and when tools cannot decide, on the HIL") into deciding truth by
model VOTING (CONFIRM/CHALLENGE) and forced agreement ("compelled convergence,"
added late as a desperation patch). All observed failures — a verifier that
can't ground prose claims, falling back to votes; "5 models barely better than
1"; endless bug-hunting that never converges on a built solution — are argued to
be faces of this ONE regression: truth-by-discussion replacing truth-by-tools.

CLAIM B — the correct pattern already exists. For the maths model (a per-finding
risk metric R_k), the runner ALREADY computes R_k independently and validates
the model's self-reported value against its own recomputation (model_rk vs
recomputed_rk). So "model reasons + self-reports, runner independently verifies
as a failsafe" is already implemented — for R_k. The fix proposed is to
propagate that pattern to per-finding claims (a finding carries a runnable
check; the runner runs it), and delete the voting.

CLAIM C — the scaling "contradiction" is dissolved (SymPy/NumPy-verified). The
founding coverage model D(n)=1-(1-p)^n has geometric diminishing returns
(optimal panel n*≈4-6) and monoculture collapse (correlation rho->1 makes
D(50)≈D(1)). This is NOT a ceiling on the system: small-n governs the PANEL PER
UNIT; SCALE comes from DECOMPOSITION (number of independent units). 1000 models
= 200 units x 5, giving 200x throughput; 1000 models on ONE artifact ≈ D(6),
wasted. So "more compute should help" is true for DECOMPOSABLE problems, false
for redundant review — a granularity question, not a contradiction.

CLAIM D — BOINC/ZetaGrid analogy. BOINC validates work units by
replication+quorum-CONSENSUS precisely because volunteer clients are
unverifiable black boxes (no tool can check a raw result, so it votes). That is
the exact analogue of CDSFL's voting committee — and CDSFL's whole reason to
exist is that it does NOT need it (it has tools + the maths model to verify
directly). The system regressed to BOINC's vote while discarding its advantage.
ZetaGrid (checked 10^13 Riemann zeros) is the precedent for scale: decompose
into independent ranges, validate by recomputation (not voting), with
falsification native (one misaligned zero disproves the Riemann Hypothesis).

### FALSIFY (attack these directly)
F1. Is "truth-by-discussion" genuinely the SINGLE root cause, or does collapsing
    distinct failures into one story hide independent problems?
F2. Does CLAIM B actually transfer? Per-finding claims about code/STEM may be
    fundamentally harder to tool-verify than a closed-form R_k. Are there large
    classes of genuine, important findings that NO tool can decide — so that
    either HIL or some model-judgement step is unavoidable? If so, the "delete
    the vote" prescription is incomplete.
F3. Is the BOINC-quorum analogy sound, or does multi-model REASONING (unlike raw
    compute) genuinely need a deliberation/aggregation step that tools cannot
    replace — i.e. is some "consensus" actually load-bearing for hard problems?

### DESIGN (the founder's real question — be concrete)
D1. To solve a BIG STEM problem (worked example: searching for an optimal path
    toward the Riemann Hypothesis) with 5-6 OR 500 models, how do you DECOMPOSE
    the labour into tool-settleable units and RECOMBINE them into one coherent
    answer? What is the unit? What is the recombination operator? How do
    SETI@home / Folding@home / ZetaGrid's mechanics (work-unit generation,
    redundancy, validators, trickle/aggregation, Markov-state recombination)
    map onto an INTELLIGENCE-bearing system, and what must change because the
    workers reason rather than just compute?
D2. When 5 models produce 5 DIFFERENT valid-looking solutions, how is ONE chosen
    WITHOUT a vote — by what tool-grounded or maths-model criterion (e.g. the
    solution that passes the most checks; minimal residual risk R_k; simplicity;
    coverage)? Is selection-without-voting always possible, or is there an
    irreducible judgement core?
D3. Which EXISTING CDSFL mechanics (Popperian falsification, the R_k maths
    model, convergence-as-exhaustion, the immune/Bugzilla finding-lifecycle,
    persistence/Merkle sealing) are genuinely reusable for decomposed STEM at
    scale, and which are coding-review-specific and should NOT be carried over?

Use mathematical/empirical tools where they sharpen a claim. Word budget ~1100.
End with: VERDICT on the single-root-cause diagnosis = SOUND / SOUND-WITH-
CAVEATS / UNSOUND; and your single most valuable concrete design recommendation
for the scaling layer.
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
    print(f"=== divergence panel review (pr) — {len(MODELS)} models ===")
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
