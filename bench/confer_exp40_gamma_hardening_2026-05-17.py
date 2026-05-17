"""Exp 40 gamma-hardening confer — NEUTRAL framing (2026-05-17).

Founder ruling: gamma DEMOTION/deprecation is OFF the table — a HARD
constraint, not a debatable position. gamma remains the load-bearing
decay metric. The confer question is narrower: given verified facts,
what is the soundest, integrity-preserving way to HARDEN/recalibrate
gamma and handle apply-back non-stationarity WITHOUT book-cooking.

Neutral among the remaining hardening options (P1-P5); no presupposed
answer; compelled convergence (one position); each model must state the
strongest case AGAINST its own recommendation and a book-cooking-risk
self-check. Panel: Gemini 3.1 Pro, Codex GPT-5.5, CC2 Opus 4.7, ChatGPT
GPT-5.5, DeepSeek V4 Pro. Star topology, latest CDSFL schema.
Logs: bench/logs/confer_exp40_gamma_hardening_2026-05-17/.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
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
            os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_exp40_gamma_hardening_2026-05-17"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("gemini",   "google/gemini-3.1-pro-preview", "openrouter"),
    ("codex",    "openai/gpt-5.5",                "openrouter"),
    ("cc2",      "opus",                          "claude_cli"),
    ("chatgpt",  "openai/gpt-5.5",                "openrouter"),
    ("deepseek", "deepseek-v4-pro",               "deepseek"),
]

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

PLANF_PM = (REPO_ROOT / "experimental_notes"
            / "Exp40_Slice_F_Convergence_Result_2026-05-17.md").read_text()

ESTIMATOR_SRC = r'''
# bench/reference_runner_v2.py — the gamma estimator (verbatim)
def _estimate_gamma(novelty_counts: List[int], min_rounds: int = 3) -> float:
    n = len(novelty_counts)
    if n < min_rounds:
        return 0.0
    cumulative = []
    total = 0
    for c in novelty_counts:
        total += c
        cumulative.append(total)
    if total == 0:
        return 0.0
    log_x, log_y = [], []
    for i, cum in enumerate(cumulative):
        if cum > 0 and (i + 1) > 0:
            log_x.append(math.log(i + 1))
            log_y.append(math.log(cum))
    if len(log_x) < 2:
        return 0.0
    n_pts = len(log_x); sum_x = sum(log_x); sum_y = sum(log_y)
    sum_xy = sum(x*y for x, y in zip(log_x, log_y))
    sum_x2 = sum(x*x for x in log_x)
    denom = n_pts * sum_x2 - sum_x * sum_x
    if abs(denom) < 1e-12:
        return 0.0
    beta = (n_pts * sum_xy - sum_x * sum_y) / denom
    return max(0.0, min(1.0, 1.0 - beta))     # gamma = clip(1 - beta)

GAMMA_BANDS = [
    (0.45, inf,  "Strong depletion — confirms state-based closure"),
    (0.30, 0.45, "Moderate depletion — consistent with PoC convergence"),
    (0.20, 0.30, "Weak depletion — state closure may be premature"),
    (0.00, 0.20, "Gamma disagrees with state closure — recommend HIL audit"),
]

# The post-reconciliation churn-strip ALREADY in the input path (verbatim):
post_reconciliation_novel = sum(
    1 for e in registry.entries.values()
    if e.get("open_since_round") == round_idx
    and e.get("status") not in {"MERGED","DUPLICATE","UNCONFIRMED","REFUTED"})
# novelty_counts[-1] := post_reconciliation_novel  (replaces raw pre-recon count)
'''

APPENDIX_71 = r'''
# docs/MATHEMATICAL_APPENDIX.md §7.1 Duane NHPP (verbatim excerpt)
lambda(t) = (beta/eta) * (t/eta)^(beta-1)        # discovery intensity
gamma = 1 - beta :  gamma>0 decreasing => genuine convergence (error space
  exhausting);  gamma~0 constant => churn;  gamma<0 increasing => divergence.
Empirical: Duane fits 17/18 CDSFL bench runs better than geometric by AICc.
Error re-injection extension (SPECIFIED, NOT IMPLEMENTED in _estimate_gamma):
  lambda_ext(n) = (beta/eta)*(n/eta)^(beta-1) + nu * Delta_{n-1}
  nu in [0,1] = re-injection coefficient; Delta = adoption magnitude.
Divergence condition: if nu*Delta_{n-1} > |d lambda_Duane/dn| the system
  shifts from convergence to entropy generation. Standard model assumes a
  CLOSED, monotonically-depleting defect pool. gamma & rho are defined as
  COMPLEMENTARY diagnostics (rho = novel/raw efficiency); appendix states
  the standard gamma is churn-blind by construction at the novel-rate level.
'''

FRAMING = r"""
## gamma-hardening confer — framing (read first)

