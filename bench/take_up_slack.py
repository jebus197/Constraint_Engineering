"""Take-up-slack falsifier resolution — capability-aware routing for falsification.

When the falsifier gate leaves a CRITICAL finding un-confirmed (a weak model wrote
a broken or missing falsifier), the system should NOT immediately escalate to a
human, and should NOT endlessly re-ask the weak model to do work it has
demonstrably failed. Instead, route the falsification to progressively STRONGER
models (ordered by capability fingerprint) with the execute_python tool loop —
"the stronger models take up the slack" — and only escalate to HIL if even the
strongest writer cannot resolve it (a genuinely-hard, e.g. nondeterministic,
defect). This restores the capability-aware routing that the flat parallel
dispatch had collapsed into identical treatment: weak models find, strong models
adjudicate.

Empirical basis (2026-06-07, the 7 hardest Exp-42 residuals; weak SOURCE models
resolved 0/7):
  * strong model (gpt-5.5) + execute_python tool loop  -> 6/7 CONFIRMED
  * the remaining one (C0063, a markdown-code-block embedding trap) is resolved by
    the next, stronger rung (opus-class) -> the 2-rung ladder reaches 7/7.
  * teaching the weak model with worked examples lifted it only 0/5 -> 1/3 — a
    marginal booster, not a cure: hence routing, not re-asking.

This module is deliberately runner-agnostic and side-effect-free: the caller
injects how to dispatch a model (`resolve_fn`), how the runner decides a verdict
(`reverify_fn`), and how to measure finding similarity (`similarity_fn`). That
keeps it unit-testable in isolation and lets the runner wire it at the single
call site after ``apply_falsifier_verdicts``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence


# Capability ordering for the FALSIFICATION task, strongest first. Ordered by the
# Exp-42 EMPIRICAL falsifier-confirm rates, not generic capability: Codex 90% / 0
# residuals (and fast — OpenRouter) leads, then CC2 75% / 0 residuals (strong but
# claude_cli-slow), ChatGPT 67%, Gemini 80%-but-format-fragile, DeepSeek 28% /
# 10-of-15-residuals last. Validated ladder: gpt-5.5 (Codex) resolved 6/7 of the
# hardest residuals; CC2 picks up the 7th (the markdown-embedding trap). The
# primary offender (DeepSeek) is last and is never asked to take up slack.
DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek")


@dataclass
class TakeupResult:
    """Outcome of a take-up-slack attempt on one un-confirmed critical."""
    finding_id: str
    verdict: str                      # CONFIRMED / REFUTED / ERROR / UNTOOLABLE / DUPLICATE
    resolved: bool                    # True iff a strong writer CONFIRMED it
    model_used: Optional[str]         # which rung resolved/last-tried it
    falsifier_code: str               # the resolving (or last) falsifier
    duplicate_of: Optional[str] = None  # set iff resolved as a duplicate
    rungs_tried: int = 0


def rank_falsifier_writers(
    labels: Sequence[str],
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    exclude: Sequence[str] = (),
) -> list[str]:
    """Return the available model labels ordered strongest-first for falsification.

    Models not in ``strength_order`` are appended (in input order) after the ranked
    ones — unknown models are tried, but only after the known-strong ones. ``exclude``
    drops models (e.g. the finding's own source model, which already failed)."""
    excl = set(exclude)
    ranked = [m for m in strength_order if m in labels and m not in excl]
    extras = [m for m in labels if m not in strength_order and m not in excl]
    return ranked + extras


def confirmed_duplicate(
    finding: dict,
    confirmed_findings: Sequence[dict],
    similarity_fn: Callable[[dict, dict], float],
    threshold: float = 0.85,
) -> Optional[str]:
    """If an already-CONFIRMED finding describes the same defect, return its id.

    This catches the C0028<->C0003 / C0015<->C0001 case from Exp 42, where the same
    real defect was independently CONFIRMED under another id by a competent writer,
    while the weak model's restatement escalated only because ITS falsifier was
    broken. A duplicate of a confirmed defect must never reach HIL."""
    best_id, best_sim = None, threshold
    fid = finding.get("finding_id") or finding.get("id")
    for other in confirmed_findings:
        oid = other.get("finding_id") or other.get("id")
        if oid == fid:
            continue
        sim = similarity_fn(finding, other)
        if sim >= best_sim:
            best_id, best_sim = oid, sim
    return best_id


def resolve_via_takeup(
    finding: dict,
    rungs: Sequence[str],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    max_rungs: int = 2,
) -> TakeupResult:
    """Climb the capability ladder until a strong writer CONFIRMS the finding.

    ``rungs``       — model labels, strongest first (from ``rank_falsifier_writers``).
    ``resolve_fn``  — (model_label, finding) -> falsifier_code. The caller dispatches
                      that model WITH the execute_python tool loop and extracts the
                      final falsifier. Empty string means the model produced none.
    ``reverify_fn`` — falsifier_code -> verdict. The runner's real decider
                      (falsifier_verify.reverify_falsifier). It, never the model,
                      decides the verdict — "tools decide".

    Returns a TakeupResult. ``resolved`` is True only on a CONFIRMED from the
    decider; otherwise the caller escalates to HIL with the diagnosis intact.
    A REFUTED here is NOT trusted to drop the critical (CONFIRM-only still holds):
    it just means this rung did not demonstrate it; we try the next rung, then HIL.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"
    last_verdict, last_code, last_model, tried = "UNTOOLABLE", "", None, 0
    for model in list(rungs)[:max_rungs]:
        tried += 1
        last_model = model
        code = (resolve_fn(model, finding) or "").strip()
        last_code = code
        if not code:
            last_verdict = "ERROR"
            continue
        verdict = reverify_fn(code)
        last_verdict = verdict
        if verdict == "CONFIRMED":
            return TakeupResult(fid, "CONFIRMED", True, model, code, rungs_tried=tried)
    # No rung confirmed -> caller escalates to HIL (genuinely-hard until proven otherwise)
    return TakeupResult(fid, last_verdict, False, last_model, last_code, rungs_tried=tried)


def take_up_slack(
    finding: dict,
    available_models: Sequence[str],
    confirmed_findings: Sequence[dict],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    similarity_fn: Callable[[dict, dict], float],
    *,
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    max_rungs: int = 2,
    dup_threshold: float = 0.85,
) -> TakeupResult:
    """Full take-up-slack pass for ONE un-confirmed critical finding.

    Order of operations:
      1. Dedup — if the defect is already CONFIRMED under another id, resolve as a
         duplicate (never escalate a confirmed defect to HIL).
      2. Ladder — route to progressively stronger writers (excluding the finding's
         own source model, which already failed) with the tool loop; CONFIRMED wins.
      3. Caller escalates to HIL only if neither step resolves it.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"

    dup = confirmed_duplicate(finding, confirmed_findings, similarity_fn, dup_threshold)
    if dup is not None:
        return TakeupResult(fid, "DUPLICATE", True, None, "", duplicate_of=dup, rungs_tried=0)

    source = finding.get("source_model")
    rungs = rank_falsifier_writers(
        available_models, strength_order=strength_order,
        exclude=(source,) if source else (),
    )
    return resolve_via_takeup(finding, rungs, resolve_fn, reverify_fn, max_rungs=max_rungs)