FOUNDER HARD CONSTRAINTS (not debatable; treat as fixed):
1. gamma is NOT to be demoted, deprecated, or removed as a load-bearing
   convergence metric. It was the founding decay-curve concept of the
   project; sidelining it late because it returns inconvenient numbers
   would invalidate the project's premise. Any answer that amounts to
   "stop using gamma as a real gate" is OUT OF SCOPE and will be rejected.
2. No book-cooking. No making the curve fit the data or the data fit the
   curve. Any recalibration must be principled, regime-justified, and
   documented; the measurement must remain real, meaningful, reliable.
3. Compelled convergence: ONE converged position. Not a menu. If you
   dissent from the emerging consensus, defend it on technical grounds.

This is NOT a leading question. The space of hardening approaches below
(P1-P5) has NO presupposed winner. Demotion is excluded by founder
ruling (above), not by the panel. Your task is to converge on the
soundest COMPOSITION of P1-P5 (or a better option you specify) that
makes gamma a rigorous, integrity-preserving decay metric under the
verified facts. Each model must also: (a) give the single strongest
argument AGAINST its own recommendation; (b) self-check whether its
recommendation risks book-cooking and argue why it does not; (c) judge
whether the severity>=0.7 "critical" cut is itself sound or arbitrary.

Word budget: 1500 words. Acceptance: 5/5 converged.
"""

VERIFIED_FACTS = r"""
## Verified facts (code- and data-grounded; reason from these, not priors)

F1. ESTIMATOR. gamma is computed by _estimate_gamma (full source in
   Background A): an ordinary least-squares fit of log(cumulative
   novelty) vs log(round index); gamma = clip(1 - slope, 0, 1). It is a
   GLOBAL CUMULATIVE statistic over all rounds — early high-discovery
   rounds dominate the slope; a short near-zero-novelty tail moves it
   little.

F2. INPUT IS ALREADY CHURN-STRIPPED. Contrary to a "gamma is naively
   counting duplicate churn" assumption, the input is already corrected
   to POST-RECONCILIATION novelty (Background A, lower block): findings
   that reconciliation merged/duped/refuted/left-unconfirmed are removed
   before they reach gamma. This correction was added after an Exp 40
   Round-9 bug (pre-recon novel=58 while reconciliation saw full
   saturation). So residual elusiveness is NOT raw-duplicate churn.

F3. RESIDUAL CAUSE — SEVERITY GRANULARITY. The churn-stripped input is
   still SEVERITY-AGNOSTIC: it counts every genuinely-new finding of any
   severity. The convergence event that actually fired counts only
   novel CRITICAL findings (severity >= 0.7). Genuine low-severity
   refinements (a near-infinite surface on language/code) keep the
   cumulative rising after critical novelty is exhausted.

F4. DUAL-SERIES EXHIBIT (plan-F, the run that converged at round 6 via
   3 consecutive zero-novel-CRITICAL rounds). Per-round critical
   (sev>=0.7) = [8,4,0,3,1,1,1]. gamma on the all-novelty series ≈ 0.27
   (production, "weak/elusive", below the 0.30 gate). gamma on the
   critical-only series ≈ 0.60 (STRONG-depletion band, decisively
   converged). SAME run, SAME estimator, different input series.
   CAVEAT: the ≈0.60 is an offline recompute on report finding-lists;
   the exact production figure must be recomputed through the full
   reconciliation+severity pipeline. Direction/magnitude robust; exact
   value to be confirmed.

F5. CALIBRATION REGIME. The 0.30 gate threshold (and the GAMMA_BANDS,
   Background A) were calibrated on long, near-stationary runs — e.g.
   Exp 37, 16 rounds, gamma 0.467, STATE_CONVERGED. plan-F converged
   structurally at round 6 (7 rounds total).

F6. APPLY-BACK NON-STATIONARITY. plan-C ("apply verified fixes back to
   a per-run working copy") mutates the review target every few rounds.
   The standard Duane model (Background B) assumes a CLOSED,
   monotonically-depleting defect pool. The appendix SPECIFIES a
   re-injection-extended intensity lambda_ext (nu, Delta terms) for
   exactly this case; _estimate_gamma implements ONLY the standard
   model. plan-F (which converged) ran with apply-back ON.

F7. plan-F is one run on the smallest decomposed slice; it changed
   several variables together (decomposition + apply-back + in-round
   re-ask + cleaned baseline). It validates the cure direction; it does
   not isolate the dominant factor (see Background C, full post-mortem).
"""

QUESTION = r"""
## The question (neutral; converge on ONE position)

Candidate hardening levers (no presupposed winner; compose, reject, or
improve as the evidence dictates — gamma DEMOTION is excluded per
founder ruling and is NOT a candidate):

  P1. Feed gamma the critical/structural series (severity-gated) as the
      reliability-growth signal it is meant to measure.
  P2. Dual-series gamma: critical-only = the structural convergence
      signal; all-novelty = a separate entropic-noise diagnostic. Both
      computed and logged; the critical-only series carries the gate.
  P3. Phase isolation: a FROZEN-target Calibration Leg (no apply-back,
      bounded rounds) where gamma is measured in the closed-pool regime
      its mathematics assumes; a separate dynamic Execution Leg with
      apply-back, measured appropriately. gamma stays rigorous, measured
      where valid.
  P4. Implement the appendix's re-injection-extended Duane (lambda_ext,
      nu/Delta) so gamma is correctly modelled under apply-back rather
      than mis-specified.
  P5. Regime-aware recalibration of the 0.30 threshold (run-length /
      stationarity aware), principled and documented — NOT fitted to a
      desired outcome.

ANSWER (one converged position):
- Which composition of P1-P5 (and/or a better-specified option) makes
  gamma a rigorous, integrity-preserving decay metric WITHOUT
  demotion and WITHOUT book-cooking? State the order of implementation.
- Is the severity>=0.7 "critical" cut sound, or arbitrary? If arbitrary,
  what principled cut/definition replaces it?
- Does apply-back's non-stationarity argue that the OLDER
  collect-fixes-at-end methodology is more gamma-compatible, or is P3/P4
  the correct reconciliation? Take a position.
- For your recommendation: the single strongest argument AGAINST it;
  and an explicit book-cooking self-check (why your recalibration is
  principled, not curve-fitting).

Separately: a prior Gemini take both opposed gamma demotion AND endorsed
it (internal contradiction). Judge all ideas on technical merit only;
explicitly flag any parroting or unsupported assertion in your own or
others' reasoning.
"""

RESPONSE_FORMAT = r"""
## Response format

CONVERGED POSITION: <the single composition of P1-P5 (+order), one
  paragraph, technically grounded in F1-F7 + Backgrounds>
SEVERITY CUT: <sound or arbitrary; if arbitrary, the principled
  replacement>
APPLY-BACK vs OLD METHODOLOGY: <position + technical reason>
STRONGEST COUNTER TO MY POSITION: <one paragraph; then: does it
  overturn the position? yes/no + why>
BOOK-COOKING SELF-CHECK: <why this recalibration is principled, not
  fitting the curve to the data>
PARROTING FLAGS: <any unsupported/echoed assertion you spotted>

Total <= 1500 words. ONE converged position. gamma demotion is OUT OF
SCOPE (founder hard constraint). No book-cooking.
"""


def build_user_prompt() -> str:
    return (
        FRAMING + "\n\n" + VERIFIED_FACTS + "\n\n" + QUESTION + "\n\n"
        + "## Background A — gamma estimator + bands + churn-strip (verbatim)\n"
        + ESTIMATOR_SRC + "\n\n"
        + "## Background B — appendix §7.1 Duane + re-injection model\n"
        + APPENDIX_71 + "\n\n"
        + "## Background C — plan-F convergence result post-mortem (full)\n\n"
        + PLANF_PM + "\n\n" + RESPONSE_FORMAT
    )


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
            "model": model_id, "label": model_label, "api": api,
            "response": response, "time_s": round(elapsed, 1),
            "chars": len(response) if response else 0,
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "model": model_id, "label": model_label, "api": api,
            "error": f"{type(e).__name__}: {e}",
            "time_s": round(elapsed, 1),
            "prompt_chars": len(system_prompt) + len(user_prompt),
        }


def main() -> int:
    system_prompt = CDSFL_TEXT
    user_prompt = build_user_prompt()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total_chars = len(system_prompt) + len(user_prompt)
    print(f"Dispatching Exp 40 gamma-hardening NEUTRAL confer to "
          f"{len(MODELS)} models")
    print(f"Prompt size: {total_chars} chars "
          f"(system {len(system_prompt)} + user {len(user_prompt)})")
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
                print(f"  {label}: ERROR in {result['time_s']}s — "
                      f"{result['error'][:200]}")
            else:
                print(f"  {label}: {result['chars']} chars in "
                      f"{result['time_s']}s")
            (LOGS_DIR / f"{label}_{timestamp}.json").write_text(
                json.dumps(result, indent=2))

    combined_path = LOGS_DIR / f"combined_{timestamp}.json"
    combined_path.write_text(json.dumps(results, indent=2))
    print()
    print(f"Combined log: {combined_path}")

    errors = [label for label, r in results.items() if "error" in r]
    if errors:
        print(f"\n{len(errors)}/{len(MODELS)} models errored: "
              f"{', '.join(errors)}")
        return 1
    print(f"\nAll {len(MODELS)} models returned cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
